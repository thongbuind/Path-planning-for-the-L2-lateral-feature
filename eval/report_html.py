"""Benchmark dashboard: static HTML slides (16:9) of one planner run (Software Qualification
Test Specification 10).

    python3 -m eval.report_html build/benchmark/<run>/suite [--out report.html]

Reads an eval.suite output folder (manifest.json, generation.json, results.jsonl,
conformance.json). Slides: the benchmark and its aspect suites, B0 conformance, then one
slide per aspect suite B1 to B8 with its conclusion, counts, main chart, failed requirements
and worst cases. Values come from the results only (black box). Display only; print to PDF.
"""

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
from urllib.parse import quote
from zoneinfo import ZoneInfo

import numpy as np

from eval import conclusion, severity
from eval.metrics import COMPUTE_BINS_MS
from interfaces.planner_io import PLANNER_PERIOD_US

ROOT = Path(__file__).resolve().parents[1]
SQTS = ROOT / "docs" / "vi" / "path-planner-software-qualification-test-specification.md"
E = html.escape

# One colour set for the whole dashboard (reference palette of the dataviz method): text and
# chrome; one data hue with its light step and a gray for context marks; the status set, with
# text and background steps. Red only ever means a failure; an extreme or a highlight is ACCENT.
INK, INK2, INK3 = "#0b0b0b", "#52514e", "#686762"  # text: primary, secondary, muted
RULE, GRID, AXIS = "#dcdbd6", "#e1e0d9", "#c3c2b7"  # card border, gridline, axis and baseline
PANEL, PLANE, SURFACE = "#f9f9f7", "#e6e5e0", "#ffffff"  # soft panel, page plane, slide
ACCENT, ACCENT_SOFT, ACCENT_TEXT, ACCENT_BG = "#2a78d6", "#cde2fb", "#1c5cab", "#eef5fd"
MUTE = "#c3c2b7"  # data marks that are context, not the point
GOOD, WARN, SERIOUS, CRIT = "#0ca30c", "#fab219", "#ec835a", "#d03b3b"
GOOD_TEXT, WARN_TEXT, SERIOUS_TEXT, CRIT_TEXT = "#006300", "#8a5a00", "#a8481f", "#a32626"
GOOD_BG, WARN_BG, SERIOUS_BG, CRIT_BG, NEUTRAL_BG = "#e9f5e9", "#fdf4dd", "#fcede5", "#fbeaea", "#f1f0ec"
GOOD_EDGE, SERIOUS_EDGE, CRIT_EDGE = "#bfe0bf", "#f3c9b4", "#efc4c4"
BLUE, GRAY = ACCENT, MUTE
LEVEL_COLOR = {severity.BLOCKER: CRIT, severity.MAJOR: SERIOUS, severity.MINOR: WARN}
WARN_MARK = 0.8  # warning mark of the limit-use table; chosen by the report, not a requirement
CSS_VARS = (f":root{{--ink:{INK};--ink2:{INK2};--ink3:{INK3};--rule:{RULE};--grid:{GRID};--axis:{AXIS};"
            f"--panel:{PANEL};--accent:{ACCENT};--good-text:{GOOD_TEXT};--crit-text:{CRIT_TEXT}}}")
REPORT_VERSION = "2.0"
BEHAVIOR_IDS = {"PP-SWR-005", "PP-SWR-006", "PP-SWR-007", "PP-SWR-030", "PP-SWR-063", "PP-SWR-089"}
COMFORT_LABELS = {
    "PP-SWR-053": ("Thời gian đưa xe về giữa", "s"),
    "PP-SWR-002": ("Gia tốc ngang thêm vào khi đưa về giữa", "m/s²"),
    "PP-SWR-057": ("Khoảng cách ngang nhỏ nhất", "m"),
    "PP-SWR-081": ("Thời lượng path LKA tới COMPLETED", "s"),
    "PP-SWR-087": ("DTLE nhỏ nhất khi LKA", "m"),
    "PP-SWR-064": ("Thời gian báo trước nhỏ nhất", "s"),
}

ASPECTS = [
    ("B1", "Nominal", "Lái đúng khi mọi thứ bình thường", "Tình huống trong ODD, xa biên, không lỗi"),
    ("B2", "Regulatory", "Qua các bài thử của văn bản", "Lưới chuẩn Euro NCAP LSS, EU 2021/646, R79, R171"),
    ("B3", "Performance limit", "Đúng ở biên ODD và khi vượt quyền lái", "Biên bề rộng làn, xe, tốc độ; cua gắt hơn aysmax"),
    ("B4", "Robustness", "Chịu được lỗi đầu vào", "Lỗi lane model, IMU, thời gian, toàn vẹn message, ego-motion, ghép lỗi"),
    ("B5", "Degradation and refusal", "Từ chối và suy giảm đúng lúc", "Ca phải từ chối, lái có giới hạn, input hỏng, ngoài ODD"),
    ("B6", "Comfort", "Path êm cho người lái", "a_y thêm vào, jerk, thời gian đưa về giữa trên ca bình thường"),
    ("B7", "Flexibility", "Một bản build chạy được mọi xe", "Các mẫu xe với cùng một bộ calibration"),
    ("B8", "Compute", "Thời gian tính", "Thời gian mỗi chu kỳ planner trên mọi ca"),
]
# How each suite is judged (Software Qualification Test Specification 5.3, 8.1 to 8.4): requirements pass
# or fail; performance targets are only measured and scored (8.2: no pass threshold).
PASS_FAIL, SCORE = "pass_fail", "score"
FUNCTIONS = ("HWA", "LKA", "ELK", "Chuyển chức năng")
EXPECTED = {"drive": "Lái", "drive_limited": "Lái có giới hạn", "refuse": "Từ chối"}
PROFILE_NAMES = {"VP-0": "Xe điện cỡ trung, giá trị điển hình", "VP-1": "3.190 × 1.679 mm", "VP-2": "4.241 × 1.834 mm",
                 "VP-3": "4.750 × 1.934 mm", "VP-4": "5.119 × 2.004 mm", "VP-5": "Như VP-4, rộng tối đa 2,5 m"}
SCORING = {
    "B1": (PASS_FAIL, "Đạt khi mọi lần chạy không trượt requirement"),
    "B2": (PASS_FAIL, "Đạt khi mọi bài thử của văn bản đạt"),
    "B3": (PASS_FAIL, "Đạt khi mọi lần chạy không trượt requirement"),
    "B4": (PASS_FAIL, "Đạt khi mọi lần chạy không trượt requirement"),
    "B5": (PASS_FAIL, "Đạt khi từ chối, suy giảm đúng; không từ chối thừa"),
    "B6": (SCORE, "Đo độ êm; không có ngưỡng đạt"),
    "B7": (PASS_FAIL, "Đạt khi 100 % trên mọi xe; độ chênh giữa các xe chỉ tính điểm"),
    "B8": (SCORE, "Đo p99 thời gian tính; không có ngưỡng đạt"),
}
REQ_SHORT = {"PP-SWR-100": "Hai path liên tiếp lệch ngang ≤ 0,05 m", "PP-SWR-101": "Hai path liên tiếp lệch hướng",
             "PP-SWR-102": "Hai path liên tiếp lệch độ cong", "PP-SWR-051": "Xe không lấn vạch khi HWA lái",
             "PP-SWR-039": "Path bắt đầu tại xe khi tài xế ghi đè", "PP-SWR-040": "Path HWA bắt đầu tại xe khi hết ghi đè",
             "PP-SWR-030": "Chọn đúng chức năng theo ưu tiên", "PP-SWR-032": "Báo COMPLETED đúng lúc",
             "PP-SWR-006": "a_y path khi cua gắt hơn aysmax", "PP-SWR-086": "DTLE ≥ −0,3 m khi LKA, ELK",
             "PP-SWR-001": "a_y path ≤ aysmax khi HWA lái", "PP-SWR-007": "Báo cờ giới hạn trước khi đè vạch",
             "PP-SWR-088": "Khoảng cách tới xe làn bên ≥ 0,3 m", "PP-SWR-143": "Path không hợp lệ khi ego-motion hỏng",
             "PP-SWR-124": "Xử lý mất lane model đúng hạn", "PP-SWR-063": "Báo làn quá hẹp",
             "EXECUTION_FAULT": "Planner dừng hoặc ra NaN",
             "PP-SWR-061": "Path liền mạch khi lane model sang làn", "PP-SWR-083": "LKA, ELK kết thúc trong ≤ 10 s",
             "PP-SWR-090": "Không báo COMPLETED quá sớm", "PP-SWR-110": "a_y path LKA ≤ 3,0 m/s²",
             "PP-SWR-111": "a_y path ELK ≤ 4,0 m/s²", "PP-SWR-112": "a_y thêm vào LKA ≤ 1,5 m/s²",
             "PP-SWR-113": "a_y thêm vào ELK ≤ 3,0 m/s²", "PP-SWR-114": "Jerk path LKA ≤ 5 m/s³",
             "PP-SWR-115": "Jerk path ELK ≤ 10 m/s³", "PP-SWR-005": "Giữ HWA khi cua gắt hơn aysmax",
             "PP-SWR-062": "Đạt mọi requirement trong toàn ODD",
             "PP-SWR-055": "Dời xa xe lớn khi khoảng hở nhỏ", "PP-SWR-058": "Bắt đầu dời trước khi xe lớn ngang hàng",
             "PP-SWR-080": "LKA, ELK: điểm đầu path khớp xe", "PP-SWR-018": "observed_horizon_s không quá tầm nhìn"}
SRS = ROOT / "docs" / "vi" / "path-planner-software-requirements-specification.md"


def srs_text() -> dict[str, str]:
    """Requirement sentence per ID, as a fallback name."""
    try:
        text_ = SRS.read_text(encoding="utf-8")
    except OSError:
        return {}
    return {m.group(1): re.sub(r"`", "", m.group(2)).strip() for m in re.finditer(r"^\| (PP-SWR-\d{3}) \| ([^|]+) \|", text_, re.M)}
# Two metrics of one target: short names for the comfort slide.
METRIC_SHORT = {"Khoảng cách ngang nhỏ nhất từ thân xe tới rào chắn khi HWA lái": "Khoảng hở tới rào chắn",
                "Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng": "Khoảng hở tới xe lớn khi ngang hàng"}
COMFORT_TARGETS = ["PP-SWR-053", "PP-SWR-002", "PP-SWR-004", "PP-SWR-057", "PP-SWR-081", "PP-SWR-087",
                   "PP-SWR-064"]
LARGER_IS_BETTER = {"PP-SWR-057", "PP-SWR-064", "PP-SWR-087"}


# ---- formatting and chart primitives -----------------------------------------------------------

def vn(x, d=2):
    return f"{x:.{d}f}".replace(".", ",").replace("-", "−")


def fmt_n(v):
    return f"{int(v):,}".replace(",", ".")


def precise(v):
    """Four significant figures; never turn a small nonzero margin into zero."""
    if v == 0:
        return "0"
    return f"{v:.4g}".replace(".", ",").replace("-", "−")


def limit_percent(ratio):
    """Keep a value below the limit visibly below 100%, even arbitrarily close."""
    if ratio < 1 and round(ratio * 100, 2) >= 100:
        return "< 100 %"
    return vn(ratio * 100, 2 if ratio >= .99 else 1) + " %"



def table(headers, rows, cls="data-table"):
    return (f'<table class="{cls}"><thead><tr>' + "".join(f"<th>{E(h)}</th>" for h in headers)
            + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
            + "</tbody></table>")


def profile_signature(r):
    """Pair on scenario inputs and seed, excluding only vehicle identity/description."""
    c = r["_case"]
    params = {k: v for k, v in c.get("parameters", {}).items() if k not in ("profile", "description")}
    return json.dumps([c.get("family"), c.get("anchor"), c.get("host"), params, r.get("seed")], sort_keys=True)


def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{E(label)}">{body}</svg>'


def text(x, y, s, size=9, anchor="start", fill=INK2, weight=400):
    bold = f' font-weight="{weight}"' if weight != 400 else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{bold}>{E(str(s))}</text>'


def bar_h(x, y, w, h, color):
    if w <= 0:
        return ""
    r = min(4, w, h / 2)
    return (f'<path d="M{x:.1f},{y:.1f} h{w - r:.1f} q{r},0 {r},{r} v{h - 2 * r:.1f} q0,{r} {-r},{r} '
            f'h{-(w - r):.1f} z" fill="{color}"/>')


def bar_v(x, y_base, w, h, color):
    if h <= 0:
        return ""
    r = min(4, h, w / 2)
    return (f'<path d="M{x:.1f},{y_base:.1f} v{-(h - r):.1f} q0,{-r} {r},{-r} h{w - 2 * r:.1f} q{r},0 {r},{r} '
            f'v{h - r:.1f} z" fill="{color}"/>')


def ranked_bars(items, W=560, row=19, label_w=250, color=BLUE, unit="", fmt=fmt_n):
    H = row * len(items) + 8
    vmax = max((v for _, v in items), default=1) or 1
    plot = W - label_w - 70
    out = []
    for i, (name, v) in enumerate(items):
        y = 4 + i * row
        out.append(text(label_w - 8, y + row * .62, name, 8.5, "end", INK))
        out.append(f'<rect x="{label_w}" y="{y + 3}" width="{plot}" height="{row - 6}" fill="{GRID}" rx="2"/>')
        c = color(name) if callable(color) else color
        out.append(bar_h(label_w, y + 3, plot * v / vmax, row - 6, c))
        out.append(text(label_w + plot * v / vmax + 5, y + row * .62, fmt(v) + unit, 8.5, "start", INK))
    return svg(W, H, "".join(out), "ranked bars")



def histogram(counts, edges, W=1180, H=180, limits=(), xlabel="", log=False, ticks=(), ylabel="", color=BLUE):
    PL, PR, PT, PB = 46, 10, 16, 30
    pw, ph = W - PL - PR, H - PT - PB
    lo, hi = (math.log10(edges[0]), math.log10(edges[-1])) if log else (edges[0], edges[-1])
    X = (lambda v: PL + (math.log10(v) - lo) / (hi - lo) * pw) if log else (lambda v: PL + (v - lo) / (hi - lo) * pw)
    ymax = max(max(counts, default=0), 1)
    mag = 10 ** math.floor(math.log10(ymax / 4)) if ymax >= 4 else 1
    step = next(m * mag for m in (1, 2, 5, 10) if m * mag >= ymax / 4)
    top = math.ceil(ymax / step) * step
    out = []
    for k in range(int(round(top / step)) + 1):
        y = PT + ph - ph * k * step / top
        out.append(f'<line x1="{PL}" x2="{W - PR}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        out.append(text(PL - 5, y + 3, fmt_n(k * step), 8, "end", INK3))
    for c, a, b in zip(counts, edges[:-1], edges[1:]):
        x0, x1 = X(a), X(b)
        out.append(bar_v(x0 + 1, PT + ph, max(x1 - x0 - 2, 1), ph * c / top, color(a) if callable(color) else color))
    for v, lab in limits:
        out.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{PT - 4}" y2="{PT + ph}" stroke="{INK2}" stroke-width="1.2"/>')
        out.append(text(X(v) + 4, PT + 4, lab, 8, "start", INK))
    out.append(f'<line x1="{PL}" x2="{W - PR}" y1="{PT + ph}" y2="{PT + ph}" stroke="{INK3}"/>')
    for v, lab in ticks:
        out.append(text(X(v), PT + ph + 12, lab, 8, "middle", INK3))
    out.append(text(PL + pw / 2, H - 3, xlabel, 8, "middle", INK2))
    out.append(text(4, 10, ylabel, 8, "start", INK3))
    return svg(W, H, "".join(out), "histogram")



def nice_ticks(lo, hi, n=4):
    """Round axis values (1, 2, 2.5, 5 x 10^k steps) covering [lo, hi]."""
    if not hi > lo:
        lo, hi = (lo - 1, hi + 1) if lo == hi else (hi, lo)
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    start, end = math.floor(lo / step) * step, math.ceil(hi / step) * step
    return [round(start + i * step, 12) for i in range(int(round((end - start) / step)) + 1)]


def halo(svg_text):
    """A label that stays legible where it crosses a mark: a surface-coloured outline under the glyphs."""
    return svg_text.replace("<text ", f'<text stroke="{SURFACE}" stroke-width="3" paint-order="stroke" ', 1)

def range_rows(rows, unit, W=380, row=20, label_w=118):
    """Small multiple of one metric, one row per scenario: range over the runs (gray rule),
    median (gray dot) and the worst run (accent dot, labelled). rows: [(label, values, worst)]."""
    PT, PB, PR = 4, 20, 46
    allv = [v for _, vs, _ in rows for v in vs]
    ticks = nice_ticks(min(allv + [0.0]), max(allv + [0.0]))
    lo, hi = ticks[0], ticks[-1]
    X = lambda v: label_w + (v - lo) / (hi - lo) * (W - label_w - PR)
    H = PT + row * len(rows) + PB
    out = [f'<line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{PT}" y2="{H - PB}" stroke="{GRID}"/>' for t in ticks]
    for i, (label, vs, worst) in enumerate(rows):
        y = PT + row * (i + .5)
        med = float(np.median(vs))
        tip = f"{label}: {len(vs)} lần chạy, {precise(min(vs))}–{precise(max(vs))} {unit}, trung vị {precise(med)}, bất lợi nhất {precise(worst)}"
        out.append(f'<g><title>{E(tip)}</title>'
                   f'<rect x="0" y="{y - row / 2:.1f}" width="{W}" height="{row}" fill="transparent"/>'
                   + text(0, y + 3.5, label, 9, "start", INK2)
                   + f'<line x1="{X(min(vs)):.1f}" x2="{X(max(vs)):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{MUTE}" stroke-width="2" stroke-linecap="round"/>'
                   f'<circle cx="{X(med):.1f}" cy="{y:.1f}" r="3" fill="{INK3}"/>'
                   f'<circle cx="{X(worst):.1f}" cy="{y:.1f}" r="4.5" fill="{ACCENT}" stroke="{SURFACE}" stroke-width="2"/>'
                   + halo(text(X(worst) - 8, y + 3.5, precise(worst), 9, "end", INK, 650)
                          if worst <= min(vs) and X(worst) - label_w > 44 else text(X(worst) + 8, y + 3.5, precise(worst), 9, "start", INK, 650))
                   + '</g>')
    out.append(f'<line x1="{label_w}" x2="{W - PR}" y1="{H - PB}" y2="{H - PB}" stroke="{AXIS}"/>')
    out += [text(X(t), H - PB + 12, precise(t), 8, "middle", INK3) for t in ticks]
    return svg(W, H, "".join(out), f"Giá trị theo tình huống, {unit}")


def ranked_ref(items, ref=None, ref_label="", unit="", W=560, row=22, label_w=190):
    """Ranked horizontal bars, one hue, value at the tip, with an optional neutral reference line.
    items: [(label, value, tooltip)], largest first."""
    PT, PB, PR = 14, 20, 56
    vmax = max([v for _, v, _ in items] + ([ref] if ref else []) + [1e-9])
    ticks = nice_ticks(0, vmax)
    hi = ticks[-1]
    X = lambda v: label_w + v / hi * (W - label_w - PR)
    H = PT + row * len(items) + PB
    out = [f'<line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{PT}" y2="{H - PB}" stroke="{GRID}"/>' for t in ticks]
    for i, (label, v, tip) in enumerate(items):
        y = PT + row * i
        out.append(f'<g><title>{E(tip)}</title><rect x="0" y="{y}" width="{W}" height="{row}" fill="transparent"/>'
                   + text(label_w - 8, y + row * .64, label, 9, "end", INK2)
                   + bar_h(label_w, y + 4, X(v) - label_w, row - 8, ACCENT)
                   + halo(text(X(v) + 5, y + row * .64, precise(v) + unit, 9, "start", INK, 650)) + '</g>')
    if ref:
        out.append(f'<line x1="{X(ref):.1f}" x2="{X(ref):.1f}" y1="{PT - 4}" y2="{H - PB}" stroke="{INK2}" stroke-width="1.2"/>')
        out.append(text(X(ref), PT - 6, ref_label, 8, "middle", INK2))
    out.append(f'<line x1="{label_w}" x2="{X(hi):.1f}" y1="{H - PB}" y2="{H - PB}" stroke="{AXIS}"/>')
    out += [text(X(t), H - PB + 12, precise(t), 8, "middle", INK3) for t in ticks]
    return svg(W, H, "".join(out), "ranked bars")


def offset_chart(names, values):
    W,H,PL,PR,PT,PB = 560,235,55,12,24,32
    finite = [v for v in values if v is not None]
    ticks = nice_ticks(0, max(finite, default=1) * 1.08 or 1)
    top = ticks[-1]
    out=[]
    for t in ticks:
        y=H-PB-(H-PT-PB)*t/top
        out.append(f'<line x1="{PL}" x2="{W-PR}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        out.append(text(PL-8,y+4,precise(t),11,'end'))
    bw=(W-PL-PR)/max(len(names),1)
    for i,(name,v) in enumerate(zip(names,values)):
        x=PL+bw*(i+.5)
        if v is not None:
            h=(H-PT-PB)*v/top
            bwid = min(24, bw*.6)
            out.append(bar_v(x-bwid/2,H-PB,bwid,h,ACCENT if v==max(finite) else MUTE))
            out.append(text(x,H-PB-h-7,precise(v),11,'middle',INK,650))
        else: out.append(text(x,H-PB-10,'—',11,'middle'))
        out.append(text(x,H-10,name,11,'middle'))
    return svg(W,H,''.join(out),'Lệch ngang lớn nhất của từng mẫu xe, mét')



REVIEW_CSS = """
.group-C2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 16px}
.check-row{padding:7px 0}.group-C2 .check-row{min-height:66px;display:block;position:relative;padding-right:0}
.group-C2 .check-row>div{padding-right:38px}.group-C2 .status{position:absolute;right:0;top:8px}
#B4 .data-table td{padding-top:7px;padding-bottom:7px}#B4 .data-table td:first-child{white-space:nowrap}
#B5 .data-table td:nth-child(n+3),#B5 .data-table th:nth-child(n+3){white-space:nowrap;min-width:42px;text-align:right}
#B5 .data-table{font-size:9pt}#B5 .data-table td{padding:8px 5px}
#B6 .data-table td{padding:2px 6px;font-size:8.5pt}#B6 .data-table th{padding:2px 6px}#B6 .card .body{align-items:flex-start}#B6 .card .body svg{height:auto;max-height:100%;max-width:470px}
#B7 .data-table td{padding-top:9px;padding-bottom:9px;font-size:9pt}#B7 .data-table td:nth-child(n+2){white-space:nowrap}
.margin-table td{padding:2px 3px;font-size:8pt}.margin-table th{padding:3px;font-size:7.5pt;white-space:nowrap}
.margin-table .limit-bar{min-width:64px;font-size:7.5pt;padding:1px 2px}
.tile-count strong{margin-right:5px}

a{color:inherit;text-underline-offset:2px} .top .meta a,.foot a{text-decoration:none}
.top{flex:none}.top>div:first-child{min-width:0}.top .meta{flex-shrink:0;max-width:320px}
.top .sub{max-width:850px}.grid>*{min-width:0}.card{min-width:0}
.card .body{overflow:visible;align-items:flex-start;width:100%}.card .body>svg{max-height:100%;height:100%;min-height:0}
.kpi .v{font-size:20pt;overflow-wrap:anywhere}.kpi .d{font-size:8pt}
.card h3{font-size:10pt}.card .cap{font-size:8pt}.chip{font-size:6.7pt}
.data-table{border-collapse:collapse;width:100%;font-size:10pt;line-height:1.3}
.data-table th{text-align:left;color:var(--ink2);font-size:8.5pt;border-bottom:1px solid var(--axis);padding:7px 8px}
.data-table td{padding:7px 8px;border-bottom:1px solid var(--grid);vertical-align:middle}
.data-table th:first-child,.data-table td:first-child{padding-left:0}
.data-table td a{text-decoration:none;border-bottom:1px dotted var(--ink3)}
.data-table td{overflow-wrap:anywhere}.margin-table{font-size:8.5pt}
.margin-table th{font-size:7.7pt}.margin-table td{padding:2px 4px}.margin-table th{padding:2px 4px}
.margin-table td:nth-child(3),.margin-table td:nth-child(4){white-space:nowrap}
.limit-bar{display:block;min-width:75px;text-align:center;font-size:8pt;font-weight:650;padding:3px 4px;color:var(--ink);border-radius:2px}
.muted{color:var(--ink3);font-size:8pt}.status{display:inline-block;font-weight:650;white-space:nowrap}
.good{color:var(--good-text)}.bad{color:var(--crit-text)}.neutral{color:var(--ink3)}
.overview-intro{display:flex;justify-content:space-between;align-items:center;padding-bottom:8px;font-size:10pt}
.overview-intro p{margin:3px 0;color:var(--ink2)}.overview-intro>div:last-child{text-align:right}
.overview-intro>div:last-child b{font-size:18pt}.flow{display:flex;justify-content:space-between;gap:16px;background:var(--panel);border:1px solid var(--axis);border-radius:5px;padding:11px 14px;text-decoration:none;font-size:10pt}
.flow-next{padding:7px 0 0;font-size:9pt;color:var(--ink2)}.overview-tile{text-decoration:none;padding:13px}
.tile-top{display:flex;justify-content:space-between;gap:8px;align-items:flex-start;font-size:10pt}
.tile-focus{font-size:10pt;font-weight:600;margin-top:8px}.tile-desc{font-size:8.5pt;color:var(--ink2);margin-top:5px}
.tile-count{margin-top:auto;font-size:8.5pt;color:var(--ink2);padding-top:10px}.tile-count strong{font-size:20pt;color:var(--ink)}
.definitions{grid-column:1/-1;font-size:8.5pt;color:var(--ink2);line-height:1.5}
.b0-summary{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--rule);padding:4px 0 10px;font-size:11pt}
.b0-summary p{font-size:9pt;margin:6px 0 0}.check-list{width:100%}.check-row{display:flex;justify-content:space-between;align-items:start;gap:10px;padding:5px 0;border-bottom:1px solid var(--grid);font-size:9pt}
.check-row a{font-size:7.5pt;color:var(--ink3);text-decoration:underline}.check-row .status{font-size:8pt}
.comfort-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px 24px;width:100%}
.comfort-cell{min-width:0}.comfort-title{font-size:10pt;font-weight:650;min-height:34px}.comfort-title span{white-space:nowrap}
.comfort-stats{display:flex;justify-content:space-between;gap:12px;font-size:9pt}.comfort-cell svg{display:block;width:100%;height:55px}
.failure-summary{display:flex;flex-wrap:wrap;gap:9px 24px;font-size:9pt}.failure-summary>span{display:flex;gap:10px}
.page:target{outline:2px solid var(--accent);outline-offset:2px}
.check-why{font-size:7.5pt;line-height:1.3;margin-top:2px;overflow-wrap:anywhere}
.howto{margin:0;padding-left:14px;font-size:8.5pt;line-height:1.45;color:var(--ink2)}
#B8 .data-table td{padding:3px 6px;font-size:8.5pt}#B8 .data-table th{padding:3px 6px}
"""


# ---- page shell ------------------------------------------------------------------------------------
CSS = f"""
*{{box-sizing:border-box}}
html,body{{margin:0;background:{PLANE};color:{INK};font:9pt/1.35 -apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{padding:20px 0}}
.page{{width:1280px;height:720px;margin:0 auto 24px;background:{SURFACE};padding:28px 36px 20px;display:flex;flex-direction:column;gap:4mm;
box-shadow:0 1px 3px rgba(0,0,0,.12),0 8px 28px rgba(0,0,0,.08);overflow:hidden}}
.top{{display:flex;align-items:center;gap:5mm;padding-bottom:3mm;border-bottom:1px solid {RULE}}}
.top .title{{font-size:20pt;font-weight:680;letter-spacing:-.01em}}
.top .sub{{color:{INK3};font-size:8pt}}
.top .meta{{margin-left:auto;text-align:right;color:{INK3};font-size:7.5pt;line-height:1.5}}
.grid{{flex:1;display:grid;gap:4mm;min-height:0}}
.card{{border:1px solid {RULE};border-radius:6px;padding:3mm 3.5mm 2.5mm;display:flex;flex-direction:column;min-height:0}}
.card h3{{margin:0;font-size:9pt;font-weight:650}}
.card .cap{{margin:.6mm 0 2mm;color:{INK3};font-size:7.5pt}}
.card .body{{flex:1;display:flex;align-items:center;min-height:0;overflow:hidden}}
.kpi .v{{font-size:22pt;font-weight:680;font-variant-numeric:tabular-nums;line-height:1.05;margin-top:1mm}}
.kpi .l{{font-size:8pt;color:{INK2}}} .kpi .d{{font-size:7.5pt;color:{INK3};margin-top:1mm}}
.v-fail{{background:{CRIT_BG};border-color:{CRIT_EDGE}}} .v-fail .v{{color:{CRIT_TEXT}}}
.v-major{{background:{SERIOUS_BG};border-color:{SERIOUS_EDGE}}} .v-major .v{{color:{SERIOUS_TEXT}}}
.v-ok{{background:{GOOD_BG};border-color:{GOOD_EDGE}}} .v-ok .v{{color:{GOOD_TEXT}}}
.v-info{{background:{ACCENT_BG};border-color:{ACCENT_SOFT}}} .v-info .v{{color:{ACCENT_TEXT}}}
.chip{{display:inline-block;font-size:7pt;font-weight:700;letter-spacing:.03em;padding:.6mm 1.8mm;border-radius:3px;white-space:nowrap}}
.chip-pf{{background:{INK};color:#fff}} .chip-sc{{background:{SURFACE};color:{ACCENT_TEXT};border:1.2px solid {ACCENT_TEXT}}}
.foot{{display:flex;justify-content:space-between;color:{INK3};font-size:7pt}}
.checks{{display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;gap:2.2mm 6mm;font-size:8.5pt;width:100%;align-self:flex-start}}
.checks div{{display:flex;align-items:flex-start;gap:1.8mm;line-height:1.3}} .checks small{{color:{INK3};font-size:7pt;margin-left:1mm}}
.ok,.ko,.nk{{width:3.8mm;height:3.8mm;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;color:#fff;font-size:7pt;font-weight:800;flex:none}}
.ok{{background:{GOOD}}} .ko{{background:{CRIT}}} .nk{{background:{GRAY}}}
.key{{display:flex;flex-wrap:wrap;gap:1mm 5mm;font-size:7.5pt;color:{INK2};margin:-1mm 0 1.5mm}}
.key span{{display:inline-flex;align-items:center;gap:1.3mm}}
.legend{{display:flex;gap:4mm;font-size:7.5pt;color:{INK2};margin-top:1.5mm;flex-wrap:wrap}}
.legend span{{display:inline-flex;align-items:center;gap:1.2mm}} .sw{{width:2.6mm;height:2.6mm;border-radius:1px;display:inline-block}}
@page{{size:1280px 720px;margin:0}}
@media print{{html,body{{background:none;padding:0}}.page{{margin:0;box-shadow:none;break-after:page}}}}
"""


# Legends keep their full text: the font shrinks until the legend fits its column (display only).
FIT_SCRIPT = ""


def card(title, body, cap="", style="", key=""):
    """Caption: one idea per line (a list, never joined by separators); key: symbols and their meaning."""
    lines = [cap] if isinstance(cap, str) else list(cap)
    caption = "".join(f"<div>{E(x)}</div>" for x in lines if x)
    return (f'<div class="card" style="{style}"><h3>{E(title)}</h3>'
            f'{f"<div class=cap>{caption}</div>" if caption else ""}{f"<div class=key>{key}</div>" if key else ""}'
            f'<div class="body">{body}</div></div>')





def chip(kind):
    return ('<span class="chip chip-pf">ĐẠT / TRƯỢT</span>' if kind == PASS_FAIL
            else '<span class="chip chip-sc">CHỈ ĐO HIỆU NĂNG</span>')


def kpi(label, value, detail, cls=""):
    return f'<div class="card kpi {cls}"><div class="l">{E(label)}</div><div class="v">{E(value)}</div><div class="d">{E(detail)}</div></div>'


VERDICT = {conclusion.BLOCKED: ("KHÔNG ĐẠT", "v-fail"), conclusion.NOT_APPROVED: ("KHÔNG ĐẠT QUY ĐỊNH", "v-major"),
           conclusion.NO_BLOCKER: ("ĐẠT", "v-ok")}


# ---- data -----------------------------------------------------------------------------------------

def names_from_sqts():
    text_ = SQTS.read_text(encoding="utf-8")
    names, groups = {}, {}
    for m in re.finditer(r"^\| (S\d+[bc]?) \| ([^|]+) \|", text_, re.M):
        names.setdefault(m.group(1), m.group(2).strip())
    for m in re.finditer(r"^\| (F\d\d) \| ([^|]+) \| ([^|]+) \|", text_, re.M):
        names[m.group(1)], groups[m.group(1)] = m.group(3).strip(), m.group(2).strip()
    names["G01"], groups["G01"] = "Đêm mưa", "Ghép lỗi"
    return names, groups


DOCS = ("R79", "R171", "EU 2021/646", "Euro NCAP LSS")


def regulatory_tests() -> list[dict]:
    """Tests of Software Qualification Test Specification 5.1 run in SIL: rows with a test point
    and a scenario. Cases: (family, anchors or None)."""
    text_ = SQTS.read_text(encoding="utf-8")
    section = text_[text_.index("{#benchmark-regulatory}"):text_.index("{#benchmark-scenario-levels}")]
    tests = []
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0] or cells[0].startswith(("Văn bản", "---")):
            continue
        source, name, point, _, scenarios = cells[:5]
        refs = [(m.group(1), set(re.findall(r"[a-z]", m.group(2))) if m.group(2) else None)
                for m in re.finditer(r"\b(S\d+[bc]?|F\d\d|G\d\d)\b(?:\s*\(([a-z, ]+)\))?", scenarios)]
        if point in ("—", "") or not refs:
            continue
        tests.append({"source": source, "name": name, "docs": [d for d in DOCS if d in source], "refs": refs})
    return tests


def test_of(case: dict, tests: list[dict]) -> list[int]:
    """Indexes of the 5.1 tests a case belongs to: protocol rows by their document, other cases
    by scenario and anchor (never to a protocol-only test)."""
    protocol = case.get("parameters", {}).get("protocol") or ""
    family, anchor = case.get("family"), case.get("anchor")
    out = []
    for i, t in enumerate(tests):
        hit = [a for f, a in t["refs"] if f == family]
        if not hit:
            continue
        if protocol:
            if protocol in t["docs"]:
                out.append(i)
        elif t["docs"] != ["Euro NCAP LSS"] and any(a is None or anchor in a for a in hit):
            out.append(i)
    return out


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


LIMIT = re.compile(r"\s*(<=|>=|<|>|=)\s*(-?[\d.]+)")
INFO_KEPT = ("vehicle_offset_max_m", "compute_hist", "no_impact", "compute_time_note")


def _slim(r: dict) -> dict:
    """Only what the slides read: failures (computed once), NCAP row criterion, targets, a few
    info values. A full run is about 180 MB of JSON; whole records would not fit an 8 GB machine."""
    if "_fail" not in r:
        inside, outside, _ = conclusion.run_failures(r)
        r["_fail"] = [{"requirement": f["requirement"], "level": f["level"]} for f in inside]
        r["_oos"] = sorted({f["requirement"] for f in outside})
    result = r.get("result")
    if result is not None:
        r["_behavior"] = [c for c in result.get("criteria", []) if c.get("id") in BEHAVIOR_IDS]
        r["_crit"] = [(c["id"], c.get("metric", ""), m.group(1), float(m.group(2)), float(c["value"]))
                      for c in result.get("criteria", [])
                      if c.get("applicable") and isinstance(c.get("value"), (int, float)) and math.isfinite(c["value"])
                      and (m := LIMIT.match(str(c.get("limit", "")))) and m.group(1) in ("<=", ">=")]
        from eval.compare import NCAP_DTLE
        r["result"] = {
            "criteria": [c for c in result.get("criteria", []) if c.get("id") == NCAP_DTLE],
            "issues": result.get("issues", [{"kind": "requirement", "text": t} for t in result.get("case_failures", [])]),
            "targets": [{k: t.get(k) for k in ("id", "metric", "value", "unit")} for t in result.get("targets", [])],
            "info": {k: v for k, v in (result.get("info") or {}).items() if k in INFO_KEPT}}
    for key in ("figure", "failed_out_of_scope"):
        r.pop(key, None)
    return r


def _records(path: Path, cases: dict) -> list[dict]:
    out = []
    if path.is_file():
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:  # last line of a stopped run
                    continue
                if r.get("case") in cases:
                    out.append(_slim(r))
    return out


def load(folder: Path, generation: Path | None = None, conformance: Path | None = None) -> dict:
    """An eval.suite folder; a stopped suite (no manifest.json, generation.json) still loads when
    the generated manifest is given."""
    folder = Path(folder)
    manifest = _json(folder / "manifest.json") or {}
    gen = _json(folder / "generation.json") or (_json(Path(generation)) if generation else None)
    if gen is None:
        raise FileNotFoundError(f"{folder}: thiếu generation.json; truyền --generation <manifest của eval.generate>")
    if generation and "generation" not in manifest:
        manifest["generation"] = {"manifest": str(Path(generation).resolve())}
    generation = gen
    cases = {c["id"]: c for c in generation["cases"]}
    records = _records(folder / "results.jsonl", cases)
    b0_path = Path(conformance) if conformance else folder / "conformance.json"
    b0 = json.loads(b0_path.read_text(encoding="utf-8")) if b0_path.is_file() else None
    case_dir = Path(manifest.get("generation", {}).get("manifest", folder / "x")).parent
    derived = {}
    for r in records:
        case = cases.get(r.get("case"), {})
        r["_family"] = case.get("family", "?")
        r["_case"] = case
        r.setdefault("profile", case.get("parameters", {}).get("profile"))
        if "aspects" not in r or "labels" not in r:  # written before eval.suite kept them
            if r["case"] not in derived:
                derived[r["case"]] = _derive(case, case_dir)
            r.setdefault("aspects", derived[r["case"]][0])
            r.setdefault("labels", derived[r["case"]][1])
    headroom = defaultdict(dict)  # aspect -> (id, metric) -> closest approach to the limit
    metric_of = {}
    for r in records:
        for rid, metric, op, limit, value in r.pop("_crit", []):
            metric_of.setdefault(rid, metric)
            if op == "<=" and limit > 0:
                key, score = (rid, metric, op), value / limit  # share of the limit used
            elif op == ">=":
                key, score = (rid, metric, op), -(value - limit)  # minus the margin above the limit
            else:
                continue
            for a in r.get("aspects", []):
                old = headroom[a].get(key)
                if old is None or score > old[0]:
                    headroom[a][key] = (score, value, limit)
    return {"folder": folder, "manifest": manifest, "generation": generation, "cases": cases, "records": records, "b0": b0,
            "conformance_path": b0_path,
            "headroom": headroom, "metric_of": metric_of}


def _derive(case: dict, case_dir: Path) -> tuple[list[str], dict]:
    """(aspects, labels) of a case from its concrete file, as eval.suite records them."""
    from eval import aspects, labels, loader
    try:
        case_labels = labels.of(loader.load_file(case_dir / case["file"]))
        return aspects.members(case["family"], case["anchor"], case.get("methods", []), case_labels), case_labels
    except Exception:
        return [], {}


def run_levels(r):
    if "_fail" in r:
        return r["_fail"], []
    inside, _, not_judged = conclusion.run_failures(r)
    return [{"requirement": f["requirement"], "level": f["level"]} for f in inside], not_judged


def aspect_stats(records):
    runs = len(records)
    cases = len({r["case"] for r in records})
    failed_req = Counter()
    levels = set()
    passed = 0
    for r in records:
        inside, _ = run_levels(r)
        passed += not inside
        for f in inside:
            failed_req[f["requirement"]] += 1
            levels.add(f["level"])
    verdict = (conclusion.BLOCKED if severity.BLOCKER in levels else conclusion.NOT_APPROVED if severity.MAJOR in levels
               else conclusion.NO_BLOCKER)
    return {"runs": runs, "cases": cases, "passed": passed, "failed_req": failed_req, "verdict": verdict}


def info(r, key):
    return ((r.get("result") or {}).get("info") or {}).get(key)


def target(r, rid, metric_prefix=""):
    for t in (r.get("result") or {}).get("targets", []):
        if t["id"] == rid and t["metric"].startswith(metric_prefix) and t.get("value") is not None and math.isfinite(t["value"]):
            return t["value"]
    return None


# ---- report -----------------------------------------------------------------------------------------

class Report:
    def __init__(self, data: dict):
        self.d = data
        self.names, self.fault_group = names_from_sqts()
        self.srs = srs_text()
        self.pages = []
        self.out_dir = data["folder"]
        self.details_name = "report-details.html"
        self.generated = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(timespec="seconds")
        self.run_id = str(data["manifest"].get("run_id") or (data["folder"].parent.name + "/" + data["folder"].name))
        self.planned = len(data["generation"].get("runs", [])) or len(data["records"])
        self.by_aspect = defaultdict(list)
        for r in data["records"]:
            for a in r.get("aspects", []):
                self.by_aspect[a].append(r)
        self.planned_by_family = Counter(data["cases"].get(r["case"], {}).get("family", "?")
                                         for r in data["generation"].get("runs", []))
        self.meta = (f'<a href="#metadata">{E(data["generation"].get("suite", ""))} · SIL · Báo cáo {REPORT_VERSION}</a>'
                     f'<br>{fmt_n(len(data["records"]))} / {fmt_n(self.planned)} lần chạy')
        if len(data["records"]) < self.planned:
            self.meta += f'<br><b>Chưa chạy hết: {fmt_n(len(data["records"]))} / {fmt_n(self.planned)} lần chạy</b>'

    def href(self, path):
        return quote(os.path.relpath(Path(path).resolve(), self.out_dir.resolve()), safe="/#")

    def details_link(self, anchor, label="Chi tiết"):
        return f'<a href="{E(self.details_name)}#{E(anchor)}">{E(label)}</a>'

    def label(self, code, n=34):
        name = self.names.get(code, "")
        name = name[:n - 1] + "…" if len(name) > n else name
        return f"{code}: {name}" if name else code

    def page(self, title, sub, grid, cards):
        n = len(self.pages) + 1
        anchor = title.split(" · ")[0] if " · " in title else "overview"
        if title.startswith("Thông tin"): anchor = "metadata"
        self.pages.append(f'<section class="page" id="{E(anchor)}"><div class="top"><div><div class="title">{E(title)}</div>'
                          f'<div class="sub">{E(sub)}</div></div><div class="meta">{self.meta}</div></div>'
                          f'<div class="grid" style="{grid}">{"".join(cards)}</div>'
                          f'<div class="foot"><a href="#overview">{E(self.run_id)}</a><span>{n} / {{TOTAL}}</span></div></section>')

    def overview(self):
        recs = self.d["records"]
        d = self.d["generation"].get("definition", {})
        intro = (f'<div class="overview-intro"><div><b>Path planner · HWA / LKA / ELK · Vòng kín SIL</b>'
                 f'<p>{len(d.get("scenarios", []))} tình huống lái · {len(d.get("faults", [])) + len(d.get("combinations", []))} loại lỗi · '
                 f'{len(d.get("profiles", []))} mẫu xe</p></div><div><b>{fmt_n(len(recs))} / {fmt_n(self.planned)}</b><br>lần chạy / kế hoạch</div></div>')
        b0 = self.d["b0"]
        note = "Chưa chạy" if b0 is None else f'{sum(c["status"] == "pass" for c in b0["checks"])} đạt · {sum(c["status"] == "fail" for c in b0["checks"])} trượt · {sum(c["status"] not in ("pass", "fail", "info") for c in b0["checks"])} không kiểm được'
        flow = (f'<a class="flow" href="#B0"><b>01 · B0 Conformance</b><span>API → Contract → Integration</span><span>{note}</span></a>'
                '<div class="flow-next">↓ 02 · B1–B8: kiểm thử theo từng khía cạnh</div>')
        tiles = []
        for k, title, focus, what in ASPECTS:
            sub = self.by_aspect.get(k, [])
            kind, rule = SCORING[k]
            tiles.append(f'<a class="card overview-tile" href="#{k}"><div class="tile-top"><b>{k} · {E(title)}</b>{chip(kind)}</div>'
                         f'<div class="tile-focus">{E(focus)}</div><div class="tile-desc">{E(what)}</div>'
                         f'<div class="tile-count"><strong>{fmt_n(len(sub))}</strong> lần chạy đã có dữ liệu</div></a>')
        definitions = ('<div class="definitions"><b>Cách đếm:</b> Tình huống = họ S/F/G. Ca = một cấu hình cụ thể, đã gồm mẫu xe. '
                       'Lần chạy = ca × seed.<br>Một ca có thể thuộc nhiều bộ; không cộng tổng các thẻ. '
                       'Đạt/trượt theo requirement; hiệu năng chỉ đo, không có ngưỡng đạt.</div>')
        self.page("Benchmark: 8 bộ kiểm tra", "Phạm vi, trình tự và đường dẫn tới từng bộ kiểm",
                  "grid-template-columns:repeat(4,minmax(0,1fr));grid-template-rows:auto 1fr 1fr auto",
                  [f'<div style="grid-column:1/-1">{intro}{flow}</div>'] + tiles + [definitions])

    def b0_slide(self):
        b0 = self.d["b0"]
        if b0 is None:
            self.page("B0 · Conformance", "API, Contract và Integration", "grid-template-columns:1fr", [card("Chưa chạy", "Không có dữ liệu B0.")])
            return
        checks = [c for c in b0["checks"] if c["status"] != "info"]
        fails = [c["id"] for c in checks if c["status"] == "fail"]
        unknown = [c["id"] for c in checks if c["status"] not in ("pass", "fail")]
        reason = "; ".join(filter(None, ["Trượt: " + ", ".join(fails) if fails else "", "Chưa kiểm được: " + ", ".join(unknown) if unknown else ""]))
        head = (f'<div class="b0-summary"><div><span class="status {"bad" if b0["blocked"] else "good"}">'
                f'{"KHÔNG ĐẠT" if b0["blocked"] else "ĐẠT"}</span> C1/C2 · <b>Tích hợp được: {"Có" if b0["integrable"] else "Không"}</b>'
                f'<p>{E(reason or "Các kiểm tra đã thực hiện đều đạt.")}</p></div>'
                '<div class="muted">C1 hoặc C2 trượt → chặn.<br>Tích hợp được khi không bị chặn và mọi C3 đạt.</div></div>')
        short = {"symbols":"Symbol/API", "layout":"Phiên bản schema và layout", "state_size":"Kích thước trạng thái", "alignment":"Căn vùng nhớ",
                 "init_ok":"Khởi tạo cấu hình hợp lệ", "init_missing":"Từ chối cấu hình thiếu", "init_out_of_limits":"Từ chối cấu hình ngoài dải",
                 "outputs_every_cycle":"Output mỗi chu kỳ", "filled":"Điền đủ mọi trường", "counter":"Counter 0–255", "stamp":"Timestamp = t0",
                 "enum":"Enum/bool hợp lệ", "trajectory_format":"Định dạng Trajectory", "finite":"Không NaN / vô cực", "robust":"Input biên không làm dừng",
                 "version":"Version / commit / calibration", "deterministic":"Tái lập từng bit", "interleaved":"Hai instance độc lập", "memory":"Không ghi ngoài vùng nhớ"}
        cards = []
        for group, name in (("C1", "API"), ("C2", "Contract"), ("C3", "Integration")):
            rows = []
            for c in checks:
                if not c["id"].startswith(group): continue
                state = {"pass": ("good", "✓ Đạt"), "fail": ("bad", "✕ Trượt")}.get(c["status"], ("neutral", "— Chưa kiểm"))
                label = "Không cấp phát / file / đồng hồ" if c["id"] == "C3.symbols" else short.get(c["id"].split(".")[-1], c.get("title", c["id"]))
                why = ""
                if c["status"] != "pass" and c.get("detail"):
                    detail = re.sub(r"^\[[^\]]*\]\s*", "", c["detail"])
                    short_detail = detail if len(detail) <= 90 else detail[:89] + "…"
                    why = (f'<div class="check-why" style="color:{CRIT_TEXT if c["status"] == "fail" else INK3}" '
                           f'title="{E(detail)}">{E(short_detail)}</div>')
                rows.append(f'<div class="check-row"><div><b>{E(label)}</b><br>{self.details_link(c["id"], c["id"])}{why}</div>'
                            f'<span class="status {state[0]}">{state[1]}</span></div>')
            cards.append(card(f"{group} · {name}", f'<div class="check-list group-{group}">' + "".join(rows) + '</div>',
                              "Lý do ghi dưới mục trượt hoặc chưa kiểm; ID mở bằng chứng"))
        self.page("B0 · Conformance", "Kiểm tra contract gọi hàm trước khi đánh giá các bộ B1–B8",
                  "grid-template-columns:1fr 1.5fr 1fr;grid-template-rows:auto 1fr",
                  [f'<div style="grid-column:1/-1">{head}</div>'] + cards)

    def failed_card(self, stats):
        rows = stats["failed_req"].most_common(5)
        if not rows:
            return card("Requirement trượt", f'<div style="font-size:11pt;color:{GOOD_TEXT};font-weight:650">Không có requirement nào trượt</div>',
                        style="grid-column:span 2")
        items = [(f"{rid.replace('PP-SWR-', '')} {REQ_SHORT.get(rid, '')}".strip(), v) for rid, v in rows]
        color = lambda name: LEVEL_COLOR.get(severity.level("PP-SWR-" + name.split(" ")[0]) or severity.level(name.split(" ")[0]), GRAY)
        legend = ('<div class="legend">' + "".join(f'<span><i class="sw" style="background:{c}"></i>{lv}</span>' for lv, c in LEVEL_COLOR.items()) + "</div>")
        return card("Requirement trượt", f'<div style="width:100%">{ranked_bars(items, color=color, unit=" lần")}{legend}</div>',
                    "Số lần chạy trượt, trong bộ này", style="grid-column:span 2")

    def worst_card(self, rows, cap="Giá trị xấu nhất qua mọi mẫu xe và seed", span="grid-column:span 2", limit=4):
        body = "".join(f'<div style="display:flex;justify-content:space-between;gap:3mm;padding:1.6mm 0;border-bottom:1px solid {GRID};font-size:9pt">'
                       f'<span>{E(a)}</span><b style="white-space:nowrap">{E(b)}</b></div>' for a, b in rows[:limit]) or "Không có."
        return card("Ca tệ nhất", f'<div style="width:100%;align-self:flex-start">{body}</div>', cap, style=span)

    def case_name(self, r, profile=True):
        c = r["_case"]
        host = f' trên {c["host"]}' if c.get("host") else ""
        base = f'{self.label(c.get("family", "?"), 28)} {c.get("anchor") or ""}{host}'
        return f'{base}, {r.get("profile", "")}' if profile else base


    def function_of(self, family):
        if family in ("S8b",):
            return "ELK"
        if family in ("S8c", "S9", "S16"):
            return "Chuyển chức năng"
        name = self.names.get(family, "")
        return "ELK" if "ELK" in name else "LKA" if "LKA" in name else "HWA"

    def req_name(self, rid, n=40):
        name = (REQ_SHORT.get(rid) or re.sub(r"\s*\[.*?\]", "", self.d["metric_of"].get(rid, ""))
                or self.srs.get(rid, ""))
        name = name[:n - 1] + "…" if len(name) > n else name
        return f"{rid.replace('PP-SWR-', '')} {name}".strip()

    def where_card(self, recs, used, group_of=None, groups=FUNCTIONS, caption="theo tình huống, nhóm theo chức năng",
                   code_label="Tình huống", group_label="Chức năng"):
        """Failed runs per scenario or fault, in groups: one unit only (runs)."""
        group_of = group_of or (lambda r: self.function_of(r["_family"]))
        fam = defaultdict(lambda: [0, 0])
        for r in recs:
            key = (group_of(r), r["_family"])
            fam[key][1] += 1
            fam[key][0] += bool(run_levels(r)[0])
        groups = list(groups) + sorted({g for g, _ in fam} - set(groups))
        order = [(g, f) for g in groups for f in sorted((f for gg, f in fam if gg == g), key=lambda f: (-fam[(g, f)][0], f))]
        fam = {f: v for (g, f), v in fam.items()} if len({f for _, f in order}) == len(order) else {f"{g}|{f}": v for (g, f), v in fam.items()}
        keyed = not all(f in fam for _, f in order)
        used["S"].update(f for _, f in order)
        W, H, PT, PB = 433, 150, 14, 40
        ph = H - PT - PB
        val = (lambda g, f: fam[f"{g}|{f}"]) if keyed else (lambda g, f: fam[f])
        vmax = max((val(g, f)[0] for g, f in order), default=1) or 1
        groups_n = len({g for g, _ in order})
        gap = 10
        LX = 56  # row labels of the axis: what the code, the number and the group under each bar are
        bw = (W - LX - gap * (groups_n - 1)) / max(len(order), 1)
        out, x, last = [], float(LX), None
        for y, label in ((PT + ph + 12, code_label), (PT + ph + 23, "Lần chạy"), (H - 1, group_label)):
            out.append(text(LX - 6, y, label, 8, "end", INK2, 600))
        starts = {}
        for g, f in order:
            if last is not None and g != last:
                x += gap
            starts.setdefault(g, x)
            bad, n = val(g, f)
            cx = x + bw / 2
            fs = min(8.5, bw / 2.3)
            if bad:
                h = max(ph * bad / vmax, 2)
                out.append(bar_v(x + bw * .18, PT + ph, bw * .64, h, CRIT))
                out.append(text(cx, PT + ph - h - 3, fmt_n(bad), 8.5, "middle", INK, 700))
            else:
                out.append(f'<circle cx="{cx:.1f}" cy="{PT + ph - 6:.1f}" r="5" fill="{GOOD}"/>'
                           f'<path d="M{cx - 2.3:.1f},{PT + ph - 6:.1f} l1.6,1.7 l3,-3.4" stroke="#fff" stroke-width="1.4" fill="none"/>')
            out.append(text(cx, PT + ph + 12, f, fs, "middle", INK, 650))
            out.append(text(cx, PT + ph + 23, fmt_n(n), min(7.5, fs), "middle", INK3))
            x += bw
            last = g
            starts[g + "_end"] = x
        out.append(f'<line x1="{LX}" x2="{W}" y1="{PT + ph}" y2="{PT + ph}" stroke="{INK3}"/>')
        for g in groups:
            if g in starts:
                x0, x1 = starts[g], starts[g + "_end"]
                label = g if len(g) * 4.6 <= x1 - x0 else g[:max(int((x1 - x0) / 4.6) - 1, 1)] + "…"
                out.append(f'<line x1="{x0 + 2:.1f}" x2="{x1 - 2:.1f}" y1="{H - 8}" y2="{H - 8}" stroke="{INK3}"/>')
                out.append(text((x0 + x1) / 2, H - 1, label, 8, "middle", INK2, 700))
        return card("Trượt ở đâu", svg(W, H, "".join(out), "failed runs per scenario"),
                    f"Số lần chạy trượt {caption}.",
                    key="",
                    style="grid-column:1 / span 2;grid-row:2")

    def what_card(self, recs, used):
        """Requirement × scenario: number of failed runs, coloured by level."""
        cells, req_level = Counter(), {}
        for r in recs:
            for f in {(f["requirement"], f["level"]) for f in run_levels(r)[0]}:
                cells[(f[0], r["_family"])] += 1
                req_level[f[0]] = f[1]
        if not cells:
            return card("Trượt cái gì", f'<div style="font-size:11pt;color:{GOOD_TEXT};font-weight:650">Không có requirement nào trượt</div>',
                        style="grid-column:3 / span 2;grid-row:2 / span 2")
        reqs = sorted(req_level, key=lambda q: (list(LEVEL_COLOR).index(req_level[q]), -sum(v for (a, _), v in cells.items() if a == q)))
        cell_h = max(2.8, min(5.6, 72 / len(reqs)))  # every failed requirement is shown; rows get lower when many
        fams = sorted({f for _, f in cells}, key=lambda f: -sum(v for (_, b), v in cells.items() if b == f))
        used["R"].update(reqs)
        vmax = max(cells.values())
        head = "".join(f'<th style="font-size:8pt;font-weight:600;color:{INK2};padding:0 .8mm 1mm;text-align:center">{E(f)}</th>' for f in fams)
        body = ""
        for q in reqs:
            col = CRIT
            tds = ""
            for f in fams:
                v = cells.get((q, f), 0)
                bg = f"color-mix(in srgb, {col} {25 + 75 * v / vmax:.0f}%, white)" if v else GRID
                tds += (f'<td style="padding:.4mm"><div style="background:{bg};border-radius:3px;height:{cell_h:.1f}mm;display:flex;align-items:center;'
                        f'justify-content:center;font-size:{min(8.5, cell_h * 1.6):.1f}pt;font-weight:650;color:{"#fff" if v / vmax > .45 else INK}">{fmt_n(v) if v else ""}</div></td>')
            body += (f'<tr><td style="font-size:{min(8.5, cell_h * 1.6):.1f}pt;font-weight:600;padding-right:2mm;white-space:nowrap;width:1%">'
                     f'<i class="sw" style="background:{col};margin-right:1.2mm"></i>{E(q.replace("PP-SWR-", ""))}</td>{tds}</tr>')
        return card("Trượt cái gì", f'<div style="width:100%;align-self:flex-start"><table style="border-collapse:collapse;width:100%">'
                    f'<tr><th></th>{head}</tr>{body}</table></div>',
                    "Số lần chạy trượt, theo requirement (hàng) và tình huống (cột).",
                    key="",
                    style="grid-column:3 / span 2;grid-row:2 / span 2")

    def margin_card(self, k, used, rows=4):
        """Requirements that passed and have an upper limit: worst value over the runs as a share
        of the limit. The 80 % warning mark is the report's choice, not a requirement."""
        hr = self.d["headroom"].get(k, {})
        failed = {q for r in self.by_aspect.get(k, []) for q in [f["requirement"] for f in run_levels(r)[0]] + r.get("_oos", [])}
        best = {}
        for (rid, metric, op), (ratio, v, lim) in hr.items():
            if op == "<=" and rid not in failed and ratio <= 1 and (rid not in best or ratio > best[rid][0]):
                best[rid] = (ratio, v, lim, metric)
        items = sorted(((ratio, v, lim, rid, metric) for rid, (ratio, v, lim, metric) in best.items()), reverse=True)[:rows]
        cells = []
        for ratio, v, lim, rid, metric in items:
            used["R"].add(rid)
            unit = (re.search(r"\[(.+?)\]", metric) or [None, ""])[1]
            near = ratio >= WARN_MARK
            fill, track = (WARN, WARN_BG) if near else (ACCENT_SOFT, GRID)
            cells.append([self.details_link(rid, rid.replace("PP-SWR-", "")),
                          f'<span class="limit-bar" style="background:linear-gradient(90deg,{fill} {max(0, ratio) * 100:.4f}%,{track} 0)">'
                          f'{limit_percent(ratio)}</span>',
                          (f'<b style="color:{WARN_TEXT}">Sát ngưỡng</b>' if near else f'<span class="muted">Còn biên</span>'),
                          f'{precise(v)} / {precise(lim)} {E(unit)}', f'{precise(lim - v)} {E(unit)}'])
        body = (table(["ID", "Sử dụng", "Mức", "Đo / giới hạn", "Biên còn lại"], cells, "data-table margin-table") if cells
                else "Không có requirement đạt nào có giới hạn trên.")
        return card("Mức sử dụng giới hạn của các yêu cầu đạt", body,
                    ["Sử dụng = giá trị xấu nhất ÷ giới hạn trên; chỉ requirement đã đạt",
                     f"Sát ngưỡng: từ {WARN_MARK * 100:.0f} %, mốc cảnh báo do báo cáo chọn, không phải requirement"],
                    style="grid-column:1 / span 2;grid-row:3")

    def legend_card(self, used):
        """Meaning of every code shown on the slide, and only those, in full (never cut).
        The font is chosen so that the whole legend fits the column."""
        fams = sorted(used["S"], key=lambda f: (f[0], int(re.sub(r"\D", "", f) or 0), f))
        scen = [(E(f), self.names.get(f, "")) for f in fams]
        reqs = []
        for q in sorted(used["R"]):
            lv = severity.level(q) if q.startswith("PP-SWR") else severity.BLOCKER
            sq = f'<i class="sw" style="background:{LEVEL_COLOR.get(lv, GRAY)};margin-right:.8mm;width:2mm;height:2mm"></i>'
            reqs.append((E(q.replace("PP-SWR-", "")), (REQ_SHORT.get(q) or self.req_name(q, 42).split(" ", 1)[-1])))
        cars = [(E(p_), PROFILE_NAMES.get(p_, "")) for p_ in sorted(used["V"])]
        title_s = "TÌNH HUỐNG VÀ LỖI" if any(f.startswith(("F", "G")) for f in fams) else "TÌNH HUỐNG"

        blocks = [b for b in (scen, reqs, cars) if b]

        def block(title, rows):
            if not rows:
                return ""
            return (f'<div style="font-size:7pt;font-weight:700;color:{INK3};letter-spacing:.04em;margin:1.6mm 0 .4mm">{E(title)}</div>'
                    + "".join(f'<div style="display:grid;grid-template-columns:8.5mm 1fr;gap:1mm;font-size:7.8pt;line-height:1.15;margin:.3mm 0">'
                              f'<b style="white-space:nowrap">{c}</b><span style="color:{INK2}">{E(t)}</span></div>' for c, t in rows))
        levels = " ".join(f'<span style="white-space:nowrap"><i class="sw" style="background:{c};width:2mm;height:2mm"></i> {lv}</span>'
                          for lv, c in LEVEL_COLOR.items())
        if len(reqs) > 20:
            requirement_block = '<div style="margin:12px 0;font-size:8.5pt"><b>REQUIREMENT · PP-SWR-</b><p style="line-height:1.7">' + ' · '.join(self.details_link(q, q.replace('PP-SWR-', '')) for q in sorted(used['R'])) + '</p><span class="muted">Mở mã để xem tên và định nghĩa đầy đủ.</span></div>'
        else:
            requirement_block = block("REQUIREMENT (MÃ PP-SWR-XXX)", reqs)
        body = block(title_s, scen) + requirement_block + block("MẪU XE", cars)
        return (f'<div class="card fit" style="grid-column:5;grid-row:1 / span 4;background:{PANEL};--lf:7.6pt">'
                f'<h3>Chú giải</h3><div style="min-width:0">{body}</div></div>')

    def pass_fail_slide(self, k, title, focus, what, where_kpi="Tình huống có trượt", **where):
        """Pass or fail suite: verdict, where it fails, what fails, how close the passes were."""
        recs = self.by_aspect.get(k, [])
        if not recs:
            self.page(f"{k} · {title}", f"{focus}? Gồm: {what[0].lower() + what[1:]}.", "grid-template-columns:1fr", [card("Không có ca", f"Bộ {k} không có ca trong lần chạy này.")])
            return
        used = {"S": set(), "R": set(), "V": set()}
        st = aspect_stats(recs)
        label, cls = VERDICT[st["verdict"]]
        failing_fams = {r["_family"] for r in recs if run_levels(r)[0]}
        levels = Counter()
        for q in st["failed_req"]:
            levels[severity.level(q) if q.startswith("PP-SWR") else severity.BLOCKER] += 1
        head = [kpi("Requirement nội bộ", label, "có trượt BLOCKER" if cls == "v-fail" else "có trượt MAJOR" if cls == "v-major" else "trong phạm vi đã thử", cls),
                kpi("Lần chạy trượt", f"{fmt_n(st['runs'] - st['passed'])} / {fmt_n(st['runs'])}", f"{vn((st['runs'] - st['passed']) / st['runs'] * 100, 1)} % số lần chạy"),
                kpi(where_kpi, f"{len(failing_fams)} / {len({r['_family'] for r in recs})}", "có ít nhất một lần chạy trượt"),
                kpi("Requirement trượt", str(len(st["failed_req"])), ", ".join(f"{levels[lv]} {lv}" for lv in LEVEL_COLOR if levels[lv]) or "không có")]
        cards = [self.where_card(recs, used, **where), self.what_card(recs, used), self.margin_card(k, used)]
        prof = Counter(r.get("profile") for r in recs if run_levels(r)[0])
        prof_all = sorted({r.get("profile") for r in recs if r.get("profile")})
        used["V"].update(prof_all)
        oos = Counter(q for r in recs for q in r.get("_oos", []))
        line = (f'<div style="grid-column:1 / span 4;grid-row:4;font-size:8pt;color:{INK2};line-height:1.45;align-self:end">'
                f'<div><b style="color:{INK}">Lần chạy trượt theo mẫu xe:</b> ' + ", ".join(f"{p_}: {prof.get(p_, 0)}" for p_ in prof_all) + "</div>"
                + (f'<div><b style="color:{INK}">Trượt ngoài phạm vi chấm (không tính kết luận):</b> '
                   + ", ".join(f"{q.replace('PP-SWR-', '')}: {n} lần" for q, n in oos.most_common()) + "</div>" if oos else "") + "</div>")
        used["R"].update(oos)
        self.page(f"{k} · {title}", f"{focus}? Gồm: {what[0].lower() + what[1:]}.", "grid-template-columns:repeat(4,1fr) 260px;grid-template-rows:auto 1.3fr 1fr auto",
                  head + cards + [line, self.legend_card(used)])

    def b2_slide(self, title, focus, what):
        """B2 by test of the documents (Software Qualification Test Specification 5.1)."""
        from eval import compare
        recs = self.by_aspect.get("B2", [])
        tests = regulatory_tests()
        runs = [[] for _ in tests]
        for r in recs:
            for i in test_of(r["_case"], tests):
                runs[i].append(r)
        status = []
        for t, rs in zip(tests, runs):
            fails = Counter(f["requirement"] for r in rs for f in run_levels(r)[0])
            ok = sum(not run_levels(r)[0] for r in rs)
            levels = {severity.level(q) if q.startswith("PP-SWR") else severity.BLOCKER for q in fails}
            state = "none" if not rs else "pass" if ok == len(rs) else "fail"
            status.append((t, rs, ok, fails, state, levels))
        sym = {"pass": ("ok", "✓"), "fail": ("ko", "✕"), "none": ("nk", "–")}
        rows = []
        for t, rs, ok, fails, state, levels in status:
            cls, mark = sym[state]
            if state == "none":
                right = f'<span style="color:{INK3}">chưa có lần chạy</span>'
            else:
                right = f'<b>{fmt_n(ok)} / {fmt_n(len(rs))}</b> <span style="color:{INK3}">lần chạy đạt</span>'
            why = ""
            if fails:
                where = Counter(f'{r["_family"]} {r["_case"].get("anchor") or ""}'.strip() for r in rs if run_levels(r)[0])
                why = ("trượt " + ", ".join(f"{q.replace('PP-SWR-', '')} {REQ_SHORT.get(q, '')}".strip() for q, _ in fails.most_common(2))
                       + ". Ở " + ", ".join(f"{c} ({n} lần)" for c, n in where.most_common(3)))
            rows.append(f'<div style="display:grid;grid-template-columns:5mm 1fr auto;gap:0 2mm;padding:1mm 0;border-bottom:1px solid {GRID};align-items:start">'
                        f'<span class="{cls}" style="margin-top:.4mm">{mark}</span>'
                        f'<div><b style="font-size:9pt">{E(t["name"])}</b><div style="font-size:7.3pt;color:{INK3}">{E(t["source"])}</div>'
                        + (f'<div style="font-size:7.5pt;color:{CRIT_TEXT}">{E(why)}</div>' if why else "")
                        + f'</div><div style="font-size:8.5pt;text-align:right;white-space:nowrap">{right}</div></div>')
        per_doc = []
        for d in DOCS:
            mine = [st for t, _, _, _, st, _ in status if d in t["docs"]]
            n_ok, n_run = sum(st == "pass" for st in mine), sum(st != "none" for st in mine)
            per_doc.append((d, n_ok, n_run, len(mine)))
        doc_line = "".join(
            f'<div style="flex:1;border-radius:4px;padding:1.2mm 2mm;background:{GOOD_BG if n_ok == n_all else CRIT_BG if n_run > n_ok else NEUTRAL_BG}">'
            f'<div style="font-size:7.5pt;color:{INK2}">{E(d)}</div><div style="font-size:11pt;font-weight:680">{n_ok} / {n_all} bài thử đạt</div>'
            f'<div style="font-size:7pt;color:{INK3}">{n_all - n_run} bài chưa có lần chạy</div></div>' for d, n_ok, n_run, n_all in per_doc)
        table = card("Kết quả theo bài thử của văn bản",
                     f'<div style="width:100%;align-self:flex-start;display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;'
                     f'grid-template-rows:repeat({math.ceil(len(rows) / 2)},auto);column-gap:8mm">{"".join(rows)}</div>',
                     "Bài thử dùng chung được dẫn chiếu ở nhiều văn bản; không cộng tổng các nhóm. Đạt khi mọi lần chạy đạt requirement trong phạm vi.", style="grid-column:span 4")
        if not recs:
            self.page(f"B2 · {title}", f"{focus}? Gồm: {what[0].lower() + what[1:]}.", "grid-template-columns:1fr", [card("Không có ca", "Bộ B2 không có ca trong lần chạy này.")])
            return
        st = aspect_stats(recs)
        label, cls = VERDICT[st["verdict"]]
        ncap = compare.ncap_points({"cases": self.d["cases"], "records": {(r["case"], r["seed"]): r for r in recs}})
        if ncap["points"] is None:
            ncap_kpi = kpi("Euro NCAP LSS", "–", "chưa có hàng của lưới chuẩn")
        else:
            missing = len(ncap["lines_without_rows"])
            ncap_kpi = kpi("Điểm theo protocol LSS", f'{vn(ncap["points"])} / {vn(ncap["max"])}',
                           (f"{missing} dòng chưa có lần chạy; " if missing else "") + "LSS v4.3 · SA v10.4.1 · mô phỏng")
        passed_tests = sum(x[4] == "pass" for x in status)
        ran_tests = sum(x[4] != "none" for x in status)
        head = [kpi("Requirement nội bộ", label, "có trượt BLOCKER" if cls == "v-fail" else "có trượt MAJOR" if cls == "v-major" else "trong phạm vi đã thử", cls),
                kpi("Bài thử đạt", f"{passed_tests} / {len(tests)}", f"{len(tests) - ran_tests} bài thử chưa có lần chạy"),
                ncap_kpi,
                kpi("Lần chạy đạt", f"{vn(st['passed'] / st['runs'] * 100, 1)} %", f"{fmt_n(st['runs'] - st['passed'])} / {fmt_n(st['runs'])} lần có trượt")]
        docs = f'<div style="grid-column:span 4;display:flex;gap:3mm">{doc_line}</div>'
        self.page(f"B2 · {title}", "Đánh giá mô phỏng theo R79 (OJ 2025/3), R171 (01 series, OJ 2025/1899), EU 2021/646 · LSS v4.3 / SA v10.4.1", "grid-template-columns:repeat(4,1fr);grid-template-rows:auto auto 1fr",
                  head + [docs, table])

    def suite_head(self, k):
        recs = self.by_aspect.get(k, [])
        st = aspect_stats(recs)
        label, cls = VERDICT[st['verdict']]
        if not recs: label, cls = 'CHƯA CHẠY', ''
        return [kpi('Kết luận trên phần đã chạy', label, 'theo requirement trong phạm vi', cls),
                kpi('Lần chạy', fmt_n(len(recs)), 'ca × seed; ca đã gồm mẫu xe'),
                kpi('Có requirement trượt', fmt_n(st['runs'] - st['passed']), 'số lần chạy'),
                kpi('Requirement trượt', str(len(st['failed_req'])), 'mã duy nhất trong bộ')]

    def b4_slide(self):
        recs = self.by_aspect.get('B4', [])
        planned, done = defaultdict(Counter), defaultdict(list)
        codes = defaultdict(set)
        for f, n in self.planned_by_family.items():
            if f.startswith(('F', 'G')):
                g = self.fault_group.get(f, 'Chưa phân nhóm')
                planned[g][f] += n
                codes[g].add(f)
        controls = []
        for r in recs:
            f = r['_family']
            if f.startswith(('F', 'G')):
                g = self.fault_group.get(f, 'Chưa phân nhóm')
                done[g].append(r)
                codes[g].add(f)
            else:
                controls.append(r)
        rows = []
        for g in sorted(codes):
            rs = done[g]
            bad = sum(bool(run_levels(r)[0]) for r in rs)
            n = sum(planned[g].values())
            state = 'Chưa chạy' if not rs else 'Có trượt' if bad else 'Hoàn tất' if len(rs) == n else 'Đang có dữ liệu'
            cls = 'neutral' if not rs or len(rs) < n and not bad else 'bad' if bad else 'good'
            rows.append([f'<b>{E(g)}</b> <span class="muted">{E(", ".join(sorted(codes[g])))}</span>',
                         fmt_n(n), fmt_n(len(rs)), fmt_n(max(0, n-len(rs))), str(bad), f'<span class="status {cls}">{state}</span>'])
        matrix = table(['Nhóm lỗi', 'Kế hoạch', 'Đã chạy', 'Chưa chạy', 'Có trượt', 'Thực thi'], rows)
        control_rows = []
        for f in sorted({r['_family'] for r in controls}):
            rs = [r for r in controls if r['_family'] == f]
            control_rows.append([E(self.label(f, 100)), fmt_n(len(rs)), str(sum(bool(run_levels(r)[0]) for r in rs))])
        control = table(['Tình huống không bơm lỗi', 'Đã chạy', 'Có trượt'], control_rows) if control_rows else 'Chưa có ca không bơm lỗi trong phần đã chạy.'
        self.page('B4 · Robustness', 'Phủ các nhóm lỗi bơm; tách riêng ca không bơm lỗi',
                  'grid-template-columns:repeat(4,minmax(0,1fr));grid-template-rows:auto 1fr auto',
                  self.suite_head('B4') + [card('Nhóm lỗi × trạng thái thực thi', matrix, 'Đơn vị: lần chạy theo manifest sinh ca.', style='grid-column:1/-1'),
                  card('Ca không bơm lỗi', control, 'Nhóm riêng trong B4; không cộng vào số ca bơm lỗi.', style='grid-column:1/-1')])

    def b5_slide(self):
        recs = self.by_aspect.get('B5', [])
        rules = [('PP-SWR-030', 'Lái / lái có giới hạn', 'Chọn đúng chức năng được yêu cầu'),
                 ('PP-SWR-005', 'Cua vượt aysmax', 'Giữ HWA và path'),
                 ('PP-SWR-006', 'Cua vượt aysmax', 'a_y path đáp ứng giới hạn yêu cầu'),
                 ('PP-SWR-007', 'Cua vượt aysmax', 'Bật cờ giới hạn trước khi đè vạch'),
                 ('PP-SWR-063', 'Làn không đủ khoảng trống', 'Báo lane_too_narrow'),
                 ('PP-SWR-089', 'ELK REQUEST quá muộn', 'Không khởi động can thiệp')]
        rows = []
        for rid, condition, expected in rules:
            ok = bad = not_observed = 0
            for r in recs:
                cs = [c for c in r.get('_behavior', []) if c['id'] == rid and c.get('applicable')
                      and (r.get('scope') is None or rid in r['scope'])]
                if not cs:
                    not_observed += 1
                elif all(c.get('passed') for c in cs): ok += 1
                else: bad += 1
            rows.append([f'{self.details_link(rid, rid.replace("PP-SWR-", ""))}<br>{E(condition)}', E(expected),
                         f'<b class="good">{fmt_n(ok)}</b>', f'<b class="{"bad" if bad else "neutral"}">{fmt_n(bad)}</b>', fmt_n(not_observed)])
        used = {'S': set(), 'R': set(), 'V': set()}
        reqs = self.what_card(recs, used).replace('grid-column:3 / span 2;grid-row:2 / span 2', 'grid-column:3 / span 2;grid-row:2')
        comparison = card('Hành vi mong đợi → quan sát qua phép kiểm', table(['Điều kiện / ID', 'Mong đợi', 'Phù hợp', 'Sai lệch', '—'], rows),
                          'Đếm lần chạy. —: không áp dụng hoặc chưa có phép kiểm; không suy ra hành vi từ nhãn ca.', style='grid-column:1 / span 2;grid-row:2')
        refs = self.details_link('requirements', 'Mở tên đầy đủ và bảng requirement')
        self.page('B5 · Degradation and refusal', 'Đối chiếu hành vi bằng các phép kiểm đã lưu trong log',
                  'grid-template-columns:repeat(4,minmax(0,1fr));grid-template-rows:auto 1fr auto',
                  self.suite_head('B5') + [comparison, reqs, f'<div class="definitions">{refs}</div>'])

    def b6_slide(self):
        """Comfort targets (performance, no pass mark): per target, where the planner is least
        comfortable. One small multiple per target, one row per scenario, worst scenarios first."""
        recs = self.by_aspect.get('B6', [])
        series = defaultdict(list)  # (id, metric) -> [(value, run)]
        for r in recs:
            for t in (r.get('result') or {}).get('targets', []):
                if t['id'] in COMFORT_TARGETS and isinstance(t.get('value'), (int, float)) and math.isfinite(t['value']):
                    series[(t['id'], t['metric'])].append((t['value'], r))
        metrics_of = Counter(rid for rid, _ in series)
        cards, rows = [], []
        for (rid, metric), samples in sorted(series.items(), key=lambda kv: (COMFORT_TARGETS.index(kv[0][0]), kv[0][1])):
            name, fallback_unit = COMFORT_LABELS[rid]
            if metrics_of[rid] > 1:
                name = METRIC_SHORT.get(metric, metric)
            unit = next((t.get('unit') for _, r in samples[:1] for t in r['result']['targets'] if t['id'] == rid and t.get('unit')), None) or fallback_unit
            high = rid in LARGER_IS_BETTER
            pick = min if high else max
            by_fam = defaultdict(list)
            for v, r in samples:
                by_fam[r['_family']].append((v, r))
            fams = sorted(by_fam, key=lambda f: pick(v for v, _ in by_fam[f]), reverse=not high)
            shown = fams[:4]
            chart_rows = [(self.label(f, 20), [v for v, _ in by_fam[f]], pick(v for v, _ in by_fam[f])) for f in shown]
            cap = (f"{rid} · {fmt_n(len(samples))} lần chạy · {'↑ cao' if high else '↓ thấp'} hơn tốt hơn"
                   f" · {len(shown)}/{len(fams)} tình huống bất lợi nhất")
            cards.append(card(f"{name} [{unit}]", range_rows(chart_rows, unit), cap))
            worst_v, worst_r = pick(samples, key=lambda x: x[0])
            values = [v for v, _ in samples]
            rows.append([rid.replace('PP-SWR-', ''), E(name), 'Cao hơn' if high else 'Thấp hơn', fmt_n(len(values)),
                         f'{precise(float(np.median(values)))} {E(unit)}', f'<b>{precise(worst_v)} {E(unit)}</b>',
                         E(self.case_name(worst_r)), self.details_link('run-' + worst_r['case'] + '-' + str(worst_r['seed']), 'Xem ca')])
        if not cards:
            self.page('B6 · Comfort', 'Chỉ đo hiệu năng; không có ngưỡng đạt', 'grid-template-columns:1fr',
                      [card('Chưa có dữ liệu', 'Không có lần chạy nào trong bộ B6 cho các chỉ số độ êm.')])
            return
        cols = min(3, len(cards))
        table_card = card('Số liệu của từng chỉ số', table(['ID', 'Chỉ số', 'Tốt hơn khi', 'Lần chạy', 'Trung vị', 'Bất lợi nhất', 'Ca bất lợi nhất', 'Bằng chứng'], rows, 'data-table comfort-table'),
                          'Bảng số liệu của các biểu đồ trên; trung vị và bất lợi nhất tính qua mọi lần chạy của chỉ số.', style='grid-column:1/-1')
        self.page('B6 · Comfort',
                  'Chỉ đo hiệu năng, không có ngưỡng đạt · mỗi hàng một tình huống: vạch xám = khoảng qua các lần chạy, chấm xám = trung vị, chấm xanh = bất lợi nhất',
                  f'grid-template-columns:repeat({cols},minmax(0,1fr));grid-template-rows:repeat({math.ceil(len(cards) / cols)},minmax(0,1fr)) auto',
                  cards + [table_card])

    def b7_slide(self):
        recs = self.by_aspect.get('B7', [])
        profiles = sorted({r.get('profile') for r in recs if r.get('profile')})
        signatures = [Counter(profile_signature(r) for r in recs if r['profile'] == p) for p in profiles]
        same = len(profiles) > 1 and all(x == signatures[0] for x in signatures[1:])
        comparability = ('Cùng tập tham số tình huống và seed giữa các mẫu xe.' if same else
                         'Tập tham số tình huống/seed chưa đồng nhất hoặc chưa đủ mẫu xe; số liệu dưới đây là tổng hợp riêng từng xe.')
        rows, offsets = [], []
        for p in profiles:
            rs = [r for r in recs if r['profile'] == p]
            n_ok = sum(not run_levels(r)[0] for r in rs)
            vals = [info(r, 'vehicle_offset_max_m') for r in rs]
            vals = [v for v in vals if isinstance(v, (float,int)) and math.isfinite(v)]
            offsets.append(max(vals) if vals else None)
            rows.append([f'<b>{E(p)}</b> · {E(PROFILE_NAMES.get(p,p))}', f'{n_ok} / {len(rs)}',
                         f'<span class="status {"good" if n_ok == len(rs) else "bad"}">{vn(100*n_ok/len(rs),1)} %</span>'])
        chart = offset_chart(profiles, offsets)
        self.page('B7 · Flexibility', 'Cùng một bản build và calibration trên các mẫu xe',
                  'grid-template-columns:repeat(4,minmax(0,1fr));grid-template-rows:auto 1fr auto',
                  self.suite_head('B7') + [card('Tỷ lệ đạt theo mẫu xe', table(['Mẫu xe', 'Đạt / đã chạy', 'Tỷ lệ'], rows), comparability, style='grid-column:span 2'),
                  card('Lệch ngang lớn nhất của xe [m]', chart, 'Trị tuyệt đối khoảng cách từ tâm cầu sau tới đường tham chiếu thật. Màu nhấn chỉ nhận diện cực đại.', style='grid-column:span 2'),
                  card('Requirement trượt', self.failure_summary(recs), 'Số lần chạy trong phạm vi; ID mở tên đầy đủ.', style='grid-column:1/-1')])

    def failure_summary(self, recs):
        counts = aspect_stats(recs)['failed_req']
        if not counts: return 'Không có requirement trượt.'
        return '<div class="failure-summary">' + ''.join(f'<span>{self.details_link(q, self.req_name(q,60))} <b class="bad">{n}</b></span>' for q,n in counts.most_common()) + '</div>'

    def b8_slide(self):
        """Compute time (performance, no pass mark): how the cycle time sits against the planner
        period, and where it is longest. Wall clock of the development machine (8.2)."""
        hist = np.zeros(len(COMPUTE_BINS_MS) - 1)
        p99s, maxes = [], []
        for r in self.by_aspect.get('B8', []):
            h = info(r, 'compute_hist')
            if h is not None:
                hist += np.asarray(h)
            v = target(r, 'PP-SWR-016', 'Thời gian tính p99')
            if v is not None:
                p99s.append((v, r))
            m = target(r, 'PP-SWR-016', 'Thời gian tính lớn nhất')
            if m is not None:
                maxes.append((m, r))
        total = hist.sum()
        if not total:
            self.page('B8 · Compute', 'Chỉ đo hiệu năng; không có ngưỡng đạt', 'grid-template-columns:1fr',
                      [card('Chưa có dữ liệu', 'Lần chạy này không ghi histogram thời gian chu kỳ.')])
            return
        edges = COMPUTE_BINS_MS
        cum = np.cumsum(hist)
        bound = lambda q: float(edges[min(int(np.searchsorted(cum, q * total)), len(hist) - 1) + 1])
        p50, p99 = bound(.5), bound(.99)
        period = PLANNER_PERIOD_US / 1000
        k_period = int(np.searchsorted(edges, period))  # first edge at or above the period
        over = float(hist[k_period:].sum())
        slowest = max(maxes, key=lambda x: x[0]) if maxes else None
        nz = np.flatnonzero(hist)
        left, right = max(int(nz[0]) - 1, 0), min(max(int(nz[-1]) + 2, k_period + 2), len(hist))
        span = edges[left:right + 1]
        ticks = [(v, precise(v)) for v in (.01, .03, .1, .3, 1, 3, 10, 30, 100, 300, 1000) if span[0] <= v <= span[-1]]
        dist = histogram(hist[left:right], span, W=560, H=230, log=True, ticks=ticks, color=ACCENT,
                         limits=[(p99, f"p99 ≤ {precise(p99)}"), (period, f"chu kỳ {precise(period)}")],
                         xlabel='Thời gian một chu kỳ [ms], thang log', ylabel='số chu kỳ')
        by_fam = defaultdict(list)
        for v, r in p99s:
            by_fam[r['_family']].append(v)
        fam_items = sorted(((max(vs), f) for f, vs in by_fam.items()), reverse=True)[:8]
        bars = ranked_ref([(self.label(f, 26), v, f"{self.label(f, 80)}: p99 lớn nhất {precise(v)} ms qua {len(by_fam[f])} lần chạy")
                           for v, f in fam_items], ref=period, ref_label=f"chu kỳ {precise(period)} ms", unit=" ms")
        rows = [[E(self.case_name(r)), f'{precise(v)} ms', f'{precise(target(r, "PP-SWR-016", "Thời gian tính lớn nhất") or float("nan"))} ms',
                 self.details_link('run-' + r['case'] + '-' + str(r['seed']), 'Xem ca')]
                for v, r in sorted(p99s, key=lambda x: x[0], reverse=True)[:4]]
        m = self.d['manifest']
        env = m.get('environment', {})
        how = [f"Đồng hồ thật của máy phát triển ({env.get('platform') or 'chưa ghi nhận'}), gồm adapter ctypes; không đại diện ECU trên xe.",
               f"Chạy song song {m.get('jobs', 'chưa ghi nhận')} tiến trình ({m.get('start_method', 'chưa ghi nhận')}); "
               "giá trị lớn hơn khi chạy một mình.",
               "Chỉ so với lần chạy cùng máy và cùng số tiến trình (Software Qualification Test Specification 8.2).",
               f"Chu kỳ {precise(period)} ms là chu kỳ planner 40 Hz, chỉ để tham chiếu, không phải ngưỡng.",
               "Trung vị và p99 gộp là cận trên của bin histogram chứa phân vị đó."]
        self.page('B8 · Compute', 'Chỉ đo hiệu năng, không có ngưỡng đạt · thời gian tính mỗi chu kỳ planner trên máy SIL',
                  'grid-template-columns:repeat(4,minmax(0,1fr));grid-template-rows:auto minmax(0,1fr) auto',
                  [kpi('Trung vị gộp', f'≤ {precise(p50)} ms', f'{fmt_n(total)} chu kỳ của mọi lần chạy'),
                   kpi('p99 gộp', f'≤ {precise(p99)} ms', 'PP-SWR-016, thấp hơn tốt hơn'),
                   kpi('Chu kỳ lâu nhất', f'{precise(slowest[0])} ms' if slowest else '—', E(self.case_name(slowest[1])) if slowest else ''),
                   kpi(f'Chu kỳ vượt {precise(float(edges[k_period]))} ms', fmt_n(over), f'{vn(100 * over / total, 2)} % số chu kỳ'),
                   card('Phân bố thời gian chu kỳ', dist, 'Gộp mọi chu kỳ của mọi lần chạy; vạch dọc: p99 gộp và chu kỳ planner.', style='grid-column:span 2'),
                   card('p99 theo tình huống [ms]', bars, f'p99 lớn nhất qua các lần chạy của tình huống; {len(fam_items)}/{len(by_fam)} tình huống chậm nhất.',
                        style='grid-column:span 2'),
                   card('Các lần chạy có p99 lớn nhất', table(['Ca / mẫu xe', 'p99', 'Lâu nhất', 'Bằng chứng'], rows, 'data-table compute-table'),
                        'p99 và chu kỳ lâu nhất của từng lần chạy.', style='grid-column:span 2'),
                   card('Cách đọc', '<ul class="howto">' + ''.join(f'<li>{E(x)}</li>' for x in how) + '</ul>', style='grid-column:span 2')])

    def metadata_slide(self):
        m = self.d['manifest']
        lib = (m.get('libraries') or [{}])[0]
        build = lib.get('build') or {}
        version = lib.get('pp_version')
        version_source = 'manifest của lượt chạy'
        if not version and self.d['b0']:
            version = next((c.get('detail') for c in self.d['b0']['checks'] if c['id']=='C2.version'), None)
            version_source = 'bằng chứng B0 được chọn; lượt này chưa lưu manifest riêng'
        fingerprint = hashlib.sha256(json.dumps(self.d['generation'].get('inputs',{}),sort_keys=True).encode()).hexdigest()[:16]
        env = m.get('environment',{})
        rows = [('Run ID / thư mục dữ liệu', self.run_id), ('Bắt đầu / kết thúc', f'{m.get("started", "Chưa ghi nhận")} / {m.get("finished", "Chưa ghi nhận")}'),
                ('Tạo báo cáo', self.generated), ('Phiên bản trình bày', REPORT_VERSION),
                ('Planner', version or 'Chưa ghi nhận'), ('Nguồn nhận diện planner', version_source),
                ('SHA-256 binary', lib.get('sha256') or 'Chưa ghi nhận cho lượt chạy này'),
                ('Benchmark commit', (m.get('git') or {}).get('commit') or 'Chưa ghi nhận cho lượt chạy này'),
                ('Dấu vân tay bộ đầu vào', fingerprint + ' (SHA-256 của danh sách hash trong generation)'),
                ('Calibration', build.get('calibration') or self.d['generation'].get('inputs',{}).get('planner/calibration/calibration.yaml','Chưa ghi nhận')),
                ('CPU / OS / workers', f'{env.get("processor") or env.get("cpu") or "Chưa ghi nhận"} / {env.get("platform") or "Chưa ghi nhận"} / {m.get("jobs", "Chưa ghi nhận")}'),
                ('Phạm vi', 'Vòng kín SIL · dữ liệu kết quả hiện có; không tự bổ sung kết quả chưa chạy')]
        body = table(['Trường', 'Giá trị / nguồn'], [[E(k),E(str(v))] for k,v in rows])
        self.page('Thông tin báo cáo', 'Nhận diện dữ liệu, phần mềm và môi trường đo', 'grid-template-columns:1fr;grid-template-rows:1fr auto',
                  [card('Thông tin truy xuất', body), card('Dữ liệu gốc',
                   f'<a href="{self.href(self.d["folder"] / "results.jsonl")}">results.jsonl</a> · '
                   f'<a href="{self.href(self.d["conformance_path"])}">Bằng chứng B0</a> · {self.details_link("requirements", "Requirement và các ca được dẫn chiếu")}',
                   'Giữ nguyên dữ liệu chạy; trường không có trong hồ sơ được hiển thị là chưa ghi nhận.')])

    def build(self):
        self.overview()
        self.b0_slide()
        a = {k:(t,f,w) for k,t,f,w in ASPECTS}
        self.pass_fail_slide('B1', *a['B1'])
        self.b2_slide(*a['B2'])
        self.pass_fail_slide('B3', *a['B3'])
        self.b4_slide()
        self.b5_slide()
        self.b6_slide()
        self.b7_slide()
        self.b8_slide()
        self.metadata_slide()

    def details_html(self):
        body = ['<h1>Bằng chứng và định nghĩa</h1>', f'<p>{E(self.run_id)} · báo cáo {REPORT_VERSION} · {E(self.generated)}</p>']
        body.append('<h2>B0 · API / Contract / Integration</h2>')
        for c in (self.d['b0'] or {}).get('checks', []):
            body.append(f'<section id="{E(c["id"])}"><h3>{E(c["id"])} · {E(c.get("title", ""))}</h3>'
                        f'<p><b>Trạng thái:</b> {E(c["status"])} · <b>Nguồn:</b> {E(c.get("source", "Không ghi nguồn"))}</p>'
                        f'<p><b>Bằng chứng / lý do:</b> {E(c.get("detail") or "Phép kiểm trả trạng thái trên; không có chi tiết bổ sung.")}</p></section>')
        body.append('<h2 id="requirements">Requirement</h2>')
        for rid, name in sorted(self.srs.items()):
            body.append(f'<section id="{E(rid)}"><h3>{E(rid)}</h3><p>{E(name)}</p></section>')
        body.append('<h2>Các lần chạy được dẫn chiếu</h2>')
        # Only exported references, not thousands of unused results.
        referenced = set(re.findall(r'#(run-[^"<>]+)', ''.join(self.pages)))
        for r in self.d['records']:
            anchor = 'run-'+r['case']+'-'+str(r['seed'])
            if html.escape(anchor) not in referenced: continue
            details = {'case': r['case'], 'seed': r['seed'], 'profile':r.get('profile'),
                       'parameters':r['_case'].get('parameters'), 'targets':(r.get('result') or {}).get('targets'),
                       'failures_in_scope':r.get('_fail'), 'rerun':r.get('rerun'), 'mcap':r.get('mcap')}
            body.append(f'<section id="{E(anchor)}"><h3>{E(r["case"])} · seed {r["seed"]}</h3><pre>{E(json.dumps(details,ensure_ascii=False,indent=2))}</pre></section>')
        return ('<!doctype html><html lang="vi"><meta charset="utf-8"><title>Bằng chứng dashboard</title>'
                f'<style>body{{max-width:1000px;margin:40px auto;padding:0 24px;font:15px/1.5 -apple-system,Arial;color:{INK}}}section{{border-top:1px solid {RULE};padding:12px 0}}section:target{{background:{WARN_BG}}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}h2{{margin-top:40px}}</style>'
                + ''.join(body) + '</html>')

    def html(self):
        total = len(self.pages)
        return (f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
                f'<title>Benchmark Report</title><style>{CSS_VARS}{CSS}{REVIEW_CSS}</style></head><body>'
                + "".join(p.replace("{TOTAL}", str(total)) for p in self.pages) + FIT_SCRIPT + "</body></html>")


def write(folder: Path, out: Path | None = None, generation: Path | None = None,
          conformance: Path | None = None) -> Path:
    report = Report(load(folder, generation, conformance))
    out = Path(out) if out else Path(folder) / "report.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    report.out_dir = out.parent
    report.details_name = out.stem + "-details.html"
    report.build()
    out.write_text(report.html(), encoding="utf-8")
    (out.parent / report.details_name).write_text(report.details_html(), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path, help="eval.suite output folder")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--generation", type=Path, help="eval.generate manifest, for a suite that stopped early")
    parser.add_argument("--conformance", type=Path, help="B0 result kept outside the folder")
    args = parser.parse_args()
    print(write(args.folder, args.out, args.generation, args.conformance))


if __name__ == "__main__":
    main()
