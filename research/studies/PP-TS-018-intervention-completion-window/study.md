# PP-TS-018 Khoảng thời gian báo COMPLETED

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; V1 phía requirement đã áp dụng (`T_end_late` = 0,5 s, SRS 1.20); phía planner cần biến thể mới, plan chưa soạn |
| Mở ngày | 2026-11-14 |
| Liên quan | PP-PR-018, PP-PR-020, PP-PR-033; PP-TS-012; PP-SWR-032, 090 |

## 1. Câu hỏi

Planner cần báo COMPLETED sau khi xe đã ổn định theo ground truth. Sai số quan sát và lấy mẫu có thể làm tick báo lệch. Cần xác định độ muộn cho phép và kiểm các lần trả lái sớm theo PP-SWR-090.

## 2. Phương án

| ID | Phương án | Bằng chứng cần có |
|---|---|---|
| V0 | Giữ yêu cầu tick COMPLETED và ngoại suy v_y của PP-TS-012 V1 | Phân bố số tick báo sớm và báo muộn, theo từng thành phần của điều kiện giữ |
| V1 | Giữ PP-SWR-090. Cho PP-SWR-032 một cửa sổ báo muộn có giới hạn và dùng biên sai số phía planner | Độ muộn so với ground truth, thời lượng tăng thêm, DLC và DTLE trong lúc can thiệp và qua bàn giao EPS |

## 3. Cách đánh giá

- Ghi sai số có dấu giữa tick COMPLETED và tick ground truth thỏa toàn bộ điều kiện đủ `T_end_hold`. Ghi phần tử nào của DLC, heading, v_lat hoặc a_y thêm vào làm đổi tick.
- Dùng S4b, S6, S7, S12 và S13. Giữ ca thẳng làm đối chứng. Tách seed chỉnh và seed kiểm.
- Với V1, chốt giới hạn độ muộn, ngân sách tăng thời lượng và tiêu chí loại trước khi chạy. Bất kỳ can thiệp sớm hơn điều kiện ground truth đều trượt PP-SWR-090.

## 4. Đề xuất

Chốt tiêu chí trực tiếp trên chuyển động thật trước khi đổi code hay SRS. Sau đó so V0 và V1 cùng baseline T2, T7 và cùng calibration. PP-TS-012 tiếp tục theo dõi riêng chất lượng ngoại suy.

## 5. Quy định đã tra (2026-11-14)

| Văn bản | Mục | Nội dung liên quan |
|---|---|---|
| UN R79 | 2.3.4.2; 5.1.6.1.1; 5.1.6.1.2.1 | CSF can thiệp trong thời gian giới hạn; cảnh báo hình ít nhất 1 s hoặc suốt can thiệp; can thiệp quá 10 s (M1, N1) thì có cảnh báo âm thanh tới hết can thiệp |
| EU 2021/646 | Annex I Part 2, 3.6.4.1, 3.6.4.1.1 | Như R79: cảnh báo hình suốt can thiệp; quá 10 s thì cảnh báo âm thanh |
| Euro NCAP LSS v4.3 | 7.4.6 | Bài thử LKA, ELK mép đường kết thúc 2 s sau khi xe đạt lệch ngang lớn nhất và quay về làn; đây là cửa sổ đo, không phải yêu cầu cho hệ thống |
| Euro NCAP SA v10.4.1 | 4.3.2, 4.3.3 | Chỉ chấm DTLE và không va chạm |
| ISO 11270 | — | Trả phí, chưa đọc được |

Không văn bản nào quy định thời điểm kết thúc can thiệp hay dung sai tick báo COMPLETED. Ngưỡng duy nhất có nguồn liên quan tới độ dài can thiệp là mốc 10 s của cảnh báo âm thanh.

Người dùng chọn hướng V1 ngày 2026-11-14, sau khi xem bảng trên.

## 6. Kế hoạch nháp cho V1 (chưa khóa)

| Mục | Đề xuất | Cần chốt |
|---|---|---|
| Tiêu chí loại | PP-SWR-090 trên trạng thái thật: không báo COMPLETED trước khi điều kiện thật giữ đủ `T_end_hold`. DTLE (PP-SWR-085 đến 087) | — |
| PP-SWR-032 mới | Báo COMPLETED không muộn hơn `T_end_late` sau tick điều kiện thật giữ đủ | Giá trị `T_end_late` (nhóm tự thống nhất), chọn trước khi chạy; can thiệp dài nhất cộng `T_end_late` phải còn dưới 10 s |
| V1 phía planner | Ngưỡng kết thúc trừ một bội sai số ước lượng (`k_end_margin`·σ) để không báo sớm | Có thêm calibration parameter `k_end_margin` không, và dải quét |
| Xếp hạng | Số lần báo sớm (phải 0), phân bố độ muộn, thời lượng can thiệp tăng thêm | — |
| Bộ chạy | S4b, S6, S7, S12, S13 và ca thẳng đối chứng; seed chỉnh 1, 2; seed kiểm 3, 4 | — |

## 7. Áp dụng V1 phía requirement (2026-11-14)

Người dùng chốt `T_end_late` = 0,5 s (nhóm tự thống nhất). SRS 1.20 sửa PP-SWR-032; bên đánh giá chấm COMPLETED trong 0,5 s sau tick điều kiện thật giữ đủ `T_end_hold`. Đây là đổi ngưỡng sau khi đã thấy kết quả, theo hướng người dùng đã chọn ở §5.

Đo nháp seed 1, độ trễ COMPLETED so với tick điều kiện thật:

| Ca | Độ trễ |
|---|---|
| S4 a, c; S5 a; S13 a, c | 0 s |
| F01 a, b, c lúc LKA (S4a) | 0,65 s |
| F01 c lúc ELK (S5a) | 1,08 s |
| S12 b | Không báo COMPLETED (13 s) |

Phát hiện: với lane model nhiễu, v_lat và heading của planner lấy từ từng frame dao động quanh ngưỡng (S12 b: σ của v_lat ≈ 0,094 m/s so với `v_lat_end` = 0,1 m/s, chuỗi đạt dài nhất 20 chu kỳ). Nới requirement một mình không đủ. Cần biến thể phía planner cho điều kiện kết thúc (lọc thông thấp v_lat và heading, hoặc kết hợp yaw rate), kiểm cả PP-SWR-090. Bỏ hướng `k_end_margin` của §6: nó làm điều kiện chặt thêm.
