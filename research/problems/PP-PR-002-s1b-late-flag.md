# PP-PR-002 Cờ giới hạn bật muộn ở S1b e

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-007 |
| Tái hiện | S1b e (clothoid 60 m), lần chạy nháp trước khi có manifest |

## 1. Hiện tượng

PP-SWR-007 cũ đòi cờ bật trong `T_flag` sau khi a_y cần vượt aysmax + `delta_ay`. Ở clothoid ngắn, a_y cần tăng nhanh hơn cờ kịp bật, nên trượt.

## 2. Nguyên nhân

Requirement đặt mốc thời gian không có nguồn. R79 chỉ đòi cảnh báo muộn nhất lúc lốp trước bắt đầu đè vạch (5.6.2.2.3; Annex 8, 3.2.5.2).

## 3. Cách sửa

Viết lại PP-SWR-007 theo R79 (SRS 1.3): cờ phải đang bật khi lốp trước bắt đầu đè vạch. Thời gian báo trước thành target PP-SWR-064.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261111-1024-matrix-M1-b9e5d4d | PP-SWR-007 đạt ở mọi lần chạy S1b; báo trước 2,0–2,6 s khi ACC bỏ qua LateralLimits |
