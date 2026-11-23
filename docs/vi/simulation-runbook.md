# Simulation Runbook

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `SIM-RB` |
| Phiên bản | 1.2 |
| Trạng thái | v1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-23 |

## 1. Purpose and scope {#rb-scope}

- **Mục đích.** Hướng dẫn cài, chạy và dùng simulator, bên chấm và workbench của Path Planning, từ clone sạch tới ba hành trình dùng chính.
- **Phạm vi.** Cài đặt, kiểm cài đặt, ba hành trình (H1 xem chất lượng planner, H2 xem cách xây nền tảng, H3 điều tra một hành vi lạ), lưu và khôi phục kết quả, gói bàn giao, thêm một SUT mới, xử lý sự cố, các việc để sau.
- **Ngoài phạm vi.** Độ tin cậy của công cụ ([Simulation Handbook](report.html?doc=simulation-handbook&lang=vi)). Requirement và phép thử của planner (Software Requirements Specification, Software Qualification Test Specification).

## 2. References {#rb-references}

| Tài liệu | Dùng cho |
|---|---|
| `README.md` | Điểm bắt đầu và cấu trúc mã nguồn |
| [Simulation Handbook](report.html?doc=simulation-handbook&lang=vi) | Model, giả định, verification, validation, yêu cầu nền tảng |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=vi) | Kịch bản, lỗi, tiêu chí đạt, kết luận |
| `research/README.md` | Lần chạy chính thức, `PP-TS`, `PP-PR` |
| `benchmark/README.md`, `benchmark/AUTHORING.md` | Viết kịch bản và lỗi |

## 3. Cài đặt {#rb-install}

Cần Python 3 (đã chạy với 3.13), CMake 3.20 trở lên, trình biên dịch C11. Linux hoặc macOS, không dùng Docker. Máy 8 GB RAM đủ; mỗi lượt chạy dài nhất dùng khoảng 420 MB.

```bash
git clone <địa chỉ repository> g1-path-planning
cd g1-path-planning
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt matplotlib
python -m eval.fetch_schemas
cmake -S planner -B build/planner -DCMAKE_BUILD_TYPE=Release \
  -DPython3_EXECUTABLE="$VIRTUAL_ENV/bin/python"
cmake --build build/planner
```

`eval.fetch_schemas` tải các XSD của ASAM và kiểm SHA-256; các file này không nằm trong git. Build tạo `build/planner/libpp_lcc` và `build/planner/libpp_lkaelk` (`.dylib` trên macOS, `.so` trên Linux).

## 4. Kiểm cài đặt {#rb-check}

| Lệnh | Kết quả đúng |
|---|---|
| `ctest --test-dir build/planner --output-on-failure` | 17/17 test C đạt |
| `python -m pytest -q` | Mọi test đạt (khoảng 2 phút) |
| `python -m eval.conformance` | Đạt C1, C2; C3 cho cờ Tích hợp được |
| `python -m eval.golden record --jobs 2` rồi `python -m eval.golden check --jobs 2` | Mọi đường chạy khớp checksum |
| `python -m eval.selfcheck --jobs 2` | Mọi planner mồi bị báo đúng requirement (`build/selfcheck/summary.md`) |

Mốc golden chỉ đúng với máy, thư viện planner và phiên bản Python, numpy đã ghi nó. Máy mới hoặc thư viện mới thì chạy `record` trước. `behavior_checksum` không so được giữa macOS và Linux.

## 5. H1: xem chất lượng planner {#rb-h1}

Khoảng 15 phút.

| Bước | Việc | Kết quả |
|---|---|---|
| 1 | `python -m eval.run_full --suite smoke --jobs 2 --out build/benchmark/planner-smoke` (vài phút) | `report.html`, `suite/report.md`, `suite/conclusion.json` |
| 2 | Mở `build/benchmark/planner-smoke/report.html` | Kết luận theo Software Qualification Test Specification 8.4, cờ Tích hợp được, danh sách trượt BLOCKER theo requirement kèm ca, profile, seed, thời điểm trượt đầu. Trang Thông tin báo cáo ghi phiên bản simulator và trạng thái validation của các model |
| 3 | `python3 -m workbench.server` rồi mở `http://127.0.0.1:8793/` | Workbench |
| 4 | Màn Suite và regression, chọn lần chạy, mục Điều tra một ca trượt, bấm Mở lại ở một ca trượt | Run mới chạy lại ca từ file đã đóng băng, so `behavior_checksum` với kết quả ghi trong suite và ghi khớp hay không |
| 5 | Mở run vừa tạo, tab Điều tra, bấm Phát lại từ đầu | Scene, tín hiệu và tiêu chí ở cùng một mốc thời gian; nhãn nguồn: truth của simulator, planner nhận, output của từng planner, arbitrator chạy thử |
| 6 | Màn Độ tin cậy | Golden set, kiểm bên chấm, verification; hồ sơ model ở Simulation Handbook |
| 7 | Màn So sánh và campaign, tab So sánh hai lần chạy: chọn hai lần chạy suite (baseline, candidate) rồi bấm So sánh | Khối Môi trường của hai bên (thư viện, calibration, commit, bộ đầu vào, máy), rồi số lượt mới trượt, hết trượt, còn trượt và lượt đổi hành vi; mỗi dòng có nút Mở lại ở candidate |

Lần chạy chính thức cuối cùng của dự án có sẵn trong `research/runs/`; `report.md` ở đó là báo cáo đã dùng để review.

Chọn `smoke` để thử luồng chạy, `regression` để kiểm hồi quy và `full` để đánh giá tập ca rộng nhất. Dùng thư mục đầu ra mới cho mỗi lần chạy. Mặc định suite ghi MCAP cho ca trượt. Dùng `--mcap none` khi chỉ cần kết quả chấm và báo cáo.

Để chấm planner khác, thêm `--planner <thư-mục-thư-viện>`. Dùng một clone riêng với `planner/calibration/calibration.yaml` khớp bản build đang chấm. Evaluator đọc `value` và `unit` của các tham số dùng để chấm.

## 6. H2: xem cách xây nền tảng {#rb-h2}

| Bước | Xem | Chứng minh |
|---|---|---|
| 1 | Sơ đồ lớp ở Simulation Handbook mục 7 | Lõi thực thi chung tách khỏi gói path planner |
| 2 | `tests/test_import_rules.py` | Ranh giới giữa các package do test giữ |
| 3 | `python -m eval.selfcheck --jobs 2` | Bên chấm phải bắt được lỗi cố ý trước khi được dùng |
| 4 | Một bundle trong `build/runs/<run_id>/`: `manifest.json`, `resolved-case.json`, `SHA256SUMS` | Mọi kết quả truy được tới code, thư viện, đầu vào |
| 5 | CI ở tab Actions của repository | Cổng tự động cho mỗi lần push |
| 6 | Simulation Handbook mục 18 và mục Thêm một SUT mới của tài liệu này | Phương pháp dùng lại được cho chức năng khác |

## 7. H3: điều tra một hành vi lạ {#rb-h3}

| Bước | Việc | Kết quả |
|---|---|---|
| 1 | Màn Chạy mới: chọn tình huống, lỗi, xe; bấm Chạy planner | Run nhận `run_id`, vào hàng đợi hoặc chạy |
| 2 | Đóng tab, mở lại sau; vào màn Run | Run vẫn chạy hoặc đã Hoàn tất |
| 3 | Mở run đã xong, bấm Phát lại | Phát lại từ bundle, không chạy planner |
| 4 | Tab Run con và giả thuyết, bấm Tạo run con, đổi một tham số | Run mới có `parent_run_id` |
| 5 | Thấy hành vi sai | Mở problem report theo `research/README.md`, ghi `run_id` |

### Campaign

Dùng khi cần chạy cùng lúc nhiều ca (một nhóm tình huống, lỗi, xe, seed) rồi so với lần chạy sau khi đổi planner.

| Bước | Việc | Kết quả |
|---|---|---|
| 1 | Màn So sánh và campaign, tab Campaign: nhập tên, chọn tình huống, lỗi, xe, seed | Số run hiện ngay (tối đa 40) |
| 2 | Bấm Tạo và chạy campaign | Danh sách run đóng băng; các run chạy qua cùng supervisor, vài run cùng lúc, còn lại chờ |
| 3 | Đóng tab, mở lại | Campaign vẫn chạy; trang tiến độ cập nhật mỗi 2 giây |
| 4 | Đọc Độ phủ: thiết kế, đã lên lịch, đã chạy xong, chấm được | Mức điều kiện xảy ra thật chưa đo |
| 5 | Hủy campaign nếu cần | Chỉ run của campaign này bị hủy |
| 6 | Sau khi đổi planner hoặc calibration và build lại, bấm Lặp lại trên bản hiện tại | Campaign mới với đúng danh sách cũ |
| 7 | Bấm So với campaign gốc | Tab So sánh với hai campaign: ghép theo cấu hình của run |

Run của campaign được ghim nên không bị dọn; bấm Xóa campaign khi không cần nữa.

Đọc riêng hai thông tin: Thực thi (có chạy hết không) và Kết luận (đạt hay trượt tiêu chí nào). Thời điểm trượt chỉ gợi ý chỗ cần nhìn; kết luận nguyên nhân cần run đối chứng.

## 8. Lần chạy chính thức {#rb-official}

| Việc | Lệnh | Ghi chú |
|---|---|---|
| Commit mọi thay đổi | | `--record` đòi cây làm việc sạch |
| Build lại hai thư viện từ đúng commit đó | `cmake --build build/planner` | Chuỗi `pp_version` mang commit |
| Ghi lại mốc golden | `python -m eval.golden record --jobs 2` | Sau mỗi lần build lại |
| Kiểm bên chấm | `python -m eval.selfcheck --jobs 2` và `python -m eval.conformance` | |
| Chạy regression | `python -m eval.run_full --suite regression --jobs 4 --record --artifact-dir "$SUITE_ARTIFACT_DIR"` | Khoảng 40 phút, mỗi tiến trình khoảng 420 MB |

Đặt `SUITE_ARTIFACT_DIR` trỏ tới kho dùng chung có quyền ghi, nằm ngoài repo. Có thể dùng `build/run-artifacts/` để thử cục bộ. `research/runs/<run-id>/` giữ `manifest.json`, `summary.json`, `report.md` và `conclusion.json`. Manifest ghi tên ZIP và SHA-256. ZIP chứa kết quả từng ca, B0 và bộ ca cụ thể đúng phiên bản đã chạy. Run ID được ghi vào `research/runs/INDEX.md`. Chỉ lần chạy chính thức được trích trong tài liệu và báo cáo.

### Khôi phục một suite

```bash
python -m eval.run_artifacts "research/runs/<run-id>" --artifact-dir "$SUITE_ARTIFACT_DIR"
```

Lệnh kiểm SHA-256, dựng lại hai bản dashboard và đặt suite dưới `build/benchmark/<run-id>/`. Mở `report.html`, chọn suite trong Workbench hoặc dùng `suite/` với `eval.compare`. Để xuất bộ đang có trong `build/benchmark/` lên web tĩnh, xem `web/README.md`. File MCAP, hình và log chẩn đoán của lượt gốc nằm ở thư mục cục bộ của lượt chạy.

### Dọn kết quả cục bộ

1. Dừng lượt ghi kết quả đang chạy. Dùng `du -sh build/benchmark/* web/dist` để biết thư mục nào chiếm chỗ.
2. Đọc `suite/summary.json` và cuối `run.log`. Giữ suite đang dùng để so sánh hoặc bàn giao. Thử khôi phục artifact của suite chính thức cần giữ trước khi dọn thư mục chạy gốc.
3. Giữ `build/runs/` và `build/campaigns/` khi còn dùng Workbench. Các run ghim nằm trong `build/runs/.pinned.json`. Dọn từng thư mục benchmark đã kiểm kê. Có thể xuất lại `web/dist/` bằng `node web/build-static.cjs`.

## 9. Gói bàn giao hai thư viện planner {#rb-handover}

SUT bàn giao là cặp `libpp_lcc` và `libpp_lkaelk` build từ cùng một commit.

```bash
cd build/planner
shasum -a 256 libpp_lcc.* libpp_lkaelk.* > SHA256SUMS      # macOS; Linux: sha256sum
```

| Việc kiểm | Cách |
|---|---|
| Cùng commit | Chuỗi `pp_version` của hai thư viện có cùng commit và cùng mã bộ calibration |
| Cùng bản đã chấm | sha256 khớp với `libraries[].sha256` trong `manifest.json` của lần chạy chính thức cuối |
| Bản cho Linux | CI build `.so` và đính kèm vào lần chạy của workflow Tests (artifact `planner-libraries`); sha256 của bản Linux khác bản macOS, vì trình biên dịch khác |
| Nạp vào bên chấm | `python -m eval.run_full --suite smoke --planner <thư mục có hai thư viện>` |

Bản Linux chỉ có kết quả smoke và B0 chạy trên chính nó; kết quả regression chính thức là của bản macOS.

Catalog ca kiểm đi kèm bản giao, để đội khác dựng test cho planner của họ mà không cần thư viện của nhóm:

```bash
python -m eval.catalog --suite regression --out build/catalog
```

| File | Nội dung |
|---|---|
| `planner-test-catalog.md`, `.csv`, `.json` | Mỗi anchor một dòng: Given (mô tả, ca chủ, profile, vòng), When chung, Then là requirement trong phạm vi chấm, Then vòng hở là phần chấm được khi xe đi theo quỹ đạo định sẵn; bảng câu requirement và mức nghiêm trọng |
| `benchmark/scenarios/`, `benchmark/faults/`, `benchmark/roads/` | OpenSCENARIO, OpenDRIVE của từng mã; ca tự chứa sinh bằng `eval.generate` |

## 10. Thêm một SUT mới {#rb-new-sut}

Thêm một SUT (ví dụ ACC, Lane Change Assist) cần năm thứ. Lõi thực thi, bundle, vòng đời run, server, quy trình `PP-TS`, `PP-PR`, `tools/trace.py` và bộ planner mồi (phương pháp) giữ nguyên.

| Thứ | Làm gì | Mẫu |
|---|---|---|
| Interface | Header C và kiểu dữ liệu của SUT, tài liệu interface | `interfaces/c/pp_planner.h`, `pp_types.h` |
| Adapter | Nạp thư viện qua ctypes, kiểm `pp_version`, bọc `init` và `step` | `adapters/sil/sil_planner.py` |
| Harness | Vòng mô phỏng: scheduler, kênh, cảm biến, stand-in cho SUT mới. Dùng lại `sim/runtime`, `sim/vehicle`, `sim/world`, `sim/faults/channel.py` | `sim/harness.py` |
| Kịch bản và lỗi | OpenSCENARIO, OpenDRIVE, lỗi, suite | `benchmark/` |
| Criterion | Requirement của SUT trong một Software Requirements Specification riêng, criterion trong `eval/`, mức nghiêm trọng theo cột Type | `eval/metrics.py`, `eval/severity.py` |

Việc kèm theo: viết bộ planner mồi riêng cho SUT (`eval/bait/`), thêm model mới vào `eval/credibility.py` và mục 9 của Simulation Handbook, đặt lệnh worker khác cho workbench. Giới hạn hiện có: `sim/runtime/channel.py` còn import kiểu `Received` của `interfaces`, cần tách trước SUT thứ hai.

## 11. Xử lý sự cố {#rb-trouble}

| Hiện tượng | Nguyên nhân thường gặp | Cách xử |
|---|---|---|
| Thiếu file XSD, test `openx` lỗi | Chưa chạy `eval.fetch_schemas` | `python -m eval.fetch_schemas` |
| Golden báo mốc không dùng được | Máy, thư viện hoặc phiên bản Python khác nơi ghi mốc | `python -m eval.golden record` rồi `check` |
| Cổng 8793 đã dùng | Workbench khác đang chạy | `python3 -m workbench.server --port <cổng>` |
| Run báo bundle từ cây làm việc có thay đổi chưa commit | Chạy khi chưa commit | Chạy lại được, nhưng chưa truy về một commit; commit rồi chạy lại nếu cần bằng chứng |
| `--record` từ chối | Cây chưa sạch hoặc thư viện build từ commit khác HEAD | Commit, build lại, ghi lại mốc golden |
| Artifact không khôi phục được | Thiếu ZIP hoặc SHA-256 không khớp | Xem tên ZIP trong `manifest.json`, lấy lại đúng bản từ kho lưu trữ |
| Hết RAM khi chạy suite | Quá nhiều tiến trình | `--jobs 2` |
| `behavior_checksum` khác giữa hai máy | Hệ điều hành hoặc trình biên dịch khác | Chỉ so trong cùng máy |

## 12. Việc để sau {#rb-backlog}

| Việc | Ước lượng (ngày công, sai số khoảng ±50 %) | Mở khi |
|---|---|---|
| `eval.suite` ghi bundle cho từng lượt | 2 đến 3 | Cần playback cho mọi ca suite |
| Campaign lớn hơn 40 run, hàng đợi qua đêm | 2 đến 3 | Cần chạy nhiều hơn một lượt |
| Ghi lỗi thật sự được bơm vào kết quả của run, để độ phủ của campaign có mức điều kiện xảy ra thật | 2 đến 3 | Cần đo độ phủ đủ năm mức |
| Quét K, tỉ số lái, trễ chấp hành theo dải có nguồn (PP-TS-023) | 3 đến 5, cộng thời gian chạy | Có nguồn dải đặc tính xe |
| Thư viện MCAP chính thức thay writer tự viết | 2 | Cần nén, chunk, seek |
| Đối chiếu hình học với esmini | 5 đến 10 | Cần chứng minh tập con OpenDRIVE |
| Chế độ thời gian thực nhiều tiến trình (PP-PR-068) | 10 trở lên | Cần kiểm jitter của hệ điều hành |
| Tách `Received` khỏi `sim/runtime/channel.py` | 1 | Trước SUT thứ hai |
| SUT thứ hai dùng lõi chung | 10 đến 15 | Có chức năng thứ hai cần kiểm |
| Nhiều người dùng: phân quyền, quota, sao lưu | 10 trở lên | Có người dùng thứ hai |
| Khai báo miền dùng của model đọc được bằng máy (SIM-REQ-122) | 3 đến 4 | Cần cảnh báo run ngoài miền |
| Validation model với dữ liệu xe thật | Theo dữ liệu | Có dữ liệu (Simulation Handbook mục 15) |

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.1 | 2026-11-21 | Bổ sung ghi, khôi phục và dọn kết quả suite |
| 1.0 | 2026-11-19 | Bản đầu: cài đặt, kiểm cài đặt, ba hành trình, so sánh và campaign, lần chạy chính thức, gói bàn giao, thêm SUT mới, xử lý sự cố, việc để sau |
| 1.2 | 2026-11-23 | Mục 9: catalog ca kiểm đi kèm bản giao (`eval.catalog`) |
