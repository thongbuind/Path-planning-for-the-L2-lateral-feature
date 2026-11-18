# PP-PR-070 Thời điểm rời FOLLOW và giữ path cũ

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở. Chờ xác nhận trên bản build chính thức |
| Mở ngày | 2026-11-18 |
| Yêu cầu | PP-SWR-170, 173 |
| Ca tái hiện | S22b, F25b–e trên S22a, VP-0, seed 1 |

S22b có nhiều phiên FOLLOW ngắn. Phiên dài nhất vẫn dưới 30 m, nên chưa quan sát được phản ứng sau khi đạt giới hạn khoảng cách.

Sau khi frame đổi ID hoặc loại xe tới planner trong F25c và F25e, bộ chấm phát hiện path mất hiệu lực trước hạn `T_coast`. Trong F25b–e, bộ chấm cũng phát hiện một số lần vào lại FOLLOW muộn.

Đối chiếu thời điểm lane model đủ tin trở lại, trạng thái LeadTarget và thời điểm LCC rời FOLLOW trong từng log để xác định nguyên nhân.
