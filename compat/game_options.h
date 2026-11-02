/* Original host presentation preferences, shared by the in-game menus. */
#ifndef NITROGEN_GAME_OPTIONS_H
#define NITROGEN_GAME_OPTIONS_H
#ifdef __cplusplus
extern "C" {
#endif
enum { NITROGEN_WINDOWED, NITROGEN_BORDERLESS, NITROGEN_FULLSCREEN };
enum { NITROGEN_VIDEO_MODE, NITROGEN_HUD_SCALE, NITROGEN_RENDER_PERCENT, NITROGEN_MASTER_VOLUME };
/* Call once on the main thread. A launcher-supplied path survives rebuilds. */
void nitrogen_options_init(const char *base_path);
int nitrogen_option_get(int option);
/* Invalid values are refused. Persist only an actual user change. */
int nitrogen_option_set(int option, int value);
int nitrogen_options_desktop(void);
#ifdef __cplusplus
}
#endif
#endif
