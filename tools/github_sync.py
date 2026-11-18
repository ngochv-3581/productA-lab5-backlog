# -*- coding: utf-8 -*-
"""Đưa backlog lên GitHub (repo + Project v2 PRIVATE) – chạy lại được, không tạo trùng.

Chạy từ gốc repo:
    python -I -X utf8 tools/github_sync.py labels issues subissues     # cần quyền repo
    python -I -X utf8 tools/github_sync.py project items verify        # cần thêm quyền project
Chỉ issue lá mang SWP / Giờ trên Project (epic, issue cha = tổng con, ghi trong nội dung) → tổng Project = tổng estimate.
Bảng đối chiếu mã ↔ issue: backlog/github_map.json (ghi sau mỗi lần tạo).
Quy tắc: chỉ dùng tài khoản ngochv-3581 (kiểm trước mọi lệnh tạo); không gán tài khoản GitHub nào;
không chép câu chữ tài liệu khách – nội dung issue chỉ gồm mã spec và câu tự viết.
"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER, REPO_NAME = "ngochv-3581", "productA-lab5-backlog"
REPO = f"{OWNER}/{REPO_NAME}"
PROJECT_TITLE = "Product A – LAB-5 Backlog"
MAP_PATH = os.path.join(ROOT, "backlog", "github_map.json")
PAUSE = 1.5

backlog = json.load(open(os.path.join(ROOT, "backlog", "backlog.json"), encoding="utf-8"))
swp = json.load(open(os.path.join(ROOT, "backlog", "swp.json"), encoding="utf-8"))
by_id = {x["id"]: x for x in backlog}
leaf = {r["id"]: r for r in swp["issues"]}
cha = {c["id"]: c for c in swp["issue_cha"]}
epic_tot = {t["epic"]: t for t in swp["theo_epic"]}
children = {}
for x in backlog:
    if x["parent"]:
        children.setdefault(x["parent"], []).append(x["id"])


def gh(args, data=None, retries=6):
    for i in range(retries):
        p = subprocess.run(["gh"] + args, input=json.dumps(data) if data is not None else None,
                           capture_output=True, text=True, encoding="utf-8")
        if p.returncode == 0:
            return json.loads(p.stdout) if p.stdout.strip() else None
        err = p.stderr + p.stdout
        if "rate limit" in err.lower() or "abuse" in err.lower() or "502" in err or "504" in err:
            wait = 60 * (i + 1)
            print(f"  … giới hạn / lỗi tạm thời, chờ {wait}s", flush=True)
            time.sleep(wait)
            continue
        raise RuntimeError(f"gh {' '.join(args[:3])} lỗi: {err.strip()[:400]}")
    raise RuntimeError("hết số lần thử")


def check_account():
    login = subprocess.run(["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True).stdout.strip()
    if login != OWNER:
        sys.exit(f"DỪNG: tài khoản gh hiện tại là '{login}', không phải {OWNER}.")


def load_map():
    return json.load(open(MAP_PATH, encoding="utf-8")) if os.path.exists(MAP_PATH) else {}


def save_map(m):
    ordered = {k: m[k] for k in [x["id"] for x in backlog] if k in m}
    for k in m:
        if k.startswith("_"):
            ordered[k] = m[k]
    with open(MAP_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=1)


# ---------------- nhãn ----------------
RB = {  # ràng buộc đặc thù (task-breakdown mục 3) – áp cho issue và sub-issue của nó
    "rang-buoc:kanno-shoreikin": ["E12"],
    "rang-buoc:eigyobi": ["E03", "E03-03", "E03-05", "E04-01", "E13-03", "E12-03"],
    "rang-buoc:kyoka-shonin": ["E06", "E06-01", "E06-02", "E06-03", "E06-04", "E06-05", "E06-09", "E01-06"],
    "rang-buoc:shime": ["E11", "E11-01", "E08-02", "E08-03", "E10-02", "E11-04"],
    "rang-buoc:tao-khac-duyet": ["E09", "E09-02", "E04-03", "E05-01", "E14-02"],
    "rang-buoc:khoa-lo-l4": ["E08-02", "E09-02"],
    "rang-buoc:luu-vet": ["E02-01", "E02-02"],
    "rang-buoc:admin-khong-xem": ["E05-02", "E02-03", "E14-03"],
}
LABELS = {
    "epic": ("5319e7", "Epic – tập hợp issue"),
    "db": ("0e8a16", "Lớp database: migration / hàm / trigger / RLS"),
    "api": ("1d76db", "Lớp API"),
    "ui": ("fbca04", "Lớp giao diện"),
    "test": ("c2e0c6", "Test tự động"),
    "clarify": ("d93f0b", "Làm rõ – kết quả là quyết định được PL chốt"),
    "spike": ("f9d0c4", "Spike kỹ thuật có thời hạn"),
    "reuse-prototype": ("bfdadc", "Tận dụng prototype LAB-2"),
    "migration": ("006b75", "Có chuyển dữ liệu"),
    "tablet": ("c5def5", "Giao diện tablet / offline"),
    "security": ("b60205", "Bảo mật / phân quyền"),
    "infra": ("ededed", "Hạ tầng / CI"),
    "blocked": ("000000", "Chờ dữ liệu / trả lời từ khách"),
    "confidence:low": ("e99695", "SWP có +20% dự phòng vì câu hỏi mở"),
}
for k in RB:
    LABELS[k] = ("fef2c0", "Ràng buộc đặc thù – task-breakdown mục 3")
KEEP = {"db", "api", "ui", "test", "spike", "reuse-prototype", "migration", "tablet", "security", "infra", "blocked"}


def rb_of(i):
    """Nhãn ràng buộc: mã nằm trong danh sách, hoặc là sub-issue của issue trong danh sách;
    riêng 完納奨励金 áp cho toàn epic E12."""
    x, out = by_id[i], []
    for lab, ids in RB.items():
        if i in ids or (x["type"] == "sub-issue" and x["parent"] in ids) or (lab == "rang-buoc:kanno-shoreikin" and x["epic"] in ids):
            out.append(lab)
    return out


def labels_of(i):
    x = by_id[i]
    out = ["epic"] if x["type"] == "epic" else []
    out += [l for l in x["labels"] if l in KEEP]
    if "clarification" in x["labels"]:
        out.append("clarify")
    out += rb_of(i)
    if i in leaf and leaf[i]["confidence"] == "low":
        out.append("confidence:low")
    return sorted(set(out), key=out.index)


# ---------------- người phụ trách (vai giả định) ----------------
BRSE = {"E01-06", "E03-05", "E06-09", "E11-05", "E13-06", "E04-04", "E13-05-UI1"}
PL = {"E12-09", "E12-10", "E02-04"}
BE1_EPICS = {"E01", "E02", "E03", "E04", "E05", "E12", "E13"}


def role_of(i):
    x = by_id[i]
    if x["type"] == "epic":
        return "PL"
    if i in children:
        roles = [role_of(c) for c in children[i]]
        return max(roles, key=lambda r: (roles.count(r), -roles.index(r)))
    if i in BRSE:
        return "BrSE"
    if i in PL:
        return "PL"
    L = set(x["labels"])
    if "test" in L and not L & {"db", "api", "ui"}:
        return "QA-1"
    if "db" not in L and ("ui" in L or ("spike" in L and x["epic"] == "E13")):
        return "FE-1"
    if i in {"E01-04", "E01-07"}:
        return "BE-2"
    return "BE-1" if x["epic"] in BE1_EPICS else "BE-2"


# ---------------- số liệu SWP ----------------
def swp_hours(i):
    x = by_id[i]
    if x["type"] == "epic":
        return epic_tot[i]["SWP"], epic_tot[i]["gio"]
    if i in cha:
        return cha[i]["SWP"], cha[i]["gio"]
    return leaf[i]["SWP"], leaf[i]["gio"]


DOD_COMMON = ["Đạt Definition of Done chung ở task-breakdown.md mục 1.3", "PR được người khác review, CI xanh"]
DOD = {
    "db": "Migration SQL nằm trong repo app; người dùng tự chạy (dev → staging); chạy lại SQL kiểm cấu trúc; test T-xx liên quan xanh",
    "api": "Kiểm quyền 2 lớp (API + RLS); lỗi trả {error, code} với câu M_xx từ ja.ts; thao tác ghi có lưu vết cùng transaction",
    "ui": "Đúng screen spec / wireframe; chữ theo GLOSSARY / ja.ts; áp CS-16, CS-17, CS-18",
    "test": "Test tự động chạy trên CI; tên test ghi mã luật (L-xx / G-xx / CS-xx / T-xx)",
    "clarify": "Câu hỏi / phương án đã gửi; quyết định được PL chốt và ghi vào PREMISE.md; bỏ nhãn blocked ở issue phụ thuộc",
    "spike": "Có kết luận + demo nhỏ; PL duyệt phương án trước khi làm issue phụ thuộc",
}


def body_of(i, m):
    x = by_id[i]
    s, g = swp_hours(i)
    ref = lambda c: (f"#{m[c]['number']} `{c}`" if c in m else f"`{c}`")
    L = [f"**Mã:** `{i}` · **Loại:** {x['type']} · **Epic:** {ref(x['epic']) if x['type'] != 'epic' else '—'}"
         + (f" · **Cha:** {ref(x['parent'])}" if x["type"] == "sub-issue" else ""), "",
         "### Mục tiêu", x["title"] + (f". {x['note']}" if x["note"] else ""), "",
         "### Spec tham chiếu (mã)", ", ".join(f"`{c}`" for c in x["spec_refs"]) or "—", ""]
    L += ["### Definition of Done"]
    if x["type"] == "epic" or i in children:
        L += ["- [ ] Mọi sub-issue đã đóng", "- [ ] Tổng giờ thực tế được ghi để so với ước lượng"]
    else:
        lab = labels_of(i)
        L += [f"- [ ] {DOD[k]}" for k in ["db", "api", "ui", "test", "clarify", "spike"] if k in lab]
        L += [f"- [ ] {d}" for d in DOD_COMMON]
    L += ["", "### Ước lượng"]
    if i in leaf:
        r = leaf[i]
        cong = (" + " + ", ".join(r["C_cong"])) if r["C_cong"] else ""
        line = f"- SWP: S{r['S']} × C{r['C']} (C nền {r['C_nen']}{cong}) → {r['swp_ai']}"
        if r["swp_chot"] is not None and r["swp_chot"] != r["swp_ai"]:
            line += f" · **PL chốt {r['swp_chot']}**: {r['ly_do_chot']}"
        elif r["swp_chot"] is not None:
            line += " · PL đồng ý"
        L += [line, f"  - Lý do S: {r['S_ly_do']}", f"  - Lý do C: {r['C_ly_do']}",
              f"- Giờ: **{g}** (confidence {r['confidence']}{', +20%' if r['confidence'] == 'low' else ''})"]
    else:
        L += [f"- SWP: **{s}** = tổng các sub-issue (không chấm riêng)", f"- Giờ: **{g}**"]
    L += [f"- Người phụ trách (giả định): **{role_of(i)}**", "", "### Phụ thuộc"]
    L += [f"- {ref(d)} {by_id[d]['title']}" for d in x["depends_on"]] or ["- Không"]
    L += ["", "<sub>Sinh từ backlog/backlog.json + backlog/swp.json bằng tools/github_sync.py.</sub>"]
    return "\n".join(L)


def creation_order():
    done, order = set(), []
    def visit(i):
        if i in done:
            return
        done.add(i)
        x = by_id[i]
        for d in ([x["parent"]] if x["parent"] else []) + ([x["epic"]] if x["type"] != "epic" else []) + x["depends_on"]:
            visit(d)
        order.append(i)
    for x in backlog:
        visit(x["id"])
    return order


# ---------------- các bước ----------------
def do_labels():
    have = {l["name"] for l in gh(["api", f"repos/{REPO}/labels?per_page=100"])}
    for name, (color, desc) in LABELS.items():
        if name not in have:
            gh(["api", "-X", "POST", f"repos/{REPO}/labels", "--input", "-"], {"name": name, "color": color, "description": desc})
            print("nhãn +", name, flush=True)
            time.sleep(0.5)


def do_issues():
    m = load_map()
    for i in creation_order():
        if i in m:
            continue
        x = by_id[i]
        r = gh(["api", "-X", "POST", f"repos/{REPO}/issues", "--input", "-"],
               {"title": f"[{i}] {x['title']}", "body": body_of(i, m), "labels": labels_of(i)})
        m[i] = {"number": r["number"], "id": r["id"], "node_id": r["node_id"], "url": r["html_url"]}
        save_map(m)
        print(f"#{r['number']:<4} {i}", flush=True)
        time.sleep(PAUSE)


def do_subissues():
    m = load_map()
    for pid, kids in children.items():
        existing = {s["number"] for s in gh(["api", f"repos/{REPO}/issues/{m[pid]['number']}/sub_issues?per_page=100"])}
        for k in kids:
            if m[k]["number"] in existing:
                continue
            gh(["api", "-X", "POST", f"repos/{REPO}/issues/{m[pid]['number']}/sub_issues", "--input", "-"], {"sub_issue_id": m[k]["id"]})
            print(f"  {pid} ← {k}", flush=True)
            time.sleep(PAUSE)


def gql(query, **v):
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, val in v.items():
        args += ["-F" if isinstance(val, (int, float)) and not isinstance(val, bool) else "-f", f"{k}={val}"]
    return gh(args)["data"]


STATUS = ["Todo", "In Progress", "In Review", "Done", "Blocked"]
ROLES = ["PL", "BrSE", "BE-1", "BE-2", "FE-1", "QA-1"]


def do_project():
    m = load_map()
    meta = m.setdefault("_project", {})
    if "id" not in meta:
        uid = gql("query{viewer{id}}")["viewer"]["id"]
        p = gql("mutation($o:ID!,$t:String!){createProjectV2(input:{ownerId:$o,title:$t}){projectV2{id number url}}}", o=uid, t=PROJECT_TITLE)["createProjectV2"]["projectV2"]
        meta.update(id=p["id"], number=p["number"], url=p["url"]); save_map(m)
        print("project +", p["url"], flush=True)
    pid = meta["id"]
    repo_id = gql("query($o:String!,$n:String!){repository(owner:$o,name:$n){id}}", o=OWNER, n=REPO_NAME)["repository"]["id"]
    linked = gql("query($p:ID!){node(id:$p){...on ProjectV2{public repositories(first:10){nodes{id}}}}}", p=pid)["node"]
    if repo_id not in [r["id"] for r in linked["repositories"]["nodes"]]:
        gql("mutation($p:ID!,$r:ID!){linkProjectV2ToRepository(input:{projectId:$p,repositoryId:$r}){repository{id}}}", p=pid, r=repo_id)
    if linked["public"]:
        gql("mutation($p:ID!){updateProjectV2(input:{projectId:$p,public:false}){projectV2{public}}}", p=pid)
    fields = {f["name"]: f for f in gql("query($p:ID!){node(id:$p){...on ProjectV2{fields(first:50){nodes{...on ProjectV2FieldCommon{id name dataType}...on ProjectV2SingleSelectField{options{id name}}}}}}}", p=pid)["node"]["fields"]["nodes"] if f}

    def opts_arg(names):
        return "[" + ",".join('{name:%s,color:GRAY,description:""}' % json.dumps(n, ensure_ascii=False) for n in names) + "]"

    st = fields["Status"]
    if [o["name"] for o in st["options"]] != STATUS:
        keep = {o["name"]: o["id"] for o in st["options"]}
        opts = ",".join(("{id:%s,name:%s,color:GRAY,description:\"\"}" % (json.dumps(keep[n]), json.dumps(n))) if n in keep else
                        ("{name:%s,color:GRAY,description:\"\"}" % json.dumps(n)) for n in STATUS)
        gql("mutation($f:ID!){updateProjectV2Field(input:{fieldId:$f,singleSelectOptions:[%s]}){projectV2Field{...on ProjectV2SingleSelectField{id}}}}" % opts, f=st["id"])
        print("Status: đặt 5 lựa chọn", flush=True)
    for name, kind, names in [("SWP", "NUMBER", None), ("Giờ ước lượng", "NUMBER", None),
                              ("Người phụ trách (giả định)", "SINGLE_SELECT", ROLES),
                              ("Epic", "SINGLE_SELECT", [x["id"] for x in backlog if x["type"] == "epic"])]:
        if name in fields:
            continue
        extra = f",singleSelectOptions:{opts_arg(names)}" if names else ""
        gql("mutation($p:ID!,$n:String!){createProjectV2Field(input:{projectId:$p,dataType:%s,name:$n%s}){projectV2Field{...on ProjectV2FieldCommon{id}}}}" % (kind, extra), p=pid, n=name)
        print("trường +", name, flush=True)
    if "Sprint" not in fields:
        try:
            gql("mutation($p:ID!){createProjectV2Field(input:{projectId:$p,dataType:ITERATION,name:\"Sprint\",iterationConfiguration:{startDate:\"2026-11-23\",duration:14,iterations:[{title:\"Sprint 1\",startDate:\"2026-11-23\",duration:14},{title:\"Sprint 2\",startDate:\"2026-12-07\",duration:14},{title:\"Sprint 3\",startDate:\"2026-12-21\",duration:14}]}}){projectV2Field{...on ProjectV2FieldCommon{id}}}}", p=pid)
            print("trường + Sprint (iteration)", flush=True)
        except RuntimeError as e:
            meta["sprint_loi"] = str(e)[:300]
            print("KHÔNG tạo được trường Sprint qua API → làm tay:", str(e)[:200], flush=True)
    save_map(m)


def do_items():
    m = load_map()
    pid = m["_project"]["id"]
    fields = {f["name"]: f for f in gql("query($p:ID!){node(id:$p){...on ProjectV2{fields(first:50){nodes{...on ProjectV2FieldCommon{id name dataType}...on ProjectV2SingleSelectField{options{id name}}}}}}}", p=pid)["node"]["fields"]["nodes"] if f}
    opt = lambda f, n: next(o["id"] for o in fields[f]["options"] if o["name"] == n)
    for x in backlog:
        i = x["id"]
        e = m[i]
        if not e.get("item_id"):
            e["item_id"] = gql("mutation($p:ID!,$c:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id}}}", p=pid, c=e["node_id"])["addProjectV2ItemById"]["item"]["id"]
            save_map(m)
        # Chỉ issue LÁ mang SWP / Giờ để tổng trên Project = tổng estimate (cha / epic = tổng con, ghi trong nội dung issue)
        s, g = (leaf[i]["SWP"], leaf[i]["gio"]) if i in leaf else (None, None)
        want = (s, g, role_of(i), x["epic"])
        if e.get("fields_set") == list(want):
            continue
        upd = lambda a, f, v: "%s:updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$it,fieldId:%s,value:{%s}}){clientMutationId}" % (a, json.dumps(fields[f]["id"]), v)
        parts = [upd("a", "Status", "singleSelectOptionId:%s" % json.dumps(opt("Status", "Todo"))),
                 upd("d", "Người phụ trách (giả định)", "singleSelectOptionId:%s" % json.dumps(opt("Người phụ trách (giả định)", want[2]))),
                 upd("e", "Epic", "singleSelectOptionId:%s" % json.dumps(opt("Epic", want[3])))]
        if s is not None:
            parts += [upd("b", "SWP", "number:%s" % s), upd("c", "Giờ ước lượng", "number:%s" % g)]
        gql("mutation($p:ID!,$it:ID!){" + "".join(parts) + "}", p=pid, it=e["item_id"])
        e["fields_set"] = list(want)
        save_map(m)
        print(f"item {i}: SWP {s}, {g} giờ, {want[2]}", flush=True)
        time.sleep(0.7)


def do_verify():
    """Đọc lại Project: đếm item, tổng SWP / Giờ, Status, Sprint; so với swp.json."""
    m = load_map()
    pid = m["_project"]["id"]
    q = ("query($p:ID!,$c:String){node(id:$p){...on ProjectV2{public items(first:100,after:$c){pageInfo{hasNextPage endCursor} nodes{"
         "content{...on Issue{title}} fieldValues(first:20){nodes{"
         "...on ProjectV2ItemFieldNumberValue{number field{...on ProjectV2FieldCommon{name}}}"
         "...on ProjectV2ItemFieldSingleSelectValue{name field{...on ProjectV2FieldCommon{name}}}"
         "...on ProjectV2ItemFieldIterationValue{title field{...on ProjectV2FieldCommon{name}}}}}}}}}}")
    items, cur = [], None
    while True:
        args = ["api", "graphql", "-f", f"query={q}", "-f", f"p={pid}"] + (["-f", f"c={cur}"] if cur else [])
        node = gh(args)["data"]["node"]
        items += node["items"]["nodes"]
        if not node["items"]["pageInfo"]["hasNextPage"]:
            break
        cur = node["items"]["pageInfo"]["endCursor"]
    tot = {"SWP": 0, "Giờ ước lượng": 0}
    status, sprint, missing = {}, 0, []
    for it in items:
        vals = {}
        for v in it["fieldValues"]["nodes"]:
            if v and v.get("field"):
                vals[v["field"]["name"]] = v.get("number", v.get("name", v.get("title")))
        for k in tot:
            tot[k] += vals.get(k) or 0
        status[vals.get("Status")] = status.get(vals.get("Status"), 0) + 1
        sprint += 1 if vals.get("Sprint") else 0
        if not vals.get("Epic") or not vals.get("Người phụ trách (giả định)"):
            missing.append(it["content"]["title"][:12])
    res = dict(public=node["public"], so_item=len(items), tong_SWP=tot["SWP"], tong_gio=tot["Giờ ước lượng"],
               status=status, co_sprint=sprint, thieu_truong=missing,
               ky_vong=dict(SWP=swp["meta"]["tong_SWP"], gio=swp["meta"]["tong_gio"], item=len(backlog)))
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    steps = sys.argv[1:] or ["labels", "issues", "subissues"]
    check_account()
    for st in steps:
        print("==", st, flush=True)
        {"labels": do_labels, "issues": do_issues, "subissues": do_subissues, "project": do_project, "items": do_items, "verify": do_verify}[st]()
    print("XONG:", " ".join(steps))
