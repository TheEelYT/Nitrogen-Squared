"""Original persistence tests: settings survive runtime rebuild locations."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('c++'), 'C++ compiler required')
class GameOptionsTests(unittest.TestCase):
    def test_fixed_fullscreen_platform_keeps_hud_and_volume_options(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            (p/'fixture.cpp').write_text('''
#include "nitrogen_options.h"
#include "window_display.h"
#include <cassert>
int main(int argc,char**argv){
 nitrogen_options_init(argv[1]);
 assert(!nitrogen_options_desktop());
 assert(nitrogen_option_get(NITROGEN_VIDEO_MODE)==NITROGEN_BORDERLESS);
 assert(!nitrogen_option_set(NITROGEN_VIDEO_MODE,NITROGEN_WINDOWED));
 assert(nitrogen_option_set(NITROGEN_HUD_SCALE,3));
 assert(nitrogen_option_set(NITROGEN_MASTER_VOLUME,40));
}
''')
            subprocess.run(['c++','-std=c++17','-D__vita__','-I',str(ROOT/'compat'),
                            str(p/'fixture.cpp'),str(ROOT/'compat/game_options.cpp'),
                            '-o',str(p/'fixture')],check=True)
            subprocess.run([str(p/'fixture'),str(p)+'/'],check=True,
                           env=dict(os.environ,NITROGEN_OPTIONS_FILE=str(p/'nitrogen-options.ini')))

    def test_video_exit_transition_and_audio_wrapper_arguments(self):
        # A synthetic guest exercises the real extension callbacks, including
        # volatile argument clobbers and the exit fade that previously stalled.
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            (p/'cpu_state.h').write_text('''#pragma once
#include <cstdint>
struct CPUState {uint32_t gpr[32]; uint32_t pc; uint32_t(*read_word)(uint32_t);
void(*write_word)(uint32_t,uint32_t); uint16_t(*read_half)(uint32_t);
void(*write_half)(uint32_t,uint16_t); uint8_t(*read_byte)(uint32_t);
void(*write_byte)(uint32_t,uint8_t);};
''')
            (p/'func_override.h').write_text('''#pragma once
#include "cpu_state.h"
#define FO_CREDIT_SELF -1
#define FO_OK 0
using FuncOverrideFn=int(*)(CPUState*);
extern "C" int func_override_add_guarded(const char*,uint32_t,FuncOverrideFn,const uint32_t*,int,int32_t);
extern "C" void func_override_guest_call(CPUState*,uint32_t,uint32_t);
extern "C" void func_override_call_original(CPUState*);
''')
            (p/'mod_plugins.h').write_text('#pragma once\n#include <cstdint>\nextern "C" uint32_t psx_mod_alloc_guest_memory(uint32_t,uint32_t);\n')
            h=14695981039346656037
            for _ in range(4): h=(h*1099511628211)&((1<<64)-1)
            (p/'binding.h').write_text('#include "options_contract.h"\nnamespace nitrogen::options { constexpr Binding binding{true,'
                f'{{0x80000100,4,{h}ull,{{0}}}},{{0x80000200,4,{h}ull,{{0}}}},{{0x80000300,4,{h}ull,{{0}}}},{{0x80000400,4,{h}ull,{{0}}}}'+'};}\n')
            (p/'fixture.cpp').write_text(r'''
#include "cpu_state.h"
#include "func_override.h"
#include "nitrogen_options.h"
#include "window_display.h"
#include <chrono>
#include <cassert>
#include <cstring>
#include <initializer_list>
static uint8_t ram[0x200000];
extern "C" {uint8_t *g_psx_ram=ram;}
static FuncOverrideFn video,audio,title;
static bool font_ready=false,caption=false;
static uint32_t rw(uint32_t a){uint32_t v;std::memcpy(&v,ram+(a&0x1fffff),4);return v;}
static void ww(uint32_t a,uint32_t v){std::memcpy(ram+(a&0x1fffff),&v,4);}
static uint16_t rh(uint32_t a){return uint16_t(rw(a));}
static void wh(uint32_t a,uint16_t v){std::memcpy(ram+(a&0x1fffff),&v,2);}
static uint8_t rb(uint32_t a){return ram[a&0x1fffff];}
static void wb(uint32_t a,uint8_t v){ram[a&0x1fffff]=v;}
extern "C" uint32_t psx_mod_alloc_guest_memory(uint32_t,uint32_t){return 0x801f0000;}
extern "C" int func_override_add_guarded(const char*,uint32_t a,FuncOverrideFn f,const uint32_t*,int,int32_t){
 if(a==0x80000100)video=f;else if(a==0x80000200)audio=f;else title=f;return FO_OK;
}
extern "C" void func_override_guest_call(CPUState*c,uint32_t f,uint32_t){
 if(f==0x80029744)font_ready=true;
 if(f==0x80062a28 && !std::strcmp(reinterpret_cast<const char*>(ram+(c->gpr[4]&0x1fffff)),"closing...")){
  assert(font_ready && c->gpr[7]==0);caption=true; // no ghost transition or selected gradient
  assert(rw(rw(c->gpr[29]+16)+4)==0); // centred, not Audio's right-aligned label
  const uint32_t p=c->gpr[5];
  for(int k:{0,20}){
   ww(p+k,(4u<<24)|0xffffffu);ww(p+k+4,k?0x66202020:0x6470707f);
   ww(p+k+8,0);ww(p+k+12,0x48733000);ww(p+k+16,0x000f0008);
  }
  ww(p+40,(1u<<24)|0xffffffu);ww(p+44,0xe100023c);c->gpr[2]=p+48;return;
 }
 uint32_t packet=f==0x80062a28?c->gpr[5]:c->gpr[4];
 c->gpr[2]=f==0x800280a0?60:packet+32;
 c->pc=0xdeadbeef;
 for(int i=4;i<=7;++i)c->gpr[i]=0xdeadbeef; // caller-saved registers
}
extern "C" void func_override_call_original(CPUState*c){
 if(c->gpr[5]==0x80160000 && c->gpr[6]==0x80132078 && c->gpr[7]==0x8011b160){
  font_ready=true;ww(c->gpr[5]+4,0x66abcdef);c->gpr[2]=c->gpr[5]+32;return;
 }
 if(c->gpr[5]==0x80132000){
  assert(false && "Main presenter must retain its outer frame pump");
 }
 assert(c->gpr[4]==0x8011b160 && c->gpr[5]==0x80160000);
 assert(c->gpr[6]==0x80132000 && c->gpr[7]==0);
 assert(!(rw(0x8011b170)&0x50));
 // Original synthetic Audio packets: a font row and a shaded highlight.
 const uint32_t p=0x80160000;
 ww(p,(4u<<24)|0xffffffu);ww(p+4,0x64808080);ww(p+8,(110u<<16)|80u);
 ww(p+12,0x48733000);ww(p+16,(15u<<16)|8u);
 ww(p+20,(8u<<24)|0xffffffu);ww(p+24,0x3a404040);
 for(int k:{1,3,5,7})ww(p+24+4*k,((k<5?118u:123u)<<16)|154u);
 ww(0x80150000,(4u<<24)|0xffffffu);ww(0x80150004,0x64808080);
 ww(0x80150008,(194u<<16)|124u);ww(0x8015000c,0x73f342b0);ww(0x80150010,0x000b0011);
 ww(0x80132078,0x00150000);
 c->gpr[2]=p+56;
}
int main(){
 assert(video && audio && title);
 CPUState c{};c.read_word=rw;c.write_word=ww;c.read_half=rh;c.write_half=wh;c.read_byte=rb;c.write_byte=wb;
 c.gpr[4]=0x8011b160;c.gpr[5]=0x80132000;c.gpr[6]=0x80160000;c.gpr[29]=0x801ee000;
 ww(0x80090624,0);ww(0x8011b170,0x1000);
 c.pc=0x80000100;
 assert(!video(&c));assert(rw(0x80090624)==0 && rw(0x8011b170)==0x1000); // Main Back unmodified
 assert(c.gpr[6]==0x80160000 && c.gpr[29]==0x801ee000 && c.pc==0x80000100 && !caption);
 auto title_call=[&](){c.gpr[4]=1;c.gpr[5]=0x80160000;c.gpr[6]=0x80132078;c.gpr[7]=0x8011b160;c.gpr[31]=0x80000460;return title(&c);};
 wh(0x8011b160+0x23c,4);
 assert(title_call());assert(caption && c.gpr[2]==0x80160050 && c.gpr[29]==0x801ee000);
 assert(rw(0x80160024)==0x66000000 && rw(0x80160038)==0x66000000);
 assert(rw(0x80160004)==0x66abcdef); // original prompt untouched
 assert(rw(0x8016004c)==0xe100023c);
 nitrogen_window_close_hold(0,0);
 const double now=std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
 nitrogen_window_close_hold(1,now-1.25);
 assert(title_call());
 assert(rw(0x80160024)==0x6670707f && rw(0x80160038)==0x66202020);
 assert(!nitrogen_window_take_close());
 ww(0x8011b170,0);assert(!title_call()); // release hides caption
 ww(0x8011b170,0x1000);wh(0x8011b160+0x23c,0);assert(!title_call()); // no title flag
 wh(0x8011b160+0x23c,4);title_call();c.gpr[31]=0;assert(!title(&c)); // shared helper's other callers
 ram[0x400]=1;assert(!title_call());ram[0x400]=0; // complete caller identity required
 c.gpr[4]=0x8011b160;c.gpr[5]=0x80132000;c.gpr[6]=0x80160000;
 ww(0x80090624,1);ww(0x8011b170,0x1000);assert(!video(&c));
 assert(rw(0x8011b170)==0x1000); // ordinary submenu Back stays original
 ww(0x80090624,9);ww(0x80090628,9);ww(0x8011b170,0x1000);
 ww(0x8008ea08,0x12345678); // original presenter's current-title cache
 assert(video(&c));assert(rw(0x80090624)==29);assert(rw(0x80090628)==1);
 assert(rw(0x8008ea08)==0x12345678);
 assert(c.gpr[4]==0x8011b160 && c.gpr[29]==0x801ee000);
 ww(0x8011b170,0);
 for(int i=0;i<26 && rw(0x80090624)==29;++i)assert(video(&c));
 assert(rw(0x80090624)==30 && rw(0x80090630)==255);
 assert(!video(&c)); // original presenter now owns the return to Game Options
 ww(0x80090624,9);ww(0x80090628,9);ww(0x80090630,0);ww(0x8011b170,0x4000);
 assert(video(&c));assert(rw(0x80090624)==29); // footer Confirm also leaves Video
 c.gpr[4]=0x8011b160;c.gpr[5]=0x80160000;c.gpr[6]=0x80132000;c.gpr[7]=0;
 ww(0x80090b60,0);ww(0x8011b170,0x40);
 assert(audio(&c));assert(rw(0x80090b60)==1);assert(rw(0x8011b170)==0x40);
 assert((rw(0x80160008)>>16)==130); // complete original font row moves down
 assert((rw(0x8016001c)>>16)==138); // both gradient halves use the same shift
 assert((rw(0x80150008)>>16)==214); // arrow clears the last Audio item
 c.gpr[4]=0x8011b160;c.gpr[5]=0x80160000;c.gpr[6]=0x80132000;c.gpr[7]=0;
 ww(0x8011b170,0x80);
 assert(audio(&c));assert(nitrogen_option_get(NITROGEN_MASTER_VOLUME)==95);
}
''')
            subprocess.run(['c++','-std=c++17','-I',str(p),'-I',str(ROOT/'compat'),'-I',str(ROOT/'native'),
                            '-DNITROGEN_OPTIONS_BINDING_HEADER="'+str(p/'binding.h')+'"',
                            str(p/'fixture.cpp'),str(ROOT/'native/options_entry.cpp'),
                            str(ROOT/'compat/game_options.cpp'),str(ROOT/'compat/window_display.cpp'),'-o',str(p/'fixture')],check=True)
            subprocess.run([str(p/'fixture')],check=True)

    def test_load_migration_validation_and_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            (p/'fixture.cpp').write_text(r'''
#include "nitrogen_options.h"
#include <cassert>
#include <cstdlib>
int main(int argc,char**argv){
 nitrogen_options_init(argv[1]);
 assert(nitrogen_options_desktop());
 assert(nitrogen_option_get(NITROGEN_MASTER_VOLUME)==std::atoi(argv[2]));
 if(argc==4){
  assert(nitrogen_option_get(NITROGEN_HUD_SCALE)==0);
  assert(nitrogen_option_get(NITROGEN_RENDER_PERCENT)==100);
  assert(!nitrogen_option_set(NITROGEN_HUD_SCALE,1));
  assert(!nitrogen_option_set(NITROGEN_RENDER_PERCENT,73));
  assert(!nitrogen_option_set(NITROGEN_MASTER_VOLUME,101));
  assert(nitrogen_option_set(NITROGEN_HUD_SCALE,4));
  assert(nitrogen_option_set(NITROGEN_VIDEO_MODE,NITROGEN_FULLSCREEN));
  assert(nitrogen_option_set(NITROGEN_RENDER_PERCENT,75));
  assert(nitrogen_option_set(NITROGEN_MASTER_VOLUME,37));
 }else{
  assert(nitrogen_option_get(NITROGEN_HUD_SCALE)==4);
  assert(nitrogen_option_get(NITROGEN_VIDEO_MODE)==NITROGEN_FULLSCREEN);
  assert(nitrogen_option_get(NITROGEN_RENDER_PERCENT)==75);
 }
}
''')
            subprocess.run(['c++','-std=c++17','-I',str(ROOT/'compat'),str(p/'fixture.cpp'),
                            str(ROOT/'compat/game_options.cpp'),'-o',str(p/'fixture')],check=True)
            config = p/'nitrogen-options.ini'
            base = p/'build-a'
            base.mkdir()
            (base/'nitrogen-menu.ini').write_text('visible 1\nvolume 61\n')
            env = dict(os.environ, NITROGEN_OPTIONS_FILE=str(config))
            subprocess.run([str(p/'fixture'),str(base)+'/', '61','write'],env=env,check=True)
            # A rebuilt runtime has another executable directory. The portable
            # settings path, unlike its old F1 settings, still owns the values.
            other = p/'build-b'; other.mkdir()
            with config.open('a') as f:
                f.write('hud_scale 1\nrender_percent 999\nmaster_volume text\nvideo_mode 0 junk\n')
            subprocess.run([str(p/'fixture'),str(other)+'/', '37'],env=env,check=True)
