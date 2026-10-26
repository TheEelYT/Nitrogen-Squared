/* Original host-clock player. Guest clocks stay frozen during native movies. */
#include "movie_player.h"
#include "gpu_gl_renderer.h"
#include "host_overlay.h"
#include "host_osd.h"
#include "frame_pacing.h"
#include <algorithm>
#include <condition_variable>
#include <cmath>
#include <cstdio>
#include <deque>
#include <exception>
#include <stdexcept>
#include <thread>
namespace nitrogen::media {
void SDLCALL AudioPlayer::feed(void *context, SDL_AudioStream *target, int additional, int)
{
    auto &self = *static_cast<AudioPlayer *>(context);
    if (additional <= 0) return;
    const uint64_t at = self.cursor.load(std::memory_order_relaxed);
    self.sequence.fetch_add(1, std::memory_order_acq_rel);
    self.anchor_sample.store(at, std::memory_order_relaxed);
    self.anchor_tick.store(SDL_GetTicksNS(), std::memory_order_relaxed);
    self.anchor_pause.store(self.paused_ns.load(), std::memory_order_relaxed);
    self.sequence.fetch_add(1, std::memory_order_release);
    size_t requested = ((size_t)additional + 3) / 4;
    const size_t frames = self.pcm.size() / 2;
    const size_t available = at < frames ? std::min<size_t>(requested, frames - at) : 0;
    if (available) SDL_PutAudioStreamData(target, self.pcm.data() + at * 2, (int)(available * 4));
    requested -= available;
    static const int16_t silence[4096] = {};
    while (requested) {
        size_t n = std::min<size_t>(requested, 2048);
        SDL_PutAudioStreamData(target, silence, (int)(n * 4)); requested -= n;
    }
    self.cursor.store(at + ((size_t)additional + 3) / 4, std::memory_order_release);
}
AudioPlayer::AudioPlayer(const Clip &clip) : pcm(clip.audio), rate(clip.sample_rate)
{
    if (!SDL_InitSubSystem(SDL_INIT_AUDIO)) throw std::runtime_error(SDL_GetError());
    pcm.resize(std::max(pcm.size(), ((size_t)std::ceil(clip.duration * rate) + 4096) * 2), 0);
    SDL_AudioSpec spec{}; spec.freq = (int)rate; spec.format = SDL_AUDIO_S16; spec.channels = 2;
    stream = SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, &spec, feed, this);
    if (!stream) { SDL_QuitSubSystem(SDL_INIT_AUDIO); throw std::runtime_error(SDL_GetError()); }
}
AudioPlayer::~AudioPlayer()
{
    if (stream) SDL_DestroyAudioStream(stream);
    SDL_QuitSubSystem(SDL_INIT_AUDIO);
}
void AudioPlayer::set_paused(bool value)
{
    if (value == paused) return;
    if (value) { SDL_PauseAudioStreamDevice(stream); pause_tick = SDL_GetTicksNS(); }
    else {
        if (pause_tick) paused_ns.fetch_add(SDL_GetTicksNS() - pause_tick);
        if (!SDL_ResumeAudioStreamDevice(stream)) throw std::runtime_error(SDL_GetError());
    }
    paused = value;
}
void AudioPlayer::volume(int percent) { SDL_SetAudioStreamGain(stream, std::clamp(percent, 0, 100) / 100.0f); }
double AudioPlayer::clock() const
{
    uint64_t sample, tick, pause;
    for (;;) {
        const uint64_t a = sequence.load(std::memory_order_acquire); if (a & 1) continue;
        sample = anchor_sample.load(); tick = anchor_tick.load(); pause = anchor_pause.load();
        if (a == sequence.load(std::memory_order_acquire)) break;
    }
    if (!tick) return 0;
    const uint64_t now = paused ? pause_tick : SDL_GetTicksNS();
    const uint64_t stopped = paused_ns.load() - pause;
    const uint64_t elapsed = now >= tick && now - tick >= stopped ? now - tick - stopped : 0;
    return std::min(sample / (double)rate + elapsed / 1e9, cursor.load() / (double)rate);
}
PlaybackResult play(Clip clip)
{
    struct Queue {
        std::mutex mutex;
        std::condition_variable ready;
        std::deque<std::shared_ptr<Frame>> frames;
        bool stop = false, done = false;
        std::exception_ptr error;
    } queue;
    AudioPlayer audio(clip);
    std::thread worker([&] {
        try {
            VideoDecoder decoder;
            for (const auto &packet : clip.video) {
                std::unique_lock<std::mutex> lock(queue.mutex);
                queue.ready.wait(lock, [&] { return queue.stop || queue.frames.size() < 3; });
                if (queue.stop) break;
                lock.unlock(); auto frame = std::make_shared<Frame>(decoder.decode(packet));
                lock.lock(); if (queue.stop) break;
                queue.frames.push_back(std::move(frame)); lock.unlock(); queue.ready.notify_all();
            }
        } catch (...) { std::lock_guard<std::mutex> lock(queue.mutex); queue.error = std::current_exception(); }
        { std::lock_guard<std::mutex> lock(queue.mutex); queue.done = true; }
        queue.ready.notify_all();
    });
    auto join = [&] {
        { std::lock_guard<std::mutex> lock(queue.mutex); queue.stop = true; }
        queue.ready.notify_all(); if (worker.joinable()) worker.join();
    };
    PlaybackResult result;
    bool started = false;
    try {
        {
            std::unique_lock<std::mutex> lock(queue.mutex);
            queue.ready.wait(lock, [&] { return !queue.frames.empty() || queue.done; });
            if (queue.error) std::rethrow_exception(queue.error);
            if (queue.frames.empty()) throw std::runtime_error("Native movie has no decoded frames");
        }
        nitrogen_media_host_begin(); started = true;
        audio.volume(host_volume_get()); audio.set_paused(false);
        std::shared_ptr<Frame> displayed;
        std::vector<uint32_t> black(320*240, 0xff000000u);
        FramePacer pacer{};
        const double period = 1000.0 / std::clamp(nitrogen_media_host_refresh(), 24.0f, 240.0f);
        while (true) {
            SDL_Event event{};
            while (SDL_PollEvent(&event)) {
                if (psx_host_input_sink_dispatch(&event)) continue;
                if (event.type == SDL_EVENT_QUIT || event.type == SDL_EVENT_WINDOW_CLOSE_REQUESTED) {
                    nitrogen_media_host_quit(); result.quitting = true;
                }
                if (event.type == SDL_EVENT_GAMEPAD_ADDED || event.type == SDL_EVENT_GAMEPAD_REMOVED) nitrogen_media_host_devices();
                if ((event.type == SDL_EVENT_KEY_DOWN && !event.key.repeat && (event.key.key == SDLK_X || event.key.key == SDLK_RETURN)) ||
                    (event.type == SDL_EVENT_GAMEPAD_BUTTON_DOWN && (event.gbutton.button == SDL_GAMEPAD_BUTTON_SOUTH || event.gbutton.button == SDL_GAMEPAD_BUTTON_START))) result.skipped = true;
            }
            const int state = nitrogen_media_host_service();
            if (state < 0) result.quitting = true;
            if (result.quitting || result.skipped) break;
            audio.set_paused(state > 0); audio.volume(host_volume_get());
            const double now = audio.clock(); nitrogen_media_host_stats(now, audio.submitted());
            {
                std::lock_guard<std::mutex> lock(queue.mutex);
                if (queue.error) std::rethrow_exception(queue.error);
                while (!queue.frames.empty() && queue.frames.front()->pts <= now) { displayed = queue.frames.front(); queue.frames.pop_front(); }
            }
            queue.ready.notify_all();
            if (now >= clip.duration) break;
            if (displayed) gl_renderer_present(displayed->argb.data(), (int)displayed->width, (int)displayed->height, 0, 1, 0);
            else gl_renderer_present(black.data(), 320, 240, 0, 1, 0);
            frame_pacer_wait(&pacer, period);
        }
        audio.set_paused(true); join(); nitrogen_media_host_end();
        for (const auto &p : clip.video) if (p.width > 16 && p.height > 16) result.frames++;
        return result;
    } catch (...) { audio.set_paused(true); join(); if (started) nitrogen_media_host_end(); throw; }
}
}
