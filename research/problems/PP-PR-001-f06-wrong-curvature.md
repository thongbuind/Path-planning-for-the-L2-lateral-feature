# PP-PR-001 Độ cong sai ở xa (F06) làm xe ra khỏi làn

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, đã tìm nguyên nhân; sửa qua PP-TS-001 |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-051, 125 |
| Tái hiện | 20261111-1024-matrix-M1-b9e5d4d: S1a + F06a (4/4 lần chạy), S1c + F06e (4/4 lần chạy), ACC `on`, VP-0 và VP-5 |

## 1. Hiện tượng

Lane model báo c2 sai; xe đi theo cua giả và lốp đè vạch.

Lần chạy nháp `build/suites/smoke-20261111-1425` trên đường chủ S1c (cua chạm aysmax): F06 a, b, d, e làm xe ra khỏi làn; F06 b còn trượt PP-SWR-100 và 101, F06 e trượt PP-SWR-100.

## 2. Nguyên nhân

Hai nguyên nhân, đã thấy khi phân tích lần chạy nháp:

- Giới hạn liên tục PP-SWR-100 áp trên cả đoạn 0–3 s của path, nên path cũ (đúng) bị kéo theo path mới (sai) ngay cả ở đoạn gần.
- T5 nhận độ cong sai trong khoảng 1 s, vì phương sai của camera lúc đó vẫn nhỏ.

Kiểm lại 2026-11-13:

- PP-TS-014 không đổi ca này: ở 25 m/s, tầm nhìn 80 m phủ 3,2 s, dài hơn horizon 3 s.
- Giới hạn liên tục là ràng buộc của PP-SWR-100, không phải lỗi; nó làm chậm cả lúc theo path sai lẫn lúc quay lại.
- F06 là bước nhảy giữa hai frame: c2 thêm 0,0005 1/m làm điểm vạch ở 40 m dời 0,8 m, ở 80 m dời 3,2 m, trong 50 ms. Hình học thật không đổi như vậy. T2 hiện chỉ kiểm nhảy ở c0 (`k_jump`).
- Sai độ cong 0,001 1/m ở 25 m/s là sai 0,63 m/s² a_y.

## 3. Cách sửa

Đưa vào PP-TS-001 thay vì mở study riêng: kiểm nhảy trên cả đường cong (vị trí vạch ở vài điểm trong tầm nhìn, sau khi dời theo ego-motion), không chỉ c0. PP-TS-005 không sửa được ca này, vì F06 là lỗi đo chứ không phải sai số khớp có hệ thống. F06 d (kéo dài 2 s, quá `T_confirm`) có cùng giới hạn với F02e: cần tham chiếu độc lập (J2).

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
