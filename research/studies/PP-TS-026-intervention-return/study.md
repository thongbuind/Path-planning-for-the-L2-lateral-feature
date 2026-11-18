# PP-TS-026 Đường về tâm làn của LKA và ELK

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã khóa |
| Mở ngày | 2026-11-18 |
| Khóa ngày | 2026-11-18 |
| Liên quan | PP-SWR-032, 084, 085, 086, 090, 091, 094, 110 đến 115; target 081, 082, 087; PP-PR-071, 072; Software Detailed Design mục 10 |

## 1. Câu hỏi

- Quyết định cần đưa ra: path LKA, ELK đưa xe từ lúc can thiệp về tâm làn theo dạng nào.
- Vì sao cần: từ khi đích là tâm làn (PP-ADR-017), một quintic ngắn đưa xe về nhanh, xe vượt qua tâm rồi quay lại. DLC phía can thiệp giảm lại quá 0,1 m, trượt PP-SWR-094 ở 124 lần trong `20261118-1546-suite-regression-edb02b8`.

## 2. Phương án

| ID | Mô tả |
|---|---|
| V0 | Một quintic về tâm, `T_lka` 3 s, `T_elk` 2 s |
| V1 | Một quintic dài hơn: 4 s, 3 s |
| V2 | Hai pha: chặn đà trôi trong `T_lka` hoặc `T_elk`, rồi về tâm trong `T_return` = 3 s |
| V3 | Như V2, `T_return` = 4 s |
| V4 | Như V3, chặn đà nhanh hơn: 1,25 s, 0,75 s |

Pha chặn đà kết thúc với tốc độ ngang, gia tốc và jerk bằng 0. Xe đang tự về phía tâm thì bỏ pha này và về thẳng trong `T_return`.

## 3. Cách đánh giá (khóa trong plan.yaml)

- Tiêu chí loại: mọi requirement trong phạm vi của suite `PP-TS-026`.
- Xếp hạng: Software Qualification Test Specification mục 9, target PP-SWR-081, 082, 087.
- Bộ chỉnh: seed 1, 2. Bộ kiểm: biến thể khác, seed 3, 4.

## 4. Lần chạy

## 5. Kết quả

## 6. Đề xuất

## 7. Quyết định
