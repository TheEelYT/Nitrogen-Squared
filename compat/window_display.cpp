#include "window_display.h"
#include <algorithm>
#include <atomic>
#include <cmath>
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
    // Square source pixels, with the owner's requested 2x minimum.
    return std::max(2, std::min(width / 365, height / 240));
}
extern "C" void nitrogen_window_ui_vertex(float *x, float *y, unsigned flags,
                                           int ox, int oy, int height,
                                           int wide_width, int wide_offset)
{
    (void)height; (void)wide_width; (void)wide_offset;
    const bool ui = (flags & 0x10u) != 0;
    const unsigned role=(flags>>5)&7u;
    if (!ui && role!=6) return;
    const auto size=drawable.load(std::memory_order_acquire);
    const int dw=static_cast<int>(size>>32), dh=static_cast<unsigned>(size);
    const int source_h=(flags>>8)&255u;
    if (dw<1 || dh<1 || source_h<1) return;
    if (!ui) {
        if (static_cast<long long>(dw)*3>static_cast<long long>(dh)*4) {
            const float cover=static_cast<float>(dw)*3.f/(dh*4.f);
            *y=oy+source_h*.5f+(*y-oy-source_h*.5f)*cover;
        }
        return;
    }
    const float ax=(role==1 || role==3) ? 0.f : role==4 ? 1.f : .5f;
    const float ay=(role==1 || role==2) ? 0.f : (role==3 || role==4 || role==5) ? 1.f : .5f;
    const int step=nitrogen_window_ui_step(dw,dh);
    const int viewport_w=static_cast<long long>(dw)*3<static_cast<long long>(dh)*4 ? dh*4/3 : dw;
    // Map square-pixel UI through the actual present/crop, independently from
    // world projection. All parts of a role use the authored 368x240 pivot.
    const int viewport_x=(dw-viewport_w)/2;
    *x=ox+(std::floor(ax*dw)+(*x-ox-ax*368.f)*step-viewport_x)*364.f/viewport_w;
    *y=oy+(std::floor(ay*dh)+(*y-oy-ay*240.f)*step)*source_h/dh;
}
