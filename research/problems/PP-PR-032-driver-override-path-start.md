# PP-PR-032 Khi tài xế ghi đè, path HWA không bắt đầu tại xe

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng; xác nhận ở 20261113-2255-suite-regression-e99cf08 |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-039, 040 (SG-05) |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): S17 a–e, S9 c, S16 d |

## 1. Hiện tượng

| Ca | PP-SWR-039 (≤ 0,05 m) | PP-SWR-040 (≤ 0,05 m) | Lần chạy |
|---|---|---|---|
| S17 (tài xế chuyển làn khi HWA bật) | 0,29–0,96 m | 0,21–0,60 m | 32 |
| S9 c (HWA bị ghi đè rồi buông) | 0,12–0,13 m | 0,051–0,055 m | 6 |
| S16 d (ngoài phạm vi 039) | 1,50 m | — | 2; kèm 100 nhảy 1,36 m |

## 2. Nguyên nhân

- `driver_override` chỉ dùng trong arbitration (`arbitration.c` dòng 51, 72, 83) để chặn LKA, ELK.
- Path HWA vẫn nối từ path cũ ở T4 (`pp_stitch_start`). Chỉ khi xe lệch path cũ quá `stitch_reset` (0,2 m) mới lấy trạng thái đo, rồi lại trộn. Vì vậy S9 c còn lệch 0,12 m, S17 lệch tới 0,96 m.
- Software Detailed Design không có bước nào cho ghi đè: PP-SWR-039, 040 chưa được thiết kế.

Nguồn liên quan:

| Văn bản | Mục | Nội dung |
|---|---|---|
| R79 | 5.6.4.3 | Tài xế lái thì ghi đè hệ thống; hệ thống được giữ active nếu ưu tiên tài xế trong lúc ghi đè |
| R171 | 5.5.3.4.1, 5.5.3.4.1.4 | Như trên cho DCAS; lực ghi đè ≤ 50 N |
| R171 | 5.5.3.4.1.4.1 | Ghi đè trong lúc đang làm manoeuvre thì kết thúc manoeuvre, trừ khi tài xế lái hỗ trợ manoeuvre |
| EU 2021/646 | Annex I Part 2, 3.6.3.1 | Không mất hỗ trợ lái đáng kể đột ngột sau khi bị ghi đè |
| R171 | Annex 4, 4.2.5.1.2 | Bài thử chuyển làn do tài xế khởi xướng |

- Path bắt đầu tại xe là cách để planner "ưu tiên tài xế": controller không kéo ngược tay lái.
- Hết ghi đè, path về tâm từ vị trí xe theo giới hạn của HWA là cách "không mất hỗ trợ đột ngột" mà không giật.

## 3. Cách sửa

- T4: trong khi `driver_override`, điểm đầu path lấy trạng thái đo của xe, không trộn với path cũ.
- Khi `driver_override` về false: path HWA bắt đầu tại xe, về tâm làn theo PP-SWR-001 đến 003, như bài đưa về giữa của S2.
- S17: sau khi lane model đổi làn, tâm mới là làn mới (PP-SWR-061). Cùng một cơ chế, không nhánh riêng cho S17.
- Ghi bước mới vào Software Detailed Design, T4.

Đã sửa 2026-11-13 (người dùng chọn sửa):

| Chỗ sửa | Nội dung |
|---|---|
| `planner/src/pp_state.h` | `driver_override`: giá trị của FunctionRequests dùng được gần nhất |
| `planner/src/pp_planner.c` | `follow_car` = đang ghi đè hoặc chu kỳ trước còn ghi đè; khi đó điểm đầu = trạng thái đo và bỏ trộn của T4 bước 4 |
| `tests/planner/c/test_step.c` | `test_driver_override_path_starts_at_car`: xe trôi 0,5 m/s; không ghi đè thì điểm đầu lệch xe > 0,05 m; ghi đè và chu kỳ đầu sau đó lệch < 0,01 m. Bỏ bản sửa thì test trượt (lệch −0,16 m) |
| Software Detailed Design 1.11 | T4 bước 2, 5 |

- 14/14 unit test C đạt (bản build T7 quintic).
- Rủi ro cần kiểm khi chạy: PP-SWR-100 đến 102 không được miễn trong lúc ghi đè. Path bám xe mỗi chu kỳ có thể làm hai path liên tiếp lệch nhau nhiều hơn trước ở S17, S9 c.

Lần chạy nháp 2026-11-13 (`benchmark/suites/PP-PR-032.yaml`, thư viện `5afcaf5` có sửa đổi, 42 lần chạy; không dùng để quyết định):

| Ca | 039, 040 | PP-SWR-100 trước sửa (20261113-1803-suite-regression-3c31309) | PP-SWR-100 sau sửa | 061 sau sửa |
|---|---|---|---|---|
| S17 a, c, d, e | Đạt, 0,0 m | 0,045–0,048 m | 2,18–2,19 m | 2,18–2,19 m |
| S17 b | Đạt | 0,047–0,052 m | 0,22–0,33 m | 0,11 m |
| S9 c | Đạt | 0,03 m | 0,12–0,13 m | — |

- Bản sửa đầu đổi lỗi 039, 040 lấy lỗi 100 đến 102, 061: không chọn.
- S9 c: lúc bắt đầu ghi đè, điểm đầu nhảy từ path cũ (lệch xe 0,12 m) về xe trong một chu kỳ. 039 ở chu kỳ đầu và 100 không thể cùng thoả khi xe đã lệch path cũ hơn 0,05 m: mâu thuẫn giữa requirement, giống trường hợp PP-SWR-031 đã có ngoại lệ.
- S17: lúc lane model đổi làn trong khi ghi đè, phần xa của path chuyển sang tâm làn mới; không còn bước trộn nên path nhảy 2,19 m. Đây là lỗi của thiết kế bản sửa: path trong lúc ghi đè vẫn nhắm tâm làn.

Theo PP-TS-017 (V2b, cách B): lần chạy nháp cuối, S17 a–e và S9 c đạt 039, 040, 061, 100 đến 102 ở cả 6 profile. S16 d còn trượt 100 đến 102 và "ELK có REQUEST nhưng thiếu path" như trước khi sửa (PP-PR-038). Quan sát kèm: S17 c (đổi làn trong cua R = 500 m) còn 051 −5,9 m ngoài phạm vi, như trước khi sửa.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

Xác nhận chính thức [20261113-2255-suite-regression-e99cf08](../runs/20261113-2255-suite-regression-e99cf08/report.md): 039, 040 hết trượt ở S17 (32 lần chạy) và S9 c (6); 039 ngoài phạm vi hết trượt ở S8c, S13, S5, S16; không có trượt mới trong phạm vi. [20261113-2330-matrix-PP-PR-032-e99cf08](../runs/20261113-2330-matrix-PP-PR-032-e99cf08/summary.md): S17 a–e, S9 c đạt hết; còn S16 d (PP-PR-038). Hệ quả phụ: PP-PR-040 (jerk S17 b chạm giới hạn).
