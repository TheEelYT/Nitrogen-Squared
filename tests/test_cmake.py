"""Exercise the real project wrapper without any game or third-party files."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CMakeVersionTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("cmake"), "CMake is needed for the configuration regression")
    def test_multiconfig_stamp_and_existing_cache_follow_project_version(self):
        if os.name != "nt" and not shutil.which("ninja"):
            self.skipTest("Ninja is needed for the Linux multi-config regression")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, framework, generated, build = (root / name for name in ("source", "framework", "generated", "build"))
            source.mkdir()
            (framework / "runtime").mkdir(parents=True)
            generated.mkdir()
            shutil.copy2(ROOT / "CMakeLists.txt", source / "CMakeLists.txt")
            version = (ROOT / "VERSION").read_text().strip()
            (source / "VERSION").write_text(version + "\n")
            (framework / "dummy_atomic.c").write_text('''
#include <stdatomic.h>
int count_once(void) {
    atomic_int count = 0;
    return atomic_fetch_add_explicit(&count, 1, memory_order_relaxed);
}
''')
            (framework / "dummy.cpp").write_text('''
extern "C" int count_once(void);
int main() {
    constexpr bool offered_a = false;
    constexpr bool offered_b = false;
    int calls = 0;
    auto start_session = [&]() {
        static_assert(!offered_a && !offered_b, "Original constexpr lambda fixture");
        return calls++;
    };
    return start_session() + count_once();
}
''')
            (generated / "SLUS_006.37_dispatch.c").write_text("/* Original test fixture, no game code. */\n")
            # Model the pinned framework's problematic shared-stamp contract.
            # The actual project wrapper must supply a scalar version before
            # invoking it. Removing the wrapper fix reproduces the reported error.
            (framework / "runtime/runtime.cmake").write_text('''
function(psxrecomp_add_game_runtime target)
    if(NOT PSX_GAME_VERSION)
        set(PSX_GAME_VERSION "$<IF:$<CONFIG:Release>,${NITROGEN_BUILD_VERSION},dev>")
    endif()
    add_executable(${target} "${PSXRECOMP_ROOT}/dummy.cpp" "${PSXRECOMP_ROOT}/dummy_atomic.c")
    target_compile_features(${target} PRIVATE c_std_11 cxx_std_17)
    file(GENERATE OUTPUT "$<TARGET_FILE_DIR:${target}>/psx_game_version.txt"
         CONTENT "${PSX_GAME_VERSION}\\n")
    get_property(is_multi GLOBAL PROPERTY GENERATOR_IS_MULTI_CONFIG)
    if(is_multi)
        file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/psx_game_version.txt"
             CONTENT "${PSX_GAME_VERSION}\\n")
    endif()
endfunction()
''')
            cmd = ["cmake", "-S", str(source), "-B", str(build),
                   f"-DPSXRECOMP_ROOT={framework}", f"-DNITROGEN_GENERATED_DIR={generated}"]
            # Windows uses its installed Visual Studio generator, matching the
            # failing user build. Linux exercises Ninja Multi-Config.
            if os.name != "nt":
                cmd += ["-G", "Ninja Multi-Config"]
            for expected in (version, "9.8.7-regression"):
                (source / "VERSION").write_text(expected + "\n")
                result = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                cache = (build / "CMakeCache.txt").read_text()
                self.assertIn("CMAKE_CONFIGURATION_TYPES:STRING=", cache)
                for rel in ("psx_game_version.txt", "Debug/psx_game_version.txt", "Release/psx_game_version.txt"):
                    self.assertEqual((build / rel).read_text().strip(), expected)
            result = subprocess.run(["cmake", "--build", str(build), "--config", "Release", "--target", "nitrogen-runtime"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
