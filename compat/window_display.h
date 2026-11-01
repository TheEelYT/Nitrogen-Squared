/* Original window presentation policy; guest clocks remain unchanged. */
#ifndef NITROGEN_WINDOW_DISPLAY_H
#define NITROGEN_WINDOW_DISPLAY_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* The USA weapon preview's separately authored projection, observed through
 * the toolkit projection ring. World/menu projection centres are different. */
static inline int nitrogen_window_projection_is_ui(int32_t ofx, int32_t ofy, int h)
{
    return ofx == 40 * 65536 && ofy == 199 * 65536 && h == 320;
}
/* Measured in drawable pixels, excluding the desktop menu. */
void nitrogen_window_publish(int width, int height);
void nitrogen_window_ui_vertex(float *x, float *y, unsigned flags,
                               int origin_x, int origin_y, int height,
                               int wide_width, int wide_offset);
int nitrogen_window_ui_step(int width, int height);
#ifdef __cplusplus
}
#endif
#endif
