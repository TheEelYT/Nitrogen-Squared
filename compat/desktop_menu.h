#pragma once

#ifdef __cplusplus
extern "C" {
#endif
void nitrogen_menu_letterbox(int ww, int wh, int num, int den,
                            int *x, int *y, int *w, int *h);
int nitrogen_menu_reserved_height(void);
#ifdef __cplusplus
}
#endif
