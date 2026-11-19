cmake_minimum_required(VERSION 3.20)
project(pp_planner VERSION 0.3.0 LANGUAGES C)

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

# LCC T7 technique (PP-TS-003): quintic (A) or qp (C). LKA and ELK always use A.
set(PP_T7 "quintic" CACHE STRING "T7 path generation technique: quintic or qp")
set_property(CACHE PP_T7 PROPERTY STRINGS quintic qp)
if(PP_T7 STREQUAL "qp")
    set(PP_T7_DEFINES PP_T7_QP)
elseif(PP_T7 STREQUAL "quintic")
    set(PP_T7_DEFINES "")
else()
    message(FATAL_ERROR "PP_T7 must be quintic or qp, got ${PP_T7}")
endif()

# PP-TS-020 V2, study only: ay_margin_hwa applies only while lateral_limit_reached is off.
option(PP_AY_MARGIN_GATE "PP-TS-020 V2: HWA path a_y margin only while the limit flag is off" OFF)
if(PP_AY_MARGIN_GATE)
    list(APPEND PP_T7_DEFINES PP_AY_MARGIN_GATE)
endif()
# PP-TS-005 preparation step, study only: every reference line is read through its sampled
# nodes instead of its cubic. OFF keeps the cubic path, bit for bit.
option(PP_REF_SAMPLED "PP-TS-005: read the reference line through sampled nodes" OFF)
if(PP_REF_SAMPLED)
    list(APPEND PP_T7_DEFINES PP_REF_SAMPLED)
endif()

# Identification of the build for pp_version(): version, source commit, calibration data
# set. Regenerated at every build (the commit can change without any file changing here).
add_custom_target(pp_build_info ALL
    COMMAND ${CMAKE_COMMAND} -DOUT=${PP_GENERATED_DIR}/pp_build_info.h
            -DREPO=${CMAKE_CURRENT_SOURCE_DIR}/.. -DCAL=${PP_CALIBRATION_FILE}
            -DVERSION=${PROJECT_VERSION} -DT7=${PP_T7}
            -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/gen_build_info.cmake
    BYPRODUCTS ${PP_GENERATED_DIR}/pp_build_info.h
    COMMENT "Build identification for pp_version()")

set(PP_WARNINGS -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow
                -Wstrict-prototypes -Wmissing-prototypes -Wcast-qual -Wundef)

# Units T1 to T12 (Software Detailed Design section 3). Both planners are built from the same
# core and share no state at run time (PP-ADR-016); each library has only the units it uses.
set(PP_CORE_SOURCES
    src/pp_math.c
    src/input_check.c
    src/latency.c
    src/reference_line.c
    src/curvature.c
    src/stitching.c
    src/feasibility.c
    src/lateral_state.c
    src/generators/quintic.c
    src/output.c
    src/pp_core.c
    ${PP_GENERATED_DIR}/pp_calibration.c)
set(PP_LCC_UNITS src/offset.c src/follow.c src/generators/qp.c)         # T8, T12, T7 C
set(PP_LKAELK_UNITS src/selection.c src/intervention.c)                 # T9, T7 for LKA and ELK
set(PP_PRIVATE_INCLUDES ${PP_INTERFACES_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/src ${PP_GENERATED_DIR})

# Shared libraries: the SIL adapter loads them with ctypes. A target build can use STATIC.
foreach(planner lcc lkaelk)
    if(planner STREQUAL "lcc")
        set(PP_PLANNER_SOURCES src/pp_lcc.c ${PP_LCC_UNITS})
    else()
        set(PP_PLANNER_SOURCES src/pp_lkaelk.c ${PP_LKAELK_UNITS})
    endif()
    add_library(pp_${planner} SHARED ${PP_PLANNER_SOURCES} ${PP_CORE_SOURCES})
    target_include_directories(pp_${planner} PRIVATE ${PP_PRIVATE_INCLUDES})
    target_compile_options(pp_${planner} PRIVATE ${PP_WARNINGS})
    add_dependencies(pp_${planner} pp_build_info)
    if(planner STREQUAL "lcc")
        target_compile_definitions(pp_${planner} PRIVATE ${PP_T7_DEFINES})
    elseif(PP_REF_SAMPLED)
        target_compile_definitions(pp_${planner} PRIVATE PP_REF_SAMPLED)
    endif()
    if(NOT APPLE)
        target_link_libraries(pp_${planner} PRIVATE m)
    endif()
endforeach()

# White-box unit tests of the units (tests/planner/c). Not part of the benchmark.
option(PP_BUILD_TESTS "Build the C unit tests of the planner units" ON)
if(PP_BUILD_TESTS)
    enable_testing()
    set(PP_TEST_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../tests/planner/c)
    set(PP_ALL_UNITS ${PP_LCC_UNITS} ${PP_LKAELK_UNITS} ${PP_CORE_SOURCES})
    foreach(name test_math test_latency test_reference_line test_curvature test_quintic test_output
                 test_stitching test_feasibility test_qp test_offset test_follow test_selection
                 test_intervention test_input_check test_version test_lcc_step test_lkaelk_step)
        set(PP_TEST_PLANNER "")
        if(name STREQUAL "test_lcc_step" OR name STREQUAL "test_version")
            list(APPEND PP_TEST_PLANNER src/pp_lcc.c)
        endif()
        if(name STREQUAL "test_lkaelk_step" OR name STREQUAL "test_version")
            list(APPEND PP_TEST_PLANNER src/pp_lkaelk.c)
        endif()
        add_executable(${name} ${PP_TEST_DIR}/${name}.c ${PP_TEST_PLANNER} ${PP_ALL_UNITS})
        target_include_directories(${name} PRIVATE ${PP_PRIVATE_INCLUDES} ${PP_TEST_DIR})
        target_compile_options(${name} PRIVATE ${PP_WARNINGS})
        target_compile_definitions(${name} PRIVATE ${PP_T7_DEFINES})
        add_dependencies(${name} pp_build_info)
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
