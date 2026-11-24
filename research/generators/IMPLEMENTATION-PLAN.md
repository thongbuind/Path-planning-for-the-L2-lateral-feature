# Generator Lab Implementation Plan

> **Tài liệu tạm.** Xóa file này khi xong bước cuối: GĐ 5.6 (dashboard sinh từ các lần chạy `--record` đã commit, PP-TS-031 đã ghi run ID và đóng). Khi xóa, mọi điều còn giá trị phải đã nằm ở `research/generators/README.md`, PP-TS-031 hoặc bộ tài liệu kỹ thuật.

| Mục | Nội dung |
|---|---|
| Lập ngày | 2026-11-23 |
| Mục đích | Nghiên cứu: một dashboard so sánh khả năng của các họ thuật toán T7 ở nhiều khía cạnh, để mentor xem. Lab không chọn generator, không xếp hạng tổng và không thuộc luồng chính. Chọn generator là việc của người dùng; đưa generator vào planner là việc riêng, ngoài lab |
| Đã chốt | Nối lab vào planner theo cách A (refactor T7 theo contract chung); tên theo thuật toán (mục 1); cách đánh giá (mục 2); các quyết định ở mục 8. Duyệt ngày 2026-11-23; mục đích và GĐ 4, 5 sửa ngày 2026-11-24 |
| Đang mở | GĐ 3 đang làm (mỗi luồng một agent con); code của GĐ 4.2, 5.2–5.4 đã có, chờ các lần chạy |
| Liên quan | PP-TS-003, PP-TS-013, PP-TS-024, PP-TS-025; suite PP-T7; SQTS mục 7–10 |

## 1. Quy tắc đặt tên

Tên = `<thuật toán gốc>[_<phần ghép>][_it<số vòng, 3 chữ số>]`.

- Một tên dùng chung cho thư mục `research/generators/<tên>/`, giá trị `PP_T7` hoặc `PP_T7_LAB`, `registry.yaml`, ID biến thể trong `plan.yaml` và dòng trên dashboard.
- Một cấu hình trong lưới calibration: `<tên>-<tham số><giá trị>-...`, ví dụ `quintic_duration-Thwa3.0-Trec3.5`.
- Hai giá trị CMake cũ `quintic` và `qp` giữ làm alias của `quintic_duration` và `qp_jerk_admm`, để plan và script cũ (PP-TS-003, PP-TS-013, `t7_potential.py`) vẫn chạy.
- Mã V0, VQ, V1… trong PP-TS-024 và 025 giữ nguyên trong hai study đó (lịch sử). PP-TS-031 chỉ dùng tên mới.
- Trên dashboard, tên đặt ở hàng, không đặt ở cột.

| Tên | Thuật toán | Mã cũ |
|---|---|---|
| `quintic_duration` | Đa thức bậc 5 d(t) từ (d0, v0, a0) tới (d1, 0, 0), tìm thời lượng tăng dần 0,25 s tới khi đạt feasibility | V0 |
| `qp_jerk_admm` | QP biến là jerk ngang trên 30 bước, mô hình thay đổi theo thời gian (LTV), ràng buộc mềm, giải bằng ADMM có warm start. Mặc định 150 vòng | VQ, V1 |
| `qp_jerk_admm_it010` … `_it100` | Như trên, số vòng cố định 10/25/50/75/100 | V1r (75) |
| `qp_jerk_admm_it1000_ref` | Như trên, 1000 vòng, chỉ làm nghiệm tham chiếu hội tụ, không so như một thuật toán | — |
| `quintic_tangent_point` | Quintic cộng hiệu chỉnh ngang smoothstep bậc 7, đỉnh đặt theo tangent point (Land và Lee, 1994) | PP-TS-024 V1 |
| `quintic_ay_sampling` | Quintic cộng hiệu chỉnh ngang, chọn trong tập ứng viên theo đỉnh a_y và jerk dự báo | PP-TS-024 V2 |
| `qp_jerk_admm_shift_warmstart_it010` … `_it075` | Warm start ADMM bằng x của chu kỳ trước được dịch theo thời gian (25 ms = 1/4 bước lưới 0,1 s; nội suy, ngoại suy jerk cuối). Đối chứng không học cho bản MLP warm start | — |
| `qp_jerk_admm_mlp_warmstart_it010` … `_it075` | MLP dự đoán chuỗi jerk làm warm start cho ADMM, cùng số vòng với bản QP để ghép cặp | PP-TS-025 V2 |
| `qp_jerk_admm_mlp_weights` | MLP chọn trọng số QP, kẹp trong dải calibration, 150 vòng | PP-TS-025 V3 |
| `mlp_jerk_direct` | MLP xuất thẳng chuỗi jerk, tích phân ra path, qua T10 và T4 chung (đối chứng) | PP-TS-025 V4 |

R-cam của PP-TS-013 là nguyên mẫu Python nên không vào benchmark.

## 2. Cách đánh giá

### 2.1 Nguyên tắc

- Dashboard so khả năng, không chấm ai thắng: không có hạng tổng, điểm tổng hay luật chọn generator. Người dùng tự đọc và quyết định.
- Một thông tin được giữ khi nó phục vụ ít nhất một khía cạnh của dashboard (GĐ 5.4), một giả thuyết của generator, hoặc độ tin của kết quả. Thông tin chỉ giải thích vì sao thì để ở mục chẩn đoán.
- Chỉ số của xe đo trên chuyển động thật so với làn thật, trong vòng kín. Chỉ số của path đọc ở vòng hở, vì ở đó đầu vào trùng nhau từng chu kỳ giữa các build.
- Ghép cặp: vòng hở theo từng chu kỳ; vòng kín theo từng lượt (ca, profile, seed).
- Mốc so sánh: `quintic_duration` ở calibration mặc định (`T_hwa` 3,0 s, `T_recenter` 3,5 s), tức bản đang giao.

### 2.2 Cờ cảnh báo

Cờ không loại thuật toán nào. Cờ hiện cạnh chỉ số để người đọc không hiểu sai một ô trông tốt.

| Cờ | Bật khi | Hiện trên dashboard | Đã có trong eval |
|---|---|---|---|
| B0 (C1, C2), lỗi thực thi | Lượt trượt C1, C2 hoặc lỗi chạy | Cờ đỏ ở cấu hình đó; lượt đó không vào hiệu ghép cặp | Có |
| Trượt mới | Requirement trong scope PP-T7 trượt mà mốc đạt ở cùng ca, profile, seed | Cờ kèm danh sách lượt. Lỗi chung (mốc cũng trượt) liệt kê riêng | Có |
| LCC lái ít hơn | Tỉ lệ thời gian LCC lái (`path_valid`, `lcc_mode`) thấp hơn mốc quá một chu kỳ (25 ms) ở một lượt | Cờ cạnh các chỉ số độ êm: generator thất bại, LCC ngừng lái, nên trông "êm" hơn | Có |

PP-SWR-006 (sàn hỗ trợ) là chỗ dễ có trượt mới với generator cắt cua.

### 2.3 Chỉ số so sánh theo khía cạnh

Nhóm và thứ tự hiện theo SQTS 9.1. Đại lượng an toàn là khoảng cách tới biên làn (DLC), không phải lệch khỏi tâm làn. PP-SWR-050 giữ lại (từ đề bài) ở nhóm bám làn và cảm nhận.

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

- Cột "Bước" chỉ là số nhóm của SQTS 9.1, dùng để sắp các nhóm trên dashboard, không phải thứ tự xếp hạng.
- **Mỗi ô so với mốc:** trung bình hiệu ghép cặp kèm CI 95 % bootstrap, n và ca xấu nhất. Ô được đánh dấu "khác có ý nghĩa" (tốt hơn hoặc xấu hơn) khi CI không chứa 0 **và** |trung bình hiệu| ≥ dung sai thực tế. Không thì ghi "trong dung sai".
- Chỉ số có n < 4 cặp: ghi "ít dữ liệu", không đánh dấu.
- Dung sai là `nhóm tự thống nhất`. Nguồn: ba mức đã có trong plan của PP-TS-024 (050, DLC, 002); ngưỡng giả thuyết của PP-TS-024 (a_y, jerk); 0,1 s là 4 chu kỳ; 5 % và 10 % là tương đối vì chưa có thang tuyệt đối hoặc vì nhiễu đo trên laptop.
- Lab không dùng luật thắng, Copeland hay cửa loại của SQTS 9.1, 9.2 để chọn generator. Hai mục đó giữ nguyên làm quy tắc chung của dự án khi người dùng quyết định đưa một kỹ thuật vào planner.

### 2.4 Chi phí vận hành

Mục đích: so phần cứng cần để chạy mỗi generator. Generator tính nhanh và nhẹ chạy được trên phần cứng rẻ hơn. Phần cứng được chọn theo trường hợp xấu nhất, và thời gian đo trên laptop không chuyển thẳng sang ECU, nên bảng có thêm thước đo không phụ thuộc máy.

| Thông tin | Vai trò | Hộp đen |
|---|---|---|
| p99 thời gian CPU của `pp_lcc_step`, kèm % chu kỳ 25 ms | So sánh (nhóm 5) | Có |
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
| `qp_jerk_admm_mlp_weights` | Trọng số thích nghi tốt hơn trọng số cố định | Các ô nhóm 2–3 so với `qp_jerk_admm` mặc định (mục 2.3) | Ít nhất một ô "tốt hơn có ý nghĩa", không ô nào "xấu hơn có ý nghĩa" | Toàn bộ test |
| `mlp_jerk_direct` | Đối chứng: MLP thuần không đủ an toàn khi đứng một mình | Cờ cảnh báo (mục 2.2) | Báo các cờ bật; dự kiến có trượt mới. Là ví dụ kỹ thuật không dùng được, kèm lý do (đề bài) | Toàn bộ test |

- Các tiêu chí này khóa trong `plan.yaml` của PP-TS-031 trước lần chạy `--record` đầu tiên.
- Thuật toán có lưới calibration thì giả thuyết được kiểm ở từng cấu hình của lưới và báo "đạt ở x/9 cấu hình". Không chọn ra cấu hình đạt để báo thay cho cả lưới.
- Mốc của giả thuyết là cấu hình mặc định: `quintic_duration` mặc định cho H1; `qp_jerk_admm` mặc định (`qp_w_dev` 0,30, `qp_w_comfort` 5,0) cho các bản QP ít vòng, bản dịch thời gian, bản MLP.

### 2.6 Độ tin của kết quả

| Thông tin | Đã có trong eval |
|---|---|
| Digest đầu vào trùng giữa các build ở vòng hở (`case_hash`) | Có |
| Số cặp n và điều kiện áp dụng của mỗi chỉ số | Một phần |
| Tỉ lệ chu kỳ path khác `quintic_duration` ở vòng hở: generator có thực sự hoạt động không | Chưa |
| Chênh lệch giữa tuning và test của từng cấu hình, để phát hiện quá khớp do dò tay bằng quick bench trên các dòng tuning | Chưa |
| Run ID, `pp_version`, hash calibration | Có |

### 2.7 Chẩn đoán (không so với mốc)

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

Không chọn cấu hình nào. Mọi cấu hình của lưới chạy trên cả tuning và test, và đều hiện trên dashboard.

| Tên | Lưới calibration | Số cấu hình | Cấu hình mặc định |
|---|---|---|---|
| `quintic_duration` | `T_hwa` 2,5/3,0/3,5 s × `T_recenter` 3,0/3,5/4,0 s | 9 | 3,0 s; 3,5 s (mốc) |
| `qp_jerk_admm` (150 vòng) | `qp_w_dev` 0,15/0,30/0,60 × `qp_w_comfort` 2,5/5/10 | 9 | 0,30; 5,0 |
| `qp_jerk_admm_it010` … `_it100` | Không có lưới; trọng số mặc định của `qp_jerk_admm` | 5 | — |
| `qp_jerk_admm_it1000_ref` | Chỉ chạy lượt vòng hở | — | — |
| `quintic_tangent_point` | Tâm cửa sổ nhìn trước 1,5/1,75/2,0 s × biên DLC 0/0,01/0,02 m (biên độ giữ 0,20 m: chặn theo DLC luôn chặn trước; 1,0 s không bao giờ kích hoạt trên tuning) | 9 | Tâm lưới, khai báo trong `generator.yaml` |
| `quintic_ay_sampling` | Cặp vị trí đỉnh (0,35; 0,55)/(0,40; 0,60)/(0,45; 0,65) × biên độ 0,10/0,20/0,30 m | 9 | Tâm lưới, khai báo trong `generator.yaml` |
| `qp_jerk_admm_shift_warmstart_it010` … `_it075` | Không có lưới; 4 mức số vòng, trọng số mặc định của `qp_jerk_admm` | 4 | — |
| `qp_jerk_admm_mlp_warmstart_it010` … `_it075` | 4 mức số vòng, ghép cặp với bản QP và bản dịch thời gian cùng số vòng | 4 | — |
| `qp_jerk_admm_mlp_weights` | Hệ số điều chuẩn khi huấn luyện, 3 mức | 3 | Mức giữa |
| `mlp_jerk_direct` | Không có lưới | 1 | — |
| **Tổng** | | **53** | |

- QP chạy đủ `qp_iters` vòng, không dừng sớm. Thời gian vì thế tăng gần tuyến tính theo số vòng.
- Bản QP ít vòng, bản dịch thời gian, bản MLP warm start và teacher của MLP dùng trọng số mặc định của `qp_jerk_admm`, để chỉ có số vòng và điểm xuất phát thay đổi. Nhờ vậy luồng C không phải chờ kết quả lưới.
- Cấu hình mặc định là dòng đại diện của thuật toán ở bảng tổng quan; cả lưới hiện ở phần độ nhạy calibration. Không lấy cấu hình tốt nhất của lưới làm đại diện, vì như thế là chọn trên chính dữ liệu dùng để so, và thuật toán có lưới lớn sẽ được lợi.
- Ngân sách tối đa 9 cấu hình cho mỗi kỹ thuật (`research/README.md`).

## 4. Bài kiểm

| Phần | Lượt | Seed | Lượt mỗi cấu hình |
|---|---|---|---|
| Tuning | 14 dòng PP-T7 | 1, 2 | 28 |
| Test | 28 dòng PP-T7 + 4 dòng mới | 3, 4 | 64 |

Dòng mới thêm vào tuning (Software Qualification Test Specification mục 5), ngày 2026-11-24, trước GĐ 4: `[S24, a]`, cua 110 km/h R = 450 m, ngắn theo mét nhưng đỉnh a_y dài 4,25 s; `[S24, b]`, cua 72 km/h R = 180 m, cả cua 2,5 s. Lý do: tuning chưa có cua ngắn nên các generator cắt cua không chỉnh được; S1 f, S14 e chỉ ở test. b thêm sau khi quick bench cho thấy a dài hơn tầm nhìn 3 s của generator.

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
| Lưới trên tuning (GĐ 4) | 53 × 28 = 1484, cộng các lượt vòng hở của bản tham chiếu | ~75 phút |
| Lưới trên test (GĐ 5) | 53 × 64 = 3392, cộng các lượt vòng hở của bản tham chiếu | ~3 giờ |
| Phiên đo thời gian (GĐ 5) | 19 cấu hình (mặc định của mỗi lưới, mỗi mức số vòng) × 4 lượt × 3 lần lặp, 1 job | ~25 phút |
| **Tổng** | | **~4,5–5 giờ**, chưa tính dữ liệu và nhãn MLP; chia nhiều lần, mỗi lần một nhóm thuật toán; bản QP có thể nặng hơn ~30 % |

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
| 2.1 | `research/generators/README.md`: cách thêm generator, ba tầng L0/L1/L2, quy tắc, link tới PP-T7, SQTS 9.1 và mục 2 của file này (chuyển sang README khi xóa file), không chép tiêu chí sang. Cập nhật mục Thư mục của `research/README.md` | Xong |
| 2.2 | `registry.yaml`: tên, base, trạng thái, study, khóa CMake, session phụ trách | Xong |
| 2.3 | `templates/generator/`: `generator.yaml`, `generator.cmake`, `src/`, `tests/`, `notes.md` | Xong (cùng `new_generator.py`) |
| 2.4 | `common/driver_shape.c`: smoothstep bậc 7, dùng chung cho `quintic_tangent_point` và `quintic_ay_sampling` | Xong |
| 2.5 | Chuyển `pilot_driver.inc`, `pilot_qp.inc` vào thư mục generator; ghi `research/t7_potential.py` là đã có công cụ thay thế | Xong: `pilots/`; `t7_potential.py` lấy nguồn từ 3b06b5d |
| 2.6 | `bench/quick.py`: build nháp, chỉ phần tuning (từ chối seed 3–4 và dòng test), mặc định 1 job. Tập nhanh: 3 dòng vòng hở × 2 seed, S1d, S1g, S1b a vòng kín seed 1 | Xong |
| 2.7 | Telemetry nghiên cứu: cờ `PP_T7_TELEMETRY`, chỉ có trong bản lab; `pp_t7_telemetry()` trả khối lượng việc mỗi chu kỳ, số lần dùng `quintic_duration` thay thế kèm lý do, mức T10 sửa path, residual, slack, thời gian suy luận MLP. Bản giao không có | Xong: phần C (`pp_lcc_t7_telemetry`, `pp_lcc_t7_workspace` cho teacher); eval đọc và tóm tắt mỗi lượt vào `t7_telemetry` (`eval/telemetry.py`); quick bench hiện cột telemetry |
| 2.8 | `eval/sweep.py` nhận giá trị cho tham số riêng của generator lab (ghi bản sao `generator.yaml` đã đổi giá trị, truyền qua `PP_T7_LAB_DIR`); cần trước GĐ 4 | Xong (`PP_T7_LAB_CALIBRATION`) |
| 2.9 | Contract bổ sung cho GĐ 3: input thêm `follow`, `start_from_car`, `objects`; `generators/t7_common.c` (vòng tìm thời lượng trả path Frenet, dựng bài toán QP); `pp_generate_qp_seeded`, `pp_qp_stats`; unit test lab qua `PP_T7_TESTS`. Golden kiểm lại | Xong |

→ Người dùng commit.

### GĐ 3: Phát triển generator (song song, mỗi luồng một session)

| Luồng | Việc | Phụ thuộc | Trạng thái |
|---|---|---|---|
| A | `qp_jerk_admm/configs/` cho `_it010` … `_it100` và `_it1000_ref`; generator `qp_jerk_admm_shift_warmstart` (C, unit test L0: dịch đúng 25 ms, bit-exact với bản QP khi không có path cũ) | GĐ 2 | Chưa |
| B | `quintic_tangent_point`, `quintic_ay_sampling`: C, unit test L0, dò bằng quick bench; điều kiện dùng `quintic_duration` thay thế theo mục 2.4 của PP-TS-024; giữ sàn PP-SWR-006 | GĐ 2 | Chưa |
| C | MLP: dữ liệu → huấn luyện → xuất, cho ba generator MLP | GĐ 2; trọng số mặc định của `qp_jerk_admm` | Chưa |

Luồng C (theo mục 2 của PP-TS-025):

1. **Dữ liệu sinh riêng, không dùng PP-T7.** Bộ sinh kịch bản lấy mẫu (SQTS 5.2) với họ đường riêng, seed từ 100, tốc độ đến 100 km/h, VP-0/1/2. Toàn bộ ca, anchor và biến thể của PP-T7 nằm ngoài train. Vùng ngoài miền để kiểm: từ 110 km/h, VP-3/5. Chia train và validation theo họ hình học đường và cấu hình nhiễu, trước khi trích cửa sổ. Tối đa 10.000 cửa sổ.
2. **Teacher.** `qp_jerk_admm` với trọng số mặc định lái vòng kín trên dữ liệu sinh riêng; ghi đầu vào T7 từng chu kỳ; giải `qp_jerk_admm_it1000_ref` offline. Chỉ lấy nhãn khi residual và mức vi phạm ràng buộc đạt ngưỡng (chốt trên phần validation của dữ liệu sinh riêng); ghi riêng mẫu không hội tụ hoặc bất khả thi.
3. **Đặc trưng.** Chỉ lấy từ input của planner: 21 đặc trưng của pilot (trạng thái đầu, `d_target`, hành lang tại k = 0, tóm tắt path cũ, v, v²κ, v³κ' tại 4 điểm nút), thêm hành lang dọc horizon và giới hạn a_y. Đầu vào lệch quá 5σ so với train thì bỏ MLP, dùng warm start của bản dịch thời gian.
4. **Huấn luyện.** MLP 2 lớp ẩn × 32 nút, tối đa 20 epoch, bằng numpy. Chuẩn hóa đóng băng theo train.
5. **Xuất.** `model/weights.h` dạng mảng `const float`; suy luận C không dùng heap.
6. **Nhãn cho `qp_jerk_admm_mlp_weights`** (cách i): với mỗi cửa sổ, thử lưới (`qp_w_dev`, `qp_w_jerk`, `qp_a_comfort`) trong dải calibration; chấm bằng hàm mục tiêu thay thế tính trên path vòng hở, chốt trước khi tạo nhãn: jerk RMS của path, lệch đích, biên DLC; nhãn là bộ tốt nhất; học hồi quy. Thêm calibration parameter giới hạn tốc độ đổi trọng số mỗi chu kỳ (chặn path nhảy, PP-SWR-100).
7. **Thứ tự.** `qp_jerk_admm_mlp_warmstart` trước. `qp_jerk_admm_mlp_weights` chỉ bắt đầu sau khi bản warm start đã có kết quả quick bench (L1). `mlp_jerk_direct` dùng chung dữ liệu và teacher của bản warm start.
8. **Data card** ghi: hash danh sách train và validation, teacher, calibration, bộ chuẩn hóa, seed, cấu hình huấn luyện, file weights, mã C sinh ra.

→ Người dùng commit sau mỗi generator.

### GĐ 4: Chạy cả lưới trên tuning (chính thức, `--record`)

Không có bước chọn. Lần chạy này cho phần tuning của dashboard và cho chênh lệch tuning–test (mục 2.6).

| Bước | Việc | Trạng thái |
|---|---|---|
| 4.1 | Khóa `plan.yaml` của PP-TS-031 (`locked`) trước lần chạy `--record` đầu tiên: lưới, cấu hình mặc định, cờ, dung sai, giả thuyết, nhóm ca, các khía cạnh của dashboard | Xong 2026-11-24: lưới đủ 54 cấu hình (gồm nghiệm tham chiếu), `grid_sets` strict không cảnh báo |
| 4.2 | `eval.study` chạy được cả lưới (`tuning_grid`) như các biến thể riêng, trên cả hai phần. `--group <biến thể>` chạy một thuật toán cùng lưới của nó, kể cả khi `--record`, và tự thêm mốc, nghiệm tham chiếu để hiệu ghép cặp tính trong cùng lần chạy | Xong code (`eval/study.py`) |
| 4.3 | Chạy 53 cấu hình × 28 lượt tuning, chia theo nhóm thuật toán khi generator của nhóm đó xong GĐ 3. Thứ tự không phụ thuộc nhau, vì mọi bản dùng trọng số mặc định | Chưa |

→ Người dùng commit, cây làm việc sạch.

### GĐ 5: Đo trên test và dashboard

| Bước | Việc | Trạng thái |
|---|---|---|
| 5.1 | `python3 -m eval.study PP-TS-031 --record --jobs 2 --part test [--group <biến thể>]`, cả 53 cấu hình; chia theo nhóm thuật toán | Chưa |
| 5.2 | Phiên đo thời gian: 1 job, S1f và S1c vòng kín, seed 3–4, lặp 3 lần, thứ tự build xen kẽ; 19 cấu hình (mặc định của mỗi lưới, mỗi mức số vòng). p99 của mọi cấu hình vẫn có từ 5.1, ghi là đo ở 2 job | Xong code (`eval/timing_session.py`); chưa chạy |
| 5.3 | Dữ liệu dashboard không xếp hạng: cờ (mục 2.2), hiệu ghép cặp có nhãn từng ô, giả thuyết cho từng cấu hình của lưới, chi phí, độ tin, chẩn đoán; gộp nhiều lần chạy; ghi `dashboard/techniques.json`. Phần báo cáo có xếp hạng của `eval/techniques.py --study` bỏ; phần so kỹ thuật theo thư mục giữ cho SQTS 9.1 chung | Xong code (`eval/campaign.py`, test trong `tests/eval/test_generator_campaign.py`) |
| 5.4 | `research/generators/dashboard/build.py` sinh `research/generators/dashboard/index.html` từ `techniques.json` (các khía cạnh dưới) | Xong code, thử trên dữ liệu giả; chưa sinh từ lần chạy thật |
| 5.5 | Viết Kết quả của PP-TS-031 (mô tả, không đề xuất chọn); phát hiện ngoài phạm vi mở PP-PR | Chưa |
| 5.6 | Đóng PP-TS-031: run ID, link dashboard. Chọn generator và đưa vào planner là việc riêng của người dùng, ngoài lab. **Xong bước này thì xóa file kế hoạch** | Chưa |

Dashboard (`index.html`):

- Một file HTML tự chứa: CSS và SVG viết sẵn trong file, không tải gì từ mạng, mở offline được, có chế độ sáng và tối.
- Sinh từ các lần chạy `--record`. Chạy nháp hay cây làm việc bẩn thì mọi trang có nhãn "nháp".
- Không có hạng, điểm tổng hay ô "thuật toán tốt nhất". Màu ô chỉ cho biết hiệu so với mốc tốt hơn, xấu hơn hay trong dung sai (mục 2.3).
- Mỗi số có n, CI và link tới run ID; chân trang ghi `pp_version` và hash calibration của từng cấu hình.

| Khía cạnh | Nội dung |
|---|---|
| Tổng quan | Hàng: từng thuật toán ở cấu hình mặc định. Cột: các nhóm của mục 2.3. Ô: hiệu so với mốc và dải min–max của cả lưới. Cờ cảnh báo ngay trên hàng |
| An toàn | PP-SWR-070, 057: hiệu ghép cặp, ca xấu nhất, phân bố theo lượt |
| Bám làn và cảm nhận | PP-SWR-050, 068, 069, 004, 002, 053, 059 |
| Theo nhóm ca | Cua ngắn (S1f, S14e), cua gắt (S1c, S1b), nhiễu (F01, S12), chức năng (S2, S3, S17, S22) |
| Flexibility | Profile × chỉ số; độ chênh giữa VP-0, VP-3, VP-5 |
| Chi phí phần cứng | Mục 2.4: p99 và % chu kỳ 25 ms, max, khối lượng việc, bộ nhớ state, kích thước thư viện và weights |
| Độ nhạy calibration | Mỗi lưới 3 × 3 một bản đồ nhiệt theo từng chỉ số, trên tuning và test |
| Số vòng QP | Lệch so với bản 1000 vòng theo p99, cho bản QP, bản dịch thời gian và bản MLP warm start; kèm Pareto |
| Giả thuyết | Mục 2.5: đạt ở bao nhiêu cấu hình, kèm số liệu |
| Cờ cảnh báo | Mục 2.2: từng lượt bật cờ; lỗi chung của cả mốc |
| Độ tin | Mục 2.6: digest đầu vào, tỉ lệ chu kỳ khác mốc, chênh tuning–test, chỉ số có n < 4 |
| Chẩn đoán | Mục 2.7, gắn nhãn "không so với mốc" |

Kết quả nháp L1 không vào dashboard.

## 7. Quy tắc

- L1 và dữ liệu MLP không dùng seed 3–4 hay dòng chỉ có ở test.
- Từ GĐ 4, không đổi suite, lưới, cấu hình mặc định, cờ, dung sai, giả thuyết, seed. Buộc phải đổi thì ghi lý do và chạy lại mọi phương án.
- Lab không chọn generator và không đề xuất chọn. Dashboard và PP-TS-031 chỉ mô tả.
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
| Cửa loại tỉ lệ thời gian LCC lái, ngưỡng một chu kỳ | Đã duyệt 2026-11-23; từ 2026-11-24 lab dùng làm cờ, không loại |
| Thêm `[S2, e]`, `[S3, a]` vào test | Đã duyệt 2026-11-23 |
| Luật thắng CI và dung sai thực tế; n < 4 không tính | Đã duyệt 2026-11-23; từ 2026-11-24 lab dùng làm nhãn từng ô, không tính thắng |
| Tiêu chí giả thuyết mục 2.5; danh sách chẩn đoán và bỏ (mục 2.7, 2.8) | Đã duyệt 2026-11-23 |
| Thêm đối chứng không học `qp_jerk_admm_shift_warmstart` (4 mức số vòng) | Đã duyệt 2026-11-23 |
| Dữ liệu MLP sinh riêng theo PP-TS-025, toàn bộ PP-T7 ngoài train, vùng ngoài miền 110–130 km/h và VP-3/5 | Đã duyệt 2026-11-23 |
| Nhãn của `qp_jerk_admm_mlp_weights` bằng lưới offline với hàm mục tiêu thay thế định trước; giới hạn tốc độ đổi trọng số; làm sau bản warm start | Đã duyệt 2026-11-23 |
| Thời gian tính được đánh giá như chi phí phần cứng; thêm max, khối lượng việc, bộ nhớ state, kích thước thư viện làm ngữ cảnh (mục 2.4) | Chờ duyệt phần ngữ cảnh |
| Lab là nghiên cứu, ra một dashboard so sánh cho mentor; không chọn generator, không xếp hạng tổng, không thuộc luồng chính | Người dùng quyết 2026-11-24 |
| Không chọn cấu hình; cả lưới chạy trên tuning và test, đều hiện trên dashboard | Người dùng quyết 2026-11-24 |
| Dashboard là một file HTML tĩnh tự chứa trong `research/generators/dashboard/` | Người dùng quyết 2026-11-24 |
| Cửa loại thành cờ cảnh báo; luật thắng thành nhãn "khác có ý nghĩa" từng ô; giữ dung sai | Đã duyệt 2026-11-24 |
| Mốc là cấu hình mặc định; dòng đại diện trên tổng quan là cấu hình mặc định, không phải cấu hình tốt nhất của lưới | Đã duyệt 2026-11-24 |
| Bản QP ít vòng, bản dịch thời gian, bản MLP và teacher dùng trọng số mặc định của `qp_jerk_admm`; luồng C không chờ GĐ 4 | Đã duyệt 2026-11-24 |
| Giữ lần chạy tuning `--record` (GĐ 4) chỉ để đo chênh lệch tuning–test và độ nhạy trên tuning | Đã duyệt 2026-11-24 |
| Phiên đo thời gian 1 job chỉ cho 19 cấu hình mặc định; p99 của cả lưới lấy từ lần chạy 2 job | Đã duyệt 2026-11-24 |
