/* Original host bridge; the pinned runtime main remains the implementation. */
#include "runtime_telemetry.h"
#include "window_title.h"
#include "psx_sdl.h"
static const char *nitrogen_base_window_title(SDL_Window *window)
{
    static NitrogenWindowTitle title;
    return title.get(SDL_GetWindowID(window), SDL_GetWindowTitle(window));
}
// The pinned main reads the title only when it re-anchors FPS telemetry.
// Pausing clears that FPS baseline; the window's original title stays owned
// by its window ID, rather than being re-read from an FPS-decorated title.
#define SDL_GetWindowTitle nitrogen_base_window_title
// Observe the existing host drain, preserving the guest DSP's sole owner.
#define spu_output_pop nitrogen_runtime_spu_output_pop
#include NITROGEN_FRAMEWORK_MAIN
#undef spu_output_pop
#undef SDL_GetWindowTitle
extern "C" uint32_t spu_output_pop(int16_t *, uint32_t);
namespace {
std::mutex runtime_status_mutex;
NitrogenRuntimeStatus runtime_status_snapshot{};
uint64_t runtime_sample_count = 0;
}
extern "C" void nitrogen_runtime_status(NitrogenRuntimeStatus *out)
{
    if (!out) return;
    std::lock_guard<std::mutex> lock(runtime_status_mutex);
    *out = runtime_status_snapshot;
}
extern "C" uint32_t nitrogen_runtime_spu_output_pop(int16_t *out, uint32_t count)
{
    const uint32_t copied = spu_output_pop(out, count);
    NitrogenRuntimeStatus status{};
    status.samples = runtime_sample_count += copied;
    double correction = 0;
    // The callback mutates bridge stats under this same device lock. UI
    // drawing must never read the bridge or a device being torn down.
    const bool lock_bridge = sdl_audio_device && !audio_legacy_mode();
    if (lock_bridge) psx_sdl_audio_lock(sdl_audio_device);
    status.audio_active = psx_audio_out_stats(&status.fill_ms, &status.target_ms,
        &status.underruns, &status.overflow_drops, &correction, &status.legacy, &status.host_rate);
    if (lock_bridge) psx_sdl_audio_unlock(sdl_audio_device);
    RtStats render{};
    rt_get_stats(&render); // Emulation-thread API; no context hand-off.
    status.worker_active = render.running;
    status.worker_held = render.held;
    status.max_frames = render.max_frames;
    status.frames_produced = render.frames_produced;
    status.frames_consumed = render.frames_consumed;
    status.backpressure_waits = render.backpressure_waits;
    { std::lock_guard<std::mutex> lock(runtime_status_mutex); runtime_status_snapshot = status; }
    return copied;
}
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
    movie_saved_title = s_fps_base_title.empty() ? nitrogen_base_window_title(sdl_window) : s_fps_base_title;
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
