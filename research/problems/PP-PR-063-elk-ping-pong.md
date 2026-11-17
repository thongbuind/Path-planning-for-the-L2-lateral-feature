# PP-PR-063 ELK lặp lại nhiều lần: xe vọt sang phía đối diện rồi ELK kích hoạt lại

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; đã mô tả hiện tượng, nguyên nhân chưa phân tích hết |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | PP-SWR-085, 086, 091; PP-SWR-035; PP-SWR-039 (S6 b); PP-SWR-090 (S5 c) |
| Tái hiện | [20261117-1217-suite-regression-d2e7d27](../runs/20261117-1217-suite-regression-d2e7d27/report.md): S13 b ELK VP-3, S6 b VP-4, VP-5, S5 c VP-5. Lượt nháp 2026-11-17, seed 1, cùng file ca của lần hồi quy |

## 1. Hiện tượng

Trong các ca ELK ở profile VP-3, VP-4, VP-5 với tốc độ trôi 0,6 m/s, ELK kích hoạt lặp lại thay vì một lần.

| Ca | Số lần ELK kích hoạt, planner c56f0bf | Số lần ELK, planner d2e7d27 | DLC hai phía nhỏ nhất trong log [m] (c56f0bf / d2e7d27) |
|---|---|---|---|
| S6 b VP-4 | 3 | 5 | −7,4 / −10,3 |
| S6 b VP-5 | 5 | 6 | −6,8 / −8,2 |
| S5 c VP-4 | 4 | 4 | −6,5 / −6,5 |
| S5 a, S5 c VP-0 đến VP-3, VP-5; S6 b VP-0 đến VP-3 | 2 | 2 | 0,04 đến 0,13 |

- Với VP-0 đến VP-3, thường 2 lần ELK, xe giữ trong làn.
- Ở các ca lặp, mỗi lần ELK hoạt động khoảng 1 s, rồi `active_function = NONE`, rồi ELK lại sau khoảng 0,65 s; lặp 4 đến 6 lần trong 7 s.
- Chuyển ELK → NONE xảy ra với `elk_phase = NONE`, tức yêu cầu rời REQUEST, không phải COMPLETED. Lúc đó tốc độ ngang thật của xe còn khoảng 0,47 m/s về phía làn, lớn hơn `v_lat_end` = 0,1 m/s.
- Xe tiếp tục qua phía đối diện (DLC phía đó còn 0,09 m lúc 2,25 s sau lần đầu) và lần ELK sau bắt đầu ở phía đó.
- DLC âm vài mét ở cuối log chưa được kiểm là xe thật sự ra khỏi đường hay hình học đường kết thúc; bên chấm chỉ chấm DTLE trong từng khoảng ELK, nên phần này không tính vào kết luận.

## 2. Nguyên nhân

Chưa phân tích hết. Đã biết:

- Kết quả của PP-SWR-085, 086, 091 ở các ca này khác nhau giữa hai planner (S6 b VP-5: DTLE 0,018 → −0,36 m) dù lần ELK đầu gần như giống nhau (đỉnh lệch −0,414 và −0,402 m; khoảng cách tới mép 0,109 và 0,119 m). Chênh lệch nằm ở lần lặp thứ hai trở đi, nên kết quả nhạy với chi tiết nhỏ, không phải hiệu quả có hệ thống của thay đổi ở chu kỳ đầu (PP-PR-062).
- Yêu cầu ELK bị rút ở khoảng 1 s là hành vi của khối Chức năng ADAS chạy thử (ADAS Function Specification mục 6, PP-TS-010), không phải của path planner. Sau đó không có chức năng nào lái và mô hình tài xế giữ tốc độ ngang.
- Chưa rõ vì sao chỉ VP-3, VP-4, VP-5; trong các ca pairwise, bề rộng làn và tốc độ trôi cũng khác (ví dụ S5 a VP-4: bề rộng 3,58 m, 0,58 m/s).

## 3. Cách sửa

Chờ phân tích. Hướng cần xem:

- Điều kiện rút ELK của khối Chức năng ADAS chạy thử: có khớp với điều kiện kết thúc của planner (PP-SWR-032) không.
- Đối chiếu ca với ADAS Function Specification: trôi một lần, hay kịch bản có chủ ý lặp (S16).
- Nếu là hành vi của khối chạy thử, sửa ở phía đánh giá (PP-TS-008) và chạy lại.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
