# PP-PR-046 F17 b trên S1c: CRC tốc độ sai, xe ra khỏi làn

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-051; liên quan 142 |
| Tái hiện | [20261114-1021-suite-regression-d7ed84c](../runs/20261114-1021-suite-regression-d7ed84c/report.md): F17-b-S1c, VP-0, VP-1, VP-5, seed 1 |

## 1. Hiện tượng

Lỗi F17 b: cứ 10 khung tốc độ thì có 1 khung CRC sai, từ 4 s, kéo dài 5 s. Kết quả mong đợi là `drive`.

| Ca | DLC nhỏ nhất so với làn thật, 051 |
|---|---|
| F17-b-S1c, VP-0 | −0,99 m |
| F17-b-S1c, VP-1 | −0,87 m |
| F17-b-S1c, VP-5 | −1,29 m |
| F17-b-S1a, VP-0, VP-1, VP-5 | Đạt (0,19–0,50 m) |

- Trượt ở cua S1c, không trượt ở đường thẳng S1a.
- Giá trị giống hệt ở [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md), [20261113-2341-suite-regression-1014d20](../runs/20261113-2341-suite-regression-1014d20/report.md) và run này. Bản sửa PP-PR-034 không đổi kết quả.
- PP-SWR-142 đạt ở 6/6 lượt F17 b.
- Lần đầu ghi nhận là quan sát kèm trong PP-PR-034.

## 2. Nguyên nhân

Chưa rõ. Cần xem MCAP của ba lượt trượt (`build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F17-b-S1c-*`) để biết:

- Xe rời làn trong lúc path không hợp lệ, hay sau khi path hồi phục.
- Lớp nhận có bỏ khung CRC sai và giữ mẫu tốc độ cuối như Interface Control Document 5.3 không, hay planner thấy tốc độ mất.

## 3. Cách sửa

Chờ phân tích nguyên nhân.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| [20261117-0908-suite-regression-c56f0bf](../runs/20261117-0908-suite-regression-c56f0bf/report.md) | F17 b trên S1c hết trượt PP-SWR-051 sau khi sửa PP-PR-059 |
| [20261122-0758-suite-regression-591e3de](../runs/20261122-0758-suite-regression-591e3de/report.md) | F17 b không có trong lượt trượt. Đóng 2026-11-23: cùng gốc với PP-PR-059 |
