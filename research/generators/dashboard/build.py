"""Sinh báo cáo so sánh generator T7 (PP-TS-031) từ techniques.json: 10 trang A4 ngang như một file PDF.

Chỉ hiện giá trị tuyệt đối của từng thuật toán, không so với mốc, không có hạng hay điểm tổng. Mỗi trang một ý:
biểu đồ chấm (Cleveland) trên thang chung, hàng sắp theo giá trị tăng dần, một màu dữ liệu, vạch đỏ chỉ giới hạn.
Một file HTML tĩnh, không script, không nút, không tải gì từ mạng; in A4 ngang hoặc "Lưu thành PDF" cho cùng bố cục.
Dữ liệu nháp (plan chưa khóa, chạy không --record) thì mọi trang có nhãn "NHÁP". Bảng số đầy đủ ở trang cuối.

    python3 -m eval.campaign PP-TS-031          # ghi dashboard/techniques.json
    python3 research/generators/dashboard/build.py
"""

import argparse
import html
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
U = 0.25                 # 1 đơn vị SVG = 0,25 mm
ROW = 24                 # chiều cao hàng của biểu đồ chấm [đơn vị]
LABEL_W = 200
PLOT_W = 300

STYLE = r"""
@page{size:297mm 210mm;margin:0}
:root{color-scheme:light;--page:#e9e8e4;--paper:#fff;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--band:#cde2fb;--crit:#d03b3b;--draft:#fff3cd;--warn:#fab219}
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html{background:var(--page)}
body{margin:0;color:var(--ink);font:9pt/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}
.page{width:297mm;height:210mm;margin:8mm auto;padding:11mm 14mm 9mm;background:var(--paper);position:relative;
overflow:hidden;box-shadow:0 1px 6px rgba(0,0,0,.18);display:flex;flex-direction:column;break-after:page;page-break-after:always}
@media print{html{background:#fff}.page{margin:0;box-shadow:none}}
.ph{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2mm}
.ph h2{font-size:16pt;margin:0;font-weight:650}.ph .meta{color:var(--muted);font-size:7.5pt;text-align:right}
.read{color:var(--ink2);font-size:9pt;margin:0 0 4mm;max-width:235mm}
.body{flex:1;min-height:0}
.pf{display:flex;justify-content:space-between;color:var(--muted);font-size:7pt;padding-top:1.5mm;margin-top:2mm}
.row{display:flex;gap:6mm;align-items:flex-start}
figure{margin:0}
figcaption h3{font-size:10.5pt;margin:0 0 .6mm;font-weight:650}
figcaption .sub{color:var(--ink2);font-size:8pt;margin:0 0 1.5mm}
.note{color:var(--muted);font-size:7.5pt;margin:1mm 0 0}
svg{display:block;overflow:visible}
svg text{font-family:inherit;fill:var(--ink2)}
svg .lbl{fill:var(--ink)}
.legend{display:flex;gap:5mm;flex-wrap:wrap;color:var(--ink2);font-size:8pt;margin:0 0 3mm;align-items:center}
.legend span{display:inline-flex;align-items:center;gap:1.5mm}
.draft{background:var(--draft);border:1px solid var(--warn);padding:1.2mm 3mm;margin-bottom:3mm;font-weight:600;font-size:8pt}
.cover h1{font-size:25pt;margin:12mm 0 3mm;line-height:1.15;font-weight:650}
.cover .lead{font-size:11pt;color:var(--ink2);max-width:215mm;margin:0 0 7mm}
table{border-collapse:collapse;font-variant-numeric:tabular-nums;width:100%}
th,td{padding:.9mm 1.5mm;text-align:left;vertical-align:top;border-bottom:1px solid var(--grid)}
th{color:var(--ink2);font-weight:600;font-size:7pt;border-bottom:1px solid var(--axis)}
td.num,th.num{text-align:right}
.alg td{font-size:9pt;padding:1.2mm 1.5mm}.alg td:first-child{font-weight:600;white-space:nowrap}
.fail th,.fail td{font-size:8pt}.fail td.c{text-align:center;font-weight:600}
.app th,.app td{font-size:6.8pt;padding:.7mm 1.1mm}.app th{vertical-align:bottom}
.toc{display:flex;flex-wrap:wrap;gap:1mm 6mm;font-size:8.5pt;color:var(--ink2);margin-top:6mm}
.toc b{color:var(--ink);font-weight:650}
.muted{color:var(--muted)}
code{font-family:ui-monospace,Menlo,monospace;font-size:.92em}
"""


# ---------- định dạng ----------

def esc(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def fmt(v, d=3) -> str:
    if v is None or isinstance(v, bool) or not isinstance(v, (int, float)) or v != v or abs(v) == float("inf"):
        return "—"
    if abs(v) >= 1000:
        return f"{v:.0f}"
    r = float(f"{v:.{d}g}")
    s = f"{r:.10f}".rstrip("0").rstrip(".")
    return (s if s not in ("-0", "") else "0").replace(".", ",")


def nice_ticks(lo: float, hi: float, n: int = 4) -> list[float]:
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / n
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    v, out = math.ceil(lo / step - 1e-9) * step, []
    while v <= hi + step * 1e-9:
        out.append(round(v, 12))
        v += step
    return out


# ---------- dữ liệu ----------

def families(D: dict) -> list[dict]:
    return [f for f in D.get("families", []) if f["compared"]]


def algorithms(D: dict, P: dict) -> list[str]:
    return [f["default"] for f in families(D) if f["default"] in P["configs"]]


def metric_key(P: dict, mid: str, contains: str = "") -> str | None:
    return next((f"{m['id']}|{m['metric']}" for m in P["metrics"] if m["id"] == mid and contains in m["metric"]), None)


def absval(P: dict, name: str, key: str | None, field: str = "mean"):
    return ((P["configs"].get(name) or {}).get("absolute") or {}).get(key, {}).get(field) if key else None


def short_metric(mid: str, text: str) -> str:
    t = text
    if "RMS của path" in t:
        return "Jerk path (RMS)"
    if "lớn nhất của path" in t:
        return "Jerk path (lớn nhất)"
    if "Tốc độ quay" in t:
        return "Tốc độ quay vô lăng"
    return {"PP-SWR-057": "Khoảng hở tới xe lớn", "PP-SWR-070": "DLC nhỏ nhất", "PP-SWR-050": "Lệch tâm làn (path)",
            "PP-SWR-053": "Thời gian về giữa", "PP-SWR-059": "Thời gian trả về", "PP-SWR-002": "a_y thêm khi về giữa",
            "PP-SWR-068": "a_y lớn nhất (xe)", "PP-SWR-069": "Jerk lớn nhất (xe)", "PP-SWR-016": "p99 thời gian tính"}.get(mid, t[:24])


# ---------- biểu đồ ----------

def axis_range(means: list[float], worsts: list[float], limit: float | None = None, floor: float | None = None):
    span = (max(means) - min(means)) or abs(max(means)) or 1.0
    lo, hi = min(means), max(means)
    near = [w for w in worsts if w is not None and lo - 1.5 * span <= w <= hi + 1.5 * span]
    extra = ([limit] if limit is not None else [])
    lo, hi = min([lo] + near + extra), max([hi] + near + extra)
    pad = (hi - lo) * .08 or 1.0
    lo, hi = lo - pad, hi + pad
    if floor is not None and lo < floor:
        lo = floor
    return lo, hi


def dotplot(rows: list[dict], lo: float, hi: float, *, unit: str = "", limit: float | None = None, limit_label: str = "",
            labels: bool = True, plot_w: int = PLOT_W, markers: bool = True) -> tuple[str, int, float | None]:
    """rows: {name, mean, worst}. Trả (svg, số hàng có ca xấu nhất ngoài khung, giá trị ngoài khung xa nhất)."""
    L = LABEL_W if labels else 8
    W, top = plot_w, 20
    H = top + ROW * len(rows) + 28
    total = L + W + 14
    x = lambda v: L + (min(max(v, lo), hi) - lo) / (hi - lo) * W
    s = [f'<svg width="{total * U:.1f}mm" height="{H * U:.1f}mm" viewBox="0 0 {total} {H}" role="img">']
    for t in nice_ticks(lo, hi):
        s.append(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top - 4}" y2="{top + ROW * len(rows)}" stroke="#eeede9" stroke-width="1"/>')
        s.append(f'<text x="{x(t):.1f}" y="{top + ROW * len(rows) + 14}" text-anchor="middle" font-size="9.5">{fmt(t)}</text>')
    s.append(f'<line x1="{L}" x2="{L + W}" y1="{top + ROW * len(rows)}" y2="{top + ROW * len(rows)}" stroke="var(--axis)"/>')
    if unit:
        s.append(f'<text x="{L + W}" y="{top + ROW * len(rows) + 26}" text-anchor="end" font-size="9">{esc(unit)}</text>')
    if limit is not None and lo <= limit <= hi:
        s.append(f'<line x1="{x(limit):.1f}" x2="{x(limit):.1f}" y1="{top - 8}" y2="{top + ROW * len(rows)}" stroke="var(--crit)" stroke-width="1.4" stroke-dasharray="4 3"/>')
        s.append(f'<text x="{x(limit) + 4:.1f}" y="{top - 9}" font-size="9" style="fill:var(--crit)">{esc(limit_label)}</text>')
    clipped, extreme = 0, None
    for i, r in enumerate(rows):
        y = top + ROW * i + ROW / 2
        s.append(f'<line x1="{L}" x2="{L + W}" y1="{y:.1f}" y2="{y:.1f}" stroke="#f0efec" stroke-width="1"/>')
        if labels:
            s.append(f'<text class="lbl" x="{L - 8}" y="{y + 3.5:.1f}" text-anchor="end" font-size="10.5">{esc(r["name"])}</text>')
        w = r.get("worst")
        if markers and w is not None:
            if lo <= w <= hi:
                s.append(f'<circle cx="{x(w):.1f}" cy="{y:.1f}" r="4" fill="#fff" stroke="var(--s1)" stroke-width="1.5"/>')
            else:
                clipped += 1
                extreme = w if extreme is None or abs(w - r["mean"]) > abs(extreme - r["mean"]) else extreme
                edge, arrow = (L + 1, "◂") if w < lo else (L + W - 1, "▸")
                s.append(f'<text x="{edge}" y="{y + 3.5:.1f}" font-size="11" text-anchor="{"start" if w < lo else "end"}" style="fill:var(--s1)">{arrow}</text>')
        s.append(f'<circle cx="{x(r["mean"]):.1f}" cy="{y:.1f}" r="4.6" fill="var(--s1)" stroke="#fff" stroke-width="1.6"/>')
    return "".join(s) + "</svg>", clipped, extreme


def dumbbell(rows: list[dict], lo: float, hi: float, profiles: list[str], *, unit: str = "") -> str:
    """rows: {name, values{profile: v}}; mỗi hàng các chấm theo profile nối bằng một đoạn."""
    L, W, top = LABEL_W, PLOT_W, 20
    H = top + ROW * len(rows) + 28
    total = L + W + 14
    x = lambda v: L + (min(max(v, lo), hi) - lo) / (hi - lo) * W
    shape = {p: i for i, p in enumerate(profiles)}

    def mark(cx, cy, k):
        if k == 0:
            return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.4" fill="var(--s1)" stroke="#fff" stroke-width="1.5"/>'
        if k == 1:
            return f'<rect x="{cx - 4:.1f}" y="{cy - 4:.1f}" width="8" height="8" fill="var(--s1)" stroke="#fff" stroke-width="1.5"/>'
        return f'<path d="M{cx:.1f} {cy - 5:.1f} L{cx + 4.8:.1f} {cy + 3.6:.1f} L{cx - 4.8:.1f} {cy + 3.6:.1f} Z" fill="var(--s1)" stroke="#fff" stroke-width="1.3"/>'
    s = [f'<svg width="{total * U:.1f}mm" height="{H * U:.1f}mm" viewBox="0 0 {total} {H}" role="img">']
    for t in nice_ticks(lo, hi):
        s.append(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top - 4}" y2="{top + ROW * len(rows)}" stroke="#eeede9"/>'
                 f'<text x="{x(t):.1f}" y="{top + ROW * len(rows) + 14}" text-anchor="middle" font-size="9.5">{fmt(t)}</text>')
    s.append(f'<line x1="{L}" x2="{L + W}" y1="{top + ROW * len(rows)}" y2="{top + ROW * len(rows)}" stroke="var(--axis)"/>')
    if unit:
        s.append(f'<text x="{L + W}" y="{top + ROW * len(rows) + 26}" text-anchor="end" font-size="9">{esc(unit)}</text>')
    for i, r in enumerate(rows):
        y = top + ROW * i + ROW / 2
        vals = [(p, r["values"][p]) for p in profiles if r["values"].get(p) is not None]
        s.append(f'<text class="lbl" x="{L - 8}" y="{y + 3.5:.1f}" text-anchor="end" font-size="10.5">{esc(r["name"])}</text>')
        if len(vals) >= 2:
            a, b = min(v for _, v in vals), max(v for _, v in vals)
            s.append(f'<line x1="{x(a):.1f}" x2="{x(b):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--s1)" stroke-width="2" stroke-opacity=".45"/>')
        for p, v in vals:
            s.append(mark(x(v), y, shape[p]))
    return "".join(s) + "</svg>"


def range_bars(rows: list[dict], lo: float, hi: float, *, unit: str = "") -> str:
    """rows: {name, lo, hi, default}: thanh min–max qua lưới calibration, chấm là cấu hình mặc định."""
    L, W, top, rh = LABEL_W, PLOT_W, 14, 34
    H = top + rh * len(rows) + 28
    total = L + W + 14
    x = lambda v: L + (v - lo) / (hi - lo) * W
    s = [f'<svg width="{total * U:.1f}mm" height="{H * U:.1f}mm" viewBox="0 0 {total} {H}" role="img">']
    for t in nice_ticks(lo, hi):
        s.append(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top - 4}" y2="{top + rh * len(rows)}" stroke="#eeede9"/>'
                 f'<text x="{x(t):.1f}" y="{top + rh * len(rows) + 14}" text-anchor="middle" font-size="9.5">{fmt(t)}</text>')
    s.append(f'<line x1="{L}" x2="{L + W}" y1="{top + rh * len(rows)}" y2="{top + rh * len(rows)}" stroke="var(--axis)"/>')
    if unit:
        s.append(f'<text x="{L + W}" y="{top + rh * len(rows) + 26}" text-anchor="end" font-size="9">{esc(unit)}</text>')
    for i, r in enumerate(rows):
        y = top + rh * i + rh / 2
        s.append(f'<text class="lbl" x="{L - 8}" y="{y + 3.5:.1f}" text-anchor="end" font-size="10.5">{esc(r["name"])}</text>')
        w = max(x(r["hi"]) - x(r["lo"]), 3)
        s.append(f'<rect x="{x(r["lo"]):.1f}" y="{y - 5:.1f}" width="{w:.1f}" height="10" rx="3" fill="var(--band)"/>')
        if r.get("default") is not None:
            s.append(f'<circle cx="{x(r["default"]):.1f}" cy="{y:.1f}" r="4.6" fill="var(--s1)" stroke="#fff" stroke-width="1.6"/>')
    return "".join(s) + "</svg>"


def scatter(rows: list[dict]) -> str:
    pts = [r for r in rows if r.get("p99_median_ms") is not None and r.get("diff_max_m") is not None]
    many = {f for f in {p["series"] for p in pts} if sum(1 for p in pts if p["series"] == f) >= 2}
    pts = [p for p in pts if p["series"] in many]
    if not pts:
        return '<p class="note">Chưa có điểm (cần lượt vòng hở và nghiệm tham chiếu).</p>'
    fams = list(dict.fromkeys(p["series"] for p in pts))[:3]
    col = lambda f: ["var(--s1)", "var(--s2)", "var(--s3)"][fams.index(f)] if f in fams else "var(--muted)"
    W, H, L, B, T, R = 1000, 520, 70, 44, 14, 20
    x1 = max(p["p99_median_ms"] for p in pts) * 1.1
    y1 = max(p["diff_max_m"] for p in pts) * 1.12
    X = lambda v: L + (W - L - R) * v / x1
    Y = lambda v: H - B - (H - B - T) * v / y1
    s = ['<div class="legend">' + "".join(f'<span><svg width="3mm" height="3mm" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4.2" fill="{col(f)}"/></svg>{esc(f)}</span>' for f in fams)
         + '<span><svg width="3.6mm" height="3.6mm" viewBox="0 0 12 12"><circle cx="6" cy="6" r="5.4" fill="#898781"/></svg>điểm to: không điểm nào vừa nhanh hơn vừa chính xác hơn</span></div>',
         f'<svg width="255mm" viewBox="0 0 {W} {H}" role="img" aria-label="độ lệch theo p99">']
    for i in range(5):
        yv, xv = y1 * i / 4, x1 * i / 4
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="#eeede9"/><text x="{L - 8}" y="{Y(yv) + 4:.1f}" text-anchor="end" font-size="12">{fmt(yv, 2)}</text>')
        s.append(f'<text x="{X(xv):.1f}" y="{H - B + 18}" text-anchor="middle" font-size="12">{fmt(xv, 2)}</text>')
    s.append(f'<line x1="{L}" x2="{W - R}" y1="{H - B}" y2="{H - B}" stroke="var(--axis)"/>'
             f'<text x="{(L + W) / 2}" y="{H - 8}" text-anchor="middle" font-size="12">p99 thời gian tính [ms]</text>'
             f'<text x="16" y="{(H - B) / 2}" transform="rotate(-90 16 {(H - B) / 2})" text-anchor="middle" font-size="12">lệch lớn nhất so với nghiệm 1000 vòng [m]</text>')
    if 0.005 < y1:
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(0.005):.1f}" y2="{Y(0.005):.1f}" stroke="var(--muted)" stroke-dasharray="2 4"/>'
                 f'<text x="{W - R}" y="{Y(0.005) - 5:.1f}" text-anchor="end" font-size="11">5 mm (dung sai PP-SWR-050)</text>')
    for f in fams:
        line = sorted((p for p in pts if p["series"] == f), key=lambda p: p["iterations"])
        s.append(f'<polyline fill="none" stroke="{col(f)}" stroke-width="2" stroke-linejoin="round" points="{" ".join(f"{X(p["p99_median_ms"]):.1f},{Y(p["diff_max_m"]):.1f}" for p in line)}"/>')
    for p in pts:
        s.append(f'<circle cx="{X(p["p99_median_ms"]):.1f}" cy="{Y(p["diff_max_m"]):.1f}" r="{7 if p["pareto"] else 4.6}" fill="{col(p["series"])}" stroke="#fff" stroke-width="2"/>'
                 f'<text x="{X(p["p99_median_ms"]) + 9:.1f}" y="{Y(p["diff_max_m"]) - 8:.1f}" font-size="12" style="fill:var(--ink)">{p["iterations"]}</text>')
    return "".join(s) + "</svg>"


def figure(title: str, sub: str, svg: str, note: str = "") -> str:
    return (f'<figure><figcaption><h3>{esc(title)}</h3><p class="sub">{sub}</p></figcaption>{svg}'
            f'{f"<p class=note>{note}</p>" if note else ""}</figure>')


LEG_DOT = ('<span><svg width="3.4mm" height="3.4mm" viewBox="0 0 12 12"><circle cx="6" cy="6" r="5" fill="#2a78d6"/></svg>trung bình trên bộ kiểm</span>'
           '<span><svg width="3.4mm" height="3.4mm" viewBox="0 0 12 12"><circle cx="6" cy="6" r="4.4" fill="#fff" stroke="#2a78d6" stroke-width="1.6"/></svg>lượt xấu nhất</span>')


def legend(*extra: str) -> str:
    return '<div class="legend">' + LEG_DOT + "".join(extra) + "<span>hàng sắp theo giá trị tăng dần, không phải xếp hạng</span></div>"


def dot_figure(D, P, key, names, title, sub, unit, *, limit=None, limit_label="", floor=None):
    """Một biểu đồ chấm cho một chỉ số, hàng sắp theo giá trị tăng dần."""
    rows = []
    for n in names:
        m = absval(P, n, key)
        if m is not None:
            rows.append({"name": n, "mean": m, "worst": absval(P, n, key, "worst")})
    if not rows:
        return ""
    rows.sort(key=lambda r: r["mean"])
    lo, hi = axis_range([r["mean"] for r in rows], [r["worst"] for r in rows], limit, floor)
    svg, clipped, extreme = dotplot(rows, lo, hi, unit=unit, limit=limit, limit_label=limit_label)
    note = f"◂ ▸ ca xấu nhất nằm ngoài khung ở {clipped} hàng (xa nhất: {fmt(extreme)} {esc(unit)})." if clipped else ""
    return figure(title, sub, svg, note)


# ---------- trang ----------

class Pages:
    def __init__(self, D: dict):
        self.D = D
        self.items: list[tuple[str, str, str]] = []

    def add(self, title: str, read: str, body: str) -> None:
        self.items.append((title, read, body))

    def render(self, cover: str) -> str:
        n = len(self.items) + 1
        tag = " · NHÁP" if self.D.get("draft", True) else ""
        out = [cover.replace("@@N@@", str(n))]
        for k, (title, read, body) in enumerate(self.items, start=2):
            out.append(f'<section class="page"><div class="ph"><h2>{esc(title)}</h2><div class="meta">{esc(self.D["study"])}{tag}</div></div>'
                       f'<p class="read">{read}</p><div class="body">{body}</div>'
                       f'<div class="pf"><span>Lab chỉ mô tả, không chọn generator.</span><span>Trang {k} / {n}</span></div></section>')
        return "".join(out)


GROUPS = [
    ("quintic_duration", "Quintic theo thời lượng: bản đang giao"),
    ("qp_jerk_admm", "QP jerk giải bằng ADMM, 10 đến 150 vòng"),
    ("qp_jerk_admm_shift_warmstart", "QP, khởi tạo bằng nghiệm chu kỳ trước dịch theo thời gian"),
    ("qp_jerk_admm_mlp_warmstart", "QP, khởi tạo bằng mạng MLP dự đoán chuỗi jerk"),
    ("qp_jerk_admm_mlp_weights", "QP, trọng số do mạng MLP chọn theo tình huống"),
    ("quintic_tangent_point", "Quintic cộng hiệu chỉnh cắt cua theo tangent point"),
    ("quintic_ay_sampling", "Quintic cộng hiệu chỉnh chọn theo a_y và jerk dự báo"),
    ("mlp_jerk_direct", "MLP xuất thẳng chuỗi jerk, không có tầng tối ưu (đối chứng)"),
]


def cover(D: dict, toc: list[tuple[str, int]]) -> str:
    banner = ('<div class="draft">NHÁP: plan chưa khóa hoặc có lần chạy không phải --record trên cây sạch. Không trích số liệu này.</div>'
              if D.get("draft", True) else "")
    count = {}
    for f in families(D):
        g = re.sub(r"_it\d+$", "", f["variant"])
        g = g if any(g == k for k, _ in GROUPS) else f["variant"]
        count[g] = count.get(g, 0) + len(f["configs"])
    rows = "".join(f'<tr><td>{esc(k)}</td><td>{esc(d)}</td><td class="num">{count.get(k, "")}</td></tr>' for k, d in GROUPS)
    runs = sorted({r.get("run_id") for p in D["parts"].values() for r in p["configs"].values() if r.get("run_id")})
    plan = D.get("plan", {})
    toc_html = "".join(f"<span><b>{pg}</b> {esc(t)}</span>" for t, pg in toc)
    return (f'<section class="page cover"><div class="body">{banner}'
            f'<div class="note">{esc(D["study"])} · LCC planner, khối T7 sinh path</div>'
            f'<h1>Tám họ thuật toán sinh path, so ở năm khía cạnh</h1>'
            f'<p class="lead">An toàn, bám làn, độ êm, flexibility giữa các vehicle profile, và chi phí phần cứng. '
            f'Mỗi biểu đồ cho thấy giá trị của từng thuật toán, không so với thuật toán nào và không có điểm tổng.</p>'
            f'<table class="alg"><thead><tr><th>Họ thuật toán</th><th>Cách làm</th><th class="num">Số cấu hình</th></tr></thead><tbody>{rows}</tbody></table>'
            f'<div class="toc">{toc_html}</div></div>'
            f'<div class="pf"><span>Plan <code>{esc(plan.get("path"))}</code> sha256 {esc((plan.get("sha256") or "")[:12])}, khóa {esc(plan.get("locked") or "chưa")}. '
            f'Run: {esc(", ".join(runs) or "nháp")}</span><span>Trang 1 / @@N@@</span></div></section>')


def build_pages(D: dict, P: dict, pages: Pages) -> None:
    names = algorithms(D, P)
    two = lambda a, b: f'<div class="row">{a}{b}</div>'
    k070, k057 = metric_key(P, "PP-SWR-070"), metric_key(P, "PP-SWR-057")
    k050, k053 = metric_key(P, "PP-SWR-050"), metric_key(P, "PP-SWR-053")
    k068, k069 = metric_key(P, "PP-SWR-068"), metric_key(P, "PP-SWR-069")

    pages.add("An toàn: xe sát vạch làn và xe lớn đến đâu",
              "Mỗi chấm là một thuật toán ở cấu hình mặc định, đo trên bộ kiểm.",
              legend('<span><svg width="5mm" height="3mm" viewBox="0 0 20 12"><line x1="2" x2="18" y1="6" y2="6" stroke="#d03b3b" stroke-width="2" stroke-dasharray="4 3"/></svg>giới hạn</span>')
              + two(dot_figure(D, P, k070, names, "Xe lại gần vạch làn nhất là bao nhiêu mét?",
                               "DLC nhỏ nhất của xe ở hai phía, m. Càng lớn càng an toàn; dưới 0: bánh xe đã chạm vạch.", "m",
                               limit=0.0, limit_label="chạm vạch"),
                    dot_figure(D, P, k057, names, "Xe lại gần xe lớn nhất là bao nhiêu mét?",
                               "Khoảng hở ngang nhỏ nhất tới xe tải khi ngang hàng, m. Càng lớn càng an toàn.", "m")))
    pages.add("Bám làn: path lệch tâm làn bao nhiêu, về giữa mất bao lâu",
              "Mỗi chấm là một thuật toán ở cấu hình mặc định, đo trên bộ kiểm.",
              legend() + two(dot_figure(D, P, k050, names, "Path lệch tâm làn thật bao nhiêu?",
                                        "Lệch ngang lớn nhất của path trong 0–1 s, m. Càng nhỏ càng sát tâm.", "m", floor=0.0),
                             dot_figure(D, P, k053, names, "Đưa xe về giữa làn mất bao lâu?",
                                        "Thời gian tới khi lệch còn ≤ 0,1 m, giây. Càng nhỏ càng nhanh.", "giây", floor=0.0)))
    pages.add("Độ êm: người lái cảm nhận cua thế nào",
              "Mỗi chấm là một thuật toán ở cấu hình mặc định, đo trên chuyển động thật của xe.",
              legend() + two(dot_figure(D, P, k068, names, "Xe chịu gia tốc ngang lớn nhất bao nhiêu?",
                                        "a_y lớn nhất của xe khi LCC lái, m/s² (R79 Annex 8, 2.4). Càng nhỏ càng êm.", "m/s²", floor=0.0),
                             dot_figure(D, P, k069, names, "Xe bị giật ngang mạnh nhất bao nhiêu?",
                                        "Jerk ngang lớn nhất của xe khi LCC lái, m/s³. Càng nhỏ càng êm.", "m/s³", floor=0.0)))

    profiles = sorted({p for n in names for p in (((P["configs"][n].get("absolute") or {}).get(k070) or {}).get("by_profile") or {}) if p})

    def flex_fig(key, title, sub, unit):
        rows = [{"name": n, "values": (((P["configs"][n].get("absolute") or {}).get(key) or {}).get("by_profile") or {})} for n in names]
        rows = [r for r in rows if len([v for v in r["values"].values() if v is not None]) >= 2]
        if not rows:
            return ""
        rows.sort(key=lambda r: max(r["values"].values()) - min(r["values"].values()))
        vals = [v for r in rows for v in r["values"].values() if v is not None]
        lo, hi = axis_range(vals, [])
        return figure(title, sub, dumbbell(rows, lo, hi, profiles, unit=unit))
    mark = lambda k, svg: f'<span><svg width="3.6mm" height="3.6mm" viewBox="0 0 12 12">{svg}</svg>{esc(k)}</span>'
    shapes = ['<circle cx="6" cy="6" r="4.6" fill="#2a78d6"/>', '<rect x="2" y="2" width="8" height="8" fill="#2a78d6"/>', '<path d="M6 1 L11 10 L1 10 Z" fill="#2a78d6"/>']
    leg = ('<div class="legend">' + "".join(mark(p, shapes[i]) for i, p in enumerate(profiles[:3]))
           + "<span>hàng sắp theo độ chênh giữa profile tăng dần</span></div>")
    pages.add("Flexibility: kết quả thay đổi thế nào giữa các vehicle profile",
              "Cùng một bản build và một bộ calibration chạy trên mọi profile. Đoạn nối càng ngắn, thuật toán càng ít phụ thuộc vào xe.",
              leg + two(flex_fig(k070, "DLC nhỏ nhất theo profile", "m. Càng lớn càng an toàn.", "m"),
                        flex_fig(k068, "a_y lớn nhất của xe theo profile", "m/s². Càng nhỏ càng êm.", "m/s²")))

    cost = {n: P["configs"][n]["cost"] for n in names}
    order = sorted((n for n in names if cost[n].get("p99_median_ms") is not None), key=lambda n: cost[n]["p99_median_ms"])
    share = max((cost[n].get("p99_cycle_share") or 0) for n in order) if order else 0

    def cost_fig(field, title, sub, unit, scale=1.0, labels=False, plot_w=250):
        rows = [{"name": n, "mean": cost[n][field] / scale, "worst": None} for n in order if cost[n].get(field) is not None]
        if not rows:
            return ""
        lo, hi = axis_range([r["mean"] for r in rows], [], None, 0.0)
        svg, _, _ = dotplot(rows, lo, hi, unit=unit, labels=labels, plot_w=plot_w, markers=False)
        return figure(title, sub, svg)
    pages.add("Chi phí phần cứng: thời gian, RAM, flash",
              f"Thời gian đo trên laptop với 2 job, không chuyển thẳng sang ECU. Chu kỳ tính là 25 ms; ở p99 thuật toán nặng nhất dùng {fmt(100 * share, 2)} % chu kỳ. "
              "Phần cứng chọn theo trường hợp xấu nhất, nên càng nhẹ càng rẻ.",
              '<div class="legend"><span>mỗi chấm là một thuật toán; ba biểu đồ dùng chung thứ tự hàng, sắp theo p99 tăng dần</span></div>'
              + '<div class="row">' + cost_fig("p99_median_ms", "Thời gian tính", "p99 mỗi chu kỳ, ms", "ms", labels=True)
              + cost_fig("state_bytes", "Bộ nhớ state (RAM)", "KB", "KB", 1000.0) + cost_fig("library_bytes", "Thư viện (flash)", "KB", "KB", 1000.0) + "</div>")

    pages.add("Số vòng QP: bớt vòng thì kém chính xác đi bao nhiêu",
              "Độ lệch lớn nhất của path trong 0–1 s so với nghiệm hội tụ 1000 vòng, ở vòng hở. Càng gần góc dưới bên trái càng tốt: ít lệch và nhanh.",
              scatter(P.get("qp_iterations") or []))

    def sens_fig(key, title, sub, unit):
        rows = []
        for f in D["families"]:
            if not f.get("grid") or not f["compared"]:
                continue
            vals = [absval(P, n, key) for n in f["configs"]]
            vals = [v for v in vals if v is not None]
            if len(vals) >= 2:
                rows.append({"name": f["variant"], "lo": min(vals), "hi": max(vals), "default": absval(P, f["default"], key)})
        if not rows:
            return ""
        rows.sort(key=lambda r: r["hi"] - r["lo"])
        every = [v for v in (absval(P, n, key) for n in names) if v is not None]  # Trục phủ cả khác biệt giữa các thuật toán.
        lo, hi = axis_range([r["lo"] for r in rows] + [r["hi"] for r in rows] + every, [])
        return figure(title, sub, range_bars(rows, lo, hi, unit=unit))
    pages.add("Độ nhạy calibration: đổi tham số trong lưới thì kết quả đổi bao nhiêu",
              "Mỗi thuật toán có lưới calibration chạy trên cùng bộ kiểm. Thanh là khoảng từ thấp nhất đến cao nhất qua các cấu hình của lưới; chấm là cấu hình mặc định. Thanh ngắn so với khoảng cách giữa các thuật toán: ít nhạy.",
              '<div class="row">' + sens_fig(k070, "DLC nhỏ nhất của xe", "m. Càng lớn càng an toàn.", "m")
              + sens_fig(k068, "a_y lớn nhất của xe", "m/s². Càng nhỏ càng êm.", "m/s²") + "</div>"
              + '<div class="row" style="margin-top:4mm">' + sens_fig(k069, "Jerk ngang lớn nhất của xe", "m/s³. Càng nhỏ càng êm.", "m/s³")
              + sens_fig(k050, "Lệch ngang của path so với tâm làn", "m. Càng nhỏ càng sát tâm.", "m") + "</div>")

    reqs = sorted({r for n in names for r in (P["configs"][n].get("failed_runs") or {}).get("by_requirement", {})})
    failing = [n for n in names if (P["configs"][n].get("failed_runs") or {}).get("by_requirement")]
    mx = max([c for n in failing for c in P["configs"][n]["failed_runs"]["by_requirement"].values()] or [1])
    head = "<th>Thuật toán</th>" + "".join(f'<th class="num">{esc(r.replace("PP-SWR-", ""))}</th>' for r in reqs) + '<th class="num">Lượt đã chạy</th>'
    rows = ""
    for n in sorted(failing, key=lambda n: -sum(P["configs"][n]["failed_runs"]["by_requirement"].values())):
        fr = P["configs"][n]["failed_runs"]
        cells = ""
        for r in reqs:
            c = fr["by_requirement"].get(r, 0)
            a = 0.12 + 0.88 * c / mx if c else 0
            cells += (f'<td class="c" style="background:rgba(42,120,214,{a:.2f});color:{"#fff" if a > .5 else "#0b0b0b"}">{c}</td>' if c else '<td class="c"></td>')
        rows += f'<tr><td>{esc(n)}</td>{cells}<td class="num">{fr["runs"]}</td></tr>'
    ok = [n for n in names if n not in failing]
    pages.add("Ca trượt requirement: thuật toán nào trượt requirement nào",
              "Số lượt trượt trên bộ kiểm, đếm cho từng thuật toán ở cấu hình mặc định. Chỉ liệt kê thuật toán có ít nhất một lượt trượt.",
              f'<table class="fail"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'
              f'<p class="note">Cột: mã PP-SWR. Không trượt lượt nào: {esc(", ".join(ok) or "không có")}.</p>')

    cols = [m for m in P["metrics"] if m["id"] not in ("PP-SWR-059", "PP-SWR-016")]
    th = "<th>Thuật toán</th>" + "".join(f'<th class="num">{esc(short_metric(m["id"], m["metric"]))}<br><span class="muted">{esc(m["id"].replace("PP-SWR-", ""))}</span></th>' for m in cols) \
        + '<th class="num">p99 [ms]</th><th class="num">State [KB]</th><th class="num">Thư viện [KB]</th>'
    body = ""
    for n in names:
        c = P["configs"][n]["cost"]
        kb = lambda v: fmt(v / 1000, 3) if v else "—"
        body += (f'<tr><td>{esc(n)}</td>' + "".join(f'<td class="num">{fmt(absval(P, n, f"{m["id"]}|{m["metric"]}"))}</td>' for m in cols)
                 + f'<td class="num">{fmt(c.get("p99_median_ms"))}</td><td class="num">{kb(c.get("state_bytes"))}</td><td class="num">{kb(c.get("library_bytes"))}</td></tr>')
    pages.add("Phụ lục: bảng số",
              "Giá trị trung bình trên bộ kiểm của mọi chỉ số ở các trang trước, cùng các chỉ số không vẽ (a_y thêm vào, jerk và tốc độ quay vô lăng). Kết quả đối chiếu giữa các thuật toán và giả thuyết: PP-TS-031 mục 5.",
              f'<table class="app"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>')


def page(data: dict) -> str:
    pages = Pages(data)
    parts = data["parts"]
    if not parts:
        return shell(cover(data, []).replace("@@N@@", "1"))
    P = parts["test"] if "test" in parts else next(iter(parts.values()))
    build_pages(data, P, pages)
    toc = [(t.split(":")[0], k) for k, (t, _, _) in enumerate(pages.items, start=2)]
    return shell(pages.render(cover(data, toc)))


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
