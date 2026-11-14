# PP-TS-015 Phạm vi chấm của ca có ca chủ

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng |
| Mở ngày | 2026-11-13 |
| Khóa ngày | — |
| Quyết định ngày | 2026-11-13 |
| Liên quan | Software Qualification Test Specification 5, 6.2, 8.1; `benchmark/suites/scope.yaml`; PP-SWR-051, 032, 005, 006 |

## 1. Câu hỏi

- Quyết định cần đưa ra: một ca chạy trên một anchor khác (lỗi trên ca chủ, ca ghép, biến thể "Sx dưới điều kiện khác") được chấm theo phạm vi nào.
- Vì sao cần: quy tắc hiện tại không nhất quán giữa các loại ca.

| Loại ca | Phạm vi trước khi sửa |
|---|---|
| Lỗi F trên ca chủ S1a, S1c (`fault_hosts`) | Chỉ phạm vi của lỗi. Ca chủ bị gán cứng là S1a và không góp phạm vi |
| Lỗi F bơm theo pha (`event_hosts`), ca ghép G01 | Phạm vi của ca chủ cộng phạm vi của lỗi (`scope_keys`) |
| S12, S13, S14 (SQTS 5 ghi biến thể là anchor khác: "a) S1c") | Chỉ phạm vi của chính mã đó |
| Bộ quét Q1–Q4, M1 có lỗi | Chỉ phạm vi của lỗi |

- Bảng phạm vi gốc lấy từ suite của sweep P1 (`scope_from: P1`). Sửa P1 thì đổi luôn phạm vi chấm chính thức.
- Lần chạy nháp `20261113-1218-full-ecf2f15` (cây làm việc chưa sạch, không trích làm bằng chứng): nhiều lần xe rời làn thật (PP-SWR-051) trên S12(a), F06, F01 bị xếp ngoài phạm vi.

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Như trước | — | Mốc so sánh |
| V1 | Quy tắc chung: ca có ca chủ nhận phạm vi của ca chủ cộng phạm vi của lỗi. Biến thể mà SQTS 5 ghi là một anchor khác nhận phạm vi của anchor đó. Bảng phạm vi gốc thuộc `scope.yaml` | `eval.matrix.scope`, `case_scope`; `scope.yaml` mục `base`, `hosts` | Một chỗ tính cho `eval.suite`, `eval.compare`, `eval.runner`, `eval.matrix` |
| V2 | Ghi tay từng mã dẫn xuất vào cột Kiểm chứng của Software Requirements Specification | Sửa SRS | Dài, dễ sót khi thêm lỗi hay ca chủ mới |

## 3. Cách đánh giá

- Tiêu chí loại: không requirement nào rời khỏi phạm vi của một lần chạy (quy tắc mới chỉ được chặt hơn). Mọi loại ca trong bảng mục 1 dùng cùng một quy tắc.
- Kiểm: chấm lại `results.jsonl` của một lần chạy với quy tắc mới, so phạm vi từng lần chạy. Không chạy lại simulator.
- Unit test: `tests/eval/test_scope.py`.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| — | V1 | Chấm lại nháp trên `20261113-1218-full-ecf2f15`: 0 lần chạy mất requirement khỏi phạm vi. Chưa có lần chạy chính thức |

## 5. Kết quả

- `base` của `scope.yaml` giống hệt phạm vi của P1 tại ngày mở (`test_base_is_owned_by_scope_file_and_equals_p1_start`).
- V1 chỉ thêm requirement vào phạm vi. Phần thêm chủ yếu là PP-SWR-051 cho lỗi trên ca chủ S1 và cho S12(a); PP-SWR-032 cho S12(b, d), S13.
- Còn ngoài phạm vi sau V1, có chủ ý:
  - Ca lấy mẫu của S12, S13, S14: tham số khác anchor, nên không coi là anchor đó.
  - S14(e): SQTS ghi S1f ở 130 km/h, tức đã đổi tham số.
- Ngoài phạm vi vì cột Kiểm chứng của SRS: PP-SWR-051 ở S2, S17. Cần xét riêng ở SRS, không thuộc quy tắc này.

## 6. Đề xuất

V1. Lý do: một quy tắc cho mọi ca có ca chủ; SQTS 8.1 đã yêu cầu chấm theo kịch bản mà cột Kiểm chứng chỉ ra, và ca lỗi trên S1a vẫn là một lần chạy S1(a). Bảng phạm vi tách khỏi study P1 để study không đổi phạm vi chấm.

## 7. Quyết định

- Người quyết, ngày: thongbui, 2026-11-13
- Chọn: V1, gồm hai điểm của mục 5: ca lấy mẫu của S12, S13, S14 không nhận phạm vi của anchor; S14(e) không nhận phạm vi của S1(f)
- Lý do: như mục 6. Ca lỗi mà planner không tự phát hiện được (ví dụ F03 c) vẫn trượt PP-SWR-051; đây là giới hạn cần báo, không thu hẹp phạm vi để giấu
- Đưa vào: Software Qualification Test Specification 1.34 mục 8.1; `benchmark/suites/scope.yaml`; `eval/matrix.py`
- Hồi quy: [20261113-1851-matrix-M1-5afcaf5](../../runs/20261113-1851-matrix-M1-5afcaf5/summary.md): 10 trượt trong phạm vi, đều PP-SWR-051 ở F02 e và F06 trên ca chủ S1(a), S1(c), đúng như mục 5; 28 trượt ngoài phạm vi (S2 c, d, PP-PR-003). [20261113-1803-suite-regression-3c31309](../../runs/20261113-1803-suite-regression-3c31309/report.md): F03 c, F08 c, F17 b, F21 c trượt PP-SWR-051 trong phạm vi theo cùng quy tắc.
