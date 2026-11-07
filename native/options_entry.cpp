/* Original menu enhancements; fonts and artwork stay in the user's import. */
#include "options_contract.h"
#include NITROGEN_OPTIONS_BINDING_HEADER
#include "../compat/nitrogen_options.h"
#include "../compat/window_display.h"
#include "cpu_state.h"
#include "func_override.h"
#include "mod_plugins.h"
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstring>
#include <chrono>

extern "C" uint8_t *g_psx_ram;
namespace nitrogen::options {
namespace {
constexpr uint32_t page = 0x80090624, next_page = page+4, old_page = page+8, fade = page+12;
constexpr uint32_t audio_selection = 0x80090b60;
uint32_t arena; // immutable address; every mutable cursor lives in guest memory
bool resident(const Function &f)
{
    const uint32_t physical = f.address & 0x1fffffff;
    if (!f.size || f.size>0x200000 || physical > 0x200000-f.size) return false;
    uint64_t h = 14695981039346656037ull;
    for (uint32_t i=0; i<f.size; ++i) { h ^= g_psx_ram[physical+i]; h *= 1099511628211ull; }
    return h == f.hash;
}
void string(CPUState *c, uint32_t p, const char *s)
{
    do { c->write_byte(p++, static_cast<uint8_t>(*s)); } while (*s++);
}
bool storage(CPUState *c)
{
    if (!arena) arena = psx_mod_alloc_guest_memory(4096, 16);
    if (!arena) return false;
    if (c->read_word(arena) != 0x4e324f50u) {
        for (unsigned i=0;i<4096;i+=4) c->write_word(arena+i,0);
        c->write_word(arena,0x4e324f50u);
        const char *labels[]{"video","audio","extras","controls"};
        for (unsigned i=0;i<4;++i) string(c,arena+64+i*32,labels[i]);
    }
    return true;
}
void labels(CPUState *c)
{
    for (auto field : {0x80090600u,0x8008ec94u}) c->write_word(field,arena+64);
    // 8ea08 is the presenter's current-title cache, not a language binding.
    // Leave it owned by the original header routine so its width can settle.
    for (auto field : {0x80090608u,0x8008eca8u}) c->write_word(field,arena+96);
    c->write_word(0x80090610,arena+128);
    c->write_word(0x8008ecac,arena+128);
    c->write_word(0x80090618,arena+160);
}
uint32_t call(CPUState *c,uint32_t function,uint32_t a,uint32_t b,uint32_t d,uint32_t e,uint32_t fifth=0)
{
    c->gpr[4]=a; c->gpr[5]=b; c->gpr[6]=d; c->gpr[7]=e;
    c->write_word(c->gpr[29]+16,fifth);
    func_override_guest_call(c,function,binding.presentation.address);
    return c->gpr[2];
}
uint32_t text(CPUState *c,uint32_t packet,uint32_t view,const char *s,int y,int x,bool selected=false,unsigned opacity=0)
{
    const uint32_t style=arena+224, buffer=arena+256;
    string(c,buffer,s);
    if (x==-10000) x=-40-static_cast<int>(call(c,0x800280a0,buffer,0,0,0))/2;
    c->write_word(style,y); c->write_word(style+4,x);
    c->write_word(style+8,selected?0x202030:0x101010);
    c->write_word(style+12,selected?0xe0e0ff:0x606060);
    return call(c,0x80062a28,buffer,packet,view+0x78,(opacity>>3)|(selected?0x8000u:0),style);
}
// The same tick cell used by the original Audio sliders, with a fresh
// parameterized packet builder. No texture pixels or font data are bundled.
uint32_t slider(CPUState *c,uint32_t packet,uint32_t view,int y,int value,int maximum,int x=152)
{
    uint32_t head=c->read_word(view+0x7c);
    for (int i=0;i<32;++i) {
        c->write_word(packet,(4u<<24)|(head&0xffffffu));
        c->write_word(packet+4,0x66805c44u);
        c->write_word(packet+8,static_cast<uint16_t>(x+i*6)|(static_cast<uint32_t>(y)<<16));
        c->write_word(packet+12,0x47adf0f8u);
        c->write_word(packet+16,(12u<<16)|5u);
        head=packet&0xffffffu; packet+=20;
    }
    // Match the original Audio fill: two additive Gouraud halves behind the
    // fixed tick track, rather than changing the tick texture's modulation.
    const int ticks=std::clamp((value*32+maximum/2)/maximum,0,32);
    if(ticks) for(int edge : {-5,5}) {
        const int left=x+2,right=x+ticks*6-4,mid=y+6;
        const auto xy=[](int px,int py){return static_cast<uint16_t>(px)|(static_cast<uint32_t>(py)<<16);};
        c->write_word(packet,(8u<<24)|(head&0xffffffu));
        c->write_word(packet+4,0x3a404040u); c->write_word(packet+8,xy(left,mid));
        c->write_word(packet+12,0x00ffffffu); c->write_word(packet+16,xy(right,mid));
        c->write_word(packet+20,0x00890000u); c->write_word(packet+24,xy(left,mid+edge));
        c->write_word(packet+28,0); c->write_word(packet+32,xy(right,mid+edge));
        head=packet&0xffffffu; packet+=36;
    }
    c->write_word(packet,(1u<<24)|(head&0xffffffu));
    c->write_word(packet+4,0xe100023bu);
    head=packet&0xffffffu; packet+=8;
    c->write_word(view+0x7c,head);
    return packet;
}
uint32_t arrow_hint(CPUState *c,uint32_t packet,uint32_t view)
{
    const uint32_t buffer=arena+256;
    string(c,buffer,"to change");
    const int width=static_cast<int>(call(c,0x800280a0,buffer,0,0,0));
    const int left=(368-(36+width))/2;
    packet=text(c,packet,view,"to change",192,left+36+width/2-184);
    uint32_t head=c->read_word(view+0x78);
    // Original help-atlas left/right cells, from the player's imported art.
    for(int i=0;i<2;++i) {
        c->write_word(packet,(4u<<24)|(head&0xffffffu));
        c->write_word(packet+4,0x64808080u);
        c->write_word(packet+8,static_cast<uint16_t>(left+i*18)|(192u<<16));
        c->write_word(packet+12,(0x5765u<<16)|(186u<<8)|(100u+i*14u));
        c->write_word(packet+16,(14u<<16)|14u);
        head=packet&0xffffffu; packet+=20;
    }
    c->write_word(packet,(1u<<24)|(head&0xffffffu));
    c->write_word(packet+4,0xe1000219u);
    c->write_word(view+0x78,packet&0xffffffu);
    return packet+8;
}
// Move complete original Audio primitives, not individual glyph vertices.
// First validate the private DMA span, then edit positions in a second pass.
bool audio_rows(CPUState *c,uint32_t begin,uint32_t end,bool apply)
{
    begin&=0x1fffffu; end&=0x1fffffu;
    if((begin|end)&3u || end<begin || end-begin>65536u) return false;
    for(uint32_t p=begin;p<end;) {
        const unsigned count=c->read_word(p)>>24;
        if(p+4u*(count+1)>end) return false;
        for(unsigned i=0;i<count;) {
            const uint32_t command=p+4+4*i;
            const unsigned op=c->read_word(command)>>24;
            unsigned words=1,n=0,stride=1;
            if(op>=0x20 && op<=0x3f) {
                n=(op&8)?4:3; stride=1+!!(op&4)+!!(op&16);
                words=1+n+((op&4)?n:0)+((op&16)?n-1:0);
            } else if(op>=0x60 && op<=0x7f) {
                n=1; words=2+!!(op&4)+((op&0x18)?0:1);
            } else if(op>=0x40 && op<=0x5f) {
                stride=(op&16)?2:1; n=2; words=3+!!(op&16);
                if(op&8) {
                    words=0;
                    for(unsigned k=1;k<count-i;++k)
                        if((c->read_word(command+4*k)&0xf000f000u)==0x50005000u) {words=k+1;break;}
                    if(!words) return false;
                    n=(op&16)?(words-1)/2:words-2;
                }
            } else if(op==2) words=3;
            else if(op==0x80) words=4;
            else if(op!=0 && op!=1 && !(op>=0xe1 && op<=0xe6)) return false;
            if(i+words>count) return false;
            int ylo=32767;
            for(unsigned v=0;v<n;++v) ylo=std::min(ylo,static_cast<int>(static_cast<int16_t>(c->read_word(command+4*(1+v*stride))>>16)));
            if(apply && n && ylo>=100) for(unsigned v=0;v<n;++v) {
                const uint32_t at=command+4*(1+v*stride),xy=c->read_word(at);
                const int y=static_cast<int16_t>(xy>>16)+20;
                c->write_word(at,(xy&65535u)|(static_cast<uint32_t>(static_cast<uint16_t>(y))<<16));
            }
            i+=words;
        }
        p+=4u*(count+1);
    }
    return true;
}
void audio_down_arrow(CPUState *c,uint32_t view)
{
    uint32_t head=c->read_word(view+0x78)&0xffffffu;
    for(unsigned i=0;i<4096 && head<0x200000u-20 && !(head&3u);++i) {
        const uint32_t tag=c->read_word(head);
        if((tag>>24)==4 && (c->read_word(head+4)>>24)==0x64 &&
           c->read_word(head+12)==0x73f342b0u && c->read_word(head+16)==0x000b0011u) {
            const uint32_t xy=c->read_word(head+8);
            if((xy>>16)==194) c->write_word(head+8,(xy&65535u)|(214u<<16));
        }
        const uint32_t next=tag&0xffffffu;
        if(next==head) break;
        head=next;
    }
}
void sound(CPUState *c) { (void)call(c,0x8004c4e0,0x2c,0,0,0); }
void center(CPUState *c,uint32_t context)
{
    c->write_word(0x800908d8,0); c->write_word(0x800908dc,0);
    for (unsigned offset : {0x16050u,0x16052u,0x16e8cu,0x16e8eu}) c->write_half(context+offset,0);
}
int slider_direction(CPUState *c,uint32_t buttons,uint32_t edge,uint32_t counter)
{
    const uint32_t held=buttons&0xa0u;
    if(!held || held==0xa0u) {c->write_word(counter,0);return 0;}
    if(edge&0xa0u) {c->write_word(counter,15);return held==0x20?1:-1;}
    const uint32_t delay=c->read_word(counter);
    c->write_word(counter,delay?delay-1:2);
    return delay?0:held==0x20?1:-1;
}
int presentation(CPUState *c)
{
    if (!resident(binding.presentation) || !storage(c)) return 0;
    const uint32_t context=c->gpr[4],view=c->gpr[5],input_packet=c->gpr[6];
    if ((context&0x1fffffff)>0x200000-0x17000 || (view&0x1fffffff)>0x200000-0x1000) return 0;
    labels(c); center(c,context);
    const uint32_t phase=c->read_word(page);
    const uint32_t effective=(phase==29?c->read_word(old_page):phase==30?c->read_word(next_page):phase);
    nitrogen_window_menu_page(effective);
    const uint32_t buttons=c->read_word(context+0x10);
    const double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
    const unsigned closing=nitrogen_window_close_hold(phase==0 && (buttons&0x1000u),seconds);
    if(effective==0) {
        // Main Back is now a cancellable hold. Keep the original presenter
        // and its guest-timed art/navigation, suppressing only its Back action.
        c->write_word(context+0x10,buttons&~0x1000u);
        func_override_call_original(c);
        c->write_word(context+0x10,buttons);
        if(closing<256) {
            std::array<uint32_t,32> saved{};
            std::copy(c->gpr,c->gpr+32,saved.begin());
            c->gpr[29]-=256;
            const uint32_t packet=text(c,c->gpr[2],view,"closing...",nitrogen_window_close_y(),-10000,true,closing);
            std::copy(saved.begin(),saved.end(),c->gpr);c->gpr[2]=packet;
        }
        return 1;
    }
    if (effective!=9) return 0;
    std::array<uint32_t,32> registers{};
    std::copy(c->gpr,c->gpr+32,registers.begin());
    c->gpr[29]-=512;
    unsigned opacity=0;
    if (phase==29) {
        opacity=std::min(255u,c->read_word(fade)+10);
        c->write_word(fade,opacity);
        if (opacity==255) c->write_word(page,30);
    }
    if (phase==30) {
        opacity=c->read_word(fade);
        opacity=opacity>10?opacity-10:0;
        c->write_word(fade,opacity);
        if (!opacity) c->write_word(page,9);
    }
    c->write_half(context+0x3c2,9);
    const uint32_t edge=buttons&~c->read_word(context+0x14);
    const int first=nitrogen_options_desktop()?0:1;
    int row=std::clamp(static_cast<int>(c->read_word(arena+4)),first,2);
    bool changed=false;
    if (!opacity) {
        if (edge&0x10) { row=row==first?2:row-1; sound(c); }
        if (edge&0x40) { row=row==2?first:row+1; sound(c); }
        const int direction=row==2?slider_direction(c,buttons,edge,arena+8):
            (edge&0x20)?1:(edge&0x80)?-1:0;
        if (direction) {
            if (row==0) changed=nitrogen_option_set(row,(nitrogen_option_get(row)+direction+3)%3)!=0;
            if (row==1) {
                constexpr int steps[]{0,2,3,4,6};
                int index=0; while(index<4 && steps[index]!=nitrogen_option_get(row)) ++index;
                changed=nitrogen_option_set(row,steps[(index+direction+5)%5])!=0;
            }
            if (row==2) changed=nitrogen_option_set(row,std::clamp(nitrogen_option_get(row)+direction*5,25,200))!=0;
            if(changed) sound(c);
        }
        if (edge&0x7000) { // Back or the original footer's Cross/Confirm action
            c->write_word(page,29); c->write_word(next_page,1); c->write_word(old_page,9); c->write_word(fade,0);
            sound(c);
        }
    }
    c->write_word(arena+4,row);
    uint32_t packet=call(c,0x80029744,input_packet,context,view,(opacity<<16)|0x103,3);
    char line[128];
    if (first==0) {
        constexpr const char *modes[]{"windowed","borderless fullscreen","fullscreen"};
        std::snprintf(line,sizeof(line),"video mode - %s",modes[nitrogen_option_get(0)]);
        packet=text(c,packet,view,line,88,0,row==0,opacity);
    }
    const int scale=nitrogen_option_get(1);
    if(scale) std::snprintf(line,sizeof(line),"HUD scale - %dX",scale);
    else std::snprintf(line,sizeof(line),"HUD scale - AUTO");
    packet=text(c,packet,view,line,118,0,row==1,opacity);
    std::snprintf(line,sizeof(line),"render resolution - %d percent",nitrogen_option_get(2));
    packet=text(c,packet,view,line,148,0,row==2,opacity);
    packet=slider(c,packet,view,168,nitrogen_option_get(2),200,88);
    packet=arrow_hint(c,packet,view);
    // The original menu ray field stays guest-timed behind our new controls.
    packet=call(c,0x80061ec0,packet,view+0x750,8,context,9);
    std::copy(registers.begin(),registers.end(),c->gpr); c->gpr[2]=packet;
    return 1; // new product UI; nested original helpers own their guest cycles
}
int audio(CPUState *c)
{
    if (!resident(binding.audio) || !storage(c)) return 0;
    const uint32_t context=c->gpr[4],view=c->gpr[6],opacity=c->gpr[7];
    std::array<uint32_t,32> arguments{};
    std::copy(c->gpr,c->gpr+32,arguments.begin());
    const uint32_t buttons=c->read_word(context+0x10),edge=buttons&~c->read_word(context+0x14);
    int row=std::clamp(static_cast<int>(c->read_word(audio_selection)),0,5);
    if(edge&0x10) {row=(row+5)%6;sound(c);}
    if(edge&0x40) {row=(row+1)%6;sound(c);}
    c->write_word(audio_selection,row==1?5:row>1?row-1:0);
    if(row==1 && !opacity) {
        const int delta=5*slider_direction(c,buttons,edge,arena+12);
        if(delta) {nitrogen_option_set(3,std::clamp(nitrogen_option_get(3)+delta,0,100));sound(c);}
    }
    // Preserve all existing audio behavior, including speaker mode and track
    // selection. Only navigation expands from five to six authored rows.
    c->write_word(context+0x10,buttons&~(row==1?0xf0u:0x50u));
    // Helpers above may clobber argument registers; restore this call's ABI.
    std::copy(arguments.begin(),arguments.end(),c->gpr);
    func_override_call_original(c);
    const uint32_t end=c->gpr[2];
    const bool reflow=audio_rows(c,arguments[5],end,false);
    if(reflow) { (void)audio_rows(c,arguments[5],end,true); audio_down_arrow(c,view); }
    c->write_word(audio_selection,row);
    c->write_word(context+0x10,buttons);
    const uint32_t sp=c->gpr[29]; c->gpr[29]-=256;
    uint32_t packet=text(c,end,view,"master volume",reflow?110:190,-10000,row==1,opacity);
    packet=slider(c,packet,view,reflow?112:192,nitrogen_option_get(3),100);
    c->gpr[29]=sp; c->gpr[2]=packet;
    return 1;
}
struct Install {
    Install() {
        if(!binding.enabled) return;
        const int a=func_override_add_guarded("n2o-game-options",binding.presentation.address,presentation,binding.presentation.guard,4,FO_CREDIT_SELF);
        const int b=func_override_add_guarded("n2o-audio-options",binding.audio.address,audio,binding.audio.guard,4,FO_CREDIT_SELF);
        if(a!=FO_OK || b!=FO_OK) std::fprintf(stderr,"nitrogen: game options binding registration failed (%d,%d)\n",a,b);
    }
} install;
}
}
