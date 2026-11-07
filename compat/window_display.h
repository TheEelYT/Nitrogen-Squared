/* Original window presentation policy; guest clocks remain unchanged. */
#ifndef NITROGEN_WINDOW_DISPLAY_H
#define NITROGEN_WINDOW_DISPLAY_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* The USA weapon preview's separately authored projection, observed through
 * the toolkit projection ring. World/menu projection centres are different. */
int nitrogen_window_projection_is_ui(int32_t ofx, int32_t ofy, int h);
/* Published by the identity-guarded title presenter, before its GTE calls. */
void nitrogen_window_menu_page(unsigned page);
void nitrogen_window_frame(uint64_t frame);
int nitrogen_window_controls_view(void);
int nitrogen_window_audio_view(void);
/* Title-screen hold feedback: 256 means hidden, 255..0 fades in. The caller
 * supplies monotonic seconds, independently of guest speed/frame count. */
unsigned nitrogen_window_close_hold(int held, double seconds);
int nitrogen_window_take_close(void);
int nitrogen_window_close_y(void);
/* Measured in drawable pixels, excluding the desktop menu. */
void nitrogen_window_publish(int width, int height);
void nitrogen_window_ui_vertex(float *x, float *y, unsigned flags,
                               int origin_x, int origin_y, int height,
                               int wide_width, int wide_offset);
int nitrogen_window_ui_step(int width, int height);
void nitrogen_window_ui_scale(int step); /* 0 = AUTO; otherwise 2,3,4,6 */
void nitrogen_window_world_raster(int width, int height, int source_width, int source_height, int percent);
void nitrogen_window_world_size(int *width, int *height);
#ifdef __cplusplus
}
#endif
#endif
