/* Original host bridge; the pinned runtime main remains the implementation. */
#include NITROGEN_FRAMEWORK_MAIN
#include "../native/movie_player.h"
extern "C" void nitrogen_gpu_native_movie_complete(void);
namespace {
std::string movie_saved_title;
std::atomic<int> movie_active{0};
std::atomic<double> movie_clock{0};
std::atomic<uint64_t> movie_samples{0};
}
extern "C" int nitrogen_media_is_active(void) { return movie_active.load(); }
extern "C" void nitrogen_media_host_stats(double seconds, uint64_t samples) { movie_clock.store(seconds); movie_samples.store(samples); }
extern "C" void nitrogen_media_get_stats(double *seconds, uint64_t *samples) { *seconds = movie_clock.load(); *samples = movie_samples.load(); }
extern "C" float nitrogen_media_host_refresh(void)
{
    SDL_DisplayMode mode{};
    return SDL_GetCurrentDisplayMode(SDL_GetDisplayForWindow(sdl_window), &mode) == 0 && mode.refresh_rate > 0 ? mode.refresh_rate : 60.0f;
}
extern "C" int nitrogen_media_host_available(void) { return g_gl_active && sdl_window && !g_headless && !psx_netplay_active(); }
extern "C" int nitrogen_media_host_service(void)
{
    if (g_ovl_exit.load()) return -1;
#ifndef PSX_NO_DEBUG_TOOLS
    debug_server_poll();
#endif
    host_pause_service(); return psx_host_pause_depth() > 0 ? 1 : 0;
}
extern "C" void nitrogen_media_host_quit(void) { g_ovl_exit = PSX_MENU_EXIT_QUIT + 1; }
extern "C" void nitrogen_media_host_devices(void) { refresh_player_devices(); }
extern "C" void nitrogen_media_host_begin(void)
{
    movie_active = 1; movie_clock = 0; movie_samples = 0;
    movie_saved_title = s_fps_base_title.empty() ? SDL_GetWindowTitle(sdl_window) : s_fps_base_title;
    SDL_SetWindowTitle(sdl_window, "Nitrogen Squared development [Native video]");
    if (sdl_audio_device) psx_sdl_audio_set_paused(sdl_audio_device, 1);
}
extern "C" void nitrogen_media_host_end(void)
{
    movie_active = 0; nitrogen_gpu_native_movie_complete();
    if (sdl_audio_device) { psx_sdl_audio_clear(sdl_audio_device); psx_sdl_audio_set_paused(sdl_audio_device, psx_host_pause_depth() > 0); }
    g_audio_cycle_resync = 1; s_frame_pacer = FramePacer{0};
    s_fps_last_time = 0; s_fps_last_frame = 0; s_fps_base_title.clear();
    SDL_SetWindowTitle(sdl_window, movie_saved_title.c_str());
}
