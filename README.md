# Path Planner: mã nguồn

Bộ tài liệu kỹ thuật trong `docs/vi/` là nguồn chính thức. Code lệch với tài liệu thì phải báo, rồi sửa một bên theo quyết định. Đổi interface thì sửa Interface Control Document trước, rồi mới sửa schema.

## Cấu trúc

| Thư mục | Vai trò | Ngôn ngữ |
|---|---|---|
| `interfaces/` | Contract của path planner: input, output, contract gọi hàm. Chỉ có định nghĩa, không có logic | Schema YAML; sinh C và Python |
| `planner/` | Sản phẩm, black box. Thư viện C11 có API C (PP-ADR-013) | C11 |
| `adapters/sil/` | Cầu nối simulator Python với thư viện planner (ctypes) | Python |
| `sim/` | Môi trường test: lập lịch, đồng hồ, CAN, thế giới, mô hình xe, cảm biến, khối chạy thử, cơ chế bơm lỗi, log | Python + numpy |
| `benchmark/` | Bài thi: kịch bản, danh mục lỗi, bộ chỉnh và bộ kiểm, seed. Chỉ có dữ liệu | YAML |
| `eval/` | Người chấm: chạy bài thi, tiêu chí đạt, chỉ số, xếp hạng, báo cáo | Python |
| `tests/` | Test của code (unit, integration). Không phải benchmark | Python, C |

```
interfaces/
  schema/            nguồn duy nhất, theo Interface Control Document
  gen.py             sinh interfaces/c/pp_types.h, kiểu Python, kiểu ctypes của adapter
  c/                 pp_types.h (sinh ra), pp_planner.h (contract gọi hàm)
  conventions.py, inputs/, outputs/   kiểu Python (sinh ra)
  planner.py         contract hành vi phía Python (Protocol)
planner/
  src/               T1 đến T11 theo Software Detailed Design
  calibration/       calibration.yaml → sinh pp_calibration.c lúc build
  CMakeLists.txt
adapters/sil/        build và gọi libpp_planner
sim/                 runtime/ can/ world/ vehicle/ sensors/ stand_ins/ faults/ logging/ harness.py
benchmark/           scenarios/ faults/ suites/ seeds.yaml
eval/                loader, runner, criteria, metrics, flexibility, ranking, report
tests/               interfaces/ planner/ sim/ eval/ test_import_rules.py
```

## Quy tắc import

Planner và bên đánh giá phát triển độc lập (Software Qualification Test Specification mục 3). Trong code, nguyên tắc này thành quy tắc import, kiểm bằng `tests/test_import_rules.py`.

| Thư mục | Được dùng | Không được dùng |
|---|---|---|
| `interfaces/` | không gì cả | mọi thư mục khác |
| `planner/` | `interfaces/c/` | `sim`, `benchmark`, `eval`, `adapters` |
| `adapters/` | `interfaces`, thư viện planner đã build | `sim`, `benchmark`, `eval` |
| `sim/` | `interfaces` | `planner`, `adapters`, `benchmark`, `eval` |
| `benchmark/` | là dữ liệu, không import gì | — |
| `eval/` | `interfaces`, `sim`, `adapters`, đọc file trong `benchmark/` | ruột của `planner` |

`sim/harness.py` nhận planner từ bên ngoài, là một đối tượng đúng contract `interfaces/planner.py`. Chỉ `eval/` biết lắp planner nào vào.

## Planner tích hợp được vào hệ thống thật

- API C duy nhất ở `interfaces/c/pp_planner.h`: `pp_state_size`, `pp_init`, `pp_step`.
- Không cấp phát động, không đọc file, không đọc đồng hồ hệ thống, không biến toàn cục. Bên gọi cấp vùng nhớ trạng thái.
- Calibration sinh thành struct hằng lúc build. `pp_init` kiểm giới hạn ở Software Requirements Specification mục 7; sai thì không gửi Trajectory.
- Simulator gọi đúng thư viện sẽ bàn giao (SIL). Trên xe thật chỉ cần viết adapter cho nền tảng đích (PP-ASM-019).
- C11, theo một phần MISRA C:2012.

## Code bám theo tài liệu

- Hàm, hằng số hay test hiện thực một requirement thì ghi ID (ví dụ `PP-SWR-001`) trong chú thích. Unit theo mã T1 đến T11 của Software Detailed Design.
- Con số từ requirement khai báo ở đúng một chỗ, kèm ID. Không viết số trực tiếp trong logic.
- Không giả định một xe cụ thể: mọi thông số xe đọc từ VehicleConfig.
- Thông số của khối chạy thử nằm trong code của `sim/`, kèm mục nguồn ở Software Qualification Test Specification.

## Lệnh

```bash
python3 interfaces/gen.py              # sinh lại kiểu C, Python, ctypes từ schema
cmake -S planner -B build/planner && cmake --build build/planner
(cd build/planner && ctest)            # C unit test của từng unit (tests/planner/c)
python3 -m pytest
python3 -m eval.runner S1 a --seed 1   # một kịch bản vòng kín SIL; kết quả ở build/runs/
```
