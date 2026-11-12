# ADAS Function Specification

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `ADAS-FS` |
| Phiên bản | 1.7 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-12 |

## 1. Purpose and scope {#adas-scope}

- **Mục đích:** Quy định khi nào khối Chức năng ADAS gửi yêu cầu HWA, LKA, ELK cho path planner, phía nào, với ngưỡng nào.
- **Phạm vi:** Điều kiện khả dụng, ý định tài xế, quyết định kích hoạt, kết thúc và kích hoạt lại, cảnh báo tài xế, message `FunctionRequests`.
- **Ngoài phạm vi:** Lập path, arbitration, giới hạn a_y (Software Architectural Design); HMI thật; khối dọc.
- **Trong simulator:** Khối chạy thử dùng đúng các ngưỡng ở tài liệu này và gửi đúng `FunctionRequests` như khối thật; không có camera trong xe, không có HMI thật. Cách chọn input của khối chạy thử (chế độ A, B) ở Software Qualification Test Specification.

## 2. References {#adas-references}

| Tài liệu | Dùng cho |
|---|---|
| [UN R79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf) | HWA là ACSF B1 (5.6.2), LKA và ELK vạch là CSF (5.1.6.1), ELK vật thể là ESF (5.1.6.2); ghi đè, cảnh báo |
| [EU 2021/646 (ELKS)](https://eur-lex.europa.eu/eli/reg_impl/2021/646/2021-04-20/eng) | Dải tốc độ 70–130 km/h, mặc định bật, cách tắt, điều kiện được chặn |
| [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf), [Assessment Protocol SA v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf) | Kịch bản thử, DTLE, mô-men ghi đè 3,5 Nm, ELK khi có xi-nhan, DIM |
| [ISO 17361:2017](https://standards.iteh.ai/catalog/standards/iso/c3d927a6-f4e1-4b4d-91d2-548cf5953983/iso-17361-2017) (trang tóm tắt) | Không cảnh báo sớm hơn khoảng TLC 1,5 s |
| ISO 21448:2022 (SOTIF) | Không can thiệp sai khi perception kém |
| [UN R171 (DCAS)](https://eur-lex.europa.eu/eli/reg/2025/1899/oj/eng) (trang tóm tắt) | Điều kiện hãng tự khai báo để vào chế độ active |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=vi), [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=vi), [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=vi) | Schema `FunctionRequests`, `PathStatus`; yêu cầu của planner; cách planner can thiệp |

## 3. Phân loại theo quy định {#adas-classification}

| Chức năng | Khái niệm trong quy định | Bật, tắt |
|---|---|---|
| HWA | ACSF Category B1 (R79); thuộc R171 khi kết hợp ACC | Tài xế bật bằng nút, cần ACC đang bật; tắt bằng một thao tác (R79 5.6.2.1.2) |
| LKA | CSF dựa trên vạch (R79 2.3.4.2 c) | Mặc định bật; tắt qua menu |
| ELK, vạch liền và mép đường | CSF và ELKS | Mặc định bật mỗi lần khởi động; tắt qua ít nhất hai thao tác (EU 2021/646 Annex I 3.2.1) |
| ELK, xe ngược chiều và xe đang vượt | ESF (R79 2.3.4.3 a) | Như dòng trên |

## 4. Phân chia với path planner {#adas-role}

| Việc | Khối Chức năng ADAS | Path planner |
|---|---|---|
| Cài đặt (nút HWA, menu LKA, ELK) | Đọc | Không biết |
| Điều kiện khả dụng (mục 7) | Kiểm | Nhận kết quả qua `state` |
| DLC, v_lat, TLC kèm độ bất định (mục 5) | Tính, riêng với planner (PP-ADR-014) | Dùng TLC để chọn thời lượng path; tự tính trạng thái ngang của mình |
| Bên kia vạch có nguy hiểm không (mục 6) | Xét | Không xét |
| Ý định tài xế (mục 8) | Đoán | Nhận `driver_override` |
| Cảnh báo tài xế (mục 10) | Gửi HMI | Báo `lateral_limit_reached`, `path_valid` |
| Arbitration, path, giới hạn, kết thúc can thiệp | Không | Làm |
| Lọc cảm biến | Không lọc lại; lane model, state estimator, ego-motion đã lọc và gửi kèm phương sai. Phải chịu được phần lỗi còn lại | Như khối Chức năng ADAS |

## 5. Đại lượng khối Chức năng ADAS tính {#adas-quantities}

v: tốc độ; v_y: vận tốc ngang tại tâm trục sau; r: yaw rate; x_f: chiều dài cơ sở; W: `vehicle_width`. Vạch trái y_L(x) = c0 + c1·x + c2·x² + c3·x³, y dương sang trái.

| Đại lượng | Cách tính |
|---|---|
| DLC_L | y_L(x_f) − W/2: từ mép ngoài lốp trước trái tới mép trong vạch trái (như DTLE của Euro NCAP) |
| v_lat_L | v_y + r·x_f − v·y_L'(x_f), với y_L'(x) = c1 + 2·c2·x + 3·c3·x² |
| TLC_L | DLC_L / v_lat_L khi v_lat_L ≥ 0,05 m/s; ngược lại vô cùng |
| Phía phải | DLC_R = −y_R(x_f) − W/2; v_lat_R = −(v_y + r·x_f) + v·y_R'(x_f) |
| Độ bất định | σ_DLC ≈ √(σ_c0² + x_f²·σ_c1²); σ_vlat ≈ √(v²·σ_c1² + σ_vy²); σ_TLC ≈ TLC·√((σ_DLC/DLC)² + (σ_vlat/v_lat)²) |

**Quy tắc dùng độ bất định** (ISO 21448: không can thiệp sai khi perception kém; Euro NCAP Assessment 4.3.3.5: không can thiệp ngoài ý muốn tài xế):

| Quy tắc | Điều kiện |
|---|---|
| Chắc chắn xe đang trôi về vạch | v_lat − `k_sigma`·σ_vlat ≥ 0,05 m/s |
| Chưa chắc về hướng | Chỉ dùng ngưỡng DLC của LKA (`dlc_lka`) |
| Quá nhiễu | σ_TLC > `sigma_tlc_max` hoặc vạch không đủ tin: UNAVAILABLE |
| Xác nhận LKA | Điều kiện kích hoạt đúng ở `n_confirm` lần cập nhật lane model liên tiếp. Không áp cho ELK |

## 6. Bên kia vạch {#adas-beyond-line}

| Bên kia vạch | Chức năng phụ trách |
|---|---|
| Vạch được vượt (`crossable = true`), làn bên trống | LKA nếu đang bật; LKA tắt thì không ai can thiệp |
| Vạch không được vượt (`crossable = false`) | LKA trước, ELK nếu LKA tắt hoặc chưa đủ |
| Mép đường (`road_edges[]`) | ELK |
| Xe ngược chiều hoặc xe đang vượt trong cửa sổ xung đột | ELK |

**Đánh giá xe ở làn bên** (ELK vật thể):

1. Chọn vật thể ở làn phía xe đang trôi tới, gán làn bằng lane model; `existence_probability` ≥ `exist_min`, đã thấy ít nhất `n_track` frame liền.
2. Dự đoán vị trí dọc với vận tốc không đổi.
3. Cửa sổ xung đột [TLC, TLC + `t_conflict`].
4. Làn bên không an toàn nếu trong cửa sổ, vật thể nằm trong hộp quanh thân xe mình, nới mỗi đầu `box_margin`.
5. Tài xế bật xi-nhan chuyển làn: ELK chỉ can thiệp khi xe sau không thể phanh kịp, tức một trong ba điều đúng: xe kia ngang hàng (hộp nới `abreast_margin` trong [TLC, TLC + 1 s]); TTC xe sau tới đuôi xe mình ≤ `ttc_rear`; xe sau cần giảm tốc Δv² / (2·khoảng cách) > `decel_rear`. Còn lại chỉ cảnh báo. Bài thử Euro NCAP có xi-nhan rơi vào trường hợp ngang hàng, nên vẫn đạt.

## 7. Điều kiện khả dụng {#adas-availability}

Không thoả thì chức năng không được gửi REQUEST. Ngoài dải tốc độ (EU ELKS), quy định không cho số; R79 5.6.2.3.1.1 để hãng tự khai báo.

| Điều kiện | HWA | LKA | ELK | Nguồn |
|---|---|---|---|---|
| Cài đặt | Tài xế đã bật, ACC đang bật | Đang bật trong menu | Đang bật | R79 5.6.2.1.2; EU 2021/646 3.2.1 |
| Tốc độ | 10–130 km/h; dưới 10 km/h thì chờ | Kích hoạt từ 70 km/h, giữ tới dưới 65 km/h, tối đa 130 km/h | Như LKA | EU 2021/646 3.6.1; R79 B1 |
| Biên làn | Hai vạch; hoặc một vạch cộng bề rộng nhớ được; hoặc tâm làn planner suy ra từ vạch làn bên, mép đường | Vạch phía đang trôi: MEASURED, confidence ≥ `conf_ego`, tầm nhìn / tốc độ ≥ `t_view_min` | Như LKA. ELK mép đường dùng mép trực tiếp MEASURED, confidence ≥ `conf_edge`, với biên đối diện đủ tin hoặc bề rộng đã nhớ khi mép đã được gắn với làn đang chạy | mentor, PP-SWR-047, PP-TS-007 |
| Biên kém tin | — | UNAVAILABLE | UNAVAILABLE ở phía đó | mentor |
| Tầm nhìn | Thời gian nhìn trước = điểm cuối tầm nhìn chung của hai biên làn / tốc độ ≥ `t_view_hwa`. Thấp hơn liên tục quá `t_view_hold` thì UNAVAILABLE; ngắn hơn thì HWA vẫn lái | Theo `t_view_min` ở dòng Biên làn | Như LKA | R171 5.3.7.1.4 (không mất trợ lực lái đột ngột); ngưỡng nhóm tự thống nhất |
| Khoảng trống | `lane_too_narrow = false` | — | — | PP-SWR-063 |
| ESC | ESC can thiệp: HWA tiếp tục | ESC can thiệp hoặc bị tắt: chặn | Như LKA | EU 2021/646 3.2.2, 3.3.2 |
| Input | LaneModel, IMU, tốc độ, góc lái hợp lệ | Như HWA, cộng VehicleStateEstimate | Như LKA; phần vật thể cần thêm ObjectList | PP-SWR-140 đến 144 |
| `path_valid` | — | true | true | PP-SWR-043 |

**Vào HWA.** Khi tài xế bấm nút, HWA chỉ vào khi thêm các điều kiện sau thoả; không thì từ chối và báo tài xế:

| Điều kiện | Ngưỡng | Nguồn |
|---|---|---|
| Xe trong làn | DLC ≥ `hwa_entry_dlc` cả hai phía | nhóm tự thống nhất |
| Lệch tâm | ≤ `hwa_entry_offset` | nhóm tự thống nhất |
| Góc lệch so với làn | ≤ `hwa_entry_heading` | nhóm tự thống nhất |
| Tay trên vô lăng | Có | R79 5.6.2.2.5 |
| Xi-nhan | Tắt | nhóm tự thống nhất |

## 8. Ý định tài xế {#adas-driver-intention}

Theo DIM của Euro NCAP, chỉ dùng tín hiệu có trên xe: mô-men tài xế, góc và tốc độ quay vô lăng, xi-nhan. Lực ghi đè 50 N của R79 ứng với khoảng 9,5 Nm ở vành bán kính 0,19 m.

| Tình huống | Điều kiện | Kết luận | Nguồn |
|---|---|---|---|
| Lơ đãng, xe tự trôi | Mô-men < `torque_passive` và tốc độ quay vô lăng < 15 °/s, giữ 0,5 s | Được kích hoạt | Euro NCAP: vô lăng 0 ± 15 °/s trước lúc trôi |
| Chuyển làn có xi-nhan | Xi-nhan về phía đang trôi, hoặc vừa tắt chưa tới `t_indicator` | Chặn LKA và ELK vạch; ELK vật thể theo mục 6, bước 5 | Euro NCAP (xi-nhan 1,0 ± 0,5 s trước lúc đánh lái) |
| Chuyển làn không xi-nhan | Mô-men ≥ `torque_intent` về phía vạch, giữ 0,2 s; hoặc tốc độ quay vô lăng ≥ 30 °/s về phía vạch | Như dòng trên | nhóm tự thống nhất |
| Ghi đè lúc đang can thiệp | Mô-men ≥ `torque_override` ngược chiều can thiệp, giữ 0,1 s | Gửi OFF, bật `driver_override`; không kích hoạt lại cùng phía trong `t_reactivate_override` | R79 5.1.6; Euro NCAP ≤ 3,5 Nm |
| Bẻ lái gấp tránh vật | v_lat > `v_lat_swerve`, xi-nhan tắt | Chặn cả LKA và ELK, kể cả khi làn bên có xe; chỉ cảnh báo | R79 5.1.6: tài xế luôn được ghi đè |
| Tay rời vô lăng | Mô-men < 0,3 Nm liên tục | HWA: cảnh báo hình sau `t_hands_off_visual`, âm thanh sau `t_hands_off_acoustic`, tắt sau `t_hands_off_off`. LKA, ELK vẫn can thiệp | R79 5.6.2.2.5 (giới hạn chậm nhất) |

Tài xế giữ vô lăng với mô-men ≥ `torque_override` thì mọi can thiệp đều hủy, kể cả khi tài xế cố ý lái vào xe khác: ở L2 tài xế chịu trách nhiệm.

## 9. Kích hoạt và kết thúc {#adas-activation}

Mỗi chu kỳ 25 ms, xét từng phía và từng chức năng. Gửi REQUEST khi: điều kiện khả dụng thoả, ý định tài xế không chặn, độ bất định cho phép, không trong thời gian chờ, và điều kiện dưới đây đúng.

| Chức năng | Kích hoạt khi | Nguồn của giới hạn |
|---|---|---|
| LKA | TLC ≤ `tlc_lka`, hoặc DLC ≤ `dlc_lka` với v_lat ≥ 0,05 m/s; và 0,1 ≤ v_lat ≤ 1,0 m/s | Euro NCAP: DTLE ≥ −0,3 m ở v_lat 0,2–0,6 m/s; ISO 17361: không sớm hơn TLC 1,5 s |
| ELK, vạch liền | TLC ≤ `tlc_elk_line` tới vạch đó | Euro NCAP, EU 2021/646: DTLE ≥ −0,3 m |
| ELK, mép đường | TLC ≤ `tlc_elk_line` tới mép đường | Euro NCAP: DTLE ≥ −0,1 m |
| ELK, xe ngược chiều hoặc đang vượt | TLC ≤ `tlc_elk_object` tới vạch, và làn bên không an toàn (mục 6) | Euro NCAP: không va chạm, khoảng cách ngang ≥ 0,3 m |

- Hai phía cùng có yêu cầu: gửi phía có TLC nhỏ hơn.
- ELK vẫn được yêu cầu khi HWA đang chạy (EU 2021/646 3.3.2 cho phép chặn; dự án không chặn).
- Xe khác cắt vào làn mà xe mình không trôi: không gửi ELK; planner dời tâm, khối dọc giữ khoảng cách.

| Sự kiện | Khối Chức năng ADAS làm gì |
|---|---|
| Planner báo COMPLETED của một chức năng | Chức năng đó về STANDBY. Kích hoạt lại cùng phía khi DLC đã ≥ `dlc_rearm` rồi lại giảm, hoặc sau `t_rearm` |
| Planner báo ELK ACTIVE | Đưa LKA cùng phía về STANDBY. Chặn yêu cầu LKA mới cùng phía trong lúc ELK ACTIVE |
| Planner báo ELK COMPLETED | Áp điều kiện tái kích hoạt LKA cùng phía như sau COMPLETED, kể cả khi LKA đã về STANDBY |
| Tài xế ghi đè | Gửi OFF ngay; chờ `t_reactivate_override`, trừ ELK vật thể |
| Tốc độ xuống dưới 65 km/h giữa lúc can thiệp | Giữ REQUEST tới COMPLETED, không kích hoạt lần mới |
| Mất một vạch giữa lúc can thiệp, vạch còn lại đủ tin | Giữ REQUEST; planner dùng vạch còn lại cộng bề rộng nhớ được |
| Mất hai vạch làn mình giữa lúc can thiệp, còn biên khác đủ tin | Hủy can thiệp dựa trên vạch. ELK mép đường tiếp tục nếu còn đủ điều kiện biên theo mục 7 |
| Không còn biên đủ tin giữa lúc can thiệp | Giữ REQUEST; planner bám path cũ tối đa `T_coast` rồi báo path không hợp lệ (PP-SWR-124) |

### 9.1 Trạng thái chức năng {#adas-modes}

Giá trị `state` trong `FunctionRequests` ([Interface Control Document 5.6](report.html?doc=path-planner-interface-control-document&lang=vi#function-requests)). Theo R79: OFF là off mode, STANDBY và UNAVAILABLE là standby mode, REQUEST là active mode.

| Từ | Tới | Khi | Chức năng | Nguồn |
|---|---|---|---|---|
| OFF | STANDBY | Bật trong menu, hoặc mặc định bật lúc khởi động | LKA, ELK | Mục 3 |
| STANDBY | UNAVAILABLE | Một điều kiện khả dụng không thoả | LKA, ELK | Mục 7 |
| UNAVAILABLE | STANDBY | Mọi điều kiện khả dụng thoả lại | LKA, ELK | Mục 7 |
| STANDBY | REQUEST | Điều kiện kích hoạt thoả, ý định tài xế không chặn | LKA, ELK | Mục 8, 9 |
| REQUEST | STANDBY | Planner báo COMPLETED | LKA, ELK | Mục 9 |
| REQUEST | OFF | Tài xế ghi đè | LKA, ELK | Mục 8, 9 |
| OFF | STANDBY | Hết `t_reactivate_override` sau lần ghi đè | LKA, ELK | Mục 9 |
| OFF | REQUEST | Tài xế bấm nút khi ACC đang bật, điều kiện khả dụng và điều kiện vào HWA thoả | HWA | Mục 3, 7 |
| REQUEST | OFF | Tay rời vô lăng quá `t_hands_off_off`, hoặc tài xế tắt bằng một thao tác | HWA | Mục 3, 8 |
| REQUEST | UNAVAILABLE | Một điều kiện khả dụng không thoả | HWA | Mục 7 |
| UNAVAILABLE | REQUEST | Điều kiện khả dụng và điều kiện vào HWA thoả lại; tài xế không phải bấm nút | HWA | nhóm tự thống nhất, như Toyota LTA, Volvo Pilot Assist |
| Mọi trạng thái | FAULT | Khối Chức năng ADAS lỗi | HWA, LKA, ELK | Interface Control Document 5.6 |

## 10. Cảnh báo tài xế {#adas-warnings}

Trong simulator chỉ ghi log qua message `HmiStatus`.

| Sự kiện | Cảnh báo | Nguồn |
|---|---|---|
| Mỗi lần LKA hoặc ELK can thiệp | Đèn báo, giữ ít nhất 1 s hoặc tới hết can thiệp | R79 5.1.6.1.1; EU 2021/646 3.6.4.1 |
| Can thiệp dài hơn 10 s | Âm thanh tới hết can thiệp | R79 5.1.6.1.2.1 |
| Lần can thiệp thứ hai trong 180 s mà tài xế không đánh lái | Âm thanh từ lần thứ hai; từ lần thứ ba, mỗi lần dài hơn lần trước ít nhất 10 s | R79 5.1.6.1.2.2 |
| ELK vật thể (ESF) | Đèn và âm thanh hoặc rung, suốt can thiệp | R79 5.1.6.2.6 |
| Chuyển làn có xi-nhan, xe sau còn phanh kịp | Cảnh báo kiểu điểm mù, không lái | nhóm tự thống nhất |
| HWA chạm aysmax và lốp trước bắt đầu đè vạch | Vẫn hỗ trợ trong khả năng; đèn kèm âm thanh hoặc rung. Dùng `lateral_limit_reached` và DLC | R79 5.6.2.2.3 |
| `path_valid = false` | Yêu cầu tài xế cầm lái | nhóm tự thống nhất |
| `lane_too_narrow = true` khi tài xế bấm HWA | Báo HWA không khả dụng | nhóm tự thống nhất |
| HWA chuyển sang UNAVAILABLE | Đèn HWA đổi sang trạng thái chờ; tự trở lại khi điều kiện thoả | nhóm tự thống nhất |
| HWA chuyển sang OFF vì tay rời vô lăng | Báo HWA đã tắt; tài xế phải bấm nút để bật lại | R79 5.6.2.2.5 |
| Tài xế tắt ELK | Đèn báo liên tục | EU 2021/646 3.2.3 |

## 11. Edge cases {#adas-edge-cases}

Số thứ tự trùng với mục Edge cases của Software Architectural Design (phần planner).

| # | Tình huống | Khối Chức năng ADAS làm gì |
|---|---|---|
| 1a | HWA đang chạy, xe trôi về phía làn bên có xe | Gửi ELK như bình thường |
| 1b | Xe khác lấn sang làn mình, xe mình ở giữa | Không gửi ELK (TLC lớn) |
| 2 | HWA vào cua gắt hơn aysmax | Cảnh báo khi lốp bắt đầu đè vạch; gửi ELK nếu tới ngưỡng ELK và bên kia nguy hiểm |
| 3 | Tài xế ghi đè HWA | Bật `driver_override`; HWA vẫn bật |
| 4 | Xi-nhan chuyển làn, xe đang vượt từ phía sau | Theo mục 6, bước 5; không gửi nếu lốp trước đã qua vạch quá 0,3 m |
| 5 | Xi-nhan, đè vạch liền hoặc ra lề có chủ đích | Chưa can thiệp: không kích hoạt. Đang can thiệp: gửi OFF, `cancel_reason = INDICATOR` |
| 6 | Trôi qua lại nhiều lần | Mỗi lần trôi là một yêu cầu mới, cùng ngưỡng; cảnh báo tăng dần theo R79 |
| 7 | Lane model báo `lane_change` | Hủy yêu cầu đang chờ, tính lại theo làn mới; không kích hoạt trong 1 s |
| 8 | c0 jump làm DLC nhảy | Khối tự kiểm tính nhất quán của biên, riêng với planner, và đánh dấu frame nhảy: không kích hoạt, không hủy dựa trên frame đó; dùng DLC mới khi frame sau xác nhận; quá 0,5 s không xác nhận thì UNAVAILABLE |
| 9 | Vật thể ảo | Lọc bằng `exist_min` và `n_track` |
| 10 | Xe ngược chiều nhưng xe mình không trôi | Không gửi ELK |
| 11 | Mất hai vạch làn mình giữa lúc can thiệp | Còn biên khác đủ tin: hủy LKA, ELK, HWA tiếp tục. Không còn biên: giữ REQUEST; khi `path_valid = false` thì yêu cầu tài xế cầm lái |
| 12 | ESC can thiệp trong lúc LKA hoặc ELK can thiệp | Gửi OFF, nhường ESC |
| 13 | Tốc độ dưới 65 km/h giữa lúc can thiệp | Giữ yêu cầu tới COMPLETED |
| 13b | Tắc đường 0–60 km/h | LKA, ELK UNAVAILABLE; HWA vẫn chạy nếu đang bật |
| 15 | Bấm HWA khi xe lệch tâm 0,4 m | Cho vào HWA nếu ≤ `hwa_entry_offset` |
| 16 | Bẻ lái gấp tránh vật, làn bên có xe | Chặn LKA, ELK; chỉ cảnh báo |

## 12. Interface {#function-requests}

- **Output.** `FunctionRequests` gửi path planner, 40 Hz; schema ở [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=vi#function-requests). Nhận lại `PathStatus`.
- **Log.** `HmiStatus`: cảnh báo đèn, âm thanh, mức cảnh báo tay rời vô lăng, số lần can thiệp trong 180 s. Chỉ để đánh giá.
- **Tín hiệu tài xế**, theo signal list nhóm Motion (mentor):

| Tín hiệu | Tần số | Đơn vị trên xe | Dùng cho |
|---|---|---|---|
| Mô-men tài xế | 50 Hz | Nm | Mục 8 |
| Góc vô lăng | 100 Hz | ° | Log |
| Tốc độ quay vô lăng | 100 Hz | °/s | Mục 8 |
| Tốc độ xe | 50 Hz | km/h | Mục 7 |
| Xi-nhan, nút HWA, trạng thái ESC | Không có trong signal list; simulator lấy từ file kịch bản | — | Mục 7, 8 |

Khối chạy 40 Hz nên mỗi chu kỳ nhận 1–2 mẫu mô-men; ngưỡng tính theo thời gian giữ, không theo số chu kỳ.

## 13. Calibration parameters {#adas-calibration}

Một bộ cho mọi xe. Software Qualification Test Specification quét trong dải; riêng `tlc_lka` chạy ba mức để chọn.

| Tham số | Đơn vị | Khởi đầu | Dải quét | Giới hạn |
|---|---|---|---|---|
| `tlc_lka` | s | 1,0 | 0,6; 1,0; 1,5 | ≤ 1,5 (ISO 17361) |
| `dlc_lka` | m | 0,1 | 0–0,2 | ≥ 0 |
| `tlc_elk_line` | s | 0,6 | 0,4–0,8 | DTLE theo PP-SWR-086 |
| `tlc_elk_object` | s | 0,8 | 0,6–1,0 | Khoảng cách ngang theo PP-SWR-088 |
| `k_sigma` | — | 2 | 1–3 | ≥ 0 |
| `sigma_tlc_max` | s | 0,5 | 0,3–0,7 | > 0 |
| `n_confirm` | frame | 2 | 1–3 | ≥ 1 |
| `conf_ego` | — | 0,6 | 0,4–0,8 | 0–1 |
| `conf_edge` | — | 0,7 | 0,5–0,9 | 0–1 |
| `t_view_min` | s | 1,0 | 0,7–1,5 | ≥ 0,7 (như `t_view_hwa`, PP-ASM-021) |
| `t_view_hwa` | s | 1,0 | 0,7–1,5 | ≥ 0,7 (thời gian nhìn trước của controller 0,6 s theo PP-ASM-021, cộng một bước Trajectory 0,1 s) |
| `t_view_hold` | s | 0,5 | 0,2–1,0 | ≥ 0 |
| `exist_min` | — | 0,7 | 0,5–0,9 | 0–1 |
| `n_track` | frame | 3 | 2–5 | ≥ 1 |
| `t_conflict` | s | 3,0 | 1,5–3,0 | > 0 (PP-TS-009) |
| `box_margin` | m | 2,0 | 1,0–3,0 | ≥ 0 |
| `abreast_margin` | m | 1,0 | 0,5–2,0 | ≥ 0 |
| `ttc_rear` | s | 1,5 | 1,0–2,0 | > 0 |
| `decel_rear` | m/s² | 3,0 | 2,0–4,0 | > 0 |
| `hwa_entry_dlc` | m | 0,2 | 0–0,3 | ≥ 0 |
| `hwa_entry_offset` | m | 0,5 | 0,3–0,7 | ≥ 0 |
| `hwa_entry_heading` | ° | 2 | 1–3 | ≥ 0 |
| `torque_passive` | Nm | 0,5 | 0,3–1,0 | < `torque_intent` |
| `torque_intent` | Nm | 1,5 | 1,0–2,5 | < `torque_override` |
| `torque_override` | Nm | 3,0 | 2,0–3,5 | ≤ 3,5 (Euro NCAP); ≤ 9,5 (R79 50 N) |
| `t_indicator` | s | 2,0 | 1,0–3,0 | ≥ 0 |
| `v_lat_swerve` | m/s | 1,0 | 0,8–1,5 | > 0,7 (Euro NCAP chuyển làn có chủ đích) |
| `t_reactivate_override` | s | 3,0 | 1,0–5,0 | ≥ 0 |
| `dlc_rearm` | m | 0,3 | 0,2–0,5 | ≥ 0 |
| `t_rearm` | s | 2,0 | 1,0–3,0 | ≥ 0 |
| `t_hands_off_visual` | s | 10 | 5–15 | ≤ 15 (R79 5.6.2.2.5) |
| `t_hands_off_acoustic` | s | 15 | 10–30 | ≤ 30 (R79 5.6.2.2.5) |
| `t_hands_off_off` | s | 30 | 20–60 | ≤ 30 s sau khi bắt đầu âm thanh (R79 5.6.2.2.5) |

## Appendix A. Analysis {#adas-appendix}

**A.1 Kiểm công thức v_lat.** Đường thẳng, v = 25 m/s, c1 = −0,016: v_lat_L = 0,40 m/s, đúng một mức trôi của Euro NCAP. Xe bám đúng cua (r = v·κ, c1 = 0, c2 = κ/2): r·x_f và v·y_L'(x_f) triệt tiêu, v_lat = 0.

**A.2 Độ bất định** với σ_c0 = 0,03 m, σ_c1 = 0,002 (ban ngày, PP-ASM-011), x_f = 2,9 m, v = 25 m/s, DLC = 0,40 m, v_lat = 0,40 m/s:

| Điều kiện | σ_DLC | σ_vlat | σ_TLC | Khoảng ±2σ của TLC |
|---|---|---|---|---|
| Ban ngày | 0,031 m | 0,05 m/s | 0,15 s | 0,7–1,3 s |
| Ban đêm hoặc mưa (×2,5) | 0,077 m | 0,125 m/s | 0,37 s | 0,3–1,7 s |

Phần lớn nhiễu đến từ c1 nhân tốc độ. Với `k_sigma` = 2, ban ngày cần v_lat ≥ 0,15 m/s, ban đêm ≥ 0,30 m/s mới chắc hướng.

**A.3 Xe ở làn bên**, 72 km/h, `tlc_elk_object` = 0,8 s, cửa sổ 0,8–2,8 s:

| Trường hợp | Kết luận |
|---|---|
| Xe ngược chiều 20 m/s, cách 90 m: lại gần thêm 32–112 m trong cửa sổ | Không an toàn: ELK |
| Như trên, cách 200 m: sau 2,8 s còn 88 m | An toàn: không ELK |
| Xe vượt nhanh hơn 2,2 m/s, đầu xe sau đuôi xe mình 7 m: sau 2,8 s còn 0,8 m | Không an toàn: ELK |
| Như trên, có xi-nhan, cách 20 m: cần giảm tốc 0,12 m/s², TTC 9 s | Chỉ cảnh báo |
| Có xi-nhan, nhanh hơn 5 m/s, cách 5 m: cần 2,5 m/s², TTC 1,0 s | ELK |

**A.4 Ngưỡng TLC.** Với trễ 0,2 s: LKA đạt DTLE Euro NCAP cần TLC khoảng 0,4 s; LKA không chạm vạch cần 0,4–0,7 s; ELK mép đường cần 0,3–0,5 s. Nhiễu ban đêm cần thêm 0,3–0,4 s. `tlc_elk_object` sớm hơn `tlc_elk_line` vì với xe ở làn bên, chạm là tai nạn; 0,8 s giữ mép lốp cách vạch 0,09–0,29 m.

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-11-10 | Refactor thành ADAS Function Specification, baseline BL1. Mọi ngưỡng tự chọn thành calibration parameter (mục 13); HWA dùng được tâm làn suy ra, LKA và ELK cần vạch làn mình đủ tin (mentor); thêm `lane_too_narrow` vào điều kiện HWA; schema `FunctionRequests` chuyển sang Interface Control Document; ví dụ tính gom vào Appendix A; bỏ nhãn trạng thái và việc mở |
| 1.1 | 2026-11-10 | Khối Chức năng ADAS tự tính trạng thái ngang và tự kiểm tính nhất quán, riêng với planner (PP-ADR-014); `conf_ego` chỉnh riêng, giới hạn 0–1 |
| 1.2 | 2026-11-11 | Mục 9.1: bảng chuyển trạng thái của từng chức năng, gom từ mục 3, 7, 8, 9. HWA tự trở lại từ UNAVAILABLE; tắt vì tay rời hoặc tài xế tắt thì phải bấm nút lại (mục 9.1, 10) |
| 1.3 | 2026-11-11 | Mục 9: xử lý COMPLETED theo chức năng, rút LKA REQUEST cùng phía khi ELK hoàn tất |
| 1.4 | 2026-11-12 | Mục 7: điều kiện biên trực tiếp của ELK. Mục 9: rút LKA cùng phía từ ELK ACTIVE. Mục 13: chốt `t_conflict` trước kiểm chứng theo PP-TS-009 |
| 1.5 | 2026-11-12 | Mục 7: HWA thêm điều kiện tầm nhìn theo thời gian nhìn trước, có thời gian giữ. Mục 13: thêm `t_view_hwa`, `t_view_hold` |
| 1.6 | 2026-11-12 | Mục 13: `t_view_hwa` ≥ 0,7 s theo PP-ASM-021; dải quét 0,7–1,5 s |
| 1.7 | 2026-11-12 | Mục 7, 13: `view_min` (20 m) thay bằng `t_view_min` (1,0 s, ≥ 0,7 s) để phần path quan sát đủ cho controller ở mọi tốc độ (PP-ASM-021) |
