// Original diagnostic interposer. Generated game bodies and witnesses stay private.
#include "cpu_state.h"
#include "dirty_ram_interp.h"
#include "psx_cycle_freeze.h"
#include "psx_icache.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <map>
#include <vector>
extern "C" {
int __real_psx_overlay_dispatch(CPUState*, uint32_t);
int psx_overlay_static_can_dispatch(uint32_t);
uint8_t *memory_get_scratchpad_ptr();
extern uint8_t *g_psx_ram;
extern uint32_t g_debug_last_store_pc;
extern uint64_t s_frame_count;
}
namespace {
struct Range { uint32_t start, size; };
const std::vector<Range>& ranges() {
    static const auto value = [] {
        std::vector<Range> result;
        bool private_directory=false;
        for(const auto &part:std::filesystem::current_path())if(part==".local")private_directory=true;
        if(!private_directory){std::fprintf(stderr,"Qualification output requires a private .local directory\n");std::exit(92);}
        const char *path = std::getenv("N2O_SELECTION");
        FILE *f = path ? std::fopen(path, "r") : nullptr;
        if (!f) { std::fprintf(stderr, "Missing private N2O_SELECTION metadata\n"); std::exit(92); }
        Range r{};
        int fields=0;
        while ((fields=std::fscanf(f, "%x %x", &r.start, &r.size)) == 2) {
            if (r.start < 0x80010000 || r.start >= 0x80200000 || !r.size ||
                r.size > 0x80200000u-r.start || (r.start|r.size)&3) std::exit(92);
            result.push_back(r);
        }
        const bool ok = fields==EOF && std::feof(f) && !result.empty(); std::fclose(f);
        if (!ok) std::exit(92);
        return result;
    }();
    return value;
}
bool selected(uint32_t pc) { for (auto r:ranges()) if (pc>=r.start && pc-r.start<r.size) return true; return false; }
bool root(uint32_t pc) { for (auto r:ranges()) if (pc==r.start) return true; return false; }
std::map<uint32_t,unsigned> seen,passed;
unsigned total=0,failed=0;
bool busy=false,edge_running=false,replay_only=false;
// Full guest-memory word scans exceed the small drawing-routine budget.
constexpr unsigned reference_block_limit=1u<<20;
std::vector<uint8_t> initial(0x200000),native_ram(0x200000);
uint8_t scratch_before[1024],scratch_native[1024];
uint32_t cache[1024];
void report() {
    FILE *f=std::fopen("qualification-summary.txt","w"); if(!f)return;
    std::fprintf(f,"comparisons=%u failures=%u pcs=%zu frame=%llu\n",total,failed,passed.size(),(unsigned long long)s_frame_count);
    for(auto &e:passed)std::fprintf(f,"%08X %u\n",e.first,e.second);
    std::fclose(f);
}
void restore(const CPUState&before,CPUState*cpu,const DirtyRamLoadDelay&ld,int bail,uint32_t store) {
    *cpu=before;std::memcpy(g_psx_ram,initial.data(),initial.size());
    std::memcpy(memory_get_scratchpad_ptr(),scratch_before,1024);
    std::memcpy(g_psx_icache_tv,cache,sizeof cache);dirty_ram_ld_delay_restore(&ld);
    g_psx_call_bail=bail;g_debug_last_store_pc=store;overlay_watch_invalidate_after_ram_restore();
}
}
extern "C" int __wrap_psx_overlay_dispatch(CPUState*cpu,uint32_t addr) {
    if(busy || !std::getenv("N2O_COMPARE") || !selected(addr) ||
       (seen[addr]>=3 && !edge_running) || !psx_overlay_static_can_dispatch(addr))
        return __real_psx_overlay_dispatch(cpu,addr);
    busy=true;seen[addr]++;
    const CPUState before=*cpu;const int bail=g_psx_call_bail;const uint32_t store=g_debug_last_store_pc;
    DirtyRamLoadDelay ld;dirty_ram_ld_delay_save(&ld);
    std::memcpy(initial.data(),g_psx_ram,initial.size());std::memcpy(scratch_before,memory_get_scratchpad_ptr(),1024);
    std::memcpy(cache,g_psx_icache_tv,sizeof cache);
    PsxCycleFreeze freeze{};
    if(!psx_cycle_uncharged_begin(&freeze,0)){busy=false;return __real_psx_overlay_dispatch(cpu,addr);}
    const int handled=__real_psx_overlay_dispatch(cpu,addr);dirty_ram_ld_delay_flush(cpu);
    const CPUState native=*cpu;std::memcpy(native_ram.data(),g_psx_ram,native_ram.size());
    std::memcpy(scratch_native,memory_get_scratchpad_ptr(),1024);psx_cycle_uncharged_end(&freeze);
    restore(before,cpu,ld,bail,store);
    uint32_t oldlo,oldhi;dirty_ram_span_get(&oldlo,&oldhi);dirty_ram_span_set(0x10000,0x200000);
    psx_cycle_uncharged_begin(&freeze,0);uint32_t pc=addr;unsigned blocks=0;bool ok=handled;
    do {
        cpu->pc=pc;if(!dirty_ram_dispatch(cpu,pc,0)){ok=false;break;}pc=cpu->pc;
        if(pc==native.pc)break;
        if(pc<0x80010000 || pc>=0x80200000){ok=false;break;}
    } while(++blocks<reference_block_limit);
    dirty_ram_ld_delay_flush(cpu);psx_cycle_uncharged_end(&freeze);dirty_ram_span_set(oldlo,oldhi);
    const bool regs=std::memcmp(cpu->gpr,native.gpr,128)==0 && cpu->pc==native.pc && cpu->hi==native.hi && cpu->lo==native.lo &&
        std::memcmp(cpu->cop0,native.cop0,128)==0 && std::memcmp(cpu->gte_data,native.gte_data,128)==0 && std::memcmp(cpu->gte_ctrl,native.gte_ctrl,128)==0;
    const bool ram=std::memcmp(g_psx_ram,native_ram.data(),native_ram.size())==0;
    const bool scratch=std::memcmp(memory_get_scratchpad_ptr(),scratch_native,1024)==0;++total;
    if(ok && blocks<reference_block_limit && regs && ram && scratch)passed[addr]++;
    else {
        ++failed;std::fprintf(stderr,"N2O_COMPARE FAIL entry=%08X native.pc=%08X ref.pc=%08X blocks=%u ok=%d regs=%d ram=%d scratch=%d frame=%llu\n",addr,native.pc,cpu->pc,blocks,ok,regs,ram,scratch,(unsigned long long)s_frame_count);
        if(blocks>=reference_block_limit)std::fprintf(stderr," Reference block budget exhausted; segment remains unqualified\n");
        for(unsigned i=0;i<32;i++)if(cpu->gpr[i]!=native.gpr[i])std::fprintf(stderr," GPR%u native=%08X ref=%08X\n",i,native.gpr[i],cpu->gpr[i]);
        for(unsigned i=0;i<32;i++)if(cpu->gte_data[i]!=native.gte_data[i] || cpu->gte_ctrl[i]!=native.gte_ctrl[i])std::fprintf(stderr," GTE%u nd=%08X rd=%08X nc=%08X rc=%08X\n",i,native.gte_data[i],cpu->gte_data[i],native.gte_ctrl[i],cpu->gte_ctrl[i]);
        for(unsigned i=0,n=0;i<initial.size() && n<8;i++)if(g_psx_ram[i]!=native_ram[i]){std::fprintf(stderr," RAM%X native=%02X ref=%02X\n",i,native_ram[i],g_psx_ram[i]);++n;}
    }
    if(seen[addr]==1 && !edge_running) {
        char name[64];std::snprintf(name,sizeof name,"call-%08X.bin",addr);FILE*f=std::fopen(name,"wb");
        if(!f)std::exit(93);
        const bool saved=std::fwrite(&before,sizeof before,1,f)==1 && std::fwrite(initial.data(),initial.size(),1,f)==1 && std::fwrite(scratch_before,1024,1,f)==1;
        std::fclose(f);if(!saved)std::exit(93);
    }
    restore(before,cpu,ld,bail,store);busy=false;report();
    if(failed){std::fflush(stderr);std::exit(91);}
    if(!edge_running && root(addr) && seen[addr]==1 && std::getenv("N2O_EDGE")) {
        edge_running=true;replay_only=true;
        const uint32_t patterns[]={0,1,0xFFFFFFFF,0x7FFF,0x8000,0x7FFFFFFF,0x80000000,0x1000,0xFFFF0000,0x55555555,0xAAAAAAAA,0x00FFFFFF};
        for(unsigned lane=0;lane<2;lane++)for(uint32_t pattern:patterns) {
            CPUState sample=before;for(unsigned i=0;i<32;i++){if(lane==0)sample.gte_data[i]=pattern;else sample.gte_ctrl[i]=pattern;}
            __wrap_psx_overlay_dispatch(&sample,addr);restore(before,cpu,ld,bail,store);
        }
        edge_running=false;replay_only=false;
    }
    if(replay_only){*cpu=native;std::memcpy(g_psx_ram,native_ram.data(),native_ram.size());std::memcpy(memory_get_scratchpad_ptr(),scratch_native,1024);return 1;}
    return __real_psx_overlay_dispatch(cpu,addr);
}
extern "C" int n2o_replay_segment(CPUState*cpu,uint32_t pc) {
    edge_running=true;replay_only=true;const int ret=__wrap_psx_overlay_dispatch(cpu,pc);
    edge_running=false;replay_only=false;return ret;
}
