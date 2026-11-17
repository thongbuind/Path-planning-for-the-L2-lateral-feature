# PP-PR-062 Reset mềm của T4 làm ELK bắt đầu muộn ở v_lat cao

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa trong cây làm việc 2026-11-17 (SRS 1.23, PP-SWR-031, 049); chờ hồi quy chính thức |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | PP-SWR-085, 086, 091, 090, 100 đến 102; PP-SWR-031, 080; PP-TS-021 |
| Tái hiện | [20261117-0908-suite-regression-c56f0bf](../runs/20261117-0908-suite-regression-c56f0bf/report.md): S13 a, c (ELK), S5 lưới Euro NCAP vạch liền 0,6 m/s, F01 c lúc ELK, S5 a |

## 1. Hiện tượng

Trượt mới so với 20261114-2252-suite-regression-98a122b, 16 nhóm, đều ở ELK:

| Ca | Requirement trượt | Giá trị |
|---|---|---|
| S13 a (ELK, EPS chậm 75 ms), VP-4 | 085, 086, 091, 102 | DTLE −0,54 m; DLC phía đối diện −0,11 m |
| S13 c (ELK, EPS chậm 150 ms), VP-3, VP-4 | 085, 086, 100, 101, 102 | DTLE −0,41 đến −0,45 m; DLC phía đối diện −0,32 m |
| S5 lưới Euro NCAP vạch liền trái, phải, 0,6 m/s | 086; 090 | DTLE −0,41 m |
| F01 c lúc ELK (S5 a), VP-4 | 086, 102 | DTLE −0,33 m |
| S5 a, VP-0 | 090 | Báo COMPLETED khi chưa đủ điều kiện |

## 2. Nguyên nhân

Khoanh vùng bằng lượt nháp 2026-11-17: cùng file ca và seed của lần hồi quy, thư viện build ngoài cây làm việc từ từng commit.

| Thư viện | S13 a ELK | S13 c ELK | S5 NCAP 0,6 m/s | F01 c lúc ELK | S5 a |
|---|---|---|---|---|---|
| 2f86a0b (reset cứng 0,2 m) | Đạt, DTLE 0,03 | Đạt, 0,01 | Đạt, 0,06 | Trượt 032, DTLE 0,07 | Đạt |
| 5a38b6e (đưa reset mềm vào bản giao) | Trượt, −0,54 | Trượt, −0,41 | Trượt, −0,41 | Trượt 086, 102, −0,33 | Trượt 090 |
| 9cc3c8e (thêm PP-PR-058) | Như 5a38b6e | Như 5a38b6e | Như 5a38b6e | Như 5a38b6e | Như 5a38b6e |
| 5e11ece (thêm PP-PR-057) | Như 5a38b6e | Như 5a38b6e | Như 5a38b6e | Như 5a38b6e | Như 5a38b6e |
| 5e11ece, calibration `stitch_reset` = `stitch_soft_min` = 0,2 m (reset cứng) | Đạt, 0,03 | Đạt, 0,01 | Đạt, 0,06 | — | Đạt |

- Trượt xuất hiện đúng ở commit đưa reset mềm của PP-TS-021 (V7) vào bản giao, và hết khi đặt lại reset cứng 0,2 m trên cùng mã nguồn. PP-PR-058 và PP-PR-057 không đổi kết quả của các ca này.
- Suite của PP-TS-021 chỉ có ca HWA, nên V7 chưa từng được thử với LKA, ELK.
- Cơ chế, xác nhận 2026-11-17 bằng log của bản build nháp (S13 a ELK, VP-4, seed 1): lúc ELK bắt đầu, xe lệch path cũ 0,026 m và 0,084 m/s, dưới dung sai 0,1 m, 0,1 m/s của PP-SWR-031. `pp_intervention_start_exception` vì vậy không áp, và path ELK bị T4 bước 4 trộn với path cũ đang hướng ra ngoài: λ = 0,11–0,14 ở các chu kỳ đầu, tới 1 sau khoảng 0,6 s.
- Hệ quả trong cùng lượt: xe vọt qua, ELK được yêu cầu lại ở phía đối diện. Năm lần can thiệp liên tiếp, v_lat lúc bắt đầu tăng dần 0,60 → 0,71 → 0,81 → 0,87 → 1,00 m/s.
- Với reset cứng 0,2 m, path trước lúc ELK tụt lại sau xe hơn 0,1 m nên ngoại lệ luôn áp. Mâu thuẫn dưới đây vì vậy đã có từ trước nhưng không lộ ra.

**Mâu thuẫn giữa hai requirement.** PP-SWR-031 đòi path thoả PP-SWR-100 đến 102 khi chức năng đổi, trừ lúc xe lệch path cũ hơn 0,1 m hoặc 0,1 m/s. Path của chức năng trước bám theo xe đang trôi ra, nên càng bám sát (reset mềm, hoặc khi tài xế ghi đè theo PP-SWR-039) thì ELK càng bị buộc phải liên tục với một path hướng ra ngoài, và PP-SWR-085, 086 trượt.

## 3. Cách sửa

Đo nháp 2026-11-17, cùng năm file ca của lần hồi quy, thư viện build ngoài cây làm việc từ c56f0bf. Ô ghi requirement trượt và DTLE [m]:

| Phương án | S13 a ELK | S13 c ELK | S5 NCAP 0,6 m/s | F01 c lúc ELK | S5 a |
|---|---|---|---|---|---|
| Bản hiện tại: reset mềm, trộn theo PP-SWR-031 | 085, 086, 091, 102; −0,54 | 085, 086, 100–102; −0,41 | 086; −0,41 | 086, 102; −0,33 | 090; 0,05 |
| A. Reset cứng 0,2 m | Đạt; 0,03 | Đạt; 0,01 | Đạt; 0,06 | — | Đạt; 0,05 |
| B. Reset mềm, không trộn ở chu kỳ đầu của can thiệp | 100–102 (gấp 3–7 lần ngưỡng); 0,03 | 100–102; 0,01 | 100–102; 0,06 | 032, 100–102; 0,07 | 100–102; 0,05 |
| D. Reset mềm, trộn theo ngưỡng từng đoạn (PP-TS-022 V1) | Đạt; 0,03 | 085, 102; −0,28 | 086; −0,40 | 086, 102; −0,34 | Đạt; 0,05 |

- B đưa DTLE về đúng giá trị của reset cứng, nhưng trái PP-SWR-031 như đang viết: bên chấm đòi liên tục vì xe còn trong dung sai.
- D chỉ cứu 2 trong 5 ca.
- A đạt cả năm ca nhưng chỉ che mâu thuẫn, và mất lợi ích của V7 (S1b a, họ S1c).
- C (reset mềm chỉ khi HWA đang lái) chưa đo; không gỡ được trường hợp tài xế ghi đè rồi ELK bắt đầu.

Đề xuất, chờ người dùng quyết định vì đổi requirement:

- PP-SWR-031: ngoại lệ áp cho mọi lần LKA hoặc ELK bắt đầu, bỏ điều kiện 0,1 m và 0,1 m/s; khi đó áp PP-SWR-080. Lý do: can thiệp bắt đầu vì xe đang rời làn, path của chức năng trước hướng ra ngoài; điểm đầu vẫn khớp trạng thái đo (080) và a_y, jerk vẫn bị chặn bởi PP-SWR-110 đến 115.
- Planner: bỏ trộn ở chu kỳ đầu của can thiệp (phương án B). Bên chấm: bỏ điều kiện dung sai ở chỗ chấm PP-SWR-031.
- Đối chiếu đề bài (`docs/reference/G1_Path_Planning.pdf`, trang 1 và mục "Arbitration and continuity"): LKA và ELK cần "an intervention path from the current drifting state back into the lane"; "Transitions between the three must not produce a step in the steering request"; "blending when a function takes over or releases". Đề bài đòi không có bước nhảy ở lệnh lái, tức ở đoạn gần xe, không đòi cả path 3 s liên tục. PP-SWR-031 hiện áp PP-SWR-100 đến 102 trên cả path.
- Hướng sát đề bài hơn, cần đo trước khi chọn: ở chu kỳ đầu của can thiệp chỉ đòi liên tục tại đoạn gần xe (vị trí theo PP-SWR-080, độ cong tại điểm đầu), phần còn lại của path không đòi. Planner khi đó lấy độ cong đầu của path can thiệp từ path cũ thay vì bỏ trộn hoàn toàn. Chưa cài, chưa đo.
- Suite của PP-TS-021 cần thêm ca LKA, ELK.

## 4. Quyết định và cách đã sửa

2026-11-17, người dùng chọn hướng "liên tục ở đoạn gần xe", sát câu của đề bài.

| Nơi | Thay đổi |
|---|---|
| Software Requirements Specification 1.23 | PP-SWR-031: ngoại lệ áp cho chu kỳ đầu của mọi lần LKA, ELK bắt đầu, bỏ điều kiện 0,1 m, 0,1 m/s. PP-SWR-049 mới: độ cong điểm đầu lệch độ cong thật của xe (r / v) ≤ 0,0003 1/m, bằng ngưỡng đoạn 0–1 s của PP-SWR-102 |
| Software Qualification Test Specification 1.46, `eval/metrics.py`, `eval/report_html.py` | Chu kỳ đầu của can thiệp không chấm PP-SWR-100 đến 102; chấm 080 và 049 |
| Planner (`pp_planner.c`, `intervention.c`, `intervention.h`) | Chu kỳ đầu của can thiệp không trộn với path cũ; bỏ `pp_intervention_start_exception` |
| Software Architectural Design 1.11, Software Detailed Design 1.24, Architecture Decision Records 1.6, HARA 1.4 | Câu nhắc PP-SWR-031 và hệ quả của PP-ADR-004 |

Đo nháp 2026-11-17, seed 1, 32 ca, cùng một bên chấm mới, planner trước (c56f0bf) và sau:

| Nhóm ca | Trước | Sau |
|---|---|---|
| Năm ca ELK của mục 1 | Trượt 085, 086, 091, 100–102, 090, 049; DTLE −0,33 đến −0,54 m | Đạt; DTLE 0,01–0,07 m. Còn F01 c lúc ELK trượt 032 (MINOR, có từ trước) |
| S16 d (ELK lần thứ ba) | Trượt 086, DTLE −0,48 m | Đạt, DTLE 0,10 m |
| S6 b | Trượt 090 | Đạt |
| PP-SWR-049, mọi ca có can thiệp | Trượt 23 / 27 ca, lệch 0,0003–0,0006 1/m | Đạt mọi ca, lệch dưới 0,00001 1/m |
| S16 c | Trượt 086, DTLE −0,39 m | Như trước: −0,38 m; chưa phân tích |
| S1 a, S1 c, S2 b, S9 c, S17 a (không có can thiệp) | Đạt | Như trước, cùng giá trị |

- Planner cũ trượt PP-SWR-049 ở hầu hết các ca: trộn với path cũ làm độ cong đầu lệch độ cong xe đang chạy, tức chính cách trộn cũ tạo bước nhảy ở lệnh lái.
- Unit test C 15/15; `tests/eval` 232 đạt, 1 trượt có từ trước ở HEAD (`test_all_old_scenario_values_preserved`: S1b a dài 17 s theo Software Qualification Test Specification 1.45, fixture chưa cập nhật).
- 12 ca chạy lại bằng bên chấm và planner của dự án cho kết quả giống bản nháp ở mọi tiêu chí.

## 5. Xác nhận

| Run ID | Kết quả |
|---|---|
