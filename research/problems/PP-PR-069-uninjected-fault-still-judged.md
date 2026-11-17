# PP-PR-069 Lỗi gắn trigger không được bơm nhưng ca vẫn được chấm như đã bơm

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; chờ quyết định cách sửa |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | Mọi requirement chấm trên ca có lỗi bơm theo sự kiện (SQTS 6, `--at`) |
| Tái hiện | Đọc code `eval/metrics.py` tại sim-up-g0; ví dụ dựng được: lỗi gắn `lka_active` trên kịch bản không có LKA |

## 1. Hiện tượng

Khi sự kiện của trigger không xảy ra, lỗi không được bơm (`start_s = NEVER_S`). Evaluator chỉ ghi `info.faults_not_injected`. Criterion vẫn được chấm đạt hoặc trượt, tỉ lệ đạt và kết luận của suite không biết lỗi chưa được bơm. Chỉ `eval.check_case` in ra ghi chú.

Một ca như vậy có thể được tính là "đạt dưới lỗi" dù planner chưa bao giờ gặp lỗi.

## 2. Nguyên nhân

`metrics.evaluate` không chuyển trường hợp này thành issue `not_judged` (SQTS 8.4: lỗi phía test, ca không được chấm).

## 3. Cách sửa

Đề xuất: khi có lỗi không được bơm, thêm issue `not_judged` cho ca, để suite và kết luận tách ca này khỏi tỉ lệ đạt. Sửa này đổi kết quả chấm của các ca bị ảnh hưởng, nên cần người phụ trách đồng ý và chạy lại hồi quy.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
