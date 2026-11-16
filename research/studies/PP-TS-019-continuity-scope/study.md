# PP-TS-019 Phạm vi và ngưỡng của PP-SWR-100 đến 102

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; plan chưa soạn |
| Mở ngày | 2026-11-14 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-SWR-100, 101, 102 và các requirement dựa vào chúng; PP-ASM-021; PP-TS-014; PP-PR-004, 005, 006 |

## 1. Câu hỏi

- Quyết định cần đưa ra: PP-SWR-100 đến 102 áp trên đoạn nào của path và với ngưỡng nào.
- Vì sao cần:
  - PP-SWR-100 trượt nhiều nhất ở [20261114-1021-suite-regression-d7ed84c](../../runs/20261114-1021-suite-regression-d7ed84c/report.md): 113 lần chạy trong phạm vi.
  - Log MCAP của 10 ca trượt (một ca mỗi nhóm, VP-0 hoặc VP-2, seed 1): lệch > 0,05 m nằm ở t = 2,1–2,9 s của path (50–75 m phía trước). Trong 0–0,6 s, lệch lớn nhất 2–8 mm; trong 0–1 s, 3–19 mm. Ngoại lệ: S14 e, 46 mm trong 0–0,6 s (PP-PR-004).
  - Nguồn ghi trong SRS là "đề bài", nhưng đề bài không có con số. Đề bài yêu cầu: "re-planning without a step when the lane model updates" và chuyển chức năng "must not produce a step in the steering request".
  - Bản phân tích trên dùng script nháp đọc MCAP, chưa phải lần chạy chính thức.

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Giữ nguyên: 0,05 m, 0,005 rad, 0,0003 1/m trên toàn tầm nhìn lane model báo | — | Mốc |
| V1 | Đoạn gần, từ 0 tới `T_near` ≥ thời gian nhìn trước của controller (PP-ASM-021, 0,6 s): requirement, ngưỡng như V0. Phần còn lại trong tầm nhìn: performance target, vẫn đo và xếp hạng | Bên chấm | `T_near` cần nguồn hoặc lập luận |
| V2 | Ngưỡng lệch ngang tăng theo khoảng cách trên toàn tầm nhìn | Bên chấm | Hệ số cần nguồn, ví dụ sai số vị trí vạch của camera theo khoảng cách |

## 3. Cách đánh giá

Chưa khóa. Hướng đề xuất:

- Chạy một lần các suite với bên chấm đo thêm độ lệch theo từng đoạn thời gian của path, rồi chấm cùng các lần chạy theo V0, V1, V2.
- Thước đo của đề bài đo trên chuyển động thật: bước nhảy của lệnh lái và của xe. Ví dụ tốc độ quay vô lăng, jerk ngang của xe trong 0,5 s sau mỗi chu kỳ có lệch lớn.
- Cần chỉ ra phương án nào loại được các trường hợp có bước nhảy lệnh lái thật, và không loại các trường hợp không có.

## 4. Tham khảo

| Nguồn | Nội dung |
|---|---|
| Apollo, `modules/planning/planning_base/common/trajectory_stitcher.cc` và `planning_gflags.cc` (đọc 2026-11-14) | Path mới nối tiếp path cũ ở đoạn đầu (điểm khớp theo thời gian hiện tại cộng một chu kỳ, giữ tối đa 20 điểm cũ); phần sau lập lại mỗi chu kỳ. Lập lại từ trạng thái xe khi lệch ngang > 0,5 m hoặc lệch dọc > 2,5 m |
| Autoware `autoware_path_optimizer`, tài liệu MPT (đọc 2026-11-14, chỉ một phần trang) | Giữ quỹ đạo gần xe trùng lần trước là ràng buộc cứng duy nhất; không thấy ràng buộc cho phần xa |
| UN R79 5.6.2.1.3; UN R171 5.3.7.1 | Giới hạn a_y và jerk của xe; không có ngưỡng cho lệch giữa hai path |

## 5. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 6. Kết quả

## 7. Đề xuất

Nguồn "đề bài" của PP-SWR-100 đến 102 cần sửa thành nguồn đúng, dù chọn phương án nào.

## 8. Quyết định
