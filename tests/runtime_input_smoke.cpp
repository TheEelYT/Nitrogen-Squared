/* Exercise the pinned runtime's real device routing and button mapping with
 * an original SDL virtual gamepad. No guest program or game data is executed. */
#define main nitrogen_unused_runtime_main
#include NITROGEN_RUNTIME_MAIN
#undef main

#if !defined(PSX_SDL3)
#error The virtual input smoke test requires the default SDL3 backend
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
    SDL_Quit();
    std::puts("Runtime input smoke passed: auto routing, ten buttons, digital stick, analog DualShock sample, unplug, keyboard source");
    return 0;
}
