# pp_version ghi commit, cờ -dirty nếu mã planner/ABI có thay đổi, và 12 ký tự SHA-256 calibration.
# Chỉ ghi lại header khi nội dung đổi để build lặp không biên dịch lại.

execute_process(COMMAND git rev-parse --short=12 HEAD
                WORKING_DIRECTORY ${REPO} RESULT_VARIABLE rc
                OUTPUT_VARIABLE commit OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
if(NOT rc EQUAL 0 OR commit STREQUAL "")
    set(commit "unknown")
else()
    execute_process(COMMAND git status --porcelain -- planner interfaces/c
                    WORKING_DIRECTORY ${REPO}
                    OUTPUT_VARIABLE changes OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
    if(NOT changes STREQUAL "")
        string(APPEND commit "-dirty")
    endif()
endif()

file(SHA256 ${CAL} cal_sha)
string(SUBSTRING ${cal_sha} 0 12 cal_id)

set(text "/* Sinh từ planner/cmake/gen_build_info.cmake. */
#ifndef PP_BUILD_INFO_H
#define PP_BUILD_INFO_H
#define PP_BUILD_INFO_LCC \"pp_lcc ${VERSION} commit ${commit} calibration ${cal_id} t7 ${T7}\"
#define PP_BUILD_INFO_LKAELK \"pp_lkaelk ${VERSION} commit ${commit} calibration ${cal_id}\"
#endif
")

set(old "")
if(EXISTS ${OUT})
    file(READ ${OUT} old)
endif()
if(NOT old STREQUAL text)
    file(WRITE ${OUT} "${text}")
endif()
