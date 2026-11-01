"""Compile the original adapter around a synthetic core, without game bytes."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class InterpreterAttributionTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'), 'C compiler required for attribution contract')
    def test_normal_omits_debug_lookup_and_keeps_execution_guards(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)
            (p/'core.c').write_text('''
extern uint32_t psx_overlay_resident_crc_at(uint32_t, int *);
extern int psx_overlay_static_match_ranges(void);
int core(void) {
    int valid=0;
    uint32_t occupant=psx_overlay_resident_crc_at(123, &valid);
    if (!psx_overlay_static_match_ranges()) return 9;
#ifdef PSX_NO_DEBUG_TOOLS
    return occupant != 0 || valid != 0;
#else
    return occupant != 456 || valid != 1;
#endif
}
''')
            (p/'main.c').write_text('''
#include <stdint.h>
static int calls, guards;
uint32_t psx_overlay_resident_crc_at(uint32_t p,int *v) {
    ++calls; *v=1; return p==123 ? 456 : 0;
}
int psx_overlay_static_match_ranges(void) { ++guards; return 1; }
extern int core(void);
int main(void) {
    int result=core();
#ifdef PSX_NO_DEBUG_TOOLS
    return result || calls != 0 || guards != 1;
#else
    return result || calls != 1 || guards != 1;
#endif
}
''')
            for normal in (False, True):
                cmd=['cc','-std=c11','-Werror',
                     '-DNITROGEN_FRAMEWORK_INTERP="'+str(p/'core.c')+'"',
                     str(ROOT/'compat/interpreter_attribution.c'),str(p/'main.c'),'-o',str(p/'fixture')]
                if normal: cmd.append('-DPSX_NO_DEBUG_TOOLS=1')
                r=subprocess.run(cmd,capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stdout+r.stderr)
                r=subprocess.run([str(p/'fixture')],capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stdout+r.stderr)
