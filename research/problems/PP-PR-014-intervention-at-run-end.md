# PP-PR-014 Ca dừng giữa lần can thiệp cuối

| Mục | Nội dung |
|---|---|
| Trạng thái | Bỏ; PP-SWR-083 obsolete (PP-TS-016) |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | PP-SWR-083 |
| Tái hiện | S4(d, e), seed 1. Lần can thiệp mới bắt đầu sau các lần đã COMPLETED, sát lúc kết thúc mô phỏng |

## 1. Hiện tượng

Eval gán thời lượng vô hạn cho lần can thiệp đang ACTIVE khi log dừng. Ca trượt PP-SWR-083 dù cửa sổ quan sát của lần này chưa tới giới hạn 10 s.

## 2. Nguyên nhân

Phép chấm gộp hai trường hợp: vẫn ACTIVE sau giới hạn thời gian và log dừng trước khi tới giới hạn.

## 3. Cách sửa

Chấm các lần có kết thúc quan sát được hoặc đã qua hạn. Báo thời lượng đã quan sát của lần cuối nếu log dừng trước hạn. Một ca được định trước cần can thiệp phải có ít nhất một lần đủ cửa sổ để chấm thời lượng.

## 4. Xác nhận

Unit test với lần đầu kết thúc đúng hạn và lần kế tiếp còn ACTIVE khi log dừng. Unit test với ACTIVE quá hạn. Chạy lại các neo bằng cùng bộ đầu vào.

PP-SWR-083 obsolete theo PP-TS-016; bên chấm không còn tiêu chí thời lượng can thiệp. [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md) không có lỗi bên chấm.
