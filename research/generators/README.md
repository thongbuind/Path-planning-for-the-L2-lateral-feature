# Generator lab

Nơi phát triển song song các generator T7 của LCC planner cho [PP-TS-031](../studies/PP-TS-031-t7-generator-campaign/study.md). Generator thắng mới chuyển vào `planner/src/generators/`.

- Contract chung: [`planner/src/generators/pp_t7.h`](../../planner/src/generators/pp_t7.h), input ở [`pp_t7_input.h`](../../planner/src/generators/pp_t7_input.h), hàm dùng chung ở [`t7_common.h`](../../planner/src/generators/t7_common.h).
- Bộ chạy: [PP-T7](../../benchmark/suites/PP-T7.yaml). Cách xếp hạng: Software Qualification Test Specification mục 9.1, 9.2. Cửa loại, giả thuyết và các bảng kết quả: mục 2 của [IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md) và `plan.yaml` của PP-TS-031. Tiêu chí không chép sang đây.
- Danh sách generator, trạng thái và session phụ trách: [registry.yaml](registry.yaml).

## Thư mục

```
research/generators/
  README.md              tệp này
  registry.yaml          tên, loại, generator gốc, trạng thái, khóa CMake, session
  new_generator.py       tạo generator mới từ templates/generator
  templates/generator/   mẫu: generator.yaml, generator.cmake, src/, tests/, notes.md
  common/                phần C dùng chung giữa các generator lab (driver_shape: smoothstep bậc 7)
  pilots/                nguyên mẫu cũ của PP-TS-024, 025 (chỉ để tham khảo; research/t7_potential.py dùng)
  bench/quick.py         quick bench (L1)
  <tên>/                 một generator lab
  RESULTS.md             bảng kết quả, do python3 -m eval.techniques --study PP-TS-031 sinh
```

## Thêm một generator

1. Thêm mục vào `registry.yaml` (session phụ trách contract), rồi tạo thư mục:

```bash
python3 research/generators/new_generator.py quintic_tangent_point
```

2. Sửa `src/<tên>.h`: `pp_t7_ws_t` (trạng thái giữa các chu kỳ, kích thước cố định) và `PP_T7_SUPPORT_FLOOR` (1 nếu LCC đặt sàn PP-SWR-006 cho path của generator).
3. Sửa `src/<tên>.c`: `pp_t7_reset`, `pp_t7_generate`, `pp_t7_report` (telemetry). Mẫu bắt đầu giống `quintic_duration`.
4. Tham số mới khai báo ở `calibration` của `generator.yaml`, tên bắt đầu bằng `calibration_prefix` + `_`. Build báo lỗi nếu thiếu tiền tố, trùng tên hoặc tiền tố trùng với tham số chung.
5. Dùng `common/`: bỏ chú thích dòng `include(.../common/common.cmake)` trong `generator.cmake`.
6. Ghi ý tưởng và các lần dò vào `notes.md`.

Build thử và chạy unit test:

```bash
cmake -S planner -B build/lab/<tên>-tests -DPP_T7=lab -DPP_T7_LAB=<tên> -DCMAKE_BUILD_TYPE=Release
```

```bash
cmake --build build/lab/<tên>-tests && ctest --test-dir build/lab/<tên>-tests --output-on-failure
```

## Ba tầng kiểm

| Tầng | Lệnh | Dùng cho | Được trích trong study |
|---|---|---|---|
| L0 unit | `ctest` của build lab: `test_t7_contract` chung cho mọi generator, cùng `tests/` của generator | Đúng contract, đúng phần mới; được biết bên trong | Không |
| L1 quick bench | `python3 research/generators/bench/quick.py <tên> [--set tên=giá trị] [--telemetry] [--against <nhãn>]` | Dò nhanh trên 3 dòng vòng hở × seed 1, 2 và S1d, S1g, S1b a vòng kín seed 1 (`--runs tuning`: cả phần tuning). Kết quả nháp trong `build/lab/<nhãn>/` | Không |
| L2 chính thức | `python3 -m eval.study PP-TS-031 --record` theo GĐ 4, 5 | Chọn calibration trên tuning, chấm trên test | Có |

Quick bench từ chối seed 3–4 và dòng chỉ có ở phần test.

## Build và `pp_version()`

| Khóa CMake | Ý nghĩa |
|---|---|
| `PP_T7` | `quintic_duration` (mặc định), `qp_jerk_admm`, `lab`; alias cũ `quintic`, `qp` |
| `PP_T7_LAB` | Tên thư mục generator lab khi `PP_T7=lab` |
| `PP_T7_LAB_CALIBRATION` | Bản `generator.yaml` có giá trị khác, do sweep ghi trong `build/` |
| `PP_T7_TELEMETRY` | Bật telemetry nghiên cứu; không bao giờ có trong bản giao và không dùng khi đo thời gian |

`pp_version()` của bản lab ghi `t7 <tên> t7_src <hash>`. Hash tính trên mã C, header và `generator.cmake`. Calibration của lab nằm trong mã `calibration`. Mã lab chưa commit làm bản build có cờ `-dirty`, nên không vào được lần chạy chính thức.

Telemetry (`pp_t7_telemetry_t`) ghi khối lượng việc, lý do dùng nghiệm thay thế, số phép tính của mô hình học, residual, slack và mức T10 sửa path ở chu kỳ gần nhất. Đọc qua `pp_lcc_t7_telemetry(state)`. Đơn vị của `work` và ý nghĩa mã `fallback` khai báo ở `generator.yaml`.

## Quy tắc

- L1 và dữ liệu huấn luyện không dùng seed 3–4 hay dòng chỉ có ở phần test.
- Từ GĐ 4, không đổi suite, tiêu chí, dung sai, seed, luật chọn. Buộc phải đổi thì ghi lý do và chạy lại mọi phương án.
- Ca trượt thì sửa cơ chế chung của generator, không sửa riêng cho ca đó.
- Mỗi generator chỉ sửa trong thư mục của nó. Contract, CMake, `common/` và `registry.yaml` (trừ trạng thái) chỉ sửa ở session phụ trách contract.
- Planner chỉ nhận dữ liệu qua interface: generator không đọc tên kịch bản, seed hay cấu hình benchmark.
