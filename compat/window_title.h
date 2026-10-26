/* Original window-lifetime title ownership, separate from transient FPS text. */
#pragma once
#include <cstdint>
#include <string>
class NitrogenWindowTitle {
    uint32_t owner = 0;
    bool bound = false;
    std::string base;
public:
    const char *get(uint32_t window, const char *current) {
        if (!bound || owner != window) {
            owner = window; bound = true; base = current ? current : "";
        }
        return base.c_str();
    }
};
