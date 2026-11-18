# Task breakdown – Product A – LAB-5

> **Nguồn:** bộ thiết kế LAB-4 trong repo thiết kế LAB-4 (private) (chỉ đọc): `specs/PREMISE.md`, `specs/06_database/diff.md`, `specs/05_adr/`, `specs/04_architecture/architecture.md`, `specs/01_screen-spec/source/`, `specs/02_detail-design/source/`; thuật ngữ theo `docs/GLOSSARY_JA.md`.
> **Ngày:** 2026-11-17 · **Trạng thái:** đã chấm SWP lần 1 ([backlog/swp.json](backlog/swp.json), [reports/swp-report.html](reports/swp-report.html)) và tách các issue ra 13 / 21; chưa viết estimate, chưa tạo gì trên GitHub.
> **Tổng:** <!-- BEGIN:TOTAL -->14 epic · 85 issue · 81 sub-issue (180 dòng trong backlog.json).<!-- END:TOTAL -->
> **Tiền đề LAB-5:** [PREMISE.md](PREMISE.md) – spec sửa, giả định P-08…P-16, hướng đã chốt.
> **Bản máy đọc:** [backlog/backlog.json](backlog/backlog.json) – mỗi dòng 1 epic / issue / sub-issue (`id, epic, title, parent, type, spec_refs, labels, depends_on, note`). Bảng mục 2 sinh ra từ file này nên hai bên luôn khớp.

---

## 1. Nguyên tắc chia task

### 1.1 Backlog để làm gì

- Backlog để **xây hệ thống thật** theo thiết kế LAB-4, không phải làm lại prototype. Nền là **prototype LAB-2** (19 màn hình chạy thật, 17 API route, 12 bảng có RLS, trigger L4, bộ test T01–T17).
- Phần prototype đã khớp thiết kế (diff.md mục 4: trigger `trades_kiem_l4`, check người duyệt ≠ người tạo, `day_closes` không mở lại, RLS bật ở mọi bảng, giao hàng nhiều lần, `amount` generated) **không tạo issue làm lại**.
- Issue nào dùng lại màn hình / API / test của prototype thì gắn nhãn **`reuse-prototype`** và ghi rõ ở `note`: **"Tận dụng prototype: …"** (phần giữ, phần đổi). Tổng <!-- BEGIN:REUSE -->35<!-- END:REUSE --> mục.
- Mỗi chênh lệch D-01…D-40 của diff.md có ít nhất 1 issue (mục 2.3); mỗi màn hình trong phạm vi có ít nhất 1 issue (mục 2.1).

### 1.2 Độ hạt

| Quy tắc | Nội dung |
|---|---|
| 1 issue = 1 kết quả kiểm được | Kết thúc bằng thứ người khác kiểm lại được: test tự động chạy xanh, màn hình thao tác được theo screen spec, migration chạy xong + câu SQL kiểm cấu trúc ra đúng, hoặc câu trả lời đã được PL chốt (issue làm rõ). |
| Tối đa khoảng 2 ngày công | Quá 2 ngày hoặc chạm từ 2 lớp trở lên có rủi ro riêng → tách **sub-issue theo lớp**: `-DB` (migration / hàm / trigger / RLS), `-API`, `-UI`, `-T` (test). Sau chấm SWP, issue / sub-issue ra **SWP 13 / 21** được tách tiếp và đánh số (`-DB1`, `-DB2`, `-UI1` …) – xem [reports/swp-report.html](reports/swp-report.html). |
| Issue cha | Issue có sub-issue không làm việc trực tiếp; đóng khi mọi sub-issue đóng. Khi chấm SWP, cha = tổng con (skill `swp-scoring`). |
| Issue làm rõ (`clarification`) | Kết quả là câu trả lời / quyết định được PL chốt và ghi vào thiết kế; issue phụ thuộc bỏ nhãn `blocked` sau đó. |
| Spike (`spike`) | Kết quả là kết luận kỹ thuật + demo nhỏ, có thời hạn; không đưa thẳng lên production. |
| Thứ tự | Theo diff.md mục 5: ít rủi ro → nguyên tử (hàm database) → theo chợ + quy tắc → vai trò → giấy tờ → ngoài luồng chính. Phụ thuộc ghi ở `depends_on`. |

### 1.3 Định nghĩa xong (DoD)

Một issue / sub-issue chỉ "Done" khi đủ các mục áp dụng được:

1. Code + **test tự động** cho luật liên quan; tên test ghi mã luật (L-xx / G-xx / CS-xx / T-xx).
2. Luật quan trọng **kiểm 2 nơi**: API (câu lỗi M_xx tiếng Nhật lấy từ `ja.ts`) và database (check / trigger / RLS) – ADR-002.
3. Thao tác ghi có **lưu vết cùng transaction** (CS-15); không thao tác nào ghi `audit_logs` bên ngoài transaction.
4. Đổi database: file SQL migration đánh số trong repo app; **người dùng tự chạy** (dev → staging → production); chạy lại SQL kiểm cấu trúc; chạy lại các test T-xx ghi trong issue.
5. 営業日 chỉ lấy từ `business_date()` – không dùng đồng hồ máy chủ / máy người dùng.
6. Chữ hiển thị theo `GLOSSARY_JA.md` / `ja.ts`; từ mới ghi vào GLOSSARY mục 10 để BrSE review.
7. Không dùng `service_role`; không có khóa, mật khẩu, URL môi trường trong code, issue, commit.
8. PR được người khác review; CI xanh; bộ hồi quy E14-01 xanh.
9. Làm khác thiết kế → ghi vào [PREMISE.md](PREMISE.md) (mục 1 spec sửa hoặc mục 2 giả định) và báo PL; không tự sửa ngầm.

### 1.4 Dùng epic → issue → sub-issue trên GitHub Project

| Cấp | Trên GitHub | Mã tạm |
|---|---|---|
| Epic | 1 issue nhãn `epic`; mô tả phạm vi + spec gốc | `E12` |
| Issue | Sub-issue của epic (tính năng sub-issues của GitHub) | `E12-05` |
| Sub-issue | Sub-issue của issue (cấp 3), theo lớp | `E12-05-DB`, `E12-05-API`, `E12-05-T` (hậu tố `-DB` / `-API` / `-UI` / `-T`) |

- Tiêu đề issue bắt đầu bằng mã tạm, ví dụ `[E12-05] Ghi 入金日 và khóa kết quả`. Sau khi tạo, lưu bảng mã tạm ↔ số issue để chuyển `depends_on` thành "blocked by #n".
- Thân issue: `spec_refs`, `note`, phụ thuộc, checklist DoD (mục 1.3) – chỉ ghi **mã**, không chép câu chữ tài liệu khách (CLAUDE.md – quy tắc PUBLIC).
- Nhãn: lớp (`db`, `api`, `ui`, `test`); tính chất (`reuse-prototype`, `constraint`, `incentive`, `migration`, `tablet`, `security`, `spike`, `infra`); trạng thái (`clarification`, `blocked`).
- Field của Project: **Status** (Backlog / Ready / In progress / Review / Done), **Epic**, **Type** (epic / issue / sub-issue), **Role** (PL, BrSE, BE-1, BE-2, FE-1, QA-1), **SWP** và **Giờ** (để trống – điền ở bước chấm SWP).
- View gợi ý: Board theo Status · Table nhóm theo Epic · "Làm rõ / chờ khách" (`clarification` + `blocked`) · "完納奨励金" (epic E12) · "Ràng buộc đặc thù" (`constraint`).

### 1.5 Danh sách epic

<!-- BEGIN:EPIC_TABLE -->
| Mã | Epic | Spec gốc | Issue | Sub-issue | Phạm vi |
|---|---|---|---|---|---|
| E01 | Nền tảng dự án và quy ước chung | ADR-001, ADR-011 | 7 | 0 | Đưa prototype LAB-2 thành codebase của hệ thống thật: CI, migration, môi trường, chuẩn lỗi / log, từ điển tiếng Nhật. |
| E02 | Lưu vết chỉ thêm và quyền database | ADR-007, ADR-002 | 4 | 7 | Chặn sửa / xóa lưu vết ở mức quyền và trigger; ghi lưu vết cùng transaction; SC-20 có phân trang và che dữ liệu. |
| E03 | Chợ và 営業日 theo cấu hình chợ | P-01, ADR-004, DD-02 | 5 | 6 | Mọi dữ liệu theo market_id; 営業日 tính ở database theo mốc chuyển ngày của phiên bản quy tắc đang hiệu lực. |
| E04 | Quy tắc vận hành theo chợ có phiên bản (SC-18) | ADR-008, P-02, D-02, D-03, D-35 | 5 | 8 | rule_versions + market_rules; người soạn ≠ người duyệt; phiên bản đã duyệt không sửa. Là nền của 営業日 (E03) và 完納奨励金 (E12). |
| E05 | Xác thực và phân quyền nhiều vai trò | ADR-002, ADR-003, DD-01 | 9 | 11 | user_roles nhiều vai trò / người theo chợ, has_role ở RLS, khóa tài khoản, lưu vết đăng nhập, quản lý người dùng SC-21. |
| E06 | Người tham gia và 許可 / 承認 hai luồng | ADR-009, P-03, L1, L3 | 9 | 7 | Trạng thái xét duyệt riêng cho 許可 và 承認, điều kiện, lịch sử xét duyệt, L1 theo trạng thái giấy. |
| E07 | Lô hàng và 目利き | L4, L11, P-04 | 4 | 0 | ロット登録 / 目利き trên tablet, danh sách lô còn hàng; chủ yếu tận dụng prototype. |
| E08 | Giao dịch 相対取引 / せり / 取消 | DD-03, ADR-005, L1, L2, L4, G-04 | 7 | 6 | Gom kiểm luật + ghi + lưu vết vào hàm database 1 transaction; giữ trigger L4 khóa lô, không tự hủy. |
| E09 | 修正依頼 (sửa sau khi chốt) | ADR-006, DD-04, L7 | 4 | 3 | Duyệt / từ chối trong 1 transaction, lý do từ chối ở cột riêng, người tạo ≠ người quyết định. |
| E10 | 引渡し (giao hàng nhiều lần) | L5, P-06 | 4 | 2 | Chặn giao vượt ở database, ghi + lưu vết cùng transaction; được giao cho ngày đã 締め (P-06). |
| E11 | 締め và xuất CSV kế toán | DD-05, ADR-010, L6 | 7 | 9 | close_day 1 transaction có snapshot; xuất CSV ghi lịch sử, mã băm, cờ cần xuất lại. |
| E12 | 完納奨励金 (thưởng trả đúng hạn) | DD-06, SC-17, L8, D-02, D-03, D-26, D-31, P-02 | 10 | 6 | Epic ràng buộc đặc thù: chạm tiền, 営業日, phiên bản quy tắc và khóa kết quả. Tính sai = trả sai tiền cho người mua. |
| E13 | Offline hẹp cho tablet (ロット登録, 引渡し入力) | ADR-012, P-05, M6 | 6 | 11 | PWA: hàng đợi trên tablet, chống trùng bằng client_uuid, server kiểm luật khi đồng bộ. |
| E14 | Kiểm thử hệ thống và chuẩn bị go-live | T01..T17, ADR-002 | 4 | 5 | Hồi quy toàn bộ luật trên cấu trúc mới, test phân quyền gọi thẳng database, nghiệm thu với BrSE. |
<!-- END:EPIC_TABLE -->

---

## 2. Bảng Spec → issue

Bảng sinh từ `spec_refs` của backlog.json (1 spec có thể ứng với nhiều issue). Cột Epic gồm cả epic chỉ nhắc spec ở cấp epic.

<!-- BEGIN:SPEC_TABLE -->
### 2.1 Màn hình (SC)

| Spec (mã) | Epic | Issue / sub-issue |
|---|---|---|
| SC-01 | E05 | E05-05, E05-05-UI |
| SC-02 | E06 | E06-07 |
| SC-03 | E01, E06 | E01-05, E01-06, E06-04, E06-04-T, E06-05, E06-05-UI1, E06-05-UI2, E06-06, E06-08, E06-09 |
| SC-04 | E06 | E06-07 |
| SC-05 | E07, E13, E14 | E07-01, E13-04, E13-04-UI3, E14-04-T1 |
| SC-06 | E07 | E07-04 |
| SC-07 | E07 | E07-03 |
| SC-08 | E08, E14 | E08-05, E14-04-T1 |
| SC-09 | E08 | E08-07 |
| SC-10 | E08, E14 | E08-06, E14-04-T1 |
| SC-11 | E09 | E09-04 |
| SC-12 | E01, E09, E14 | E01-06, E09-03, E14-04-T2 |
| SC-13 | E10 | E10-03 |
| SC-14 | E10, E13, E14 | E10-04, E13-04, E13-04-UI4, E14-04-T1 |
| SC-15 | E11, E14 | E11-02, E11-02-UI, E11-04, E14-04-T2 |
| SC-17 | E01, E12, E14 | E01-05, E12-01, E12-04, E12-06, E12-06-UI1, E12-06-UI2, E12-09, E12-10, E14-04-T3 |
| SC-18 | E01, E04, E14 | E01-05, E01-06, E04-04, E04-05, E04-05-UI1, E04-05-UI2, E14-04-T3 |
| SC-19 | E11, E14 | E11-04, E11-06, E11-07, E14-04-T2 |
| SC-20 | E02 | E02-03, E02-03-UI |
| SC-21 | E05 | E05-06, E05-06-UI, E05-06-T, E05-07 |
| SC-24 | E01, E13 | E01-05, E13-05, E13-05-UI1, E13-05-UI2 |
| SC-25 | E03, E05, E14 | E03-04, E05-03, E14-04 |

### 2.2 API

| Spec (mã) | Epic | Issue / sub-issue |
|---|---|---|
| API-02 | E05 | E05-05, E05-05-API |
| API-04 | E03 | E03-04 |
| API-07 | E06 | E06-06 |
| API-08 | E06 | E06-04, E06-04-API |
| API-09 | E06 | E06-04, E06-04-API |
| API-11 | E06 | E06-04, E06-04-API |
| API-12 | E07 | E07-01 |
| API-13 | E07 | E07-03 |
| API-14 | E07 | E07-02 |
| API-15 | E08 | E08-02, E08-02-API |
| API-16 | E08 | E08-03, E08-03-API |
| API-17 | E08 | E08-04 |
| API-18 | E08 | E08-04 |
| API-19 | E10 | E10-02, E10-02-API |
| API-20 | E10 | E10-03 |
| API-21 | E13 | E13-03, E13-03-API, E13-04-UI5, E13-05-UI2 |
| API-22 | E09 | E09-04 |
| API-23 | E09 | E09-02, E09-02-API |
| API-24 | E09 | E09-02, E09-02-API |
| API-25 | E09 | E09-03 |
| API-26 | E11 | E11-02, E11-02-API |
| API-27 | E11 | E11-01, E11-01-API |
| API-28 | E11 | E11-03, E11-03-API |
| API-29 | E11 | E11-03, E11-03-API, E11-07 |
| API-30 | E12 | E12-06, E12-06-API, E12-06-UI1, E12-09 |
| API-31 | E12 | E12-05, E12-05-API, E12-06-UI2 |
| API-32 | E12 | E12-04, E12-06-UI2 |
| API-33 | E04, E12 | E04-02, E04-05, E04-05-UI1, E12-06, E12-06-UI1 |
| API-34 | E04 | E04-03, E04-03-API, E04-05, E04-05-UI2 |
| API-35 | E04 | E04-03, E04-03-API, E04-05, E04-05-UI2 |
| API-36 | E04 | E04-03, E04-03-API, E04-05, E04-05-UI2 |
| API-37 | E04 | E04-03, E04-03-API, E04-05, E04-05-UI2 |
| API-38 | E05 | E05-06, E05-06-API |
| API-39 | E05 | E05-06, E05-06-API |
| API-40 | E05 | E05-06, E05-06-API |
| API-41 | E05 | E05-06, E05-06-API |
| API-42 | E05 | E05-07, E05-09 |
| API-43 | E02 | E02-03, E02-03-API |

### 2.3 Database – chênh lệch thiết kế ↔ prototype (D)

| Spec (mã) | Epic | Issue / sub-issue |
|---|---|---|
| D-01 | E03 | E03-01 |
| D-01..D-40 | E01 | E01-02 |
| D-02 | E04, E12 | E04-01, E04-01-DB1, E12-01 |
| D-03 | E04, E12 | E04-01, E04-01-DB1, E04-01-DB2, E12-01 |
| D-04 | E04, E12 | E04-01-DB2, E12-07 |
| D-05 | E05 | E05-01, E05-01-DB |
| D-06 | E06 | E06-02 |
| D-07 | E11 | E11-03, E11-03-DB |
| D-08 | E06, E11 | E06-08, E11-03-DB |
| D-09 | E03 | E03-02, E03-02-DB1, E03-02-DB2, E03-02-API |
| D-10 | E05 | E05-08 |
| D-11 | E05 | E05-04 |
| D-12 | E06 | E06-06 |
| D-13 | E06 | E06-01, E06-01-DB, E06-01-T |
| D-14 | E06 | E06-01, E06-01-DB, E06-04-DB, E06-05-UI2 |
| D-15 | E06 | E06-01, E06-01-DB, E06-01-T |
| D-16 | E03, E07 | E03-02, E03-02-DB1, E07-04 |
| D-17 | E13 | E13-02, E13-04-UI3 |
| D-18 | E13 | E13-02, E13-04-UI4 |
| D-19 | E08 | E08-01, E08-06 |
| D-20 | E08 | E08-01 |
| D-21 | E08 | E08-01, E08-03, E08-03-DB, E08-07 |
| D-22 | E09 | E09-01 |
| D-23 | E09 | E09-01, E09-02-DB |
| D-24 | E09 | E09-01 |
| D-25 | E03, E11 | E03-02, E03-02-DB2, E11-01, E11-01-DB2, E11-02-API |
| D-26 | E12 | E12-05, E12-05-DB, E12-05-T, E12-07 |
| D-27 | E01, E12 | E01-07, E12-05, E12-05-DB |
| D-28 | E02 | E02-02, E02-02-DB1, E02-02-T |
| D-29 | E03 | E03-03, E03-03-DB |
| D-30 | E05 | E05-02, E05-02-DB1, E05-02-DB2, E05-02-DB3 |
| D-31 | E12 | E12-02 |
| D-32 | E09 | E09-02, E09-02-DB |
| D-33 | E02, E08, E10, E11, E12 | E02-02, E02-02-DB1, E02-02-DB2, E08-02, E08-02-DB, E08-03, E08-03-DB, E10-02, E10-02-DB, E11-01, E11-01-DB1, E12-05, E12-05-DB |
| D-34 | E02 | E02-01 |
| D-35 | E04 | E04-01, E04-01-DB1, E04-01-T |
| D-36 | E05 | E05-01, E05-01-DB, E05-01-T, E05-06 |
| D-37 | E02, E05, E14 | E02-03, E02-03-DB, E05-02, E05-02-DB3, E05-02-T, E14-03, E14-03-T2 |
| D-38 | E05 | E05-05, E05-05-API, E05-09 |
| D-39 | E10 | E10-01 |
| D-40 | E02, E05, E14 | E02-01, E05-09, E14-03, E14-03-T1 |

### 2.4 Detail design (DD) và ADR

| Spec (mã) | Epic | Issue / sub-issue |
|---|---|---|
| DD-01 | E01, E05 | E01-04, E05-03, E05-04, E05-05, E05-05-API, E05-09 |
| DD-02 | E01, E03, E13 | E01-04, E03-03, E03-03-DB, E03-03-T, E13-03 |
| DD-03 | E01, E06, E08 | E01-04, E06-03, E08-02, E08-02-DB, E08-02-API |
| DD-04 | E01, E09, E11, E12 | E01-04, E09-02, E09-02-DB, E11-04, E12-09 |
| DD-05 | E01, E11 | E01-04, E11-01, E11-01-DB1, E11-03-T |
| DD-06 | E01, E12 | E01-04, E12-01, E12-02, E12-03, E12-04, E12-05, E12-06-API, E12-09 |
| ADR-001 | E01 | E01-01, E01-02, E01-03 |
| ADR-002 | E02, E05, E14 | E05-02, E05-09, E14-03 |
| ADR-003 | E05, E14 | E05-01, E05-02-DB1, E14-02 |
| ADR-004 | E03, E04, E12 | E03-03, E03-03-T, E03-05, E04-03-DB, E12-03 |
| ADR-005 | E08 | E08-02 |
| ADR-006 | E09 | (cấp epic) |
| ADR-007 | E02 | E02-01, E02-02, E02-04 |
| ADR-008 | E03, E04, E12 | E03-01, E04-01, E04-02, E04-03, E04-03-DB, E04-03-T, E04-04, E12-08 |
| ADR-009 | E01, E06 | E01-05, E01-06, E06-01, E06-02, E06-03, E06-04, E06-04-DB, E06-05, E06-05-UI1, E06-05-UI2, E06-09 |
| ADR-010 | E11 | E11-03, E11-03-T, E11-04, E11-05, E11-06 |
| ADR-011 | E01 | E01-05, E01-06 |
| ADR-012 | E13 | E13-01, E13-01-UI1, E13-01-UI2, E13-03, E13-03-API, E13-03-T, E13-04, E13-04-UI2, E13-05, E13-05-UI1, E13-05-UI2, E13-06 |

### 2.5 Tiền đề (P) và luật nghiệp vụ (L, G)

| Spec (mã) | Epic | Issue / sub-issue |
|---|---|---|
| L1 | E03, E06, E08, E10, E13 | E03-05, E06-03, E10-02, E10-02-DB, E13-03 |
| L1..L12 | E14 | E14-04 |
| L2 | E06, E08 | E06-06, E08-02 |
| L3 | E06 | E06-04, E06-04-T |
| L4 | E07, E08 | E07-02 |
| L5 | E10, E13 | E10-01, E13-03, E13-03-T |
| L6 | E08, E11 | E08-03, E08-03-DB |
| L7 | E09, E14 | E09-02, E09-02-T, E14-02 |
| L8 | E03, E12, E14 | E03-05, E12-02, E12-03, E12-08, E14-04-T3 |
| L9 | E02 | E02-02 |
| L10 | E05 | E05-04 |
| L11 | E03, E07 | E03-03 |
| L12 | E05 | E05-02, E05-03 |
| G-01 | E08 | E08-02, E08-02-DB |
| G-02 | E08 | E08-03, E08-03-DB, E08-03-T |
| G-03 | E07 | E07-02 |
| G-04 | E08 | E08-02, E08-02-T |
| G-05 | E08 | E08-01 |
| G-06 | E10 | E10-02, E10-02-DB |
| G-07 | E08, E09 | E08-03, E08-03-DB, E08-03-T, E09-01 |
| G-08 | E09 | E09-02 |
| G-09 | E08 | E08-01 |
| G-10 | E08 | E08-02 |
| G-11 | E02 | E02-02, E02-02-T |
| G-12 | E01 | E01-07 |
| G-13 | E09 | E09-04 |
| G-14 | E10 | E10-03 |
| G-15 | E08 | E08-04 |
| G-16 | E06 | E06-04 |
| G-17 | E09 | E09-02 |
| G-18 | E11 | E11-01, E11-01-DB1, E11-01-T |
| G-19 | E09 | E09-01 |
| G-20 | E09 | E09-01 |
| G-21 | E11 | E11-01, E11-01-DB1, E11-01-T |
| G-22 | E12 | E12-05, E12-05-DB, E12-05-T |
| G-23 | E12 | E12-05, E12-05-DB, E12-05-T, E12-10 |
| G-24 | E05 | E05-01, E05-01-T, E05-06 |
| G-25 | E09 | E09-02 |
| G-26 | E09, E14 | E09-02-T, E14-02 |
| G-27 | E11 | E11-01 |
| G-28 | E01 | E01-07 |
| G-29 | E01 | E01-07 |
| G-30 | E11 | E11-03 |
| G-31 | E02 | E02-03, E02-03-API |
| P-01 | E03 | E03-01, E03-02, E03-02-API |
| P-02 | E03, E04, E12 | E03-05, E04-01, E04-01-T, E12-01, E12-05, E12-05-T, E12-10 |
| P-03 | E06 | E06-01 |
| P-04 | E01, E07, E10, E13 | E01-03, E07-01, E07-03, E10-04, E13-01, E13-01-UI1 |
| P-05 | E13 | E13-01, E13-01-UI2, E13-04-UI2 |
| P-06 | E10, E11 | E10-02, E10-02-DB, E11-01 |
| P-07 | E02, E05 | E02-03, E02-03-DB, E02-03-T, E05-02 |
| P-10 | E04 | E04-01-DB1 |
| P-12 | E04 | E04-01-DB2 |
| P-14 | E02 | E02-02-DB1 |
| P-15 | E05 | E05-02-DB1 |
| P-16 | E02 | E02-02-DB2 |

### 2.6 Common spec (CS)

| Spec (mã) | Epic | Issue / sub-issue |
|---|---|---|
| CS-01 | E05 | E05-04 |
| CS-02 | E05 | E05-03 |
| CS-03 | E05 | E05-03 |
| CS-04 | E05, E14 | E05-03, E14-03, E14-03-T1 |
| CS-05 | E03 | E03-03, E03-04 |
| CS-06 | E03, E08 | E03-04, E08-05 |
| CS-07 | E06 | E06-03, E06-07 |
| CS-08 | E08 | E08-02 |
| CS-09 | E06 | E06-04, E06-04-API |
| CS-10 | E08 | E08-02, E08-02-T |
| CS-11 | E10 | E10-01 |
| CS-12 | E08, E10 | E08-03, E08-03-T, E10-02 |
| CS-13 | E04, E09, E14 | E04-01-T, E04-03, E04-03-T, E04-05-UI2, E09-02, E14-02 |
| CS-14 | E12 | E12-01, E12-02, E12-03 |
| CS-15 | E02 | E02-01, E02-02, E02-02-DB2, E02-02-T |
| CS-19 | E01 | E01-04 |
| CS-20 | E01 | E01-04 |
| CS-21 | E05 | E05-04 |
| CS-22 | E13 | E13-04, E13-04-UI1, E13-04-UI2, E13-04-UI3, E13-04-UI4, E13-04-UI5 |
| CS-23 | E05 | E05-03 |
| CS-24 | E02, E05, E14 | E02-03, E02-03-DB, E02-03-UI, E02-03-T, E05-02, E14-03, E14-03-T2 |
| CS-25 | E08, E11 | E08-05, E11-02, E11-02-UI |

### 2.7 Kịch bản test (T) và mã khác (M, W, Q)

| Spec (mã) | Epic | Issue / sub-issue |
|---|---|---|
| T01..T17 | E03, E14 | E03-02-T, E14-01 |
| T03 | E08 | E08-02-T |
| T04 | E08 | E08-02-T |
| T05 | E08 | E08-02-T |
| T06 | E06 | E06-01-T |
| T07 | E10 | E10-01 |
| T08 | E10 | E10-01 |
| T09 | E08, E11 | E08-03-T, E11-01-T |
| T10 | E09 | E09-02-T |
| T11 | E05, E09 | E05-02-T, E09-02-T |
| T12 | E05 | E05-02-T |
| T13 | E12 | E12-07 |
| T14 | E02 | E02-03-T |
| T15 | E03, E13 | E03-03-T, E13-03-T |
| T16 | E05 | E05-06-T |
| T17 | E05 | E05-02-T |
| M3 | E05 | E05-07 |
| M4 | E12 | E12-08 |
| M5 | E06 | E06-08 |
| M6 | E13 | (cấp epic) |
| M11 | E05 | E05-05 |
| M12 | E01 | E01-06 |
| M_110 | E09 | E09-03 |
| M_111 | E11 | E11-04 |
| W-05 | E08 | E08-05 |
| W-08 | E12 | E12-01 |
| Q6 | E11 | E11-05 |
| Q8 | E13 | E13-06 |

<!-- END:SPEC_TABLE -->

### 2.8 Phần spec chưa thành issue và vì sao

| Spec | Vì sao chưa thành issue |
|---|---|
| SC-16 紛争対応 | Ngoài phạm vi (screen_list, LAB2_SCOPE mục 5): không nằm trên luồng chính. |
| SC-22 買受人向けページ | Ngoài phạm vi, chờ Q7; LAB-4 PREMISE mục 4 chốt người dùng bên ngoài không đăng nhập. |
| SC-23 通知 / dịch vụ email (M7) | Thiết kế ghi "tương lai" (architecture 4.1); chưa có spec màn hình. Mời người dùng (E05-07) đi bằng cơ chế riêng. |
| SC-04 期限切れ警告 | Đã gộp vào SC-02 (LAB-4 PREMISE dòng 17) → nằm trong E06-07, không có issue riêng. |
| MFA (M1, architecture 4.5) | SC-01 mục 5 ghi "thiết kế sau"; chưa có screen spec / luồng → để mở, xem GAP-25. |
| 12 báo cáo batch (M8) | Không có trong bộ thiết kế LAB-4 (chỉ CSV kế toán – ADR-010). |
| Chuyển dữ liệu từ hệ thống cũ (M9, F-23) | Architecture 4.1 ghi "ngoài prototype", chưa thiết kế. Chỉ có chuyển dữ liệu prototype → cấu trúc mới (các issue nhãn `migration`). |
| Function LAB-1 F-03, F-04, F-14, F-19, F-20, F-21 (ánh xạ do PL đưa ở bước estimate) | Không có màn hình / API / detail design tương ứng trong bộ thiết kế LAB-4 → chưa thành issue; so sánh với LAB-1 ở [estimate.md](estimate.md) mục 5. |
| Che dữ liệu cá nhân theo vai trò + log người xem (M10) ngoài D-37 | Thiết kế mới chỉ cụ thể phần admin không đọc dữ liệu nghiệp vụ (D-37, P-07) → đã có E05-02, E02-03; phần "log người xem" chưa có thiết kế. |
| Thông báo, dữ liệu cá nhân tách khỏi SC-21 | LAB-4 PREMISE dòng 18: "tách thành màn hình / chức năng riêng khi làm thật" nhưng chưa có spec. |
| 5 đề xuất upsale LAB-3 (dashboard KPI, vận hành giờ chợ, mô phỏng tỷ lệ, QR, API kế toán) | LAB-4 PREMISE dòng 22: không thuộc bộ thiết kế này. |
| Màn hình chọn chợ | P-01 (LAB-4 PREMISE dòng 43): go-live 1 chợ, không có màn hình chọn chợ. |
| API-01, API-03, API-05, API-06, API-10 | Giữ nguyên như prototype (api_list: "Hiện có", không sửa); chỉ được kiểm lại trong hồi quy E14-01 và khi thêm `market_id` (E03-02-API). |
| CS-16 định dạng, CS-17 bắt buộc nhập, CS-18 chống bấm 2 lần | Đã có ở prototype (`format.ts`, form chung); áp dụng như điều kiện DoD cho mọi issue `ui`, không tách issue. |

---

## 3. Hạng mục chịu ràng buộc đặc thù

Các hạng mục dưới đây được **tách issue riêng** (nhãn `constraint`) thay vì gộp vào issue màn hình, vì sai ở đây là sai tiền, sai ngày hoặc sai trách nhiệm – và phải test được độc lập với giao diện.

### 3.1 完納奨励金 – EPIC RIÊNG E12 (DD-06, SC-17, L8, D-02, D-03, D-26, D-31, P-02)

| Ràng buộc | Issue | Vì sao tách riêng |
|---|---|---|
| Chọn **phiên bản quy tắc** có hiệu lực tại 支払期限 (料率, 係数, 猶予) | E12-01 | Chọn sai phiên bản = trả sai tiền dù công thức đúng; phụ thuộc E04 (D-02, D-03), cần test riêng với nhiều phiên bản / ngày hiệu lực. |
| **Tính bằng số nguyên + làm tròn xuống** (料率 / 係数 thành phân số, 係数 đọc từ `market_rules`) | E12-02 | Sai số số thực làm lệch 1 yên; bỏ 1.1 viết cứng (D-31). Hàm thuần, test bằng bảng giá trị biên. |
| **期限内 / 期限超過**, không ân hạn, so sánh theo 営業日 | E12-03 | Biên ngày (đúng hạn / trễ 1 ngày / 01:30) là nơi dễ sai nhất; `grace_days = 0` phải chặn ở database (LAB-4 PREMISE dòng 37). |
| **Xem trước** (API-32) | E12-04 | Chỉ đọc, không lưu vết; phải ra cùng kết quả với lúc ghi (dùng chung hàm E12-02, E12-03). |
| **Ghi 入金日 và khóa kết quả** (`incentive_amount`, `rule_version_id`, ghi 1 lần) | E12-05 (-DB, -API, -T) | Chạm tiền + khóa dòng + lưu vết cùng transaction; đổi 料率 sau này không được làm đổi số đã lưu (P-02, D-26). |
| **Màn hình** SC-17 | E12-06 (-API, -UI1, -UI2) | Hiển thị công thức từng dòng, phiên bản đã dùng; tách khỏi logic tính để test logic không cần giao diện. |
| Chuyển dữ liệu 完納奨励金 (lưu kết quả cho dòng đã trả gắn phiên bản v1 do E04-01-DB2 tạo; bỏ `incentive_rates`) | E12-07 | Prototype tính lại mỗi lần xem; phải chốt số đã hiển thị cho khách = số lưu (T13). |
| **Test vector chờ dữ liệu Phụ lục C** | E12-08 (`blocked`) | Dữ liệu từ khách chưa có (LAB2_SCOPE M4, ADR-008); dựng khung trước để khi có chỉ thêm file. |
| Nguồn 請求 và 修正依頼 sau khi lập 請求 | E12-09 (`clarification`) | Thiết kế chưa có chỗ tạo `payments` (GAP-01, GAP-02). |
| Sửa 入金日 ghi nhầm | E12-10 (`clarification`) | Kết quả đã khóa; quy trình sửa chưa thiết kế (GAP-03). |

### 3.2 Các ràng buộc đặc thù khác

| Ràng buộc | Issue | Vì sao tách riêng |
|---|---|---|
| **営業日 theo chợ** (mốc chuyển ngày theo phiên bản quy tắc, không theo ngày lịch / đồng hồ máy) | E03-03 (-DB, -T), E04-01, E03-05, E13-03 (offline theo `client_recorded_at`), E12-03 | Một nguồn duy nhất cho mọi hạn (L1, L8, G-21, G-22); đổi chữ ký hàm ảnh hưởng `default` của cột → phải giữ hàm tương thích và test riêng (ADR-004, D-29). |
| **Quy tắc theo chợ có phiên bản**, phiên bản đã duyệt không sửa | E04-01, E04-03 | Nền chung của 営業日 và 完納奨励金; trigger khóa + check người soạn ≠ người duyệt (D-35). |
| **許可 / 承認 hai luồng** (trạng thái riêng theo `kind`, 条件, 決定者（開設者側） ≠ 登録者) | E06-01, E06-02, E06-03, E06-04, E06-05, E06-09, E01-06 | Hai tập trạng thái khác nhau trong 1 bảng (ADR-009 phương án C); L1 đổi thành "đúng loại + đúng trạng thái + còn hạn" dùng chung cho 確定, 引渡し, đồng bộ offline → hàm riêng E06-03. |
| **締め** (không mở lại, G-18, G-21, snapshot; chặn 確定 / 取消 / sửa trực tiếp nhưng **cho** 引渡し) | E11-01, E08-02 (G-04), E08-03 (L6), E10-02 (P-06), E11-04 | Khóa sổ là điểm chốt số liệu cho kế toán; mỗi nơi chặn / không chặn khác nhau → mỗi nơi có test riêng. |
| **Người tạo ≠ người duyệt** (修正依頼, phiên bản quy tắc) + システム管理者 không kiêm / không tự gán | E09-02, E04-03, E05-01, E14-02 | Kiểm theo **bản ghi**, không theo vai trò (ADR-003 mục 4); khi 1 người kiêm nhiều quyền mới thật sự bị thử (G-26) → test riêng. |
| L4 tồn lô: khóa lô ở database, **không tự hủy** | E08-02, E09-02 | Tranh chấp đồng thời chỉ test được ở database (ADR-005). |
| Lưu vết chỉ thêm, cùng transaction | E02-01, E02-02 | Đổi quyền / trigger ở mức database ảnh hưởng mọi bảng (D-34, D-40, G-11). |
| システム管理者 không xem dữ liệu nghiệp vụ | E05-02, E02-03, E14-03 | Viết lại toàn bộ policy; phải test bằng gọi thẳng database, không chỉ giao diện (D-37, P-07). |

---

## 4. Chỗ hở / mâu thuẫn phát hiện khi chia task

**Lưu ý cách xử lý:** repo thiết kế LAB-4 chỉ đọc trong LAB-5 (CLAUDE.md – quy tắc cách ly). Chỗ xử lý bằng **giả định** hoặc phải **sửa spec** được ghi ở [PREMISE.md](PREMISE.md) của repo này (mục 1: spec sửa, mục 2: giả định P-08…P-16, mục 3: hướng đã chốt); bảng dưới trỏ đúng dòng. Chỗ đã được thiết kế LAB-4 xử lý từ trước thì trỏ dòng của LAB-4 `specs/PREMISE.md`.

### 4.1 Bảng chỗ hở / mâu thuẫn

| # | Spec | Chỗ hở / mâu thuẫn | Xử lý |
|---|---|---|---|
| GAP-01 | SC-17, DD-06, API list, er-design (`payments`) | Không có API / màn hình nào **tạo** `payments` (対象期間, 請求金額, 支払期限). Prototype nạp bằng SQL. Không rõ ai lập 請求, khi nào, 請求金額 tính từ giao dịch nào. | **Tạo issue làm rõ** E12-09. |
| GAP-02 | DD-04 bước 9, DD-06, ADR-010 | 修正依頼 được duyệt sau khi đã lập 請求 (hoặc đã ghi 入金日) làm 請求金額 lệch với giao dịch; thiết kế chỉ đánh dấu CSV cần xuất lại, không nói gì về 請求 / 奨励金. | **Tạo issue làm rõ** E12-09 (cùng GAP-01). |
| GAP-03 | SC-17 mục 5, G-23, P-02 | 入金日 chỉ ghi 1 lần, kết quả bị khóa; "quy trình sửa riêng" chưa thiết kế → ghi nhầm thì không có đường sửa. | **Tạo issue làm rõ** E12-10. |
| GAP-04 | DD-06 sơ đồ + bước 5–8 ↔ D-33, CS-15 | DD-06 vẽ API tự khóa dòng, tính, ghi, ghi lưu vết (nhiều lệnh), trong khi D-33 / CS-15 yêu cầu 入金日 chạy trong **hàm database 1 transaction** cùng lưu vết. | **Giả định** – **P-08** → [PREMISE.md](PREMISE.md) dòng 22 (spec sửa: dòng 11): làm hàm `record_payment` theo D-33; DD-06 cần vẽ lại sơ đồ. Thực hiện ở E12-05-DB. |
| GAP-05 | LAB-4 PREMISE dòng 37, ADR-004 ↔ DD-06 bước 3, SC-17 D-3 | Luật nói 完納奨励金 tính theo 営業日, nhưng 入金日 là ngày trên chứng từ (ngày lịch) và 支払期限 là `date`; không nói 2 giá trị so sánh trên trục nào. | **Giả định** – **P-09** → [PREMISE.md](PREMISE.md) dòng 23: 入金日, 支払期限 là `date` của 営業日; so sánh trực tiếp; 営業日 hiện tại chỉ là mặc định + giới hạn trên (G-22). Test biên ở E12-03. |
| GAP-06 | L8, CS-14, ADR-008 (`incentive_rate` 0 ≤ x < 1), er-design (`amount_due numeric`) | Không quy định số chữ số thập phân của 料率 / 係数; `amount_due` kiểu `numeric` có thể lẻ → "đổi sang phân số" (DD-06) không xác định. | **Giả định** – **P-10** → [PREMISE.md](PREMISE.md) dòng 24 (spec sửa: dòng 15): `amount_due` là số nguyên yên ≥ 0; 料率 tối đa 6 chữ số thập phân, 係数 tối đa 3; check constraint ở E04-01-DB1; phép tính ở E12-02. |
| GAP-07 | LAB2_SCOPE M4, ADR-008 | Test vector Phụ lục C để kiểm 完納奨励金 chưa có. | **Để mở** – chờ khách gửi dữ liệu; không chặn vì đã có T13 + vector tự soạn. Khung test E12-08 (`blocked`). |
| GAP-08 | DD-02 bước 2–3 ↔ ADR-008 (`effective_from` là 営業日), ADR-004 | DD-02 chọn phiên bản theo **ngày lịch** (tránh vòng lặp), ADR-008 coi `effective_from` là 営業日 → trong khoảng 00:00 → mốc chuyển ngày của ngày `effective_from`, mốc mới đã áp dụng dù 営業日 vẫn là hôm trước. | **Giả định** – **P-11** → [PREMISE.md](PREMISE.md) dòng 25: theo DD-02; vì chỉ đổi mốc khi chợ nghỉ (ADR-004) nên khoảng chồng không có giao dịch. Test ở E03-03-T. |
| GAP-09 | ADR-004 (chỉ đổi mốc khi chợ nghỉ), L8 / LAB-4 PREMISE dòng 37 (không ân hạn), L1 | Thiết kế không có **lịch 休市日**: không biết 支払期限 / 有効期限 rơi vào ngày chợ nghỉ thì xử lý thế nào, và hệ thống không kiểm được "đổi mốc khi chợ nghỉ". | **Tạo issue làm rõ** E03-05. |
| GAP-10 | ADR-008 (không duyệt `effective_from` ≤ 営業日 hiện tại; `approved_by <> drafted_by`) ↔ DD-02 bước 3, D-03 (phiên bản đầu hiệu lực 2026-04-01) | Phiên bản khởi tạo bắt buộc có từ đầu, hiệu lực trong quá khứ → không đi qua được luồng duyệt; ai là người soạn / người duyệt của bản này? | **Giả định** – **P-12** → [PREMISE.md](PREMISE.md) dòng 26 (spec sửa: dòng 16): phiên bản v1 tạo bằng migration (người dùng tự chạy); 2 tài khoản 精算担当 khác nhau do PL chỉ định ghi làm người soạn / người duyệt; ngoại lệ ngày quá khứ chỉ áp dụng cho v1. Thực hiện ở E04-01. |
| GAP-11 | SC-03 STD-02 (審査開始), STD-07 (承認結果) ↔ API-11 | Không có API cho chuyển 申請中 → 審査中; API-11 chỉ mô tả 許可 / 不許可, không nói 届出 → 承認. | **Giả định** – **P-13** → [PREMISE.md](PREMISE.md) dòng 27 (spec sửa: dòng 12): API-11 nhận mọi chuyển trạng thái hợp lệ theo `kind`, database kiểm tính hợp lệ. Thực hiện ở E06-04. |
| GAP-12 | ADR-009 (câu hỏi mở), SC-03 mục 5 | Có thu hồi / đình chỉ giấy không; 承認 có bị từ chối không (không có trạng thái tương ứng 不許可); 承認 ghi người quyết định như 許可 không. | **Tạo issue làm rõ** E06-09. |
| GAP-13 | GLOSSARY mục 3 (承認 = loại giấy) ↔ mục 5, 7 (承認 = duyệt, 承認待ち, 承認者); SC-03 ↔ SC-12, SC-18 | Cùng chữ 承認 cho 2 nghĩa; SC-03 dùng 承認者（開設者側）, SC-12 dùng 承認者 cho người duyệt phiếu; `status = 'approved'` ở 3 bảng → dễ nhầm trên giao diện và lưu vết. | **Tạo issue làm rõ** E01-06 (BrSE). |
| GAP-14 | DD-01 bước 4, D-38 ↔ D-40, ADR-002, er-design (`audit_logs` insert: `actor = auth.uid()`) | Ghi `LOGIN_FAILED` khi **chưa có phiên**: `anon` bị thu hồi quyền, policy insert cần `auth.uid()`, không dùng `service_role` → theo thiết kế hiện tại không ghi được. | **Tạo issue làm rõ** (spike) E05-09. |
| GAP-15 | API-42, M3 ↔ architecture 2.2, DD-01 bước 7 | Mời người dùng qua Supabase Auth cần quyền quản trị (khóa `service_role`), mâu thuẫn "không dùng service_role ở bất kỳ đâu". | **Tạo issue làm rõ** (spike) E05-09 (cùng GAP-14). |
| GAP-16 | D-09 (`audit_logs.market_id` not null) ↔ D-38 | Lưu vết đăng nhập xảy ra trước khi biết chợ (người chưa có quyền / sai mật khẩu) → không có `market_id`. | **Giả định** – **P-14** → [PREMISE.md](PREMISE.md) dòng 28 (spec sửa: dòng 13): cho phép `market_id` null chỉ với `table_name = 'auth'`. Thực hiện ở E02-02. |
| GAP-17 | D-09 (6 bảng có `market_id`) ↔ D-30 (`has_role(role, market_id)`) | `permits`, `inspections`, `deliveries`, `adjustments`, `permit_reviews` không có `market_id` nhưng RLS cần lọc theo chợ. | **Giả định** – **P-15** → [PREMISE.md](PREMISE.md) dòng 29: lấy chợ qua bảng cha (hàm `stable` dùng trong policy), không thêm cột; đo hiệu năng ở E05-02-T. |
| GAP-18 | screen_list (SC-07, SC-18, SC-24 "chưa vẽ") | 3 màn hình trong phạm vi chưa có wireframe / screen spec chi tiết. | **Tạo issue làm rõ** (thiết kế trước khi code): E04-04 (SC-18), E07-03 (SC-07), E13-05 (SC-24). |
| GAP-19 | ADR-010, SC-15 mục 5, DD-05 bước 10 | Chưa có mẫu CSV của phần mềm kế toán, chưa chốt UTF-8 BOM hay Shift_JIS. | **Tạo issue làm rõ** E11-05; E11-06 `blocked`. |
| GAP-20 | ADR-012 (câu hỏi mở), Q8 | Thời gian offline tối đa; tablet dùng chung hay riêng từng người (ảnh hưởng hàng đợi trên máy). | **Tạo issue làm rõ** E13-06. |
| GAP-21 | ADR-007 (câu hỏi mở) | Thời hạn lưu `audit_logs` theo quy định của khách. | **Tạo issue làm rõ** E02-04 (không chặn go-live). |
| GAP-22 | D-33 (chỉ liệt kê 確定 / 取消 / 締め / 入金日 / 引渡し) ↔ CS-15 ("mọi thao tác ghi") | ロット登録, 参加者, 許可・承認, 修正依頼作成, quy tắc, phân quyền không được nêu trong D-33 → lưu vết cùng transaction không đồng đều. | **Giả định** – **P-16** → [PREMISE.md](PREMISE.md) dòng 30 (spec sửa: dòng 14): mọi thao tác ghi dùng trigger / hàm lưu vết chung (E02-02); API không tự ghi `audit_logs`. |
| GAP-23 | SC-14, CS-12 ↔ L6 | Giao hàng cho giao dịch của 営業日 đã 締め có bị chặn không. | **Đã sửa thiết kế** → LAB-4 `specs/PREMISE.md` **dòng 48** (P-06): được giao; E10-02 không kiểm 締め. |
| GAP-24 | diff D-37 ↔ Role matrix v1.1 (admin xem SC-02, SC-03, SC-20 đầy đủ) | Quyền đọc của システム管理者 khác nhau giữa role matrix và database thiết kế. | **Đã sửa thiết kế** → LAB-4 `specs/PREMISE.md` **dòng 23** (mục 1 #9) và **dòng 49** (P-07). Thực hiện ở E05-02, E02-03. |
| GAP-25 | architecture 4.5 (MFA cho 精算担当 / システム管理者) ↔ SC-01 mục 5 ("thiết kế sau") | Kiến trúc coi MFA là thiết kế, screen spec để sau; không có luồng màn hình. | **Để mở** – chưa đủ spec để chia task; đưa vào mục 2.8, hỏi PL ở lần chốt phạm vi tiếp theo. |

### 4.2 Chỗ hở → giả định / spec sửa trong PREMISE.md

| Chỗ hở | Giả định ([PREMISE.md](PREMISE.md) mục 2) | Spec sửa ([PREMISE.md](PREMISE.md) mục 1) |
|---|---|---|
| GAP-04 | P-08 – dòng 22 | dòng 11 |
| GAP-05 | P-09 – dòng 23 | — |
| GAP-06 | P-10 – dòng 24 | dòng 15 |
| GAP-08 | P-11 – dòng 25 | — |
| GAP-10 | P-12 – dòng 26 | dòng 16 |
| GAP-11 | P-13 – dòng 27 | dòng 12 |
| GAP-16 | P-14 – dòng 28 | dòng 13 |
| GAP-17 | P-15 – dòng 29 | — |
| GAP-22 | P-16 – dòng 30 | dòng 14 |
