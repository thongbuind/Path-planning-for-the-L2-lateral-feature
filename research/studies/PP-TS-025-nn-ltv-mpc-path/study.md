# PP-TS-025 NN và LTV-MPC cho path generation (T7)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-18 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-TS-003 (T7 C QP), PP-TS-013, PP-TS-024; PP-SWR-003, 004, 006, 015, 016, 051, 100; PP-ADR-013; PP-ASM-019 |

## 1. Câu hỏi

- Quyết định cần đưa ra: NN có giúp T7 C đạt chất lượng path của QP mặc định với ít vòng ADMM và thời gian thực thi thấp hơn không. V0 Quintic cho biết chi phí và chất lượng của baseline giao.
- T7 C hiện là LTV-MPC ở cấp lập path. Nó giải lại một QP nén theo jerk trên 30 bước 0,1 s. Gia tốc ngang dự báo được tuyến tính hóa với q = 1 − κ·d lấy từ path cũ hoặc path jerk bằng 0. Biên thay đổi theo tốc độ và độ cong từng bước. QP dùng biến nới hành lang và kiểm tính hữu hạn khi kết thúc số vòng cố định. [T7 C](../../../planner/src/generators/qp.c)
- T7/T11 xuất `Trajectory` cho Lateral Controller. Mọi phương án dùng T10, T4, T10 như [TS-024](../PP-TS-024-driver-model-path/study.md#3-cách-đánh-giá-khóa-trong-planyaml). Hồ sơ đánh giá phải kiểm path trước/sau T10 và chuyển động xe. Việc ghi NN trong hồ sơ an toàn cần xem các nguồn ISO 21448 và ISO/PAS 8800 trước khi trích điều khoản.

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Quintic T7 A, calibration mặc định | `PP_T7=quintic` | Cùng V0 của TS-024 |
| V1 | QP T7 C, 150 vòng và warm start hiện tại | `PP_T7=qp` | Cùng VQ của TS-024 |
| V1r | Cùng QP V1 với ngân sách vòng của V2 | `PP_T7=qp`, `qp_iters` | Đo lợi ích do giảm vòng khi không thêm NN |
| V2 | NN khởi tạo riêng 30 jerk cho ADMM, giữ cùng QP và số vòng với V1r | `PP_T7=qp_nn_warmstart` | Thí nghiệm ưu tiên |
| V3 | NN chỉnh `qp_w_jerk`, `qp_w_dev`, `qp_a_comfort`, giải 150 vòng | `PP_T7=qp_nn_weights` | So với QP chỉnh trọng số cố định trên cùng tuning |
| V4 | NN dự đoán jerk, tích phân từ trạng thái đầu rồi dùng hậu xử lý chung | `PP_T7=nn_direct` | Đối chứng về chi phí và chất lượng ứng viên |

1. **V2, giữ nguyên bài toán QP.** ADMM hiện giữ x, y và rho từ chu kỳ trước, tính lại z theo biên mới. NN chỉ thay khối jerk của x, giữ cơ chế hiện tại cho các khối còn lại. Kẹp jerk về biên theo bước, rồi tính z bằng đúng quy trình hiện có. Với đầu ra lỗi, dùng điểm khởi tạo của V1r. Nếu thiếu lịch sử, ghi riêng kết quả chu kỳ khởi động lại và các chu kỳ ổn định. Giữ nguyên hệ số rho và quy tắc factorization khi so cùng số vòng. [Sambharya và cộng sự, 2024](https://jmlr.org/papers/v25/23-1174.html) · [Mã khởi tạo ADMM](../../../planner/src/generators/qp.c)
2. **Đầu vào của NN.** Dùng trạng thái đầu, đích và profile v, κ, dκ trên lưới. Mã hóa biên gia tốc/jerk, hành lang, phần quan sát, mask và các điểm path cũ. Cùng v, κ và d ban đầu vẫn có thể tạo bài toán QP khác nhau khi hành lang hoặc path cũ thay đổi. Đóng băng chuẩn hóa theo dữ liệu huấn luyện, kích thước MLP và trọng số C `const`.
3. **Nhãn và phân tập.** Dùng lời giải QP cùng mô hình, trọng số và constraint, xác nhận residual và mức vi phạm constraint trước khi lấy nhãn. Ghi riêng mẫu bất khả thi hoặc không hội tụ. Chia train/validation theo họ hình học đường và cấu hình nhiễu, trước khi trích cửa sổ. Dùng bộ sinh riêng cho train, seed từ 100, tốc độ đến 100 km/h và VP-0/1/2. Giữ toàn bộ ca, anchor và biến thể của PP-T7 ngoài train, gồm vùng kiểm ngoài miền có tốc độ từ 110 km/h và VP-3/5. Dùng tuning để chọn cấu hình rồi cố định trước khi chấm test.
4. **Thứ tự thực hiện.** Thử V1r trước tại 50/75/100/150 vòng trên tuning. Chạy V2 trên đúng lưới đó. Nếu QP giảm vòng tự đạt mục tiêu, V2 chỉ có giá trị khi cải thiện thêm. Với V3, chốt khoảng hữu hạn cho từng trọng số và kiểm cả phần tối ưu bị tác động. Với V4, ghi riêng các chu kỳ cần T10 sửa mạnh, vượt hành lang hoặc mất liên tục. Ưu tiên hoàn thành V2 trước khi chi ngân sách huấn luyện cho V3/V4.

## 3. Cách đánh giá (khóa trong plan.yaml)

| Mục | Nội dung |
|---|---|
| Bộ so sánh chung | [PP-T7](../../../benchmark/suites/PP-T7.yaml) và cách ghép, cửa loại, xếp hạng của TS-024. Dùng lại lượt chạy vòng hở/kín của V0 và V1 giữa hai study chỉ khi cùng mã nguồn, calibration, suite và môi trường. Khi đo thời gian, chạy lại cùng phiên đo. |
| Chất lượng solver | Trên cùng đầu vào vòng hở, đo residual primal/dual cuối, vượt giới hạn a_y/jerk, slack corridor, độ lệch d so với nghiệm tham chiếu hội tụ và chênh objective. So V2 với V1r ở cùng số vòng. Đo tần suất T10 đổi path và mức đổi theo d, a_y, jerk trước/sau T10. |
| Chất lượng path | So V2 với V1 và V0 trên mọi yêu cầu áp dụng và các chỉ số chung. Báo riêng khởi động lại, cua vượt khả năng hỗ trợ, tầm nhìn ngắn, FOLLOW, các profile và dải tốc độ ngoài train. Lưu số chu kỳ thực sự được chấm cho mỗi chỉ số. |
| Thời gian tính | Đo p50/p95/p99/max riêng cho `pp_lcc_step`, gồm suy luận NN và hậu xử lý, cùng máy, cùng concurrency. Mục tiêu nháp: trung vị tỉ số p99 theo cặp V2/V1 trên test vòng kín ≤ 0,90, đồng thời đạt requirement và giữ chất lượng path trong dung sai của plan. Chạy xen kẽ thứ tự build khi đo lại để kiểm độ ổn định. PP-SWR-015 kiểm trường thời gian từng chu kỳ. PP-SWR-016 dùng để xếp hạng. |
| Ngân sách | Tối đa 4 mức vòng cho V1r/V2. Thử trước MLP hai lớp ẩn × 32 nút, tối đa 10.000 cửa sổ huấn luyện và 20 epoch. Chốt kích thước, số cấu hình và số update chung trước khi thử V3/V4. Dùng cùng giới hạn 9 bộ calibration cho các đối chứng có chỉnh trọng số như TS-024. |
| Truy vết | Ghi hash của danh sách train/validation, teacher và calibration, bộ chuẩn hóa, seed, cấu hình huấn luyện, tệp trọng số và mã C sinh ra. Bản test dùng một bộ trọng số cho mọi profile và seed. Chốt số vòng V1r/V2 và ngưỡng residual trên tuning trước khi mở test. |

Chỉ số p99 và các metric cuối path có trong dữ liệu ghép cặp của `eval.study`. Thêm telemetry nghiên cứu vào T7/T10 khi cài V2 để ghi residual, slack, thời gian suy luận riêng, số vòng, lý do dùng warm start cũ và mức sửa của mỗi lần T10.

## 4. Lần chạy

Chạy dò các đối chứng trên tuning bằng `python3 -m eval.study PP-TS-025 --part tuning --variant V0 --variant V1 --variant V1r --jobs 1`. Lần dò V1r dùng 75 vòng từ plan nháp. So thêm 50, 100 và 150 vòng trên tuning trước khi chọn ngân sách để chấm V2.

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

### Bằng chứng hiện có

PP-TS-003 cho thấy QP 150 vòng đưa xe về giữa nhanh hơn Quintic ở S2d, 2,22 s so với khoảng 3,10 s. Đỉnh a_y thêm vào ở ca này cao hơn khoảng 0,045 m/s². QP phải chứng minh lại chất lượng và thời gian trên bản LCC hiện tại. TS-025 chưa có số đo về lợi ích của NN. [Kết quả từng lượt PP-TS-003](../../runs/20261114-1934-study-PP-TS-003-272a711/results.json)

## 6. Đề xuất

Đo V0/V1 trên bộ chung, sau đó đo V1r để tìm ngân sách vòng nhỏ nhất giữ chất lượng trên tuning. Chỉ ưu tiên V2 nếu còn khoảng cải thiện về residual hoặc thời gian. Chốt tiêu chí residual, mô hình và ngân sách huấn luyện trước khi đưa V2 vào test.

## 7. Quyết định

- Người quyết, ngày:
- Chọn:
- Lý do:
- Đưa vào: PP-ADR-…, SDD mục 10, calibration …, SRS …
- Hồi quy: run ID
