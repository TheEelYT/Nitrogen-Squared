/* Select the pinned renderer's ordered dual-source batching implementation.
 * Its mask-check and subtractive paths retain the reference classification. */
#include "gl_batch_policy.h"

GlBatchClass gl_batch_classify(int semi, int mask_check, int bank_batch)
{
    return gl_batch_policy_hle(semi, mask_check, bank_batch);
}

const char *gl_batch_policy_name(void) { return "HLE"; }
