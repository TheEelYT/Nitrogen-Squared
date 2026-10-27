/* Exercise the pinned runtime's real device routing and button mapping with
 * an original SDL virtual gamepad. No guest program or game data is executed. */
#define main nitrogen_unused_runtime_main
#include NITROGEN_RUNTIME_MAIN
#undef main

#if !defined(PSX_SDL3)
#error The virtual input smoke test requires the default SDL3 backend
#endif

#if defined(NITROGEN_MENU_SMOKE)
void nitrogen_menu_smoke();
#endif

#if defined(NITROGEN_MEDIA_SMOKE)
void nitrogen_media_smoke();
#endif

static void require_input(bool condition, const char *message)
{
    if (!condition) {
        std::fprintf(stderr, "Input smoke test failed: %s (%s)\n", message, SDL_GetError());
        std::exit(1);
    }
}

static void update_virtual_input()
{
    SDL_UpdateJoysticks();
    SDL_PumpEvents();
    SDL_UpdateGamepads();
}

static void runtime_status_and_title_smoke()
{
    NitrogenRuntimeStatus before{}, after{};
    nitrogen_runtime_status(&before);
    spu_init(); spu_catch_up();
    psx_cycle_count += 768u * 32u;
    spu_catch_up();
    const uint32_t queued = spu_output_available();
    require_input(queued == 32, "generate original silent SPU samples");
    int16_t pcm[64];
    require_input(nitrogen_runtime_spu_output_pop(pcm, 32) == 32, "preserve the SPU drain result");
    require_input(spu_output_available() == 0, "drain each sample exactly once");
    nitrogen_runtime_status(&after);
    require_input(after.samples - before.samples == 32, "publish actual drained samples");
    require_input(!after.audio_active && !after.worker_active, "snapshot handles an unopened device/worker");
#ifdef _WIN32
    SDL_SetHint(SDL_HINT_VIDEO_DRIVER, "dummy");
#endif
    require_input(psx_sdl_init_subsystem(SDL_INIT_VIDEO) == 0, "initialize hidden title fixture");
    SDL_Window *window = psx_sdl_create_window("Original title fixture", 0, 0, 320, 240, SDL_WINDOW_HIDDEN);
    require_input(window != nullptr, "create hidden title fixture");
    SDL_Window *saved_window = sdl_window; sdl_window = window;
    require_input(std::string(nitrogen_base_window_title(window)) == "Original title fixture", "capture original window title");
    for (int pause = 0; pause < 6; ++pause) {
        s_fps_base_title = nitrogen_base_window_title(window);
        std::string decorated = s_fps_base_title + "  [Game 60 fps 1.00x] [Present 60.0 fps]";
        SDL_SetWindowTitle(window, decorated.c_str());
        present_session_reset(); // The real menu resume clears the FPS baseline.
        require_input(std::string(nitrogen_base_window_title(window)) == "Original title fixture", "menu resume never captures an FPS suffix");
    }
    SDL_DestroyWindow(window);
    window = psx_sdl_create_window("New session title", 0, 0, 320, 240, SDL_WINDOW_HIDDEN);
    require_input(window && std::string(nitrogen_base_window_title(window)) == "New session title", "new window gets its own base title");
    SDL_DestroyWindow(window); sdl_window = saved_window;
    SDL_QuitSubSystem(SDL_INIT_VIDEO);
#ifdef _WIN32
    SDL_ResetHint(SDL_HINT_VIDEO_DRIVER);
#endif
    std::puts("Runtime status/title smoke passed: exact SPU drain, coherent snapshot, six pause cycles, new window");
}

int main()
{
    SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1");
    require_input(psx_sdl_init(SDL_INIT_GAMEPAD | SDL_INIT_EVENTS) == 0, "initialize SDL input");
    SDL_VirtualJoystickDesc desc;
    SDL_INIT_INTERFACE(&desc);
    desc.type = SDL_JOYSTICK_TYPE_GAMEPAD;
    desc.naxes = SDL_GAMEPAD_AXIS_COUNT;
    desc.nbuttons = SDL_GAMEPAD_BUTTON_COUNT;
    desc.axis_mask = (1u << SDL_GAMEPAD_AXIS_COUNT) - 1u;
    desc.button_mask = (1u << SDL_GAMEPAD_BUTTON_COUNT) - 1u;
    desc.name = "Nitrogen original input fixture";
    const SDL_JoystickID id = SDL_AttachVirtualJoystick(&desc);
    require_input(id != 0, "attach virtual gamepad");
    update_virtual_input();

    set_default_controller_mapping_into(controller_map);
    set_player_device(g_players[0], "auto", PSXRecompV4::PAD_MODE_DIGITAL);
    set_player_device(g_players[1], "none", PSXRecompV4::PAD_MODE_DIGITAL);
    open_player(g_players[0], 0);
    PlayerInput &player = g_players[0];
    require_input(player.handle != nullptr, "route first gamepad to Player 1");
    require_input(g_players[1].kind == 0, "leave Player 2 unassigned");
    require_input(pad_sources_for(player, false).keybinds, "keep keyboard bindings available");
    SDL_Joystick *joystick = SDL_GameControllerGetJoystick(player.handle);
    require_input(joystick != nullptr, "open routed joystick");

    const struct { SDL_GamepadButton button; uint16_t psx_bit; } buttons[] = {
        {SDL_GAMEPAD_BUTTON_SOUTH, PAD_CROSS},
        {SDL_GAMEPAD_BUTTON_EAST, PAD_CIRCLE},
        {SDL_GAMEPAD_BUTTON_WEST, PAD_SQUARE},
        {SDL_GAMEPAD_BUTTON_NORTH, PAD_TRIANGLE},
        {SDL_GAMEPAD_BUTTON_START, PAD_START},
        {SDL_GAMEPAD_BUTTON_BACK, PAD_SELECT},
        {SDL_GAMEPAD_BUTTON_DPAD_UP, PAD_UP},
        {SDL_GAMEPAD_BUTTON_DPAD_DOWN, PAD_DOWN},
        {SDL_GAMEPAD_BUTTON_DPAD_LEFT, PAD_LEFT},
        {SDL_GAMEPAD_BUTTON_DPAD_RIGHT, PAD_RIGHT},
    };
    for (const auto &test : buttons) {
        require_input(SDL_SetJoystickVirtualButton(joystick, test.button, true), "press virtual button");
        update_virtual_input();
        require_input(pad_buttons_for(player, 1, false) == (uint16_t)(0xFFFFu & ~test.psx_bit),
                      "map gamepad button to PS1 digital pad");
        require_input(SDL_SetJoystickVirtualButton(joystick, test.button, false), "release virtual button");
        update_virtual_input();
        require_input(pad_buttons_for(player, 1, false) == 0xFFFFu, "release PS1 button");
    }
    require_input(SDL_SetJoystickVirtualAxis(joystick, SDL_GAMEPAD_AXIS_LEFTX, 32767), "move left stick");
    update_virtual_input();
    require_input((pad_buttons_for(player, 1, false) & PAD_RIGHT) == 0, "fold left stick into digital movement");
    require_input((pad_buttons_for(player, 1, true) & PAD_RIGHT) != 0, "suppress stick fold when requested");
    sio_init();
    player.mode = PSXRecompV4::PAD_MODE_ANALOG;
    refresh_player_devices();
    require_input(sio_get_pad_analog(0) == SIO_PAD_DUALSHOCK, "present an analog DualShock to the guest");
    PsxNetPad sample{};
    require_input(capture_pad_slot(0, &sample, false) != 0, "capture routed analog input");
    require_input(sample.connected && sample.analog == SIO_PAD_DUALSHOCK, "retain analog pad identity in sample");
    require_input(sample.lx >= 250 && sample.ly == 128, "report left stick as analog axes");
    require_input((sample.buttons & PAD_RIGHT) != 0, "analog movement does not press digital right");
    require_input(SDL_DetachVirtualJoystick(id), "unplug virtual gamepad");
    update_virtual_input();
    require_input(!SDL_GameControllerGetAttached(player.handle), "observe unplugged gamepad");
    close_player(player);
    require_input(pad_sources_for(player, false).keybinds, "retain keyboard source after unplug");
    runtime_status_and_title_smoke();
    #if defined(NITROGEN_MENU_SMOKE)
    nitrogen_menu_smoke();
    #endif
    #if defined(NITROGEN_MEDIA_SMOKE)
    nitrogen_media_smoke();
    #endif
    #if defined(NITROGEN_NATIVE_SMOKE)
    extern void nitrogen_native_smoke();
    nitrogen_native_smoke();
    #endif
    SDL_Quit();
    std::puts("Runtime input smoke passed: auto routing, ten buttons, digital stick, analog DualShock sample, unplug, keyboard source");
    return 0;
}
