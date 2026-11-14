# PP-TS-011 Pha LKA và ELK trong PathStatus

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã quyết |
| Mở ngày | 2026-11-12 |
| Khóa ngày | — |
| Quyết định ngày | 2026-11-12 |
| Liên quan | PP-ADR-015, PP-SWR-032, 033, 041, Interface Control Document mục 6.2 |

## 1. Câu hỏi

PathStatus biểu diễn ELK COMPLETED và LKA ACTIVE tại cùng một tick thế nào?

## 2. Phương án

| ID | Phương án | Hệ quả |
|---|---|---|
| V0 | Một pha chung đi cùng `active_function` | Một trường pha chỉ có thể công bố một trong hai trạng thái. Bên nhận có thể rút nhầm LKA nếu ghép COMPLETED với LKA |
| V1 | Hai pha `lka_phase` và `elk_phase` | Bên nhận xác định được trạng thái của từng yêu cầu. Schema và ABI thay đổi |

## 3. Cách đánh giá

Kiểm cùng một output có ELK COMPLETED, LKA ACTIVE, sau đó xóa đúng pha ELK khi state ELK rời REQUEST.

## 7. Quyết định

Người dùng chọn V1 theo quyền sở hữu của từng yêu cầu. PP-ADR-015 ghi hợp đồng.
