#!/usr/bin/env python3
"""Adapt a pinned private renderer copy; never edit the framework checkout."""
from pathlib import Path
import argparse


def replace(text, old, new, count=1):
    if text.count(old) != count:
        raise ValueError(f"Pinned display contract changed: {old[:100]!r}")
    return text.replace(old, new)


def adapt_gpu(text):
    # Classification runs at native and native-wide too. Existing integer CPU
    # coordinate correction stays off: host-only float vertices own this policy.
    text = replace(text, 'if (!ws_auto_ui_squash || !ws_active() ||',
                   'if (!ws_auto_ui_squash ||', 1)
    text = replace(text, 'if (!ws_auto_ui_squash || !ws_active()) return;',
                   'if (!ws_auto_ui_squash) return;')
    for sig in ('static int ws_auto_ui_transform_part(int32_t *vx, int32_t *vy, int n) {',
                'static int ws_auto_ui_transform_quad(int32_t vx[4], int32_t vy[4]) {',
                'static int ws_auto_ui_transform_rect(int32_t *x, int32_t *y, int *w, int *h) {'):
        text = replace(text, sig, sig + '\n    return 0; /* Nitrogen: GL-only UI correction. */')
    # N2O's 364x238 game/menu mode has 3D backgrounds. Its 320/640-column
    # logos and image screens retain their authored 4:3 framing.
    text = replace(text, 'int gpu_ws_present_native_43(void) {',
        'int gpu_ws_present_native_43(void) {\n'
        '    GpuDisplayInfo nitrogen_di; gpu_get_display_info(&nitrogen_di);\n'
        '    if (nitrogen_di.width == 364 && nitrogen_di.height == 238 &&\n'
        '        !nitrogen_di.depth24) return 0;\n'
        '    if (nitrogen_di.width != 364) return 1;')
    return text + '\n#include "window_gpu.inc"\n'



def adapt_renderer(text):
    text = '#include "window_display.h"\nextern unsigned nitrogen_gpu_ui_flags(void);\nextern unsigned nitrogen_gpu_line_flags(int,int,int,int);\n' + text
    text = replace(text, 'static int       s_rthx_tagged = 0, s_rthx_backdrop = 0;',
                   'static int       s_rthx_tagged = 0, s_rthx_backdrop = 0;\nstatic unsigned nitrogen_replay_ui;')
    marker = 'static void gpu_geometry(GLenum mode, const int *xs, const int *ys,'
    helper = '''static void nitrogen_ui_vertex_flags(float *x, float *y, unsigned flags) {
    nitrogen_window_ui_vertex(x, y, flags, s_area_x1, s_area_y1,
        (flags >> 9) == 91u ? 238 : s_area_y2 - s_area_y1 + 1,
        g_wide_cur ? g_wide_w : 0, g_wide_cur ? g_wide_off : 0);
}
static void nitrogen_ui_vertex(float *x, float *y) {
    nitrogen_ui_vertex_flags(x, y, rth_replaying() ? nitrogen_replay_ui : nitrogen_gpu_ui_flags());
}

'''
    text = replace(text, marker, helper + marker)
    # Both flat paths and the textured path. Position-only changes preserve UV,
    # painter order, blending, uploads, readbacks and the guest packet bytes.
    for xs, ys, ptr in [('precise ? s_pc_x[i] : (float)xs[i]', 'precise ? s_pc_y[i] : (float)ys[i]', 'verts[i*6+'),
                         ('precise ? s_pc_x[i] : (float)xs[i]', 'precise ? s_pc_y[i] : (float)ys[i]', 'v['),
                         ('s_pc_valid ? s_pc_x[i] : (float)xs[i]', 's_pc_valid ? s_pc_y[i] : (float)ys[i]', 'vp[')]:
        old = f'{ptr}1] = {ys};'
        new = old + (f'\n            nitrogen_ui_vertex(&{ptr}0], &{ptr}1]);' if ptr == 'vp[' else f'\n            nitrogen_ui_vertex_flags(&{ptr}0], &{ptr}1], nitrogen_geometry_ui);')
        text = replace(text, old, new)
    text = replace(text,
        '    const int precise = s_pc_valid && mode == GL_TRIANGLES && n == 3;',
        '    const int precise = s_pc_valid && mode == GL_TRIANGLES && n == 3;\n'
        '    const unsigned nitrogen_geometry_ui = rth_replaying() ? nitrogen_replay_ui :\n'
        '        mode == GL_LINES && n == 2 ? nitrogen_gpu_line_flags(xs[0],ys[0],xs[1],ys[1]) : nitrogen_gpu_ui_flags();')
    text = replace(text, '            v[1] = (float)ys[i];',
        '            v[1] = (float)ys[i];\n'
        '            nitrogen_ui_vertex_flags(&v[0], &v[1], nitrogen_geometry_ui);')
    text = replace(text, '        line_to_quad(lv, quad);',
        '        line_to_quad(lv, quad);\n'
        '        for (int i=0;i<6;i++) nitrogen_ui_vertex_flags(&quad[i*6], &quad[i*6+1], nitrogen_geometry_ui);\n'
        '        for (int i=0;i<2;i++) nitrogen_ui_vertex_flags(&lv[i*6], &lv[i*6+1], nitrogen_geometry_ui);')
    for record in ['RTH_REC(RTH_LINE, rth_prim_flags(),', 'RTH_REC(RTH_SHADED_LINE, rth_prim_flags(),']:
        text = replace(text, record, record.replace('rth_prim_flags()',
            '(rth_prim_flags() | nitrogen_gpu_line_flags(x0,y0,x1,y1))'))
    text = replace(text, 'if (s_rthm_wide_w <= 0 || !g_ws_bd_stretch_on) return 0;\n    uint16_t f = RTHF_PRIM;',
                   'uint16_t ui = (uint16_t)nitrogen_gpu_ui_flags();\n    if (s_rthm_wide_w <= 0 || !g_ws_bd_stretch_on) return ui;\n    uint16_t f = RTHF_PRIM | ui;')
    for field in ['h.flags', 'c->flags']:
        old = f's_rthx_backdrop = ({field} >> RTHF_BD_SHIFT) & 3;'
        text = replace(text, old, old + f'\n    nitrogen_replay_ui = {field} & 0xfff0u;')
    # Only function reset statements; do not alter the static initializer.
    text = replace(text, '\n    s_rthx_prim = 0;', '\n    s_rthx_prim = 0;\n    nitrogen_replay_ui = 0;', 2)
    # Nearest presentation also means no implicit supersampling area average.
    text = replace(text, 'if (src_scale > 1 && lw > 0 && lh > 0 && w > 0 && h > 0) {',
                   'if (linear && src_scale > 1 && lw > 0 && lh > 0 && w > 0 && h > 0) {')
    text = replace(text,
        '    letterbox_rect_aspect(ww, wh, s_aspect_num, s_aspect_den, x, y, w, h);',
        '    extern void nitrogen_menu_world_letterbox(int,int,int,int,int*,int*,int*,int*);\n'
        '    nitrogen_menu_world_letterbox(ww, wh, s_aspect_num, s_aspect_den, x, y, w, h);')
    return text


def adapt_main(text):
    # Below 4:3, crop the authentic projection at presentation. Expanding GTE X
    # does not correct N2O's unprojected backdrop/feedback geometry.
    text = replace(text,
        '    gte_set_display_aspect(mode == 1 ? proj_num : 4,\n'
        '                           mode == 1 ? proj_den : 3);',
        '    const bool nitrogen_narrow = (int64_t)proj_num * 3 < (int64_t)proj_den * 4;\n'
        '    gte_set_display_aspect(mode == 1 && !nitrogen_narrow ? proj_num : 4,\n'
        '                           mode == 1 && !nitrogen_narrow ? proj_den : 3);')
    text = replace(text,
        '    gpu_ws_configure(proj_num, proj_den, g_ws_anchor_addr,\n'
        '                     g_ws_hud_sprt ? 1 : 0, mode);',
        '    gpu_ws_configure(nitrogen_narrow ? 4 : proj_num, nitrogen_narrow ? 3 : proj_den,\n'
        '                     g_ws_anchor_addr, g_ws_hud_sprt ? 1 : 0, nitrogen_narrow ? 0 : mode);')
    start = text.index('static void update_adaptive_widescreen() {')
    end = text.index('\n/* SDL GL attributes', start)
    return text[:start] + 'static void update_adaptive_widescreen() { nitrogen_window_update(); }\n' + text[end:]


def adapt_gte(text):
    text = '#include "window_display.h"\n' + text
    return replace(text,
        '    bool do_squash = (s_ws_xnum != s_ws_xden) && !gpu_ws_present_native_43();',
        '    bool do_squash = (s_ws_xnum != s_ws_xden) && !gpu_ws_present_native_43() &&\n'
        '        !nitrogen_window_projection_is_ui(gte->OFX, gte->OFY, gte->H);')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('kind', choices=['gpu', 'renderer', 'main', 'gte'])
    p.add_argument('source', type=Path); p.add_argument('output', type=Path)
    a = p.parse_args()
    result = globals()['adapt_' + a.kind](a.source.read_text(encoding="utf-8"))
    if not a.output.exists() or a.output.read_text(encoding="utf-8") != result:
        a.output.write_text(result, encoding="utf-8")


if __name__ == '__main__':
    main()
