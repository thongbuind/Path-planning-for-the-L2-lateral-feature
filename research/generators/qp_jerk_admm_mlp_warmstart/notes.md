# qp_jerk_admm_mlp_warmstart

Sổ tay phát triển, không phải kết quả. Kết quả chính thức chỉ nằm ở PP-TS-031 và `research/runs/`.

## Ý tưởng

Cùng bài toán QP, trọng số mặc định và đúng `qp_iters` vòng như `qp_jerk_admm`. Chỉ khác điểm xuất phát: khối jerk của
x là chuỗi jerk do MLP dự đoán (kẹp vào hàng jerk cứng), qua `pp_generate_qp_seeded`. Model, đặc trưng, dữ liệu:
`../mlp/notes.md`, `../mlp/data_card.md` (model vòng 1).

## Thay đổi so với generator gốc

- Đầu vào trong miền: jerk MLP thay khối jerk; biến nới, y, rho giữ như warm start của `qp_jerk_admm`.
- Ngoài miền (mã 1, 2) hoặc `qmw_seed_mode = 1` khi nghiệm trước dịch được (mã 3): warm start dịch thời gian của luồng A
  (`../qp_jerk_admm_shift_warmstart/src/shift.c`, dùng nguyên, chỉ đọc): dịch ba khối x, không dịch y (luồng A đo được
  dịch y xấu hơn). Không dịch được thì như `qp_jerk_admm`.
- Calibration riêng: `qmw_slack_shift` (dịch hai khối biến nới khi dùng MLP; mặc định 0), `qmw_seed_mode` (mặc định 0
  = luôn dùng MLP, đúng thiết kế PP-TS-031; 1 = chỉ dùng MLP khi không có nghiệm trước dịch được).
- work = số vòng ADMM (luôn đúng qp_iters); infer_ops = 3 962 khi suy luận, 0 khi không.

## Kiểm L0 (ctest, telemetry OFF và ON, 19/19, không cảnh báo)

Đặc trưng C trùng Python; suy luận trùng numpy (1e-4); gương đúng tuyệt đối; ngoài miền bị từ chối (ops 0, jerk không
ghi); MLP seed trùng từng bit `pp_generate_qp_seeded` với đúng 10/25/50/75/150 vòng; ngoài miền lần đầu trùng
`qp_jerk_admm`; ngoài miền có nghiệm trước trùng bản dịch của luồng A, y không đổi; `qmw_seed_mode = 1` trùng bản dịch
của luồng A và không suy luận; seed MLP gần nghiệm 1000 vòng hơn khởi động lạnh ở 10 vòng; test contract chung.

## Lần dò bằng quick bench

Lệch output vòng hở 0–1 s so với `qp_jerk_admm-708cc600` (1000 vòng), max / p99 [mm], 6 lượt vòng hở. Mọi số sau
commit 28c4995 (rho thích nghi theo qp_iters). Bản dịch của luồng A lấy từ thư mục của luồng A (chạy sau 28c4995), K = 75
chưa có bản mới.

| K | qp_jerk_admm | Dịch (luồng A) | MLP, mode 0 | MLP, mode 0, dịch nới | MLP, mode 1 |
|---|---|---|---|---|---|
| 10 | 29,2 / 24,8 | 42,9 / 36,5 | 71,8 / 70,9 | 71,8 / 70,9 | 47,4 / 41,6 |
| 25 | 9,4 / 5,6 | 6,4 / 4,1 | 22,3 / 12,6 | — | 6,4 / 4,1 |
| 50 | 2,2 / 0,86 | 3,3 / 1,13 | 11,5 / 8,0 | — | 3,3 / 1,13 |
| 75 | 0,8 / 0,40 | — | 2,2 / 1,30 | — | — |

- Mặc định 150 vòng: 0,2 / 0,04 mm. Không lượt nào trượt requirement mới ở mọi K (bộ QUICK 10–11 lượt).
- Tỉ lệ không dùng MLP (telemetry, K = 10): S1d 0, S1g F01a 5 %, S1b a 75 % (ngoài miền a_y), S24 a 15 %, S24 b 23 %.
- Trung vị p99 thời gian LCC (bản không telemetry, chạy tuần tự, nhiễu tải lớn): MLP mode 0 ở K = 10/25/50/75 là 0,92 /
  1,72 / 1,79 / 1,32 ms; qp_jerk_admm cùng K 0,96 / 1,29 / 1,32 / 1,21 ms; mặc định 1,42 ms. Suy luận chỉ 1,1 µs nên
  chênh lệch này là nhiễu đo, không phải chi phí MLP.

Kết luận dò (nháp):

- H4a (cùng K, lệch nhỏ hơn cả `qp_jerk_admm_itk` và bản dịch ít nhất 5 mm): không đạt ở K nào; mode 0 xấu hơn ở mọi K.
- H4b (có K với lệch ≤ lệch của `qp_jerk_admm` và p99 ≤ 0,90 lần): không đạt.
- Lý do: ở trạng thái ổn định, nghiệm của chu kỳ trước lệch nhãn p99 0,7–3 mm, MLP lệch p50 7,5 mm, p99 77 mm
  (validation). Thay khối jerk bằng MLP làm hỏng một warm start vốn đã tốt, và x mới không khớp y cũ. Mode 1 chỉ dùng MLP
  ở chu kỳ lạnh, gần như bằng bản dịch, xấu hơn ở K = 10 trên S1g F01a.

| Ngày | Lệnh (quick.py, --jobs 1) | Thay đổi | Nhận xét |
|---|---|---|---|
| 2026-11-24 | `--set qp_iters={10,25,50,75}` ×4, `qp_iters=10/25 --set qmw_slack_shift=1`, `--telemetry qp_iters=10` | qp.c cũ (trước 28c4995) | Bỏ, qp.c đã đổi |
| 2026-11-24 | `--set qp_iters={10,25,50,75} --against qp_jerk_admm-708cc600` | qp.c mới, model vòng 1 | Bảng trên, cột mode 0 |
| 2026-11-24 | `--set qp_iters=10 --set qmw_slack_shift=1` | dịch biến nới | Trùng mode 0: biến nới gần như luôn 0 |
| 2026-11-24 | `--telemetry --set qp_iters=10`, `--telemetry --set qp_iters=50` | chẩn đoán | Tỉ lệ fallback như trên |
| 2026-11-24 | `--set qp_iters={10,25,50} --set qmw_seed_mode=1` | MLP chỉ ở chu kỳ lạnh | Cột mode 1 |

Tổng 17 lần quick bench cho generator này (giới hạn 20).

## Vấn đề còn mở

- Ở K ≤ 25, rho chỉ đổi theo lịch của qp.c; ADMM với y cũ và x mới cần cả hai đều mới (ví dụ dự đoán thêm y) mới có hy
  vọng. Ngoài phạm vi đã giao.
- Bản dịch K = 75 của luồng A chưa chạy lại sau 28c4995.
