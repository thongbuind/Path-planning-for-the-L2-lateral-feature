# PP-PR-020 Tick COMPLETED còn lệch khi đối chiếu điều kiện thật

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | PP-SWR-032, 090 |
| Tái hiện | S4b(b, c, e), S6(b), VP-0, seed 1. Dùng phép đo bổ sung PP-SWR-032, 090 ngoài cột Kiểm chứng của các neo này |

## 1. Hiện tượng

S4b(b) đạt điều kiện giữ trên ground truth trước tick COMPLETED. S4b(c, e) và S6(b) báo COMPLETED trước khi điều kiện thật giữ đủ. Hai bản build có cùng hành vi.

## 2. Nguyên nhân

T9 xét điều kiện từ geometry ước lượng và tín hiệu chassis. Eval xét cùng giới hạn trên geometry thật và chuyển động thật. Sai lệch vẫn còn ở các ca này sau khi đưa v_y về t0 theo PP-PR-018. Chưa xác định tín hiệu chi phối ở từng tick chuyển ngưỡng.

Đối chiếu code 2026-11-13 (`pp_intervention_settled`, `eval/metrics.py` `_end_condition`):

| Thành phần | Planner | Bên chấm | Khác |
|---|---|---|---|
| DLC | Lệch tâm tại cầu trước, hành lang của reference line (mép đường ở phía nguy hiểm với ELK mép đường) | DLC tại cầu trước, mép đường ở phía nguy hiểm, vạch ở phía kia | Cùng định nghĩa; khác ước lượng và thật |
| Góc lệch | Tại base_link so với reference line | Tại cầu sau so với làn thật | Cùng điểm |
| v_lat | Tại cầu trước, v_y đưa về t0 (PP-TS-012) | Tại cầu trước, chuyển động thật | Cùng định nghĩa |
| a_y thêm vào | Path cũ tại t0 trừ v²·κ của reference line ước lượng | Path cũ tại t0 trừ v²·κ của làn thật | κ ước lượng và κ thật |

- Hai bên dùng cùng định nghĩa và cùng thời điểm. Chỗ lệch là sai số ước lượng so với ngưỡng: `heading_end` 0,5°, `v_lat_end` 0,1 m/s, `ay_add_end` 0,2 m/s². Ở 25 m/s, sai 0,1° góc lệch là sai 0,044 m/s v_lat; sai 0,0003 1/m độ cong là sai 0,19 m/s² a_y.
- Sai số khớp đa thức trên cung R = 500 m (S4b b, c) tại xe chỉ 0,01°, 4·10⁻⁵ 1/m: không đủ giải thích S4b(c). Còn lại: độ trễ của T5 trên clothoid (S4b e), tuổi của v_y, reference line từ mép đường (S6 b).
- Hướng chung, không phụ thuộc nguyên nhân: PP-SWR-090 chấm trên chuyển động thật, nên planner cần biên cho sai số ước lượng (ví dụ ngưỡng trừ một bội của phương sai lane model báo). Báo muộn thì an toàn hơn báo sớm.

## 3. Cách xác nhận

Đối chiếu mỗi thành phần của điều kiện kết thúc quanh đầu cửa sổ giữ. Dùng input ICD và ground truth để kiểm sai số của heading, v_lat tại cầu trước và a_y thêm vào. Giữ ngưỡng và các kịch bản đã chốt. Xem PP-TS-012 khi chọn cách xử lý.
