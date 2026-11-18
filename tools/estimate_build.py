# -*- coding: utf-8 -*-
"""Sinh các bảng của estimate.md từ backlog/swp.json + backlog/swp_review.json.
Chạy từ gốc repo, sau tools/swp_build.py:  python -I -X utf8 tools/estimate_build.py
Thay nội dung giữa <!-- BEGIN:X --> / <!-- END:X --> (TOTAL, SAMPLE, EPIC, LAB1).
Số liệu LAB-1 (dev MD theo function, chưa gồm unit test 30%) do PL cung cấp ở bước estimate LAB-5.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
swp = json.load(open(os.path.join(ROOT, "backlog", "swp.json"), encoding="utf-8"))
review = json.load(open(os.path.join(ROOT, "backlog", "swp_review.json"), encoding="utf-8"))
meta, rows = swp["meta"], {r["id"]: r for r in swp["issues"]}
ep = {t["epic"]: t for t in swp["theo_epic"]}

def vn(x, d=1):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def sign(x):
    return ("+" if x > 0 else "−" if x < 0 else "±") + vn(abs(x))

# ---------------- TOTAL ----------------
total = (f"**Tổng sau khi PL chốt:** {meta['so_issue_la']} issue lá · **{vn(meta['tong_SWP'], 0)} SWP** · **{vn(meta['tong_gio'], 0)} giờ** "
         f"(≈ {vn(meta['tong_gio'] / 8)} MD) · skill chấm ban đầu {vn(meta['tong_SWP_ai'], 0)} SWP / {vn(meta['tong_gio_ai'], 0)} giờ · "
         f"{meta['so_low']} issue confidence = low · {meta['so_lan_tach']} lần tách vì SWP 13 / 21. "
         f"Giờ đã gồm tự test; chưa gồm QA test riêng, PM, BrSE.")

# ---------------- SAMPLE ----------------
mau = {m["id"]: m["ly_do_chon"] for m in swp["mau"]}
n, n_sua = meta["so_mau_da_chot"], meta["so_mau_sua"]
s = [f"Skill chọn **{len(review)} issue mẫu** theo SKILL mục 6 (seed **{meta['seed_mau']}**): (1) mọi issue epic E12 完納奨励金, "
     f"(2) 2 issue SWP cao nhất + 2 thấp nhất trong phần còn lại, (3) mọi issue `confidence = low`, (4) 1 issue ngẫu nhiên mỗi epic còn lại.",
     "",
     f"PL sửa **{n_sua} / {n} = {meta['ty_le_sua'] * 100:.0f}%** issue mẫu. Vì **< 30%** nên theo SKILL mục 6 **giữ nguyên tiêu chí** chấm (mục 2–3 của skill), "
     "**không chấm lại toàn bộ**: chỉ áp điểm chốt cho issue mẫu, issue ngoài mẫu giữ điểm skill. "
     "Hai kiểu lỗi PL chỉ ra (cộng điểm đặc thù chồng nhau; issue làm rõ chấm như issue code) ghi ở [AI_LOG.md](AI_LOG.md) mục 2 để dùng cho AI-report.",
     "",
     "| Issue | Skill chấm (S × C → SWP) | Bạn chốt | Lý do |", "|---|---|---|---|"]
order = {"1": 0, "2": 1, "3": 2, "4": 3}
for o in sorted(review, key=lambda o: (order[mau[o["id"]][0]], o["id"])):
    r = rows[o["id"]]
    cong = (" + " + ", ".join(r["C_cong"])) if r["C_cong"] else ""
    chot = f"**{o['swp_chot']}** ({r['gio']} giờ)" if o["swp_chot"] != o["swp_ai"] else f"{o['swp_chot']} ({r['gio']} giờ)"
    s.append(f"| `{r['id']}` {r['title']} | S{r['S']} × C{r['C']} (C nền {r['C_nen']}{cong}) → {o['swp_ai']} | {chot} | {o['ly_do']} |")
sample = "\n".join(s)

# ---------------- EPIC ----------------
NOTE = {
    "E01": "Hạng mục WBS (CI, môi trường, migration, từ điển); không có trong function MD của LAB-1.",
    "E02": "Ràng buộc: lưu vết chỉ thêm, cùng transaction cho mọi thao tác (P-16 – PREMISE.md dòng 30).",
    "E03": "Ràng buộc đặc thù **営業日 theo chợ** (P-11 – PREMISE.md dòng 25); issue làm rõ 休市日 (low).",
    "E04": "Quy tắc có phiên bản, người soạn ≠ người duyệt; phiên bản v1 bằng migration (P-12 – PREMISE.md dòng 26). Nền của E03 và E12.",
    "E05": "Phân quyền nhiều vai trò; 3 issue low chờ spike E05-09 (GAP-14, GAP-15 – không dùng service_role).",
    "E06": "Ràng buộc đặc thù **許可 / 承認 hai luồng**; 6 issue low vì câu hỏi mở ADR-009.",
    "E07": "Chủ yếu tận dụng prototype LAB-2 (SC-05, SC-06, SC-07 chạy thật).",
    "E08": "Ràng buộc: confirm_trade 1 transaction, L4 khóa lô không tự hủy, G-04 (締め).",
    "E09": "Ràng buộc đặc thù **người tạo ≠ người duyệt** (L7) kiểm theo bản ghi.",
    "E10": "Trigger L5; được giao cho ngày đã 締め (LAB-4 PREMISE P-06).",
    "E11": "Ràng buộc đặc thù **締め** (không mở lại, snapshot); CSV theo mẫu khách chưa có (2 issue low).",
    "E12": "**EPIC RIÊNG 完納奨励金** (tiền + 営業日 + phiên bản quy tắc + khóa kết quả). PL chốt giảm 7 issue mẫu (88 → 66 SWP).",
    "E13": "Offline hẹp (ADR-012); 9 issue low chờ Q8 → +20% dự phòng.",
    "E14": "Hạng mục WBS (hồi quy, test bảo mật, nghiệm thu nội bộ); không có trong function MD của LAB-1.",
}
e = ["| Epic | Số issue (lá) | Tổng SWP | Tổng giờ | Ghi chú |", "|---|---|---|---|---|"]
for t in swp["theo_epic"]:
    e.append(f"| `{t['epic']}` {t['ten']} | {t['so_issue']} | {t['SWP']} | {vn(t['gio'], 0)} | {NOTE[t['epic']]} |")
e.append(f"| **Tổng** | **{meta['so_issue_la']}** | **{meta['tong_SWP']}** | **{vn(meta['tong_gio'], 0)}** | ≈ {vn(meta['tong_gio'] / 8)} MD; chưa gồm QA test riêng, PM, BrSE |")
epic_md = "\n".join(e)

# ---------------- LAB1 ----------------
F = {"F-01": 30, "F-02": 16, "F-03": 6, "F-04": 8, "F-05": 19, "F-06": 18, "F-07": 16, "F-08": 5, "F-09": 10, "F-10": 24, "F-11": 9, "F-12": 19,
     "F-13": 16, "F-14": 10, "F-15": 21, "F-16": 21, "F-17": 14, "F-18": 5, "F-19": 22, "F-20": 14, "F-21": 5, "F-22": 18, "F-23": 16}
assert sum(F.values()) == 342
MAP = [
    (["F-01"], ["E05"], "Gộp 7 → 3 vai trò (LAB-4 `specs/PREMISE.md` dòng 16) và thu gọn SC-21 (dòng 18); tận dụng prototype (requireRole, SC-01, SC-21). MFA chưa thiết kế (task-breakdown 2.8). Phần thêm: has_role + viết lại policy (P-15 – PREMISE.md dòng 29), spike không dùng service_role."),
    (["F-02"], ["E02"], "audit_logs + SC-20 đã chạy thật ở prototype; LAB-5 chỉ thêm chặn quyền / trigger, view che, phân trang. Lưu vết mọi thao tác gom về 1 hàm chung (P-16 – PREMISE.md dòng 30, spec sửa dòng 14)."),
    (["F-05", "F-06"], ["E06"], "SC-02, SC-03 chạy thật ở prototype; SC-04 gộp vào SC-02 (LAB-4 PREMISE dòng 17). Phần tăng: 2 luồng 許可 / 承認 (LAB-4 PREMISE dòng 21; API-11 – PREMISE.md dòng 12, P-13 dòng 27), 6 issue low."),
    (["F-07", "F-08", "F-09"], ["E07"], "SC-05, SC-06, SC-07 chạy thật ở prototype; LAB-5 chỉ chỉnh giao diện tablet + API-14. Phần offline của ロット登録 tính ở E13."),
    (["F-10", "F-11"], ["E08"], "SC-08, SC-09, SC-10 + trigger L4 có sẵn ở prototype; LAB-5 chỉ chuyển kiểm luật vào hàm database 1 transaction và thêm cột (D-19…D-21)."),
    (["F-12"], ["E09"], "SC-11, SC-12 chạy thật; duyệt 1 cấp (LAB-4 PREMISE dòng 56). LAB-5 chỉ thêm hàm 1 transaction + cột reject_reason / decided_by."),
    (["F-13"], ["E10"], "SC-13, SC-14 chạy thật; LAB-5 chỉ thêm trigger L5 + hàm ghi. Offline 引渡し tính ở E13. F-14 xem dòng riêng."),
    (["F-15", "F-18"], ["E11"], "締め + CSV có sẵn (đơn giản) ở prototype; CSV sau 締め, không API kế toán (LAB-4 PREMISE dòng 55). Thêm export_batches, cờ cần xuất lại; CSV theo mẫu khách chưa có (low)."),
    (["F-16"], ["E12"], "Phép tính BigInt có sẵn ở prototype; tách epic riêng theo ràng buộc; thêm hàm record_payment (P-08 – PREMISE.md dòng 22, spec sửa dòng 11), miền 料率 (P-10 – dòng 24). PL chốt giảm 22 SWP (AI_LOG lỗi 1, 2)."),
    (["F-17"], ["E03", "E04"], "**Tăng**: thiết kế mới quy tắc theo chợ có phiên bản (LAB-4 PREMISE dòng 20) + market_id cho 6 bảng + 営業日 theo chợ (P-11 – PREMISE.md dòng 25) + phiên bản v1 bằng migration (P-12 – dòng 26, spec sửa dòng 16). Prototype chỉ có mock (M4), không tận dụng được."),
    (["F-22"], ["E13"], "Prototype không làm offline (M6) nên không tận dụng; phạm vi hẹp 2 thao tác (LAB-4 PREMISE dòng 47) kéo xuống, 9 issue low +20% (Q8) kéo lên → gần bằng."),
]
CHUA = ["F-03", "F-04", "F-14", "F-19", "F-20", "F-21", "F-23"]
l = ["| Phần (chức năng / epic) | LAB-1 (MD × 1,3) | LAB-5 (giờ ÷ 8) | Chênh | Vì sao |", "|---|---|---|---|---|"]
tot1 = tot5 = 0.0
for fs, es, why in MAP:
    m1 = sum(F[f] for f in fs) * 1.3
    m5 = sum(ep[x]["gio"] for x in es) / 8
    tot1 += m1; tot5 += m5
    l.append(f"| {' + '.join(fs)} ↔ {' + '.join(es)} | {vn(m1)} ({' + '.join(str(F[f]) for f in fs)} MD) | {vn(m5)} | {sign(m5 - m1)} | {why} |")
for f in CHUA:
    m1 = F[f] * 1.3; tot1 += m1
    extra = " (F-23: chuyển dữ liệu hệ thống cũ – M9)" if f == "F-23" else ""
    l.append(f"| {f} | {vn(m1)} ({F[f]} MD) | 0 | {sign(-m1)} | Chưa có trong thiết kế LAB-4 → chưa thành issue{extra} – [task-breakdown.md](task-breakdown.md) mục 2.8 \"Phần spec chưa thành issue\". |")
chua1 = sum(F[f] for f in CHUA) * 1.3
l.append(f"| **Cộng phần function** | **{vn(tot1)}** (342 MD) | **{vn(tot5)}** | **{sign(tot5 - tot1)}** | LAB-5 = {tot5 / tot1 * 100:.0f}% LAB-1. Bỏ 7 function chưa có thiết kế: {vn(tot5)} / {vn(tot1 - chua1)} = {tot5 / (tot1 - chua1) * 100:.0f}%. |")
wbs = (ep["E01"]["gio"] + ep["E14"]["gio"]) / 8
l.append(f"| E01 + E14 ↔ hạng mục WBS | — (nằm trong WBS, không có trong function MD) | {vn(wbs)} | — | Nền dự án (CI, môi trường, migration) và kiểm thử hệ thống; LAB-1 tính ở WBS cùng test / PM / BrSE. |")
l.append(f"| **Tổng LAB-5 (dev + tự test)** | — | **{vn(tot5 + wbs)}** | — | = {vn(meta['tong_gio'], 0)} giờ ÷ 8. |")
l += ["",
      f"- Tổng dự án LAB-1 là **1.050,6 MD** (gồm test, PM, BrSE, dự phòng). LAB-5 hiện chỉ có phần dev + tự test (**{vn(tot5 + wbs)} MD**); "
      "QA test riêng, PM, BrSE, dự phòng sẽ cộng ở cấp tổng theo tỷ lệ như LAB-1 (bước sau) – **chưa so được** ở cấp tổng dự án.",
      "- Chênh lớn nhất ở phần đã chạy thật trong prototype LAB-2 (E07, E08, E09, E10, E06): LAB-5 chỉ tính phần **sửa theo thiết kế LAB-4**, không tính lại phần đã có (nhãn `reuse-prototype`, 35 mục).",
      "- Phần **tăng** so với LAB-1 (E03 + E04) đến từ thay đổi thiết kế ở LAB-4 (quy tắc theo chợ có phiên bản) và giả định LAB-5 (PREMISE.md mục 1–2).",
      "- Rủi ro: quy ước 1 SWP ≈ 2 giờ chưa được hiệu chỉnh bằng số liệu thật của đội; nếu sprint đầu cho thấy lệch, sửa bảng quy đổi (SKILL mục 5) cho mọi issue, không sửa từng issue.",
      "- 7 function chưa có thiết kế (≈ " + vn(sum(F[f] for f in CHUA) * 1.3) + " MD theo LAB-1) chưa nằm trong LAB-5; khi có spec phải chia task và chấm thêm."]
lab1 = "\n".join(l)

p = os.path.join(ROOT, "estimate.md")
txt = open(p, encoding="utf-8").read()
for k, v in {"TOTAL": total, "SAMPLE": "\n" + sample + "\n", "EPIC": "\n" + epic_md + "\n", "LAB1": "\n" + lab1 + "\n"}.items():
    pat = re.compile(r"(<!-- BEGIN:%s -->).*?(<!-- END:%s -->)" % (k, k), re.S)
    assert pat.search(txt), k
    txt = pat.sub(lambda m: m.group(1) + v + m.group(2), txt)
open(p, "w", encoding="utf-8", newline="\n").write(txt)
print(f"function: LAB-1 {tot1:.1f} MD | LAB-5 {tot5:.1f} MD | WBS {wbs:.2f} | tổng LAB-5 {tot5 + wbs:.2f}")
