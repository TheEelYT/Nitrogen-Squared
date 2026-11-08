/* Original keyboard fixtures through the production SDK parser and sampler. */
static void runtime_keyboard_smoke(const char *argv0)
{
    namespace fs = std::filesystem;
    const fs::path directory = exe_dir_from_argv(argv0);
    const fs::path ini = directory / "keybinds.ini";
    require_input(!fs::exists(ini), "keyboard fixture starts with no bindings file");
    load_input_config(argv0); // The same startup path as a direct game launch.
    require_input(fs::is_regular_file(ini), "first launch creates defaults beside the executable");
    auto contents = [&]() {
        std::ifstream in(ini, std::ios::binary);
        return std::string((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
    };
    const std::string fresh = contents();
    struct KeyCase { SDL_Scancode key; uint16_t pressed; };
    const KeyCase cases[] = {
        {SDL_SCANCODE_W, PAD_UP}, {SDL_SCANCODE_D, PAD_RIGHT},
        {SDL_SCANCODE_S, PAD_DOWN | PAD_L1}, {SDL_SCANCODE_A, PAD_LEFT},
        {SDL_SCANCODE_RETURN, PAD_CROSS}, {SDL_SCANCODE_RSHIFT, PAD_CIRCLE},
        {SDL_SCANCODE_BACKSPACE, PAD_TRIANGLE}, {SDL_SCANCODE_E, PAD_SQUARE},
        {SDL_SCANCODE_P, PAD_START}, {SDL_SCANCODE_O, PAD_SELECT},
        {SDL_SCANCODE_SPACE, PAD_R1}, {SDL_SCANCODE_MINUS, PAD_L2},
        {SDL_SCANCODE_EQUALS, PAD_R2}
    };
    auto check_defaults = [&]() {
        for (int player = 1; player <= PSXKB_MAX_PLAYERS; ++player) {
            for (const auto &c : cases) {
                uint8_t keys[SDL_NUM_SCANCODES]{};
                keys[c.key] = 1;
                require_input(psx_keybinds_pad_word(keys, player) == (uint16_t)~c.pressed,
                              "README key produces exactly the intended PS1 buttons");
                uint8_t sticks[] = {128,128,128,128};
                psx_keybinds_sticks(keys, player, sticks);
                require_input(sticks[0] == (c.key == SDL_SCANCODE_A ? 0 : c.key == SDL_SCANCODE_D ? 255 : 128)
                              && sticks[1] == 128 && sticks[2] == 128 && sticks[3] == 128,
                              "A/D steer analog; weapon and brake keys leave other axes neutral");
            }
            for (auto key : {SDL_SCANCODE_UP, SDL_SCANCODE_X, SDL_SCANCODE_Z, SDL_SCANCODE_Q, SDL_SCANCODE_TAB}) {
                uint8_t keys[SDL_NUM_SCANCODES]{}; keys[key] = 1;
                require_input(psx_keybinds_pad_word(keys, player) == 0xffff, "obsolete stock keys do not leak buttons");
            }
        }
    };
    check_defaults();
    load_input_config(argv0);
    check_defaults(); // Persisted duplicate S and A/D binds survive reload.
    require_input(contents() == fresh, "reloading does not rewrite existing files");

    const std::string legacy =
        "up=Up\ndown=Down\nleft=Left\nright=Right\n"
        "cross=X\ncircle=S\nsquare=Z\ntriangle=A\n"
        "l1=Q\nr1=W\nl2=E\nr2=R\nl3=T\nr3=Y\nstart=Return\nselect=Right Shift\n"
        "ls_up=Up\nls_down=Down\nls_left=Left\nls_right=Right\n"
        "rs_up=None\nrs_down=None\nrs_left=None\nrs_right=None\n";
    std::string stock;
    for (int p = 1; p <= PSXKB_MAX_PLAYERS; ++p)
        stock += "[player" + std::to_string(p) + "]\n" + legacy;
    { std::ofstream out(ini, std::ios::binary); out << stock; }
    load_input_config(argv0);
    check_defaults();
    require_input(contents() == stock, "stock upgrade keeps the existing file byte-for-byte");

    const std::string custom = "# preserve custom profile and alternate mouse bind\n[player1]\ncross=K, Mouse1\n";
    { std::ofstream out(ini, std::ios::binary); out << custom; }
    load_input_config(argv0);
    require_input(psx_keybinds_get_button(1, PSX_KB_CROSS) == SDL_SCANCODE_K &&
                  psx_keybinds_get_button_alt(1, PSX_KB_CROSS) == PSXKB_MOUSE_SC(1), "custom primary and alternate survive");
    require_input(psx_keybinds_get_button(1, PSX_KB_UP) == SDL_SCANCODE_UP,
                  "partial legacy custom profiles retain their old unspecified defaults");
    require_input(psx_keybinds_get_button(2, PSX_KB_UP) == SDL_SCANCODE_W,
                  "untouched players independently receive the new default profile");
    require_input(contents() == custom, "custom file remains byte-for-byte unchanged");
    const std::string alternate_only = stock + "[player1]\ncross=X, Mouse1\n";
    { std::ofstream out(ini, std::ios::binary); out << alternate_only; }
    load_input_config(argv0);
    require_input(psx_keybinds_get_button(1, PSX_KB_UP) == SDL_SCANCODE_UP &&
                  psx_keybinds_get_button(1, PSX_KB_CROSS) == SDL_SCANCODE_X &&
                  psx_keybinds_get_button_alt(1, PSX_KB_CROSS) == PSXKB_MOUSE_SC(1),
                  "an alternate-only customization is not mistaken for stock");
    require_input(contents() == alternate_only, "alternate-only custom file remains unchanged");
    psx_keybinds_reset_player(1);
    require_input(psx_keybinds_get_button_alt(1, PSX_KB_CROSS) == SDL_SCANCODE_UNKNOWN, "reset clears alternate binds");
    psx_keybinds_save();
    load_input_config(argv0);
    check_defaults();
    std::puts("Runtime keyboard smoke passed: README buttons, shared S, analog steering, stock migration, custom profiles, reset/save/reload, direct launch");
}
