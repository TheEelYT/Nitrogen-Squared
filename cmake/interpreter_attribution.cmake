# The external-entry occupant stamp is consumed only by the debug server.
# Preserve the original interpreter and every native residency guard.
file(SHA256 "${_nitrogen_interp}" _nitrogen_interp_sha)
if(NOT _nitrogen_interp_sha STREQUAL "7439cdbb38d8142ab4719d7a9667e16259e7edc27273962b43f67f9de9f8f8b7")
    message(FATAL_ERROR "Pinned interpreter attribution contract changed")
endif()
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${_nitrogen_interp}")
list(REMOVE_ITEM _nitrogen_sources "${_nitrogen_interp}")
set_property(TARGET nitrogen-runtime PROPERTY SOURCES ${_nitrogen_sources})
set_property(SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/compat/interpreter_attribution.c"
    APPEND PROPERTY COMPILE_DEFINITIONS NITROGEN_FRAMEWORK_INTERP="${_nitrogen_interp}")
psxrecomp_add_implementation(nitrogen-runtime
    NAME n2o-interpreter-attribution CONTRACT debug-only-resident-occupant-v1
    HLE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/compat/interpreter_attribution.c"
    LLE_SOURCES "${_nitrogen_interp}"
    CONTRACT_FILES "${CMAKE_CURRENT_SOURCE_DIR}/cmake/interpreter_attribution.cmake"
        "${_nitrogen_interp}" "${PSXRECOMP_ROOT}/runtime/src/overlay_loader.c"
        "${PSXRECOMP_ROOT}/runtime/src/debug_server.c")
