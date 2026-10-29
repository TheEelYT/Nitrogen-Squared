# Explicit diagnostic-only opt-in through CMAKE_PROJECT_NitrogenSquared_INCLUDE.
if(NOT CMAKE_SYSTEM_NAME STREQUAL "Linux" OR NOT NITROGEN_DIAGNOSTICS)
    message(FATAL_ERROR "Qualification interposition requires a Linux diagnostic build")
endif()
function(nitrogen_qualification)
    target_sources(nitrogen-runtime PRIVATE
        "${CMAKE_SOURCE_DIR}/tools/qualification/compare.cpp"
        "${CMAKE_SOURCE_DIR}/tools/qualification/replay.cpp")
    target_link_options(nitrogen-runtime PRIVATE -Wl,--wrap=psx_overlay_dispatch -Wl,--wrap=main)
endfunction()
cmake_language(DEFER CALL nitrogen_qualification)
