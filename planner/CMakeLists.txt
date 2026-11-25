cmake_minimum_required(VERSION 3.20)
project(pp_planner VERSION 0.3.0 LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(PP_INTERFACES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../interfaces/c)
set(PP_CALIBRATION_FILE ${CMAKE_CURRENT_SOURCE_DIR}/calibration/calibration.yaml
    CACHE FILEPATH "Calibration data set built into the library")
set(PP_GENERATED_DIR ${CMAKE_CURRENT_BINARY_DIR}/generated)

# Chọn T7 cho LCC (PP-TS-031). LKA và ELK luôn dùng quintic (PP-TS-003).
set(PP_T7 "quintic_duration" CACHE STRING
    "T7 generator of the LCC planner: quintic_duration, qp_jerk_admm or lab (aliases: quintic, qp)")
set_property(CACHE PP_T7 PROPERTY STRINGS quintic_duration qp_jerk_admm lab quintic qp)
set(PP_T7_LAB "" CACHE STRING "Lab generator research/generators/<name>, used when PP_T7 is lab")
set(PP_T7_LAB_DIR "" CACHE PATH "Directory of the lab generator; default research/generators/<PP_T7_LAB>")
set(PP_T7_LAB_CALIBRATION "" CACHE FILEPATH "Calibration of the lab generator instead of its generator.yaml (sweeps)")
set(PP_T7_NAME ${PP_T7})
if(PP_T7 STREQUAL "quintic")
    set(PP_T7_NAME quintic_duration)
elseif(PP_T7 STREQUAL "qp")
    set(PP_T7_NAME qp_jerk_admm)
endif()
set(PP_T7_DEFINES "")
set(PP_T7_INCLUDE_DIRS "")
set(PP_T7_TESTS "")
set(PP_T7_CALIBRATION "")
set(PP_T7_SOURCE_DIR "")
if(PP_T7_NAME STREQUAL "quintic_duration" OR PP_T7_NAME STREQUAL "qp_jerk_admm")
    set(PP_T7_SOURCES src/generators/${PP_T7_NAME}.c)
    set(PP_T7_HEADER generators/${PP_T7_NAME}.h)
elseif(PP_T7_NAME STREQUAL "lab")
    if(NOT PP_T7_LAB MATCHES "^[a-z][a-z0-9_]*$")
        message(FATAL_ERROR "PP_T7=lab needs PP_T7_LAB=<name> of research/generators/<name>, got '${PP_T7_LAB}'")
    endif()
    set(PP_T7_SOURCE_DIR "${PP_T7_LAB_DIR}")
    if(PP_T7_SOURCE_DIR STREQUAL "")
        set(PP_T7_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../research/generators/${PP_T7_LAB})
    endif()
    get_filename_component(PP_T7_SOURCE_DIR ${PP_T7_SOURCE_DIR} ABSOLUTE)
    if(NOT EXISTS ${PP_T7_SOURCE_DIR}/generator.cmake)
        message(FATAL_ERROR "no generator.cmake in ${PP_T7_SOURCE_DIR}")
    endif()
    # generator.cmake đặt PP_T7_SOURCES, PP_T7_HEADER (đường dẫn theo PP_T7_SOURCE_DIR); tùy chọn
    # PP_T7_INCLUDE_DIRS, PP_T7_DEFINES, PP_T7_TESTS (unit test C của lab, chạy cùng ctest).
    set(PP_T7_SOURCES "")
    set(PP_T7_HEADER "")
    include(${PP_T7_SOURCE_DIR}/generator.cmake)
    if(PP_T7_SOURCES STREQUAL "" OR PP_T7_HEADER STREQUAL "")
        message(FATAL_ERROR "${PP_T7_SOURCE_DIR}/generator.cmake must set PP_T7_SOURCES and PP_T7_HEADER")
    endif()
    if(NOT PP_T7_LAB_CALIBRATION STREQUAL "")
        if(NOT EXISTS ${PP_T7_LAB_CALIBRATION})
            message(FATAL_ERROR "PP_T7_LAB_CALIBRATION not found: ${PP_T7_LAB_CALIBRATION}")
        endif()
        set(PP_T7_CALIBRATION ${PP_T7_LAB_CALIBRATION})
    elseif(EXISTS ${PP_T7_SOURCE_DIR}/generator.yaml)
        set(PP_T7_CALIBRATION ${PP_T7_SOURCE_DIR}/generator.yaml)
    endif()
    set(PP_T7_NAME ${PP_T7_LAB})
else()
    message(FATAL_ERROR "PP_T7 must be quintic_duration, qp_jerk_admm or lab (aliases quintic, qp), got ${PP_T7}")
endif()
file(CONFIGURE OUTPUT ${PP_GENERATED_DIR}/pp_t7_selected.h
     CONTENT "/* Sinh từ planner/CMakeLists.txt: T7 của LCC là ${PP_T7_NAME}. */\n#include \"${PP_T7_HEADER}\"\n")

# Mã của generator lab; pp_version() ghi hash của chúng (t7_src) vì nguồn lab nằm ngoài planner/. Calibration
# của lab nằm trong mã calibration của pp_version(), không trong t7_src.
set(PP_T7_FILES_LIST "")
if(NOT PP_T7_SOURCE_DIR STREQUAL "")
    set(PP_T7_FILES ${PP_T7_SOURCE_DIR}/generator.cmake)
    foreach(source IN LISTS PP_T7_SOURCES)
        get_filename_component(source ${source} ABSOLUTE)
        list(APPEND PP_T7_FILES ${source})
    endforeach()
    foreach(dir IN LISTS PP_T7_INCLUDE_DIRS)
        file(GLOB_RECURSE headers ${dir}/*.h)
        list(APPEND PP_T7_FILES ${headers})
    endforeach()
    list(REMOVE_DUPLICATES PP_T7_FILES)
    list(SORT PP_T7_FILES)
    string(REPLACE ";" "\n" files_text "${PP_T7_FILES}")
    set(PP_T7_FILES_LIST ${PP_GENERATED_DIR}/pp_t7_files.txt)
    file(CONFIGURE OUTPUT ${PP_T7_FILES_LIST} CONTENT "${files_text}\n")
endif()

# Sinh calibration để biên dịch vào thư viện (PP-ADR-013). Generator lab thêm tham số riêng có tiền tố.
set(PP_CALIBRATION_ARGS --input ${PP_CALIBRATION_FILE} --out-dir ${PP_GENERATED_DIR})
if(NOT PP_T7_CALIBRATION STREQUAL "")
    list(APPEND PP_CALIBRATION_ARGS --extra ${PP_T7_CALIBRATION})
endif()
add_custom_command(
    OUTPUT ${PP_GENERATED_DIR}/pp_calibration.c ${PP_GENERATED_DIR}/pp_calibration.h
    COMMAND Python3::Interpreter ${CMAKE_CURRENT_SOURCE_DIR}/calibration/gen_calibration.py
            ${PP_CALIBRATION_ARGS}
    DEPENDS ${PP_CALIBRATION_FILE} ${PP_T7_CALIBRATION} ${CMAKE_CURRENT_SOURCE_DIR}/calibration/gen_calibration.py
    COMMENT "Generating calibration from ${PP_CALIBRATION_FILE}"
    VERBATIM)

option(PP_AY_MARGIN_GATE "PP-TS-020 V2: HWA path a_y margin only while the limit flag is off" OFF)
if(PP_AY_MARGIN_GATE)
    list(APPEND PP_T7_DEFINES PP_AY_MARGIN_GATE)
endif()
option(PP_T7_TELEMETRY "PP-TS-031: research telemetry of the T7 generator (never in a delivered build)" OFF)
if(PP_T7_TELEMETRY)
    list(APPEND PP_T7_DEFINES PP_T7_TELEMETRY)
endif()
option(PP_REF_SAMPLED "PP-TS-005: read the reference line through sampled nodes" OFF)
if(PP_REF_SAMPLED)
    list(APPEND PP_T7_DEFINES PP_REF_SAMPLED)
endif()

# Kiểm lại commit ở mỗi build vì HEAD có thể đổi dù tệp C giữ nguyên.
add_custom_target(pp_build_info ALL
    COMMAND ${CMAKE_COMMAND} -DOUT=${PP_GENERATED_DIR}/pp_build_info.h
            -DREPO=${CMAKE_CURRENT_SOURCE_DIR}/.. -DCAL=${PP_CALIBRATION_FILE}
            -DVERSION=${PROJECT_VERSION} -DT7=${PP_T7_NAME} -DT7_FILES=${PP_T7_FILES_LIST} -DCAL_EXTRA=${PP_T7_CALIBRATION}
            -DT7_TELEMETRY=${PP_T7_TELEMETRY}
            -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/gen_build_info.cmake
    BYPRODUCTS ${PP_GENERATED_DIR}/pp_build_info.h
    COMMENT "Build identification for pp_version()"
    VERBATIM)

set(PP_WARNINGS -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow
                -Wstrict-prototypes -Wmissing-prototypes -Wcast-qual -Wundef)

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
set(PP_LCC_UNITS src/offset.c src/follow.c src/generators/qp.c src/generators/t7_common.c ${PP_T7_SOURCES})
set(PP_LKAELK_UNITS src/selection.c src/intervention.c)
set(PP_PRIVATE_INCLUDES ${PP_INTERFACES_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/src ${PP_GENERATED_DIR}
    ${PP_T7_INCLUDE_DIRS})

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
    else()
        set(PP_LKAELK_DEFINES "")
        if(PP_REF_SAMPLED)
            list(APPEND PP_LKAELK_DEFINES PP_REF_SAMPLED)
        endif()
        target_compile_definitions(pp_${planner} PRIVATE ${PP_LKAELK_DEFINES})
    endif()
    if(NOT APPLE)
        target_link_libraries(pp_${planner} PRIVATE m)
    endif()
endforeach()

option(PP_BUILD_TESTS "Build the C unit tests of the planner units" ON)
if(PP_BUILD_TESTS)
    enable_testing()
    set(PP_TEST_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../tests/planner/c)
    set(PP_ALL_UNITS ${PP_LCC_UNITS} ${PP_LKAELK_UNITS} ${PP_CORE_SOURCES})
    foreach(name test_math test_latency test_reference_line test_curvature test_quintic test_output
                 test_stitching test_feasibility test_qp test_offset test_follow test_selection
                 test_intervention test_input_check test_version test_lcc_step test_lkaelk_step
                 test_t7_contract)
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
    foreach(test_source IN LISTS PP_T7_TESTS)
        get_filename_component(name ${test_source} NAME_WE)
        set(name lab_${name})
        add_executable(${name} ${test_source} ${PP_ALL_UNITS})
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

option(PP_BUILD_LAYOUT_PROBE "Build the interface layout probe for tests" ON)
if(PP_BUILD_LAYOUT_PROBE)
    add_library(pp_layout_probe SHARED
        ${CMAKE_CURRENT_SOURCE_DIR}/../tests/interfaces/pp_layout_probe.c)
    target_include_directories(pp_layout_probe PRIVATE ${PP_INTERFACES_DIR})
endif()
