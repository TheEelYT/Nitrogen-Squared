/* Exercise the actual provider and OpenGL/SDL backends with original pixels. */
#include "psx_menu_host.h"
#include "desktop_menu.h"
#include <SDL3/SDL.h>
#include <SDL3/SDL_opengl.h>
#include "imgui.h"
#include <cstdio>
#include <cstdlib>
#include <vector>

namespace {
int paused = 0, video_calls = 0, exit_request = -1;
PsxHostVideoSettings video{};
int pause_game(int value) { paused = value; return 1; }
int offline() { return 0; }
void video_get(PsxHostVideoSettings *out) { *out = video; }
unsigned video_apply(const PsxHostVideoSettings *next) { video = *next; video_calls++; return 0; }
void request_exit(int value) { exit_request = value; }
void check(bool condition, const char *message)
{
    if (!condition) { std::fprintf(stderr, "Menu smoke failed: %s (%s)\n", message, SDL_GetError()); std::exit(1); }
}
}

void nitrogen_menu_smoke()
{
    check(SDL_InitSubSystem(SDL_INIT_VIDEO), "initialize offscreen video");
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);
    SDL_Window *window = SDL_CreateWindow("Original menu fixture", 640, 480, SDL_WINDOW_OPENGL | SDL_WINDOW_HIDDEN);
    check(window != nullptr, "create window");
    SDL_GLContext gl = SDL_GL_CreateContext(window);
    check(gl != nullptr, "create GL context");
    const PsxMenuProvider *p = psx_menu_provider();
    check(p != nullptr, "register provider");
    PsxMenuHost host{};
    host.abi_version = PSX_MENU_ABI_VERSION;
    host.set_paused = pause_game; host.netplay_active = offline;
    host.video_get = video_get; host.video_apply = video_apply; host.request_exit = request_exit;
    check(p->attach(p->ctx, window, gl, &host) != 0, "attach provider");
    // A test-owned menu preference file is isolated by the CI build directory.
    auto frame = [&]() {
        SDL_PumpEvents();
        glViewport(0, 0, 640, 480);
        glClearColor(.0f, .2f, .7f, 1); glClear(GL_COLOR_BUFFER_BIT);
        p->draw(p->ctx, 640, 480);
    };
    auto key = [&](SDL_Keycode code) {
        SDL_Event ev{}; ev.type = SDL_EVENT_KEY_DOWN; ev.key.key = code;
        check(p->event(p->ctx, &ev) != 0, "consume host shortcut");
        ev.type = SDL_EVENT_KEY_UP; p->event(p->ctx, &ev);
    };
    auto mouse = [&](Uint32 type, float mx, float my) {
        SDL_Event ev{}; ev.type = type;
        if (type == SDL_EVENT_MOUSE_MOTION) {
            ev.motion.windowID = SDL_GetWindowID(window); ev.motion.x = mx; ev.motion.y = my;
        } else {
            ev.button.windowID = SDL_GetWindowID(window); ev.button.x = mx; ev.button.y = my;
            ev.button.button = SDL_BUTTON_LEFT; ev.button.down = type == SDL_EVENT_MOUSE_BUTTON_DOWN;
        }
        p->event(p->ctx, &ev);
    };
    frame();
    check(nitrogen_menu_reserved_height() > 0, "reserve menu space");
    int x, y, w, h;
    nitrogen_menu_letterbox(640, 480, 4, 3, &x, &y, &w, &h);
    check(y + h <= 480 - nitrogen_menu_reserved_height(), "keep complete game below menu");
    check(w * 3 <= h * 4 + 4 && w * 3 >= h * 4 - 4, "retain 4:3 aspect");
    check(ImGui::GetDrawData()->TotalVtxCount > 0, "render live menu geometry");
    std::vector<unsigned char> pixels(640 * 480 * 4);
    glReadPixels(0, 0, 640, 480, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    // The menu changes the top strip, while the original synthetic canvas remains below it.
    const size_t top = ((480 - 6) * 640 + 630) * 4;
    const size_t bottom = (6 * 640 + 630) * 4;
    check(pixels[top + 2] < 100 && pixels[bottom + 2] > 150, "compose only the menu strip");
    mouse(SDL_EVENT_MOUSE_MOTION, 25, 10); frame();
    mouse(SDL_EVENT_MOUSE_BUTTON_DOWN, 25, 10); frame();
    mouse(SDL_EVENT_MOUSE_BUTTON_UP, 25, 10); frame();
    check(p->is_open(p->ctx) && paused, "open System dropdown by mouse");
    if (const char *path = std::getenv("NITROGEN_MENU_TEST_PPM")) {
        glReadPixels(0, 0, 640, 480, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
        FILE *file = std::fopen(path, "wb");
        check(file != nullptr, "open original UI test capture");
        std::fprintf(file, "P6\n640 480\n255\n");
        for (int py = 479; py >= 0; --py)
            for (int px = 0; px < 640; ++px)
                std::fwrite(&pixels[(py * 640 + px) * 4], 1, 3, file);
        std::fclose(file);
    }
    key(SDLK_ESCAPE); frame(); frame();
    check(!p->is_open(p->ctx) && !paused, "close System dropdown with Escape");
    key(SDLK_F1); frame();
    check(nitrogen_menu_reserved_height() == 0, "hide and reclaim viewport");
    key(SDLK_F1); frame();
    check(nitrogen_menu_reserved_height() > 0, "restore hidden menu");
    key(SDLK_F11);
    check(video_calls == 1 && video.fullscreen == 1, "apply fullscreen through host");
    key(SDLK_F11);
    check(video_calls == 2 && video.fullscreen == 0, "return to windowed mode");
    p->set_open(p->ctx, 1); frame();
    check(p->is_open(p->ctx) && paused, "pause guest for settings");
    SDL_Event cross{}; cross.type = SDL_EVENT_GAMEPAD_BUTTON_DOWN; cross.gbutton.button = SDL_GAMEPAD_BUTTON_SOUTH;
    check(p->event(p->ctx, &cross) != 0, "consume gameplay input in settings");
    SDL_Event quit{}; quit.type = SDL_EVENT_QUIT;
    check(p->event(p->ctx, &quit) == 0, "preserve application quit");
    key(SDLK_ESCAPE); frame();
    check(!p->is_open(p->ctx) && !paused, "escape resumes guest");
    check(exit_request == -1, "opening menus does not reset or quit");
    p->detach(p->ctx);
    check(nitrogen_menu_reserved_height() == 0, "release viewport on detach");
    check(p->attach(p->ctx, window, gl, &host) != 0, "reattach after session reset");
    frame(); p->detach(p->ctx);
    SDL_GL_DestroyContext(gl); SDL_DestroyWindow(window);
    std::puts("Runtime menu smoke passed: composition, viewport, F1, F11, pause, input capture, Escape, reattach");
}
