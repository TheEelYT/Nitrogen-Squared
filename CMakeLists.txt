cmake_minimum_required(VERSION 3.20)
project(NitrogenSquared LANGUAGES C CXX)

# The pinned framework's default differs between Debug and Release, but it
# also writes a shared build-root stamp. Visual Studio/Ninja Multi-Config
# cannot generate that file with different content for each configuration.
# This private development project uses VERSION for every configuration.
# FORCE also repairs an existing cache when the project version changes.
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" NITROGEN_BUILD_VERSION)
string(STRIP "${NITROGEN_BUILD_VERSION}" NITROGEN_BUILD_VERSION)
if(NITROGEN_BUILD_VERSION STREQUAL "")
    message(FATAL_ERROR "Project VERSION is empty")
endif()
set(PSX_GAME_VERSION "${NITROGEN_BUILD_VERSION}" CACHE STRING
    "Project version shared by every development configuration" FORCE)

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
option(NITROGEN_DIAGNOSTICS "Enable expensive per-instruction diagnostics and the TCP probe" OFF)
set(PSX_DEBUG_TOOLS ${NITROGEN_DIAGNOSTICS} CACHE BOOL "Development diagnostics" FORCE)
set(PSX_EXECUTION_PROFILE "ENHANCED" CACHE STRING "ENHANCED or REFERENCE implementation profile")
string(TOUPPER "${PSX_EXECUTION_PROFILE}" _nitrogen_profile)
if(_nitrogen_profile STREQUAL "REFERENCE")
    set(PSX_GL_BATCH_IMPL "LLE" CACHE STRING "OpenGL batching selected by execution profile" FORCE)
else()
    set(PSX_GL_BATCH_IMPL "HLE" CACHE STRING "OpenGL batching selected by execution profile" FORCE)
endif()
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
get_target_property(_nitrogen_sources nitrogen-runtime SOURCES)
set(_nitrogen_gpu "${PSXRECOMP_ROOT}/runtime/src/gpu.c")
if(_nitrogen_gpu IN_LIST _nitrogen_sources)
    # Interpose only this public entry point. The pinned checkout stays clean;
    # a depth transition publishes the CPU-authoritative movie/title uploads.
    set_property(SOURCE "${_nitrogen_gpu}" APPEND PROPERTY COMPILE_DEFINITIONS
        gpu_write_gp1=nitrogen_framework_gpu_write_gp1)
    target_sources(nitrogen-runtime PRIVATE compat/n2o_gpu_mode.c)
endif()
set(_nitrogen_batch_selector "${PSXRECOMP_ROOT}/runtime/src/gl_batch_policy_select.c")
if(_nitrogen_batch_selector IN_LIST _nitrogen_sources)
    get_target_property(_nitrogen_sources nitrogen-runtime SOURCES)
    list(REMOVE_ITEM _nitrogen_sources "${_nitrogen_batch_selector}")
    set_property(TARGET nitrogen-runtime PROPERTY SOURCES ${_nitrogen_sources})
    target_include_directories(nitrogen-runtime PRIVATE "${PSXRECOMP_ROOT}/runtime/src")
    # Select at build time and record the implementation in the framework's
    # execution identity. REFERENCE keeps the original single-primitive path.
    psxrecomp_add_implementation(nitrogen-runtime
        NAME n2o-textured-batching CONTRACT ordered-ps1-texture-blending-v1
        HLE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/compat/gl_batch_enhanced.c"
        LLE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/compat/gl_batch_reference.c"
        CONTRACT_FILES
            "${PSXRECOMP_ROOT}/runtime/src/gl_batch_policy.h"
            "${PSXRECOMP_ROOT}/runtime/src/gl_batch_policy_hle.c"
            "${PSXRECOMP_ROOT}/runtime/src/gl_batch_policy_lle.c"
            "${PSXRECOMP_ROOT}/runtime/src/gpu_gl_renderer.c")
endif()
get_target_property(_nitrogen_sources nitrogen-runtime SOURCES)
set(_nitrogen_renderer "${PSXRECOMP_ROOT}/runtime/src/gpu_gl_renderer.c")
option(NITROGEN_DESKTOP_MENU "Build the System/Debug desktop menu" ON)
if(NITROGEN_DESKTOP_MENU AND _nitrogen_renderer IN_LIST _nitrogen_sources)
    include(cmake/desktop_menu.cmake)
endif()
option(NITROGEN_INPUT_SMOKE "Replace guest execution with the original virtual-gamepad test" OFF)
if(NITROGEN_INPUT_SMOKE)
    get_target_property(_nitrogen_sources nitrogen-runtime SOURCES)
    set(_nitrogen_main "${PSXRECOMP_ROOT}/runtime/src/main.cpp")
    if(NOT _nitrogen_main IN_LIST _nitrogen_sources)
        message(FATAL_ERROR "The pinned runtime main source was not found for the input test")
    endif()
    list(REMOVE_ITEM _nitrogen_sources "${_nitrogen_main}")
    set_property(TARGET nitrogen-runtime PROPERTY SOURCES ${_nitrogen_sources}
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/runtime_input_smoke.cpp")
    set_property(SOURCE tests/runtime_input_smoke.cpp APPEND PROPERTY COMPILE_DEFINITIONS
        NITROGEN_RUNTIME_MAIN="${_nitrogen_main}")
    set_target_properties(nitrogen-runtime PROPERTIES OUTPUT_NAME "NitrogenSquared-input-test")
    if(NOT WIN32 AND NITROGEN_DESKTOP_MENU)
        target_sources(nitrogen-runtime PRIVATE tests/runtime_menu_smoke.cpp)
        set_property(SOURCE tests/runtime_input_smoke.cpp APPEND PROPERTY COMPILE_DEFINITIONS
            NITROGEN_MENU_SMOKE=1)
    endif()
    if(MSVC)
        get_target_property(_nitrogen_link_options nitrogen-runtime LINK_OPTIONS)
        list(FILTER _nitrogen_link_options EXCLUDE REGEX "/SUBSYSTEM:WINDOWS")
        set_property(TARGET nitrogen-runtime PROPERTY LINK_OPTIONS ${_nitrogen_link_options})
        target_link_options(nitrogen-runtime PRIVATE /SUBSYSTEM:CONSOLE)
    endif()
endif()
if(MSVC)
    # The legacy C++17 lambda processor misclassifies local constexpr values
    # in the runtime's session lambda and rejects its static_assert (C2131).
    # Visual Studio shares target-wide flags between C and C++ sources.
    # Set both MSVC options directly so the C option is not dropped by a
    # COMPILE_LANGUAGE expression in this mixed-language target.
    target_compile_options(nitrogen-runtime PRIVATE
        /Zc:lambda /experimental:c11atomics
        "/FI${CMAKE_CURRENT_SOURCE_DIR}/compat/msvc_atomics.h")
endif()
