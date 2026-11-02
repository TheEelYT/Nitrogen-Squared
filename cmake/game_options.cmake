# Original product enhancement, guarded against overlapping executable images.
set(NITROGEN_OPTIONS_BINDING "" CACHE FILEPATH "Private verified game-options binding")
if(NITROGEN_OPTIONS_BINDING)
    if(NOT EXISTS "${NITROGEN_OPTIONS_BINDING}")
        message(FATAL_ERROR "Private options binding missing; rebuild with build_runtime.py")
    endif()
    set(_nitrogen_options_header "${NITROGEN_OPTIONS_BINDING}")
else()
    set(_nitrogen_options_header "${CMAKE_CURRENT_BINARY_DIR}/game-options-unbound.h")
    file(WRITE "${_nitrogen_options_header}" "#include \"options_contract.h\"\nnamespace nitrogen::options { constexpr Binding binding{}; }\n")
endif()
set_property(SOURCE native/options_entry.cpp APPEND PROPERTY COMPILE_DEFINITIONS
    NITROGEN_OPTIONS_BINDING_HEADER="${_nitrogen_options_header}")
psxrecomp_add_implementation(nitrogen-runtime
    NAME n2o-game-options CONTRACT n2o-guarded-video-audio-options-v1
    HLE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/native/options_entry.cpp"
    LLE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/native/options_entry.cpp"
    CONTRACT_FILES "${_nitrogen_options_header}"
        "${CMAKE_CURRENT_SOURCE_DIR}/native/options_contract.h"
        "${CMAKE_CURRENT_SOURCE_DIR}/compat/nitrogen_options.h"
        "${CMAKE_CURRENT_SOURCE_DIR}/compat/game_options.cpp"
        "${CMAKE_CURRENT_SOURCE_DIR}/tools/prepare_options.py"
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake/game_options.cmake")
