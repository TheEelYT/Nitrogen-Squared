"""Check the real GP1 adapter's ordering with an original mock GPU backend."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GpuModeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("cmake"), "CMake is needed for the native adapter test")
    def test_movie_exit_republishes_cpu_vram_only_for_opengl(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "gpu.h").write_text('''
#include <stdint.h>
typedef struct { unsigned width, height; } GpuDisplayInfo;
void gpu_get_display_info(GpuDisplayInfo*);
void nitrogen_gpu_native_movie_complete(void);
int gpu_display_is_depth24(void);
void gpu_write_gp1(uint32_t);
''')
            (root / "gpu_render.h").write_text('''
typedef enum { GR_BACKEND_SOFTWARE, GR_BACKEND_OPENGL, GR_BACKEND_VULKAN } GrBackend;
GrBackend gr_backend(void);
''')
            (root / "gpu_gl_renderer.h").write_text('''
void gl_renderer_restage_vram_after_savestate(void);
void gl_renderer_invalidate_present(void);
''')
            (root / "fixture.c").write_text('''
#include "gpu.h"
#include "gpu_render.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c) do { if (!(c)) { fprintf(stderr, "Failed at line %d\\n", __LINE__); exit(1); } } while (0)
static int depth, mode_calls, stages, invalidations, cpu_pixel, fbo_pixel;
static unsigned width = 320, height = 240;
void gpu_get_display_info(GpuDisplayInfo* out) { out->width = width; out->height = height; }
static GrBackend backend = GR_BACKEND_OPENGL;
static uint32_t last_value;
int gpu_display_is_depth24(void) { return depth; }
GrBackend gr_backend(void) { return backend; }
void nitrogen_framework_gpu_write_gp1(uint32_t value) {
    ++mode_calls; last_value = value;
    if (((value >> 24) & 0x3F) == 8) depth = (value & 0x10) != 0;
}
void gl_renderer_restage_vram_after_savestate(void) {
    CHECK(depth == 0); CHECK(stages == invalidations);
    fbo_pixel = cpu_pixel; ++stages;
}
void gl_renderer_invalidate_present(void) {
    CHECK(stages == invalidations + 1); ++invalidations;
}
int main(void) {
    gpu_write_gp1(0x08000011); /* enter RGB888 movie */
    CHECK(depth == 1 && stages == 0 && mode_calls == 1);
    cpu_pixel = 1234; /* new 15-bit title is uploaded while movie mode remains on */
    gpu_write_gp1(0x08000027);
    CHECK(depth == 0 && stages == 1 && invalidations == 1 && fbo_pixel == 1234);
    CHECK(last_value == 0x08000027 && mode_calls == 2);
    gpu_write_gp1(0x08000027); /* same mode must not restage every frame */
    CHECK(stages == 1 && mode_calls == 3);
    gpu_write_gp1(0x08000011);
    gpu_write_gp1(0x03000000); /* display enable is not a depth change */
    CHECK(depth == 1 && stages == 1 && mode_calls == 5);
    backend = GR_BACKEND_SOFTWARE;
    gpu_write_gp1(0x08000027);
    CHECK(depth == 0 && stages == 1 && invalidations == 1 && mode_calls == 6);
    backend = GR_BACKEND_VULKAN;
    gpu_write_gp1(0x08000011);
    gpu_write_gp1(0x08000027);
    CHECK(stages == 1 && invalidations == 1 && mode_calls == 8);
    backend = GR_BACKEND_OPENGL;
    nitrogen_gpu_native_movie_complete();
    gpu_write_gp1(0x08000027);
    CHECK(stages == 1);
    width = 640; height = 476; cpu_pixel = 5678;
    gpu_write_gp1(0x08000027);
    CHECK(stages == 2 && invalidations == 2 && fbo_pixel == 5678);
    gpu_write_gp1(0x08000027);
    CHECK(stages == 2);
    return 0;
}
''')
            adapter = (ROOT / "compat/n2o_gpu_mode.c").as_posix()
            (root / "CMakeLists.txt").write_text(
                'cmake_minimum_required(VERSION 3.20)\nproject(GpuModeTest C)\n'
                f'add_executable(gpu-mode fixture.c "{adapter}")\n'
                'target_include_directories(gpu-mode PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")\n')
            build = root / "build"
            for command in (["cmake", "-S", str(root), "-B", str(build)],
                            ["cmake", "--build", str(build), "--config", "Release"]):
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            binaries = [p for p in build.rglob("gpu-mode*") if p.is_file() and p.name in ("gpu-mode", "gpu-mode.exe")]
            self.assertEqual(len(binaries), 1)
            result = subprocess.run([str(binaries[0])], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
