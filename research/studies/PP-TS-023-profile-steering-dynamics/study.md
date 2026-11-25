# PP-TS-023 Dải đặc tính lái của vehicle profile cho phép chấm flexibility

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-17 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | SQTS 4.4, 8.3; `sim/vehicle/profiles.py` |

## 1. Câu hỏi

- Quyết định cần đưa ra: các vehicle profile có cần khác nhau về đặc tính lái (understeer gradient, steering ratio, actuator delay) để phép chấm flexibility có nghĩa không.
- Vì sao cần: với l_f = l_r = L/2, C_f = 50·m, C_r = 70·m (SQTS 4.4), K = (m/L)·(l_r/C_f − l_f/C_r) = ½·(1/50 − 1/70) ≈ 0,00286 rad/(m/s²) với mọi profile. Steering ratio 15 và actuator delay 0,05 s cũng chung. Profile chỉ khác hình học (L, bề rộng, góc bánh lớn nhất) và I_z. Flexibility (SQTS 8.3) vì vậy chưa kiểm một bộ calibration trên xe có đặc tính lái khác nhau.

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Bản hiện tại: K, ratio, delay chung | — | Mốc; ghi giới hạn này vào kết luận flexibility |
| V1 | Quét K, steering ratio, actuator delay trong dải có nguồn, trên bộ flexibility | Tham số của profile ở phía simulator; planner vẫn chỉ nhận VehicleConfig | Cần nguồn công bố cho dải của từng đại lượng trước khi khóa |

## 3. Cách đánh giá (khóa trong plan.yaml)

Chưa khóa. Cần nguồn cho dải trước.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

## 6. Đề xuất

2026-11-23, người phụ trách duyệt hướng; plan khóa khi cài xong ở simulator, chạy sau nhóm sửa planner:

| Đại lượng | Nguồn tìm được | Dải đề xuất |
|---|---|---|
| Understeer gradient K | Bộ số liệu SAE của xe những năm 1980, trích lại qua tài liệu giảng dạy: trung bình 2,6 deg/g (châu Âu), 4,4 deg/g (Mỹ). Chưa đọc được bản gốc | Quét 1, 2,5, 4,5 deg/g (0,0018 đến 0,0080 rad/(m/s²)); bản hiện tại 0,00286 rad/(m/s²) ≈ 1,6 deg/g |
| Steering ratio | Chỉ có tài liệu tra cứu chung: 12:1 đến 20:1 | Lấy số hãng công bố của từng xe trong profile khi có; không có thì quét 12, 15, 18 |
| Actuator delay | Không có số đo công bố | Quét 0,05, 0,10, 0,15 s, như S13 |

- Theo quy tắc của dự án, đại lượng không có nguồn uy tín thì quét nhiều mức; kết luận flexibility ghi rõ dải đã quét.
- Cài ở phía simulator (`sim/vehicle/profiles.py`), planner vẫn chỉ nhận VehicleConfig. Chạy trên bộ flexibility sau khi nhóm sửa planner xong, để không chỉnh planner theo dải này.

## 7. Quyết định
