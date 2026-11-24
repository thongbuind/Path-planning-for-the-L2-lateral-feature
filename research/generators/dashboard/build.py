"""Sinh dashboard so sánh generator T7 (PP-TS-031, IMPLEMENTATION-PLAN.md GĐ 5.4) từ techniques.json.

Một file HTML tự chứa: CSS, JS và dữ liệu nằm trong file, không tải gì từ mạng, có chế độ sáng và tối.
Không có hạng, điểm tổng hay ô "tốt nhất": màu ô chỉ cho biết hiệu so với mốc tốt hơn, xấu hơn hay trong
dung sai. Dữ liệu nháp (plan chưa khóa, chạy không --record) thì mọi trang có nhãn "nháp".

    python3 -m eval.campaign PP-TS-031          # ghi dashboard/techniques.json
    python3 research/generators/dashboard/build.py
"""

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

STYLE = r"""
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--ring:rgba(11,11,11,.10);--neutral:#f0efec;
--b1:#cde2fb;--b2:#86b6ef;--b3:#2a78d6;--r1:#f8d3d2;--r2:#ee9493;--r3:#d03b3b;
--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--warn:#fab219;--crit:#d03b3b;--draft:#fff3cd}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;--page:#0d0d0d;
--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;
--ring:rgba(255,255,255,.10);--neutral:#383835;--b1:#184f95;--b2:#256abf;--b3:#5598e7;--r1:#5c2120;
--r2:#9e3433;--r3:#e66767;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--draft:#4a3b00}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;
--muted:#898781;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--neutral:#383835;--b1:#184f95;
--b2:#256abf;--b3:#5598e7;--r1:#5c2120;--r2:#9e3433;--r3:#e66767;--s1:#3987e5;--s2:#d95926;--s3:#199e70;
--draft:#4a3b00}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
header{padding:16px 20px 8px;max-width:1400px;margin:auto}
h1{font-size:20px;margin:0 0 4px}h2{font-size:17px;margin:24px 0 8px}h3{font-size:15px;margin:16px 0 6px}
.sub{color:var(--ink2);margin:0 0 8px}
.draft{background:var(--draft);border:1px solid var(--warn);border-radius:6px;padding:8px 12px;margin:8px 0;font-weight:600}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0}
.bar label{color:var(--ink2)}
select,button{font:inherit;color:var(--ink);background:var(--surface);border:1px solid var(--axis);border-radius:6px;padding:4px 8px}
nav{display:flex;flex-wrap:wrap;gap:4px;max-width:1400px;margin:auto;padding:0 20px}
nav button{border:1px solid var(--ring);background:transparent;cursor:pointer}
nav button[aria-selected=true]{background:var(--surface);border-color:var(--axis);font-weight:600}
main{max-width:1400px;margin:auto;padding:0 20px 40px}
.card{background:var(--surface);border:1px solid var(--ring);border-radius:8px;padding:12px 16px;margin:12px 0;overflow-x:auto}
table{border-collapse:collapse;font-variant-numeric:tabular-nums;width:100%}
th,td{border-bottom:1px solid var(--grid);padding:4px 8px;text-align:left;vertical-align:top}
th{color:var(--ink2);font-weight:600;position:sticky;top:0;background:var(--surface)}
td.num{text-align:right}
.chip{display:inline-block;border-radius:4px;padding:1px 6px;white-space:nowrap}
.better{background:var(--b2);color:#0b0b0b}.worse{background:var(--r2);color:#0b0b0b}
.within{background:var(--neutral)}.few{border:1px dashed var(--muted);color:var(--ink2)}
.range{display:block;color:var(--muted);font-size:12px}
.flag{display:inline-block;margin-right:4px;padding:0 5px;border-radius:4px;font-size:12px;font-weight:600}
.flag.red{background:var(--crit);color:#fff}.flag.amber{background:var(--warn);color:#0b0b0b}
.muted{color:var(--muted)}.note{color:var(--ink2);font-size:13px}
footer{max-width:1400px;margin:auto;padding:0 20px 40px;color:var(--ink2);font-size:12px}
svg text{fill:var(--ink2);font-size:11px}
#tip{position:fixed;pointer-events:none;background:var(--surface);color:var(--ink);border:1px solid var(--axis);
border-radius:6px;padding:6px 8px;font-size:12px;display:none;max-width:360px;box-shadow:0 2px 8px rgba(0,0,0,.15);z-index:9}
.legend{display:flex;gap:12px;flex-wrap:wrap;margin:4px 0;color:var(--ink2);font-size:12px}
.legend span::before{content:"";display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px;background:var(--c)}
a{color:var(--s1)}
"""

SCRIPT = r"""
const D = JSON.parse(document.getElementById('data').textContent);
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt = (v, d = 3) => v == null || !isFinite(v) ? '—' : (Math.abs(v) >= 1000 ? v.toFixed(0) : Number(v.toPrecision(d)).toString());
const pct = v => v == null || !isFinite(v) ? '—' : (100 * v).toFixed(1) + ' %';
const LABEL = {better: '▲ tốt hơn', worse: '▼ xấu hơn', within: '≈ trong dung sai', few: 'ít dữ liệu'};
const GROUPS = ['An toàn', 'Bám làn và cảm nhận người lái', 'Thời gian tính'];
let part = Object.keys(D.parts).includes('test') ? 'test' : Object.keys(D.parts)[0];
let scope = 'default';
const tip = $('#tip');
function showTip(e, html) { tip.innerHTML = html; tip.style.display = 'block';
  const x = Math.min(e.clientX + 14, innerWidth - 370); tip.style.left = x + 'px'; tip.style.top = (e.clientY + 14) + 'px'; }
document.addEventListener('mouseover', e => { const t = e.target.closest('[data-tip]'); if (t) showTip(e, t.dataset.tip); });
document.addEventListener('mousemove', e => { if (tip.style.display === 'block' && e.target.closest('[data-tip]')) showTip(e, e.target.closest('[data-tip]').dataset.tip); });
document.addEventListener('mouseout', e => { if (e.target.closest('[data-tip]')) tip.style.display = 'none'; });

const P = () => D.parts[part];
const cfg = n => D.configs[n] || {family: n.split('-')[0], default: true, compared: true, values: {}};
const runLink = id => id ? `<a href="../../runs/${esc(id)}/summary.md">${esc(id)}</a>` : 'nháp';
const families = () => D.families.filter(f => f.compared);
const shown = () => Object.keys(P().configs).filter(n => cfg(n).compared && (scope === 'all' || cfg(n).default));
const mkey = m => m.id + '|' + m.metric;
const metricsOf = g => P().metrics.filter(m => m.group === g);

function cellHtml(c, name, extra = '') {
  if (!c) return '<span class="muted">—</span>';
  const row = P().configs[name] || {};
  const ci = c.ci ? `[${fmt(c.ci[0])}, ${fmt(c.ci[1])}]` : '—';
  const worst = c.worst ? `<br>Lượt xấu nhất: ${esc(c.worst.case)}, seed ${c.worst.seed}: ${fmt(c.worst.diff)}` : '';
  const t = `<b>${esc(name)}</b><br>Hiệu TB ${fmt(c.mean)} (dương: tốt hơn mốc)<br>CI 95 % ${ci}, n = ${c.n}<br>`
    + `Dung sai ${fmt(c.tolerance)}; giá trị ${fmt(c.level)} so với mốc ${fmt(c.level_base)}${worst}<br>Run ${esc(row.run_id || 'nháp')}`;
  return `<span class="chip ${c.label}" data-tip="${esc(t)}">${LABEL[c.label].split(' ')[0]} ${fmt(c.mean)}</span>${extra}`;
}

function flagsHtml(f) {
  if (!f) return '';
  let s = '';
  if (f.b0_blocked) s += '<span class="flag red" title="Trượt C1 hoặc C2">⛔ B0</span>';
  if (f.new_failure_runs) s += `<span class="flag red" title="Requirement trượt mà mốc đạt ở cùng ca, profile, seed">⚠ ${f.new_failure_runs} trượt mới</span>`;
  if (f.lcc_runs_lost) s += `<span class="flag amber" title="LCC lái ít hơn mốc quá ${D.lost_max} chu kỳ: chỉ số độ êm có thể trông tốt hơn thật">⚠ LCC lái ít hơn ở ${f.lcc_runs_lost} lượt</span>`;
  if (f.evaluator_errors) s += `<span class="flag amber">⚠ ${f.evaluator_errors} lỗi chấm</span>`;
  return s;
}

function gridRange(family, key) {
  const fam = D.families.find(f => f.variant === family);
  if (!fam || fam.configs.length < 2) return '';
  const vals = fam.configs.map(n => (P().configs[n]?.cells || {})[key]?.mean).filter(v => v != null && isFinite(v));
  if (vals.length < 2) return '';
  return `<span class="range" title="Dải hiệu TB qua ${vals.length} cấu hình của lưới">lưới ${fmt(Math.min(...vals))} … ${fmt(Math.max(...vals))}</span>`;
}

function metricHead(ms) { return ms.map(m => `<th title="${esc(m.metric)}">${esc(m.id.replace('PP-SWR-', ''))}<br><span class="muted">${esc(m.metric.slice(0, 38))}</span></th>`).join(''); }

const views = {
  'Tổng quan'() {
    const ms = P().metrics;
    let h = `<p class="note">Hàng: từng thuật toán ở cấu hình mặc định. Ô: hiệu ghép cặp so với mốc <code>${esc(D.baseline)}</code> (dương: tốt hơn), màu chỉ theo nhãn của mục 2.3; dòng nhỏ là dải hiệu của cả lưới calibration. Không có hạng hay điểm tổng.</p>`;
    h += '<table><thead><tr><th>Thuật toán</th><th>Cờ</th>' + metricHead(ms) + '</tr></thead><tbody>';
    for (const f of families()) {
      const r = P().configs[f.default];
      if (!r) { h += `<tr><td>${esc(f.variant)}</td><td colspan="${ms.length + 1}" class="muted">chưa chạy ở phần ${part}</td></tr>`; continue; }
      h += `<tr><td><b>${esc(f.variant)}</b><br><span class="muted">${esc(f.description)}</span></td><td>${flagsHtml(r.flags)}</td>`;
      for (const m of ms) h += `<td>${f.variant === D.baseline ? '<span class="muted">mốc</span>' : cellHtml(r.cells[mkey(m)], f.default, gridRange(f.variant, mkey(m)))}</td>`;
      h += '</tr>';
    }
    return h + '</tbody></table>' + legend();
  },
  'An toàn'() { return groupView('An toàn', true); },
  'Bám làn và cảm nhận'() { return groupView('Bám làn và cảm nhận người lái', false); },
  'Theo nhóm ca'() {
    const groups = Object.keys(D.case_groups);
    let h = `<p class="note">Hiệu so với mốc trong từng nhóm ca: ${groups.map(g => `${esc(g)} = ${esc(JSON.stringify(D.case_groups[g]))}`).join('; ')}.</p>`;
    for (const name of shown()) {
      if (name === D.baseline) continue;
      const r = P().configs[name];
      h += `<h3>${esc(name)} ${flagsHtml(r.flags)}</h3><table><thead><tr><th>Chỉ số</th><th>Tất cả</th>${groups.map(g => `<th>${esc(g)}</th>`).join('')}</tr></thead><tbody>`;
      for (const m of P().metrics) {
        const c = r.cells[mkey(m)]; if (!c) continue;
        h += `<tr><td>${esc(m.id)} ${esc(m.metric)}</td><td>${cellHtml(c, name)}</td>${groups.map(g => `<td>${c.groups && c.groups[g] && c.groups[g].n ? cellHtml(c.groups[g], name) : '<span class="muted">—</span>'}</td>`).join('')}</tr>`;
      }
      h += '</tbody></table>';
    }
    return h;
  },
  'Flexibility'() {
    let h = '<p class="note">Cùng một bản build và một bộ calibration trên mọi vehicle profile. Bảng 1: hiệu ghép cặp của độ chênh giữa các profile so với mốc (dương: ít chênh hơn mốc). Bảng 2: giá trị xấu nhất theo profile.</p>';
    const fm = P().flex_metrics;
    h += '<table><thead><tr><th>Cấu hình</th>' + fm.map(m => `<th>${esc(m[0].replace('PP-SWR-', ''))}<br><span class="muted">${esc(m[1].slice(0, 38))}</span></th>`).join('') + '</tr></thead><tbody>';
    for (const name of shown()) { if (name === D.baseline) continue; const r = P().configs[name];
      h += `<tr><td>${esc(name)}</td>` + fm.map(m => `<td>${cellHtml(r.cells['flex|' + m[0] + '|' + m[1]], name)}</td>`).join('') + '</tr>'; }
    h += '</tbody></table>';
    for (const name of shown()) {
      const bp = P().configs[name].by_profile; const keys = Object.keys(bp); if (!keys.length) continue;
      const profiles = [...new Set(keys.flatMap(k => Object.keys(bp[k])))].sort();
      h += `<h3>${esc(name)}</h3><table><thead><tr><th>Chỉ số</th>${profiles.map(p => `<th>${esc(p)}</th>`).join('')}</tr></thead><tbody>`;
      for (const k of keys) h += `<tr><td>${esc(k.replace('|', ' '))}</td>${profiles.map(p => `<td class="num">${fmt(bp[k][p])}</td>`).join('')}</tr>`;
      h += '</tbody></table>';
    }
    return h;
  },
  'Chi phí phần cứng'() {
    let h = `<p class="note">Thời gian CPU của <code>pp_lcc_step</code> qua adapter SIL trên laptop, không chuyển thẳng sang ECU. p99 là trung vị qua các lượt của p99 từng lượt, đo ở 2 job; cột "phiên 1 job" đo riêng cho cấu hình mặc định (S1f, S1c vòng kín, lặp 3 lần, thứ tự xen kẽ), ít nhiễu hơn; max, khối lượng việc, bộ nhớ và kích thước là ngữ cảnh. Phần cứng chọn theo trường hợp xấu nhất.</p>`;
    h += '<table><thead><tr><th>Cấu hình</th><th>016 p99</th><th>p99 [ms]</th><th>% chu kỳ 25 ms</th><th>p99 lớn nhất [ms]</th><th>p99 phiên 1 job [ms]</th><th>Thời gian lớn nhất [ms]</th><th>Khối lượng việc lớn nhất</th><th>Phép nhân MLP</th><th>State [byte]</th><th>Thư viện [byte]</th><th>Weights [byte]</th></tr></thead><tbody>';
    const t016 = P().metrics.find(m => m.id === 'PP-SWR-016');
    for (const name of shown()) { const r = P().configs[name], c = r.cost;
      h += `<tr><td>${esc(name)}</td><td>${name === D.baseline ? '<span class="muted">mốc</span>' : cellHtml(t016 && r.cells[mkey(t016)], name)}</td><td class="num">${fmt(c.p99_median_ms)}</td><td class="num">${pct(c.p99_cycle_share)}</td><td class="num">${fmt(c.p99_max_ms)}</td><td class="num">${c.timing_1job ? fmt(c.timing_1job.p99_median_ms) : '—'}</td><td class="num">${fmt(c.max_ms)}</td><td class="num">${fmt(c.work_max)}</td><td class="num">${fmt(c.infer_ops_max)}</td><td class="num">${c.state_bytes ?? '—'}</td><td class="num">${c.library_bytes ?? '—'}</td><td class="num">${c.weights_bytes ?? '—'}</td></tr>`; }
    return h + '</tbody></table><p class="note">Khối lượng việc đọc từ telemetry (bản build lab có <code>PP_T7_TELEMETRY</code>); — là chưa có.</p>';
  },
  'Độ nhạy calibration'() {
    let h = '<p class="note">Mỗi lưới 3 × 3 một bản đồ nhiệt theo từng chỉ số. Ô: hiệu TB so với mốc chia cho dung sai (xanh: tốt hơn, đỏ: xấu hơn, xám: trong dung sai); viền đậm là cấu hình mặc định. Đổi phần tuning/test ở trên để xem cả hai.</p>';
    for (const f of D.families.filter(f => f.grid)) {
      const axes = Object.keys(f.grid); if (axes.length !== 2 || !f.grid[axes[0]] || !f.grid[axes[1]]) continue;
      h += `<h3>${esc(f.variant)}</h3><div style="display:flex;flex-wrap:wrap;gap:12px">`;
      for (const m of P().metrics) h += heatmap(f, axes, m);
      h += '</div>';
    }
    return h;
  },
  'Số vòng QP'() {
    const rows = P().qp_iterations;
    let h = `<p class="note">Lệch output vòng hở 0–1 s so với <code>${esc(D.reference)}</code> theo p99 thời gian tính. Pareto: không cấu hình nào vừa nhanh hơn vừa lệch ít hơn. Mỗi họ một màu, nhãn đặt cạnh điểm.</p>`;
    h += scatter(rows);
    h += '<table><thead><tr><th>Cấu hình</th><th>Số vòng</th><th>p99 [ms]</th><th>Lệch lớn nhất [m]</th><th>Lệch TB [m]</th><th>Pareto</th></tr></thead><tbody>';
    for (const r of rows) h += `<tr><td>${esc(r.config)}</td><td class="num">${r.iterations}</td><td class="num">${fmt(r.p99_median_ms)}</td><td class="num">${fmt(r.diff_max_m)}</td><td class="num">${fmt(r.diff_mean_m)}</td><td>${r.pareto ? 'có' : ''}</td></tr>`;
    return h + '</tbody></table>';
  },
  'Giả thuyết'() {
    const H = D.hypotheses[part] || {};
    let h = '<p class="note">Tiêu chí khóa trong plan.yaml trước lần chạy --record. Thuật toán có lưới được kiểm ở từng cấu hình và báo "đạt ở x/n cấu hình"; không chọn riêng cấu hình đạt.</p>';
    const word = v => v === true ? '✓ đạt' : v === false ? '✗ không đạt' : 'thiếu dữ liệu';
    for (const [id, hy] of Object.entries(H)) {
      const sum = Object.entries(hy.summary).map(([v, s]) => `${esc(v)}: đạt ở ${s.held}/${s.configs} cấu hình${s.measured < s.configs ? ` (đo được ${s.measured})` : ''}`).join('; ');
      h += `<h3>${esc(id)} <span class="muted">(${esc(hy.kind)})</span></h3><p class="note">${sum}</p><table><thead><tr><th>Cấu hình</th><th>So với</th><th>Kết quả</th><th>Số liệu</th></tr></thead><tbody>`;
      for (const r of hy.rows) {
        const vals = Object.entries(r.values || {}).filter(([k, v]) => typeof v !== 'object' || v === null).map(([k, v]) => `${esc(k)} ${fmt(v)}`).join(', ');
        const cells = Object.entries(r.values || {}).filter(([k, v]) => v && typeof v === 'object' && 'label' in v).map(([k, v]) => `${esc(k.split('|')[0])} ${cellHtml(v, r.config)}`).join(' ');
        h += `<tr><td>${esc(r.config ?? '—')}</td><td>${esc(r.against ?? '')}</td><td>${word(r.holds)}</td><td>${cells} ${vals}</td></tr>`;
      }
      h += '</tbody></table>';
    }
    return h;
  },
  'Cờ cảnh báo'() {
    let h = '<p class="note">Cờ không loại cấu hình nào; nó cảnh báo ô trông tốt có thể đang hiểu sai. Lượt có cờ B0 hay lỗi chạy không vào hiệu ghép cặp.</p><table><thead><tr><th>Cấu hình</th><th>Cờ</th><th>Lượt trượt mới</th><th>LCC lái ít hơn mốc</th></tr></thead><tbody>';
    for (const name of shown()) { const f = P().configs[name].flags;
      const nf = f.new_failures.slice(0, 12).map(x => `${esc(x.case)} s${x.seed}: ${esc(x.failed.join(', '))}`).join('<br>') + (f.new_failures.length > 12 ? `<br>… ${f.new_failures.length - 12} lượt nữa` : '');
      const ll = f.lcc_lost.slice(0, 8).map(x => `${esc(x.case)} s${x.seed}: −${x.lost} chu kỳ`).join('<br>');
      h += `<tr><td>${esc(name)}</td><td>${flagsHtml(f) || '<span class="muted">không</span>'}</td><td>${nf || '—'}</td><td>${ll || '—'}</td></tr>`; }
    const sh = P().configs[D.baseline]?.flags.shared_failures || {};
    return h + `</tbody></table><p class="note">Lỗi chung (mốc cũng trượt): ${Object.entries(sh).map(([k, v]) => `${esc(k)} (${v})`).join(', ') || 'không'}.</p>`;
  },
  'Độ tin'() {
    let h = '<p class="note">Vòng hở: chỉ so chu kỳ có digest đầu vào trùng nhau. "Path khác mốc": tỉ lệ chu kỳ lệch 0–1 s vượt 0,005 m (generator có thực sự hoạt động không). Chênh tuning–test: nhãn đổi chiều, hoặc tốt hơn ở tuning mà chỉ trong dung sai ở test (dấu hiệu quá khớp khi dò tay).</p>';
    h += '<table><thead><tr><th>Cấu hình</th><th>Chu kỳ so được</th><th>Digest lệch</th><th>Chỉ một bên có path</th><th>Path khác mốc</th><th>Chỉ số ít dữ liệu</th><th>Đổi chiều tuning–test</th><th>Tốt hơn ở tuning, trong dung sai ở test</th><th>Run</th></tr></thead><tbody>';
    for (const name of shown()) { const r = P().configs[name], c = r.credibility || {}; const g = c.tuning_test_gap;
      h += `<tr><td>${esc(name)}</td><td class="num">${c.compared_cycles ?? '—'}</td><td class="num">${c.digest_mismatch ?? '—'}</td><td class="num">${c.valid_mismatch ?? '—'}</td><td class="num">${pct(c.differs_share)}</td><td class="num">${c.few_data_metrics ?? '—'}</td><td>${g ? esc(g.flipped.join(', ') || 'không') : '—'}</td><td>${g ? esc(g.faded.join(', ') || 'không') : '—'}</td><td>${runLink(r.run_id)}</td></tr>`; }
    h += '</tbody></table>';
    const rep = Object.entries(D.repeats);
    if (rep.length) h += `<p class="note">Cấu hình chạy lại ở nhiều lần (mốc trong mỗi lần chạy theo nhóm): ${rep.map(([k, v]) => `${esc(k)} ${v.every(Boolean) ? 'trùng giá trị' : '<b>KHÁC giá trị</b>'}`).join('; ')}.</p>`;
    return h;
  },
  'Chẩn đoán'() {
    let h = '<p class="note"><b>Không so với mốc.</b> Chỉ để giải thích vì sao.</p><table><thead><tr><th>Cấu hình</th><th>Jerk path lớn nhất (003)</th><th>Chu kỳ gần trần a_y/jerk TB / max</th><th>a_y xe > aysmax + 0,3 lâu nhất [s]</th><th>Lượt ngoài R79 5.6.2.1.1</th><th>PP-SWR-125 max</th><th>Telemetry: fallback TB</th><th>T10 sửa path max [m]</th><th>Residual p99</th><th>Slack max</th></tr></thead><tbody>';
    for (const name of shown()) { const d = P().configs[name].diagnostics, t = d.telemetry || {};
      h += `<tr><td>${esc(name)}</td><td class="num">${fmt(d.path_jerk_max)}</td><td class="num">${pct(d.near_limit_share_mean)} / ${pct(d.near_limit_share_max)}</td><td class="num">${fmt(d.ay_over_sustained_max_s)}</td><td class="num">${d.r79_outside_runs}</td><td class="num">${fmt(d.swr125_max)}</td><td class="num">${pct(t.fallback_share_mean)}</td><td class="num">${fmt(t.t10_change_max_m)}</td><td class="num">${fmt(t.residual_p99)}</td><td class="num">${fmt(t.slack_max)}</td></tr>`; }
    return h + '</tbody></table>';
  },
};

function groupView(group, strip) {
  const ms = metricsOf(group);
  let h = `<p class="note">Hiệu ghép cặp so với mốc <code>${esc(D.baseline)}</code>, kèm CI 95 %, n và lượt xấu nhất (di chuột lên ô).${strip ? ' Biểu đồ: hiệu của từng lượt, đường dọc là 0.' : ''}</p>`;
  h += '<table><thead><tr><th>Cấu hình</th><th>Cờ</th>' + metricHead(ms) + '</tr></thead><tbody>';
  for (const name of shown()) { if (name === D.baseline) continue; const r = P().configs[name];
    h += `<tr><td>${esc(name)}</td><td>${flagsHtml(r.flags)}</td>` + ms.map(m => { const c = r.cells[mkey(m)];
      const w = c && c.worst ? `<span class="range">xấu nhất ${esc(c.worst.case)} s${c.worst.seed}: ${fmt(c.worst.diff)}</span>` : '';
      return `<td>${cellHtml(c, name, w + (strip && c ? stripPlot(c, name) : ''))}</td>`; }).join('') + '</tr>'; }
  return h + '</tbody></table>' + legend();
}

function stripPlot(c, name) {
  const ds = (c.diffs || []).map(x => x.d); if (!ds.length) return '';
  const W = 150, H = 22, lo = Math.min(0, ...ds), hi = Math.max(0, ...ds), span = (hi - lo) || 1;
  const x = v => 4 + (W - 8) * (v - lo) / span;
  let s = `<svg width="${W}" height="${H}" role="img" aria-label="hiệu từng lượt"><line x1="${x(0)}" x2="${x(0)}" y1="2" y2="${H - 2}" stroke="var(--axis)"/>`;
  for (const p of c.diffs) s += `<circle cx="${x(p.d)}" cy="${H / 2}" r="4" fill="${p.d >= 0 ? 'var(--b3)' : 'var(--r3)'}" fill-opacity=".7" stroke="var(--surface)" stroke-width="1" data-tip="${esc(`${p.case}, seed ${p.seed}: ${fmt(p.d)}`)}"/>`;
  return '<br>' + s + '</svg>';
}

function heatmap(f, axes, m) {
  const [a, b] = axes, la = f.grid[a], lb = f.grid[b];
  const cs = 46, pad = 70, W = pad + cs * lb.length + 4, Hh = 24 + cs * la.length + 34;
  const val = (n, k) => { const v = D.configs[n]?.values?.[k]; return v; };
  const same = (x, y) => Math.abs(Number(x) - Number(y)) < 1e-9;
  const pick = (lv, k) => Array.isArray(lv) ? lv : [lv];
  let s = `<div class="card" style="padding:8px;margin:0"><div style="font-size:12px;color:var(--ink2);max-width:${W}px">${esc(m.id)} ${esc(m.metric.slice(0, 40))}</div><svg width="${W}" height="${Hh}" role="img" aria-label="bản đồ nhiệt ${esc(m.id)}">`;
  const keysA = a.split('+'), keysB = b.split('+');
  la.forEach((va, i) => { s += `<text x="${pad - 6}" y="${24 + cs * i + cs / 2 + 4}" text-anchor="end">${esc(pick(va).join('/'))}</text>`;
    lb.forEach((vb, j) => {
      const name = f.configs.find(n => keysA.every((k, q) => same(val(n, k), pick(va)[q])) && keysB.every((k, q) => same(val(n, k), pick(vb)[q])));
      const c = name && (P().configs[name]?.cells || {})[mkey(m)];
      const base = name === D.baseline;
      let fill = 'var(--neutral)', txt = base ? 'mốc' : '—';
      if (c && c.mean != null) { const r = c.tolerance ? c.mean / c.tolerance : 0;
        const step = Math.abs(r) < 1 ? 0 : Math.abs(r) < 2 ? 1 : Math.abs(r) < 4 ? 2 : 3;
        fill = step === 0 || c.label === 'few' ? 'var(--neutral)' : `var(--${r > 0 ? 'b' : 'r'}${step})`; txt = fmt(c.mean, 2); }
      const tipText = name ? `<b>${esc(name)}</b><br>${c ? `${LABEL[c.label]}; hiệu TB ${fmt(c.mean)}, CI ${c.ci ? '[' + fmt(c.ci[0]) + ', ' + fmt(c.ci[1]) + ']' : '—'}, n = ${c.n}, dung sai ${fmt(c.tolerance)}` : (base ? 'mốc' : 'chưa chạy')}` : 'không có cấu hình';
      const isDefault = name && D.configs[name]?.default;
      s += `<rect x="${pad + cs * j + 1}" y="${24 + cs * i + 1}" width="${cs - 2}" height="${cs - 2}" rx="4" fill="${fill}" stroke="${isDefault ? 'var(--ink)' : 'var(--surface)'}" stroke-width="${isDefault ? 2 : 2}" data-tip="${esc(tipText)}"/>`;
      s += `<text x="${pad + cs * j + cs / 2}" y="${24 + cs * i + cs / 2 + 4}" text-anchor="middle" style="fill:var(--ink);pointer-events:none">${esc(txt)}</text>`;
    }); });
  lb.forEach((vb, j) => s += `<text x="${pad + cs * j + cs / 2}" y="16" text-anchor="middle">${esc(pick(vb).join('/'))}</text>`);
  s += `<text x="${pad}" y="${Hh - 8}">hàng: ${esc(a)}; cột: ${esc(b)}</text>`;
  return s + '</svg></div>';
}

function scatter(rows) {
  const pts = rows.filter(r => r.p99_median_ms != null && r.diff_max_m != null);
  if (!pts.length) return '<p class="muted">Chưa có điểm (cần lượt vòng hở và nghiệm tham chiếu).</p>';
  const fams = [...new Set(pts.map(r => r.series))].slice(0, 3);
  const color = fam => ['var(--s1)', 'var(--s2)', 'var(--s3)'][fams.indexOf(fam)] || 'var(--muted)';
  const W = 640, H = 320, L = 60, B = 40, T = 12, R = 16;
  const xs = pts.map(p => p.p99_median_ms), ys = pts.map(p => p.diff_max_m);
  const x0 = 0, x1 = Math.max(...xs) * 1.1, y0 = 0, y1 = Math.max(...ys) * 1.15 || 1;
  const X = v => L + (W - L - R) * (v - x0) / (x1 - x0), Y = v => H - B - (H - B - T) * (v - y0) / (y1 - y0);
  let s = `<div class="legend">${fams.map(f => `<span style="--c:${color(f)}">${esc(f)}</span>`).join('')}</div><svg width="${W}" height="${H}" role="img" aria-label="lệch so với nghiệm tham chiếu theo p99">`;
  for (let i = 0; i <= 4; i++) { const yv = y0 + (y1 - y0) * i / 4; s += `<line x1="${L}" x2="${W - R}" y1="${Y(yv)}" y2="${Y(yv)}" stroke="var(--grid)"/><text x="${L - 6}" y="${Y(yv) + 4}" text-anchor="end">${fmt(yv, 2)}</text>`; }
  for (let i = 0; i <= 4; i++) { const xv = x0 + (x1 - x0) * i / 4; s += `<text x="${X(xv)}" y="${H - B + 16}" text-anchor="middle">${fmt(xv, 2)}</text>`; }
  s += `<line x1="${L}" x2="${W - R}" y1="${H - B}" y2="${H - B}" stroke="var(--axis)"/><text x="${(L + W) / 2}" y="${H - 6}" text-anchor="middle">p99 thời gian tính [ms]</text><text x="14" y="${(H - B) / 2}" transform="rotate(-90 14 ${(H - B) / 2})" text-anchor="middle">lệch lớn nhất [m]</text>`;
  for (const f of fams) { const line = pts.filter(p => p.series === f).sort((a, b) => a.iterations - b.iterations);
    s += `<polyline fill="none" stroke="${color(f)}" stroke-width="2" points="${line.map(p => X(p.p99_median_ms) + ',' + Y(p.diff_max_m)).join(' ')}"/>`; }
  for (const p of pts) s += `<circle cx="${X(p.p99_median_ms)}" cy="${Y(p.diff_max_m)}" r="${p.pareto ? 6 : 4.5}" fill="${color(p.series)}" stroke="var(--surface)" stroke-width="2" data-tip="${esc(`<b>${p.config}</b><br>${p.iterations} vòng; p99 ${fmt(p.p99_median_ms)} ms; lệch ${fmt(p.diff_max_m)} m${p.pareto ? '; Pareto' : ''}`)}"/><text x="${X(p.p99_median_ms) + 7}" y="${Y(p.diff_max_m) - 6}">${p.iterations}</text>`;
  return s + '</svg>';
}

function legend() {
  return '<div class="legend"><span style="--c:var(--b2)">▲ tốt hơn mốc (CI không chứa 0, |hiệu| ≥ dung sai)</span><span style="--c:var(--r2)">▼ xấu hơn mốc</span><span style="--c:var(--neutral)">≈ trong dung sai</span><span style="--c:transparent;outline:1px dashed var(--muted)">ít dữ liệu (n &lt; 4)</span></div>';
}

let current = 'Tổng quan';
function render() {
  document.querySelectorAll('nav button').forEach(b => b.setAttribute('aria-selected', b.textContent === current));
  $('main').innerHTML = `<section class="card"><h2>${esc(current)}</h2>${views[current]()}</section>`;
}
$('nav').innerHTML = Object.keys(views).map(k => `<button type="button">${k}</button>`).join('');
$('nav').addEventListener('click', e => { if (e.target.tagName === 'BUTTON') { current = e.target.textContent; render(); } });
$('#part').innerHTML = Object.keys(D.parts).map(p => `<option ${p === part ? 'selected' : ''}>${p}</option>`).join('');
$('#part').addEventListener('change', e => { part = e.target.value; render(); });
$('#scope').addEventListener('change', e => { scope = e.target.value; render(); });
$('#theme').addEventListener('click', () => { const r = document.documentElement;
  const dark = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; r.dataset.theme = dark ? 'light' : 'dark'; });
$('footer').innerHTML = '<b>Cấu hình và bản build</b><table><thead><tr><th>Cấu hình</th><th>pp_version</th><th>Hash calibration</th><th>Run ID</th></tr></thead><tbody>'
  + Object.entries(D.parts).flatMap(([p, v]) => Object.entries(v.configs).map(([n, r]) => `<tr><td>${esc(n)} <span class="muted">(${p})</span></td><td>${esc(r.pp_version || '—')}</td><td>${esc(r.calibration_hash || '—')}</td><td>${runLink(r.run_id)}</td></tr>`)).join('')
  + `</tbody></table><p>Plan <code>${esc(D.plan.path)}</code> sha256 ${esc((D.plan.sha256 || '').slice(0, 12))}, khóa ${esc(D.plan.locked || 'chưa')}. Lab chỉ mô tả, không chọn generator.</p>`;
render();
"""


def page(data: dict) -> str:
    draft = data.get("draft", True)
    banner = ('<div class="draft">NHÁP: plan chưa khóa hoặc có lần chạy không phải --record trên cây sạch. '
              'Không trích số liệu này.</div>') if draft else ""
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    warn = "".join(f"<li>{w}</li>" for w in data.get("grid_warnings") or [])
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>T7 Generator Dashboard</title>
<style>{STYLE}</style>
</head>
<body>
<header>
<h1>So sánh generator T7 của LCC planner{' (nháp)' if draft else ''}</h1>
<p class="sub">{data['study']}: so khả năng của các họ thuật toán ở nhiều khía cạnh. Không có hạng, điểm tổng hay
lựa chọn; mốc là <code>{data['baseline']}</code> ở calibration mặc định. Hiệu dương là tốt hơn mốc.</p>
{banner}{f'<ul class="note">{warn}</ul>' if warn else ''}
<div class="bar"><label for="part">Phần</label><select id="part"></select>
<label for="scope">Cấu hình</label><select id="scope"><option value="default">mặc định của mỗi thuật toán</option>
<option value="all">cả lưới calibration</option></select>
<button id="theme" type="button">Sáng / tối</button></div>
</header>
<nav aria-label="Khía cạnh"></nav>
<main></main>
<footer></footer>
<div id="tip" role="tooltip"></div>
<script type="application/json" id="data">{payload}</script>
<script>{SCRIPT}</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the static T7 generator dashboard from techniques.json")
    parser.add_argument("--data", type=Path, default=HERE / "techniques.json")
    parser.add_argument("--out", type=Path, default=HERE / "index.html")
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    args.out.write_text(page(data), encoding="utf-8")
    print(f"{args.out} ({'draft' if data.get('draft', True) else 'official'})")


if __name__ == "__main__":
    main()
