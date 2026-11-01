#include "window_display.h"
#include <algorithm>
#include <atomic>
namespace {
// One atomic pair: a render worker never sees half of a resize.
std::atomic<unsigned long long> drawable{0};
}
extern "C" void nitrogen_window_publish(int width, int height)
{
    drawable.store((static_cast<unsigned long long>(std::max(0, width)) << 32) |
                   static_cast<unsigned>(std::max(0, height)), std::memory_order_release);
}
extern "C" int nitrogen_window_ui_step(int width, int height)
{
    // A 4:3 authored canvas, with the game's non-square PS1 pixels preserved.
    return std::max(1, std::min(width / 320, height / 240));
}
extern "C" void nitrogen_window_ui_vertex(float *x, float *y, unsigned flags,
                                           int ox, int oy, int height,
                                           int wide_width, int wide_offset)
{
    const bool ui = (flags & 0x10u) != 0;
    const bool backdrop = (flags & 0x70u) == 0x60u;
    if (!ui && !backdrop) return;
    const auto size = drawable.load(std::memory_order_acquire);
    const int dw = static_cast<int>(size >> 32), dh = static_cast<unsigned>(size);
    const int width = static_cast<int>(flags >> 9) * 4;
    if (dw < 1 || dh < 1 || width < 1 || height < 1) return;
    if (backdrop) {
        if (static_cast<long long>(dw) * 3 > static_cast<long long>(dh) * 4) {
            const float cover = static_cast<float>(dw) * 3.f / (dh * 4.f);
            *y = oy + height * .5f + (*y - oy - height * .5f) * cover;
        }
        return;
    }
    const int step = nitrogen_window_ui_step(dw, dh);
    const float ax = static_cast<float>((flags >> 5) & 3u) * .5f;
    const float ay = static_cast<float>((flags >> 7) & 3u) * .5f;
    const int view_width = wide_width > 0 ? wide_width : width;
    const bool narrow = static_cast<long long>(dw) * 3 < static_cast<long long>(dh) * 4;
    const int viewport_width = narrow ? dh * 4 / 3 : dw;
    const float visible_width = narrow ? static_cast<float>(width) * dw / viewport_width : view_width;
    const float crop = narrow ? (width - visible_width) * .5f : 0.f;
    // Keep original physical 4:3 proportions; an authored pixel need not be
    // square (N2O uses both 320- and 368-column display modes).
    const float sx = (320.f / width) * step * view_width / viewport_width;
    const float sy = (240.f / height) * step * height / dh;
    *x = ox + crop + ax * visible_width - wide_offset + (*x - ox - ax * width) * sx;
    *y = oy + ay * height + (*y - oy - ay * height) * sy;
}
