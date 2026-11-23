# Thêm phần dùng chung vào generator lab: include(${PP_T7_SOURCE_DIR}/../common/common.cmake) trong generator.cmake.
get_filename_component(PP_T7_COMMON_DIR "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)
list(APPEND PP_T7_SOURCES "${PP_T7_COMMON_DIR}/src/driver_shape.c")
list(APPEND PP_T7_INCLUDE_DIRS "${PP_T7_COMMON_DIR}/src")
list(APPEND PP_T7_TESTS "${PP_T7_COMMON_DIR}/tests/test_driver_shape.c")
