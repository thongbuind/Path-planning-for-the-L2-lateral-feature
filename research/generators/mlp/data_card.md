# Data card: MLP của luồng C (PP-TS-031)

Ngày: 2026-11-24. Hash là 16 ký tự đầu của sha256. Tệp dữ liệu nằm ở `build/lab/mlp/` (không vào git); sinh lại theo
mục Cách sinh lại.

## Model đang dùng

| Generator | weights.h | Model | Dataset |
|---|---|---|---|
| `qp_jerk_admm_mlp_warmstart` | `343271974bbcffa6` | `round1/model.npz` `599f8e74cc251718` | `round1/dataset.npz` `5f6a9c6cf7034e03` |
| `mlp_jerk_direct` | `343271974bbcffa6` (trùng) | như trên | như trên |

Vòng 2 (DAgger, không dùng): `model.npz` `4cffd61d73665bce`, `dataset.npz` `08838e6cd724d600`, `rejected.npz`
`30fe9093dc671d28`.

## Nguồn dữ liệu

| Mục | Giá trị |
|---|---|
| Bộ sinh kịch bản | `scenarios.py`; manifest `ec99671d75a1a4d2` (140 kịch bản), DAgger `efb8fe8fe0db23ed` (40) |
| Seed | Master 100; kịch bản trong miền 100–219; ngoài miền 5000–5019; DAgger master 102, kịch bản 1100+; lấy mẫu theo seed kịch bản; bỏ cửa sổ cho trần: 100; huấn luyện 100 |
| Loại trừ PP-T7 | Mọi lượt tuning và test cùng mọi anchor của các họ PP-T7 dùng (88 chữ ký sau S24 a); 0 kịch bản bị loại. S24 b thêm sau, là tuning, được phép dùng |
| Miền | 40–100 km/h, VP-0/1/2, làn 2,75–5,0 m, R 180–3000 m |
| Ngoài miền (báo riêng) | 110–130 km/h hoặc VP-3/5 |
| Chia | Theo ô (họ đường, nhiễu) trước khi cắt cửa sổ; ô validation ở `../mlp/notes.md` |

## Teacher và nhãn

| Mục | Giá trị |
|---|---|
| Teacher | `qp_jerk_admm_teacher`: `.c` `97a19f133ec3dda6`, `.h` `23b7e5d386070afe`; nhãn = ADMM 1000 vòng, chuỗi warm start riêng |
| qp.c | Bản ghi sinh với qp.c ở 28c4995; b38c6e1 trùng từng bit (coordinator); qp.c hiện tại `8dadcb6bc769ed57` |
| Calibration | `build/lab/mlp/teacher/calibration.yaml` `981c00a3e31f52e5` (bản sao `planner/calibration/calibration.yaml` `2432aea753bc5917`, giá trị mặc định) |
| Ngưỡng nhận nhãn | primal ≤ 1e-4, dual ≤ 1e-3, vi phạm hàng cứng (a_y, jerk) ≤ 1e-6; chốt trên validation vòng 1 (max 3,3e-5 / 1,4e-4 / 2,1e-7), lấy lũy thừa 10 nhỏ nhất ở trên |
| Bị loại | Vòng 1: 0. Vòng 2: 3 (validation; 2 bất khả thi, 1 không hội tụ) ở `rejected.npz` |

## Danh sách cửa sổ (scenario:call)

| Danh sách | Số cửa sổ | Hash |
|---|---|---|
| Vòng 1 train | 6 316 | `b9507288d5257204` |
| Vòng 1 validation | 2 176 | `1c5d617763f4d79d` |
| Ngoài miền (cả hai vòng) | 1 387 | `6e0d7c6402220c00` |
| Vòng 2 train | 6 465 | `7ae3fa64478cbe85` |
| Vòng 2 validation | 2 145 | `e8632173ae06b9c8` |

## Đặc trưng và chuẩn hóa

- 28 đặc trưng (`c/mlp_features.c` `eedcddf06efa29ea`, Python `common.features`; lệch C so với Python 0).
- Chuẩn hóa theo train, đối xứng gương, sàn σ 1e-6·max(1, |mean|), inv_std = 0 với đặc trưng hằng (trần a_y).
  Hash chuẩn hóa (sha256 của JSON): vòng 1 `d1a883032a812bc1`, vòng 2 `2b3f9c231280ed73`.
- Ngoài miền khi |x − mean| > 5 σ ở bất kỳ đặc trưng nào.

## Huấn luyện

Cấu hình (hash `ce346e782ef01dac`): 2 × 32 ReLU, đối xứng gương, 20 epoch, batch 32, Adam (0,9; 0,999; 1e-8), lr 1e-2 →
1e-4 cosine, l2 1e-5, seed 100, MSE trên jerk chuẩn hóa với trọng số bước `1 + 4·exp(−k/5)` (tổng 30), chỉ cửa sổ trong
miền, chọn epoch có loss validation trong miền nhỏ nhất (vòng 1: epoch 8).

## Mã C sinh ra

| Tệp | Hash |
|---|---|
| `c/mlp_infer.c` | `13c95c55b5bd0523` |
| `qp_jerk_admm_mlp_warmstart/tests/mlp_fixture.h`, `mlp_jerk_direct/tests/mlp_fixture.h` (trùng) | `ea9e78c4e3675d08` |
| `model/weights.h` của cả hai generator (trùng) | `343271974bbcffa6` |

Export kiểm float32 kiểu C so với float64 trên validation: lệch lớn nhất 1,2e-6 m/s³.

## Cách sinh lại

```bash
cd research/generators/mlp
python3 scenarios.py --per-cell 6 --ood 20
python3 collect.py                      # ~12 phút, 1 tiến trình, slot 'mlp data'
python3 label.py && python3 train.py
mkdir -p ../../../build/lab/mlp/round1 && cp ../../../build/lab/mlp/{dataset.npz,model.npz,list_*.txt} ../../../build/lab/mlp/round1/
python3 export.py --model ../../../build/lab/mlp/round1/model.npz --dataset ../../../build/lab/mlp/round1/dataset.npz
# Vòng 2 (không dùng): scenarios.py --dagger --per-cell 2; collect.py --drive mlp --stride 20;
# label.py --dagger ../../../build/lab/mlp/manifest_dagger.json; train.py
```
