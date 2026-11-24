# mlp_jerk_direct

Sổ tay phát triển, không phải kết quả. Kết quả chính thức chỉ nằm ở PP-TS-031 và `research/runs/`.

## Ý tưởng

Đối chứng của PP-TS-031: MLP xuất thẳng 30 bước jerk, kẹp vào hàng jerk cứng (`|j + v³κ'| ≤ jerk_limit`), tích phân
chính xác từ trạng thái đầu, rồi qua T10 và T4 chung của LCC. Không có QP, không có quintic, không có nghiệm thay thế.
Model và dữ liệu: `../mlp/notes.md`, `../mlp/data_card.md` (model vòng 1, cùng model với warm start).

## Quyết định

- Guard tự nhiên duy nhất: đặc trưng không hữu hạn (mã 1), ngoài miền 5 σ (mã 2), path tích phân không hữu hạn (mã 3)
  thì trả false (không có path); LCC xử lý như khi T7 không có path.
- `PP_T7_SUPPORT_FLOOR = 0`: như `qp_jerk_admm` (teacher). Nhãn đã mang hành vi giữ a_y ở trần trong cua gắt; đối chứng
  phải cho thấy MLP tự làm được gì, không có lưới an toàn riêng mà QP không có.
- work = 1 khi suy luận, 0 khi dừng ở bước kiểm đầu vào.

## Kiểm L0

- Test riêng (`lab_test_mlp_jerk_direct`) và test contract chung: đạt (telemetry OFF và ON, không cảnh báo). Gồm đặc
  trưng, suy luận, gương, ngoài miền như `../mlp/c/mlp_l0.h`; path trùng jerk đã kẹp tích phân; kẹp jerk; ngoài miền thì
  không có path; đường thẳng ở giữa làn cho y = 0.
- `test_lcc_step` (test của planner, chạy cùng ctest) trượt, đúng như giả thuyết "dự kiến có trượt mới":
  - v = 182 m/s (PP_LONGITUDINAL_PLAN_V_MAX_MPS): ngoài miền nên không có path (dòng 331–334);
  - trong override, path phải song song làn tại offset của xe: MLP lệch tới 0,3 m (dòng 390, 427);
  - sau override, đưa về giữa làn lệch 0,3 m không đủ (404); bám xe trước khi mất hai vạch: không giữ được mode FOLLOW
    (530–541). Nguyên nhân: lỗi tích lũy vòng kín (MLP chỉ học trạng thái do QP lái).

## Vòng DAgger (thử, không dùng)

Teacher lái bằng model vòng 1 trên 40 kịch bản mới, gộp nhãn, học lại (vòng 2, `../mlp/notes.md`).

| | test_lcc_step: check trượt | Lệch output vòng hở so với 1000 vòng, max / p99 [mm] | Lượt trượt (quick) |
|---|---|---|---|
| Vòng 1 (đang dùng) | 54 | 398,9 / 326,3 | S1g (051) |
| Vòng 2 (DAgger) | 12 | 597,0 / 475,3 | S1g, S24 a (051) |

Vòng 2 qua được đưa về giữa làn và FOLLOW, nhưng quick bench xấu hơn rõ, nên giữ vòng 1. Một vòng DAgger không đủ; cần
nhiều vòng và nhiều dữ liệu hơn trần 10 000 cửa sổ.

## Lần dò bằng quick bench

Mốc: `quintic_duration` lệch so với 1000 vòng 167,5 / 136,9 mm, không trượt; `qp_jerk_admm` 0,2 / 0,04 mm.

| Lượt | mlp_jerk_direct (vòng 1) | quintic_duration |
|---|---|---|
| Lệch so với 1000 vòng, max / p99 / mean [mm] | 398,9 / 326,3 / 113,9 | 167,5 / 136,9 / 30,5 |
| Lệch so với quintic_duration, max / p99 [mm] | 393,5 / 312,9 | — |
| Chu kỳ không có path (vòng hở): S1d / S1g F01a / S1b a | 0,5 % / 6 % / 75 % | — |
| Trượt mới | S1g: PP-SWR-051 | — |
| S1d vòng kín: 068 / 069 / 050 (mốc qp_jerk_admm) | 1,23 / 1,20 / 0,71 (1,26 / 0,35 / 0,04) | 1,29 / 0,37 / 0,03 |
| Trung vị p99 LCC [ms], phần chung 10 lượt | 0,80 (tỉ số 0,56 so với qp_jerk_admm 150 vòng) | 1,23 |

- Tỉ lệ chu kỳ không có path đọc từ cờ valid của file vòng hở: telemetry chỉ được gọi khi generator trả ok, nên mã
  fallback 1–3 của generator này không bao giờ hiện trong telemetry (yêu cầu contract ở báo cáo).
- S1b a: MLP ngoài miền 75 % chu kỳ (a_y lớn hơn mọi cửa sổ train), không có path.

| Ngày | Lệnh (quick.py, --jobs 1, `--against qp_jerk_admm-708cc600`) | Thay đổi | Nhận xét |
|---|---|---|---|
| 2026-11-24 | mặc định, `--telemetry` | qp.c cũ, model cũ | Bỏ (`build/lab/mlp/old_qpc/bench`) |
| 2026-11-24 | mặc định | qp.c cũ, DAgger cũ | Bỏ |
| 2026-11-24 | mặc định | model vòng 1 | Bảng trên (`build/lab/mlp/bench_r1`) |
| 2026-11-24 | mặc định, `--telemetry` | model vòng 2 (DAgger) | Xấu hơn (`build/lab/mlp/bench_r2`) |
| 2026-11-24 | mặc định, `--telemetry` | trả lại model vòng 1 | Trùng bench_r1 từng số |

Tổng 8 lần quick bench cho generator này (giới hạn 20).

## Vấn đề còn mở

- Không có path ngoài miền là hệ quả của thiết kế đối chứng; LCC xử lý như T7 không có path.
- Cần nhiều vòng DAgger nếu muốn MLP tự lái được; vượt trần dữ liệu hiện tại.
