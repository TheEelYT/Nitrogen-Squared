/* Synthetic codec/audio checks; never reads game data. */
#include "media.h"
#include "movie_player.h"
#include "mdec.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <stdexcept>
namespace {
void check(bool value, const char *message) {
    if (!value) { std::fprintf(stderr,"Media smoke failed: %s (%s)\n",message,SDL_GetError()); std::exit(1); }
}
nitrogen::media::Packet grey(unsigned version) {
    nitrogen::media::Packet p; p.width=p.height=16; p.bytes={0,0,0,0x38,1,0,(uint8_t)version,0};
    std::vector<unsigned> bits;
    auto put=[&](unsigned value,unsigned count){for(unsigned i=count;i>0;--i)bits.push_back(value>>(i-1)&1);};
    for(unsigned block=0;block<6;block++) {
        if(version==2)put(0,10);else if(block<2)put(0,2);else put(4,3);
        put(2,2);
    }
    while(bits.size()%16)bits.push_back(0);
    for(size_t i=0;i<bits.size();i+=16){unsigned word=0;for(unsigned b=0;b<16;b++)word=word<<1|bits[i+b];p.bytes.push_back((uint8_t)word);p.bytes.push_back((uint8_t)(word>>8));}
    return p;
}
}
void nitrogen_media_smoke() {
    using namespace nitrogen::media;
    const auto guest_decodes=mdec_get_decode_count();
    {
        VideoDecoder decoder;
        for(unsigned v:{2u,3u}) {
            auto f=decoder.decode(grey(v));
            check(f.argb.size()==256&&std::all_of(f.argb.begin(),f.argb.end(),[](uint32_t p){return p==0xff808080u;}),"STR v2/v3 neutral frame");
        }
        for(unsigned failure=0;failure<3;failure++) {
            auto p=grey(2);if(failure==0){p.bytes.pop_back();p.bytes.pop_back();}else if(failure==1)p.bytes[6]=42;else p.width=10000;
            bool rejected=false;try{decoder.decode(p);}catch(const std::runtime_error&){rejected=true;}check(rejected,"reject malformed packet");
        }
    }
    check(mdec_get_decode_count()==guest_decodes,"isolate guest decoder state");
    uint8_t sector[2352]{};sector[18]=4;sector[19]=1;XaDecoder xa;
    auto samples=xa.decode(sector,sizeof(sector));
    check(samples.size()==4032&&std::all_of(samples.begin(),samples.end(),[](int16_t s){return s==0;}),"XA silence");
    for(unsigned g=0;g<18;g++)for(unsigned i=16;i<128;i++)sector[24+g*128+i]=0xf1;
    samples=xa.decode(sector,sizeof(sector));check(samples[0]==4096&&samples[1]==-4096,"independent stereo XA channels");
    bool rejected=false;try{xa.decode(sector,sizeof(sector)-1);}catch(const std::runtime_error&){rejected=true;}check(rejected,"reject short XA");
    std::vector<uint8_t> transport(2352*3,0);auto packet=grey(2);
    auto put16=[](uint8_t*p,unsigned v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);};
    auto put32=[&](uint8_t*p,unsigned v){put16(p,v);put16(p+2,v>>16);};
    for(unsigned i=0;i<3;i++) {
        auto*p=transport.data()+i*2352;p[15]=2;p[16]=1;p[17]=i?3:1;p[18]=i?8:0x64;p[19]=i?0:1;std::copy(p+16,p+20,p+20);
        if(i){put32(p+24,0x80010160);put16(p+28,i-1);put16(p+30,2);put32(p+32,1);put32(p+36,(unsigned)packet.bytes.size());put16(p+40,16);put16(p+42,16);if(i==1)std::copy(packet.bytes.begin(),packet.bytes.end(),p+56);}
    }
    struct Temporary{std::filesystem::path path;~Temporary(){std::error_code ec;std::filesystem::remove(path,ec);}}temp{std::filesystem::temp_directory_path()/("nitrogen-media-"+std::to_string(SDL_GetTicksNS())+".bin")};
    auto write=[&]{std::ofstream out(temp.path,std::ios::binary);out.write((char*)transport.data(),(std::streamsize)transport.size());};
    write();auto assembled=read_clip(temp.path.string(),0,3);
    check(assembled.video.size()==1&&assembled.video[0].bytes==packet.bytes&&assembled.audio.size()==4032,"transport assembly and padding-only chunk");
    transport[2352*2+28]=0;write();rejected=false;try{read_clip(temp.path.string(),0,3);}catch(const std::runtime_error&){rejected=true;}check(rejected,"duplicate chunk");
    Clip clip;clip.sample_rate=37800;clip.duration=.5;clip.audio.resize(37800,0);
    {
        AudioPlayer player(clip);player.set_paused(false);
        SDL_Delay(180); // No video, event pumping or guest simulation.
        check(player.submitted()>3000&&player.clock()>.08,"audio advances through main-thread stall");
        player.set_paused(true);const auto count=player.submitted();const double at=player.clock();SDL_Delay(60);
        check(player.submitted()==count&&std::abs(player.clock()-at)<.001,"pause media clock");
        player.set_paused(false);SDL_Delay(80);check(player.clock()>at+.025&&player.clock()<at+.2,"resume without time jump");
    }
    std::puts("Runtime media smoke passed: STR v2/v3, isolated DSP, XA stereo, transport bounds, independent audio, pause/resume");
}
