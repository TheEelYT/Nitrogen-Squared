// Original controller-logic fixture. No guest instructions or imported bytes.
#include "cpu_state.h"
#include "dirty_ram_interp.h"
#include "psx_cycle_freeze.h"
#include <cassert>
#include <cstdio>
#include <cstring>
extern "C" {
int __wrap_psx_overlay_dispatch(CPUState*,uint32_t);
int n2o_replay_segment(CPUState*,uint32_t);
uint8_t ram_image[0x200000],scratch_image[1024];
uint8_t*g_psx_ram=ram_image;
uint32_t g_psx_icache_tv[1024],g_debug_last_store_pc;
uint64_t s_frame_count;
int g_psx_call_bail;
}
static unsigned resident_image=1,native_calls=0;
static bool inject_failure=false,exhaust_budget=false;
static DirtyRamLoadDelay delay{};
extern "C" uint8_t*memory_get_scratchpad_ptr(){return scratch_image;}
extern "C" int psx_overlay_static_can_dispatch(uint32_t){return 1;}
extern "C" int psx_overlay_static_code_matches(const uint32_t*,uint32_t,uint32_t crc){return crc==(resident_image==1?123u:456u);}
extern "C" int psx_cycle_uncharged_begin(PsxCycleFreeze*,uint64_t){return 1;}
extern "C" int psx_cycle_uncharged_end(const PsxCycleFreeze*){return !exhaust_budget;}
extern "C" void overlay_watch_invalidate_after_ram_restore(){}
extern "C" void dirty_ram_span_get(uint32_t*lo,uint32_t*hi){*lo=*hi=0;}
extern "C" void dirty_ram_span_set(uint32_t,uint32_t){}
extern "C" void dirty_ram_ld_delay_save(DirtyRamLoadDelay*out){*out=delay;}
extern "C" void dirty_ram_ld_delay_restore(const DirtyRamLoadDelay*in){delay=*in;}
extern "C" void dirty_ram_ld_delay_flush(CPUState*){}
extern "C" int dirty_ram_dispatch(CPUState*cpu,uint32_t addr,uint32_t){cpu->gpr[2]=resident_image==1?11:22;cpu->pc=addr+8;return 1;}
extern "C" int __real_psx_overlay_dispatch(CPUState*cpu,uint32_t addr){
    if(addr==0x80020080)return 0;
    ++native_calls;cpu->gpr[2]=resident_image==1?11:22;cpu->pc=addr+8;
    if(inject_failure && resident_image==1){cpu->gpr[2]=99;ram_image[17]=88;scratch_image[7]=55;g_psx_icache_tv[0]=77;delay.val=66;g_psx_call_bail=19;g_debug_last_store_pc=44;}
    return 1;
}
int main(int argc,char**argv){
    assert(argc==2);const char*mode=argv[1];CPUState cpu{};cpu.pc=0x80020000;
    if(!std::strcmp(mode,"wrong-id")){assert(!n2o_replay_segment(&cpu,cpu.pc));assert(native_calls==0);std::puts("TOOLS_SMOKE_PASS");return 0;}
    const bool collect=!std::strcmp(mode,"collect");
    const bool preblocked=!std::strcmp(mode,"preblocked");
    inject_failure=collect || !std::strcmp(mode,"failfast");
    exhaust_budget=!std::strcmp(mode,"budget");
    const int handled=__wrap_psx_overlay_dispatch(&cpu,0x80020000);
    if(collect || preblocked){
        const unsigned expected_calls=collect?1:0;
        assert(!handled && native_calls==expected_calls && cpu.pc==0x80020000 && cpu.gpr[2]==0);
        assert(!ram_image[17] && !scratch_image[7] && !g_psx_icache_tv[0] && !delay.val && !g_psx_call_bail && !g_debug_last_store_pc);
        assert(!__wrap_psx_overlay_dispatch(&cpu,0x80020004) && native_calls==expected_calls);
    }else assert(handled);
    if(std::strcmp(mode,"legacy")){
        if(!collect && !preblocked){cpu={};assert(__wrap_psx_overlay_dispatch(&cpu,0x80020004));}
        resident_image=2;cpu={};assert(__wrap_psx_overlay_dispatch(&cpu,0x80020000));
        cpu={};assert(__wrap_psx_overlay_dispatch(&cpu,0x80020004));
        assert(cpu.gpr[2]==22);
    }
    if(!std::strcmp(mode,"trace")){assert(!__wrap_psx_overlay_dispatch(&cpu,0x80020080));assert(!__wrap_psx_overlay_dispatch(&cpu,0x80020080));}
    std::puts("TOOLS_SMOKE_PASS");return 0;
}
