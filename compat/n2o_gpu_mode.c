/* N2O uploads its complete 640x480 15-bit title image while the GPU is still
 * in the movie's 24-bit mode, then switches GP1(08h) to 15-bit. The pinned
 * OpenGL backend classifies that upload as movie data and clears it on exit.
 * At this boundary CPU VRAM is authoritative: publish it to the FBO once so
 * the new display sees the title image the guest actually uploaded. */
#include "gpu.h"
#include "gpu_render.h"
#include "gpu_gl_renderer.h"

void nitrogen_framework_gpu_write_gp1(uint32_t value);

static int native_movie_completed;
void nitrogen_gpu_native_movie_complete(void) { native_movie_completed = 1; }

void gpu_write_gp1(uint32_t value)
{
    const int leaving_movie = ((value >> 24) & 0x3Fu) == 8u &&
        gpu_display_is_depth24() && (value & 0x10u) == 0u;
    nitrogen_framework_gpu_write_gp1(value);
    int publishing_title = 0;
    if (native_movie_completed && ((value >> 24) & 0x3fu) == 8u && !gpu_display_is_depth24()) {
        GpuDisplayInfo display;
        gpu_get_display_info(&display);
        if (display.width == 640 && display.height > 240) { native_movie_completed = 0; publishing_title = 1; }
    }
    if ((leaving_movie || publishing_title) && gr_backend() == GR_BACKEND_OPENGL) {
        gl_renderer_restage_vram_after_savestate();
        gl_renderer_invalidate_present();
    }
}
