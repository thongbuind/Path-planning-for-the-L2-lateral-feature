/* Màn hình mô phỏng 2D: nhìn từ trên xuống, xe ở bên trái màn hình và hướng sang phải, đường chạy ngang.
   Tỉ lệ đẳng hướng (1 m ngang = 1 m dọc). Vẽ khung d (chỉ số k) của lượt chạy đang diễn ra: hình học đường
   (Road của sim), pose xe (ground truth), quỹ đạo 31 điểm của planner (khung xe tại stamp), xe khác.
   Không tính lại gì của planner. */
(() => {
  'use strict';
  const PP = window.PP;

  const AHEAD_M = 96;           // bề rộng cảnh theo mét; xe đứng ở 14% từ trái: ~13 m phía sau, ~83 m phía trước
  const CAR_X = 0.14;
  const CAR_FRONT = 0.9, CAR_REAR = 0.95;
  const PAINT_HALF = 0.075;

  const cv = document.getElementById('scene');
  const ctx = cv.getContext('2d');
  const mm = document.getElementById('minimap');
  const mctx = mm.getContext('2d');

  let W = 0, H = 0, dpr = 1, S = 8, UX = 0, VY = 0;   // S: px mỗi mét
  let C = {};
  let cur = null, curK = -1;
  let road = null, sHint = -1;
  let ego = { x: 0, y: 0, c: 1, s: 0 };
  let rain = [];

  function readColors() {
    const cs = getComputedStyle(document.documentElement);
    const g = (n) => cs.getPropertyValue(n).trim();
    C = {
      sky: g('--scr-sky'), ground: g('--scr-ground'), road: g('--scr-road'), paint: g('--scr-paint'), lm: g('--scr-lm'), edge: g('--scr-edge'),
      text: g('--scr-text'), text2: g('--scr-text-2'),
      fn: [g('--scr-none'), g('--scr-hwa'), g('--scr-lka'), g('--scr-elk')],
    };
  }

  function resize() {
    const r = cv.parentElement.getBoundingClientRect();
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = Math.max(10, Math.round(r.width));
    H = Math.max(10, Math.round(r.height));
    cv.width = Math.round(W * dpr);
    cv.height = Math.round(H * dpr);
    S = W / AHEAD_M;
    UX = W * CAR_X;
    VY = H / 2;
    mm.width = Math.round(190 * dpr);     // kích thước CSS cố định; không đo khi HUD đang ẩn
    mm.height = Math.round(104 * dpr);
    rain = Array.from({ length: 110 }, () => ({ x: Math.random(), y: Math.random(), l: 8 + Math.random() * 14, v: 0.7 + Math.random() * 0.9 }));
    if (cur && curK >= 0) render(cur, curK); else clear();
  }

  // Khung xe (x tiến, y trái, gốc ở trục sau) -> điểm ảnh
  const Q = (x, y) => [UX + x * S, VY - y * S];
  const toEgo = (wx, wy) => {
    const rx = wx - ego.x, ry = wy - ego.y;
    return [rx * ego.c + ry * ego.s, -rx * ego.s + ry * ego.c];
  };

  // ---------- Đường ----------
  function setCase(d) {
    cur = d;
    curK = -1;
    road = d.road;
    sHint = -1;
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    for (let i = 0; i < road.x.length; i++) {
      x0 = Math.min(x0, road.x[i]); x1 = Math.max(x1, road.x[i]);
      y0 = Math.min(y0, road.y[i]); y1 = Math.max(y1, road.y[i]);
    }
    d._mm = { x0, x1, y0, y1 };
  }

  function clear() {
    if (!W) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = C.ground;
    ctx.fillRect(0, 0, W, H);
    mctx.setTransform(1, 0, 0, 1, 0, 0);
    mctx.clearRect(0, 0, mm.width, mm.height);
  }

  function roadPt(s, off) {
    const n = road.x.length;
    const i = PP.clamp(Math.floor(s), 0, n - 2), f = PP.clamp(s - i, 0, 1);
    const x = road.x[i] + (road.x[i + 1] - road.x[i]) * f;
    const y = road.y[i] + (road.y[i + 1] - road.y[i]) * f;
    const th = road.th[i] + (road.th[i + 1] - road.th[i]) * f;
    return [x - off * Math.sin(th), y + off * Math.cos(th)];
  }

  function scan(x, y, lo, hi) {
    let best = lo, bd = Infinity;
    for (let i = lo; i <= hi; i++) {
      const dx = road.x[i] - x, dy = road.y[i] - y, dd = dx * dx + dy * dy;
      if (dd < bd) { bd = dd; best = i; }
    }
    return [best, bd];
  }
  // Vị trí xe dọc đường (m). Tìm quanh vị trí khung trước cho nhanh; khi xem lại ở chỗ xa thì tìm lại toàn đường.
  function nearestS(x, y) {
    const n = road.x.length;
    let r = sHint >= 0 ? scan(x, y, Math.max(0, sHint - 40), Math.min(n - 1, sHint + 60)) : null;
    if (!r || r[1] > 15 * 15) r = scan(x, y, 0, n - 1);
    sHint = r[0];
    return r[0];
  }

  // Dải giữa hai độ lệch ngang o1, o2 so với tim làn, từ s0 tới s1
  function strip(o1, o2, s0, s1, step) {
    const A = [], B = [];
    s0 = Math.max(0, s0); s1 = Math.min(road.len, s1);
    for (let s = s0; s <= s1 + 1e-6; s += step) {
      const a = toEgo(...roadPt(s, o1)), b = toEgo(...roadPt(s, o2));
      A.push(Q(a[0], a[1])); B.push(Q(b[0], b[1]));
    }
    return [A, B];
  }
  function polyPath(A, B) {
    if (A.length < 2) return false;
    ctx.moveTo(A[0][0], A[0][1]);
    for (let i = 1; i < A.length; i++) ctx.lineTo(A[i][0], A[i][1]);
    for (let i = B.length - 1; i >= 0; i--) ctx.lineTo(B[i][0], B[i][1]);
    ctx.closePath();
    return true;
  }

  function extents() {
    let lo = Infinity, hi = -Infinity;
    for (const l of road.lines) if (l) { lo = Math.min(lo, l.o); hi = Math.max(hi, l.o); }
    for (const e of road.edges) if (e) { lo = Math.min(lo, e.o); hi = Math.max(hi, e.o); }
    if (!isFinite(lo)) { lo = -road.w / 2; hi = road.w / 2; }
    // không có vạch ngoài ở một bên: coi như đường còn tiếp tục (làn bên cạnh)
    if (!road.lines[0] && !road.edges[0]) hi += road.w;
    if (!road.lines[3] && !road.edges[1]) lo -= road.w;
    return [lo - 0.5, hi + 0.5];
  }
  const isDash = (t) => /DASH/i.test(t || '');
  const isDouble = (t) => /DOUBLE/i.test(t || '');
  // Nét đứt: DASH_ON m có sơn, hết chu kỳ DASH_PERIOD m, tính theo toạ độ dọc tim đường.
  // Vạch thật và vạch lane model dùng chung nên đứt đúng chỗ của nhau.
  const DASH_PERIOD = 12, DASH_ON = 4;

  // Dải mặt đường: độ lệch hằng số, hoặc theo từng mét khi làn đổi bề rộng
  function asphalt(sA, sB) {
    if (!road.ext) { const [lo, hi] = extents(); return strip(lo, hi, sA, sB, 2); }
    const A = [], B = [];
    for (let s = Math.max(0, sA); s <= Math.min(road.len, sB) + 1e-6; s += 2) {
      const i = Math.min(road.ext.lo.length - 1, Math.floor(s));
      const a = toEgo(...roadPt(s, road.ext.lo[i] - 0.5)), b = toEgo(...roadPt(s, road.ext.hi[i] + 0.5));
      A.push(Q(a[0], a[1])); B.push(Q(b[0], b[1]));
    }
    return [A, B];
  }

  // Mép đường: BARRIER là gờ liền dày; GRASS_GRAVEL, CURB... là hàng chấm thưa
  function drawEdge(e, sA, sB) {
    ctx.beginPath();
    let first = true;
    for (let s = Math.max(0, sA); s <= Math.min(road.len, sB); s += 2) {
      const q = toEgo(...roadPt(s, e.o)), p = Q(q[0], q[1]);
      (first ? ctx.moveTo : ctx.lineTo).call(ctx, p[0], p[1]);
      first = false;
    }
    ctx.strokeStyle = C.edge;
    if (/CURB|BARRIER|GUARD|WALL/i.test(e.t)) { ctx.lineWidth = 3.4; ctx.globalAlpha = 0.95; ctx.setLineDash([]); }
    else { ctx.lineWidth = 2.2; ctx.globalAlpha = 0.8; ctx.setLineDash([1, 6]); }
    ctx.stroke();
    ctx.setLineDash([]); ctx.globalAlpha = 1;
  }

  // Vạch sơn trên đường có độ lệch hằng số: liền, đứt, hoặc kép (hai vạch liền song song)
  function paintStrips(ln, lost, sA, sB) {
    const dash = isDash(ln.t) || lost, dbl = isDouble(ln.t) && !lost;
    const half = lost ? 0.04 : dbl ? 0.05 : PAINT_HALF;
    const offs = dbl ? [ln.o - 0.14, ln.o + 0.14] : [ln.o];
    ctx.beginPath();
    let any = false;
    for (const o of offs) {
      if (dash) {
        const on = lost ? 1.2 : DASH_ON;
        for (let s = Math.floor(sA / DASH_PERIOD) * DASH_PERIOD; s < sB; s += DASH_PERIOD) {
          const a = Math.max(s, sA), b = Math.min(s + on, sB);
          if (b - a < 0.2) continue;
          const [pl, pr] = strip(o - half, o + half, a, b, 1);
          any = polyPath(pl, pr) || any;
        }
      } else {
        const [pl, pr] = strip(o - half, o + half, sA, sB, 1);
        any = polyPath(pl, pr) || any;
      }
    }
    if (any) { ctx.fillStyle = C.paint; ctx.globalAlpha = lost ? 0.6 : 1; ctx.fill(); ctx.globalAlpha = 1; }
  }

  // Toạ độ dọc tim đường của chân đường vuông góc hạ từ một điểm thế giới; hint là chỉ số mẫu gần đó
  function footS(wx, wy, hint) {
    const n = road.x.length;
    let r = null;
    if (hint != null) {
      const lo = Math.max(0, Math.round(hint) - 8), hi = Math.min(n - 1, Math.round(hint) + 8);
      r = scan(wx, wy, lo, hi);
      if ((r[0] === lo && lo > 0) || (r[0] === hi && hi < n - 1)) r = null;   // chạm biên cửa sổ: tìm lại toàn đường
    }
    if (r === null) r = scan(wx, wy, 0, n - 1);
    const i = r[0], j = Math.min(i + 1, n - 1);
    const dx = road.x[j] - road.x[i], dy = road.y[j] - road.y[i], L = dx * dx + dy * dy;
    const u = L > 0 ? PP.clamp(((wx - road.x[i]) * dx + (wy - road.y[i]) * dy) / L, -1, 1) : 0;
    return i + u;
  }

  // Một polyline qua các điểm khung xe (E: [x,y]); on(sm) cho biết đoạn đó có sơn không, theo toạ độ s
  function strokeDashed(E, hintS, dash, onLen) {
    ctx.beginPath();
    let prevS = null, prev = null, open = false, hint = null;
    for (const e of E) {
      const wx = ego.x + e[0] * ego.c - e[1] * ego.s, wy = ego.y + e[0] * ego.s + e[1] * ego.c;
      const s = dash ? footS(wx, wy, hint) : 0;
      hint = s;
      const p = Q(e[0], e[1]);
      if (prev) {
        const on = !dash || (((prevS + s) / 2) % DASH_PERIOD + DASH_PERIOD) % DASH_PERIOD < onLen;
        if (on) { if (!open) ctx.moveTo(prev[0], prev[1]); ctx.lineTo(p[0], p[1]); open = true; } else open = false;
      }
      prev = p; prevS = s;
    }
    ctx.stroke();
  }

  // Vạch sơn của đường có hình học đoạn (làn đổi bề rộng): polyline theo toạ độ thế giới
  function paintPoly(ln, lost, sE) {
    const dash = isDash(ln.t) || lost;
    ctx.strokeStyle = C.paint; ctx.lineCap = 'butt'; ctx.lineJoin = 'round';
    ctx.lineWidth = lost ? 1 : Math.max(1.2, 0.15 * S);
    ctx.globalAlpha = lost ? 0.6 : 1;
    for (const seg of ln.segs) {
      const E = [];
      for (let j = 0; j < seg.length; j += 2) {
        const e = toEgo(seg[j], seg[j + 1]);
        if (e[0] > -45 && e[0] < 140) E.push(e);
      }
      if (E.length > 1) strokeDashed(E, sE, dash, lost ? 1.2 : DASH_ON);
    }
    ctx.globalAlpha = 1;
  }

  function drawRoad(d, k, sE) {
    const sA = sE - 40, sB = sE + 130;
    ctx.beginPath();
    const [A, B] = asphalt(sA, sB);
    if (polyPath(A, B)) { ctx.fillStyle = C.road; ctx.fill(); }

    const view = d.view[k] != null ? d.view[k] : 80;
    const nf = d.faults.length, lostNow = new Set();
    for (let i = 0; i < nf; i++) {
      const f = d.faults[i];
      if (f.lost && d.fa[k * nf + i]) f.lost.forEach((j) => lostNow.add(j));
    }

    for (const e of road.edges) if (e) drawEdge(e, sA, sB);

    // tim làn mình, nét chấm mờ, để thấy xe lệch bao nhiêu
    ctx.beginPath();
    for (let s = Math.max(0, sA); s <= Math.min(road.len, sB); s += 2) {
      const e = toEgo(...roadPt(s, 0)), p = Q(e[0], e[1]);
      (s === Math.max(0, sA) ? ctx.moveTo : ctx.lineTo).call(ctx, p[0], p[1]);
    }
    ctx.strokeStyle = C.text2; ctx.globalAlpha = 0.45; ctx.lineWidth = 1; ctx.setLineDash([1, 7]); ctx.stroke();
    ctx.setLineDash([]); ctx.globalAlpha = 1;

    // vạch kẻ của đường thật
    road.lines.forEach((ln, i) => {
      if (!ln) return;
      const lost = lostNow.has(i);
      if (ln.segs) paintPoly(ln, lost, sE); else paintStrips(ln, lost, sA, sB);
      if (lost) {
        const m = toEgo(...roadPt(sE + 33, ln.o));
        const p = Q(m[0], m[1]);
        ctx.font = '600 11px ui-sans-serif, system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillStyle = C.lm;
        ctx.globalAlpha = 0.95;
        ctx.fillText((document.documentElement.lang === 'en' ? 'lane model lost marking ' : 'lane model mất vạch ') + ['L2', 'L1', 'R1', 'R2'][i], p[0], p[1] + (i < 2 ? -13 : 22));
        ctx.globalAlpha = 1;
      }
    });

    // vùng ngoài tầm nhìn của camera: planner không thấy
    const vx = Q(view, 0)[0];
    if (vx < W) {
      ctx.fillStyle = 'rgba(0,0,0,.30)';
      ctx.fillRect(vx, 0, W - vx, H);
      ctx.strokeStyle = C.text2;
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 4]);
      ctx.beginPath(); ctx.moveTo(Math.round(vx) + 0.5, 0); ctx.lineTo(Math.round(vx) + 0.5, H); ctx.stroke();
      ctx.setLineDash([]);
    }
  }

  // ---------- Vạch và mép đường mà lane model báo cho planner ----------
  // Toạ độ thế giới, đặt theo tư thế xe lúc camera chụp. Kiểu nét theo `type` mà lane model báo:
  // D đứt, S liền, B kép (hai nét liền song song), U chưa rõ (chấm), E gờ liền, G cỏ sỏi (chấm). PREDICTED vẽ mờ hơn.
  function drawLaneModel(d, k, sE) {
    const li = d.lmk[k];
    if (li < 0) return;
    ctx.strokeStyle = C.lm; ctx.lineJoin = 'round'; ctx.lineCap = 'butt';
    for (const ln of d.lm[li].ls) {
      // đa thức đã lấy mẫu mỗi 4 m; nội suy tuyến tính mỗi 0,5 m để nét đứt khớp pha với vạch thật
      const W0 = [];
      const pts = ln.pts;
      for (let j = 0; j + 3 < pts.length; j += 2) {
        const m = Math.max(1, Math.round(Math.hypot(pts[j + 2] - pts[j], pts[j + 3] - pts[j + 1]) / 0.5));
        for (let q = 0; q < m; q++) W0.push([pts[j] + (pts[j + 2] - pts[j]) * q / m, pts[j + 1] + (pts[j + 3] - pts[j + 1]) * q / m]);
      }
      W0.push([pts[pts.length - 2], pts[pts.length - 1]]);
      const E = W0.map((p) => toEgo(p[0], p[1]));
      ctx.globalAlpha = ln.p ? 0.5 : 0.95;
      ctx.lineWidth = ln.t === 'E' ? 3 : ln.t === 'G' ? 2.2 : 1.7;
      if (ln.t === 'D') {
        strokeDashed(E, sE, true, DASH_ON);
      } else if (ln.t === 'B') {
        for (const sg of [-1, 1]) {
          const F = E.map((e, i) => {
            const a = E[Math.max(0, i - 1)], b = E[Math.min(E.length - 1, i + 1)];
            const tx = b[0] - a[0], ty = b[1] - a[1], n = Math.hypot(tx, ty) || 1;
            return [e[0] - sg * 0.17 * ty / n, e[1] + sg * 0.17 * tx / n];
          });
          strokeDashed(F, sE, false, 0);
        }
      } else {
        if (ln.t === 'U') ctx.setLineDash([1, 4]);
        else if (ln.t === 'G') ctx.setLineDash([1, 6]);
        strokeDashed(E, sE, false, 0);
        ctx.setLineDash([]);
      }
    }
    ctx.globalAlpha = 1;
  }

  // ---------- Quỹ đạo của planner ----------
  function drawPath(d, k) {
    const alt = d.alt && d.alt[k];
    if (alt) {   // Path của planner còn lại: có hiệu lực nhưng arbitrator không chọn.
      const ca = Math.cos(d.ego.yaw[k]), sa = Math.sin(d.ego.yaw[k]);
      ctx.globalAlpha = 0.6;
      ctx.strokeStyle = C.text;
      ctx.lineWidth = 1.5;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      for (let i = 0; i < 31; i++) {
        const px = alt[2 * i] / 100, py = alt[2 * i + 1] / 100;
        const e = toEgo(d.ego.x[k] + px * ca - py * sa, d.ego.y[k] + px * sa + py * ca), p = Q(e[0], e[1]);
        if (i) ctx.lineTo(p[0], p[1]); else ctx.moveTo(p[0], p[1]);
      }
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha = 1;
    }
    if (!d.tv[k]) return;
    const fn = d.fn[k], col = C.fn[fn];
    const base = k * 62;
    const c = Math.cos(d.ego.yaw[k]), s = Math.sin(d.ego.yaw[k]);
    const pts = [];
    for (let i = 0; i < 31; i++) {
      const px = d.traj[base + 2 * i] / 100, py = d.traj[base + 2 * i + 1] / 100;
      pts.push(toEgo(d.ego.x[k] + px * c - py * s, d.ego.y[k] + px * s + py * c));
    }
    const M = pts.map((p) => Q(p[0], p[1]));
    ctx.globalAlpha = fn === 0 ? 0.55 : 1;
    ctx.strokeStyle = col;
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.beginPath();
    M.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
    ctx.stroke();
    ctx.globalAlpha = 1;
    ctx.font = '600 11px ui-sans-serif, system-ui, sans-serif';
    ctx.textAlign = 'center';
    for (const sec of [1, 2, 3]) {
      const p = M[sec * 10];
      ctx.fillStyle = col;
      ctx.beginPath(); ctx.arc(p[0], p[1], 3.5, 0, 6.2832); ctx.fill();
      ctx.strokeStyle = '#0e1116'; ctx.lineWidth = 1.5; ctx.stroke();
      ctx.fillStyle = C.text;
      ctx.globalAlpha = 0.92;
      ctx.fillText(sec + ' s', p[0], p[1] - 10);
      ctx.globalAlpha = 1;
    }
  }

  // ---------- Xe ----------
  function rectPath(cx, cy, yaw, L, Wd) {   // tâm và hướng trong khung xe
    const c = Math.cos(yaw), s = Math.sin(yaw), hl = L / 2, hw = Wd / 2;
    return [[-hl, -hw], [hl, -hw], [hl, hw], [-hl, hw]].map(([lx, ly]) => Q(cx + lx * c - ly * s, cy + lx * s + ly * c));
  }
  function fillPoly(p, fill, stroke) {
    ctx.beginPath();
    p.forEach((q, i) => (i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1])));
    ctx.closePath();
    ctx.fillStyle = fill; ctx.fill();
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1; ctx.stroke(); }
  }

  function drawEgo(d, k) {
    const wb = d.veh.wb, L = wb + CAR_FRONT + CAR_REAR, Wd = d.veh.w * 0.93;
    const cx = (wb + CAR_FRONT - CAR_REAR) / 2;
    fillPoly(rectPath(cx + 0.12, -0.12, 0, L + 0.3, Wd + 0.2), 'rgba(0,0,0,.35)');       // bóng
    const ang = d.whl[k];                                                                  // bánh trước xoay theo góc lái thật
    for (const [ax, yaw] of [[0, 0], [wb, ang]]) {
      for (const sg of [-1, 1]) fillPoly(rectPath(ax, sg * (Wd / 2 - 0.05), yaw, 0.7, 0.26), '#0b0d11');
    }
    fillPoly(rectPath(cx, 0, 0, L, Wd), '#d9dde4', 'rgba(0,0,0,.25)');
    fillPoly(rectPath(wb - 0.35, 0, 0, 1.1, Wd * 0.82), '#2a303a');                          // kính chắn gió
    fillPoly(rectPath(-CAR_REAR + 0.35, 0, 0, 0.5, Wd * 0.78), '#2a303a');                  // kính sau
    const o = Q(0, 0);                                                                       // trục sau: gốc khung xe
    ctx.fillStyle = '#0e1116';
    ctx.beginPath(); ctx.arc(o[0], o[1], 2.2, 0, 6.2832); ctx.fill();
  }

  function drawTraffic(d, k) {
    const nobj = d.tr.dims.length;
    for (let i = 0; i < nobj; i++) {
      const o = (k * nobj + i) * 3;
      const e = toEgo(d.tr.pos[o], d.tr.pos[o + 1]);
      const yaw = d.tr.pos[o + 2] - Math.atan2(ego.s, ego.c);
      const [len, wid] = d.tr.dims[i];
      fillPoly(rectPath(e[0] + 0.12, e[1] - 0.12, yaw, len + 0.3, wid + 0.2), 'rgba(0,0,0,.35)');
      fillPoly(rectPath(e[0], e[1], yaw, len, wid), len > 8 ? '#6b7485' : '#8a93a3', 'rgba(0,0,0,.3)');
    }
  }

  function drawRain() {
    const t = performance.now() / 1000;
    ctx.strokeStyle = 'rgba(205,214,230,.20)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (const r of rain) {
      const y = ((r.y + t * r.v * 0.9) % 1.15) * H - 20;
      const x = ((r.x - t * 0.05 * r.v) % 1.05) * W;
      ctx.moveTo(x, y); ctx.lineTo(x - 3, y + r.l);
    }
    ctx.stroke();
  }

  function drawScale() {
    const x0 = W * 0.5 - 10 * S, y = H - 22;
    ctx.strokeStyle = C.text2; ctx.lineWidth = 1.5; ctx.lineCap = 'butt';
    ctx.beginPath();
    ctx.moveTo(x0, y - 4); ctx.lineTo(x0, y); ctx.lineTo(x0 + 20 * S, y); ctx.lineTo(x0 + 20 * S, y - 4);
    ctx.stroke();
    ctx.fillStyle = C.text2;
    ctx.font = '11px ui-sans-serif, system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('20 m', x0 + 10 * S, y - 7);
  }

  // ---------- Bản đồ nhỏ ----------
  function drawMini(d, k) {
    const w = mm.width / dpr, h = mm.height / dpr;
    mctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    mctx.clearRect(0, 0, w, h);
    const b = d._mm, pad = 12;
    const sc = Math.min((w - 2 * pad) / Math.max(1, b.x1 - b.x0), (h - 2 * pad) / Math.max(1, b.y1 - b.y0));
    const ox = (w - (b.x1 - b.x0) * sc) / 2, oy = (h + (b.y1 - b.y0) * sc) / 2;
    const X = (x) => ox + (x - b.x0) * sc, Y = (y) => oy - (y - b.y0) * sc;
    mctx.lineCap = 'round'; mctx.lineJoin = 'round';
    mctx.strokeStyle = 'rgba(255,255,255,.28)'; mctx.lineWidth = 3;
    mctx.beginPath();
    for (let i = 0; i < road.x.length; i += 2) (i ? mctx.lineTo : mctx.moveTo).call(mctx, X(road.x[i]), Y(road.y[i]));
    mctx.stroke();
    mctx.strokeStyle = C.text; mctx.globalAlpha = 0.9; mctx.lineWidth = 1.5;
    mctx.beginPath();
    for (let i = 0; i <= k; i += 6) (i ? mctx.lineTo : mctx.moveTo).call(mctx, X(d.ego.x[i]), Y(d.ego.y[i]));
    mctx.stroke(); mctx.globalAlpha = 1;
    const fn = d.fn[k];
    if (d.tv[k]) {
      const c = Math.cos(d.ego.yaw[k]), s = Math.sin(d.ego.yaw[k]), base = k * 62;
      mctx.strokeStyle = C.fn[fn]; mctx.lineWidth = 2.5;
      mctx.beginPath();
      for (let i = 0; i < 31; i += 2) {
        const px = d.traj[base + 2 * i] / 100, py = d.traj[base + 2 * i + 1] / 100;
        (i ? mctx.lineTo : mctx.moveTo).call(mctx, X(d.ego.x[k] + px * c - py * s), Y(d.ego.y[k] + px * s + py * c));
      }
      mctx.stroke();
    }
    const nobj = d.tr.dims.length;
    mctx.fillStyle = 'rgba(255,255,255,.55)';
    for (let i = 0; i < nobj; i++) {
      const o = (k * nobj + i) * 3;
      mctx.fillRect(X(d.tr.pos[o]) - 2, Y(d.tr.pos[o + 1]) - 2, 4, 4);
    }
    mctx.fillStyle = C.fn[fn]; mctx.strokeStyle = '#0e1116'; mctx.lineWidth = 2;
    mctx.beginPath(); mctx.arc(X(d.ego.x[k]), Y(d.ego.y[k]), 4, 0, 6.2832); mctx.stroke(); mctx.fill();
  }

  // ---------- Vẽ một khung ----------
  function render(d, k) {
    if (!d || !W || k < 0 || k >= d.n) return;
    cur = d; curK = k;
    ego = { x: d.ego.x[k], y: d.ego.y[k], c: Math.cos(d.ego.yaw[k]), s: Math.sin(d.ego.yaw[k]) };
    const sE = nearestS(ego.x, ego.y);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = C.ground;
    ctx.fillRect(0, 0, W, H);
    drawRoad(d, k, sE);
    drawLaneModel(d, k, sE);
    drawTraffic(d, k);
    drawPath(d, k);
    drawEgo(d, k);
    if (d.env && d.env.rain && !PP.reduceMotion) drawRain();
    drawScale();
    drawMini(d, k);
  }

  PP.scene = { setCase, render, clear, resize, readColors };
  PP.reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  readColors();
  window.addEventListener('resize', resize);
})();
