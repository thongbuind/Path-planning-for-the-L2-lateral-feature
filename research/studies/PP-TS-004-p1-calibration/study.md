# PP-TS-004 Calibration của T2, T5 và cờ giới hạn (sweep P1)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, cần chạy lại |
| Mở ngày | 2026-11-11 |
| Khóa ngày | 2026-11-11 (`benchmark/suites/P1.yaml`) |
| Quyết định ngày | — |
| Liên quan | SQTS mục 7 (P1); Software Architectural Design mục 11 |

## 1. Câu hỏi

- Quyết định cần đưa ra: giá trị khởi đầu của `k_jump`, `T_confirm`, `T_coast`, `q_kappa`, `sigma_kappa_min`, `T_flag`, `delta_ay`.

## 2. Phương án

Mỗi giá trị trong dải quét của `P1.yaml`, từng tham số một; rồi gộp các giá trị tốt nhất.

## 3. Cách đánh giá

Khóa trong `benchmark/suites/P1.yaml`: chọn trên bộ chỉnh (seed 1, 2), chấm trên bộ kiểm (seed 3, 4); xếp hạng theo SQTS mục 9.

## 4. Lần chạy

| Run ID | Ghi chú |
|---|---|
| Không có | Lần chạy ngày 2026-11-11 lúc 01:26 ở `build/sweep/P1` là nháp: trước khi có commit và manifest |

## 5. Kết quả

- Lần chạy nháp chọn `k_jump` = 2, `T_flag` = 0,3 s. Hai lần trượt của bộ khởi đầu đều là PP-SWR-007 ở S1b e, theo cách chấm cũ.
- Sau đó PP-SWR-007 viết lại theo R79 (SRS 1.3) và `T_flag`, `delta_ay` không còn là giới hạn của requirement. Kết quả trên vì vậy đã cũ; calibration giữ giá trị khởi đầu.

## 6. Đề xuất

Chạy lại P1 chính thức trên `bl1-sil` hoặc commit sau đó.

## 7. Quyết định
