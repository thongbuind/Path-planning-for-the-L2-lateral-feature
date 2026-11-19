# PP-TS-021 Điểm đầu path HWA khi xe rời path cũ (T4)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã quyết: V7 |
| Mở ngày | 2026-11-16 |
| Khóa ngày | 2026-11-16 |
| Quyết định ngày | 2026-11-16 |
| Liên quan | PP-SWR-100, 101, 102, 001, 051; R79 5.6.2.1.1, Annex 8 3.2.2; `stitch_reset`, `cont_margin`, T4; PP-PR-056; PP-TS-019 (V3, V4), PP-TS-020 |

## 1. Câu hỏi

- Quyết định cần đưa ra: khi xe đã rời path cũ, path HWA mới bắt đầu ở đâu, và T4 bước 4 được kéo điểm đầu về path cũ tới mức nào.
- Vì sao cần: ở S1b a, b (bài R79 Annex 8, 3.2.2), a_y của xe vượt aysmax + 0,3 m/s² quá 2 s ở bản hiện tại (PP-PR-056, [20261116-1607-study-PP-TS-020-d1d50de](../../runs/20261116-1607-study-PP-TS-020-d1d50de/summary.md)).

Chẩn đoán nháp ở PP-PR-056, mục 2:

| Ca | Bản | Điểm đầu path lệch xe | a_y xe trừ a_y path, 5 s cuối [m/s²] | R79 |
|---|---|---|---|---|
| S1b a | V0 | 0,16–0,20 m | 0,46 | Trượt |
| S1b a | `stitch_reset` = 0 | 0 | 0,10 | Đạt |
| S1b b | V0 | 0,16–0,20 m | 0,78 | Trượt |
| S1b b | `stitch_reset` = 0 | 0 tới 13 s, rồi tới 0,42 m | 0,83 | Trượt |

Cơ chế, đọc từ code T4 (`pp_stitch_start`, `pp_stitch_blend`):

- Bước 2: lệch quá `stitch_reset` (0,2 m) thì lấy trạng thái đo.
- Bước 4 chạy sau đó với HWA ở mọi chu kỳ, kể cả chu kỳ vừa reset: path gửi = path cũ + λ·(path ứng viên − path cũ), một λ cho cả 31 điểm, gồm điểm 0. Bước 4 kéo lại phần lớn lần reset, nên lệch đứng sát dưới 0,2 m.
- λ do chênh lệch lớn nhất trên cả tầm nhìn quyết định. Khi path ứng viên khác path cũ nhiều ở phần xa, λ nhỏ và điểm đầu gần như không theo xe (S1b b).
- Controller chạy thử bám được path khi path bắt đầu từ xe (S1b a, `stitch_reset` = 0). Nguồn làm xe rời path cũ ban đầu chưa rõ (PP-PR-056, mục 2).

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Bản hiện tại: `stitch_reset` 0,2 m; bước 4 một λ cho cả path | — | Mốc; cũng là V3 của PP-TS-019 |
| V1 | `stitch_reset` 0,1 m | `calibration: {stitch_reset: 0.1}` | Trong dải quét của Software Architectural Design 11 |
| V2 | `stitch_reset` 0 m: luôn bắt đầu từ trạng thái đo | `calibration: {stitch_reset: 0.0}` | Ngoài dải quét (0,1–0,4), trong giới hạn của SRS (≥ 0). Bước 4 vẫn trộn |
| V3 | Bước 4 trộn theo từng đoạn 0–1 s, 1–2 s, sau 2 s; mỗi đoạn tới `cont_margin` · ngưỡng của đoạn đó (SRS 1.22) | `cmake: {PP_T4_BLEND: segments}` | V4 của PP-TS-019. Đoạn gần có λ riêng, không bị phần xa chặn |
| V4 | V2 và V3 | `calibration: {stitch_reset: 0.0}`, `cmake: {PP_T4_BLEND: segments}` | |
| V5 | `stitch_reset` 0,025 m | `calibration: {stitch_reset: 0.025}` | Thêm 2026-11-16 sau lần chạy 20261116-1702. Ngoài dải quét |
| V6 | `stitch_reset` 0,05 m | `calibration: {stitch_reset: 0.05}` | Như V5. Bằng ngưỡng 0–1 s của PP-SWR-100. Ngoài dải quét |
| V7 | Reset mềm: điểm đầu = path cũ + w · (trạng thái đo − path cũ), w = 0 dưới `stitch_soft_min` = 0,02 m, 1 từ `stitch_reset` = 0,1 m, tuyến tính ở giữa | `calibration: {stitch_soft_min: 0.02, stitch_reset: 0.1}`, `cmake: {PP_T4_START: soft}` | Thêm 2026-11-16 sau chẩn đoán V6. Trộn cả d, ḋ, d̈, góc lệch. `stitch_soft_min` là calibration parameter mới (Software Detailed Design 15) |
| V8 | Như V7, w tuyến tính từ 0 m | `calibration: {stitch_soft_min: 0.0, stitch_reset: 0.1}`, `cmake: {PP_T4_START: soft}` | Như V7 |
| Không xét | Bắt đầu từ trạng thái đo khi path chạm trần a_y | — | Dựa vào cờ `lateral_limit_reached`; cờ bật cả ở S1c (PP-TS-020 V2) |
| Không xét | Bỏ bước 4 ở chu kỳ reset | — | Bước nhảy tới `stitch_reset` trong một chu kỳ, trượt PP-SWR-100 ở 0–1 s khi `stitch_reset` > 0,05 m |

- V1, V2 chỉ đổi calibration. V3, V4 cần code T4 mới, chọn lúc build; bản giao không có nhánh chọn lúc chạy.
- Tham khảo: Apollo lập lại path từ trạng thái xe khi lệch ngang > 0,5 m (`trajectory_stitcher.cc`, PP-TS-019 mục 4). Autoware giữ đoạn gần xe trùng lần trước.

## 3. Cách đánh giá (khóa trong plan.yaml)

Khóa 2026-11-16: [plan.yaml](plan.yaml), suite [PP-TS-021](../../../benchmark/suites/PP-TS-021.yaml). Mở lại và khóa lại cùng ngày sau lần chạy 20261116-1702: thêm V5, V6; suite, seed và tiêu chí không đổi; mọi phương án chạy lại. Mở lại và khóa lại lần nữa sau lần chạy 20261116-1724 và chẩn đoán V6: thêm V7, V8 (reset mềm); mọi phương án chạy lại.

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | Requirement của SRS trong phạm vi của suite, gồm PP-SWR-100 đến 102 theo ba đoạn; a_y đo trên xe trong giới hạn R79 5.6.2.1.1 (`PP-TS-020/R79-5.6.2.1.1`) |
| Xếp hạng | SQTS mục 9; thêm a_y xe trừ a_y path ở S1b |
| Bộ chỉnh, bộ kiểm | Suite PP-TS-021: bộ chỉnh seed 1, 2; bộ kiểm seed 3, 4 |
| Ngân sách chỉnh | Không có; mọi phương án ở calibration khởi đầu, trừ tham số phương án đổi |
| Coi như ngang nhau khi | PP-SWR-051 chênh < 0,01 m; PP-SWR-050 chênh < 0,005 m |

Ca: bài R79 Annex 8, 3.2.2 (S1b a, b, c, ACC bỏ qua LateralLimits), cùng các ca nhạy với liên tục của path: cua chạm aysmax có nhiễu (S1 c + F01 c, S12 a), c0 jump (F02 b), độ cong sai (F06 e), đưa về giữa (S2), cua chữ S (S14 e).

Người dùng duyệt 2026-11-16:

| # | Điểm | Đã chốt | Cài đặt (2026-11-16) |
|---|---|---|---|
| 1 | Phần T4 của PP-TS-019 (V3 hay V4) chính là V0 và V3 ở đây | Gộp: phần T4 chuyển sang PP-TS-021, không chạy riêng | Ghi ở PP-TS-019 mục 8 |
| 2 | V2, V4 đặt `stitch_reset` ngoài dải quét của Software Architectural Design 11 | Cho phép trong study; nếu chọn thì sửa dải quét kèm lý do | — |
| 3 | `ay_margin_hwa` của PP-TS-020 | Giữ 0 ở mọi phương án. PP-TS-020 chạy lại sau khi PP-TS-021 quyết định | Giá trị khởi đầu là 0 |
| 4 | Thước đo xếp hạng a_y xe trừ a_y path | Target của bên chấm, chỉ dùng trong suite này | `PP-TS-021/ay-vehicle-over-path` ở `eval/proposed.py`: trung bình 2 s lớn nhất của (trị tuyệt đối a_y xe − trị tuyệt đối a_y path tại 0 s) khi HWA lái. Có trong `results.json`, không có trong bảng tóm tắt |

Cài V3 (`PP_T4_BLEND=segments`, `pp_stitch_blend`):

- λ_j của từng đoạn từ chênh lệch lớn nhất trong đoạn j và `cont_margin` · ngưỡng của đoạn đó. Điểm ở đúng 1 s, 2 s thuộc đoạn trước, như bên chấm.
- λ(t) tuyến tính qua λ₀, min(λ₀, λ₁), min(λ₁, λ₂), λ₂ tại 0, 1, 2, 3 s: mọi điểm có λ ≤ λ của đoạn mình, và λ không nhảy bậc giữa hai đoạn. Đổi lại, đoạn 1–2 s bị đoạn sau 2 s kéo xuống ở gần mốc 2 s.
- Khi λ đổi theo t, vị trí và hướng, độ cong của path không còn khớp chính xác. T10 kiểm lại path sau khi trộn (cắt jerk và a_y, tích phân lại). Bản `single` (V0 đến V2) giữ nguyên code cũ.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| [20261116-1702-study-PP-TS-021-f51044d](../../runs/20261116-1702-study-PP-TS-021-f51044d/summary.md) | V0 đến V4 | Theo plan khóa 2026-11-16. Chạy trong git worktree sạch ở f51044d, vì `web/` có thay đổi ngoài study; bản ghi chép về thư mục chính |
| [20261116-1724-study-PP-TS-021-0a1d8c9](../../runs/20261116-1724-study-PP-TS-021-0a1d8c9/summary.md) | V0 đến V6 | Khóa lại: thêm V5, V6. Cùng cách chạy trong worktree. V0 đến V4 cho đúng số của lần trước |
| [20261116-1748-study-PP-TS-021-8726b80](../../runs/20261116-1748-study-PP-TS-021-8726b80/summary.md) | V0 đến V8 | Khóa lại: thêm V7, V8 (reset mềm). Cùng cách chạy trong worktree. V0 đến V6 cho đúng số của lần trước |

## 5. Kết quả

Số lượt trượt (chỉnh / kiểm): V0 4 / 5; V1 6 / 6; V2 4 / 2; V3 4 / 6; V4 4 / 4.

| Ca (2 seed mỗi ô) | V0 | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|
| S1b a, ACC bỏ qua LateralLimits | R79 | R79, 100 | Đạt | R79 | Đạt |
| S1b b, ACC bỏ qua LateralLimits | R79 | R79 | R79 | R79 | R79 |
| S1b c, ACC bỏ qua LateralLimits | Đạt | Đạt | Đạt | Đạt | Đạt |
| S2 b (đưa về giữa từ 0,4 m) | Đạt | Đạt | 100 | Đạt | 100 |
| S14 e, ACC đọc LateralLimits | 051 (1 seed) | 051 (1 seed) | Đạt | 051, 100 | Đạt |
| S1c + F06 e | Đạt | Đạt | Đạt | Đạt | 051 |
| Mọi ca còn lại | Đạt | Đạt | Đạt | Đạt | Đạt |

a_y xe trừ a_y path, trung bình 2 s lớn nhất [m/s²] (`PP-TS-021/ay-vehicle-over-path`):

| Ca | V0 | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|
| S1b a | 0,50 | 0,40 | 0,16 | 0,50 | 0,16 |
| S1b b | 1,02 | 1,11 | 1,13 | 1,16 | 1,41 |
| S1b c | 0,52 | 0,40 | 0,11 | 0,54 | 0,11 |
| S1b e (ACC đọc LateralLimits) | 0,14 | 0,11 | 0,03 | 0,14 | 0,03 |

Lệch ngang của path so với tâm làn thật (PP-SWR-050), lớn nhất theo seed, các ca khác nhau hơn 0,05 m:

| Ca | V0 | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|
| S1 c | 0,33 | 0,33 | 0,15 | 0,33 | 0,15 |
| S1 c + F01 b | 0,37 | 0,37 | 0,15 | 0,39 | 0,15 |
| S1 c + F01 c | 0,50 | 0,48 | 0,28 | 0,53 | 0,30 |
| S1 c + F01 c, VP-5 | 0,45 | 0,44 | 0,31 | 0,49 | 0,29 |
| S1 c + F02 b | 0,33 | 0,33 | 0,15 | 0,33 | 0,15 |
| S12 a | 0,50 | 0,48 | 0,30 | 0,53 | 0,31 |
| S1 f (cua chữ S, R171) | 0,28 | 0,26 | 0,82 | 0,26 | 0,83 |
| S1 g | 0,05 | 0,05 | 0,12 | 0,05 | 0,12 |

- Bắt đầu từ trạng thái đo (V2) gỡ phần xe đuổi path ở S1b a, c, e: a_y xe trừ path còn 0,03–0,16 m/s². S1b a đạt R79.
- V2 cũng giảm lệch tâm làn ở cả họ S1c (cua chạm aysmax) khoảng 0,2 m. Đây là cùng hiện tượng trôi mà PP-TS-020 nhắm tới bằng `ay_margin_hwa`.
- Giá phải trả của V2: trạng thái đo lấy từ lane model nên mang theo sai số của nó. S1 f (cua chữ S, sai số khớp đa thức, PP-PR-004) lệch 0,82 m; S2 b trượt PP-SWR-100 khi đưa về giữa.
- S1b b trượt R79 ở mọi phương án; a_y xe vượt path 1,0–1,4 m/s² kể cả khi path bắt đầu từ xe. Cơ chế khác với S1b a, c; còn mở trong PP-PR-056.
- Trộn theo đoạn (V3, V4) không giúp ở ca nào; V3 thêm trượt ở S14 e, V4 thêm trượt ở F06 e. Loại V3, V4.
- V1 (0,1 m) không đủ: vẫn trượt R79 ở S1b a và thêm trượt PP-SWR-100.

**Lần chạy sau khi khóa lại** [20261116-1724-study-PP-TS-021-0a1d8c9](../../runs/20261116-1724-study-PP-TS-021-0a1d8c9/summary.md). Số lượt trượt (chỉnh / kiểm): V0 4 / 5; V1 6 / 6; V2 4 / 2; V3 4 / 6; V4 4 / 4; V5 3 / 3; V6 4 / 4.

| Ca (2 seed mỗi ô) | V0 (0,2 m) | V2 (0) | V5 (0,025 m) | V6 (0,05 m) |
|---|---|---|---|---|
| S1b a, bài R79 | R79 | Đạt | 100 | 100 |
| S1b b, bài R79 | R79 | R79 | R79 | R79 |
| S2 b | Đạt | 100 | Đạt | Đạt |
| S14 e | 051 (1 seed) | Đạt | Đạt | Đạt |
| Mọi ca còn lại | Đạt | Đạt | Đạt | Đạt |

| Đại lượng | V0 | V2 | V5 | V6 |
|---|---|---|---|---|
| a_y xe trừ path, S1b a / c [m/s²] | 0,50 / 0,52 | 0,16 / 0,11 | 0,23 / 0,21 | 0,29 / 0,29 |
| PP-SWR-050, S1 c [m] | 0,33 | 0,15 | 0,07 | 0,05 |
| PP-SWR-050, S1 c + F02 b [m] | 0,33 | 0,15 | 0,07 | 0,05 |
| PP-SWR-050, S12 a [m] | 0,50 | 0,30 | 0,34 | 0,33 |
| PP-SWR-050, S1 f (cua chữ S) [m] | 0,28 | 0,82 | 0,46 | 0,36 |
| PP-SWR-050, xấu nhất ở bộ kiểm [m] | 0,45 | 0,82 | 0,46 | 0,36 |

- V5, V6 giữ được phần lớn lợi ích của V2: S1b a đạt R79, S1c gần tâm làn hơn cả V2, S1 f xấu ít hơn nhiều, S2 b đạt.
- V5, V6 trượt PP-SWR-100 ở S1b a, ở mọi seed. V2 không trượt ở ca này. Giả thuyết: khi `stitch_reset` nhỏ nhưng khác 0, điểm đầu đổi qua lại giữa path cũ và trạng thái đo, và lần T10 kiểm lại sau T4 cắt path ở trần a_y (cua cần vượt aysmax), phá giới hạn trộn (cơ chế của PP-PR-005, 006). Chưa kiểm; `results.json` không ghi giá trị của PP-SWR-100.
- V6 có lệch tâm làn xấu nhất nhỏ nhất ở bộ kiểm (0,36 m so với 0,45 m của V0).
- S1b b trượt R79 ở mọi phương án.

**Chẩn đoán V6 ở S1b a** (2026-11-16, nháp: thư viện build lại bằng `eval.sweep` từ 0a1d8c9 với calibration của từng phương án; seed 1, 3; ACC bỏ qua LateralLimits). Lệch giữa hai path liên tiếp tính theo từng điểm, như `eval.metrics._continuity`, chia cho ngưỡng của đoạn.

| Bản | Chu kỳ lệch > 80 % ngưỡng | Đổi dấu giữa hai chu kỳ liền nhau | Khoảng | PP-SWR-100 lớn nhất |
|---|---|---|---|---|
| V0 (0,2 m) | 7 | 0 | 16,1–16,9 s | 0,95–0,99 (đạt) |
| V6 (0,05 m) | 19–20 | 12 | 6,6–17,0 s | 1,02 (trượt) |
| V2 (0) | 0 | — | — | 0,38 (đạt) |

- Giả thuyết về T10 (mục trên) sai: quanh chu kỳ trượt, a_y của path đứng ở 2,50 m/s², độ cong path không đổi giữa hai chu kỳ.
- Nguyên nhân: điểm đầu path đứng ở 0,038–0,047 m so với xe, sát dưới `stitch_reset`. T4 bước 2 đổi qua lại giữa nối từ path cũ và bắt đầu từ trạng thái đo. Lệch tại điểm 1 s đổi dấu mỗi chu kỳ (+0,047, −0,043, +0,051, −0,043 m): path dao động 40 Hz ở đúng giới hạn trộn `cont_margin` · 0,05 = 0,045 m.
- Lần vượt 0,05 m: T4 đo lệch trên path cũ dời bằng ego-motion của planner, bên chấm dời bằng chuyển động thật. Khác vài mm, lớn hơn phần biên 10 % của `cont_margin`. V0 cũng tới 0,99 ở cuối S1b a.
- Ngưỡng reset nhị phân càng nhỏ thì càng dễ dao động quanh ngưỡng. Chọn giá trị khác cho `stitch_reset` không gỡ được cơ chế này.

**Lần chạy với reset mềm** [20261116-1748-study-PP-TS-021-8726b80](../../runs/20261116-1748-study-PP-TS-021-8726b80/summary.md). Số lượt trượt (chỉnh / kiểm): V0 4 / 5; V1 6 / 6; V2 4 / 2; V3 4 / 6; V4 4 / 4; V5 3 / 3; V6 4 / 4; **V7 2 / 2; V8 2 / 2**. Đứng đầu ở bộ kiểm: V7.

| Ca (2 seed mỗi ô) | V0 | V2 | V6 | V7 | V8 |
|---|---|---|---|---|---|
| S1b a, bài R79 | R79 | Đạt | 100 | Đạt | Đạt |
| S1b b, bài R79 | R79 | R79 | R79 | R79 | R79 |
| S2 b | Đạt | 100 | Đạt | Đạt | Đạt |
| S14 e | 051 (1 seed) | Đạt | Đạt | Đạt | Đạt |
| Mọi ca còn lại | Đạt | Đạt | Đạt | Đạt | Đạt |

| Đại lượng | V0 | V2 | V6 | V7 | V8 |
|---|---|---|---|---|---|
| a_y xe trừ path, S1b a / c [m/s²] | 0,50 / 0,52 | 0,16 / 0,11 | 0,29 / 0,29 | 0,36 / 0,33 | 0,34 / 0,29 |
| PP-SWR-050, S1 c [m] | 0,33 | 0,15 | 0,05 | 0,04 | 0,08 |
| PP-SWR-050, S12 a [m] | 0,50 | 0,30 | 0,33 | 0,34 | 0,30 |
| PP-SWR-050, S1 f (cua chữ S) [m] | 0,28 | 0,82 | 0,36 | 0,39 | 0,49 |
| PP-SWR-050, xấu nhất bộ chỉnh / kiểm [m] | 0,50 / 0,45 | 0,30 / 0,82 | 0,38 / 0,36 | 0,34 / 0,39 | 0,30 / 0,49 |
| PP-SWR-053, bộ chỉnh [s] | 3,29 | 0,78 | 0,88 | 0,83 | 0,80 |

- V7, V8 chỉ trượt S1b b, ca trượt ở mọi phương án. Reset mềm gỡ dao động của V5, V6 ở S1b a và giữ được S2 b.
- V7 tốt hơn V8 ở ca xấu nhất bộ kiểm (S1 f: 0,39 so với 0,49 m). V8 tốt hơn ở vài ca mưa, nhiễu (S12 a, S1 c + F01 c), kém hơn ở S1 c, F02 b.
- So với V0: lệch tâm làn ở họ S1c giảm từ 0,33–0,50 xuống 0,04–0,34 m; S1 f xấu hơn 0,11 m (sai số khớp đa thức của lane model, PP-PR-004, PP-TS-005).
- a_y xe trừ path ở S1b a, c còn 0,33–0,36 m/s², cao hơn V2 (0,11–0,16) nhưng R79 đạt.

## 6. Đề xuất

2026-11-16, sau lần chạy 20261116-1748, chờ người dùng quyết định (bước 7):

- Chọn V7: reset mềm, `stitch_soft_min` 0,02 m, `stitch_reset` 0,1 m, trộn một λ như cũ.
- Lý do: cùng số trượt ít nhất với V8 (chỉ S1b b, chung cho mọi phương án); lệch tâm làn xấu nhất ở bộ kiểm nhỏ hơn V8; gỡ R79 ở S1b a, dao động của V5, V6, và S2 b của V2.
- Khi đưa vào (bước 8): Software Detailed Design mục 7 (T4 bước 2 reset mềm) và mục 15 (`stitch_soft_min`); Software Architectural Design mục 11 (`stitch_reset` khởi đầu 0,1 m); calibration; bỏ `PP_T4_BLEND`, `PP_T4_START=hard` khỏi code giao; đóng phần T4 của PP-TS-019; hồi quy.
- Sau đó: chạy lại PP-TS-020 trên baseline mới; mở problem report cho S1b b.

Đề xuất trước đó (2026-11-16, sau chẩn đoán V6):

- Loại V5, V6: dao động theo chu kỳ ở S1b a. V2 không dao động nhưng mang sai số lane model vào path (S1 f, S2 b).
- Phương án mới, cần mở lại khóa và cài code: reset mềm. Điểm đầu = trạng thái path cũ + w · (trạng thái đo − trạng thái path cũ), w tăng liên tục từ 0 tới 1 theo độ lệch giữa hai trạng thái (ví dụ 0 dưới 0,02 m, 1 từ 0,1 m). Không có ngưỡng nhị phân nên không dao động; V0 và V2 là hai đầu của cách này.
- Cần chốt cùng lúc: biên của `cont_margin` so với sai số ego-motion (V0 cũng tới 0,99).
- S1b b: problem report riêng.
- 2026-11-16: người dùng đồng ý thêm reset mềm. Cài: `PP_T4_START=soft` (mặc định `hard`, code cũ giữ nguyên), `pp_stitch_soft_weight`; khi `stitch_reset` ≤ `stitch_soft_min` thì quay về reset nhị phân, nên V2 chạy được trên cả hai bản. Unit test C đạt 15/15 ở cả bốn tổ hợp hard, soft × single, segments.

Đề xuất trước đó (2026-11-16, sau lần chạy 20261116-1724):

- Chưa chọn. Không phương án nào đạt hết. V6 gần nhất: chỉ còn PP-SWR-100 ở S1b a, ngoài S1b b chung cho mọi phương án.
- Bước tiếp: chẩn đoán S1b a với V6 (một lượt mô phỏng): chu kỳ trượt PP-SWR-100, điểm đầu lấy từ path cũ hay trạng thái đo, và T10 có cắt lại sau T4 không. Nếu đúng giả thuyết thì sửa T10 hoặc T4 ở cơ chế chung, rồi chạy lại.
- S1b b: problem report riêng.

Đề xuất trước đó (2026-11-16, sau lần chạy 20261116-1702):

- Chưa chọn. V2 đi đúng hướng nhưng trượt PP-SWR-100 ở S2 b và làm S1 f xấu đi nhiều.
- Loại V1, V3, V4. Phần T4 của PP-TS-019 kết thúc: trộn một λ (V0 của PP-TS-019, tức V3 ở đó) giữ nguyên.
- Phương án mới cần thêm (mở lại khóa, chạy lại): `stitch_reset` giữa 0 và 0,1 m (ví dụ 0,025 và 0,05 m, quanh ngưỡng 0,05 m của PP-SWR-100 ở đoạn 0–1 s), để giữ lọc nhiễu của path cũ mà vẫn không để xe đứng xa path.
- S1b b: mở problem report riêng hoặc tiếp tục ở PP-PR-056.
- PP-TS-020 chạy lại sau khi chọn, vì S1c có thể không còn cần `ay_margin_hwa`.
- 2026-11-16: người dùng đồng ý thêm V5, V6 và chạy lại.

## 7. Quyết định

- Người quyết, ngày: thongbui, 2026-11-16.
- Chọn: V7. Reset mềm ở T4 bước 2: điểm đầu = path cũ + w · (trạng thái đo − path cũ), w từ 0 ở `stitch_soft_min` = 0,02 m tới 1 ở `stitch_reset` = 0,1 m. T4 bước 4 giữ một λ cho cả path.
- Lý do: theo đề xuất ở mục 6, lần chạy 20261116-1748-study-PP-TS-021-8726b80.
- Đưa vào: Software Detailed Design mục 7, 15; Software Architectural Design mục 4.2, 11; PP-ADR-004; calibration; code giao bỏ `PP_T4_BLEND`, `PP_T4_START`. Phần T4 của PP-TS-019 đóng theo quyết định này.
- Hồi quy: chờ.
