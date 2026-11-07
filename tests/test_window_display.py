"""Original regression fixtures for complete UI phrases, popups and pixel roles."""
from pathlib import Path
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]

class WindowDisplayTests(unittest.TestCase):
    def compile_run(self, source, policy=False):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'fixture.cpp').write_text(source)
            args=['c++','-std=c++17','-I',str(ROOT/'compat'),str(p/'fixture.cpp')]
            if policy:args.append(str(ROOT/'compat/window_display.cpp'))
            r=subprocess.run(args+['-o',str(p/'fixture')],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            r=subprocess.run([str(p/'fixture')],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    @unittest.skipUnless(shutil.which('c++'), 'C++ compiler required for geometry fixture')
    def test_fractional_sizes_and_anchored_widgets(self):
        self.compile_run(r'''
#include "window_display.h"
#include <cassert>
#include <cmath>
#include <initializer_list>
bool near(float a,float b){return std::fabs(a-b)<.001f;}
int main(){
 assert(nitrogen_window_projection_is_ui(40*65536,199*65536,320));
 assert(!nitrogen_window_projection_is_ui(184*65536,130*65536,320));
 assert(!nitrogen_window_projection_is_ui(184*65536,120*65536,320));
 nitrogen_window_menu_page(8);
 assert(nitrogen_window_projection_is_ui(184*65536,120*65536,320));
 assert(!nitrogen_window_projection_is_ui(184*65536,130*65536,320));
 nitrogen_window_menu_page(1);
 assert(!nitrogen_window_projection_is_ui(184*65536,120*65536,320));
 nitrogen_window_frame(20);nitrogen_window_menu_page(8);
 nitrogen_window_frame(21);assert(nitrogen_window_controls_view());
 nitrogen_window_frame(22);assert(!nitrogen_window_controls_view());
 nitrogen_window_frame(19);assert(!nitrogen_window_controls_view());
 nitrogen_window_frame(30);nitrogen_window_menu_page(19);assert(nitrogen_window_audio_view());
 nitrogen_window_frame(31);assert(nitrogen_window_audio_view());
 nitrogen_window_frame(32);assert(!nitrogen_window_audio_view());
 nitrogen_window_menu_page(1);assert(!nitrogen_window_audio_view());
 assert(nitrogen_window_close_hold(0,0)==256);
 assert(nitrogen_window_close_hold(1,10)==255);
 assert(nitrogen_window_close_hold(1,10.5)==127);
 assert(nitrogen_window_close_hold(1,11)==0);
 assert(nitrogen_window_close_hold(1,11.999)==0);assert(!nitrogen_window_take_close());
 assert(nitrogen_window_close_hold(0,12)==256);assert(!nitrogen_window_take_close());
 assert(nitrogen_window_close_hold(1,20)==255);assert(!nitrogen_window_take_close());
 assert(nitrogen_window_close_hold(1,22)==0);assert(nitrogen_window_take_close());
 assert(!nitrogen_window_take_close());nitrogen_window_close_hold(1,24);assert(!nitrogen_window_take_close());
 nitrogen_window_close_hold(0,25);assert(nitrogen_window_close_hold(1,30)==255);
 nitrogen_window_frame(40);assert(nitrogen_window_close_hold(1,40)==255);assert(!nitrogen_window_take_close());
 assert(nitrogen_window_ui_step(320,240)==2);
 assert(nitrogen_window_ui_step(800,600)==2);
 assert(nitrogen_window_ui_step(1094,720)==2);
 assert(nitrogen_window_ui_step(1095,720)==3);
 for(int step:{2,3,4,6}){
  nitrogen_window_ui_scale(step);
  assert(nitrogen_window_ui_step(730,480)==step);
  assert(nitrogen_window_ui_step(2560,1440)==step);
  nitrogen_window_ui_scale(1); // an invalid manual value cannot shrink text
  assert(nitrogen_window_ui_step(730,480)==step);
 }
 nitrogen_window_ui_scale(0);
 int rw=0,rh=0;
 nitrogen_window_world_raster(1280,720,364,238,50);
 nitrogen_window_world_size(&rw,&rh);
 assert(std::abs(rw*364.f/1024-640)<1);
 assert(std::abs(rh*238.f/512-360)<1);
 assert(nitrogen_window_ui_step(1280,720)==3); // world percentage cannot change HUD scale
 nitrogen_window_world_raster(1280,720,320,240,50);
 nitrogen_window_world_size(&rw,&rh);
 assert(rw==0&&rh==0); // original movie/image modes keep their presentation
 for(int dw:{600,801,1280,2048})for(int dh:{480,675,720,1000})for(int sh:{236,238,240}){
  nitrogen_window_publish(dw,dh);int step=nitrogen_window_ui_step(dw,dh);
  int vw=(long long)dw*3<(long long)dh*4?dh*4/3:dw;
  unsigned flags=0x10u|(sh<<8);float x=184,y=120,x1=194,y1=130;
  nitrogen_window_ui_vertex(&x,&y,flags,0,0,240,0,0);
  nitrogen_window_ui_vertex(&x1,&y1,flags,0,0,240,0,0);
  assert(near((x1-x)*vw/364,10.f*step));
  assert(near((y1-y)*dh/sh,10.f*step));
  assert(near(x*vw/364+(dw-vw)/2,float(dw/2))&&near(y*dh/sh,float(dh/2)));
  // Two halves of the attract prompt retain their authored gap around centre.
  float a=167,b=187,ay=208,by=208;
  nitrogen_window_ui_vertex(&a,&ay,flags,0,0,240,0,0);
  nitrogen_window_ui_vertex(&b,&by,flags,0,0,240,0,0);
  assert(near((b-a)*vw/364,20.f*step)&&near(ay,by));
  float wx=12,wy=34;nitrogen_window_ui_vertex(&wx,&wy,0,0,0,240,0,0);
  assert(wx==12&&wy==34);
 }
 nitrogen_window_publish(1280,720);float x=0,y=496;
 nitrogen_window_ui_vertex(&x,&y,0x10u|(3<<5)|(238<<8),0,256,240,0,0);
 assert(near(x,0)&&near(y,494));
}
''',True)

    @unittest.skipUnless(shutil.which('c++'), 'C++ compiler required for packet fixture')
    def test_complete_font_atlas_and_world_sprite_exclusion(self):
        self.compile_run(r'''
#include <cstddef>
#include <cstdint>
#include <cassert>
#include <initializer_list>
struct GpuDisplayInfo{unsigned width=364,height=238;};
static unsigned source_height=238;
static void gpu_get_display_info(GpuDisplayInfo*p){p->width=364;p->height=source_height;}
struct WsUiPrepassItem{int full_draw_area=1;unsigned op=0x66;};
static uint32_t gp0_cmd_buf[12];static uint16_t gp0_ot_rank=440;
static int ws_auto_ui_squash,gp0_state,draw_offset_x,draw_offset_y;
static bool controls_view,audio_view;
int nitrogen_window_audio_view(){return audio_view;}
int nitrogen_window_controls_view(){return controls_view;}
enum{GP0_POLYLINE_MONO=4,GP0_POLYLINE_SHADED=5};
static WsUiPrepassItem item;
static const WsUiPrepassItem*ws_auto_ui_item(){return &item;}
static int ws_ui_untextured_op(unsigned op){return op==0x28||op==0x60;}
static unsigned current_texpage(){return 0x13c;}
static void parse_vertex(uint32_t p,int32_t*x,int32_t*y){*x=(int16_t)p;*y=(int16_t)(p>>16);}
#include "window_gpu.inc"
unsigned role(){unsigned f=nitrogen_gpu_ui_flags();assert(f&0x10);return(f>>5)&7;}
void sprite(int x,int y,unsigned palette){gp0_cmd_buf[0]=0x64000000u;gp0_cmd_buf[1]=(uint32_t(y)<<16)|(uint16_t)x;gp0_cmd_buf[2]=(palette<<16)|0x3000u;gp0_cmd_buf[3]=(15u<<16)|8u;}
void digits(int x,int y,bool small=false){sprite(x,y,0x4873);gp0_cmd_buf[2]=(0x4873u<<16)|(small ? 0x5840u : 0x2000u);gp0_cmd_buf[3]=small ? (8u<<16)|6u : (16u<<16)|8u;}
int main(){
 // A menu phrase crossing the old score-region and centre boundary stays whole.
 for(int x:{71,80,93,102,181,199,291}){sprite(x,40,0x4873);gp0_cmd_buf[0]=0x66000000u;assert(role()==0);}
 gp0_ot_rank=877;
 for(int x:{127,157,167,187,193,234}){sprite(x,208,0x4873);gp0_cmd_buf[0]=0x66000000u;assert(role()==0);}
 gp0_ot_rank=440;digits(24,16);assert(role()==1);
 digits(191,12,true);assert(role()==2);
 sprite(95,23,0x4873);gp0_cmd_buf[2]=0x48733d78u;gp0_cmd_buf[3]=(8u<<16)|7u;assert(role()==1);
 sprite(97,25,0x4873);gp0_cmd_buf[2]=0x48733d78u;gp0_cmd_buf[3]=(8u<<16)|7u;assert(role()==1);
 // Every star, including those beyond the old x=128 split, stays at left.
 for(int x:{87,95,103,111,119,127,135,143,151,159,167,175}){
  sprite(x,23,0x4873);gp0_cmd_buf[2]=0x48733d78u;
  gp0_cmd_buf[3]=(8u<<16)|7u;assert(role()==1);
 }
 // Bonus LCD frame and all ten digit cells follow the weapon panel.
 for(unsigned u=196;u<=232;u+=4){
  sprite(44,197,0x5eb7);gp0_cmd_buf[2]=(0x5eb7u<<16)|(55u<<8)|u;
  gp0_cmd_buf[3]=(7u<<16)|4u;assert(role()==3);
 }
 sprite(22,184,0x5fb7);gp0_cmd_buf[2]=0x5fb700e0u;
 gp0_cmd_buf[3]=(32u<<16)|32u;assert(role()==3);
 sprite(200,100,0x5fb7);gp0_cmd_buf[2]=0x5fb700e0u;
 gp0_cmd_buf[3]=(32u<<16)|32u;assert(role()==0);
 // Opaque title/button glyphs and pause-menu shadows are complete centre UI.
 for(int y:{20,58,60,61,160,162})for(int x:{145,155,160,183,202}){
  sprite(x,y,0x4873);assert(role()==0);
 }
 // The complete pulsing rings share footer anchors above and below y=200.
 for(int y:{176,198,212,244}){
  sprite(32,y,0);assert(role()==3);sprite(317,y,0);assert(role()==4);
 }
 // Selected menu gradient quads are UI even outside the prepass's HUD rank.
 gp0_ot_rank=3;gp0_cmd_buf[0]=0x3a000000u;gp0_cmd_buf[2]=0;
 for(int i:{1,3,5,7})gp0_cmd_buf[i]=(180u<<16)|188u;
 assert(role()==0);
 gp0_ot_rank=22;assert(nitrogen_gpu_ui_flags()==0);
 gp0_ot_rank=440;
 sprite(115,21,0x4d33);assert(role()==2);
 sprite(32,205,0x4db3);assert(role()==3);
 sprite(317,205,0x4d73);assert(role()==4);
 // Password label, shadows and all eight symbols sit just above the footer.
 // The first letters and final symbols must not choose either screen edge.
 for(int y:{202,203,204})for(int x:{95,97,103,105,113,115,122,124,135,137,146,162,178,194,210,226,242,258,259}){
  sprite(x,y,0x4873);assert(role()==0);
  gp0_cmd_buf[0]=0x66000000u;assert(role()==0);
 }
 sprite(50,208,0x4873);assert(role()==3);
 sprite(286,208,0x4873);assert(role()==4);
 // Audio's two-line track value has no right footer. Both shadow and
 // foreground stay together even where the actual "remix" crosses x=244.
 audio_view=true;
 for(int y:{205,206,208,214})for(int x:{235,243,244,250,268,290})for(unsigned p:{0x4873u,0x4d73u,0x4db3u}){
  sprite(x,y,p);assert(role()==0);
 }
 sprite(32,205,0x4db3);assert(role()==3); // Audio Back stays bottom left
 audio_view=false;
 sprite(286,208,0x4873);assert(role()==4); // other screens keep right footer
 sprite(8,162,0x7a27);assert(role()==3);
 for(int y:{162,178,188,200,214}){sprite(19,y,0x7667);assert(role()==3);}
 sprite(100,100,0x7667);assert(nitrogen_gpu_ui_flags()==0);
 gp0_state=GP0_POLYLINE_SHADED;
 gp0_cmd_buf[0]=0xe100023cu; // stale preceding packet, not the line header
 assert(((nitrogen_gpu_line_flags(22,200,31,219)>>5)&7)==3);
 assert(nitrogen_gpu_line_flags(112,200,113,219)==0);
 gp0_ot_rank=397;assert(nitrogen_gpu_line_flags(22,200,31,219)==0);
 gp0_ot_rank=440;gp0_state=GP0_POLYLINE_MONO;
 assert(nitrogen_gpu_line_flags(22,200,31,219)==0);
 gp0_state=0;
 for(unsigned p:{0x7a64u,0x7ba4u,0x4ba1u,0x73b2u,0x73f2u}){sprite(60,201,p);assert(role()==3);}
 // Actual shield/firewall icon palettes differ from the button outlines.
 for(unsigned palette:{0x73b2u,0x73f2u}){
  sprite(60,201,palette);assert(role()==3);
  gp0_ot_rank=22;assert(nitrogen_gpu_ui_flags()==0);gp0_ot_rank=440;
 }
 // Every weapon-upgrade flash palette stays with its HUD frame.
 for(unsigned palette:{0x48b3u,0x4a73u,0x4b73u,0x4cb3u}){
  sprite(16,177,palette);assert(role()==3);
 }
 // The multiplier is not a pause-menu word, despite sharing its font.
 sprite(30,203,0x4873);gp0_cmd_buf[2]=0x48738076u;assert(role()==3);
 sprite(39,203,0x4873);gp0_cmd_buf[2]=0x48739050u;assert(role()==3);
 sprite(100,100,0x4cf3);assert(nitrogen_gpu_ui_flags()==0); // lens flare
 sprite(100,100,0x5da3);assert(nitrogen_gpu_ui_flags()==0); // world sprite
 gp0_ot_rank=438;sprite(100,100,0x5ff7);assert(role()==0); // name-entry art
 gp0_ot_rank=441;sprite(72,28,0x73b3);assert(role()==0);
 source_height=240;assert((nitrogen_gpu_ui_flags()>>8)==240);
 gp0_cmd_buf[0]=0x3a000000u;
 for(int i:{1,3,5,7})gp0_cmd_buf[i]=(115u<<16)|64u;
 assert(role()==0); // popup panel uses the same pivot as its text/icons
 gp0_cmd_buf[0]=0x62000000u;assert(role()==0); // translucent popup fill
 // Help bevels extend beyond the inner text and use the same centre transform.
 gp0_cmd_buf[0]=0x3a404040u;
 for(int i:{1,3,5,7})gp0_cmd_buf[i]=(179u<<16)|335u;
 assert(role()==0);
 for(unsigned uv:{0xba64u,0xba72u,0xba80u,0xba8eu}){
  sprite(92,62,0x5765);gp0_cmd_buf[2]=(0x5765u<<16)|uv;
  gp0_cmd_buf[3]=0x000e000eu;assert(role()==0); // four imported help arrows
 }
 // The title's segmented preview frame shares help's draw rank. It remains
 // perspective geometry, including segments inside the card's screen bounds.
 for(int y:{24,72,120,168}){
  gp0_cmd_buf[0]=0x2c574040u;gp0_cmd_buf[2]=0;
  gp0_cmd_buf[1]=(uint32_t(y)<<16)|40u;
  gp0_cmd_buf[3]=(uint32_t(y+24)<<16)|40u;
  gp0_cmd_buf[5]=(uint32_t(y+16)<<16)|67u;
  gp0_cmd_buf[7]=(uint32_t(y+36)<<16)|67u;
  assert(nitrogen_gpu_ui_flags()==0);
 }
 sprite(92,62,0x5765);gp0_cmd_buf[3]=0x000e000eu;
 assert(nitrogen_gpu_ui_flags()==0); // unrelated atlas cell is not a help arrow
 gp0_ot_rank=439;gp0_cmd_buf[0]=0x3a404040u;
 for(int i:{1,3,5,7})gp0_cmd_buf[i]=(118u<<16)|244u;
 assert(role()==0); // native/new Audio gradient and tick track stay aligned
 gp0_ot_rank=440;sprite(136,192,0x5765);gp0_cmd_buf[2]=0x5765ba64u;
 gp0_cmd_buf[3]=0x000e000eu;assert(role()==0); // Video help-atlas hint
 gp0_ot_rank=441;
 assert(nitrogen_gpu_line_flags(64,20,304,20)&0x10);
 assert(nitrogen_gpu_line_flags(0,-40,368,180)&0x10); // complete popup border
 gp0_state=GP0_POLYLINE_SHADED;assert(nitrogen_gpu_ui_flags()==0);
 gp0_ot_rank=427;draw_offset_y=256;
 assert(nitrogen_gpu_line_flags(30,456,50,466)&0x10);
 assert(nitrogen_gpu_line_flags(30,456,150,466)==0);
 controls_view=true;draw_offset_y=0;gp0_state=0;
 gp0_ot_rank=400;gp0_cmd_buf[0]=0x38000000u;assert(role()==0);
 gp0_ot_rank=427;gp0_cmd_buf[0]=0x38000000u;assert(role()==0);
 gp0_ot_rank=440;digits(24,16);assert(role()==0); // not a gameplay score
 gp0_cmd_buf[0]=0x62808080u;gp0_cmd_buf[1]=(150u<<16)|177u;assert(role()==0); // flat callout backing
 sprite(130,150,0x5fe3);assert(role()==0); // controller callout art
 sprite(32,205,0x4db3);assert(role()==3);sprite(317,205,0x4d73);assert(role()==4);
 assert((nitrogen_gpu_line_flags(30,80,150,120)&0x10)!=0);
 controls_view=false;assert(nitrogen_gpu_line_flags(30,80,150,120)==0);
}
''')

    def test_adapter_rejects_changed_contract(self):
        spec=importlib.util.spec_from_file_location('window_adapter',ROOT/'tools/adapt_window_display.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with self.assertRaises(ValueError):module.adapt_gpu('/* incompatible pinned GPU */')
        with self.assertRaises(ValueError):module.adapt_renderer('/* incompatible pinned renderer */')

if __name__=='__main__':unittest.main()
