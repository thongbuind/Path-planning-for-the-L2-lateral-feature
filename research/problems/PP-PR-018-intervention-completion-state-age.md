# PP-PR-018 Pha COMPLETED dùng v_y ở mốc trước t0

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã cài PP-TS-012 V1, chờ xác nhận chính thức |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | PP-SWR-032, 090 |
| Tái hiện | S4(c), seed 1. So VehicleStateEstimate với ground truth ở đầu cửa sổ T_end_hold |

## 1. Hiện tượng

S4(c) báo COMPLETED sớm một tick so với cửa sổ đủ điều kiện trên ground truth.

## 2. Nguyên nhân

T9 dùng v_y của VehicleStateEstimate tại thời điểm đo. Trong S4(c), v_y đã tăng từ lúc đo đến t0, đủ để v_lat tại cầu trước còn ở trên ngưỡng.

## 3. Cách sửa

PP-TS-012 V1 đưa v_y về t0 trước khi kiểm điều kiện kết thúc. Chỉ sử dụng mẫu qua kiểm tra input. Không đổi dung sai, T_end_hold hay dữ liệu đánh giá.

## 4. Xác nhận

Unit test bù thời gian, giữ đạo hàm khi nhận lại cùng mẫu và xóa bộ nhớ khi mất input. Chạy lại smoke để kiểm PP-SWR-032 và 090.
