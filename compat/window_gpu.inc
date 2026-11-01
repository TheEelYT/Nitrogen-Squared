/* Original USA UI roles. The authored drawing canvas is 368x240; its
 * CRTC scanout is 364 pixels wide in this pinned runtime. Record the actual
 * scanout height with each primitive, including centre-screen adjustments.
 * Bits0..3 belong to the renderer; bit4 is UI, bits5..7 are a shared role,
 * bits8..15 carry source height. No game instructions or image bytes. */
static unsigned nitrogen_ui_role(unsigned role, int ui)
{
    GpuDisplayInfo di; gpu_get_display_info(&di);
    if (di.width != 364 || !di.height || di.height > 255) return 0;
    return (ui ? 0x10u : 0u) | (role << 5) | (di.height << 8);
}
static int nitrogen_widget_vertices(unsigned op, int xlo, int xhi, int ylo, int yhi)
{
    const int n = (op & 8u) ? 4 : 3;
    const int stride = 1 + ((op & 4u) ? 1 : 0) + ((op & 16u) ? 1 : 0);
    for (int i = 0; i < n; i++) {
        int32_t x,y; parse_vertex(gp0_cmd_buf[1+i*stride],&x,&y);
        if (x<xlo || x>xhi || y<ylo || y>yhi) return 0;
    }
    return 1;
}
unsigned nitrogen_gpu_ui_flags(void)
{
    if (gp0_state == GP0_POLYLINE_MONO || gp0_state == GP0_POLYLINE_SHADED) return 0;
    const unsigned op = gp0_cmd_buf[0] >> 24;
    const int polygon = op >= 0x20u && op <= 0x3fu;
    if (polygon && (gp0_ot_rank == 427u || gp0_ot_rank == 428u) &&
        nitrogen_widget_vertices(op,-16,112,128,255)) return nitrogen_ui_role(3,1);
    if (polygon && gp0_ot_rank == 3u && op == 0x3au &&
        !(gp0_cmd_buf[0]&0xffffffu) && !(gp0_cmd_buf[2]&0xffffffu) &&
        nitrogen_widget_vertices(op,16,352,-32,255)) return nitrogen_ui_role(0,1);
    if (polygon && gp0_ot_rank == 441u && !(op & 4u) &&
        nitrogen_widget_vertices(op,16,352,-32,160)) return nitrogen_ui_role(0,1);
    if (op>=0x60u && op<=0x63u && gp0_ot_rank==441u) return nitrogen_ui_role(0,1);
    const int rect = op >= 0x64u && op <= 0x7fu && (op & 4u);
    const int textured_quad = op >= 0x2cu && op <= 0x2fu;
    const unsigned palette = (rect || textured_quad) ? gp0_cmd_buf[2] >> 16 : 0;
    int32_t x=0,y=0;
    if (rect || textured_quad) parse_vertex(gp0_cmd_buf[1],&x,&y);
    const int weapon_frame = rect && (palette == 0x7a27u || palette == 0x76e7u || palette == 0x7667u) &&
        gp0_ot_rank == 440u && x>=-16 && x<=112 && y>=128 && y<=255;
    // The bonus-weapon atlas and the shield/firewall atlas are distinct.
    // Their counters share the panel; palette similarity is not ownership.
    const int perk = rect && gp0_ot_rank == 440u && x>=0 && x<=192 && y>=160 && y<=239 &&
        (((palette & 63u)==36u && palette>=0x7a24u && palette<=0x7be4u) ||
         palette==0x4ba1u || palette==0x73b2u || palette==0x73f2u);
    const int weapon_flash = rect && gp0_ot_rank==440u &&
        x>=-16 && x<=112 && y>=128 && y<=255 &&
        (palette&63u)==51u && palette>=0x48b3u && palette<=0x4cb3u;
    const int tutorial_icon = rect && palette == 0x3ba0u && gp0_ot_rank == 441u;
    const int font = palette == 0x4873u || palette == 0x4d33u ||
        palette == 0x4d73u || palette == 0x4db3u || palette == 0x73b3u || palette == 0x73f3u;
    const int menu_art = rect && ((palette & 63u) == 55u ||
        (palette == 0x5765u && gp0_ot_rank == 438u)) &&
        ((palette >= 0x5837u && palette <= 0x5ff7u) || palette == 0x5765u) &&
        (gp0_ot_rank == 438u || gp0_ot_rank == 440u);
    const int menu_marker = rect && palette == 0 && current_texpage() == 0x13cu && gp0_ot_rank == 440u;
    if (rect && palette == 0 && current_texpage() == 0x13cu && gp0_ot_rank == 2u)
        return nitrogen_ui_role(6,0); // ray field only, never footer decorations
    const int atlas = ((rect || textured_quad) && font) || weapon_frame || weapon_flash || perk || tutorial_icon || menu_art || menu_marker;
    const WsUiPrepassItem *it = atlas ? NULL : ws_auto_ui_item();
    if (!atlas && (!it || !it->full_draw_area || !ws_ui_untextured_op(it->op))) return 0;
    // Centre is one transform for complete phrases, shadows, panels and menu
    // art. No individual glyph chooses a different anchor by crossing mid-screen.
    unsigned role=0;
    if (palette == 0x4d33u) role=2;
    // HUD and opaque menu shadows share a palette and draw rank. Identify
    // the HUD atlas cells, never arbitrary letters by their screen position.
    const unsigned u=gp0_cmd_buf[2]&255u, v=(gp0_cmd_buf[2]>>8)&255u;
    const unsigned w=op>=0x64u && op<=0x67u ? gp0_cmd_buf[3]&65535u : 0u;
    const unsigned h=op>=0x64u && op<=0x67u ? gp0_cmd_buf[3]>>16 : 0u;
    const int digits=(v==32u && u<80u && w==8u && h==16u) ||
        (v==88u && u>=64u && u<124u && w==6u && h==8u);
    const int hud_symbol=(v==60u && u>=80u && w<=16u && h<=16u) ||
        (u==76u && v==54u && w==51u && h==6u) ||
        (u==120u && v==61u && w==7u && h==8u);
    const int bonus_star=u==120u && v==61u && w==7u && h==8u;
    if (palette==0x4873u && rect && (digits || hud_symbol)) {
        if (y<=64) role=bonus_star || x<128 ? 1u : 2u;
        else if (digits && x>=0 && x<=192 && y>=160 && y<=239) role=3;
    }
    const int multiplier=rect && palette==0x4873u && w==8u && h==15u &&
        ((v==144u && u>=64u && u<144u) || (u==118u && v==128u));
    if (multiplier && x>=16 && x<=56 && y>=192 && y<=223) role=3;
    // The bonus speed readout shares menu-art palettes. Match its exact cells
    // inside the weapon panel; its backing and all digits use one anchor.
    const int speed_readout=rect && gp0_ot_rank==440u &&
        x>=-16 && x<=112 && y>=128 && y<=255 &&
        ((palette==0x5eb7u && v==55u && u>=196u && u<=232u &&
          (u-196u)%4u==0u && w==4u && h==7u) ||
         (palette==0x5fb7u && u==224u && v==0u && w==32u && h==32u));
    if (weapon_frame || weapon_flash || perk || speed_readout) role=3;
    // Footer plates start at 205. The complete password row (including its
    // shadows at 204) is centred immediately above them, never edge anchored.
    if (gp0_ot_rank == 440u &&
        ((menu_marker && y>=160 && y<=255) || (!menu_marker && y>=205 && y<=239)) &&
        (palette==0x4873u || palette==0x4d73u || palette==0x4db3u || menu_marker)) {
        if (x>=0 && x<=112) role=3;
        else if (x>=244 && x<=368) role=4;
    }
    return nitrogen_ui_role(role,1);
}
void nitrogen_gpu_enable_ui(void) { ws_auto_ui_squash = 1; }
unsigned nitrogen_gpu_line_flags(int x0,int y0,int x1,int y1)
{
    x0-=draw_offset_x; x1-=draw_offset_x; y0-=draw_offset_y; y1-=draw_offset_y;
    if ((gp0_ot_rank==427u || gp0_ot_rank==428u) &&
        x0>=-16 && x0<=112 && x1>=-16 && x1<=112 &&
        y0>=128 && y0<=255 && y1>=128 && y1<=255) return nitrogen_ui_role(3,1);
    // Streaming polylines do not populate gp0_cmd_buf: use their live state.
    if (gp0_ot_rank==440u && gp0_state==GP0_POLYLINE_SHADED &&
        x0>=-16 && x0<=112 && x1>=-16 && x1<=112 &&
        y0>=128 && y0<=255 && y1>=128 && y1<=255) return nitrogen_ui_role(3,1);
    if (gp0_ot_rank==441u) return nitrogen_ui_role(0,1);
    return 0;
}
