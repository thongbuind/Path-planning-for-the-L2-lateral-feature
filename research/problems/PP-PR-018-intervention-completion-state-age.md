# PP-PR-018 Pha COMPLETED dùng v_y ở mốc trước t0

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã cài PP-TS-012 V1; chưa đạt: PP-SWR-032, 090 còn trượt (PP-PR-020) |
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

Lần chạy chính thức [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): PP-SWR-032 trượt 50 lần trong phạm vi (F01, G01, S12, F06, S13), PP-SWR-090 trượt 4 lần trong phạm vi và 35 lần ngoài phạm vi. Xem PP-PR-020.
