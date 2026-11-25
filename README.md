# Path Planning cho ADAS L2

Hai planner C11 chạy trong môi trường Software-in-the-Loop (SIL). LCC giữ làn và bám xe trước khi mất vạch. LKA/ELK sinh quỹ đạo can thiệp khi xe lệch làn. Arbitrator của hệ thống chọn quỹ đạo.

## 1. Build planner

Chạy từ thư mục gốc trên Linux hoặc macOS. Cần Python 3, CMake 3.20 trở lên và trình biên dịch C11.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt matplotlib
python -m eval.fetch_schemas
cmake -S planner -B build/planner -DCMAKE_BUILD_TYPE=Release \
  -DPython3_EXECUTABLE="$VIRTUAL_ENV/bin/python"
cmake --build build/planner
```

Hai thư viện `libpp_lcc` và `libpp_lkaelk` nằm trong `build/planner/`. [C API](interfaces/c/pp_planner.h) · [Calibration](planner/calibration/calibration.yaml)

## 2. Chạy smoke

```bash
python -m eval.run_full --suite smoke --max-runs 6 --jobs 2 --mcap none \
  --out build/benchmark/planner-smoke-quick
```

Mở `build/benchmark/planner-smoke-quick/report.html`. Đây là lượt kiểm tra nhanh sáu ca đầu. [Chạy đủ suite, chấm planner khác và ghi kết quả chính thức](docs/vi/simulation-runbook.md)

## 3. Mở Workbench

```bash
python -m workbench.server
```

Mở [Workbench cục bộ](http://127.0.0.1:8793/) để chạy một ca, phát lại, so sánh suite hoặc mở campaign. [Simulation Runbook](docs/vi/simulation-runbook.md) · [Web tài liệu và dashboard](web/README.md)

## Tra cứu

| Đường dẫn | Nội dung |
|---|---|
| [`planner/`](planner/) · [`interfaces/`](interfaces/) | Planner C11, calibration và giao diện C/Python |
| [`sim/`](sim/) · [`adapters/sil/`](adapters/sil/) | Simulator và cầu nối tới hai thư viện planner |
| [`benchmark/`](benchmark/) · [`eval/`](eval/) | Định nghĩa ca, tiêu chí chấm và báo cáo |
| [`execution/`](execution/) · [`workbench/`](workbench/) · [`web/`](web/) | Thực thi run, bundle, Workbench và trang dự án |
| [Simulation Handbook](docs/vi/simulation-handbook.md) · [Tài liệu VI](docs/vi/) · [Tài liệu EN](docs/en/) | Mô hình SIL, yêu cầu, giao diện, thiết kế và đặc tả kiểm thử |
| [`research/`](research/) · [Run Index](research/runs/INDEX.md) | Trade study, problem report và hồ sơ lần chạy chính thức |
| [`tests/`](tests/) · [CI](.github/workflows/tests.yml) | Unit test, integration test, conformance B0 và golden set |
