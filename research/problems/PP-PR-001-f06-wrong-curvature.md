# PP-PR-001 Độ cong sai ở xa (F06) làm xe ra khỏi làn

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-051, 125 |
| Tái hiện | 20261111-1024-matrix-M1-b9e5d4d: S1a + F06a (4/4 lần chạy), S1c + F06e (4/4 lần chạy), ACC `on`, VP-0 và VP-5 |

## 1. Hiện tượng

Lane model báo c2 sai; xe đi theo cua giả và lốp đè vạch.

Lần chạy nháp `build/suites/smoke-20261111-1425` trên đường chủ S1c (cua chạm aysmax): F06 a, b, d, e làm xe ra khỏi làn; F06 b còn trượt PP-SWR-100 và 101, F06 e trượt PP-SWR-100.

## 2. Nguyên nhân

Hai nguyên nhân, đã thấy khi phân tích lần chạy nháp:

- Giới hạn liên tục PP-SWR-100 áp trên cả đoạn 0–3 s của path, nên path cũ (đúng) bị kéo theo path mới (sai) ngay cả ở đoạn gần.
- T5 nhận độ cong sai trong khoảng 1 s, vì phương sai của camera lúc đó vẫn nhỏ.

## 3. Cách sửa

Chưa chọn. Có hai hướng trở lên (giới hạn liên tục theo đoạn; T5 tin camera ít hơn ở xa), nên sẽ mở trade study.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
