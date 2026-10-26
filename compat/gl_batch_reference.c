/* Reference build: retain the pinned renderer's individual translucent draws. */
#include "gl_batch_policy.h"

GlBatchClass gl_batch_classify(int semi, int mask_check, int bank_batch)
{
    return gl_batch_policy_lle(semi, mask_check, bank_batch);
}

const char *gl_batch_policy_name(void) { return "LLE"; }
