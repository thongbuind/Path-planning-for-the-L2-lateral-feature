# PP-PR-015 Xe khởi đầu trong cua đã trôi trước lệnh tài xế

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ xác nhận chính thức |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | Tiền điều kiện S4b, S7(e). PP-SWR-085, 088, 110 đến 115 |
| Tái hiện | S4b(b, c, d) và S7(e), seed 1 |

## 1. Hiện tượng

Trong các neo bắt đầu trên cung, xe có v_lat trước Tsteer. S4b(c) có thể can thiệp về phía đối diện với phía tạo trôi của kịch bản. S7(e) thiếu REQUEST trong lần chạy nháp.

## 2. Nguyên nhân

Harness khởi tạo yaw thân trùng tiếp tuyến tâm làn nhưng cấp v_y và yaw rate của trạng thái cua ổn định. Tại cầu sau, v_y khác 0. Hướng chuyển động vì vậy không trùng tiếp tuyến của làn. Góc lái danh định còn dùng độ cong tâm làn khi xe đứng trên đường offset.

## 3. Cách sửa

Với mô hình tài xế tạo trôi, khởi tạo hướng chuyển động của cầu sau theo tiếp tuyến và dùng độ cong của đường offset cho điều khiển danh định. Giữ thời điểm, cung tạo trôi và các mức trong kịch bản.

## 4. Xác nhận

Đo v_lat trước Tsteer bằng ground truth. Kiểm hướng của REQUEST đầu tiên trong các neo cua.
