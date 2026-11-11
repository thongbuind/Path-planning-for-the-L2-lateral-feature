# PP-TS-003 Kỹ thuật tạo path HWA (T7)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-11 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-SWR-001 đến 007, 050 đến 053, 100 đến 102, 151; SQTS mục 9 |

## 1. Câu hỏi

- Quyết định cần đưa ra: kỹ thuật tạo path HWA, và cắt cua nhẹ trong làn khi cần và đủ điều kiện an toàn.
- Yêu cầu của người dùng: cắt cua là một phần của cùng một thuật toán vẽ path, không phải một chế độ bật bằng `if`.

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Quintic theo thời lượng (T7 A), T10 cắt theo giới hạn | Bản hiện tại | Mốc |
| V1 | QP hợp nhất (T7 C): biến d_k tại 31 điểm; chi phí jerk, lệch tâm, phạt a_y vượt `a_comfort`; ràng buộc hành lang mỗi bên, a_y ≤ aysmax, jerk, góc lái; nối với path cũ | Build-time; `a_comfort` là calibration | Cắt cua tự xuất hiện khi ràng buộc chạm |
| V1 với `a_comfort` = 0 | Phạt thẳng a_y² | Calibration | Cùng công thức với V1: ràng buộc thành σ ≥ trị tuyệt đối của a_y |

Câu hỏi con: bộ giải ADMM tự viết hay OSQP (cần quyền tải về).

## 3. Cách đánh giá

Chưa khóa.

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | Requirement trong phạm vi của P1 và S14 |
| Xếp hạng | SQTS mục 9; thêm a_y lớn nhất của xe trong cua ngắn |
| Bộ chạy | Như M1, thêm cua ngắn và cua chữ S |
| Ngân sách chỉnh | Mỗi phương án một sweep cùng số bộ calibration |

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| 20261111-1024-matrix-M1-b9e5d4d | V0 | Đăng ký lại; mốc |

## 5. Kết quả

## 6. Đề xuất

## 7. Quyết định
