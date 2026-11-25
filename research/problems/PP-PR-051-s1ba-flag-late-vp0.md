# PP-PR-051 S1b a, VP-0: cờ giới hạn chưa bật khi lốp đè vạch

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng, xác nhận ở 20261122-0758-suite-regression-591e3de |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-007 |
| Tái hiện | [20261114-1952-suite-regression-0776bad](../runs/20261114-1952-suite-regression-0776bad/report.md): S1b a VP-0 seed 1 |

## 1. Hiện tượng

- PP-SWR-007 trượt tại 8,69 s, 1 lượt; đạt ở d7ed84c.
- Thay đổi giữa hai lần chạy: kiểm hình dạng (PP-TS-001), kiểm counter (PP-PR-035), T10 trước T4 (PP-TS-003).

## 2. Nguyên nhân

Trong [hồi quy bb08d77](../runs/20261119-0948-suite-regression-bb08d77/report.md), LCC đang ở COAST và cờ đã bật trước khi `path_valid` mất ở 7,858 s. Nhánh path không hợp lệ xóa trạng thái cờ. Path trở lại ở 8,583 s, PP-SWR-007 trượt ở 8,641 s và cờ bật lại ở 8,658 s. Cần phân tích vì sao path mất trước khi đánh giá cách giữ cờ qua giai đoạn mất path.

## 3. Cách sửa

Ở bản quintic `ecfe00e`, T10 giữ mức hỗ trợ gia tốc ngang cho đoạn gần khi cờ giới hạn đã bật và hình học cua từ camera nhất quán với reference line. Hồi quy trên ca tái hiện giữ path hợp lệ qua đoạn từng mất path.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| [20261119-0948-suite-regression-bb08d77](../runs/20261119-0948-suite-regression-bb08d77/report.md) | S1b a VP-0 seed 1 còn trượt tại 8,641 s |
| [20261122-0758-suite-regression-591e3de](../runs/20261122-0758-suite-regression-591e3de/report.md) | S1b a VP-0 seed 1 đạt PP-SWR-005, 006 và 007 |
