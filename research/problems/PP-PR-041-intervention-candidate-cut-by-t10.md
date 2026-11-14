# PP-PR-041 Path ELK bị T10 cắt jerk, không kết thúc song song với làn (S7)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng; xác nhận ở 20261114-1021-suite-regression-d7ed84c |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-100; liên quan 085, 088, 115 |
| Tái hiện | [20261113-2341-suite-regression-1014d20](../runs/20261113-2341-suite-regression-1014d20/report.md): S7-ncap-oncoming-left-2 VP-1, VP-5, seed 1. Cùng hiện tượng ở S7 a VP-1, VP-5 (bộ khác, không thuộc B2) |

## 1. Hiện tượng

| Ca | PP-SWR-100 | Thời điểm | Ghi chú |
|---|---|---|---|
| S7-ncap-oncoming-left-2, VP-1 | 0,0505 m | 6,827 s | Sát giới hạn |
| S7-ncap-oncoming-left-2, VP-5 | 0,0558 m | 7,027 s | ELK bắt đầu 6,877 s |
| S7 a, VP-1 | 0,0505 m | 6,827 s | Giá trị giống hệt ca Euro NCAP: cùng hình học |

- Bên chấm bỏ qua chu kỳ đầu theo PP-SWR-031. Các chu kỳ sau, điểm xa nhất của path (t = 2,9 s, x ≈ 58 m) dời 0,02–0,056 m mỗi chu kỳ, cùng một chiều, trong khoảng 0,3 s.
- Path ELK đầu tiên (VP-5, đường thẳng): sau đoạn kéo vào, path đi thẳng với hướng +8,6 mrad so với làn, quay ra lại phía vạch trái. Vị trí điểm cuối +0,55 m so với tâm làn; path ở các chu kỳ sau hội tụ về +0,09 m.

## 2. Nguyên nhân

- T7 chọn ứng viên quintic bằng `pp_feasibility_check`: jerk là trung bình trượt 0,5 s (định nghĩa của requirement).
- T10 bước 2 (`pp_feasibility_limit`) cắt jerk theo từng bước 0,1 s, chặt hơn (Software Detailed Design mục 13).
- Ứng viên 1,25 s đạt theo trung bình 0,5 s nhưng vượt theo từng bước. T10 cắt jerk ở ±10 m/s³ tại 9 bước. Tích phân độ cong của path sau khi cắt: hướng chỉ đổi −1,4 mrad, trong khi cần −10 mrad để song song với làn. Phần còn lại của path lệch 8,6 mrad.
- Mỗi chu kỳ T7 lấy mẫu cùng quintic tại thời điểm muộn hơn, T10 cắt khác đi, nên phần xa đổi. T4 trộn giới hạn mức dời ở `cont_margin`·0,05 m. T10 chạy sau T4, nên vài chu kỳ vượt 0,05 m.
- Đã loại giả thuyết T5 lấy yaw rate làm số đo độ cong: độ cong phần xa của path giữ 0 suốt lần can thiệp.

## 3. Cách sửa

- T7 coi ứng viên thoả giới hạn khi T10 bước 2 không cắt nó. Ứng viên bị cắt chỉ được chọn khi không còn ứng viên nào khác (`planner/src/intervention.c`, `candidate_score`). Áp cho cả LKA và ELK.
- Software Detailed Design 1.12, mục 10 ghi quy tắc này. Không đổi requirement, không đổi calibration.
- Unit test: `tests/planner/c/test_intervention.c`, `test_chosen_candidate_is_not_cut_by_t10`.
- Hệ quả cần kiểm: ứng viên dài hơn có thể làm DTLE (PP-SWR-086) và khoảng hở tới xe (088) xấu đi. Chạy lại toàn bộ lưới LKA, ELK (S4 đến S8, S16), không chỉ S7.
- Còn lại, chưa sửa: T10 chạy sau T4, nên path bị cắt sau khi trộn vẫn có thể vượt PP-SWR-100. Chỉ mở thêm nếu lần xác nhận còn thấy.

Lần chạy nháp ngày 2026-11-14 (`build/pr041-b2`, bộ B2 của manifest regression 1014d20, 594 lần chạy; thư viện có cả code chưa commit của PP-PR-030): S7-ncap-oncoming-left-2 và S7 a hết trượt 100; lưới LKA, ELK không có trượt mới; DTLE, 085, 088 xấu nhất không đổi; jerk lớn nhất của path ELK 9,2 → 4,1 m/s³. Chưa phải xác nhận chính thức.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| [20261114-1021-suite-regression-d7ed84c](../runs/20261114-1021-suite-regression-d7ed84c/report.md) | S7-ncap-oncoming-left-2 (VP-1, VP-5), S7 a hết trượt 100; S8b c hết trượt 100. Không trượt mới do bản sửa này: trượt mới F02 e lúc LKA (085) có trước bản sửa và nặng hơn khi bỏ bản sửa (PP-PR-044) |
