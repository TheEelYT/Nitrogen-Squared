cmake_minimum_required(VERSION 3.20)
project(NitrogenSquared LANGUAGES C CXX)

# This is a PRIVATE development build. The linked game code is generated
# from the player's disc and must never enter a distributed executable.
set(PSXRECOMP_ROOT "" CACHE PATH "Pinned PSXRecomp checkout")
set(NITROGEN_GENERATED_DIR "" CACHE PATH "Private generated boot-loader C directory")
if(NOT EXISTS "${PSXRECOMP_ROOT}/runtime/runtime.cmake")
    message(FATAL_ERROR "Run python tools/build_runtime.py to prepare the pinned framework")
endif()
if(NOT EXISTS "${NITROGEN_GENERATED_DIR}/SLUS_006.37_dispatch.c")
    message(FATAL_ERROR "Private generated game code is missing; run tools/build_runtime.py")
endif()

set(PSX_RECOMP_UI OFF CACHE BOOL "Development window, no upstream launcher" FORCE)
set(PSX_REWIND OFF CACHE BOOL "No rewind dependency in the first runtime" FORCE)
set(PSX_OPENXR OFF CACHE BOOL "No VR integration" FORCE)
set(PSX_ENABLE_VULKAN OFF CACHE BOOL "OpenGL and software baseline" FORCE)
set(PSXRECOMP_BIOS_STEMS OpenBIOS CACHE STRING "OpenBIOS only" FORCE)
set(PSXRECOMP_REQUIRE_GAME_C ON CACHE BOOL "Never produce an empty setup runtime" FORCE)
set(PSX_DEBUG_TOOLS ON CACHE BOOL "Development diagnostics" FORCE)
include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")

psxrecomp_add_game_runtime(nitrogen-runtime
    WINDOW_TITLE "Nitrogen Squared development"
    DEFAULT_GAME_CONFIG_PATH "game.toml"
    MAX_PLAYERS 2
    PRELOADED_MODS_DIR NONE
    VERSION_FILE "${CMAKE_CURRENT_SOURCE_DIR}/VERSION"
    GEN_MARKER "${NITROGEN_GENERATED_DIR}/SLUS_006.37_dispatch.c"
    GEN_FULL_GLOB "${NITROGEN_GENERATED_DIR}/SLUS_006.37_full_*.c"
)
set_target_properties(nitrogen-runtime PROPERTIES OUTPUT_NAME "NitrogenSquared-dev")
