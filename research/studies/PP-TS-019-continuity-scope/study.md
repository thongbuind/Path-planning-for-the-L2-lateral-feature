# PP-TS-019 Phạm vi của PP-SWR-100 đến 102 và giới hạn trộn của T4

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; phạm vi requirement đã quyết, giới hạn trộn của T4 chưa có plan |
| Mở ngày | 2026-11-14 |
| Khóa ngày | — |
| Quyết định ngày | 2026-11-16 (phạm vi và ngưỡng của PP-SWR-100 đến 102) |
| Liên quan | PP-SWR-100, 101, 102 và các requirement dựa vào chúng; giới hạn jerk, a_y của chức năng đang lái; PP-ASM-021; `cont_margin`, T4; PP-TS-014; PP-PR-004, 005, 006, 021 |

## 1. Câu hỏi

- Quyết định cần đưa ra:
  - PP-SWR-100 đến 102 áp trên đoạn nào của path.
  - T4 trộn với giới hạn nào ở đoạn gần và ở phần xa của path.
- Vì sao cần:
  - PP-SWR-100 trượt nhiều nhất ở [20261114-1021-suite-regression-d7ed84c](../../runs/20261114-1021-suite-regression-d7ed84c/report.md): 113 lần chạy trong phạm vi, chấm theo ngưỡng cũ 0,05 m.
  - Log MCAP của 10 ca trượt (một ca mỗi nhóm, VP-0 hoặc VP-2, seed 1): lệch > 0,05 m nằm ở t = 2,1–2,9 s của path (50–75 m phía trước). Trong 0–0,6 s, lệch lớn nhất 2–8 mm; trong 0–1 s, 3–19 mm. Ngoại lệ: S14 e, 46 mm trong 0–0,6 s (PP-PR-004).
  - Bản phân tích trên dùng script nháp đọc MCAP, chưa phải lần chạy chính thức.
  - 2026-11-16 mentor nới ngưỡng: PP-SWR-100 lên 0,2 m; 101, 102 nới tương ứng thành 0,02 rad, 0,0012 1/m (SRS 1.21). Ngưỡng không còn là câu hỏi của study này.
  - T4 trộn một λ cho cả path theo ngưỡng chặt nhất, đoạn 0–1 s, với `cont_margin` 0,9 (Software Detailed Design 1.20): 0,045 m, 0,0045 rad, 0,00027 1/m trên toàn tầm nhìn. Phần xa không dùng được ngưỡng nới của SRS 1.22.
  - Ước lượng ở đoạn gần: 25 m/s, controller nhìn trước 0,6 s (PP-ASM-021), tức 15 m. Lệch ngang Δy tại điểm nhìn trước đổi độ cong khoảng 2·Δy/15².

| Δy tại 15 m | Δκ | Bước a_y = v²·Δκ | Bước góc vô lăng (VP-0: 2,9 m, tỉ số 15) |
|---|---|---|---|
| 0,045 m | 0,0004 1/m | 0,25 m/s² | 1,0° |
| 0,18 m | 0,0016 1/m | 1,0 m/s² | 4,0° |
| 0,2 m | 0,0018 1/m | 1,1 m/s² | 4,4° |

Các bước trên xảy ra trong một chu kỳ 25 ms. Riêng PP-SWR-102 ở 0,0012 1/m cho bước a_y tới 0,75 m/s².

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Một ngưỡng mentor trên toàn tầm nhìn lane model báo (SRS 1.21); T4 một λ theo ngưỡng chặt nhất | — | Mốc; requirement đã thay bằng V1 ba đoạn (mục 8) |
| V1 | Đoạn gần, từ 0 tới `T_near` ≥ thời gian nhìn trước của controller (PP-ASM-021, 0,6 s): requirement chặt hơn ngưỡng mentor. Phần còn lại trong tầm nhìn: ngưỡng mentor | Bên chấm | `T_near` và ngưỡng đoạn gần cần lập luận an toàn và mentor đồng ý |
| V2 | Ngưỡng lệch ngang tăng theo khoảng cách, tới ngưỡng mentor ở cuối tầm nhìn | Bên chấm | Hệ số cần nguồn, ví dụ sai số vị trí vạch của camera theo khoảng cách |
| V3 | Requirement ba đoạn (mục 8); T4 một λ trên cả path, `cont_margin` 0,9, ngưỡng đoạn 0–1 s | — | Bản hiện tại (Software Detailed Design 1.20); mốc cho phần T4 |
| V4 | Requirement ba đoạn; T4 trộn theo từng đoạn, mỗi đoạn tới `cont_margin` · ngưỡng của đoạn đó | Planner T4, chọn lúc build | Theo cách Autoware, Apollo giữ đoạn gần; cần sửa Software Detailed Design T4 |

## 3. Cách đánh giá

Chưa khóa. Hướng đề xuất:

- Chạy một lần các suite với bên chấm đo thêm độ lệch theo từng đoạn thời gian của path, rồi chấm cùng các lần chạy theo V0, V1, V2.
- V3, V4 là các thư viện planner khác nhau, chấm theo SRS 1.21. Loại phương án trượt requirement. Xếp hạng theo độ lệch tâm làn và độ trễ bám làn khi tầm nhìn ngắn hoặc vào cua (PP-PR-021).
- Thước đo của đề bài đo trên chuyển động thật: bước nhảy của lệnh lái và của xe. Ví dụ tốc độ quay vô lăng, bước a_y, jerk ngang của xe trong 0,5 s sau mỗi chu kỳ có lệch lớn.
- Cần chỉ ra phương án nào loại được các trường hợp có bước nhảy lệnh lái thật, và không loại các trường hợp không có.

## 4. Tham khảo

| Nguồn | Nội dung |
|---|---|
| Apollo, `modules/planning/planning_base/common/trajectory_stitcher.cc` và `planning_gflags.cc` (đọc 2026-11-14) | Path mới nối tiếp path cũ ở đoạn đầu (điểm khớp theo thời gian hiện tại cộng một chu kỳ, giữ tối đa 20 điểm cũ); phần sau lập lại mỗi chu kỳ. Lập lại từ trạng thái xe khi lệch ngang > 0,5 m hoặc lệch dọc > 2,5 m |
| Autoware `autoware_path_optimizer`, tài liệu MPT (đọc 2026-11-14, chỉ một phần trang) | Giữ quỹ đạo gần xe trùng lần trước là ràng buộc cứng duy nhất; không thấy ràng buộc cho phần xa |
| Autoware `autoware_path_optimizer`, mục replan (đọc 2026-11-16 qua kết quả tìm kiếm, chưa đối chiếu trang gốc) | Tối ưu lại khi path đầu vào đổi ngang quanh xe > 2,0 m, xe đi > 3,0 m trong một chu kỳ, hoặc sau 1,0 s; ngoài ra dùng lại quỹ đạo cũ. `enable_reset_prev_optimization` mặc định false |
| openpilot (tìm 2026-11-16) | Không thấy ngưỡng lệch giữa hai path |
| UN R79 5.6.2.1.3; UN R171 5.3.7.1 | Giới hạn a_y và jerk của xe; không có ngưỡng cho lệch giữa hai path |

## 5. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 6. Kết quả

## 7. Đề xuất

- Soạn plan so V3 với V4 trên bộ chỉnh và bộ kiểm, chấm theo SRS 1.22.

## 8. Quyết định

2026-11-16, người quyết định: thongbui. Chọn V1 với ba đoạn, không chờ lần chạy:

| Đoạn theo `time_from_start` | Lệch ngang | Lệch hướng | Lệch độ cong | Nguồn |
|---|---|---|---|---|
| 0–1 s | 0,05 m | 0,005 rad | 0,0003 1/m | nhóm tự thống nhất |
| 1–2 s | 0,1 m | 0,01 rad | 0,0006 1/m | nhóm tự thống nhất |
| Sau 2 s | 0,2 m | 0,02 rad | 0,0012 1/m | mentor |

- Lý do: đoạn 0–1 s chứa thời gian nhìn trước của controller (PP-ASM-021) và cùng đoạn với PP-SWR-006; bước a_y ở mục 1. Lệch lớn ở log cũ nằm sau 2 s.
- Đã áp: SRS 1.22, Software Qualification Test Specification 1.44, Software Detailed Design 1.20, Software Architectural Design 1.9, Mentor Report 1.6; `eval/metrics.py`.
- V2 bỏ. Giới hạn trộn của T4 (V3 hay V4) còn mở.
