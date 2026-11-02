# All adaptations are private build products with exact pinned-source guards.
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(_nitrogen_display_adapter "${CMAKE_CURRENT_SOURCE_DIR}/tools/adapt_window_display.py")
function(nitrogen_adapt_display kind input output)
    execute_process(COMMAND "${Python3_EXECUTABLE}" "${_nitrogen_display_adapter}"
        "${kind}" "${input}" "${output}" RESULT_VARIABLE result)
    if(NOT result EQUAL 0)
        message(FATAL_ERROR "Pinned ${kind} window display contract changed")
    endif()
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${input}" "${_nitrogen_display_adapter}")
endfunction()
set(_nitrogen_window_gpu "${CMAKE_CURRENT_BINARY_DIR}/nitrogen_window_gpu.c")
nitrogen_adapt_display(gpu "${_nitrogen_gpu}" "${_nitrogen_window_gpu}")
get_target_property(_nitrogen_sources nitrogen-runtime SOURCES)
list(REMOVE_ITEM _nitrogen_sources "${_nitrogen_gpu}")
set_property(TARGET nitrogen-runtime PROPERTY SOURCES ${_nitrogen_sources} "${_nitrogen_window_gpu}")
set_property(SOURCE "${_nitrogen_window_gpu}" APPEND PROPERTY COMPILE_DEFINITIONS
    gpu_write_gp1=nitrogen_framework_gpu_write_gp1)
set(_nitrogen_gte "${PSXRECOMP_ROOT}/runtime/src/gte.cpp")
set(_nitrogen_window_gte "${CMAKE_CURRENT_BINARY_DIR}/nitrogen_window_gte.cpp")
nitrogen_adapt_display(gte "${_nitrogen_gte}" "${_nitrogen_window_gte}")
get_target_property(_nitrogen_sources nitrogen-runtime SOURCES)
list(REMOVE_ITEM _nitrogen_sources "${_nitrogen_gte}")
set_property(TARGET nitrogen-runtime PROPERTY SOURCES ${_nitrogen_sources} "${_nitrogen_window_gte}")
set(_nitrogen_framework_main "${CMAKE_CURRENT_BINARY_DIR}/nitrogen_window_main.cpp")
nitrogen_adapt_display(main "${PSXRECOMP_ROOT}/runtime/src/main.cpp" "${_nitrogen_framework_main}")
target_include_directories(nitrogen-runtime PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/compat")
target_compile_definitions(nitrogen-runtime PRIVATE NITROGEN_WINDOW_DISPLAY=1)
psxrecomp_add_implementation(nitrogen-runtime
    NAME n2o-window-display CONTRACT n2o-window-aspect-stepped-ui-nearest-v1
    HLE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/compat/window_display.cpp"
        "${CMAKE_CURRENT_SOURCE_DIR}/compat/game_options.cpp"
    LLE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/compat/window_display.cpp"
        "${CMAKE_CURRENT_SOURCE_DIR}/compat/game_options.cpp"
    CONTRACT_FILES "${_nitrogen_display_adapter}"
        "${CMAKE_CURRENT_SOURCE_DIR}/compat/window_display.h"
        "${CMAKE_CURRENT_SOURCE_DIR}/compat/game_options.h"
        "${CMAKE_CURRENT_SOURCE_DIR}/compat/window_gpu.inc"
        "${CMAKE_CURRENT_SOURCE_DIR}/compat/world_raster.inc"
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake/window_display.cmake"
        "${CMAKE_CURRENT_SOURCE_DIR}/compat/desktop_menu.cpp"
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake/desktop_menu.cmake"
        "${PSXRECOMP_ROOT}/runtime/src/gpu.c"
        "${PSXRECOMP_ROOT}/runtime/src/gte.cpp"
        "${PSXRECOMP_ROOT}/runtime/src/gpu_gl_renderer.c"
        "${PSXRECOMP_ROOT}/runtime/src/main.cpp")
