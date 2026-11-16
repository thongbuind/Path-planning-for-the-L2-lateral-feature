# Path Planner SIL, chạy thời gian thực

Web một khung để present Path Planner. Mỗi lần bấm **Chạy planner**, `libpp_planner` thật chạy trong simulator SIL của repo, mỗi 25 ms một lần `pp_step()` theo đồng hồ thật. Từng chu kỳ được đẩy lên web ngay khi tính xong. Thông số nhảy theo từng chu kỳ, biểu đồ hiện dần. Không có dữ liệu thu sẵn.

## Chạy

```bash
python3 web/serve.py
```

Mở http://127.0.0.1:8770/simulation/ (đổi cổng bằng `--port`). Cần Python có numpy, scipy, pyyaml (đã đủ nếu chạy được benchmark của repo) và `build/planner/libpp_planner.dylib` đã build. Trang không chạy khi mở thẳng file `index.html`, vì cần server.

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

- `server.py`: tệp tĩnh và API (`/api/catalog`, `/api/run`, `/api/control`, `/api/stop`). Chỉ nghe ở 127.0.0.1. Một lượt chạy tại một thời điểm; bấm Chạy lần nữa, Dừng hoặc đóng tab thì lượt cũ bị dừng.
- `tools/rt_run.py`: kế thừa `Harness` của `sim/` trong file này (không sửa repo), sau mỗi `planner.step()` lấy kết quả của chu kỳ, chờ cho kịp đồng hồ thật rồi gửi một dòng JSON. Hết lượt chạy thì chạy `eval.metrics` để có kết luận. Lệnh `catalog` đọc danh mục từ benchmark.
- Mô phỏng tất định theo seed: cùng cấu hình và seed thì cho cùng kết quả như `eval.runner`. Riêng thời gian tính là đồng hồ thật của máy lúc chạy, nên có thể giật khi máy bận.
- Chỉ ĐỌC repo; mã web nằm trong `web/simulation/`.

Ca trượt hiển thị đúng như evaluator chấm (ví dụ ELK vạch liền với nhiễu ×2,5 khi ELK can thiệp trượt PP-SWR-032). Ca ngoài benchmark (chồng nhiều lỗi tuỳ ý) vẫn được chấm theo các tiêu chí áp dụng, nhưng không thuộc bộ kiểm chính thức.
