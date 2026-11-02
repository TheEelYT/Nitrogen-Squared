/* Original variable-resolution world target. Included only in a guarded copy
 * of the pinned renderer, on its GL owner. The canonical VRAM remains full
 * resolution: ordered handoffs resolve world draws before UI, CPU uploads,
 * copies, readbacks or presentation access it. */
static GLuint nitrogen_world_fbo, nitrogen_world_tex, nitrogen_world_rb;
static int nitrogen_world_width, nitrogen_world_height;
static int nitrogen_world_selected, nitrogen_world_pending;

static void nitrogen_world_blit(GLuint from,GLuint to,int fw,int fh,int tw,int th)
{
    glDisable(GL_SCISSOR_TEST);
    p_glBindFramebuffer(PSXGL_READ_FRAMEBUFFER,from);
    p_glBindFramebuffer(PSXGL_DRAW_FRAMEBUFFER,to);
    p_glBlitFramebuffer(0,0,fw,fh,0,0,tw,th,
        GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT|GL_STENCIL_BUFFER_BIT,GL_NEAREST);
}
static void nitrogen_world_resolve(void)
{
    if (!nitrogen_world_pending) return;
    nitrogen_world_pending=0;
    nitrogen_world_blit(nitrogen_world_fbo,s_hr_fbo,nitrogen_world_width,nitrogen_world_height,
                        VRAM_W*s_hr_scale,VRAM_H*s_hr_scale);
}
static void nitrogen_world_delete(void)
{
    nitrogen_world_resolve();
    if(nitrogen_world_fbo) p_glDeleteFramebuffers(1,&nitrogen_world_fbo);
    if(nitrogen_world_tex) glDeleteTextures(1,&nitrogen_world_tex);
    if(nitrogen_world_rb) p_glDeleteRenderbuffers(1,&nitrogen_world_rb);
    nitrogen_world_fbo=nitrogen_world_tex=nitrogen_world_rb=0;
    nitrogen_world_width=nitrogen_world_height=0;
}
static int nitrogen_world_begin(int clip)
{
    int width=0,height=0;
    nitrogen_window_world_size(&width,&height);
    if(!clip || !nitrogen_world_selected || width<1 || height<1 || s_hiw ||
       g_wide_cur || s_pass_active || s_cpu_auth_dual || s_hd_native_authority) return 0;
    if(width!=nitrogen_world_width || height!=nitrogen_world_height) {
        GLint limit=0;
        glGetIntegerv(GL_MAX_TEXTURE_SIZE,&limit);
        if(width>limit || height>limit) return 0;
        nitrogen_world_delete();
        nitrogen_world_tex=make_tex(GL_RGBA8,width,height,GL_RGBA,GL_UNSIGNED_BYTE);
        p_glGenRenderbuffers(1,&nitrogen_world_rb);
        p_glBindRenderbuffer(PSXGL_RENDERBUFFER,nitrogen_world_rb);
        p_glRenderbufferStorage(PSXGL_RENDERBUFFER,PSXGL_DEPTH24_STENCIL8,width,height);
        p_glBindRenderbuffer(PSXGL_RENDERBUFFER,0);
        if(!make_fbo(&nitrogen_world_fbo,nitrogen_world_tex,nitrogen_world_rb)) {
            nitrogen_world_delete(); return 0;
        }
        nitrogen_world_width=width; nitrogen_world_height=height;
    }
    if(!nitrogen_world_pending) {
        nitrogen_world_blit(s_hr_fbo,nitrogen_world_fbo,VRAM_W*s_hr_scale,VRAM_H*s_hr_scale,width,height);
        nitrogen_world_pending=1;
    }
    p_glBindFramebuffer(PSXGL_FRAMEBUFFER,nitrogen_world_fbo);
    glViewport(0,0,width,height);
    glEnable(GL_SCISSOR_TEST);
    const int x1=s_area_x1*width/VRAM_W, y1=s_area_y1*height/VRAM_H;
    const int x2=(s_area_x2+1)*width/VRAM_W, y2=(s_area_y2+1)*height/VRAM_H;
    glScissor(x1,y1,x2>x1?x2-x1:0,y2>y1?y2-y1:0);
    return 1;
}
static void nitrogen_bind_framebuffer(GLenum target,GLuint framebuffer)
{
    if(framebuffer && framebuffer==s_hr_fbo) nitrogen_world_resolve();
    p_glBindFramebuffer(target,framebuffer);
}
/* All later canonical surface accesses pass through this fence. Our own blits
 * above use the original pointer and therefore cannot recurse into the fence. */
#define p_glBindFramebuffer nitrogen_bind_framebuffer

static void nitrogen_world_select(unsigned flags)
{
    const int world=(flags&0x10u)==0;
    if(world==nitrogen_world_selected) return;
    flush_tex_batch(); flush_flat_batch();
    nitrogen_world_selected=world;
}
