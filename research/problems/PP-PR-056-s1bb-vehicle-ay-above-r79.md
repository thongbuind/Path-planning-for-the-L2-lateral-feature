# PP-PR-056 S1b b: a_y của xe vượt aysmax + 0,3 tới cuối ca; ca quá ngắn để chấm 2 s của R79

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, đã tìm nguyên nhân chính: T4 giữ điểm đầu path trên path cũ. Kịch bản đã sửa (SQTS 1.45). Sửa qua PP-TS-021 |
| Mở ngày | 2026-11-16 |
| Requirement bị ảnh hưởng | R79 5.6.2.1.1, Annex 8 3.2.2 (chưa có PP-SWR; tiêu chí `PP-TS-020/R79-5.6.2.1.1`); PP-SWR-001; SQTS 5.1 (S1b) |
| Tái hiện | [20261116-1548-study-PP-TS-020-04ae8c5](../runs/20261116-1548-study-PP-TS-020-04ae8c5/summary.md): S1b b, ACC `ignore_limits`, VP-0, seed 3, 4. Chẩn đoán 2026-11-16 (nháp, thư viện của lần chạy đó): seed 3, V0, V1a, V1b |

## 1. Hiện tượng

S1b b: 90 km/h, R = 150 m, cua cần 4,2 m/s², ACC không giảm tốc (bài R79 Annex 8, 3.2.2). a_y của xe lọc theo Annex 8, 2.4:

| Phương án | Trần path [m/s²] | a_y path từ 9 s | a_y xe thô từ 10,5 s | a_y xe lọc lớn nhất | Thời gian trên 2,8 m/s² | Tiêu chí R79 |
|---|---|---|---|---|---|---|
| V0 | 2,5 | 2,50 | 3,0–3,15 | 3,19 | 1,89 s | Đạt |
| V1a | 2,6 | 2,60 | 3,1–3,26 | 3,29 | 1,91 s | Đạt |
| V1b | 2,7 | 2,70 | 3,1–3,41 | 3,39 | 1,93 s | Trượt (> 3,3) |

- Path đứng ở trần từ 9 s. Xe vượt path 0,5–0,7 m/s² từ 10,5 s, ở cả ba phương án.
- Điểm đầu của path lệch khỏi xe 0,16–0,19 m từ 10,5 s, dưới `stitch_reset` = 0,2 m, nên path vẫn nối từ path cũ.
- Log dừng khoảng 13 s. Thời gian a_y xe trên 2,8 m/s² bị cắt ở cuối log, ở mọi phương án.

## 2. Nguyên nhân

Hai phần, chưa tách hết:

- **Bên chấm (kịch bản):** ca S1b b kết thúc trước khi đo được 2 s của R79 5.6.2.1.1. Với V0 và V1a, kết quả "đạt" là do độ dài ca, không phải do hành vi. Cần xem lại độ dài cung của S1b (a, b, c).
- **Bám path:** khi path bão hòa, xe lệch khỏi path khoảng 0,18 m và controller thêm 0,5–0,7 m/s² để kéo về. Chưa rõ phần nào do Lateral Controller chạy thử, phần nào do T4 giữ path nối từ path cũ khi xe lệch dưới `stitch_reset`.

**Chẩn đoán 2026-11-16** (nháp, không dùng để quyết định): S1b a, b dài 17 s (SQTS 1.45), seed 3, ACC `ignore_limits`, VP-0. V0 là thư viện của 20261116-1607-study-PP-TS-020-d1d50de; bản nháp là V0 với `stitch_reset` = 0 (path luôn bắt đầu từ trạng thái đo). "Lệch đầu path" là y của điểm 0 trong `base_link`.

| Ca | Bản | Lệch đầu path từ 11 s [m] | a_y xe trừ a_y path, 5 s cuối [m/s²] | a_y xe lọc lớn nhất | Trên 2,8 m/s² | Tiêu chí R79 |
|---|---|---|---|---|---|---|
| S1b a | V0 | 0,16–0,20 | 0,46 | 3,10 | 2,12 s | Trượt |
| S1b a | `stitch_reset` = 0 | 0,00 | 0,10 | 2,67 | 0 s | Đạt |
| S1b b | V0 | 0,16–0,20 | 0,78 | 3,52 | 5,89 s | Trượt |
| S1b b | `stitch_reset` = 0 | 0 tới 13 s, rồi tăng tới 0,42 | 0,83 | 3,61 | 3,96 s | Trượt |

- Controller chạy thử bám được path khi path bắt đầu từ xe (S1b a: a_y xe cách path 0,1 m/s²). Phần lớn a_y xe vượt path không do controller.
- Nguyên nhân phía planner: T4 bước 2 giữ điểm đầu path trên path cũ khi xe lệch dưới `stitch_reset` (0,2 m). Xe đứng cách đầu path khoảng 0,18 m suốt đoạn cua, và controller kéo thêm 0,5–0,8 m/s² để về path.
- S1b b: với `stitch_reset` = 0, từ 13 s đầu path vẫn rời xe tới 0,42 m. Giả thuyết: T4 bước 4 (trộn về path cũ theo ngưỡng liên tục) kéo điểm đầu về path cũ; khi cua cần 4,2 m/s², xe rời path nhanh hơn mức trộn cho phép.
- Chưa rõ vì sao điểm đầu nối từ path cũ trôi vào trong so với xe ở V0 (ego-motion khi dời path cũ, hoặc T10 tích phân lại từ điểm 0). PP-SWR-100 đạt ở cả hai bản.

## 3. Cách sửa

- Không sửa kịch bản sau khi thấy kết quả mà không ghi lý do (SQTS 3). Đề xuất: kéo dài cung của S1b đủ để đo trọn 2 s sau khi a_y xe vượt aysmax + 0,3, ghi lý do ở SQTS, rồi chạy lại mọi phương án của PP-TS-020.
- ~~Phân tích log: lệch ngang xe so với path, lệnh của controller, giới hạn góc lái ở 10–13 s.~~ Đã làm 2026-11-16 (mục 2).
- Phía planner, có nhiều cách nên cần trade study: (A) giảm `stitch_reset` trong dải quét; (B) khi path đã chạm trần a_y, bắt đầu từ trạng thái đo; (C) T4 bước 4 không kéo điểm đầu về path cũ (gần V4 của PP-TS-019); (D) tìm và sửa nguồn trôi của điểm đầu nối từ path cũ.
- Trước khi chọn: một lần chẩn đoán S1b b với bản nháp bỏ T4 bước 4, để kiểm giả thuyết ở mục 2.
- 2026-11-16: người dùng chọn mở [PP-TS-021](../studies/PP-TS-021-stitch-start/study.md) thay cho chẩn đoán thêm. Đọc code xác nhận giả thuyết: T4 bước 4 trộn cả path, gồm điểm 0, ở mọi chu kỳ HWA, kể cả chu kỳ vừa reset về trạng thái đo.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| [20261116-1607-study-PP-TS-020-d1d50de](../runs/20261116-1607-study-PP-TS-020-d1d50de/summary.md) | S1b a, b chạy 17 s (SQTS 1.45): tiêu chí R79 trượt ở mọi phương án, kể cả V0 (path ở aysmax). Phần kịch bản đã sửa; bản hiện tại trượt bài R79 Annex 8, 3.2.2. Phần bám path còn mở |
