# PP-PR-003 Đưa về giữa khi xe đang hướng ra ngoài: lốp đè vạch (S2c, S2d)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ hồi quy |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-051, 052 |
| Tái hiện | 20261111-1024-matrix-M1-b9e5d4d: S2c (24/24 lần chạy), S2d (4/24), cả ACC `off` và `on` |

## 1. Hiện tượng

- S2c: HWA bật khi xe lệch 0,5 m, góc 2° hướng ra ngoài, 90 km/h. Xe tiếp tục ra tới khoảng 1,0 m rồi mới quay về. DLC nhỏ nhất −0,19 m (VP-0) đến −0,50 m (VP-5).
- S2d: lệch 0,4 m phía ngoài cua trái R = 500 m. DLC nhỏ nhất −0,02 m ở VP-5.
- M1 không tính các lần này là trượt, vì cột Kiểm chứng của SRS không gán PP-SWR-051 cho S2.

## 2. Nguyên nhân

Phân tích trạng thái đầu của S2c (làn 3,5 m) theo điều kiện vào HWA (ADAS Function Specification mục 7: `hwa_entry_dlc` 0,2 m, `hwa_entry_offset` 0,5 m, `hwa_entry_heading` 2°). Bề rộng xe tính cả gương, theo `sim/vehicle/profiles.py`.

| Profile | Bề rộng | DLC lúc bật | Điều kiện vào |
|---|---|---|---|
| VP-0 | 1,90 m | 0,30 m | Thoả, đúng biên của lệch tâm và góc lệch |
| VP-1 | 1,96 m | 0,27 m | Thoả |
| VP-2 | 2,11 m | 0,195 m | Không thoả DLC |
| VP-3 | 2,21 m | 0,145 m | Không thoả DLC |
| VP-4 | 2,254 m | 0,123 m | Không thoả DLC |
| VP-5 | 2,50 m | 0,0 m | Không thoả DLC |

Hai nguyên nhân:

- Khối Chức năng ADAS chạy thử chưa kiểm điều kiện vào HWA. `hold_until_hwa` giữ xe tới khi HWA lái, nên ở VP-2 đến VP-5 kịch bản chạy ngoài điều kiện vào.
- Ở VP-0, VP-1, ba ngưỡng vào thoả riêng từng cái nhưng gộp lại vẫn chắc chắn đè vạch. Vận tốc ngang 25·sin 2° ≈ 0,87 m/s; còn 0,30 m tới vạch, tức TLC ≈ 0,34 s. Muốn dừng trôi trước vạch cần a_y thêm vào ≈ 0,87² / (2 · 0,30) ≈ 1,26 m/s², chưa tính trễ; `ay_add_max_hwa` là 0,5 m/s².

Planner đúng với calibration hiện có. Đây là mâu thuẫn giữa các calibration parameter của điều kiện vào và ngân sách đưa về giữa.

## 3. Cách sửa

Chưa chọn. Các hướng chung, không riêng cho S2c:

| Hướng | Nội dung | Thuộc |
|---|---|---|
| A | Khối Chức năng ADAS chạy thử kiểm điều kiện vào HWA theo ADAS Function Specification mục 7; ngoài điều kiện thì từ chối | Bên chấm (SIL) |
| B | Thêm điều kiện vào theo TLC (hoặc theo lệch tâm và góc lệch gộp), để trạng thái đầu luôn dừng trôi được với `ay_add_max_hwa` | ADAS Function Specification |
| C | Khi xe đang hướng ra ngoài, cho a_y thêm vào lớn hơn `ay_add_max_hwa`, trong giới hạn của PP-SWR-001 | Software Detailed Design, calibration |

A cần làm trong mọi trường hợp. B hoặc C xử lý phần còn lại ở VP-0, VP-1.

Tác động của hướng A (2026-11-23, tính từ trạng thái đầu của anchor, chưa chạy): với `hwa_entry_dlc` 0,2 m, `hwa_entry_offset` 0,5 m, `hwa_entry_heading` 2°, khối Chức năng ADAS sẽ từ chối LCC ở 9 anchor trên một số profile: S2 b, c, d, e; S3b e; S9 a, c; S19 a, b. Ở S19 (làn 2,5 m), mọi profile rộng từ 2,11 m trở lên bị từ chối, nên PP-SWR-063 mất ca chấm lúc bắt đầu. Cần quyết cùng lúc cách giữ độ phủ của PP-SWR-063 (làn hẹp lại trong lúc LCC đang lái).

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| Sửa 2026-11-23, hướng A, người phụ trách duyệt | `sim/stand_ins/hwa_entry_gate.py`, nối ở `sim/harness.py` `_gated_hwa` cho cả chế độ scripted và A, B. DLC tại trục trước theo ADAS Function Specification mục 5. Bị từ chối mà không có mô hình tài xế thì xe được giữ bám làn. Lượt nháp: S2 c từ chối ở mọi profile (VP-0: DLC tại trục trước 0,199 m < 0,2 m vì góc 2° hướng ra ngoài); S2 b VP-0 vào được; S2 b, d, e, S3b e, S9 a, c trên VP-5 đạt; S19 b đạt PP-SWR-063. Thêm S19 (f) để giữ độ phủ của PP-SWR-063 khi làn hẹp lại trong lúc LCC lái. Hướng B, C không cần nữa: điều kiện DLC tại trục trước đã loại trạng thái đầu chắc chắn đè vạch |
