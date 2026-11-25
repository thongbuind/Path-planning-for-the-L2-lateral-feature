# pp_version ghi commit, cờ -dirty nếu mã planner/ABI có thay đổi, 12 ký tự SHA-256 calibration (gồm cả
# calibration riêng của lab, CAL_EXTRA) và generator T7. Generator lab (T7_FILES liệt kê mã của nó) thêm
# t7_src: 12 ký tự SHA-256 của các tệp đó.
# Chỉ ghi lại header khi nội dung đổi để build lặp không biên dịch lại.

execute_process(COMMAND git rev-parse --short=12 HEAD
                WORKING_DIRECTORY ${REPO} RESULT_VARIABLE rc
                OUTPUT_VARIABLE commit OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
set(t7_files "")
if(T7_FILES)
    # Đọc nguyên tệp: file(STRINGS) bỏ ký tự ngoài ASCII trong đường dẫn.
    file(READ "${T7_FILES}" t7_text_files)
    string(STRIP "${t7_text_files}" t7_text_files)
    string(REPLACE "\n" ";" t7_files "${t7_text_files}")
endif()

if(NOT rc EQUAL 0 OR commit STREQUAL "")
    set(commit "unknown")
else()
    execute_process(COMMAND git status --porcelain -- planner interfaces/c ${t7_files} ${CAL_EXTRA}
                    WORKING_DIRECTORY ${REPO} RESULT_VARIABLE status_rc
                    OUTPUT_VARIABLE changes OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
    # Tệp lab ngoài repo làm git status lỗi: không xác nhận được nguồn nên coi là dirty.
    if(NOT status_rc EQUAL 0 OR NOT changes STREQUAL "")
        string(APPEND commit "-dirty")
    endif()
endif()

file(SHA256 ${CAL} cal_sha)
if(CAL_EXTRA)
    file(SHA256 "${CAL_EXTRA}" extra_sha)
    string(SHA256 cal_sha "${cal_sha} ${extra_sha}")
endif()
string(SUBSTRING ${cal_sha} 0 12 cal_id)

set(t7_text "${T7}")
if(t7_files)
    set(manifest "")
    foreach(f IN LISTS t7_files)
        file(SHA256 "${f}" h)
        get_filename_component(name "${f}" NAME)
        string(APPEND manifest "${name} ${h}\n")
    endforeach()
    string(SHA256 t7_sha "${manifest}")
    string(SUBSTRING ${t7_sha} 0 12 t7_id)
    string(APPEND t7_text " t7_src ${t7_id}")
endif()
if(T7_TELEMETRY)
    string(APPEND t7_text " t7_telemetry on")
endif()

set(text "/* Sinh từ planner/cmake/gen_build_info.cmake. */
#ifndef PP_BUILD_INFO_H
#define PP_BUILD_INFO_H
#define PP_BUILD_INFO_LCC \"pp_lcc ${VERSION} commit ${commit} calibration ${cal_id} t7 ${t7_text}\"
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
