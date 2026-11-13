# PP-PR-031 Bên chấm không có tiêu chí cho PP-SWR-147 và 047

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; chờ sửa bên chấm |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-147, 047 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): 2.073 lần chạy, không lần nào có tiêu chí 147 hay 047 |

## 1. Hiện tượng

- PP-SWR-147 (Test: F21 a–d) và PP-SWR-047 (Test: F21) có cột Kiểm chứng là Test, nhưng `eval/metrics.py` không chấm.
- PP-SWR-148 được chấm gián tiếp qua 051, 100 đến 102 ở F21, đúng theo câu của 148.
- Hệ quả: PP-PR-030 chỉ lộ nhờ PP-SWR-030. PP-PR-011 không xác nhận được.

## 2. Nguyên nhân

- Không có hàm chấm 147, 047.
- `tools/trace.py` kiểm truy vết giữa SRS và kịch bản, không kiểm mỗi requirement Test có tiêu chí ở bên chấm.

## 3. Cách sửa

| Phần | Đề xuất |
|---|---|
| PP-SWR-147 | Số chu kỳ `path_valid = false` khi lane model báo mất hai vạch làn mình mà còn ít nhất một biên đủ tin. Điều kiện xét trên input lane model mà planner nhận (bên chấm thấy qua interface) |
| PP-SWR-047 | Số chu kỳ LKA hoặc ELK được chọn khi biên đủ tin chỉ còn ở ngoài làn đang chạy. Trừ ngoại lệ ELK mép đường theo câu của 047 (mép MEASURED, confidence ≥ `conf_edge`) |
| Chống lặp lại | Một test của bên chấm: mọi PP-SWR có Kiểm chứng là Test (trừ obsolete) phải có ít nhất một tiêu chí hoặc target mang ID đó |

- Ngưỡng `conf_edge`, `conf_inferred` đọc từ calibration như các tiêu chí khác.
- Nguồn của yêu cầu truy vết hai chiều giữa requirement và test: Automotive SPICE 3.1, SWE.6 (cần kiểm số BP); quy tắc bên chấm suy từ SRS của dự án.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
