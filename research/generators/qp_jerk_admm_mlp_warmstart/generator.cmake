# Đọc bởi planner/CMakeLists.txt khi PP_T7=lab, PP_T7_LAB=qp_jerk_admm_mlp_warmstart. Đường dẫn theo PP_T7_SOURCE_DIR, trong ngoặc kép.
set(PP_T7_SOURCES "${PP_T7_SOURCE_DIR}/src/qp_jerk_admm_mlp_warmstart.c"
    # Dịch thời gian của luồng A, dùng nguyên (chỉ đọc) làm warm start dự phòng khi MLP ngoài miền.
    "${PP_T7_SOURCE_DIR}/../qp_jerk_admm_shift_warmstart/src/shift.c")
set(PP_T7_HEADER qp_jerk_admm_mlp_warmstart.h)
set(PP_T7_INCLUDE_DIRS "${PP_T7_SOURCE_DIR}/src" "${PP_T7_SOURCE_DIR}/model")
set(PP_T7_TESTS "${PP_T7_SOURCE_DIR}/tests/test_qp_jerk_admm_mlp_warmstart.c")
# Đặc trưng và suy luận MLP dùng chung với teacher (research/generators/mlp/c).
include("${PP_T7_SOURCE_DIR}/../mlp/c/mlp.cmake")
