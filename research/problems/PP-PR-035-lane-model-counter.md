# PP-PR-035 Counter của lane model: planner không kiểm; nghĩa của counter nhảy chưa rõ

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; cần quyết định về requirement |
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
| AUTOSAR E2E Protocol Specification | Phân biệt mất vài khung nhưng khung hiện tại dùng được (bước counter ≤ `MaxDeltaCounter`) với sai thứ tự hoặc lặp (không dùng) | Chưa tải; cần kiểm số mục và tên trạng thái |
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

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
