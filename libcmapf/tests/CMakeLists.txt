# [[[source: .
set(ide_source_group "Source Files")
set(source-group
    "${CMAKE_CURRENT_SOURCE_DIR}/cmapf.cc")
source_group("${ide_source_group}" FILES ${source-group})
set(source
    ${source-group})
# ]]]

add_executable(test_cmapf ${source})
target_link_libraries(test_cmapf PRIVATE libcmapf_t Catch2::Catch2WithMain)
target_include_directories(test_cmapf PRIVATE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
)
set_target_properties(test_cmapf PROPERTIES FOLDER test)
if(MSVC)
    target_compile_definitions(test_cmapf PRIVATE _SCL_SECURE_NO_WARNINGS)
endif()

add_test(NAME test_cmapf COMMAND test_cmapf)
