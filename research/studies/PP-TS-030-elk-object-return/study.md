# PP-TS-030 Đường về tâm của ELK vì xe làn bên

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã khóa |
| Mở ngày | 2026-11-23 |
| Khóa ngày | 2026-11-23 |
| Quyết định ngày | — |
| Liên quan | PP-PR-077; PP-SWR-082, 085, 088, 094; PP-TS-026; Software Detailed Design T7 |

## 1. Câu hỏi

- Quyết định cần đưa ra: path ELK vì xe làn bên về tâm theo dạng nào để không vượt qua tâm (PP-SWR-094) mà vẫn giữ 0,3 m tới xe làn bên (PP-SWR-088).
- Vì sao cần: hồi quy 20261123-1254-suite-regression-54307f1 có 146 lượt PP-SWR-094 trượt ở S7, S8, S8b, S12, S21 sau khi mở phạm vi (PP-PR-077). Lượt nháp S8 theo protocol: path nhắm đúng tâm, nhưng về trong `T_return_object` = 2 s nên xe qua tâm với vận tốc ngang khoảng 0,6 m/s, controller trễ làm xe vượt tâm 0,14 m rồi quay lại; DLC phía can thiệp giảm 0,17 m.

## 2. Phương án

| ID | Phương án | Cách cài |
|---|---|---|
| V0 | Bản hiện tại: sau pha chặn đà, một quintic về tâm trong `T_return_object` = 2 s | — |
| V1 | Về hai tốc độ: quintic nhanh từ điểm chặn đà tới `d_return_object` = 0,2 m trước tâm trong 2 s, kết thúc với vận tốc 1,5·`d_return_object` / `T_return` hướng về tâm; rồi quintic chậm tới tâm trong `T_return`. Vận tốc và gia tốc liên tục ở điểm nối | `PP_RETURN_TWO_SPEED`; calibration `d_return_object` |
| V2 | Như V1, đoạn nhanh 1,5 s | Như V1, `T_return_object` = 1,5 |
| V3 | Đối chứng của PP-PR-077: một quintic, `T_return_object` = 4 s | Calibration |

- Đoạn nhanh dựng bằng quintic đảo thời gian: q từ (mid, −v_mid, 0) tới (điểm chặn đà, 0, 0); đường đi là q(T − t). Không cần solver mới.
- Không dừng ở điểm nối: dừng giữa chừng thì xe vượt điểm dừng rồi bị kéo lại, cùng kiểu trượt PP-SWR-094.
- Chỉ áp cho ELK vì xe ngược chiều hoặc xe đang vượt, có pha chặn đà. LKA, ELK vạch liền và mép đường không đổi.

## 3. Cách đánh giá

Khóa 2026-11-23, người phụ trách duyệt: [plan.yaml](plan.yaml), suite [PP-TS-030](../../../benchmark/suites/PP-TS-030.yaml).

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | Requirement trong phạm vi của suite, gồm PP-SWR-085, 088, 094, 111, 113, 115 và 100 đến 102 |
| Xếp hạng | Software Qualification Test Specification mục 9; target PP-SWR-082 (thời gian tới COMPLETED), ngang nhau trong 0,25 s |
| Bộ chỉnh | S7 a, b; S8 a, b; S8b c; S21 a; S12 c; S4 a, S5 a đối chứng; seed 1, 2 |
| Bộ kiểm | S7 c, d, e; S8 c, d, e; S8b d, e; S21 b, c, e; S12 d; S8b c VP-5; S7 a VP-5; S8 a VP-4; S4 c, S5 c; seed 3, 4 |
| Ngoài suite | Ca theo protocol Euro NCAP (S7, S8) không chạy được bằng `eval.study`; kiểm ở lần hồi quy sau khi chọn |

Lượt nháp trước khi viết suite (thư viện cây làm việc, seed 1; chỉ để dò, không dùng để quyết):

| Ca | V0: 094 / 088 [m] | V1 (0,2; 2 s) | V2 (0,2; 1,5 s) | V3 (4 s) |
|---|---|---|---|---|
| S8 protocol vượt có xi-nhan 72-5, VP-0 | 0,17 ✗ / 0,75 | 0,01 / 0,75 | 0,00 / 0,75 | 0,02 / 0,75 |
| S8b c VP-0 | 0,28 ✗ / 0,37 | 0,03 / 0,34 | 0,03 / 0,43 | 0,07 / 0,27 ✗ |
| S8b c VP-5 | 0,22 ✗ / 0,33 | 0,01 / 0,30 ✗ | 0,00 / 0,35 | 0,04 / 0,26 ✗ |
| S21 c VP-0 | 0,15 ✗ / 0,70 | 0,00 / 0,70 | 0,00 / 0,70 | 0,00 / 0,59 |

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

## 6. Đề xuất

## 7. Quyết định
