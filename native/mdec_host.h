#pragma once
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
void nitrogen_mdec_start(const uint8_t quant[64], const int16_t scale[64]);
void nitrogen_mdec_finish(void);
int nitrogen_mdec_decode(const uint16_t *words, size_t count, uint8_t *rgb, size_t bytes);
#ifdef __cplusplus
}
#endif
