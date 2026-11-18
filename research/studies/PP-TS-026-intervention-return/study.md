# PP-TS-026 Đường về tâm làn của LKA và ELK

| Mục | Nội dung |
|---|---|
| Trạng thái | Chờ quyết định; V4 đang được áp dụng để chạy hồi quy |
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

- [20261118-1712-study-PP-TS-026-3875f8e](../../runs/20261118-1712-study-PP-TS-026-3875f8e/summary.md)

## 5. Kết quả

| Phương án | Lần trượt, bộ chỉnh | Lần trượt, bộ kiểm | Trượt còn lại ở bộ kiểm | 081 xấu nhất, bộ kiểm [s] | 082 xấu nhất, bộ kiểm [s] | 087 xấu nhất, bộ kiểm [m] |
|---|---|---|---|---|---|---|
| V0 | 18 | 34 | PP-SWR-094, 090, 032 | 3,60 | 4,30 | 0,183 |
| V1 | 14 | 32 | PP-SWR-094 | 4,23 | 4,80 | 0,118 |
| V2 | 5 | 10 | PP-SWR-094, 090 | 4,85 | 5,55 | 0,144 |
| V3 | 4 | 6 | PP-SWR-090 | 5,48 | 6,25 | 0,075 |
| V4 | 4 | 6 | PP-SWR-090 | 5,20 | 5,93 | 0,174 |

- Hai pha với về tâm 4 s bỏ hết PP-SWR-094 trên bộ kiểm. Một quintic dài hơn (V1) không đủ.
- V3 và V4 cùng số lần trượt. V4 tới COMPLETED sớm hơn và giữ DTLE tốt hơn.
- Giá phải trả: thời gian tới COMPLETED dài thêm 1–2 s so với V0.

## 6. Đề xuất

- Chọn V4: `T_lka` 1,25 s, `T_elk` 0,75 s, `T_return` 4 s.
- Bổ sung ngoài các phương án đã khóa: lượt nháp S8b c cho thấy về tâm chậm làm khoảng cách tới xe làn bên còn 0,27 m (PP-SWR-088), nên ELK vì xe làn bên dùng `T_return_object` = 2 s. Phần này được kiểm ở lần hồi quy, không thuộc so sánh của study.

## 7. Quyết định

- Chờ người phụ trách xác nhận. V4 đã đưa vào calibration để chạy hồi quy.
