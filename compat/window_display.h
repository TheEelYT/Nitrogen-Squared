/* Original window presentation policy. No guest memory or timing changes. */
#ifndef NITROGEN_WINDOW_DISPLAY_H
#define NITROGEN_WINDOW_DISPLAY_H
#ifdef __cplusplus
extern "C" {
#endif
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
