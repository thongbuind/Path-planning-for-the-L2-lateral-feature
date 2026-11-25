"""Sinh báo cáo so sánh generator T7 (PP-TS-031) từ techniques.json: các trang A4 ngang như một file PDF.

Một file HTML tĩnh tự chứa: CSS nằm trong file, không có script, nút bấm hay ô chọn, không tải gì từ mạng.
Mỗi `.page` là một trang A4 ngang; in ra (Ctrl+P, khổ A4 ngang, không lề) hoặc "Lưu thành PDF" cho cùng bố cục.
Không có hạng, điểm tổng hay ô "tốt nhất": màu ô chỉ cho biết hiệu so với mốc tốt hơn, xấu hơn hay trong dung sai.
Dữ liệu nháp (plan chưa khóa, chạy không --record) thì mọi trang có nhãn "NHÁP".

    python3 -m eval.campaign PP-TS-031          # ghi dashboard/techniques.json
    python3 research/generators/dashboard/build.py
"""

import argparse
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

PAGE_W, PAGE_H = 297, 210
BODY_MM = 158          # chiều cao dùng được của thân trang
ROW, ROW2, ROW3 = 4.9, 6.4, 12.0

STYLE = r"""
@page{size:297mm 210mm;margin:0}
:root{color-scheme:light;--page:#e9e8e4;--paper:#fff;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--neutral:#f0efec;
--b1:#cde2fb;--b2:#86b6ef;--b3:#2a78d6;--r1:#f8d3d2;--r2:#ee9493;--r3:#d03b3b;
--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--warn:#fab219;--crit:#d03b3b;--draft:#fff3cd}
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html{background:var(--page)}
body{margin:0;color:var(--ink);font:8.5pt/1.35 system-ui,-apple-system,"Segoe UI",sans-serif}
.page{width:297mm;height:210mm;margin:8mm auto;padding:11mm 14mm 9mm;background:var(--paper);position:relative;
overflow:hidden;box-shadow:0 1px 6px rgba(0,0,0,.18);display:flex;flex-direction:column;break-after:page;page-break-after:always}
@media print{html{background:#fff}.page{margin:0;box-shadow:none}}
.ph{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--axis);padding-bottom:2mm;margin-bottom:3mm}
.ph h2{font-size:14pt;margin:0}.ph .meta{color:var(--ink2);font-size:7.5pt;text-align:right}
.body{flex:1;min-height:0}
.pf{display:flex;justify-content:space-between;color:var(--muted);font-size:7pt;border-top:1px solid var(--grid);padding-top:1.5mm;margin-top:2mm}
h3{font-size:10pt;margin:3mm 0 1.5mm}
p{margin:0 0 2mm}.note{color:var(--ink2);font-size:7.8pt;margin:0 0 2.5mm}
.draft{background:var(--draft);border:1px solid var(--warn);padding:1.2mm 3mm;margin-bottom:2mm;font-weight:600;font-size:8pt}
table{border-collapse:collapse;font-variant-numeric:tabular-nums;width:100%;font-size:7pt}
th,td{border-bottom:1px solid var(--grid);padding:.5mm 1.3mm;text-align:left;vertical-align:top}
th{color:var(--ink2);font-weight:600;font-size:6.4pt;border-bottom:1px solid var(--axis)}
th .m{display:block;font-weight:400;color:var(--muted)}
td.num,th.num{text-align:right}
.chip{display:inline-block;overflow-wrap:normal;border-radius:1mm;padding:0 1.3mm;white-space:nowrap}
.better{background:var(--b2)}.worse{background:var(--r2)}.within{background:var(--neutral)}
.few{border:1px dashed var(--muted);color:var(--ink2)}
.cc{display:flex;flex-wrap:wrap;align-items:center;gap:0 1.4mm}.cc svg{flex:none}
.sub{color:var(--muted);font-size:6pt;line-height:1.25}
.flag{display:inline-block;margin-right:1mm;padding:0 1.2mm;border-radius:1mm;font-size:6.2pt;font-weight:600;white-space:nowrap}
.flag.red{background:var(--crit);color:#fff}.flag.amber{background:var(--warn)}
.muted{color:var(--muted)}b{font-weight:650}
.two{display:flex;gap:6mm}.two>div{flex:1}
td.name{overflow-wrap:anywhere}
td,th{overflow-wrap:anywhere}
.fx,.fx1{table-layout:fixed}.fx th:first-child,.fx1 th:first-child{width:58mm}.fx th:nth-child(2){width:26mm}
.two table{table-layout:fixed}.two th:first-child{width:62mm}
code{font:inherit;font-family:ui-monospace,Menlo,monospace;font-size:.95em}
.legend{display:flex;gap:4mm;flex-wrap:wrap;margin:2mm 0;color:var(--ink2);font-size:7pt}
.legend span::before{content:"";display:inline-block;width:2.6mm;height:2.6mm;border-radius:.6mm;margin-right:1.2mm;vertical-align:-.4mm;background:var(--c)}
.legend span.dash::before{background:transparent;border:1px dashed var(--muted)}
svg text{fill:var(--ink2);font-size:9px;font-family:inherit}
.tiles{display:flex;gap:5mm;margin:6mm 0}
.tile{flex:1;border:1px solid var(--grid);border-radius:1.5mm;padding:3mm 4mm}
.tile .v{font-size:24pt;font-weight:650;line-height:1.1}.tile .l{color:var(--ink2);font-size:7.5pt}
.cover h1{font-size:24pt;margin:14mm 0 2mm;line-height:1.15}.cover .sub2{font-size:10.5pt;color:var(--ink2);max-width:210mm}
.toc{columns:2;column-gap:10mm;font-size:8.5pt}.toc div{display:flex;justify-content:space-between;border-bottom:1px dotted var(--axis);padding:.9mm 0;break-inside:avoid}
.toc .sec{font-weight:650;border:0;margin-top:2mm}
.grid6{display:flex;flex-wrap:wrap;gap:2mm 3mm}
.hm{width:40mm}.hm .t{font-size:6.2pt;color:var(--ink2);height:10.5mm;line-height:1.2;overflow:hidden}
a{color:var(--s1)}
"""

LABEL = {"better": "▲", "worse": "▼", "within": "≈", "few": "○"}


# ---------- định dạng ----------

def esc(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def nm(s) -> str:
    """Tên cấu hình, cho phép ngắt dòng sau dấu gạch ngang."""
    return esc(s).replace("-", "-<wbr>")


def fmt(v, d=3) -> str:
    if v is None or isinstance(v, bool) or not isinstance(v, (int, float)) or v != v or abs(v) == float("inf"):
        return "—"
    if abs(v) >= 1000:
        return f"{v:.0f}"
    r = float(f"{v:.{d}g}")
    s = f"{r:.10f}".rstrip("0").rstrip(".")
    return (s if s not in ("-0", "") else "0").replace(".", ",")


def pct(v) -> str:
    return "—" if v is None else f"{100 * v:.1f} %".replace(".", ",")


# ---------- thành phần HTML ----------

def chip(c, extra="", ci=True) -> str:
    if not c or c.get("mean") is None:
        return '<span class="muted">—</span>'
    sub = ""
    if ci:
        sub = (f"CI [{fmt(c['ci'][0])}; {fmt(c['ci'][1])}], n = {c.get('n')}" if c.get("ci") else f"n = {c.get('n')}")
        sub = f'<span class="sub">{sub}</span>'
    return f'<div class="cc"><span class="chip {c["label"]}">{LABEL[c["label"]]} {fmt(c.get("mean"), 2)}</span>{extra}{sub}</div>'


def chip_plain(c) -> str:
    if not c or c.get("mean") is None:
        return '<span class="muted">—</span>'
    return f'<span class="chip {c["label"]}">{LABEL[c["label"]]} {fmt(c["mean"], 2)}</span>'


def flags(f) -> str:
    if not f:
        return ""
    s = ""
    if f.get("b0_blocked"):
        s += '<span class="flag red">B0</span>'
    if f.get("new_failure_runs"):
        s += f'<span class="flag red">{f["new_failure_runs"]} trượt mới</span>'
    if f.get("lcc_runs_lost"):
        s += f'<span class="flag amber">LCC lái ít hơn: {f["lcc_runs_lost"]} lượt</span>'
    if f.get("evaluator_errors"):
        s += f'<span class="flag amber">{f["evaluator_errors"]} lỗi chấm</span>'
    return s


def legend() -> str:
    return ('<div class="legend"><span style="--c:var(--b2)">▲ tốt hơn mốc (CI không chứa 0 và |hiệu| ≥ dung sai)</span>'
            '<span style="--c:var(--r2)">▼ xấu hơn mốc</span><span style="--c:var(--neutral)">≈ trong dung sai</span>'
            '<span class="dash">○ ít dữ liệu (n &lt; 4)</span></div>')


def metric_head(ms, cls="") -> str:
    return "".join(f'<th{cls}>{esc(m["id"].replace("PP-SWR-", ""))}<span class="m">{esc(m["metric"][:30])}</span></th>' for m in ms)


def strip_plot(c) -> str:
    diffs = c.get("diffs") or []
    if not diffs:
        return ""
    W, H = 80, 14
    ds = [p["d"] for p in diffs]
    lo, hi = min(0, *ds), max(0, *ds)
    span = (hi - lo) or 1
    x = lambda v: 3 + (W - 6) * (v - lo) / span
    s = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="hiệu từng lượt">'
         f'<line x1="{x(0):.1f}" x2="{x(0):.1f}" y1="1" y2="{H - 1}" stroke="var(--axis)"/>')
    for p in diffs:
        s += (f'<circle cx="{x(p["d"]):.1f}" cy="{H / 2}" r="3" fill="{"var(--b3)" if p["d"] >= 0 else "var(--r3)"}" '
              f'fill-opacity=".75" stroke="#fff" stroke-width="1"/>')
    return s + "</svg>"


def heatmap(D, P, f, axes, m) -> str:
    a, b = axes
    la, lb = f["grid"][a], f["grid"][b]
    cs, pad = 26, 30
    W, Hh = pad + cs * len(lb) + 3, 12 + cs * len(la) + 12
    same = lambda x, y: abs(float(x) - float(y)) < 1e-9
    val = lambda n, k: (D["configs"].get(n) or {}).get("values", {}).get(k)
    pick = lambda lv: lv if isinstance(lv, list) else [lv]
    ka, kb = a.split("+"), b.split("+")
    key = m["id"] + "|" + m["metric"]
    s = f'<svg width="40mm" viewBox="0 0 {W} {Hh}" role="img">'
    for i, va in enumerate(la):
        s += f'<text x="{pad - 3}" y="{12 + cs * i + cs / 2 + 3}" text-anchor="end" style="font-size:7px">{esc("/".join(map(fmt, pick(va))))}</text>'
        for j, vb in enumerate(lb):
            name = next((n for n in f["configs"] if all(val(n, k) is not None and same(val(n, k), pick(va)[q]) for q, k in enumerate(ka))
                         and all(val(n, k) is not None and same(val(n, k), pick(vb)[q]) for q, k in enumerate(kb))), None)
            c = (P["configs"].get(name, {}).get("cells") or {}).get(key) if name else None
            fill, txt = "var(--neutral)", "mốc" if name == D["baseline"] else "—"
            if c and c.get("mean") is not None:
                r = c["mean"] / c["tolerance"] if c.get("tolerance") else 0
                step = 0 if abs(r) < 1 else 1 if abs(r) < 2 else 2 if abs(r) < 4 else 3
                fill = "var(--neutral)" if step == 0 or c["label"] == "few" else f"var(--{'b' if r > 0 else 'r'}{step})"
                txt = fmt(c["mean"], 2)
            is_def = bool(name and (D["configs"].get(name) or {}).get("default"))
            s += (f'<rect x="{pad + cs * j + .5}" y="{12 + cs * i + .5}" width="{cs - 1}" height="{cs - 1}" rx="2" fill="{fill}" '
                  f'stroke="{"var(--ink)" if is_def else "#fff"}" stroke-width="{1.3 if is_def else 1}"/>'
                  f'<text x="{pad + cs * j + cs / 2}" y="{12 + cs * i + cs / 2 + 2.5}" text-anchor="middle" style="fill:var(--ink);font-size:6.3px">{esc(txt)}</text>')
    for j, vb in enumerate(lb):
        s += f'<text x="{pad + cs * j + cs / 2}" y="9" text-anchor="middle" style="font-size:7px">{esc("/".join(map(fmt, pick(vb))))}</text>'
    s += "</svg>"
    return s


def scatter(rows) -> str:
    pts = [r for r in rows if r.get("p99_median_ms") is not None and r.get("diff_max_m") is not None]
    many = {f for f in {p["series"] for p in pts} if sum(1 for p in pts if p["series"] == f) >= 2}
    pts = [p for p in pts if p["series"] in many]
    if not pts:
        return '<p class="muted">Chưa có điểm (cần lượt vòng hở và nghiệm tham chiếu).</p>'
    fams = list(dict.fromkeys(p["series"] for p in pts))[:3]
    col = lambda f: ["var(--s1)", "var(--s2)", "var(--s3)"][fams.index(f)] if f in fams else "var(--muted)"
    W, H, L, B, T, R = 640, 260, 56, 38, 10, 16
    x1 = max(p["p99_median_ms"] for p in pts) * 1.1
    y1 = max(p["diff_max_m"] for p in pts) * 1.15 or 1
    X = lambda v: L + (W - L - R) * v / x1
    Y = lambda v: H - B - (H - B - T) * v / y1
    s = (f'<div class="legend">' + "".join(f'<span style="--c:{col(f)}">{esc(f)}</span>' for f in fams) + '</div>'
         f'<svg width="160mm" viewBox="0 0 {W} {H}" role="img" aria-label="lệch so với nghiệm tham chiếu theo p99">')
    for i in range(5):
        yv = y1 * i / 4
        s += f'<line x1="{L}" x2="{W - R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="var(--grid)"/><text x="{L - 5}" y="{Y(yv) + 3:.1f}" text-anchor="end">{fmt(yv, 2)}</text>'
        xv = x1 * i / 4
        s += f'<text x="{X(xv):.1f}" y="{H - B + 14}" text-anchor="middle">{fmt(xv, 2)}</text>'
    s += (f'<line x1="{L}" x2="{W - R}" y1="{H - B}" y2="{H - B}" stroke="var(--axis)"/>'
          f'<text x="{(L + W - R) / 2}" y="{H - 5}" text-anchor="middle">p99 thời gian tính [ms]</text>'
          f'<text x="12" y="{(H - B) / 2}" transform="rotate(-90 12 {(H - B) / 2})" text-anchor="middle">lệch lớn nhất [m]</text>')
    for f in fams:
        line = sorted((p for p in pts if p["series"] == f), key=lambda p: p["iterations"])
        s += f'<polyline fill="none" stroke="{col(f)}" stroke-width="2" stroke-linejoin="round" points="{" ".join(f"{X(p["p99_median_ms"]):.1f},{Y(p["diff_max_m"]):.1f}" for p in line)}"/>'
    for p in pts:
        s += (f'<circle cx="{X(p["p99_median_ms"]):.1f}" cy="{Y(p["diff_max_m"]):.1f}" r="{5.5 if p["pareto"] else 4}" fill="{col(p["series"])}" stroke="#fff" stroke-width="2"/>'
              f'<text x="{X(p["p99_median_ms"]) + 6:.1f}" y="{Y(p["diff_max_m"]) - 6:.1f}">{p["iterations"]}</text>')
    return s + "</svg>"


def cost_bars(D, P, names) -> str:
    rows = [(n, P["configs"][n]["cost"]["p99_median_ms"]) for n in names if P["configs"][n]["cost"].get("p99_median_ms") is not None]
    if not rows:
        return ""
    W, rh, L, R = 640, 12.5, 240, 60
    H = 10 + rh * len(rows) + 22
    mx = max(v for _, v in rows) * 1.1
    X = lambda v: L + (W - L - R) * v / mx
    s = f'<svg width="190mm" viewBox="0 0 {W} {H}" role="img" aria-label="p99 thời gian tính">'
    for i in range(5):
        xv = mx * i / 4
        s += f'<line x1="{X(xv):.1f}" x2="{X(xv):.1f}" y1="6" y2="{H - 18}" stroke="var(--grid)"/><text x="{X(xv):.1f}" y="{H - 6}" text-anchor="middle">{fmt(xv, 2)}</text>'
    for i, (n, v) in enumerate(rows):
        y = 10 + rh * i
        s += (f'<text x="{L - 6}" y="{y + 8}" text-anchor="end" style="fill:var(--ink)">{esc(n)}</text>'
              f'<rect x="{L}" y="{y + 1}" width="{X(v) - L:.1f}" height="9" rx="2" fill="var(--s1)"/>'
              f'<text x="{X(v) + 4:.1f}" y="{y + 8}">{fmt(v)}</text>')
    return s + f'<text x="{L}" y="{H - 20}" style="font-size:0"> </text></svg>'


# ---------- phân trang ----------

class Doc:
    def __init__(self, data: dict):
        self.D = data
        self.pages: list[dict] = []   # {section, title, html, cont}
        self.cur: dict | None = None
        self.used = 0.0

    def new_page(self, section: str, title: str, cont: bool = False) -> None:
        self.cur = {"section": section, "title": title + (" (tiếp)" if cont else ""), "html": [], "first": not cont}
        self.pages.append(self.cur)
        self.used = 0.0

    def begin(self, title: str, section: str | None = None) -> None:
        self.title, self.section = title, section or title
        self.new_page(self.section, title)

    def add(self, html_: str, h: float) -> None:
        if self.used + h > BODY_MM and self.used > 0:
            self.new_page(self.section, self.title, cont=True)
        self.cur["html"].append(html_)
        self.used += h

    def table(self, head: str, rows: list[tuple[str, float]], head_h: float = 9.5, cls: str = "") -> None:
        """Bảng chia nhiều trang, lặp lại hàng tiêu đề."""
        i = 0
        while i < len(rows):
            if self.used + head_h + rows[i][1] > BODY_MM and self.used > 0:
                self.new_page(self.section, self.title, cont=True)
            chunk, hh = [], head_h
            while i < len(rows) and self.used + hh + rows[i][1] <= BODY_MM:
                chunk.append(rows[i][0])
                hh += rows[i][1]
                i += 1
            if not chunk:            # một hàng cao hơn cả trang
                chunk.append(rows[i][0]); hh += rows[i][1]; i += 1
            self.cur["html"].append(f'<table{cls}><thead><tr>{head}</tr></thead><tbody>{"".join(chunk)}</tbody></table>')
            self.used += hh + 2
            if i < len(rows):
                self.new_page(self.section, self.title, cont=True)

    def render(self) -> str:
        D = self.D
        draft = D.get("draft", True)
        n = len(self.pages) + 1
        toc, seen = [], {}
        for k, p in enumerate(self.pages, start=2):
            seen.setdefault(p["section"], k)
        out = [self.cover(seen, n)]
        for k, p in enumerate(self.pages, start=2):
            tag = " · NHÁP" if draft else ""
            out.append(f'<section class="page"><div class="ph"><h2>{esc(p["title"])}</h2>'
                       f'<div class="meta">{esc(D["study"])}{tag}<br>mốc <code>{esc(D["baseline"])}</code></div></div>'
                       f'<div class="body">{"".join(p["html"])}</div>'
                       f'<div class="pf"><span>Lab chỉ mô tả, không chọn generator. Hiệu dương: tốt hơn mốc.</span><span>Trang {k} / {n}</span></div></section>')
        return "".join(out)

    def cover(self, seen: dict, n: int) -> str:
        D = self.D
        draft = D.get("draft", True)
        banner = ('<div class="draft">NHÁP: plan chưa khóa hoặc có lần chạy không phải --record trên cây sạch. Không trích số liệu này.</div>'
                  if draft else "")
        tp = D["parts"].get("test") or next(iter(D["parts"].values()), {"metrics": [], "configs": {}})
        runs = sorted({r.get("run_id") for p in D["parts"].values() for r in p["configs"].values() if r.get("run_id")})
        nconf = len({n_ for p in D["parts"].values() for n_ in p["configs"]})
        tiles = [(nconf, "cấu hình, gồm nghiệm tham chiếu 1000 vòng"), (len(runs), "lần chạy chính thức"),
                 (len(tp["metrics"]), "chỉ số so với mốc"), (len(D["parts"]), "phần: " + ", ".join(D["parts"]))]
        toc = ""
        for name, pg in seen.items():
            cls = "sec" if name.startswith(("Phần", "Phụ lục")) else ""
            toc += f'<div class="{cls}"><span>{esc(name)}</span><span>{pg}</span></div>'
        return (f'<section class="page cover"><div class="body">{banner}'
                f'<div class="muted" style="margin-top:6mm">{esc(D["study"])} · Chiến dịch generator T7 của LCC planner</div>'
                f'<h1>So sánh khả năng của các họ thuật toán sinh path</h1>'
                f'<p class="sub2">Quintic, QP jerk (ADMM) theo số vòng, warm start dịch thời gian, driver model và MLP quanh QP, '
                f'so ở an toàn, bám làn và cảm nhận, flexibility, chi phí phần cứng và độ nhạy calibration. '
                f'Không có hạng, điểm tổng hay lựa chọn: mỗi ô là hiệu so với mốc <code>{esc(D["baseline"])}</code> ở calibration mặc định. '
                f'Chọn generator là việc của người dùng.</p>'
                f'<div class="tiles">{"".join(f"<div class=tile><div class=v>{v}</div><div class=l>{esc(l)}</div></div>" for v, l in tiles)}</div>'
                f'<h3>Cách đọc một ô</h3><p class="note">Ô là hiệu ghép cặp so với mốc (dương: tốt hơn), kèm khoảng tin cậy 95 % và số cặp n. '
                f'Màu chỉ theo nhãn: "khác có ý nghĩa" khi khoảng tin cậy không chứa 0 và hiệu vượt dung sai '
                f'(<code>study.md</code> mục 3.3); ít hơn 4 cặp thì ghi "ít dữ liệu". Cờ cảnh báo không loại cấu hình nào.</p>{legend()}'
                f'<h3>Nội dung</h3><div class="toc">{toc}</div></div>'
                f'<div class="pf"><span>Plan <code>{esc(D.get("plan", {}).get("path"))}</code> sha256 {esc((D.get("plan", {}).get("sha256") or "")[:12])}, '
                f'khóa {esc(D.get("plan", {}).get("locked") or "chưa")}. Run: {esc(", ".join(runs) or "nháp")}</span><span>Trang 1 / {n}</span></div></section>')


# ---------- các trang ----------

def families(D):
    return [f for f in D["families"] if f["compared"]]


def default_names(D, P):
    return [f["default"] for f in families(D) if f["default"] in P["configs"]]


def all_names(D, P):
    return [n for n in P["configs"] if (D["configs"].get(n) or {}).get("compared", True)]


def grid_range(D, P, family, key) -> str:
    fam = next((f for f in D["families"] if f["variant"] == family), None)
    if not fam or len(fam["configs"]) < 2:
        return ""
    vals = [((P["configs"].get(n) or {}).get("cells") or {}).get(key, {}).get("mean") for n in fam["configs"]]
    vals = [v for v in vals if v is not None]
    return f'<span class="sub">lưới {fmt(min(vals))} … {fmt(max(vals))}</span>' if len(vals) >= 2 else ""


def page_overview(doc, D, P, title, section):
    ms = P["metrics"]
    mk = lambda m: m["id"] + "|" + m["metric"]
    doc.begin(title, section)
    doc.add('<p class="note">Hàng: từng thuật toán ở cấu hình mặc định. Ô: hiệu ghép cặp so với mốc (dương: tốt hơn), màu theo nhãn; '
            'CI 95 % và n ở các trang An toàn, Bám làn và cảm nhận; dải hiệu của cả lưới calibration ở trang Độ nhạy calibration. Không có hạng hay điểm tổng.</p>' + legend(), 12)
    rows = []
    for f in families(D):
        r = P["configs"].get(f["default"])
        if not r:
            rows.append((f'<tr><td>{esc(f["variant"])}</td><td colspan="{len(ms) + 1}" class="muted">chưa chạy</td></tr>', ROW))
            continue
        cells = "".join(f'<td>{"<span class=muted>mốc</span>" if f["variant"] == D["baseline"] else chip(r["cells"].get(mk(m)), "", ci=False)}</td>' for m in ms)
        rows.append((f'<tr><td><b>{esc(f["variant"])}</b></td><td>{flags(r.get("flags"))}</td>{cells}</tr>', ROW2))
    doc.table(f'<th>Thuật toán</th><th>Cờ</th>{metric_head(ms)}', rows, head_h=22, cls=' class="fx"')


def page_group(doc, D, P, title, section, group, strip):
    ms = [m for m in P["metrics"] if m["group"] == group]
    mk = lambda m: m["id"] + "|" + m["metric"]
    doc.begin(title, section)
    doc.add(f'<p class="note">Hiệu ghép cặp so với mốc, kèm CI 95 % và n.{" Chấm: hiệu của từng lượt (xanh: tốt hơn, đỏ: xấu hơn), vạch đứng là 0." if strip else ""}</p>', 6)
    rows = []
    for n in default_names(D, P):
        if n == D["baseline"]:
            continue
        r = P["configs"][n]
        tds = ""
        for m in ms:
            c = r["cells"].get(mk(m))
            tds += f'<td>{chip(c, strip_plot(c) if strip and c else "")}</td>'
        rows.append((f'<tr><td class="name"><b>{nm(n)}</b></td><td>{flags(r.get("flags"))}</td>{tds}</tr>', 6.8 if strip else 12.8))
    doc.table(f'<th>Cấu hình</th><th>Cờ</th>{metric_head(ms)}', rows, head_h=22 if len(ms) > 6 else 9, cls=' class="fx"')
    doc.add(legend(), 6)


def page_case_groups(doc, D, P, title, section):
    groups = list(D["case_groups"])
    mk = lambda m: m["id"] + "|" + m["metric"]
    ms = P["metrics"]
    for g in groups:
        doc.begin(f"{title}: {g}", f"{title}: {g}" if g != groups[0] else title)
        doc.add(f'<p class="note">Nhóm ca <b>{esc(g)}</b> = {esc(", ".join("".join(x) for x in D["case_groups"][g]))}. Hiệu ghép cặp so với mốc chỉ trong nhóm này; — là nhóm không có cặp nào cho chỉ số đó.</p>' + legend(), 12)
        rows = []
        for n in default_names(D, P):
            if n == D["baseline"]:
                continue
            r = P["configs"][n]
            cells = "".join(f'<td>{chip_plain(((r["cells"].get(mk(m)) or {}).get("groups") or {}).get(g))}</td>' for m in ms)
            rows.append((f'<tr><td class="name"><b>{nm(n)}</b></td>{cells}</tr>', ROW2))
        doc.table(f'<th>Cấu hình</th>{metric_head(ms)}', rows, head_h=22, cls=' class="fx1"')


def page_flex(doc, D, P, title, section):
    doc.begin(title, section)
    fm = P["flex_metrics"]
    doc.add('<p class="note">Cùng một bản build và một bộ calibration trên mọi vehicle profile. Bảng 1: hiệu ghép cặp của độ chênh giữa các profile so với mốc (dương: ít chênh hơn mốc). Bảng 2: giá trị của các chỉ số an toàn và êm theo từng profile (số liệu đầy đủ ở <code>techniques.json</code>).</p>' + legend(), 14)
    head = "<th>Cấu hình</th>" + "".join(f'<th>{esc(m[0].replace("PP-SWR-", ""))}<span class="m">{esc(m[1][:30])}</span></th>' for m in fm)
    rows = [(f'<tr><td class="name"><b>{nm(n)}</b></td>' + "".join(f'<td>{chip_plain(P["configs"][n]["cells"].get("flex|" + m[0] + "|" + m[1]))}</td>' for m in fm) + "</tr>", ROW2)
            for n in default_names(D, P) if n != D["baseline"]]
    doc.table(head, rows, head_h=22, cls=' class="fx1"')
    doc.begin("Flexibility: giá trị theo profile", "Flexibility (giá trị theo profile)")
    pick = ["PP-SWR-070", "PP-SWR-068", "PP-SWR-069", "PP-SWR-050"]
    names = default_names(D, P)
    keys = []
    for pid in pick:
        for n in names:
            k = next((k for k in (P["configs"][n].get("by_profile") or {}) if k.startswith(pid + "|")), None)
            if k:
                keys.append(k); break
    profiles = sorted({pr for n in names for k in keys for pr in (P["configs"][n].get("by_profile") or {}).get(k, {})})
    if keys and profiles:
        doc.add('<p class="note">Giá trị xấu nhất của chỉ số theo profile (đơn vị của chỉ số).</p>', 6)
        head1 = "<th rowspan=2>Cấu hình</th>" + "".join(f'<th colspan={len(profiles)}>{esc(k.split("|")[0].replace("PP-SWR-", ""))}<span class="m">{esc(k.split("|")[1][:44])}</span></th>' for k in keys)
        head2 = "".join(f'<th class="num">{esc(pr)}</th>' for _ in keys for pr in profiles)
        rows = [(f'<tr><td class="name"><b>{nm(n)}</b></td>' + "".join(f'<td class="num">{fmt(((P["configs"][n].get("by_profile") or {}).get(k) or {}).get(pr))}</td>' for k in keys for pr in profiles) + "</tr>", ROW) for n in names]
        doc.table(head1 + "</tr><tr>" + head2, rows, head_h=18, cls=' class="fx1"')


def page_cost(doc, D, P, title, section):
    doc.begin(title, section)
    names = default_names(D, P)
    doc.add('<p class="note">Thời gian CPU của <code>pp_lcc_step</code> qua adapter SIL trên laptop, không chuyển thẳng sang ECU. p99 là trung vị qua các lượt của p99 từng lượt, đo ở 2 job; "phiên 1 job" đo riêng cho cấu hình mặc định (S1f, S1c vòng kín, lặp 3 lần, thứ tự xen kẽ), ít nhiễu hơn. Phần cứng chọn theo trường hợp xấu nhất nên max, khối lượng việc, bộ nhớ và kích thước là ngữ cảnh.</p>', 13)
    doc.add("<h3>p99 thời gian tính, 2 job [ms]</h3>" + cost_bars(D, P, names), 12 + 3.6 * len(names))
    t016 = next((m for m in P["metrics"] if m["id"] == "PP-SWR-016"), None)
    doc.begin("Chi phí phần cứng: bảng số", "Chi phí phần cứng (bảng số)")
    head = ("<th>Cấu hình</th><th>016 p99</th><th class=num>p99 [ms]</th><th class=num>% chu kỳ 25 ms</th><th class=num>p99 lớn nhất [ms]</th>"
            "<th class=num>p99 phiên 1 job [ms]</th><th class=num>Thời gian lớn nhất [ms]</th><th class=num>Khối lượng việc lớn nhất</th>"
            "<th class=num>Phép nhân MLP</th><th class=num>State [byte]</th><th class=num>Thư viện [byte]</th><th class=num>Weights [byte]</th>")
    rows = []
    for n in names:
        r = P["configs"][n]
        c = r["cost"]
        k016 = r["cells"].get(t016["id"] + "|" + t016["metric"]) if t016 else None
        rows.append((f'<tr><td class="name"><b>{nm(n)}</b></td><td>{"<span class=muted>mốc</span>" if n == D["baseline"] else chip_plain(k016)}</td>'
                     f'<td class="num">{fmt(c.get("p99_median_ms"))}</td><td class="num">{pct(c.get("p99_cycle_share"))}</td><td class="num">{fmt(c.get("p99_max_ms"))}</td>'
                     f'<td class="num">{fmt(c["timing_1job"]["p99_median_ms"]) if c.get("timing_1job") else "—"}</td><td class="num">{fmt(c.get("max_ms"))}</td>'
                     f'<td class="num">{fmt(c.get("work_max"))}</td><td class="num">{fmt(c.get("infer_ops_max"))}</td>'
                     f'<td class="num">{c.get("state_bytes") if c.get("state_bytes") is not None else "—"}</td><td class="num">{c.get("library_bytes") if c.get("library_bytes") is not None else "—"}</td>'
                     f'<td class="num">{c.get("weights_bytes") if c.get("weights_bytes") is not None else "—"}</td></tr>', ROW))
    doc.table(head, rows, head_h=10, cls=' class="fx1"')
    doc.add('<p class="note">Khối lượng việc đọc từ telemetry (bản build lab có <code>PP_T7_TELEMETRY</code>); — là chưa có.</p>', 6)


def page_sensitivity(doc, D, P, title, section):
    doc.begin(title, section)
    doc.add('<p class="note">Mỗi lưới một bản đồ nhiệt theo từng chỉ số. Ô: hiệu TB so với mốc; sắc xanh: tốt hơn, đỏ: xấu hơn, xám: trong dung sai, đậm dần theo bội của dung sai (1×, 2×, 4×). Viền đậm là cấu hình mặc định.</p>', 9)
    mk = lambda m: m["id"] + "|" + m["metric"]
    for f in (x for x in D["families"] if x.get("grid")):
        axes = list(f["grid"])
        if len(axes) == 2 and all(f["grid"][a] for a in axes):
            per_row = 6
            ms = P["metrics"]
            for i in range(0, len(ms), per_row):
                cells = "".join(f'<div class="hm"><div class="t">{esc(m["id"].replace("PP-SWR-", ""))} {esc(m["metric"][:40])}</div>{heatmap(D, P, f, axes, m)}</div>' for m in ms[i:i + per_row])
                head = f'<h3>{esc(f["variant"])} <span class="muted">(hàng: {esc(axes[0])}; cột: {esc(axes[1])})</span></h3>' if i == 0 else ""
                doc.add(f'{head}<div class="grid6">{cells}</div>', 49 + (8 if i == 0 else 0))
        elif len(axes) == 1:
            levels = f["grid"][axes[0]]
            doc.add(f'<h3>{esc(f["variant"])} <span class="muted">(trục {esc(axes[0])})</span></h3>', 8)
            head = "<th>Chỉ số</th>" + "".join(f"<th>{esc(axes[0])} = {esc(fmt(v) if not isinstance(v, list) else '/'.join(map(fmt, v)))}</th>" for v in levels)
            rows = []
            for m in P["metrics"]:
                tds = ""
                for lv in levels:
                    name = next((n for n in f["configs"] if (D["configs"].get(n) or {}).get("values", {}).get(axes[0]) is not None
                                 and abs(float(D["configs"][n]["values"][axes[0]]) - float(lv)) < 1e-12), None)
                    tds += f'<td>{chip_plain(((P["configs"].get(name) or {}).get("cells") or {}).get(mk(m))) if name else "—"}</td>'
                rows.append((f'<tr><td>{esc(m["id"].replace("PP-SWR-", ""))} {esc(m["metric"][:60])}</td>{tds}</tr>', ROW))
            doc.table(head, rows, head_h=6)


def page_qp(doc, D, P, title, section):
    rows = P.get("qp_iterations") or []
    doc.begin(title, section)
    doc.add(f'<p class="note">Lệch output vòng hở 0–1 s so với <code>{esc(D["reference"])}</code> theo p99 thời gian tính, mỗi điểm một cấu hình (nhãn: số vòng). '
            'Pareto: điểm lớn, không cấu hình nào vừa nhanh hơn vừa lệch ít hơn. Mỗi họ một màu (chú giải phía trên); `qp_jerk_admm_mlp_weights` chỉ có một điểm nên không vẽ, xem bảng.</p>', 11)
    doc.add(scatter(rows), 68)
    head = "<th>Cấu hình</th><th class=num>Số vòng</th><th class=num>p99 [ms]</th><th class=num>Lệch lớn nhất [m]</th><th class=num>Lệch TB [m]</th><th>Pareto</th>"
    body = [(f'<tr><td class="name">{nm(r["config"])}</td><td class="num">{r["iterations"]}</td><td class="num">{fmt(r.get("p99_median_ms"))}</td>'
             f'<td class="num">{fmt(r.get("diff_max_m"))}</td><td class="num">{fmt(r.get("diff_mean_m"))}</td><td>{"có" if r.get("pareto") else ""}</td></tr>', 4.55) for r in rows]
    doc.table(head, body, head_h=6)


def page_hyp(doc, D, part, title, section):
    H = D["hypotheses"].get(part) or {}
    doc.begin(title, section)
    doc.add('<p class="note">Tiêu chí khóa trong plan.yaml trước lần chạy --record. Thuật toán có lưới được kiểm ở từng cấu hình và báo "đạt ở x/n cấu hình"; không chọn riêng cấu hình đạt.</p>', 7)
    word = lambda v: "✓ đạt" if v is True else "✗ không đạt" if v is False else "thiếu dữ liệu"
    for hid, hy in H.items():
        summ = "; ".join(f'{esc(v)}: đạt ở {s["held"]}/{s["configs"]} cấu hình' + (f' (đo được {s["measured"]})' if s["measured"] < s["configs"] else "") for v, s in hy["summary"].items())
        doc.add(f'<h3>{esc(hid)} <span class="muted">({esc(hy["kind"])})</span></h3><p class="note">{summ}</p>', 12)
        rows = []
        for r in hy["rows"]:
            vals = r.get("values") or {}
            plain = ", ".join(f"{esc(k)} {fmt(v)}" for k, v in vals.items() if not isinstance(v, dict))
            cells = " ".join(f'{esc(k.split("|")[0].replace("PP-SWR-", ""))} {chip_plain(v)}' for k, v in vals.items() if isinstance(v, dict) and "label" in v)
            rows.append((f'<tr><td class="name">{nm(r.get("config") or "—")}</td><td>{esc(r.get("against") or "")}</td><td>{word(r.get("holds"))}</td><td>{cells} {plain}</td></tr>', ROW))
        doc.table("<th>Cấu hình</th><th>So với</th><th>Kết quả</th><th>Số liệu</th>", rows, head_h=6)


def page_flags(doc, D, P, title, section):
    doc.begin(title, section)
    doc.add('<p class="note">Cờ không loại cấu hình nào; nó cảnh báo ô trông tốt có thể đang hiểu sai. Lượt có cờ B0 hay lỗi chạy không vào hiệu ghép cặp.</p>', 7)
    rows = []
    for n in default_names(D, P):
        f = P["configs"][n].get("flags") or {}
        nf = "<br>".join(f'{esc(x["case"])} s{x["seed"]}: {esc(", ".join(x["failed"]))}' for x in f.get("new_failures", [])[:10])
        if len(f.get("new_failures", [])) > 10:
            nf += f'<br>… {len(f["new_failures"]) - 10} lượt nữa'
        ll = "<br>".join(f'{esc(x["case"])} s{x["seed"]}: −{x["lost"]} chu kỳ' for x in f.get("lcc_lost", [])[:6])
        rows.append((f'<tr><td class="name"><b>{nm(n)}</b></td><td>{flags(f) or "<span class=muted>không</span>"}</td><td>{nf or "—"}</td><td>{ll or "—"}</td></tr>',
                     ROW + 3.5 * max(1, min(len(f.get("new_failures", [])), 10), min(len(f.get("lcc_lost", [])), 6)) + 2 if (nf or ll) else ROW))
    doc.table("<th>Cấu hình</th><th>Cờ</th><th>Lượt trượt mới</th><th>LCC lái ít hơn mốc</th>", rows, head_h=6)
    shared = (P["configs"].get(D["baseline"]) or {}).get("flags", {}).get("shared_failures") or {}
    doc.add(f'<p class="note">Lỗi chung (mốc cũng trượt): {esc(", ".join(f"{k} ({v})" for k, v in shared.items()) or "không")}.</p>', 6)


def page_trust(doc, D, P, title, section):
    doc.begin(title, section)
    doc.add('<p class="note">Vòng hở: chỉ so chu kỳ có digest đầu vào trùng nhau. "Path khác mốc": tỉ lệ chu kỳ lệch 0–1 s vượt 0,005 m (generator có thực sự hoạt động không). Chênh tuning–test: nhãn đổi chiều, hoặc tốt hơn ở tuning mà chỉ trong dung sai ở test (dấu hiệu quá khớp khi dò tay).</p>', 11)
    head = ("<th>Cấu hình</th><th class=num>Chu kỳ so được</th><th class=num>Digest lệch</th><th class=num>Chỉ một bên có path</th><th class=num>Path khác mốc</th>"
            "<th class=num>Chỉ số ít dữ liệu</th><th>Đổi chiều tuning–test</th><th>Tốt hơn ở tuning, trong dung sai ở test</th>")
    rows = []
    for n in default_names(D, P):
        c = P["configs"][n].get("credibility") or {}
        g = c.get("tuning_test_gap")
        rows.append((f'<tr><td class="name"><b>{nm(n)}</b></td><td class="num">{c.get("compared_cycles", "—")}</td><td class="num">{c.get("digest_mismatch", "—")}</td>'
                     f'<td class="num">{c.get("valid_mismatch", "—")}</td><td class="num">{pct(c.get("differs_share"))}</td><td class="num">{c.get("few_data_metrics", "—")}</td>'
                     f'<td>{esc(", ".join(g["flipped"]) or "không") if g else "—"}</td><td>{esc(", ".join(g["faded"]) or "không") if g else "—"}</td></tr>', ROW2))
    doc.table(head, rows, head_h=10, cls=' class="fx1"')
    rep = list((D.get("repeats") or {}).items())
    if rep:
        doc.add('<p class="note">Cấu hình chạy lại ở nhiều lần: ' + "; ".join(f'{esc(k)} {"trùng giá trị" if all(v) else "<b>KHÁC giá trị</b>"}' for k, v in rep) + ".</p>", 6)


def page_diag(doc, D, P, title, section):
    doc.begin(title, section)
    doc.add('<p class="note"><b>Không so với mốc.</b> Chỉ để giải thích vì sao.</p>', 6)
    head = ("<th>Cấu hình</th><th class=num>Jerk path lớn nhất (003)</th><th class=num>Chu kỳ gần trần a_y/jerk TB / max</th><th class=num>a_y xe &gt; aysmax + 0,3 lâu nhất [s]</th>"
            "<th class=num>Lượt ngoài R79 5.6.2.1.1</th><th class=num>PP-SWR-125 max</th><th class=num>Telemetry: fallback TB</th><th class=num>T10 sửa path max [m]</th>"
            "<th class=num>Residual p99</th><th class=num>Slack max</th>")
    rows = []
    for n in default_names(D, P):
        d = P["configs"][n].get("diagnostics") or {}
        t = d.get("telemetry") or {}
        rows.append((f'<tr><td class="name"><b>{nm(n)}</b></td><td class="num">{fmt(d.get("path_jerk_max"))}</td><td class="num">{pct(d.get("near_limit_share_mean"))} / {pct(d.get("near_limit_share_max"))}</td>'
                     f'<td class="num">{fmt(d.get("ay_over_sustained_max_s"))}</td><td class="num">{d.get("r79_outside_runs", "—")}</td><td class="num">{fmt(d.get("swr125_max"))}</td>'
                     f'<td class="num">{pct(t.get("fallback_share_mean"))}</td><td class="num">{fmt(t.get("t10_change_max_m"))}</td><td class="num">{fmt(t.get("residual_p99"))}</td><td class="num">{fmt(t.get("slack_max"))}</td></tr>', ROW))
    doc.table(head, rows, head_h=12, cls=' class="fx1"')


def page_full_grid(doc, D, P, title, section):
    ms = P["metrics"]
    mk = lambda m: m["id"] + "|" + m["metric"]
    doc.begin(title, section)
    doc.add('<p class="note">Mọi cấu hình của lưới calibration, so với mốc. Cùng cách đọc như trang Tổng quan.</p>', 6)
    rows = []
    for n in all_names(D, P):
        r = P["configs"][n]
        rows.append((f'<tr><td class="name">{"<b>" if (D["configs"].get(n) or {}).get("default") else ""}{nm(n)}{"</b>" if (D["configs"].get(n) or {}).get("default") else ""}</td><td>{flags(r.get("flags"))}</td>'
                     + "".join(f'<td>{"<span class=muted>mốc</span>" if n == D["baseline"] else chip_plain(r["cells"].get(mk(m)))}</td>' for m in ms) + "</tr>",
                     max(6.2, 3.2 * -(-len(n) // 27) + 1.6)))
    doc.table(f'<th>Cấu hình (đậm: mặc định)</th><th>Cờ</th>{metric_head(ms)}', rows, head_h=22, cls=' class="fx"')
    doc.add(legend(), 6)


def short_version(v: str) -> str:
    import re
    m = re.search(r"commit (\w+)", v or "")
    t = re.search(r"t7_src (\w+)", v or "")
    if not m:
        return v or "—"
    return f"{m.group(1)[:8]}" + (f" / t7_src {t.group(1)[:8]}" if t else "")


def page_provenance(doc, D, title, section):
    doc.begin(title, section)
    doc.add(f'<p class="note">Plan <code>{esc(D["plan"]["path"])}</code> sha256 {esc((D["plan"].get("sha256") or "")[:12])}, khóa {esc(D["plan"].get("locked") or "chưa")}. '
            'Run ID trỏ tới <code>research/runs/&lt;run&gt;/summary.md</code>.</p>', 6)
    runs = {}
    for part, v in D["parts"].items():
        for n, r in v["configs"].items():
            runs.setdefault(r.get("run_id") or "nháp", set()).add(part)
    doc.add("<table><thead><tr><th>Run ID</th><th>Phần</th></tr></thead><tbody>" + "".join(f"<tr><td>{esc(k)}</td><td>{esc(', '.join(sorted(v)))}</td></tr>" for k, v in runs.items()) + "</tbody></table>", 6 + 5 * len(runs))
    part = "test" if "test" in D["parts"] else next(iter(D["parts"]), None)
    if part is None:
        return
    items = list(D["parts"][part]["configs"].items())
    per = 18

    def tab(chunk):
        return ("<div><table><thead><tr><th>Cấu hình</th><th>Bản build</th><th>Hash calibration</th></tr></thead><tbody>"
                + "".join(f'<tr><td class="name">{nm(n)}</td><td>{esc(short_version(r.get("pp_version")))}</td><td>{esc(r.get("calibration_hash") or "—")}</td></tr>' for n, r in chunk) + "</tbody></table></div>")
    doc.add(f'<h3>Phần {esc(part)}</h3>', 8)
    for i in range(0, len(items), 2 * per):
        right = items[i + per:i + 2 * per]
        doc.add(f'<div class="two">{tab(items[i:i + per])}{tab(right) if right else "<div></div>"}</div>', 4.5 + 7.2 * per)


# ---------- ghép ----------

def page(data: dict) -> str:
    doc = Doc(data)
    parts = data["parts"]
    if not parts:
        return shell(doc.render())
    main = "test" if "test" in parts else next(iter(parts))
    P = parts[main]
    sec = f"Phần {main}: kết quả chính"
    doc.begin(sec, sec)
    doc.add(f'<p class="note">Các trang dưới đây dùng phần <b>{esc(main)}</b> (seed của phần này không dùng khi chỉnh). Phần còn lại ở phụ lục.</p>', 8)
    doc.pages.pop()   # trang mục lục phần chỉ là dấu mốc cho mục lục, không tạo trang rỗng
    page_overview(doc, data, P, "Tổng quan", "Tổng quan")
    page_group(doc, data, P, "An toàn", "An toàn", "An toàn", True)
    page_group(doc, data, P, "Bám làn và cảm nhận người lái", "Bám làn và cảm nhận", "Bám làn và cảm nhận người lái", False)
    page_case_groups(doc, data, P, "Theo nhóm ca", "Theo nhóm ca")
    page_flex(doc, data, P, "Flexibility: độ chênh giữa các profile", "Flexibility")
    page_cost(doc, data, P, "Chi phí phần cứng", "Chi phí phần cứng")
    page_sensitivity(doc, data, P, "Độ nhạy calibration", "Độ nhạy calibration")
    page_qp(doc, data, P, "Số vòng QP: lệch so với nghiệm tham chiếu", "Số vòng QP")
    page_hyp(doc, data, main, "Giả thuyết", "Giả thuyết")
    page_flags(doc, data, P, "Cờ cảnh báo", "Cờ cảnh báo")
    page_trust(doc, data, P, "Độ tin của kết quả", "Độ tin")
    page_diag(doc, data, P, "Chẩn đoán", "Chẩn đoán")
    other = [p for p in parts if p != main]
    doc.begin("Phụ lục A: cả lưới calibration", "Phụ lục A: cả lưới calibration")
    doc.pages.pop()
    page_full_grid(doc, data, P, f"Phụ lục A: cả lưới calibration, phần {main}", "Phụ lục A: cả lưới calibration")
    for p in other:
        page_overview(doc, data, parts[p], f"Phụ lục B: phần {p}, tổng quan", f"Phụ lục B: phần {p}")
        page_hyp(doc, data, p, f"Phụ lục B: phần {p}, giả thuyết", f"Phụ lục B: phần {p}, giả thuyết")
    page_provenance(doc, data, "Phụ lục C: bản build và run ID", "Phụ lục C: bản build và run ID")
    return shell(doc.render())


def shell(body: str) -> str:
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>So sánh generator T7 của LCC planner</title>
<style>{STYLE}</style>
</head>
<body>
{body}
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the static paged T7 generator report from techniques.json")
    parser.add_argument("--data", type=Path, default=HERE / "techniques.json")
    parser.add_argument("--out", type=Path, default=HERE / "index.html")
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    args.out.write_text(page(data), encoding="utf-8")
    print(f"{args.out} ({'draft' if data.get('draft', True) else 'official'})")


if __name__ == "__main__":
    main()
