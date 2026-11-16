# PP-TS-021 Điểm đầu path HWA khi xe rời path cũ (T4)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã khóa |
| Mở ngày | 2026-11-16 |
| Khóa ngày | 2026-11-16 |
| Quyết định ngày | — |
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
| Không xét | Bắt đầu từ trạng thái đo khi path chạm trần a_y | — | Dựa vào cờ `lateral_limit_reached`; cờ bật cả ở S1c (PP-TS-020 V2) |
| Không xét | Bỏ bước 4 ở chu kỳ reset | — | Bước nhảy tới `stitch_reset` trong một chu kỳ, trượt PP-SWR-100 ở 0–1 s khi `stitch_reset` > 0,05 m |

- V1, V2 chỉ đổi calibration. V3, V4 cần code T4 mới, chọn lúc build; bản giao không có nhánh chọn lúc chạy.
- Tham khảo: Apollo lập lại path từ trạng thái xe khi lệch ngang > 0,5 m (`trajectory_stitcher.cc`, PP-TS-019 mục 4). Autoware giữ đoạn gần xe trùng lần trước.

## 3. Cách đánh giá (khóa trong plan.yaml)

Khóa 2026-11-16: [plan.yaml](plan.yaml), suite [PP-TS-021](../../../benchmark/suites/PP-TS-021.yaml).

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

## 5. Kết quả

## 6. Đề xuất

## 7. Quyết định

- Người quyết, ngày:
- Chọn:
- Lý do:
- Đưa vào: Software Detailed Design mục 7 (T4), Software Architectural Design mục 11 (`stitch_reset`), calibration
- Hồi quy: run ID
