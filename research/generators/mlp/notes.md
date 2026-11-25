# Pipeline MLP của luồng C

Sổ tay phát triển, không phải kết quả. Kết quả chính thức chỉ nằm ở PP-TS-031 và `research/runs/`. Hash và cấu hình
từng tệp ở `data_card.md`.

## Thành phần

| Tệp | Việc |
|---|---|
| `scenarios.py` | Bộ sinh kịch bản riêng: 5 họ đường × 4 mức nhiễu, chia train/validation theo ô (họ, nhiễu) trước khi cắt cửa sổ; bộ ngoài miền riêng; loại mọi ca PP-T7 |
| `collect.py` | Chạy teacher (`qp_jerk_admm_teacher`) trong tiến trình con, lấy mẫu chu kỳ, ghi `build/lab/mlp/raw/` (float64); `--drive mlp` là vòng DAgger |
| `label.py` | Lọc nhãn theo ngưỡng, ghi `dataset.npz`, `rejected.npz`, `list_*.txt`; trần 10 000 cửa sổ |
| `model.py`, `train.py` | MLP 2 × 32 ReLU đối xứng gương, numpy, Adam; chuẩn hóa đóng băng theo train |
| `export.py` | Ghi `model/weights.h` và `tests/mlp_fixture.h` của generator; kiểm float32 kiểu C so với float64 |
| `c/` | Đặc trưng, suy luận, kẹp jerk, tích phân (C11, không heap, không global ngoài trọng số const); `mlp_l0.h` là L0 chung |
| `bench_summary.py` | Tóm tắt quick bench: lệch output so với nhãn tham chiếu, p99 trên phần chung của các nhãn |
| `tests/test_pipeline.py` | 6 pytest: gương, export, gradient, loại PP-T7, chia ô, tích phân |

## Quyết định (cần người duyệt)

1. Dữ liệu: 5 họ (thẳng lệch, một cua, cua chữ S, chuỗi độ cong, xe tải bên cạnh), R 180–3000 m, 40–100 km/h, VP-0/1/2,
   làn 2,75–5,0 m, ACC off/on/ignore_limits, 20 % vòng hở. Mức nhiễu N1–N3 tránh mức F01. 50 % kịch bản có 1–2 lần tài
   xế override 0,3–1,2 s: không có thì cửa sổ không nối path cũ quá hiếm, bị kiểm 5 σ coi là ngoài miền.
2. Ô validation: (chuỗi độ cong, N3), (chữ S, N2), (một cua, N1), (thẳng, N0), (xe tải, N2).
3. Lấy mẫu: lần gọi 1, 3, 6; mỗi 3 lần một chu kỳ không nối path cũ; còn lại 1/14 với pha ngẫu nhiên theo seed.
4. Ngưỡng nhãn (chốt trên validation, qp.c sau 28c4995): lũy thừa 10 nhỏ nhất trên max của validation: primal 1e-4,
   dual 1e-3, vi phạm hàng cứng 1e-6.
5. Đặc trưng: 21 của pilot, cộng hành lang tại k = 9, 19, 29 và trần a_y (28). MLP lẻ theo gương do cấu trúc, lớp 1 tính
   một lần theo cơ sở chẵn/lẻ. Ngoài miền: bất kỳ đặc trưng nào lệch > 5 σ so với train.
6. Huấn luyện: chọn trong 8 cấu hình (bảng dưới) theo loss validation trong miền. Cấu hình chốt: batch 32, lr 1e-2 → 1e-4
   cosine, l2 1e-5, 20 epoch, trọng số bước sớm `1 + 4·exp(−k/5)`, chỉ học cửa sổ trong miền.
7. Một model chung cho cả hai generator: model vòng 1 (dữ liệu do QP lái). Vòng DAgger (vòng 2) cho `mlp_jerk_direct`
   giảm số check trượt của test_lcc_step nhưng làm quick bench xấu hơn, nên không dùng (bảng ở `../mlp_jerk_direct/notes.md`).

## Dữ liệu (qp.c sau 28c4995; b38c6e1 trùng từng bit)

- Lần chạy thử: 3 kịch bản, 16 s, ~5 s/kịch bản, RSS con 118 MB. Ước tính 140 kịch bản ~12 phút, đã khớp.
- Vòng 1: 140 kịch bản, 800 chu kỳ mỗi kịch bản, 111 233 lần gọi teacher, mọi nhãn hữu hạn; 689 s CPU (704 s thực, 1
  tiến trình), RSS con lớn nhất 122 MB. 9 879 cửa sổ: train 6 316 (90 kịch bản), validation 2 176 (30), ngoài miền
  1 387 (20; 678 tốc độ 110–130 km/h, 709 VP-3/5). Không mẫu nào bị loại. Đặc trưng C trùng numpy (lệch 0).
- Vòng 2 (DAgger, chỉ để thử): 40 kịch bản mới (30 train, 10 validation), lái bằng model vòng 1, 2 208 cửa sổ, 242 s
  CPU. Bỏ ngẫu nhiên 2 087 cửa sổ QP lái để giữ trần 10 000. 3 cửa sổ validation bị loại (MLP đưa xe vào trạng thái QP
  bất khả thi: vi phạm ≈ 1,9, primal ≈ 0,6), nằm ở `rejected.npz`.
- Bản ghi sinh bằng qp.c trước 28c4995 ở `build/lab/mlp/old_qpc/`, không dùng.

## Huấn luyện

Chọn cấu hình (dữ liệu old_qpc, validation trong miền; jerk RMSE m/s³, lệch d trên 0–1 s mm):

| Cấu hình | Loss val | Jerk RMSE val | d p50 / p99 val |
|---|---|---|---|
| đều, mọi cửa sổ, batch 64, lr 3e-3 (gốc) | 7,14 | 0,307 | 10,4 / 110 |
| đều, trong miền | 7,05 | 0,320 | 6,8 / 113 |
| bước sớm, trong miền | 6,26 | 0,280 | 6,0 / 98 |
| bước sớm, trong miền, l2 1e-3 | 6,27 | 0,285 | 6,4 / 98 |
| bước sớm, trong miền, batch 32, lr 1e-2 (chốt) | 4,07 | 0,190 | 4,5 / 80 |
| như trên, batch 16 | 5,32 | 0,230 | 4,2 / 87 |
| như trên, batch 32, lr 2e-2 | 4,83 | 0,220 | 5,9 / 77 |
| đều, trong miền, batch 32, lr 1e-2 | 4,47 | 0,187 | 6,5 / 93 |

Model vòng 1 trên dữ liệu hiện tại (epoch 8; loss = tổng bình phương 30 bước jerk chuẩn hóa):

| Phần | n | Trong miền | Loss (trong miền) | Jerk RMSE | d 0–1 s p50 / p99 (trong miền) | Jerk = 0 p50 / p99 |
|---|---|---|---|---|---|---|
| train | 6 316 | 96,4 % | 13,96 (1,30) | 0,318 (0,117) | 4,3 / 54 mm | 5,8 / 450 mm |
| validation | 2 176 | 97,9 % | 6,64 (4,32) | 0,275 (0,210) | 7,5 / 77 mm | 7,4 / 485 mm |
| ngoài miền: tốc độ | 678 | 91,4 % | 13,15 (7,63) | 0,295 (0,217) | 9,5 / 123 mm | 12,8 / 152 mm |
| ngoài miền: VP-3/5 | 709 | 93,5 % | 8,08 (2,88) | 0,352 (0,200) | 5,4 / 89 mm | 6,0 / 189 mm |

So sánh: nghiệm 150 vòng có warm start của chu kỳ trước lệch nhãn p50 0 mm, p99 0,7–3 mm. MLP tốt hơn jerk = 0 rất
nhiều ở p99 nhưng kém xa nghiệm của chu kỳ trước: đây là lý do warm start MLP không thắng (notes của generator).

## Chi phí suy luận (C, -O2, máy dev)

3 962 phép nhân cộng (`MLP_OPS`); đặc trưng + suy luận 1,1 µs; một vòng ADMM 2,9 µs; QP 10 vòng 94 µs (gồm phân rã).
Suy luận ≈ 0,4 vòng ADMM. Tối ưu đã làm: lớp 1 dùng chung cho x và Mx (cơ sở chẵn/lẻ), float32, bias lớp ra bỏ do đối xứng.

## Dùng lại cho qp_jerk_admm_mlp_weights (chưa làm)

- `dataset.npz` giữ bài toán QP đầy đủ từng cửa sổ (float64, `problem`, bố cục `TR_PROBLEM`) cùng đặc trưng, cờ, nhãn:
  giải lại offline với lưới trọng số mà không cần chạy lại mô phỏng.
- Dùng lại nguyên: `scenarios.py` (manifest, chia ô, loại PP-T7), `collect.py`, teacher, `label.py` (ngưỡng), đặc trưng
  C/Python, chuẩn hóa, `model.py` (đổi đầu ra 30 jerk thành số trọng số), `export.py`, `c/mlp_infer.c` (đổi MLP_OUTPUTS).
- Cần thêm: công cụ giải lại offline (gọi `pp_generate_qp_seeded` qua một .so nhỏ hoặc numpy ADMM trùng qp.c) để sinh
  nhãn "trọng số tốt nhất" theo tiêu chí của study; tiêu chí đó chưa có.
