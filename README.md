# Framework và Technical Documents giúp triển khai và đánh giá Path Planning cho L2 Lateral Features

Framework dùng mô phỏng Software-in-the-Loop (SIL) để kiểm thử path planner cho ba L2 lateral features HWA, LKA và ELK. Tải về và triển khai planner theo technical documents, build thành shared library, rồi chạy benchmark để xem kết quả trên dashboard HTML.

`interfaces/` cung cấp interface dùng chung, `adapters/sil/` nối planner library với simulator `sim/`, `benchmark/` chứa test data và `eval/` sinh test case, chạy simulation, tính metrics và tạo report.

## Technical Documents

| Tài liệu | Nội dung |
|---|---|
| [ADAS Function Specification (ADAS-FS)](docs/vi/adas-function-specification.md) | Điều kiện kích hoạt, can thiệp và kết thúc của HWA, LKA và ELK |
| [Software Requirements Specification (SRS)](docs/vi/path-planner-software-requirements-specification.md) | Operational Design Domain (ODD), requirements và performance targets |
| [Interface Control Document (ICD)](docs/vi/path-planner-interface-control-document.md) | Function call contract, inputs, outputs và signal conventions |
| [Software Qualification Test Specification (SQTS)](docs/vi/path-planner-software-qualification-test-specification.md) | Simulation environment, scenarios, fault injection, pass criteria và cách tổng hợp kết quả |
| [Hazard Analysis and Risk Assessment (HARA)](docs/vi/path-planner-hazard-analysis-and-risk-assessment.md) | Hazards, hazardous events và safety goals |
| [Software Architectural Design (SAD)](docs/vi/path-planner-software-architectural-design.md) | Thành phần, data flow và trình tự xử lý mỗi chu kỳ |
| [Software Detailed Design (SDD)](docs/vi/path-planner-software-detailed-design.md) | Thiết kế các khối xử lý T1–T11 và algorithm parameters |
| [Architecture Decision Records (ADR)](docs/vi/path-planner-architecture-decision-records.md) | Các quyết định thiết kế và lý do lựa chọn |
| [Mentor Report](docs/vi/mentor-report.md) | Tổng quan phạm vi, thiết kế và cách đánh giá của dự án |

Các bản tiếng Anh nằm trong [`docs/en/`](docs/en/).

## Hướng dẫn triển khai

Chạy các lệnh dưới đây tại thư mục gốc repository trên Linux hoặc macOS. Dùng cùng một phiên terminal để giữ Python virtual environment và biến `PLANNER_LIB`.

### 1. Cài môi trường chạy benchmark

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt matplotlib
python -m eval.fetch_schemas
python -m eval.validate benchmark
```

`eval.fetch_schemas` tải các schema ASAM còn thiếu và kiểm tra SHA-256. Matplotlib dùng để vẽ biểu đồ của test suite.

### 2. Build planner theo C interface

Dùng [`pp_planner.h`](interfaces/c/pp_planner.h) và [`pp_types.h`](interfaces/c/pp_types.h) khi build. Shared library cần export bốn hàm `pp_state_size`, `pp_init`, `pp_step` và `pp_version`. Nếu planner đã có interface riêng, hãy triển khai bốn hàm này trong adapter.

Ví dụ, nếu mã nguồn của bạn nằm trong `/duong/dan/toi/my_planner.c`, thay đường dẫn đó trong lệnh dành cho hệ điều hành của bạn. Với dự án có nhiều tệp, dùng hệ thống build của dự án để tạo shared library tương ứng.

```bash
# Linux
mkdir -p build/external
cc -std=c11 -O2 -shared -fPIC -I interfaces/c /duong/dan/toi/my_planner.c -o build/external/libmy_planner.so -lm
PLANNER_LIB="$PWD/build/external/libmy_planner.so"
```

```bash
# macOS
mkdir -p build/external
cc -std=c11 -O2 -dynamiclib -I interfaces/c /duong/dan/toi/my_planner.c -o build/external/libmy_planner.dylib -lm
PLANNER_LIB="$PWD/build/external/libmy_planner.dylib"
```

### 3. Chuẩn bị calibration data

Test case generator và evaluator hiện đọc `planner/calibration/calibration.yaml`. Trong bản clone dùng cho planner của bạn, tạo tệp này từ calibration dataset của đúng bản build đang thử. Dưới khóa `parameters`, mỗi calibration parameter mà evaluator đọc cần có `value` và `unit`. Danh sách parameters và cách đổi đơn vị nằm trong [`eval/calibration.py`](eval/calibration.py).

```bash
mkdir -p planner/calibration
cp /duong/dan/toi/calibration.yaml planner/calibration/calibration.yaml
```

### 4. Chạy test suite và mở dashboard

```bash
python -m eval.run_full --suite smoke --planner "$PLANNER_LIB" --mcap none --out build/benchmark/my-planner-smoke
```

Lệnh này sinh test case, chạy B0 conformance checks, chạy suite `smoke` và xuất dashboard. Mở `build/benchmark/my-planner-smoke/report.html` trong trình duyệt. Trang này liên kết tới `report-details.html` để xem chi tiết. Xem `run.log` nếu một bước dừng và `suite/summary.json` để kiểm tra số lượt đã chạy. Dashboard vẫn có thể được tạo khi một bước chạy test suite dừng giữa chừng.

Để thử nhanh luồng tích hợp, thêm `--max-runs 6` và chọn một output directory mới. Để chạy toàn bộ benchmark và giữ log MCAP cho các lượt có test failure, dùng lệnh sau.

```bash
python -m eval.run_full --suite full --planner "$PLANNER_LIB" --jobs 4 --out build/benchmark/my-planner-full
```

Để xuất lại dashboard từ kết quả `smoke` đã có, chạy lệnh sau.

```bash
python -m eval.report_html build/benchmark/my-planner-smoke/suite \
  --generation build/benchmark/my-planner-smoke/concrete/manifest.json \
  --out build/benchmark/my-planner-smoke/report.html
```

## Benchmark

Scenarios và faults dùng ASAM OpenSCENARIO XML 1.3.1 (`.xosc`). Road geometry dùng ASAM OpenDRIVE 1.8.1 (`.xodr`).

| Dữ liệu | Nội dung |
|---|---|
| [Scenarios](benchmark/scenarios/) | Logical scenarios, anchor variants và parameter ranges để sinh thêm test case |
| [Roads](benchmark/roads/) | Road geometry dùng trong các test case |
| [Faults](benchmark/faults/) và [Combinations](benchmark/combinations/) | Định nghĩa faults và cấu hình ghép nhiều faults trong một test case |
| [Test suites](benchmark/suites/) | Cấu hình chọn test case, vehicle profiles và seeds cho `smoke`, `regression` và `full` |

Để xem một test case, mở [scenario S1](benchmark/scenarios/S1.xosc), đối chiếu variant `a` trong [anchor file](benchmark/scenarios/S1.anchors.xosc) và xem [road geometry của S1a](benchmark/roads/S1a.xodr). Test case này mô tả xe chạy 90 km/h từ đoạn chuyển tiếp clothoid vào cung tròn bán kính 1.000 m.

Một số test case dùng extensions `pp:*` cho ADAS function signals hoặc fault injection. Khi đưa các test case này sang simulator khác, adapter cần hỗ trợ các extensions tương ứng. Cấu trúc tệp và sampling rules được mô tả trong [hướng dẫn benchmark](benchmark/README.md). Cách bổ sung test case được trình bày trong [hướng dẫn viết scenarios và faults](benchmark/AUTHORING.md).

## Evaluation

| Công cụ | Đầu vào và kết quả |
|---|---|
| [`eval.validate`](eval/validate.py) và [`eval.generate`](eval/generate.py) | Kiểm tra XML theo XSD. Test case generator đọc cấu hình test suite để tạo các cặp concrete scenario và road file cùng manifest. |
| [`eval.runner`](eval/runner.py) và [`eval.suite`](eval/suite.py) | Chạy một test case hoặc một test suite với planner. Kết quả gồm metrics, verdict và logs theo cấu hình chạy. |
| [`eval.report_html`](eval/report_html.py) | Đọc thư mục kết quả của một test suite để tạo HTML dashboard. |
