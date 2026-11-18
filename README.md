# Product A – Hệ thống hỗ trợ vận hành chợ bán sỉ thủy sản

## 1. Thông tin

**Tên dự án:** Product A – Hệ thống hỗ trợ vận hành chợ bán sỉ thủy sản · **Mã học viên:** B123581 · **Đề:** Product A · **Bài:** AIDD LAB-5 – chia task, ước lượng, đưa backlog lên GitHub Project, báo cáo tiến độ

---

## 2. Tổng quan

- **Nguồn:** backlog được chia (break) từ bộ thiết kế LAB-4 (nộp 2026-11-13): screen spec, detail design DD-01…DD-06, kiến trúc, ADR-001…012, đối chiếu database D-01…D-40, PREMISE của LAB-4. Prototype LAB-2 được dùng làm nền; 35 issue ghi rõ "tận dụng prototype".
- **PREMISE.md có thay đổi so với LAB-4:** sửa 6 điểm spec phát hiện khi chia task (DD-06 ghi 入金日 bằng 1 hàm database, API-11 nhận đủ chuyển trạng thái 許可 / 承認, lưu vết đăng nhập không cần chợ, lưu vết cùng transaction cho mọi thao tác, miền giá trị 料率 / 請求金額, phiên bản quy tắc v1 tạo bằng migration) và thêm 9 giả định P-08…P-16 – xem [PREMISE.md](PREMISE.md).
- **Backlog:** **14 epic · 85 issue · 81 sub-issue** (180 issue trên GitHub, có quan hệ sub-issue thật). Ràng buộc đặc thù tách issue riêng; **完納奨励金 là epic riêng (E12)**.
- **Ước lượng:** chấm SWP bằng skill tự viết, PL chốt 53 issue mẫu → **691 SWP / 1.462 giờ** (dev + tự test) – xem [estimate.md](estimate.md).
- **Sprint giả lập đã chạy:** **Sprint 1, 2026-11-23 → 2026-12-06** – kế hoạch 23 issue / 95 SWP, hoàn thành 74 SWP (78%) – xem [progress-report.md](progress-report.md). Số liệu sprint là giả lập.

## 3. Link

| | |
|---|---|
| Repo | https://github.com/ngochv-3581/productA-lab5-backlog |
| GitHub Project | https://github.com/users/ngochv-3581/projects/1 ("Product A – LAB-5 Backlog") |
| Báo cáo SWP (HTML, trong repo) | [reports/swp-report.html](reports/swp-report.html) – tải về rồi mở bằng trình duyệt (tự chứa, không gọi mạng) |
| Burndown Sprint 1 | [reports/burndown-sprint1.png](reports/burndown-sprint1.png) |

Đã mở thử bằng cửa sổ ẩn danh: 2026-11-18 (repo và GitHub Project, không đăng nhập)

## 4. Cấu trúc repo

| File / thư mục | Nội dung |
|---|---|
| `README.md` | File này: tổng quan, link, cấu trúc, Spec → epic |
| `PREMISE.md` | Tiền đề LAB-5: spec thêm / bỏ / sửa so với LAB-4, giả định P-08…P-16, hướng đã chốt |
| `task-breakdown.md` | Nguyên tắc chia task, Definition of Done, bảng Spec → issue, phần spec chưa thành issue, ràng buộc đặc thù, 25 chỗ hở / mâu thuẫn |
| `estimate.md` | Issue mẫu và điểm PL chốt, cách quy ra giờ, tổng theo epic, so với estimate LAB-1 |
| `progress-report.md` | Báo cáo tiến độ Sprint 1 (giả lập): trạng thái, burndown, rủi ro trễ |
| `AI-report.md` | Cách dùng AI ở LAB-5: công cụ / prompt, review, điểm đặc biệt |
| `AI_LOG.md` | Nhật ký làm việc với AI và lỗi AI ghi nhận khi review |
| `CLAUDE.md` | Quy tắc cách ly, quy tắc public, quy ước sửa backlog cho agent làm việc trong repo |
| `.gitignore` | Bỏ qua file môi trường, log, `__pycache__/`, `.venv/` |
| `backlog/` | `backlog.json` (backlog máy đọc được), `swp.json` (điểm SWP, giờ), `swp_review.json` (điểm PL chốt), `github_map.json` (mã ↔ số issue / item Project), `sprint1_sim.json` (dữ liệu giả lập Sprint 1) |
| `reports/` | `swp-report.html` (báo cáo chấm SWP), `burndown-sprint1.png` |
| `skills/` | `swp-scoring/SKILL.md` – skill chấm SWP (Scope × Complexity → SWP → giờ) |
| `tools/` | Script tái tạo mọi số liệu: `gen_backlog.py` (nguồn backlog), `swp_scores.py` + `swp_build.py` (chấm SWP, báo cáo), `estimate_build.py` (bảng estimate), `github_sync.py` (đưa lên GitHub, chạy lại không tạo trùng), `sprint1_sim.py` (giả lập Sprint 1, burndown) |

Chạy lại (từ gốc repo): `python -I -X utf8 tools/gen_backlog.py` → `tools/swp_build.py` → `tools/estimate_build.py`; vẽ burndown cần matplotlib (môi trường ảo `.venv`, không commit).

## 5. Spec → epic

| Spec (mã / file LAB-4 hoặc dòng PREMISE) | Epic trên Project (#số – tên) | Ghi chú |
|---|---|---|
| ADR-001, ADR-011 (`specs/05_adr/`), `docs/GLOSSARY_JA.md` | #1 – E01 Nền tảng dự án và quy ước chung | Hạng mục WBS: CI, môi trường vùng Tokyo, quy trình migration, từ điển tiếng Nhật |
| ADR-007, SC-20, D-28, D-33, D-34, D-40 (`specs/06_database/diff.md`); PREMISE.md dòng 13–14, 28, 30 | #9 – E02 Lưu vết chỉ thêm và quyền database | Ràng buộc: lưu vết chỉ thêm, cùng transaction cho mọi thao tác |
| DD-02, ADR-004, D-01, D-09, D-16, D-25, D-29; LAB-4 PREMISE dòng 43 (P-01); PREMISE.md dòng 25 | #11 – E03 Chợ và 営業日 theo cấu hình chợ | **Ràng buộc đặc thù 営業日 theo chợ** (mốc chuyển ngày theo phiên bản quy tắc) |
| SC-18, ADR-008, D-02, D-03, D-35; LAB-4 PREMISE dòng 20, 44; PREMISE.md dòng 16, 26 | #31 – E04 Quy tắc vận hành theo chợ có phiên bản (SC-18) | Người soạn ≠ người duyệt; phiên bản đã duyệt không sửa; nền của E03 và E12 |
| SC-01, SC-21, SC-25, DD-01, ADR-002, ADR-003, D-05, D-10, D-11, D-30, D-36, D-37, D-38; PREMISE.md dòng 29 | #14 – E05 Xác thực và phân quyền nhiều vai trò | Gộp 7 → 3 vai trò (LAB-4 PREMISE dòng 16); システム管理者 không xem dữ liệu nghiệp vụ |
| SC-02, SC-03, ADR-009, D-06, D-08, D-12…D-15; LAB-4 PREMISE dòng 21, 45; PREMISE.md dòng 12, 27 | #68 – E06 Người tham gia và 許可 / 承認 hai luồng | **Ràng buộc đặc thù 許可 / 承認 hai luồng** |
| SC-05, SC-06, SC-07, API-12…API-14 | #85 – E07 Lô hàng và 目利き | Chủ yếu tận dụng prototype |
| SC-08, SC-09, SC-10, DD-03, ADR-005, D-19…D-21 | #90 – E08 Giao dịch 相対取引 / せり / 取消 | Khóa lô ở database, không tự hủy (L4); chặn sau 締め (G-04) |
| SC-11, SC-12, DD-04, ADR-006, D-22…D-24, D-32 | #104 – E09 修正依頼 (sửa sau khi chốt) | **Ràng buộc đặc thù người tạo ≠ người duyệt** |
| SC-13, SC-14, D-39; LAB-4 PREMISE dòng 48 (P-06) | #112 – E10 引渡し (giao hàng nhiều lần) | Được giao cho ngày đã 締め |
| SC-15, SC-19, DD-05, ADR-010, D-07; LAB-4 PREMISE dòng 55 | #119 – E11 締め và xuất CSV kế toán | **Ràng buộc đặc thù 締め** (không mở lại, snapshot); CSV theo mẫu khách đang chờ |
| SC-17, DD-06, L8, D-04, D-26, D-27, D-31; LAB-4 PREMISE dòng 44 (P-02); PREMISE.md dòng 11, 15, 22–24 | #136 – E12 完納奨励金 (thưởng trả đúng hạn) | **EPIC RIÊNG**: phiên bản quy tắc, số nguyên + làm tròn, 期限内 / 期限超過 không ân hạn, xem trước, ghi 入金日 và khóa kết quả, màn hình, test vector Phụ lục C |
| SC-24, ADR-012, D-17, D-18; LAB-4 PREMISE dòng 47 (P-05) | #153 – E13 Offline hẹp cho tablet (ロット登録, 引渡し入力) | Phần rủi ro kỹ thuật cao; chờ trả lời Q8 |
| T01–T17 (`docs/LAB2_SCOPE.md` mục 8), CS-04, CS-24, L7 / G-26 | #171 – E14 Kiểm thử hệ thống và chuẩn bị go-live | Hạng mục WBS: hồi quy, test bảo mật gọi thẳng database, nghiệm thu nội bộ |

Bảng ánh xạ chi tiết từng mã spec → issue / sub-issue: [task-breakdown.md](task-breakdown.md) mục 2.
