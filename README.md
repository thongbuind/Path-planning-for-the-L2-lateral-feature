# Path Planning cho ADAS L2

Triển khai **hai path planner C11** dùng chung một lõi: LCC planner (giữ làn, bám xe trước khi mất vạch) và LKA/ELK planner (can thiệp khi lệch làn). Việc chọn path của planner nào thuộc arbitrator của hệ thống. Repo có mã nguồn và calibration để build planner, mô phỏng Software-in-the-Loop (SIL) để chạy và đánh giá planner, cùng bộ tài liệu kỹ thuật mô tả yêu cầu, thiết kế, giao diện và tiêu chí kiểm thử.

## **Technical Documents**

| Tài liệu | Nội dung |
|---|---|
| [ADAS Function Specification (ADAS-FS)](docs/vi/adas-function-specification.md) | Mô tả khi nào LCC (HWA), LKA và ELK khả dụng, yêu cầu can thiệp, kết thúc hoặc nhường quyền lái cho tài xế. Tài liệu định nghĩa trạng thái chức năng, cách dùng khoảng cách và thời gian tới vạch, điều kiện cảnh báo, và trách nhiệm của khối Chức năng ADAS khi trao đổi với planner. |
| [Software Requirements Specification (SRS)](docs/vi/path-planner-software-requirements-specification.md) | Xác định phạm vi vận hành (ODD), giả định về xe và tín hiệu, cùng giới hạn calibration. Các yêu cầu có mã `PP-SWR` bao quát giữ làn, can thiệp, tính liên tục của quỹ đạo, xử lý đầu vào lỗi và trao đổi với khối dọc. Tài liệu cũng liệt kê các chỉ tiêu hiệu năng dùng để đo và so sánh. |
| [Interface Control Document (ICD)](docs/vi/path-planner-interface-control-document.md) | Đặc tả API C và các thông điệp trao đổi với mô hình làn, nhận dạng vật thể, CAN khung gầm, khối Chức năng ADAS và bộ điều khiển. Tra cứu ở đây kiểu dữ liệu, đơn vị, hệ tọa độ, timestamp, counter, tần số, timeout và ý nghĩa của từng trường đầu ra. |
| [Software Architectural Design (SAD)](docs/vi/path-planner-software-architectural-design.md) | Mô tả cách các khối của planner nối với nhau trong một chu kỳ, từ kiểm tra dữ liệu và bù trễ đến dựng đường tham chiếu, chọn chức năng và sinh quỹ đạo. Tài liệu giải thích tương tác với khối dọc khi vào cua, các mức suy giảm khi mất tín hiệu và các tình huống biên. |
| [Software Detailed Design (SDD)](docs/vi/path-planner-software-detailed-design.md) | Ánh xạ các khối xử lý T1–T12 sang module C và mô tả thuật toán ở từng bước. Có công thức và tham số cho dựng đường tham chiếu, nối với quỹ đạo cũ, sinh quỹ đạo bằng đa thức bậc năm hoặc QP, dời tâm làn và kiểm tra tính khả thi. |
| [Architecture Decision Records (ADR)](docs/vi/path-planner-architecture-decision-records.md) | Ghi bối cảnh, các phương án đã xét, quyết định và hệ quả cho từng lựa chọn kiến trúc. Các mục giải thích vì sao hệ thống tách lập kế hoạch ngang và dọc, bù trễ theo thời điểm camera chụp, nối quỹ đạo giữa các chu kỳ và đóng gói planner thành thư viện C11. |
| [Hazard Analysis and Risk Assessment (HARA)](docs/vi/path-planner-hazard-analysis-and-risk-assessment.md) | Xác định ranh giới hệ thống, các tình huống vận hành và sự kiện nguy hiểm. Tài liệu ghi mức độ nghiêm trọng, mức phơi nhiễm, khả năng kiểm soát và ASIL đề xuất, rồi liên hệ các mục tiêu an toàn, điều kiện kích hoạt SOTIF và cơ chế xử lý của planner. |
| [Software Qualification Test Specification (SQTS)](docs/vi/path-planner-software-qualification-test-specification.md) | Mô tả môi trường SIL, cách sinh kịch bản, tiêm lỗi và quét tham số. Tài liệu chỉ ra cách dùng B0 để kiểm tra giao diện, cách chọn ca cho B1–B8, tiêu chí đạt/trượt theo yêu cầu, chỉ số hiệu năng và cách lập báo cáo hoặc so sánh planner. |
| [Mentor Report tuần 2](docs/vi/mentor-report.md) | Tổng quan dự án từ tài liệu kỹ thuật đến framework, SIL, path planner, kết quả benchmark và các hướng nghiên cứu đang mở. |

Mở `web` để xem sơ đồ hệ thống, tài liệu song ngữ, mô phỏng và dashboard benchmark đã lưu. [Hướng dẫn mở web](web/README.md) · [Tài liệu tiếng Anh](docs/en/)

## Framework

Framework chạy thư viện planner trong môi trường Software-in-the-Loop (SIL). Trong ca vòng kín, bộ điều khiển ngang và EPS giả lập dùng quỹ đạo của planner để điều khiển mô hình xe. Trạng thái xe sau đó đi qua cảm biến giả lập và quay lại làm đầu vào cho chu kỳ kế tiếp. Ca vòng hở dùng chuyển động xe theo kịch bản để kiểm tra đầu ra của planner với đầu vào có thể lặp lại. [Môi trường kiểm thử SIL](docs/vi/path-planner-software-qualification-test-specification.md)

- **Interface.** Các kiểu dữ liệu C và Python dùng chung định nghĩa tín hiệu, quy ước và cách gọi planner. [`interfaces/`](interfaces/)
- **SIL adapter.** Nạp hai thư viện chia sẻ bằng `ctypes` và chuyển đổi dữ liệu giữa simulator Python và C API của hai planner. [`adapters/sil/`](adapters/sil/)
- **Simulator.** Mô phỏng đường, xe, cảm biến (có LeadTarget), thời gian truyền tín hiệu và các khối ADAS, ACC, arbitrator chạy thử, điều khiển ngang, EPS. Bộ mô phỏng dùng seed để lặp lại điều kiện chạy và có thể đưa lỗi vào cảm biến hoặc kênh truyền. [`sim/`](sim/)
- **Evaluator.** Đọc dữ liệu benchmark, sinh ca cụ thể, chạy từng ca với thư viện đã chọn, rồi tính chỉ số và xuất kết quả đạt/trượt cùng dashboard. [`eval/`](eval/)
- **Lõi thực thi.** Dùng chung cho mọi hệ thống được kiểm, không biết path planner: định danh run, bundle kết quả (ghi tạm rồi đổi tên, `SHA256SUMS`), vòng đời run trong tiến trình riêng, phân loại lỗi. Chỉ dùng thư viện chuẩn. [`execution/`](execution/)
- **Workbench.** Server cục bộ của web mô phỏng: lượt chạy thuộc về server, không thuộc về tab; mỗi lượt để lại bundle ở `build/runs/<run_id>/`. Có màn so sánh hai lần chạy suite (hoặc hai campaign) và campaign (danh sách run đóng băng, tối đa 40 run, lưu ở `build/campaigns/`). Chạy `python3 -m workbench.server`. Hướng dẫn dùng: [Simulation Runbook](docs/vi/simulation-runbook.md). [`workbench/`](workbench/) · [Web mô phỏng](web/simulation/README.md)

## Path Planner

Hai planner C11 chạy mỗi 25 ms (40 Hz), mỗi planner một thư viện (`libpp_lcc`, `libpp_lkaelk`) và không chia sẻ trạng thái lúc chạy. Đầu vào gồm mô hình làn, tín hiệu khung gầm, trạng thái và chuyển động xe, yêu cầu ADAS, kế hoạch dọc và cấu hình xe; LCC planner còn nhận danh sách vật thể và xe trước (LeadTarget). Mỗi chu kỳ kiểm tra tín hiệu, bù trễ theo chuyển động xe, dựng đường tham chiếu; LKA/ELK planner chọn ELK trước LKA. [Mã nguồn planner](planner/src/) · [Giao diện C](interfaces/c/pp_planner.h)

LCC planner sinh quỹ đạo giữ làn, dời tâm làn 10 cm khi có một xe lớn ở làn bên, và bám xe trước khi mất cả hai vạch. LKA/ELK planner sinh quỹ đạo can thiệp về tâm làn khi nhận yêu cầu phù hợp; Trajectory của nó chỉ hợp lệ khi đang can thiệp. Planner tận dụng quỹ đạo chu kỳ trước để giữ liên tục trong phạm vi quan sát và kiểm tra giới hạn động học, gia tốc ngang và độ giật. [Thiết kế chi tiết](docs/vi/path-planner-software-detailed-design.md)

| Đầu ra | Planner | Nội dung |
|---|---|---|
| `Trajectory` | Cả hai | Quỹ đạo 31 điểm cho 3 giây tới, kèm mốc kết thúc phần nằm trong tầm nhìn của mô hình làn và `planner_id` |
| `LccStatus` | LCC | Quỹ đạo có dùng được hay không, chế độ dựng path (`lcc_mode`: LANE, INFERRED, FOLLOW, COAST) và các cờ giới hạn |
| `InterventionStatus` | LKA/ELK | Chức năng đang can thiệp, pha LKA và ELK, cờ giới hạn |
| `LateralLimits` | LCC | Tốc độ tối đa theo độ cong và khoảng cách tới điểm có độ cong lớn nhất trong tầm nhìn, phục vụ khối dọc |

### Build planner

Chạy từ thư mục gốc của repo trên Linux hoặc macOS. Cần Python 3, CMake 3.20 trở lên và trình biên dịch C11.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt matplotlib
python -m eval.fetch_schemas

cmake -S planner -B build/planner -DCMAKE_BUILD_TYPE=Release \
  -DPython3_EXECUTABLE="$VIRTUAL_ENV/bin/python"
cmake --build build/planner --target pp_lcc pp_lkaelk
```

`eval.fetch_schemas` tải các XSD của ASAM từ ASAM và kiểm SHA-256; các file này không nằm trong git vì điều khoản giấy phép của ASAM.

CMake tạo `build/planner/libpp_lcc` và `build/planner/libpp_lkaelk` (đuôi `.so` trên Linux, `.dylib` trên macOS). Bộ calibration đi kèm được biên dịch vào thư viện. Sửa YAML rồi build lại để áp dụng giá trị mới. [Calibration](planner/calibration/calibration.yaml)

## Benchmark

Benchmark dùng ASAM OpenSCENARIO XML 1.3.1 cho kịch bản và định nghĩa lỗi, ASAM OpenDRIVE 1.8.1 cho hình học đường. Cấu hình mỗi bộ chọn kịch bản, biến thể, lỗi, cấu hình xe và seed. `smoke` là bộ chạy nhanh, `regression` dùng để kiểm tra hồi quy sau thay đổi, và `full` dùng để đánh giá trên tập ca rộng nhất. [Cấu hình các bộ chạy](benchmark/suites/) · [Cách viết ca mới](benchmark/AUTHORING.md)

Trước khi chạy các kịch bản, **B0** kiểm tra API C, bố trí dữ liệu và cách thư viện xử lý trạng thái và đầu ra. Dashboard tổng hợp kết quả mô phỏng theo tám nhóm dưới đây. Một ca có thể được tính vào nhiều nhóm. [Cấu trúc benchmark](benchmark/README.md) · [Các lần chạy đã ghi nhận](research/runs/INDEX.md)

| Nhóm | Nội dung đánh giá |
|---|---|
| B1 · Nominal | Hành vi trong điều kiện vận hành bình thường |
| B2 · Regulatory | Các ca thử theo quy định và giao thức đánh giá được nêu trong SQTS |
| B3 · Performance limit | Hành vi ở biên ODD hoặc khi đường đòi hỏi gia tốc ngang vượt giới hạn của chức năng |
| B4 · Robustness | Khả năng xử lý lỗi cảm biến, thời gian và tính toàn vẹn của tín hiệu |
| B5 · Degradation and refusal | Khi nào planner cần giới hạn hỗ trợ, suy giảm hoặc từ chối sinh quỹ đạo |
| B6 · Comfort | Độ êm của quỹ đạo và chuyển động xe trong các ca danh định |
| B7 · Flexibility | Kết quả của cùng một bản build và calibration trên các cấu hình xe khác nhau |
| B8 · Compute | Thời gian tính của planner trên các ca chạy |

### Chạy benchmark và xem kết quả

Chạy thử 6 lượt đầu của bộ `smoke` với thư viện vừa build.

```bash
python -m eval.run_full --suite smoke --max-runs 6 --mcap none \
  --out build/benchmark/planner-smoke-quick
```

Lệnh tự nạp hai planner từ `build/planner/` khi `PP_PLANNER_LIB` chưa được đặt. Mở `build/benchmark/planner-smoke-quick/report.html` trong trình duyệt để xem kết quả và chuyển sang `report-details.html` khi cần xem từng ca. Xem `suite/summary.json` để kiểm tra số lượt đã chạy và `run.log` để xem đầu ra từng bước.

Chạy đủ bộ `smoke` hoặc `full` với planner trong repo. Dùng thư mục đầu ra mới cho mỗi lần chạy.

```bash
python -m eval.run_full --suite smoke --mcap none --out build/benchmark/planner-smoke
python -m eval.run_full --suite full --jobs 4 --out build/benchmark/planner-full
```

Kiểm hành vi của simulator sau mỗi thay đổi công cụ bằng golden set: `python -m eval.golden record` trước khi sửa, `python -m eval.golden check --paths runner,suite,live` sau khi sửa; checksum phải giữ nguyên. [Golden set](benchmark/suites/golden.yaml)

Mặc định, `eval.run_full` ghi log MCAP cho các lượt có tiêu chí trượt. Sau khi sửa dữ liệu benchmark, kiểm tra XML bằng `python -m eval.validate benchmark`. Dùng `python -m eval.fetch_schemas` nếu cần tải các XSD ASAM còn thiếu và kiểm tra SHA-256.

### Dùng planner khác

Build mỗi planner thành thư viện chia sẻ (`.so` hoặc `.dylib`) theo C API, với bốn hàm `pp_<planner>_state_size`, `_init`, `_step` và `_version` (`pp_lcc_` cho LCC planner, `pp_lkaelk_` cho LKA/ELK planner). Các kiểu dữ liệu nằm trong `pp_types.h`. [Khai báo API](interfaces/c/pp_planner.h) · [Kiểu dữ liệu](interfaces/c/pp_types.h)

```bash
python -m eval.run_full --suite smoke --planner /duong/dan/toi/thu-muc-co-libpp_lcc-va-libpp_lkaelk \
  --mcap none --out build/benchmark/my-planner-smoke
```

Khi đánh giá planner khác, dùng một bản clone riêng và đặt bộ calibration của đúng bản build đang thử tại `planner/calibration/calibration.yaml`. Evaluator đọc `value` và `unit` của các tham số dùng để chấm. [Danh sách tham số evaluator đọc](eval/calibration.py)
