/* N2O uploads its complete 640x480 15-bit title image while the GPU is still
 * in the movie's 24-bit mode, then switches GP1(08h) to 15-bit. The pinned
 * OpenGL backend classifies that upload as movie data and clears it on exit.
 * At this boundary CPU VRAM is authoritative: publish it to the FBO once so
 * the new display sees the title image the guest actually uploaded. */
#include "gpu.h"
#include "gpu_render.h"
#include "gpu_gl_renderer.h"

void nitrogen_framework_gpu_write_gp1(uint32_t value);

void gpu_write_gp1(uint32_t value)
{
    const int leaving_movie = ((value >> 24) & 0x3Fu) == 8u &&
        gpu_display_is_depth24() && (value & 0x10u) == 0u;
    nitrogen_framework_gpu_write_gp1(value);
    if (leaving_movie && gr_backend() == GR_BACKEND_OPENGL) {
        gl_renderer_restage_vram_after_savestate();
        gl_renderer_invalidate_present();
    }
}
