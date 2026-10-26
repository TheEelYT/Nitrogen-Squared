/* Original host-only snapshot. Never exposes live guest or DSP memory. */
#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct NitrogenRuntimeStatus {
    uint64_t samples, underruns, overflow_drops;
    uint64_t frames_produced, frames_consumed, backpressure_waits;
    double fill_ms, target_ms;
    int audio_active, legacy, host_rate;
    int worker_active, worker_held, max_frames;
} NitrogenRuntimeStatus;
/* Any thread: copy the last main-thread sample under the snapshot mutex. */
void nitrogen_runtime_status(NitrogenRuntimeStatus *out);
#ifdef __cplusplus
}
#endif
