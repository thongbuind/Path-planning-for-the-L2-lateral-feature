cmake_minimum_required(VERSION 3.20)
project(pp_planner LANGUAGES C)

# PP-ADR-013: C11, no compiler extensions.
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(PP_INTERFACES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../interfaces/c)
set(PP_CALIBRATION_FILE ${CMAKE_CURRENT_SOURCE_DIR}/calibration/calibration.yaml
    CACHE FILEPATH "Calibration data set built into the library")
set(PP_GENERATED_DIR ${CMAKE_CURRENT_BINARY_DIR}/generated)

# Calibration is a constant data set generated at build time, not a file read at run time.
add_custom_command(
    OUTPUT ${PP_GENERATED_DIR}/pp_calibration.c ${PP_GENERATED_DIR}/pp_calibration.h
    COMMAND Python3::Interpreter ${CMAKE_CURRENT_SOURCE_DIR}/calibration/gen_calibration.py
            --input ${PP_CALIBRATION_FILE} --out-dir ${PP_GENERATED_DIR}
    DEPENDS ${PP_CALIBRATION_FILE} ${CMAKE_CURRENT_SOURCE_DIR}/calibration/gen_calibration.py
    COMMENT "Generating calibration from ${PP_CALIBRATION_FILE}")

set(PP_WARNINGS -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow
                -Wstrict-prototypes -Wmissing-prototypes -Wcast-qual -Wundef)

# Units T1 to T11 (Software Detailed Design section 3).
set(PP_UNIT_SOURCES
    src/pp_math.c
    src/input_check.c
    src/latency.c
    src/reference_line.c
    src/curvature.c
    src/stitching.c
    src/feasibility.c
    src/lateral_state.c
    src/generators/quintic.c
    src/arbitration.c
    src/output.c)
set(PP_PRIVATE_INCLUDES ${PP_INTERFACES_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/src ${PP_GENERATED_DIR})

# Shared library: the SIL adapter loads it with ctypes. A target build can use STATIC.
add_library(pp_planner SHARED
    src/pp_planner.c
    ${PP_UNIT_SOURCES}
    ${PP_GENERATED_DIR}/pp_calibration.c)
target_include_directories(pp_planner PRIVATE ${PP_PRIVATE_INCLUDES})
target_compile_options(pp_planner PRIVATE ${PP_WARNINGS})
if(NOT APPLE)
    target_link_libraries(pp_planner PRIVATE m)
endif()

# White-box unit tests of the units (tests/planner/c). Not part of the benchmark.
option(PP_BUILD_TESTS "Build the C unit tests of the planner units" ON)
if(PP_BUILD_TESTS)
    enable_testing()
    set(PP_TEST_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../tests/planner/c)
    foreach(name test_math test_latency test_reference_line test_curvature test_quintic test_output test_stitching test_feasibility test_step)
        add_executable(${name} ${PP_TEST_DIR}/${name}.c src/pp_planner.c ${PP_UNIT_SOURCES}
                       ${PP_GENERATED_DIR}/pp_calibration.c)
        target_include_directories(${name} PRIVATE ${PP_PRIVATE_INCLUDES} ${PP_TEST_DIR})
        target_compile_options(${name} PRIVATE ${PP_WARNINGS})
        if(NOT APPLE)
            target_link_libraries(${name} PRIVATE m)
        endif()
        add_test(NAME ${name} COMMAND ${name})
    endforeach()
endif()

# Test support only: sizeof/offsetof of every interface struct (tests/interfaces/test_layout.py).
option(PP_BUILD_LAYOUT_PROBE "Build the interface layout probe for tests" ON)
if(PP_BUILD_LAYOUT_PROBE)
    add_library(pp_layout_probe SHARED
        ${CMAKE_CURRENT_SOURCE_DIR}/../tests/interfaces/pp_layout_probe.c)
    target_include_directories(pp_layout_probe PRIVATE ${PP_INTERFACES_DIR})
endif()
