# qp_jerk_admm_shift_warmstart

Sổ tay phát triển, không phải kết quả. Kết quả chính thức chỉ nằm ở PP-TS-031 và `research/runs/`.

## Ý tưởng

- Chu kỳ sau bắt đầu muộn hơn chu kỳ trước một khoảng dt (thường 25 ms = 1/4 bước lưới QP 0,1 s). Warm start của `qp_jerk_admm` dùng nghiệm cũ đúng chỉ số, nên lệch thời gian dt.
- Ở đây nghiệm cũ được dịch sớm lên dt trước khi giải: `out[i] = (1 − f)·x[i+m] + f·x[i+m+1]`, m = ⌊dt/0,1⌋, f = phần lẻ; quá đuôi thì giữ mẫu cuối. Với jerk hằng từng đoạn, đây đúng là trung bình jerk trên đoạn đã dịch.
- Đối chứng không học cho `qp_jerk_admm_mlp_warmstart` (H3, H4a).

## Thay đổi so với generator gốc

- Cùng bài toán (`pp_t7_qp_problem`), cùng bộ giải (`pp_generate_qp`), cùng trọng số mặc định và `qp_iters`, chạy đủ `qp_iters` vòng. `PP_T7_SUPPORT_FLOOR` 0 như `qp_jerk_admm`.
- Chỉ thêm: trước khi giải, dịch tại chỗ `ws->qp.x` (và `ws->qp.y` nếu `sws_shift_vars` = 2). z do bộ giải tự đặt lại bằng clamp(A·x).
- Hàm dịch ở `src/shift.h`, `src/shift.c`: `bool sws_shift_hold(const double *in, double *out, size_t n, double step_s, double dt_s)`. Không phụ thuộc ws; luồng C dùng lại.

### Thời gian đã trôi

- Lấy `in->old->shift_s` = (t0 − t0 của path cũ), do stitching tính từ stamp. Đây là input của contract, đúng cả khi lỡ chu kỳ (50, 75 ms; quá 75 ms thì path cũ hết hạn, `from_old` false).
- Không dùng hằng `PP_PLANNER_PERIOD_US`: sai khi lỡ chu kỳ hoặc jitter.
- Path cũ luôn là output của lần giải cuối cùng có path hợp lệ, vì LCC ghi path mỗi chu kỳ (kể cả path không hợp lệ).

### Khi không dịch (mã fallback trong `generator.yaml`)

| Mã | Khi | Warm start |
|---|---|---|
| 1 | Không có nghiệm warm (reset, lần giải trước hỏng) | Khởi động lạnh như gốc |
| 2 | `start_from_car` | Như gốc |
| 3 | `from_old` false hoặc path cũ không hợp lệ | Như gốc |
| 4 | `follow` khác lần giải trước | Như gốc |
| 5 | `shift_s` không hữu hạn hoặc ≤ 0 | Như gốc |

- Mã 4 cũng bắt lần gọi thứ hai trong cùng chu kỳ (thử FOLLOW thất bại, giải lại theo làn): khi đó nghiệm trong ws là của chính chu kỳ này, dt thật bằng 0. Lần gọi thứ hai luôn có `follow` false sau lần đầu `follow` true.
- Mọi nhánh không dịch gọi đúng đường của `qp_jerk_admm`, nên output trùng từng bit (L0 kiểm).

### Dịch biến nào (`sws_shift_vars`)

- 0: chỉ jerk; 1: cả x (jerk, nới a_y, nới hành lang); 2: cả x và y.
- Chọn 1. Dịch y làm lệch so với bản 1000 vòng tăng gần gấp đôi (trung bình) ở 10 và 25 vòng; residual ADMM của S1ba tăng từ p50 0,006 lên 0,20. 0 và 1 cho kết quả như nhau; giữ 1 cho z ban đầu nhất quán, thêm 60 phép nhân cộng mỗi chu kỳ.
- Lý do dịch x gần như không đổi kết quả: x chỉ vào bước giải đầu qua σ = 1e-6 và qua z = clamp(A·x); thông tin warm start chủ yếu nằm ở y.

### Chi phí CPU

- Dịch 3 khối × 30 phần tử: khoảng 90 phép nhân cộng mỗi chu kỳ, cỡ 3 % một vòng ADMM. Không cấp phát, không thêm bộ nhớ ngoài `follow_last`, `fallback`.
- Phần nặng của QP nằm ở `planner/src/generators/qp.c`, ngoài thư mục này (xem Vấn đề còn mở).

## Lần dò bằng quick bench

Tham chiếu: `qp_jerk_admm --set qp_iters=1000` (nhãn `qp_jerk_admm-708cc600`). Lệch: lớn nhất trên 0–1 s mỗi chu kỳ vòng hở, gộp 6 lượt vòng hở (5490 chu kỳ). p99 [ms]: trung vị 9 lượt, bản không telemetry; máy dùng chung với các luồng khác nên p99 nhiễu.

| Ngày | Nhãn | Thay đổi | Lệch max / p99 / trung bình [mm] | Trượt | p99 [ms] |
|---|---|---|---|---|---|
| 2026-11-24 | `qp_jerk_admm-708cc600` | Gốc, 1000 vòng (tham chiếu) | 0 | — | 3,62 |
| 2026-11-24 | `qp_jerk_admm-2ce187e9` | Gốc, 10 vòng | 130,4 / 64,6 / 4,68 | 006 ở S1b a vòng kín | 0,59 |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-2ce187e9` | Dịch, 10 vòng, mức 2 | 131,1 / 65,8 / 8,15 | — | 0,66 |
| 2026-11-24 | `qp_jerk_admm-e28e2a7c` | Gốc, 25 vòng | 128,7 / 58,7 / 2,50 | 006 ở S1b a vòng kín | 0,67 |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-e28e2a7c` | Dịch, 25 vòng, mức 2 | 130,5 / 64,1 / 5,31 | 006 ở S1b a vòng kín | 0,79 |
| 2026-11-24 | `qp_jerk_admm-0ea0ac68` | Gốc, 50 vòng | 4,7 / 0,8 / 0,06 | — | 1,81 |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-0ea0ac68` | Dịch, 50 vòng, mức 2 | 2,9 / 1,0 / 0,10 | — | 0,91 |
| 2026-11-24 | `qp_jerk_admm-e667f64d` | Gốc, 75 vòng | 0,6 / 0,2 / 0,01 | — | 1,92 |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-e667f64d` | Dịch, 75 vòng, mức 2 | 0,6 / 0,1 / 0,01 | — | 1,13 |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-tm-2ce187e9` | Mức 2, 10 vòng, telemetry | Như bản không telemetry | — | — |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-cceccbb4` | Mức 0, 10 vòng | 130,4 / 64,6 / 4,94 | 006 ở S1b a vòng kín | 0,83 |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-d546341f` | Mức 1, 10 vòng | 130,4 / 64,6 / 4,95 | 006 ở S1b a vòng kín | 0,77 |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-c569e59b` | Mức 0, 25 vòng | 128,7 / 58,7 / 2,51 | 006 ở S1b a vòng kín | 0,93 |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-078401cc` | Mức 1, 25 vòng | 128,7 / 58,7 / 2,51 | 006 ở S1b a vòng kín | 1,19 |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-ac0ef20f` | Mức 1, 50 vòng | 2,9 / 1,0 / 0,09 | — | 1,05 |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-d43a33cf` | Mức 1, 75 vòng | 2,4 / 0,2 / 0,01 | — | 1,07 |
| 2026-11-24 | `qp_jerk_admm-tm-2ce187e9` | Gốc, 10 vòng, telemetry | Residual S1b a vòng hở p50 0,006 | — | — |
| 2026-11-24 | `qp_jerk_admm_shift_warmstart-tm-d546341f` | Mức 1, 10 vòng, telemetry | Residual như gốc (p50 0,007); fallback chỉ chu kỳ đầu (mã 1, 0,1 %) | — | — |

Nhận xét:

- H3 (lệch nhỏ hơn bản gốc cùng số vòng ít nhất 5 mm) không đạt ở mức nào trên quick bench. Ở 10, 25 vòng lệch max do S1b a chi phối (~130 mm) ở mọi bản; ở 50, 75 vòng mọi bản đã dưới 5 mm.
- Lệch max 10–25 vòng gần như không phụ thuộc warm start: hai mức này không lần nào chỉnh rho (xem dưới), nên ADMM hội tụ chậm bất kể điểm xuất phát.
- p99 nhiễu tới ±50 % giữa các lần (bản dịch có lúc nhanh hơn bản gốc dù làm thêm việc), nên không đọc chênh thời gian từ quick bench.
- Đã dùng 18/20 lần quick bench.

## Vấn đề còn mở

- Rho chỉ được chỉnh ở vòng 25, 50, … và bỏ ở vòng cuối (`it < iters`), mà rho mang sang chu kỳ sau. Vì vậy 10 và 25 vòng giữ rho = `qp_rho0` mãi mãi; 50 vòng là mức đầu tiên có chỉnh rho, giải thích bước nhảy lệch từ ~130 mm xuống ~5 mm. Không sửa ở đây (thuộc `qp.c`); nêu cho dashboard và session contract.
- Vì sao dịch y làm xấu đi chưa rõ. Giả thuyết: ở ít vòng với rho cố định, (x, z, y) chưa cân bằng; dịch y mà z đặt lại theo clamp(A·x) phá cặp z–y.
- Lỗi CMake: `planner/CMakeLists.txt` dòng 40 `set(PP_T7_SOURCE_DIR ${PP_T7_LAB_DIR})` không ngoặc kép; khi `PP_T7_LAB_DIR` rỗng thì biến bị xóa, `if(... STREQUAL "")` sai, configure lỗi ở dòng 44. Build bằng lệnh của README cần thêm `-DPP_T7_LAB_DIR=<đường dẫn tuyệt đối>`; quick bench ở đây chạy được nhờ tạo sẵn CMakeCache có biến đó trong `build/lab/<nhãn>/build`.
- Cơ hội giảm CPU chung cho mọi bản QP (ngoài lab, `qp.c`): `integrators()` và phần ρ·AᵀA của `factor()` không đổi giữa các chu kỳ nhưng tính lại mỗi lần.
