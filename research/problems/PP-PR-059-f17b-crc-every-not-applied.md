# PP-PR-059 F17 b: bộ bơm lỗi làm hỏng CRC của mọi khung, không phải 1 trong 10

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa trong cây làm việc 2026-11-17 (phía đánh giá); chờ chạy lại F16, F17 |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | PP-SWR-130, 142; PP-SWR-051 (chấm sai); PP-PR-046, 054 |
| Tái hiện | [20261115-1126-suite-full-7495822](../runs/20261115-1126-suite-full-7495822/report.md): F17 b trên S1c, 3/3 lượt trượt PP-SWR-051 (DLC −0,87 đến −1,29 m). Lượt nháp 2026-11-17: `python3 -m eval.runner S1 c --fault F17 b --seed 1`, bản build nháp có in trạng thái input |

## 1. Hiện tượng

- F17 b: "Khung tốc độ CRC sai, 1 trong 10", `every` = 10, 4,0–9,0 s, nhãn kỳ vọng `drive`.
- Lượt nháp: `path_valid = false` và `active_function = NONE` liên tục từ 4,058 tới 9,158 s. Xe vào cua S1c không được lái, lệch 1,77 m.
- Log input của planner: từ 4,0 tới 9,0 s không có khung tốc độ nào tới. Counter của message đứng ở 199 rồi sang 200 lúc 9,008 s; tuổi của khung tăng đều tới 4 999 ms. Trước lỗi, tuổi lớn nhất 19 ms.

## 2. Nguyên nhân

`ChannelFaultInjector.deliveries` (`sim/faults/channel.py`): nhánh `crc` áp cho mọi message trong cửa sổ lỗi, không xét `pick = k % every == 0`. Các nhánh `drop`, `late`, `counter_repeat`, `counter_jump` có xét. Nhánh `invalid` và `out_of_range` cũng không xét `every`.

- Lớp nhận CAN bỏ mọi khung CRC sai, nên tốc độ mất hẳn 5 s. Khung tốc độ gửi 50 Hz, timeout 60 ms (Interface Control Document 5.3).
- Planner đặt `path_valid = false` trong một chu kỳ, đúng PP-SWR-142. Ca này vì vậy không kiểm được hành vi "mất 1 trong 10 khung", và PP-SWR-051 bị chấm trên một ca mà planner phải từ chối.
- PP-PR-046 và phần F17 b của PP-PR-054 có cùng gốc này. Phần F21 c của PP-PR-054 không liên quan.

## 3. Cách sửa

Phía đánh giá, người dùng quyết định:

- Nhánh `crc` (và `invalid`) xét `every` như `drop`; ca có `every` = 1 không đổi.
- Chạy lại F17 và F16 sau khi sửa; so với ca đối chứng mất message tương ứng (PP-SWR-130).
- Đây là sửa cho đúng định nghĩa đã ghi của ca, không phải đổi kịch bản sau khi thấy kết quả.

## 4. Xác nhận

Đã sửa 2026-11-17, người dùng duyệt: nhánh `crc` và `invalid` của `sim/faults/channel.py` xét `every`. `tests/sim/test_fault_mechanisms.py`, `test_framework_extensions.py`, `test_faults.py`: 31 test đạt.

Lượt nháp sau khi sửa, S1 c + F17 b, seed 1, VP-0: HWA lái 99,9 % thời gian sau REQUEST, DLC nhỏ nhất 0,75 m, xe lệch lớn nhất 0,06 m; PP-SWR-051, 130, 142 đạt.

| Run ID | Kết quả |
|---|---|
| [20261117-0908-suite-regression-c56f0bf](../runs/20261117-0908-suite-regression-c56f0bf/report.md) | F17 b trên S1c hết trượt PP-SWR-051 (3 lượt) |
