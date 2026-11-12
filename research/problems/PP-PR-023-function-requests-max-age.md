# PP-PR-023 Q3 ở 60 ms vượt tuổi tối đa của FunctionRequests

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | PP-SWR-038, 145; Interface Control Document 4 (tuổi tối đa 45 ms) |
| Tái hiện | [20261112-1419-matrix-Q3-5e8cabc](../runs/20261112-1419-matrix-Q3-5e8cabc/summary.md), VP-0, seed 1 |

## 1. Hiện tượng

| Trễ FunctionRequests [ms] | S4a (LKA) | S5a (ELK) | S2b (HWA) |
|---|---|---|---|
| 1, 20, 40 | Can thiệp | Can thiệp | HWA lái |
| 60 | Không can thiệp, ca báo thiếu REQUEST đến planner | Như S4a | HWA không lái |

## 2. Nguyên nhân

- Interface Control Document 4 đặt tuổi tối đa của FunctionRequests là 45 ms (`FUNCTION_REQUESTS_MAX_AGE_US`). Ở 60 ms mọi message tới planner đều quá tuổi, planner coi input không hợp lệ.
- Planner làm đúng interface. Mức 60 ms của Q3 (Software Qualification Test Specification 6.1) nằm ngoài interface, và không requirement nào của SRS nói planner phải làm gì khi FunctionRequests quá tuổi nhưng chưa quá timeout 75 ms (PP-SWR-145).
- PP-ASM-006 giả định trễ khoảng 20 ms.

## 3. Cách sửa

Cần quyết định:

| Hướng | Nội dung |
|---|---|
| A | Giữ 45 ms. Thêm requirement cho FunctionRequests quá tuổi; Q3 60 ms thành ca kiểm planner từ chối input, chấm theo requirement đó |
| B | Nới tuổi tối đa trong Interface Control Document lên trên 60 ms (cần lý do; giới hạn trên là timeout 75 ms) |
| C | Bỏ mức 60 ms khỏi Q3 |

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
