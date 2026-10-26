# Original menu integration; third-party sources are fetched into the private build.
include(FetchContent)
FetchContent_Declare(nitrogen_imgui
    GIT_REPOSITORY https://github.com/ocornut/imgui.git
    GIT_TAG f5befd2d29e66809cd1110a152e375a7f1981f06
    GIT_SHALLOW FALSE)
FetchContent_MakeAvailable(nitrogen_imgui)

# The pinned presenter has no inset API. Adapt just its letterbox helper in a
# private build copy; retain full-size framebuffers, captures and GL viewports.
# Fail closed if the upstream contract changes. Never patch the checkout.
file(READ "${_nitrogen_renderer}" _nitrogen_renderer_text)
set(_nitrogen_letterbox [=[    int dw = ww, dh = (ww * den) / num;
    if (dh > wh) { dh = wh; dw = (wh * num) / den; }
    *x = (ww - dw) / 2;
    *y = (wh - dh) / 2;
    *w = dw; *h = dh;]=])
string(FIND "${_nitrogen_renderer_text}" "${_nitrogen_letterbox}" _nitrogen_letterbox_at)
if(_nitrogen_letterbox_at LESS 0)
    message(FATAL_ERROR "Pinned renderer letterbox contract changed")
endif()
string(REPLACE "${_nitrogen_letterbox}" [=[    extern void nitrogen_menu_letterbox(int, int, int, int, int*, int*, int*, int*);
    nitrogen_menu_letterbox(ww, wh, num, den, x, y, w, h);]=]
    _nitrogen_renderer_text "${_nitrogen_renderer_text}")
set(_nitrogen_menu_renderer "${CMAKE_CURRENT_BINARY_DIR}/nitrogen_gpu_renderer.c")
# configure_file avoids recompiling this large unit when its content is unchanged.
file(WRITE "${_nitrogen_menu_renderer}.in" "${_nitrogen_renderer_text}")
configure_file("${_nitrogen_menu_renderer}.in" "${_nitrogen_menu_renderer}" COPYONLY)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${_nitrogen_renderer}")
list(REMOVE_ITEM _nitrogen_sources "${_nitrogen_renderer}")
set_property(TARGET nitrogen-runtime PROPERTY SOURCES ${_nitrogen_sources})
target_sources(nitrogen-runtime PRIVATE "${_nitrogen_menu_renderer}"
    compat/desktop_menu.cpp
    "${nitrogen_imgui_SOURCE_DIR}/imgui.cpp"
    "${nitrogen_imgui_SOURCE_DIR}/imgui_draw.cpp"
    "${nitrogen_imgui_SOURCE_DIR}/imgui_tables.cpp"
    "${nitrogen_imgui_SOURCE_DIR}/imgui_widgets.cpp"
    "${nitrogen_imgui_SOURCE_DIR}/backends/imgui_impl_sdl3.cpp"
    "${nitrogen_imgui_SOURCE_DIR}/backends/imgui_impl_opengl3.cpp")
target_include_directories(nitrogen-runtime PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/compat" "${PSXRECOMP_ROOT}/runtime/src"
    "${nitrogen_imgui_SOURCE_DIR}" "${nitrogen_imgui_SOURCE_DIR}/backends")
set_property(SOURCE compat/desktop_menu.cpp APPEND PROPERTY COMPILE_DEFINITIONS
    NITROGEN_MENU_VERSION="${NITROGEN_BUILD_VERSION}")
