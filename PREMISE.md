# PREMISE – Tiền đề của backlog LAB-5 (Product A)

> Nền: bộ thiết kế LAB-4 trong repo thiết kế LAB-4 (private) (`specs/PREMISE.md` với P-01…P-07, `specs/06_database/diff.md`, ADR-001…012, screen spec, detail design). Repo đó chỉ đọc trong LAB-5 – **không sửa**.
> File này ghi những gì LAB-5 **thay đổi hoặc chốt thêm** khi chia task ([task-breakdown.md](task-breakdown.md)). Mã giả định nối tiếp LAB-4: **P-08…P-16**. Mã chỗ hở GAP-xx theo task-breakdown.md mục 4.
> Các sửa ở mục 1 áp dụng khi làm LAB-5; PL đồng bộ lại vào bộ thiết kế LAB-4 (repo thiết kế LAB-4 (private)) khi được phép sửa.

## 1. Spec thêm / bỏ / sửa so với LAB-4

| Spec (mã / file) | Thêm / Bỏ / Sửa | Trước → sau | Vì sao | Issue bị ảnh hưởng |
|---|---|---|---|---|
| DD-06 – sơ đồ sequence và bước 5–8 (`specs/02_detail-design/source/DD-06_tinh-thuong-hoan-nap.md`) | Sửa | API tự khóa dòng, tính, ghi `payments`, ghi lưu vết bằng nhiều lệnh → API chỉ gọi **1 hàm database `record_payment`** chạy cả 4 việc trong 1 transaction | **GAP-04** phát hiện khi break E12-05: DD-06 trái D-33 và CS-15 (lưu vết cùng transaction). Giả định P-08 | E12-05-DB, E12-05-API, E12-05-T |
| API-11 審査結果の登録 (`specs/01_screen-spec/source/api_list.md`) | Sửa | Chỉ ghi 許可 / 不許可 → ghi **mọi chuyển trạng thái hợp lệ theo `kind`**: 審査開始 (申請中 → 審査中), 審査結果 (許可 / 不許可), 承認結果 (届出 → 承認) | **GAP-11** phát hiện khi break E06-04: SC-03 STD-02 và STD-07 không có API nào. Giả định P-13 | E06-04-DB, E06-04-API, E06-04-T, E06-05-UI1, E06-05-UI2 |
| `audit_logs.market_id` (D-09; `specs/06_database/er-design.md` mục 2.7) | Sửa | `not null` cho mọi dòng → `null` được **chỉ khi `table_name = 'auth'`** | **GAP-16** phát hiện khi break E05-05: lưu vết đăng nhập (D-38) xảy ra trước khi biết chợ. Giả định P-14 | E02-02-DB1, E03-02-DB2, E05-05-API |
| D-33 – phạm vi lưu vết cùng transaction (`specs/06_database/diff.md`) | Sửa | 5 thao tác (確定, 取消, 締め, 入金日, 引渡し) → **mọi thao tác ghi**, qua hàm `write_audit` chung + trigger cho bảng chưa có hàm nghiệp vụ | **GAP-22** phát hiện khi break E02-02: D-33 hẹp hơn CS-15 ("mọi thao tác"). Giả định P-16 | E02-02-DB1, E02-02-DB2, E02-02-T |
| `market_rules.incentive_rate`, `incentive_tax_factor`, `payments.amount_due` (ADR-008, er-design) | Sửa | 料率 `0 ≤ x < 1` không giới hạn số lẻ, `amount_due numeric` → 料率 tối đa 6 chữ số thập phân, 係数 tối đa 3, `amount_due` số nguyên yên ≥ 0 (check constraint) | **GAP-06** phát hiện khi break E12-02: không quy định thì không đổi được sang phân số chính xác (DD-06 bước 3). Giả định P-10 | E04-01-DB1, E12-02, E12-05-DB |
| ADR-008 – quy tắc duyệt phiên bản (`specs/05_adr/ADR-008-…md`) | Sửa | Mọi phiên bản qua luồng duyệt, không duyệt `effective_from` ≤ 営業日 → thêm **ngoại lệ cho phiên bản v1** tạo bằng migration, hiệu lực quá khứ | **GAP-10** phát hiện khi break E04-01: DD-02 bắt buộc có phiên bản từ đầu (D-03: hiệu lực 2026-04-01) nên v1 không đi qua được luồng duyệt. Giả định P-12 | E04-01-DB2, E04-01-T, E12-07 |

## 2. Giả định bổ sung

| Giả định | Chỗ spec / RFP để ngỏ | Ảnh hưởng tới issue / estimate |
|---|---|---|
| **P-08** Ghi 入金日 bằng hàm database `record_payment` 1 transaction: khóa dòng, kiểm G-22 / G-23, tính, lưu `incentive_amount` + `rule_version_id`, ghi lưu vết | DD-06 vẽ nhiều bước ở API; D-33 nói hàm database (GAP-04) | E12-05-DB chấm C nền 4 (transaction + khóa dòng). Đã có câu trả lời tạm → **không** cộng "câu hỏi mở". Nếu PL bác: bỏ hàm, làm ở API, E12-05-DB nhỏ đi nhưng mất tính nguyên tử |
| **P-09** 入金日 và 支払期限 là giá trị ngày (`date`) theo 営業日, so sánh trực tiếp; 営業日 hiện tại chỉ là giá trị mặc định và giới hạn trên của 入金日 (G-22) | LAB-4 PREMISE luật #7 nói tính theo 営業日 nhưng không nói 入金日 nhập theo ngày lịch hay 営業日 (GAP-05) | E12-03 (test biên đúng hạn / trễ 1 ngày), E12-05-T. Không đổi phạm vi |
| **P-10** `amount_due` là số nguyên yên ≥ 0; 料率 tối đa 6 chữ số thập phân; 係数 tối đa 3 chữ số thập phân | ADR-008 chỉ nói 0 ≤ 料率 < 1; `amount_due numeric` (GAP-06) | Thêm check constraint ở E04-01-DB1; E12-02 đổi phân số theo 10^6 / 10^3. Nếu khách cần 料率 lẻ hơn: chỉ đổi hằng số và check |
| **P-11** Phiên bản quy tắc dùng cho 営業日 chọn theo ngày lịch địa phương của thời điểm (DD-02); chỉ đổi mốc chuyển ngày vào ngày chợ nghỉ nên khoảng chồng 00:00 → mốc không có giao dịch | ADR-008 coi `effective_from` là 営業日, DD-02 chọn theo ngày lịch (GAP-08) | E03-03-DB, E03-03-T thêm ca đổi mốc. Phụ thuộc E03-05 (lịch 休市日) để kiểm được "ngày chợ nghỉ" |
| **P-12** Phiên bản quy tắc v1 của mỗi chợ tạo bằng migration (người dùng tự chạy); người soạn / người duyệt ghi là 2 tài khoản 精算担当 khác nhau do PL chỉ định; ngày hiệu lực quá khứ chỉ cho phép với v1 | ADR-008 (không hồi tố, người soạn ≠ người duyệt) ↔ DD-02 (bắt buộc có phiên bản từ đầu) (GAP-10) | Tách riêng E04-01-DB2 (migration v1); E12-07 dùng v1 để gắn kết quả thưởng đã có |
| **P-13** API-11 nhận mọi chuyển trạng thái hợp lệ theo `kind` (審査開始, 審査結果, 承認結果); database kiểm chuyển hợp lệ, 決定日 ≤ 営業日 | SC-03 STD-02, STD-07 không có API riêng (GAP-11) | E06-04-DB / -API gánh thêm 2 chuyển trạng thái; không thêm API mới |
| **P-14** `audit_logs.market_id` được `null` chỉ khi `table_name = 'auth'` (lưu vết đăng nhập) | D-09 bắt buộc `market_id`, D-38 ghi đăng nhập trước khi biết chợ (GAP-16) | E02-02-DB1, E03-02-DB2 (check có điều kiện); SC-20 lọc đăng nhập không theo chợ |
| **P-15** Bảng con không có `market_id` (`permits`, `permit_reviews`, `inspections`, `deliveries`, `adjustments`) lấy chợ qua bảng cha trong policy RLS (hàm `stable`), không thêm cột | D-09 chỉ thêm cột cho 6 bảng, D-30 cần `has_role(role, market_id)` (GAP-17) | E05-02-DB1 thêm hàm lấy chợ qua bảng cha; E05-02-T đo hiệu năng truy vấn. Tránh migration thêm cột ở 5 bảng |
| **P-16** Mọi thao tác ghi lưu vết qua hàm / trigger database chung trong cùng transaction; API route không tự ghi `audit_logs` | D-33 chỉ liệt kê 5 thao tác, CS-15 yêu cầu mọi thao tác (GAP-22) | E02-02 phải tách 3 sub-issue (SWP lần 1 ra 21); các route hiện có bỏ ghi log trong issue của route đó |

## 3. Hướng đã chốt

| Vấn đề | Các phương án ở LAB-4 | Phương án chốt | Vì sao |
|---|---|---|---|
| Ghi lưu vết cùng transaction – phạm vi và cơ chế | D-33: hàm nghiệp vụ cho 5 thao tác · architecture 4.3: "trigger database hoặc hàm database" · prototype: API ghi sau thao tác (G-11) | **Hàm `write_audit` chung + trigger** cho bảng chưa có hàm nghiệp vụ; hàm nghiệp vụ gọi `write_audit`; API không ghi `audit_logs` (P-16) | Đáp ứng CS-15 cho mọi thao tác bằng 1 cơ chế, test được 1 lần (E02-02-T); bỏ hẳn lỗi G-11 |
| Ghi 入金日 / tính 完納奨励金 | DD-06: tính và ghi ở API · D-33: hàm database | **Hàm database `record_payment`**; phép tính dùng chung cho xem trước (API-32) và lúc ghi (P-08) | Khóa dòng + lưu kết quả + lưu vết phải nguyên tử vì chạm tiền; xem trước và ghi phải ra cùng số |
| Phiên bản quy tắc đầu tiên | ADR-008: mọi phiên bản qua soạn → duyệt, không hồi tố · DD-02: mỗi chợ bắt buộc có phiên bản `approved` | **Migration tạo v1** với giá trị prototype, ngoại lệ ngày quá khứ chỉ cho v1 (P-12) | Hệ thống không chạy được nếu thiếu v1 (BD001); v1 không có người soạn / duyệt thật trong hệ thống |
| Lọc theo chợ cho bảng con | er-design: `market_id` ở 6 bảng · D-30: `has_role(role, market_id)` cho mọi policy | **Lấy chợ qua bảng cha** trong policy, không thêm cột (P-15) | Go-live 1 chợ (P-01); tránh migration 5 bảng; đổi lại được nếu đo thấy chậm |
| Phiên bản dùng để tính 営業日 | DD-02: theo ngày lịch địa phương · ADR-008: `effective_from` là 営業日 | **Theo DD-02**, kèm quy định chỉ đổi mốc vào ngày chợ nghỉ (P-11) | Tránh vòng lặp "cần 営業日 để tìm phiên bản quyết định 営業日"; khoảng chồng không có giao dịch |
| Trạng thái 許可 / 承認 qua API | api_list: API-11 chỉ 許可 / 不許可 · SC-03: có thêm 審査開始, 承認結果 | **Gộp vào API-11** theo `kind` (P-13) | Một chỗ kiểm chuyển trạng thái hợp lệ ở database; không thêm API |
| Tổ chức 完納奨励金 trong backlog | LAB-2 / LAB-4: 1 màn hình SC-17 + DD-06 | **Epic riêng E12**, tách theo ràng buộc (phiên bản, số nguyên, 判定, xem trước, ghi + khóa, màn hình, chuyển dữ liệu, test vector, 2 câu hỏi) | Sai = trả sai tiền; mỗi ràng buộc test độc lập với giao diện |
| Độ hạt issue | LAB-4 không quy định; estimate LAB-1 theo màn hình / chức năng | **1 issue = 1 kết quả kiểm được, ≤ ~2 ngày**; quá thì sub-issue theo lớp `-DB` / `-API` / `-UI` / `-T`, đánh số `-DB1`, `-UI2` khi phải tách tiếp sau chấm SWP | Theo DoD từng lớp; khớp quy tắc SKILL "SWP 13 / 21 bắt buộc tách" |
| Thứ tự làm | diff.md mục 5: 6 nhóm (ít rủi ro → nguyên tử → theo chợ + quy tắc → vai trò → giấy tờ → ngoài luồng) | **Theo diff.md mục 5**, đặt trước nhóm nền E01 (CI, migration, dọn dữ liệu test) và E02-01 (thu hồi quyền) | Các ràng buộc mới (unique, khóa) cần dữ liệu test của prototype được dọn trước (E01-07) |
