# PP-TS-024 Driver model cho path generation (T7)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-18 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-TS-003 (kỹ thuật T7), PP-TS-013 (comfort line), PP-TS-025; PP-SWR-001, 003, 004, 006, 051, 100; PP-ADR-013 |

## 1. Câu hỏi

- Quyết định cần đưa ra: phương án dựa trên hành vi nhìn trước có giảm gia tốc ngang của xe qua cua so với **cả Quintic lẫn QP** với chi phí tính phù hợp không.
- Giả thuyết: điều chỉnh đường vào và ra cua giúp giảm đỉnh độ cong ở cua ngắn trong phạm vi quan sát. Trên cung tròn, dịch đều vào trong làm bán kính nhỏ đi và tăng a_y ở cùng tốc độ. PP-TS-013 cũng ghi nhận quintic có điểm trung gian giảm a_y đỉnh 1,9% ở S1f sạch đồng thời làm jerk đỉnh tăng khoảng 15%. So cả hai đại lượng trên xe. [Kết quả PP-TS-013](../PP-TS-013-comfort-line/study.md#53-so-sánh-quintic-c-và-quintic-có-điểm-trung-gian)
- Phạm vi: T7 sinh d(t) trên lưới thời gian chung, tương ứng d(s) qua kế hoạch tốc độ. T11 đổi sang `Trajectory`. Lateral Controller và kế hoạch tốc độ giữ chung cho các phương án.
- Ràng buộc:
  - Các ứng viên đi qua T10, T4 và lần T10 cuối như hai mốc. Kiểm riêng các giới hạn trên path cuối và DLC trên xe. T10 thay đổi hình học khi kẹp độ cong.
  - Mã C11, không cấp phát động, không biến toàn cục (PP-ADR-013). Driver model dạng quy tắc có tham số thì đạt; mô hình cần học thì xem PP-TS-025.
  - Giữ `sim/stand_ins/driver.py` độc lập với thuật toán của T7. SIL hiện chấm độ êm và giữ làn. Cần log lái thật để kiểm giả thuyết path giống người lái.

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Quintic T7 A, calibration mặc định | `PP_T7=quintic` | Mốc sản phẩm, chạy lại trên LCC hiện tại |
| VQ | QP T7 C, calibration mặc định, 150 vòng ADMM | `PP_T7=qp` | Mốc tối ưu, cùng cấu hình với V1 của TS-025 |
| V1 | Tangent point xác định vị trí đỉnh của hiệu chỉnh ngang | `PP_T7=driver_tangent` | Giả thuyết mô phỏng hành vi nhìn trước |
| V2 | Chấm một tập nhỏ hiệu chỉnh ngang theo đỉnh a_y và jerk dự báo | `PP_T7=driver_ay` | Quy tắc tạo path có xét độ êm ở cùng tốc độ |
| VR | R-cam của PP-TS-013 | Nguyên mẫu Python | Dùng giải thích ảnh hưởng của chất lượng độ cong đầu vào |

1. **Hình dạng chung.** Cộng một hiệu chỉnh hữu hạn vào d(t) của V0 trên phần quan sát. Dùng hai nửa smoothstep bậc 7, cùng đạt biên độ đỉnh, với đạo hàm bậc 1–3 bằng 0 ở đầu, đỉnh và cuối. Khi phần quan sát ngắn, jerk của cùng một biên độ tăng xấp xỉ theo nghịch đảo lập phương thời lượng. Thu nhỏ toàn biên độ hoặc dùng V0 nếu không còn đủ chiều dài để chuyển tiếp. Tránh kẹp từng mẫu d vì tạo góc gãy.
2. **V1.** Tìm tiếp điểm của tia nhìn từ xe lên vạch trong cua trên đoạn có hai biên đủ tin. Chuyển khoảng cách tới tiếp điểm thành thời gian đỉnh theo speed profile. Bắt đầu tìm trong 1–2 s, theo khoảng nhìn trước quan sát ở bài gốc. Độ lệch đỉnh là tham số thiết kế của planner và được kiểm trong hành lang. Khi có nhiều ứng viên, chọn tiếp điểm gần nhất còn đủ đoạn giảm hiệu chỉnh về 0. [Land và Lee, 1994](https://www.nature.com/articles/369742a0) · [Boer, 1996](https://doi.org/10.1109/IVS.1996.566341)
3. **V2.** Thử tối đa bốn hiệu chỉnh (hai dấu × hai thời điểm đỉnh), cùng ứng viên biên độ 0. Dùng hình học T11 để chấm đỉnh |a_y| trên phần quan sát; chỉ xét ứng viên có jerk trong dung sai và giữ sàn PP-SWR-006 khi áp dụng. Nếu không giảm đỉnh ít nhất 0,05 m/s² so với biên độ 0 ở bước chọn ứng viên, lấy V0. Reymond và cộng sự đo điều chỉnh **tốc độ** trong cua. Quy tắc d(t) ở tốc độ đã cho của V2 là giả thuyết cần kiểm trong study. [Reymond và cộng sự, 2001](https://pubmed.ncbi.nlm.nih.gov/11866202/)
4. **Điều kiện dùng chung cho V1/V2.** Dựng hành lang từng phía từ biên quan sát, bề rộng xe và khoảng hở cần giữ với vật thể. Giữ ưu tiên T8. Dùng V0 khi ước lượng làn hoặc vật thể thiếu điều kiện áp dụng, khi FOLLOW, trong pha đưa về giữa, khi driver override hoặc LKA/ELK đang REQUEST và ở chu kỳ đầu sau đó. Báo tỷ lệ dùng V0 theo lý do để thấy mức bao phủ của mỗi quy tắc. S22 kiểm chuyển LANE ↔ FOLLOW. S2, S3 và S14c kiểm bảo toàn đưa về giữa và ưu tiên vật thể.

## 3. Cách đánh giá (khóa trong plan.yaml)

| Mục | Nội dung |
|---|---|
| Bộ chung | [PP-T7](../../../benchmark/suites/PP-T7.yaml) dùng chung cho TS-024 và TS-025. Mỗi build dùng cùng mã nguồn, T4, T8, T10, T11, T12, simulator, ca, chế độ ACC, mode vòng, profile và seed. Ghép theo chính xác các trường đó. Suite bật cảm biến ObjectList chuẩn cả khi đường trống. F12b kiểm mất bản tin sau khi cảm biến đã chạy. |
| Bộ chỉnh và bộ kiểm | Tuning dùng seed 1–2. Test dùng seed 3–4, gồm 90–130 km/h, VP-0/3/5 trên S1f và S1c, cua vượt khả năng hỗ trợ, camera nhiễu/tầm nhìn ngắn, S17 ghi đè của người lái và hồi quy FOLLOW. Bảng linh hoạt chỉ dùng ca chạy cùng tập profile. |
| Điều kiện loại | Qua B0 theo SQTS §11; đạt mọi requirement áp dụng trong suite theo §9.1. Ghi giá trị, điều kiện áp dụng và lỗi theo từng cặp ca–profile–seed. Lỗi chung giữa các mốc vẫn là lần trượt. Báo thêm các lỗi chỉ xuất hiện ở ứng viên và độ lớn thay đổi để định vị nguyên nhân. |
| Thứ tự xếp hạng | SQTS §9.1: requirement, chỉ số an toàn, độ êm, linh hoạt giữa profile, thời gian. PP-SWR-004 và 016 là mục tiêu hiệu năng. PP-SWR-015 là yêu cầu ghi thời gian từng chu kỳ. |
| Ngân sách chỉnh | Luôn báo V0 và VQ với calibration chung mặc định. Khi xét chọn kỹ thuật, dùng tối đa 9 cấu hình trên tuning cho mỗi kỹ thuật có tham số. Dùng chung calibration SRS, T4, T8, T10 và T12. |

Lưới nháp để duyệt:

| Biến thể | 3 × 3 cấu hình trên tuning |
|---|---|
| V0 | `T_hwa` 2,5/3,0/3,5 s × `T_recenter` 3,0/3,5/4,0 s |
| VQ | `qp_w_dev` 0,15/0,30/0,60 × `qp_w_comfort` 2,5/5/10. Giữ 150 vòng. |
| V1 | Tâm cửa sổ nhìn trước 1,0/1,5/2,0 s (±0,25 s, giới hạn trong 1–2 s) × biên độ tối đa 0,10/0,20/0,30 m |
| V2 | Cặp vị trí đỉnh (0,35; 0,55), (0,40; 0,60), (0,45; 0,65) theo phần thời lượng dùng được trong tầm nhìn × cùng ba biên độ của V1 |

Các biên độ là tham số nghiên cứu. Ở mỗi chu kỳ, giới hạn hành lang và jerk có thể làm biên độ thực thấp hơn.

- **Vòng hở:** đọc path cuối, đỉnh |a_y|, jerk và PP-SWR-100 đến 102 trên đầu vào ghép cặp. Thêm log trước/lần sau T10 để định lượng can thiệp. Kiểm đầu vào có thực sự trùng giữa các build. **Vòng kín:** đọc DLC nhỏ nhất, đỉnh |a_y| và jerk xe theo SQTS §8.2, RMS jerk của path, khoảng hở vật thể, thời gian đưa về giữa và p99 LCC. Chỉ dùng các đoạn LCC thực sự đang lái cho chỉ số độ êm; kiểm thời lượng khả dụng cùng lúc để phát hiện phương án ngừng lái sớm.
- **Giả thuyết chính, ngưỡng nháp.** Trên S1f vòng kín, xét hiệu theo từng cặp đối với từng mốc. Mục tiêu giảm trung bình đỉnh |a_y| của xe ít nhất 0,10 m/s², với jerk đỉnh của xe tăng tối đa 0,10 m/s³ và DLC giảm tối đa 0,01 m ở từng cặp áp dụng. Báo hiệu từng cặp, số cặp có dữ liệu, hiệu trung bình và khoảng tin cậy theo SQTS §9.2. Kiểm ca dài S1e, nhiễu S1c/F01 và S14e riêng để biết phạm vi cải thiện. Các ngưỡng so sánh trong plan là dung sai hiệu năng, dùng DLC tính bằng mét cho mức 0,01 m.
- **Dữ liệu báo cáo.** `eval.study` chạy từng phương án với cùng suite và lưu tiêu chí áp dụng, chỉ số có nhãn, thời gian riêng LCC và lỗi theo từng lượt trong `results.json`. Bảng tổng mặc định của runner dùng để dò nhanh. Báo cáo quyết định dùng cửa loại và hiệu ghép cặp ở trên, cùng kết quả B0. Các chỉ số trước T10 và tỷ lệ dùng V0 cần thêm khi cài V1/V2.

## 4. Lần chạy

Từ 2026-11-23, study này giữ thiết kế biến thể; lần chạy chính thức, cách đánh giá và kết quả ở [PP-TS-031](../PP-TS-031-t7-generator-campaign/study.md). Tên ở đó theo thuật toán: V0, VQ, V1, V2 là `quintic_duration`, `qp_jerk_admm`, `quintic_tangent_point`, `quintic_ay_sampling`.

Chạy dò cặp mốc trên tuning bằng `python3 -m eval.study PP-TS-024 --part tuning --variant V0 --variant VQ --jobs 1`. Ghi B0 riêng cho hai thư viện của từng build bằng `python3 -m eval.conformance --planner <thư_mục_build>`. Kết quả dò nằm dưới `build/study/PP-TS-024/draft/`. Khi chấm chính thức, chạy đủ phương án đã khóa trên cùng suite theo quy trình trong [research/README.md](../../README.md).

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

### Bằng chứng hiện có

Trong 30 lượt test lịch sử của PP-TS-003, Quintic V0b và QP V1b đều trượt trên cùng hai lượt S14e với ACC bỏ qua giới hạn. QP trượt thêm PP-SWR-051 ở cả hai seed, thành 8 lần trượt tiêu chí so với 6. Trên S1f, QP giảm jerk đỉnh của path khoảng 0,12 m/s³ ở cả hai seed và làm lệch ngang xấu nhất tăng khoảng 0,05 m. Đây là lý do giữ cả S1f và S14e, đo đồng thời độ êm, lệch ngang, DLC và tính liên tục. Số liệu thuộc planner cũ. [Kết quả từng lượt PP-TS-003](../../runs/20261114-1934-study-PP-TS-003-272a711/results.json)

## 6. Đề xuất

Chạy lại V0 và VQ, sau đó thử V1. Nếu V1 chọn được điểm đỉnh ổn định và giữ đủ biên DLC nhưng độ êm thiếu ổn định, so tiếp V2 với cùng hàm tạo hình. Sự chênh giữa V1 và V2 khi đó chủ yếu đến từ quy tắc chọn hiệu chỉnh.

## 7. Quyết định

- Người quyết, ngày:
- Chọn:
- Lý do:
- Đưa vào: PP-ADR-…, SDD mục 10, calibration …, SRS …
- Hồi quy: run ID
