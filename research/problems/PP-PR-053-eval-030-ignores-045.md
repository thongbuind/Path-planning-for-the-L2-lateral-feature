# PP-PR-053 Cách chấm PP-SWR-030 mâu thuẫn với PP-SWR-045 (F20 a)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa phía đánh giá, chờ hồi quy chính thức |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-030, 045 |
| Tái hiện | [20261114-1952-suite-regression-0776bad](../runs/20261114-1952-suite-regression-0776bad/report.md): F20 a trên S4a lúc LKA, S5a lúc ELK, 4 lượt, 214–418 chu kỳ |

## 1. Hiện tượng

Ego-motion không hợp lệ một chu kỳ lúc LKA (ELK) đang chạy. Planner đặt `path_valid = false` (PP-SWR-143), sau đó không bắt đầu lại LKA vì REQUEST chưa rời rồi quay lại (PP-SWR-045). Bên đánh giá vẫn chờ LKA tới COMPLETED và tính mọi chu kỳ sau 1 s miễn trừ là chọn sai.

## 2. Nguyên nhân

Lỗi của bên đánh giá: `over_refusal` coi LKA, ELK đã bắt đầu là còn chạy tới COMPLETED, không xét mất input kết thúc lần can thiệp (PP-SWR-045).

## 3. Cách sửa

- `eval/metrics.py` (`over_refusal`): input cần cho path không dùng được thì lần LKA, ELK đang chạy kết thúc; chỉ tính lại khi bắt đầu cho REQUEST mới.
- Software Qualification Test Specification 1.42, mục 5.3.
- Nháp seed 1: F20 a trên S4a lúc LKA, S5a lúc ELK đạt. Planner không đổi.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
