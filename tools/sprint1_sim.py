# -*- coding: utf-8 -*-
"""Giả lập Sprint 1 (LAB-5) – số liệu GIẢ LẬP, không phải tiến độ thật.

Chạy từ gốc repo:
    python -I -X utf8 tools/sprint1_sim.py plan            # kiểm năng lực / phụ thuộc, ghi backlog/sprint1_sim.json
    python -I -X utf8 tools/sprint1_sim.py apply           # cập nhật Project + issue trên GitHub (chạy lại an toàn)
    .venv/Scripts/python -X utf8 tools/sprint1_sim.py chart  # vẽ reports/burndown-sprint1.png (cần matplotlib)
Dữ liệu giả lập viết tay ở đây (nguồn duy nhất); sprint1_sim.json là bản xuất để tạo lại.
"""
import datetime, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
OUT = os.path.join(ROOT, "backlog", "sprint1_sim.json")

START = datetime.date(2026, 11, 23)
END = datetime.date(2026, 12, 6)
DAYS = [START + datetime.timedelta(d) for d in range(14) if (START + datetime.timedelta(d)).weekday() < 5]  # 10 ngày làm việc
CAP_PER_DAY = {"BE-1": 6, "BE-2": 6, "FE-1": 6, "QA-1": 4, "BrSE": 2, "PL": 2}
TARGET = 0.85

# Người phụ trách được PL điều chỉnh cho Sprint 1 để cân tải (vai giả định)
REASSIGN = {
    "E01-04": "BE-1", "E01-07": "BE-1",
    "E03-02-DB1": "BE-2", "E03-02-DB2": "BE-2", "E03-02-API": "BE-2", "E05-01-DB": "BE-2",
    "E03-05": "PL",
}
REASSIGN_WHY = "PL cân tải Sprint 1: BE-2 nhận phần chuyển dữ liệu market_id và bảng phân quyền; PL nhận câu hỏi lịch 休市日 vì BrSE đã đủ tải."

# Kế hoạch Sprint 1 theo thứ tự ưu tiên (làm rõ gửi khách sớm → nền tảng → lưu vết → chợ → quy tắc → phân quyền → spike offline)
PLAN = [
    "E12-09", "E06-09", "E11-05", "E13-06", "E03-05",
    "E01-01", "E01-02", "E01-03", "E01-04", "E01-07", "E01-05",
    "E02-01",
    "E03-01", "E03-02-DB1", "E03-02-DB2", "E03-02-API", "E03-02-T",
    "E04-01-DB1",
    "E05-01-DB", "E05-01-T",
    "E14-01",
    "E13-01-UI1", "E13-01-UI2",
]
DEFERRED = {
    "E02-04": "Thời hạn lưu audit_logs không chặn go-live; PL và BrSE đã đủ tải → Sprint 2.",
    "E04-01-DB2": "BE-1 đủ tải; phiên bản v1 làm đầu Sprint 2 → kéo theo E03-03 (営業日 theo chợ).",
    "E03-03": "Phụ thuộc phiên bản quy tắc v1 (E04-01-DB2) → Sprint 2.",
}

# Kết quả giả lập cuối Sprint 1: (trạng thái, ngày xong (1..10) nếu Done, ghi chú)
RESULT = {
    "E01-01": ("Done", 2, "CI chạy lint + unit + E2E trên PR."),
    "E01-02": ("Done", 2, "Quy trình migration đánh số, có câu kiểm cấu trúc."),
    "E01-05": ("Done", 2, "Thêm từ mới vào ja.ts."),
    "E01-03": ("Done", 3, "3 môi trường vùng Tokyo."),
    "E01-07": ("Done", 3, "Đã dọn dữ liệu test trong day_closes / payments."),
    "E03-01": ("Done", 3, "Bảng markets + chợ mặc định."),
    "E01-04": ("Done", 4, "Logger + định dạng lỗi dùng chung."),
    "E02-01": ("Done", 4, "Thu hồi quyền + trigger chặn sửa / xóa lưu vết."),
    "E03-02-DB1": ("Done", 5, "market_id cho participants, lots, trades."),
    "E13-01-UI1": ("Done", 5, "Spike xong; phát hiện giới hạn Safari trên iPad (xem rủi ro)."),
    "E06-09": ("Done", 6, "Khách trả lời: chưa cần thu hồi giấy ở go-live; 承認 ghi giống 許可."),
    "E05-01-DB": ("Done", 7, "user_roles + trigger guard."),
    "E04-01-DB1": ("Done", 8, "Bảng quy tắc + ràng buộc."),
    "E03-02-DB2": ("Done", 9, "Xong muộn 4 ngày do phát sinh việc dọn dữ liệu (sự kiện 1)."),
    "E05-01-T": ("Done", 9, "Test trigger phân quyền."),
    "E14-01": ("Done", 10, "Bộ hồi quy chạy trên CI; dữ liệu mẫu theo chợ sẽ cập nhật cùng E03-02."),
    "E13-01-UI2": ("Done", 10, "Hàng đợi IndexedDB + gửi lại chạy trên Chrome; Safari cần cách khác."),
    "E03-05": ("In Review", None, "Khách trả lời ngày 8; PL đang ghi quyết định vào PREMISE.md."),
    "E03-02-API": ("In Progress", None, "Bắt đầu trễ vì E03-02-DB2 kéo dài; còn khoảng 40%."),
    "E03-02-T": ("Todo", None, "Chưa bắt đầu (chờ E03-02-API)."),
    "E12-09": ("Blocked", None, "Đã gửi câu hỏi nguồn 請求 ngày 2026-11-24, khách chưa trả lời."),
    "E11-05": ("Blocked", None, "Đã xin mẫu CSV kế toán ngày 2026-11-24, khách chưa gửi."),
    "E13-06": ("Blocked", None, "Đã hỏi thời gian offline tối đa / tablet dùng chung (Q8) ngày 2026-11-24, chưa có trả lời."),
}
EVENTS = [
    {"ngay": 5, "issue": "E03-02-DB2", "loai": "Phát sinh việc",
     "mo_ta": "Khi chuyển dữ liệu market_id, phát hiện dòng lưu vết đăng nhập cũ không xác định được chợ và dòng test còn sót "
              "ngoài phạm vi E01-07 → phải viết thêm bước dọn và điều kiện null cho lưu vết đăng nhập (PREMISE.md P-14).",
     "anh_huong": "Thực tế khoảng 18 giờ thay vì 10 giờ; E03-02-API bắt đầu trễ 3 ngày, chuyển sang Sprint 2."},
    {"ngay": 2, "issue": "E12-09, E11-05, E13-06, E06-09, E03-05", "loai": "Khách trả lời chậm",
     "mo_ta": "Gửi 5 câu hỏi cho khách ngày 2026-11-24. Đến cuối sprint khách trả lời 2/5 (E06-09 ngày 6, E03-05 ngày 8).",
     "anh_huong": "3 issue làm rõ ở trạng thái Blocked; các issue phụ thuộc (E12-*, E11-06, E13-03…) chưa thể lên kế hoạch chắc chắn."},
]
CARRY = ["E03-05", "E03-02-API", "E03-02-T", "E12-09", "E11-05", "E13-06"]  # chuyển sang Sprint 2


def load():
    import github_sync as g
    return g


def plan():
    g = load()
    leaf, by_id = g.leaf, g.by_id
    role = {i: REASSIGN.get(i, g.role_of(i)) for i in PLAN}
    cap = {r: c * len(DAYS) for r, c in CAP_PER_DAY.items()}
    tot_cap = sum(cap.values())
    used = {r: 0 for r in cap}
    for i in PLAN:
        assert i in leaf, i
        used[role[i]] += leaf[i]["gio"]
    # phụ thuộc: mọi issue lá của phụ thuộc (kể cả phụ thuộc của issue cha) phải nằm trước trong kế hoạch hoặc là issue làm rõ
    def leaves_of(x):
        kids = [y["id"] for y in g.backlog if y["parent"] == x]
        return [x] if not kids else [l for k in kids for l in leaves_of(k)]
    def deps_of(i):
        x = by_id[i]
        d = list(x["depends_on"])
        if x["type"] == "sub-issue":
            d += by_id[x["parent"]]["depends_on"]
        return [l for dd in d for l in leaves_of(dd)]
    for k, i in enumerate(PLAN):
        miss = [d for d in deps_of(i) if d not in PLAN[:k]]
        assert not miss, (i, miss)
    plan_h = sum(used.values())
    assert plan_h <= TARGET * tot_cap, (plan_h, tot_cap)
    for r in cap:
        assert used[r] <= cap[r], (r, used[r], cap[r])
    assert set(RESULT) == set(PLAN)
    swp_plan = sum(leaf[i]["SWP"] for i in PLAN)
    done = [i for i in PLAN if RESULT[i][0] == "Done"]
    swp_done = sum(leaf[i]["SWP"] for i in done)
    # burndown
    actual = [swp_plan]
    for d in range(1, len(DAYS) + 1):
        actual.append(swp_plan - sum(leaf[i]["SWP"] for i in done if RESULT[i][1] <= d))
    ideal = [round(swp_plan - swp_plan * d / len(DAYS), 1) for d in range(len(DAYS) + 1)]
    m = g.load_map()
    items = []
    for i in PLAN:
        st, day, note = RESULT[i]
        items.append(dict(id=i, so=m[i]["number"], epic=by_id[i]["epic"], title=by_id[i]["title"], vai=role[i],
                          vai_cu=g.role_of(i) if i in REASSIGN else None, SWP=leaf[i]["SWP"], gio=leaf[i]["gio"],
                          trang_thai=st, ngay_xong=(DAYS[day - 1].isoformat() if day else None), ghi_chu=note,
                          sprint_cuoi=("Sprint 2" if i in CARRY else "Sprint 1")))
    by_status = {}
    for it in items:
        s = by_status.setdefault(it["trang_thai"], {"so_issue": 0, "SWP": 0, "gio": 0})
        s["so_issue"] += 1; s["SWP"] += it["SWP"]; s["gio"] += it["gio"]
    data = dict(
        ghi_chu="SỐ LIỆU GIẢ LẬP phục vụ LAB-5 – không phải tiến độ thật.",
        iteration="Sprint 1", bat_dau=START.isoformat(), ket_thuc=END.isoformat(), ngay_lam_viec=[d.isoformat() for d in DAYS],
        nang_luc=dict(gio_moi_ngay=CAP_PER_DAY, gio_sprint=cap, tong=tot_cap, muc_tieu=TARGET, gio_ke_hoach=plan_h,
                      ty_le=round(plan_h / tot_cap, 3), theo_vai={r: dict(ke_hoach=used[r], nang_luc=cap[r]) for r in cap}),
        dieu_chinh_nguoi_phu_trach=dict(ly_do=REASSIGN_WHY, issue=REASSIGN), hoan_sang_sprint2=DEFERRED,
        ke_hoach=dict(so_issue=len(PLAN), SWP=swp_plan), ket_qua=dict(SWP_done=swp_done, ty_le_done=round(swp_done / swp_plan, 3),
                                                                    velocity=swp_done, theo_trang_thai=by_status),
        su_kien=EVENTS, chuyen_sprint2=CARRY, burndown=dict(ngay=["Bắt đầu"] + [d.strftime("%d/%m") for d in DAYS], ly_tuong=ideal, thuc_te=actual),
        issues=items)
    json.dump(data, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(f"Năng lực {tot_cap} giờ, kế hoạch {plan_h} giờ ({plan_h / tot_cap:.0%}); {len(PLAN)} issue, {swp_plan} SWP; Done {swp_done} SWP ({swp_done / swp_plan:.0%})")
    print({r: f"{used[r]}/{cap[r]}" for r in cap}, by_status)


def apply():
    g = load()
    g.check_account()
    d = json.load(open(OUT, encoding="utf-8"))
    m = g.load_map()
    pid = m["_project"]["id"]
    fields = {f["name"]: f for f in g.gql("query($p:ID!){node(id:$p){...on ProjectV2{fields(first:50){nodes{...on ProjectV2FieldCommon{id name}...on ProjectV2SingleSelectField{options{id name}}...on ProjectV2IterationField{configuration{iterations{id title}}}}}}}}", p=pid)["node"]["fields"]["nodes"] if f}
    opt = lambda f, n: next(o["id"] for o in fields[f]["options"] if o["name"] == n)
    it_id = {x["title"]: x["id"] for x in fields["Sprint"]["configuration"]["iterations"]}
    have = {l["name"] for l in g.gh(["api", f"repos/{g.REPO}/labels?per_page=100"])}
    if "gia-lap" not in have:
        g.gh(["api", "-X", "POST", f"repos/{g.REPO}/labels", "--input", "-"], {"name": "gia-lap", "color": "d4c5f9", "description": "Trạng thái giả lập (LAB-5) – không phải tiến độ thật"})
    for it in d["issues"]:
        i, n = it["id"], it["so"]
        item = m[i]["item_id"]
        upd = lambda a, f, v: "%s:updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$it,fieldId:%s,value:{%s}}){clientMutationId}" % (a, json.dumps(fields[f]["id"]), v)
        parts = [upd("a", "Status", "singleSelectOptionId:%s" % json.dumps(opt("Status", it["trang_thai"]))),
                 upd("b", "Sprint", "iterationId:%s" % json.dumps(it_id[it["sprint_cuoi"]])),
                 upd("c", "Người phụ trách (giả định)", "singleSelectOptionId:%s" % json.dumps(opt("Người phụ trách (giả định)", it["vai"])))]
        g.gql("mutation($p:ID!,$it:ID!){" + "".join(parts) + "}", p=pid, it=item)
        iss = g.gh(["api", f"repos/{g.REPO}/issues/{n}"])
        labels = [l["name"] for l in iss["labels"]]
        add = ["gia-lap"] + (["blocked"] if it["trang_thai"] == "Blocked" else [])
        if any(a not in labels for a in add):
            g.gh(["api", "-X", "POST", f"repos/{g.REPO}/issues/{n}/labels", "--input", "-"], {"labels": add})
        if it["vai_cu"]:
            body = iss["body"]
            new = body.replace(f"Người phụ trách (giả định): **{it['vai_cu']}**", f"Người phụ trách (giả định): **{it['vai']}** (Sprint 1: đổi từ {it['vai_cu']} để cân tải)")
            if new != body and f"đổi từ {it['vai_cu']}" not in body:
                g.gh(["api", "-X", "PATCH", f"repos/{g.REPO}/issues/{n}", "--input", "-"], {"body": new})
        comments = [c["body"] for c in g.gh(["api", f"repos/{g.REPO}/issues/{n}/comments?per_page=100"])]
        if it["trang_thai"] == "Done":
            if iss["state"] == "open":
                if not any(c.startswith("Done (giả lập Sprint 1)") for c in comments):
                    g.gh(["api", "-X", "POST", f"repos/{g.REPO}/issues/{n}/comments", "--input", "-"],
                         {"body": f"Done (giả lập Sprint 1) – {it['ngay_xong']}. {it['ghi_chu']}"})
                g.gh(["api", "-X", "PATCH", f"repos/{g.REPO}/issues/{n}", "--input", "-"], {"state": "closed", "state_reason": "completed"})
        else:
            msg = f"{it['trang_thai']} (giả lập Sprint 1) – {it['ghi_chu']}" + (" Chuyển sang Sprint 2." if it["sprint_cuoi"] == "Sprint 2" else "")
            if not any(c.startswith(f"{it['trang_thai']} (giả lập Sprint 1)") for c in comments):
                g.gh(["api", "-X", "POST", f"repos/{g.REPO}/issues/{n}/comments", "--input", "-"], {"body": msg})
        print(f"#{n} {i}: {it['trang_thai']} · {it['sprint_cuoi']} · {it['vai']}", flush=True)
        time.sleep(1.2)


def chart():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["Segoe UI", "Noto Sans JP", "Yu Gothic"]
    d = json.load(open(OUT, encoding="utf-8"))
    b = d["burndown"]
    x = list(range(len(b["ngay"])))
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    ax.plot(x, b["ly_tuong"], color="#9aa0a6", linestyle="--", linewidth=2, label="Kế hoạch lý tưởng")
    ax.plot(x, b["thuc_te"], color="#2f5d8a", marker="o", linewidth=2.4, label="Thực tế (giả lập)")
    for xi, v in zip(x, b["thuc_te"]):
        ax.annotate(str(v), (xi, v), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8, color="#2f5d8a")
    ev = d["su_kien"][0]
    ax.axvspan(ev["ngay"], 9, color="#e9a23b", alpha=0.12)
    ax.text(ev["ngay"] + 0.1, max(b["thuc_te"]) * 0.97, "Phát sinh việc khi chuyển dữ liệu\nsang mô hình nhiều chợ (ngày 5–9)", fontsize=8, color="#8a5a12", va="top")
    ax.set_xticks(x, b["ngay"], fontsize=8)
    ax.set_xlabel("Ngày làm việc")
    ax.set_ylabel("Khối lượng còn lại (SWP)")
    ax.set_ylim(0, max(b["thuc_te"]) * 1.12)
    ax.set_title(f"Sprint 1 ({d['bat_dau']} → {d['ket_thuc']}) – SWP còn lại theo ngày · số liệu giả lập", fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower left")
    fig.tight_layout()
    out = os.path.join(ROOT, "reports", "burndown-sprint1.png")
    fig.savefig(out)
    print("ảnh:", out)


if __name__ == "__main__":
    for st in sys.argv[1:] or ["plan"]:
        {"plan": plan, "apply": apply, "chart": chart}[st]()
