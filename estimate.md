# Estimate – Product A – LAB-5

## 1. Báo cáo HTML

**Báo cáo chi tiết:** [reports/swp-report.html](reports/swp-report.html) (tự chứa, mở bằng trình duyệt; lọc được theo epic).
Nguồn số liệu: [backlog/swp.json](backlog/swp.json) · điểm người chốt: [backlog/swp_review.json](backlog/swp_review.json) · skill: [skills/swp-scoring/SKILL.md](skills/swp-scoring/SKILL.md) · tiền đề: [PREMISE.md](PREMISE.md) · backlog: [task-breakdown.md](task-breakdown.md).
Các bảng trong file này sinh bằng `python -I -X utf8 tools/estimate_build.py` (sau `tools/swp_build.py`).

<!-- BEGIN:TOTAL -->**Tổng sau khi PL chốt:** 137 issue lá · **691 SWP** · **1.462 giờ** (≈ 182,8 MD) · skill chấm ban đầu 723 SWP / 1.532 giờ · 27 issue confidence = low · 18 lần tách vì SWP 13 / 21. Giờ đã gồm tự test; chưa gồm QA test riêng, PM, BrSE.<!-- END:TOTAL -->

---

## 2. Issue mẫu skill chọn để kiểm

<!-- BEGIN:SAMPLE -->
Skill chọn **53 issue mẫu** theo SKILL mục 6 (seed **20261117**): (1) mọi issue epic E12 完納奨励金, (2) 2 issue SWP cao nhất + 2 thấp nhất trong phần còn lại, (3) mọi issue `confidence = low`, (4) 1 issue ngẫu nhiên mỗi epic còn lại.

PL sửa **11 / 53 = 21%** issue mẫu. Vì **< 30%** nên theo SKILL mục 6 **giữ nguyên tiêu chí** chấm (mục 2–3 của skill), **không chấm lại toàn bộ**: chỉ áp điểm chốt cho issue mẫu, issue ngoài mẫu giữ điểm skill. Hai kiểu lỗi PL chỉ ra (cộng điểm đặc thù chồng nhau; issue làm rõ chấm như issue code) ghi ở [AI_LOG.md](AI_LOG.md) mục 2 để dùng cho AI-report.

| Issue | Skill chấm (S × C → SWP) | Bạn chốt | Lý do |
|---|---|---|---|
| `E12-01` Chọn phiên bản quy tắc có hiệu lực tại 支払期限 (料率, 係数, 猶予) | S2 × C5 (C nền 3 + Chạm tiền / làm tròn, Chạm 営業日) → 8 | **5** (10 giờ) | Logic giống E04-02 (API-33, chấm 3), dùng lại hàm E04-02; điểm cao do cộng chồng tiền + 営業日. |
| `E12-02` Tính bằng số nguyên + làm tròn xuống: 料率 / 係数 đổi phân số chính xác, đọc 係数 từ market_rules | S2 × C4 (C nền 3 + Chạm tiền / làm tròn) → 5 | 5 (10 giờ) | Đồng ý: lý do S / C khớp spec |
| `E12-03` 判定 期限内 / 期限超過 / 未入金, không ân hạn (grace_days = 0), so sánh ngày theo 営業日 | S2 × C5 (C nền 3 + Chạm tiền / làm tròn, Chạm 営業日) → 8 | **5** (10 giờ) | So 2 ngày, 3 trạng thái; test biên ngày đã có ở E12-05-T, E12-08. |
| `E12-04` Xem trước API-32 奨励金の試算 (chỉ đọc, không lưu vết) | S2 × C4 (C nền 2 + Chạm tiền / làm tròn, Chạm 営業日) → 5 | **3** (6 giờ) | Chỉ đọc, gọi lại hàm E12-01…03, không ghi. |
| `E12-05-API` API-31 gọi rpc, trả 判定 + 奨励金額 | S2 × C3 (C nền 2 + Chạm tiền / làm tròn) → 3 | 3 (6 giờ) | Đồng ý: lý do S / C khớp spec |
| `E12-05-DB` Cột D-26 + unique D-27 + hàm record_payment (khóa dòng, G-22, G-23, tính, lưu, audit) | S2 × C5 (C nền 4 + Chạm tiền / làm tròn, Chạm 営業日, Ghi đồng thời / offline) → 8 | 8 (16 giờ) | Đồng ý: lý do S / C khớp spec |
| `E12-05-T` Test: ghi 2 lần → M_62; ngày tương lai → M_61; đổi 料率 sau khi ghi không đổi số đã lưu; lưu vết record_payment | S2 × C5 (C nền 4 + Chạm tiền / làm tròn, Chạm 営業日) → 8 | **5** (10 giờ) | 4 kịch bản lớp API / DB, dùng lại dữ liệu test chung. |
| `E12-06-API` API-30 danh sách theo kỳ / 判定: đọc giá trị đã lưu, tổng Σ incentive_amount | S2 × C3 (C nền 2 + Chạm tiền / làm tròn) → 3 | 3 (6 giờ) | Đồng ý: lý do S / C khớp spec |
| `E12-06-UI1` SC-17: chọn kỳ, lọc 判定, thẻ 適用ルール, bảng có cột ルール版 / 計算内容, tổng 奨励金額 | S3 × C3 (C nền 2 + Chạm tiền / làm tròn) → 5 | 5 (10 giờ) | Đồng ý: lý do S / C khớp spec |
| `E12-06-UI2` SC-17: hộp ghi 入金日 có xem trước (API-32), M_61 / M_62 / M_67 / M_113 / M_115 | S2 × C5 (C nền 3 + Chạm tiền / làm tròn, Chạm 営業日) → 8 | **5** (10 giờ) | 1 hộp thoại, logic tính ở API (E12-04); nhất quán với E06-05-UI2. |
| `E12-07` Chuyển dữ liệu 完納奨励金: lưu kết quả (gắn phiên bản v1) cho dòng đã có 入金日; khóa rồi bỏ incentive_rates; chạy lại T13 | S3 × C4 (C nền 3 + Chạm tiền / làm tròn) → 8 | **5** (10 giờ) | Dữ liệu cũ rất ít dòng, đối chiếu bằng T13 sẵn có. |
| `E12-08` Test vector Phụ lục C: khung test chạy theo bộ dữ liệu (chờ dữ liệu khách) | S2 × C5 (C nền 3 + Chạm tiền / làm tròn, Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E12-09` Làm rõ nguồn 請求: ai / khi nào lập 請求, 請求金額 tính từ đâu, 修正依頼 sau khi lập 請求 | S2 × C5 (C nền 3 + Chạm tiền / làm tròn, Spec còn câu hỏi mở) → 8 | **3** (8 giờ) | Issue làm rõ là việc PL / BrSE, không phải lập trình. |
| `E12-10` Làm rõ quy trình sửa 入金日 đã ghi nhầm (kết quả đã khóa) | S1 × C5 (C nền 3 + Chạm tiền / làm tròn, Spec còn câu hỏi mở) → 3 | 3 (8 giờ) | Đồng ý: lý do S / C khớp spec |
| `E01-07` Dọn dữ liệu test của prototype trước khi đặt khóa / unique mới | S1 × C2 (C nền 2) → 1 | 1 (2 giờ) | Đồng ý: lý do S / C khớp spec |
| `E03-01` Bảng markets + 1 chợ mặc định (go-live 1 chợ) | S2 × C1 (C nền 1) → 1 | 1 (2 giờ) | Đồng ý: lý do S / C khớp spec |
| `E04-04` Wireframe + screen spec SC-18 業務ルールの版管理 (chưa vẽ ở LAB-4) | S3 × C4 (C nền 3 + Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E05-09` Spike / làm rõ: ghi LOGIN_FAILED khi chưa có phiên và mời người dùng khi không dùng service_role | S3 × C4 (C nền 3 + Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E01-06` Làm rõ thuật ngữ 承認 (loại giấy 売買参加者) trùng với 承認 (duyệt) + BrSE review chữ hiển thị | S3 × C3 (C nền 2 + Spec còn câu hỏi mở) → 5 | 5 (12 giờ) | Đồng ý: lý do S / C khớp spec |
| `E02-04` Làm rõ thời hạn lưu audit_logs và cách lưu trữ lâu dài | S1 × C3 (C nền 2 + Spec còn câu hỏi mở) → 2 | 2 (6 giờ) | Đồng ý: lý do S / C khớp spec |
| `E03-05` Làm rõ lịch 休市日: hạn (支払期限, 有効期限) rơi vào ngày chợ nghỉ; thời điểm được đổi mốc chuyển ngày | S1 × C5 (C nền 3 + Chạm 営業日, Spec còn câu hỏi mở) → 3 | 3 (8 giờ) | Đồng ý: lý do S / C khớp spec |
| `E05-05-API` API-02: chặn locked (M_99) / không quyền (M_77) + lưu vết LOGIN_SUCCESS / LOGIN_FAILED | S2 × C5 (C nền 4 + Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E05-07` API-42 mời người dùng bằng email | S3 × C3 (C nền 2 + Spec còn câu hỏi mở) → 5 | 5 (12 giờ) | Đồng ý: lý do S / C khớp spec |
| `E06-04-API` API-08, API-09 sửa, API-11 mới | S3 × C4 (C nền 3 + Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E06-04-DB` Hàm chuyển trạng thái giấy (kiểm chuyển hợp lệ, 決定日 ≤ 営業日, 登録者 = người đăng nhập) + lưu vết | S2 × C5 (C nền 4 + Chạm 営業日, Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E06-04-T` Test luồng 許可: 申請中 → 審査中 → 許可 / 不許可; 承認: 届出 → 承認; M_122, M_124, M_64 / M_65 | S2 × C4 (C nền 3 + Spec còn câu hỏi mở) → 5 | 5 (12 giờ) | Đồng ý: lý do S / C khớp spec |
| `E06-05-UI1` SC-03: 2 tab, sơ đồ luồng, thẻ giấy hiện hành, bảng lịch sử, nút 審査開始 / đăng ký đơn | S4 × C3 (C nền 2 + Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E06-05-UI2` SC-03: hộp 審査結果の登録 / 承認結果の登録 (決定日, 決定者（開設者側）, 有効期間, 条件 / 不許可理由) | S2 × C5 (C nền 3 + Chạm 営業日, Spec còn câu hỏi mở) → 8 | **5** (12 giờ) | 1 hộp thoại, nhất quán với E12-06-UI2. |
| `E06-09` Làm rõ: thu hồi / đình chỉ giấy; 承認 có bị từ chối không; 承認 ghi như 許可 | S2 × C4 (C nền 3 + Spec còn câu hỏi mở) → 5 | **3** (8 giờ) | Issue làm rõ, như E12-09. |
| `E11-05` Làm rõ mẫu CSV phần mềm kế toán và mã ký tự (UTF-8 BOM / Shift_JIS) | S1 × C3 (C nền 2 + Spec còn câu hỏi mở) → 2 | 2 (6 giờ) | Đồng ý: lý do S / C khớp spec |
| `E11-06` Định dạng CSV theo mẫu khách (cấu hình format_version) | S2 × C4 (C nền 3 + Spec còn câu hỏi mở) → 5 | 5 (12 giờ) | Đồng ý: lý do S / C khớp spec |
| `E13-01-UI1` Spike: Service Worker giữ app chạy khi mất mạng trên Chrome / Safari tablet | S2 × C5 (C nền 3 + Ghi đồng thời / offline, Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E13-01-UI2` Spike: hàng đợi IndexedDB + gửi lại có client_uuid | S2 × C5 (C nền 3 + Ghi đồng thời / offline, Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E13-03-API` Route đồng bộ + cấp lot_no chính thức + chống trùng | S2 × C5 (C nền 4 + Chạm 営業日, Ghi đồng thời / offline, Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E13-03-T` Test: gửi lại nhiều lần chỉ ghi 1; 2 tablet giao vượt → 1 dòng lỗi; 01:30 offline → 営業日 hôm trước | S2 × C5 (C nền 4 + Chạm 営業日, Ghi đồng thời / offline, Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E13-04-UI3` SC-05 ghi ロット登録 offline vào hàng đợi, số tạm (M_101, M_102) | S2 × C5 (C nền 3 + Ghi đồng thời / offline, Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E13-04-UI4` SC-14 ghi 引渡し offline vào hàng đợi (M_101, M_102) | S2 × C5 (C nền 3 + Ghi đồng thời / offline, Spec còn câu hỏi mở) → 8 | **5** (12 giờ) | Cùng cách làm E13-04-UI3, dùng lại hàng đợi. |
| `E13-04-UI5` Tự gửi hàng đợi qua API-21 khi có mạng, hiện kết quả (M_104, M_105) | S2 × C5 (C nền 3 + Ghi đồng thời / offline, Spec còn câu hỏi mở) → 8 | 8 (20 giờ) | Đồng ý: lý do S / C khớp spec |
| `E13-05-UI1` Wireframe + screen spec SC-24 theo template | S3 × C3 (C nền 2 + Spec còn câu hỏi mở) → 5 | 5 (12 giờ) | Đồng ý: lý do S / C khớp spec |
| `E13-06` Làm rõ thời gian offline tối đa và tablet dùng chung / riêng | S1 × C4 (C nền 2 + Ghi đồng thời / offline, Spec còn câu hỏi mở) → 2 | 2 (6 giờ) | Đồng ý: lý do S / C khớp spec |
| `E01-02` Quy trình migration SQL đánh số (AI viết, người dùng tự chạy) + kiểm cấu trúc sau khi chạy | S2 × C3 (C nền 3) → 3 | 3 (6 giờ) | Đồng ý: lý do S / C khớp spec |
| `E02-01` Thu hồi quyền bảng mặc định + trigger chặn update / delete / truncate audit_logs | S2 × C3 (C nền 3) → 3 | 3 (6 giờ) | Đồng ý: lý do S / C khớp spec |
| `E03-02-DB1` Migration market_id cho participants, lots, trades + unique (market_id, code / lot_no) | S3 × C3 (C nền 3) → 5 | 5 (10 giờ) | Đồng ý: lý do S / C khớp spec |
| `E04-02` API-33 適用ルールの取得 (phiên bản approved hiệu lực tại ngày) | S2 × C3 (C nền 2 + Chạm 営業日) → 3 | 3 (6 giờ) | Đồng ý: lý do S / C khớp spec |
| `E05-02-DB2` Viết lại policy nhóm tài khoản / quy tắc / lưu vết bằng has_role | S5 × C2 (C nền 2) → 8 | 8 (16 giờ) | Đồng ý: lý do S / C khớp spec |
| `E06-02` Bảng permit_reviews + ghi lịch sử mỗi lần chuyển trạng thái | S2 × C2 (C nền 2) → 2 | 2 (4 giờ) | Đồng ý: lý do S / C khớp spec |
| `E07-03` Wireframe + giao diện tablet SC-07 目利き結果入力 | S3 × C2 (C nền 2) → 3 | 3 (6 giờ) | Đồng ý: lý do S / C khớp spec |
| `E08-02-T` Test T03, T04, T05, tranh chấp 2 người cùng lúc, G-04, rollback khi lỗi lưu vết | S2 × C5 (C nền 4 + Ghi đồng thời / offline) → 8 | 8 (16 giờ) | Đồng ý: lý do S / C khớp spec |
| `E09-02-DB` Hai hàm database + check decided_by <> requested_by | S2 × C5 (C nền 4 + Chạm tiền / làm tròn, Ghi đồng thời / offline) → 8 | 8 (16 giờ) | Đồng ý: lý do S / C khớp spec |
| `E10-03` SC-13 引渡し待ち一覧 + API-20 (mọi 営業日) | S3 × C2 (C nền 2) → 3 | 3 (6 giờ) | Đồng ý: lý do S / C khớp spec |
| `E11-01-API` API-27 gọi rpc | S2 × C2 (C nền 2) → 2 | 2 (4 giờ) | Đồng ý: lý do S / C khớp spec |
| `E13-02` Cột client_uuid / client_recorded_at / synced_at cho lots, deliveries + unique | S3 × C3 (C nền 2 + Ghi đồng thời / offline) → 5 | **3** (6 giờ) | Chỉ thêm cột nullable + unique, không chuyển dữ liệu (S = 2). |
| `E14-04-T2` Kịch bản văn phòng: 修正依頼 → 締め → CSV → 再出力 | S5 × C2 (C nền 2) → 8 | 8 (16 giờ) | Đồng ý: lý do S / C khớp spec |
<!-- END:SAMPLE -->

---

## 3. Cách quy ra giờ

**Cách đã chọn:** quy ước đổi **SWP → giờ cố định**, áp như nhau cho mọi issue (SKILL mục 5). **Không** ước giờ trực tiếp cho từng issue.

**Vì sao:**
- Giờ ước trực tiếp từng issue phụ thuộc người ước, khó kiểm lại và khó so giữa các issue. SWP chấm theo 2 trục có lý do ghi rõ (S, C trỏ mã spec), người review sửa **điểm**, không sửa **giờ** → tranh luận tập trung vào độ lớn / độ khó, không vào con số giờ.
- Cùng 1 bảng quy đổi cho mọi issue → tổng giờ chỉ đổi khi điểm đổi; khi chấm lại (backlog đổi, người chốt sửa) giờ tự tính lại, không phải ước lại.
- Dãy Fibonacci (1, 2, 3, 5, 8) giữ sai số tương đối: issue càng lớn càng khó ước chính xác; issue ra 13 / 21 bắt buộc tách (đã tách 18 lần) để mọi issue ≤ khoảng 2 ngày công.

**Quy tắc cụ thể:**

| SWP | 1 | 2 | 3 | 5 | 8 |
|---|---|---|---|---|---|
| Giờ | 2 | 4 | 6 | 10 | 16 |
| Giờ khi `confidence = low` (+20%, làm tròn lên số chẵn) | 4 | 6 | 8 | 12 | 20 |

- 1 SWP ≈ 2 giờ của 1 người có kinh nghiệm; **đã gồm** tự test (unit / integration của chính issue) và sửa lỗi review.
- **Chưa gồm** QA test riêng, quản lý dự án (PM), BrSE – cộng ở cấp tổng theo tỷ lệ như estimate LAB-1 (bước sau, không thuộc file này).
- `confidence = low` khi issue còn câu hỏi mở chưa có trả lời (Q-xx, câu hỏi mở ADR, chỗ hở chưa có giả định, dữ liệu khách chưa có) → +20% dự phòng cho chính issue đó.

**Cách áp dụng nhất quán:**
1. Chỉ chấm issue / sub-issue **lá**; issue cha = tổng con (không chấm riêng, không cộng thêm).
2. Giờ tính bằng script (`tools/swp_build.py`) từ SWP cuối cùng: SWP người chốt nếu có (`swp_review.json`), ngược lại SWP của skill. Không chỉnh tay giờ; muốn đổi giờ thì đổi S / C hoặc `swp_chot` kèm lý do.
3. Issue ngoài mẫu giữ điểm skill vì tỷ lệ sửa < 30% (mục 2). Nếu lần sau ≥ 30% thì sửa tiêu chí và chấm lại toàn bộ.
4. Quy đổi sang MD khi so với LAB-1: **giờ ÷ 8**.

---

## 4. Tổng theo epic

<!-- BEGIN:EPIC -->
| Epic | Số issue (lá) | Tổng SWP | Tổng giờ | Ghi chú |
|---|---|---|---|---|
| `E01` Nền tảng dự án và quy ước chung | 7 | 19 | 40 | Hạng mục WBS (CI, môi trường, migration, từ điển); không có trong function MD của LAB-1. |
| `E02` Lưu vết chỉ thêm và quyền database | 9 | 33 | 68 | Ràng buộc: lưu vết chỉ thêm, cùng transaction cho mọi thao tác (P-16 – PREMISE.md dòng 30). |
| `E03` Chợ và 営業日 theo cấu hình chợ | 9 | 43 | 88 | Ràng buộc đặc thù **営業日 theo chợ** (P-11 – PREMISE.md dòng 25); issue làm rõ 休市日 (low). |
| `E04` Quy tắc vận hành theo chợ có phiên bản (SC-18) | 10 | 57 | 118 | Quy tắc có phiên bản, người soạn ≠ người duyệt; phiên bản v1 bằng migration (P-12 – PREMISE.md dòng 26). Nền của E03 và E12. |
| `E05` Xác thực và phân quyền nhiều vai trò | 16 | 94 | 198 | Phân quyền nhiều vai trò; 3 issue low chờ spike E05-09 (GAP-14, GAP-15 – không dùng service_role). |
| `E06` Người tham gia và 許可 / 承認 hai luồng | 13 | 72 | 162 | Ràng buộc đặc thù **許可 / 承認 hai luồng**; 6 issue low vì câu hỏi mở ADR-009. |
| `E07` Lô hàng và 目利き | 4 | 9 | 18 | Chủ yếu tận dụng prototype LAB-2 (SC-05, SC-06, SC-07 chạy thật). |
| `E08` Giao dịch 相対取引 / せり / 取消 | 11 | 48 | 96 | Ràng buộc: confirm_trade 1 transaction, L4 khóa lô không tự hủy, G-04 (締め). |
| `E09` 修正依頼 (sửa sau khi chốt) | 6 | 30 | 60 | Ràng buộc đặc thù **người tạo ≠ người duyệt** (L7) kiểm theo bản ghi. |
| `E10` 引渡し (giao hàng nhiều lần) | 5 | 24 | 48 | Trigger L5; được giao cho ngày đã 締め (LAB-4 PREMISE P-06). |
| `E11` 締め và xuất CSV kế toán | 13 | 63 | 130 | Ràng buộc đặc thù **締め** (không mở lại, snapshot); CSV theo mẫu khách chưa có (2 issue low). |
| `E12` 完納奨励金 (thưởng trả đúng hạn) | 14 | 66 | 140 | **EPIC RIÊNG 完納奨励金** (tiền + 営業日 + phiên bản quy tắc + khóa kết quả). PL chốt giảm 7 issue mẫu (88 → 66 SWP). |
| `E13` Offline hẹp cho tablet (ロット登録, 引渡し入力) | 13 | 82 | 194 | Offline hẹp (ADR-012); 9 issue low chờ Q8 → +20% dự phòng. |
| `E14` Kiểm thử hệ thống và chuẩn bị go-live | 7 | 51 | 102 | Hạng mục WBS (hồi quy, test bảo mật, nghiệm thu nội bộ); không có trong function MD của LAB-1. |
| **Tổng** | **137** | **691** | **1.462** | ≈ 182,8 MD; chưa gồm QA test riêng, PM, BrSE |
<!-- END:EPIC -->

---

## 5. So với estimate LAB-1

Cách so cùng đơn vị: **LAB-5 = giờ ÷ 8 (MD, đã gồm tự test)** so với **LAB-1 = MD theo function × 1,3** (LAB-1 tính dev MD chưa gồm unit test 30%). Cả hai **chưa gồm** QA test riêng, PM, BrSE, dự phòng.

<!-- BEGIN:LAB1 -->
| Phần (chức năng / epic) | LAB-1 (MD × 1,3) | LAB-5 (giờ ÷ 8) | Chênh | Vì sao |
|---|---|---|---|---|
| F-01 ↔ E05 | 39,0 (30 MD) | 24,8 | −14,2 | Gộp 7 → 3 vai trò (LAB-4 `specs/PREMISE.md` dòng 16) và thu gọn SC-21 (dòng 18); tận dụng prototype (requireRole, SC-01, SC-21). MFA chưa thiết kế (task-breakdown 2.8). Phần thêm: has_role + viết lại policy (P-15 – PREMISE.md dòng 29), spike không dùng service_role. |
| F-02 ↔ E02 | 20,8 (16 MD) | 8,5 | −12,3 | audit_logs + SC-20 đã chạy thật ở prototype; LAB-5 chỉ thêm chặn quyền / trigger, view che, phân trang. Lưu vết mọi thao tác gom về 1 hàm chung (P-16 – PREMISE.md dòng 30, spec sửa dòng 14). |
| F-05 + F-06 ↔ E06 | 48,1 (19 + 18 MD) | 20,2 | −27,9 | SC-02, SC-03 chạy thật ở prototype; SC-04 gộp vào SC-02 (LAB-4 PREMISE dòng 17). Phần tăng: 2 luồng 許可 / 承認 (LAB-4 PREMISE dòng 21; API-11 – PREMISE.md dòng 12, P-13 dòng 27), 6 issue low. |
| F-07 + F-08 + F-09 ↔ E07 | 40,3 (16 + 5 + 10 MD) | 2,2 | −38,1 | SC-05, SC-06, SC-07 chạy thật ở prototype; LAB-5 chỉ chỉnh giao diện tablet + API-14. Phần offline của ロット登録 tính ở E13. |
| F-10 + F-11 ↔ E08 | 42,9 (24 + 9 MD) | 12,0 | −30,9 | SC-08, SC-09, SC-10 + trigger L4 có sẵn ở prototype; LAB-5 chỉ chuyển kiểm luật vào hàm database 1 transaction và thêm cột (D-19…D-21). |
| F-12 ↔ E09 | 24,7 (19 MD) | 7,5 | −17,2 | SC-11, SC-12 chạy thật; duyệt 1 cấp (LAB-4 PREMISE dòng 56). LAB-5 chỉ thêm hàm 1 transaction + cột reject_reason / decided_by. |
| F-13 ↔ E10 | 20,8 (16 MD) | 6,0 | −14,8 | SC-13, SC-14 chạy thật; LAB-5 chỉ thêm trigger L5 + hàm ghi. Offline 引渡し tính ở E13. F-14 xem dòng riêng. |
| F-15 + F-18 ↔ E11 | 33,8 (21 + 5 MD) | 16,2 | −17,6 | 締め + CSV có sẵn (đơn giản) ở prototype; CSV sau 締め, không API kế toán (LAB-4 PREMISE dòng 55). Thêm export_batches, cờ cần xuất lại; CSV theo mẫu khách chưa có (low). |
| F-16 ↔ E12 | 27,3 (21 MD) | 17,5 | −9,8 | Phép tính BigInt có sẵn ở prototype; tách epic riêng theo ràng buộc; thêm hàm record_payment (P-08 – PREMISE.md dòng 22, spec sửa dòng 11), miền 料率 (P-10 – dòng 24). PL chốt giảm 22 SWP (AI_LOG lỗi 1, 2). |
| F-17 ↔ E03 + E04 | 18,2 (14 MD) | 25,8 | +7,6 | **Tăng**: thiết kế mới quy tắc theo chợ có phiên bản (LAB-4 PREMISE dòng 20) + market_id cho 6 bảng + 営業日 theo chợ (P-11 – PREMISE.md dòng 25) + phiên bản v1 bằng migration (P-12 – dòng 26, spec sửa dòng 16). Prototype chỉ có mock (M4), không tận dụng được. |
| F-22 ↔ E13 | 23,4 (18 MD) | 24,2 | +0,8 | Prototype không làm offline (M6) nên không tận dụng; phạm vi hẹp 2 thao tác (LAB-4 PREMISE dòng 47) kéo xuống, 9 issue low +20% (Q8) kéo lên → gần bằng. |
| F-03 | 7,8 (6 MD) | 0 | −7,8 | Chưa có trong thiết kế LAB-4 → chưa thành issue – [task-breakdown.md](task-breakdown.md) mục 2.8 "Phần spec chưa thành issue". |
| F-04 | 10,4 (8 MD) | 0 | −10,4 | Chưa có trong thiết kế LAB-4 → chưa thành issue – [task-breakdown.md](task-breakdown.md) mục 2.8 "Phần spec chưa thành issue". |
| F-14 | 13,0 (10 MD) | 0 | −13,0 | Chưa có trong thiết kế LAB-4 → chưa thành issue – [task-breakdown.md](task-breakdown.md) mục 2.8 "Phần spec chưa thành issue". |
| F-19 | 28,6 (22 MD) | 0 | −28,6 | Chưa có trong thiết kế LAB-4 → chưa thành issue – [task-breakdown.md](task-breakdown.md) mục 2.8 "Phần spec chưa thành issue". |
| F-20 | 18,2 (14 MD) | 0 | −18,2 | Chưa có trong thiết kế LAB-4 → chưa thành issue – [task-breakdown.md](task-breakdown.md) mục 2.8 "Phần spec chưa thành issue". |
| F-21 | 6,5 (5 MD) | 0 | −6,5 | Chưa có trong thiết kế LAB-4 → chưa thành issue – [task-breakdown.md](task-breakdown.md) mục 2.8 "Phần spec chưa thành issue". |
| F-23 | 20,8 (16 MD) | 0 | −20,8 | Chưa có trong thiết kế LAB-4 → chưa thành issue (F-23: chuyển dữ liệu hệ thống cũ – M9) – [task-breakdown.md](task-breakdown.md) mục 2.8 "Phần spec chưa thành issue". |
| **Cộng phần function** | **444,6** (342 MD) | **165,0** | **−279,6** | LAB-5 = 37% LAB-1. Bỏ 7 function chưa có thiết kế: 165,0 / 339,3 = 49%. |
| E01 + E14 ↔ hạng mục WBS | — (nằm trong WBS, không có trong function MD) | 17,8 | — | Nền dự án (CI, môi trường, migration) và kiểm thử hệ thống; LAB-1 tính ở WBS cùng test / PM / BrSE. |
| **Tổng LAB-5 (dev + tự test)** | — | **182,8** | — | = 1.462 giờ ÷ 8. |

- Tổng dự án LAB-1 là **1.050,6 MD** (gồm test, PM, BrSE, dự phòng). LAB-5 hiện chỉ có phần dev + tự test (**182,8 MD**); QA test riêng, PM, BrSE, dự phòng sẽ cộng ở cấp tổng theo tỷ lệ như LAB-1 (bước sau) – **chưa so được** ở cấp tổng dự án.
- Chênh lớn nhất ở phần đã chạy thật trong prototype LAB-2 (E07, E08, E09, E10, E06): LAB-5 chỉ tính phần **sửa theo thiết kế LAB-4**, không tính lại phần đã có (nhãn `reuse-prototype`, 35 mục).
- Phần **tăng** so với LAB-1 (E03 + E04) đến từ thay đổi thiết kế ở LAB-4 (quy tắc theo chợ có phiên bản) và giả định LAB-5 (PREMISE.md mục 1–2).
- Rủi ro: quy ước 1 SWP ≈ 2 giờ chưa được hiệu chỉnh bằng số liệu thật của đội; nếu sprint đầu cho thấy lệch, sửa bảng quy đổi (SKILL mục 5) cho mọi issue, không sửa từng issue.
- 7 function chưa có thiết kế (≈ 105,3 MD theo LAB-1) chưa nằm trong LAB-5; khi có spec phải chia task và chấm thêm.
<!-- END:LAB1 -->
