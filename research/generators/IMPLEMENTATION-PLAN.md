# Generator Lab Implementation Plan

> **Tài liệu tạm.** Xóa file này khi xong bước cuối: GĐ 5.5 (đóng PP-TS-031: generator thắng đã vào `planner/src/generators/`, có PP-ADR, SDD và calibration đã cập nhật, regression trên baseline mới đã có run ID). Khi xóa, mọi điều còn giá trị phải đã nằm ở `research/generators/README.md`, PP-TS-031 hoặc bộ tài liệu kỹ thuật.

| Mục | Nội dung |
|---|---|
| Lập ngày | 2026-11-23 |
| Đã chốt | Nối lab vào planner theo cách A (refactor T7 theo contract chung); tên theo thuật toán (mục 1); cách đánh giá (mục 2); các quyết định ở mục 8. Duyệt ngày 2026-11-23 |
| Đang mở | Không. Bước tiếp theo: GĐ 1 |
| Liên quan | PP-TS-003, PP-TS-013, PP-TS-024, PP-TS-025; suite PP-T7; SQTS mục 7–10 |

## 1. Quy tắc đặt tên

Tên = `<thuật toán gốc>[_<phần ghép>][_it<số vòng, 3 chữ số>]`.

- Một tên dùng chung cho thư mục `research/generators/<tên>/`, giá trị `PP_T7` hoặc `PP_T7_LAB`, `registry.yaml`, ID biến thể trong `plan.yaml` và dòng trong bảng kết quả.
- Cấu hình chỉnh trên tuning: `<tên>-<tham số><giá trị>-...`, ví dụ `quintic_duration-Thwa3.0-Trec3.5`.
- Hai giá trị CMake cũ `quintic` và `qp` giữ làm alias của `quintic_duration` và `qp_jerk_admm`, để plan và script cũ (PP-TS-003, PP-TS-013, `t7_potential.py`) vẫn chạy.
- Mã V0, VQ, V1… trong PP-TS-024 và 025 giữ nguyên trong hai study đó (lịch sử). PP-TS-031 chỉ dùng tên mới.
- Trong `RESULTS.md`, tên đặt ở hàng, không đặt ở cột.

| Tên | Thuật toán | Mã cũ |
|---|---|---|
| `quintic_duration` | Đa thức bậc 5 d(t) từ (d0, v0, a0) tới (d1, 0, 0), tìm thời lượng tăng dần 0,25 s tới khi đạt feasibility | V0 |
| `qp_jerk_admm` | QP biến là jerk ngang trên 30 bước, mô hình thay đổi theo thời gian (LTV), ràng buộc mềm, giải bằng ADMM có warm start. Mặc định 150 vòng | VQ, V1 |
| `qp_jerk_admm_it010` … `_it100` | Như trên, số vòng cố định 10/25/50/75/100 | V1r (75) |
| `qp_jerk_admm_it1000_ref` | Như trên, 1000 vòng, làm nghiệm tham chiếu hội tụ. Không xếp hạng | — |
| `quintic_tangent_point` | Quintic cộng hiệu chỉnh ngang smoothstep bậc 7, đỉnh đặt theo tangent point (Land và Lee, 1994) | PP-TS-024 V1 |
| `quintic_ay_sampling` | Quintic cộng hiệu chỉnh ngang, chọn trong tập ứng viên theo đỉnh a_y và jerk dự báo | PP-TS-024 V2 |
| `qp_jerk_admm_shift_warmstart_it010` … `_it075` | Warm start ADMM bằng x của chu kỳ trước được dịch theo thời gian (25 ms = 1/4 bước lưới 0,1 s; nội suy, ngoại suy jerk cuối). Đối chứng không học cho bản MLP warm start | — |
| `qp_jerk_admm_mlp_warmstart_it010` … `_it075` | MLP dự đoán chuỗi jerk làm warm start cho ADMM, cùng số vòng với bản QP để ghép cặp | PP-TS-025 V2 |
| `qp_jerk_admm_mlp_weights` | MLP chọn trọng số QP, kẹp trong dải calibration, 150 vòng | PP-TS-025 V3 |
| `mlp_jerk_direct` | MLP xuất thẳng chuỗi jerk, tích phân ra path, qua T10 và T4 chung (đối chứng) | PP-TS-025 V4 |

R-cam của PP-TS-013 là nguyên mẫu Python nên không vào benchmark.

## 2. Cách đánh giá

### 2.1 Nguyên tắc

- Một thông tin được giữ khi nó phục vụ ít nhất một trong bốn quyết định: loại, xếp hạng, giả thuyết của generator, độ tin của kết quả. Thông tin chỉ giải thích vì sao thì để ở mục chẩn đoán.
- Chỉ số của xe đo trên chuyển động thật so với làn thật, trong vòng kín. Chỉ số của path đọc ở vòng hở, vì ở đó đầu vào trùng nhau từng chu kỳ giữa các build.
- Ghép cặp: vòng hở theo từng chu kỳ; vòng kín theo từng lượt (ca, profile, seed).

### 2.2 Cửa loại

| Cửa | Luật | Đã có trong eval |
|---|---|---|
| B0 (C1, C2), lỗi thực thi | Trượt là loại | Có |
| Requirement trong scope PP-T7 | Loại khi trượt mà `quintic_duration` không trượt ở cùng ca, profile, seed. Lỗi chung vẫn liệt kê và vẫn tính vào kết luận khi giao | Có; cần luật tương đối |
| Tỉ lệ thời gian LCC lái (`path_valid`, `lcc_mode`) | Loại khi thấp hơn mốc quá một chu kỳ (25 ms) ở bất kỳ lượt nào. Chặn trường hợp generator thất bại, LCC ngừng lái, nên trông "êm" hơn | Chưa |

PP-SWR-006 (sàn hỗ trợ) là cửa có rủi ro cao với generator cắt cua.

### 2.3 Xếp hạng

Thứ tự theo SQTS 9.1 sau khi sửa ở GĐ 0. Đại lượng an toàn là khoảng cách tới biên làn (DLC), không phải lệch khỏi tâm làn. PP-SWR-050 giữ lại (từ đề bài) nhưng chuyển sang bước 3.

| Bước | Nhóm | Chỉ số | Dung sai thực tế |
|---|---|---|---|
| 2 | An toàn | PP-SWR-070 DLC nhỏ nhất của xe, hai phía (mới) | 0,01 m |
| 2 | An toàn | PP-SWR-057 khoảng hở khi dời tâm | 0,01 m |
| 3 | Bám làn và cảm nhận | PP-SWR-050 lệch ngang path 0–1 s | 0,005 m |
| 3 | Bám làn và cảm nhận | PP-SWR-068 a_y đỉnh của xe (R79 Annex 8, 2.4) (mới) | 0,10 m/s² |
| 3 | Bám làn và cảm nhận | PP-SWR-069 jerk của xe (mới) | 0,10 m/s³ |
| 3 | Bám làn và cảm nhận | PP-SWR-004 jerk path RMS | 0,10 m/s³ |
| 3 | Bám làn và cảm nhận | PP-SWR-004 tốc độ quay vô lăng RMS, vòng kín | 5 % |
| 3 | Bám làn và cảm nhận | PP-SWR-002 a_y thêm vào | 0,05 m/s² |
| 3 | Bám làn và cảm nhận | PP-SWR-053 thời gian đưa về giữa; PP-SWR-059 thời gian trả về | 0,1 s |
| 4 | Flexibility | Độ chênh của các chỉ số bước 2–3 giữa VP-0, VP-3, VP-5 | Như chỉ số gốc |
| 5 | Chi phí vận hành | PP-SWR-016 p99 thời gian CPU | 10 % |

- **Luật thắng:** A thắng B ở một chỉ số khi CI 95 % bootstrap của trung bình hiệu không chứa 0 **và** |trung bình hiệu| ≥ dung sai thực tế. Không thì hòa.
- Chỉ số có n < 4 cặp: ghi "ít dữ liệu", không tính vào Copeland.
- Dung sai là `nhóm tự thống nhất`. Nguồn: ba mức đã có trong plan của PP-TS-024 (050, DLC, 002); ngưỡng giả thuyết của PP-TS-024 (a_y, jerk); 0,1 s là 4 chu kỳ; 5 % và 10 % là tương đối vì chưa có thang tuyệt đối hoặc vì nhiễu đo trên laptop.
- Luật thắng và nhóm mới áp cho cả SQTS 9.2 (so sánh planner). Ở 9.2, các chỉ số LKA và ELK (081, 082, 087) vẫn giữ trong nhóm của chúng.

### 2.4 Chi phí vận hành

Mục đích: so phần cứng cần để chạy mỗi generator. Generator tính nhanh và nhẹ chạy được trên phần cứng rẻ hơn. Phần cứng được chọn theo trường hợp xấu nhất, và thời gian đo trên laptop không chuyển thẳng sang ECU, nên bảng có thêm thước đo không phụ thuộc máy.

| Thông tin | Vai trò | Hộp đen |
|---|---|---|
| p99 thời gian CPU của `pp_lcc_step`, kèm % chu kỳ 25 ms | Xếp hạng (bước 5) | Có |
| Thời gian CPU lớn nhất | Ngữ cảnh: phần cứng chọn theo trường hợp xấu nhất; nhiễu trên laptop | Có |
| Khối lượng việc lớn nhất mỗi chu kỳ: số vòng ADMM, số lần thử thời lượng, số phép nhân của MLP | Ngữ cảnh, không phụ thuộc máy | Telemetry |
| Bộ nhớ state: `pp_lcc_state_size()` | Ngữ cảnh: RAM | Có (interface) |
| Kích thước thư viện, kích thước weights | Ngữ cảnh: flash | Có (file) |

### 2.5 Giả thuyết của từng generator

| Generator | Giả thuyết | Chỉ số chính | Đạt khi | Nhóm ca |
|---|---|---|---|---|
| `quintic_tangent_point`, `quintic_ay_sampling` | Giảm a_y đỉnh của xe ở cua ngắn | 068 ghép cặp với `quintic_duration` | Trung bình giảm ≥ 0,10 m/s², CI không chứa 0; jerk xe (069) tăng ≤ 0,10 m/s³; DLC xe (070) giảm ≤ 0,01 m; không trượt mới | S1f, S14e, S1b f |
| `qp_jerk_admm_it010` … `_it100` | Ít vòng vẫn đủ | Lệch output so với `qp_jerk_admm_it1000_ref`, vòng hở, đoạn 0–1 s | Chọn k nhỏ nhất có lệch lớn nhất ≤ 0,005 m (bằng dung sai 050) và không trượt mới | Mọi lượt vòng hở |
| `qp_jerk_admm_shift_warmstart_itk` | Dịch warm start theo thời gian đã giảm sai số ở cùng số vòng | Lệch so với bản 1000 vòng ở cùng k | Ở cùng k, lệch nhỏ hơn `qp_jerk_admm_itk` vượt dung sai 0,005 m | Vòng hở; S1f, S2, S17 |
| `qp_jerk_admm_mlp_warmstart_itk` | Warm start cho chất lượng của QP với ít vòng hơn | Lệch so với bản 1000 vòng ở cùng k; tỉ số p99 | Ở cùng k, lệch nhỏ hơn **cả** `qp_jerk_admm_itk` và `qp_jerk_admm_shift_warmstart_itk` (lợi phải đến từ MLP, không chỉ từ việc sửa lệch thời gian). Có một k mà lệch ≤ lệch của `qp_jerk_admm` (150 vòng) và trung vị p99 ≤ 0,90 lần | Vòng hở; S1f, S1c vòng kín; vùng ngoài miền (110–130 km/h, VP-3/5) báo riêng |
| `qp_jerk_admm_mlp_weights` | Trọng số thích nghi tốt hơn trọng số cố định | Copeland bước 2–3 so với `qp_jerk_admm` | Thắng ít nhất một nhóm, không thua nhóm nào | Toàn bộ test |
| `mlp_jerk_direct` | Đối chứng: MLP thuần không đủ an toàn khi đứng một mình | Cửa loại | Dự kiến bị loại; dùng làm kỹ thuật bị loại kèm lý do (đề bài, SQTS 9.1) | Toàn bộ test |

Các tiêu chí này khóa trong `plan.yaml` của PP-TS-031 trước khi chạy.

### 2.6 Độ tin của kết quả

| Thông tin | Đã có trong eval |
|---|---|
| Digest đầu vào trùng giữa các build ở vòng hở (`case_hash`) | Có |
| Số cặp n và điều kiện áp dụng của mỗi chỉ số | Một phần |
| Tỉ lệ chu kỳ path khác `quintic_duration` ở vòng hở: generator có thực sự hoạt động không | Chưa |
| Chênh lệch giữa tuning và test, để phát hiện quá khớp | Chưa |
| Run ID, `pp_version`, hash calibration | Có |

### 2.7 Chẩn đoán (không xếp hạng)

- Jerk path đỉnh: bị T10 kẹp ở trần, nên các generator dễ cho cùng giá trị.
- Tỉ lệ chu kỳ output chạm trần a_y hoặc jerk (hộp đen, thay cho "T10 sửa bao nhiêu").
- Telemetry: T10 trước và sau, residual, slack, số vòng, lý do dùng mốc, thời gian suy luận MLP.
- Ngữ cảnh: thời gian a_y xe vượt aysmax + 0,3 m/s², có trong giới hạn R79 5.6.2.1.1 không; PP-SWR-125 (F06).

### 2.8 Bỏ khỏi bảng

| Thông tin | Lý do |
|---|---|
| Thời gian tính trung bình | p99 và max đã đủ |
| PP-SWR-064, 008 | Generator không đổi logic cờ |
| PP-SWR-081, 082, 087, Euro NCAP LSS | Chỉ LKA và ELK dùng, PP-T7 không có |
| PP-SWR-013 | PP-T7 không chạy quét Q1 |

## 3. Số cấu hình

| Tên | Tham số chỉnh trên tuning | Số cấu hình chỉnh | Vào test |
|---|---|---|---|
| `quintic_duration` | `T_hwa` 2,5/3,0/3,5 s × `T_recenter` 3,0/3,5/4,0 s | 9 | 1 |
| `qp_jerk_admm` (150 vòng) | `qp_w_dev` 0,15/0,30/0,60 × `qp_w_comfort` 2,5/5/10 | 9 | 1 |
| `qp_jerk_admm_it010` … `_it100` | Không chỉnh; dùng trọng số tốt nhất của `qp_jerk_admm` | 5 | 5 |
| `qp_jerk_admm_it1000_ref` | Chỉ chạy lượt vòng hở | — | chỉ đo |
| `quintic_tangent_point` | Tâm cửa sổ nhìn trước 1,0/1,5/2,0 s × biên độ 0,10/0,20/0,30 m | 9 | 1 |
| `quintic_ay_sampling` | Cặp vị trí đỉnh (0,35; 0,55)/(0,40; 0,60)/(0,45; 0,65) × biên độ 0,10/0,20/0,30 m | 9 | 1 |
| `qp_jerk_admm_shift_warmstart_it010` … `_it075` | Không chỉnh; 4 mức số vòng, trọng số của `qp_jerk_admm` | 4 | 4 |
| `qp_jerk_admm_mlp_warmstart_it010` … `_it075` | 4 mức số vòng, ghép cặp với bản QP và bản dịch thời gian cùng số vòng | 4 | 4 |
| `qp_jerk_admm_mlp_weights` | Hệ số điều chuẩn khi huấn luyện, 3 mức | 3 | 1 |
| `mlp_jerk_direct` | Không chỉnh | 1 | 1 |
| **Tổng** | | **53** | **19** |

- QP chạy đủ `qp_iters` vòng, không dừng sớm. Thời gian vì thế tăng gần tuyến tính theo số vòng.
- Bản QP ít vòng, bản dịch thời gian và bản MLP warm start dùng chung trọng số của `qp_jerk_admm` để chỉ có số vòng và điểm xuất phát thay đổi.
- Ngân sách tối đa 9 cấu hình cho mỗi kỹ thuật (`research/README.md`).

## 4. Bài kiểm

| Phần | Lượt | Seed | Lượt mỗi cấu hình |
|---|---|---|---|
| Tuning | 12 dòng PP-T7 | 1, 2 | 24 |
| Test | 28 dòng PP-T7 + 4 dòng mới | 3, 4 | 64 |

Bốn dòng mới thêm vào test:

| Dòng | Lý do |
|---|---|
| `[S1, a, F01, c]` | Cua R = 1000 m gần thẳng, camera nhiễu ban đêm ×2,5. Bắt dao động ngang do generator tự tạo khi không có cua |
| `[S1b, f, {acc: ignore_limits}]` | Cua R = 230 m, a_y trong dải aysmax + 0,1 đến + 0,4. Cho thấy cắt cua giúp hay hại |
| `[S2, e]` | Đưa về giữa ở 130 km/h. Nâng n của 002 và 053 từ 2 lên 4 |
| `[S3, a]` | Dời tâm khi xe tải chậm hơn 5 m/s. Nâng n của 057 và 059 từ 2 lên 4 |

## 5. Chi phí ước tính

Đo được 3,8–6,3 giây CPU mỗi lượt (PP-TS-020, PP-TS-030). Ước tính dùng 6 giây, chạy 2 job.

| Lần chạy | Số lượt | Thời gian (2 job) |
|---|---|---|
| Golden trước và sau refactor (GĐ 1) | ~96 | ~5 phút |
| Quick bench mỗi lần dò (GĐ 3) | ~10 | ~1 phút |
| Sinh dữ liệu MLP (GĐ 3): kịch bản sinh riêng + giải QP 1000 vòng offline | ≤ 10.000 cửa sổ | Ước lượng khi cài bộ sinh, hỏi trước |
| Nhãn của `qp_jerk_admm_mlp_weights`: lưới trọng số offline trên từng cửa sổ | Lưới × số cửa sổ | Ước lượng khi chốt lưới, hỏi trước |
| Sweep tuning (GĐ 4) | 53 × 24 = 1272 | ~65 phút |
| Test chính thức (GĐ 5) | 19 × 64 = 1216 + 16 lượt tham chiếu | ~70 phút |
| Phiên đo thời gian (GĐ 5) | 19 × 4 lượt × 3 lần lặp, 1 job | ~25 phút |
| **Tổng** | | **~3–3,5 giờ**, chưa tính dữ liệu và nhãn MLP; chia nhiều lần; bản QP có thể nặng hơn ~30 % |

Mỗi lần chạy phải nói lệnh và chờ người dùng đồng ý (máy 8 GB).

## 6. Các giai đoạn

### GĐ 0: Chốt cách đánh giá vào tài liệu và eval

| Bước | Việc | File | Trạng thái |
|---|---|---|---|
| 0.1 | Thêm ba performance target khối LCC, viết "nên", không ngưỡng (một câu một ý): PP-SWR-068 a_y của xe, PP-SWR-069 jerk ngang của xe (đo theo R79 Annex 8, 2.4), PP-SWR-070 DLC nhỏ nhất của xe ở hai phía. SRS 1.28 | SRS | Xong |
| 0.2 | SQTS 8.2 thêm 068, 069, 070. SQTS 9.1: nhóm An toàn gồm 070, 057 (và 087 cho LKA); chuyển 050 sang nhóm bám làn và cảm nhận, thêm 068; bước 5 ghi mục đích chi phí phần cứng; cửa loại tương đối và cửa tỉ lệ thời gian LCC lái cho so sánh kỹ thuật. SQTS 9.1 và 9.2: luật thắng có dung sai, n < 4 không tính. SQTS 1.52 | SQTS | Xong |
| 0.3 | Mở PP-TS-031 "Chiến dịch generator T7". `plan.yaml` ghi dung sai theo ID PP-SWR (thay khóa `DLC_min_m`), cửa loại, tiêu chí giả thuyết mục 2.5. PP-TS-024 và 025 ghi "chạy trong PP-TS-031" | `research/studies/PP-TS-031-*/`, `register.md`, hai study cũ | Xong |
| 0.4 | Thêm bốn dòng test vào PP-T7; scope thêm 068, 069, 070 | `benchmark/suites/PP-T7.yaml` | Xong |
| 0.5 | `Target` cho 068, 069 (chuyển từ `info`) và 070 (DLC của xe, mặt nạ riêng không có điều kiện aysmax); tỉ lệ thời gian LCC lái; tỉ lệ chu kỳ chạm trần a_y hoặc jerk; `pp_lcc_state_size()` và kích thước thư viện | `eval/metrics.py`, `eval/provenance.py` | Xong |
| 0.6 | `eval/output_diff.py`: lệch output so với `qp_jerk_admm_it1000_ref` và tỉ lệ chu kỳ path khác `quintic_duration`, ở vòng hở; kiểm digest đầu vào trùng | `eval/output_diff.py` (mới) | Xong |
| 0.7 | `GROUPS` mới; luật thắng có dung sai; n < 4 không tính | `eval/compare.py` | Xong |
| 0.8 | Cửa loại tương đối và cửa tỉ lệ thời gian LCC lái; bảy bảng ở GĐ 5.3; chênh lệch tuning và test; ghi `research/generators/RESULTS.md` | `eval/techniques.py` | Xong |
| 0.9 | Kiểm bên chấm cho mọi chỉ số và luật mới | `tests/eval/` | Xong phần kiểm nhẹ (25 test); cả bộ `tests/eval` chưa chạy |
| 0.10 | `python3 tools/trace.py --quiet` sạch | — | Xong |

→ Người dùng commit.

### GĐ 1: Refactor planner theo contract (cách A)

| Bước | Việc | Trạng thái |
|---|---|---|
| 1.1 | Ghi golden trước khi sửa: build `quintic` và `qp` hiện tại, chạy tuning PP-T7 (vòng hở và kín), lưu checksum bằng `eval/golden.py` | Xong: `build/golden/t7-old-quintic.json`, `t7-old-qp.json` (24 lượt mỗi bản, build từ 3b06b5d) |
| 1.2 | Tạo `planner/src/generators/pp_t7.h` (contract bên dưới) | Xong |
| 1.3 | Chuyển vòng tìm thời lượng và feasibility check từ `pp_lcc.c` sang `generators/quintic_duration.c`; chuyển phần dựng `pp_qp_problem_t` sang `generators/qp_jerk_admm.c` | Xong |
| 1.4 | `pp_lcc.c` chỉ gọi `pp_t7_generate`, `pp_t7_reset`; không còn `#ifdef PP_T7_QP` | Xong |
| 1.5 | CMake: `PP_T7` ∈ {`quintic_duration`, `qp_jerk_admm`, `lab`} cùng alias `quintic`, `qp`; `PP_T7_LAB=<tên>` đọc `research/generators/<tên>/generator.cmake`; `pp_version()` ghi tên generator và hash source lab | Xong |
| 1.6 | `gen_calibration.py` gộp phần `calibration` của `generator.yaml`; tên phải có tiền tố, trùng thì báo lỗi | Xong |
| 1.7 | Unit test `test_quintic`, `test_qp`, `test_lcc_step` cho cả hai bản; thêm `test_t7_contract.c` (L0) | Xong |
| 1.8 | So bit-exact với golden. Lệch một bit cũng phải tìm ra nguyên nhân | Xong: 24/24 lượt trùng checksum từng bit cho cả hai bản |
| 1.9 | Regression liên quan cho bản giao (`quintic_duration`), hỏi trước khi chạy (~1 giờ) | Chưa |

```c
typedef struct {
    const pp_reference_line_t *ref;
    const pp_lateral_state_t  *start;
    const pp_speed_profile_t  *speed;
    const pp_old_path_t       *old;
    bool   from_old;
    bool   recentering;
    double d_target;
    const pp_vehicle_config_t *vehicle;
} pp_t7_input_t;

/* pp_t7_ws_t do header của generator được chọn định nghĩa, kích thước cố định. */
void pp_t7_reset(pp_t7_ws_t *ws);
bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples);
```

Sàn trợ giúp PP-SWR-006 (`confirmed_turn`, `ay_support`) hiện chỉ có ở bản quintic (`#ifndef PP_T7_QP`). Contract khai báo nó thành thuộc tính của generator: `PP_T7_SUPPORT_FLOOR` bằng 1 với `quintic_duration` và 0 với `qp_jerk_admm`. Mỗi generator lab phải khai báo giá trị này.

→ Người dùng commit.

### GĐ 2: Khung lab

| Bước | Việc | Trạng thái |
|---|---|---|
| 2.1 | `research/generators/README.md`: cách thêm generator, ba tầng L0/L1/L2, quy tắc, link tới PP-T7, SQTS 9.1 và mục 2 của file này (chuyển sang README khi xóa file), không chép tiêu chí sang. Cập nhật mục Thư mục của `research/README.md` | Chưa |
| 2.2 | `registry.yaml`: tên, base, trạng thái, study, khóa CMake, session phụ trách | Chưa |
| 2.3 | `templates/generator/`: `generator.yaml`, `generator.cmake`, `src/`, `tests/`, `notes.md` | Chưa |
| 2.4 | `common/driver_shape.c`: smoothstep bậc 7, dùng chung cho `quintic_tangent_point` và `quintic_ay_sampling` | Chưa |
| 2.5 | Chuyển `pilot_driver.inc`, `pilot_qp.inc` vào thư mục generator; ghi `research/t7_potential.py` là đã có công cụ thay thế | Chưa |
| 2.6 | `bench/quick.py`: build nháp, chỉ phần tuning (từ chối seed 3–4 và dòng test), mặc định 1 job. Tập nhanh: 3 dòng vòng hở × 2 seed, S1d, S1g, S1b a vòng kín seed 1 | Chưa |
| 2.7 | Telemetry nghiên cứu: cờ `PP_T7_TELEMETRY`, chỉ có trong bản lab; `pp_t7_telemetry()` trả khối lượng việc mỗi chu kỳ, số lần dùng `quintic_duration` thay thế kèm lý do, mức T10 sửa path, residual, slack, thời gian suy luận MLP. Bản giao không có | Chưa |
| 2.8 | `eval/sweep.py` nhận giá trị cho tham số riêng của generator lab (ghi bản sao `generator.yaml` đã đổi giá trị, truyền qua `PP_T7_LAB_DIR`); cần trước GĐ 4 | Chưa |

→ Người dùng commit.

### GĐ 3: Phát triển generator (song song, mỗi luồng một session)

| Luồng | Việc | Phụ thuộc | Trạng thái |
|---|---|---|---|
| A | `qp_jerk_admm/configs/` cho `_it010` … `_it100` và `_it1000_ref`; generator `qp_jerk_admm_shift_warmstart` (C, unit test L0: dịch đúng 25 ms, bit-exact với bản QP khi không có path cũ) | GĐ 2 | Chưa |
| B | `quintic_tangent_point`, `quintic_ay_sampling`: C, unit test L0, dò bằng quick bench; điều kiện dùng `quintic_duration` thay thế theo mục 2.4 của PP-TS-024; giữ sàn PP-SWR-006 | GĐ 2 | Chưa |
| C | MLP: dữ liệu → huấn luyện → xuất, cho ba generator MLP | Trọng số tốt nhất của `qp_jerk_admm` (GĐ 4) | Chưa |

Luồng C (theo mục 2 của PP-TS-025):

1. **Dữ liệu sinh riêng, không dùng PP-T7.** Bộ sinh kịch bản lấy mẫu (SQTS 5.2) với họ đường riêng, seed từ 100, tốc độ đến 100 km/h, VP-0/1/2. Toàn bộ ca, anchor và biến thể của PP-T7 nằm ngoài train. Vùng ngoài miền để kiểm: từ 110 km/h, VP-3/5. Chia train và validation theo họ hình học đường và cấu hình nhiễu, trước khi trích cửa sổ. Tối đa 10.000 cửa sổ.
2. **Teacher.** `qp_jerk_admm` với bộ tốt nhất lái vòng kín trên dữ liệu sinh riêng; ghi đầu vào T7 từng chu kỳ; giải `qp_jerk_admm_it1000_ref` offline. Chỉ lấy nhãn khi residual và mức vi phạm ràng buộc đạt ngưỡng (chốt trên tuning); ghi riêng mẫu không hội tụ hoặc bất khả thi.
3. **Đặc trưng.** Chỉ lấy từ input của planner: 21 đặc trưng của pilot (trạng thái đầu, `d_target`, hành lang tại k = 0, tóm tắt path cũ, v, v²κ, v³κ' tại 4 điểm nút), thêm hành lang dọc horizon và giới hạn a_y. Đầu vào lệch quá 5σ so với train thì bỏ MLP, dùng warm start của bản dịch thời gian.
4. **Huấn luyện.** MLP 2 lớp ẩn × 32 nút, tối đa 20 epoch, bằng numpy. Chuẩn hóa đóng băng theo train.
5. **Xuất.** `model/weights.h` dạng mảng `const float`; suy luận C không dùng heap.
6. **Nhãn cho `qp_jerk_admm_mlp_weights`** (cách i): với mỗi cửa sổ, thử lưới (`qp_w_dev`, `qp_w_jerk`, `qp_a_comfort`) trong dải calibration; chấm bằng hàm mục tiêu thay thế tính trên path vòng hở, chốt trước khi tạo nhãn: jerk RMS của path, lệch đích, biên DLC; nhãn là bộ tốt nhất; học hồi quy. Thêm calibration parameter giới hạn tốc độ đổi trọng số mỗi chu kỳ (chặn path nhảy, PP-SWR-100).
7. **Thứ tự.** `qp_jerk_admm_mlp_warmstart` trước. `qp_jerk_admm_mlp_weights` chỉ bắt đầu sau khi có kết quả tuning của bản warm start. `mlp_jerk_direct` dùng chung dữ liệu và teacher của bản warm start.
8. **Data card** ghi: hash danh sách train và validation, teacher, calibration, bộ chuẩn hóa, seed, cấu hình huấn luyện, file weights, mã C sinh ra.

→ Người dùng commit sau mỗi generator.

### GĐ 4: Sweep tuning (chính thức, `--record`)

| Bước | Việc | Trạng thái |
|---|---|---|
| 4.1 | Chạy `qp_jerk_admm` trước để có trọng số cho bản ít vòng, bản dịch thời gian, bản MLP và teacher MLP; `qp_jerk_admm_mlp_weights` chạy sau bản MLP warm start | Chưa |
| 4.2 | Mỗi kỹ thuật chạy sweep riêng trên 24 lượt tuning | Chưa |
| 4.3 | Luật chọn (khóa trước khi chạy): qua cửa loại mục 2.2 trên tuning; rồi Copeland theo mục 2.3 giữa các cấu hình của cùng kỹ thuật; hòa thì chọn cấu hình gần mặc định nhất | Chưa |
| 4.4 | Ghi bộ tốt nhất vào `plan.yaml` của PP-TS-031, đặt `locked` | Chưa |

→ Người dùng commit, cây làm việc sạch.

### GĐ 5: Test chính thức và bảng kết quả

| Bước | Việc | Trạng thái |
|---|---|---|
| 5.1 | `python3 -m eval.study PP-TS-031 --record --jobs 2`, phần test, 19 cấu hình | Chưa |
| 5.2 | Phiên đo thời gian: 1 job, S1f và S1c vòng kín, seed 3–4, lặp 3 lần, thứ tự build xen kẽ | Chưa |
| 5.3 | `eval.techniques` sinh `research/generators/RESULTS.md` (các bảng dưới) | Chưa |
| 5.4 | Viết Kết quả và Đề xuất của PP-TS-031; phát hiện ngoài phạm vi mở PP-PR. Người dùng quyết định | Chưa |
| 5.5 | Đóng PP-TS-031: generator thắng vào `planner/src/generators/`; PP-ADR; SDD và calibration; regression trên baseline mới. **Xong bước này thì xóa file kế hoạch** | Chưa |

Bảng trong `RESULTS.md`:

| Bảng | Nội dung |
|---|---|
| 1. Kết luận và xếp hạng | Cửa loại (B0, trượt mới so với `quintic_duration`, tỉ lệ thời gian LCC lái); Copeland theo nhóm; hạng; một dòng lý do cho generator bị loại |
| 2. Hiệu ghép cặp so với `quintic_duration` | Chỉ các chỉ số xếp hạng (mục 2.3): trung bình [CI 95 %], n, dung sai, ca xấu nhất; tách theo cua ngắn (S1f, S14e), cua gắt (S1c, S1b), nhiễu (F01, S12), chức năng (S2, S3, S17, S22) |
| 3. Giả thuyết | Mục 2.5, mỗi generator một dòng: đạt hay không đạt, kèm số liệu |
| 4. Số vòng QP | Số vòng, p99 và % chu kỳ 25 ms, lệch so với bản 1000 vòng, a_y và jerk xe, trượt; bản QP, bản dịch thời gian và bản MLP warm start; kèm Pareto |
| 5. Chi phí vận hành | Mục 2.4: p99, max, khối lượng việc, bộ nhớ state, kích thước thư viện và weights |
| 6. Độ tin | Mục 2.6: digest đầu vào, tỉ lệ chu kỳ khác mốc, chênh tuning và test, số chỉ số có n < 4 |
| 7. Chẩn đoán | Mục 2.7, gắn nhãn không xếp hạng |
| 8. Flexibility | Profile × chỉ số |

Mỗi dòng ghi run ID và `pp_version`. Kết quả nháp L1 có nhãn "nháp".

## 7. Quy tắc

- L1 và dữ liệu MLP không dùng seed 3–4 hay dòng chỉ có ở test.
- Từ GĐ 4, không đổi suite, tiêu chí, dung sai, seed, luật chọn. Buộc phải đổi thì ghi lý do và chạy lại mọi phương án.
- Ca trượt thì sửa cơ chế chung của generator, không sửa riêng cho ca đó.
- Mỗi generator chỉ sửa trong thư mục của nó. Contract, CMake, registry chỉ sửa ở một session.

## 8. Quyết định

| Quyết định | Trạng thái |
|---|---|
| Mở PP-TS-031 gộp mọi biến thể thay vì chạy riêng PP-TS-024, 025 | Đã duyệt 2026-11-23 |
| Số vòng QP 10/25/50/75/100/150, cộng bản tham chiếu 1000; bản MLP warm start ở 10/25/50/75 | Đã duyệt 2026-11-23 |
| Huấn luyện MLP bằng numpy | Đã duyệt 2026-11-23 |
| ID mới PP-SWR-068 (a_y xe), PP-SWR-069 (jerk xe), PP-SWR-070 (DLC nhỏ nhất của xe); tách ba ID theo luật một câu một ý | Đã duyệt 2026-11-23 (tách ba ID: chờ duyệt) |
| Sàn PP-SWR-006 là thuộc tính khai báo của generator | Đã duyệt 2026-11-23 |
| Đổi giá trị CMake sang `quintic_duration`, `qp_jerk_admm`, giữ alias `quintic`, `qp` | Đã duyệt 2026-11-23 |
| Bước An toàn dùng DLC (070) thay cho lệch tâm (050); 050 chuyển sang bước 3 | Đã duyệt 2026-11-23 |
| Cửa loại tỉ lệ thời gian LCC lái, ngưỡng một chu kỳ | Đã duyệt 2026-11-23 |
| Thêm `[S2, e]`, `[S3, a]` vào test | Đã duyệt 2026-11-23 |
| Luật thắng CI và dung sai thực tế; n < 4 không tính | Đã duyệt 2026-11-23 |
| Tiêu chí giả thuyết mục 2.5; danh sách chẩn đoán và bỏ (mục 2.7, 2.8) | Đã duyệt 2026-11-23 |
| Thêm đối chứng không học `qp_jerk_admm_shift_warmstart` (4 mức số vòng) | Đã duyệt 2026-11-23 |
| Dữ liệu MLP sinh riêng theo PP-TS-025, toàn bộ PP-T7 ngoài train, vùng ngoài miền 110–130 km/h và VP-3/5 | Đã duyệt 2026-11-23 |
| Nhãn của `qp_jerk_admm_mlp_weights` bằng lưới offline với hàm mục tiêu thay thế định trước; giới hạn tốc độ đổi trọng số; làm sau bản warm start | Đã duyệt 2026-11-23 |
| Thời gian tính được đánh giá như chi phí phần cứng; thêm max, khối lượng việc, bộ nhớ state, kích thước thư viện làm ngữ cảnh (mục 2.4) | Chờ duyệt phần ngữ cảnh |
