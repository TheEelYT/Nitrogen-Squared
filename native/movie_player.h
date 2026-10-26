#pragma once
#include "media.h"
#include <SDL3/SDL.h>
#include <atomic>
namespace nitrogen::media {
class AudioPlayer {
    SDL_AudioStream *stream = nullptr;
    std::vector<int16_t> pcm;
    unsigned rate;
    std::atomic<uint64_t> cursor{0}, sequence{0}, anchor_sample{0}, anchor_tick{0};
    std::atomic<uint64_t> paused_ns{0}, anchor_pause{0};
    bool paused = true;
    uint64_t pause_tick = 0;
    static void SDLCALL feed(void *, SDL_AudioStream *, int, int);
public:
    AudioPlayer(const Clip &clip);
    ~AudioPlayer();
    AudioPlayer(const AudioPlayer &) = delete;
    AudioPlayer &operator=(const AudioPlayer &) = delete;
    void set_paused(bool value);
    void volume(int percent);
    double clock() const;
    uint64_t submitted() const { return cursor.load(); }
};
struct PlaybackResult { bool skipped = false, quitting = false; uint32_t frames = 0; };
PlaybackResult play(Clip clip);
}
extern "C" {
int nitrogen_media_host_available(void);
int nitrogen_media_host_service(void);
void nitrogen_media_host_quit(void);
void nitrogen_media_host_devices(void);
void nitrogen_media_host_begin(void);
void nitrogen_media_host_end(void);
float nitrogen_media_host_refresh(void);
int nitrogen_media_is_active(void);
void nitrogen_media_host_stats(double seconds, uint64_t samples);
void nitrogen_media_get_stats(double *seconds, uint64_t *samples);
}
