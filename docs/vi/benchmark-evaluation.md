# Benchmark và Evaluation path planner

Tài liệu này mô tả **môi trường giả lập và cách chấm path planner của G1**. Báo cáo quy định kịch bản, lỗi bơm vào, chỉ số, ngưỡng đạt và cách so sánh các kỹ thuật. Đề bài yêu cầu so sánh các kỹ thuật về độ mượt, số lần vượt giới hạn, độ vượt ra khỏi làn, phản ứng với lỗi bơm vào, và thời gian tính mỗi chu kỳ.

**Liên hệ với hai tài liệu khác.**

| Tài liệu | Quan hệ với tài liệu này |
|---|---|
| Thiết kế tính năng Path Planner | Cho các **yêu cầu phải đạt**: ngân sách a_y và jerk, ngưỡng liên tục, điều kiện kết thúc, phản ứng phải có khi input lỗi. Benchmark chỉ lấy phần yêu cầu (làm gì), không lấy cơ chế bên trong planner (làm thế nào). Mỗi yêu cầu có một chỉ số ở mục 5 |
| Chức năng ADAS | Cho **lúc kích hoạt**. Benchmark dùng khối ADAS giả: chế độ B (dữ liệu thật của kịch bản) để chấm G1, chế độ A (message có nhiễu) để thử cả chuỗi. Benchmark cũng đo các chỉ số cần cho việc chốt ngưỡng TLC |

## 0. Công tâm, và khác gì test chức năng

**Benchmark khác test chức năng.**

| | Test chức năng | Benchmark và Evaluation |
|---|---|---|
| Hỏi gì | Một phiên bản planner có đạt từng yêu cầu không (pass hoặc fail) | Các kỹ thuật so với nhau thế nào, trên cùng điều kiện |
| Khi nào chạy | Liên tục trong lúc phát triển, mỗi lần sửa code | Khi đã có các phương án để so sánh, và khi chốt kết quả cho báo cáo |
| Ai dùng kết quả | Người viết code, để sửa lỗi | Người chọn kỹ thuật, mentor, người đọc báo cáo |
| Được chỉnh theo kết quả không | Được: test fail thì sửa code | Không được chỉnh kịch bản hay ngưỡng sau khi đã thấy kết quả |

**Quy tắc công tâm.**

| Quy tắc | Nội dung | Trạng thái |
|---|---|---|
| Định trước | Kịch bản, seed, chỉ số, ngưỡng đạt và thứ tự xếp hạng được chốt **trước** khi chạy bất kỳ kỹ thuật nào. Muốn đổi thì ghi lại lý do, và chạy lại cho mọi kỹ thuật | đề xuất |
| Cùng điều kiện | Mọi kỹ thuật dùng cùng kịch bản, cùng seed, cùng controller chạy thử và ACC chạy thử đã cố định hệ số, cùng khối ADAS giả ở chế độ B | đã chốt |
| Chỉnh tham số công bằng | Mỗi kỹ thuật được chỉnh tham số với cùng một ngân sách công sức và trên **bộ kịch bản chỉnh**. Điểm chính thức chấm trên **bộ kịch bản kiểm**: seed khác, và một số kịch bản không dùng lúc chỉnh. Như vậy không kỹ thuật nào được "học thuộc" bộ chấm | đề xuất |
| Báo cáo đủ | Báo cáo mọi kịch bản và mọi seed, kể cả ca xấu nhất; không chỉ chọn ca đẹp | đề xuất |
| Tái lập được | Mỗi kết quả kèm phiên bản code, file kịch bản và seed; chạy lại phải ra đúng số | đã chốt |
| Không đối phó bài thi | Planner được thiết kế tổng quát. Kịch bản và lỗi mới chỉ thêm ở phía đánh giá; không thêm vào planner một nhánh xử lý chỉ để qua một kịch bản cụ thể. Ca nào trượt thì sửa cơ chế chung, rồi chạy lại cả bộ | đã chốt |
| Độc lập với planner | Benchmark và planner phát triển độc lập, như kiểm thử hộp đen dựa trên yêu cầu. Benchmark chỉ quan sát planner qua interface (input, output, thời gian tính), không đọc biến nội bộ, không dựa vào cơ chế hay ngưỡng bên trong planner, không chỉnh cấu hình của planner. Thế nào là đạt thì suy ra từ yêu cầu (đề bài, quy định, kỳ vọng của người lái), ghi bằng thứ quan sát được. Simulator và mức lỗi do bên đánh giá đặt từ dữ liệu thật hoặc tài liệu. Chiều ngược lại, planner không đọc tên kịch bản, ground truth, seed hay cấu hình của benchmark | đã chốt |
| Hướng về người dùng và an toàn | Thứ tự ưu tiên khi chọn chỉ số và xếp hạng: an toàn (không va chạm, không ra khỏi làn, không can thiệp sai hướng), rồi đúng quy định, rồi cảm nhận của người lái (êm, không rung lắc, không can thiệp thừa, dễ đoán, nhường khi tài xế giành lái), sau cùng là hiệu năng. Đo trên chuyển động thật của xe so với làn thật trong simulator, không đo trên ước lượng của planner | đề xuất |

## 1. Bộ tối thiểu theo đề bài

Đề bài yêu cầu prototype chạy ít nhất bộ sau. Đây là phần bắt buộc, phải có trước mọi mở rộng.

| Kịch bản | Không lỗi | Nhiễu | c0 jump | Mất một vạch | c2 sai |
|---|---|---|---|---|---|
| HWA bám cua | có | có | có | có | có |
| LKA trôi làn | có | có | có | có | có |
| ELK có xe ngược chiều | có | có | có | có | có |

Tức là 3 kịch bản nhân 5 trạng thái lỗi, mỗi ô cho ra path của từng kỹ thuật, kèm biểu đồ.

## 2. Cách chạy {#benchmark-run}

Cấu hình các khối dùng chung xem ở [Thiết kế môi trường giả lập](report.html?doc=benchmark-evaluation&lang=vi#simulation-design).

| Mục | Quy định | Trạng thái |
|---|---|---|
| Chế độ chấm điểm | Chạy tất định trong một tiến trình, bước 1 ms, nhanh nhất có thể theo đồng hồ mô phỏng. Cùng seed thì cùng kết quả. Chỉ số chính thức lấy từ chế độ này | đã chốt |
| Chế độ thời gian thực | Mỗi ECU chạy một tiến trình theo đồng hồ thật và dùng socket thật. Bus CAN ảo dùng `udp_multicast` của `python-can`, chạy được trên macOS. Chế độ này chỉ dùng để kiểm tra tích hợp vì kết quả không tất định | đã chốt |
| Vòng hở | Planner nhận dữ liệu của kịch bản, xe đi theo quỹ đạo kịch bản định sẵn, không theo path. Đo chất lượng path thuần tuý | đã chốt |
| Vòng kín | Path qua controller và EPS chạy thử rồi vào mô hình xe. Controller cố định cho mọi kỹ thuật, để không che lỗi của planner | đã chốt |
| Độ mượt luôn tính trên path | Cả ở vòng kín, chỉ số độ mượt tính trên output của planner. Vòng kín thêm các chỉ số về chuyển động thật của xe | đã chốt |
| Khối ADAS giả | Chế độ B để chấm G1; chế độ A để báo cáo độ bền của cả chuỗi. Log ghi cả TLC đo được lẫn TLC thật | đã chốt |
| Kịch bản không nhiễu | Mỗi kịch bản có một bản không nhiễu làm mốc, để tách lỗi do thuật toán với lỗi do nhiễu | đã chốt |
| IMU mặc định | Kịch bản chính dùng IMU sạch, vì IMU đến planner được coi là đã lọc. Nhiễu và bias IMU là lỗi bơm vào (mục 4) | mentor |
| Tần số | Planner và khối ADAS giả chạy 40 Hz; tín hiệu xe theo signal list (IMU, góc lái 100 Hz; tốc độ 50 Hz) | mentor |
| Seed | Một seed chính mỗi lần chạy, sinh luồng ngẫu nhiên riêng cho từng kênh và cảm biến. 10 seed cho mỗi ô có nhiễu | đã chốt |
| Log | Một file MCAP mỗi lần chạy, ghi mọi message kèm stamp và counter, đủ để chạy lại; xem bằng Foxglove | đã chốt |
| Tài nguyên máy | Máy 8 GB RAM: chạy từng lô nhỏ, hỏi trước khi chạy lô lớn | đã chốt |

### 2.1 Chạy lại log thật (vòng hở)

Đề bài yêu cầu planner chạy được trên output thật, không chỉ trên dữ liệu mô phỏng sạch. Nếu mentor cung cấp log của xe, benchmark có thêm một phần chạy lại log. Phần này **chỉ là tham chiếu**, không dùng để xếp hạng chính, vì ground truth (gt) của log rất hạn chế.

| Mục | Nội dung | Trạng thái |
|---|---|---|
| Dữ liệu | Tín hiệu ego trên xe luôn có (signal list nhóm Motion). Cột gt có ít dữ liệu, chỉ dùng làm tham chiếu | mentor |
| Cách chạy | Vòng hở: planner đọc log, xe đi theo log, không theo path. Không chạy vòng kín được vì không điều khiển được xe trong log | đề xuất |
| Đầu vào cần thêm | Log phải có output của camera (lane model, vật thể). Signal list hiện mới là nhóm Motion; cần hỏi mentor log có phần camera không | cần chốt |

**Chấm được gì khi gt hạn chế.**

| Chỉ số | Cần gt không | Cách làm | Trạng thái |
|---|---|---|---|
| Độ mượt, giới hạn a_y và jerk, ngưỡng liên tục, thời gian tính | Không | Như mục 5.2, 5.3, 5.4, 5.7, tính trên path | đề xuất |
| Path có rung vì nhiễu thật không | Không | So jerk và tốc độ quay vô lăng gợi ý trên log thật với cùng chỉ số trên kịch bản mô phỏng tương tự | đề xuất |
| Tự nhất quán của bù trễ | Không | Dời lane model của frame trước tới thời điểm frame sau bằng ego-motion, so với lane model đo ở frame sau. Lệch lớn là dấu hiệu bù trễ sai hoặc trễ thật khác giả định | đề xuất |
| v_lat và TLC | Có, cột "Ego lateral speed relative to the line" | So v_lat tính từ input với v_lat của gt | đề xuất |
| Độ trễ của yaw rate đã lọc | Có một phần | Tương quan chéo giữa bản thô và bản đã lọc; kiểm thêm bằng "Ego yaw rate" của gt (tài liệu Thiết kế tính năng Path Planner, mục 3) | đề xuất |
| Ego-motion | Có, vị trí và yaw của gt | Sai số Δx, Δy, Δψ trong 0,5 s; dùng để kiểm giả định T_coast | đề xuất |
| Tình huống có xe khác | Có, cột Target | Khoảng cách ngang, TTC tới xe kia; dùng cho ELK vật thể | đề xuất |

**Không chấm được:** lấn vạch (DTLE) và độ lệch so với tâm làn thật, vì gt không có hình học làn; mọi chỉ số vòng kín. Có cột steering robot và một xe target, nên log có thể là dữ liệu thử trên sân thử; nếu đúng vậy, các đoạn log ứng với S4–S8 nên được ưu tiên.

## 3. Danh mục kịch bản {#benchmark-scenarios}

Mỗi kịch bản có một file cấu hình và seed. Cách tạo trôi làn được mô tả ở mục [mô hình xe](report.html?doc=benchmark-evaluation&lang=vi#sim-vehicle).

Thông số thử theo Euro NCAP LSS v4.3 khi có thể: xe thử chạy 72 km/h; trôi bằng một cung tròn R = 1200 m rồi giữ v_lat không đổi; v_lat 0,2–0,6 m/s, bước 0,1 m/s. Thêm 90 km/h để khớp các ví dụ trong tài liệu, vì cao tốc Việt Nam giới hạn tối đa 120 km/h.

**Mỗi loại kịch bản có 3–5 biến thể**, để thấy planner thay đổi thế nào khi một thông số đổi, không chỉ đạt hay trượt ở một điểm. Biến thể được chọn để đi từ dễ tới khó, và có ít nhất một biến thể nằm ngay ranh giới của một quy tắc. Các kịch bản có hai phía (trái, phải) chạy cả hai phía cho mọi biến thể. Bề rộng làn mặc định 3,5 m.

Cột Yêu cầu được sinh bằng `python3 tools/trace.py --write` từ cột Kiểm chứng của tài liệu Yêu cầu phần mềm Path Planner; không sửa tay. Yêu cầu áp cho mọi kịch bản hoặc mọi lỗi không ghi lặp ở từng dòng.

| # | Kịch bản | Biến thể | Đo gì | Yêu cầu | Trạng thái |
|---|---|---|---|---|---|
| S1 | HWA bám cua | 90 km/h, vào cua bằng clothoid. a) R = 1000 m (a_y do cua khoảng 0,6 m/s²); b) R = 500 m (1,25); c) R = 250 m (2,5, chạm aysmax); d) cua chữ S, R = 500 m rồi đổi chiều; e) 130 km/h, R = 1000 m (1,3) | Bám tâm làn, độ mượt, giới hạn a_y | PP-SWR-001, 003, 004, 008 (a, b, d, e), 050 (a, b, d, e), 051 (vòng kín) | đề bài |
| S1b | HWA cua gắt hơn aysmax | a) 90 km/h, R = 200 m (a_y khoảng 3,1 m/s²); b) 90 km/h, R = 150 m (4,2); c) 110 km/h, R = 300 m (3,1); d) R = 200 m ngay sau đỉnh dốc, camera chỉ thấy 40 m | Path giữ trong aysmax, bật lateral_limit_reached, không thả đột ngột | PP-SWR-001, 005, 006, 007 | đề xuất |
| S2 | HWA bật khi xe lệch tâm | a) lệch 0,2 m, góc 0°; b) 0,4 m, 1°; c) 0,5 m, 2° hướng ra ngoài; d) 0,4 m trong cua R = 500 m; e) 0,5 m ở 130 km/h | Đoạn đưa xe về giữa: a_y thêm vào ≤ 0,5 m/s², không nhảy bậc | PP-SWR-002, 052, 053 | đề xuất |
| S3 | HWA dời tâm khi mình vượt xe tải ở làn bên | Xe tải rộng 2,5 m. a) chậm hơn mình 5 m/s; b) chậm hơn 2 m/s (ngang hàng lâu hơn); c) chậm hơn 10 m/s; d) xe tải đi sát vạch, cách vạch 0,1 m; e) xe tải lấn vạch 0,3 m vào làn mình | Bắt đầu dời sớm theo TTC, offset ≤ 0,3 m, trả về sau khi qua | PP-SWR-002, 055, 058, 059 | đề bài |
| S3b | HWA khi xe lớn vượt mình từ phía sau, bên kia có hoặc không có xe, làn hẹp | Xe tải nhanh hơn mình 5 m/s, đi từ phía sau lên; chỉ radar góc thấy trước khi tới ngang hàng. a) bên kia trống, làn 3,5 m; b) bên kia có xe con đi song song; c) bên kia có xe tải; d) như a, làn 3,0 m; e) như c, làn 2,75 m | Dời muộn nhưng vẫn êm; không đẩy xe về phía xe bên kia; DLC ≥ 0,3 m cả hai phía | PP-SWR-055, 056, 057 | mentor |
| S4 | LKA trôi làn trên đường thẳng | a) 72 km/h, vạch đứt, v_lat 0,2 m/s; b) 72 km/h, vạch liền, 0,4; c) 90 km/h, 0,6; d) trôi do gió ngang; e) trôi do đường nghiêng ngang | DTLE, độ êm, điều kiện kết thúc | PP-SWR-032, 080, 081, 083, 084, 085, 086 (vòng kín), 087 (vòng kín), 090, 110, 112, 114 | đề bài, Euro NCAP |
| S4b | LKA trôi làn trong cua | 90 km/h. a) R = 1000 m, trôi ra phía ngoài cua 0,3 m/s; b) R = 500 m, ra ngoài 0,3; c) R = 500 m, vào phía trong 0,3; d) R = 250 m, ra ngoài 0,3: a_y do cua đã 2,5 m/s², ngân sách LKA tổng 3,0 nên chỉ còn 0,5 m/s² để kéo về; e) trôi ra ngoài ngay đoạn vào cua (clothoid) | DTLE; a_y tổng trong ngân sách; lateral_limit_reached khi hết ngân sách; trôi ra ngoài so với trôi vào trong | PP-SWR-083, 085, 110, 112, 114 | mentor |
| S5 | ELK vạch liền, LKA tắt | a) 72 km/h, v_lat 0,2; b) 0,4; c) 0,6; d) 90 km/h, 0,4; e) vạch kép | DTLE ≥ −0,3 m | PP-SWR-032, 080, 082, 083, 085, 086 (vòng kín), 090, 111, 113, 115 | Euro NCAP |
| S6 | ELK mép đường | Phía hành khách. a) chỉ có mép đường, v_lat 0,2; b) chỉ có mép đường, 0,6; c) vạch giữa đứt và không có vạch sát mép; d) mép đường là rào chắn; e) 90 km/h, 0,4 | DTLE ≥ −0,1 m | PP-SWR-080, 082, 083, 085, 086 (vòng kín), 111, 113, 115 | Euro NCAP |
| S6b | Làn mở rộng | Mép đường hoặc vạch tự nhiên rộng ra; xe đang bật HWA. a) làn dừng khẩn cấp rộng dần 1,5 m trên 100 m, phía phải; b) tách nhánh lối ra, vạch phải đi theo nhánh; c) thêm làn bên trái; d) mở rộng trong cua R = 500 m; e) mở rộng đúng lúc HWA đang dời tâm vì có xe tải phía bên kia | Path không dịch về phía mở rộng: lệch ngang so với tâm làn thật ≤ 0,1 m | PP-SWR-060 | mentor |
| S7 | ELK xe ngược chiều | Xe kia ở làn bên, cách mép trong vạch giữa 1,5 m, hai xe gặp nhau với 10 % chồng lấn bề rộng nếu không can thiệp; phía tài xế. a) cả hai 72 km/h, v_lat 0,2; b) 0,4; c) 0,6; d) xe kia 90 km/h; e) trong cua R = 500 m | Không va chạm | PP-SWR-082, 083, 085, 088 (vòng kín), 111, 113, 115 | đề bài, Euro NCAP |
| S8 | ELK xe đang vượt | a) xe kia 80 km/h so với mình 72 km/h, trôi không chủ đích 0,2 m/s; b) cùng 72 km/h, trôi 0,4; c) chuyển làn có xi-nhan (bật 1,0 ± 0,5 s trước lúc đánh lái), 0,5 m/s; d) như c, 0,7 m/s; e) xe kia 100 km/h, trôi 0,4 | Không va chạm, kể cả khi có xi-nhan | PP-SWR-082, 083, 085, 088 (vòng kín), 089, 111, 113, 115 | Euro NCAP |
| S8b | Chuyển làn có xi-nhan, xe sau ở nhiều khoảng cách | Gia tốc xe sau cần là (chênh tốc)² / (2 × khoảng cách). a) cách 20 m, nhanh hơn 2,2 m/s: cần 0,12 m/s²; b) 10 m, 2,2 m/s: 0,24 m/s²; c) 20 m, 8 m/s: 1,6 m/s², TTC 2,5 s; d) 12 m, 10 m/s: TTC 1,2 s; e) 30 m, 14 m/s: cần 3,3 m/s², TTC 2,1 s | a, b, c: **không được can thiệp**, chỉ cảnh báo. d (TTC ≤ 1,5 s) và e (cần hơn 3 m/s²): phải can thiệp theo quy tắc mục 3.2, bước 6 của tài liệu Chức năng ADAS | PP-SWR-082 (d, e), 083 (d, e), 085 (d, e), 111 (d, e), 113 (d, e), 115 (d, e) | đề xuất |
| S8c | Bẻ lái gấp tránh vật, làn bên có xe | Không xi-nhan. a) v_lat 1,2 m/s; b) 1,5 m/s; c) bẻ gấp rồi trả lái ngay (né ổ gà); d) bẻ gấp khi đang có LKA can thiệp | Không can thiệp, chỉ cảnh báo; nếu đang can thiệp thì nhả êm | PP-SWR-031 (d), 036 (d), 037 (d) | đề xuất |
| S9 | Chuyển giữa chức năng | a) LKA lên ELK giữa chừng; b) ELK xong về HWA; c) HWA bị tài xế ghi đè rồi buông; d) yêu cầu bị hủy vì xi-nhan giữa lúc can thiệp; e) tài xế tắt HWA giữa cua R = 500 m | Không nhảy bậc ở mọi lần chuyển | PP-SWR-030 (a), 031, 033 (b), 036 (d), 037 (d), 038, 039 (c), 040 (c) | đề bài |
| S10 | Đi gần vạch mà không trôi | a) DLC 0,2 m, v_lat gần 0; b) DLC 0,4 m; c) cắt cua ở R = 500 m; d) tài xế đi lệch về một bên khi có xe tải; e) như a, ban đêm, khối ADAS giả ở chế độ A | **Không được can thiệp**. Đo số lần kích hoạt thừa, cần cho việc chốt ngưỡng TLC | | đề xuất |
| S11 | Tắc đường trên cao tốc | HWA bật. a) stop and go 0–30 km/h; b) 0–60 km/h; c) dừng hẳn 10 s rồi chạy lại; d) xe khác cắt vào ở 20 km/h | HWA vẫn giữ làn; LKA, ELK không khả dụng | PP-SWR-050, 054 | đề xuất |
| S12 | Trời mưa | μ = 0,5 cho mô hình xe, cùng với nhiễu camera ban đêm hoặc khi mưa và nhiễu perception gấp 1,5 lần. a) chạy lại S1c; b) S4c; c) S7c; d) S4b-d | Biên an toàn khi bám đường kém | PP-SWR-001 (a) | đã chốt |
| S13 | EPS chậm | Chạy lại S4c và S5c với trễ EPS a) 75 ms; b) 100 ms; c) 150 ms, thay cho 50 ms | Planner còn ổn khi bộ chấp hành chậm | PP-SWR-091 (a, b, vòng kín) | đã chốt |
| S14 | Ngang và dọc trao đổi ràng buộc | Chạy hai lần: ACC chạy thử đọc LateralLimits (thiết kế chính) và bỏ qua LateralLimits (để so sánh). a) cua gắt S1b-a; b) xe khác lấn 0,5 m vào làn mình; c) cả hai cùng lúc; d) mất LongitudinalPlan giữa cua | So sánh hai cách trên cùng chỉ số: DLC nhỏ nhất, khoảng cách tới xe kia, a_y, mức giảm tốc. Không giả định trước cách nào tốt hơn | PP-SWR-009, 150, 151, 152, 153, 154 (d), 155 (d) | đã chốt |
| S15 | Dời tâm khi hai bên đều có vật | a) xe tải hai bên; b) xe tải một bên, rào chắn bên kia; c) xe tải một bên, xe con bên kia; d) xe tải hai bên, làn 3,0 m; e) rào chắn hai bên (công trường) | Không dời về phía vật gần hơn; luôn giữ DLC ≥ 0,3 m cả hai phía; ghi khoảng cách ngang nhỏ nhất tới vật mỗi bên | PP-SWR-055, 056, 057 | đề xuất |
| S16 | Can thiệp lặp | FunctionRequests do khối ADAS giả gửi theo chuỗi định trước. a) LKA báo COMPLETED, khối ADAS giữ REQUEST thêm 1 s; b) như a, rồi REQUEST rời 0,2 s và quay lại khi xe trôi lần nữa; c) trôi qua lại ba lần, v_lat 0,4 m/s, cách nhau 2 s; d) như c, với ELK vạch liền; e) lần can thiệp thứ hai bắt đầu 0,2 s sau COMPLETED | a: không có lần can thiệp mới khi REQUEST chưa rời; b–e: mỗi lần can thiệp đạt cùng giới hạn như lần đầu (DTLE, a_y, jerk, thời lượng) | PP-SWR-034 (a, b), 035 (c, d, e) | đề xuất |
| S17 | Tài xế chuyển làn khi HWA bật | Tài xế bật xi-nhan, ghi đè và đưa xe sang làn bên; Lane Model đổi sang làn mới khi xe qua vạch và bật cờ chuyển làn. a) đường thẳng, 90 km/h, chuyển trong 4 s; b) chuyển nhanh trong 2,5 s; c) trong cua R = 500 m; d) chuyển hai lần liên tiếp; e) cờ chuyển làn đến trễ một frame so với lúc Lane Model đổi làn | Path liên tục ở mọi chu kỳ quanh lúc đổi làn; trong lúc ghi đè, path bám vị trí xe; sau khi tài xế buông, HWA về tâm làn mới | PP-SWR-039, 040, 061 | đề xuất |

Bề rộng làn hẹp 3,0 m và 2,75 m là số tự chọn, chưa có nguồn; cần đối chiếu với tiêu chuẩn đường của Việt Nam (mục 8).

## 4. Danh mục lỗi bơm vào {#benchmark-faults}

Mỗi lỗi được bơm ở ba thời điểm: khi HWA đang chạy ổn định, ngay lúc kích hoạt LKA hoặc ELK, và giữa lúc can thiệp. Mỗi lỗi cũng có 3–5 mức hoặc dạng.

Mã lỗi cố định: không đánh số lại, không dùng lại. Cột Yêu cầu được sinh bằng `python3 tools/trace.py --write` từ cột Kiểm chứng của tài liệu Yêu cầu phần mềm Path Planner; không sửa tay. Yêu cầu áp cho mọi kịch bản hoặc mọi lỗi không ghi lặp ở từng dòng.

| Mã | Nhóm | Lỗi | Mức hoặc dạng | Phản ứng mong muốn | Yêu cầu | Trạng thái |
|---|---|---|---|---|---|---|
| F01 | Lane model | Nhiễu c0, c1 | a) ban ngày σ_c0 = 0,03 m, σ_c1 = 0,002; b) gấp 1,5 lần; c) ban đêm hoặc mưa, gấp 2,5 lần | Path không rung, jerk trong giới hạn | PP-SWR-120 | đã chốt |
| F02 |   | c0 jump | a) 0,3 m; b) 0,6 m; c) 1,0 m trong một frame; d) nhảy rồi quay lại sau một frame; e) nhảy và giữ nguyên. Lane Model không gửi cờ báo nhảy | Không nhảy bậc: thoả ngưỡng liên tục; tốc độ dời ngang của path có giới hạn | PP-SWR-121 | đề bài |
| F03 |   | Nhận nhầm vạch làn bên | a) vạch trái nhảy sang vạch L2, bề rộng 3,5 → 7 m, trong một frame; b) như a, kéo dài 0,5 s; c) cả hai vạch nhảy sang làn bên, tâm làn dời 3,5 m, không có cờ chuyển làn; d) nhận nhầm một vạch cũ hoặc vết nứt lệch 0,5 m, kéo dài 2 s; e) như a, giữa lúc ELK | Path không đi theo vạch nhầm: lệch ngang so với tâm làn thật ≤ 0,1 m; không kích hoạt hoặc hủy chức năng vì vạch nhầm | PP-SWR-122 | mentor |
| F04 |   | Mất một vạch | a) trái; b) phải; c) độ tin giảm về 0 trong 2 s rồi mất; d) mất ngay; e) mất đúng lúc bề rộng làn đang đổi | Path vẫn bám tâm làn thật: ghi lệch ngang so với tâm làn thật và so với ca không lỗi; thoả ngưỡng liên tục | PP-SWR-123 (a–d) | đề bài, mentor |
| F05 |   | Mất cả hai vạch | a) dựng lại 0,5 s rồi mất; b) dựng lại 1 s rồi mất; c) mất 0,5 s rồi có lại; d) mất giữa cua R = 500 m | path_valid = false đúng lúc T_coast = 1 s sau khi mất vạch; trước đó ghi lệch ngang so với tâm làn thật | PP-SWR-124 | đã chốt |
| F06 |   | Độ cong ước lượng sai | a) c2 +0,0005 1/m trên đường thẳng; b) −0,0005 1/m trong cua; c) c2 đúng nhưng c3 sai; d) sai kéo dài 2 s; e) sai ở đoạn vào cua | Path không theo cua giả: ghi lệch ngang so với tâm làn thật ở 2–3 s phía trước | PP-SWR-125 | đề bài, mentor |
| F07 | IMU | Nhiễu | Kịch bản chính dùng IMU sạch. a) yaw rate σ = 0,07 °/s, a_y σ = 0,004 m/s²; b) σ = 0,14 °/s và 0,008 m/s² ([Mô hình cảm biến](report.html?doc=benchmark-evaluation&lang=vi#sim-sensors), theo datasheet Bosch SMI230) | Path không rung: jerk trong giới hạn; ghi lệch ngang so với ca không lỗi | PP-SWR-135 (a, b) | mentor |
| F08 |   | Bias yaw rate | a) 0,1 °/s; b) 0,3 °/s; c) 1 °/s, offset của cảm biến thô chưa bù, mức xấu nhất | Ghi lệch ngang so với tâm làn thật và so với ca không lỗi; với c, đo thêm lệch ngang sau 1 s và 2 s không có vạch | PP-SWR-136 (a, b) | mentor |
| F09 | Thời gian | Trễ | Quét ở mục 4.1 | Lệch ngang so với tâm làn thật theo từng mức trễ |   | mentor |
| F10 |   | Jitter, mất message | a) mất lẻ; b) mất chuỗi 2 message; c) mất chuỗi 5 message; d) jitter ±20 ms | Path không giật: thoả ngưỡng liên tục và giới hạn jerk | PP-SWR-126 | đã chốt |
| F11 |   | Muộn, sai thứ tự | Message đến sau message mới hơn | Path không bị kéo theo dữ liệu cũ: thoả ngưỡng liên tục; ghi lệch so với ca không lỗi | PP-SWR-127 | đã chốt |
| F12 |   | Ngừng gửi | Một input ngừng gửi tới quá timeout; làm cho từng input | Output (path_valid, active_function, offset HWA) đúng như yêu cầu ở bảng input không hợp lệ (tài liệu Yêu cầu phần mềm Path Planner, mục 8.3) | PP-SWR-124 (Lane Model), 140 (Perception, trong S3), 141 (Perception, trong S5), 142 (IMU, tốc độ, góc lái), 144 (v_y), 145 (FunctionRequests) | đã chốt |
| F13 |   | Camera chậm hơn planner | 20 Hz so với 40 Hz, luôn có | Path liên tục ở mọi chu kỳ planner, không có bậc thang theo nhịp camera: thoả ngưỡng liên tục | PP-SWR-128 | đã chốt |
| F14 |   | Mất đồng bộ đồng hồ | a) trôi ±20 ppm; b) ±100 ppm; c) mất đồng bộ gPTP 10 s | Path không lệch thêm vì stamp sai: ghi lệch ngang so với tâm làn thật và so với ca đồng hồ đúng | PP-SWR-137 (a, b, c) | đã chốt |
| F15 | Toàn vẹn | Counter lặp hoặc nhảy, counter đứng yên | Trên từng kênh | Message lặp: path giống ca không lỗi. Counter nhảy hoặc đứng yên: path giống ca mất message tương ứng | PP-SWR-129 (lặp), 130 (nhảy, đứng yên) | đã chốt |
| F16 |   | Cờ không hợp lệ, qualifier lỗi | valid = false, qualifier FAULT | Path giống ca mất message tương ứng | PP-SWR-130 | đã chốt |
| F17 |   | CRC sai | Khung CAN | Path giống ca mất khung tương ứng | PP-SWR-130, 142 | đã chốt |
| F18 |   | Làm tròn CAN | Theo factor của DBC, luôn có | Không ảnh hưởng đáng kể | PP-SWR-139 | đã chốt |
| F19 | Thời gian | Stamp ở tương lai | a) stamp của lane model ở tương lai 5 ms so với đồng hồ planner; b) 15 ms; c) 50 ms; d) chỉ một frame ở tương lai 50 ms; e) stamp của ObjectList ở tương lai 15 ms | a: input vẫn được dùng; b, c, e: như input tương ứng không hợp lệ; d: như mất một frame | PP-SWR-132 | đề xuất |
| F20 | Ego-motion | Không hợp lệ | a) báo lỗi ở một lần truy vấn; b) báo lỗi liên tục; c) báo lỗi xen kẽ, mỗi chu kỳ một lần; d) như b, giữa lúc LKA can thiệp | path_valid = false trong không quá một chu kỳ kể từ lần truy vấn lỗi | PP-SWR-143 | đề xuất |

**Chỉ thêm ca ở phía đánh giá.** Các ca mới (nhận nhầm vạch, làn mở rộng, và c0 jump khi Lane Model không gửi cờ) được thêm vào benchmark để kiểm planner, không phải để planner viết riêng một nhánh xử lý cho từng ca. Planner phải được thiết kế tổng quát. Benchmark không biết và không dựa vào cách planner xử lý các ca này; chỉ chấm trên output qua interface.

### 4.1 Quét độ trễ

Mentor cho biết độ trễ thật chưa biết. Vì vậy benchmark không thử một mức danh định, mà quét nhiều mức để thấy planner suy giảm thế nào khi trễ tăng. Benchmark chỉ đổi độ trễ thật trong simulator; planner chạy với cấu hình của chính nó ở mọi mức, giống nhau cho mọi lần chạy.

Mã lỗi cố định: không đánh số lại, không dùng lại. Cột Yêu cầu được sinh bằng `python3 tools/trace.py --write` từ cột Kiểm chứng của tài liệu Yêu cầu phần mềm Path Planner; không sửa tay. Yêu cầu áp cho mọi kịch bản hoặc mọi lỗi không ghi lặp ở từng dòng.

| Mã | Quét | Mức | Đo gì | Yêu cầu | Trạng thái |
|---|---|---|---|---|---|
| Q1 | Trễ camera (lane model và vật thể) | 0 / 50 / 100 / 150 / 200 / 300 ms, mỗi mức kèm jitter ±20 ms. Mức 300 ms vượt xa mọi độ trễ camera hợp lý, để xem planner làm gì khi dữ liệu đã quá cũ | Lệch ngang của path so với tâm làn thật ở 0, 25, 50 m, trên đường thẳng và trong cua R = 250 m. Ở mọi mức, output phải an toàn: hoặc path vẫn trong làn, hoặc path_valid = false | PP-SWR-012, 013, 131 (300 ms), 133 (200 ms) | đề xuất |
| Q2 | Trễ yaw rate đã lọc | 0 / 25 / 50 / 100 ms | Lệch ngang của path so với tâm làn thật, trên đường thẳng và khi vào clothoid; so sánh với ảnh hưởng của trễ camera | PP-SWR-138 (0–50 ms) | đề xuất |
| Q3 | Trễ khối ADAS tới planner | 20 / 40 / 60 ms | Thời điểm path can thiệp bắt đầu so với lúc khối ADAS quyết định; DTLE ở S4c, S5c | PP-SWR-038 | đề xuất |

Kết quả trình bày thành đường cong: chỉ số theo mức trễ, mỗi kỹ thuật một đường. Kỹ thuật có đường cong thoải hơn là kỹ thuật chịu trễ tốt hơn.

### 4.2 Ghép lỗi

Chạy đủ mọi tổ hợp (kịch bản × biến thể × lỗi × mức × thời điểm × vòng hở và kín × seed) là quá nhiều. Đề xuất:

1. Mỗi kịch bản và biến thể với **từng lỗi một**, ở ba thời điểm, cả vòng hở và vòng kín. Lỗi có nhiều mức thì chạy đủ mức trên biến thể khó nhất của kịch bản, và chỉ mức giữa trên các biến thể còn lại.
2. Thêm vài **ca xấu gộp** có ý nghĩa thật, ví dụ "đêm mưa": nhiễu gấp 2,5 lần, μ = 0,5, mất một vạch, trễ 150 ms.
3. Máy 8 GB RAM: chạy theo lô nhỏ, mỗi lô một kịch bản, hỏi trước khi chạy lô lớn.

### 4.3 Mã không truy về yêu cầu của planner {#benchmark-trace-exempt}

Mỗi kịch bản, lỗi và mức quét phải kiểm chứng ít nhất một yêu cầu của planner. Mã nào không như vậy thì ghi ở đây kèm lý do. `tools/trace.py` không cảnh báo các mã này, và cảnh báo nếu một mã ở đây lại có yêu cầu trỏ tới.

| Mã | Lý do |
|---|---|
| S10 | Kiểm khối Chức năng ADAS: không kích hoạt thừa khi xe đi gần vạch mà không trôi. Dùng để chốt ngưỡng TLC (mục 5.6). Yêu cầu của khối ADAS chưa có ID |
| F09 | Dòng gom của quét độ trễ. Chi tiết và truy vết ở Q1, Q2, Q3 (mục 4.1) |

## 5. Chỉ số và ngưỡng đạt

### 5.1 An toàn và lấn làn

| Chỉ số | Cách đo | Ngưỡng đạt | Căn cứ | Trạng thái |
|---|---|---|---|---|
| DTLE nhỏ nhất | Khoảng cách từ mép ngoài lốp tới mép trong của vạch, nhỏ nhất trong lần can thiệp | LKA ≥ −0,3 m; ELK vạch liền ≥ −0,3 m; ELK mép đường ≥ −0,1 m | Euro NCAP Assessment 4.3.2, 4.3.3.3; EU 2021/646 3.6.2 | đã chốt |
| DTLE mục tiêu thiết kế | Như trên | LKA ≥ 0 (không chạm vạch) ở chế độ B, ban ngày | Mục tiêu chặt hơn quy định, để còn dư cho nhiễu | đề xuất |
| Va chạm với xe ở làn bên | Khoảng cách ngang nhỏ nhất giữa hai xe | Không chạm; khoảng cách ≥ 0,3 m | Euro NCAP 4.3.3.4 và LSS 7.4.7 | đã chốt |
| Vọt sang phía bên kia | Sau can thiệp, DLC nhỏ nhất ở phía đối diện | ≥ 0,3 m, tức không vượt quá đích sang phía kia | Đề bài: "no overshoot into the other lane" | đề xuất |
| HWA không đè vạch | DLC nhỏ nhất khi a_y dưới aysmax | ≥ 0 | R79 5.6.2.1.1 | đã chốt |

### 5.2 Giới hạn

| Chỉ số | Cách đo | Ngưỡng đạt | Trạng thái |
|---|---|---|---|
| Vượt ngân sách a_y | Trên path: a_y tổng và a_y do hệ thống thêm vào, theo chức năng đang lái | Không vượt: tổng HWA 2,5 / LKA 3,0 / ELK 4,0 m/s²; thêm vào HWA 0,5 / LKA 1,5 / ELK 3,0 m/s². HWA được vượt aysmax theo R79 (0,3 m/s², hoặc 40 % trong tối đa 2 s) | đã chốt |
| Vượt jerk | Trung bình trượt 0,5 s của jerk ngang | HWA, LKA ≤ 5 m/s³; ELK ≤ 10 m/s³ | đã chốt |
| Góc và tốc độ lái | Góc bánh trước gợi ý trên path; vòng kín đo thêm trên EPS | ≤ 0,61 rad; ≤ 6 rad/s ở vô lăng | đã chốt |
| Thời lượng can thiệp | Từ REQUEST tới COMPLETED | ≤ 10 s | đã chốt |
| Ghi nhận | Mỗi lần vượt: đếm số lần, ghi mức vượt lớn nhất và thời gian vượt | — | đề bài |

### 5.3 Độ mượt và độ êm

| Chỉ số | Cách đo | Ngưỡng hoặc cách dùng | Trạng thái |
|---|---|---|---|
| Jerk ngang đỉnh và RMS | Trên path của planner, theo từng chức năng | So sánh giữa các kỹ thuật; HWA mục tiêu ≤ 2,5 m/s³ | đề bài |
| a_y đỉnh và RMS | Trên path | So sánh giữa các kỹ thuật | đề bài |
| Tốc độ quay vô lăng RMS | Vòng kín | So sánh; thấy được rung vô lăng do nhiễu | đề xuất |
| Độ êm lúc trả quyền | a_y do hệ thống thêm vào tại thời điểm COMPLETED | ≤ 0,2 m/s² | đề xuất |

### 5.4 Liên tục giữa hai path

| Chỉ số | Cách đo | Ngưỡng đạt | Trạng thái |
|---|---|---|---|
| Lệch ngang, hướng, độ cong giữa hai path liên tiếp | Trên đoạn cả hai cùng mô tả, sau khi đưa path cũ về base_link mới | ≤ 0,05 m; ≤ 0,005 rad; ≤ 0,0003 1/m ở mọi chu kỳ, kể cả lúc đổi chức năng và lúc c0 jump | đã chốt |
| Ghi nhận | Tỉ lệ chu kỳ đạt, giá trị lớn nhất, chu kỳ vi phạm | — | đã chốt |

### 5.5 Phản ứng với lỗi

| Chỉ số | Cách đo | Ngưỡng đạt | Trạng thái |
|---|---|---|---|
| Thời điểm báo path không hợp lệ | Từ lúc Lane Model báo mất cả hai vạch tới lúc path_valid = false | T_coast = 1 s, sai lệch không quá một chu kỳ (25 ms) | đã chốt |
| Phản ứng với input quá timeout | Từ lúc vượt timeout tới hành vi đúng theo bảng input không hợp lệ | Không quá một chu kỳ | đã chốt |
| c0 jump | Lệch ngang lớn nhất giữa hai path liên tiếp quanh frame jump; tốc độ dời tâm | Thoả ngưỡng liên tục | đã chốt |
| Nhận nhầm vạch | Lệch ngang lớn nhất giữa path và tâm làn thật trong lúc có lỗi; số frame từ lúc lỗi bắt đầu tới lúc lệch ngang về lại dưới 0,1 m | Lệch ≤ 0,1 m; thoả ngưỡng liên tục; không kích hoạt hoặc hủy chức năng vì vạch nhầm | đề xuất |
| Làn mở rộng (S6b) | Lệch ngang giữa path và tâm làn thật | Lệch ≤ 0,1 m; path không dịch về phía mở rộng | đề xuất |
| Quét độ trễ (mục 4.1) | Chỉ số theo từng mức trễ | Báo cáo đường cong suy giảm cho từng kỹ thuật | đề xuất |
| c2 sai | Độ lệch giữa path và tâm làn thật ở 2–3 s phía trước | So sánh giữa các kỹ thuật | đề bài |
| So với mốc không nhiễu | Mỗi chỉ số ở ô có lỗi so với ô không lỗi cùng kịch bản | Báo cáo mức suy giảm | đã chốt |

### 5.6 Kích hoạt (dùng để chốt ngưỡng TLC)

| Chỉ số | Cách đo | Dùng để | Trạng thái |
|---|---|---|---|
| Kích hoạt thừa | Số lần LKA hoặc ELK kích hoạt trong S10 | Ngưỡng TLC không được quá sớm. Mục tiêu 0 | đề xuất |
| Lệch thời điểm kích hoạt | Chế độ A so với chế độ B, cùng seed | Thấy ảnh hưởng của nhiễu camera lên lúc kích hoạt | đề xuất |
| DTLE theo ngưỡng TLC | Chạy S4 đến S8 với **ba phương án ngưỡng LKA: 0,6 / 1,0 / 1,5 s** | Ngưỡng TLC không được quá muộn | đã chốt |
| Kết luận cho ba phương án | Đặt mức lấn vạch (S4–S8) cạnh số lần kích hoạt thừa (S10) cho từng phương án | Chốt ngưỡng LKA sau khi có số liệu | đã chốt |

### 5.7 Thời gian tính

| Chỉ số | Cách đo | Ngưỡng | Trạng thái |
|---|---|---|---|
| Thời gian tính mỗi chu kỳ | Đo thật bằng đồng hồ của máy, không phải thời gian mô phỏng; trung bình, p95, p99, lớn nhất | Báo cáo cho từng kỹ thuật. Đề xuất p99 ≤ 5 ms trên máy phát triển, để còn xa chu kỳ 25 ms | cần chốt |
| Ghi chú | Python trên laptop chậm và dao động hơn code C trên ECU. Số đo dùng để **so sánh giữa các kỹ thuật**, không phải để khẳng định chạy được trên ECU | — | đề xuất |

### 5.8 Bám path (chỉ vòng kín)

| Chỉ số | Cách đo | Cách dùng | Trạng thái |
|---|---|---|---|
| Sai số ngang và sai số hướng so với path | Vòng kín | Kiểm tra controller chạy thử không che lỗi của planner. Không dùng để chấm planner | đề xuất |

## 6. So sánh các kỹ thuật

| Quy tắc | Nội dung | Trạng thái |
|---|---|---|
| Cùng điều kiện | Mọi kỹ thuật chạy cùng kịch bản, cùng seed, cùng controller chạy thử đã cố định hệ số | đã chốt |
| Thứ tự xếp hạng | 1. Đạt mọi ngưỡng an toàn (5.1). 2. Không vượt giới hạn (5.2) và đạt ngưỡng liên tục (5.4). 3. Phản ứng với lỗi (5.5). 4. Độ mượt (5.3). 5. Thời gian tính (5.7). Một kỹ thuật trượt bước 1 hoặc 2 thì bị loại, dù mượt hơn | đề xuất |
| Ứng viên | Theo tài liệu Triển khai Path Planner (đang chờ): quintic hoặc clothoid theo thời lượng; lấy mẫu trong Frenet (Werling 2010); QP hoặc MPC. Thêm biến thể đa thức bậc 7 nếu cần jerk cuối bằng 0 | đề bài |
| Kết quả cho báo cáo | Một bảng so sánh, và ít nhất một kỹ thuật bị loại kèm lý do bằng số liệu | đề bài |

## 7. Trình bày kết quả

| Loại | Nội dung |
|---|---|
| Bảng tổng | Mỗi kỹ thuật một hàng; cột là các chỉ số ở mục 5, đạt hay trượt, giá trị xấu nhất qua mọi seed |
| Biểu đồ theo thời gian | d(t) của path và của xe, cùng hai mép làn; a_y; jerk; chức năng đang lái; các lần đổi chức năng; thời điểm bơm lỗi |
| Biểu đồ liên tục | Lệch ngang, hướng, độ cong giữa hai path liên tiếp theo từng chu kỳ, kèm đường ngưỡng |
| Biểu đồ theo v_lat | DTLE nhỏ nhất theo v_lat cho S4–S8, giống cách trình bày của Euro NCAP |
| Phân bố thời gian tính | Histogram, kèm p95 và p99 |

## 8. Còn cần chốt

1. **Quy tắc công tâm** (mục 0): định trước, bộ kịch bản chỉnh và bộ kịch bản kiểm tách riêng.
2. **Tốc độ thử**: 72 km/h theo Euro NCAP, thêm 90 km/h.
3. **Định nghĩa vọt sang phía bên kia**: DLC phía đối diện ≥ 0,3 m.
4. **Kịch bản S10** (đi gần vạch mà không trôi) và mục tiêu 0 lần kích hoạt thừa.
5. **Ngưỡng thời gian tính**: p99 ≤ 5 ms trên máy phát triển.
6. **Các ca xấu gộp** (mục 4).
7. **Thứ tự xếp hạng** các kỹ thuật (mục 6).
8. **Mục tiêu DTLE ≥ 0 cho LKA**, chặt hơn Euro NCAP.
9. **Kịch bản S8b, S8c, S15**.
10. **Biến thể của từng kịch bản và mức của từng lỗi** (mục 3, 4).
11. **Bề rộng làn hẹp** 3,0 m và 2,75 m: đối chiếu với tiêu chuẩn đường của Việt Nam.
12. **Ngưỡng lệch 0,1 m** cho các ca nhận nhầm vạch và làn mở rộng.
13. **Các mức quét độ trễ** (mục 4.1).
14. **Log thật**: mentor có cung cấp không, có phần camera không (mục 2.1).
15. **Nguồn cho mức lỗi lane model** (mục 4): σ_c0, σ_c1, mức c0 jump, sai c2 hiện trùng với giả định của planner và chưa có nguồn từ dữ liệu thật. Cần một nguồn độc lập với planner: log thật, hoặc tài liệu về sai số của camera làn.
16. **Ngưỡng đạt cho các dòng chỉ ghi lệch** (mục 4): mất một vạch, mất cả hai vạch (trước khi hết T_coast), c2 sai, nhiễu IMU, bias yaw rate, trễ, message muộn hoặc sai thứ tự, mất đồng bộ đồng hồ. Hiện các dòng này chỉ ghi lệch ngang so với tâm làn thật hoặc so với ca không lỗi: đủ để so sánh các kỹ thuật, chưa đủ để kết luận đạt hay trượt. Ngưỡng cần suy ra từ yêu cầu an toàn của người dùng (ví dụ khoảng trống còn lại từ bánh xe tới vạch) và có nguồn.

## 9. Thiết kế môi trường giả lập {#simulation-design}

Các khối dưới đây dùng chung khi chạy prototype G1. Mục [Cách chạy](report.html?doc=benchmark-evaluation&lang=vi#benchmark-run) quy định chế độ chạy và ghi log. Thiết kế [ACC chạy thử](report.html?doc=thiet-ke-path-planner&lang=vi#acc-stub) mô tả cách hai khối ngang và dọc trao đổi ràng buộc.

### Bộ lập lịch {#sim-scheduler}

**Kiến trúc hai chế độ**

| Mục | Yêu cầu | — | Trạng thái |
| --- | --- | --- | --- |
| Cùng một code | Các thành phần chỉ nói chuyện qua interface, nên dùng chung cho cả hai chế độ; chỉ lớp truyền và lớp lập lịch thay đổi | — | đã chốt |
| Ngôn ngữ | Python thuần cộng numpy, không dùng ROS 2 | — | đã chốt |
| Giao thức pub/sub ở chế độ thời gian thực | UDP trên localhost, mỗi message mã hoá nhị phân theo đúng schema | — | đã chốt |

**Lập lịch**

| Mục | Yêu cầu | — | Trạng thái |
| --- | --- | --- | --- |
| Bước thời gian | 1 ms cố định. Mô hình xe tích phân mỗi bước; trễ và jitter có độ phân giải 1 ms; thời gian truyền khung CAN tính gộp vào độ trễ | ms | đã chốt |
| Độ lệch pha | Mỗi khối bắt đầu ở một độ lệch pha ngẫu nhiên trong chu kỳ của nó, sinh theo seed | — | đã chốt |
| Thứ tự trong một bước | Tích phân mô hình xe, cảm biến lấy mẫu, giao message đến hạn, rồi chạy các khối đến lượt theo thứ tự ưu tiên cố định | — | đã chốt |
| Kênh truyền | Trễ = danh định + jitter phân bố đều; có xác suất mất; bên nhận giữ message mới nhất (last-is-best); kiểm tra counter, CRC, qualifier ngay lúc nhận từng message | — | đã chốt |
| Bơm lỗi | Gắn vào từng kênh theo kịch bản: mất chuỗi message, thêm trễ, gửi trùng, đảo thứ tự, ngừng gửi, CRC sai, counter đứng yên | — | đã chốt |
| Thời gian tính của planner | Trong giả lập coi là 5 ms thời gian mô phỏng; thời gian tính thật của code đo riêng cho chỉ số của đề bài | ms | đã chốt |
| Seed | Dùng `numpy.random.SeedSequence.spawn` để tách các luồng từ seed chính (mục 2) | — | đã chốt |

**Đồng hồ**

| Mục | Yêu cầu | Đơn vị | Trạng thái |
| --- | --- | --- | --- |
| Đồng hồ riêng | Mỗi ECU có đồng hồ riêng: trôi tới ±100 ppm, lệch ban đầu ngẫu nhiên theo seed | ppm | đã chốt |
| Đồng bộ | Kiểu gPTP, chỉnh lại mỗi 125 ms, sau mỗi lần chỉnh vẫn còn sai số nhỏ | ms | đã chốt |
| stamp_us | Ghi theo đồng hồ của ECU gửi; khung CAN gán stamp theo đồng hồ của ECU nhận | — | đã chốt |
| Lỗi bơm vào | Mất đồng bộ: đồng hồ của một ECU trôi dần so với các ECU khác | — | đã chốt |
| Lệch ban đầu | Tới ±10 ms trước lần đồng bộ đầu tiên | ms | đã chốt |
| Sai số sau đồng bộ | Tới ±50 µs | µs | đã chốt |
| Chế độ thời gian thực | Các tiến trình chạy trên cùng một máy nên chung đồng hồ hệ điều hành; đồng hồ riêng của từng ECU được mô phỏng chồng lên đó | — | đã chốt |

### Bus CAN ảo {#sim-can}

**Yêu cầu**

| Quy định | Trạng thái |
| --- | --- |
| Tín hiệu khung gầm đi qua bus CAN ảo, theo [khung DBC](report.html?doc=interface-he-thong&lang=vi#can). | đã chốt |
| Thấy được hiệu ứng thật: giá trị bị làm tròn theo factor, chu kỳ cố định, counter, CRC, timeout. | đã chốt |
| Bơm lỗi được: mất khung, CRC sai, counter lặp hoặc nhảy, ngừng gửi. | đã chốt |
| Thư viện: cantools (đọc DBC, mã hoá, giải mã) và bus ảo của python-can. | đã chốt |

### Mô hình xe {#sim-vehicle}

**Mô hình**

| Trường | Yêu cầu | Đơn vị | Trạng thái |
| --- | --- | --- | --- |
| Loại | Bicycle động lực học, lốp tuyến tính F = C·α. Trạng thái: x, y, ψ, v_y, r | — | đã chốt |
| Giới hạn bám | Lực ngang của mỗi trục không vượt μ·F_z. μ = 1,0 khi đường khô, 0,5 khi đường ướt (kịch bản trời mưa) | — | đã chốt |
| Tốc độ thấp | Chuyển dần sang kinematic trong khoảng 3–5 m/s, tránh chia cho tốc độ gần 0 mà không làm trạng thái giật | m/s | đã chốt |
| Tốc độ dọc | Từ ACC chạy thử: lệnh gia tốc qua trễ 0,1 s và khâu bậc một τ = 0,3 s. Kịch bản vẫn có thể ghi sẵn tốc độ khi không cần ACC | m/s | đề xuất |
| Đầu vào | Góc bánh trước từ EPS chạy thử | rad | đã chốt |
| Nguồn trôi làn | Tài xế giả cộng một góc lái lệch nhỏ, hoặc lực ngang không đổi do đường nghiêng ngang hay gió ngang. Chọn theo từng kịch bản | — | đã chốt |
| Tích phân | RK4, bước 1 ms theo bộ lập lịch | ms | đã chốt |

**Tham số**

Giá trị điển hình của xe điện cỡ trung

| Tham số | Giá trị | Đơn vị | Trạng thái |
| --- | --- | --- | --- |
| Khối lượng m | 2000 | kg | đã chốt |
| Mô-men quán tính I_z | 3500 | kg·m² | đã chốt |
| Chiều dài cơ sở L | 2,9 | m | đã chốt |
| l_f, l_r | 1,45 và 1,45 | m | đã chốt |
| C_f, C_r (mỗi trục) | 100 000 và 140 000 | N/rad | đã chốt |
| Bề rộng xe | 1,9 | m | đã chốt |
| Tỉ số lái | 15 | — | đã chốt |

**Kiểm tra độ hợp lý**

| Đại lượng | Giá trị | Đơn vị | Trạng thái |
| --- | --- | --- | --- |
| Hệ số thiếu lái K | m/L · (l_r/C_f − l_f/C_r) ≈ 0,0029, tức khoảng 1,6°/g | rad/(m/s²) | đã chốt |
| Tốc độ đặc trưng | √(L/K) ≈ 32 m/s, khoảng 115 km/h; xe con thường 70–110 km/h | m/s | đã chốt |
| I_z / (m · l_f · l_r) | ≈ 0,83; xe con thường 0,8–1,1 | — | đã chốt |

**Cố ý bỏ qua**

| Quy định | Trạng thái |
| --- | --- |
| Chuyển tải trọng khi vào cua, độ nảy hệ treo, độ nhún cột lái, mặt đường gồ ghề. Ở gia tốc ngang của HWA và LKA các hiệu ứng này nhỏ. | đã chốt |

Giá trị điển hình của xe điện cỡ trung, chưa phải số đo của một xe cụ thể. Planner đọc cùng bộ tham số qua [VehicleConfig](report.html?doc=interface-he-thong&lang=vi#vehicle-config).

### Mô hình cảm biến {#sim-sensors}

**Yêu cầu**

| Quy định | Trạng thái |
| --- | --- |
| Lane model: lấy hình học làn trong tầm nhìn, đưa về base_link, khớp đa thức bậc 3 cho từng vạch, rồi bơm lỗi theo [danh mục lỗi bơm vào](report.html?doc=benchmark-evaluation&lang=vi#benchmark-faults) của tài liệu này. Đây là bản thay thế của khối Lane Model. Mức lỗi do bên đánh giá đặt từ dữ liệu thật hoặc tài liệu, không lấy từ giả định của planner về lỗi mà nó chịu được. | đã chốt |
| Vật thể: lấy từ kịch bản, đưa về base_link, gửi theo [interface ObjectList](report.html?doc=interface-he-thong&lang=vi#perception). | đã chốt |
| IMU: kịch bản chính dùng IMU sạch, tức giá trị thật của mô hình xe, chỉ bị làm tròn theo factor của DBC. Nhiễu và bias IMU được bơm vào theo mục 4. Xem mức lấy từ datasheet trong bảng Tín hiệu khung gầm. | mentor |
| Tốc độ, góc lái: lấy từ mô hình xe, cộng nhiễu và sai lệch ở bảng Tín hiệu khung gầm trước khi mã hoá CAN, rồi làm tròn theo factor của DBC. | đã chốt |

**Tín hiệu khung gầm**

Mỗi mẫu có nhiễu trắng. Sai lệch cố định được chọn theo seed và giữ nguyên trong một lần chạy.

| Tín hiệu | Nhiễu trắng σ; sai lệch cố định | Đơn vị | Trạng thái |
| --- | --- | --- | --- |
| Yaw rate, kịch bản chính | Sạch: σ = 0, bias = 0 | °/s | mentor |
| Yaw rate, lỗi bơm vào | Nhiễu: σ = 0,07 hoặc 0,14 (mật độ nhiễu 0,02 °/s/√Hz nhân √12 Hz hoặc √50 Hz). Bias: 0,1 / 0,3 / 1. Mức 1 °/s là offset ở 25 °C của cảm biến thô trước khi bù, nên là mức xấu nhất | °/s | đề xuất |
| a_x, a_y, kịch bản chính | Sạch: σ = 0, bias = 0. Trên đường nghiêng ngang, a_y đo được vẫn chứa g·sin(góc nghiêng), vì đó là vật lý chứ không phải lỗi cảm biến | m/s² | mentor |
| a_x, a_y, lỗi bơm vào | Nhiễu: σ = 0,004 hoặc 0,008 (0,12 mg/√Hz nhân √12 Hz hoặc √50 Hz). Bias: tới 0,2 (offset 20 mg ở 25 °C) | m/s² | đề xuất |
| Tốc độ v | σ = 0,02 m/s; sai tỉ lệ tới ±0,5% (bán kính lốp) | m/s | đã chốt |
| Góc vô lăng | σ = 0,001; lệch điểm 0 tới ±0,01 (khoảng 0,6°) | rad | đã chốt |

**Perception**

| Lỗi | Mức | Đơn vị | Trạng thái |
| --- | --- | --- | --- |
| Vị trí dọc x | σ = 0,2 + 1% khoảng cách | m | đã chốt |
| Vị trí ngang y | σ = 0,1 + 0,5% khoảng cách | m | đã chốt |
| Vận tốc vx, vy | σ = 0,3 và 0,2 | m/s | đã chốt |
| Kích thước | σ = 0,1 cho cả dài và rộng | m | đã chốt |
| Bỏ sót | 2% số frame, mỗi vật thể | — | đã chốt |
| Vật thể ảo | Trung bình 0,05 lần mỗi giây, tồn tại khoảng 0,2 s, xác suất tồn tại thấp | 1/s | đã chốt |
| Trời mưa | Nhân σ lên 1,5 lần, cùng kịch bản với μ = 0,5 và nhiễu camera tăng | — | đã chốt |

**Khối thay thế của G2 và G4**

| Quy định | Trạng thái |
| --- | --- |
| Ước lượng trạng thái xe dùng v_y thật cộng nhiễu có σ = 0,05 m/s. Trường phương sai gửi kèm là σ². | đã chốt |
| Ego-motion: không cộng nhiễu riêng. Tích phân chuyển động từ chính các tín hiệu CAN, nên khi bơm nhiễu hoặc bias IMU, sai số ego-motion tự sinh theo cơ chế thật. | đã chốt |

Mọi nhiễu và sai lệch được sinh từ các luồng ngẫu nhiên theo seed ở mục 2.

Mức nhiễu IMU lấy từ datasheet Bosch SMI230 (cảm biến quán tính AEC-Q100 Grade 2 cho ô tô, bản giới thiệu sản phẩm 2018): gyro 0,02 °/s/√Hz, offset ±1 °/s ở 25 °C, thay đổi thêm ±1 °/s theo nhiệt độ; gia tốc 0,12 mg/√Hz, offset ±20 mg. Đây là cảm biến thô; tín hiệu đã lọc trên xe sạch hơn, nên các mức này là chặn trên. Đổi mật độ nhiễu sang σ theo giả định bộ lọc lý tưởng với băng thông 12 Hz (mức thấp nhất của SMI230) hoặc 50 Hz (nửa tần số 100 Hz). Mức nhiễu tốc độ, góc lái và perception vẫn là giá trị điển hình tự đặt, chưa có nguồn.

### Controller và EPS chạy thử {#sim-controller}

**Yêu cầu**

| Quy định | Trạng thái |
| --- | --- |
| Chỉ là công cụ chạy thử vòng kín, không phải sản phẩm của G1. | đã chốt |
| Nhận đúng [interface Trajectory](report.html?doc=interface-he-thong&lang=vi#trajectory). | đã chốt |
| Đơn giản và cố định: chỉnh hệ số một lần rồi giữ nguyên cho mọi phiên bản planner đem ra so sánh, để controller không che lỗi của planner. | đã chốt |

**Controller**

| Mục | Yêu cầu | Đơn vị | Trạng thái |
| --- | --- | --- | --- |
| Tần số | 100 Hz, nhanh hơn planner 40 Hz; nội suy giữa hai path liên tiếp | Hz | đã chốt |
| Đọc path | Lấy điểm theo stamp_us + time_from_start, đưa về base_link hiện tại bằng khối Ego-motion | — | đã chốt |
| Luật lái | δ = L·κ + K·v²·κ + k_y·e_y + k_ψ·e_ψ. Hai số hạng đầu là feedforward theo độ cong, K ≈ 0,0029 từ mô hình xe; hai số hạng sau là feedback theo sai số ngang và sai số hướng | rad | đã chốt |
| Điểm nhìn trước | Tính sai số tại điểm cách 0,5 s trên path, để bù trễ của EPS | s | đã chốt |
| Hệ số k_y, k_ψ | Chỉnh một lần trong giả lập rồi giữ cố định | — | đã chốt |
| Đầu ra | Góc vô lăng yêu cầu | rad | đã chốt |
| Path không hợp lệ hoặc quá timeout 75 ms | Giữ lệnh cuối cùng, rồi trả quyền lái trong 1 s | s | đã chốt |

**EPS**

| Mục | Yêu cầu | Đơn vị | Trạng thái |
| --- | --- | --- | --- |
| Kiểu giao tiếp | Theo góc: bám góc vô lăng yêu cầu | — | đã chốt |
| Trễ thuần | 50 | ms | đã chốt |
| Quán tính | Khâu bậc một, hằng số thời gian τ = 0,1 s | s | đã chốt |
| Giới hạn tốc độ | 6 rad/s ở vô lăng, khoảng 340°/s | rad/s | đã chốt |
| Giới hạn góc | 0,61 rad ở bánh xe, khoảng 35° | rad | đã chốt |
| Khi controller không điều khiển | Góc lái chuyển dần trong 1 s sang góc của tài xế giả | s | đã chốt |
| Đầu ra | Góc bánh trước = góc vô lăng / 15, đưa vào mô hình xe | rad | đã chốt |

**Giới hạn và mở rộng**

| Quy định | Trạng thái |
| --- | --- |
| EPS giả lập nhận góc để đơn giản hóa. EPS trên xe L2 thật thường nhận mô-men. | đã chốt |
| Các con số là giá trị điển hình để chạy thử, không phải số đo của một EPS cụ thể. | đã chốt |
| Dùng [kịch bản S13](report.html?doc=benchmark-evaluation&lang=vi#benchmark-scenarios) để thử khi bộ chấp hành chậm hơn. | đã chốt |

## Nguồn

- Đề bài G1 (`G1_Path_Planning.pdf`), mục Prototype focus
- Bosch, SMI230 combined inertial sensor for motion detection, bản giới thiệu sản phẩm 2018 (mức nhiễu và offset IMU)
- Signal list nhóm Motion và các trao đổi với mentor
- [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf)
- [Euro NCAP Assessment Protocol Safety Assist Collision Avoidance v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf)
- [Commission Implementing Regulation (EU) 2021/646, ELKS](https://lawplayer.com/eu/act/32021R0646)
- [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf)
