get_target_property(_nitrogen_sources nitrogen-runtime SOURCES)
list(REMOVE_ITEM _nitrogen_sources "${PSXRECOMP_ROOT}/runtime/src/main.cpp")
set(_nitrogen_main "${CMAKE_CURRENT_SOURCE_DIR}/compat/runtime_host.cpp")
set_property(TARGET nitrogen-runtime PROPERTY SOURCES ${_nitrogen_sources} "${_nitrogen_main}")
set_property(SOURCE "${_nitrogen_main}" tests/runtime_input_smoke.cpp APPEND PROPERTY COMPILE_DEFINITIONS
    NITROGEN_FRAMEWORK_MAIN="${PSXRECOMP_ROOT}/runtime/src/main.cpp")
target_include_directories(nitrogen-runtime PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/native")
set(NITROGEN_MEDIA_BINDING "" CACHE FILEPATH "Private verified native-movie binding header")
set(_nitrogen_media_contracts "${CMAKE_CURRENT_SOURCE_DIR}/native/media_contract.h")
if(NOT _nitrogen_profile STREQUAL "REFERENCE")
    if(NITROGEN_MEDIA_BINDING)
        if(NOT EXISTS "${NITROGEN_MEDIA_BINDING}")
            message(FATAL_ERROR "Private movie binding missing; rebuild with build_runtime.py")
        endif()
        set(_nitrogen_media_header "${NITROGEN_MEDIA_BINDING}")
    else()
        set(_nitrogen_media_header "${CMAKE_CURRENT_BINARY_DIR}/native-media-unbound.h")
        file(WRITE "${_nitrogen_media_header}" "#include \"media_contract.h\"\nnamespace nitrogen::media { constexpr Binding binding{}; }\n")
    endif()
    list(APPEND _nitrogen_media_contracts "${_nitrogen_media_header}")
    set_property(SOURCE native/media_entry.cpp APPEND PROPERTY COMPILE_DEFINITIONS NITROGEN_MEDIA_BINDING_HEADER="${_nitrogen_media_header}")
endif()
set_property(SOURCE native/mdec_host.c APPEND PROPERTY COMPILE_DEFINITIONS
    NITROGEN_FRAMEWORK_MDEC="${PSXRECOMP_ROOT}/runtime/src/mdec.c" PSX_NO_DEBUG_TOOLS=1)
psxrecomp_add_implementation(nitrogen-runtime
    NAME n2o-native-opening-movies CONTRACT n2o-opening-movie-loop-v1
    HLE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/native/media_entry.cpp"
        "${CMAKE_CURRENT_SOURCE_DIR}/native/str_decode.cpp"
        "${CMAKE_CURRENT_SOURCE_DIR}/native/movie_player.cpp"
        "${CMAKE_CURRENT_SOURCE_DIR}/native/mdec_host.c"
    LLE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/native/media_reference.cpp"
    CONTRACT_FILES ${_nitrogen_media_contracts}
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake/native_media.cmake"
        "${CMAKE_CURRENT_SOURCE_DIR}/native/media.h" "${CMAKE_CURRENT_SOURCE_DIR}/native/mdec_host.h"
        "${CMAKE_CURRENT_SOURCE_DIR}/native/movie_player.h" "${CMAKE_CURRENT_SOURCE_DIR}/native/mpeg_tables.h"
        "${CMAKE_CURRENT_SOURCE_DIR}/compat/runtime_host.cpp" "${CMAKE_CURRENT_SOURCE_DIR}/compat/n2o_gpu_mode.c"
        "${PSXRECOMP_ROOT}/runtime/src/mdec.c")
