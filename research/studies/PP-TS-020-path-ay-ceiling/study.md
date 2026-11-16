# PP-TS-020 Trần a_y của path HWA so với aysmax khai báo

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã khóa |
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

Khóa 2026-11-16: [plan.yaml](plan.yaml), suite [PP-TS-020](../../../benchmark/suites/PP-TS-020.yaml).

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

## 5. Kết quả

Bản build nháp ở PP-PR-049 (không dùng để quyết định): trần + 0,3 m/s² cho S1c, F08 a, F08 b trên S1c đạt PP-SWR-051 với DLC 0,60–0,74 m.

## 6. Đề xuất

## 7. Quyết định

- Người quyết, ngày:
- Chọn:
- Lý do:
- Đưa vào: SRS (PP-SWR-001, mục 7), Software Architectural Design mục 9, 11, Software Detailed Design mục 13, HARA (SG-01), `calibration.yaml`
- Hồi quy: run ID
