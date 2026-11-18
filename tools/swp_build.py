# -*- coding: utf-8 -*-
"""Tính SWP / giờ từ tools/swp_scores.py theo skills/swp-scoring/SKILL.md, xuất:
  backlog/swp.json · backlog/swp_review.json (giữ swp_chot đã có) · reports/swp-report.html
Chạy từ gốc repo:  python -I -X utf8 tools/swp_build.py
Dừng (exit 1) nếu thiếu / thừa điểm so với backlog.json hoặc còn issue SWP 13 / 21 chưa tách.
"""
import datetime, hashlib, html, json, math, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from swp_scores import SCORES, DA_TACH, __doc__ as SCORE_DOC  # noqa: E402

SEED = 20261117
CONG = {"T": "Chạm tiền / làm tròn", "B": "Chạm 営業日", "D": "Ghi đồng thời / offline", "Q": "Spec còn câu hỏi mở"}
GIO = {1: 2, 2: 4, 3: 6, 5: 10, 8: 16}


def swp_of(p):
    for lo, hi, v in [(1, 2, 1), (3, 4, 2), (5, 6, 3), (8, 9, 5), (10, 12, 8), (15, 16, 13), (20, 25, 21)]:
        if lo <= p <= hi:
            return v
    raise ValueError(p)


def score(s, c_nen, cong):
    c = min(5, c_nen + len(cong))
    swp = swp_of(s * c)
    low = "Q" in cong
    gio = None
    if swp in GIO:
        gio = GIO[swp]
        if low:
            gio = int(math.ceil(gio * 1.2 / 2.0) * 2)
    return c, swp, ("low" if low else "normal"), gio


backlog = json.load(open(os.path.join(ROOT, "backlog", "backlog.json"), encoding="utf-8"))
by_id = {x["id"]: x for x in backlog}
parents = {x["parent"] for x in backlog if x["type"] == "sub-issue"}
leaves = [x for x in backlog if x["type"] != "epic" and x["id"] not in parents]
leaf_ids = {x["id"] for x in leaves}

missing, extra = sorted(leaf_ids - set(SCORES)), sorted(set(SCORES) - leaf_ids)
if missing or extra:
    sys.exit("Thiếu điểm: %s | Thừa điểm (không phải issue lá): %s" % (missing, extra))

rows = []
for x in leaves:
    s, s_ly_do, c_nen, cong, c_ly_do = SCORES[x["id"]]
    assert 1 <= s <= 5 and 1 <= c_nen <= 5 and set(cong) <= set(CONG), x["id"]
    c, swp, conf, gio = score(s, c_nen, cong)
    rows.append(dict(id=x["id"], epic=x["epic"], title=x["title"], type=x["type"], parent=x["parent"],
                     S=s, S_ly_do=s_ly_do, C_nen=c_nen, C_cong=[CONG[k] for k in cong], C=c, C_ly_do=c_ly_do,
                     SWP=swp, gio=gio, confidence=conf, can_tach=swp >= 13))

can_tach = [r["id"] for r in rows if r["can_tach"]]
if can_tach:
    for r in rows:
        if r["can_tach"]:
            print("PHẢI TÁCH:", r["id"], r["S"], "x", r["C"], "->", r["SWP"])
    sys.exit(1)

# issue cha = tổng con (đệ quy 1 cấp: issue → sub-issue)
cha = []
for pid in sorted(parents):
    kids = [r for r in rows if r["parent"] == pid]
    cha.append(dict(id=pid, epic=by_id[pid]["epic"], title=by_id[pid]["title"], type=by_id[pid]["type"],
                    con=[k["id"] for k in kids], SWP=sum(k["SWP"] for k in kids), gio=sum(k["gio"] for k in kids)))

da_tach = []
for oid, vong, s, c_nen, cong, new_ids, ly_do in DA_TACH:
    c, swp, conf, _ = score(s, c_nen, cong)
    assert swp >= 13, oid
    for n in new_ids:
        assert n in leaf_ids or n in parents, (oid, n)
    da_tach.append(dict(id_goc=oid, vong=vong, S=s, C_nen=c_nen, C_cong=[CONG[k] for k in cong], C=c,
                        SWP=swp, tach_thanh=new_ids, ly_do=ly_do))

# ---------------- chọn issue mẫu (skill mục 6) ----------------
rng = random.Random(SEED)
chosen = {}
order = lambda r: (r["epic"], r["id"])
for r in sorted([r for r in rows if r["epic"] == "E12"], key=order):
    chosen[r["id"]] = "1. Epic ràng buộc đặc thù 完納奨励金"
rest = [r for r in rows if r["id"] not in chosen]
hi = sorted(rest, key=lambda r: (-r["SWP"], -r["gio"], -r["S"] * r["C"], r["id"]))[:2]
lo = sorted(rest, key=lambda r: (r["SWP"], r["gio"], r["S"] * r["C"], r["id"]))[:2]
for r in hi:
    chosen[r["id"]] = "2. SWP cao nhất"
for r in lo:
    chosen[r["id"]] = "2. SWP thấp nhất"
for r in sorted(rows, key=order):
    if r["confidence"] == "low" and r["id"] not in chosen:
        chosen[r["id"]] = "3. confidence = low"
epics = [x for x in backlog if x["type"] == "epic"]
for e in epics:
    if e["id"] == "E12":
        continue
    cand = sorted(r["id"] for r in rows if r["epic"] == e["id"] and r["id"] not in chosen)
    if cand:
        chosen[rng.choice(cand)] = "4. Ngẫu nhiên trong epic (seed %d)" % SEED
row_by_id = {r["id"]: r for r in rows}
mau = [dict(row_by_id[i], ly_do_chon=chosen[i]) for i in sorted(chosen, key=lambda i: (chosen[i][0], i))]
for r in rows:
    r["mau"] = r["id"] in chosen

# ---------------- swp_review.json (người chốt) ----------------
rv_path = os.path.join(ROOT, "backlog", "swp_review.json")
old = {}
if os.path.exists(rv_path):
    for o in json.load(open(rv_path, encoding="utf-8")):
        old[o["id"]] = o
review = []
for m in mau:
    o = old.get(m["id"])
    keep = o is not None and o.get("swp_ai") == m["SWP"]
    review.append(dict(id=m["id"], swp_ai=m["SWP"], swp_chot=o.get("swp_chot") if keep else None,
                       ly_do=o.get("ly_do", "") if keep else ""))
with open(rv_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("[\n" + ",\n".join("  " + json.dumps(r, ensure_ascii=False) for r in review) + "\n]\n")
rv = {r["id"]: r for r in review}

# ---------------- áp swp_chot của người review (SKILL mục 6), tính lại giờ (mục 5) ----------------
def gio_of(swp, conf):
    g = GIO[swp]
    return int(math.ceil(g * 1.2 / 2.0) * 2) if conf == "low" else g

for r in rows:
    r["swp_ai"], r["gio_ai"] = r["SWP"], r["gio"]
    o = rv.get(r["id"])
    r["swp_chot"] = o["swp_chot"] if o else None
    r["ly_do_chot"] = o["ly_do"] if o else ""
    if r["swp_chot"] is not None:
        assert r["swp_chot"] in GIO, (r["id"], r["swp_chot"])
        r["SWP"], r["gio"] = r["swp_chot"], gio_of(r["swp_chot"], r["confidence"])
for c in cha:
    kids = [r for r in rows if r["parent"] == c["id"]]
    c["SWP"], c["gio"] = sum(k["SWP"] for k in kids), sum(k["gio"] for k in kids)
n_chot = sum(1 for o in review if o["swp_chot"] is not None)
n_sua = sum(1 for o in review if o["swp_chot"] is not None and o["swp_chot"] != o["swp_ai"])
ty_le = (n_sua / n_chot) if n_chot else 0.0
if not n_chot:
    ket_luan = "Chưa có điểm người chốt."
elif ty_le >= 0.30:
    ket_luan = "Sửa ≥ 30% issue mẫu → phải sửa tiêu chí mục 2–3 rồi chấm lại toàn bộ (SKILL mục 6)."
else:
    ket_luan = "Sửa < 30% issue mẫu → giữ tiêu chí, chỉ áp điểm đã chốt cho issue mẫu (SKILL mục 6)."

# ---------------- swp.json ----------------
skill_path = os.path.join(ROOT, "skills", "swp-scoring", "SKILL.md")
skill_ver = "swp-scoring @ sha256:" + hashlib.sha256(open(skill_path, "rb").read()).hexdigest()[:12]
today = datetime.date.today().isoformat()
tong_swp, tong_gio = sum(r["SWP"] for r in rows), sum(r["gio"] for r in rows)
theo_epic = []
for e in epics:
    rs = [r for r in rows if r["epic"] == e["id"]]
    theo_epic.append(dict(epic=e["id"], ten=e["title"], so_issue=len(rs), SWP=sum(r["SWP"] for r in rs), gio=sum(r["gio"] for r in rs),
                          low=sum(1 for r in rs if r["confidence"] == "low")))
meta = dict(ngay_chay=today, skill=skill_ver, seed_mau=SEED, quy_doi_gio="1 SWP ≈ 2 giờ: 1→2, 2→4, 3→6, 5→10, 8→16; confidence low +20% làm tròn lên số chẵn",
            so_issue_la=len(rows), so_issue_cha=len(cha), tong_SWP=tong_swp, tong_gio=tong_gio,
            tong_SWP_ai=sum(r["swp_ai"] for r in rows), tong_gio_ai=sum(r["gio_ai"] for r in rows),
            so_mau=len(review), so_mau_da_chot=n_chot, so_mau_sua=n_sua, ty_le_sua=round(ty_le, 4), ket_luan_review=ket_luan,
            so_low=sum(1 for r in rows if r["confidence"] == "low"), so_lan_tach=len(da_tach),
            ghi_chu="Giờ chưa gồm QA test riêng, quản lý, BrSE (SKILL mục 5).")
out = dict(meta=meta, issues=rows, issue_cha=cha, da_tach=da_tach, theo_epic=theo_epic,
           mau=[dict(id=m["id"], ly_do_chon=m["ly_do_chon"]) for m in mau])
json.dump(out, open(os.path.join(ROOT, "backlog", "swp.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ---------------- reports/swp-report.html ----------------
E = html.escape
def sc(r):
    cong = (" + " + ", ".join(r["C_cong"])) if r["C_cong"] else ""
    return f'S{r["S"]} × C{r["C"]} → <b>{r["SWP"]}</b><div class="sub">C nền {r["C_nen"]}{E(cong)}</div>'

dist = {k: sum(1 for r in rows if r["SWP"] == k) for k in (1, 2, 3, 5, 8)}
mx = max(dist.values()) or 1
bars = "".join(f'<div class="bar"><span class="lab">SWP {k}</span><span class="track"><span class="fill" style="width:{v / mx * 100:.1f}%"></span></span><span class="n">{v}</span></div>' for k, v in dist.items())

mau_rows = ""
for m in mau:
    r = rv[m["id"]]
    chot = "" if r["swp_chot"] is None else f'<b>{r["swp_chot"]}</b> · {row_by_id[m["id"]]["gio"]} giờ<div class="sub">{E(r["ly_do"])}</div>'
    cls = ' class="chg"' if r["swp_chot"] is not None and r["swp_chot"] != r["swp_ai"] else ""
    mau_rows += (f'<tr{cls}><td><code>{m["id"]}</code><div>{E(m["title"])}</div><div class="sub">{E(m["ly_do_chon"])} · {m["gio"]} giờ'
                 f'{" · low" if m["confidence"] == "low" else ""}</div></td><td>{sc(m)}</td><td>{chot}</td>'
                 f'<td><div><b>S:</b> {E(m["S_ly_do"])}</div><div><b>C:</b> {E(m["C_ly_do"])}</div></td></tr>')

all_rows = "".join(
    f'<tr data-epic="{r["epic"]}"><td><code>{r["id"]}</code></td><td>{E(r["title"])}</td><td>{r["S"]}</td><td>{r["C"]}'
    f'<div class="sub">{r["C_nen"]}{(" + " + E(", ".join(r["C_cong"]))) if r["C_cong"] else ""}</div></td><td><b>{r["SWP"]}</b>'
    f'{("<div class=sub>AI " + str(r["swp_ai"]) + "</div>") if r["swp_ai"] != r["SWP"] else ""}</td><td>{r["gio"]}</td>'
    f'<td>{"low" if r["confidence"] == "low" else ""}</td><td class="why"><div><b>S:</b> {E(r["S_ly_do"])}</div><div><b>C:</b> {E(r["C_ly_do"])}</div></td></tr>'
    for r in sorted(rows, key=order))
opts = "".join(f'<option value="{e["id"]}">{e["id"]} {E(e["title"])}</option>' for e in epics)
tach_rows = "".join(
    f'<tr><td><code>{d["id_goc"]}</code></td><td>{d["vong"]}</td><td>S{d["S"]} × C{d["C"]} = {d["S"] * d["C"]} → <b>{d["SWP"]}</b>'
    f'<div class="sub">C nền {d["C_nen"]}{(" + " + E(", ".join(d["C_cong"]))) if d["C_cong"] else ""}</div></td>'
    f'<td>{", ".join("<code>%s</code>" % n for n in d["tach_thanh"])}</td><td>{E(d["ly_do"])}</td></tr>' for d in da_tach)
low_rows = "".join(f'<tr><td><code>{r["id"]}</code></td><td>{E(r["title"])}</td><td>{r["SWP"]}</td><td>{r["gio"]}</td><td>{E(r["C_ly_do"])}</td></tr>'
                   for r in sorted(rows, key=order) if r["confidence"] == "low")
ep_rows = "".join(f'<tr><td><code>{t["epic"]}</code> {E(t["ten"])}</td><td>{t["so_issue"]}</td><td>{t["SWP"]}</td><td>{t["gio"]}</td><td>{t["low"]}</td></tr>' for t in theo_epic)
ep_rows += f'<tr class="tot"><td>Tổng</td><td>{len(rows)}</td><td>{tong_swp}</td><td>{tong_gio}</td><td>{meta["so_low"]}</td></tr>'
_items = []
for l in SCORE_DOC.splitlines():
    t = l.strip()
    if len(t) > 2 and t[0] == "R" and t[1].isdigit() and t[2] == ".":
        _items.append(t)
    elif _items and t and l.startswith("      "):
        _items[-1] += " " + t
rules = "".join(f"<li>{E(t)}</li>" for t in _items)

page = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Báo cáo SWP LAB-5</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#6b6a66;--line:#e2dfd8;--card:#fff;--acc:#2f5d8a;--low:#a4441c}}
@media (prefers-color-scheme:dark){{:root{{--bg:#171716;--fg:#ecebe7;--mut:#a3a19b;--line:#33322f;--card:#1f1f1d;--acc:#7fa9d4;--low:#e08a62}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,"Segoe UI","Hiragino Sans","Yu Gothic",sans-serif}}
main{{max-width:1180px;margin:0 auto;padding:24px 16px 64px}}h1{{font-size:22px;margin:0 0 4px}}h2{{font-size:17px;margin:32px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}}
.meta{{color:var(--mut);font-size:13px}}.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px}}.kpi b{{display:block;font-size:22px}}.kpi span{{color:var(--mut);font-size:12px}}
.bar{{display:flex;align-items:center;gap:8px;margin:4px 0}}.lab{{width:56px;color:var(--mut)}}.track{{flex:1;max-width:520px;height:14px;background:var(--line);border-radius:3px;overflow:hidden}}
.fill{{display:block;height:100%;background:var(--acc)}}.n{{width:32px;text-align:right}}
.wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;background:var(--card)}}th,td{{border:1px solid var(--line);padding:6px 8px;vertical-align:top;text-align:left}}
th{{font-size:12px;color:var(--mut);font-weight:600}}.sub{{color:var(--mut);font-size:12px}}.why{{min-width:280px}}code{{font-size:12px}}tr.tot td{{font-weight:700}}
select{{font:inherit;padding:4px 6px;margin:0 0 8px;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px}}
ul{{margin:6px 0;padding-left:20px}}tr.chg td{{background:color-mix(in srgb,var(--low) 12%,var(--card))}}
</style></head><body><main>
<h1>Báo cáo chấm SWP – Product A, LAB-5</h1>
<div class="meta">Ngày chạy {today} · {E(skill_ver)} · seed chọn mẫu {SEED} · nguồn: backlog/backlog.json, tools/swp_scores.py</div>
<div class="kpis">
<div class="kpi"><b>{len(rows)}</b><span>issue lá được chấm</span></div>
<div class="kpi"><b>{tong_swp}</b><span>tổng SWP sau chốt (AI: {meta["tong_SWP_ai"]})</span></div>
<div class="kpi"><b>{tong_gio}</b><span>tổng giờ sau chốt, gồm +20% low (AI: {meta["tong_gio_ai"]})</span></div>
<div class="kpi"><b>{n_sua}/{n_chot}</b><span>issue mẫu bị sửa ({ty_le * 100:.0f}%)</span></div>
<div class="kpi"><b>{meta["so_low"]}</b><span>issue confidence = low</span></div>
<div class="kpi"><b>{len(da_tach)}</b><span>lần tách vì SWP 13 / 21</span></div>
<div class="kpi"><b>{len(mau)}</b><span>issue mẫu (đã chốt {n_chot})</span></div>
</div>
<p class="meta">Quy đổi giờ: {E(meta["quy_doi_gio"])}. {E(meta["ghi_chu"])} Issue cha không chấm riêng: SWP cha = tổng con ({len(cha)} issue cha).</p>
<h2>Phân bố SWP</h2>{bars}
<h2>Cách hiểu tiêu chí khi chấm</h2><ul>{rules}</ul>
<h2>Issue mẫu để người chốt ({len(mau)})</h2>
<p class="meta">Chọn theo SKILL mục 6: (1) mọi issue epic 完納奨励金, (2) 2 SWP cao nhất + 2 thấp nhất trong phần còn lại, (3) mọi issue confidence = low, (4) 1 issue ngẫu nhiên mỗi epic còn lại (seed {SEED}). Cột "Bạn chốt" đọc từ backlog/swp_review.json.</p>
<p><b>Kết quả review:</b> {E(ket_luan)} Dòng tô màu là issue người chốt sửa điểm; tổng và bảng bên dưới dùng điểm đã chốt.</p>
<div class="wrap"><table><tr><th>Issue</th><th>Skill chấm (S × C → SWP)</th><th>Bạn chốt</th><th>Lý do</th></tr>{mau_rows}</table></div>
<h2>Issue phải tách (SWP 13 / 21) – đã tách và chấm lại</h2>
<div class="wrap"><table><tr><th>Issue gốc</th><th>Vòng</th><th>Điểm trước khi tách</th><th>Tách thành</th><th>Cách tách</th></tr>{tach_rows}</table></div>
<h2>Issue confidence = low</h2>
<div class="wrap"><table><tr><th>Issue</th><th>Tên</th><th>SWP</th><th>Giờ</th><th>Câu hỏi mở</th></tr>{low_rows}</table></div>
<h2>Tổng theo epic</h2>
<div class="wrap"><table><tr><th>Epic</th><th>Số issue lá</th><th>Tổng SWP</th><th>Tổng giờ</th><th>Low</th></tr>{ep_rows}</table></div>
<h2>Toàn bộ issue</h2>
<select id="f" aria-label="Lọc theo epic"><option value="">Tất cả epic</option>{opts}</select>
<div class="wrap"><table id="t"><tr><th>Issue</th><th>Tên</th><th>S</th><th>C</th><th>SWP</th><th>Giờ</th><th>Conf.</th><th>Lý do</th></tr>{all_rows}</table></div>
</main>
<script>
document.getElementById('f').addEventListener('change',function(e){{var v=e.target.value;
document.querySelectorAll('#t tr[data-epic]').forEach(function(tr){{tr.style.display=(!v||tr.dataset.epic===v)?'':'none'}})}});
</script></body></html>
"""
os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
open(os.path.join(ROOT, "reports", "swp-report.html"), "w", encoding="utf-8", newline="\n").write(page)

print("issue lá:", len(rows), "| tổng SWP:", tong_swp, "| tổng giờ:", tong_gio, "| low:", meta["so_low"], "| lần tách:", len(da_tach), "| mẫu:", len(mau))
