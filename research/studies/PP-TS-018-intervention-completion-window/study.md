# PP-TS-018 Khoảng thời gian báo COMPLETED

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, chờ chốt tiêu chí |
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
