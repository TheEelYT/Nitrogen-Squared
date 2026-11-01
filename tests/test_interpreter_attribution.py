"""Compile the original adapter around a synthetic core, without game bytes."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import hashlib

ROOT = Path(__file__).resolve().parents[1]

class InterpreterAttributionTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cmake'), 'CMake required for source guard')
    def test_source_guard_accepts_git_line_endings_and_rejects_changes(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); core=p/'core.c'
            original=b'/* Original synthetic interpreter fixture. */\nint core(void) { return 7; }\n'
            # Substitute only the expected fingerprint; exercise the complete
            # real adapter with a source-only synthetic framework contract.
            adapter=(ROOT/'cmake/interpreter_attribution.cmake').read_text().replace(
                '7439cdbb38d8142ab4719d7a9667e16259e7edc27273962b43f67f9de9f8f8b7',
                hashlib.sha256(original).hexdigest())
            (p/'adapter.cmake').write_text(adapter)
            (p/'CMakeLists.txt').write_text('''
cmake_minimum_required(VERSION 3.20)
project(SourceGuard NONE)
add_custom_target(nitrogen-runtime)
set(_nitrogen_interp "${CMAKE_CURRENT_SOURCE_DIR}/core.c")
set(_nitrogen_sources "${_nitrogen_interp}")
function(psxrecomp_add_implementation target)
    cmake_parse_arguments(I "" "NAME;CONTRACT" "HLE_SOURCES;LLE_SOURCES;CONTRACT_FILES" ${ARGN})
    if(NOT I_NAME STREQUAL "n2o-interpreter-attribution" OR NOT I_LLE_SOURCES STREQUAL _nitrogen_interp)
        message(FATAL_ERROR "Original reference interpreter was not retained")
    endif()
endfunction()
include(adapter.cmake)
''')
            for data,ok in ((original,True),(original.replace(b'\n',b'\r\n'),True),
                            (original.replace(b'return 7',b'return 8'),False)):
                core.write_bytes(data)
                r=subprocess.run(['cmake','-S',str(p),'-B',str(p/'build')],capture_output=True,text=True)
                self.assertEqual(r.returncode==0,ok,r.stdout+r.stderr)
                if not ok: self.assertIn('Pinned interpreter attribution contract changed',r.stdout+r.stderr)

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
