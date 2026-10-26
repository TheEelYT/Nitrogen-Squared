/* Original desktop frontend. Game media and guest memory never enter the UI. */
#include "desktop_menu.h"
#include "psx_menu_host.h"
#include "host_osd.h"
#include "runtime_telemetry.h"
#include "../native/movie_player.h"
#include <SDL3/SDL.h>
#include "imgui.h"
#include "imgui_impl_sdl3.h"
#include "imgui_impl_opengl3.h"
#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <mutex>
#include <string>

namespace {
struct DesktopMenu {
    std::mutex mutex;
    const PsxMenuHost *host = nullptr;
    ImGuiContext *imgui = nullptr;
    SDL_Window *window = nullptr;
    std::atomic<bool> open{false};
    bool visible = true, autohide = false, settings = false, about = false;
    bool performance = false, audio = false, reset = false;
    bool escape = false, close_requested = false;
    int volume = 100, unmuted = 100;
    Uint32 volume_event = 0;
    float bar_height = 24.0f;
    std::string preferences;
    double rate_time = 0, sample_rate = 0;
    uint64_t last_samples = 0;
};
DesktopMenu menu;
std::atomic<int> reserved{0};

void save_preferences(DesktopMenu &m)
{
    if (m.preferences.empty()) return;
    std::ofstream out(m.preferences, std::ios::trunc);
    if (!out) { std::fprintf(stderr, "nitrogen: could not save menu preferences\n"); return; }
    out << "visible " << m.visible << "\nautohide " << m.autohide
        << "\nvolume " << m.volume << "\nperformance " << m.performance
        << "\naudio " << m.audio << '\n';
}

void fullscreen(DesktopMenu &m)
{
    PsxHostVideoSettings v{};
    m.host->video_get(&v);
    v.fullscreen = v.fullscreen ? 0 : 1;
    m.host->video_apply(&v);
}

int attach(void *context, void *window, void *gl, const PsxMenuHost *host)
{
    auto &m = *static_cast<DesktopMenu *>(context);
    std::lock_guard<std::mutex> lock(m.mutex);
    if (!host || host->abi_version != PSX_MENU_ABI_VERSION) return 0;
    m.host = host;
    m.volume_event = SDL_RegisterEvents(1);
    if (!m.volume_event) return 0;
    m.window = static_cast<SDL_Window *>(window);
    m.settings = m.about = m.reset = m.escape = m.close_requested = false;
    m.open = false;
    const char *base = SDL_GetBasePath();
    m.preferences = base ? std::string(base) + "nitrogen-menu.ini" : "";
    m.volume = host_volume_get();
    std::ifstream in(m.preferences);
    std::string name;
    int value;
    while (in >> name >> value) {
        if (name == "visible") m.visible = value != 0;
        else if (name == "autohide") m.autohide = value != 0;
        else if (name == "volume") m.volume = std::clamp(value, 0, 100);
        else if (name == "performance") m.performance = value != 0;
        else if (name == "audio") m.audio = value != 0;
    }
    host_volume_set(m.volume);
    if (m.volume) m.unmuted = m.volume;
    IMGUI_CHECKVERSION();
    m.imgui = ImGui::CreateContext();
    ImGui::SetCurrentContext(m.imgui);
    ImGuiIO &io = ImGui::GetIO();
    io.IniFilename = nullptr;
    io.LogFilename = nullptr;
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    const float scale = std::clamp(SDL_GetWindowDisplayScale(m.window), 1.0f, 3.0f);
    ImFontConfig font;
    font.SizePixels = 15.0f * scale;
    std::string font_path;
#ifdef _WIN32
    if (const char *windows = std::getenv("WINDIR")) font_path = std::string(windows) + "/Fonts/segoeui.ttf";
#else
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf";
#endif
    // Use an installed host font, never copy it into the project/package.
    ImFont *loaded = nullptr;
    if (!font_path.empty() && std::ifstream(font_path, std::ios::binary).good())
        loaded = io.Fonts->AddFontFromFileTTF(font_path.c_str(), font.SizePixels);
    if (!loaded) io.Fonts->AddFontDefault(&font);
    ImGui::StyleColorsDark();
    ImGuiStyle &style = ImGui::GetStyle();
    style.WindowRounding = 5;
    style.PopupRounding = 5;
    style.FrameRounding = 3;
    style.Colors[ImGuiCol_MenuBarBg] = ImVec4(.15f, .15f, .15f, 1);
    style.Colors[ImGuiCol_PopupBg] = ImVec4(.15f, .15f, .15f, 1);
    style.ScaleAllSizes(scale);
    if (!ImGui_ImplSDL3_InitForOpenGL(m.window, gl)) {
        ImGui::DestroyContext(m.imgui); m.imgui = nullptr; return 0;
    }
    if (!ImGui_ImplOpenGL3_Init("#version 330")) {
        ImGui_ImplSDL3_Shutdown();
        ImGui::DestroyContext(m.imgui); m.imgui = nullptr; return 0;
    }
    m.bar_height = font.SizePixels + style.FramePadding.y * 2;
    reserved = m.visible && !m.autohide ? (int)std::ceil(m.bar_height) : 0;
    m.rate_time = 0; m.last_samples = 0; m.sample_rate = 0;
    return 1;
}

int event(void *context, const void *input)
{
    auto &m = *static_cast<DesktopMenu *>(context);
    std::lock_guard<std::mutex> lock(m.mutex);
    if (!m.imgui) return 0;
    ImGui::SetCurrentContext(m.imgui);
    const auto &ev = *static_cast<const SDL_Event *>(input);
    ImGui_ImplSDL3_ProcessEvent(&ev);
    if (ev.type == m.volume_event) { host_volume_set(ev.user.code); return 1; }
    if (ev.type == SDL_EVENT_KEY_DOWN && !ev.key.repeat) {
        if (ev.key.key == SDLK_F1) {
            m.visible = !m.visible;
            if (!m.visible) m.close_requested = true;
            save_preferences(m);
            return 1;
        }
        if (ev.key.key == SDLK_F11) { fullscreen(m); return 1; }
        if (ev.key.key == SDLK_ESCAPE && m.open.load()) { m.escape = true; return 1; }
    }
    if (ev.type == SDL_EVENT_WINDOW_FOCUS_LOST) m.close_requested = true;
    const bool key = ev.type == SDL_EVENT_KEY_DOWN || ev.type == SDL_EVENT_KEY_UP ||
                     ev.type == SDL_EVENT_TEXT_INPUT || ev.type == SDL_EVENT_TEXT_EDITING;
    const bool mouse = ev.type == SDL_EVENT_MOUSE_MOTION || ev.type == SDL_EVENT_MOUSE_BUTTON_DOWN ||
                       ev.type == SDL_EVENT_MOUSE_BUTTON_UP || ev.type == SDL_EVENT_MOUSE_WHEEL;
    const bool pad = ev.type == SDL_EVENT_GAMEPAD_BUTTON_DOWN || ev.type == SDL_EVENT_GAMEPAD_BUTTON_UP ||
                     ev.type == SDL_EVENT_GAMEPAD_AXIS_MOTION;
    if (m.open && (key || mouse || pad)) return 1;
    if (mouse && m.visible) {
        float x = 0, y = 0;
        SDL_GetMouseState(&x, &y);
        if (ev.type == SDL_EVENT_MOUSE_BUTTON_DOWN || ev.type == SDL_EVENT_MOUSE_BUTTON_UP)
            y = ev.button.y;
        if (y >= 0 && y < m.bar_height) return 1;
    }
    return 0; // Never consume quit, resize, focus or device-removal events.
}

void passive_window(DesktopMenu &m, const char *title, bool audio)
{
    ImGui::SetNextWindowBgAlpha(.9f);
    ImGui::SetNextWindowPos(ImVec2(12, m.bar_height + (audio && m.performance ? 85 : 12)), ImGuiCond_Always);
    ImGui::Begin(title, nullptr, ImGuiWindowFlags_AlwaysAutoResize | ImGuiWindowFlags_NoInputs |
                 ImGuiWindowFlags_NoNav | ImGuiWindowFlags_NoSavedSettings);
    if (audio) {
        NitrogenRuntimeStatus stats{};
        nitrogen_runtime_status(&stats);
        if (nitrogen_media_is_active()) {
            double seconds; uint64_t samples; nitrogen_media_get_stats(&seconds, &samples);
            ImGui::Text("Native media: %.2f seconds", seconds);
            ImGui::Text("Audio submitted: %llu samples", (unsigned long long)samples);
            ImGui::TextUnformatted("Independent audio; video follows media clock.");
        } else {
        ImGui::Text("SPU production: %.0f samples/s", m.sample_rate);
        if (stats.audio_active) {
            ImGui::Text("Output: %d Hz (%s)", stats.host_rate, stats.legacy ? "queue" : "clock bridge");
            ImGui::Text("Buffer: %.1f ms | target %.1f ms", stats.fill_ms, stats.target_ms);
            ImGui::Text("%s: %llu | overflow frames: %llu",
                stats.legacy ? "Empty queue events" : "Underflow samples",
                (unsigned long long)stats.underruns, (unsigned long long)stats.overflow_drops);
        } else ImGui::TextUnformatted("Audio output initializing.");
        ImGui::TextUnformatted("Independent output callback; guest-timed SPU/CD.");
        }
    } else {
        ImGui::Text("Display: %.1f FPS", ImGui::GetIO().Framerate);
        NitrogenRuntimeStatus stats{}; nitrogen_runtime_status(&stats);
        if (!nitrogen_media_is_active()) {
            ImGui::Text("Render worker: %s", stats.worker_active ? (stats.worker_held ? "synchronized" : "active") : "off");
            if (stats.worker_active) ImGui::Text("Queued frame bound: %d", stats.max_frames);
        }
        ImGui::TextUnformatted("Game speed: use the title-bar readout (--show-fps).");
    }
    ImGui::End();
}

void draw(void *context, int, int)
{
    auto &m = *static_cast<DesktopMenu *>(context);
    std::lock_guard<std::mutex> lock(m.mutex);
    if (!m.imgui) return;
    ImGui::SetCurrentContext(m.imgui);
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplSDL3_NewFrame();
    ImGui::NewFrame();
    const bool close = m.escape || m.close_requested;
    if (close) {
        m.settings = m.about = m.reset = false;
        m.escape = m.close_requested = false;
    }
    bool changed = false, popup = false;
    const ImVec2 mouse = ImGui::GetIO().MousePos;
    const bool over_bar = mouse.x >= 0 && mouse.x < ImGui::GetIO().DisplaySize.x &&
                          mouse.y >= 0 && mouse.y <= m.bar_height;
    const bool bar = m.visible && (!m.autohide || m.open || over_bar);
    if (bar && ImGui::BeginMainMenuBar()) {
        m.bar_height = ImGui::GetWindowHeight();
        if (!close && ImGui::BeginMenu("System")) {
            popup = true;
            if (ImGui::MenuItem("Settings")) m.settings = true;
            ImGui::Separator();
            changed |= ImGui::MenuItem("Show Menu Bar", "F1", &m.visible);
            changed |= ImGui::MenuItem("Autohide Menu Bar", nullptr, &m.autohide);
            PsxHostVideoSettings v{};
            m.host->video_get(&v);
            if (ImGui::MenuItem("Fullscreen", "F11", v.fullscreen != 0)) fullscreen(m);
            ImGui::Separator();
            if (ImGui::MenuItem("Hard Reset")) m.reset = true;
            ImGui::Separator();
            if (ImGui::MenuItem("Quit Application")) m.host->request_exit(PSX_MENU_EXIT_QUIT);
            ImGui::EndMenu();
        }
        if (!close && ImGui::BeginMenu("Debug")) {
            popup = true;
            changed |= ImGui::MenuItem("Performance Overlay", nullptr, &m.performance);
            changed |= ImGui::MenuItem("Audio Status", nullptr, &m.audio);
            ImGui::Separator();
            if (ImGui::MenuItem("About This Build")) m.about = true;
            ImGui::EndMenu();
        }
        ImGui::EndMainMenuBar();
    }
    if (m.settings) {
        ImGui::SetNextWindowSize(ImVec2(390, 0), ImGuiCond_FirstUseEver);
        if (ImGui::Begin("Settings", &m.settings, ImGuiWindowFlags_AlwaysAutoResize)) {
            PsxHostVideoSettings v{};
            m.host->video_get(&v);
            bool full = v.fullscreen != 0;
            if (ImGui::Checkbox("Fullscreen", &full)) fullscreen(m);
            ImGui::SeparatorText("Audio");
            if (ImGui::SliderInt("Volume", &m.volume, 0, 100, "%d%%")) {
                SDL_Event volume{}; volume.type = m.volume_event; volume.user.code = m.volume;
                SDL_PushEvent(&volume); changed = true;
                if (m.volume) m.unmuted = m.volume;
            }
            bool mute = m.volume == 0;
            if (ImGui::Checkbox("Mute", &mute)) {
                m.volume = mute ? 0 : m.unmuted;
                SDL_Event volume{}; volume.type = m.volume_event; volume.user.code = m.volume;
                SDL_PushEvent(&volume); changed = true;
            }
            ImGui::SeparatorText("Menu");
            changed |= ImGui::Checkbox("Show menu bar (F1)", &m.visible);
            changed |= ImGui::Checkbox("Autohide menu bar", &m.autohide);
            ImGui::TextUnformatted("Escape closes menus. F1 restores a hidden bar.");
        }
        ImGui::End();
    }
    if (m.about) {
        if (ImGui::Begin("About Nitrogen Squared", &m.about, ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::Text("Nitrogen Squared %s", NITROGEN_MENU_VERSION);
            ImGui::TextUnformatted("Private development runtime - user-provided game.");
            ImGui::TextUnformatted("C11 / C++17 | SDL3 | OpenGL | Dear ImGui");
        }
        ImGui::End();
    }
    if (m.reset) ImGui::OpenPopup("Hard Reset?");
    if (ImGui::BeginPopupModal("Hard Reset?", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
        ImGui::TextUnformatted("Restart the game? Unsaved progress will be lost.");
        if (ImGui::Button("Restart")) { m.reset = false; m.host->request_exit(PSX_MENU_EXIT_RELAUNCH); }
        ImGui::SameLine();
        if (ImGui::Button("Cancel") || close) { m.reset = false; ImGui::CloseCurrentPopup(); }
        ImGui::EndPopup();
    }
    NitrogenRuntimeStatus stats{};
    nitrogen_runtime_status(&stats);
    const double now = ImGui::GetTime();
    if (m.rate_time && now - m.rate_time >= 1.0) {
        const uint64_t count = stats.samples;
        m.sample_rate = count >= m.last_samples ? (count - m.last_samples) / (now - m.rate_time) : 0;
        m.last_samples = count; m.rate_time = now;
    } else if (!m.rate_time) { m.rate_time = now; m.last_samples = stats.samples; }
    if (m.performance) passive_window(m, "Performance", false);
    if (m.audio) passive_window(m, "Audio Status", true);
    m.open = popup || m.settings || m.about || m.reset;
    m.host->set_paused(m.open ? 1 : 0);
    // Autohide overlays briefly at the top; the persistent bar reserves space.
    reserved = m.visible && !m.autohide ? (int)std::ceil(m.bar_height * ImGui::GetIO().DisplayFramebufferScale.y) : 0;
    if (changed) save_preferences(m);
    ImGui::Render();
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
}

int is_open(void *context) { return static_cast<DesktopMenu *>(context)->open ? 1 : 0; }
void set_open(void *context, int open)
{
    auto &m = *static_cast<DesktopMenu *>(context);
    std::lock_guard<std::mutex> lock(m.mutex);
    m.settings = open != 0;
    if (!open) m.close_requested = true;
    m.open = open != 0;
}
void detach(void *context)
{
    auto &m = *static_cast<DesktopMenu *>(context);
    std::lock_guard<std::mutex> lock(m.mutex);
    if (m.imgui) {
        ImGui::SetCurrentContext(m.imgui);
        ImGui_ImplOpenGL3_Shutdown();
        ImGui_ImplSDL3_Shutdown();
        ImGui::DestroyContext(m.imgui);
    }
    m.imgui = nullptr; m.host = nullptr; m.window = nullptr;
    m.open = false; reserved = 0;
}
const PsxMenuProvider provider = {PSX_MENU_ABI_VERSION, "Nitrogen desktop menu", &menu,
    attach, event, is_open, set_open, draw, detach};
struct Registration { Registration() { psx_menu_set_provider(&provider); } } registration;
}

extern "C" int nitrogen_menu_reserved_height(void) { return reserved.load(); }
extern "C" void nitrogen_menu_letterbox(int ww, int wh, int num, int den,
                                        int *x, int *y, int *w, int *h)
{
    const int usable = std::max(1, wh - std::clamp(reserved.load(), 0, std::max(0, wh - 1)));
    int dw = ww, dh = (int)((int64_t)ww * den / std::max(1, num));
    if (dh > usable) { dh = usable; dw = (int)((int64_t)usable * num / std::max(1, den)); }
    *x = (ww - dw) / 2; *y = (usable - dh) / 2;
    *w = dw; *h = dh;
}
