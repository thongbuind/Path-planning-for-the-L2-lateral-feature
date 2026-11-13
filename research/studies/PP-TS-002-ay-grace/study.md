# PP-TS-002 Khoảng nới a_y 40 % trong 2 s của R79 (PP-SWR-001)

| Mục | Nội dung |
|---|---|
| Trạng thái | Chờ quyết định |
| Mở ngày | 2026-11-11 |
| Khóa ngày | 2026-11-11 (luật quyết định, mục 3) |
| Quyết định ngày | — |
| Liên quan | PP-SWR-001, 005, 006, 007, 064, 151; SG-01; SOTIF TC-04, TC-05; R79 5.6.2.1.1; R171 5.3.7.1.2 |

## 1. Câu hỏi

- Quyết định cần đưa ra: PP-SWR-001 có thêm khoảng nới của R79 5.6.2.1.1 không. R79 cho a_y đo trên xe vượt aysmax tới 40 % trong tối đa 2 s, không quá 3,3 m/s².
- Vì sao cần: cua hiện ra muộn (đỉnh dốc, clothoid ngắn) có thể đẩy xe ra khỏi làn nếu path bị cắt ngay về aysmax.

## 2. Phương án

| ID | Phương án | Ghi chú |
|---|---|---|
| V0 = A | Giữ PP-SWR-001: a_y của path ≤ aysmax = 2,5 m/s² mọi lúc | Đơn giản, an toàn hơn về a_y |
| V1 = B | Khoảng nới: a_y của path tới `ay_grace` = 3,0 m/s², mỗi khoảng ≤ `T_grace` = 1,5 s, cách nhau ≥ `T_grace_gap` = 2 s; cờ bật ngay khi mở khoảng nới | Giới hạn của `ay_grace`, `T_grace` lấy từ R79; `T_grace_gap` nhóm tự thống nhất. Phải ghi vào HARA vì PP-SWR-001 thuộc SG-01 |
| Không xét | Nâng mức liên tục lên aysmax + 0,3 | Ăn hết biên R79 dành cho sai số của controller |

## 3. Cách đánh giá

Luật quyết định, thống nhất ngày 2026-11-11, trước khi chạy:

- Làm ACC chạy thử (SQTS 4.7) trước; chạy S1b với ACC đọc LateralLimits trên mọi profile.
- ACC đủ giữ xe trong làn ở mọi biến thể: chọn A.
- Còn ca xe ra khỏi làn, nhất là ca thấy cua muộn: chọn B.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| 20261111-1024-matrix-M1-b9e5d4d | A | Đăng ký lại. S1b a, b, c, e và S14a; ACC `on` và `ignore_limits`; VP-0 đến VP-5; seed 1, 2 |

## 5. Kết quả

Lốp trước đè vạch: số lần chạy có ít nhất một lần lốp trước chạm vạch (cũng là điều kiện để chấm PP-SWR-007).

| Ca | ACC `ignore_limits` | ACC `on` | Tốc độ nhỏ nhất với ACC `on` | Báo trước với `ignore_limits` |
|---|---|---|---|---|
| S1b a (R = 200 m, 90 km/h) | 12/12 | 0/12 | 20,0 m/s | 2,4–2,5 s |
| S1b b (R = 150 m, 90 km/h) | 12/12 | 0/12 | 17,8 m/s | 2,5–2,6 s |
| S1b c (R = 300 m, 110 km/h) | 12/12 | 0/12 | 24,1 m/s | 2,0 s |
| S1b e (clothoid 60 m) | 12/12 | 0/12 | 18,9 m/s | 2,5 s |
| S14a | 12/12 | 0/12 | 20,0 m/s | 2,4–2,5 s |

- Không giảm tốc thì xe luôn đè vạch; ACC đọc LateralLimits thì không lần nào. Cờ báo trước 2,0–2,6 s là đủ để ACC giảm tốc.
- Theo luật ở mục 3, số liệu hiện có chọn A.
- Chưa có ca thấy cua muộn: S1b d (đỉnh dốc) chưa có trong simulator. Đây đúng là ca mà B nhắm tới.

## 6. Đề xuất

Chọn A cho BL1. Mở lại study khi S1b d có trong simulator; nếu S1b d với ACC `on` có xe ra khỏi làn thì chạy B.

2026-11-13: S1b d đã có trong `S1b.anchors.xosc` (camera thấy 40 m). Người dùng đồng ý chạy điều kiện mở lại trước khi chốt A: `benchmark/suites/PP-TS-002.yaml`, S1b d, ACC `ignore_limits` và `on`, VP-0 đến VP-5, seed 1, 2. Cùng luật ở mục 3.

## 7. Quyết định
