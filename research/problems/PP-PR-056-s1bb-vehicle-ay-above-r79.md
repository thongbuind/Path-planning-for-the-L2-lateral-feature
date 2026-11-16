# PP-PR-056 S1b b: a_y của xe vượt aysmax + 0,3 tới cuối ca; ca quá ngắn để chấm 2 s của R79

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
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

## 3. Cách sửa

- Không sửa kịch bản sau khi thấy kết quả mà không ghi lý do (SQTS 3). Đề xuất: kéo dài cung của S1b đủ để đo trọn 2 s sau khi a_y xe vượt aysmax + 0,3, ghi lý do ở SQTS, rồi chạy lại mọi phương án của PP-TS-020.
- Phân tích log: lệch ngang xe so với path, lệnh của controller, giới hạn góc lái ở 10–13 s.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
