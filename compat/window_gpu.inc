/* Original N2O presentation metadata. Palette column 816 contains the shared
 * screen font and UI atlases in the verified USA import, including menu text
 * submitted below the front ordering-table layer. World sprite atlases use
 * other palette columns. No instructions, texels or palette bytes are stored.
 * Bits 0..3 remain owned by the pinned renderer's backdrop protocol. */
unsigned nitrogen_gpu_ui_flags(void)
{
    if (gp0_state == GP0_POLYLINE_MONO || gp0_state == GP0_POLYLINE_SHADED) return 0;
    const int width = (int)ws_disp_w();
    if (width < 4 || width > 508 || width % 4) return 0;
    const unsigned op = gp0_cmd_buf[0] >> 24;
    // The lower-left weapon preview is a projected model in two reserved
    // UI ordering buckets, not a font sprite. Require the complete authored
    // widget bounds as well, so ordinary depth-sorted models stay untouched.
    if (op >= 0x20u && op <= 0x3fu &&
        (gp0_ot_rank == 427u || gp0_ot_rank == 428u)) {
        const int n = (op & 8u) ? 4 : 3;
        const int stride = 1 + ((op & 4u) ? 1 : 0) + ((op & 16u) ? 1 : 0);
        int widget = 1;
        for (int i = 0; i < n; i++) {
            int32_t x, y; parse_vertex(gp0_cmd_buf[1 + i * stride], &x, &y);
            if (x < -16 || x > 112 || y < 128 || y > 255) widget = 0;
        }
        if (widget) return 0x10u | (2u << 7) | ((unsigned)(width / 4) << 9);
    }
    const int rect = op >= 0x64u && op <= 0x7fu && (op & 4u);
    const int textured_quad = op >= 0x2cu && op <= 0x2fu;
    const unsigned palette = (rect || textured_quad) ? gp0_cmd_buf[2] >> 16 : 0;
    int32_t packet_x = 0, packet_y = 0;
    if (rect || textured_quad) parse_vertex(gp0_cmd_buf[1], &packet_x, &packet_y);
    const int weapon_frame = rect && (palette == 0x7a27u || palette == 0x76e7u) &&
        gp0_ot_rank == 440u && packet_x >= -16 && packet_x <= 112 &&
        packet_y >= 128 && packet_y <= 255;
    const int tutorial_icon = rect && palette == 0x3ba0u && gp0_ot_rank == 441u &&
        packet_x >= 48 && packet_x <= 304 && packet_y >= 90 && packet_y <= 120;
    const int atlas = ((rect || textured_quad) && (palette & 63u) == 51u) ||
        weapon_frame || tutorial_icon;
    const WsUiPrepassItem *it = atlas ? NULL : ws_auto_ui_item();
    // Unrecognized textured sprites may be world particles even in a front
    // layer. The fallback is only for a grouped flat UI backing panel.
    if (!atlas && (!it || !it->full_draw_area || !ws_ui_untextured_op(it->op))) return 0;
    int32_t x, y;
    if (atlas) parse_vertex(gp0_cmd_buf[1], &x, &y);
    else { x = it->group.x; y = it->y; }
    unsigned ax = 1, ay = y < 48 ? 0u : y >= 192 ? 2u : 1u;
    if (y >= 192) ax = x < width / 2 ? 0u : 2u;
    // Keep the complete score/coin/lives stack at the upper left, the progress
    // bar centred, and the weapon frame with its model at the lower left.
    // Tutorial text/icons share the backing panel's top-centred transform.
    if (palette == 0x4d33u) { ax = 1; ay = 0; } // centred progress bar
    if (palette == 0x4873u && gp0_ot_rank == 440u &&
        x >= 16 && x < 100 && y >= 12 && y <= 64) { ax = 0; ay = 0; }
    if (weapon_frame) { ax = 0; ay = 2; }
    if (palette == 0x73b3u || tutorial_icon) { ax = 1; ay = 0; }
    if (it && it->group.width > width / 2 && it->y < 60 && it->h < 120) {
        ax = 1; ay = 0;
    }
    return 0x10u | (ax << 5) | (ay << 7) | ((unsigned)(width / 4) << 9);
}

void nitrogen_gpu_enable_ui(void) { ws_auto_ui_squash = 1; }

// Variable-length polylines do not populate gp0_cmd_buf. Classify the actual
// segment endpoints, including draw offsets, and serialize the result normally.
unsigned nitrogen_gpu_line_flags(int x0, int y0, int x1, int y1)
{
    const int width = (int)ws_disp_w();
    if (width < 4 || width > 508 || width % 4 ||
        (gp0_ot_rank != 427u && gp0_ot_rank != 428u)) return 0;
    x0 -= draw_offset_x; x1 -= draw_offset_x;
    y0 -= draw_offset_y; y1 -= draw_offset_y;
    if (x0 < -16 || x0 > 112 || x1 < -16 || x1 > 112 ||
        y0 < 128 || y0 > 255 || y1 < 128 || y1 > 255) return 0;
    return 0x10u | (2u << 7) | ((unsigned)(width / 4) << 9);
}
