# PP-PR-027 S8b(c): khối Chức năng ADAS chạy thử gửi REQUEST trong ca không được can thiệp

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa theo cách C (thongbui, 2026-11-13); chờ xác nhận chính thức |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | Không có requirement của planner. Định nghĩa S8b(c) ở Software Qualification Test Specification 5; ADAS Function Specification mục 6, bước 5 |
| Tái hiện | Lần chạy nháp `20261113-1218-full-ecf2f15`: S8b(c) trên VP-0 đến VP-5, seed 1, cả 6 ca "không được chấm" |

## 1. Hiện tượng

- S8b(c): tài xế bật xi-nhan chuyển làn; xe sau cách 20 m tại TLC 0,8 s, nhanh hơn 8 m/s. Software Qualification Test Specification 5 ghi ca này không can thiệp.
- Khối Chức năng ADAS chạy thử gửi ELK REQUEST một lần ở chế độ A và một lần ở chế độ B (`adas_requests`). Theo Software Qualification Test Specification 4.8, ca không được chấm planner.
- Kết quả là ca S8b(c) chưa từng chấm planner.

## 2. Nguyên nhân

- Biến thể a–e được chọn bằng cách so ngưỡng của ADAS Function Specification mục 6, bước 5 tại một thời điểm, TLC 0,8 s: a, b, c dưới ngưỡng; d trên `ttc_rear` (TTC 1,2 s); e trên `decel_rear` (3,3 m/s²).
- ADAS Function Specification không nói xét điều kiện tới lúc nào. Khối chạy thử xét liên tục tới khi lốp qua vạch 0,3 m (`_LATE_LINE_M`, mục 11).
- Diễn biến của c, ước tính với v_lat khoảng 0,5 m/s (cung R = 800 m như bài thử Euro NCAP có xi-nhan); chưa đo trong log:

| Thời điểm từ TLC 0,8 s | Khe | TTC | Giảm tốc cần |
|---|---|---|---|
| 0 s | 20 m | 2,5 s | 1,6 m/s² |
| 0,8 s, lốp chạm vạch | 13,6 m | 1,7 s | 2,4 m/s² |
| 1,4 s, lốp qua vạch 0,3 m | 8,8 m | 1,1 s | 3,6 m/s² |
| 2,5 s | 0 m nếu xe sau không phanh | — | — |

- Kết luận: c là ca cắt vào trước xe đang tới gần nhanh. Xe sau phải phanh gấp, hoặc va chạm nếu không phanh. Khối chạy thử gửi ELK là đúng. Nhãn "không can thiệp" của SQTS sai, vì chỉ xét một thời điểm.
- Văn bản ủng hộ can thiệp: R79 2.3.4.3 (a)(iii), ESF cho xe ở làn mà tài xế chủ ý chuyển sang; Euro NCAP SA 4.3.3.5, DIM phải bị bỏ qua để tránh va chạm với vật trên hướng va chạm. Văn bản ủng hộ không can thiệp khi không có nguy cơ va chạm: EU 2021/646 điều (5), (6), Annex I 3.3.1; R79 5.1.6.2.1.

## 3. Cách sửa

Lỗi ở phía test. Không sửa planner.

| Cách | Thay đổi | Hệ quả |
|---|---|---|
| A | Đổi tham số của c cho khe an toàn | Dùng lại mã c cho một tình huống khác; mất một ca cắt vào nguy hiểm |
| B | ADAS Function Specification: chỉ xét tới lúc lốp chạm vạch | c còn TTC 1,7 s, sát ngưỡng; bỏ qua nguy cơ còn tăng sau khi chạm vạch |
| C | Giữ tham số của c, đổi kết quả mong đợi thành can thiệp; thêm biến thể f mới với khe an toàn (ví dụ 40 m, Δv 8 m/s, tính lại trước khi chạy); ADAS Function Specification ghi rõ xét liên tục tới khi lốp qua vạch 0,3 m | SQTS mục 5 (S8b c, f), mục 4.8; `S8b.anchors.xosc`; ADAS Function Specification mục 6 bước 5 |

Đề xuất C. Mã c giữ nguyên tham số, chỉ sửa kết quả mong đợi sai. Ca c chuyển từ không chấm sang chấm planner, nên chặt hơn, không làm planner trông tốt hơn. Trước khi chốt, đo v_lat và thời điểm qua vạch trong log của S8b(c).

Câu hỏi mở cho ADAS Function Specification: tiêu chí giảm tốc của xe sau chưa tính thời gian phản ứng của tài xế xe sau; `ttc_rear`, `decel_rear` chưa có nguồn.

## 4. Xác nhận

Đã sửa: Software Qualification Test Specification 1.35 mục 4.8, 5 (S8b c, f); Software Requirements Specification 1.14 (cột Kiểm chứng của PP-SWR-082, 085, 111, 113, 115); ADAS Function Specification 1.8 mục 6 bước 5; `S8b.anchors.xosc` (c: ELK; f: khe 40 m, `target_s_m` 25,353 m). Lần chạy nháp 2026-11-13 (cây làm việc chưa sạch, thư viện build từ `1f61551` có sửa đổi), seed 1, VP-0, đo trên chuyển động thật:

| | c | f |
|---|---|---|
| v_lat | 0,50 m/s | 0,50 m/s |
| TLC 0,8 s (t = 3,78 s) | khe 21,0 m, TTC 2,6 s | khe 41,0 m, TTC 5,1 s |
| Lốp chạm vạch (t = 4,58 s) | khe 14,6 m, TTC 1,8 s | khe 34,6 m, TTC 4,3 s |
| ELK REQUEST | chế độ A 4,68 s, B 4,91 s: sau lúc chạm vạch | không có |
| Lốp qua vạch 0,3 m | không xảy ra; DTLE −0,29 m | t = 5,18 s, khe 29,8 m, TTC 3,7 s |
| Kết quả | được chấm; đạt requirement trong phạm vi | đạt; không có REQUEST |

- REQUEST của c tới sau lúc lốp chạm vạch, nên cách B (chỉ xét tới lúc chạm vạch) bỏ sót ca này.
- Ngoài phạm vi: PP-SWR-088 ở c, khoảng cách ngang nhỏ nhất tới xe sau 0,22 m (PP-PR-029).
- Chưa có lần chạy chính thức.

| Run ID | Kết quả |
|---|---|
