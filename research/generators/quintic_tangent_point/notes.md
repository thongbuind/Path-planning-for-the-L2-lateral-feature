# quintic_tangent_point

Sổ tay phát triển, không phải kết quả. Kết quả chính thức chỉ nằm ở PP-TS-031 và `research/runs/`.

## Ý tưởng

PP-TS-024 V1 (Land và Lee 1994): path `quintic_duration` cộng một hiệu chỉnh ngang về phía trong cua, dạng hai nửa smoothstep bậc 7 (`common/driver_shape`), đỉnh tại thời điểm xe tới tiếp điểm của tia nhìn từ base_link với vạch trong, về 0 ở cuối tầm nhìn.

## Thay đổi so với generator gốc

| Phần | Cách làm | Lý do |
|---|---|---|
| Tiếp điểm | Trên các điểm path quintic đã có: f = side·(x sin θ − y cos θ + d) − h, tiếp điểm ở f đổi dấu từ âm sang dương, nội suy tuyến tính theo t | Không cần atan2 hay đi lại đường tham chiếu; khoảng 8 điểm |
| Phía trong | Dấu của a_y cần lớn nhất trên đoạn 0 tới cuối cửa sổ | Cua gần nhất mà tiếp điểm có thể nằm trên; không cần ngưỡng κ như pilot |
| Cửa sổ | [tâm − 0,25; tâm + 0,25] kẹp trong 1–2 s | PP-TS-024 mục 3 |
| Biên độ | Biên độ của **path** tại đỉnh so với d_target (phần cộng thêm = biên độ − path gốc tại đỉnh) | Bản pilot cộng biên độ vào path gốc: qua các chu kỳ lệch cộng dồn tới sát hành lang (lần 1: DLC −0,48 m) |
| Bắt đầu, giữ, thả | Bắt đầu khi tiếp điểm trong cửa sổ. Đang hiệu chỉnh thì tìm tiếp điểm từ 0 tới cuối cửa sổ; đỉnh = max(tiếp điểm, đầu cửa sổ). Tiếp điểm mất (gần hết cua) thì thả: quintic đưa về d_target | Trên cung dài, tiếp điểm luôn ở trước xe một khoảng cố định; không giữ thì hiệu chỉnh tắt giữa cua và xe trở ra trong cua (lần 2: 068 S1g +0,23) |
| Tăng biên độ | Biên độ tăng theo `ref_rate` (0,1 m/s, PP-SWR-120), thời gian chu kỳ lấy từ `old->shift_s` | Path không đổi đột ngột ở chu kỳ đầu; giảm 069 (lần 3 → 5) |
| Giới hạn | Hành lang 0,5·(W − w) − `dlc_offset_min` như offset; phần cộng thêm ≤ jerk_target_hwa·T³/52,5 và ≤ ay_add_max_hwa·T²/7,51 (T = nửa ngắn hơn); path cuối ≤ aysmax và ≤ jerk_target_hwa, không đạt thì thử một nửa (pilot) | PP-TS-024 2.1; PP-SWR-051, 003, 001 |
| Fallback | Mã 1–13 trong `generator.yaml`; dùng path `quintic_duration` nguyên bit | PP-TS-024 2.4 cùng dữ liệu thiếu |
| Vật thể | Fallback khi không có ObjectList, hoặc vật thể (existence ≥ `exist_min`) chạm vạch trong hay ở làn bên phía trong, trong phạm vi path. Vật thể phía ngoài cua hay trong làn mình mà không chạm vạch trong thì không chặn | Hiệu chỉnh chỉ đi vào trong; ngưỡng làn bên lấy như `offset.c` |
| Sàn PP-SWR-006 | `PP_T7_SUPPORT_FLOOR` 1; không hiệu chỉnh khi a_y cần ≥ aysmax − `qtp_ay_need_margin` | Cua sát giới hạn giữ nguyên quintic |
| Chi phí | Thêm 1 (ít khi 2) lần dựng path; p99 trong nhiễu đo | — |

## Lần dò bằng quick bench

Mốc: `quintic_duration` (quick), `quintic_duration-ad15c8ac` (= mặc định, `--runs tuning`). Số trong ngoặc là hiệu so với mốc. Lần 1–13 dựng bằng cache có sẵn `PP_T7_LAB_DIR` (lỗi CMake của contract, đã sửa); lần 14 trở đi build sạch, số liệu trùng lần 7.

| Lần | Lệnh | Thay đổi | Nhận xét |
|---|---|---|---|
| 1 | quick `--telemetry` | Bản pilot (biên độ cộng vào path gốc) | S1d: 070 −0,48, 068 +0,05, 069 +0,12; lệch cộng dồn |
| 2 | quick `--telemetry` | Biên độ của path tại đỉnh | 070 −0,25; S1g 068 +0,23: tắt giữa cua |
| 3 | quick `--telemetry` | Giữ khi tiếp điểm còn trước cửa sổ | S1g 068 +0,015, 069 +0,17 |
| 4 | quick `--telemetry --set qtp_amplitude_m=0.10` | Như lần 3 | 069 vẫn +0,06/+0,12: jerk không tỉ lệ biên độ, do path đổi đột ngột |
| 5 | quick `--telemetry` | Biên độ đổi theo ref_rate cả lúc tăng và lúc thả | S1g 068 −0,036, 069 +0,07; S1d 068 +0,09, 069 +0,08 |
| 6 | quick `--telemetry` | Thả ngay về quintic (chỉ tăng theo ref_rate) | S1d 069 +0,04; còn lại như lần 5. **Giữ** |
| 7 | quick | Đo thời gian, không telemetry | Như lần 6; p99 0,47–1,5 ms, mốc 0,70–0,91 ms (nhiễu) |
| 8–9 | `quintic_duration --set T_hwa=3.0 --runs tuning` | Mốc tuning, nhãn riêng để không ghi đè `quintic_duration` | — |
| 10–11 | `--telemetry --runs tuning --against quintic_duration-ad15c8ac` | Mặc định | Không trượt. S1a, S2b, S3a, S22a, S1b a trùng mốc (fallback 100 %). S1g_F01a xấu nhất: 068 +0,28/+0,17, 069 +0,17/+0,12 |
| 12–13 | như 10–11 | Thử: lúc giữ, đỉnh cố định ở đầu cửa sổ | Xấu hơn mọi dòng (S1g_F01a 069 +0,23/+0,33). **Bỏ** |
| 14 | quick | Build sạch sau khi contract sửa CMake | Trùng lần 7 |
| 15–20 | quick `--telemetry --set` 6 bộ lưới | Lưới (bảng dưới) | — |

Lưới (quick, vòng kín seed 1, hiệu so với mốc; fb = tỉ lệ fallback):

| Tâm; biên độ | S1d 070 / 068 / 069 | S1g 070 / 068 / 069 | fb S1d / S1g |
|---|---|---|---|
| 1,0; 0,10 và 0,30 | 0 / 0 / 0 | 0 / 0 / 0 | 1,00 / 1,00 |
| 1,5; 0,10 | −0,125 / +0,051 / +0,015 | −0,128 / +0,007 / +0,074 | 0,53 / 0,39 |
| 1,5; 0,20 (mặc định) | −0,251 / +0,090 / +0,043 | −0,246 / −0,036 / +0,073 | 0,51 / 0,39 |
| 1,5; 0,30 | −0,376 / +0,090 / +0,075 | −0,371 / −0,009 / +0,073 | 0,50 / 0,39 |
| 2,0; 0,10 | −0,108 / −0,034 / +0,020 | −0,002 / +0,048 / +0,066 | 0,42 / 0,92 |
| 2,0; 0,30 | −0,164 / −0,032 / +0,025 | −0,002 / +0,044 / +0,065 | 0,42 / 0,93 |

## Vấn đề còn mở

- Trên cung dài (mọi dòng tuning), tiếp điểm đứng yên trước xe: hiệu chỉnh thành offset cố định vào trong, DLC phía trong giảm gần đúng biên độ, a_y không giảm. Lợi chỉ có thể ở cua ngắn (S1f, S14e, chỉ có ở test); tuning không đo được.
- Tâm 1,0 s không bao giờ bắt đầu trên S1d, S1g: tiếp điểm giảm dần tới giá trị của cung, √(2Rh)/v ≈ 1,67 s và 1,3 s, không vào được cửa sổ [1,0; 1,25].
- Camera nhiễu (F01): 068, 069, 004 xấu hơn rõ; chưa rõ cơ chế (thử cố định đỉnh làm xấu hơn). Cần log từng chu kỳ để xem bắt đầu/thả có bật tắt không.
- Tâm 2,0 trên S1g: fallback 92 % dù S1d chạy được; chưa xác định mã fallback trội.
- Hiệu chỉnh đi vào trong luôn làm giảm DLC phía trong; giả thuyết H1 với cận DLC 0,01 m khó đạt ở biên độ nào cũng vậy, trừ khi DLC nhỏ nhất của xe nằm ở phía ngoài.
