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

    def test_adapter_rejects_changed_contract(self):
        spec=importlib.util.spec_from_file_location('window_adapter',ROOT/'tools/adapt_window_display.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with self.assertRaises(ValueError):module.adapt_gpu('/* incompatible pinned GPU */')
        with self.assertRaises(ValueError):module.adapt_renderer('/* incompatible pinned renderer */')

if __name__=='__main__':unittest.main()
