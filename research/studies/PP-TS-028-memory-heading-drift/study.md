# PP-TS-028 Bộ nhớ của planner trôi theo bias yaw của EgoMotionQuery

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-23 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-PR-049; PP-SWR-051, 100 đến 102, 120, 136; PP-ADR-007; PP-TS-005; Software Detailed Design T3, T4, T5 |

## 1. Câu hỏi

- Quyết định cần đưa ra: planner giữ bộ nhớ giữa các chu kỳ thế nào để bias yaw trong EgoMotionQuery không làm reference line trôi khỏi làn, mà vẫn chống được nhiễu của lane model.
- Vì sao cần: PP-PR-049. T3 dời r(s) bằng ego-motion rồi chỉ cho r(s) tiến về camera tối đa `ref_rate`·Δt. Bias b làm sai số tại s tăng với tốc độ s·b; vượt `ref_rate` thì không kéo lại được. F08 b, c trên S1c VP-5 trượt PP-SWR-051 vì lý do này.

## 2. Phương án

| ID | Phương án | Ghi chú |
|---|---|---|
| V0 | Bản hiện tại | Mốc |
| V1 | T3 tách chênh lệch giữa camera và bộ nhớ thành phần quay quanh xe (a + b·s) và phần còn lại. Phần quay tiến về camera với hằng số thời gian `tau_rot`, không bị chặn bởi `ref_rate`; phần còn lại giữ giới hạn `ref_rate` | Ít thay đổi; chỉ sửa T3 |
| V2 | Ước lượng bias yaw của ego-motion từ độ quay kéo dài giữa camera và bộ nhớ; trừ bias khỏi phép quay khi dời mọi bộ nhớ (T3, T4, T5, hành lang can thiệp) | Sửa gốc cho mọi bộ nhớ; thêm một trạng thái nhỏ |
| V3 | Road estimator của PP-TS-005 V3 với thêm trạng thái bias yaw | Gộp với PP-TS-005; lớn nhất |

## 3. Cách đánh giá

Chưa khóa. Đề xuất: tiêu chí loại là PP-SWR-051, 100 đến 102, 120, 136; bộ chỉnh F08 a, b trên S1 a và S1 c, seed 1, 2; bộ kiểm F08 a, b, c trên S1 c, S1 d, S14 e, cùng S1, S12 không lỗi để kiểm chống nhiễu (PP-SWR-120), seed 3, 4; mọi profile.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

## 6. Đề xuất

## 7. Quyết định
