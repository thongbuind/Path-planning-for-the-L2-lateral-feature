# PP-TS-031 Chiến dịch generator T7 của LCC

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng |
| Mở ngày | 2026-11-23 |
| Khóa ngày | 2026-11-24 |
| Đóng ngày | 2026-11-25 |
| Liên quan | PP-TS-003, PP-TS-013, PP-TS-024, PP-TS-025; PP-SWR-001, 003, 004, 006, 016, 050, 051, 068, 069, 070, 100 đến 102; PP-ADR-013; SQTS 9.1, 9.2 |

## 1. Câu hỏi

- Câu hỏi nghiên cứu: các họ thuật toán T7 (quintic, QP, driver model, MLP) khác nhau thế nào về an toàn, bám làn và cảm nhận, flexibility, chi phí phần cứng và độ nhạy calibration.
- Sản phẩm: một dashboard so sánh cho mentor (`research/generators/dashboard/index.html`). Study không chọn generator và không xếp hạng tổng. Chọn generator là việc của người dùng; đưa một generator vào planner là việc riêng, ngoài study này.
- Vì sao cần: PP-TS-024 (driver model) và PP-TS-025 (MLP quanh QP) cùng dùng suite PP-T7 và cùng mốc. Chạy chung một plan cho một dashboard, một phiên đo thời gian và cách ghép cặp nhất quán. Hai study đó giữ thiết kế biến thể; lần chạy và kết quả ở đây.
- Phạm vi: chỉ T7 của LCC planner. T4, T8, T10, T11, T12, Lateral Controller, kế hoạch tốc độ và LKA/ELK planner giữ chung.

## 2. Phương án

Tên theo thuật toán: `<thuật toán gốc>[_<phần ghép>][_it<số vòng>]`. Tên này là ID biến thể ở `plan.yaml`, thư mục trong `research/generators/` và dòng trong bảng kết quả.

| ID | Thuật toán | Cách cài | Mã cũ |
|---|---|---|---|
| `quintic_duration` | Đa thức bậc 5 d(t), tìm thời lượng tăng dần 0,25 s tới khi đạt feasibility | `PP_T7=quintic_duration` | Mốc, bản đang giao |
| `qp_jerk_admm` | QP biến là jerk ngang trên 30 bước, LTV, ràng buộc mềm, ADMM có warm start, 150 vòng | `PP_T7=qp_jerk_admm` | PP-TS-024 VQ, PP-TS-025 V1 |
| `qp_jerk_admm_it010` … `_it100` | Như trên, 10/25/50/75/100 vòng | `qp_iters` | PP-TS-025 V1r |
| `qp_jerk_admm_it1000_ref` | Như trên, 1000 vòng, nghiệm tham chiếu. Chỉ chạy vòng hở, không so như một thuật toán | `qp_iters` | — |
| `qp_jerk_admm_shift_warmstart_it010` … `_it075` | Warm start bằng x của chu kỳ trước dịch theo thời gian | `PP_T7=lab`, `PP_T7_LAB=qp_jerk_admm_shift_warmstart` | — |
| `quintic_tangent_point` | Quintic cộng hiệu chỉnh ngang, đỉnh theo tangent point | `PP_T7=lab` | PP-TS-024 V1 |
| `quintic_ay_sampling` | Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo | `PP_T7=lab` | PP-TS-024 V2 |
| `qp_jerk_admm_mlp_warmstart_it010` … `_it075` | MLP dự đoán chuỗi jerk làm warm start cho ADMM | `PP_T7=lab` | PP-TS-025 V2 |
| `qp_jerk_admm_mlp_weights` | MLP chọn `qp_w_dev`, `qp_w_jerk`, `qp_a_comfort` trong dải calibration, 150 vòng | `PP_T7=lab` | PP-TS-025 V3 |
| `mlp_jerk_direct` | MLP xuất chuỗi jerk, qua T10 và T4 chung (đối chứng) | `PP_T7=lab` | PP-TS-025 V4 |

Lưới calibration (tối đa 9 cấu hình mỗi kỹ thuật, `research/README.md`). Không chọn cấu hình: mọi cấu hình chạy trên cả tuning và test. Cấu hình mặc định là dòng đại diện; mốc là `quintic_duration` mặc định:

| ID | Lưới |
|---|---|
| `quintic_duration` | `T_hwa` 2,5/3,0/3,5 s × `T_recenter` 3,0/3,5/4,0 s |
| `qp_jerk_admm` | `qp_w_dev` 0,15/0,30/0,60 × `qp_w_comfort` 2,5/5/10 |
| Bản QP ít vòng, bản dịch thời gian, bản MLP warm start | Không có lưới; dùng trọng số mặc định của `qp_jerk_admm` |
| `quintic_tangent_point` | Tâm cửa sổ nhìn trước 1,5/1,75/2,0 s × biên DLC 0/0,01/0,02 m (biên độ giữ 0,20 m: chặn theo DLC luôn chặn trước; 1,0 s không bao giờ kích hoạt trên tuning) |
| `quintic_ay_sampling` | Cặp vị trí đỉnh (0,35; 0,55)/(0,40; 0,60)/(0,45; 0,65) × biên độ 0,10/0,20/0,30 m |
| `qp_jerk_admm_mlp_weights` | Hệ số điều chuẩn khi huấn luyện, 3 mức |

Tổng: 53 cấu hình, chạy trên cả tuning và test.

Dữ liệu MLP theo mục 2 của PP-TS-025: sinh riêng (seed từ 100, tốc độ đến 100 km/h, VP-0/1/2), toàn bộ PP-T7 ngoài train; vùng ngoài miền từ 110 km/h và VP-3/5. Nhãn của `qp_jerk_admm_mlp_weights` bằng lưới offline với hàm mục tiêu thay thế chốt trước (jerk RMS của path, lệch đích, biên DLC).

## 3. Cách đánh giá (khóa trong plan.yaml)

| Mục | Nội dung |
|---|---|
| Bộ chạy | [PP-T7](../../../benchmark/suites/PP-T7.yaml): tuning 14 dòng × seed 1, 2; test 32 dòng × seed 3, 4 |
| Cờ cảnh báo | Không loại thuật toán nào. Bật khi: trượt một requirement mà mốc đạt ở cùng ca, profile, seed; thời gian LCC lái ít hơn mốc quá một chu kỳ ở một lần chạy; B0 (C1, C2) |
| So sánh | Chỉ số và nhóm theo SQTS 9.1 bước 2 đến 5. Mỗi ô là hiệu ghép cặp so với mốc, kèm CI 95 %; "khác có ý nghĩa" khi CI không chứa 0 và hiệu vượt dung sai của SQTS 9.2. Không có thứ hạng hay điểm tổng |
| Calibration | Không chọn; cả lưới hiện ở phần độ nhạy calibration của dashboard |
| Ghép cặp | Vòng hở theo từng chu kỳ (đầu vào trùng nhau, kiểm bằng digest); vòng kín theo từng lần chạy |

Giả thuyết của từng kỹ thuật:

| Kỹ thuật | Giả thuyết | Chỉ số chính | Đạt khi | Nhóm ca |
|---|---|---|---|---|
| `quintic_tangent_point`, `quintic_ay_sampling` | Giảm a_y lớn nhất của xe ở cua ngắn | PP-SWR-068, ghép cặp với `quintic_duration` | Trung bình giảm ≥ 0,10 m/s², khoảng tin cậy không chứa 0; jerk của xe (069) tăng ≤ 0,10 m/s³; DLC của xe (070) giảm ≤ 0,01 m; không trượt mới | S1f, S14e, S1b f |
| `qp_jerk_admm_itk` | Ít vòng vẫn đủ | Lệch output so với `qp_jerk_admm_it1000_ref`, vòng hở, 0–1 s | Chọn k nhỏ nhất có lệch lớn nhất ≤ 0,005 m và không trượt mới | Lượt vòng hở |
| `qp_jerk_admm_shift_warmstart_itk` | Dịch warm start theo thời gian giảm sai số ở cùng số vòng | Như trên | Ở cùng k, lệch nhỏ hơn `qp_jerk_admm_itk` ít nhất 0,005 m | Lượt vòng hở |
| `qp_jerk_admm_mlp_warmstart_itk` | MLP cho chất lượng của QP với ít vòng hơn | Như trên; tỉ số p99 | Ở cùng k, lệch nhỏ hơn cả `qp_jerk_admm_itk` và `qp_jerk_admm_shift_warmstart_itk` ít nhất 0,005 m; có một k mà lệch ≤ lệch của `qp_jerk_admm` và trung vị p99 ≤ 0,90 lần | Lượt vòng hở; S1f, S1c vòng kín |
| `qp_jerk_admm_mlp_weights` | Trọng số theo tình huống tốt hơn trọng số cố định | Các ô bước 2, 3 so với `qp_jerk_admm` mặc định | Ít nhất một ô tốt hơn có ý nghĩa, không ô nào xấu hơn có ý nghĩa | Toàn bộ test |
| `mlp_jerk_direct` | Đối chứng: MLP không có tầng tối ưu | Cờ cảnh báo | Báo các cờ bật; dự kiến có trượt mới | Toàn bộ test |

Giả thuyết có lưới được kiểm ở từng cấu hình và báo "đạt ở x/9 cấu hình".

Báo kèm, không so với mốc:

| Nhóm | Nội dung |
|---|---|
| Chi phí vận hành | p99 kèm % chu kỳ 25 ms; thời gian lớn nhất; khối lượng việc mỗi chu kỳ (telemetry); `pp_lcc_state_size()`; kích thước thư viện và weights |
| Độ tin | Digest đầu vào ở vòng hở; số cặp và điều kiện áp dụng; tỉ lệ chu kỳ path khác `quintic_duration` ở vòng hở; chênh lệch tuning và test |
| Chẩn đoán | Jerk path lớn nhất (bị T10 kẹp); tỉ lệ chu kỳ output chạm trần a_y hoặc jerk; telemetry của T7 và T10; thời gian a_y xe vượt aysmax + 0,3 m/s² |

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| [20261124-2203-study-PP-TS-031-ebfca18](../../runs/20261124-2203-study-PP-TS-031-ebfca18/summary.md) | 53 cấu hình và nghiệm tham chiếu, tuning | 28 lượt mỗi cấu hình; không lượt trượt |
| [20261125-0007-study-PP-TS-031-074a928](../../runs/20261125-0007-study-PP-TS-031-074a928/summary.md) | 53 cấu hình và nghiệm tham chiếu, test | 64 lượt mỗi cấu hình |
| [20261125-0208-timing-PP-TS-031-06cbbe3](../../runs/20261125-0208-timing-PP-TS-031-06cbbe3/manifest.json) | 19 cấu hình mặc định, 1 job | S1f, S1c vòng kín, seed 3, 4, lặp 3 lần |

## 5. Kết quả

Số liệu đầy đủ ở dashboard. Mục này chỉ tóm tắt, không xếp hạng.

### 5.1 Giả thuyết

| Giả thuyết | Tuning | Test | Ghi chú |
|---|---|---|---|
| H1: `quintic_tangent_point`, `quintic_ay_sampling` giảm 068 ở cua ngắn | Không áp dụng (nhóm ca chỉ có ở test) | Không đạt, 0/18 cấu hình | Hiệu 068, 069, 070 dưới 0,002 ở mọi cấu hình. Hai generator gần như không đổi path ở S1f, S14e, S1b f |
| H2: k nhỏ nhất có lệch lớn nhất ≤ 0,005 m | k = 50 (lệch 2,2 mm) | Không có k nào | Ở test, lệch lớn nhất đến từ S14e vòng hở: 0,23 m ở 150 vòng, 0,40 m ở 50 vòng (PP-PR-086). Các lượt vòng hở khác dưới 2,5 mm ở 150 vòng |
| H3: warm start dịch thời gian ≥ 0,005 m tốt hơn QP cùng k | 0/4 | 3/4 (k = 10, 50, 75) | Kết quả test do S14e quyết định |
| H4a: MLP warm start tốt hơn QP và bản dịch thời gian cùng k | 0/8 | 6/8 | Như H3. Ở tuning, MLP warm start lệch nhiều nhất trong ba bản ở mọi k |
| H4b: MLP warm start có k mà lệch ≤ `qp_jerk_admm` và p99 ≤ 0,90 lần | 0/4 | 3/4 (k = 10, 25, 50) | Tỉ số p99 0,67 đến 0,88. Ở test, `qp_jerk_admm` cũng lệch 0,23 m ở S14e nên mốc lệch rộng |
| H5: `qp_jerk_admm_mlp_weights` có ô tốt hơn, không ô nào xấu hơn | 2/3 | 1/3 (l2 1e-4: 2 ô tốt hơn) | Mức giữa: test không ô nào khác có ý nghĩa; mức 1e-2: tuning 1 ô xấu hơn |
| H6: `mlp_jerk_direct` (đối chứng) | — | Cờ bật | 24 lượt trượt mới (PP-SWR-051, 052, 055, 056, 058, 173); 54 lượt LCC lái ít hơn mốc |

- Các giả thuyết H2 đến H4 dùng lệch lớn nhất trên mọi lượt vòng hở. Ở test, một dòng (S14e, a_y cần vượt aysmax) quyết định kết quả, nên tuning và test cho chiều ngược nhau.
- Tiêu chí, nhóm ca và dung sai không đổi sau khi thấy kết quả.

### 5.2 Trượt requirement ở test

| Cấu hình | Lượt trượt | Requirement và ca |
|---|---|---|
| `quintic_duration` (mốc) | 10 | 006 ở S14e (6); 100 ở S1b b, c, f (4, PP-PR-085) |
| `qp_jerk_admm` và các bản QP | 6 đến 7 | 006 ở S14e (6); 100 ở S1b b (1) |
| `qp_jerk_admm_it1000_ref` | 2 | 006 ở S14e vòng hở |
| `mlp_jerk_direct` | 24 | Xem H6 |

- 006 ở S14e đã có ở PP-PR-004.
- Không generator nào ngoài `mlp_jerk_direct` có lượt trượt mới so với mốc.

### 5.3 Thời gian tính (1 job)

| Cấu hình | p99 trung vị [ms] | p99 lớn nhất [ms] |
|---|---|---|
| `mlp_jerk_direct` | 0,69 | 1,47 |
| `quintic_duration` | 0,78 | 2,28 |
| `quintic_tangent_point`, `quintic_ay_sampling` | 0,78 | 1,24 |
| `qp_jerk_admm_it010` | 0,85 | 1,87 |
| `qp_jerk_admm_mlp_warmstart_it010` | 0,91 | 2,32 |
| `qp_jerk_admm_shift_warmstart_it010` | 0,98 | 2,06 |
| `qp_jerk_admm_mlp_weights` | 1,36 | 2,08 |
| `qp_jerk_admm` (150 vòng) | 1,41 | 3,00 |

p99 lớn nhất của mọi cấu hình là 3,2 ms (12,9 % chu kỳ 25 ms). Thời gian trên PC, không khẳng định cho ECU (SQTS 9.1).

### 5.4 Phát hiện trong lúc làm

- `quintic_ay_sampling` không áp được hiệu chỉnh trên cả hai cua ngắn của tuning: S24 a dài 4,25 s, quá tầm nhìn 3 s; S24 b bị giới hạn jerk chặn.
- `quintic_tangent_point`: khi chặn hiệu chỉnh theo DLC phía trong của path quintic thì không còn giảm 070, và lợi về a_y cũng mất.
- Ước lượng a_y cần trong `research/generators/common/` cao hơn thật 15 đến 20 % trên cua ngắn (chỉ dùng trong lab).
- `mlp_jerk_direct` trượt `test_lcc_step` (unit test của planner), như dự kiến của đối chứng.

## 6. Đóng

- Study chỉ mô tả, không đề xuất chọn. Chọn generator và đưa vào planner là việc riêng của người dùng.
- Ngày đóng: 2026-11-25.
- Dashboard: [`research/generators/dashboard/index.html`](../../generators/dashboard/index.html), sinh từ ba run ID ở mục 4 (`python3 -m eval.campaign`, rồi `python3 research/generators/dashboard/build.py`).
- Problem report mở từ study: PP-PR-085, PP-PR-086.
