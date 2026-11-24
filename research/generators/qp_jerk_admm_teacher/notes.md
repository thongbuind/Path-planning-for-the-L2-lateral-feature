# qp_jerk_admm_teacher

Sổ tay phát triển, không phải kết quả. Kết quả chính thức chỉ nằm ở PP-TS-031 và `research/runs/`.

## Ý tưởng

Công cụ (kind: tool) sinh nhãn cho luồng C. Mỗi lần gọi generator:

- lái xe giống hệt `qp_jerk_admm` (150 vòng, warm start của chính nó);
- song song giải lại cùng bài toán bằng một chuỗi warm start riêng 1000 vòng (như `it1000_ref`), lấy jerk làm nhãn;
- ghi vào đầu ws một bản ghi float64 (`TR_*` trong `src/qp_jerk_admm_teacher.h`): đặc trưng MLP, nhãn, jerk của bản lái,
  bài toán QP đóng gói (để giải lại offline), residual primal/dual, vi phạm hàng cứng a_y và jerk, các cờ đầu vào.

`mlp/collect.py` đọc bản ghi qua `eval.telemetry.Recording(capture=...)`, không cần sửa planner hay contract.

## Quyết định

- Chuỗi 1000 vòng chỉ giữ x, z, y, rho, d_target, warm (`teacher_chain_t`); bộ giải đầy đủ nằm trên stack. Lý do: hai
  `pp_qp_ws_t` làm state LCC vượt 64 KB và `test_lcc_step` trượt.
- Vi phạm a_y và jerk tính lại đúng như `bounds()` của qp.c (hàm đó static), dual residual chuẩn hóa như `next_rho`.
- `COUNT` tăng mỗi lần gọi, không bị `pp_t7_reset` xóa: collect.py dùng nó để bỏ bản ghi trùng.
- Tùy chọn CMake `TEACHER_DRIVE_MLP=ON` (chỉ cho vòng DAgger của `mlp_jerk_direct`): lái bằng MLP trong
  `../mlp_jerk_direct/model/weights.h`, ngoài miền thì lái bằng QP. Bản build này cố ý không qua test contract và test
  của thư mục (lái khác `qp_jerk_admm`); chỉ dùng để thu dữ liệu.

## Kiểm (ctest, telemetry ON, 19/19)

- Lái trùng từng bit với `qp_jerk_admm` qua 3 chu kỳ.
- Bản ghi (đặc trưng, bài toán, nhãn) trùng một lần giải lạnh 1000 vòng; COUNT tăng.
- Hội tụ ở R = 500 m, 25 m/s (primal < 1e-4, dual < 1e-3, vi phạm < 1e-4); nhiễu x[0] += 30 thì vi phạm jerk > 1.
- Ca bất khả thi R = 200 m từ a_y = 0: vi phạm > 0,1 và primal > 1e-2 (nhãn bị loại ở label.py).
- Đầu vào NaN: nhãn hỏng, chu kỳ sau phục hồi.

## Lần chạy

Không chạy quick bench (công cụ, không phải generator để so). Chi phí thu dữ liệu ghi ở `../mlp/notes.md`.

## Vấn đề còn mở

- Nhãn hiện dùng qp.c sau commit 28c4995 (rho thích nghi theo qp_iters). Bản ghi sinh trước commit đó nằm ở
  `build/lab/mlp/old_qpc/`, không dùng.
