# ASAM benchmark

Nguồn kịch bản là OpenSCENARIO XML 1.3.1; đường là OpenDRIVE 1.8.1. Các giá trị cũ được giữ nguyên trong các neo có mã cố định. `eval/` đọc file và tạo `sim.scenario.Scenario`; simulator và planner không đọc benchmark.

| File | Vai trò |
|---|---|
| `scenarios/<ID>.xosc` | Kịch bản logic, khai báo tham số và giá trị danh định |
| `scenarios/<ID>.anchors.xosc` | `ParameterValueDistribution` với các bộ giá trị neo đi cùng nhau; `variant` giữ mã a, b… |
| `scenarios/<ID>.ranges.xosc` | `ParameterValueDistribution`, dùng `DistributionRange` hoặc `DistributionSet` |
| `roads/<ID><variant>.xodr` | Hình học đường của từng neo; đường tham chiếu nằm ở tâm làn −2 |
| `faults/<ID>*.xosc` | Cùng cấu trúc; mỗi ca lỗi chạy trên đường và thời lượng của từng neo trong `fault_hosts` của bộ chạy (S1a, S1c) |
| `suites/{smoke,regression,full}.json` | Cách chọn, profile, seed chạy và seed lấy mẫu |
| `schema/` | XSD nguyên bản tải từ ASAM; URL và SHA-256 trong `sources.json` |

XSD dùng bản `local_schema` của gói OpenDRIVE, giữ nguyên các include tương đối. OpenDRIVE có cấu trúc XSD 1.1; kiểm tra bằng `xmlschema.XMLSchema11`, không sửa XSD để dùng bộ kiểm XSD 1.0. Bản quyền và điều khoản ASAM giữ trong file nguồn; xem [ASAM license](https://www.asam.net/license.html).

## Generate and run

Tại thư mục gốc repository, dùng Python có các gói trong `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
python3 -m eval.validate benchmark
python3 -m eval.generate smoke --plan-only
python3 -m eval.generate smoke
python3 -m eval.suite build/concrete/smoke/manifest.json --jobs 2
python3 -m eval.runner S1 a --seed 1
python3 -m eval.runner S1 a --fault F02 c
python3 -m eval.runner build/concrete/smoke/cases/<case-id>.xosc --seed 1
```

Thay `smoke` bằng `regression` hoặc `full` để sinh hai bộ còn lại. `--plan-only` chỉ đếm, không chạy simulator. `eval.generate` kiểm XSD và nạp thử từng cặp `.xosc`–`.xodr` trước khi viết manifest. Mỗi thư mục đầu ra phải mới; dùng `--out` để giữ riêng các lần sinh/chạy. Các cặp cụ thể chỉ tham chiếu file đường cùng thư mục, không cần cây benchmark gốc.

| Bộ | Cách chọn | Profile | Seed | Lượt chạy hiện tại |
|---|---|---|---|---|
| Smoke | Mọi neo đã hỗ trợ | VP-0 | 1 | 69 (0,4 giờ mô phỏng) |
| Regression | Neo và biên | VP-0…VP-5 | 1, 2 | 1.788 (12,8 giờ mô phỏng) |
| Full | Neo, biên, pairwise, Latin hypercube | VP-0…VP-5 | 1; riêng F01: 1…10 | 4.032 (33,4 giờ mô phỏng) |

Ca lỗi chạy trên hai đường chủ: S1a (cua nhẹ) và S1c (cua chạm aysmax), như M1. Mã ca lỗi ghi đường chủ, ví dụ `F06-e-S1c-VP-0-<hash>`.

S14 luôn có cả ACC đọc và bỏ qua LateralLimits. `eval.suite` chạy `--jobs` tiến trình (mặc định 1), mỗi tiến trình chỉ giữ log của một lượt trong RAM; kết quả ghi vào `results.jsonl` theo đúng thứ tự của manifest. Máy 8 GB: tối đa 2. Một lượt lỗi thực thi được ghi rõ, không làm mất các lượt khác. `summary.json` tách trượt trong phạm vi, trượt ngoài phạm vi và lỗi thực thi. Phạm vi chấm dùng P1 như M1 hiện có. `--max-runs N` dành cho kiểm tích hợp một phần, báo `partial`; không được dùng với `--record`.

`--record` vẫn yêu cầu cây làm việc sạch, thư viện planner từ đúng commit và đầu vào benchmark chưa đổi từ lúc sinh. SHA-256 bao gồm kịch bản, đường, dải tham số, bộ chạy và XSD. Khi chạy, hash từng cặp cụ thể được đối chiếu với manifest. Kết quả lưu cả định nghĩa và hash của lần sinh. M1, P1 và các study hiện có tiếp tục dùng API `loader.load()` / `with_fault()` nhưng đọc XML.

## Sampling

- Neo giữ nguyên toàn bộ giá trị, gồm thời gian chạy và hình học. S1f, S1g, S1bf, S14e được thêm theo Software Qualification Test Specification mục 5. S1f dùng đúng sáu chiều dài 30; 57,1; 14; 26; 5,1; 39 m và hai bán kính 787; 374 m của R171 Annex 4, 4.2.4.1; thêm đường tiếp cận và thoát.
- Biên: từng tham số số ở min/max, tham số khác ở danh định. Tham số phân loại dùng mọi giá trị trong tập.
- Pairwise: phủ mọi cặp min/danh định/max; với tham số phân loại là mọi cặp giá trị. Các tham số còn lại ở danh định. Đây là bộ phủ cặp xác định, không tối ưu số ca.
- Latin hypercube: 24 mẫu mỗi kịch bản logic, seed `20261111`; mỗi chiều số dùng một mẫu trong mỗi khoảng chia đều. Tập phân loại dùng chỉ số của khoảng mẫu. Mọi profile được ghép sau bước lấy mẫu.
- Khi lấy mẫu tốc độ, thời gian chạy thay đổi theo tỷ lệ nghịch để giữ quãng đường của ca danh định. Quy tắc này không áp dụng cho neo. Không loại ca vì kết quả planner.
- `curvature_scale` nhân độ cong của đường danh định; `direction` đảo trái/phải. S1 dùng tỷ lệ 1…4 tương ứng R = 1000…250 m; S1b dùng 2/3…4/3 tương ứng R = 300…150 m. Làn 2,5…5,5 m và tốc độ 10…130 km/h lấy từ ODD; biên offset/góc S2 lấy từ các neo. Không thêm ngưỡng đạt/trượt.
- Với lỗi, các mức cũ là bộ neo đi cùng nhau. F04 chỉ lấy mẫu thêm chế độ mất vạch; chế độ giảm độ tin giữ các neo c/d. F06 chỉ lấy mẫu thêm sai c2; sai c3 giữ neo c để không trộn tham số khác đơn vị. F01 lấy mẫu các mức sigma đã có; F02 lấy mẫu giá trị/thời điểm/thời lượng đã có.
- Ca trùng giá trị chỉ xuất một lần, ghi lại mọi cách chọn đã tạo ra nó. Các neo khác mã vẫn được giữ.

## Supported simulator subset

Đây là adapter cho một ego trên một đường phẳng ba làn có bề rộng không đổi. Hình học hỗ trợ `line`, `arc`, `spiral`; trạng thái ban đầu dùng `RoadPosition`, `Orientation`, `SpeedAction`; kết thúc dùng `SimulationTimeCondition`. Các cấu trúc ngoài tập hỗ trợ bị từ chối, không được coi là đã chạy.

| Phần mở rộng | Ý nghĩa |
|---|---|
| Vehicle `Properties`, `pp:adapter=single-ego-v1` | Nhận diện contract của adapter |
| `pp:profile` | Vehicle profile simulator; file cụ thể cập nhật bề rộng, wheelbase và khối lượng của Vehicle |
| `pp:acc` | `off`, `on`, `ignore_limits` như simulator hiện có |
| `pp:camera_view_m` | Tầm nhìn của camera [m], mặc định 80; tuỳ chọn |
| `pp:hwa_request_s`, `pp:hold_until_hwa` | Thời điểm yêu cầu HWA và giữ offset/góc đến khi HWA bắt đầu |
| `CustomCommandAction type="pp:lane_fault:v1"` | JSON có `kind`, `start_s`, `duration_s`, `lines`, `value`, `sigma_c0`, `sigma_c1`; áp dụng theo thời điểm chụp frame; duration −1 là tới cuối ca |
| `lane_width_m`, `curvature_scale`, `direction` | Bộ sinh dựng lại `.xodr` với số cụ thể; OpenDRIVE không chứa biểu thức `$parameter` |

Các phần mở rộng cần adapter tương ứng khi chuyển sang simulator khác. Qua XSD chứng minh đúng cấu trúc, không chứng minh các simulator khác tự hiểu HWA, ACC hay bơm lỗi của dự án.

Các ca chưa được simulator hỗ trợ được giữ ngoài manifest: S14-b/c/d (xe khác/mất LongitudinalPlan), F03-e (giữa lúc ELK), F04-e (làn mở rộng). S1b-d dùng `pp:camera_view_m` = 40: đường phẳng, camera thấy 40 m suốt ca. Loại biên khác, Q1 và các kịch bản chưa có trong phạm vi chuyển đổi này không được tính là đã phủ. Bộ full là đầy đủ theo các nguồn đã triển khai ở trên, không phải toàn bộ bảng kịch bản của tài liệu.
