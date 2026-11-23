# PP-PR-082 Requirement có trong phạm vi chấm nhưng bên chấm chưa có criterion

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-23 |
| Requirement bị ảnh hưởng | PP-SWR-045, 046, 132, 141, 144, 151, 152 |
| Tái hiện | `python -m eval.verification_metrics` trên `results.jsonl` của 20261122-0758-suite-regression-591e3de |

## 1. Hiện tượng

- PP-SWR-045, 046, 141, 144, 151, 152 nằm trong phạm vi của các ca ở cột Kiểm chứng (F12, S14, Q4), nhưng không lượt nào có criterion mang ID đó. Câu requirement không trỏ tới requirement khác, nên không được kiểm gián tiếp.
- PP-SWR-132 (stamp ở tương lai quá 10 ms) có trong phạm vi của F19 nhưng criterion chưa lần nào áp dụng được.
- Cách đếm requirement coverage cũ coi các requirement này là đã kiểm vì có trong phạm vi.

## 2. Nguyên nhân

Phía đánh giá: `eval/metrics.py` chưa có phép chấm cho các câu này; với PP-SWR-132, điều kiện áp dụng của criterion chưa xảy ra trên F19.

## 3. Cách sửa

Viết criterion theo câu requirement, từ thứ quan sát được qua Interface Control Document; chạy lại F12, F19, S14, Q4. Không đổi planner trước khi có kết quả.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
