/* Included only in a private copy of the pinned GPU implementation. The
 * read-only packet guard and front-layer grouping remain the toolkit's.
 * These flags accompany each recorded primitive; never query guest state on
 * the GL worker. Bits 0..3 remain owned by the pinned backdrop protocol. */
unsigned nitrogen_gpu_ui_flags(void)
{
    const WsUiPrepassItem *it = ws_auto_ui_item();
    if (!it || !it->full_draw_area) return 0;
    const int width = (int)ws_disp_w();
    if (width < 4 || width > 508 || width % 4) return 0;
    unsigned ax = it->group.anchor <= ws_disp_x() ? 0u :
                  it->group.anchor >= ws_disp_x() + width ? 2u : 1u;
    unsigned ay = ws_auto_ui_dense ? 1u :
                  (it->y + it->h / 2 < ws_disp_h() / 2 ? 0u : 2u);
    return 0x10u | (ax << 5) | (ay << 7) | ((unsigned)(width / 4) << 9);
}

void nitrogen_gpu_enable_ui(void) { ws_auto_ui_squash = 1; }
