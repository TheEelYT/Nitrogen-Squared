/* Original host bridge; the pinned runtime main remains the implementation. */
#include "runtime_telemetry.h"
#include "window_title.h"
#include "psx_sdl.h"
#include "host_hotkeys.h"
#ifdef NITROGEN_WINDOW_DISPLAY
#include "window_display.h"
#include "nitrogen_options.h"
static void nitrogen_window_update();
#endif
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
#define debug_server_shutdown nitrogen_runtime_shutdown
#define host_keymap_down nitrogen_host_keymap_down
#include NITROGEN_FRAMEWORK_MAIN
#undef host_keymap_down
#undef spu_output_pop
#undef debug_server_shutdown
#undef SDL_GetWindowTitle
#ifdef NITROGEN_WINDOW_DISPLAY
extern "C" int nitrogen_menu_reserved_height(void);
extern "C" void nitrogen_gpu_enable_ui(void);
static void nitrogen_window_update()
{
    if(nitrogen_window_take_close()) {
        SDL_Event event{};event.type=SDL_EVENT_QUIT;SDL_PushEvent(&event);
    }
    if (!g_gl_active || !sdl_window || g_headless) return;
    nitrogen_window_frame(s_frame_count);
    nitrogen_options_init(SDL_GetBasePath());
    nitrogen_window_ui_scale(nitrogen_option_get(NITROGEN_HUD_SCALE));
    static int applied_volume = -1;
    const int volume = nitrogen_option_get(NITROGEN_MASTER_VOLUME);
    if (applied_volume != volume) { host_volume_set(volume); applied_volume = volume; }
    static int applied_mode = -1;
    const int mode = nitrogen_option_get(NITROGEN_VIDEO_MODE);
    if (applied_mode != mode) {
        if (psx_window_fullscreen_set(sdl_window, &s_window_fullscreen, mode) == 0) {
            g_fullscreen = mode;
            applied_mode = mode;
        } else {
            std::fprintf(stderr,"nitrogen: video mode %d unavailable (%s); keeping mode %d\n",mode,SDL_GetError(),s_window_fullscreen.mode);
            applied_mode=s_window_fullscreen.mode;
            (void)nitrogen_option_set(NITROGEN_VIDEO_MODE,applied_mode);
        }
    }
    int width = 0, height = 0;
    SDL_GL_GetDrawableSize(sdl_window, &width, &height);
    height -= nitrogen_menu_reserved_height();
    if (width <= 0 || height <= 0) return; // minimized: keep the last valid frame
    nitrogen_window_publish(width, height);
    // The old title config may already exist after an update. Resolve the
    // requested sharp presentation here, rather than requiring a reimport.
    g_video_aa = false;
    g_video_texfilter = 0;
    g_video_fmv_filter = 0;
    if (gr_texture_filter() != 0) gr_set_texture_filter(0);
    nitrogen_gpu_enable_ui();
    gpu_ws_set_auto_ui_in_place(0);
    int num = width, den = height;
    const int divisor = aspect_gcd(num, den);
    num /= divisor; den /= divisor;
    // Project into the game's authored viewport, so its clipper receives
    // the wider field before rejecting polygons. Unprojected menu backdrop
    // sprites cover the drawable with a separate uniform transform.
    if (num != g_video_aspect_num || den != g_video_aspect_den ||
        g_ws_native_wide != 0) {
        g_video_aspect_num = num; g_video_aspect_den = den;
        g_ws_native_wide = 0;
        gl_renderer_set_display_aspect(num, den);
        g_ws_projection_mode = -1;
        refresh_widescreen_projection();
    }
    // Integer internal raster surfaces round upward to cover the drawable;
    // nearest presentation samples the result at the actual window size.
    static int last_scale = 0;
    static Uint32 last_window = 0;
    const Uint32 window_id = SDL_GetWindowID(sdl_window);
    if (last_window != window_id) {
        last_window = window_id;
        last_scale = 0;
        // The getter also takes renderer ownership. Set the fixed policy once
        // for a new window instead of draining the worker on every frame.
        (void)gl_renderer_set_post_aa(0);
    }
    GpuDisplayInfo display{}; gpu_get_display_info(&display);
    const int source_h=std::max(1,(int)display.height);
    const int source_w=std::max(1,(int)display.width);
    nitrogen_window_world_raster(width,height,source_w,source_h,nitrogen_option_get(NITROGEN_RENDER_PERCENT));
    const int viewport_w=(int64_t)num*3<(int64_t)den*4 ? height*4/3 : width;
    const int scale=std::max({1,(height+source_h-1)/source_h,
                            (viewport_w+source_w-1)/source_w});
    if (last_scale != scale) {
        (void)video_resolution_apply_live(std::min(scale * 240, PSX_IR_MAX_LINES), 0, 1000);
        last_scale = scale; // a refused request is retried on the next size step
    }
}
#endif
extern "C" uint32_t spu_output_pop(int16_t *, uint32_t);
extern "C" void debug_server_shutdown(void);
#ifdef PSX_HAS_OVERLAY_DISPATCH
extern "C" void psx_overlay_static_get_stats(uint64_t *, uint64_t *, uint64_t *, uint64_t *);
#endif
// The pinned main reaches this last step of every normal shutdown, including
// window-close paths that call exit(). Join GL before global UI mutexes die.
extern "C" void nitrogen_runtime_shutdown(void)
{
    gl_renderer_render_thread_stop();
    NitrogenRuntimeStatus status{};
    nitrogen_runtime_status(&status);
    std::fprintf(stdout, "nitrogen: last audio/render sample: worker=%d bound=%d rate=%d output_frames=%llu underflow_%s=%llu overflow_frames=%llu\n",
        status.worker_active, status.max_frames, status.host_rate,
        (unsigned long long)status.samples, status.legacy ? "events" : "samples",
        (unsigned long long)status.underruns, (unsigned long long)status.overflow_drops);
#ifdef PSX_HAS_OVERLAY_DISPATCH
    uint64_t checks = 0, hits = 0, variant_misses = 0, address_misses = 0;
    psx_overlay_static_get_stats(&checks, &hits, &variant_misses, &address_misses);
    std::fprintf(stdout, "nitrogen: native game slice: dispatches=%llu residency_rejections=%llu\n",
        (unsigned long long)hits, (unsigned long long)variant_misses);
#endif
    debug_server_shutdown();
}
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
#ifdef NITROGEN_WINDOW_DISPLAY
    nitrogen_window_update();
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
