# PP-TS-027 Giới hạn tổng lệnh lái của HWA

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, bộ ca và runner nháp sẵn sàng cho V0. V1 và V2 chờ duyệt triển khai |
| Mở ngày | 2026-11-23 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-SWR-001, 003, 005, 006, 007, 051, 100–102. [PP-PR-056](../../problems/PP-PR-056-s1bb-vehicle-ay-above-r79.md). [PP-TS-020](../PP-TS-020-path-ay-ceiling/study.md) |

## 1. Câu hỏi

- Giới hạn tổng lệnh lái HWA ở Lateral Controller theo cách nào để gia tốc ngang đo trên xe đạt tiêu chí hiện hành và xe vẫn bám làn khi đủ điều kiện giữ làn?
- Ở S1b(b), hồi quy [591e3de](../../runs/20261122-0758-suite-regression-591e3de/report.md) ghi đỉnh a_y của path 2,50 m/s² và đỉnh a_y đã lọc của xe 4,09 m/s². Lateral Controller cộng feedforward với phản hồi lệch ngang và lệch hướng trước khi gửi lệnh sang EPS.
- Phạm vi là điều khiển HWA trong SIL, từ Trajectory tới Lateral Controller, EPS và mô hình xe. Dùng cùng bản build planner, EPS, ACC và arbitrator cho mọi phương án. PP-TS-020 tiếp tục theo dõi câu hỏi về trần a_y của path.

## 2. Phương án

| ID | Phương án | Cách thử trong SIL | Điểm cần đo |
|---|---|---|---|
| V0 | Tổng lệnh lái hiện tại | Giữ feedforward, phản hồi lệch ngang và lệch hướng, cùng giới hạn góc lái của xe | Mốc gia tốc xe và chất lượng bám làn |
| V1 | Giới hạn tĩnh tổng lệnh | Dùng tốc độ và quan hệ lái ổn định đang dùng cho feedforward để quy đổi giới hạn a_y liên tục thành khoảng góc lái. Chiếu tổng lệnh vào khoảng này trước giới hạn góc lái của xe | Gia tốc xe khi chuyển tiếp, DLC và sai số bám path khi lệnh bão hòa |
| V2 | Giới hạn tổng lệnh theo dự báo đáp ứng | Từ trạng thái xe mà controller nhận và độ trễ EPS của profile, dự báo a_y do tổng lệnh gây ra. Giữ cùng mục tiêu a_y liên tục với V1 khi chọn lệnh khả thi gần lệnh gốc nhất | Lợi ích so với V1 khi tốc độ, độ cong hoặc phản hồi đổi nhanh. Độ nhạy với profile và sai số tín hiệu |

Giới hạn của V1 và V2 chỉ áp khi lệnh của LCC đang có hiệu lực. Giữ xử lý sẵn có khi driver override, đổi nguồn path hoặc LKA/ELK lái. Các phương án dùng tín hiệu controller nhận lúc chạy và tham số profile đã có. Ground truth chỉ dùng để chấm.

**Cấu hình đề xuất cho lần chạy đầu:**

- V1 dùng `delta_max = (L + K·v²)·2,8/v²` cho biên góc bánh trước. `L` và `K` lấy như feedforward hiện tại. Kết hợp biên này với giới hạn góc bánh của xe. Khi `v = 0`, dùng giới hạn góc bánh sẵn có.
- V2 dự báo từ `v·yaw_rate` và các lệnh controller đã gửi trong khoảng trễ EPS. Dùng đáp ứng bậc nhất với tham số EPS hiện có. Sau độ trễ, chọn tổng lệnh gần lệnh gốc nhất sao cho dự báo tới hết cửa sổ preview nằm trong khoảng ±2,8 m/s². Khi trạng thái ban đầu đã vượt mục tiêu, giới hạn phần lệnh có thể làm a_y tăng thêm theo hướng đang vượt và ghi thời gian trở lại giới hạn.
- Cả hai dùng 2,8 m/s² làm mục tiêu của lệnh. Kết luận vẫn dùng a_y xe đã lọc, cả đỉnh và thời gian vượt, theo phép chấm hiện hành.

## 3. Cách đánh giá

Kế hoạch nháp nằm trong [plan.yaml](plan.yaml). Bộ ca [PP-TS-027](../../../benchmark/suites/PP-TS-027.yaml) có 22 lượt chỉnh và 28 lượt kiểm trên mỗi phương án. Khóa danh sách ca, seed, tiêu chí loại và ngân sách chỉnh sau khi duyệt.

| Mục | Nội dung |
|---|---|
| Phép chấm giữ nguyên | Giữ PP-SWR-001 hiện hành và các điều kiện áp dụng trong bộ chấm. Đọc tiêu chí a_y xe qua `PP-TS-020/R79-5.6.2.1.1` đang có ở các ca S1b dùng để kiểm giới hạn a_y xe. Giữ bộ lọc, ngưỡng và cửa sổ thời gian hiện hành |
| Tiêu chí loại | Ca tái hiện S1b(b) phải đạt tiêu chí a_y xe. Đối chiếu mọi requirement áp dụng trong bộ kiểm, đặc biệt PP-SWR-001, 005–007, 051, 100–102. Ghi cả lỗi có sẵn ở V0 và lỗi mới. Lỗi có sẵn còn tồn tại thì kết luận phương án vẫn còn trượt |
| Bộ chỉnh và bộ kiểm | Dùng lại ca, profile và seed 1–2 / 3–4 của [bộ PP-TS-020](../../../benchmark/suites/PP-TS-020.yaml). Ca S1b(b) với ACC `ignore_limits` ở bộ kiểm. Dùng ca F08(c), G01 trên S1c và các ca chuyển quyền S9, S17 đã có trong hồi quy để xác nhận sau khi chọn |
| Ngân sách chỉnh | Đề xuất không quét tham số ở vòng đầu. V1 và V2 dùng cùng mục tiêu a_y liên tục và tham số xe có sẵn. Nếu cần chỉnh, duyệt cùng ngân sách cho hai phương án trước khi chạy |
| Xếp hạng | Dùng thứ tự SQTS mục 9. So theo ca, profile và seed. Báo riêng đỉnh a_y xe, thời gian vượt ngưỡng liên tục, DLC trong phạm vi chấm, sai số bám path, jerk và tỷ lệ chu kỳ bão hòa. Chỉ số chẩn đoán không đổi kết luận đạt/trượt |
| Coi như ngang nhau khi | Dùng mức chênh của PP-TS-020 cho PP-SWR-050 (0,005 m) và PP-SWR-051 (0,01 m). Mức chênh chỉ dùng để xếp hạng |

Runner nháp `eval.controller_study` chọn controller theo phương án và kiểm hash của cả hai thư viện planner từ hồi quy `591e3de`. Manifest ghi cấu hình, hash mã controller và đầu vào. Mỗi kết quả giữ hash ca, checksum hành vi, phạm vi chấm, tiêu chí và chỉ số gốc. Ca đối chứng của PP-SWR-129/130 dùng cùng controller với ca bơm lỗi.

Xem danh sách ca bằng `python3 -m eval.controller_study PP-TS-027 --list`. V0 sẵn sàng chạy nháp. V1 và V2 có cấu hình dự kiến và sẽ được đăng ký khi cài đặt. Trước lần chạy chính thức cần chốt cách build một lần trên commit đã khóa, dùng lại hai thư viện đó cho toàn bộ phương án và giữ quy tắc provenance của dự án.

Chạy nháp riêng S1b(b), seed 3, với hai thư viện đã đóng băng:

```bash
python3 -m eval.controller_study PP-TS-027 --planner build/p0/planner \
  --variant V0 --part test --case 2 --seed 3 --out build/study/PP-TS-027/v0-check
```

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

## 6. Đề xuất

## 7. Quyết định

- Người quyết, ngày:
- Chọn:
- Lý do:
- Đưa vào:
- Hồi quy:
