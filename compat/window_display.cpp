#include "window_display.h"
#include <algorithm>
#include <atomic>
#include <cmath>
namespace {
// One atomic pair: a render worker never sees half of a resize.
std::atomic<unsigned long long> drawable{0};
std::atomic<int> ui_scale{0};
std::atomic<unsigned long long> world_size{0};
std::atomic<unsigned> menu_page{0};
}
extern "C" void nitrogen_window_menu_page(unsigned page) { menu_page.store(page, std::memory_order_release); }
extern "C" int nitrogen_window_controls_view(void) { return menu_page.load(std::memory_order_acquire)==8; }
extern "C" int nitrogen_window_projection_is_ui(int32_t ofx,int32_t ofy,int h)
{
    if(ofx==40*65536 && ofy==199*65536 && h==320) return 1;
    return nitrogen_window_controls_view() && ofx==184*65536 && ofy==120*65536 && h==320;
}
extern "C" void nitrogen_window_publish(int width, int height)
{
    drawable.store((static_cast<unsigned long long>(std::max(0, width)) << 32) |
                   static_cast<unsigned>(std::max(0, height)), std::memory_order_release);
}
extern "C" int nitrogen_window_ui_step(int width, int height)
{
    const int manual = ui_scale.load(std::memory_order_acquire);
    if (manual) return manual;
    // Square source pixels, with the owner's requested 2x minimum.
    return std::max(2, std::min(width / 365, height / 240));
}
extern "C" void nitrogen_window_ui_scale(int step)
{
    if (step == 0 || step == 2 || step == 3 || step == 4 || step == 6)
        ui_scale.store(step, std::memory_order_release);
}
extern "C" void nitrogen_window_world_raster(int width,int height,int sw,int sh,int percent)
{
    if (sw!=364 || sh<1 || width<1 || height<1) { world_size=0; return; }
    const int viewport_w=static_cast<long long>(width)*3<static_cast<long long>(height)*4?height*4/3:width;
    const unsigned w=static_cast<unsigned>((static_cast<long long>(viewport_w)*percent*1024+100*sw-1)/(100*sw));
    const unsigned h=static_cast<unsigned>((static_cast<long long>(height)*percent*512+100*sh-1)/(100*sh));
    world_size.store((static_cast<unsigned long long>(w)<<32)|h,std::memory_order_release);
}
extern "C" void nitrogen_window_world_size(int *width,int *height)
{
    const auto size=world_size.load(std::memory_order_acquire);
    *width=static_cast<int>(size>>32); *height=static_cast<unsigned>(size);
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
