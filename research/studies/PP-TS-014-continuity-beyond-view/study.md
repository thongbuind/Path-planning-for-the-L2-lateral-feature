# PP-TS-014 Liên tục của path khi phần xa nằm ngoài tầm nhìn

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng |
| Mở ngày | 2026-11-12 |
| Khóa ngày | 2026-11-12 |
| Quyết định ngày | 2026-11-12 |
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
| [20261112-1150-study-PP-TS-014-fe420b5](../../runs/20261112-1150-study-PP-TS-014-fe420b5/summary.md) | V0, V1 × `cont_margin` 0,7 / 0,8 / 0,9 | Chính thức |

## 5. Kết quả

Lần chạy 20261112-1150-study-PP-TS-014-fe420b5. Trượt đếm theo (ca, requirement).

| Bộ | Bộ chỉnh: trượt | Bộ chỉnh: PP-SWR-050 [m] | Bộ kiểm: trượt | Bộ kiểm: PP-SWR-050 [m] | Bộ kiểm: jerk [m/s³] |
|---|---|---|---|---|---|
| V0-m9 | 2 | 2,15 | 21 | 1,36 | 2,60 |
| V0-m8 | 4 | 2,88 | 18 | 1,88 | 2,60 |
| V0-m7 | 5 | 4,04 | 14 | 2,72 | 2,59 |
| V1-m9 | 9 | 0,41 | 34 | 0,40 | 3,71 |
| V1-m8 | 9 | 0,41 | 34 | 0,40 | 3,80 |
| V1-m7 | 14 | 2,08 | 31 | 0,40 | 3,89 |

- Chọn mức trên bộ chỉnh: V0-m9, V1-m9 (hoặc m8, ngang nhau).
- V1 giảm PP-SWR-050 khoảng 3 lần và hết trượt PP-SWR-051 ở S1c, S1f với tầm nhìn 30–40 m. Đổi lại V1 trượt PP-SWR-100 (và 101, 102 ở S14e) ở nhiều ca hơn V0.
- Hạ `cont_margin` không làm hết trượt PP-SWR-100 của V1.
- Cả hai cùng trượt S14e (PP-PR-004) và F06 trên S1c (PP-PR-001).

**Vì sao V1 trượt PP-SWR-100.** Tái hiện S1c 30 m, seed 1, thư viện V1-m7 của lần chạy này: 21 trong 873 cặp path vượt 0,05 m, lớn nhất 1,15 m ở 2,9 s lúc 10,558 s. V1 trộn vị trí, hướng và độ cong của từng điểm với λ khác nhau, nên trường độ cong không còn khớp với hình học của path. T10 bước 2 (`pp_feasibility_limit`) cắt độ cong theo jerk, tốc độ quay vô lăng rồi tích phân lại vị trí từ điểm đầu tiên bị cắt, nên phần xa bị đẩy đi. Đây là lỗi của cách cài V1, không phải của ý tưởng λ theo từng điểm.


## 6. Đề xuất

- Chưa chọn được: V0 đạt nhiều requirement hơn nhưng vẫn để xe rời làn khi tầm nhìn ngắn (PP-PR-021); V1 như đã cài có lỗi hình học ở mục 5.
- Sửa V1 thành V1b: sau khi trộn theo từng điểm, tính lại hướng và độ cong từ vị trí đã trộn, và giới hạn độ đổi của λ giữa hai điểm liền nhau để không sinh thêm jerk. Chạy lại V0-m9 và V1b với cùng bộ chạy, seed, tiêu chí.


## 7. Quyết định

- Người quyết, ngày: thongbui, 2026-11-12.
- Chọn: không chọn V1, V2. Đổi requirement: PP-SWR-100 đến 102 chỉ xét phần path trong tầm nhìn lane model báo. T4 giữ một λ, tính trên phần đó. Trajectory báo `observed_horizon_s`.
- Lý do: phần ngoài tầm nhìn là ngoại suy; giữ nó liên tục làm path không theo được làn khi tầm nhìn ngắn. V1 sửa lại theo hình học (tính lại hướng, độ cong từ vị trí đã trộn) cho path chữ S, jerk chạm 5 m/s³, xe rời làn cả ở 80 m (thử nháp, không ghi).
- Đưa vào: Software Requirements Specification 1.9 (định nghĩa Hai path liên tiếp, PP-SWR-018, PP-ASM-021); Interface Control Document 1.9; Software Detailed Design 1.8 (T4 bước 4, T11); Software Qualification Test Specification 1.19 (mục 8.1). Code V1, V2 đã gỡ ở commit 1bfd184.
- Hồi quy: [20261112-1239-matrix-Q4-1bfd184](../../runs/20261112-1239-matrix-Q4-1bfd184/summary.md): S1 và S14a đạt ở mọi mức tầm nhìn; còn S14e (PP-PR-004, PP-PR-007). [20261112-1240-matrix-M1-1bfd184](../../runs/20261112-1240-matrix-M1-1bfd184/summary.md): 12 trượt trong phạm vi, đều là PP-SWR-018 ở F02 (planner bám reference line cũ nên báo `observed_horizon_s` ngắn hơn tầm nhìn lane model báo). Sửa PP-SWR-018 thành chặn phía trên (SRS 1.10), chạy lại: [20261112-1254-matrix-M1-8418fd9](../../runs/20261112-1254-matrix-M1-8418fd9/summary.md), 0 trượt trong phạm vi; 38 trượt PP-SWR-051 ngoài phạm vi, bằng baseline 20261111-1024-matrix-M1-b9e5d4d
