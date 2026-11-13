# PP-TS-016 Chức năng đang lái sau giới hạn 10 s của PP-SWR-083

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã quyết; đã đưa vào tài liệu và code, chờ build, unit test C và hồi quy |
| Mở ngày | 2026-11-13 |
| Khóa ngày | — |
| Quyết định ngày | 2026-11-13 |
| Liên quan | PP-SWR-030, 033, 034, 083; SG-02, SG-03; Software Detailed Design T7, T9; ADAS Function Specification mục 9, 10; Hazard Analysis and Risk Assessment mục 4 |

## 1. Câu hỏi

- Quyết định cần đưa ra: khi một lần LKA hoặc ELK tới giới hạn 10 s mà khối Chức năng ADAS vẫn giữ REQUEST, planner phải chọn chức năng đang lái nào.
- Vì sao cần: hai requirement mâu thuẫn, không planner nào đạt được cả hai.

| Requirement | Đòi hỏi |
|---|---|
| PP-SWR-083 (Safety, SG-01) | Lần can thiệp kết thúc, bằng COMPLETED hoặc bị hủy, trong ≤ 10 s |
| PP-SWR-030 (Safety, SG-01) | Chức năng đang lái là chức năng ưu tiên cao nhất đang ở REQUEST |

- Sau mốc 10 s, chức năng vừa hủy vẫn ở REQUEST. Bên chấm của PP-SWR-030 coi đó là chức năng phải lái, nên mỗi chu kỳ planner tuân PP-SWR-083 đều bị tính là sai.
- Lần chạy nháp `20261113-1218-full-ecf2f15` (cây làm việc chưa sạch, không trích làm bằng chứng), S12(d): LKA hủy ở mốc 10 s, REQUEST còn giữ thêm khoảng 1 s; PP-SWR-030 trượt 86 chu kỳ.
- Hành vi "hủy khi tới giới hạn" hiện chỉ có ở Software Detailed Design (T9 bước 4). Software Requirements Specification không nói sau khi hủy planner chọn gì.
- Nguồn của mốc, đối chiếu văn bản (2026-11-13):

| Văn bản | Nội dung | Hệ quả cho PP-SWR-083 |
|---|---|---|
| R79 2.3.4.2, 2.3.4.3 | CSF, ESF can thiệp "trong thời gian giới hạn"; không có con số | Chỉ đòi lần can thiệp có điểm kết thúc |
| R79 5.1.6.1.2.1 | CSF dựa trên vạch, dài hơn 10 s (M1, N1): cảnh báo âm thanh tới hết can thiệp | Coi can thiệp quá 10 s là hợp lệ, kèm cảnh báo |
| R79 Annex 8, 3.1.1.1 | Bài thử cố ý giữ can thiệp CSF quá 10 s để kiểm cảnh báo | Như trên |
| EU 2021/646 Annex I, 3.6.4.1.1 | Can thiệp ELKS dài hơn 10 s: cảnh báo âm thanh tới hết can thiệp | Như trên |
| EU 2021/646 Annex I, 5.3.2.2 (b); R79 Annex 6, 3.4.3.3 | Không mất hỗ trợ lái đột ngột; bỏ chức năng thì hạn chế nhiễu khi chuyển | Kết thúc phải êm, không cắt ngang |
| Euro NCAP LSS 7.4.6 | Bài thử LKA, ELK kết thúc 2 s sau khi xe đạt lệch lớn nhất | Không có giới hạn thời lượng |

- Bên trong bộ tài liệu: ADAS Function Specification mục 10 đã theo R79 (âm thanh tới hết can thiệp dài hơn 10 s). Hazard Analysis and Risk Assessment mục 4 ghi "≤ 10 s (R79)" và PP-SWR-083 ghi "dựa trên R79": đọc chưa đúng văn bản.
- Hủy ở 10 s khi xe còn trôi đi ngược SG-02 (không mất hỗ trợ lái đột ngột) và SG-03 (can thiệp đủ để giữ xe trong làn khi ELK được yêu cầu).

## 2. Phương án

| ID | Phương án | Thay đổi | Hệ quả |
|---|---|---|---|
| V0 | Giữ nguyên | — | Mâu thuẫn còn; ca can thiệp chưa xong ở 10 s luôn trượt một trong hai requirement |
| V1 | Đối xử như COMPLETED. Thêm requirement theo mẫu PP-SWR-033 và 034: khi lần can thiệp bị hủy vì giới hạn của PP-SWR-083, planner chọn theo PP-SWR-030 trong các chức năng còn ở REQUEST, không tính chức năng vừa hủy; không bắt đầu lần mới cho chức năng đó cho tới khi state rời REQUEST rồi quay lại | Software Requirements Specification: hai dòng mới hoặc mở rộng 033, 034. Bên chấm PP-SWR-030: chức năng hết 10 s tính từ REQUEST được coi như đã kết thúc | Nhất quán với cách xử lý COMPLETED đã có. Bên chấm dùng thời điểm nhận REQUEST, thấy được qua interface |
| V2 | Đẩy giới hạn sang khối Chức năng ADAS: khối đó rút REQUEST ở mốc 10 s; planner chỉ theo REQUEST | ADAS Function Specification mục 9; khối chạy thử; PP-SWR-083 đổi thành yêu cầu khi REQUEST rút | Planner phụ thuộc đội khác cho một safety goal; mất tự bảo vệ khi khối ADAS lỗi |
| V3 | Bỏ việc kết thúc trong 10 s, chỉ giữ cảnh báo theo R79 | PP-SWR-083 | Không còn mâu thuẫn, nhưng nới một requirement Safety; cần lý do an toàn, không chỉ vì ca trượt |
| V4 | Theo văn bản: bỏ việc buộc kết thúc ở 10 s. Lần can thiệp kết thúc bằng COMPLETED, bằng các điều kiện hủy đã có, hoặc khi REQUEST rời; quá 10 s thì cảnh báo âm thanh tới hết can thiệp (ADAS Function Specification mục 10). Lý do "thời gian giới hạn" của R79 2.3.4.2 chứng minh bằng các điều kiện kết thúc, không bằng một mốc cắt | PP-SWR-083 obsolete hoặc viết lại; giới hạn của `T_lka`, `T_elk` (SRS mục 7); Software Architectural Design, Software Detailed Design (T7, T9); Hazard Analysis and Risk Assessment mục 4; planner; bên chấm 083 | Khớp R79, EU 2021/646 và SG-02, SG-03. Đổi nhiều tài liệu; lập luận dựa trên văn bản, không trên ca trượt |

## 3. Cách đánh giá

- Tiêu chí loại: không còn cặp requirement không thể cùng đạt; không nới requirement Safety chỉ để ca qua.
- Không chạy so sánh: đây là câu hỏi requirement. Sau quyết định, chạy lại cả bộ.
- Lưu ý độc lập: V1 và V3 làm bớt trượt ở các ca đã thấy kết quả. Lý do chọn phải đứng được mà không dựa vào kết quả đó.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

## 6. Đề xuất

V4 (đổi từ V1 sau khi đối chiếu văn bản, 2026-11-13). Lý do:
- R79 và EU 2021/646 đều coi can thiệp quá 10 s là hợp lệ và chỉ đòi cảnh báo âm thanh tới hết can thiệp; mốc cắt 10 s không có nguồn.
- Cắt ở 10 s khi xe còn trôi đi ngược SG-02, SG-03 của chính bộ tài liệu.
- V1 giữ một requirement không có nguồn và vẫn để xe mất hỗ trợ giữa chừng. V2 có cùng vấn đề, chỉ chuyển sang khối khác. V3 là V4 khi chưa có lập luận văn bản.
- Lập luận không dựa vào kết quả S12(d): mâu thuẫn và nguồn đều thấy trên giấy.

## 7. Quyết định

- Người quyết, ngày: thongbui, 2026-11-13
- Chọn: V4
- Lý do: như mục 6; bám R79 5.1.6.1.2.1, Annex 8 3.1.1.1 và EU 2021/646 Annex I 3.6.4.1.1, giữ SG-02, SG-03
- Đưa vào: Software Requirements Specification (PP-SWR-083 obsolete); Hazard Analysis and Risk Assessment mục 4; Software Architectural Design; Software Detailed Design T7, T9 và mục 15 (`intervention_T_max`); Software Qualification Test Specification 8.1; Mentor Report; planner (`arbitration.c`, `intervention.c`); bên chấm (bỏ tiêu chí 083)
- Hồi quy: chưa có run ID
