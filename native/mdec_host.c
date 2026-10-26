/* An isolated DSP instance, included from the pinned framework at build time. */
#include "mdec_host.h"
#include <stdlib.h>
#include <string.h>
uint64_t nitrogen_media_cycle_count;
uint64_t nitrogen_media_frame_count;
#define psx_cycle_count nitrogen_media_cycle_count
#define s_frame_count nitrogen_media_frame_count
#define mdec_color_age_cycles nitrogen_private_mdec_color_age_cycles
#define mdec_debug_clear nitrogen_private_mdec_debug_clear
#define mdec_debug_copy_events nitrogen_private_mdec_debug_copy_events
#define mdec_debug_dma_in_end nitrogen_private_mdec_debug_dma_in_end
#define mdec_debug_dma_in_start nitrogen_private_mdec_debug_dma_in_start
#define mdec_debug_dma_out_end nitrogen_private_mdec_debug_dma_out_end
#define mdec_debug_dma_out_start nitrogen_private_mdec_debug_dma_out_start
#define mdec_debug_get_event_total nitrogen_private_mdec_debug_get_event_total
#define mdec_debug_get_state nitrogen_private_mdec_debug_get_state
#define mdec_dma_read_ready nitrogen_private_mdec_dma_read_ready
#define mdec_dma_read_word nitrogen_private_mdec_dma_read_word
#define mdec_dma_read_words nitrogen_private_mdec_dma_read_words
#define mdec_dma_write_ready nitrogen_private_mdec_dma_write_ready
#define mdec_dma_write_word nitrogen_private_mdec_dma_write_word
#define mdec_dma_write_words nitrogen_private_mdec_dma_write_words
#define mdec_get_decode_count nitrogen_private_mdec_get_decode_count
#define mdec_init nitrogen_private_mdec_init
#define mdec_read nitrogen_private_mdec_read
#define mdec_recently_active nitrogen_private_mdec_recently_active
#define mdec_snapshot_bytes nitrogen_private_mdec_snapshot_bytes
#define mdec_snapshot_read nitrogen_private_mdec_snapshot_read
#define mdec_snapshot_validate nitrogen_private_mdec_snapshot_validate
#define mdec_snapshot_write nitrogen_private_mdec_snapshot_write
#define mdec_write nitrogen_private_mdec_write
#include NITROGEN_FRAMEWORK_MDEC
void nitrogen_mdec_finish(void)
{
    free(mdec.input); free(mdec.output); memset(&mdec, 0, sizeof(mdec));
}
void nitrogen_mdec_start(const uint8_t quant[64], const int16_t scale[64])
{
    nitrogen_mdec_finish(); mdec_init();
    mdec_write(0x1f801820u, 0x40000001u);
    for (unsigned i=0;i<128;i+=4) {
        uint32_t value=0;
        for (unsigned b=0;b<4;b++) value |= (uint32_t)quant[(i+b)%64] << (8*b);
        mdec_dma_write_word(value);
    }
    mdec_write(0x1f801820u, 0x60000000u);
    for (unsigned i=0;i<64;i+=2)
        mdec_dma_write_word((uint16_t)scale[i] | (uint32_t)(uint16_t)scale[i+1] << 16);
}
int nitrogen_mdec_decode(const uint16_t *words, size_t count, uint8_t *rgb, size_t bytes)
{
    if (!count || (count & 1) || count > 131070 || !words || !rgb) return 0;
    mdec_write(0x1f801820u, 0x30000000u | (uint32_t)(count/2));
    for (size_t i=0;i<count;i+=2) mdec_dma_write_word(words[i] | (uint32_t)words[i+1] << 16);
    if (mdec.output_size != bytes) { clear_output(); return 0; }
    memcpy(rgb, mdec.output, bytes); clear_output(); return 1;
}
