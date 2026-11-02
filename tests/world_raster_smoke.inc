/* Original GL regression, included in a private copy of the pinned synthetic
 * fixture. All pixels and primitives here are invented, with no game input. */
static unsigned nitrogen_test_flags;
unsigned nitrogen_gpu_ui_flags(void) { return nitrogen_test_flags; }
unsigned nitrogen_gpu_line_flags(int a,int b,int c,int d)
{ (void)a;(void)b;(void)c;(void)d;return nitrogen_test_flags; }
void nitrogen_menu_world_letterbox(int ww,int wh,int n,int d,int*x,int*y,int*w,int*h)
{
    int dw=ww,dh=ww*d/n;
    if(dh>wh){dh=wh;dw=wh*n/d;}
    *x=(ww-dw)/2;*y=(wh-dh)/2;*w=dw;*h=dh;
}
static void nitrogen_test_read(int x,int y,int w,int h,uint32_t *pixels)
{
    flush_tex_batch();flush_flat_batch();
    p_glBindFramebuffer(PSXGL_FRAMEBUFFER,s_hr_fbo);
    glReadPixels(x*s_hr_scale,y*s_hr_scale,w*s_hr_scale,h*s_hr_scale,
                 GL_RGBA,GL_UNSIGNED_BYTE,pixels);
}
static void nitrogen_world_smoke(void)
{
    const int scale=s_hr_scale;
    const size_t scene_bytes=(size_t)160*180*scale*scale*4;
    const size_t ui_bytes=(size_t)32*32*scale*scale*4;
    uint32_t *world_a=malloc(scene_bytes),*world_b=malloc(scene_bytes);
    uint32_t *ui_a=malloc(ui_bytes),*ui_b=malloc(ui_bytes);
    uint16_t atlas[16*16],atlas_before[16*16],atlas_after[16*16];
    check(world_a&&world_b&&ui_a&&ui_b,"world raster capture storage");
    if(!world_a||!world_b||!ui_a||!ui_b)exit(2);
    glb_wide_configure(0,0);
    s_pc_valid=s_pq_valid=0;
    glb_set_draw_area(0,0,363,239);glb_set_mask_bits(0,0);
    glb_set_semi_transparency(0,0);gl_renderer_select_texture_bank(0);
    nitrogen_window_publish(730,480);
    for(int i=0;i<256;++i)atlas[i]=(uint16_t)((i*73+17)&0x7fff);
    glb_vram_transfer_in(768,32,16,16,atlas);
    check(gl_renderer_fbo_peek(768,32,16,16,atlas_before),"synthetic atlas baseline");
    for(int pass=0;pass<2;++pass){
        nitrogen_window_world_raster(730,480,364,240,pass?100:50);
        nitrogen_test_flags=0;
        glb_fill_rect(0,0,364,240,0);
        glb_draw_gouraud_triangle(10,10,0x001f,160,61,0x001f,99,180,0x001f);
        nitrogen_test_flags=0x10u|(240u<<8);
        glb_draw_flat_rect(300,40,8,8,0x03e0);
        nitrogen_test_read(0,0,160,180,pass?world_b:world_a);
        nitrogen_test_read(290,30,32,32,pass?ui_b:ui_a);
        check(nitrogen_world_width>0&&nitrogen_world_height>0,"separate world target allocated");
        check(gl_renderer_fbo_peek(768,32,16,16,atlas_after),"synthetic atlas after world/UI handoff");
        check(!memcmp(atlas_before,atlas_after,sizeof atlas_before),"world resolve preserves texture/CLUT storage");
        check(glGetError()==GL_NO_ERROR,"world raster GL error");
    }
    check(memcmp(world_a,world_b,scene_bytes)!=0,"world raster percentage changes geometry sampling");
    check(!memcmp(ui_a,ui_b,ui_bytes),"UI pixels identical at 50 and 100 percent world resolution");
    nitrogen_window_world_raster(730,480,320,240,100);
    nitrogen_test_flags=0;
    free(world_a);free(world_b);free(ui_a);free(ui_b);
}
