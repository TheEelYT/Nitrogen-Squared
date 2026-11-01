/* Original N2O presentation metadata. Palette column 816 contains the shared
 * screen font and UI atlases in the verified USA import, including menu text
 * submitted below the front ordering-table layer. World sprite atlases use
 * other palette columns. No instructions, texels or palette bytes are stored.
 * Bits 0..3 remain owned by the pinned renderer's backdrop protocol. */
unsigned nitrogen_gpu_ui_flags(void)
{
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
    const int atlas = (rect || textured_quad) && (palette & 63u) == 51u;
    const WsUiPrepassItem *it = atlas ? NULL : ws_auto_ui_item();
    // Unrecognized textured sprites may be world particles even in a front
    // layer. The fallback is only for a grouped flat UI backing panel.
    if (!atlas && (!it || !it->full_draw_area || !ws_ui_untextured_op(it->op))) return 0;
    int32_t x, y;
    if (atlas) parse_vertex(gp0_cmd_buf[1], &x, &y);
    else { x = it->group.x; y = it->y; }
    unsigned ax = 1, ay = y < 48 ? 0u : y >= 192 ? 2u : 1u;
    if (y >= 192) ax = x < width / 2 ? 0u : 2u;
    // The score/coin font is one widget at the upper left. Tutorial text
    // keeps one top-centred transform together with its backing panel.
    if (palette == 0x4d33u) { ax = 0; ay = 0; }
    if (palette == 0x73b3u) { ax = 1; ay = 0; }
    if (it && it->group.width > width / 2 && it->y < 60 && it->h < 120) {
        ax = 1; ay = 0;
    }
    return 0x10u | (ax << 5) | (ay << 7) | ((unsigned)(width / 4) << 9);
}

void nitrogen_gpu_enable_ui(void) { ws_auto_ui_squash = 1; }
