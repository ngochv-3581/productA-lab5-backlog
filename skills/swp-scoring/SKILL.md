---
name: swp-scoring
description: Chấm điểm SWP (Scope × Complexity → SWP) và quy đổi ra số giờ cho từng issue trong backlog, xuất báo cáo HTML và danh sách issue mẫu để người chốt. Dùng khi cần ước lượng backlog (backlog/backlog.json) cho GitHub Project, khi được yêu cầu "chấm SWP", "ước lượng story point", "quy đổi giờ", hoặc chấm lại sau khi người review sửa điểm.
---

# Skill chấm SWP – Scope × Complexity → SWP → giờ

SWP (Story Weight Point) là điểm ước lượng của 1 issue, tính từ 2 trục chấm riêng rồi tra bảng.
Mục tiêu: **chấm nhất quán, có lý do ghi rõ, người kiểm lại được** – không phải đoán 1 con số.

## 1. Đầu vào

- `backlog/backlog.json`: mỗi dòng có `id, epic, title, parent, type, spec_refs, labels, depends_on, note`.
- Bộ thiết kế để tra khi chấm (chỉ đọc): screen spec, detail design, diff database, ADR, PREMISE.
- Nếu có: `backlog/swp_review.json` – điểm người đã chốt ở lần trước.

## 2. Trục 1 – Scope (S): issue chạm vào bao nhiêu thứ

| S | Tiêu chí (chọn mức cao nhất mà issue thỏa) |
|---|---|
| 1 | Sửa nhỏ 1 chỗ: 1 hằng số, 1 câu thông báo, 1 cột / ràng buộc database không cần chuyển dữ liệu |
| 2 | 1 lớp: chỉ database (bảng / hàm / trigger nhỏ) **hoặc** chỉ 1 API **hoặc** chỉ giao diện 1 khu vực màn hình |
| 3 | 2 lớp (ví dụ API + giao diện) **hoặc** 1 màn hình đầy đủ ít trường (≤ 8 mục trong bảng View) **hoặc** chuyển dữ liệu cũ sang cấu trúc mới |
| 4 | 3 lớp (database + API + giao diện) **hoặc** 1 màn hình nhiều trường / nhiều trạng thái (> 8 mục, có hộp thoại) |
| 5 | Nhiều màn hình / nhiều bảng cùng lúc, **hoặc** thay đổi dùng chung ảnh hưởng toàn hệ thống (phân quyền, hàm dùng chung, khung giao diện) |

## 3. Trục 2 – Complexity (C): logic khó và rủi ro tới đâu

Chấm mức nền, rồi **cộng điểm đặc thù**, tối đa 5.

| C nền | Tiêu chí |
|---|---|
| 1 | Hiển thị / lưu thẳng, không có luật |
| 2 | Kiểm tra nhập đơn giản (bắt buộc, khoảng giá trị), 1 luật |
| 3 | 2–3 luật nghiệp vụ, có rẽ nhánh lỗi rõ ràng (mã thông báo M_xx) |
| 4 | Nhiều luật đan xen **hoặc** cần 1 transaction / khóa dòng để chống ghi đồng thời |
| 5 | Logic tính toán nhiều biến có tiền / ngày **và** đồng thời / đồng bộ, hoặc thiết kế còn chỗ mở lớn |

**Cộng điểm đặc thù Product A** (+1 mỗi mục, tổng C không quá 5):
- Chạm tiền hoặc làm tròn (完納奨励金, 金額, snapshot 締め).
- Chạm **営業日** (mốc chuyển ngày theo chợ, không dùng ngày máy).
- Ghi đồng thời / offline đồng bộ (trigger khóa dòng, client_uuid).
- Spec còn **câu hỏi mở chưa có trả lời** (Q-xx, câu hỏi mở trong ADR) → đồng thời đánh dấu `confidence = low`.

## 4. Tra bảng S × C → SWP (dãy Fibonacci)

| S × C | 1–2 | 3–4 | 5–6 | 8–9 | 10–12 | 15–16 | 20–25 |
|---|---|---|---|---|---|---|---|
| **SWP** | 1 | 2 | 3 | 5 | 8 | 13 | 21 |

- **SWP 13 hoặc 21 → bắt buộc tách** thành sub-issue rồi chấm lại từng sub-issue (vượt định nghĩa "tối đa khoảng 2 ngày công / issue"). Không để issue 13 / 21 lên Project.
- Issue cha (có sub-issue) **không chấm riêng**: SWP cha = tổng SWP các sub-issue.

## 5. Quy đổi giờ (quy ước cố định, áp dụng như nhau cho mọi issue)

| SWP | 1 | 2 | 3 | 5 | 8 |
|---|---|---|---|---|---|
| **Giờ** | 2 | 4 | 6 | 10 | 16 |

- Quy ước: **1 SWP ≈ 2 giờ** của 1 người làm có kinh nghiệm, **đã gồm** tự test và sửa lỗi review; **chưa gồm** QA test riêng, quản lý, BrSE (cộng ở cấp tổng theo tỷ lệ như estimate LAB-1).
- Cộng **+20% giờ** (làm tròn lên số chẵn) nếu `confidence = low` – phần dự phòng cho câu hỏi chưa có trả lời. Ghi rõ trong cột lý do.
- Không chỉnh tay số giờ ngoài quy ước này; muốn đổi thì đổi điểm S / C (có lý do).

## 6. Chọn issue mẫu để người chốt

Chọn **ít nhất 12 issue**, ưu tiên theo thứ tự:
1. **Mọi issue của epic ràng buộc đặc thù** (ví dụ 完納奨励金).
2. 2 issue SWP cao nhất và 2 issue SWP thấp nhất.
3. Mọi issue `confidence = low`.
4. 1 issue ngẫu nhiên ở mỗi epic còn lại (ghi seed để chọn lại được).

Người review ghi vào `backlog/swp_review.json`: `id, swp_ai, swp_chot, ly_do`.
Nếu người chốt khác AI ở **≥ 30% số issue mẫu**: không sửa từng con số, mà **sửa tiêu chí ở mục 2–3** cho đúng, rồi chấm lại toàn bộ.

## 7. Đầu ra

1. `backlog/swp.json`: mỗi issue có `id, S, S_ly_do, C_nen, C_cong (danh sách mục +1), C, C_ly_do, SWP, gio, confidence, can_tach`.
2. `reports/swp-report.html` (1 file, tự chứa, không gọi mạng):
   - Tóm tắt: số issue, tổng SWP, tổng giờ, phân bố SWP (biểu đồ cột đơn giản bằng HTML/CSS).
   - Bảng issue mẫu: `Issue | Skill chấm (S × C → SWP) | Bạn chốt | Lý do` (cột "Bạn chốt" lấy từ swp_review.json, chưa có thì để trống).
   - Bảng toàn bộ issue (lọc được theo epic).
   - Danh sách issue phải tách (13 / 21) và issue `confidence = low`.
   - Tổng theo epic: `Epic | Số issue | Tổng SWP | Tổng giờ`.
   - Ghi ngày chạy, phiên bản skill, quy ước quy đổi giờ.
3. Báo lại người dùng: tổng SWP / giờ, số issue phải tách, danh sách issue mẫu cần chốt.

## 8. Quy tắc

- Mỗi điểm S và C **phải có lý do 1 câu**, trỏ mã spec (SC-xx, DD-xx, D-xx, L-xx…).
- Không chép câu chữ từ tài liệu khách vào lý do (repo public).
- Chấm lại toàn bộ khi backlog đổi; giữ `swp_chot` của người nếu issue không đổi.
