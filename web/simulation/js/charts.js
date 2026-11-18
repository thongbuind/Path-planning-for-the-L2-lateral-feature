/* Biểu đồ trực tiếp: một SVG, các panel dùng chung trục thời gian 0 tới hết lượt chạy.
   Khung dựng một lần; mỗi chu kỳ planner mới chỉ nối thêm điểm, nên biểu đồ hiện dần theo lượt chạy.
   Đường đổi màu theo chức năng đang lái (LCC, LKA, ELK); lỗi đang tiêm là dải xám phủ qua mọi panel. */
(() => {
  'use strict';
  const PP = window.PP;
  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.getElementById('chart');
  const plot = document.getElementById('plot');
  const tip = document.getElementById('tip');
  const legend = document.getElementById('legend');
  const tablebox = document.getElementById('tablebox');

  const GUT_L = 108, GUT_R = 38, GAP = 8;
  const FN_CLS = ['', 'hwa', 'lka', 'elk'];
  const mk = (n, a, p) => {
    const e = document.createElementNS(NS, n);
    for (const k in a || {}) e.setAttribute(k, a[k]);
    if (p) p.appendChild(e);
    return e;
  };

  let d = null, G = null, H = null, R = null;
  let mode = 'chart', curK = -1, dragging = false, tableRows = 0;
  const dom = { vals: {}, dots: [], cur: null, hov: null };

  function niceTicks(lo, hi, want) {
    const span = hi - lo;
    if (!(span > 0)) return [lo];
    const raw = span / want, mag = Math.pow(10, Math.floor(Math.log10(raw))), nm = raw / mag;
    const step = (nm < 1.5 ? 1 : nm < 3 ? 2 : nm < 7 ? 5 : 10) * mag;
    const out = [];
    for (let v = Math.ceil(lo / step - 1e-9) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(9));
    return out;
  }

  // ---------- Panel và dải trục y ----------
  function panelsOf() {
    const sr = d.veh.sr || 15;
    const free = ((d.road.w - d.veh.w) / 2) * 100;   // cm: lệch tại đó DLC = 0
    const lim = d.lim_ay;
    const ayRefs = [];
    if (lim) {
      ayRefs.push({ y: lim[0], t: 'giới hạn R79: ' + PP.f(lim[0], 1) + ' liên tục, ' + PP.f(lim[1], 1) + ' trong ≤ ' + PP.f(lim[2], 0) + ' s', below: true }, { y: lim[1] });
      if (R.ay[0] < -lim[0]) ayRefs.push({ y: -lim[0] }, { y: -lim[1] });
    }
    return [
      { key: 'off', name: 'Lệch tâm làn · truth', unit: 'cm', sym: true, get: (k) => d.off[k] * 100, fmt: (x) => PP.fs(x, 0), refs: [{ y: free, t: 'mép làn' }, { y: -free }] },
      { key: 'ay', name: 'a_y xe, lọc R79 · truth', unit: 'm/s²', get: (k) => d.ayf[k], fmt: (x) => PP.f(x, 2), refs: ayRefs },
      { key: 'st', name: 'Góc vô lăng · truth', unit: '°', sym: true, get: (k) => d.whl[k] * sr * 180 / Math.PI, fmt: (x) => PP.fs(x, 1) },
      { key: 'cms', name: 'Thời gian tính · đo thật', unit: 'ms', zero: true, cap: 30, get: (k) => d.cms[k], fmt: (x) => PP.f(x, 2), refs: [{ y: 25, t: 'chu kỳ 25 ms' }] },
    ];
  }
  function initRanges() {
    const free = ((d.road.w - d.veh.w) / 2) * 100;
    R = { off: [-free * 1.15, free * 1.15], ay: [-1, 1], st: [-6, 6], cms: [0, 1.5] };
  }
  // Nở dải khi dữ liệu vượt; trả về true nếu dải đổi (phải dựng lại khung).
  function grow(key, v, sym, zero, cap) {
    if (v == null) return false;
    const r = R[key];
    let ch = false;
    if (v > r[1] && !(cap && r[1] >= cap)) { r[1] = Math.max(v * 1.2, r[1] * 1.6); if (cap) r[1] = Math.min(r[1], cap); ch = true; if (sym) r[0] = -r[1]; }
    if (!zero && v < r[0]) { r[0] = Math.min(v * 1.2, r[0] * 1.6); ch = true; if (sym) r[1] = -r[0]; }
    return ch;
  }

  // ---------- Dựng khung ----------
  function build() {
    if (!d || !R) return;
    const w = plot.clientWidth, h = plot.clientHeight;
    if (w < 50 || h < 50) return;
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
    svg.textContent = '';
    dom.vals = {}; dom.dots = [];

    let P = panelsOf();
    for (let k = 0; k < d.n; k++) P.forEach((p) => grow(p.key, p.get(k), p.sym, p.zero, p.cap));
    if (d.lim_ay) grow('ay', d.lim_ay[1] + 0.3, false);
    P = panelsOf();
    P.forEach((p) => { p.lo = R[p.key][0]; p.hi = R[p.key][1]; });

    const nF = Math.min(3, d.faults.length);
    const rowsTop = nF ? nF * 15 + 3 : 0, bandH = 16, limH = 7, axisH = 18;
    const headH = rowsTop + bandH + limH + 3 + 8;
    const avail = h - headH - axisH - GAP * (P.length - 1);
    const ph = Math.max(28, avail / P.length);
    const x0 = GUT_L, x1 = w - GUT_R, T = d.dur;
    const X = (t) => x0 + (t / T) * (x1 - x0);
    G = { w, h, x0, x1, X, T, P, ph, headH, nF, by: rowsTop, bandH, limY: rowsTop + bandH + 3, bottom: headH + P.length * ph + (P.length - 1) * GAP };
    H = { curFn: -1, band: null, bandX0: 0, bandLabel: null, limRect: null, limX0: 0, fe: [] };
    d.faults.forEach((f) => { f.t0 = null; f.t1 = null; });

    H.gWash = mk('g', {}, svg);
    H.gF = mk('g', {}, svg);
    H.gB = mk('g', {}, svg);
    if (nF) mk('text', { x: 0, y: 11 }, svg).textContent = 'Lỗi tiêm';
    mk('text', { x: 0, y: G.by + 12 }, svg).textContent = 'Chức năng';
    mk('text', { x: 0, y: G.limY + 5, style: 'font-size:10px' }, svg).textContent = 'Giới hạn ngang';

    P.forEach((p, i) => {
      const yt = headH + i * (ph + GAP), yb = yt + ph;
      const Y = (v) => yb - ((v - p.lo) / (p.hi - p.lo)) * ph;
      p.Y = Y; p.yt = yt; p.yb = yb; p.hasPrev = false; p.el = null; p.dd = '';
      mk('text', { class: 'p-name', x: 0, y: yt + 12 }, svg).textContent = p.name;
      dom.vals[p.key] = mk('text', { class: 'p-val', x: 0, y: yt + 28 }, svg);
      const gridG = mk('g', {}, svg);
      niceTicks(p.lo, p.hi, ph < 60 ? 2 : 3).forEach((v) => {
        const yy = Math.round(Y(v)) + 0.5;
        mk('line', { class: Math.abs(v) < 1e-9 ? 'zero' : 'grid', x1: x0, x2: x1, y1: yy, y2: yy }, gridG);
        mk('text', { class: 'tick-t', x: x1 + 6, y: yy + 3.5 }, gridG).textContent = PP.f(v, Math.abs(v) < 10 && v % 1 ? 1 : 0);
      });
      mk('text', { x: x1 + 6, y: yt - 0.5, style: 'font-size:9.5px' }, svg).textContent = p.unit;
      (p.refs || []).forEach((r) => {
        if (r.y < p.lo || r.y > p.hi) return;
        const yy = Math.round(Y(r.y)) + 0.5;
        mk('line', { class: 'lim', x1: x0, x2: x1, y1: yy, y2: yy }, svg);
        if (r.t) mk('text', { class: 'lim-t', x: x0 + 4, y: r.below ? yy + 11 : yy - 3 }, svg).textContent = r.t;
      });
      p.gs = mk('g', {}, svg);
    });

    const ay = G.bottom + 13;
    const step = [1, 2, 5, 10].find((s) => T / s <= 11) || 10;
    for (let t = 0; t <= T + 1e-6; t += step) mk('text', { class: 'axis-t', x: X(t), y: ay }, svg).textContent = PP.f(t, 0) + ' s';

    dom.hov = mk('line', { class: 'hov', y1: 0, y2: G.bottom, x1: -9, x2: -9, style: 'display:none' }, svg);
    dom.cur = mk('line', { class: 'cur', y1: 0, y2: G.bottom, x1: x0, x2: x0, style: 'display:none' }, svg);
    P.forEach((p) => dom.dots.push(mk('circle', { class: 'dot-m', r: 4.5, cx: x0, cy: p.yb, style: 'display:none' }, svg)));

    for (let k = 0; k < d.n; k++) addPoint(k);
    setCursor(curK);
  }

  // ---------- Nối thêm một chu kỳ ----------
  function faultEl(i) {
    if (H.fe[i]) return H.fe[i];
    const f = d.faults[i], e = {};
    const whole = f.plan && f.plan[0] === 0 && f.plan[1] == null;   // lỗi suốt chuyến: không phủ dải, vẫn có thanh nhãn
    if (!whole) e.wash = mk('rect', { class: 'wash', y: 0, height: G.bottom }, H.gWash);
    if (i < 3) {
      e.bar = mk('rect', { class: 'fbar', y: i * 15 + 0.5, height: 13, rx: 3 }, H.gF);
      mk('title', {}, e.bar).textContent = f.label;
    }
    H.fe[i] = e;
    return e;
  }
  function updFault(i) {
    const f = d.faults[i], e = faultEl(i);
    const xa = G.X(f.t0), wd = Math.max(2, G.X(Math.min(G.T, f.t1)) - xa);
    if (e.wash) { e.wash.setAttribute('x', xa); e.wash.setAttribute('width', wd); }
    if (e.bar) {
      e.bar.setAttribute('x', xa + 0.5); e.bar.setAttribute('width', Math.max(1, wd - 1));
      if (!e.text && wd > f.short.length * 5.8 + 14) {
        e.text = mk('text', { class: 'fbar-t', x: xa + 7, y: i * 15 + 10.5 }, H.gF);
        e.text.textContent = f.short;
      }
    }
  }

  function addPoint(k) {
    const t = d.t[k], x = G.X(t), xe = G.X(Math.min(G.T, t + d.dt)), fn = d.fn[k];
    const newRun = fn !== H.curFn;
    G.P.forEach((p) => {
      const v = p.get(k);
      if (v == null) return;
      const y = p.Y(PP.clamp(v, p.lo, p.hi));
      if (newRun || !p.el) {
        p.dd = (p.hasPrev ? 'M' + p.px.toFixed(1) + ' ' + p.py.toFixed(1) + 'L' : 'M') + x.toFixed(1) + ' ' + y.toFixed(1);
        p.el = mk('path', { class: 'ser', style: `stroke:var(${PP.FN_VAR[fn]})` }, p.gs);
      } else p.dd += 'L' + x.toFixed(1) + ' ' + y.toFixed(1);
      p.el.setAttribute('d', p.dd);
      p.px = x; p.py = y; p.hasPrev = true;
    });

    // dải chức năng
    if (newRun) {
      H.bandX0 = x;
      H.band = mk('rect', { x: x + 1, y: G.by, width: 1, height: G.bandH, rx: 3, style: `fill:var(${PP.FN_VAR[fn]})` }, H.gB);
      H.bandLabel = null;
      H.curFn = fn;
      legendOf();
    }
    const bw = Math.max(1, xe - H.bandX0 - 2);
    H.band.setAttribute('width', bw);
    if (fn && !H.bandLabel && bw > 40) {
      H.bandLabel = mk('text', { class: 'seg-t', x: H.bandX0 + 8, y: G.by + 11.5 }, H.gB);
      H.bandLabel.textContent = PP.FN[fn];
    }

    // giới hạn ngang
    if (d.lim[k]) {
      if (!H.limRect) { H.limX0 = x; H.limRect = mk('rect', { x, y: G.limY, width: 1, height: 4, rx: 2, style: 'fill:var(--ink-2);opacity:.55' }, H.gB); }
      H.limRect.setAttribute('width', Math.max(1, xe - H.limX0));
    } else H.limRect = null;

    // lỗi đang tiêm
    const nf = d.faults.length;
    for (let i = 0; i < nf; i++) {
      if (!d.fa[k * nf + i]) continue;
      const f = d.faults[i];
      if (f.t0 == null) f.t0 = t;
      f.t1 = t + d.dt;
      updFault(i);
    }
  }

  function push(k) {
    if (!d || !G) return;
    let changed = false;
    G.P.forEach((p) => { if (grow(p.key, p.get(k), p.sym, p.zero, p.cap)) changed = true; });
    if (mode !== 'chart') { tableTick(k); return; }
    if (changed) build(); else addPoint(k);
    tableTick(k);
  }

  function legendOf() {
    legend.textContent = '';
    const used = [...new Set(d.fn)].sort();
    const add = (cls, text) => {
      const s = document.createElement('span');
      const i = document.createElement('i');
      i.className = cls;
      s.appendChild(i);
      s.appendChild(document.createTextNode(text));
      legend.appendChild(s);
    };
    used.forEach((fn) => add(FN_CLS[fn], fn ? PP.FN[fn] + ' đang lái' : 'Không có chức năng'));
    if (d.faults.length) add('wash', 'Lỗi đang tiêm');
    if (d.lim_ay) add('lim', 'Giới hạn');
  }

  // ---------- Con trỏ ----------
  function setCursor(k) {
    curK = k;
    if (!d || !G || !dom.cur) return;
    const ok = k >= 0 && k < d.n;
    dom.cur.style.display = ok ? '' : 'none';
    dom.dots.forEach((c) => { c.style.display = ok ? '' : 'none'; });
    if (!ok) return;
    const x = G.X(d.t[k]);
    dom.cur.setAttribute('x1', x); dom.cur.setAttribute('x2', x);
    G.P.forEach((p, i) => {
      const v = p.get(k);
      dom.dots[i].setAttribute('cx', x);
      dom.dots[i].setAttribute('cy', v == null ? p.yb : p.Y(PP.clamp(v, p.lo, p.hi)));
      dom.dots[i].style.fill = `var(${PP.FN_VAR[d.fn[k]]})`;
      dom.vals[p.key].textContent = (v == null ? '—' : p.fmt(v)) + ' ' + p.unit;
    });
    if (mode === 'table') markRow(k);
  }

  // ---------- Tooltip và xem lại ----------
  function frameAt(ev) {
    const r = svg.getBoundingClientRect();
    const x = ev.clientX - r.left;
    const t = ((x - G.x0) / (G.x1 - G.x0)) * d.dur;
    return { x, t, k: PP.clamp(Math.round((t - d.t[0]) / d.dt), 0, d.n - 1) };
  }
  function showTip(ev) {
    if (!d || !G || mode !== 'chart' || !d.n) return;
    const { x, t, k } = frameAt(ev);
    if (x < G.x0 - 4 || x > G.x1 + 4 || t > d.t[d.n - 1] + 0.03) return hideTip();   // chưa chạy tới
    dom.hov.style.display = '';
    dom.hov.setAttribute('x1', G.X(d.t[k])); dom.hov.setAttribute('x2', G.X(d.t[k]));
    tip.textContent = '';
    const head = document.createElement('div');
    head.className = 'tt';
    head.textContent = 't = ' + PP.f(d.t[k], 2) + ' s';
    tip.appendChild(head);
    const row = (cls, name, val) => {
      const r = document.createElement('div');
      r.className = 'r';
      const a = document.createElement('span');
      const i = document.createElement('i');
      i.className = cls;
      a.appendChild(i); a.appendChild(document.createTextNode(name));
      const b = document.createElement('b');
      b.textContent = val;
      r.appendChild(a); r.appendChild(b);
      tip.appendChild(r);
    };
    row(FN_CLS[d.fn[k]], 'Chức năng', PP.FN[d.fn[k]]);
    G.P.forEach((p) => row(FN_CLS[d.fn[k]], p.name, p.get(k) == null ? '—' : p.fmt(p.get(k)) + ' ' + p.unit));
    const nf = d.faults.length, act = [];
    for (let i = 0; i < nf; i++) if (d.fa[k * nf + i]) act.push(d.faults[i].short);
    if (act.length) {
      const e = document.createElement('div');
      e.className = 'tt';
      e.style.margin = '4px 0 0';
      e.textContent = 'Lỗi: ' + act.join(', ');
      tip.appendChild(e);
    }
    tip.hidden = false;
    const pw = plot.clientWidth, tw = tip.offsetWidth, th = tip.offsetHeight;
    let lx = x + 16;
    if (lx + tw > pw - 4) lx = x - tw - 16;
    tip.style.left = Math.max(4, lx) + 'px';
    tip.style.top = Math.max(0, Math.min(plot.clientHeight - th - 4, (ev.clientY - svg.getBoundingClientRect().top) - th / 2)) + 'px';
  }
  function hideTip() {
    tip.hidden = true;
    if (dom.hov) dom.hov.style.display = 'none';
  }

  svg.addEventListener('pointermove', (ev) => {
    if (!d || !G || !d.n) return;
    if (dragging && PP.charts.onSeek) PP.charts.onSeek(frameAt(ev).k);
    showTip(ev);
  });
  svg.addEventListener('pointerleave', () => { if (!dragging) hideTip(); });
  svg.addEventListener('pointerdown', (ev) => {
    if (!d || !G || !d.n) return;
    dragging = true;
    svg.setPointerCapture(ev.pointerId);
    if (PP.charts.onSeek) PP.charts.onSeek(frameAt(ev).k);
  });
  const endDrag = (ev) => { dragging = false; try { svg.releasePointerCapture(ev.pointerId); } catch (e) { /* đã nhả */ } };
  svg.addEventListener('pointerup', endDrag);
  svg.addEventListener('pointercancel', endDrag);

  // ---------- Bảng (tương đương biểu đồ), mỗi giây một hàng, hiện dần ----------
  function tableHead() {
    const t = document.createElement('table');
    const tr = document.createElement('tr');
    ['Thời điểm', 'Chức năng', 'Lệch tâm (cm)', 'DLC nhỏ nhất (cm)', 'a_y lọc (m/s²)', 'Vô lăng (°)', 'Thời gian tính (ms)']
      .forEach((h) => { const th = document.createElement('th'); th.textContent = h; tr.appendChild(th); });
    const thead = document.createElement('thead'); thead.appendChild(tr); t.appendChild(thead);
    t.appendChild(document.createElement('tbody'));
    tablebox.textContent = '';
    tablebox.appendChild(t);
    tableRows = 0;
  }
  function addRow(sec) {
    const k = Math.min(d.n - 1, Math.max(0, Math.round((sec - d.t[0]) / d.dt)));
    const sr = d.veh.sr || 15;
    const r = document.createElement('tr');
    [PP.f(sec, 0) + ' s', PP.FN[d.fn[k]], PP.fs(d.off[k] * 100, 0), PP.f(Math.min(d.dl[k], d.dr[k]) * 100, 0),
      PP.f(d.ayf[k], 2), PP.fs(d.whl[k] * sr * 180 / Math.PI, 1), PP.f(d.cms[k], 2)]
      .forEach((c) => { const td = document.createElement('td'); td.textContent = c; r.appendChild(td); });
    tablebox.querySelector('tbody').appendChild(r);
  }
  function tableTick(k) {
    const s = Math.floor(d.t[k]);
    while (tableRows <= s) addRow(tableRows++);
  }
  function markRow(k) {
    const rows = tablebox.querySelectorAll('tbody tr');
    const idx = Math.min(rows.length - 1, Math.floor(d.t[Math.max(0, k)] || 0));
    rows.forEach((r, i) => r.classList.toggle('now', i === idx));
  }

  function setMode(m) {
    mode = m;
    svg.style.display = m === 'chart' ? '' : 'none';
    tablebox.hidden = m !== 'table';
    legend.style.visibility = m === 'chart' ? '' : 'hidden';
    hideTip();
    if (m === 'table') { if (d) { tableHead(); for (let k = 0; k < d.n; k++) tableTick(k); markRow(curK); } } else build();
  }

  PP.charts = {
    onSeek: null,
    // Lượt chạy mới: khung trống, chưa có chu kỳ nào.
    init(newCase) {
      d = newCase; curK = -1;
      initRanges();
      legend.textContent = '';
      tableHead();
      if (mode === 'chart') build();
    },
    // Khi chưa có lượt chạy: xoá hết.
    reset() { d = null; G = null; R = null; curK = -1; svg.textContent = ''; legend.textContent = ''; tablebox.textContent = ''; hideTip(); },
    push,
    setCursor,
    setMode,
    // Chạy xong: có thêm giới hạn R79 của a_y.
    finish() { if (d && mode === 'chart') build(); legendOf(); },
    resize() { if (d && mode === 'chart') build(); },
  };
  if (window.ResizeObserver) new ResizeObserver(() => PP.charts.resize()).observe(plot);
})();
