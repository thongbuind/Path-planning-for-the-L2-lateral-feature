# qp_jerk_admm_mlp_weights

Sổ tay phát triển, không phải kết quả. Kết quả chính thức chỉ nằm ở PP-TS-031 và `research/runs/`.

## Ý tưởng

- MLP chọn `qp_w_dev`, `qp_w_jerk`, `qp_a_comfort` theo tình huống, kẹp trong dải calibration (PP-TS-025 V3).
- Sau đó `qp_jerk_admm` giải như thường: đúng `qp_iters` vòng (150), warm start như bản gốc.
- Đổi trọng số giữa hai chu kỳ có giới hạn tốc độ, để path không nhảy (PP-SWR-100; duyệt 2026-11-23).
- Giả thuyết H5 (plan.yaml): ít nhất một ô nhóm 2–3 tốt hơn có ý nghĩa so với `qp_jerk_admm` mặc định, không ô nào xấu
  hơn có ý nghĩa, trên toàn bộ test.

## Nhãn: lưới offline (cách i, PP-TS-031 mục 2)

Chốt ngày 2026-11-24, trước khi tạo nhãn. Không đổi sau khi đã thấy nhãn.

### Dữ liệu và bộ giải

| Mục | Giá trị | Nguồn |
|---|---|---|
| Cửa sổ | `build/lab/mlp/round1/dataset.npz` của luồng C (9 879: train 6 316, validation 2 176, ngoài miền 1 387) | `../mlp/data_card.md` |
| Bài toán | Khối `problem` (float64); dời path cũ theo `TR_REF_DTARGET` của bản ghi thô khi chuỗi nhãn đang warm | Như teacher |
| Bộ giải | Đúng `qp.c` của planner, biên dịch cùng `tools/resolve.c`; calibration mặc định trừ ba trọng số | `tools/resolve.py` |
| Khởi động | Lạnh, 1 000 vòng | Như `qp_jerk_admm_it1000_ref`; lạnh để nhãn không phụ thuộc lịch sử warm start |
| Nhận nghiệm | primal ≤ 1e-4, dual ≤ 1e-3, vi phạm hàng cứng ≤ 1e-6 | Ngưỡng nhãn của luồng C (`../mlp/label.py`) |
| Ô không đạt | Bỏ ô đó (S = +∞). Ô mặc định không đạt thì cửa sổ không có nhãn | nhóm tự thống nhất |

### Lưới trọng số (5 × 5 × 4 = 100 ô)

| Trọng số | Dải | Mức | Nguồn |
|---|---|---|---|
| `qp_w_dev` | 0,15–0,60 | 0,15 / 0,212 / 0,30 / 0,424 / 0,60 (bước ×√2) | Dải lưới `qp_jerk_admm` của PP-TS-031 (plan.yaml, ×0,5–×2 quanh 0,30) |
| `qp_w_jerk` | 0,5–2,0 | 0,5 / 0,707 / 1,0 / 1,414 / 2,0 (bước ×√2) | nhóm tự thống nhất: cùng quy tắc ×0,5–×2 quanh mặc định 1,0 |
| `qp_a_comfort` | 1,0–2,5 m/s² | 1,0 / 1,5 / 2,0 / 2,5 | Trần 2,5 của `calibration.yaml` (PP-SWR-001); sàn: nhóm tự thống nhất, ×0,5 quanh 2,0 |

- Mặc định (0,30; 1,0; 2,0) là một ô của lưới.
- Dải này cũng là dải kẹp đầu ra MLP trong C (calibration của generator).
- Bước nhân cho hai trọng số vì tác dụng của trọng số QP theo tỉ lệ, không theo hiệu.

### Hàm mục tiêu thay thế

Tính trên path vòng hở của nghiệm từng ô. Mỗi thành phần chia cho dung sai thực tế của dashboard, nên một đơn vị là
mức nhỏ nhất dashboard coi là "khác có ý nghĩa".

S = J / 0,10 + E / 0,005 − D / 0,01 (nhỏ hơn là tốt hơn)

| Thành phần | Định nghĩa | Chia cho | Nguồn |
|---|---|---|---|
| J: jerk path RMS | RMS của j_k + v_k³κ'_k trên 10 bước đầu (0–1 s) | 0,10 m/s³ | PP-SWR-004 (RMS path 0–1 s, eval); dung sai PP-TS-031 mục 3.3 |
| E: lệch đích | RMS của d(t_k) − d_target, t_k = 0,1 … 1,0 s | 0,005 m | PP-SWR-050 (0–1 s); dung sai 2.3 |
| D: biên DLC | min trên t_1 … t_30 của khoảng từ thân xe tới vạch hai bên: d_max + 0,3 − d và d − d_min + 0,3 | 0,01 m | PP-SWR-070, 051; dung sai 2.3; 0,3 m là `qp_corridor_margin` mặc định |

- Nhãn: ô có S nhỏ nhất. Nếu S của ô mặc định chỉ lớn hơn ô đó dưới 1 đơn vị, nhãn là ô mặc định (vùng chết).
  Lý do: khác dưới một dung sai thì dashboard không phân biệt; tránh nhãn nhảy ngẫu nhiên khi các ô gần bằng nhau.
- J và E đo 0–1 s, đúng cửa sổ của chỉ số dashboard. D đo cả path 0–3 s: hành lang của QP và PP-SWR-051 áp cho cả
  path, và DLC của xe (070) là min của cả lần chạy. Đây là quyết định nhóm tự thống nhất, chờ người duyệt.
- Không thêm a_y hay thời gian về giữa: plan chỉ duyệt ba thành phần.
- Hạn chế: E so với d_target (đích của planner), không với tâm làn thật; D dùng hành lang ước lượng của planner. Đó là
  điều duy nhất có được ở vòng hở offline.

### Lần chạy nhãn (2026-11-24)

- Mẫu thời gian trước (40 cửa sổ train): 0,36 s CPU mỗi cửa sổ, 3,5 ms mỗi lần giải, RSS 65 MB. Ở ô mặc định, nghiệm
  lạnh 1 000 vòng lệch nhãn teacher p50 6e-10 m, max 1,2 mm; 1 000 so với 2 000 vòng: p50 0, max 1,2 mm.
- Cả bộ (`python3 grid_labels.py`, 1 tiến trình, 1 slot, người dùng duyệt): 9 879 cửa sổ × 100 ô, 2 364 s CPU, RSS
  lớn nhất 102 MB. 99,9 % ô đạt ngưỡng nghiệm. 5 cửa sổ train không có nhãn (ô mặc định không đạt).

Phân bố nhãn (cửa sổ có nhãn):

| Phần | n | Nhãn = mặc định | Khác mặc định |
|---|---|---|---|
| train | 6 311 | 90,9 % | 9,1 % |
| validation | 2 176 | 77,8 % | 22,2 % |
| ngoài miền | 1 387 | 85,1 % | 14,9 % |
| tất cả | 9 874 | 87,2 % | 12,8 % |

Tần suất từng mức (tất cả cửa sổ có nhãn):

| Trọng số | Mức: tỉ lệ |
|---|---|
| `qp_w_dev` | 0,15: 9,0 % · 0,212: 0 % · 0,30: 87,2 % · 0,424: 0 % · 0,60: 3,8 % |
| `qp_w_jerk` | 0,5: 1,6 % · 0,707: 0,1 % · 1,0: 87,3 % · 1,414: 0 % · 2,0: 11,0 % |
| `qp_a_comfort` | 1,0: 10,1 % · 1,5: 1,7 % · 2,0: 87,2 % · 2,5: 0,9 % |

Bộ khác mặc định hay gặp nhất: (0,15; 2,0; 1,0) 7,7 %; (0,60; 2,0; 1,0) 1,7 %; (0,15; 2,0; 1,5) 1,3 %; còn lại < 1 %.

Thành phần trội của S (cửa sổ có nhãn khác mặc định, thành phần có |hiệu so với mặc định| lớn nhất, đơn vị dung sai):

| Thành phần | Trội ở | Hiệu trung bình (dương là xấu hơn) | Trung vị theo đơn vị vật lý |
|---|---|---|---|
| J | 79,6 % | −3,42 | −0,43 m/s³ |
| E | 3,0 % | +0,58 | +6,0 mm |
| D | 17,4 % | −0,71 | 0 mm (p10 −0,2 mm; xấu hơn > 1 cm ở 0,2 %) |

- Lợi của nhãn so với mặc định (cửa sổ khác mặc định): p50 2,8, p90 5,7, max 29,8 đơn vị.
- Độ chênh S giữa các ô nhỏ: trung vị biên độ trên lưới J 0,04, E 0,04, D 0,03 đơn vị. Phần lớn cửa sổ nằm trong vùng
  chết.
- Nhận xét: nhãn gần như chỉ ở góc lưới (nhãn kiểu bật–tắt). Hướng chính là path êm hơn: `qp_w_dev` thấp, `qp_w_jerk`
  cao, `qp_a_comfort` thấp; đổi lại lệch đích 0–1 s tăng khoảng 6 mm. D ít khi quyết định, khác dự đoán ở bản trước.
  Không đổi hàm mục tiêu sau khi thấy các số này.

## Thay đổi so với generator gốc

- Mỗi chu kỳ: dựng bài toán như `qp_jerk_admm`, tính 28 đặc trưng của luồng C, MLP ra u = (ln `qp_w_dev`, ln
  `qp_w_jerk`, `qp_a_comfort`), kẹp vào dải `mlpw_*_min/max`.
- Ngoài miền (lệch > 5 σ) hoặc đặc trưng không hữu hạn: đích là trọng số mặc định của calibration chung.
- Giới hạn tốc độ: mỗi chu kỳ ln trọng số đổi tối đa `mlpw_rate_log` 0,035, `qp_a_comfort` tối đa `mlpw_rate_ac`
  0,0375 m/s². Sau reset, bắt đầu từ trọng số mặc định.
- Rồi `pp_generate_qp` với bản calibration chỉ khác ba trọng số: cùng warm start, đúng `qp_iters` vòng.
- MLP bất biến theo gương (đầu ra chẵn), khác bản lẻ của luồng C; đặc trưng `mlp_features.c` dùng chung; suy luận riêng
  `src/mlpw_infer.c`. Không biên dịch `mlp_infer.c`.
- `mlpw_regularisation` chọn một trong ba model đã xuất (log10 gần nhất), cho lưới PP-TS-031.

## Huấn luyện (`tools/train_weights.py`)

- Như luồng C: 2 × 32 ReLU, Adam, 20 epoch, batch 32, lr 1e-2 → 1e-4 cosine, seed 100, chuẩn hóa đóng băng theo train,
  chỉ học cửa sổ train trong miền có nhãn, chọn epoch theo loss validation trong miền. Đầu ra chuẩn hóa (u − tâm) / nửa
  dải; loss MSE. Khác: đầu ra chẵn theo gương, 3 đầu ra, có bias lớp ra.
- Lưới PP-TS-031: l2 = 1e-4 / 1e-3 / 1e-2 (`mlpw_regularisation`, tâm 1e-3). Ba model đều xuất vào `model/weights.h`.
- Chấm lại bằng chính S: giải QP 1 000 vòng lạnh với trọng số MLP (đã kẹp), so với ô mặc định và với nhãn. "Lợi" =
  S(mặc định) − S(MLP), đơn vị dung sai, trên cửa sổ có nhãn và trong miền.

| l2 | Epoch | Loss val (hằng: 0,683) | Val: lợi TB (nhãn: 0,592) | Val: lợi ≥ 1 / thiệt ≥ 1 | Val: thiệt lớn nhất | Ngoài miền: lợi TB (nhãn: 0,316) | Ngoài miền: thiệt ≥ 1 / lớn nhất |
|---|---|---|---|---|---|---|---|
| 1e-4 | 6 | 0,096 | 0,492 | 20,0 % / 0,47 % | 7,6 | −0,183 | 3,6 % / 35,3 |
| 1e-3 | 4 | 0,086 | 0,473 | 19,5 % / 0,19 % | 1,9 | 0,062 | 1,3 % / 5,6 |
| 1e-2 | 11 | 0,092 | 0,464 | 19,5 % / 0 % | 0,66 | 0,082 | 0,8 % / 1,8 |

- Validation: 2 130 cửa sổ trong miền (97,9 %); ngoài miền 1 283 (92,5 % lọt qua bộ kiểm 5 σ). Không lần giải nào hỏng.
- MLP lấy được 78–83 % lợi của nhãn trên validation. Trung vị trọng số gần mặc định (0,30; 1,0; 2,0); MLP làm mượt nhãn
  góc lưới thành giá trị giữa.
- Điều chuẩn mạnh hơn giảm ca thiệt lớn, nhất là ngoài miền (tốc độ 110–130 km/h, VP-3/5).
- Xuất C: float32 kiểu C lệch numpy ≤ 3,4e-7 trên u.

## Chi phí

- Suy luận: `MLPW_OPS` = 3 071 phép nhân cộng mỗi chu kỳ (một lần suy luận). Không đổi số vòng ADMM (150).
- Thư viện `libpp_lcc.dylib` của bản quick bench: 123 088 byte, so với 88 384 byte của `qp_jerk_admm` (ba model,
  mỗi model 2 167 float ≈ 8,7 KB).
- State thêm 3 double, một cờ và hai uint32 so với `qp_jerk_admm`.

## Kiểm L0 (ctest, telemetry OFF và ON, 19/19, 0 cảnh báo)

Đặc trưng C trùng Python (1e-12); suy luận ba model trùng numpy (1e-4); gương đúng từng bit; ngoài miền và không hữu
hạn bị từ chối (ops 0, u không ghi); `mlpw_regularisation` chọn model có log10 gần nhất; đích luôn trong dải và kẹp
đúng biên khi dải hẹp; ngoài miền thì đích mặc định; giới hạn tốc độ đúng từng chu kỳ, bắt đầu từ mặc định sau reset,
calibration ra chỉ khác ba trọng số; `pp_t7_generate` trùng từng bit `pp_generate_qp` với trọng số đã chọn qua 5 chu
kỳ warm start, đúng `qp_iters` vòng; ngoài miền trùng từng bit `qp_jerk_admm` qua 3 chu kỳ; test contract chung.

## Lần dò bằng quick bench

Nháp L1, `--jobs 1`, so với `qp_jerk_admm` mặc định (chạy lại cùng ngày để có S24 b). Hiệu trong ngoặc: dương ở 070 là
DLC lớn hơn (tốt hơn); dương ở 050, 068, 069 là xấu hơn. Không lượt nào trượt requirement.

| Lượt | Chỉ số | l2 1e-4 | l2 1e-3 (mặc định) | l2 1e-2 |
|---|---|---|---|---|
| S1g vòng kín | 070 DLC [m] | +0,127 | +0,055 | −0,073 |
| S1g vòng kín | 050 [m] | −0,144 | −0,054 | +0,074 |
| S24 a vòng kín | 070 / 069 | +0,043 / −0,102 | +0,009 / −0,018 | +0,002 / −0,002 |
| S24 b vòng kín | 070 / 069 | +0,003 / −0,014 | +0,002 / −0,017 | +0,005 / −0,026 |
| S1g F01a vòng hở | 050 seed 1 / 2 [m] | −0,058 / −0,055 | +0,002 / +0,003 | +0,017 / −0,003 |
| S1g F01a vòng hở | lệch output max [m] | 0,085 | 0,019 | 0,024 |
| S1d, S1b a | mọi chỉ số | ≤ 0,001 | ≤ 0,001 | ≤ 0,001 |

- Telemetry (mặc định): tỉ lệ fallback S1d 0, S1g 5,4 %, S24 a 15 %, S24 b 23,6 %, S1b a 75 % (ngoài miền a_y như bản
  warm start). work luôn 150.
- p99 LCC 0,81–1,41 ms ở mọi bản, trong nhiễu của `qp_jerk_admm` (0,91 ms trên cùng máy).
- S1g nhạy: cùng một lượt đổi dấu theo mức điều chuẩn. Một lượt vòng kín không đủ để kết luận; số chính thức chỉ ở L2.
- Không dò thêm: không có tham số nào được chỉnh theo kết quả quick bench.

| Ngày | Lệnh (quick.py, --jobs 1) | Thay đổi | Nhận xét |
|---|---|---|---|
| 2026-11-24 | `qp_jerk_admm_mlp_weights --against qp_jerk_admm` | model l2 1e-3 | Cột giữa |
| 2026-11-24 | `qp_jerk_admm` | mốc mới có S24 b | S24 b: 070 0,305, 069 2,917 |
| 2026-11-24 | `--telemetry --against qp_jerk_admm` | chẩn đoán | Tỉ lệ fallback như trên; số trùng lần 1 |
| 2026-11-24 | `--set mlpw_regularisation=1.0e-4`, `=1.0e-2` | hai mức còn lại | Hai cột ngoài |

Tổng 5 lần quick bench (giới hạn 20).

## Data card

Hash là 16 ký tự đầu của sha256. Tệp dữ liệu ở `build/lab/mlp_weights/` (không vào git).

| Mục | Giá trị |
|---|---|
| Dataset | `build/lab/mlp/round1/dataset.npz` `5f6a9c6cf7034e03` (luồng C vòng 1; danh sách, seed, loại PP-T7 ở `../mlp/data_card.md`) |
| Không dùng | seed 3–4, dòng test PP-T7: dataset là kịch bản sinh riêng của luồng C, không có dòng PP-T7 |
| Bộ giải nhãn | `tools/resolve.c` `5053aa67fa220041` + `planner/src/generators/qp.c` `8dadcb6bc769ed57`; calibration mặc định của `calibration.yaml` |
| Lưới, mục tiêu | `tools/resolve.py` `581299b5e6bc462c` (mục Nhãn ở trên) |
| Nhãn | `labels.npz` `733e98ab94ea8d13`: 9 874 / 9 879 có nhãn |
| Đặc trưng | `../mlp/c/mlp_features.c` `eedcddf06efa29ea` (28, như luồng C); chuẩn hóa theo train, ngoài miền > 5 σ |
| Huấn luyện | `tools/train_weights.py`, cấu hình hash `ca8d344743aa593a` (không tính l2), seed 100 |
| Model | l2 1e-4 `model_r1e-4.npz` `afa69565ffb6175c` (epoch 6); 1e-3 `model_r1e-3.npz` `82a709fa52bbb1d8` (epoch 4); 1e-2 `model_r1e-2.npz` `a42fa257b1a79cdf` (epoch 11) |
| Mã C sinh ra | `model/weights.h` `e146baef49a280e7`, `tests/mlpw_fixture.h` `21369637f8cfaf96` (`tools/export_weights.py`); suy luận `src/mlpw_infer.c` `7f6f195b7b0f10dc` |

Sinh lại (chạy nặng là bước 1, ~40 phút CPU, 1 slot):

```bash
cd research/generators/qp_jerk_admm_mlp_weights/tools
python3 grid_labels.py          # nhãn, ghi build/lab/mlp_weights/labels.npz
python3 train_weights.py        # ba mức l2, ~25 s
python3 export_weights.py       # model/weights.h, tests/mlpw_fixture.h
```

## Vấn đề còn mở

- Nhãn chủ yếu ở góc lưới và 87 % là mặc định. Hàm mục tiêu trả lợi cho path êm hơn (J trội ở 80 % nhãn khác mặc
  định), đổi lại lệch đích 0–1 s tăng ~6 mm. Ô 050 trên dashboard có thể xấu hơn ở vài lượt; H5 cần cả nhóm 2–3 không
  xấu hơn.
- D (biên DLC) gần như không quyết định trên dữ liệu sinh riêng; chưa biết trên S1f, S14 e (chỉ ở test).
- S1b a 75 % ngoài miền: ở đó generator chỉ là `qp_jerk_admm`.
- Giới hạn tốc độ là cơ chế duy nhất chống nhảy path khi đổi trọng số; chưa đo riêng PP-SWR-100 trên cả tuning.
- Hai trường hợp mép: hành lang bị cắt về 0 (làn quá hẹp) thì D không còn là DLC; E so với d_target chứ không với
  tâm làn thật.
