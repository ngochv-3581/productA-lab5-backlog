# AI_LOG – LAB-5 (Product A)

> Nhật ký làm việc với AI ở LAB-5: AI làm gì, người sửa gì, lỗi AI để dùng cho AI-report.
> Chỉ ghi mã (GAP-xx, P-xx, E..), không chép câu chữ tài liệu khách (CLAUDE.md – quy tắc PUBLIC).

## 1. Nhật ký

| Ngày | Bước | AI làm | Người quyết / sửa |
|---|---|---|---|
| 2026-11-17 | Chia task | Đọc bộ thiết kế LAB-4, tạo task-breakdown.md + backlog.json (14 epic), tìm 25 chỗ hở GAP-01…GAP-25, đề xuất giả định P-08…P-16 | PL yêu cầu đưa giả định vào PREMISE.md của LAB-5 (không sửa repo thiết kế LAB-4) |
| 2026-11-17 | Chấm SWP lần 1 | Chấm 137 issue lá theo skill swp-scoring, đặt 6 cách hiểu tiêu chí R1–R6, tách 18 lần vì SWP 13 / 21; 723 SWP / 1.532 giờ; chọn 53 issue mẫu (seed 20261117) | — |
| 2026-11-18 | Đưa lên GitHub | Kiểm tài khoản / tác giả commit / quét nội dung; tạo repo + Project v2 PRIVATE, 6 trường (Sprint 1–3 tạo được qua API), 180 issue + 166 quan hệ sub-issue, điền trường; tổng Project 691 SWP / 1.462 giờ khớp estimate.md | Người dùng tự cấp quyền `project` cho gh (lần đầu chưa lưu được, làm lại thì được) |
| 2026-11-18 | Quét bảo mật trước khi public | Quét file, toàn bộ lịch sử git và dữ liệu GitHub: không có khóa, đường dẫn máy, link Google, tên / email thật; chỉ có tên thư mục repo thiết kế LAB-4 và tên chợ trong 3 tiêu đề. Đã thay bằng cụm trung tính và gộp lịch sử thành 1 commit sạch (sao lưu lịch sử cũ trên máy, không đưa lên GitHub) | Người dùng duyệt phương án gộp lịch sử trước khi làm |
| 2026-11-18 | README + AI-report | Viết README.md (5 phần, số epic trên Project lấy từ github_map.json) và AI-report.md (3 phần) | Người dùng điền ngày mở thử bằng cửa sổ ẩn danh sau khi chuyển public |
| 2026-11-18 | Giả lập Sprint 1 | Lập kế hoạch theo năng lực (208 / 260 giờ = 80%, 23 issue / 95 SWP), cân tải vai giả định, giả lập kết quả (74 SWP Done = 78%, 3 Blocked chờ khách, 1 sự kiện phát sinh việc), cập nhật Project + đóng 17 issue (nhãn `gia-lap`), vẽ burndown, viết progress-report.md | Người dùng đặt khung giả lập (75–80% Done, sự kiện lệch kế hoạch) |
| 2026-11-18 | Review issue mẫu | Ghi swp_review.json, áp điểm chốt, tính lại giờ: 691 SWP / 1.462 giờ | PL sửa 11 / 53 issue mẫu (21% < 30%) → giữ tiêu chí, không chấm lại toàn bộ (SKILL mục 6) |

## 2. Lỗi AI ghi nhận khi PL review SWP (dùng cho AI-report)

### Lỗi 1 – Cộng điểm đặc thù chồng nhau

| | |
|---|---|
| Hiện tượng | Issue logic đơn giản nhưng chạm đồng thời "tiền" và "営業日" bị đẩy C lên 5 → SWP 8, cao hơn issue cùng logic không chạm tiền. |
| Issue bị sửa | E12-01 (8 → 5, cùng logic E04-02 chấm 3), E12-03 (8 → 5), E12-04 (5 → 3), E12-05-T (8 → 5), E12-06-UI2 (8 → 5), E12-07 (8 → 5); cùng kiểu: E06-05-UI2 (8 → 5), E13-04-UI4 (8 → 5, làm giống E13-04-UI3), E13-02 (5 → 3, S chấm 3 thay vì 2) |
| Nguyên nhân | AI áp mục cộng +1 của SKILL mục 3 một cách máy móc cho mọi issue chạm tiền / ngày, không xét (a) logic đã có ở issue khác và được dùng lại, (b) phần khó đã nằm ở issue khác (hàm tính ở API, test biên ở issue test), (c) issue làm cùng cách với issue anh em. |
| Cách tránh lần sau | Trước khi cộng mục đặc thù, hỏi: rủi ro tiền / ngày có **nằm trong issue này** không, hay đã được issue khác gánh? Issue dùng lại hàm / mẫu của issue khác thì chấm theo phần làm thêm, không theo độ khó của cả luồng. So chéo điểm các issue anh em (UI1 / UI2, UI3 / UI4) trước khi xuất. |

### Lỗi 2 – Issue làm rõ chấm như issue code

| | |
|---|---|
| Hiện tượng | Issue làm rõ (câu hỏi cho khách / PL) được chấm S × C như việc lập trình, cộng cả "tiền" và "câu hỏi mở" → SWP 5–8. |
| Issue bị sửa | E12-09 (8 → 3), E06-09 (5 → 3) |
| Nguyên nhân | Cách hiểu R3 của AI cho issue làm rõ vẫn dùng thang S / C của code và cộng mục đặc thù theo nội dung câu hỏi, trong khi người làm là PL / BrSE và việc thật là soạn câu hỏi + ghi quyết định. |
| Cách tránh lần sau | Issue `clarification` chấm theo công soạn câu hỏi / họp / ghi lại (thường SWP 1–3); rủi ro nội dung thể hiện bằng `confidence = low` và dự phòng ở issue code phụ thuộc, không cộng vào chính issue làm rõ. |

### Kết luận áp dụng

- Tỷ lệ sửa 11 / 53 = 21% < 30% → theo SKILL mục 6 **giữ nguyên tiêu chí mục 2–3**, chỉ áp điểm chốt cho issue mẫu; issue ngoài mẫu giữ điểm AI.
- Hai kiểu lỗi trên được ghi lại để: (1) đưa vào AI-report LAB-5; (2) đề xuất bổ sung cách hiểu R7 (không cộng mục đặc thù khi rủi ro do issue khác gánh) và sửa R3 (issue làm rõ) ở lần chỉnh skill sau – **chưa áp dụng** ở lần chấm này.
