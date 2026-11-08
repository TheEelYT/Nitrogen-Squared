/* Original title defaults around the pinned keyboard parser and sampler.
 * Keep existing custom profiles and alternate/mouse bindings unchanged. */
#define psx_keybinds_init nitrogen_framework_keybinds_init
#define psx_keybinds_reset_player nitrogen_framework_keybinds_reset_player
#include NITROGEN_FRAMEWORK_KEYBINDS
#undef psx_keybinds_init
#undef psx_keybinds_reset_player
#include <sys/stat.h>

static const PsxPlayerBinds nitrogen_keyboard_defaults = {
    .up = SDL_SCANCODE_W, .down = SDL_SCANCODE_S,
    .left = SDL_SCANCODE_A, .right = SDL_SCANCODE_D,
    .cross = SDL_SCANCODE_RETURN, .circle = SDL_SCANCODE_RSHIFT,
    .square = SDL_SCANCODE_E, .triangle = SDL_SCANCODE_BACKSPACE,
    .l1 = SDL_SCANCODE_S, .r1 = SDL_SCANCODE_SPACE,
    .l2 = SDL_SCANCODE_MINUS, .r2 = SDL_SCANCODE_EQUALS,
    .start = SDL_SCANCODE_P, .select = SDL_SCANCODE_O,
    /* A/D also steer when the game selects an analog pad. W/S remain digital
     * weapon/menu and brake inputs; they must not move the vertical stick. */
    .ls_left = SDL_SCANCODE_A, .ls_right = SDL_SCANCODE_D,
};

static int nitrogen_stock_keyboard(int player)
{
    for (int i = 0; i < PSXKB_N; ++i) {
        const size_t offset = s_buttons[i].offset;
        const SDL_Scancode current = *(const SDL_Scancode *)((const char *)&s_binds.player[player] + offset);
        const SDL_Scancode stock = *(const SDL_Scancode *)((const char *)&s_default_binds.player[player] + offset);
        const SDL_Scancode alt = *(const SDL_Scancode *)((const char *)&s_alt_binds.player[player] + offset);
        if (current != stock || alt != SDL_SCANCODE_UNKNOWN) return 0;
    }
    return 1;
}

void psx_keybinds_reset_player(int player)
{
    if (player < 1 || player > PSXKB_MAX_PLAYERS) return;
    s_binds.player[player - 1] = nitrogen_keyboard_defaults;
    memset(&s_alt_binds.player[player - 1], 0, sizeof(PsxPlayerBinds));
}

void psx_keybinds_init(const char *exe_path)
{
    /* Start from the old defaults when parsing a custom/partial legacy file.
     * Compare complete semantic profiles, including alts, before upgrading. */
    s_binds = s_default_binds;
    memset(&s_alt_binds, 0, sizeof(s_alt_binds));
    derive_ini_path(exe_path);
    /* The SDK's extension heuristic treats an extensionless Linux executable
     * as a directory. Recognize real files/directories before using it. */
    if (exe_path && *exe_path) {
        struct stat info;
        if (stat(exe_path, &info) == 0) {
            char directory[sizeof(s_ini_path)];
            if (snprintf(directory, sizeof(directory), "%s", exe_path) < (int)sizeof(directory)) {
#ifdef _WIN32
                if ((info.st_mode & _S_IFDIR) != 0) {
#else
                if (S_ISDIR(info.st_mode)) {
#endif
                    const size_t len = strlen(directory);
                    if (len + 1 < sizeof(directory)) {
                        directory[len] = '/'; directory[len + 1] = '\0';
                        derive_ini_path(directory);
                    }
                } else {
                    char *slash = NULL;
                    for (char *p = directory; *p; ++p)
                        if (*p == '/' || *p == '\\') slash = p;
                    if (slash) { slash[1] = '\0'; derive_ini_path(directory); }
                    else derive_ini_path(NULL);
                }
            }
        }
    }
    FILE *existing = fopen(s_ini_path, "r");
    if (existing) {
        fclose(existing);
        load_ini(s_ini_path);
        for (int p = 0; p < PSXKB_MAX_PLAYERS; ++p)
            if (nitrogen_stock_keyboard(p)) s_binds.player[p] = nitrogen_keyboard_defaults;
        /* Do not rewrite a user's file merely to migrate stock profiles.
         * Explicit Save persists the effective bindings through the SDK API. */
    } else {
        for (int p = 1; p <= PSXKB_MAX_PLAYERS; ++p) psx_keybinds_reset_player(p);
        write_ini(s_ini_path);
    }
}
