"""Original geometry checks: fractional resizes, integer boundaries and anchors."""
from pathlib import Path
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]

class WindowDisplayTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('c++'), 'C++ compiler required for geometry fixture')
    def test_fractional_sizes_and_anchored_widgets(self):
        source = r'''
#include "window_display.h"
#include <cassert>
#include <cmath>
bool near(float a, float b) { return std::fabs(a-b) < .001f; }
int main() {
    assert(nitrogen_window_ui_step(320,240)==1);
    assert(nitrogen_window_ui_step(480,360)==1);
    assert(nitrogen_window_ui_step(639,479)==1);
    assert(nitrogen_window_ui_step(640,480)==2);
    assert(nitrogen_window_ui_step(800,600)==2);
    assert(nitrogen_window_ui_step(960,720)==3);
    assert(nitrogen_window_ui_step(1080,1920)==3);
    assert(nitrogen_window_ui_step(0,0)==1);
    for (int width : {320,364}) for (int dh : {240,360,479,480,600,720}) {
        int dw=dh*16/9, step=nitrogen_window_ui_step(dw,dh);
        nitrogen_window_publish(dw,dh);
        unsigned flags=0x10 | (1<<5) | (1<<7) | ((width/4)<<9);
        float x=width/2.f,y=119, x1=x+width/32.f,y1=y+10;
        // A native-wide 16:9 surface; unchanged world geometry must not acquire
        // this transform, while a 10-reference-pixel UI glyph has integer size.
        int wide=width*4/3, off=(wide-width)/2;
        nitrogen_window_ui_vertex(&x,&y,flags,0,0,238,wide,off);
        nitrogen_window_ui_vertex(&x1,&y1,flags,0,0,238,wide,off);
        assert(near((x1-x)*dw/wide,10.f*step));
        assert(near((y1-y)*dh/238,10.f*240/238*step));
        float wx=12,wy=34;
        nitrogen_window_ui_vertex(&wx,&wy,0,0,0,238,wide,off);
        assert(wx==12 && wy==34);
    }
    // A portrait window crops a 4:3 world; text still fits its visible width.
    nitrogen_window_publish(600,800);
    unsigned portrait=0x10 | (1<<5) | (1<<7) | (91<<9);
    float px=182,py=120,px1=182+364.f/32,py1=130;
    nitrogen_window_ui_vertex(&px,&py,portrait,0,0,240,0,0);
    nitrogen_window_ui_vertex(&px1,&py1,portrait,0,0,240,0,0);
    assert(near((px1-px)*1066/364,10));
    assert(near((py1-py)*800/240,10));
    // Right/bottom anchoring stays at the edge across resizes and buffer origins.
    nitrogen_window_publish(1280,720);
    unsigned flags=0x10 | (2<<5) | (2<<7) | (80<<9);
    float x=320, y=256+240;
    nitrogen_window_ui_vertex(&x,&y,flags,0,256,240,426,53);
    assert(near(x,373) && near(y,496));
}
'''
        # Standard initializer lists are explicit for every supported compiler.
        source='#include <initializer_list>\n'+source
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'fixture.cpp').write_text(source)
            r=subprocess.run(['c++','-std=c++17','-I',str(ROOT/'compat'),str(p/'fixture.cpp'),
                              str(ROOT/'compat/window_display.cpp'),'-o',str(p/'fixture')],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            r=subprocess.run([str(p/'fixture')],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    @unittest.skipUnless(shutil.which('c++'), 'C++ compiler required for packet fixture')
    def test_complete_font_atlas_and_world_sprite_exclusion(self):
        source = r'''#include <cstddef>
#include <cstdint>
#include <cassert>
struct WsUiPrepassItem {
 struct { int x=0, width=20; } group;
 int y=20,h=15,full_draw_area=1; unsigned char op=0x66;
};
static uint32_t gp0_cmd_buf[12];
static uint16_t gp0_ot_rank=3;
static int ws_auto_ui_squash;
static int gp0_state,draw_offset_x,draw_offset_y;
enum {GP0_POLYLINE_MONO=4,GP0_POLYLINE_SHADED=5};
static WsUiPrepassItem item;
static const WsUiPrepassItem *ws_auto_ui_item(){return &item;}
static int ws_ui_untextured_op(unsigned op){return op==0x28 || op==0x60;}
static int ws_disp_w(){return 364;}
static void parse_vertex(uint32_t p,int32_t *x,int32_t *y){*x=(int16_t)p;*y=(int16_t)(p>>16);}
#include "window_gpu.inc"
int main(){
 for(unsigned op : {0x64u,0x66u}) for(unsigned x : {80u,120u,200u,280u}) {
  gp0_cmd_buf[0]=op<<24;gp0_cmd_buf[1]=(112u<<16)|x;
  gp0_cmd_buf[2]=0x48730000u;
  const unsigned f=nitrogen_gpu_ui_flags();
  assert(f&0x10);assert(((f>>5)&3)==1);assert(((f>>7)&3)==1);
  assert((f&0xfff0u)==((f|0x0fu)&0xfff0u));
  gp0_cmd_buf[2]=0x5da30000u; // unrelated world sprite, even in front layer
  assert(nitrogen_gpu_ui_flags()==0);
 }
 gp0_cmd_buf[0]=0x64000000u;gp0_cmd_buf[1]=(24u<<16)|30;
 gp0_cmd_buf[2]=0x48730000u;gp0_ot_rank=440;
 assert(((nitrogen_gpu_ui_flags()>>5)&15)==0); // score widget: top left
 gp0_cmd_buf[1]=(21u<<16)|115;gp0_cmd_buf[2]=0x4d330000u;
 assert(((nitrogen_gpu_ui_flags()>>5)&15)==1); // complete centred progress bar
 gp0_cmd_buf[1]=(162u<<16)|8;gp0_cmd_buf[2]=0x7a270000u;
 assert(((nitrogen_gpu_ui_flags()>>5)&15)==8); // complete bottom-left frame
 gp0_cmd_buf[0]=0x2c000000u;gp0_cmd_buf[2]=0x6fe30000u;gp0_ot_rank=427;
 for(int i : {1,3,5,7})gp0_cmd_buf[i]=(200u<<16)|40u;
 assert(nitrogen_gpu_ui_flags()&0x10); // complete weapon widget
 gp0_cmd_buf[7]=(200u<<16)|200u;
 assert(nitrogen_gpu_ui_flags()==0); // ordinary geometry outside widget
 gp0_state=GP0_POLYLINE_SHADED;draw_offset_y=256;
 assert(nitrogen_gpu_ui_flags()==0); // never reuse a stale polygon packet
 assert(nitrogen_gpu_line_flags(30,456,50,466)&0x10);
 assert(nitrogen_gpu_line_flags(30,456,150,466)==0);
 gp0_ot_rank=9;
 assert(nitrogen_gpu_line_flags(30,456,50,466)==0);
}
'''
        source='#include <initializer_list>\n'+source
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'fixture.cpp').write_text(source)
            r=subprocess.run(['c++','-std=c++17','-I',str(ROOT/'compat'),str(p/'fixture.cpp'),
                              '-o',str(p/'fixture')],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            r=subprocess.run([str(p/'fixture')],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_adapter_rejects_changed_contract(self):
        spec=importlib.util.spec_from_file_location('window_adapter',ROOT/'tools/adapt_window_display.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with self.assertRaises(ValueError):module.adapt_gpu('/* incompatible pinned GPU */')
        with self.assertRaises(ValueError):module.adapt_renderer('/* incompatible pinned renderer */')

if __name__=='__main__':unittest.main()
