/* Original title binding; instruction guards are generated privately. */
#include "media_contract.h"
#include NITROGEN_MEDIA_BINDING_HEADER
#include "movie_player.h"
#include "cpu_state.h"
#include "func_override.h"
#include <cstdio>
#include <cstdlib>
#include <exception>
extern "C" uint8_t *g_psx_ram;
namespace nitrogen::media {
namespace {
uint64_t hash_body(const uint8_t *bytes, uint32_t size)
{
    uint64_t hash = 14695981039346656037ull;
    for (uint32_t i = 0; i < size; ++i) { hash ^= bytes[i]; hash *= 1099511628211ull; }
    return hash;
}
int movie(CPUState *cpu)
{
    const char *bin = std::getenv("NITROGEN_NATIVE_DISC_BIN");
    if (!bin || !*bin || !nitrogen_media_host_available() || cpu->gpr[4] != 0) return 0;
    const uint32_t physical = binding.entry & 0x1fffffff;
    if (binding.body_size > 0x200000 || physical > 0x200000 - binding.body_size || hash_body(g_psx_ram + physical, binding.body_size) != binding.body_hash) return 0;
    const uint32_t index = cpu->read_word(binding.index_address);
    if (index > 3 || index == 2) return 0;
    const uint32_t context = cpu->gpr[5];
    if ((context & 0x1fffffff) > 0x200000 - 0x1e0) return 0;
    const MovieExtent &extent = binding.clips[index];
    try {
        Clip clip = read_clip(bin, extent.lba, extent.sectors);
        std::fprintf(stdout, "nitrogen: native movie %s (%zu frames, %.3f s)\n", extent.name, clip.video.size(), clip.duration);
        const auto result = play(std::move(clip));
        cpu->write_half(context + 0xda, result.skipped ? 0 : 1);
        cpu->write_half(context + 0xdc, result.skipped ? 1 : 0);
        cpu->write_byte(context + 0xde, result.skipped ? 0 : 1);
        cpu->write_word(binding.index_address + 4, result.frames);
        cpu->gpr[2] = 3;
        std::fprintf(stdout, "nitrogen: native movie complete (%s%s)\n", result.skipped ? "skipped" : "end", result.quitting ? ", exit pending" : "");
        return 1;
    } catch (const std::exception &e) {
        std::fprintf(stderr, "nitrogen: native movie unavailable: %s; using original playback\n", e.what()); return 0;
    }
}
struct Install {
    Install() {
        if (!binding.enabled) return;
        const int status = func_override_add_guarded("n2o-native-opening-movies", binding.entry, movie, binding.guard, 4, FO_CREDIT_SELF);
        if (status != FO_OK) std::fprintf(stderr, "nitrogen: movie binding registration failed (%d)\n", status);
    }
} install;
}
}
