# Hazard Analysis and Risk Assessment (HARA)

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-HARA` |
| Phiên bản | 1.2 |
| Trạng thái | Chờ confirmation review |
| Tác giả | thongbui |
| Người review |   |
| Cập nhật | 2026-11-11 |

## 1. Purpose and scope {#safety-scope}

- **Mục đích.** Phân tích hazard và đánh giá rủi ro cho hệ thống hỗ trợ lái ngang HWA, LKA, ELK theo ISO 26262-3 (concept phase); đề xuất S, E, C, ASIL và safety goal để phòng an toàn làm confirmation review.
- **Phạm vi.** Item definition, operational situation, hazard, hazardous event, safety goal, SOTIF triggering condition (ISO 21448), safety mechanism của path planner.
- **Ngoài phạm vi.** Functional safety concept, phân bổ ASIL xuống từng khối, technical safety concept; ACC và AEB; lỗi phần cứng của cảm biến và EPS.
- **Kết quả mong muốn từ phòng an toàn.** Xác nhận hoặc sửa S, E, C, ASIL ở mục 6; xác nhận safety goal ở mục 7; trả lời các điểm ở mục 10.

## 2. References {#safety-references}

| Tài liệu | Dùng cho |
|---|---|
| ISO 26262-3:2018, mục 6 và Phụ lục B | Quy trình HARA, thang S, E, C, bảng ASIL |
| ISO 26262-2:2018 | Confirmation review |
| ISO 21448:2022 | SOTIF triggering condition |
| [UN R79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf) | Phân loại ACSF B1, CSF, ESF; aysmax; lực ghi đè 50 N; cảnh báo; không thả lái đột ngột (5.6.2.2.3) |
| [EU 2021/646 (ELKS)](https://eur-lex.europa.eu/eli/reg_impl/2021/646/2021-04-20/eng) | ELK bắt buộc, dải tốc độ |
| Euro NCAP LSS v4.3, Assessment Protocol SA v10.4.1 | Kịch bản thử, mô-men ghi đè 3,5 Nm, DTLE |
| Software Requirements Specification, Software Architectural Design, ADAS Function Specification, Software Qualification Test Specification | Requirement, cách đáp ứng, kiểm chứng (tài liệu kèm, không cần để đọc tài liệu này) |

## 3. Item definition {#safety-item}

**Chức năng**

| Chức năng | Mô tả | Loại theo R79 | Bật |
|---|---|---|---|
| HWA | Giữ xe ở tâm làn liên tục, dời tâm khi có xe lớn ở làn bên | ACSF Category B1 | Tài xế bật bằng nút; cần ACC bật, tay trên vô lăng |
| LKA | Lái xe về trong làn khi xe trôi về vạch mà tài xế không chủ đích | CSF | Mặc định bật |
| ELK | Lái khẩn cấp khi xe sắp vượt vạch liền, ra mép đường, hoặc sắp va xe ngược chiều, xe đang vượt ở làn bên | CSF, ESF; ELKS | Mặc định bật mỗi lần khởi động |

**Ranh giới và interface**

| Phần | Nội dung |
|---|---|
| Trong item | Khối Chức năng ADAS (quyết định khi nào can thiệp); path planner (lập path ngang, arbitration); Lateral Controller; EPS (chấp hành) |
| Input từ ngoài item | Lane model (camera), perception (camera, radar), state estimator (v_y), ego-motion, CAN khung gầm (yaw rate, tốc độ, góc lái, mô-men tài xế), khối dọc (ACC) |
| Output | Mô-men hoặc góc lái qua EPS; cảnh báo HMI (đèn, âm thanh, rung) |
| Phản ứng khi lỗi | Path planner báo `path_valid = false`; Lateral Controller và EPS giảm mô-men về 0 theo dốc; HMI yêu cầu tài xế cầm lái |

**Giới hạn quyền lái** (safety mechanism, áp ở path planner)

| Chức năng | a_y tổng | a_y thêm vào | Jerk | Thời lượng một lần can thiệp |
|---|---|---|---|---|
| HWA | ≤ 2,5 m/s² (R79 cho tới 3 m/s²) | ≤ 0,5 m/s² (giá trị khởi đầu) | ≤ 5 m/s³ (R79) | Liên tục |
| LKA | ≤ 3,0 m/s² | ≤ 1,5 m/s² | ≤ 5 m/s³ | ≤ 10 s (R79) |
| ELK | ≤ 4,0 m/s² | ≤ 3,0 m/s² | ≤ 10 m/s³ | ≤ 10 s (R79) |

Tài xế ghi đè được bất cứ lúc nào: khối Chức năng ADAS hủy can thiệp khi mô-men tài xế ≥ 3,0 Nm giữ 0,1 s, dưới 3,5 Nm của Euro NCAP và xa dưới 50 N (khoảng 9,5 Nm) của R79.

**Operating conditions**

| Điều kiện | Giá trị |
|---|---|
| Tốc độ | HWA 10–130 km/h; LKA, ELK kích hoạt từ 70 km/h, giữ tới dưới 65 km/h, tối đa 130 km/h |
| Đường | Có vạch hoặc mép đường đủ tin; bề rộng làn 2,5–5,5 m, kể cả làn hỗn hợp ô tô và xe máy ở Việt Nam |
| Xe | Mọi xe gia đình, rộng tới 2,5 m kể cả gương (QCVN 09:2015/BGTVT) |
| Tài xế | Mức L2: tài xế giám sát và chịu trách nhiệm lái; HWA đòi tay trên vô lăng |

**Giả định**

- Input từ ngoài item có cờ hợp lệ, counter, CRC; input không hợp lệ được phát hiện trong một chu kỳ 25 ms.
- EPS giảm mô-men theo dốc khi path không hợp lệ; không thả mô-men đột ngột.
- Tài xế L2 chú ý và giữ vô lăng khi HWA bật.

## 4. Operational situations {#safety-situations}

E theo ISO 26262-3, Phụ lục B:

| Cách tính | E1 | E2 | E3 | E4 | Dùng cho |
|---|---|---|---|---|---|
| Thời lượng | — | Dưới 1 % thời gian lái | 1–10 % | Trên 10 % | OS-01 đến OS-04, OS-06 |
| Tần suất | Ít hơn một lần mỗi năm với đa số tài xế | Vài lần mỗi năm | Một lần mỗi tháng trở lên | Gần như mỗi chuyến | OS-05, OS-07 |

| ID | Tình huống | E đề xuất | Rationale |
|---|---|---|---|
| OS-01 | Cao tốc 90–130 km/h, có xe ngang hàng ở làn bên kề | E3 | Có xe ngang hàng là thường gặp nhưng không chiếm phần lớn thời gian lái |
| OS-02 | Đường hai chiều 70–90 km/h, có xe ngược chiều ở làn bên | E3 | Thường gặp ngoài đô thị Việt Nam; xe ngược chiều trong vùng xung đột chiếm phần nhỏ thời gian |
| OS-03 | Làn sát mép đường, lề hoặc rào chắn, 70–130 km/h | E4 | Hầu hết đường có làn sát mép |
| OS-04 | HWA đang lái trong cua R ≤ 500 m trên cao tốc | E3 | Cua có bán kính này chiếm phần nhỏ chiều dài cao tốc |
| OS-05 | Xe trôi không chủ đích về phía xe ngược chiều hoặc xe đang vượt | E1 | Cần đồng thời tài xế lơ đãng và xe khác trong vùng xung đột |
| OS-06 | HWA đang lái trên cao tốc | E4 | Tình huống dùng chính của HWA |
| OS-07 | Tài xế bẻ lái né vật cản trên làn | E2 | Vài lần mỗi năm |

## 5. Hazard identification {#safety-hazards}

Hazard là hành vi sai ở cấp xe, suy từ các kiểu lỗi chức năng: can thiệp khi không cần, sai hướng, quá mạnh, quá yếu hoặc quá muộn, mất đột ngột, giật, chống lại tài xế.

| ID | Hazard ở cấp xe | Lỗi chức năng dẫn tới |
|---|---|---|
| H1 | Can thiệp lái ngang không mong muốn: khi không cần, sai hướng hoặc quá mạnh | Path theo vạch nhận nhầm; arbitration sai; path vượt giới hạn quyền lái |
| H2 | Mất hỗ trợ lái đột ngột khi chức năng đang giữ xe | Path không hợp lệ đột ngột; path bị cắt mà không báo |
| H3 | Can thiệp không đủ hoặc quá muộn khi ELK cần can thiệp | Path can thiệp quá yếu hoặc bắt đầu muộn |
| H4 | Lệnh lái giật | Path nhảy bậc khi đổi chức năng hoặc khi lane model nhảy |
| H5 | Chống lại tài xế khi tài xế ghi đè hoặc né vật cản | Path kéo xe về làn trong lúc tài xế lái ra |

## 6. Hazardous events và ASIL đề xuất {#safety-hara}

**Thang.** S0 không thương tích; S1 nhẹ đến vừa; S2 nặng, có khả năng sống; S3 đe doạ tính mạng. C0 nói chung kiểm soát được; C1 ≥ 99 % tài xế tránh được; C2 ≥ 90 %; C3 < 90 %. ASIL tra theo ISO 26262-3 Bảng 4.

**Lập luận C.** Ngân sách a_y thêm vào giới hạn độ lệch ngang trước khi tài xế phản ứng: lệch ≈ ½·a·t². Trong 1 s: HWA 0,5 m/s² lệch 0,25 m; LKA 1,5 m/s² lệch 0,75 m; ELK 3,0 m/s² lệch 1,5 m. Vì vậy cùng hazard H1, sự kiện được tách theo quyền lái của chức năng.

| ID | Hazard | Chức năng | Tình huống | Hậu quả | S | E | C | ASIL |
|---|---|---|---|---|---|---|---|---|
| HE-01 | H1 | HWA, LKA | OS-01 | Va chạm bên ở tốc độ cao, mất lái | S3 | E3 | C2 | B |
| HE-02 | H1 | HWA, LKA | OS-02 | Va chạm trực diện | S3 | E3 | C2 | B |
| HE-03 | H1 | HWA, LKA | OS-03 | Lao ra lề, va rào chắn góc nhỏ | S2 | E4 | C2 | B |
| HE-08 | H1 | ELK | OS-01, OS-02 | Va chạm bên hoặc trực diện | S3 | E3 | C3 | C |
| HE-04 | H2 | HWA | OS-04 | Xe ra khỏi làn trong cua, va xe làn bên | S3 | E3 | C2 | B |
| HE-05 | H3 | ELK | OS-05 | Va chạm bên hoặc trực diện | S3 | E1 | C3 | A |
| HE-06 | H4 | HWA | OS-06 | Giật lái, lệch làn nhẹ | S2 | E4 | C1 | A |
| HE-07 | H5 | HWA, LKA, ELK | OS-07 | Va vào vật cản | S3 | E2 | C2 | A |

**Rationale**

| ID | S | C |
|---|---|---|
| HE-01, HE-02 | Va chạm với xe khác ở 70–130 km/h có thể gây mất lái và va chạm thứ cấp | a_y thêm vào ≤ 1,5 m/s²; tài xế L2 giữ vô lăng, ghi đè với 3 Nm |
| HE-03 | Ra lề hoặc va rào góc nhỏ thường gây thương tích nặng nhưng ít khi tử vong | Như HE-01 |
| HE-08 | Như HE-01, HE-02 | a_y thêm vào tới 3,0 m/s² đẩy xe lệch 1,5 m trong 1 s, nhanh hơn phản ứng của phần lớn tài xế |
| HE-04 | Ra khỏi làn trong cua ở tốc độ cao | Tài xế đang giữ vô lăng (HWA); R79 đòi cảnh báo và không thả đột ngột |
| HE-05 | Như HE-02 | Tài xế lơ đãng là điều kiện của tình huống. Ở L2, tình huống này tương đương xe không có ELK; xem mục 10 |
| HE-06 | Giật lái trong giới hạn quyền lái gây lệch nhỏ | Tài xế giữ vô lăng; bước nhảy bị giới hạn bởi giới hạn a_y và tốc độ quay của EPS |
| HE-07 | Va vào vật cản ở tốc độ cao | Can thiệp hủy khi mô-men tài xế ≥ 3 Nm; quyền lái có giới hạn |

## 7. Safety goals {#safety-goals}

FTTI của SG-01, SG-02 ước lượng bằng thời gian để xe lệch hết khoảng dư 0,5 m tới vạch dưới gia tốc a: t = √(2·0,5 / a). FTTI của SG-04, SG-05 là giá trị nhóm tự thống nhất, chưa có phép tính.

| ID | Safety goal | Hazardous event | ASIL đề xuất | Safe state | FTTI đề xuất |
|---|---|---|---|---|---|
| SG-01 | Tránh can thiệp lái ngang không mong muốn vượt giới hạn tài xế kiểm soát được | HE-01, HE-02, HE-03, HE-08 | C | Tắt hỗ trợ ngang, giảm mô-men về 0 theo dốc, không thả đột ngột (như SG-02), cảnh báo tài xế | 0,5 s (a = 3,0 m/s²: 0,58 s) |
| SG-02 | Không mất hỗ trợ lái đột ngột khi một chức năng đang lái | HE-04 | B | Tiếp tục hỗ trợ trong khả năng, rồi giảm mô-men theo dốc kèm cảnh báo (R79 5.6.2.2.3) | 0,5 s (a = 2,5 m/s²: 0,63 s) |
| SG-03 | Can thiệp đủ để giữ xe trong làn khi ELK được yêu cầu | HE-05 | A | Cảnh báo tài xế | — |
| SG-04 | Không tạo bước nhảy trong lệnh lái | HE-06 | A | Path không hợp lệ, giảm mô-men theo dốc | 0,1 s (nhóm tự thống nhất) |
| SG-05 | Không chống lại tài xế khi tài xế ghi đè | HE-07 | A | Hủy can thiệp | 0,3 s (nhóm tự thống nhất) |

## 8. SOTIF triggering conditions {#safety-sotif}

Giới hạn của cảm biến và thuật toán khi không có gì hỏng. Mỗi điều kiện có biện pháp trong path planner và được kiểm bằng test case (S) hoặc fault injection (F) trong Software Qualification Test Specification.

| ID | Triggering condition | Hạn chế có thể lộ ra | Biện pháp | Kiểm chứng |
|---|---|---|---|---|
| TC-01 | Vạch cũ, vết nứt, vết nhựa giống vạch | Lane model nhận nhầm vạch | Kiểm tính nhất quán của biên ở hai thang thời gian | F03 |
| TC-02 | Làn mở rộng: làn khẩn cấp, tách nhánh, thêm làn | Path dịch về phía mở rộng | Neo tâm làn vào biên ổn định | S6b |
| TC-03 | Ban đêm hoặc mưa | Nhiễu lane model gấp 2,5 lần | Bắt đầu từ path cũ, giới hạn tốc độ đổi tham chiếu, phạt jerk | F01, S12 |
| TC-04 | Đỉnh dốc che tầm nhìn trước cua | Thấy cua muộn | Giới hạn a_y; báo `lateral_limit_reached`, khối dọc giảm tốc | S1b |
| TC-05 | Cua gắt hơn aysmax | Path bị cắt, xe ra sát vạch | Như TC-04 | S1b |
| TC-06 | Đường ướt, μ = 0,5 | Lốp bám kém hơn giới hạn a_y | Giới hạn a_y của ELK 4,0 m/s² dưới mức bám 4,9 m/s² | S12 |
| TC-07 | Xe lớn ở làn bên, làn hẹp, vật ở hai bên | Dời tâm sai hướng hoặc quá sát | Dời ra xa xe lớn theo khoảng hở tới nó; hai bên có xe lớn thì đứng giữa; offset giới hạn theo khoảng trống thật | S3, S3b, S15 |
| TC-08 | Tắc đường, tốc độ thấp | Path chỉ phủ đoạn ngắn | HWA tiếp tục; LKA, ELK không khả dụng | S11 |
| TC-09 | Gió ngang, đường nghiêng ngang | Xe trôi dù path đúng | Vòng kín của Lateral Controller; LKA can thiệp | S4 |
| TC-10 | Mất mọi biên làn kéo dài | Dead reckoning tích luỹ sai | Bám path cũ tối đa 1 s rồi path không hợp lệ | F05 |
| TC-11 | Độ cong ước lượng sai ở xa | Path theo cua giả | Kết hợp độ cong camera với yaw rate và lịch sử path | F06 |
| TC-12 | Làn mình mất vạch, vạch làn bên hoặc mép đường còn thấy | Tâm làn suy từ biên xa bị lệch | Biên suy ra cần độ tin cao hơn; chỉ HWA dùng | F21 |
| TC-13 | Làn hẹp với xe rộng | Không đủ khoảng trống để giữ xe trong làn | Báo `lane_too_narrow`, HWA không khả dụng | S19 |

## 9. Safety mechanisms của path planner {#safety-mechanisms}

| Mechanism | Safety goal | Requirement |
|---|---|---|
| Giới hạn a_y, a_y thêm vào, jerk theo chức năng | SG-01 | PP-SWR-001, 003, 110 đến 115 |
| Arbitration theo ưu tiên, chỉ xét chức năng ở REQUEST | SG-01 | PP-SWR-030, 047 |
| Kiểm tính nhất quán của biên làn | SG-01 | PP-SWR-121, 122, 148 |
| Giữ hỗ trợ khi chạm giới hạn; bám path cũ tối đa 1 s khi mất biên | SG-02 | PP-SWR-005, 006, 037, 124 |
| Kiểm liên tục giữa hai path liên tiếp mỗi chu kỳ | SG-04 | PP-SWR-031, 100 đến 102, 126 đến 128 |
| Input không hợp lệ thì path không hợp lệ trong một chu kỳ | SG-01, SG-04 | PP-SWR-142, 143, 145 |
| Path bám vị trí xe khi tài xế ghi đè | SG-05 | PP-SWR-039, 040 |
| Giới hạn DTLE và khoảng cách tới xe ở làn bên | SG-03 | PP-SWR-086, 088 |

## 10. Open points for reviewer {#safety-open-points}

| # | Điểm cần phòng an toàn trả lời |
|---|---|
| 1 | Xác nhận hoặc sửa S, E, C, ASIL ở mục 6 |
| 2 | C3 của HE-08: ELK thêm tới 3,0 m/s² a_y, xe lệch 1,5 m trong 1 s |
| 3 | E3 của OS-01 (xe ngang hàng ở làn bên trên cao tốc) và OS-02 (xe ngược chiều trên đường hai chiều) trên đường Việt Nam |
| 4 | S2 của HE-03: ở Việt Nam lề đường thường ít rào chắn, có xe máy, người đi bộ, mương, cây. Nếu là S3 thì HE-03 lên ASIL C |
| 5 | S2 của HE-06: nếu hậu quả chỉ là lệch nhẹ trong làn thì có thể là S1 (khi đó QM); S2 khi xét xe lệch sang làn bên đang có xe |
| 6 | HE-05 (ELK can thiệp không đủ): nhóm đề xuất ASIL A, tra bảng từ S3, E1, C3. Phương án khác là QM: ở L2, ELK can thiệp không đủ thì tương đương xe không có ELK, tài xế vẫn chịu trách nhiệm lái |
| 7 | Phương pháp chứng minh C: thử với tài xế hay dựa vào nghiên cứu controllability đã công bố |
| 8 | FTTI ở mục 7: SG-01, SG-02 ước lượng theo động học; SG-04, SG-05 do nhóm tự thống nhất; SG-03 chưa có. Cần đối chiếu với thời gian phát hiện và phản ứng của path planner, Lateral Controller và EPS |
| 9 | Tiêu chí chấp nhận SOTIF (số lần can thiệp sai trên quãng đường); hiện Software Qualification Test Specification đòi 0 lần trên toàn bộ test case |
| 10 | Triggering condition chưa có test case: hầm, bóng đổ, chói nắng, vạch tạm ở công trường, làn hỗn hợp ô tô và xe máy. Nhóm sẽ bổ sung test case; xin xác nhận danh sách đã đủ chưa |

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-11-10 | Viết lại thành HARA gửi phòng an toàn. Item definition tự đọc được; thêm operational situation, S, E, C, ASIL, safe state, FTTI đề xuất; tách HE-08 cho ELK; thêm TC-13; thêm safety mechanism và open points |
| 1.1 | 2026-11-10 | Thêm cách tính E theo tần suất; ghi nguồn FTTI của SG-04, SG-05; safe state của SG-01 không thả mô-men đột ngột; tách open points, thêm câu hỏi về S của HE-03, HE-06; sửa lập luận ASIL của HE-05 |
| 1.2 | 2026-11-11 | TC-07 theo cách dời tâm mới (PP-ADR-008) |
