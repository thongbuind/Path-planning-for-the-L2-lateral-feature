# Quy trình nghiên cứu và truy vết kết quả

Thư mục này giữ dấu vết của mọi lựa chọn kỹ thuật: câu hỏi, phương án, cách đánh giá đã định trước, kết quả chạy và quyết định. Bộ tài liệu kỹ thuật (`docs/vi/`) chỉ chứa điều đã quyết; lý do và số liệu đứng sau mỗi quyết định nằm ở đây.

## Nguồn của quy trình

| Văn bản | Lấy gì |
|---|---|
| Automotive SPICE 3.1, SWE.2.BP6 | Đánh giá các phương án theo tiêu chí đặt trước; ghi lý do chọn |
| Automotive SPICE 3.1, SUP.8, SUP.9, SUP.10 | Configuration management; problem resolution; change request |
| ISO 26262-8:2018, mục 7, 8 | Mỗi kết quả và điều kiện tạo ra nó định danh được, tái lập được; thay đổi có phân tích ảnh hưởng |
| NASA Systems Engineering Handbook, mục 6.8 | Tiêu chí loại (bắt buộc) tách khỏi tiêu chí xếp hạng; công sức tỷ lệ với hậu quả của quyết định |
| Software Qualification Test Specification, mục 3, 7, 9 | Định trước; chỉnh và chấm tách riêng; thứ tự xếp hạng |

## Hai loại hồ sơ

| Loại | ID | Mở khi | File |
|---|---|---|---|
| Trade study | `PP-TS-nnn` | Một câu hỏi thiết kế có ít nhất hai phương án thật, hoặc một quyết định đổi requirement, ADR, interface | `studies/PP-TS-nnn-<tên>/study.md`, `plan.yaml` |
| Problem report | `PP-PR-nnn` | Một ca trượt requirement, hoặc hành vi sai thấy được trong log | `problems/PP-PR-nnn-<tên>.md` |

- ID không đánh số lại, không dùng lại. Hồ sơ bị bỏ thì giữ file, trạng thái `Bỏ`.
- Không cần study cho: chỉnh một calibration parameter trong dải quét đã có (dùng sweep), sửa lỗi code không đổi hành vi đã quy định.
- Danh sách mọi hồ sơ: [register.md](register.md). Mọi lần chạy chính thức: [runs/INDEX.md](runs/INDEX.md).

## Trạng thái

| Trạng thái | Nghĩa |
|---|---|
| Mở | Đã ghi câu hỏi và phương án |
| Đã khóa | `plan.yaml` có ngày khóa; tiêu chí, bộ chạy, seed không đổi nữa |
| Đang chạy | Đã có ít nhất một lần chạy chính thức |
| Chờ quyết định | Đủ số liệu, có đề xuất |
| Đã quyết | Có quyết định, đang đưa vào code và tài liệu |
| Đóng | Đã đưa vào; đã chạy hồi quy trên baseline mới |
| Bỏ | Không làm nữa, ghi lý do |

## Các bước của trade study

| Bước | Việc | Sản phẩm | Ai |
|---|---|---|---|
| 1. Mở | Câu hỏi, quyết định cần đưa ra; requirement và target liên quan; phương án, V0 là bản hiện tại | `study.md` mục 1–3; dòng mới ở `register.md` | Agent hoặc người |
| 2. Định trước | Tiêu chí loại: requirement của SRS. Xếp hạng: SQTS mục 9. Bộ chỉnh và bộ kiểm (suite trong `benchmark/suites/`), seed, ngân sách chỉnh cho mỗi phương án, mức chênh coi như ngang nhau | `plan.yaml` với `locked: <ngày>` | Người duyệt rồi mới khóa |
| 3. Cài phương án | Đổi thuật toán: chọn lúc build (`cmake`), mỗi phương án một thư viện; bản giao không có nhánh `if` chọn thuật toán. Đổi tham số: ghi đè calibration | Code kèm unit test | Agent |
| 4. Đóng băng | Commit mọi thứ phương án cần | Commit, tag nếu cần | Người |
| 5. Chạy | `python3 -m eval.study PP-TS-nnn --record` | `runs/<run-id>/` và một dòng ở `runs/INDEX.md` | Agent, sau khi người cho chạy |
| 6. Phân tích | Loại phương án trượt requirement; xếp hạng theo target; ca xấu nhất theo từng profile | `study.md` mục Kết quả | Agent |
| 7. Quyết định | Chọn phương án | `study.md` mục Quyết định; PP-ADR mới trỏ về study, hoặc sửa SDD, calibration, SRS kèm lý do | Người |
| 8. Đóng | Xóa phương án thua khỏi code giao (git giữ lại); chạy hồi quy (M1) trên baseline mới | Trạng thái `Đóng`, run ID của lần hồi quy | Agent, người duyệt |

- Đổi tiêu chí, bộ chạy hay seed sau khi đã thấy kết quả: ghi lý do ở `study.md`, mở lại khóa và chạy lại mọi phương án (SQTS mục 3).
- Phương án đổi thuật toán phải cùng ngân sách chỉnh: mỗi phương án chạy sweep của chính nó trước, rồi ghi bộ calibration tốt nhất vào `plan.yaml`.

## Các bước của problem report

| Bước | Việc |
|---|---|
| 1. Ghi nhận | Hiện tượng thấy được qua interface; run ID và seed tái hiện được |
| 2. Phân tích | Nguyên nhân gốc; requirement nào bị ảnh hưởng |
| 3. Cách sửa | Sửa cơ chế chung, không sửa riêng cho ca trượt. Có nhiều cách thì mở trade study |
| 4. Xác nhận | Run ID sau khi sửa: ca trượt đạt, bộ hồi quy không xấu đi |

## Lần chạy chính thức và nháp

| | Chính thức | Nháp |
|---|---|---|
| Lệnh | Thêm `--record` | Không có `--record` |
| Điều kiện | Cây làm việc sạch (đã commit); thư viện planner build từ đúng commit đó (`pp_version()`) | Không |
| Kết quả | `runs/<run-id>/`: `manifest.json`, `summary.md`, `results.json`; một dòng ở `runs/INDEX.md` | Chỉ trong `build/` |
| Được trích trong study, tài liệu, báo cáo | Có | Không |

`manifest.json` ghi: run ID, loại lần chạy, lệnh, commit và nhánh, thư viện (đường dẫn, sha256, chuỗi `pp_version()`), sha256 của calibration, suite và mọi file kịch bản, lỗi đã dùng, seed, phiên bản Python và numpy, máy, thời điểm. Log thô của simulator ở `build/`, không commit; chạy lại từ manifest để có lại.

Run ID: `<yyyymmdd-hhmm>-<loại>-<đối tượng>-<commit 7 ký tự>`.

## Thư mục

```
research/
  README.md            quy trình này
  register.md          danh sách trade study và problem report
  templates/           mẫu study.md, plan.yaml, problem.md
  studies/PP-TS-nnn-<tên>/study.md, plan.yaml
  problems/PP-PR-nnn-<tên>.md
  runs/INDEX.md        mọi lần chạy chính thức
  runs/<run-id>/       manifest.json, summary.md, results.json
```

## Liên hệ với tài liệu kỹ thuật

- Quyết định đổi kiến trúc: PP-ADR mới, phần "Liên quan" ghi `PP-TS-nnn`.
- Quyết định đổi requirement hay giới hạn: sửa SRS theo quy tắc sau BL1 (lý do, `tools/trace.py`, tăng phiên bản), lý do trỏ về study.
- Calibration chọn từ sweep: giá trị khởi đầu ở Software Architectural Design mục 11 đổi theo, lịch sử sửa ghi run ID.
- Tài liệu kỹ thuật không chép số liệu thô; chỉ ghi kết luận và run ID.
