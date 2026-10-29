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
#include <algorithm>
#include <charconv>
#include <fstream>
#include <set>
#include <sstream>
#include <string>
extern "C" {
int __real_psx_overlay_dispatch(CPUState*, uint32_t);
int psx_overlay_static_can_dispatch(uint32_t);
int psx_overlay_static_code_matches(const uint32_t*,uint32_t,uint32_t);
uint8_t *memory_get_scratchpad_ptr();
extern uint8_t *g_psx_ram;
extern uint32_t g_debug_last_store_pc;
extern uint64_t s_frame_count;
}
namespace {
struct Range {
    uint32_t start=0,size=0,crc=0;
    uint64_t id=0;
    std::vector<uint32_t> code,pcs;
};
using Key=std::pair<uint64_t,uint32_t>;
std::map<Key,unsigned> seen,passed;
std::set<uint64_t> blocked;
unsigned total=0,failed=0;
bool busy=false,edge_running=false,replay_only=false;
uint64_t wanted_id=0;
uint64_t bytes_hash(const uint8_t*p,size_t size) {
    uint64_t h=14695981039346656037ull;
    for(size_t i=0;i<size;i++){h^=p[i];h*=1099511628211ull;}return h;
}
void trace_miss(uint32_t pc) {
    if(!std::getenv("N2O_TRACE_MISSES") || !g_psx_ram || pc<0x80010000 || pc>0x801FFFE0 || pc%4)return;
    static uint64_t frame=~uint64_t(0),occupant=0;static std::set<Key>observed;static FILE*file=nullptr;
    if(frame!=s_frame_count){frame=s_frame_count;occupant=bytes_hash(g_psx_ram+0x21500,32);}
    if(!observed.insert({occupant,pc}).second)return;
    if(!file){file=std::fopen("untranslated-pcs.tsv","w");if(!file)std::exit(93);}
    // Discovery metadata only. Never infer executable identity from this hash.
    std::fprintf(file,"%016llX %08X %016llX %llu\n",(unsigned long long)occupant,pc,
                 (unsigned long long)bytes_hash(g_psx_ram+(pc&0x1FFFFF),32),(unsigned long long)s_frame_count);
}
bool hexword(const std::string&s,uint64_t&v) {
    const char*b=s.data(),*e=b+s.size();
    if(s.size()>2 && b[0]=='0' && (b[1]=='x'||b[1]=='X'))b+=2;
    const auto r=std::from_chars(b,e,v,16);
    return b!=e && r.ec==std::errc{} && r.ptr==e;
}
void fail_at_exit() { if(failed){std::fflush(nullptr);std::_Exit(91);} }
const std::vector<Range>& ranges() {
    static const auto value = [] {
        std::vector<Range> result;
        bool private_directory=false;
        for(const auto &part:std::filesystem::current_path())if(part==".local")private_directory=true;
        if(!private_directory){std::fprintf(stderr,"Qualification output requires a private .local directory\n");std::exit(92);}
        const char *path = std::getenv("N2O_SELECTION");
        if(!path)std::exit(92);
        std::ifstream f(path);if(!f)std::exit(92);
        std::string line;bool v2=false,first=true;std::set<uint64_t>ids;
        while(std::getline(f,line)) {
            std::istringstream stream(line);std::string word;std::vector<uint64_t>w;
            if(!(stream>>word))continue;
            if(first && word=="v2") {if(stream>>word)std::exit(92);v2=true;first=false;continue;}
            first=false;
            do {uint64_t value;if(!hexword(word,value))std::exit(92);w.push_back(value);}while(stream>>word);
            Range r;
            if(!v2) {if(w.size()!=2)std::exit(92);}
            else {
                if(w.size()<6 || !w[0] || !w[4] || w[4]>4096 || !w[5] || w[5]>0x80000 ||
                   w.size()!=6+2*w[4]+w[5] || !ids.insert(w[0]).second)std::exit(92);
                r.id=w[0];w.erase(w.begin());
            }
            for(uint64_t value:w)if(value>0xFFFFFFFFu)std::exit(92);
            r.start=uint32_t(w[0]);r.size=uint32_t(w[1]);
            if (r.start < 0x80010000 || r.start >= 0x80200000 || !r.size ||
                r.size > 0x80200000u-r.start || (r.start|r.size)&3) std::exit(92);
            if(v2) {
                r.crc=uint32_t(w[2]);const size_t nr=w[3],np=w[4];
                for(size_t i=0;i<nr;i++) {
                    const uint32_t lo=uint32_t(w[5+2*i]),size=uint32_t(w[6+2*i]);
                    if((lo|size)&3 || !size || lo<r.start || lo>=r.start+r.size || size>r.start+r.size-lo)std::exit(92);
                    r.code.push_back(lo);r.code.push_back(size);
                }
                for(size_t i=0;i<np;i++) {
                    const uint32_t pc=uint32_t(w[5+2*nr+i]);bool guarded=false;
                    for(size_t j=0;j<r.code.size();j+=2)if(pc>=r.code[j] && pc-r.code[j]<r.code[j+1])guarded=true;
                    if(pc%4 || !guarded || (!r.pcs.empty() && pc<=r.pcs.back()))std::exit(92);
                    r.pcs.push_back(pc);
                }
                if(!std::binary_search(r.pcs.begin(),r.pcs.end(),r.start))std::exit(92);
            }
            result.push_back(std::move(r));
        }
        if (!f.eof() || result.empty() || (std::getenv("N2O_COLLECT_FAILURES") && !v2)) std::exit(92);
        if(const char*disabled=std::getenv("N2O_BLOCKED_IDS")) {
            if(!v2)std::exit(92);
            std::ifstream input(disabled);if(!input)std::exit(92);
            std::string word;
            while(input>>word){uint64_t id;if(!hexword(word,id) || !ids.count(id) || !blocked.insert(id).second)std::exit(92);}
            if(!input.eof())std::exit(92);
        }
        if(std::getenv("N2O_COLLECT_FAILURES"))std::atexit(fail_at_exit);
        return result;
    }();
    return value;
}
const std::map<uint32_t,std::vector<const Range*>>& pc_index() {
    static const auto index=[] {
        std::map<uint32_t,std::vector<const Range*>> value;
        for(const auto&r:ranges())for(uint32_t pc:r.pcs)value[pc].push_back(&r);
        return value;
    }();return index;
}
const std::vector<const Range*>& legacy_ranges() {
    static const auto value=[] {std::vector<const Range*>v;for(const auto&r:ranges())if(!r.id)v.push_back(&r);return v;}();
    return value;
}
bool resident(const Range&r) {
    return !r.id || psx_overlay_static_code_matches(r.code.data(),uint32_t(r.code.size()/2),r.crc);
}
const Range* selected(uint32_t pc,bool disabled=false) {
    const auto acceptable=[&](const Range&r) {
        if(disabled)return blocked.count(r.id) && resident(r);
        if(blocked.count(r.id) || (replay_only && r.id!=wanted_id) ||
           (!edge_running && seen[{r.id,pc}]>=3))return false;
        return resident(r);
    };
    const auto&index=pc_index();const auto found=index.find(pc);
    if(found!=index.end())for(const Range*r:found->second)if(acceptable(*r))return r;
    for(const Range*r:legacy_ranges())if(pc>=r->start && pc-r->start<r->size && acceptable(*r))return r;
    return nullptr;
}
// Full guest-memory word scans exceed the small drawing-routine budget.
constexpr unsigned reference_block_limit=1u<<20;
constexpr uint64_t native_cycle_limit=1u<<24;
std::vector<uint8_t> initial(0x200000),native_ram(0x200000);
uint8_t scratch_before[1024],scratch_native[1024];
uint32_t cache[1024];
void report() {
    FILE *f=std::fopen("qualification-summary.txt","w"); if(!f)return;
    std::fprintf(f,"comparisons=%u failures=%u pcs=%zu frame=%llu\n",total,failed,passed.size(),(unsigned long long)s_frame_count);
    for(auto &e:passed) {
        if(e.first.first)std::fprintf(f,"%016llX ",(unsigned long long)e.first.first);
        std::fprintf(f,"%08X %u\n",e.first.second,e.second);
    }
    std::fclose(f);
    if(!blocked.empty()) {
        f=std::fopen("blocked-identities.txt","w");if(!f)std::exit(93);
        for(uint64_t id:blocked)std::fprintf(f,"%016llX\n",(unsigned long long)id);
        std::fclose(f);
    }
}
void restore(const CPUState&before,CPUState*cpu,const DirtyRamLoadDelay&ld,int bail,uint32_t store) {
    *cpu=before;std::memcpy(g_psx_ram,initial.data(),initial.size());
    std::memcpy(memory_get_scratchpad_ptr(),scratch_before,1024);
    std::memcpy(g_psx_icache_tv,cache,sizeof cache);dirty_ram_ld_delay_restore(&ld);
    g_psx_call_bail=bail;g_debug_last_store_pc=store;overlay_watch_invalidate_after_ram_restore();
}
}
extern "C" int __wrap_psx_overlay_dispatch(CPUState*cpu,uint32_t addr) {
    if(!std::getenv("N2O_COMPARE"))return __real_psx_overlay_dispatch(cpu,addr);
    (void)ranges(); // Load explicit exclusions before the first native dispatch.
    if(!blocked.empty() && selected(addr,true))return 0;
    if(busy)return __real_psx_overlay_dispatch(cpu,addr);
    const Range*selection=selected(addr);
    if(!selection || !psx_overlay_static_can_dispatch(addr)) {
        const int handled=__real_psx_overlay_dispatch(cpu,addr);if(!handled)trace_miss(addr);return handled;
    }
    const Key key={selection->id,addr};busy=true;seen[key]++;
    const CPUState before=*cpu;const int bail=g_psx_call_bail;const uint32_t store=g_debug_last_store_pc;
    DirtyRamLoadDelay ld;dirty_ram_ld_delay_save(&ld);
    std::memcpy(initial.data(),g_psx_ram,initial.size());std::memcpy(scratch_before,memory_get_scratchpad_ptr(),1024);
    std::memcpy(cache,g_psx_icache_tv,sizeof cache);
    PsxCycleFreeze freeze{};
    if(!psx_cycle_uncharged_begin(&freeze,native_cycle_limit)){busy=false;return __real_psx_overlay_dispatch(cpu,addr);}
    const int handled=__real_psx_overlay_dispatch(cpu,addr);dirty_ram_ld_delay_flush(cpu);
    const CPUState native=*cpu;std::memcpy(native_ram.data(),g_psx_ram,native_ram.size());
    std::memcpy(scratch_native,memory_get_scratchpad_ptr(),1024);
    const bool native_uncharged=psx_cycle_uncharged_end(&freeze);
    restore(before,cpu,ld,bail,store);
    uint32_t oldlo,oldhi;dirty_ram_span_get(&oldlo,&oldhi);dirty_ram_span_set(0x10000,0x200000);
    psx_cycle_uncharged_begin(&freeze,native_cycle_limit);uint32_t pc=addr;unsigned blocks=0;bool ok=handled;
    do {
        cpu->pc=pc;if(!dirty_ram_dispatch(cpu,pc,0)){ok=false;break;}pc=cpu->pc;
        if(pc==native.pc)break;
        if(pc<0x80010000 || pc>=0x80200000){ok=false;break;}
    } while(++blocks<reference_block_limit);
    dirty_ram_ld_delay_flush(cpu);const bool reference_uncharged=psx_cycle_uncharged_end(&freeze);dirty_ram_span_set(oldlo,oldhi);
    const bool regs=std::memcmp(cpu->gpr,native.gpr,128)==0 && cpu->pc==native.pc && cpu->hi==native.hi && cpu->lo==native.lo &&
        std::memcmp(cpu->cop0,native.cop0,128)==0 && std::memcmp(cpu->gte_data,native.gte_data,128)==0 && std::memcmp(cpu->gte_ctrl,native.gte_ctrl,128)==0;
    const bool ram=std::memcmp(g_psx_ram,native_ram.data(),native_ram.size())==0;
    const bool scratch=std::memcmp(memory_get_scratchpad_ptr(),scratch_native,1024)==0;++total;
    const bool matched=ok && native_uncharged && reference_uncharged && blocks<reference_block_limit && regs && ram && scratch;
    if(matched)passed[key]++;
    else {
        ++failed;std::fprintf(stderr,"N2O_COMPARE FAIL id=%016llX entry=%08X native.pc=%08X ref.pc=%08X blocks=%u ok=%d regs=%d ram=%d scratch=%d frame=%llu\n",(unsigned long long)selection->id,addr,native.pc,cpu->pc,blocks,ok,regs,ram,scratch,(unsigned long long)s_frame_count);
        if(blocks>=reference_block_limit)std::fprintf(stderr," Reference block budget exhausted; segment remains unqualified\n");
        if(!native_uncharged || !reference_uncharged)std::fprintf(stderr," Uncharged cycle budget exhausted; stop before collecting further evidence\n");
        for(unsigned i=0;i<32;i++)if(cpu->gpr[i]!=native.gpr[i])std::fprintf(stderr," GPR%u native=%08X ref=%08X\n",i,native.gpr[i],cpu->gpr[i]);
        for(unsigned i=0;i<32;i++)if(cpu->gte_data[i]!=native.gte_data[i] || cpu->gte_ctrl[i]!=native.gte_ctrl[i])std::fprintf(stderr," GTE%u nd=%08X rd=%08X nc=%08X rc=%08X\n",i,native.gte_data[i],cpu->gte_data[i],native.gte_ctrl[i],cpu->gte_ctrl[i]);
        for(unsigned i=0,n=0;i<initial.size() && n<8;i++)if(g_psx_ram[i]!=native_ram[i]){std::fprintf(stderr," RAM%X native=%02X ref=%02X\n",i,native_ram[i],g_psx_ram[i]);++n;}
    }
    if(seen[key]==1 && !edge_running) {
        char name[96];
        if(selection->id)std::snprintf(name,sizeof name,"call-%016llX-%08X.bin",(unsigned long long)selection->id,addr);
        else std::snprintf(name,sizeof name,"call-%08X.bin",addr);
        FILE*f=std::fopen(name,"wb");
        if(!f)std::exit(93);
        const bool saved=std::fwrite(&before,sizeof before,1,f)==1 && std::fwrite(initial.data(),initial.size(),1,f)==1 && std::fwrite(scratch_before,1024,1,f)==1;
        std::fclose(f);if(!saved)std::exit(93);
    }
    const bool collect=!matched && native_uncharged && reference_uncharged && !edge_running && selection->id && std::getenv("N2O_COLLECT_FAILURES");
    if(collect)blocked.insert(selection->id);
    restore(before,cpu,ld,bail,store);busy=false;report();
    if(collect)return 0; // Caller executes the original interpreter path.
    if(!matched){std::fflush(stderr);std::exit(91);}
    if(!edge_running && addr==selection->start && seen[key]==1 && std::getenv("N2O_EDGE")) {
        edge_running=true;replay_only=true;wanted_id=selection->id;
        const uint32_t patterns[]={0,1,0xFFFFFFFF,0x7FFF,0x8000,0x7FFFFFFF,0x80000000,0x1000,0xFFFF0000,0x55555555,0xAAAAAAAA,0x00FFFFFF};
        for(unsigned lane=0;lane<2;lane++)for(uint32_t pattern:patterns) {
            CPUState sample=before;for(unsigned i=0;i<32;i++){if(lane==0)sample.gte_data[i]=pattern;else sample.gte_ctrl[i]=pattern;}
            __wrap_psx_overlay_dispatch(&sample,addr);restore(before,cpu,ld,bail,store);
        }
        edge_running=false;replay_only=false;wanted_id=0;
    }
    if(replay_only){*cpu=native;std::memcpy(g_psx_ram,native_ram.data(),native_ram.size());std::memcpy(memory_get_scratchpad_ptr(),scratch_native,1024);return 1;}
    return __real_psx_overlay_dispatch(cpu,addr);
}
extern "C" int n2o_replay_segment(CPUState*cpu,uint32_t pc) {
    wanted_id=0;
    if(const char*id=std::getenv("N2O_REPLAY_ID"))if(!hexword(id,wanted_id))return 0;
    edge_running=true;replay_only=true;
    if(!selected(pc)){edge_running=false;replay_only=false;return 0;}
    const int ret=__wrap_psx_overlay_dispatch(cpu,pc);
    edge_running=false;replay_only=false;return ret;
}
