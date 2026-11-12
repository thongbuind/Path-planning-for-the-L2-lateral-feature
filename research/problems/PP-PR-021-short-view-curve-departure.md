# PP-PR-021 Xe rời làn trong cua khi tầm nhìn camera ngắn

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | PP-SWR-051, 100; target PP-SWR-050 |
| Tái hiện | Lần chạy nháp `build/matrix/Q4` (Q4, VP-0, seed 1), cây làm việc chưa commit; tái hiện riêng S1c 10 m, S1f 40 m, S1f 80 m |

Đây là ghi nhận để điều tra, chưa phải kết luận benchmark.

## 1. Hiện tượng

Lane model không lỗi, chỉ đổi điểm cuối tầm nhìn. ACC tắt với S1, theo hai chế độ với S14.

| Ca | Tầm nhìn [m] | Nhìn trước ở 25 m/s [s] | DLC nhỏ nhất [m] | Trượt |
|---|---|---|---|---|
| S1c | 80 | 3,2 | 0,48 | — |
| S1c | 40 | 1,6 | 0,42 | — |
| S1c | 20 | 0,8 | −0,90 | 051 |
| S1c | 10 | 0,4 | −15,4 | 051, 100 |
| S1f | 80 | 3,2 | 0,61 | — |
| S1f | 40 | 1,6 | 0,06 | — |
| S1f | 20 | 0,8 | −3,59 | 051 |
| S1f | 10 | 0,4 | −5,29 | 051 |
| S14e, ACC đọc LateralLimits | 80 | 2,2 ở 36,1 m/s | −0,31 | 051, 100 |
| S14e, ACC đọc LateralLimits | 40 | 1,1 ở 36,1 m/s | −6,99 | 051 |
| S14e, ACC đọc LateralLimits | 126 | 3,5 ở 36,1 m/s | 0,41 | — |

- Trên đường gần thẳng (S1a) mọi mức đều đạt.
- Mức 10 m và 20 m có thời gian nhìn trước dưới `t_view_hwa` = 1,0 s, nên trong xe thật HWA đã trả lái (ADAS Function Specification 7). Q4 vẫn chạy để thấy khả năng của thuật toán.
- Mức 40 m vẫn trên `t_view_hwa` ở 25 m/s: HWA được phép lái, mà S1f chỉ còn DLC 0,06 m.
- Ở 10 m, path đi gần như thẳng dù vạch trong 0–10 m vẫn cho đủ c0, c1, c2 (camera không nhiễu).

## 2. Nguyên nhân

Đã tái hiện S1c 10 m, S1f 40 m, S1f 80 m (cùng cây làm việc, VP-0, seed 1), đọc qua interface và log simulator.

**Lane model báo đúng.** Ở 10 m, 2·c2 = 0,0040 (bằng độ cong đường) và c0 tăng dần tới 16 m. Planner nhận được thông tin xe đang lệch.

**Path không hướng về tâm làn.** Lúc 14 s, S1c 10 m:

| Điểm path | x [m] | y path [m] | Tâm làn theo lane model [m] |
|---|---|---|---|
| 0 | 0 | 0,05 | 5,45 |
| 10 | 25 | 0,79 | 8,00 |

**T4 chặn mọi thay đổi vì phần xa ngoài tầm nhìn.** So hai path liên tiếp, đã đưa về cùng `base_link` bằng chuyển động thật:

| Ca | Thời gian | Lệch lớn nhất [m] | Ở x [m] | Lệch lớn nhất trong 0–10 m [m] |
|---|---|---|---|---|
| S1c 10 m | 9–13 s, mỗi giây | 0,045–0,047 | ≈ 72 | 0,001–0,002 |
| S1f 40 m | 5–12 s, đa số chu kỳ | 0,045 | ≈ 72 | ≤ 0,001 |
| S1f 80 m | 8–14 s | ≤ 0,016 | 55–72 | ≤ 0,001 |

- 0,045 m = `cont_margin` 0,9 × 0,05 m: bước 4 của T4 đang chặn (Software Detailed Design 7).
- λ = min(1, `cont_margin`·0,05/Δd, …) lấy Δd lớn nhất trên cả path. Phần xa ngoài tầm nhìn là cung tròn ngoại suy, đổi nhiều giữa các frame khi xe vào clothoid, nên λ rất nhỏ. Phần gần xe chỉ được dời 1–2 mm mỗi chu kỳ.
- Path giữ độ cong cũ, thấp hơn đường; xe trôi ra ngoài; độ lệch xa càng lớn thì λ càng nhỏ.
- Thư viện của các lần chạy trên build với `PP_T7=quintic` (T7 A, mặc định). Riêng nhánh QP (T7 C, chưa là bản giao) chỉ có chi phí `qp_w_cont` tại điểm trong tầm nhìn (`generate_hwa_qp`), khác Software Detailed Design T7 C ghi trên mọi điểm. Vênh này không gây ra hiện tượng ở mục 1.
- Ở 80 m phần ngoại suy chỉ còn khoảng 0–3 m cuối path, nên không chặn.

## 3. Cách sửa

Có nhiều cách; so sánh ở [PP-TS-014](../studies/PP-TS-014-continuity-beyond-view/study.md):

| ID | Hướng |
|---|---|
| V1 | T4 một λ cho từng điểm, không tăng theo t |
| V2 | Độ cong của cung ngoài tầm nhìn đổi có giới hạn tốc độ |
| V3 | V1 và V2 |

PP-SWR-100 lấy từ đề bài và đo trên cả đoạn hai path cùng mô tả, nên không đổi requirement. PP-PR-022 có thể cùng gốc.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
