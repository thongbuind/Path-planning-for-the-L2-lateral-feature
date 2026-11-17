# Path Planner SIL, chạy thời gian thực

Web một khung để present Path Planner. Mỗi lần bấm **Chạy planner**, `libpp_planner` thật chạy trong simulator SIL của repo, mỗi 25 ms một lần `pp_step()` theo đồng hồ thật. Từng chu kỳ được đẩy lên web ngay khi tính xong. Thông số nhảy theo từng chu kỳ, biểu đồ hiện dần. Không có dữ liệu thu sẵn.

## Chạy

```bash
python3 -m workbench.server
```

Chạy từ thư mục gốc của repo, rồi mở http://127.0.0.1:8793/ (đổi cổng bằng `--port`). Cần Python có numpy, scipy, pyyaml (đã đủ nếu chạy được benchmark của repo) và `build/planner/libpp_planner.dylib` đã build. Trang không chạy khi mở thẳng file `index.html`, vì cần server.

Trang mô phỏng trong web tài liệu (`python3 web/serve.py`, http://127.0.0.1:8770/simulation/) dùng cùng workbench: `serve.py` chuyển tiếp `/simulation/api/*` qua HTTP, nên workbench phải đang chạy.

Nếu thiếu thư viện Python, cài các phụ thuộc dự án bằng `python3 -m pip install -r requirements.txt` trong môi trường Python sử dụng để chạy server.

## Dùng

| Phần | Làm gì |
|---|---|
| Tình huống | Toàn bộ 120 kịch bản của `benchmark/scenarios` (S1 đến S19), lọc theo chức năng, tìm theo chữ |
| Lỗi tiêm | 22 loại lỗi F01 đến F23 với mọi mức; chọn nhiều lỗi cùng lúc; tổ hợp có sẵn (G01 Đêm mưa); lỗi bắt đầu theo định nghĩa hoặc khi LKA, ELK can thiệp |
| Môi trường | Mặt đường ướt (μ 0,5), camera trễ 150 ms, nhiễu cảm biến vật thể ×1,5 |
| Xe, seed, ACC | VP-0 đến VP-5, seed 1 đến 999, chế độ ACC |
| Điều khiển | Tạm dừng và tiếp tục (Space), dừng, tốc độ 0,5×, 1×, 2×, tối đa. Khi đã tạm dừng hoặc chạy xong, kéo thanh thời gian hoặc bấm vào biểu đồ để xem lại |

Màn hình 2D nhìn từ trên xuống, xe hướng sang phải. Quỹ đạo 31 điểm (3 s) của planner đổi màu theo chức năng đang lái (HWA xanh, LKA cam, ELK lục). Vạch thật của đường vẽ xám, đúng kiểu sơn (liền, đứt 4 m vạch 8 m trống, kép, mép gờ liền, mép cỏ sỏi chấm thưa, và hình học riêng khi làn đổi bề rộng); vạch và mép đường mà lane model báo cho planner vẽ trắng, theo đúng `type` lane model báo (liền, đứt, kép, chưa rõ) và đứt cùng pha với vạch thật, đặt theo tư thế xe lúc camera chụp, nên thấy ngay nhiễu, mất vạch và dữ liệu cũ do lỗi tiêm gây ra. Tab **Kết quả** có số liệu đến thời điểm hiện tại, rồi tiêu chí và chỉ tiêu hiệu năng của evaluator khi lượt chạy kết thúc.

## Cách hoạt động

- `workbench/server.py`: tệp tĩnh của thư mục này và API lượt chạy (`/api/catalog`, `/api/runs`, `/api/runs/<id>/events`, `/control`, `/cancel`, `/files/<tên>`). Chỉ nghe ở 127.0.0.1.
- Lượt chạy thuộc về server, không thuộc về tab: đóng tab không dừng lượt chạy; mở lại trang thì nối tiếp lượt đang chạy. Dừng là hủy đúng lượt đó. Tối đa 2 lượt cùng lúc, lượt sau chờ.
- `eval/live.py`: worker của mỗi lượt. Dựng ca bằng `eval.case` như `eval.runner`, chạy `Harness` với observer: sau mỗi chu kỳ 25 ms lấy kết quả, chờ cho kịp đồng hồ thật rồi gửi một dòng JSON. Hết lượt chạy thì chấm bằng `eval.metrics`. Lệnh `catalog` đọc danh mục từ benchmark.
- Mỗi lượt để lại một bundle ở `build/runs/<run_id>/`: manifest, ca đã resolve, kết quả chấm, MCAP, luồng khung hình, log của worker, SHA256SUMS. Lượt lỗi vẫn để lại bundle, ghi trạng thái và lớp lỗi.
- Mô phỏng tất định theo seed: cùng cấu hình và seed thì cùng behaviour checksum như `eval.runner`, ở mọi tốc độ phát, kể cả khi tạm dừng. Riêng thời gian tính là đồng hồ thật của máy lúc chạy, nên có thể giật khi máy bận.
- Mã web nằm trong `web/simulation/` và không đọc mã nguồn; mọi thứ đi qua HTTP.

Ca trượt hiển thị đúng như evaluator chấm (ví dụ ELK vạch liền với nhiễu ×2,5 khi ELK can thiệp trượt PP-SWR-032). Ca ngoài benchmark (chồng nhiều lỗi tuỳ ý) vẫn được chấm theo các tiêu chí áp dụng, nhưng không thuộc bộ kiểm chính thức.
