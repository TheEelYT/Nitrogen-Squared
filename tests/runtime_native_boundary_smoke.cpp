/* Original programs only. Exercise the production mixed-backend trampoline,
 * not a test loop that chooses backends or repairs guest return state. */
#include "cpu_state.h"
#include "dirty_ram_interp.h"
#include "psx_bios_backend.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <initializer_list>

#ifdef PSX_HAS_OVERLAY_DISPATCH
extern "C" {
void psx_write_word(uint32_t, uint32_t);
uint32_t psx_read_word(uint32_t);
void psx_write_half(uint32_t, uint16_t);
uint16_t psx_read_half(uint32_t);
void psx_write_byte(uint32_t, uint8_t);
uint8_t psx_read_byte(uint32_t);
int psx_overlay_static_can_dispatch(uint32_t);
void psx_overlay_static_get_stats(uint64_t *, uint64_t *, uint64_t *, uint64_t *);
extern uint8_t *g_psx_ram;
}

namespace {
constexpr uint32_t stop = 0x8001D000, stack = 0x801FFF00, data = 0x80110000;
// Save RA/s0, call t9 with a delay-slot argument, then publish exactly once.
// The second placement straddles a 4 KiB code-page boundary.
const uint32_t caller[] = {0x27BDFFE8, 0xAFBF0014, 0xAFB00010, 0x00808025,
    0x0320F809, 0x24A50001, 0xAE020000, 0x8FB00010, 0x8FBF0014, 0x27BD0018,
    0x03E00008, 0x24630001};
const uint32_t leaf[] = {0x8C880004, 0x24C60003, 0x01051021, 0x03E00008, 0x00461021};
// Untranslated callee calls a compiled callback through t7, preserving its RA.
const uint32_t nested[] = {0x27BDFFF0, 0xAFBF000C, 0x01E0F809, 0x24A50002,
    0x8FBF000C, 0x27BD0010, 0x03E00008, 0};
const uint32_t tail[] = {0x01E00008, 0x24A50002};
// A guest store replaces the suspended native caller's final instruction.
const uint32_t patcher[] = {0xAF070000, 0x03E00008, 0x2402002A};

void require(bool ok, const char *message) {
    if (!ok) { std::fprintf(stderr, "Native boundary smoke failed: %s\n", message); std::exit(1); }
}
template<size_t N> void load(uint32_t pc, const uint32_t (&words)[N]) {
    for (size_t i = 0; i < N; ++i) psx_write_word(pc + uint32_t(i * 4), words[i]);
}
CPUState fixture(uint32_t value, uint32_t target) {
    CPUState cpu{};
    cpu.read_word = psx_read_word; cpu.write_word = psx_write_word;
    cpu.read_half = psx_read_half; cpu.write_half = psx_write_half;
    cpu.read_byte = psx_read_byte; cpu.write_byte = psx_write_byte;
    for (unsigned i = 1; i < 32; ++i) cpu.gpr[i] = 0x10101010u * i;
    cpu.gpr[3] = value; cpu.gpr[4] = data; cpu.gpr[5] = value; cpu.gpr[6] = 17;
    cpu.gpr[15] = 0x8001B700; cpu.gpr[25] = target;
    cpu.gpr[29] = stack; cpu.gpr[31] = stop;
    cpu.hi = 0xABCDEF01; cpu.lo = 0x98765432;
    return cpu;
}
void reset_data() {
    dirty_ram_ld_delay_discard();
    for (uint32_t p = stack - 64; p <= stack + 4; p += 4) psx_write_word(p, 0xCDCDCDCD);
    psx_write_word(data - 4, 0x11223344); psx_write_word(data, 0xBAD0BAD0);
    psx_write_word(data + 4, 0xFFFFFFF0); psx_write_word(data + 8, 0x55667788);
}
void check_return(const CPUState &cpu, const CPUState &before, uint32_t result,
                  uint32_t a1_delta, uint32_t v1_delta, bool patched) {
    for (unsigned i = 0; i < 32; ++i) {
        uint32_t expected = before.gpr[i];
        if (i == 2) expected = result;
        if (i == 3) expected += v1_delta;
        if (i == 5) expected += a1_delta;
        if (i == 6 && !patched) expected += 3;
        if (i == 8 && !patched) expected = 0xFFFFFFF0;
        require(cpu.gpr[i] == expected, "all GPR effects including SP/RA and delay slots");
    }
    require(cpu.hi == before.hi && cpu.lo == before.lo, "preserve HI/LO");
    for (unsigned i = 0; i < 32; ++i)
        require(cpu.cop0[i] == before.cop0[i] && cpu.gte_data[i] == before.gte_data[i] &&
                cpu.gte_ctrl[i] == before.gte_ctrl[i], "preserve COP0/GTE state");
    require(cpu.pc == 0 && !g_psx_call_bail, "complete the real dispatch return contract");
    require(psx_read_word(data) == result && psx_read_word(data - 4) == 0x11223344 &&
            psx_read_word(data + 4) == 0xFFFFFFF0 && psx_read_word(data + 8) == 0x55667788,
            "publish caller result without writing neighboring data");
    require(psx_read_word(stack - 4) == stop && psx_read_word(stack - 8) == before.gpr[16] &&
            psx_read_word(stack) == 0xCDCDCDCD && psx_read_word(stack + 4) == 0xCDCDCDCD,
            "caller stack saves and upper canaries");
}
uint64_t native_hits() {
    uint64_t checks, hits, variants, addresses;
    psx_overlay_static_get_stats(&checks, &hits, &variants, &addresses);
    return hits;
}
}
#endif

void nitrogen_native_boundary_smoke() {
#ifdef PSX_HAS_OVERLAY_DISPATCH
    require(psx_bios_activate(psx_bios_bundled()) != 0, "select linked OpenBIOS dispatcher");
    load(0x8001B600, caller); load(0x8001BFE8, caller); load(0x8001B700, leaf);
    load(0x8001C100, leaf); load(0x8001C200, patcher);
    load(0x8001C300, nested); load(0x8001C400, tail);
    require(psx_overlay_static_can_dispatch(0x8001B700), "callback is compiled");
    require(!psx_overlay_static_can_dispatch(0x8001C100) &&
            !psx_overlay_static_can_dispatch(0x8001C300) &&
            !psx_overlay_static_can_dispatch(0x8001C400), "fallback callees are not compiled");
    unsigned cases = 0;
    for (uint32_t root : {0x8001B600u, 0x8001BFE8u}) {
        require(psx_overlay_static_can_dispatch(root) && psx_overlay_static_can_dispatch(root + 24),
                "caller root and continuation are resident");
        for (uint32_t segment : {0u, 0x80000000u, 0xA0000000u}) {
            const uint32_t entry = (root & 0x1FFFFFFFu) | segment;
            require(bool(psx_overlay_static_can_dispatch(entry)) == (segment == 0x80000000u),
                    "compiled caller requires its own segment");
            for (uint32_t target : {0x8001B700u, 0x8001C100u, 0xA001C100u,
                                     0x8001C300u, 0x8001C400u}) {
                for (uint32_t value : {0u, 1u, 0x7FFFFFFFu, 0xFFFFFFFFu}) {
                    reset_data();
                    auto cpu = fixture(value, target); const auto before = cpu;
                    const auto native_before = native_hits(), interp_before = g_dirty_ram_insns_run;
                    psx_dispatch_call(&cpu, entry, stop);
                    const uint32_t extra = target == 0x8001C300 || target == 0x8001C400 ? 2 : 0;
                    check_return(cpu, before, 0xFFFFFFF0u + value + 1 + extra + 20, 1 + extra, 1, false);
                    if (segment == 0x80000000u || (target != 0x8001C100u && target != 0xA001C100u))
                        require(native_hits() > native_before, "execute a resident native segment");
                    if (segment != 0x80000000u || target != 0x8001B700u)
                        require(g_dirty_ram_insns_run > interp_before, "execute fallback instructions");
                    ++cases;
                }
            }
        }
        // Invalidate a warm root AND alias via byte/halfword stores through
        // a different data segment, including the caller's second code page.
        const uint32_t tail_pc = root + 44, alias = tail_pc | 0x20000000u;
        psx_write_byte(alias, 5);
        require(!psx_overlay_static_can_dispatch(root) && !psx_overlay_static_can_dispatch(root + 24),
                "byte write invalidates the whole owner and continuation");
        psx_write_half(alias, 1);
        require(psx_overlay_static_can_dispatch(root) && psx_overlay_static_can_dispatch(root + 24),
                "halfword restore revalidates owner and continuation");
        reset_data();
        auto cpu = fixture(7, 0x8001C200); cpu.gpr[7] = 0x24630005; cpu.gpr[24] = alias;
        const auto before = cpu; const auto native_before = native_hits(), interp_before = g_dirty_ram_insns_run;
        psx_dispatch_call(&cpu, root, stop);
        check_return(cpu, before, 42, 1, 5, true);
        require(psx_read_word(tail_pc) == 0x24630005 &&
                !psx_overlay_static_can_dispatch(root + 24), "guest patch rejects a suspended native continuation");
        require(native_hits() > native_before && g_dirty_ram_insns_run > interp_before,
                "native caller returns through the authoritative changed-code fallback");
        // Bulk restore bypasses guest-store hooks, as savestate RAM does.
        std::memcpy(g_psx_ram + (root & 0x1FFFFFFFu), caller, sizeof caller);
        overlay_watch_invalidate_after_ram_restore();
        require(psx_overlay_static_can_dispatch(root) && psx_overlay_static_can_dispatch(root + 24),
                "RAM restore revalidates both code pages");
        g_psx_ram[tail_pc & 0x1FFFFFFFu] = 5;
        overlay_watch_invalidate_after_ram_restore();
        require(!psx_overlay_static_can_dispatch(root) && !psx_overlay_static_can_dispatch(root + 24),
                "bulk restore of changed code invalidates a warm native match");
        std::memcpy(g_psx_ram + (root & 0x1FFFFFFFu), caller, sizeof caller);
        overlay_watch_invalidate_after_ram_restore();
        ++cases;
    }
    std::printf("Runtime native boundary smoke passed: %u production-dispatch cases, mixed calls/callbacks/tails, segment isolation, two-page guards and mid-call code replacement\n", cases);
#else
    std::puts("Runtime native boundary smoke passed: REFERENCE links no loaded-code translations");
#endif
}
