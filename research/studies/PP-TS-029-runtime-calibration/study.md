# PP-TS-029 Calibration chỉnh được khi tune trên xe

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-23 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-ADR-013; Interface Control Document; Software Requirements Specification mục 7; Software Detailed Design mục 3, 3.1; `planner/calibration/` |

## 1. Câu hỏi

- Quyết định cần đưa ra: calibration parameter của planner được nạp và chỉnh thế nào khi tune trên xe, mà vẫn giữ kiểm giới hạn của Software Requirements Specification mục 7.
- Vì sao cần: hiện `calibration.yaml` sinh thành struct hằng lúc build (PP-ADR-013), `pp_*_init` chỉ nhận VehicleConfig. Đổi một con số phải build lại. Bước tune trên xe của quy trình công ty cần đổi calibration mà không build lại.

## 2. Phương án

| ID | Phương án | Ghi chú |
|---|---|---|
| V0 | Struct hằng lúc build | Mốc |
| V1 | `pp_*_init` nhận thêm con trỏ tới bộ calibration do bên gọi cấp; NULL thì dùng bộ build sẵn. Planner kiểm từng giá trị theo mục 7, sao vào vùng trạng thái; sai thì không gửi Trajectory như khi thiếu VehicleConfig | Đổi C API và adapter SIL; đổi calibration giữa hai lần khởi tạo |
| V2 | Bộ calibration nằm ở một vùng nhớ riêng có mô tả ASAM MCD-2 MC (A2L) sinh từ `calibration.yaml`, để công cụ tune đọc và ghi qua ASAM XCP trong lúc chạy; planner kiểm giới hạn mỗi khi bộ calibration đổi | Phụ thuộc nền tảng đích; XCP thuộc nền tảng, không thuộc planner |
| V3 | V1, cộng sinh file mô tả A2L từ `calibration.yaml` để nền tảng dùng khi cần V2 | Planner không phụ thuộc XCP |

## 3. Cách đánh giá

Chưa khóa. Tiêu chí đề xuất: không đổi output của bộ calibration giao (golden khớp từng bit), kiểm giới hạn từ chối mọi giá trị ngoài mục 7 (unit test), không cấp phát động, thời gian khởi tạo không tăng đáng kể. Không cần chạy benchmark ngoài golden và smoke.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

## 6. Đề xuất

2026-11-23: đề xuất V3. V1 đủ cho tune trên xe giữa các lần khởi động, không buộc planner vào một nền tảng; file A2L sinh kèm cho phép nền tảng làm V2 khi đã chọn ECU. Chọn V3 thì viết ADR mới thay phần calibration của PP-ADR-013 và sửa Interface Control Document.

## 7. Quyết định
