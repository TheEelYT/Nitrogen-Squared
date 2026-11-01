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
    if (!(flags & 0x10u)) return;
    const auto size = drawable.load(std::memory_order_acquire);
    const int dw = static_cast<int>(size >> 32), dh = static_cast<unsigned>(size);
    const int width = static_cast<int>(flags >> 9) * 4;
    if (dw < 1 || dh < 1 || width < 1 || height < 1) return;
    const int step = nitrogen_window_ui_step(dw, dh);
    const float ax = static_cast<float>((flags >> 5) & 3u) * .5f;
    const float ay = static_cast<float>((flags >> 7) & 3u) * .5f;
    const int view_width = wide_width > 0 ? wide_width : width;
    // Keep original physical 4:3 proportions; an authored pixel need not be
    // square (N2O uses both 320- and 368-column display modes).
    const float sx = (320.f / width) * step * view_width / dw;
    const float sy = (240.f / height) * step * height / dh;
    *x = ox + ax * view_width - wide_offset + (*x - ox - ax * width) * sx;
    *y = oy + ay * height + (*y - oy - ay * height) * sy;
}
