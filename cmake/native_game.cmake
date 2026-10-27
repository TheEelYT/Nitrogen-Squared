# All generated sources remain private. The framework CRC/page-generation gate
# selects a resident variant by full guest PC and invalidates it on code writes.
set(_nitrogen_slice_contracts
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/native_game.cmake"
    "${CMAKE_CURRENT_SOURCE_DIR}/tools/prepare_native.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/configs/native_usa.json"
    "${PSXRECOMP_ROOT}/tools/compile_overlays.py"
    "${PSXRECOMP_ROOT}/runtime/src/overlay_loader.c")
if(_nitrogen_profile STREQUAL "REFERENCE")
    # A reference configure does not require private generated inputs to exist.
    set(_nitrogen_slice_sources "${CMAKE_CURRENT_SOURCE_DIR}/native/game_slice_reference.c")
else()
    psxrecomp_overlay_static_sources(_nitrogen_slice_sources _nitrogen_slices_present
        TARGET nitrogen-runtime STATIC_C "${NITROGEN_NATIVE_STATIC}" GAME_LINKED TRUE)
    if(NOT _nitrogen_slices_present)
        message(FATAL_ERROR "Private native slices missing; rebuild with build_runtime.py")
    endif()
    set_source_files_properties(${_nitrogen_slice_sources} PROPERTIES GENERATED TRUE)
    target_compile_definitions(nitrogen-runtime PRIVATE PSX_HAS_OVERLAY_DISPATCH=1)
endif()
psxrecomp_add_implementation(nitrogen-runtime
    NAME n2o-native-game-slices CONTRACT n2o-resident-code-ranges-v1
    HLE_SOURCES ${_nitrogen_slice_sources}
    LLE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/native/game_slice_reference.c"
    CONTRACT_FILES ${_nitrogen_slice_contracts})
