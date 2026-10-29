// Original same-build witness replay; no guest instruction words are embedded.
#include "cpu_state.h"
#include "dirty_ram_interp.h"
#include "psx_bios_backend.h"
#include "psx_icache.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
extern "C" {
int __real_main(int,char**);int n2o_replay_segment(CPUState*,uint32_t);
extern uint8_t*g_psx_ram;uint8_t*memory_get_scratchpad_ptr();
void memory_init(const char*);void memory_set_sr_ptr(const uint32_t*);
uint32_t psx_read_word(uint32_t);uint16_t psx_read_half(uint32_t);uint8_t psx_read_byte(uint32_t);
void psx_write_word(uint32_t,uint32_t);void psx_write_half(uint32_t,uint16_t);void psx_write_byte(uint32_t,uint8_t);
}
extern "C" int __wrap_main(int argc,char**argv) {
    if(!std::getenv("N2O_REPLAY"))return __real_main(argc,argv);
    if(argc!=4)return 4;
    psx_bios_activate(psx_bios_bundled());memory_init(argv[2]);
    CPUState witness{};std::vector<uint8_t>image(0x200000);uint8_t scratch[1024];
    FILE*f=std::fopen(argv[1],"rb");if(!f)return 5;
    const bool read=std::fread(&witness,sizeof witness,1,f)==1 && std::fread(image.data(),image.size(),1,f)==1 && std::fread(scratch,1024,1,f)==1;
    const bool ended=std::fgetc(f)==EOF;std::fclose(f);if(!read || !ended)return 6;
    char*end=nullptr;const unsigned long parsed=std::strtoul(argv[3],&end,0);
    if(!end || *end || parsed>0xFFFFFFFFul || parsed<0x80010000ul || parsed>=0x80200000ul || parsed%4)return 4;
    const uint32_t pc=uint32_t(parsed);
    const uint32_t patterns[]={0,1,0xFFFFFFFF,0x7FFF,0x8000,0x7FFFFFFF,0x80000000,0x1000,0xFFFF0000,0x55555555,0xAAAAAAAA,0x00FFFFFF};
    unsigned cases=0;
    for(unsigned variant=0;variant<25;variant++) {
        std::memcpy(g_psx_ram,image.data(),image.size());std::memcpy(memory_get_scratchpad_ptr(),scratch,1024);
        CPUState cpu=witness;cpu.read_word=psx_read_word;cpu.read_half=psx_read_half;cpu.read_byte=psx_read_byte;
        cpu.write_word=psx_write_word;cpu.write_half=psx_write_half;cpu.write_byte=psx_write_byte;
        cpu.muldiv_ts_done=cpu.gte_ts_done=0;memory_set_sr_ptr(&cpu.cop0[12]);dirty_ram_ld_delay_discard();psx_icache_reset();
        if(variant){uint32_t*v=variant<=12?cpu.gte_data:cpu.gte_ctrl;for(unsigned j=0;j<32;j++)v[j]=patterns[(variant-1)%12];}
        overlay_watch_invalidate_after_ram_restore();
        if(!n2o_replay_segment(&cpu,pc)){std::fprintf(stderr,"REPLAY declined %08X\n",pc);return 7;}++cases;
    }
    std::printf("REPLAY_PASS pc=%08X cases=%u\n",pc,cases);return 0;
}
