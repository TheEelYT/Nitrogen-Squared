/* Original host hotkey policy. Tab remains available to ordinary UI input. */
#ifndef NITROGEN_HOST_HOTKEYS_H
#define NITROGEN_HOST_HOTKEYS_H
#include "psx_sdl.h"
#include "host_keymap.h"
#include <array>
#include <algorithm>
static int nitrogen_host_keymap_down(HostKeymapAction action,const uint8_t *keys,int mod)
{
    if(action!=HOST_KEYMAP_TURBO || !keys || !keys[SDL_SCANCODE_TAB])
        return host_keymap_down(action,keys,mod);
    // Mask only the Turbo poll, including an existing saved Tab binding.
    // Other configured Turbo keys and every non-Turbo action still work.
    std::array<uint8_t,SDL_NUM_SCANCODES> filtered{};
    std::copy_n(keys,filtered.size(),filtered.begin());
    filtered[SDL_SCANCODE_TAB]=0;
    return host_keymap_down(action,filtered.data(),mod);
}
#endif
