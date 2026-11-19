# PP-TS-022 Giới hạn trộn của T4 khi path phải quay về từ xa

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã quyết: V1; chờ hồi quy |
| Mở ngày | 2026-11-17 |
| Khóa ngày | 2026-11-17 |
| Quyết định ngày | 2026-11-17 |
| Liên quan | PP-SWR-100, 101, 102, 051, 121, 122, 125; PP-PR-057, 058; PP-TS-019, 021; Software Detailed Design mục 7 (T4 bước 4); `cont_margin` |

## 1. Câu hỏi

- Quyết định cần đưa ra: ở T4 bước 4, mỗi điểm của path được so với ngưỡng nào khi tính λ.
- Vì sao cần: sau khi sửa cơ chế 1 của PP-PR-057, F06 d và F03 c vẫn trượt PP-SWR-051 vì path quay về chậm.

Hiện tượng, lượt nháp 2026-11-17 (S1 a + F06 d, seed 1, VP-0, bản có PP-PR-058 và phương án B của PP-PR-057; PP-PR-057 mục 4):

| Đại lượng | Giá trị |
|---|---|
| Hình học đúng được T2 nhận | 6,108 s |
| λ từ 6,3 đến 7,8 s | 0,03–0,09; luôn do lệch ngang quyết định |
| Lệch ngang giữa path ứng viên và path cũ ở đầu xa | 1,0–1,7 m |
| Lệch ngang giữa hai path tại điểm 1 s | 0,03–0,11 m |
| Độ cong của path tại xe về 0 | 7,5 s |
| Lốp đè vạch | 7,86 s; xe lệch lớn nhất 1,10 m |

- Bản hiện tại so mọi điểm với ngưỡng đoạn 0–1 s (`cont_margin` · 0,05 m). Ở đầu xa, PP-SWR-100 cho 0,2 m.
- PP-TS-021 loại trộn theo từng đoạn (V3, V4 ở đó): không giúp ca nào, thêm trượt ở S14 e và F06 e. Suite của PP-TS-021 không có ca nào cần path quay về nhanh từ xa (F06 d, F03 c).
- Trộn nhanh hơn có hai mặt: path cũng bám một reference line sai nhanh hơn. Vì vậy bộ chạy phải có cả nhiễu (F01), cua chữ S (S14 e) và lỗi ngắn hơn `T_confirm`.

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Một λ cho cả path; mọi điểm so với ngưỡng đoạn 0–1 s | — | Mốc; Software Detailed Design 1.20 |
| V1 | Một λ cho cả path; mỗi điểm so với ngưỡng của đoạn mình (0–1 s, 1–2 s, sau 2 s), λ là giá trị nhỏ nhất | `cmake: {PP_T4_BLEND: banded}` | Path gửi vẫn là tổ hợp lồi của hai path, nên giữ lập luận khả thi của Software Detailed Design mục 7. Chưa có trong PP-TS-019, 021 |
| Không xét | λ riêng từng đoạn, nối tuyến tính | — | V3 của PP-TS-021, đã loại và đã xoá khỏi code. Người dùng chốt không cài lại (mục 3, điểm 2) |

- V1 cần code T4 mới, chọn lúc build; bản giao không có nhánh chọn lúc chạy.
- Ước lượng từ log cho V1 ở ca trên: λ lớn hơn V0 khoảng 3–4 lần. Chưa cài, chưa đo.

## 3. Cách đánh giá (khóa trong plan.yaml)

Khóa 2026-11-17: [plan.yaml](plan.yaml), suite [PP-TS-022](../../../benchmark/suites/PP-TS-022.yaml).

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | Requirement của SRS trong phạm vi của suite, gồm PP-SWR-100 đến 102 theo ba đoạn; a_y đo trên xe trong giới hạn R79 5.6.2.1.1 (`PP-TS-020/R79-5.6.2.1.1`) |
| Xếp hạng | SQTS mục 9; trong đó PP-SWR-050 (lệch tâm làn) và PP-SWR-004 (jerk, tốc độ quay vô lăng vòng kín) để thấy cái giá của trộn nhanh |
| Bộ chỉnh, bộ kiểm | Suite PP-TS-022: bộ chỉnh seed 1, 2; bộ kiểm seed 3, 4 |
| Ngân sách chỉnh | Không có; mọi phương án dùng `cont_margin` khởi đầu 0,9 |
| Coi như ngang nhau khi | PP-SWR-051 chênh < 0,01 m; PP-SWR-050 chênh < 0,005 m |

Người dùng duyệt 2026-11-17:

| # | Điểm | Đã chốt |
|---|---|---|
| 1 | Baseline | Commit và hồi quy PP-PR-058 cùng phương án B của PP-PR-057 trước; study chạy trên baseline đó |
| 2 | Có cài lại V2 không | Không; PP-TS-021 đã loại. Cài lại nếu muốn biết nó có giúp F06 d không |
| 3 | Ca đã thấy kết quả | S1 a + F06 d và S1 a + F03 c (seed 1) đã chạy nháp, nên nằm ở bộ chỉnh. Bộ kiểm dùng ca chủ S1 c và seed 3, 4 |
| 4 | Thời lượng lỗi | F06, F03 chỉ có 1 s và 2 s. Thêm biến thể 1,5 s và 3 s là việc của benchmark (PP-PR-057 mục 3); study này không chờ |

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| [20261117-1315-study-PP-TS-022-d2e7d27](../../runs/20261117-1315-study-PP-TS-022-d2e7d27/summary.md) | V0, V1 | Theo plan khóa 2026-11-17; 50 lượt mỗi phương án (chỉnh 20, kiểm 30). Chạy trong git worktree sạch ở d2e7d27 (cây chính có thay đổi của phiên khác); 1,5 phút, 2 tiến trình |

## 5. Kết quả

**Cài V1 (bước 3, 2026-11-17, cây làm việc chưa commit).** `PP_T4_BLEND=banded` (mặc định `single`), `pp_stitch_blend`:

- Lệch của mỗi điểm chia cho hệ số của đoạn mình (1, 2, 4) trước khi lấy giá trị lớn nhất; λ vẫn là một số cho cả path. Điểm ở đúng 1 s, 2 s thuộc đoạn trước.
- Bản `single` cho thư viện giống bản trước từng byte.
- Unit test `test_blend_limit_of_a_far_change`; unit test C 15/15 đạt ở cả hai bản build.

**Lần dò nháp 2026-11-17 (chỉ để dò lỗi, không dùng để quyết định).** Seed 1, VP-0, 9 ca của bộ chỉnh; thư viện build ngoài cây làm việc, có PP-PR-058 và phương án B của PP-PR-057. Ô ghi DLC nhỏ nhất [m] / lệch giữa hai path chia ngưỡng / tốc độ quay vô lăng RMS [rad/s]:

| Ca | V0 | V1 |
|---|---|---|
| S1 a + F06 d | −0,29 / 0,45 / 0,029 (trượt 051) | 0,03 / 0,91 / 0,037 |
| S1 a + F03 c | −0,24 / 0,45 / 0,035 (trượt 051) | −0,28 / 0,90 / 0,045 (trượt 051) |
| S1 a + F06 a | 0,64 / 0,31 / 0,019 | 0,61 / 0,90 / 0,026 |
| S1 c + F01 c | 0,51 / 0,43 / 0,040 | 0,48 / 0,92 / 0,051 |
| S12 a | 0,51 / 0,43 / 0,040 | 0,48 / 0,92 / 0,051 |
| S1 a + F02 b | 0,79 / 0,35 / 0,007 | 0,79 / 0,90 / 0,007 |
| S1 a; S1 c; S2 b | Đạt | Như V0, cùng giá trị |

- Không thấy lỗi cài đặt: không ca nào trượt PP-SWR-100 đến 102, lệch giữa hai path dừng ở 0,90–0,92 ngưỡng, đúng `cont_margin`.
- Hai mặt đúng như mục 1: F06 d hết trượt nhưng chỉ còn 0,03 m; ca nhiễu mất 0,03 m DLC và vô lăng quay nhiều hơn khoảng 25–30 %; F03 c không tốt lên.

Lần chạy chính thức [20261117-1315-study-PP-TS-022-d2e7d27](../../runs/20261117-1315-study-PP-TS-022-d2e7d27/summary.md). Số lượt trượt (chỉnh / kiểm): V0 4 / 5; **V1 2 / 3**. Không ca nào chạy đủ cả hai phương án mà V1 trượt thêm.

| Ca (2 seed mỗi ô) | V0 | V1 |
|---|---|---|
| S1 a + F06 d (chỉnh) | Trượt PP-SWR-051; lệch tâm 1,08 m | Đạt; 0,75 m |
| S1 c + F06 d (kiểm) | Trượt 051; 1,69 m | Đạt; 0,77 m |
| S1 a + F03 c (chỉnh) | Trượt 051; 1,04 m | Trượt 051; 1,08 m |
| S1 c + F03 c (kiểm) | Trượt 051; 1,03 m | Trượt 051; 1,15 m |
| S14 e, ACC đọc LateralLimits (kiểm) | Trượt 051 | Trượt 051 |
| Mọi ca còn lại | Đạt | Đạt |

Cái giá của V1, trên các lượt có chỉ số của cả hai phương án:

| Chỉ số | Kết quả của V1 so với V0 |
|---|---|
| PP-SWR-050 (lệch tâm làn, nên nhỏ) | Xấu hơn hơn 0,005 m ở 19 / 36 lượt, tốt hơn ở 6, ngang ở 11. Xấu nhất +0,12 m (S1 c + F03 c), +0,10 m (S1 c + F06 e). Tốt nhất −0,92 m (F06 d) |
| Cùng ca không lỗi hoặc nhiễu | S1 a + F06 a +0,06 m; S1 c + F01 c +0,03 đến +0,08 m; S12 a +0,03 m; S1 a + F02 b +0,01 m; S1 f −0,01 đến −0,03 m |
| PP-SWR-004 (tốc độ quay vô lăng RMS, nên nhỏ) | Trung vị tăng 4 % trên 14 lượt; tới +36 % ở S1 c + F01 c (VP-5): 0,041 → 0,055 rad/s |
| PP-SWR-125 (theo c2 sai, nên nhỏ) | Xấu hơn ở F06 d (+0,12 và +0,24) và F06 a (+0,05) |
| PP-SWR-003 (jerk ngang) | Tăng 0,03 đến 0,5 m/s³ ở các ca F06, F03; dưới giới hạn 5 m/s³ |

- V1 chỉ sửa được một nhóm: F06 d, 4 lượt trên 50. F03 c vẫn trượt và hơi xấu đi; S14 e không đổi.
- Cái giá trải rộng hơn lợi ích: path theo lane model mới nhanh hơn ở cả ca lỗi ngắn (F06 a, e), nhiễu (F01 c, S12 a) lẫn ca sạch có đổi nhỏ, nên lệch tâm và tốc độ quay vô lăng tăng ở ca đó.
- Giới hạn của kết quả: bộ chạy không có ca ELK nên ELK lặp (PP-PR-063) không ảnh hưởng; không có hồi quy cả bộ cho V1. Bộ kiểm dùng ca chủ S1 c, nên ca F06 d trên S1 a chỉ có ở bộ chỉnh.

## 6. Đề xuất

2026-11-17, sau lần chạy [20261117-1315-study-PP-TS-022-d2e7d27](../../runs/20261117-1315-study-PP-TS-022-d2e7d27/summary.md), chờ người dùng quyết định (bước 7):

- Theo thứ tự ưu tiên của Software Qualification Test Specification mục 9 (an toàn, quy định, cảm nhận người lái), V1 đứng đầu: ít lượt trượt hơn ở cả bộ chỉnh lẫn bộ kiểm, không trượt thêm.
- Tôi nghiêng về chọn V1, nhưng lợi ích mỏng: một nhóm lỗi (F06 d), trong khi F03 c, S14 e cần cách khác; DLC của F06 d chỉ vừa qua ngưỡng ở lượt dò nháp (khoảng 0,03 m).
- Cái giá nằm ở ca thường gặp: nhiễu đêm, mưa (F01 c, S12 a) lệch tâm tăng 0,03–0,08 m và vô lăng quay nhiều hơn tới 36 %.
- Phương án khác: giữ V0 và sửa gốc ở T2 (PP-PR-057, PP-TS-005 V3: nhận theo bằng chứng); khi đó V1 có thể không còn cần. Chỉ nên chọn cách này nếu chấp nhận F06 d trượt trong thời gian chờ.
- Khi đưa V1 vào (bước 8): đổi `PP_T4_BLEND` mặc định sang `banded`, cập nhật Software Detailed Design mục 7 (T4 bước 4) và Architecture Decision Records, bỏ nhánh `single`, chạy hồi quy.

## 7. Quyết định

- Người quyết, ngày: thongbui, 2026-11-17.
- Chọn: V1. T4 bước 4 so mỗi điểm với ngưỡng của đoạn thời gian chứa nó (0–1 s, 1–2 s, sau 2 s), vẫn một λ cho cả path.
- Lý do: theo đề xuất ở mục 6, lần chạy 20261117-1315-study-PP-TS-022-d2e7d27: ít lượt trượt hơn ở cả bộ chỉnh và bộ kiểm, không trượt thêm; sửa F06 d. Cái giá (lệch tâm và tốc độ quay vô lăng ở ca nhiễu) được chấp nhận, theo dõi ở hồi quy.
- Đưa vào: Software Detailed Design 1.25 (T4 bước 4); code giao (`stitching.c`, `stitching.h`); bỏ tuỳ chọn build `PP_T4_BLEND` và nhánh `single` (git giữ lại ở d2e7d27).
- Hồi quy: chờ.
