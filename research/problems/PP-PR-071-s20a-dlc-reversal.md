# PP-PR-071 DLC giảm lại trong S20a

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng (e395662, PP-TS-026) |
| Mở ngày | 2026-11-18 |
| Yêu cầu | PP-SWR-094 |
| Ca tái hiện | S20a và F24a trên S20a tại ELK ACTIVE, VP-0, seed 1 |

DLC thật phía can thiệp giảm lại quá 0,1 m sau khi đã phục hồi. Hiện tượng xuất hiện cả ở ca danh định S20a và ở ca có frame F24a đã tới planner.

So sánh hai log tại thời điểm DLC bắt đầu giảm để xác định vai trò của quỹ đạo và bộ điều khiển ngang.

## Xác nhận 20261118-2030-suite-regression-e3158a5

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | PP-SWR-094 từ 124 lần còn 0 |
