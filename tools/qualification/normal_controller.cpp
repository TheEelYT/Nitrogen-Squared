// Original SDL fixture linked separately from unmodified production objects.
#include "psx_sdl.h"
#include "gpu.h"
#include "gpu_gl_renderer.h"
#include <cstdio>
#include <cstdint>
extern "C" uint64_t s_frame_count;
extern "C" bool __real_SDL_PollEvent(SDL_Event*);
extern "C" {int sio_get_pad_analog(int);void sio_get_pad_sticks(int,uint8_t*);uint16_t sio_get_pad_buttons_slot(int);}
namespace {
void capture(uint64_t frame) {
    static uint16_t vram[1024*512];GpuDisplayInfo info{};gpu_get_display_info(&info);
    if(!gl_renderer_fbo_peek(0,0,1024,512,vram))return;
    char name[64];std::snprintf(name,sizeof name,"normal-frame-%llu.ppm",(unsigned long long)frame);
    FILE*f=std::fopen(name,"wb");if(!f)return;
    std::fprintf(f,"P6\n%u %u\n255\n",info.width,info.height);
    for(uint32_t y=0;y<info.height;y++)for(uint32_t x=0;x<info.width;x++) {
        uint8_t rgb[3];gpu_display_pixel_rgb_in(vram,&info,x,y,&rgb[0],&rgb[1],&rgb[2]);std::fwrite(rgb,3,1,f);
    }
    std::fclose(f);
}
SDL_Joystick*pad=nullptr;
uint64_t last_frame=~uint64_t(0);
bool quit_sent=false;
}
extern "C" bool __wrap_SDL_PollEvent(SDL_Event*event) {
    if(!pad) {
        SDL_VirtualJoystickDesc desc;SDL_INIT_INTERFACE(&desc);desc.type=SDL_JOYSTICK_TYPE_GAMEPAD;
        desc.naxes=SDL_GAMEPAD_AXIS_COUNT;desc.nbuttons=SDL_GAMEPAD_BUTTON_COUNT;
        desc.axis_mask=(1u<<SDL_GAMEPAD_AXIS_COUNT)-1;desc.button_mask=(1u<<SDL_GAMEPAD_BUTTON_COUNT)-1;
        desc.name="Original production controller fixture";
        pad=SDL_OpenJoystick(SDL_AttachVirtualJoystick(&desc));
        if(!pad){std::fprintf(stderr,"NORMAL_SMOKE pad failed: %s\n",SDL_GetError());return __real_SDL_PollEvent(event);}
    }
    const uint64_t frame=s_frame_count;
    if(frame!=last_frame) {
        last_frame=frame;
        for(int i=0;i<SDL_GAMEPAD_BUTTON_COUNT;i++)SDL_SetJoystickVirtualButton(pad,i,false);
        for(int n=0;n<6;n++)if(frame>=uint64_t(1800+n*200) && frame<uint64_t(1820+n*200))
            SDL_SetJoystickVirtualButton(pad,n==4?SDL_GAMEPAD_BUTTON_NORTH:SDL_GAMEPAD_BUTTON_SOUTH,true);
        if(frame>=3000)SDL_SetJoystickVirtualButton(pad,SDL_GAMEPAD_BUTTON_SOUTH,true);
        if((frame>=3600 && frame<3620)||(frame>=3800 && frame<3820))SDL_SetJoystickVirtualButton(pad,SDL_GAMEPAD_BUTTON_START,true);
        SDL_SetJoystickVirtualAxis(pad,SDL_GAMEPAD_AXIS_LEFTX,(frame>=3200 && frame<3380)?24000:(frame>=3400 && frame<3580)?-24000:0);
        SDL_UpdateJoysticks();
        if(frame==3000 || frame==4000)capture(frame);
        if(frame==3300 || frame==3500){uint8_t sticks[4];sio_get_pad_sticks(0,sticks);std::fprintf(stdout,"NORMAL_SMOKE sampled pad type=%d buttons=%04X lx=%u ly=%u frame=%llu\n",sio_get_pad_analog(0),sio_get_pad_buttons_slot(0),sticks[0],sticks[1],(unsigned long long)frame);}
        if(frame%500==0){std::fprintf(stdout,"NORMAL_SMOKE frame=%llu\n",(unsigned long long)frame);std::fflush(stdout);}
    }
    if(frame>=4500 && !quit_sent){quit_sent=true;*event={};event->type=SDL_EVENT_QUIT;std::fprintf(stdout,"NORMAL_SMOKE requested SDL_QUIT at frame=%llu\n",(unsigned long long)frame);return true;}
    return __real_SDL_PollEvent(event);
}
