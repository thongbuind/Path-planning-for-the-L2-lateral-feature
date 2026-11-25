# Đọc bởi planner/CMakeLists.txt khi PP_T7=lab, PP_T7_LAB=qp_jerk_admm_mlp_weights. Đường dẫn theo PP_T7_SOURCE_DIR, trong ngoặc kép.
# Đặc trưng dùng chung với teacher của luồng C (chỉ mlp_features.c; suy luận jerk mlp_infer.c không cần).
set(PP_T7_SOURCES "${PP_T7_SOURCE_DIR}/src/qp_jerk_admm_mlp_weights.c" "${PP_T7_SOURCE_DIR}/src/mlpw_infer.c"
    "${PP_T7_SOURCE_DIR}/../mlp/c/mlp_features.c")
set(PP_T7_HEADER qp_jerk_admm_mlp_weights.h)
set(PP_T7_INCLUDE_DIRS "${PP_T7_SOURCE_DIR}/src" "${PP_T7_SOURCE_DIR}/model" "${PP_T7_SOURCE_DIR}/../mlp/c")
set(PP_T7_TESTS "${PP_T7_SOURCE_DIR}/tests/test_qp_jerk_admm_mlp_weights.c")
