# PP-PR-035 Counter của lane model: planner không kiểm; nghĩa của counter nhảy chưa rõ

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa (theo AUTOSAR E2E, người dùng chọn 2026-11-14), chờ hồi quy chính thức |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-130 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): F15 b, c trên S1a, S1c |

## 1. Hiện tượng

| Ca | Lỗi | Chu kỳ output khác ca tham chiếu |
|---|---|---|
| F15 b | Counter lane model nhảy 3, 1 trong 10 | 699–939 |
| F15 c | Counter lane model đứng yên 0,5 s | 715–955 |
| F15 d, e, f | Counter khung IMU lặp, đứng yên, nhảy | Đạt |

Một khung khác ca tham chiếu thì mọi chu kỳ sau đều khác, vì bộ lọc mang theo sai khác. Vậy số chu kỳ lớn không có nghĩa lỗi nặng.

## 2. Nguyên nhân

- Planner không kiểm counter của input; chỉ sinh counter cho output.
- Khung CAN (IMU) có lớp nhận trong simulator kiểm theo Interface Control Document: lặp hoặc CRC sai thì bỏ khung; nhảy thì ghi nhận mất khung và vẫn dùng khung. Lane model không qua lớp này.
- F15 c: counter đứng yên mà dữ liệu vẫn đổi. Theo cách hiểu thông thường của E2E, đó là khung lặp hoặc nguồn bị treo. Planner vẫn dùng, nên khác ca tham chiếu.
- F15 b: bên chấm coi khung có counter nhảy là không dùng được (`sim/faults/channel.py`, `LOSS_EQUIVALENT`); ca tham chiếu bỏ chính khung đó. Interface Control Document và lớp nhận CAN lại dùng khung đó. Câu "giống ca mất message tương ứng" của PP-SWR-130 hiểu được theo cả hai cách.

Nguồn liên quan:

| Văn bản | Nội dung | Tình trạng |
|---|---|---|
| Interface Control Document | Tham chiếu AUTOSAR E2E Profile 1 cho counter và CRC; counter nhảy thì ghi nhận mất khung | Có |
| AUTOSAR E2E Protocol Specification R22-11, mục 6.8.4.3, 6.8.4.4 ([PRS_E2E_00591], [PRS_E2E_00654]) | Profile 5 (counter 8 bit): OK (bước 1), OKSOMELOST (bước trong `MaxDeltaCounter`), REPEATED, WRONGSEQUENCE (bước lớn hơn). `MaxDeltaCounter` là cấu hình của hệ thống; ví dụ trong văn bản dùng 1 | Đã đọc 2026-11-14 |
| ISO 26262-6:2018, Annex D | Lỗi truyền thông (lặp, mất, trễ, sai thứ tự, hỏng) và cơ chế (counter, CRC, timeout) | Chưa có bản; cần kiểm |

## 3. Cách sửa

Chốt nghĩa trước, rồi sửa bên chấm và planner. Đề xuất theo cách của E2E:

| Trường hợp | Xử lý | Ca tham chiếu |
|---|---|---|
| Counter tăng 1 | Dùng | — |
| Counter nhảy, bước ≤ ngưỡng | Dùng khung; ghi nhận mất khung | Như không lỗi (giống CAN hiện nay) |
| Counter nhảy quá ngưỡng, hoặc đứng yên, hoặc lặp | Bỏ khung | Mất các khung đó |

- Ngưỡng bước counter cần nguồn (AUTOSAR E2E) hoặc ghi nhóm tự thống nhất.
- Sửa: Interface Control Document (quy tắc cho message pub/sub), PP-SWR-130 (tách nhảy trong ngưỡng và quá ngưỡng), `sim/faults/channel.py`, planner T1.

Đã làm 2026-11-14:

| Phần | Thay đổi |
|---|---|
| Interface Control Document 1.11 | Mục 3: MaxDeltaCounter = ⌊(timeout + chu kỳ planner) / chu kỳ message⌋, LaneModel và ObjectList 3, các input pub/sub 40–50 Hz 4. Mục 4: bảng trạng thái E2E; giữ message dùng được gần nhất |
| Software Requirements Specification 1.19 | PP-SWR-129: lặp hoặc nhảy trong giới hạn thì như không lỗi. PP-SWR-130: đứng yên hoặc nhảy quá giới hạn thì như mất message |
| Planner T1 | `pp_counter_accept` (`planner/src/input_check.c`); `pp_held_inputs_t` giữ message được nhận; unit test `tests/planner/c/test_input_check.c` |
| Bên chấm | `sim/faults/channel.py`: counter nhảy giữ độ lệch cho các message sau (trước đây message kế tiếp quay về counter cũ, tạo bước lùi); ca tham chiếu theo MaxDeltaCounter của kênh. Thêm F15 g |

- MaxDeltaCounter theo từng input: người dùng chọn "3 cho mọi input pub/sub". Cùng quy tắc suy từ timeout cho 4 ở input 40–50 Hz, vì planner 40 Hz lấy message mới nhất nên đôi khi bỏ qua một message mà không có gì mất. Chờ người dùng duyệt.
- SIL cục bộ (bản build từ cây làm việc, seed 1): F15 b trên S1a, S1c và F15 c trên S1a đạt 130 với 0 chu kỳ khác ca tham chiếu (trước đây 699–955); F15 g đạt 129 với 0 chu kỳ khác; S1 a không lỗi giữ kết quả cũ.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
