# Wrap the pinned parser in the same C translation unit. Its private tables
# are part of this narrow integration contract; reject drift before compiling.
set(_nitrogen_keybinds "${PSXRECOMP_ROOT}/runtime/src/psx_keybinds.c")
file(READ "${_nitrogen_keybinds}" _nitrogen_keybinds_text)
# Windows Git checkouts may use CRLF; line endings do not change the contract.
string(REPLACE "\r\n" "\n" _nitrogen_keybinds_text "${_nitrogen_keybinds_text}")
string(SHA256 _nitrogen_keybinds_sha "${_nitrogen_keybinds_text}")
if(NOT _nitrogen_keybinds_sha STREQUAL "7690f77ce5cd618c1a9013e0aa2870d8b5c162e5bb03bcb7dda5f8bf1222d830")
    message(FATAL_ERROR "Pinned keyboard parser changed; review the title defaults adapter")
endif()
list(REMOVE_ITEM _nitrogen_sources "${_nitrogen_keybinds}")
set_property(TARGET nitrogen-runtime PROPERTY SOURCES ${_nitrogen_sources})
target_sources(nitrogen-runtime PRIVATE compat/keyboard_defaults.c)
set_property(SOURCE compat/keyboard_defaults.c APPEND PROPERTY COMPILE_DEFINITIONS
    NITROGEN_FRAMEWORK_KEYBINDS="${_nitrogen_keybinds}")
