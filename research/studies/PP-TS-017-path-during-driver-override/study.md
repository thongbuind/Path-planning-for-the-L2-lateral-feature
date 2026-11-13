# PP-TS-017 Path HWA trong lúc tài xế ghi đè

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã quyết V2b, cách B; đã đưa vào, chờ hồi quy chính thức |
| Mở ngày | 2026-11-13 |
| Khóa ngày | — (người dùng chọn trước khi chạy so sánh, mục 7) |
| Quyết định ngày | 2026-11-13 |
| Liên quan | PP-SWR-039, 040, 061, 100 đến 102; PP-PR-032; SG-05 |

## 1. Câu hỏi

- Quyết định cần đưa ra: path HWA có hình dạng nào trong lúc `driver_override`, và PP-SWR-100 đến 102 áp ra sao ở chu kỳ bắt đầu ghi đè.
- Vì sao cần: PP-PR-032. Bản sửa đầu (V1) làm 039, 040 đạt nhưng 100 trượt tới 2,19 m ở S17 và 0,12 m ở S9 c (lần chạy nháp). Ở chu kỳ đầu của lần ghi đè, khi xe đã lệch path cũ hơn 0,05 m, 039 và 100 không thể cùng thoả.

## 2. Phương án

| ID | Phương án | Ghi chú |
|---|---|---|
| V0 | Bản trước PP-PR-032: path nối từ path cũ, ghi đè không đổi gì ở T4 | 039, 040 trượt ([20261113-1803-suite-regression-3c31309](../../runs/20261113-1803-suite-regression-3c31309/report.md)) |
| V1 | Điểm đầu tại xe, vẫn về tâm làn, bỏ trộn của T4 | Loại theo lần chạy nháp: 100 trượt 2,19 m lúc lane model đổi làn |
| V2 | Điểm đầu tại xe; đích ngang = độ lệch hiện tại của xe (song song với làn, không về tâm); chỉ bỏ trộn ở chu kỳ đầu ghi đè. Hết ghi đè: điểm đầu tại xe, về tâm theo `T_recenter`, có trộn. Định nghĩa Hai path liên tiếp không tính cặp path ở chu kỳ đầu ghi đè khi xe thật lệch path cũ hơn 0,05 m | Cùng kiểu ngoại lệ với PP-SWR-031 |
| V3 | Giữ 100 chặt; nới 039: điểm đầu tiến dần về xe | Controller còn kéo ngược tài xế trong lúc chuyển tiếp; đi ngược R79 5.6.4.3 |
| V4 | Path ngoại suy chuyển động hiện tại của xe (hướng, yaw rate) | Bám ý định tài xế nhất; phần xa đổi nhiều khi tài xế xoay vô lăng, dễ trượt 100 |

Nguồn: R79 5.6.4.3 (ưu tiên tài xế trong lúc ghi đè); R171 5.5.3.4.1, 5.5.3.4.1.4; EU 2021/646 Annex I Part 2, 3.6.3.1 (không mất hỗ trợ đột ngột); Software Architectural Design, bảng T9 ("path bám vị trí xe").

## 3. Cách đánh giá

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | PP-SWR-039, 040, 061, 100 đến 102 và phạm vi của `benchmark/suites/scope.yaml` |
| Bộ chạy | `benchmark/suites/PP-PR-032.yaml`: S17 a–e, S16 d (ACC tắt), S9 c (ACC bật), VP-0 đến VP-5, seed 1 |
| Hồi quy | Bộ hồi quy đầy đủ sau khi đưa vào |

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

Chỉ có lần chạy nháp (`benchmark/suites/PP-PR-032.yaml`, thư viện `5afcaf5` có sửa đổi, 42 lần chạy). Không dùng để trích dẫn; dùng để chọn biến thể trước khi chạy chính thức.

| Biến thể | 039, 040 | PP-SWR-100 ở S17 a–e | 061 | S9 c |
|---|---|---|---|---|
| V0 (hồi quy chính thức) | Trượt: S17 0,29–0,96 m; S9 c 0,12 m | Đạt, 0,045–0,052 m | Đạt | 039 trượt |
| V1 | Đạt | Trượt, tới 2,19 m | Trượt, tới 2,19 m | 100 trượt 0,12 m |
| V2 (bỏ trộn ở chu kỳ đầu ghi đè) | Đạt, trừ S17 b: 039 0,30–0,32 m, 040 0,19 m | Đạt, 0,046–0,049 m | Đạt | Đạt hết |
| V2b (bỏ trộn trong cả lần ghi đè), chấm như cũ | Đạt ở mọi ca | Trượt, 0,17–0,30 m | S17 b trượt (0,12 m) | Đạt hết |
| V2b, cách B (không chấm liên tục trong lúc ghi đè) | Đạt ở mọi ca | Đạt, 0,045–0,047 m | Đạt | Đạt hết |

- Với cách B, ngoài phạm vi cũng tốt hơn V0: 051 ở S17 a, d, e đạt (trước −0,56 đến −1,31 m), S17 b −0,33 m (trước −1,26 m). S17 c vẫn −5,9 m như V0 (đổi làn trong cua R = 500 m), chưa rõ nguyên nhân.
- S16 d không đổi giữa các biến thể (100 tới 1,34 m, "ELK có REQUEST nhưng thiếu path"): thuộc PP-PR-038.
- S17 b là đổi làn nhanh (2,5 s). Ở V2, bước trộn giữ 100 ở 0,049 m nên kéo điểm đầu khỏi xe. Ở V2b, điểm đầu ở xe nhưng path mỗi chu kỳ đoán tài xế sẽ dừng trôi, tài xế lại không dừng, nên hai path liên tiếp lệch 0,17–0,30 m.
- Khi tài xế lái thật (đổi làn), không hình dạng path nào giữ cả 039 và 100 trong 0,05 m: planner không đoán trước tay lái của tài xế.

## 6. Đề xuất

V2 cho hình dạng path. Còn một câu hỏi về requirement, người dùng quyết:

| Cách | Nội dung | Hệ quả |
|---|---|---|
| A | Giữ như hiện tại (V2, ngoại lệ chỉ ở chu kỳ đầu ghi đè) | Path liên tục; khi tài xế lái nhanh, điểm đầu lệch xe tới 0,3 m (S17 b trượt 039, 040) |
| B | V2b; định nghĩa Hai path liên tiếp không tính mọi cặp path trong khi `driver_override = true` | 039, 040 đạt ở mọi ca; liên tục chỉ chấm ngoài lúc ghi đè (kể cả 061 khi lane model đổi làn trong lúc ghi đè) |

Cách làm của hệ thống thật (đọc bản gốc 2026-11-13):

| Nguồn | Trong lúc tài xế lái | Khi tài xế buông |
|---|---|---|
| Apollo, `modules/planning/planning_base/common/trajectory_stitcher.cc` | Không nối với path cũ khi xe không ở `COMPLETE_AUTO_DRIVE` ("replan for manual mode"); path mới tính từ trạng thái hiện tại của xe (`ComputeReinitStitchingTrajectory`) | Nối lại với path cũ; vẫn tính lại từ xe khi lệch ngang quá `replan_lateral_distance_threshold` (mặc định 0,5, `planning_gflags.cc`) |
| Mando, US 8,406,957 B2 (2013) | Mô-men hỗ trợ giảm dần (fade out) | Mô-men tăng lại dần; nếu độ lệch ngang đã ổn định thì lấy làm vị trí bám mới (vị trí tài xế chọn), nếu không thì về tâm làn |
| Volvo Car Corp., EP 3018040 A1 (2016) | Mô-men overlay nhân hệ số theo mô-men tài xế; ghi đè kéo dài thì giảm hẳn về 0 | Có trễ theo thời gian, mô-men; hết ghi đè thì hệ số trở lại |
| Subaru, US 10,780,882 B2 (2020) | Đích vẫn là tâm làn; các số hạng hiệu chỉnh không cập nhật | Hiệu chỉnh trở về dần, tuyến tính trong một khoảng thời gian định trước |
| Robert Bosch GmbH, US 9,567,006 B2 (2017) | Mô-men tài xế quá ngưỡng thì LKA tắt | LKA tự bật lại khi mô-men tay dưới ngưỡng |

- Việc "ưu tiên tài xế" nằm chủ yếu ở controller và EPS (giảm hoặc nhân mô-men theo mô-men tài xế), không ở path.
- Planner chỉ nối liên tục với path cũ khi hệ thống đang tự lái (Apollo). Khi tài xế lái, path tính lại từ trạng thái xe mỗi chu kỳ, không có ràng buộc liên tục.
- Lúc trả quyền lái lại cho hệ thống thì mọi nguồn đều làm dần: mô-men tăng dần, hoặc đích trở về tâm dần.
- openpilot: không đọc được mã nguồn (đường dẫn trên GitHub đã đổi); không dùng làm nguồn.

Đề xuất B. Lý do: R79 5.6.4.3 và R171 5.5.3.4.1 ưu tiên tài xế trong lúc ghi đè; lúc đó tài xế cầm lái, nên điểm đầu path lệch xe nghĩa là controller kéo ngược tài xế (SG-05). Liên tục của path (SG-04) vẫn giữ từ chu kỳ tài xế buông: path đầu tiên bắt đầu tại xe và được trộn với path trước. B giống cách của Apollo (không nối path khi không tự lái); phần về tâm dần sau khi buông giống Subaru, Mando.

Hướng mở thêm, chưa đề xuất làm: như Mando, sau khi buông giữ vị trí tài xế đã chọn thay vì về tâm, nếu độ lệch đã ổn định. R79 5.6.4.1.2 cho phép vị trí khác tâm khi hợp lý; cần requirement riêng.

## 7. Quyết định

- Người quyết, ngày: thongbui, 2026-11-13
- Chọn: V2 cho hình dạng path (thongbui, 2026-11-13); rồi cách B ở mục 6, tức V2b và không chấm liên tục trong lúc ghi đè (thongbui, 2026-11-13, sau khi xem cách làm của hệ thống thật)
- Lý do: như mục 6; V1 loại theo lần chạy nháp; V3 đi ngược R79 5.6.4.3; A để điểm đầu lệch xe 0,3 m khi tài xế lái nhanh
- Đưa vào: Software Requirements Specification 1.16 (định nghĩa Hai path liên tiếp); Software Qualification Test Specification 1.37 mục 8.1; Software Detailed Design 1.11 T4, T7; planner (`pp_state.h`, `pp_planner.c`); bên chấm (`eval/metrics.py`: `_overriding`, 100 đến 102, 061); unit test C `test_driver_override_path_starts_at_car`, Python `test_continuity_not_judged_while_the_driver_overrides`
- Hồi quy: chưa có run ID
