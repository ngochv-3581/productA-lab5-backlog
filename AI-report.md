# AI-report – LAB-5 (Product A)

> Báo cáo cách dùng AI ở LAB-5: chia task, chấm SWP, quy giờ, đưa backlog lên GitHub Project, giả lập sprint và báo cáo tiến độ.
> Công cụ AI: Claude Code (agent trong ứng dụng desktop) – đọc / ghi file, chạy lệnh shell, gọi `gh` CLI, chạy script Python. Nhật ký chi tiết: [AI_LOG.md](AI_LOG.md).

## 1. Skill / công cụ và cách viết prompt cho từng việc

**Cách viết prompt chung (áp cho mọi bước):**
- Mỗi bước là 1 prompt có cấu trúc: mục tiêu → dữ liệu đầu vào (đường dẫn cụ thể) → **định dạng đầu ra bắt buộc** (đúng số phần, đúng thứ tự, đúng tên cột) → điểm **DỪNG** (ví dụ "CHƯA chấm SWP, CHƯA tạo gì trên GitHub", "DỪNG, chưa viết estimate.md") → nội dung phải báo lại.
- Quy tắc lâu dài đặt trong `CLAUDE.md` của repo (agent tự đọc mỗi lần): **quy tắc cách ly** (máy có dự án khác: chỉ ghi trong `productA-lab5`, repo LAB-4 chỉ đọc, không đổi cấu hình git / gh chung, kiểm tài khoản `gh` trước mọi lệnh tạo) và **quy tắc public** (chỉ mã spec, không chép câu tài liệu khách, không tên / email thật, không khóa / URL môi trường).
- Chế độ "TỰ ĐỘNG": agent tự làm hết bước, chỉ dừng khi gặp điều kiện DỪNG hoặc việc cần người (cấp quyền).

| Việc | Skill / công cụ | Prompt và cách làm |
|---|---|---|
| **Break task** | Agent đọc file + Python | Prompt liệt kê đúng các file LAB-4 phải đọc, yêu cầu `task-breakdown.md` 4 phần (nguyên tắc, Spec → issue, ràng buộc đặc thù với 完納奨励金 là epic riêng, chỗ hở) và schema `backlog.json`. Agent viết dữ liệu backlog trong 1 script (`tools/gen_backlog.py`) rồi **sinh** cả `backlog.json` lẫn bảng Spec → issue từ cùng nguồn, kèm kiểm tự động: không trùng mã, phụ thuộc không vòng, mọi mã nhắc trong `.md` đều có trong backlog. |
| **Chấm SWP** | Skill tự viết `skills/swp-scoring/SKILL.md` (rubric Scope × Complexity, mục cộng đặc thù, bảng Fibonacci, quy tắc tách 13 / 21, chọn mẫu) | Prompt: "chấm theo đúng SKILL.md", mỗi điểm S / C có lý do 1 câu trỏ mã spec, tách issue 13 / 21 rồi chấm lại. Agent ghi điểm tay + lý do vào `tools/swp_scores.py`, ghi rõ 6 cách hiểu tiêu chí (R1–R6); `tools/swp_build.py` tính SWP, chặn khi còn 13 / 21 (đã tách 18 lần), chọn 53 issue mẫu với seed cố định, xuất `swp.json` + báo cáo HTML. |
| **Quy giờ** | Quy ước trong SKILL mục 5 + `tools/estimate_build.py` | Prompt nêu cách quy đổi cố định (1→2, 2→4, 3→6, 5→10, 8→16 giờ; low +20%) và số liệu LAB-1 để so. Giờ chỉ tính bằng script từ SWP đã chốt – không ước tay từng issue; bảng estimate sinh lại được. |
| **Ghi lên GitHub Project** | `gh` CLI (REST + GraphQL) trong `tools/github_sync.py` | Script **kiểm `gh api user` = ngochv-3581 trước khi ghi**; lưu `github_map.json` sau mỗi lần tạo nên chạy lại **không tạo trùng**; **nghỉ 1,5 giây** giữa các lần tạo issue và tự chờ khi gặp giới hạn; tạo quan hệ sub-issue thật; chỉ issue lá mang SWP / Giờ để tổng Project = tổng estimate; bước `verify` đọc lại Project và so (691 SWP / 1.462 giờ khớp). Push dùng credential helper cho riêng lệnh đó, không đổi cấu hình chung. |
| **Báo cáo tiến độ** | `tools/sprint1_sim.py` + matplotlib | Prompt nêu năng lực đội, mức 85%, thứ tự ưu tiên, yêu cầu kết quả "thực tế, không đẹp quá" (75–80% Done, 2–3 Blocked, 1–2 sự kiện lệch). Script kiểm năng lực theo vai và phụ thuộc, ghi `sprint1_sim.json`, cập nhật Project (Sprint, Status, đóng issue kèm comment, nhãn `gia-lap`), vẽ burndown; báo cáo viết theo văn phong gửi khách. |

## 2. Review output của AI

| Bước | Người review | Phát hiện | Xử lý |
|---|---|---|---|
| Break task | PL (người dùng) đọc task-breakdown + danh sách chỗ hở | AI đề xuất để PL **chép giả định P-08…P-16 vào PREMISE.md của repo LAB-4** – sai chỗ: repo LAB-4 chỉ đọc và file nộp LAB-5 phải tự chứa | Tạo `PREMISE.md` trong repo LAB-5 (spec sửa, giả định, hướng chốt); `task-breakdown.md` trỏ lại đúng dòng của file mới |
| Break task | AI tự kiểm khi tách issue | Trùng phạm vi: E12-07 và E04-01-DB2 cùng tạo phiên bản quy tắc v1 | Thu hẹp E12-07 chỉ còn chuyển kết quả thưởng |
| Chấm SWP | **PL chốt 53 issue mẫu** | Sửa **11 / 53 = 21%** (< 30% → theo skill giữ tiêu chí, không chấm lại toàn bộ). **Lỗi 1 – cộng điểm đặc thù chồng nhau:** E12-01 ra 8 trong khi E04-02 cùng logic chỉ 3, vì cộng cả "tiền" lẫn "営業日"; tương tự E12-03, E12-04, E12-05-T, E12-06-UI2, E12-07, E06-05-UI2, E13-04-UI4, E13-02. **Lỗi 2 – issue làm rõ chấm như issue code:** E12-09 8 → 3, E06-09 5 → 3 | Áp điểm chốt (723 → 691 SWP, 1.532 → 1.462 giờ); ghi 2 kiểu lỗi vào AI_LOG và đề xuất bổ sung rubric cho lần sau |
| Estimate | PL đưa số liệu LAB-1 và bảng ánh xạ function ↔ epic | LAB-5 = 165 MD so với 444,6 MD (37%; 49% nếu bỏ 7 function chưa có thiết kế) | Giải thích theo nguyên nhân cụ thể (tận dụng prototype, gộp vai trò, function chưa thiết kế); ghi rủi ro quy ước giờ chưa hiệu chỉnh; thêm dòng function chưa có thiết kế vào task-breakdown mục 2.8 |
| GitHub | Người dùng | Token `gh` thiếu quyền `project`; lần cấp quyền đầu chưa lưu được | AI **không tự đăng nhập / cấp quyền**, chỉ hướng dẫn; kiểm lại quyền thật (header phản hồi của GitHub) trước khi chạy tiếp. Người dùng cấp quyền `project` và **bỏ qua quyền truy cập tổ chức của công ty** |
| GitHub | AI kiểm trước khi tạo | Tác giả mọi commit là email noreply; quét nội dung và lịch sử: không khóa, URL môi trường, link Google, tên / email thật | Mới tạo repo / Project ở chế độ private |
| Báo cáo tiến độ | AI tự soát văn phong | Ảnh burndown có tên cột kỹ thuật (`market_id`) không hợp với báo cáo gửi khách | Đổi thành "chuyển dữ liệu sang mô hình nhiều chợ" |
| Khác (AI_LOG) | — | Prompt bước chấm SWP bị gửi lại lần 2 sau khi đã xong | AI kiểm commit và chạy lại script thấy kết quả không đổi → không làm lại, báo người dùng |

## 3. Điểm đặc biệt

**Chỗ tin là hiệu quả**
- **Skill tự viết có rubric + người chốt mẫu:** mỗi điểm có lý do trỏ mã spec nên PL review nhanh; quy tắc "sửa ≥ 30% mẫu thì sửa tiêu chí" giúp quyết định có căn cứ thay vì sửa từng con số.
- **Script tái tạo được mọi số liệu:** backlog, SWP, estimate, issue GitHub, giả lập sprint đều sinh từ dữ liệu trong `tools/`; sửa 1 chỗ rồi chạy lại, các bảng luôn khớp nhau (kể cả tổng trên Project = estimate).
- **Cách ly với dự án khác trên cùng máy:** chỉ ghi trong thư mục LAB-5, repo LAB-4 chỉ đọc, không đổi cấu hình git / gh chung, kiểm tài khoản trước mọi lệnh tạo, email commit noreply.
- **Làm private trước rồi mới public:** quét nội dung trước khi tạo repo, báo cáo HTML tự chứa không gọi mạng; chỉ chuyển public khi người dùng đồng ý.

**Chỗ chưa tốt / cần cải thiện khi làm thật**
- **Rubric cần quy tắc tránh cộng chồng:** không cộng mục đặc thù khi rủi ro đã do issue khác gánh hoặc issue dùng lại logic có sẵn; issue làm rõ cần thang điểm riêng.
- **Quy ước 1 SWP ≈ 2 giờ chưa hiệu chỉnh** bằng số liệu thực tế của đội; cần đo sau 1–2 sprint thật rồi sửa bảng quy đổi cho mọi issue.
- **Sprint 1 là giả lập:** velocity, burndown, sự kiện lệch kế hoạch do người dùng đặt khung và AI dựng số liệu; chưa dùng để cam kết với khách.
- **Chưa có review của đội thật / khách:** điểm SWP mới qua 1 người chốt; 25 chỗ hở và 9 giả định chưa được khách xác nhận; vai phụ trách là vai giả định.
