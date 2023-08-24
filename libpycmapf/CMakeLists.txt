# [[[source: .
set(ide_source_group "Source Files")
set(source-group
    "${CMAKE_CURRENT_SOURCE_DIR}/_cmapf.c")
source_group("${ide_source_group}" FILES ${source-group})
set(source
    ${source-group})
# ]]]

if (NOT PYCMAPF_INSTALL_DIR AND Python_EXECUTABLE)
    if (PYCMAPF_INSTALL STREQUAL "user")
        execute_process(COMMAND ${Python_EXECUTABLE} ${CMAPF_SOURCE_DIR}/cmake/python-site.py site OUTPUT_VARIABLE PYCMAPF_INSTALL_DIR OUTPUT_STRIP_TRAILING_WHITESPACE)
    elseif(PYCMAPF_INSTALL STREQUAL "prefix")
        execute_process(COMMAND ${Python_EXECUTABLE} ${CMAPF_SOURCE_DIR}/cmake/python-site.py prefix "${CMAKE_INSTALL_PREFIX}" OUTPUT_VARIABLE PYCMAPF_INSTALL_DIR OUTPUT_STRIP_TRAILING_WHITESPACE)
    else()
        execute_process(COMMAND ${Python_EXECUTABLE} ${CMAPF_SOURCE_DIR}/cmake/python-site.py prefix OUTPUT_VARIABLE PYCMAPF_INSTALL_DIR OUTPUT_STRIP_TRAILING_WHITESPACE)
    endif()
endif()

if (NOT PYCMAPF_SUFFIX)
    if (Python_EXECUTABLE)
        execute_process(COMMAND ${Python_EXECUTABLE} ${CMAPF_SOURCE_DIR}/cmake/python-site.py suffix OUTPUT_VARIABLE PYCMAPF_SUFFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    else()
        if (CYGWIN)
            set(PYCMAPF_SUFFIX ".dll")
        elseif (UNIX)
            set(PYCMAPF_SUFFIX ".so")
        else()
            set(PYCMAPF_SUFFIX ".pyd")
        endif()
    endif()
endif()

# Note: For the pip package, we actually not just want to load this library but
# also link agaist it. This is mainly for Windows to ensure that the import
# library is installed.
if (PYCMAPF_ENABLE STREQUAL "pip")
    add_library(pycmapf SHARED ${source})
else()
    add_library(pycmapf MODULE ${source})
endif()
target_link_libraries(pycmapf PRIVATE libcmapf Python::Module)
target_compile_definitions(pycmapf PRIVATE _CFFI_NO_LIMITED_API)
set_target_properties(pycmapf PROPERTIES
    FOLDER lib
    OUTPUT_NAME _cmapf
    SUFFIX ${PYCMAPF_SUFFIX}
    PREFIX "")
if (CMAKE_RUNTIME_OUTPUT_DIRECTORY)
    set_target_properties(pycmapf PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/python)
endif()
if (CMAKE_LIBRARY_OUTPUT_DIRECTORY)
    set_target_properties(pycmapf PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/python)
endif()
if (CMAKE_ARCHIVE_OUTPUT_DIRECTORY)
    set_target_properties(pycmapf PROPERTIES ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_ARCHIVE_OUTPUT_DIRECTORY}/python)
endif()

if (PYCMAPF_INSTALL_DIR)
    file(TO_CMAKE_PATH "${PYCMAPF_INSTALL_DIR}" _PYCMAPF_INSTALL_DIR)
    install(TARGETS pycmapf
        RUNTIME DESTINATION ${_PYCMAPF_INSTALL_DIR}/cmapf
        LIBRARY DESTINATION ${_PYCMAPF_INSTALL_DIR}/cmapf
        ARCHIVE DESTINATION ${_PYCMAPF_INSTALL_DIR}/cmapf)
    install(DIRECTORY ${CMAKE_SOURCE_DIR}/libpycmapf/cmapf/
        DESTINATION ${_PYCMAPF_INSTALL_DIR}/cmapf
        FILES_MATCHING
        PATTERN "*.py"
        PATTERN "*.typed"
        PATTERN "tests" EXCLUDE)
    if (NOT PYCMAPF_ENABLE STREQUAL "pip")
        file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/INSTALLER "pip\n")
        file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/METADATA "Metadata-Version: 1.1\nName: cmapf\nVersion: ${CMAPF_VERSION}\n")
        install(FILES
            ${CMAKE_CURRENT_BINARY_DIR}/INSTALLER
            ${CMAKE_CURRENT_BINARY_DIR}/METADATA
            DESTINATION ${_PYCMAPF_INSTALL_DIR}/cmapf-${CMAPF_VERSION}.dist-info)
    else()
        install(FILES ${CMAKE_SOURCE_DIR}/libcmapf/include/cmapf.h
            DESTINATION ${_PYCMAPF_INSTALL_DIR}/cmapf)
    endif()
endif()
