# PP-PR-058 Đa thức dời bằng ego-motion mất 1 m tầm nhìn mỗi chu kỳ khi xe đổi hướng

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa trong cây làm việc 2026-11-17; chờ hồi quy chính thức |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | PP-SWR-121, 122, 124, 125; PP-SWR-018 |
| Tái hiện | Lượt nháp 2026-11-17: `python3 -m eval.runner S1 a --fault F06 d --seed 1`, bản build nháp từ cây làm việc 2f86a0b có in bộ nhớ biên (PP-PR-057) |

## 1. Hiện tượng

Tầm nhìn [đầu, cuối] của vị trí cũ (`previous`) của vạch L1, chỉ được dời bằng ego-motion, 25 m/s:

| Lúc [s] | Tầm nhìn [m] | Dài [m] | Cuối tầm nhìn đổi mỗi chu kỳ |
|---|---|---|---|
| 5,108–5,183 (xe chưa đổi hướng) | [−28,9; 50,1] tới [−30,8; 48,2] | 79 | −0,625 m, bằng quãng xe đi |
| 5,208 (xe bắt đầu đổi hướng) | [−31,4; 46,6] | 78 | −1,625 m |
| 5,283 | [−33,3; 41,7] | 75 | −1,625 m |
| 6,083 | [−53,3; −10,3] | 43 | — |

- Sau 0,9 s cuối tầm nhìn đã ở sau xe, trong khi theo quãng đường đi nó phải còn khoảng 25 m phía trước.
- Bộ nhớ đang dùng (`accepted`) trong 1 s bị loại trước đó, lúc xe đi thẳng, chỉ mất 0,625 m mỗi chu kỳ.

## 2. Nguyên nhân

`pp_cubic_move` (`latency.c`) lấy mẫu tại x_start + i · 1 m, số mẫu = floor(dài / 1 m) + 1, và trả tầm nhìn mới là x nhỏ nhất, lớn nhất của các mẫu đã xoay.

- Khi Δψ ≠ 0, các mẫu sau khi xoay cách nhau hơi dưới 1 m, nên độ dài mới hơi dưới một số nguyên. Lần gọi sau floor bỏ một mẫu: mất 1 m. Lặp lại ở mọi chu kỳ.
- Khi độ dài không nguyên, lần gọi đầu mất phần lẻ (lane model 80 m thành 79 m sau T1).

Nơi dùng đa thức được dời nhiều chu kỳ liên tiếp:

| Nơi | Hậu quả |
|---|---|
| T2, bộ nhớ biên (`accepted` khi đang loại frame, `candidate`, `previous`) | Đoạn tầm nhìn chung với frame mới ngắn dần rồi hết; phép kiểm hình dạng (PP-TS-001) yếu dần rồi bị bỏ, chỉ còn so c0. PP-PR-048 đã ghi hiện tượng này mà chưa tìm nguyên nhân |
| T2 bước 5, bám reference line cũ trong `T_coast` | Trong cua, `view_end` của reference line co nhanh hơn quãng xe đi; ảnh hưởng `observed_horizon_s`. Chưa đo |
| T1, một lần dời mỗi frame | Mất dưới 1 m; không tích luỹ |

## 3. Cách sửa

Sửa cơ chế chung trong `pp_cubic_move` (2026-11-17, cây làm việc chưa commit):

- Thêm một mẫu tại đúng x_end khi tầm nhìn không dài tròn bước lấy mẫu; tầm nhìn mới vì vậy kết thúc ở x_end đã dời.
- Giữ quy tắc tầm nhìn dưới 3 m thì không khớp lại, nay viết thành điều kiện riêng (trước đây là hệ quả của số mẫu).
- Không đổi hành vi đã quy định (Software Detailed Design mục 4, bước 3), nên không cần trade study.
- Unit test mới trong `tests/planner/c/test_latency.c`: `test_repeated_move_keeps_the_view_range` (40 chu kỳ có đổi hướng, tầm nhìn 79,9 m chỉ mất quãng xe đi), `test_move_under_three_metres_fails`. Unit test C 15/15 đạt.

Lỗi này không phải nguyên nhân của PP-PR-057: F06 d không đổi sau khi sửa.

## 4. Xác nhận

Lượt nháp 2026-11-17, seed 1, VP-0, thư viện build ngoài cây làm việc từ 2f86a0b cộng thay đổi chưa commit. Trước là `build/planner` (build 2026-11-16), sau là bản đã sửa. Ô ghi DLC nhỏ nhất [m] / lệch giữa hai path chia ngưỡng (PP-SWR-100):

| Ca | Trước | Sau |
|---|---|---|
| S1 a, S1 c, S1 f, S12 a, S4 a, S5 a | Đạt | Như trước, cùng giá trị |
| S1 a + F02 a; S1 c + F01 c; S1 c + F05 a | Đạt | Như trước, cùng giá trị |
| S1 a + F06 a | 0,64 / 0,301 | 0,64 / 0,305 |
| S1 c + F06 e | 0,32 / 0,409 | 0,30 / 0,363 |
| S1 a + F06 d | −0,99 / 0,450 (trượt 051) | −0,99 / 0,449 (trượt 051) |

| Run ID | Kết quả |
|---|---|
