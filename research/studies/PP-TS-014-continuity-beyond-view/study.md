# PP-TS-014 Liên tục của path khi phần xa nằm ngoài tầm nhìn

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã khóa |
| Mở ngày | 2026-11-12 |
| Khóa ngày | 2026-11-12 |
| Quyết định ngày | — |
| Liên quan | PP-SWR-050, 051, 100, 101, 102, 149; PP-ADR-004; PP-PR-021, PP-PR-022 |

## 1. Câu hỏi

- Quyết định cần đưa ra: T4 và T7 giữ liên tục với path cũ thế nào khi một phần path nằm ngoài tầm nhìn của lane model.
- Vì sao cần: PP-PR-021. Khi tầm nhìn ngắn hơn quãng xe đi trong 3 s, T4 bước 4 lấy một λ theo lệch lớn nhất trên cả path. Lệch lớn nhất nằm ở phần ngoại suy ngoài tầm nhìn, nên phần gần xe chỉ dời được 1–2 mm mỗi chu kỳ và xe rời làn trong cua. Software Detailed Design T7 C ghi chi phí liên tục trên mọi điểm; code chỉ áp trong tầm nhìn.
- Ràng buộc: PP-SWR-100 đến 102 (đề bài) giữ nguyên, đo trên cả đoạn hai path cùng mô tả.

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Bản hiện tại: T7 A (quintic); T4 một λ cho cả path; ngoài tầm nhìn là cung tròn của độ cong ở cuối tầm nhìn | `cmake: {PP_T4_BLEND: single, PP_T2_BEYOND: arc}` | Mốc so sánh |
| V1 | T4 một λ cho từng điểm, không tăng theo t; mỗi điểm vẫn trong `cont_margin` của ngưỡng PP-SWR-100 đến 102 | `cmake: {PP_T4_BLEND: per_time}` | Phần gần xe được dời khi chỉ phần xa lệch |
| V2 | Độ cong của cung ngoài tầm nhìn theo độ cong ở cuối tầm nhìn, đổi tối đa `kappa_far_rate` mỗi giây | `cmake: {PP_T2_BEYOND: rate_limited}`; `kappa_far_rate` 2,5e-4 / 5e-4 / 1e-3 1/m/s | Phần ngoại suy đổi chậm từ nguồn |
| V3 | V1 và V2 | Cả hai | Bỏ, xem dưới |

Thay đổi sau lần chạy không ghi được (2026-11-12, commit 0606b07): số nháp cho thấy V2, V3 không giảm lệch ngang so với V0, nên bỏ. V1 giảm lệch ngang nhưng trượt PP-SWR-100 sát ngưỡng: với λ riêng từng điểm, nhiều điểm cùng lên sát `cont_margin`·0,05 m, phần sai khác giữa ego-motion của planner và chuyển động thật đủ để vượt 0,05 m. `cont_margin` 0,9 được chọn cho một λ. Vì vậy ngân sách chỉnh đổi thành `cont_margin` 0,7 / 0,8 / 0,9 (dải quét của Software Architectural Design 11), cho cả V0 và V1 để công bằng. Bộ chạy, seed, tiêu chí giữ nguyên; chạy lại mọi phương án.

Thay đổi trước lần chạy đầu (2026-11-12): bản mở đầu có V1 là chi phí liên tục của QP (T7 C) trên mọi điểm. Thư viện giao và các lần chạy của PP-PR-021 dùng T7 A, nên V1 đó không áp lên bản hiện tại; bỏ. V3 cũ (reference line cũ đi tiếp) không làm được vì reference line cũ cũng chỉ dài tới hết tầm nhìn cũ; thay bằng V2 có giới hạn tốc độ đổi. Bộ chạy, seed, tiêu chí giữ nguyên.

## 3. Cách đánh giá (khóa trong plan.yaml)

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | Requirement của SRS trong `scope` của suite `PP-TS-014`: PP-SWR-001, 003, 051, 100, 101, 102, 116, 117; thêm 017, 149 với F22; thêm 009, 150, 151 với S14. Chỉ chấm loại ở mức tầm nhìn có thời gian nhìn trước ≥ `t_view_hwa` (ADAS Function Specification 7); mức thấp hơn chỉ báo cáo |
| Xếp hạng | Software Qualification Test Specification mục 9: DLC nhỏ nhất, PP-SWR-050, rồi PP-SWR-125, 002, 053, jerk |
| Bộ chỉnh | S1 c, f với tầm nhìn 30 m và 40 m; S14 a (ACC đọc LateralLimits) 40 m; F22 c trên S1 c. Seed 1, 2 |
| Bộ kiểm | S1 a, c, f, g với tầm nhìn 35 m, 60 m, 80 m; S1b d; S2 b; S14 a, e (hai chế độ ACC) 80 m và 126 m; F02 (a, e), F06 (b, e), F22 (a–f) trên S1 c. Seed 3, 4 |
| Ngân sách chỉnh | V0, V1: `cont_margin` 0,7 / 0,8 / 0,9; chọn mức trên bộ chỉnh, so sánh trên bộ kiểm |
| Coi như ngang nhau khi | DLC nhỏ nhất chênh < 0,01 m; PP-SWR-050 chênh < 0,005 m |

Thời gian nhìn trước ở 25 m/s: 30 m là 1,2 s, 35 m là 1,4 s, 40 m là 1,6 s; đều ≥ `t_view_hwa` = 1,0 s.

Mỗi dòng chạy có thể kết thúc bằng một mục giá trị simulator (tầm nhìn camera, chế độ ACC), đọc bởi `eval.sweep.load_run`.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| — | V0–V3 | 2026-11-12, commit 0606b07, `--record`: chạy hết nhưng không ghi được hồ sơ (ngày `locked` không ghi ra JSON). Không phải lần chạy chính thức; không trích |

## 5. Kết quả

## 6. Đề xuất

## 7. Quyết định

- Người quyết, ngày:
- Chọn:
- Lý do:
- Đưa vào: PP-ADR-…, Software Detailed Design mục 7, 8 …
- Hồi quy: run ID
