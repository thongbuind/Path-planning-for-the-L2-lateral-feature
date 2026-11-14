# PP-TS-012 Đưa v_y về t0 khi kiểm điều kiện kết thúc

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, cài V1 để kiểm |
| Mở ngày | 2026-11-12 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-PR-018, PP-SWR-032, 090 |

## 1. Câu hỏi

Planner nên đồng bộ v_y và hình học tại t0 bằng cách nào khi xét COMPLETED?

## 2. Phương án

| ID | Phương án | Hệ quả |
|---|---|---|
| V0 | Dùng trực tiếp mẫu VehicleStateEstimate hợp lệ gần nhất | Độ lệch thời gian gây sai ở ngưỡng v_lat |
| V1 | Ngoại suy v_y đến t0 từ hai stamp gần nhất | Dùng tín hiệu sẵn có. Có thể khuếch đại nhiễu và chỉ áp trong cửa sổ tuổi mẫu của interface |
| V2 | Tích phân gia tốc ngang từ IMU với vận tốc, yaw rate và vị trí CG | Cần kiểm ảnh hưởng độ nghiêng, bias gia tốc và nhiễu khi lấy đạo hàm yaw rate |

## 3. Cách đánh giá

Đo sai lệch thời điểm đạt điều kiện kết thúc bằng ground truth. So cùng S4, S5 và cùng seed, giữ calibration. Kiểm riêng đoạn có gió và độ nghiêng.
