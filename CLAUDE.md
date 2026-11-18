# CLAUDE.md – productA-lab5 (LAB-5: chia task và backlog cho Product A)

Repo này chứa backlog để xây hệ thống thật theo bộ thiết kế LAB-4, dùng prototype LAB-2 làm nền.
Tài liệu viết tiếng Việt; tên bảng / cột / API giữ tiếng Anh; thuật ngữ nghiệp vụ tiếng Nhật theo `docs/GLOSSARY_JA.md` của repo thiết kế LAB-4 (chỉ đọc).

## 1. Quy tắc cách ly (bắt buộc – máy có dự án khác)

- Chỉ tạo / sửa file trong `aidd-lab/productA-lab5`. Thư mục repo thiết kế LAB-4 (đặt cạnh `productA-lab5`, private – không ghi tên ở đây) **chỉ ĐỌC**: không chép file nào sang, không sửa gì.
- **KHÔNG** chạy `git config --global`, `gh auth login` / `logout` / `switch` / `setup-git`. Chỉ dùng `git config --local` trong productA-lab5.
- Tài khoản GitHub dùng cho repo này: `ngochv-3581`. Trước **mọi** lệnh `gh` tạo repo / project / issue, chạy `gh api user --jq .login` – kết quả phải là `ngochv-3581`; sai thì **DỪNG**, không chạy tiếp.
- Không ghi gì vào thư mục `~/.claude`; skill để trong repo (`productA-lab5/skills`).
- Repo và GitHub Project tạo ở chế độ **PRIVATE**; chỉ chuyển public khi người dùng đồng ý ở bước cuối.

## 2. Quy tắc PUBLIC (repo có thể chuyển public)

- Chỉ nội dung tự viết. **KHÔNG** chép câu chữ từ RFP / tài liệu khách; chỉ ghi mã (FR-xx, SC-xx, DD-xx, D-xx, L-xx, G-xx, P-xx, ADR-xxx).
- **KHÔNG** tên thật, email thật. Người phụ trách dùng vai giả định: `PL`, `BrSE`, `BE-1`, `BE-2`, `FE-1`, `QA-1`.
- **KHÔNG** mật khẩu, token, khóa, URL Supabase / Vercel, link Google Drive / Sheets, link hoặc tên repo thiết kế LAB-4 (private).
- Trỏ tới thiết kế LAB-4 bằng **đường dẫn tương đối trong repo thiết kế LAB-4** (ví dụ `specs/PREMISE.md dòng 44`), không dán URL.

## 3. Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `README.md`, `AI-report.md` | Giới thiệu bài nộp (tổng quan, link, cấu trúc, Spec → epic); báo cáo cách dùng AI |
| `PREMISE.md` | Tiền đề LAB-5: spec thêm / bỏ / sửa so với LAB-4, giả định P-08…P-16, hướng đã chốt |
| `task-breakdown.md` | Nguyên tắc chia task, bảng Spec → issue, ràng buộc đặc thù, chỗ hở / mâu thuẫn |
| `backlog/backlog.json` | Backlog máy đọc được (epic / issue / sub-issue) – **sinh từ** `tools/gen_backlog.py` |
| `backlog/swp.json`, `backlog/swp_review.json` | Kết quả chấm SWP; danh sách issue mẫu để người chốt (`swp_chot`, `ly_do`) |
| `reports/swp-report.html` | Báo cáo SWP tự chứa (không gọi mạng) |
| `skills/swp-scoring/SKILL.md` | Skill chấm SWP (Scope × Complexity → SWP → giờ) |
| `tools/gen_backlog.py` | Nguồn dữ liệu backlog; sinh backlog.json + bảng tự động trong task-breakdown.md (giữa `<!-- BEGIN:… -->` / `<!-- END:… -->`) |
| `tools/swp_scores.py`, `tools/swp_build.py` | Điểm S / C chấm tay + lý do; script tính SWP / giờ, chọn mẫu, áp `swp_chot`, xuất swp.json và báo cáo |
| `estimate.md`, `tools/estimate_build.py` | Estimate LAB-5 (5 phần); script sinh bảng issue mẫu, tổng theo epic, so với LAB-1 |
| `AI_LOG.md` | Nhật ký làm việc với AI + lỗi AI ghi nhận (dùng cho AI-report) |
| `progress-report.md`, `tools/sprint1_sim.py`, `backlog/sprint1_sim.json`, `reports/burndown-sprint1.png` | Giả lập Sprint 1 (số liệu GIẢ LẬP): kế hoạch, kết quả, burndown, báo cáo gửi khách. Vẽ ảnh cần matplotlib trong `.venv` (không commit) |
| `tools/github_sync.py`, `backlog/github_map.json` | Đưa backlog lên repo `ngochv-3581/productA-lab5-backlog` + Project v2 (PRIVATE); bảng mã ↔ số issue / item, chạy lại không tạo trùng |

## 4. Quy ước khi sửa backlog

- Sửa backlog **trong `tools/gen_backlog.py`**, không sửa tay backlog.json. Chạy lại từ gốc repo:
  `python -I -X utf8 tools/gen_backlog.py` rồi `python -I -X utf8 tools/swp_build.py` (script dừng nếu thiếu điểm hoặc còn SWP 13 / 21).
- Mã tạm: epic `E01`; issue `E01-03`; sub-issue `E01-03-DB` / `-API` / `-UI` / `-T` (test); tách tiếp sau chấm SWP thì đánh số `-DB1`, `-UI2`, `-T3`.
- Giả định / spec sửa mới ghi vào `PREMISE.md` (mã P-17 trở đi), không sửa repo thiết kế LAB-4.
- Chưa tạo gì trên GitHub cho tới khi người dùng yêu cầu.
