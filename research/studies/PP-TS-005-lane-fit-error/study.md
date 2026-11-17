# PP-TS-005 Sai số khớp đa thức của lane model (T2, T5)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; plan nháp chờ duyệt (cập nhật 2026-11-16: thêm V3 và bước chuẩn bị) |
| Mở ngày | 2026-11-11 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-PR-004; PP-SWR-051, 100, 125; PP-ADR-007; SOTIF TC-11; García-Fernández và cộng sự 2014 (Chalmers, `docs/reference/standards/`) |

## 1. Câu hỏi

- Quyết định cần đưa ra: planner xử lý thế nào khi đa thức bậc 3 của lane model sai có hệ thống (không phải nhiễu) ở hai đầu cửa sổ khớp, như trên cua chữ S của R171.
- Vì sao cần: PP-PR-004, độ cong tại xe sai cả dấu.

Sai số đi qua bốn tầng; ba tầng sau thuộc planner:

| Tầng | Hiện làm gì | Vì sao sai trên cua chữ S |
|---|---|---|
| Lane model (interface) | Một đa thức bậc 3 trên 0–80 m cho mỗi vạch | Bậc 3 chỉ có một lần đổi dấu độ cong; sai lớn nhất ở hai đầu cửa sổ khớp, gồm cả tại xe |
| T1, T2 | Mỗi frame khớp lại một đa thức; bộ nhớ biên chỉ dùng để kiểm nhất quán | Điểm đang ở x = 0 từng nằm giữa cửa sổ, nơi khớp chính xác nhất; thông tin đó bị bỏ |
| T5 | Nhớ độ cong theo s, rồi khớp lại κ = a + b·x và thay c2, c3 | Lại thành một clothoid; c0, c1 vẫn của frame hiện tại nên hình dạng không khớp nhau |
| T7, T10, T11 | Đọc `pp_cubic_t` qua `pp_ref_walk`, `pp_ref_project` | Reference line tốt hơn một đa thức không truyền được xuống dưới |

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Bản hiện tại: T5 tin camera như nhau trên cả tầm nhìn | — | Mốc |
| V1 | T5: phương sai đo của camera tăng ở hai đầu cửa sổ khớp (gần xe và cuối tầm nhìn); điểm gần xe chủ yếu lấy từ lần quan sát trước, khi điểm đó còn ở giữa cửa sổ, dời theo ego-motion | Build-time | Ít thay đổi; vẫn chỉ nhớ độ cong |
| V2 | Bộ nhớ điểm vạch: giữ các điểm vạch đã quan sát (lấy mẫu từ đa thức ở giữa cửa sổ), dời theo ego-motion, khớp lại reference line từ bộ nhớ và lần đo mới | Build-time | Đối chứng cho V3; tốn bộ nhớ cố định hơn |
| V3 | Bộ ước lượng đường: trạng thái là lệch ngang d₀, hướng ψ₀ tại xe và độ cong κ₁…κ_M trên lưới 2 m theo s; ước lượng chung cả ba từ các frame | Build-time | Thêm 2026-11-16; mô hình của García-Fernández và cộng sự (2014) |

- V1: bỏ ngày 2026-11-16 trước khi cài, người dùng duyệt. Lý do ở mục 5 (nguyên mẫu): hướng tại xe vẫn lấy từ c1 của frame hiện tại. ID V1 không dùng lại.

**Bước chuẩn bị, chung cho V2, V3 (không phải phương án; người dùng duyệt làm ngày 2026-11-16).** Reference line có thêm cách biểu diễn thứ hai sau `pp_ref_walk`, `pp_ref_project`:

| Phần | Cách làm |
|---|---|
| Mảng mẫu | `pp_ref_nodes_t` trong `pp_reference_line_t`: nút theo s, bước 2 m, từ 80 m sau xe tới cuối tầm nhìn (tối đa 120 nút): x, y, θ, κ, dκ/ds. Nút cuối là điểm cuối tầm nhìn |
| Đọc | Giữa hai nút nội suy Hermite; ngoài nút cuối nối cung tròn như đường đa thức. T4, T7, T8, T10, T11 không đổi vì chỉ đọc qua hai hàm trên |
| Bản mặc định | `sampled = false`: hình học vẫn là đa thức, kết quả giữ nguyên từng bit |
| Công tắc build `PP_REF_SAMPLED` | T2, T5 và reference line mép đường của ELK điền mảng mẫu từ đa thức (`pp_ref_sample_cubic`) và mọi module đọc qua mảng. Dùng để đo mảng mẫu có tương đương đa thức không, trước khi V2, V3 điền mảng bằng cách khác |
| Khác biệt đã biết khi bật công tắc | Chiếu một điểm nằm sau cuối tầm nhìn: mảng mẫu chiếu lên cung nối, đa thức chiếu lên đa thức kéo dài. Ảnh hưởng tới việc gán làn cho vật thể xa hơn tầm nhìn (T8) |

Xác nhận:

- Unit test C (2026-11-16, cây làm việc chưa commit): 15/15 đạt ở cả hai bản build. Mảng mẫu khớp đa thức trong 5 µm vị trí, 10⁻⁷ rad hướng, 10⁻⁸ 1/m độ cong, từ 75 m sau xe tới cuối tầm nhìn.
- Hồi quy SIL với công tắc bật so với công tắc tắt: chưa chạy.

**Thiết kế của V3.**

| Phần | Cách làm |
|---|---|
| Trạng thái | d₀, ψ₀, κ₁…κ_M (khoảng 50 ẩn), hiệp phương sai đầy đủ trong vùng nhớ của bên gọi |
| Dự báo mỗi chu kỳ | Dời lưới theo quãng đường đã đi; cập nhật d₀, ψ₀ bằng ego-motion; phương sai κ tăng theo quãng đường |
| Phép đo, mỗi frame mới | Mỗi biên đủ tin cho các điểm lấy mẫu từ đa thức, đã dời về tâm làn. Phương sai = phần lane model báo + phần tăng ở hai đầu cửa sổ khớp |
| Prior | Độ cong đổi chậm theo s (độ lệch chuẩn của hiệu κ giữa hai ô kề nhau), thay cho giả định một clothoid |
| Cổng kiểm | Điểm đo lệch dự báo quá `k_jump`·σ thì giảm trọng số, như T5 hiện nay |
| Xoá bộ nhớ | Khi `lane_change`, khi T2 nhận thay đổi thật của làn, khi mất ego-motion |
| Output | Mảng mẫu của bước chuẩn bị. Cờ và `v_max` vẫn lấy độ cong lớn hơn giữa camera và ước lượng (T10) |
| Thay thế | T5 và phần reference line nhớ được của T2 (bám reference line cũ thành bước dự báo của cùng trạng thái) |

Calibration mới của V3: mức tăng phương sai ở đầu cửa sổ, độ lệch chuẩn của thay đổi κ theo s, độ dài nhớ. Chưa có nguồn cho con số thứ hai (tiêu chuẩn thiết kế đường); để calibration và quét.

Ảnh hưởng tới quyết định đã có: PP-ADR-007 chọn không lọc lại cảm biến trong planner. V2 và V3 đi ngược một phần; nếu được chọn thì cần ADR mới thay thế.

## 3. Cách đánh giá

Bản nháp ngày 2026-11-14, chưa khóa: [plan.yaml](plan.yaml), suite `benchmark/suites/PP-TS-005.yaml`.

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | PP-SWR-051, 100 đến 102 và requirement trong phạm vi của suite |
| Xếp hạng | Software Qualification Test Specification mục 9 |
| Bộ chỉnh | Cua chữ S R = 500 m (S1 d), S1 b, S1b a, F01, F06, F02 trên S1, F08 b trên S1 d; seed 1, 2 |
| Bộ kiểm | Cua chữ S của R171 (S1 f, S14 e hai chế độ ACC), S1 g, S1 c, S1 e, S1b b, c, S14 a, tầm nhìn 40 m, F01, F06, F02, F08 b trên S1 f; seed 3, 4 |
| Đo thêm | Thời gian tính mỗi chu kỳ (target PP-SWR-016) và `pp_state_size()` của từng phương án |
| Ngân sách chỉnh | Như nhau cho mọi phương án; ghi khi V1, V2 đã cài, trước khi khóa |
| Liên quan khác | V1, V2, V3 sửa T2, T5; cài sau khi PP-PR-030 (bước 4 của T2) đã vào nhánh chính để không sửa chồng |

F08 b (bias yaw rate 0,3 °/s) thêm ngày 2026-11-16, trước khi có lần chạy nào: bộ nhớ dời bằng ego-motion nên trôi theo bias. Đặt trên cua chữ S, không đặt trên S1 c, để không lẫn với PP-PR-049.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

**Nguyên mẫu hình học (nháp 2026-11-16, chỉ để chọn phương án đáng cài, không dùng để quyết định).** [prototype.py](prototype.py): tâm làn của `S14e.xodr`, 28 m/s, camera 20 Hz khớp đa thức trên 0–80 m như `sim/sensors/lane_camera.py`. Không nhiễu, xe ở tâm làn, không có planner hay simulator. Bỏ 1,4 s đầu (bộ nhớ còn trống). Sai a_y = v²·sai độ cong.

| Cách dựng reference line | Lệch vị trí lớn nhất, 0–30 m | Sai độ cong tại xe lớn nhất | Sai a_y | Với bias yaw rate 0,3 °/s |
|---|---|---|---|---|
| V0, đa thức của frame hiện tại | 0,12 m | 0,0031 1/m | 2,4 m/s² | Không đổi |
| V1 | 0,76 m | 0,0006 1/m | 0,46 m/s² | Không đổi |
| V2, khớp bậc 2 cục bộ, nhớ 3 s | 0,06 m | 0,0010 1/m | 0,78 m/s² | 0,11 m; 0,0013 1/m |
| V1 cho độ cong, V2 cho lệch và hướng tại xe | 0,11 m | 0,0006 1/m | 0,46 m/s² | 0,27 m |
| V3, nhớ 3 s | 0,04 m | 0,0004 1/m | 0,29 m/s² | 0,10 m; 0,0008 1/m |

- V1: độ cong tốt, nhưng hướng tại xe lấy từ c1 của frame hiện tại; tích phân 30 m cho lệch 0,76 m.
- Ước lượng rời rồi ghép (dòng 4) kém hơn ước lượng chung (V3): lệch, hướng và độ cong phải khớp nhau.
- Không cách nào khôi phục được đỉnh của cung ngắn 5,1 m: đa thức của camera đã làm mượt nó.
- Bias 0,3 °/s đưa lệch vị trí của V3 từ 0,04 lên 0,10 m với bộ nhớ 3 s. Điểm ở x = 0 nằm giữa cửa sổ 1–1,5 s trước đó, nên độ dài nhớ thuộc dải quét.
- Mô phỏng thô của T5 hiện tại (khớp lại κ = a + b·x, giữ c0, c1) cho lệch vị trí 0,49 m, lớn hơn V0. Chưa đối chiếu với log của planner; cần xác nhận khi chạy V0.
- Chưa xét: nhiễu F01 (prior có làm chậm lúc vào cua thật không), sai số khi xe lệch tâm, thời gian tính.

## 6. Đề xuất

- 2026-11-16, trước khi cài: làm bước chuẩn bị; cài V3 làm phương án chính và V2 làm đối chứng; bỏ V1. Người dùng duyệt cùng ngày. Plan khóa sau khi V2, V3 đã cài và có bộ calibration của từng phương án.

## 7. Quyết định
