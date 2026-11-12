# spec-web: bản đồ yêu cầu

Đề bài G1 nằm ở `docs/reference/G1_Path_Planning.pdf` tính từ thư mục G1. Bộ tài liệu kỹ thuật (Technical Documents) là nguồn chính thức cho yêu cầu, thiết kế, interface và giả lập. Bản đồ cho biết các khối làm gì, nối với nhau ra sao và mở đúng mục của tài liệu. Prototype nằm ở `../src/`.

## Mở

Chạy:

```sh
python3 spec-web/serve.py
```

rồi vào http://127.0.0.1:8770/ . `serve.py` chỉ dùng thư viện chuẩn, phục vụ file tĩnh và đọc, ghi
các file tài liệu `.md`. Mở thẳng `index.html` thì bản đồ vẫn xem được, nhưng không đọc được tài liệu. Font Inter tải từ Google Fonts; khi offline, web dùng font hệ thống.

## Thao tác

- Chọn **VI** hoặc **EN** ở góc trên bên phải. Lần đầu mở dùng tiếng Việt. Trình duyệt ghi nhớ ngôn ngữ đã chọn.
- Di chuyển bản đồ: kéo chuột, kéo một ngón, hoặc lướt hai ngón cùng nhau trên trackpad.
- Phóng to, thu nhỏ quanh con trỏ: chụm hai ngón, lăn bánh xe chuột, hoặc giữ Ctrl/Cmd rồi cuộn.
- Nút góc phải: phóng to, thu nhỏ, đưa tất cả thẻ vào khung. Khi bản đồ đang được focus: phím `+`, `-`, `0` và các phím mũi tên.
- Bấm thẻ phần mềm, giả lập hoặc nhãn đường nối để mở mục tương ứng trong tài liệu.
- Bấm **Tài liệu kỹ thuật** để mở danh sách tại `technical-documents/`. Bấm thẻ báo cáo để mở URL riêng, ví dụ `technical-documents/?doc=adas-function-specification&lang=vi`. Liên kết **Trang chủ** đưa về bản đồ tại `home/`.

## Chuẩn bị bản tĩnh cho GitHub Pages

Từ thư mục dự án, chạy lệnh sau mỗi khi cần xuất lại web hoặc cập nhật báo cáo.

```sh
node spec-web/build-static.cjs
```

Lệnh tạo lại `spec-web/dist/` với `index.html`, trang báo cáo, tài nguyên, bản Markdown tiếng Việt và các bản dịch hiện có. Người đọc có thể lưu nháp nhận xét trên trình duyệt.

Để xem thử, chạy `python3 -m http.server 8772 --directory spec-web/dist` rồi mở [bản tĩnh cục bộ](http://127.0.0.1:8772/).

GitHub Pages dùng nguồn **GitHub Actions**. Workflow `Deploy GitHub Pages` xuất bản `spec-web/dist/` sau mỗi lần push lên `main`. Có thể chạy lại từ tab **Actions**. [Hướng dẫn cấu hình GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

## Nhận xét theo đoạn

Bôi chọn văn bản trong báo cáo, bấm **Nhận xét**, rồi nhấn **Enter** để lưu hoặc **Shift+Enter** để xuống dòng. Khi lưu thành công, ô nhận xét tự đóng và trang giữ nguyên vị trí đang đọc. Thẻ số cạnh đoạn trích mở các nhận xét của đoạn đó để xem, sửa hoặc viết thêm. Nút **Nhận xét (n)** ở đầu báo cáo mở danh sách đầy đủ, kể cả khi đoạn trích đã đổi hoặc thuộc bản ngôn ngữ khác.

Mỗi nhận xét có nút **Đã xong** và **Mở lại**. Nhận xét đã xong bị ẩn khỏi trang và khỏi danh sách; số trên nút **Nhận xét (n)** chỉ đếm nhận xét còn mở. Trong danh sách, nút **Xem nhận xét đã xong (n)** hiện lại chúng, kèm ghi chú đã xử lý thế nào nếu có. Agent đánh dấu từ dòng lệnh, qua cùng khoá ghi với web:

```sh
python3 spec-web/review_store.py resolve <id-báo-cáo> <số> [<số> ...] --note "Đã xử lý thế nào"
python3 spec-web/review_store.py reopen <id-báo-cáo> <số>
```

Trong file JSON, nhận xét đã xong có `resolved: true`, `resolvedAt` và `resolution` (ghi chú, không bắt buộc). Sau khi sửa `review_store.py`, cần khởi động lại `serve.py`.

Khi chạy cục bộ, `serve.py` lưu tại `spec-web/data/review-comments/<id-báo-cáo>.json`. Các file này đi qua API nhận xét và nằm ngoài phần tài nguyên web phục vụ trực tiếp. Agent có thể đọc trường `reviews` để lấy số nhận xét, nội dung và vị trí. `anchor` chứa ngôn ngữ, đoạn trích, ngữ cảnh trước và sau, vị trí ký tự tính từ 0 trong văn bản hiển thị và SHA-256 nếu có phiên bản đã lưu. Nếu đang chạy phiên cũ của `serve.py`, hãy khởi động lại máy chủ để nạp API nhận xét.

Trên GitHub Pages, bấm **Gửi qua GitHub** trong bảng nhận xét để xem trước góp ý, rồi bấm **Mở GitHub Issue**. Người đọc kiểm tra và gửi issue bằng tài khoản GitHub của họ. Với góp ý dài, nút **Sao chép góp ý** cho phép dán toàn bộ nội dung vào issue. Bản xuất chỉ chứa mã web và tài liệu. Các file nhận xét cục bộ nằm ngoài thư mục xuất bản. [Cách GitHub điền sẵn nội dung issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue#creating-an-issue-from-a-url-query)

Web dùng URL GitHub Pages mặc định để xác định repo nhận góp ý. Với tên miền riêng hoặc repo nhận góp ý khác, đặt đích khi xuất. Bật **Issues** trong repo đích để người đọc có thể gửi.

```sh
SPEC_WEB_GITHUB_REPOSITORY=owner/repo node spec-web/build-static.cjs
```

## Quy trình nội dung song ngữ

Soạn và chỉnh sửa bản tiếng Việt trước, sau đó cập nhật bản dịch tiếng Anh tương ứng.

- Giao diện và bản đồ lấy tiếng Việt từ `home/index.html`, `app.js` và `cards.js`. Trong `en/strings.js`, khoá là nguyên văn tiếng Việt, giá trị là bản dịch. Khi sửa câu gốc, cập nhật cả khoá và giá trị. Giữ nguyên tên trường, ID, kiểu dữ liệu và đơn vị.
- Từ thư mục G1, tài liệu tiếng Việt nằm ở `docs/vi/<id>.md`. Bản tiếng Anh tương ứng nằm ở `docs/en/<id>.md` và mở ở chế độ chỉ đọc. Cập nhật bản dịch sau khi bản gốc đổi và giữ cùng ID mục ở cả hai bản. Mục lục và liên kết tới từng mục dùng ngôn ngữ đã chọn. Khi dùng giao diện EN mà báo cáo chưa có bản dịch, web mở bản tiếng Việt và ghi rõ ngôn ngữ đang xem.

### Phiên bản tài liệu

Thẻ và trình xem hiển thị mã phiên bản hiện tại của cả hai file. Mỗi mã là tám ký tự đầu của SHA-256 tính từ file đã lưu. Hai ngôn ngữ có mã riêng. Trạng thái **Khớp bản đã đối chiếu** xuất hiện khi cả hai mã đầy đủ trùng với cặp đã ghi nhận trong `docs/en/versions.json`.

Sau khi cập nhật và kiểm tra bản tiếng Anh theo bản tiếng Việt, chạy lệnh sau từ thư mục dự án để ghi nhận cặp mới. Thay `adas-function-specification` bằng ID tài liệu cần xác nhận.

```sh
python3 spec-web/confirm-translation.py adas-function-specification
```

Sửa bản Việt sẽ báo **Cần cập nhật EN**. Nếu chỉ sửa bản Anh, web báo **Cần đối chiếu EN** cho đến khi cặp mới được ghi nhận. Trạng thái phản ánh cặp file đã được người biên soạn kiểm tra.

## Thêm thẻ hoặc đường dữ liệu

Viết chi tiết vào tài liệu kỹ thuật trước. Mục cần dẫn tới dùng tiêu đề có ID cố định, ví dụ `## EgoMotionQuery {#ego-motion}`. ID được giữ khi sửa báo cáo trên web.

- Thẻ khối trong `SPEC_CARDS` có tên, một câu về vai trò và `research: { doc, section }`. `doc` là ID báo cáo, `section` là ID của mục. Tọa độ `x`, `y` đặt các khối trên xe có đường nối. Các vùng tài liệu, SIL và sơ đồ xếp thẻ theo thứ tự khai báo.
- Đường dữ liệu trong `SPEC_EDGES` có `from`, `to`, `label` và `research: { doc, section }`. Các trường, đơn vị và trạng thái của interface nằm trong báo cáo được liên kết.
- Dịch nhãn hiển thị trong `en/strings.js`. Khi bản đồ và tài liệu vênh nhau, sửa bản đồ theo tài liệu.

## Tài liệu

Thẻ có `kind: "doc"` vẽ như một trang giấy. Bản gốc của tài liệu Chức năng ADAS là
`docs/vi/adas-function-specification.md` và bản dịch là `docs/en/adas-function-specification.md` (tính từ thư mục G1). Bản gốc đồng bộ hai chiều:

- Sửa trên web cục bộ: mở bản VI bằng `serve.py` và gõ thẳng lên trang báo cáo. Sau 0,7 s web đổi
  trang sang Markdown và ghi vào file md. Khi đổi ngôn ngữ hoặc bấm **Bản đồ yêu cầu**, web lưu thay đổi đang chờ trước.
- Sửa file md bằng editor: web hỏi `serve.py` mỗi 1,5 s, thấy file đổi thì tải lại trang và mục lục.
- Nếu file md đổi ở ngoài trong lúc web đang lưu, web không ghi đè mà lấy bản trên file.

Markdown được hỗ trợ: `#`–`###`, đoạn văn, `-` và `1.`, bảng kiểu GitHub, `**đậm**`, `*nghiêng*`, `` `code` ``,
link. Ô bảng chỉ ghi "đã chốt", "đề bài", "đề xuất" hoặc "cần chốt" hiện thành nhãn màu. Lưu từ web sẽ
viết lại md theo một kiểu chuẩn (ví dụ bảng `| a | b |`), nội dung không đổi.

Để thêm tài liệu, tạo `docs/vi/<id>.md` rồi thêm thẻ với `kind: "doc"` và `doc: "<id>"` trong `cards.js`. Đổi tên tài liệu thì ghi ID cũ vào `renamedFrom` (một ID hoặc danh sách ID) để link cũ tự chuyển sang ID mới. Khi có bản dịch, đặt tại `docs/en/<id>.md`.

| File | Vai trò |
|---|---|
| `cards.js` | Tên, vị trí, mô tả ngắn và link tới tài liệu |
| `en/strings.js` | Bản dịch giao diện, thẻ và đường dữ liệu |
| `../docs/en/*.md` | Bản dịch tài liệu Markdown |
| `app.js` | Pan, zoom, vẽ bản đồ và mở báo cáo |
| `technical-documents/index.html` | Danh sách và trang đọc báo cáo |
| `build-static.cjs` | Tạo bản tĩnh trong `dist/` |
| `docmd.js` | Chuyển Markdown ↔ HTML cho trang tài liệu |
| `serve.py` | Server tĩnh, đọc và ghi file tài liệu `.md` |
| `style.css` | Giao diện theo tông SAI: nền trắng, Inter, điểm nhấn tím |
