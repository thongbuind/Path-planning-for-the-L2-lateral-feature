# Chức năng ADAS: khi nào HWA, LKA, ELK được phép can thiệp

Tài liệu này mô tả khối **Chức năng ADAS** **ở mức output**: trong tình huống nào khối này gửi yêu cầu nào cho Path Planner, với ngưỡng số cụ thể. Đề bài không giao khối này cho G1. Dự án vẫn cần một bản giả lập, vì kịch bản thử phải biết lúc nào chức năng được kích hoạt.

**Khối thật và khối giả.** Khối thật nhận lane model, vật thể, tín hiệu xe và tài xế, xử lý chi tiết (lọc, theo dõi ý định tài xế, HMI) rồi gửi yêu cầu. Khối giả trong simulator của G1 chỉ **phân loại tình huống bằng các ngưỡng trong tài liệu này** rồi gửi đúng message `FunctionRequests` như khối thật. Nó không có camera trong xe, không có học máy, không có HMI thật.

**Liên hệ với hai tài liệu khác.**

| Tài liệu | Trả lời câu hỏi | Nối với tài liệu này ở đâu |
|---|---|---|
| Chức năng ADAS (tài liệu này) | **Khi nào** từng chức năng muốn can thiệp, và phía nào | Gửi `FunctionRequests` sang Path Planner; nhận lại `PathStatus` |
| Thiết kế tính năng Path Planner | **Can thiệp như thế nào**: phân xử, lập path, giới hạn a_y và jerk, điều kiện kết thúc, chịu lỗi | Dùng TLC, phía, driver_override từ tài liệu này; báo COMPLETED và chức năng đang lái về đây |
| Benchmark và Evaluation | **Chấm thế nào**: kịch bản, lỗi bơm vào, chỉ số, ngưỡng đạt | Dùng khối ADAS giả ở chế độ B (mục 9) để chấm G1, chế độ A để thử cả chuỗi; chạy ba phương án ngưỡng TLC của LKA |

## 1. Căn cứ: các văn bản, tiêu chuẩn dùng ở đây

| Văn bản | Là gì | Dùng cho |
|---|---|---|
| UN R79, bản OJ L 2025/3 | Quy định phê duyệt hệ thống lái, bắt buộc khi xe được phê duyệt kiểu theo UNECE | HWA là ACSF Category B1 (mục 5.6.2), LKA và phần vạch của ELK là CSF (mục 5.1.6.1), phần vật thể của ELK là ESF (mục 5.1.6.2). Lực ghi đè 50 N, cảnh báo |
| EU 2021/646 (ELKS) | Quy định EU bắt buộc mọi xe mới có ELKS, áp dụng từ 6/7/2022 | Dải tốc độ 70–130 km/h, mặc định bật, cách tắt, các điều kiện được phép chặn can thiệp |
| Euro NCAP LSS Test Protocol v4.3 và Assessment Protocol Safety Assist v10.4.1 | Thử nghiệm chấm sao, không bắt buộc nhưng hãng nào cũng nhắm tới | Kịch bản thử (72 km/h, v_lat 0,2–0,6 m/s), ngưỡng DTLE, mô-men ghi đè 3,5 Nm, ELK khi tài xế bật xi-nhan |
| ISO 17361:2017 (LDWS) | Tiêu chuẩn cảnh báo lệch làn | Vùng cảnh báo: không sớm hơn "đường cảnh báo sớm nhất", không muộn hơn "đường cảnh báo muộn nhất". **Chưa đọc bản gốc**, chỉ qua nguồn thứ cấp (mục 6.1) |
| ISO 21448:2022 (SOTIF) | An toàn của chức năng dự định: rủi ro do giới hạn của cảm biến và thuật toán, khi không có hỏng hóc | Nguyên tắc cho mục 3.1: phải nhận diện điều kiện làm perception kém và có biện pháp tránh kích hoạt sai. **Chưa đọc bản gốc**; tiêu chuẩn này không cho con số |
| UN R171 (DCAS) | Quy định mới cho hệ thống hỗ trợ lái kết hợp ngang và dọc, tức nhóm của HWA | Điều kiện vào chế độ active. **Chưa đọc được bản gốc** |

Ba chức năng ứng với các khái niệm trong quy định như sau:

| Chức năng | Khái niệm trong quy định | Bật thế nào | Trạng thái |
|---|---|---|---|
| HWA | ACSF Category B1 (R79): hỗ trợ giữ xe trong làn liên tục. Cũng thuộc phạm vi R171 khi kết hợp với ACC | Tài xế bật bằng nút, cần ACC đang bật. Tắt được bằng một thao tác (R79 5.6.2.1.2) | đã chốt |
| LKA | CSF dựa trên vạch làn (R79 2.3.4.2 c) | Mặc định bật, tài xế tắt được qua menu | đã chốt |
| ELK, phần vạch liền và mép đường | CSF và ELKS | Mặc định bật mỗi lần khởi động xe. Tắt phải qua ít nhất hai thao tác có chủ đích; lần khởi động sau tự bật lại (EU 2021/646, Annex I, 3.2.1) | đã chốt |
| ELK, phần xe ngược chiều và xe đang vượt | ESF (R79 2.3.4.3 a): tránh va chạm với xe ở làn bên | Như dòng trên | đã chốt |

## 2. Phân chia nhiệm vụ giữa khối ADAS và G1 {#adas-role}

| Việc | Khối Chức năng ADAS | G1 Path planner |
|---|---|---|
| Đọc cài đặt: nút HWA, menu LKA, ELK | Làm | Không biết |
| Kiểm tra điều kiện chung: tốc độ, ACC, chất lượng vạch, ESC, lỗi input | Làm (mục 4) | Chỉ nhận kết quả là trạng thái từng chức năng |
| Lọc nhiễu và kết hợp nhiều nguồn cảm biến | Không làm lại. Lane Model đã lọc vạch; khối Ước lượng trạng thái (G2) đã ước lượng v_y; Ego-motion (G4) đã tính chuyển động. Mỗi khối gửi kèm phương sai. **Nhưng phải chịu được lỗi còn lại** của các khối đó: dùng phương sai và quy tắc ở mục 3.1, kiểm tính nhất quán của vạch (hàm dùng chung với G1), trạng thái và độ tin của từng vạch | Không làm lại. Phải chịu được lỗi còn lại của lane model (tài liệu Yêu cầu phần mềm Path Planner, mục 8) |
| Tính DLC, v_lat, TLC cho hai phía, kèm độ bất định | Làm (mục 3) | Dùng lại TLC để chọn thời lượng path |
| Xét bên kia vạch có nguy hiểm không | Làm (mục 3.2 và 6) | Không làm |
| Đoán ý định tài xế | Làm (mục 5) | Chỉ nhận cờ driver_override |
| Cảnh báo tài xế theo R79 | Làm (mục 7) | Báo khi path đã chạm giới hạn a_y |
| Phân xử, lập path, giới hạn, điều kiện kết thúc, chịu lỗi | Không làm | Làm (tài liệu Thiết kế tính năng Path Planner) |
| Phanh, giảm tốc (ACC, AEB) | Ngoài phạm vi G1 | Ngoài phạm vi G1. Như xe thật, ngang và dọc là hai khối tách riêng, trao đổi ràng buộc; simulator dùng ACC chạy thử (tài liệu Thiết kế tính năng Path Planner, mục 6.1) |
| Giới hạn mô-men lái, lực ghi đè ≤ 50 N | Không làm | Không đặt mô-men, nhưng **path phải nằm trong ngân sách** a_y, jerk, góc và tốc độ lái (tài liệu Yêu cầu phần mềm Path Planner, mục 5.1 và 7). Nhờ vậy controller bám được với mô-men trong giới hạn, và tài xế vẫn ghi đè được |

## 3. Các đại lượng khối ADAS tính

Các ký hiệu: v là tốc độ xe, v_y là vận tốc ngang tại tâm trục sau, r là yaw rate, x_f là khoảng cách từ tâm trục sau tới trục trước (bằng chiều dài cơ sở), W là bề rộng xe. Vạch trái trong base_link là `y_L(x) = c0 + c1·x + c2·x² + c3·x³`, y dương sang trái.

| Đại lượng | Cách tính | Ý nghĩa | Trạng thái |
|---|---|---|---|
| DLC_L | `y_L(x_f) − W/2` | Khoảng cách còn lại từ mép ngoài lốp trước bên trái tới mép trong của vạch trái. Giống định nghĩa DTLE của Euro NCAP, chỉ khác tên | đề xuất |
| v_lat_L | `v_y + r·x_f − v·y_L'(x_f)`, với `y_L'(x) = c1 + 2·c2·x + 3·c3·x²` | Tốc độ DLC_L giảm, tức xe tiến về vạch trái nhanh cỡ nào. Công thức này đã kết hợp ba nguồn: góc vạch từ camera, v_y từ khối ước lượng trạng thái, r từ IMU | đề xuất |
| TLC_L | `DLC_L / v_lat_L` nếu v_lat_L ≥ 0,05 m/s; ngược lại coi là vô cùng | Thời gian tới lúc chạm vạch, giả định v_lat không đổi (cùng giả định với DTLE) | đề xuất |
| Phía phải | Đối xứng: `DLC_R = −y_R(x_f) − W/2`, `v_lat_R = −(v_y + r·x_f) + v·y_R'(x_f)` |   | đề xuất |

**Kiểm tra công thức v_lat.**

- Đường thẳng (c2 = c3 = 0, r = 0, v_y = 0), v = 25 m/s, c1 = −0,016 rad (vạch trái nghiêng dần vào xe): v_lat_L = −25·(−0,016) = **0,40 m/s**. Đây đúng là một mức trôi trong bài thử Euro NCAP.
- Xe bám đúng cua: r = v·κ, vạch có c1 = 0, c2 = κ/2. Khi đó `r·x_f = v·κ·x_f` và `v·y_L'(x_f) = v·κ·x_f`, hai số hạng triệt tiêu nên v_lat = 0, đúng như mong đợi.

### 3.1 Độ bất định của DLC, v_lat, TLC

**Ai làm việc gì.** Lọc nhiễu và kết hợp nhiều nguồn được làm **một lần, ở khối sinh ra dữ liệu**: Lane Model lọc Kalman các hệ số vạch, khối Ước lượng trạng thái (G2) ước lượng v_y, Ego-motion (G4) tính chuyển động. Mỗi khối gửi kèm phương sai. Khối ADAS và G1 **không lọc lại** từ cảm biến thô; nếu mỗi bên tự lọc một kiểu, hai bên sẽ thấy hai làn khác nhau. Nhưng cả hai **phải chịu được phần lỗi còn lại**. Việc của khối ADAS là lan truyền phương sai sang DLC, v_lat, TLC, rồi dùng độ bất định khi quyết định.

**Lan truyền phương sai** (bậc một, bỏ qua tương quan giữa các hệ số):

- `σ_DLC ≈ √(σ_c0² + x_f²·σ_c1²)`
- `σ_vlat ≈ √(v²·σ_c1² + σ_vy²)`
- `σ_TLC ≈ TLC·√((σ_DLC/DLC)² + (σ_vlat/v_lat)²)`

Với số liệu mức nhiễu Lane Model trong [Thiết kế tính năng Path Planner](report.html?doc=thiet-ke-path-planner&lang=vi#lane-faults) (σ_c0 = 0,03 m, σ_c1 = 0,002 ban ngày, gấp 2,5 lần ban đêm hoặc khi mưa), x_f = 2,9 m, v = 25 m/s, xe đang ở DLC = 0,40 m và v_lat = 0,40 m/s (TLC = 1,0 s), bỏ qua σ_vy:

| Điều kiện | σ_DLC | σ_vlat | σ_TLC | Đọc số thế nào |
|---|---|---|---|---|
| Ban ngày | 0,031 m | 0,05 m/s | 0,15 s | TLC thật nằm trong khoảng 0,7–1,3 s (±2σ). Đủ tin để kích hoạt |
| Ban đêm hoặc mưa | 0,077 m | 0,125 m/s | 0,37 s | Khoảng ±2σ là 0,3–1,7 s. Một trôi chậm 0,2 m/s gần như không phân biệt được với nhiễu |

Phần lớn nhiễu đến từ góc vạch c1 nhân với tốc độ, không phải từ khoảng cách c0. Ở 25 m/s, sai 0,002 rad trên c1 đã thành sai 0,05 m/s trên v_lat.

**Nguồn cho các quy tắc dưới đây.** Không quy định hay tiêu chuẩn nào cho con số. Hai nguồn có tiếng nói chỉ cho nguyên tắc:

- **ISO 21448 (SOTIF)** đòi phân tích các điều kiện làm perception kém (đêm, mưa, vạch mờ) và có biện pháp để chúng không gây can thiệp sai.
- **Euro NCAP** (Assessment 4.3.3.5) đòi hãng chứng minh hệ thống không can thiệp ngoài ý muốn tài xế.

Cách làm cụ thể (ngưỡng tin cậy 2σ, giữ qua nhiều frame) là kỹ thuật ước lượng thông thường. Các con số dưới đây là lựa chọn thiết kế, sẽ chỉnh bằng benchmark.

| Quy tắc | Ngưỡng | Lý do | Trạng thái |
|---|---|---|---|
| Chắc chắn xe đang trôi về phía vạch | v_lat − 2·σ_vlat ≥ 0,05 m/s | Không kích hoạt chỉ vì nhiễu làm v_lat đổi dấu. Ban ngày: cần v_lat ≥ 0,15 m/s. Ban đêm: cần v_lat ≥ 0,30 m/s | đề xuất |
| Khi chưa chắc về hướng | Chỉ dùng ngưỡng DLC (LKA: DLC ≤ 0,1 m) | Trôi chậm ban đêm vẫn được bắt khi lốp đã sát vạch. DLC ít nhiễu hơn nhiều so với v_lat | đề xuất |
| Quá nhiễu thì không khả dụng | σ_TLC > 0,5 s, hoặc confidence vạch < 0,6 | Báo UNAVAILABLE thay vì kích hoạt dựa trên số không tin được | đề xuất |
| Giữ điều kiện qua hai frame camera | Điều kiện kích hoạt LKA đúng ở hai lần cập nhật lane model liên tiếp (khoảng 50–100 ms) | Chống kích hoạt vì một frame lỗi. Không áp dụng cho ELK, vì ELK đã kích hoạt muộn | đề xuất |

### 3.2 Đánh giá xe ở làn bên (dùng cho ELK phần vật thể)

Phần này trả lời câu hỏi "làn bên có an toàn để xe mình lấn sang không".

**Bước 1. Chọn vật thể cần xét.** Từ danh sách perception, lấy vật thể ở làn phía xe đang trôi tới. Gán làn bằng lane model, cùng cách G1 làm. Chỉ xét vật thể có existence_probability ≥ 0,7 và đã thấy ít nhất 3 frame liền.

**Bước 2. Dự đoán vị trí.** Giả định vật thể giữ nguyên vận tốc, giống giả định của G1 trong tầm nhìn 2–3 s. Chỉ cần vị trí dọc theo làn, tức x so với xe mình.

**Bước 3. Xác định cửa sổ xung đột.** Xe mình bắt đầu lấn sang làn bên sau TLC giây. Nếu không ai can thiệp, xe còn ở một phần trong làn bên khoảng 2 s nữa. Vậy cửa sổ là `[TLC, TLC + 2,0 s]`.

**Bước 4. Kiểm tra chồng nhau.** Vẽ một hộp quanh thân xe mình, nới mỗi đầu 2 m. Làn bên **không an toàn** nếu trong cửa sổ xung đột có lúc vật thể nằm trong hộp này.

**Bước 5. Kích hoạt.** ELK phần vật thể gửi REQUEST khi TLC ≤ 0,8 s và làn bên không an toàn. Nếu tài xế đang **chuyển làn có chủ đích** (có xi-nhan), dùng thêm quy tắc chặt hơn ở bước 6.

**Bước 6. Khi tài xế chuyển làn có chủ đích.** Trên đường thật, tài xế bật xi-nhan rồi chuyển làn thường nghĩ xe sau sẽ phanh. Nếu ELK kéo xe lại mỗi lần có xe ở phía sau, tài xế sẽ thấy hệ thống cản mình. Vì vậy, khi có xi-nhan, ELK chỉ can thiệp khi xe sau **không thể phanh kịp một cách hợp lý**, tức khi một trong ba điều sau đúng:

- Xe kia đang ngang hàng: chồng lên thân xe mình, nới 1 m, trong khoảng [TLC, TLC + 1 s].
- TTC của xe sau tới đuôi xe mình ≤ 1,5 s.
- Xe sau cần giảm tốc hơn 3 m/s² để không chạm. Mức này được tính là `Δv² / (2·khoảng cách)`.

Ngoài ba trường hợp trên thì chỉ cảnh báo (kiểu cảnh báo điểm mù), không lái.

Ví dụ ở 72 km/h (20 m/s), giống bài thử Euro NCAP:

| Trường hợp | Số liệu | Tính | Kết luận |
|---|---|---|---|
| Xe ngược chiều | Chạy 20 m/s, đang ở phía trước 90 m. Tốc độ tiếp cận 40 m/s | TLC = 0,8 s thì cửa sổ là 0,8–2,8 s. Trong cửa sổ đó xe ngược chiều lại gần thêm 32–112 m. 90 m nằm trong khoảng này | Không an toàn: ELK REQUEST |
| Xe ngược chiều ở xa | Như trên nhưng ở phía trước 200 m | Sau 2,8 s xe đó vẫn còn cách 88 m | An toàn: không ELK. LKA vẫn có thể can thiệp nếu đang bật |
| Xe đang vượt, tài xế lơ đãng | Chạy 80 km/h, nhanh hơn mình 2,2 m/s; đầu xe đang ở sau đuôi xe mình 7 m | Sau 2,8 s xe đó tiến thêm 6,2 m, đầu xe còn cách đuôi xe mình 0,8 m, lọt vào phần nới 2 m | Không an toàn: ELK REQUEST |
| Xe đang vượt, tài xế bật xi-nhan, xe sau còn xa | Như trên nhưng cách 20 m | Xe sau chỉ cần giảm tốc 0,12 m/s², TTC 9 s | Chỉ cảnh báo, không ELK |
| Xe đang vượt, tài xế bật xi-nhan, xe sau rất gần | Nhanh hơn 5 m/s, cách 5 m | Cần giảm tốc 2,5 m/s², TTC 1,0 s ≤ 1,5 s | ELK REQUEST |
| Xe chạy cùng tốc độ ở làn bên, ngang hàng | Tốc độ tương đối 0 | Luôn nằm trong hộp | Không an toàn: ELK REQUEST, kể cả khi có xi-nhan |

Bài thử Euro NCAP với xe đang vượt, có xi-nhan, được thiết kế sao cho đầu xe vượt tới ngang trục sau xe mình đúng lúc va chạm. Trường hợp đó rơi vào điều thứ nhất ("đang ngang hàng"), nên quy tắc ở bước 6 vẫn đạt bài thử.

**Vì sao ngưỡng là 0,8 s, sớm hơn 0,6 s của ELK vạch liền.** Với vạch liền, lấn qua vạch một chút chưa gây tai nạn: Euro NCAP cho lấn tới 0,3 m. Với xe ở làn bên, chỉ cần chạm là tai nạn. Euro NCAP coi bài thử là trượt khi khoảng cách ngang giữa hai xe còn dưới 0,3 m. Kích hoạt ở 0,8 s giữ được mép lốp cách vạch 0,09–0,29 m.

## 4. Điều kiện chung để một chức năng có hiệu lực

Nếu một điều kiện ở đây không thoả mãn, chức năng đó không được gửi REQUEST, dù tình huống trông như cần can thiệp.

**Về nguồn của các con số.** Ngoài dải tốc độ 65–70–130 km/h (EU ELKS), không quy định nào cho sẵn con số cho các điều kiện này. R79 5.6.2.3.1.1 chỉ yêu cầu hãng tự khai báo điều kiện kích hoạt và giới hạn hoạt động. R171 có danh sách điều kiện để vào chế độ active, và ví dụ các điều kiện hãng tự khai (bề rộng làn, loại đường, thời điểm trong ngày, thời tiết). Vì vậy các ngưỡng dưới đây là lựa chọn thiết kế.

| Điều kiện | HWA | LKA | ELK | Căn cứ | Trạng thái |
|---|---|---|---|---|---|
| Cài đặt | Tài xế đã bấm nút và ACC đang bật | Đang bật trong menu (mặc định bật) | Đang bật (mặc định bật, tự bật lại mỗi lần khởi động) | R79 5.6.2.1.2; EU 2021/646 3.2.1 | đã chốt |
| Tốc độ | 10–130 km/h. Dưới 10 km/h thì chờ, ACC vẫn giữ xe | Kích hoạt từ 70 km/h; khi giảm tốc vẫn giữ tới dưới 65 km/h. Tối đa 130 km/h | Như LKA | EU 2021/646 3.6.1: ELKS chạy ít nhất 70–130 km/h, trễ ngưỡng xuống 65 km/h. R79 B1: bảng giới hạn bắt đầu từ 10 km/h | đã chốt |
| Vạch phía xe đang trôi tới | Hai vạch, hoặc một vạch cộng bề rộng làn nhớ được | status MEASURED, confidence ≥ 0,6, tầm nhìn ≥ 20 m | Như LKA. Với mép đường: type ROAD_EDGE hoặc BARRIER, confidence ≥ 0,7 | Không có số trong quy định; chọn để tránh can thiệp vì vạch ảo | cần chốt |
| Vạch hoặc mép đường kém tin | — | Không thoả dòng trên thì không can thiệp: gửi UNAVAILABLE | Như LKA. Mép đường đo không ổn định thì ELK phía đó UNAVAILABLE; planner không phải tự vẽ path từ một mép đường không tin được | Mentor xác nhận: ở L2 tài xế chịu trách nhiệm chính, nên phản ứng trên input không chắc chắn nguy hiểm hơn không can thiệp | mentor |
| ESC | ESC đang can thiệp: HWA tiếp tục | ESC đang can thiệp hoặc ESC bị tắt: chặn | Như LKA | EU 2021/646 3.2.2 và 3.3.2 cho phép tự tắt khi ESC bị tắt, và chặn khi ESC can thiệp | đã chốt |
| Lỗi input | Lane model, vật thể, tốc độ hoặc góc lái không hợp lệ: chức năng không khả dụng | Như HWA | Phần vật thể của ELK chỉ cần perception hợp lệ | Thẻ Path Planner, mục khi input không hợp lệ | cần chốt |

**Điều kiện riêng để bật HWA.** Khi tài xế bấm nút, HWA chỉ vào được khi thêm các điều kiện sau thoả. Nếu không, khối ADAS từ chối và báo cho tài xế. **Không tìm được quy định nào cho con số** lệch tâm, góc lệch hay khoảng cách tới vạch lúc bật HWA. Đây là con số hãng tự chọn và khai báo khi phê duyệt (R79 5.6.2.3.1.1).

| Điều kiện | Ngưỡng | Lý do | Trạng thái |
|---|---|---|---|
| Xe nằm trong làn | DLC ≥ 0,2 m cả hai phía | HWA không bắt đầu khi xe đang đè vạch | cần chốt |
| Lệch tâm | Tuyệt đối không quá 0,5 m | G1 đưa xe từ 0,5 m về giữa bằng a_y thêm vào ≤ 0,5 m/s² trong khoảng 3–4 s (tài liệu Thiết kế tính năng Path Planner) | cần chốt |
| Góc lệch so với làn | Không quá 2° | Ở 25 m/s, 2° tương đương v_lat 0,87 m/s, gần mức coi là có chủ đích (1,0 m/s) | cần chốt |
| Tay trên vô lăng | Có | R79 5.6.2.2.5: B1 phải phát hiện được tay | đã chốt |
| Xi-nhan | Tắt | Tài xế đang định chuyển làn thì không vào HWA | đã chốt |

## 5. Đoán ý định tài xế

Euro NCAP gọi phần này là DIM (Driver Intention Monitoring): phân biệt lấn vạch có chủ đích và lấn vạch do lơ đãng, rồi chặn những can thiệp không mong muốn. Khối ADAS chỉ dùng tín hiệu có trên xe: mô-men tài xế (EPS), góc và tốc độ quay vô lăng, xi-nhan, tốc độ xe.

Đổi lực sang mô-men: R79 giới hạn lực ghi đè **50 N đo ở vành vô lăng**. Với bán kính vành khoảng 0,19 m, 50 N ứng với khoảng **9,5 Nm**. Euro NCAP chặt hơn: với hệ thống dùng LKA vạch đứt làm ELK mà không có DIM, mô-men ghi đè phải **≤ 3,5 Nm**.

| Tình huống | Dấu hiệu đo được | Ngưỡng | Khối ADAS kết luận | Căn cứ | Trạng thái |
|---|---|---|---|---|---|
| Lơ đãng, xe tự trôi | Mô-men tài xế nhỏ, vô lăng gần như đứng yên, xi-nhan tắt | Trị tuyệt đối T_drv < 0,5 Nm và tốc độ quay vô lăng < 15 °/s, giữ 0,5 s | Không chủ đích: được kích hoạt | Euro NCAP: trước lúc trôi, tốc độ quay vô lăng phải trong 0 ± 15 °/s; tài xế giữ vô lăng thụ động | đã chốt |
| Chuyển làn có xi-nhan | Xi-nhan bật về phía xe đang trôi, hoặc vừa tắt chưa tới 2 s | — | Chủ đích: chặn LKA và phần vạch của ELK. Phần vật thể của ELK chỉ can thiệp theo quy tắc chặt ở mục 3.2, bước 6 | Euro NCAP thử ELK xe đang vượt cả khi tài xế bật xi-nhan 1,0 ± 0,5 s trước lúc đánh lái, v_lat 0,5–0,7 m/s, yêu cầu không va chạm | đã chốt |
| Chuyển làn không xi-nhan | Tài xế chủ động lái về phía vạch | T_drv ≥ 1,5 Nm hướng về phía vạch, giữ ≥ 0,2 s, hoặc tốc độ quay vô lăng ≥ 30 °/s về phía vạch | Như dòng trên | Không có số trong quy định; chọn nằm giữa mức thụ động (0,5 Nm) và mức ghi đè (3,0 Nm) | đã chốt |
| Tài xế ghi đè lúc đang can thiệp | Mô-men tài xế ngược chiều với hệ thống | T_drv ≥ 3,0 Nm ngược chiều can thiệp, giữ ≥ 0,1 s | Hủy yêu cầu, gửi OFF, bật driver_override. Không kích hoạt lại cùng phía trong 3 s | R79 5.1.6: tài xế phải ghi đè được bất cứ lúc nào bằng hành động có chủ đích. Ngưỡng 3,0 Nm thấp hơn 3,5 Nm của Euro NCAP và xa dưới 50 N của R79 | đã chốt |
| Bẻ lái gấp để tránh vật | v_lat lớn, xi-nhan tắt | v_lat > 1,0 m/s | Coi là thao tác né tránh có chủ đích: **chặn cả LKA và ELK**, kể cả khi làn bên có xe. Chỉ cảnh báo. Tài xế thấy thứ mà hệ thống không thấy (vật cản phía trước), nên lệnh tài xế được ưu tiên | Euro NCAP chỉ thử trôi không chủ đích tới 0,6 m/s và chuyển làn có chủ đích tới 0,7 m/s; R79 5.1.6: tài xế luôn được ghi đè | đề xuất |
| Tay rời vô lăng | Mô-men gần 0 liên tục | Trị tuyệt đối T_drv < 0,3 Nm | HWA: 10 s thì cảnh báo hình, 15 s thì hình đỏ và âm thanh, 30 s thì tắt HWA. LKA và ELK vẫn can thiệp, vì tài xế lúc đó có thể đã mất khả năng lái | R79 5.6.2.2.5 chỉ cho mức chậm nhất: cảnh báo hình 15 s, âm thanh 30 s, tắt 30 s sau khi bắt đầu âm thanh. Dự án chọn nhanh hơn: ở 25 m/s, 10 s đã là 250 m không cầm lái | đề xuất |

**Tài xế cố ý lao vào xe khác thì sao?** Hệ thống không chặn và không được phép chặn. Tài xế giữ vô lăng với mô-men ≥ 3,0 Nm thì ELK hủy. Đó là điều R79 bắt buộc, vì ở L2 tài xế luôn chịu trách nhiệm.

"An toàn" ở đây nghĩa là ba điều:

1. Ngân sách a_y có giới hạn (tài liệu Thiết kế tính năng Path Planner), để một lần kích hoạt sai cũng không đẩy xe vào tình huống tài xế không kịp xử lý.
2. Tài xế luôn ghi đè được, với lực ≤ 50 N.
3. Khối ADAS ghi log lần ghi đè và cảnh báo.

## 6. Bảng quyết định: khi nào gửi REQUEST

Mỗi chu kỳ 25 ms (40 Hz, như cả khối L2), khối ADAS xét từng phía và từng chức năng. Một chức năng được gửi REQUEST khi điều kiện chung (mục 4) thoả, ý định tài xế không chặn (mục 5), độ bất định cho phép (mục 3.1), chức năng không trong thời gian chờ sau ghi đè hoặc sau COMPLETED, và điều kiện riêng dưới đây đúng.

**Bên kia vạch có gì.** Khối ADAS dùng các trường type và crossable của lane model cùng danh sách vật thể:

| Bên kia vạch | Ví dụ | Chức năng phụ trách | Trạng thái |
|---|---|---|---|
| Làn trống, vạch được phép vượt (crossable = true, thường là vạch đứt) | Cao tốc nhiều làn, làn bên trống | LKA nếu đang bật. Nếu LKA tắt thì không ai can thiệp | đã chốt |
| Vạch không được vượt (crossable = false: SOLID, DOUBLE) | Vạch liền giữa hai chiều | LKA trước (TLC lớn hơn), ELK nếu LKA tắt hoặc chưa đủ | đã chốt |
| Mép đường (ROAD_EDGE, BARRIER) | Lề đất, cỏ, dải phân cách cứng | ELK | đã chốt |
| Có xe ngược chiều hoặc xe đang vượt trong cửa sổ xung đột (mục 3.2) | Đường hai chiều, xe đang tới; xe ở làn bên từ phía sau | ELK; khi có xi-nhan thì theo bước 6 của mục 3.2 | đã chốt |

**Ngưỡng kích hoạt.** LKA giữ ba phương án để chạy benchmark; ELK dùng một giá trị.

| Chức năng | Kích hoạt khi | Căn cứ | Trạng thái |
|---|---|---|---|
| LKA | TLC ≤ T_LKA, hoặc DLC ≤ 0,1 m với v_lat ≥ 0,05 m/s; và 0,1 ≤ v_lat ≤ 1,0 m/s. T_LKA chạy ba phương án: 0,6 s (muộn), 1,0 s (giữa), 1,5 s (sớm) | Euro NCAP: DTLE ≥ −0,3 m ở v_lat 0,2–0,6 m/s. ISO 17361: không cảnh báo sớm hơn khoảng TLC 1,5 s | cần chốt |
| ELK, vạch liền | TLC ≤ 0,6 s tới vạch đó | Euro NCAP và EU 2021/646: DTLE ≥ −0,3 m | cần chốt |
| ELK, mép đường | TLC ≤ 0,6 s tới mép đường | Euro NCAP: DTLE ≥ −0,1 m, chỉ cho một phần bánh trước ra ngoài | cần chốt |
| ELK, xe ngược chiều hoặc đang vượt | TLC ≤ 0,8 s tới vạch giữa, và làn bên không an toàn (mục 3.2) | Euro NCAP: không va chạm; bài thử coi là trượt khi khoảng cách ngang giữa hai xe dưới 0,3 m | cần chốt |

### 6.1 Ghi chú về ngưỡng TLC

- Quy định chỉ cho **kết quả phải đạt** (Euro NCAP, ELKS: lấn vạch ≤ 0,3 m, mép đường ≤ 0,1 m, không chạm xe) và **giới hạn sớm** (ISO 17361: không cảnh báo sớm hơn khoảng TLC 1,5 s). Ngưỡng TLC là lựa chọn thiết kế nằm giữa hai giới hạn này.
- TLC tối thiểu theo vật lý, với trễ 0,2 s: LKA đạt Euro NCAP chỉ cần khoảng 0,4 s; LKA không chạm vạch cần 0,4–0,7 s; ELK mép đường cần 0,3–0,5 s.
- Nhiễu ban đêm (σ_TLC ≈ 0,37 s) cần thêm phần dư khoảng 0,3–0,4 s.
- LKA sớm và nhẹ (1,5 m/s²), ELK muộn và mạnh (3,0 m/s²); ELK là lưới an toàn cuối.
- Benchmark chạy ba phương án của LKA trên S4–S8 (mức lấn vạch) và S10 (kích hoạt thừa), rồi mới chốt.

**Khi hai phía cùng có yêu cầu.** Việc này chỉ xảy ra khi làn hẹp, hoặc khi xe vừa bị kéo khỏi một phía lại trôi sang phía kia. Khối ADAS gửi phía có TLC nhỏ hơn. G1 vẫn phân xử theo ưu tiên ELK > LKA > HWA.

**Trả lại STANDBY và kích hoạt lại.**

| Sự kiện | Khối ADAS làm gì | Trạng thái |
|---|---|---|
| G1 báo COMPLETED | Đưa chức năng về STANDBY. Kích hoạt lại cùng phía khi DLC đã ≥ 0,3 m rồi lại giảm, hoặc sau 2 s | đã chốt |
| Tài xế ghi đè | Gửi OFF ngay. Không kích hoạt lại cùng phía trong 3 s, trừ phần vật thể của ELK | đã chốt |
| Tốc độ xuống dưới 65 km/h giữa lúc can thiệp | Giữ REQUEST tới khi G1 báo COMPLETED, không kích hoạt lần mới | đã chốt |
| Vạch phía đó mất giữa lúc can thiệp | Giữ REQUEST. G1 tự bám path cũ tối đa T_coast = 1 s rồi báo path không hợp lệ | đã chốt |

## 7. Cảnh báo tài xế (khối ADAS gửi HMI)

Trong simulator, phần này chỉ ghi log để kiểm tra. Không có HMI thật.

| Sự kiện | Cảnh báo | Căn cứ | Trạng thái |
|---|---|---|---|
| Mỗi lần LKA hoặc ELK can thiệp | Đèn báo ngay, giữ ít nhất 1 s hoặc tới hết lần can thiệp | R79 5.1.6.1.1; EU 2021/646 3.6.4.1 | đã chốt |
| Can thiệp dài hơn 10 s | Âm thanh tới hết lần can thiệp | R79 5.1.6.1.2.1 | đã chốt |
| Can thiệp lần thứ hai trong 180 s mà tài xế không đánh lái | Âm thanh từ lần thứ hai. Từ lần thứ ba, mỗi lần dài hơn lần trước ít nhất 10 s | R79 5.1.6.1.2.2 | đã chốt |
| ELK phần vật thể (ESF) | Đèn và âm thanh hoặc rung, từ lúc bắt đầu tới hết can thiệp | R79 5.1.6.2.6 | đã chốt |
| Chuyển làn có xi-nhan, xe sau còn phanh kịp (mục 3.2, bước 6) | Cảnh báo kiểu điểm mù, không lái | Lựa chọn thiết kế | đề xuất |
| HWA chạm giới hạn aysmax và lốp trước bắt đầu đè vạch | Vẫn hỗ trợ trong khả năng, không thả đột ngột; đèn kèm âm thanh hoặc rung. Dùng cờ lateral_limit_reached của G1 và DLC | R79 5.6.2.2.3 | đã chốt |
| G1 báo path không hợp lệ | Yêu cầu tài xế cầm lái, giảm mô-men từ từ | Quy ước của nhóm | đã chốt |
| Tài xế tắt ELK | Đèn báo liên tục khi ELK đang tắt | EU 2021/646 3.2.3 | đã chốt |

## 8. Trường hợp biên: phần của khối ADAS

Bảng này chỉ ghi khối ADAS làm gì. Phần G1 làm gì (path, chuyển tiếp) nằm ở mục Trường hợp biên của tài liệu Thiết kế tính năng Path Planner, cùng số thứ tự.

**Chia việc ngang và dọc.** G1 lo phần ngang. Phanh và giảm tốc là việc của ACC và AEB. Như xe thật, ngang và dọc là hai khối tách riêng, trao đổi ràng buộc; simulator dùng ACC chạy thử (tài liệu Thiết kế tính năng Path Planner, mục 6.1).

| # | Tình huống | Khối ADAS làm gì | Trạng thái |
|---|---|---|---|
| 1a | HWA đang chạy, xe mình trôi về phía làn bên có xe (ví dụ do gió ngang vượt sức HWA) | Gửi ELK REQUEST như bình thường. EU 2021/646 3.3.2 cho phép chặn ELKS khi một chức năng khác đang điều khiển ngang; dự án chọn không chặn | cần chốt |
| 1b | HWA đang chạy, xe mình ở giữa làn, **xe khác** lấn sang làn mình | **Không gửi ELK**, vì xe mình không trôi (TLC lớn). G1 dời tâm, ACC chọn xe đó làm mục tiêu (tài liệu Thiết kế tính năng Path Planner, mục 6.1) | cần chốt |
| 2 | HWA vào cua gắt hơn aysmax | Đọc cờ lateral_limit_reached và DLC; cảnh báo khi lốp bắt đầu đè vạch (R79 5.6.2.2.3). Gửi ELK nếu tới ngưỡng ELK và bên kia nguy hiểm | cần chốt |
| 3 | Tài xế ghi đè HWA | Bật driver_override khi T_drv ≥ 3,0 Nm; HWA vẫn bật | đã chốt |
| 4 | Tài xế bật xi-nhan chuyển làn, xe đang vượt tới từ phía sau | Theo mục 3.2, bước 6: ELK REQUEST chỉ khi xe kia đang ngang hàng, TTC xe sau ≤ 1,5 s, hoặc xe sau cần giảm tốc hơn 3 m/s²; còn lại chỉ cảnh báo. Không gửi nếu lốp trước đã sang quá 0,3 m qua vạch | đề xuất |
| 5 | Tài xế bật xi-nhan, đè vạch liền hoặc ra lề có chủ đích | Nếu chưa can thiệp: không kích hoạt. Nếu đang can thiệp: gửi OFF, cancel_reason = INDICATOR, tức trả quyền cho tài xế. Phần vật thể của ELK theo mục 3.2, bước 6 | đề xuất |
| 6 | Xe trôi qua lại giữa hai vạch (tài xế buồn ngủ) | Mỗi lần trôi là một yêu cầu mới, cùng ngưỡng. Kích hoạt lại theo quy tắc mục 6. Cảnh báo tăng dần theo R79 (từ lần thứ hai trong 180 s). Ghi log số lần | đề xuất |
| 7 | Tài xế chuyển làn xong, lane model báo lane_change | Hủy yêu cầu đang chờ, tính lại DLC, TLC theo làn mới; không kích hoạt trong 1 s | đã chốt |
| 8 | c0 jump làm DLC nhảy 0,3–1 m trong một frame | Lane Model không gửi cờ báo nhảy. Frame bị hàm kiểm tính nhất quán của đường biên đánh dấu là nhảy (hàm dùng chung với G1, tài liệu Thiết kế tính năng Path Planner, mục 4): không kích hoạt và không hủy dựa trên frame đó; tạm dự đoán DLC từ giá trị cũ cộng chuyển động. Dùng DLC mới khi frame liền sau xác nhận (lệch dưới 0,1 m). Nếu DLC mới thật sự nhỏ (làn hẹp lại) thì kích hoạt bình thường. Quá 0,5 s không xác nhận được thì UNAVAILABLE | đề xuất |
| 9 | Vật thể ảo | Chỉ tính vật thể có existence ≥ 0,7 và đã thấy ít nhất 3 frame liền (0,15 s) | đã chốt |
| 10 | Xe ngược chiều ở làn bên nhưng xe mình không trôi | Không gửi ELK: cần cả TLC ≤ 0,8 s lẫn làn bên không an toàn | đã chốt |
| 11 | Mất cả hai vạch giữa lúc can thiệp | Giữ REQUEST; khi G1 báo path không hợp lệ thì yêu cầu tài xế cầm lái | đã chốt |
| 12 | ESC can thiệp trong lúc LKA hoặc ELK đang can thiệp | Gửi OFF, nhường cho ESC | đã chốt |
| 13 | Tốc độ giảm dưới 65 km/h giữa lúc can thiệp | Giữ yêu cầu đang chạy tới COMPLETED, không kích hoạt lần mới | đã chốt |
| 13b | Cao tốc tắc đường, 0–60 km/h | LKA, ELK: UNAVAILABLE. HWA vẫn có hiệu lực nếu đang bật (10–130 km/h), tức chế độ Traffic Jam Assist. HWA tắt thì không có hỗ trợ ngang | đề xuất |
| 15 | Tài xế bấm HWA khi xe lệch tâm 0,4 m | Cho vào HWA (dưới 0,5 m) | đã chốt |
| 16 | Tài xế bẻ lái gấp (v_lat > 1,0 m/s) để tránh vật, làn bên có xe | Chặn cả LKA và ELK, chỉ cảnh báo (mục 5) | đề xuất |

## 9. Input của khối ADAS giả

| Cách | Khối giả đọc gì | Ví dụ ban đêm, trôi 0,4 m/s | Ưu | Nhược |
|---|---|---|---|---|
| A. Đọc message như G1 | Lane model, vật thể, CAN đã đi qua mô hình cảm biến, có nhiễu, trễ, mất frame bơm vào | TLC đo được dao động ±0,37 s, nên LKA kích hoạt sớm hoặc muộn vài trăm ms tuỳ lần chạy; c0 jump có thể làm kích hoạt sai | Giống xe thật: lỗi camera ảnh hưởng cả lúc kích hoạt lẫn path | Nếu xe lấn vạch 0,35 m, khó biết do planner hay do kích hoạt muộn |
| B. Đọc dữ liệu thật của kịch bản | DLC, v_lat, vị trí xe khác lấy thẳng từ simulator, không nhiễu | LKA kích hoạt theo TLC thật và ngưỡng của phương án đang thử (mục 6) | Tách được: mọi sai lệch là của planner | Không thật |

**Đã chốt:** làm cả hai, chọn bằng một cờ trong file kịch bản. Điểm của G1 chấm ở chế độ B; chế độ A dùng để báo cáo độ bền của cả chuỗi. Log luôn ghi cả TLC đo được lẫn TLC thật.

Tín hiệu tài xế (mô-men, tốc độ quay vô lăng, xi-nhan) và cài đặt (nút HWA, menu LKA, ELK) lấy từ tài xế giả và file kịch bản, ở cả hai chế độ.

**Tần số và đơn vị của tín hiệu tài xế**, theo signal list nhóm Motion của mentor:

| Tín hiệu | Tên trên xe | Tần số | Đơn vị trên xe | Dùng cho | Trạng thái |
|---|---|---|---|---|---|
| Mô-men tài xế | Driver steering torque | 50 Hz | Nm | Lơ đãng, chủ đích, ghi đè, tay rời (mục 5). Ngưỡng ghi đè giữ 0,1 s tức 5 mẫu; ngưỡng chủ đích giữ 0,2 s tức 10 mẫu | mentor |
| Góc vô lăng | Steering wheel angle | 100 Hz | ° | Tình huống và log | mentor |
| Tốc độ quay vô lăng | Steering wheel speed | 100 Hz | °/s | Ngưỡng 15 °/s và 30 °/s ở mục 5 dùng thẳng đơn vị của xe | mentor |
| Tốc độ xe | Vehicle speed | 50 Hz | km/h | Dải tốc độ 65–130 km/h ở mục 4 dùng thẳng đơn vị của xe | mentor |
| Xi-nhan, nút HWA, cờ ESC | Chưa có, vì danh sách mới là nhóm Motion | — | — | Mục 4, 5 và trường hợp biên 12 | cần chốt |

Khối ADAS chạy 40 Hz nên mỗi chu kỳ nhận 1 hoặc 2 mẫu mô-men; các ngưỡng tính theo thời gian giữ, không theo số chu kỳ.

## 10. Output của khối ADAS giả {#function-requests}

Khối giả gửi đúng message `FunctionRequests` như khối thật qua pub/sub ở 40 Hz. Trễ giả định khoảng 20 ms, timeout 75 ms và tuổi tối đa 45 ms. Dùng [header chung](report.html?doc=interface-he-thong&lang=vi#header) không có `frame_id`, stamp là thời điểm gửi yêu cầu. Mảng `requests[3]` xếp theo HWA, LKA, ELK.

| Trường | Kiểu | Vì sao cần | Trạng thái |
|---|---|---|---|
| state (mỗi chức năng) | uint8 enum { OFF, UNAVAILABLE, STANDBY, REQUEST, FAULT } | OFF là tài xế tắt; UNAVAILABLE là đang bật nhưng điều kiện chung chưa thoả (dưới 70 km/h, vạch kém, quá nhiễu); FAULT là lỗi. G1 xử lý OFF, UNAVAILABLE, FAULT như nhau, nhưng log và kịch bản thử phân biệt được | đã chốt |
| side (mỗi chức năng) | uint8 enum { NONE, LEFT, RIGHT } | Phía xe đang trôi. ELK dùng phía này để siết biên. HWA dùng NONE | đã chốt |
| tlc (mỗi chức năng) | float32, s | ADAS tính, G1 dùng để chọn thời lượng path. HWA bỏ qua | đã chốt |
| elk_reason (mỗi chức năng) | uint8 enum { NONE, SOLID_LINE, ROAD_EDGE, ONCOMING, OVERTAKING } | Chỉ ghi log | đã chốt |
| driver_override | bool, chung cho message | Tài xế đang ghi đè (T_drv ≥ 3,0 Nm) | đã chốt |
| cancel_reason (mỗi chức năng) | uint8 enum { NONE, DRIVER_OVERRIDE, INDICATOR, SPEED, LANE_QUALITY, ESC, FAULT } | Chỉ để ghi log: biết vì sao một yêu cầu bị hủy | đã chốt |

Khối giả nhận lại `PathStatus` từ G1: path_valid, active_function, intervention_phase (đã chốt), và cờ lateral_limit_reached (cần chốt; định nghĩa, yêu cầu và lý do ở tài liệu Yêu cầu phần mềm Path Planner, mục 5.1).

Ngoài message gửi G1, khối giả ghi thêm một message `HmiStatus`, chỉ để ghi log và đánh giá: cảnh báo đèn, âm thanh, mức cảnh báo tay rời vô lăng, số lần can thiệp trong 180 s.

## 11. Còn cần chốt

1. **Ngưỡng kích hoạt** (mục 6): LKA chạy ba phương án 0,6 / 1,0 / 1,5 s trong benchmark; ELK vạch liền và mép đường 0,6 s; ELK vật thể 0,8 s.
2. **Chất lượng vạch** và **lỗi input** trong điều kiện chung (mục 4).
3. **Điều kiện bật HWA** (mục 4): DLC ≥ 0,2 m, lệch tâm ≤ 0,5 m, góc ≤ 2°. Không có quy định cho con số.
4. **ELK phần vật thể** (mục 3.2): cửa sổ [TLC, TLC + 2 s], hộp nới 2 m; quy tắc chặt khi có xi-nhan (ngang hàng, TTC ≤ 1,5 s, giảm tốc cần > 3 m/s²).
5. **Độ bất định** (mục 3.1): xác nhận hướng bằng v_lat − 2σ, UNAVAILABLE khi σ_TLC > 0,5 s, giữ qua hai frame cho LKA.
6. **Bẻ lái gấp** (mục 5): chặn cả ELK, chỉ cảnh báo.
7. **Tay rời vô lăng** (mục 5): 10 / 15 / 30 s.
8. **ELK khi HWA đang chạy** (trường hợp biên 1a): chọn không chặn.
9. **Xe khác cắt vào làn** (trường hợp biên 1b): không phải ELK; G1 dời tâm, ACC giữ khoảng cách.

## Nguồn

- [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf), bản EUR-Lex: [eur-lex.europa.eu](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202500003)
- [Commission Implementing Regulation (EU) 2021/646, ELKS](https://eur-lex.europa.eu/eli/reg_impl/2021/646/2021-04-20/eng), đọc qua [bản sao LawPlayer](https://lawplayer.com/eu/act/32021R0646)
- [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf)
- [Euro NCAP Assessment Protocol Safety Assist Collision Avoidance v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf)
- [ISO 17361:2017, trang tóm tắt](https://standards.iteh.ai/catalog/standards/iso/c3d927a6-f4e1-4b4d-91d2-548cf5953983/iso-17361-2017) (chưa đọc bản gốc; số liệu vùng cảnh báo lấy từ nguồn thứ cấp)
- ISO 21448:2022, Road vehicles — Safety of the intended functionality (chưa đọc bản gốc)
- [UN Regulation No 171 (DCAS), EUR-Lex](https://eur-lex.europa.eu/eli/reg/2025/1899/oj/eng) (chưa đọc được bản gốc)
