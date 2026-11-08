# src — code phát triển thật

Thư mục này chứa code thật của path planner (Python prototype) và các đối tượng
giao tiếp, ví dụ kiểu dữ liệu mà Lateral Controller nhận.

## Trạng thái

Research về đề bài, chức năng ADAS, thiết kế planner, interface và benchmark đã gần xong. Dự án chuyển sang triển khai. Chưa có code.

Báo cáo Research trong `../docs/vi/` là nguồn chính thức. Bản đồ ở `../spec-web/` dẫn tới từng mục.

| Cần biết | Đọc |
|---|---|
| Planner phải đạt gì (yêu cầu có ID) | `docs/vi/yeu-cau-path-planner.md` |
| Planner chạy thế nào mỗi chu kỳ, cách đáp ứng yêu cầu | `docs/vi/thiet-ke-path-planner.md` |
| Kiểu dữ liệu, đơn vị, quy ước truyền | `docs/vi/interface-he-thong.md` |
| Ghi chú thuật toán, kỹ thuật ứng viên | `docs/vi/trien-khai-path-planner.md` |
| Simulator, kịch bản, chỉ số | `docs/vi/benchmark-evaluation.md` |

## Code bám theo yêu cầu

- Code chỉ hiện thực yêu cầu có trạng thái `đề bài`, `mentor` hoặc `đã chốt`. Phần dựa trên yêu cầu `đề xuất` hoặc `cần chốt` phải được đánh dấu là tạm trong code, kèm ID hoặc mục của yêu cầu đó.
- Hàm, hằng số hay test hiện thực một yêu cầu có ID thì ghi ID đó (ví dụ `PP-SWR-001`) trong docstring hoặc chú thích. Yêu cầu chưa có ID thì ghi tên tài liệu và số mục.
- Mỗi ngưỡng (aysmax, timeout, giới hạn jerk...) khai báo ở đúng một chỗ, kèm ID hoặc mục nguồn. Không viết số trực tiếp trong logic.
- Kiểu dữ liệu của interface định nghĩa một lần, theo `interface-he-thong.md`. Đổi interface thì sửa tài liệu trước, rồi mới sửa code.
- Code lệch với tài liệu thì phải báo, rồi sửa một bên theo quyết định. Không để hai bên lệch nhau.

## Planner tách khỏi bên đánh giá

Planner và benchmark phát triển độc lập (tài liệu Benchmark và Evaluation, mục 0). Trong code, nguyên tắc này thành quy tắc import:

- Code planner chỉ import kiểu dữ liệu của interface. Code planner không được import simulator, kịch bản, ground truth, seed hay cấu hình benchmark.
- Code đánh giá gọi planner chỉ qua interface: đưa input, nhận Trajectory và PathStatus, đo thời gian tính. Code đánh giá không được đọc biến nội bộ của planner.
- Unit test của planner được phép biết bên trong planner, nhưng không tính là benchmark.

## Cấu trúc thư mục (đề xuất)

```
src/
  interfaces/   kiểu dữ liệu của interface, dùng chung cho hai bên
  planner/      path planner; chỉ import interfaces
  eval/         simulator, mô hình cảm biến, lỗi bơm vào, kịch bản, chỉ số;
                import interfaces, gọi planner qua interface
  tests/        unit test của planner
```

Ràng buộc: Python thuần cộng numpy. Không dùng ROS 2 hay Docker.

## Tách với spec-web

- `spec-web/` chỉ để mô tả và thống nhất yêu cầu. Code ở đây không import gì từ `spec-web/`.
- `spec-web/` không đọc file nào trong `src/`. Khi một yêu cầu đã chốt, nó được viết lại thành code ở đây (dataclass, interface, test). Trạng thái quyết định vẫn ghi trong báo cáo Research.
