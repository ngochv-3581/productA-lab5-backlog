# -*- coding: utf-8 -*-
"""Sinh backlog/backlog.json và các bảng sinh tự động trong task-breakdown.md.

Dữ liệu backlog viết tay trong file này (nguồn duy nhất). Chạy từ gốc repo:
    python -I -X utf8 tools/gen_backlog.py
Script thay nội dung giữa các cặp <!-- BEGIN:XXX --> / <!-- END:XXX --> trong task-breakdown.md
(TOTAL, REUSE, EPIC_TABLE, SPEC_TABLE) và kiểm mọi mã E.. nhắc trong task-breakdown.md đều có trong backlog.
"""
import json, sys, re, os
from collections import defaultdict, Counter

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
items = []

def E(id, title, spec, note, labels=None):
    items.append(dict(id=id, epic=id, title=title, parent=None, type="epic",
                      spec_refs=spec, labels=["epic"] + (labels or []), depends_on=[], note=note))

def I(id, title, spec, labels, deps=None, note=""):
    items.append(dict(id=id, epic=id[:3], title=title, parent=id[:3], type="issue",
                      spec_refs=spec, labels=labels, depends_on=deps or [], note=note))

def S(id, title, spec, labels, deps=None, note=""):
    parent = id.rsplit("-", 1)[0]
    items.append(dict(id=id, epic=id[:3], title=title, parent=parent, type="sub-issue",
                      spec_refs=spec, labels=labels, depends_on=deps or [], note=note))

RP = "reuse-prototype"

# ---------------- E01 ----------------
E("E01", "Nền tảng dự án và quy ước chung", ["ADR-001", "ADR-011"],
  "Đưa prototype LAB-2 thành codebase của hệ thống thật: CI, migration, môi trường, chuẩn lỗi / log, từ điển tiếng Nhật.")
I("E01-01", "Dựng codebase hệ thống thật từ prototype LAB-2 + CI (lint, unit, E2E)", ["ADR-001"], ["infra", RP],
  note="Tận dụng prototype: giữ nguyên Next.js + Supabase + bộ test hiện có; chỉ thêm pipeline CI chạy tự động trên PR.")
I("E01-02", "Quy trình migration SQL đánh số (AI viết, người dùng tự chạy) + kiểm cấu trúc sau khi chạy", ["ADR-001", "D-01..D-40"], ["infra", "db"],
  deps=["E01-01"], note="Mọi issue đổi database dùng quy trình này; tái dùng câu SQL đọc cấu trúc của LAB-4 để kiểm sau migration.")
I("E01-03", "Môi trường dev / staging / production (Supabase vùng Tokyo, gói trả phí, không SSO)", ["ADR-001", "P-04"], ["infra"],
  deps=["E01-01"], note="Biến môi trường chỉ có khóa publishable; không có service_role (ADR-002).")
I("E01-04", "Chuẩn lỗi API {error, code} + logger kỹ thuật theo quy ước DD (category, không ghi bí mật)", ["DD-01", "DD-02", "DD-03", "DD-04", "DD-05", "DD-06", "CS-19", "CS-20"], ["api", RP],
  deps=["E01-01"], note="Tận dụng prototype: định dạng lỗi đã có; thêm logger dùng chung và mã lỗi mới M_xx.")
I("E01-05", "Bổ sung từ điển ja.ts: từ mới LAB-4 (申請中 / 審査中 / 不許可 / 届出 / 未送信 …) và message mới", ["ADR-011", "ADR-009", "SC-03", "SC-17", "SC-18", "SC-24"], ["ui", RP],
  deps=["E01-01"], note="Tận dụng prototype: ja.ts là nguồn chữ duy nhất; ADR-009 yêu cầu có từ mới trước khi làm giao diện SC-03.")
I("E01-06", "Làm rõ thuật ngữ 承認 (loại giấy 売買参加者) trùng với 承認 (duyệt) + BrSE review chữ hiển thị", ["ADR-011", "ADR-009", "SC-03", "SC-12", "SC-18"], ["clarification", "ui"],
  deps=["E01-05"], note="Chỗ hở GAP-13. Người phụ trách: BrSE. Kết quả: GLOSSARY / ja.ts thống nhất cách gọi trên SC-03, SC-12, SC-18.")
I("E01-07", "Dọn dữ liệu test của prototype trước khi đặt khóa / unique mới", ["D-27", "G-12", "G-28", "G-29"], ["db", "migration"],
  deps=["E01-02"], note="Ngày giả 2000 / 2001 trong day_closes và kỳ 0000-TEST trong payments chặn các ràng buộc mới (D-25, D-27).")

# ---------------- E02 ----------------
E("E02", "Lưu vết chỉ thêm và quyền database", ["ADR-007", "ADR-002"],
  "Chặn sửa / xóa lưu vết ở mức quyền và trigger; ghi lưu vết cùng transaction; SC-20 có phân trang và che dữ liệu.", ["security"])
I("E02-01", "Thu hồi quyền bảng mặc định + trigger chặn update / delete / truncate audit_logs", ["D-34", "D-40", "ADR-007", "CS-15"], ["db", "security", "test", "constraint"],
  deps=["E01-02"], note="Ưu tiên đầu (diff mục 5 nhóm 1). Test: gọi thẳng bằng phiên authenticated / anon bị từ chối; app vẫn đọc / ghi được.")
I("E02-02", "Hàm / trigger lưu vết dùng chung trong database (market_id, actor_roles, cùng transaction)", ["D-28", "D-33", "ADR-007", "CS-15"], ["db", "constraint"],
  deps=["E02-01", "E03-02", "E05-01"], note="Khung cho mọi hàm nghiệp vụ (confirm_trade, close_day, record_payment …). Giả định P-14, P-16. Tách sau chấm SWP lần 1 (S5 × C4 = 20 → 21).")
S("E02-02-DB1", "Hàm ghi lưu vết chung write_audit + cột market_id (null chỉ cho auth), actor_roles", ["D-28", "D-33", "P-14"], ["db"])
S("E02-02-DB2", "Trigger lưu vết cho các bảng chưa có hàm nghiệp vụ (参加者, 許可・承認, ロット, 目利き, quy tắc, phân quyền)", ["D-33", "P-16", "CS-15"], ["db"], deps=["E02-02-DB1"],
  note="API route tương ứng bỏ tự ghi audit_logs trong issue của route đó (G-11).")
S("E02-02-T", "Test: lỗi ghi lưu vết → rollback cả thao tác; actor_roles đúng vai trò lúc làm", ["CS-15", "G-11", "D-28"], ["test"], deps=["E02-02-DB2"])
I("E02-03", "SC-20 監査証跡の検索: lọc, phân trang, che 変更前 / 変更後 cho システム管理者", ["SC-20", "API-43", "D-37", "P-07", "CS-24", "G-31"], ["security"],
  deps=["E02-02", "E05-02"], note="Tận dụng prototype SC-20 (bảng, bộ lọc); thay giới hạn 200 dòng bằng phân trang.")
S("E02-03-DB", "View audit_logs_masked che before / after của bảng nghiệp vụ cho admin", ["D-37", "P-07", "CS-24"], ["db", "security"])
S("E02-03-API", "API-43 tìm kiếm lưu vết có phân trang", ["API-43", "G-31"], ["api"], deps=["E02-03-DB"])
S("E02-03-UI", "Giao diện SC-20: phân trang, lọc thao tác đăng nhập, hiện **** cho admin", ["SC-20", "CS-24"], ["ui", RP], deps=["E02-03-API"],
  note="Tận dụng prototype: màn hình SC-20 đã chạy thật.")
S("E02-03-T", "Test: admin thấy đủ lưu vết tài khoản / quyền, bị che lưu vết nghiệp vụ; 精算担当 thấy đủ", ["CS-24", "P-07", "T14"], ["test"], deps=["E02-03-UI"])
I("E02-04", "Làm rõ thời hạn lưu audit_logs và cách lưu trữ lâu dài", ["ADR-007"], ["clarification"],
  note="Câu hỏi mở của ADR-007; không chặn go-live, ảnh hưởng thiết kế lưu trữ / chỉ mục.")

# ---------------- E03 ----------------
E("E03", "Chợ và 営業日 theo cấu hình chợ", ["P-01", "ADR-004", "DD-02"],
  "Mọi dữ liệu theo market_id; 営業日 tính ở database theo mốc chuyển ngày của phiên bản quy tắc đang hiệu lực.", ["constraint"])
I("E03-01", "Bảng markets + 1 chợ mặc định (go-live 1 chợ)", ["D-01", "P-01", "ADR-008"], ["db", "migration"],
  deps=["E01-02"])
I("E03-02", "Thêm market_id cho 6 bảng nghiệp vụ, unique theo chợ, đổi khóa day_closes", ["D-09", "D-16", "D-25", "P-01"], ["db", "migration"],
  deps=["E03-01", "E01-07"], note="Chạm nhiều bảng → tách DB / API / test.")
S("E03-02-DB1", "Migration market_id cho participants, lots, trades + unique (market_id, code / lot_no)", ["D-09", "D-16"], ["db", "migration"],
  note="Tách sau chấm SWP lần 1 (E03-02-DB: S5 × C3 = 15 → 13).")
S("E03-02-DB2", "Migration market_id cho day_closes (PK mới), payments, audit_logs", ["D-09", "D-25"], ["db", "migration"],
  note="Tách sau chấm SWP lần 1 (E03-02-DB: S5 × C3 = 15 → 13).")
S("E03-02-API", "Sửa truy vấn / API lọc theo chợ của người dùng", ["D-09", "P-01"], ["api", RP], deps=["E03-02-DB1", "E03-02-DB2"],
  note="Tận dụng prototype: chỉ thêm điều kiện market_id vào truy vấn hiện có.")
S("E03-02-T", "Chạy lại toàn bộ test sau khi thêm market_id", ["T01..T17"], ["test"], deps=["E03-02-API"])
I("E03-03", "Hàm business_date(market_id, ts) đọc mốc chuyển ngày từ phiên bản quy tắc", ["D-29", "DD-02", "ADR-004", "L11", "CS-05"], ["db", "constraint"],
  deps=["E03-02", "E04-01"], note="Giữ hàm cũ business_date(ts) gọi hàm mới với chợ mặc định để không vỡ default cột. Giả định P-11.")
S("E03-03-DB", "Hàm mới + hàm tương thích + chỉ mục rule_versions(market_id, status, effective_from)", ["D-29", "DD-02"], ["db"])
S("E03-03-T", "Test 営業日: 01:30 → hôm trước (T15), 02:00 đúng mốc, đổi mốc theo phiên bản, thiếu phiên bản → M_115", ["T15", "DD-02", "ADR-004"], ["test"], deps=["E03-03-DB"])
I("E03-04", "API-04 /api/session + header H-2 (営業日) / H-3 (締め) theo chợ", ["API-04", "CS-05", "CS-06", "SC-25"], ["api", "ui", RP],
  deps=["E03-03"], note="Tận dụng prototype: header đã hiện 営業日; đổi sang API dùng chung (cả tablet offline).")
I("E03-05", "Làm rõ lịch 休市日: hạn (支払期限, 有効期限) rơi vào ngày chợ nghỉ; thời điểm được đổi mốc chuyển ngày", ["ADR-004", "L8", "L1", "P-02"], ["clarification", "constraint"],
  note="Chỗ hở GAP-09: thiết kế không có lịch ngày nghỉ của chợ.")

# ---------------- E04 ----------------
E("E04", "Quy tắc vận hành theo chợ có phiên bản (SC-18)", ["ADR-008", "P-02", "D-02", "D-03", "D-35"],
  "rule_versions + market_rules; người soạn ≠ người duyệt; phiên bản đã duyệt không sửa. Là nền của 営業日 (E03) và 完納奨励金 (E12).", ["constraint"])
I("E04-01", "Bảng rule_versions + market_rules + trigger khóa phiên bản đã duyệt + phiên bản khởi tạo", ["D-02", "D-03", "D-35", "ADR-008", "P-02"], ["db", "migration", "constraint"],
  deps=["E03-01"], note="Phiên bản đầu = giá trị prototype (02:00, 料率 hiện tại, 係数 1.1, hiệu lực 2026-04-01). Giả định P-10, P-12.")
S("E04-01-DB1", "Bảng rule_versions + market_rules + check (approved_by <> drafted_by, miền 料率 / 係数, grace_days = 0) + trigger rule_versions_locked", ["D-02", "D-03", "D-35", "P-10"], ["db"],
  note="Tách sau chấm SWP lần 1 (E04-01-DB: S3 × C5 = 15 → 13).")
S("E04-01-DB2", "Migration phiên bản v1 của chợ mặc định từ giá trị prototype (02:00, 料率, 係数 1.1, hiệu lực 2026-04-01)", ["D-03", "D-04", "P-12"], ["db", "migration"], deps=["E04-01-DB1"],
  note="Tách sau chấm SWP lần 1. Ngoại lệ ngày quá khứ chỉ cho v1 (P-12).")
S("E04-01-T", "Test: sửa phiên bản đã duyệt bị chặn; tự duyệt bị chặn; grace_days ≠ 0 bị chặn", ["D-35", "CS-13", "P-02"], ["test"], deps=["E04-01-DB2"])
I("E04-02", "API-33 適用ルールの取得 (phiên bản approved hiệu lực tại ngày)", ["API-33", "ADR-008"], ["api"],
  deps=["E04-01"])
I("E04-03", "Luồng soạn / gửi duyệt / duyệt / từ chối phiên bản quy tắc", ["API-34", "API-35", "API-36", "API-37", "CS-13", "ADR-008"], ["constraint"],
  deps=["E04-01", "E05-02"], note="Người soạn ≠ người duyệt kiểm theo bản ghi, không theo quyền (ADR-003 mục 4).")
S("E04-03-DB", "Hàm chuyển trạng thái + chặn effective_from ≤ 営業日 hiện tại khi duyệt + lưu vết", ["ADR-008", "ADR-004"], ["db"])
S("E04-03-API", "API-34…37 (M_126 khi tự duyệt)", ["API-34", "API-35", "API-36", "API-37"], ["api"], deps=["E04-03-DB"])
S("E04-03-T", "Test: soạn → duyệt bởi người khác; tự duyệt bị chặn ở API và database; rollback = phiên bản mới", ["CS-13", "ADR-008"], ["test"], deps=["E04-03-API"])
I("E04-04", "Wireframe + screen spec SC-18 業務ルールの版管理 (chưa vẽ ở LAB-4)", ["SC-18", "ADR-008"], ["clarification", "ui"],
  note="Chỗ hở GAP-18. Người phụ trách: BrSE + FE-1; ghi chú: chỉ đổi mốc chuyển ngày khi chợ nghỉ (ADR-004).")
I("E04-05", "Màn hình SC-18: danh sách phiên bản, soạn, duyệt / từ chối, lịch sử", ["SC-18", "API-33", "API-34", "API-35", "API-36", "API-37"], ["ui"],
  deps=["E04-03", "E04-04"], note="Thay mock SC-18 của prototype. Tách sau chấm SWP lần 1 (S4 × C4 = 16 → 13).")
S("E04-05-UI1", "SC-18: danh sách phiên bản, chi tiết giá trị quy tắc, lịch sử", ["SC-18", "API-33"], ["ui"])
S("E04-05-UI2", "SC-18: hộp soạn / gửi duyệt / duyệt / từ chối (M_126, ngày hiệu lực > 営業日)", ["SC-18", "API-34", "API-35", "API-36", "API-37", "CS-13"], ["ui"], deps=["E04-05-UI1"])

# ---------------- E05 ----------------
E("E05", "Xác thực và phân quyền nhiều vai trò", ["ADR-002", "ADR-003", "DD-01"],
  "user_roles nhiều vai trò / người theo chợ, has_role ở RLS, khóa tài khoản, lưu vết đăng nhập, quản lý người dùng SC-21.", ["security"])
I("E05-01", "Bảng user_roles + chuyển profiles.role + trigger user_roles_guard (admin không kiêm, không tự gán)", ["D-05", "D-36", "ADR-003", "G-24"], ["db", "migration", "constraint"],
  deps=["E03-01"])
S("E05-01-DB", "Migration user_roles, chuyển dữ liệu vai trò hiện có, trigger guard", ["D-05", "D-36"], ["db", "migration"])
S("E05-01-T", "Test trigger: admin + vai trò nghiệp vụ bị chặn (M_116); tự gán bị chặn", ["D-36", "G-24"], ["test"], deps=["E05-01-DB"])
I("E05-02", "has_role(role, market_id) + viết lại toàn bộ policy; システム管理者 không đọc bảng nghiệp vụ", ["D-30", "D-37", "ADR-002", "CS-24", "P-07"], ["db", "security"],
  deps=["E05-01", "E03-02"], note="Giả định P-15 (bảng không có market_id lấy chợ qua bảng cha).")
S("E05-02-DB1", "Hàm has_role(role, market_id) (vai trò cha / con, revoked_at) + hàm lấy chợ qua bảng cha", ["D-30", "ADR-003", "P-15"], ["db", "security"],
  note="Tách sau chấm SWP lần 1 (E05-02-DB: S5 × C4 = 20 → 21).")
S("E05-02-DB2", "Viết lại policy nhóm tài khoản / quy tắc / lưu vết bằng has_role", ["D-30"], ["db", "security"], deps=["E05-02-DB1"])
S("E05-02-DB3", "Viết lại policy bảng nghiệp vụ bằng has_role, bỏ quyền đọc của システム管理者", ["D-30", "D-37"], ["db", "security"], deps=["E05-02-DB1"])
S("E05-02-T", "Test RLS: T11, T12, T17 + admin gọi thẳng đọc participants → rỗng", ["T11", "T12", "T17", "D-37"], ["test"], deps=["E05-02-DB2", "E05-02-DB3"])
I("E05-03", "requireRole nhiều quyền + menu SC-25 theo hợp các quyền", ["CS-02", "CS-03", "CS-04", "SC-25", "DD-01"], ["api", "ui", RP],
  deps=["E05-02"], note="Tận dụng prototype: requireRole và menu theo vai trò đã có; đổi sang danh sách quyền.")
I("E05-04", "Khóa tài khoản: profiles.status + proxy đăng xuất tài khoản bị khóa", ["D-11", "CS-21", "DD-01"], ["db", "api", "security"],
  deps=["E05-01"], note="Tận dụng prototype: proxy.ts đã kiểm phiên (L10).")
I("E05-05", "API-02 đăng nhập: chặn locked / không quyền + lưu vết LOGIN_SUCCESS / LOGIN_FAILED", ["API-02", "D-38", "DD-01", "SC-01", "M11"], ["api", "security"],
  deps=["E05-04", "E02-02", "E05-09"], note="Tận dụng prototype SC-01 (form đăng nhập). Phụ thuộc kết quả spike E05-09. Tách sau chấm SWP lần 1 (S3 × C5 = 15 → 13).")
S("E05-05-API", "API-02: chặn locked (M_99) / không quyền (M_77) + lưu vết LOGIN_SUCCESS / LOGIN_FAILED", ["API-02", "D-38", "DD-01"], ["api", "security"])
S("E05-05-UI", "SC-01 gọi API-02, hiện M_29 / M_81 / M_82 / M_99 / M_77", ["SC-01"], ["ui", RP], deps=["E05-05-API"],
  note="Tận dụng prototype: form SC-01 đã chạy.")
I("E05-06", "SC-21 ユーザー・権限管理: nhiều quyền, khóa / mở khóa; bỏ API-39", ["SC-21", "API-38", "API-40", "API-41", "API-39", "G-24", "D-36"], ["security"],
  deps=["E05-01", "E05-04"])
S("E05-06-API", "API-38, API-40, API-41; bỏ API-39", ["API-38", "API-40", "API-41", "API-39"], ["api"])
S("E05-06-UI", "Giao diện SC-21: hộp đổi quyền nhiều lựa chọn, hộp khóa có lý do, dòng của mình bị khóa", ["SC-21"], ["ui", RP], deps=["E05-06-API"],
  note="Tận dụng prototype: SC-21 bản đơn giản đã chạy.")
S("E05-06-T", "Test SC-21: M_44, M_116, M_70, M_75; T16", ["SC-21", "T16"], ["test"], deps=["E05-06-UI"])
I("E05-07", "API-42 mời người dùng bằng email", ["API-42", "SC-21", "M3"], ["api"],
  deps=["E05-09"], note="Cách gọi phụ thuộc kết quả E05-09 (không dùng service_role).")
I("E05-08", "Bỏ cột profiles.role sau khi user_roles và RLS mới chạy ổn", ["D-10"], ["db", "migration"],
  deps=["E05-02", "E05-03", "E05-06"])
I("E05-09", "Spike / làm rõ: ghi LOGIN_FAILED khi chưa có phiên và mời người dùng khi không dùng service_role", ["D-38", "D-40", "API-42", "ADR-002", "DD-01"], ["clarification", "spike", "security"],
  note="Chỗ hở GAP-14, GAP-15. Kết quả: phương án (Auth hook / hàm security definer có giới hạn / ngoại lệ có kiểm soát) được PL duyệt.")

# ---------------- E06 ----------------
E("E06", "Người tham gia và 許可 / 承認 hai luồng", ["ADR-009", "P-03", "L1", "L3"],
  "Trạng thái xét duyệt riêng cho 許可 và 承認, điều kiện, lịch sử xét duyệt, L1 theo trạng thái giấy.", ["constraint"])
I("E06-01", "permits: trạng thái theo kind, cột quyết định, valid_* chỉ bắt buộc khi đã cấp + chuyển dữ liệu cũ", ["D-13", "D-14", "D-15", "ADR-009", "P-03"], ["db", "migration", "constraint"],
  deps=["E03-02"])
S("E06-01-DB", "Migration cột + check theo kind + giấy hiện có → granted / approved", ["D-13", "D-14", "D-15"], ["db", "migration"])
S("E06-01-T", "Test check constraint: trạng thái sai kind bị chặn; valid_from > valid_to bị chặn; T06", ["D-13", "D-15", "T06"], ["test"], deps=["E06-01-DB"])
I("E06-02", "Bảng permit_reviews + ghi lịch sử mỗi lần chuyển trạng thái", ["D-06", "ADR-009"], ["db"],
  deps=["E06-01"])
I("E06-03", "L1 dùng chung: giấy hợp lệ = đúng loại + trạng thái 許可 / 承認 + còn hạn tại 営業日", ["L1", "CS-07", "ADR-009", "DD-03"], ["db", "constraint"],
  deps=["E06-01", "E03-03"], note="Hàm database dùng chung cho 確定 (E08-02), 引渡し (E10-02), đồng bộ offline (E13-03). Test T03.")
I("E06-04", "API xét duyệt: API-08, API-09 (trạng thái đầu 申請中 / 届出), API-11 (審査開始 / 審査結果 / 承認結果)", ["API-08", "API-09", "API-11", "SC-03", "ADR-009"], ["constraint"],
  deps=["E06-02"], note="Giả định P-13 (API-11 nhận mọi chuyển trạng thái hợp lệ theo kind).")
S("E06-04-DB", "Hàm chuyển trạng thái giấy (kiểm chuyển hợp lệ, 決定日 ≤ 営業日, 登録者 = người đăng nhập) + lưu vết", ["ADR-009", "D-14"], ["db"])
S("E06-04-API", "API-08, API-09 sửa, API-11 mới", ["API-08", "API-09", "API-11"], ["api", RP], deps=["E06-04-DB"],
  note="Tận dụng prototype: API-09, API-10 đã có.")
S("E06-04-T", "Test luồng 許可: 申請中 → 審査中 → 許可 / 不許可; 承認: 届出 → 承認; M_122, M_124, M_64 / M_65", ["SC-03", "L3"], ["test"], deps=["E06-04-API"])
I("E06-05", "SC-03 参加者詳細: 2 tab 許可 / 承認, sơ đồ luồng, hộp 審査結果の登録", ["SC-03", "ADR-009"], ["ui", RP],
  deps=["E06-04", "E01-05"], note="Tận dụng prototype: SC-03 đã tách 許可 / 承認 (L3); thêm trạng thái, 条件, 決定者（開設者側）, 登録者. Tách sau chấm SWP lần 1 (S4 × C5 = 20 → 21).")
S("E06-05-UI1", "SC-03: 2 tab, sơ đồ luồng, thẻ giấy hiện hành, bảng lịch sử, nút 審査開始 / đăng ký đơn", ["SC-03", "ADR-009"], ["ui", RP])
S("E06-05-UI2", "SC-03: hộp 審査結果の登録 / 承認結果の登録 (決定日, 決定者（開設者側）, 有効期間, 条件 / 不許可理由)", ["SC-03", "ADR-009", "D-14"], ["ui"], deps=["E06-05-UI1"])
I("E06-06", "一時停止 có lý do ở cột riêng: status_reason / status_changed_at + API-07", ["D-12", "API-07", "L2", "SC-03"], ["db", "api", "migration"],
  deps=["E03-02"], note="Chuyển lý do mới nhất từ audit_logs sang cột (dữ liệu prototype).")
I("E06-07", "SC-02 参加者一覧: tô màu 期限切れ / 期限間近 theo giấy hợp lệ đúng loại", ["SC-02", "SC-04", "CS-07"], ["ui", RP],
  deps=["E06-03"], note="Tận dụng prototype: SC-02 đã tô màu (gộp SC-04); đổi điều kiện theo trạng thái giấy.")
I("E06-08", "Đính kèm chứng từ 許可 / 承認: attachments + Storage bucket có RLS + upload ở SC-03", ["D-08", "M5", "SC-03"], ["db", "ui"],
  deps=["E06-05"])
I("E06-09", "Làm rõ: thu hồi / đình chỉ giấy; 承認 có bị từ chối không; 承認 ghi như 許可", ["ADR-009", "SC-03"], ["clarification", "constraint"],
  note="Chỗ hở GAP-12 – câu hỏi mở của ADR-009, chưa có mã Q.")

# ---------------- E07 ----------------
E("E07", "Lô hàng và 目利き", ["L4", "L11", "P-04"],
  "ロット登録 / 目利き trên tablet, danh sách lô còn hàng; chủ yếu tận dụng prototype.")
I("E07-01", "SC-05 ロット登録 tối ưu tablet 10–11 inch", ["SC-05", "P-04", "API-12"], ["ui", "tablet", RP],
  deps=["E03-02"], note="Tận dụng prototype: SC-05 chạy thật; chỉnh bố cục theo wireframe tablet.")
I("E07-02", "API-14 lô còn hàng (gồm lô của 前の営業日)", ["API-14", "G-03", "L4"], ["api"],
  deps=["E03-02"], note="Dùng cho SC-08, SC-10 và tablet.")
I("E07-03", "Wireframe + giao diện tablet SC-07 目利き結果入力", ["SC-07", "API-13", "P-04"], ["ui", "tablet", RP],
  deps=["E03-02"], note="Chỗ hở GAP-18 (chưa vẽ wireframe). Tận dụng prototype: SC-07 chạy thật bản PC.")
I("E07-04", "SC-06 ロット一覧・詳細 theo chợ", ["SC-06", "D-16"], ["ui", RP],
  deps=["E03-02"], note="Tận dụng prototype: chỉ đổi lọc theo chợ / lot_no unique theo chợ.")

# ---------------- E08 ----------------
E("E08", "Giao dịch 相対取引 / せり / 取消", ["DD-03", "ADR-005", "L1", "L2", "L4", "G-04"],
  "Gom kiểm luật + ghi + lưu vết vào hàm database 1 transaction; giữ trigger L4 khóa lô, không tự hủy.", ["constraint"])
I("E08-01", "trades: cột confirmed_by_name, cancelled_by / cancelled_at, unit_price > 0 + chuyển dữ liệu từ audit_logs", ["D-19", "D-20", "D-21", "G-05", "G-09"], ["db", "migration"],
  deps=["E03-02"], note="Nhóm ít rủi ro (diff mục 5): câu alter đã có sẵn từ G-05.")
I("E08-02", "Hàm confirm_trade 1 transaction (G-04 → G-01 → L2 → L1 → L4) + lưu vết", ["DD-03", "D-33", "API-15", "ADR-005", "G-04", "CS-10"], ["constraint"],
  deps=["E08-01", "E06-03", "E02-02"], note="Trigger trades_kiem_l4 giữ nguyên (đã khớp ở diff mục 4).")
S("E08-02-DB", "Hàm confirm_trade (business_date, 締め, người mua, giấy, insert, audit)", ["DD-03", "D-33"], ["db"])
S("E08-02-API", "API-15 gọi rpc, đổi lỗi P0001 → M_35 / M_31 … ", ["API-15", "DD-03"], ["api", RP], deps=["E08-02-DB"],
  note="Tận dụng prototype: route API-15 và câu lỗi đã có.")
S("E08-02-T", "Test T03, T04, T05, tranh chấp 2 người cùng lúc, G-04, rollback khi lỗi lưu vết", ["T03", "T04", "T05", "CS-10", "G-04"], ["test"], deps=["E08-02-API"])
I("E08-03", "Hàm cancel_trade: L6, G-02, G-07, lưu cancelled_by / cancelled_at + lưu vết", ["API-16", "L6", "G-02", "G-07", "D-21", "D-33", "CS-12"], ["db", "api", "constraint"],
  deps=["E08-01", "E02-02"], note="Tận dụng prototype: luật đã chạy ở API, chuyển xuống hàm database. Tách sau chấm SWP lần 1 (S3 × C5 = 15 → 13).")
S("E08-03-DB", "Hàm cancel_trade (L6, G-02, G-07, cancelled_by / cancelled_at, lưu vết)", ["D-21", "D-33", "L6", "G-02", "G-07"], ["db"])
S("E08-03-API", "API-16 gọi rpc, đổi lỗi → M_37 / M_xx", ["API-16"], ["api", RP], deps=["E08-03-DB"], note="Tận dụng prototype: route API-16.")
S("E08-03-T", "Test T09 + G-02 + G-07 + lưu vết hủy", ["T09", "G-02", "G-07", "CS-12"], ["test"], deps=["E08-03-API"])
I("E08-04", "API-17 当日取引, API-18 買受人候補 (kèm cảnh báo giấy / 一時停止)", ["API-17", "API-18", "G-15"], ["api"],
  deps=["E06-03"])
I("E08-05", "SC-08 相対取引: hộp xác nhận 確定, banner 締め済み", ["SC-08", "CS-06", "CS-25", "W-05"], ["ui", RP],
  deps=["E08-02", "E08-04", "E07-02"], note="Tận dụng prototype: màn hình trung tâm đã chạy; thêm hộp xác nhận (W-05).")
I("E08-06", "SC-10 せり結果入力: 確認者（せり人） đọc / ghi cột riêng", ["SC-10", "D-19"], ["ui", RP],
  deps=["E08-02"], note="Tận dụng prototype: SC-10 đã chạy.")
I("E08-07", "SC-09 当日取引一覧: hiện người / thời điểm 取消 từ cột mới", ["SC-09", "D-21"], ["ui", RP],
  deps=["E08-03"], note="Tận dụng prototype.")

# ---------------- E09 ----------------
E("E09", "修正依頼 (sửa sau khi chốt)", ["ADR-006", "DD-04", "L7"],
  "Duyệt / từ chối trong 1 transaction, lý do từ chối ở cột riêng, người tạo ≠ người quyết định.", ["constraint"])
I("E09-01", "adjustments: reject_reason, approved_by → decided_by, unique 1 phiếu chờ / giao dịch + chuyển dữ liệu", ["D-22", "D-23", "D-24", "G-07", "G-19", "G-20"], ["db", "migration", "constraint"],
  deps=["E03-02"])
I("E09-02", "Hàm approve_adjustment / reject_adjustment 1 transaction (L7, G-17, G-08, L4) + lưu vết 2 dòng", ["D-32", "DD-04", "API-23", "API-24", "L7", "CS-13", "G-25"], ["constraint"],
  deps=["E09-01", "E02-02"])
S("E09-02-DB", "Hai hàm database + check decided_by <> requested_by", ["D-32", "D-23", "DD-04"], ["db"])
S("E09-02-API", "API-23, API-24 chỉ gọi rpc", ["API-23", "API-24"], ["api", RP], deps=["E09-02-DB"],
  note="Tận dụng prototype: route và câu lỗi đã có.")
S("E09-02-T", "Test T10, T11, L7 với tài khoản kiêm 2 quyền, G-17, G-08, L4 khi duyệt số lượng", ["T10", "T11", "L7", "G-26"], ["test"], deps=["E09-02-API"])
I("E09-03", "SC-12 修正依頼の承認: API-25 danh sách + 自分の依頼 + cảnh báo CSV", ["SC-12", "API-25", "M_110"], ["api", "ui", RP],
  deps=["E09-02"], note="Tận dụng prototype: SC-12 đã chạy.")
I("E09-04", "SC-11 修正依頼作成 theo cấu trúc mới (G-07, G-08, G-13)", ["SC-11", "API-22"], ["ui", "api", RP],
  deps=["E09-01"], note="Tận dụng prototype.")

# ---------------- E10 ----------------
E("E10", "引渡し (giao hàng nhiều lần)", ["L5", "P-06"],
  "Chặn giao vượt ở database, ghi + lưu vết cùng transaction; được giao cho ngày đã 締め (P-06).")
I("E10-01", "Trigger deliveries_kiem_l5 khóa dòng giao dịch, chặn Σ giao > số đã mua", ["D-39", "L5", "CS-11"], ["db", "test", "constraint"],
  deps=["E03-02"], note="Bắt buộc trước offline (ADR-012). Test T07, T08 + 2 người giao cùng lúc.")
I("E10-02", "Hàm ghi 引渡し (L1 tại ngày giao, không kiểm 締め) + lưu vết + API-19", ["API-19", "D-33", "L1", "P-06", "G-06", "CS-12"], ["db", "api"],
  deps=["E10-01", "E06-03", "E02-02"], note="Tận dụng prototype: route API-19. Tách sau chấm SWP lần 1 (S3 × C5 = 15 → 13).")
S("E10-02-DB", "Hàm ghi 引渡し: L1 tại ngày giao, L5 (trigger), không kiểm 締め (P-06), lưu vết", ["D-33", "L1", "P-06", "G-06"], ["db"])
S("E10-02-API", "API-19 gọi rpc, đổi lỗi → M_36 / M_45 / M_46", ["API-19"], ["api", RP], deps=["E10-02-DB"], note="Tận dụng prototype: route API-19.")
I("E10-03", "SC-13 引渡し待ち一覧 + API-20 (mọi 営業日)", ["SC-13", "API-20", "G-14"], ["api", "ui", RP],
  deps=["E10-02"], note="Tận dụng prototype.")
I("E10-04", "SC-14 引渡し入力 tối ưu tablet", ["SC-14", "P-04"], ["ui", "tablet", RP],
  deps=["E10-02"], note="Tận dụng prototype.")

# ---------------- E11 ----------------
E("E11", "締め và xuất CSV kế toán", ["DD-05", "ADR-010", "L6"],
  "close_day 1 transaction có snapshot; xuất CSV ghi lịch sử, mã băm, cờ cần xuất lại.", ["constraint"])
I("E11-01", "Hàm close_day: G-21, khóa (market_id, date), G-18, snapshot, lưu vết", ["DD-05", "D-25", "D-33", "API-27", "G-18", "G-21"], ["constraint"],
  deps=["E03-02", "E02-02", "E09-01"])
S("E11-01-DB1", "Hàm close_day (G-21, khóa tư vấn (market_id, date), G-18, snapshot, lưu vết)", ["D-33", "DD-05", "G-18", "G-21"], ["db"],
  note="Tách sau chấm SWP lần 1 (E11-01-DB: S3 × C5 = 15 → 13).")
S("E11-01-DB2", "Cột snapshot trade_count / total_amount + tính lại 1 lần cho dòng day_closes cũ", ["D-25"], ["db", "migration"],
  note="Tách sau chấm SWP lần 1.")
S("E11-01-API", "API-27 gọi rpc", ["API-27"], ["api", RP], deps=["E11-01-DB1", "E11-01-DB2"], note="Tận dụng prototype.")
S("E11-01-T", "Test: còn phiếu chờ → M_41; ngày tương lai → M_60; 2 người cùng 締め → M_59; T09", ["T09", "G-18", "G-21"], ["test"], deps=["E11-01-API"])
I("E11-02", "SC-15 日次照合・締め: API-26 tổng hợp, snapshot so với hiện tại, hộp xác nhận", ["SC-15", "API-26", "CS-25"], ["api", "ui", RP],
  deps=["E11-01"], note="Tận dụng prototype: SC-15 đã chạy. Tách sau chấm SWP lần 1 (S4 × C4 = 16 → 13).")
S("E11-02-API", "API-26 日次集計: số liệu theo loại, 取消, 引渡し未完了, phiếu chờ, snapshot", ["API-26", "D-25"], ["api"])
S("E11-02-UI", "SC-15: checklist trước 締め, snapshot so với hiện tại, hộp xác nhận", ["SC-15", "CS-25"], ["ui", RP], deps=["E11-02-API"],
  note="Tận dụng prototype: SC-15 đã chạy.")
I("E11-03", "Lịch sử xuất CSV: export_batches + Storage + API-28 sửa + API-29", ["D-07", "API-28", "API-29", "ADR-010", "G-30"], ["db", "api"],
  deps=["E11-01", "E06-08"], note="Xuất lại dữ liệu không đổi → file giống hệt (cùng SHA-256).")
S("E11-03-DB", "Bảng export_batches + bucket lưu file có RLS", ["D-07", "D-08"], ["db"])
S("E11-03-API", "API-28 ghi export_batches + lưu vết; API-29 lịch sử", ["API-28", "API-29"], ["api", RP], deps=["E11-03-DB"])
S("E11-03-T", "Test: chưa 締め → M_63; xuất 2 lần cùng mã băm; lưu Storage lỗi vẫn trả file", ["ADR-010", "DD-05"], ["test"], deps=["E11-03-API"])
I("E11-04", "Cờ 再出力が必要 khi duyệt 修正依頼 cho ngày đã xuất + cảnh báo SC-15 / SC-19", ["ADR-010", "DD-04", "M_111", "SC-15", "SC-19"], ["db", "ui"],
  deps=["E11-03", "E09-02"])
I("E11-05", "Làm rõ mẫu CSV phần mềm kế toán và mã ký tự (UTF-8 BOM / Shift_JIS)", ["ADR-010", "Q6"], ["clarification", "blocked"],
  note="Chỗ hở GAP-19; chờ khách gửi mẫu file.")
I("E11-06", "Định dạng CSV theo mẫu khách (cấu hình format_version)", ["ADR-010", "SC-19"], ["api", "blocked"],
  deps=["E11-05", "E11-03"])
I("E11-07", "SC-19 データ出力（CSV） dùng chung lịch sử xuất với SC-15", ["SC-19", "API-29"], ["ui", RP],
  deps=["E11-03"], note="Tận dụng prototype: SC-19 bản đơn giản.")

# ---------------- E12 ----------------
E("E12", "完納奨励金 (thưởng trả đúng hạn)", ["DD-06", "SC-17", "L8", "D-02", "D-03", "D-26", "D-31", "P-02"],
  "Epic ràng buộc đặc thù: chạm tiền, 営業日, phiên bản quy tắc và khóa kết quả. Tính sai = trả sai tiền cho người mua.", ["constraint", "incentive"])
I("E12-01", "Chọn phiên bản quy tắc có hiệu lực tại 支払期限 (料率, 係数, 猶予)", ["DD-06", "SC-17", "D-02", "D-03", "P-02", "CS-14", "W-08"], ["db", "incentive", "constraint"],
  deps=["E04-01", "E04-02"], note="Không có phiên bản → M_115, không tính. Chọn theo 支払期限, không theo 入金日 hay ngày xem.")
I("E12-02", "Tính bằng số nguyên + làm tròn xuống: 料率 / 係数 đổi phân số chính xác, đọc 係数 từ market_rules", ["L8", "DD-06", "D-31", "CS-14"], ["api", "incentive", "constraint", "test"],
  deps=["E12-01"], note="Tận dụng prototype: phép tính BigInt đã có; bỏ 1.1 viết cứng (D-31). Giả định P-10. Test: 1,200,000 → 3,960; 530,000 → 1,749; số biên.")
I("E12-03", "判定 期限内 / 期限超過 / 未入金, không ân hạn (grace_days = 0), so sánh ngày theo 営業日", ["L8", "DD-06", "CS-14", "ADR-004"], ["api", "incentive", "constraint", "test"],
  deps=["E12-02", "E03-03"], note="Giả định P-09. Test biên: 入金日 = 支払期限 → 期限内; +1 ngày → 期限超過 = 0; T13.")
I("E12-04", "Xem trước API-32 奨励金の試算 (chỉ đọc, không lưu vết)", ["API-32", "DD-06", "SC-17"], ["api", "incentive"],
  deps=["E12-03"])
I("E12-05", "Ghi 入金日 và khóa kết quả: lưu incentive_amount + rule_version_id, chỉ ghi 1 lần", ["API-31", "D-26", "D-27", "D-33", "G-22", "G-23", "P-02", "DD-06"], ["incentive", "constraint"],
  deps=["E12-03", "E02-02", "E01-07"], note="Giả định P-08 (hàm record_payment 1 transaction thay vì nhiều bước ở API).")
S("E12-05-DB", "Cột D-26 + unique D-27 + hàm record_payment (khóa dòng, G-22, G-23, tính, lưu, audit)", ["D-26", "D-27", "D-33", "G-22", "G-23"], ["db", "incentive"])
S("E12-05-API", "API-31 gọi rpc, trả 判定 + 奨励金額", ["API-31"], ["api", "incentive", RP], deps=["E12-05-DB"],
  note="Tận dụng prototype: route API-31 đã có.")
S("E12-05-T", "Test: ghi 2 lần → M_62; ngày tương lai → M_61; đổi 料率 sau khi ghi không đổi số đã lưu; lưu vết record_payment", ["G-22", "G-23", "P-02", "D-26"], ["test", "incentive"], deps=["E12-05-API"])
I("E12-06", "Màn hình SC-17 完納奨励金: thẻ 適用ルール, cột ルール版 / 計算内容, hộp ghi 入金日 có xem trước", ["SC-17", "API-30", "API-33"], ["incentive"],
  deps=["E12-04", "E12-05"])
S("E12-06-API", "API-30 danh sách theo kỳ / 判定: đọc giá trị đã lưu, tổng Σ incentive_amount", ["API-30", "DD-06"], ["api", "incentive"])
S("E12-06-UI1", "SC-17: chọn kỳ, lọc 判定, thẻ 適用ルール, bảng có cột ルール版 / 計算内容, tổng 奨励金額", ["SC-17", "API-30", "API-33"], ["ui", "incentive", RP], deps=["E12-06-API"],
  note="Tận dụng prototype: SC-17 bản đơn giản đã chạy. Tách sau chấm SWP lần 1 (E12-06-UI: S4 × C5 = 20 → 21).")
S("E12-06-UI2", "SC-17: hộp ghi 入金日 có xem trước (API-32), M_61 / M_62 / M_67 / M_113 / M_115", ["SC-17", "API-31", "API-32"], ["ui", "incentive"], deps=["E12-06-UI1"],
  note="Tách sau chấm SWP lần 1.")
I("E12-07", "Chuyển dữ liệu 完納奨励金: lưu kết quả (gắn phiên bản v1) cho dòng đã có 入金日; khóa rồi bỏ incentive_rates; chạy lại T13", ["D-04", "D-26", "T13"], ["db", "migration", "incentive"],
  deps=["E12-05", "E04-01"], note="Phiên bản v1 do E04-01-DB2 tạo; issue này chỉ chuyển kết quả thưởng và bỏ bảng cũ (D-04).")
I("E12-08", "Test vector Phụ lục C: khung test chạy theo bộ dữ liệu (chờ dữ liệu khách)", ["M4", "ADR-008", "L8"], ["test", "incentive", "blocked"],
  deps=["E12-03"], note="Chỗ hở GAP-07. Dựng khung đọc CSV vector + vector tự soạn; khi có Phụ lục C thì chỉ thêm file dữ liệu.")
I("E12-09", "Làm rõ nguồn 請求: ai / khi nào lập 請求, 請求金額 tính từ đâu, 修正依頼 sau khi lập 請求", ["SC-17", "DD-06", "DD-04", "API-30"], ["clarification", "incentive", "constraint"],
  note="Chỗ hở GAP-01, GAP-02: không có API / màn hình tạo payments.")
I("E12-10", "Làm rõ quy trình sửa 入金日 đã ghi nhầm (kết quả đã khóa)", ["SC-17", "G-23", "P-02"], ["clarification", "incentive"],
  note="Chỗ hở GAP-03.")

# ---------------- E13 ----------------
E("E13", "Offline hẹp cho tablet (ロット登録, 引渡し入力)", ["ADR-012", "P-05", "M6"],
  "PWA: hàng đợi trên tablet, chống trùng bằng client_uuid, server kiểm luật khi đồng bộ.", ["tablet"])
I("E13-01", "Spike PWA: Service Worker + IndexedDB trên tablet Chrome / Safari", ["ADR-012", "P-04", "P-05"], ["spike", "tablet"],
  deps=["E01-01"], note="ADR-012: phần khó nhất, prototype chưa chứng minh. Tách sau chấm SWP lần 1 (S3 × C5 = 15 → 13).")
S("E13-01-UI1", "Spike: Service Worker giữ app chạy khi mất mạng trên Chrome / Safari tablet", ["ADR-012", "P-04"], ["ui", "spike", "tablet"])
S("E13-01-UI2", "Spike: hàng đợi IndexedDB + gửi lại có client_uuid", ["ADR-012", "P-05"], ["ui", "spike", "tablet"], deps=["E13-01-UI1"])
I("E13-02", "Cột client_uuid / client_recorded_at / synced_at cho lots, deliveries + unique", ["D-17", "D-18"], ["db", "migration"],
  deps=["E03-02"])
I("E13-03", "API-21 /api/sync: kiểm L1, L5, 営業日 theo client_recorded_at, kết quả từng dòng", ["API-21", "ADR-012", "DD-02", "L1", "L5"], ["constraint"],
  deps=["E13-02", "E10-01", "E10-02", "E03-03"])
S("E13-03-API", "Route đồng bộ + cấp lot_no chính thức + chống trùng", ["API-21", "ADR-012"], ["api"])
S("E13-03-T", "Test: gửi lại nhiều lần chỉ ghi 1; 2 tablet giao vượt → 1 dòng lỗi; 01:30 offline → 営業日 hôm trước", ["ADR-012", "L5", "T15"], ["test"], deps=["E13-03-API"])
I("E13-04", "Hàng đợi offline ở SC-05, SC-14 + trạng thái H-8 + chặn thao tác khác (M_101…M_105)", ["CS-22", "SC-05", "SC-14", "ADR-012"], ["ui", "tablet"],
  deps=["E13-01", "E13-03"], note="Tách sau chấm SWP lần 1 (S5 × C5 = 25 → 21).")
S("E13-04-UI1", "Header H-8: trạng thái mạng + số 未送信", ["CS-22"], ["ui", "tablet"])
S("E13-04-UI2", "Chặn thao tác bắt buộc online khi mất mạng trên mọi màn hình (M_103)", ["CS-22", "ADR-012", "P-05"], ["ui", "tablet"], deps=["E13-04-UI1"])
S("E13-04-UI3", "SC-05 ghi ロット登録 offline vào hàng đợi, số tạm (M_101, M_102)", ["SC-05", "CS-22", "D-17"], ["ui", "tablet"], deps=["E13-04-UI1"])
S("E13-04-UI4", "SC-14 ghi 引渡し offline vào hàng đợi (M_101, M_102)", ["SC-14", "CS-22", "D-18"], ["ui", "tablet"], deps=["E13-04-UI1"])
S("E13-04-UI5", "Tự gửi hàng đợi qua API-21 khi có mạng, hiện kết quả (M_104, M_105)", ["API-21", "CS-22"], ["ui", "tablet"], deps=["E13-04-UI3", "E13-04-UI4"])
I("E13-05", "Wireframe + màn hình SC-24 未送信データ (danh sách chưa gửi / lỗi đồng bộ)", ["SC-24", "ADR-012"], ["ui", "tablet"],
  deps=["E13-04"], note="Chỗ hở GAP-18 (chưa vẽ wireframe). Tách sau chấm SWP lần 1 (S3 × C5 = 15 → 13).")
S("E13-05-UI1", "Wireframe + screen spec SC-24 theo template", ["SC-24", "ADR-012"], ["ui", "clarification"])
S("E13-05-UI2", "Màn hình SC-24: danh sách chưa gửi / lỗi đồng bộ, gửi lại, xử lý dòng lỗi", ["SC-24", "ADR-012", "API-21"], ["ui", "tablet"], deps=["E13-05-UI1"])
I("E13-06", "Làm rõ thời gian offline tối đa và tablet dùng chung / riêng", ["ADR-012", "Q8"], ["clarification"],
  note="Chỗ hở GAP-20.")

# ---------------- E14 ----------------
E("E14", "Kiểm thử hệ thống và chuẩn bị go-live", ["T01..T17", "ADR-002"],
  "Hồi quy toàn bộ luật trên cấu trúc mới, test phân quyền gọi thẳng database, nghiệm thu với BrSE.", ["test"])
I("E14-01", "Bộ hồi quy E2E T01–T17 chạy trên CI với cấu trúc database mới", ["T01..T17"], ["test", RP],
  deps=["E01-01"], note="Tận dụng prototype: kịch bản và test E2E đã có; cập nhật dữ liệu mẫu theo chợ.")
I("E14-02", "Test 'người tạo ≠ người duyệt' với tài khoản kiêm nhiều quyền (修正依頼, phiên bản quy tắc)", ["L7", "G-26", "CS-13", "ADR-003"], ["test", "constraint"],
  deps=["E09-02", "E04-03"], note="G-26: prototype không test được vì mỗi tài khoản 1 vai trò.")
I("E14-03", "Test bảo mật: gọi thẳng Supabase bằng phiên anon / authenticated / admin cho mọi bảng", ["ADR-002", "D-37", "D-40", "CS-04", "CS-24"], ["test", "security"],
  deps=["E05-02", "E02-01"], note="Tách sau chấm SWP lần 1 (S5 × C3 = 15 → 13).")
S("E14-03-T1", "Test quyền mức bảng: anon không quyền; authenticated không TRUNCATE / REFERENCES / TRIGGER", ["D-40", "CS-04"], ["test", "security"])
S("E14-03-T2", "Test RLS: システム管理者 gọi thẳng đọc mọi bảng nghiệp vụ → rỗng; lưu vết bị che", ["D-37", "CS-24"], ["test", "security"])
I("E14-04", "Nghiệm thu nội bộ theo kịch bản nghiệp vụ 1 ngày chợ (BrSE, QA-1)", ["SC-25", "L1..L12"], ["test"],
  deps=["E14-01", "E12-06", "E11-02"], note="Tách sau chấm SWP lần 1 (S5 × C3 = 15 → 13).")
S("E14-04-T1", "Kịch bản sàn chợ: ロット登録 → 相対取引 / せり → 引渡し (tablet)", ["SC-05", "SC-08", "SC-10", "SC-14"], ["test"])
S("E14-04-T2", "Kịch bản văn phòng: 修正依頼 → 締め → CSV → 再出力", ["SC-12", "SC-15", "SC-19"], ["test"],
  note="Tách lần 2 sau chấm SWP (E14-04-T2 gồm cả 完納奨励金: S5 × C3 = 15 → 13).")
S("E14-04-T3", "Kịch bản 完納奨励金: soạn / duyệt phiên bản quy tắc → ghi 入金日 đúng hạn / trễ hạn → đối chiếu số tiền", ["SC-17", "SC-18", "L8"], ["test", "incentive"],
  note="Tách lần 2 sau chấm SWP.")

# ---------------- bổ sung spec_refs ----------------
EXTRA = {
    "E08-02": ["CS-08", "L2", "G-01", "G-10"], "E08-02-DB": ["G-01"],
    "E06-04": ["CS-09", "L3", "G-16"], "E06-04-API": ["CS-09"],
    "E05-04": ["CS-01", "L10"], "E05-02": ["L12"], "E05-03": ["CS-23", "L12"],
    "E02-02": ["L9", "G-11"], "E09-02": ["G-08", "G-17"], "E09-04": ["G-13"],
    "E11-01": ["G-27", "P-06"], "E10-01": ["T07", "T08"], "E01-06": ["M12"],
}
for x in items:
    for r in EXTRA.get(x["id"], []):
        if r not in x["spec_refs"]:
            x["spec_refs"].append(r)

# ---------------- kiểm tra ----------------
ids = [x["id"] for x in items]
assert len(ids) == len(set(ids)), "trùng id"
idset = set(ids)
for x in items:
    for d in x["depends_on"]:
        assert d in idset, (x["id"], d)
    if x["parent"]:
        assert x["parent"] in idset, (x["id"], x["parent"])
# issue có sub-issue không mang nhãn layer riêng lẻ là ổn; đảm bảo sub-issue có cha là issue
for x in items:
    if x["type"] == "sub-issue":
        p = next(y for y in items if y["id"] == x["parent"])
        assert p["type"] == "issue"

os.makedirs(os.path.join(OUT, "backlog"), exist_ok=True)
with open(os.path.join(OUT, "backlog", "backlog.json"), "w", encoding="utf-8", newline="\n") as f:
    f.write("[\n")
    f.write(",\n".join("  " + json.dumps(x, ensure_ascii=False) for x in items))
    f.write("\n]\n")

# ---- bảng Spec -> issue ----
def expand(ref):
    return [ref]
spec_map = defaultdict(lambda: defaultdict(list))
for x in items:
    for r in x["spec_refs"]:
        spec_map[r][x["epic"]].append(x["id"])

def sort_key(r):
    order = ["SC-", "API-", "DD-", "D-", "ADR-", "CS-", "L", "G-", "P-", "T", "M", "W-", "Q", "PREMISE"]
    for i, p in enumerate(order):
        if r.startswith(p):
            nums = re.findall(r"\d+", r)
            return (i, int(nums[0]) if nums else 0, r)
    return (99, 0, r)

GROUPS = [
    ("2.1 Màn hình (SC)", lambda r: r.startswith("SC-")),
    ("2.2 API", lambda r: r.startswith("API-")),
    ("2.3 Database – chênh lệch thiết kế ↔ prototype (D)", lambda r: r.startswith("D-")),
    ("2.4 Detail design (DD) và ADR", lambda r: r.startswith("DD-") or r.startswith("ADR-")),
    ("2.5 Tiền đề (P) và luật nghiệp vụ (L, G)", lambda r: r.startswith("P-") or re.match(r"^L\d", r) or r.startswith("G-")),
    ("2.6 Common spec (CS)", lambda r: r.startswith("CS-")),
    ("2.7 Kịch bản test (T) và mã khác (M, W, Q)", lambda r: True),
]
def row(r):
    eps = spec_map[r]
    iss = []
    for e in sorted(eps):
        iss += [i for i in eps[e] if len(i) > 3]
    return f"| {r} | {', '.join(sorted(eps))} | {', '.join(iss) if iss else '(cấp epic)'} |"
done, md = set(), []
for title, pred in GROUPS:
    rs = [r for r in sorted(spec_map, key=sort_key) if r not in done and pred(r)]
    done.update(rs)
    md.append(f"### {title}\n\n| Spec (mã) | Epic | Issue / sub-issue |\n|---|---|---|")
    md += [row(r) for r in rs]
    md.append("")
spec_md = "\n".join(md)

epics = [x for x in items if x["type"] == "epic"]
et = ["| Mã | Epic | Spec gốc | Issue | Sub-issue | Phạm vi |", "|---|---|---|---|---|---|"]
for e in epics:
    n_i = sum(1 for y in items if y["type"] == "issue" and y["epic"] == e["id"])
    n_s = sum(1 for y in items if y["type"] == "sub-issue" and y["epic"] == e["id"])
    et.append(f"| {e['id']} | {e['title']} | {', '.join(e['spec_refs'])} | {n_i} | {n_s} | {e['note']} |")
cnt = Counter(x["type"] for x in items)
total = f"{cnt['epic']} epic · {cnt['issue']} issue · {cnt['sub-issue']} sub-issue ({len(items)} dòng trong backlog.json)."
reuse = str(sum(1 for x in items if RP in x["labels"]))

tb = os.path.join(OUT, "task-breakdown.md")
txt = open(tb, encoding="utf-8").read()
blocks = {"TOTAL": total, "REUSE": reuse, "EPIC_TABLE": "\n" + "\n".join(et) + "\n", "SPEC_TABLE": "\n" + spec_md + "\n"}
for k, v in blocks.items():
    pat = re.compile(r"(<!-- BEGIN:%s -->).*?(<!-- END:%s -->)" % (k, k), re.S)
    assert pat.search(txt), "thiếu cặp marker " + k
    txt = pat.sub(lambda m: m.group(1) + v + m.group(2), txt)
open(tb, "w", encoding="utf-8", newline="\n").write(txt)

# ---- kiểm mã nhắc trong các file .md đều có trong backlog ----
bad = {}
for name in ("task-breakdown.md", "PREMISE.md"):
    p = os.path.join(OUT, name)
    if os.path.exists(p):
        refs = set(re.findall(r"\bE\d\d(?:-\d\d(?:-(?:DB|API|UI|T)\d?)?)?\b", open(p, encoding="utf-8").read()))
        miss = sorted(refs - idset)
        if miss:
            bad[name] = miss
assert not bad, "mã không có trong backlog: %s" % bad

print(dict(cnt), "| reuse-prototype:", reuse)
