# PP-PR-006 Vào cua vượt aysmax: xe bám trễ, stitching reset làm path nhảy

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, đã tìm nguyên nhân |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-100 |
| Tái hiện | Lần chạy nháp: S1b b, S1b e, seed 1, `PP_T7=qp`; quintic cùng cơ chế nhưng dưới ngưỡng |

## 1. Hiện tượng

- S1b b, e với T7 C: lệch ngang giữa hai path liên tiếp 0,065 và 0,068 m (ngưỡng 0,05 m).
- Mỗi ca chỉ trượt ở 1 đến 3 chu kỳ. Ở các chu kỳ đó, điểm đầu path mới lệch path cũ 0,02 đến 0,05 m. Các chu kỳ còn lại ≤ 0,04 m.
- Quintic trên cùng ca: 0,036 đến 0,047 m, sát ngưỡng.

## 2. Nguyên nhân

- Lúc vào cua, a_y của path tăng nhanh tới aysmax. Bộ điều khiển trong simulator bám trễ: xe cách điểm đầu path tới 0,2 m.
- T4 (`pp_stitch_start`): khi xe cách path cũ quá `stitch_reset` (0,2 m), điểm đầu lấy theo trạng thái đo của xe. T4 trộn chỉ giảm bớt bước nhảy.
- T7 C tăng a_y nhanh hơn quintic (tới aysmax sau khoảng 0,6 s thay vì 1,3 s), nên sai số bám vượt 0,2 m sớm hơn và nhiều lần hơn.

## 3. Cách sửa

Chưa chọn. Các hướng chung, không riêng cho S1b:

| Hướng | Nội dung |
|---|---|
| A | T4 đưa điểm đầu về trạng thái đo dần dần thay vì một lần khi vượt `stitch_reset` |
| B | Chọn lại `stitch_reset` trong sweep P1 (PP-TS-004) |
| C | T7 C giới hạn tốc độ tăng a_y ở đầu path theo độ trễ bám đã biết |

Phân tích thêm 2026-11-13:

- Lateral Controller chạy thử (Software Qualification Test Specification 4.6) có feedforward theo κ tại `actuator_delay`, nhưng không bù khâu bậc một τ = 0,1 s của EPS. Với a_y path tăng khoảng 4,2 m/s³ (T7 C), riêng τ gây thiếu khoảng 0,4 m/s² a_y lúc vào cua; quintic (khoảng 1,9 m/s³) thiếu khoảng 0,2 m/s². Đây là giả thuyết cho phần lớn sai số bám 0,2 m; cần đo trên log.
- Controller thật chưa biết. C làm planner phụ thuộc vào độ trễ của một controller cụ thể. A không phụ thuộc controller. Đề xuất A.
- Sửa controller chạy thử là sửa bên chấm sau khi thấy kết quả: chỉ làm nếu có nguồn cho thấy controller thật bù độ trễ của actuator, và phải chạy lại mọi phương án.

Chỉnh `qp_w_jerk` (3, 10, 30) trên lần chạy nháp: không sửa được S1b e và làm thời gian tính tăng, nên không chọn.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

Quan sát thêm ở [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md) (T7 quintic): PP-SWR-100 sát ngưỡng 0,050–0,056 m ở S7 a và ncap-oncoming (3), S8b c VP-1 (1), S17 b VP-4 (1), S1b a (1). Chưa xác định có cùng cơ chế stitching reset không.
