# PP-PR-038 ELK có REQUEST nhưng planner không có path can thiệp (F04, S16)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa cho F04 (PP-SWR-092, bên chấm); chờ xác nhận. S16 còn mở |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | Kết quả mong đợi của ca; liên quan PP-SWR-030, 047 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): F04 a, c trên S5a lúc ELK đang lái (4), S16 (2) |

## 1. Hiện tượng

Bên chấm báo "ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ". F04 a (vạch trái mất ngay) và c (độ tin vạch trái giảm về 0 trong 2 s) ở VP-2 đến VP-5.

## 2. Nguyên nhân

Chưa phân tích. Giả thuyết:
- `can_start` của ELK cần vạch phía đó đáng tin (`pp_intervention_line_trusted`). Mất vạch phía can thiệp thì planner không bắt đầu được.
- Nếu đúng, planner từ chối là hợp với văn bản. Câu hỏi là khối Chức năng ADAS chạy thử có nên gửi REQUEST khi vạch phía đó mất không, và ca có nên mong đợi can thiệp không.

Nguồn liên quan:

| Văn bản | Mục | Nội dung |
|---|---|---|
| EU 2021/646 | Recital (bản text dòng 59) | ELKS không bắt buộc hoạt động khi không có vạch |
| R79 | Annex 8, 3.3.4 | Chỉ thử khi không có vạch nếu hệ thống khai báo làm được |
| ADAS Function Specification | Bảng khả dụng | Biên kém tin thì UNAVAILABLE ở phía đó |
| PP-SWR-046 | — | Chỉ nói tiếp tục khi VehicleStateEstimate mất; chưa nói khi vạch mất giữa lúc ELK đang lái |

S16 (can thiệp lặp, 2 lần chạy) có thể là nguyên nhân khác: cần xem riêng.

**Phân tích log (2026-11-14,** [20261113-2341-suite-regression-1014d20](../runs/20261113-2341-suite-regression-1014d20/report.md), F04 a S5a, VP-4, seed 1**).**

| Thời điểm | Sự kiện |
|---|---|
| 5,702 s | ELK REQUEST trái, SOLID_LINE; planner ACTIVE. Cùng tick, L1 mất đến hết ca (F04 a, `elk_active`) |
| 8,152 s | COMPLETED. ELK đang lái khi vạch mất vẫn đi hết, DLC trái +0,64 m |
| 12,502 s | Xe trôi lần hai. ELK REQUEST trái, SOLID_LINE, trong khi L1 đã mất gần 7 s. Planner không bắt đầu: bên chấm báo lỗi |

- Giả thuyết đầu đúng: REQUEST tới khi vạch phía đó đã mất. Không phải trường hợp vạch mất giữa lúc ELK đang lái.
- Ca chạy chế độ B (Software Qualification Test Specification 4.8). Khối Chức năng ADAS chạy thử đọc lane model lý tưởng, không bị bơm lỗi, nên vẫn thấy L1. Theo code, ở chế độ A nó không gửi REQUEST này (`line_ok` cần L1 đủ tin); chưa kiểm bằng lần chạy.
- Planner không bắt đầu vì `pp_intervention_line_trusted` (Software Detailed Design mục 10). Software Requirements Specification không có requirement cho hành vi này: PP-SWR-047 chỉ nói tâm làn suy từ biên ngoài; ở đây tâm làn vẫn có từ R1 và bề rộng đã nhớ.
- Bên chấm đòi mọi REQUEST đúng phía phải có lần can thiệp và gắn PP-SWR-030. Không có requirement nào cho planner từ chối, nên bên chấm cũng không sai theo Software Requirements Specification hiện tại.

## 3. Cách sửa

Quyết định ngày 2026-11-14 (người dùng): theo văn bản và hệ thống trên xe bán ra, không đòi can thiệp về phía không nhận ra vạch.

| Nguồn | Nội dung |
|---|---|
| EU 2021/646 | Recital 6: ELKS không bắt buộc hoạt động khi không có vạch. Annex I 3.6.2: tránh rời làn qua vạch nhìn thấy được |
| Euro NCAP LSS 7.2.6 | Bài một vạch: xe trôi về phía còn vạch. Không có bài trôi về phía không có biên |
| Sổ tay Lexus GS 350, Mazda MX-30 2023, Kia | Chỉ nhận vạch một bên thì không hỗ trợ lái về phía không nhận ra vạch |

- Software Requirements Specification 1.18: thêm PP-SWR-092. LKA, hoặc ELK với lý do khác mép đường, không được bắt đầu về phía có vạch làn mình không là biên làn đủ tin. ELK mép đường vẫn theo PP-SWR-047.
- Planner không đổi: `pp_intervention_line_trusted` đã kiểm chặt hơn 092. Software Detailed Design T9 bước 4 trỏ về 092.
- Bên chấm (`eval/metrics.py`): REQUEST mà suốt khoảng đó vạch phía `side` trong lane model planner nhận không đủ tin thì không đòi path can thiệp. Thêm tiêu chí 092: số lần bắt đầu khi vạch phía đó không đủ tin. Software Qualification Test Specification 1.39, mục 8.1. Test `tests/eval/test_unseen_line_request.py`.
- Khối Chức năng ADAS chạy thử chế độ B giữ nguyên: nó vẫn gửi REQUEST này, đúng để kiểm 092.
- Lần chạy nháp: F04 a S5a VP-4, F04 c S5a VP-2 đạt; 092 được chấm và đạt.
- S16 (2 lần chạy) chưa phân tích, không thuộc B2.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
