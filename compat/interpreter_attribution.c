/* Build-time suppression of diagnostic-only occupant enrichment. Including the
 * pinned core keeps execution, entry counters and native guards unchanged. */
#include <stdint.h>
#ifdef PSX_NO_DEBUG_TOOLS
static uint32_t nitrogen_unused_debug_occupant(uint32_t phys, int *valid)
{
    (void)phys;
    if (valid) *valid = 0;
    return 0;
}
#define psx_overlay_resident_crc_at nitrogen_unused_debug_occupant
#endif
#include NITROGEN_FRAMEWORK_INTERP
