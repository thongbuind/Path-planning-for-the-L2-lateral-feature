# PP-TS-020 Trần a_y của path HWA so với aysmax khai báo

| Mục | Nội dung |
|---|---|
| Trạng thái | Đang chạy |
| Mở ngày | 2026-11-16 |
| Khóa ngày | 2026-11-16 |
| Quyết định ngày | — |
| Liên quan | PP-SWR-001, 005, 006, 007, 051, 136, 151; SG-01; PP-PR-049, 054; PP-TS-002; R79 5.6.2.1.1, Annex 8 3.2.1, 3.2.2; R171 5.3.7.1 |

## 1. Câu hỏi

- Quyết định cần đưa ra: trần a_y mà path HWA được dùng có tách khỏi aysmax khai báo không, và tách bao nhiêu.
- Vì sao cần: trần của path đang bằng aysmax = 2,5 m/s² (PP-SWR-001). Ở cua cần đúng aysmax, path không còn phần a_y nào để kéo xe về khi xe đã lệch. Thiếu hụt Δa không đổi cho lệch ngang ½·Δa·t².
- Khác PP-TS-002: study đó hỏi khoảng nới 40 % trong 2 s cho cua thấy muộn (S1b), đã loại mức liên tục + 0,3 mà không chạy. Study này hỏi mức liên tục, cho cua nằm trong aysmax.

Hiện tượng ở [20261115-1126-suite-full-7495822](../../runs/20261115-1126-suite-full-7495822/report.md), PP-SWR-051 (DLC nhỏ nhất):

| Ca | a_y cần [m/s²] | DLC nhỏ nhất [m] | Lượt trượt |
|---|---|---|---|
| S1 g | 2,08 | 0,45 đến 0,76 | 0/6 |
| S1 c | 2,5 | 0,22 đến 0,52 | 0/6 |
| S12 a | 2,5 | −0,06 đến 0,50 | 1/110 |
| G01 trên S1c | 2,5 | −0,34 đến 0,37 | 13/60 |
| F08 a trên S1c | 2,5 | −1,21 đến −0,91 | 6/6 |
| F08 b trên S1c | 2,5 | −1,28 đến −0,97 | 3/3 |

Quy định:

| Mục | Nội dung |
|---|---|
| R79 5.6.2.1.1 | Xe không vượt vạch khi a_y dưới aysmax. Hệ thống được vượt aysmax tới 0,3 m/s², không quá mức của bảng 5.6.2.1.3 (M1: 3 m/s²) |
| R79 Annex 8, 3.2.1 | Bài giữ làn: cua cần 80–90 % aysmax |
| R79 Annex 8, 3.2.2 | a_y đo trên xe trong giới hạn của 5.6.2.1.1 |
| R171 5.3.7.1 | Cùng các con số |

## 2. Phương án

`ay_margin_hwa` là calibration parameter mới: trần a_y của path HWA = aysmax + `ay_margin_hwa`.

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Trần path = aysmax | `calibration: {ay_margin_hwa: 0.0}` | Mốc |
| V1a | Trần path = aysmax + 0,1 | `calibration: {ay_margin_hwa: 0.1}` | |
| V1b | Trần path = aysmax + 0,2 | `calibration: {ay_margin_hwa: 0.2}` | Chừa 0,1 m/s² cho controller |
| V1c | Trần path = aysmax + 0,3 | `calibration: {ay_margin_hwa: 0.3}` | Hết phần R79 cho; không chừa cho controller |
| V2 | Như V1b khi `lateral_limit_reached` tắt; trần aysmax khi cờ bật | `calibration: {ay_margin_hwa: 0.2}`, `cmake: {PP_AY_MARGIN_GATE: 'ON'}` | Thêm 2026-11-16 sau chẩn đoán S1b b (mục 5). Cờ của chu kỳ trước |
| Không xét | Hạ aysmax khai báo xuống 2,2, giữ trần 2,5 | — | Đưa S1c ra khỏi phạm vi của PP-SWR-051 sau khi đã thấy kết quả; hạ năng lực khai báo |
| Không xét | Khoảng nới 40 % trong 2 s | — | PP-TS-002 |

Cơ chế chung của V1a đến V1c:

| Phần | Cách làm |
|---|---|
| T10 bước 2 | Cắt κ theo aysmax + `ay_margin_hwa` thay cho aysmax, ở cả hai lần cắt của HWA (`pp_hwa_path_limits`) |
| Cua cần ≤ aysmax | Path cần đúng a_y của tâm làn; phần trên aysmax chỉ xuất hiện khi path kéo xe về. Không có chế độ riêng |
| Cua cần > aysmax (S1b) | Path nằm ở aysmax + `ay_margin_hwa` thay cho aysmax: vẫn trong R79 5.6.2.1.1, xe lệch ra ít hơn |
| `v_max` của LateralLimits | Giữ theo aysmax |
| `lateral_limit_reached`, PP-SWR-005 đến 007 | Giữ ngưỡng theo aysmax |
| LKA, ELK | Không đổi |
| T7 C (bản QP) | Không đổi: ràng buộc a_y của QP vẫn theo aysmax. Study chạy bản quintic |

## 3. Cách đánh giá (khóa trong plan.yaml)

Khóa 2026-11-16: [plan.yaml](plan.yaml), suite [PP-TS-020](../../../benchmark/suites/PP-TS-020.yaml). Mở lại và khóa lại cùng ngày sau lần chạy 20261116-1548: S1b a, b, c chạy dài hơn (Software Qualification Test Specification 1.45, PP-PR-056), thêm V2; mọi phương án chạy lại.

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | Requirement của SRS trong phạm vi của suite; a_y đo trên xe trong giới hạn R79 5.6.2.1.1 (`ay_vehicle_r79_within_limits` của bên chấm) |
| Xếp hạng | SQTS mục 9. Trong các phương án không bị loại, chọn `ay_margin_hwa` nhỏ nhất |
| Bộ chỉnh, bộ kiểm | Suite PP-TS-020: bộ chỉnh seed 1, 2; bộ kiểm seed 3, 4 |
| Ngân sách chỉnh | Không có; mỗi phương án là một giá trị của cùng một tham số |
| Coi như ngang nhau khi | PP-SWR-051 chênh < 0,01 m; PP-SWR-050 chênh < 0,005 m |

Người dùng duyệt 2026-11-16:

| # | Điểm | Đã chốt | Cài đặt (2026-11-16) |
|---|---|---|---|
| 1 | PP-SWR-001 hiện chấm path ≤ 2,5 m/s²; V1 trượt theo cách cài | Trong study, chấm câu đề xuất: a_y của path ≤ aysmax + 0,3 m/s². Bỏ PP-SWR-001 bản hiện tại khỏi phạm vi của suite | Tiêu chí `PP-TS-020/PP-SWR-001` ở `eval/proposed.py` |
| 2 | `ay_vehicle_r79_within_limits` đã đo nhưng chưa là tiêu chí | Tiêu chí loại của study: a_y đo trên xe trong giới hạn R79 5.6.2.1.1 (Annex 8, 3.2.2). Thêm requirement nếu chọn V1 | Tiêu chí `PP-TS-020/R79-5.6.2.1.1` ở `eval/proposed.py` |
| 3 | Suite chỉ chạy VP-0 | Thêm VP-5, profile tệ nhất về PP-SWR-051 ở lần chạy full | Khóa `profile` của một ca trong `eval.sweep`; các ca chạm aysmax trên S1c chạy thêm VP-5 |
| 4 | G01 không chạy được bằng `eval.study` | Xác nhận G01 trên S1c ở lần hồi quy của bước 8 | — |

Hai tiêu chí ở `eval/proposed.py` chỉ được tính khi suite liệt kê ở khóa `proposed`.

Tiêu chí của điểm 1 và 2 viết từ câu đề xuất và từ R79, không từ calibration của planner: ngưỡng cố định aysmax + 0,3, không đọc `ay_margin_hwa`. Bộ full và hồi quy giữ PP-SWR-001 bản hiện tại tới khi SRS đổi.

Ca chọn từ nhóm trượt PP-SWR-051 trên S1c của lần chạy full, cùng các ca phải giữ (S1, S1b, S2, S14). F17 b trên S1c là đối chứng: bản nháp của PP-PR-049 cho thấy trần cao hơn không đổi ca này (PP-PR-054).

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| [20261116-1548-study-PP-TS-020-04ae8c5](../../runs/20261116-1548-study-PP-TS-020-04ae8c5/summary.md) | V0, V1a, V1b, V1c | Theo plan khóa 2026-11-16. S1b quá ngắn để chấm R79 (PP-PR-056); thay bằng lần dưới |
| [20261116-1607-study-PP-TS-020-d1d50de](../../runs/20261116-1607-study-PP-TS-020-d1d50de/summary.md) | V0, V1a, V1b, V1c, V2 | Khóa lại: S1b a, b 17 s, c 15 s; thêm V2 |

## 5. Kết quả

Bản build nháp ở PP-PR-049 (không dùng để quyết định): trần + 0,3 m/s² cho S1c, F08 a, F08 b trên S1c đạt PP-SWR-051 với DLC 0,60–0,74 m.

**Lần chạy chính thức** [20261116-1548-study-PP-TS-020-04ae8c5](../../runs/20261116-1548-study-PP-TS-020-04ae8c5/summary.md). Số lượt trượt (chỉnh / kiểm): V0 4 / 10; V1a 0 / 8; V1b 0 / 6; V1c 0 / 6.

| Ca (2 seed mỗi ô) | V0 | V1a | V1b | V1c |
|---|---|---|---|---|
| S1c + F08 a, VP-0 và VP-5 | 051 | Đạt | Đạt | Đạt |
| S1c + F06 e, VP-5 | 051 | Đạt | Đạt | Đạt |
| S1c + F08 b, VP-0 và VP-5 | 051 | 051 | Đạt | Đạt |
| S1b b, ACC bỏ qua LateralLimits | Đạt | Đạt | R79-5.6.2.1.1 | R79-5.6.2.1.1 |
| S1c + F17 b, VP-0 và VP-5 (đối chứng) | 051 | 051 | 051 | 051 |
| Mọi ca còn lại, gồm S1 c, S1 g, S12 a, S1b a, c, e, f, S14 a | Đạt | Đạt | Đạt | Đạt |

- Không phương án nào đạt mọi tiêu chí. Theo luật ở mục 3, chưa chọn được.
- V1b, V1c trượt tiêu chí loại R79: a_y đo trên xe ở S1b b (cua cần 4,2 m/s², bài R79 Annex 8, 3.2.2) vượt giới hạn của 5.6.2.1.1. Path nằm ở 2,7 hoặc 2,8 m/s²; xe vượt thêm. Biên cho controller dưới 0,2 m/s² không đủ ở cua này.
- V1a giữ được R79 nhưng còn trượt F08 b (0,3 °/s, PP-SWR-136).
- F17 b trượt ở mọi phương án, đúng như đối chứng: không cùng gốc (PP-PR-054).
- Lệch tâm làn xấu nhất (PP-SWR-050): chỉnh V0 0,50 m, V1 0,12–0,13 m; kiểm V0 0,45 m, V1 0,28 m. PP-SWR-002, 053, 003 không đổi.
- `results.json` của `eval.study` chỉ ghi ID trượt và target, không ghi giá trị của tiêu chí. Chưa có a_y của xe ở S1b b và DLC của F08 b theo từng phương án.

**Chẩn đoán S1b b** (2026-11-16, nháp: thư viện của lần chạy chính thức, seed 3, chỉ để hiểu cơ chế). Chi tiết ở [PP-PR-056](../../problems/PP-PR-056-s1bb-vehicle-ay-above-r79.md).

| Phương án | a_y path | a_y xe lọc lớn nhất | Thời gian trên 2,8 m/s² |
|---|---|---|---|
| V0 | 2,50 | 3,19 | 1,89 s |
| V1a | 2,60 | 3,29 | 1,91 s |
| V1b | 2,70 | 3,39 | 1,93 s |

- Xe vượt khi path đã bão hòa, không phải khi path kéo xe về: path đứng ở trần từ 9 s, xe lệch khỏi path 0,18 m và vượt path 0,5–0,7 m/s².
- Margin cộng thẳng vào a_y của xe (mỗi 0,1 m/s² thêm 0,1), không giúp gì ở ca này: DLC nhỏ nhất 0,80 m ở mọi phương án.
- Thời gian trên 2,8 m/s² bị cắt ở cuối log ở cả ba phương án. V0 và V1a "đạt" phần thời lượng của R79 vì ca ngắn, không phải vì hành vi.

**Lần chạy chính thức sau khi khóa lại** [20261116-1607-study-PP-TS-020-d1d50de](../../runs/20261116-1607-study-PP-TS-020-d1d50de/summary.md). Số lượt trượt (chỉnh / kiểm): V0 6 / 12; V1a 2 / 12; V1b 2 / 8; V1c 2 / 8; V2 6 / 16.

| Ca (2 seed mỗi ô) | V0 | V1a | V1b | V1c | V2 |
|---|---|---|---|---|---|
| S1b a, b, ACC bỏ qua LateralLimits | R79 | R79 | R79 | R79 | R79 |
| S1b c, ACC bỏ qua LateralLimits | Đạt | R79 | R79 | R79 | Đạt |
| S1c + F08 a, VP-0 và VP-5 | 051 | Đạt | Đạt | Đạt | 051 |
| S1c + F06 e, VP-5 | 051 | Đạt | Đạt | Đạt | 051 |
| S1c + F08 b, VP-0 và VP-5 | 051 | 051 | Đạt | Đạt | 051 |
| S1c + F17 b, VP-0 và VP-5 (đối chứng) | 051 | 051 | 051 | 051 | 051, 100 |
| Mọi ca còn lại | Đạt | Đạt | Đạt | Đạt | Đạt |

- S1b a, b trượt R79 ở mọi phương án, kể cả V0 với path ở aysmax. a_y của xe vượt aysmax + 0,3 quá 2 s không do trần của path: đây là trượt của bản hiện tại, trước bị ca ngắn che (PP-PR-056). Ở hai ca này tiêu chí R79 không phân biệt được các phương án.
- S1b c (110 km/h, cua cần 3,1 m/s²): V0, V2 đạt, V1a đến V1c trượt. Margin đẩy a_y của xe qua giới hạn ở ca này.
- V2 giống V0 ở mọi ca S1c: cờ giới hạn bật ở S1c, nên margin bị tắt đúng ở ca cần nó. V2 còn thêm trượt PP-SWR-100 ở F17 b, do trần đổi bậc khi cờ đổi. Loại V2.
- Ở S1c, V1b và V1c như nhau và tốt nhất: gỡ F08 a, F08 b, F06 e. Lệch tâm làn xấu nhất (PP-SWR-050): V0, V2 0,50 / 0,45 m; V1 0,12–0,13 / 0,28 m.

## 6. Đề xuất

2026-11-16, sau lần chạy 20261116-1607, chờ người dùng:

- 2026-11-16: chờ [PP-TS-021](../PP-TS-021-stitch-start/study.md) (T4), rồi chạy lại study này trên bản đã sửa T4.
- Chưa chọn. Bản hiện tại trượt bài R79 Annex 8, 3.2.2 ở S1b a, b; chưa sửa thì chưa chấm được margin về phía R79. Ưu tiên PP-PR-056: tách phần do Lateral Controller chạy thử và phần do T4 nối path cũ khi xe lệch dưới `stitch_reset`.
- V2 loại: cờ bật ở S1c, và trần đổi bậc làm trượt PP-SWR-100.
- Giữa V1a và V1b: V1b giữ làn tốt hơn (F08 b); cả hai trượt S1b c. Chọn sau khi PP-PR-056 có nguyên nhân, vì cách sửa đó đổi phần a_y xe vượt path.
- Chưa rõ vì sao cờ giới hạn bật ở S1c (cua cần đúng aysmax, ngưỡng bật aysmax + `delta_ay`). Có thể do T10 bước 3 lấy độ cong lớn hơn của camera và T5. Cần chẩn đoán; có thể là problem report riêng.

Đề xuất trước đó (2026-11-16, sau lần chạy 20261116-1548), đã làm:

- Chưa chọn phương án nào. Kết quả R79 ở S1b chưa đủ tin để loại hay giữ phương án (PP-PR-056).
- Bước 1, bên chấm: kéo dài cung của S1b để đo trọn 2 s của R79, ghi lý do ở SQTS. Đây là sửa kịch bản sau khi thấy kết quả, nên mở lại khóa.
- Bước 2, thêm phương án V2: trần aysmax + `ay_margin_hwa` khi cờ `lateral_limit_reached` tắt; khi cờ bật (cua cần vượt aysmax + `delta_ay`) thì trần giữ aysmax (PP-SWR-006 không đổi). Lý do: margin có ích ở S1c (kéo xe về) và có hại ở S1b (cộng thẳng vào a_y xe).
- Dùng cờ thay cho so trực tiếp a_y cần với aysmax: S1c cần đúng aysmax, nên a_y cần ước lượng dao động quanh aysmax theo nhiễu và trần sẽ bật tắt đúng ở ca cần margin. Cờ có trễ `delta_ay` và xác nhận `T_flag`.
- Bước 3: chạy lại mọi phương án (V0, V1a, V1b, V1c, V2) trên suite đã sửa.
- 2026-11-16: người dùng đồng ý cả ba bước.

## 7. Quyết định

- Người quyết, ngày:
- Chọn:
- Lý do:
- Đưa vào: SRS (PP-SWR-001, mục 7), Software Architectural Design mục 9, 11, Software Detailed Design mục 13, HARA (SG-01), `calibration.yaml`
- Hồi quy: run ID
