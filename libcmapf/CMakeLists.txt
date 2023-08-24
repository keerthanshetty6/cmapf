# [[[header: .
set(ide_header_group "Header Files")
set(header-group-include
    "${CMAKE_CURRENT_SOURCE_DIR}/include/cmapf.h")
source_group("${ide_header_group}\\include" FILES ${header-group-include})
set(header
    ${header-group-include})
# ]]]
# [[[source: src
set(ide_source_group "Source Files")
set(source-group
    "${CMAKE_CURRENT_SOURCE_DIR}/src/cmapf.cc")
source_group("${ide_source_group}" FILES ${source-group})
set(source
    ${source-group})
# ]]]

if (PYCMAPF_ENABLE STREQUAL "pip")
    set(cmapf_build_interface ON)
else()
    set(cmapf_build_interface OFF)
endif()

set(cmapf_public_scope_ PUBLIC)
set(cmapf_private_scope_ PRIVATE)
if (CMAPF_BUILD_SHARED)
    set(cmapf_lib_type SHARED)
    if (cmapf_build_interface)
        set(cmapf_lib_type INTERFACE)
        set(cmapf_public_scope_ INTERFACE)
        set(cmapf_private_scope_ INTERFACE)
    endif()
else()
    set(cmapf_lib_type STATIC)
endif()

add_library(libcmapf ${cmapf_lib_type})
target_sources(libcmapf ${cmapf_private_scope_} ${header} ${source})
target_include_directories(libcmapf ${cmapf_public_scope_} "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>")
target_compile_definitions(libcmapf ${cmapf_private_scope_} CMAPF_BUILD_LIBRARY)
if (CMAPF_CROSSCHECK)
    target_compile_definitions(libcmapf PUBLIC "CMAPF_CROSSCHECK")
endif()

if (NOT CMAPF_BUILD_STATIC AND CMAPF_BUILD_SHARED AND NOT cmapf_build_interface)
    set_target_properties(libcmapf PROPERTIES POSITION_INDEPENDENT_CODE ON)
endif()
target_link_libraries(libcmapf ${cmapf_public_scope_} libclingo)
if (NOT CMAPF_BUILD_SHARED)
    target_compile_definitions(libcmapf ${cmapf_public_scope_}  CMAPF_NO_VISIBILITY)
elseif(NOT cmapf_build_interface)
    set_target_properties(libcmapf PROPERTIES PUBLIC_HEADER include/cmapf.h)
    install(TARGETS libcmapf
        EXPORT CMAPFTargets
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

    install(EXPORT CMAPFTargets
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/CMAPF)

    include(CMakePackageConfigHelpers)
    configure_package_config_file(
        ${PROJECT_SOURCE_DIR}/cmake/CMAPFConfig.cmake.in
        ${CMAKE_CURRENT_BINARY_DIR}/CMAPFConfig.cmake
        INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/CMAPF)
    write_basic_package_version_file(
        ${CMAKE_CURRENT_BINARY_DIR}/CMAPFConfigVersion.cmake
        COMPATIBILITY SameMajorVersion)
    install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/CMAPFConfig.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/CMAPFConfigVersion.cmake
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/CMAPF)
endif()
if (NOT cmapf_build_interface)
    set_target_properties(libcmapf PROPERTIES
        OUTPUT_NAME cmapf
        LIBRARY_OUTPUT_NAME cmapf
        FOLDER lib)
endif()

if (CMAPF_BUILD_TESTS)
    # NOTE: we build statically without hiding symbols
    add_library(libcmapf_t STATIC ${header} ${source})
    target_include_directories(libcmapf_t PUBLIC "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>")
    target_compile_definitions(libcmapf_t PUBLIC CMAPF_NO_VISIBILITY)
    target_link_libraries(libcmapf_t PUBLIC libclingo)
    target_compile_definitions(libcmapf_t PUBLIC "CMAPF_CROSSCHECK")
    set_target_properties(libcmapf_t PROPERTIES
        OUTPUT_NAME cmapf_t
        LIBRARY_OUTPUT_NAME cmapf_t
        FOLDER lib)
    add_subdirectory(tests)
endif()
