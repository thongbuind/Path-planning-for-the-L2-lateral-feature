(() => {
  'use strict';
  const PP = window.PP;
  const WB = (window.WB = { views: {}, leave: [] });

  const SVGNS = 'http://www.w3.org/2000/svg';
  WB.h = (tag, attrs, ...kids) => {
    const e = document.createElement(tag);
    for (const k in attrs || {}) {
      const v = attrs[k];
      if (v == null || v === false) continue;
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    kids.flat(Infinity).forEach((c) => c != null && c !== false && e.appendChild(typeof c === 'string' || typeof c === 'number' ? document.createTextNode(String(c)) : c));
    return e;
  };
  const h = WB.h;
  WB.ico = (id, cls) => {
    const s = document.createElementNS(SVGNS, 'svg');
    const u = document.createElementNS(SVGNS, 'use');
    u.setAttribute('href', '#' + id);
    s.appendChild(u);
    s.setAttribute('aria-hidden', 'true');
    if (cls) s.setAttribute('class', cls);
    return s;
  };
  WB.mono = (t, attrs) => h('span', { class: 'wb-mono', ...(attrs || {}) }, t);
  WB.wait = (t) => h('span', { class: 'wb-wait', text: t });
  WB.tag = (t) => h('span', { class: 'wb-tag', text: t });
  WB.lbl = (t, extra) => h('div', { class: 'wb-lbl', ...(extra || {}) }, t);
  WB.kv = (k, v) => h('div', { class: 'wb-kv' }, h('span', null, k), h('span', null, v));
  WB.card = (cls, ...kids) => h('section', { class: 'wb-card ' + (cls || '') }, kids);
  WB.page = (...kids) => h('div', { class: 'wb-col' }, kids);

  WB.num = (v) => {
    if (v == null || typeof v !== 'number' || !isFinite(v)) return '—';
    if (Number.isInteger(v)) return String(v).replace('-', '−');
    const a = Math.abs(v);
    const s = a >= 100 ? v.toFixed(1) : a >= 1 ? v.toFixed(2) : a >= 0.001 ? v.toPrecision(3) : v.toExponential(2);
    return PP.vn(s).replace('-', '−');
  };
  WB.limit = (s) => PP.limit(s == null ? '' : s);
  WB.time = (epoch) => {
    if (epoch == null) return '—';
    const d = new Date(epoch * 1000);
    const p = (n) => String(n).padStart(2, '0');
    const hms = p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
    return d.toDateString() === new Date().toDateString() ? hms : p(d.getDate()) + '/' + p(d.getMonth() + 1) + ' ' + hms;
  };
  WB.dur = (s) => (s == null || !isFinite(s) ? '—' : PP.f(Math.max(0, s), 1) + ' s');
  WB.short = (hash, n) => (hash ? String(hash).slice(0, n || 8) : '—');
  WB.prettyLabel = (label) => {
    const t = String(label || '').split(/\s+/).filter(Boolean);
    if (t.length < 2) return label || '—';
    const faults = t.slice(2).filter((x) => /^F\d+[a-z]$/.test(x)).map((x) => x.replace(/^(F\d+)([a-z])$/, '$1 $2'));
    const rest = t.slice(2).filter((x) => !/^F\d+[a-z]$/.test(x));
    const veh = rest.filter((x) => /^VP-\d$/.test(x));
    const seed = rest.join(' ').match(/seed \d+/);
    const other = rest.filter((x) => !/^VP-\d$/.test(x) && x !== 'seed' && !/^\d+$/.test(x));
    return [t[0] + ' ' + t[1], faults.length ? faults.join(' + ') : '', ...other, veh[0] || '', seed ? seed[0] : ''].filter(Boolean).join(' · ');
  };
  WB.copy = async (text, btn) => {
    try { await navigator.clipboard.writeText(text); } catch (e) { return; }
    if (!btn) return;
    const old = btn.textContent;
    btn.textContent = 'Đã sao chép';
    setTimeout(() => { btn.textContent = old; }, 1400);
  };

  WB.api = async (path, opts) => {
    const r = await fetch('api/' + path, opts);
    let body = null;
    try { body = await r.json(); } catch (e) {   }
    if (!r.ok) throw new Error((body && body.error) || 'HTTP ' + r.status);
    return body;
  };
  let catalogP = null;
  WB.catalog = () => (catalogP = catalogP || WB.api('catalog').catch((e) => { catalogP = null; throw e; }));
  WB.runs = async () => {
    const d = await WB.api('runs');
    WB.lastRuns = d;
    paintFoot(d);
    return d;
  };

  WB.cho = (o) => {
    const planned = o.planned || [];
    const avail = o.available || [];
    const ghost = o.ghost === 'table'
      ? h('div', { class: 'wb-ghost', 'aria-hidden': 'true' },
          h('div', { class: 'wb-lbl' }, 'Phác bố cục dự kiến'),
          h('div', { style: 'display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:8px;font-size:11.5px;color:var(--ink-3)' },
            ...['Ca', 'Baseline', 'Candidate', 'Delta, margin'].map((t) => h('span', null, t)),
            ...Array.from({ length: 12 }, (_, i) => h('div', { class: 'g', style: 'height:22px' + (i === 6 ? ';background:var(--wb-crit-bg)' : '') }))))
      : o.ghost === 'scene'
        ? h('div', { class: 'wb-ghost', 'aria-hidden': 'true' },
            h('div', { class: 'wb-lbl' }, 'Phác bố cục dự kiến'),
            h('div', { style: 'display:flex;flex-wrap:wrap;gap:12px' },
              h('div', { class: 'g', style: 'flex:3 1 360px;height:200px;display:grid;place-items:center;font-size:12px;color:var(--ink-3)' }, 'Scene 2D phát lại từ frames.ndjson.gz'),
              h('div', { style: 'flex:1 1 180px;display:flex;flex-direction:column;gap:8px' },
                ...[0, 1, 2, 3].map((i) => h('div', { class: 'g', style: 'height:30px' + (i === 1 ? ';background:var(--wb-crit-bg);color:var(--wb-crit-ink);display:flex;align-items:center;padding:0 10px;font-size:11.5px' : '') }, i === 1 ? 'PP-SWR-xxx trượt' : '')))),
            h('div', { class: 'g', style: 'position:relative;height:44px' },
              h('div', { style: 'position:absolute;left:31%;top:6px;bottom:6px;width:2px;background:var(--ink-3)' }),
              h('div', { style: 'position:absolute;left:calc(31% + 6px);top:13px;font-size:11px;color:var(--ink-2)' }, 'lỗi bơm thật'),
              h('div', { style: 'position:absolute;left:63%;top:6px;bottom:6px;width:2px;background:var(--lka)' }),
              h('div', { style: 'position:absolute;left:calc(63% + 6px);top:13px;font-size:11px;color:var(--ink-2)' }, 'first_fail_s')))
        : null;
    return h('section', { class: 'wb-cho', 'aria-label': 'Tính năng trong backlog' },
      h('div', { class: 'hd' }, h('span', { class: 'badge' }, WB.ico('i-wait'), 'Backlog, chưa cam kết')),
      h('div', { style: 'display:flex;flex-direction:column;gap:8px;max-width:720px' },
        h('h2', null, o.heading), h('p', { class: 'wb-sub' }, o.summary)),
      h('div', { class: 'two' },
        h('div', null, WB.lbl('Màn hình này sẽ có'),
          ...planned.map((p) => h('div', { class: 'wb-li' }, WB.ico('i-wait', 'dim'), h('span', { style: 'flex:1;min-width:0' }, p.t), h('span', { class: 'ref' }, p.ref || '')))),
        h('div', null, WB.lbl('Dùng được ngay hôm nay'),
          ...avail.map((a) => h('div', { class: 'wb-li' }, WB.ico('i-check', 'ok-ico'), h('div', { style: 'flex:1;min-width:0;display:flex;flex-direction:column;gap:3px' }, h('span', null, a.t), a.d ? h('code', null, a.d) : null))))),
      ghost);
  };

  const GROUPS = [
    { title: 'Thực thi', items: [
      { key: 'chay', label: 'Chạy mới', href: '#/chay', st: 'done' },
      { key: 'runs', label: 'Run', href: '#/runs', st: 'done' }] },
    { title: 'Đánh giá', items: [
      { key: 'suite', label: 'Suite và regression', href: '#/suite', st: 'done' },
      { key: 'review', label: 'So sánh và campaign', href: '#/review', st: 'done' }] },
    { title: 'Bằng chứng', items: [
      { key: 'tincay', label: 'Độ tin cậy', href: '#/tincay', st: 'part' },
      { key: 'nentang', label: 'Nền tảng', href: '#/nentang', st: 'part' }] },
  ];
  const ST_ICON = { done: ['i-check', 'st-done', 'Đã có'], part: ['i-half', 'st-part', 'Một phần'], wait: ['i-wait', 'st-wait', 'Backlog, chưa cam kết'] };
  function buildNav() {
    const box = document.getElementById('wb-groups');
    box.textContent = '';
    GROUPS.forEach((g) => {
      const grp = h('div', { class: 'wb-group', role: 'group', 'aria-label': g.title }, h('h2', null, g.title));
      g.items.forEach((it) => {
        const [id, cls, name] = ST_ICON[it.st];
        const svg = WB.ico(id, cls);
        svg.removeAttribute('aria-hidden');
        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', name);
        grp.appendChild(h('a', { class: 'wb-item', href: it.href, 'data-key': it.key }, svg, h('span', { class: 't' }, it.label), it.note ? h('small', null, it.note) : null));
      });
      box.appendChild(grp);
    });
    document.getElementById('wb-host').textContent = location.host || '—';
  }
  function markNav(key) {
    document.querySelectorAll('.wb-item').forEach((a) => {
      if (a.dataset.key === key) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
  }
  function paintFoot(d) {
    const led = document.getElementById('wb-led');
    led.className = 'wb-led ' + (d ? 'on' : 'off');
    const box = document.getElementById('wb-slots');
    if (!d) { box.textContent = 'Không nối được server'; return; }
    const active = d.runs.filter((r) => ['QUEUED', 'RUNNING', 'PAUSED'].includes(r.state)).length;
    const lim = d.limits || {};
    const keep = lim.keep != null ? ', giữ tối đa ' + lim.keep : '';
    box.textContent = 'Đang chạy ' + active + (lim.max_running ? '/' + lim.max_running + ' slot' : ' run') + '\nLưu ' + d.runs.filter((r) => !['QUEUED', 'RUNNING', 'PAUSED'].includes(r.state)).length + ' run' + keep;
    box.style.whiteSpace = 'pre-line';
  }
  async function pollFoot() {
    try { await WB.runs(); } catch (e) { paintFoot(null); }
  }

  const chay = document.getElementById('v-chay');
  const page = document.getElementById('v-page');
  let token = 0;
  WB.onLeave = (fn) => WB.leave.push(fn);
  const leaveAll = () => { WB.leave.splice(0).forEach((fn) => { try { fn(); } catch (e) {   } }); };

  async function route(quiet) {
    const parts = (location.hash || '#/chay').replace(/^#\/?/, '').split('/').filter(Boolean);
    const key = parts[0] || 'chay';
    const my = ++token;
    leaveAll();
    markNav(key === 'phat' ? 'runs' : ['chay', 'runs', 'suite', 'review', 'tincay', 'nentang'].includes(key) ? key : 'chay');
    if (key === 'phat' && parts[1]) {
      chay.hidden = false; page.hidden = true;
      document.title = 'Phát lại · Path Planner Workbench';
      window.dispatchEvent(new Event('resize'));
      PP.sim.play(parts[1], parts[2] != null ? Number(parts[2]) : null);
      return;
    }
    if (key === 'chay' || !WB.views[key]) {
      chay.hidden = false; page.hidden = true;
      document.title = 'Chạy mới · Path Planner Workbench';
      window.dispatchEvent(new Event('resize'));
      return;
    }
    chay.hidden = true; page.hidden = false;
    if (quiet !== true) {
      page.textContent = '';
      page.appendChild(h('div', { class: 'wb-loading', role: 'status' }, 'Đang tải…'));
    }
    try {
      const node = await WB.views[key](parts.slice(1));
      if (my !== token) return;
      const top = quiet === true ? page.scrollTop : 0;
      page.textContent = '';
      page.appendChild(node);
      page.scrollTop = top;
      const want = parts[2] === 'tep' && document.getElementById('tep');
      if (want) want.scrollIntoView({ block: 'start' });
    } catch (e) {
      if (my !== token) return;
      page.textContent = '';
      page.appendChild(h('div', { class: 'wb-err', role: 'alert' }, 'Không tải được màn hình: ' + e.message));
    }
    if (my === token && quiet !== true) document.getElementById('wb-content').focus({ preventScroll: true });
  }
  WB.go = (hash) => { if (location.hash === hash) route(); else location.hash = hash; };
  WB.title = (t) => { document.title = t + ' · Path Planner Workbench'; };

  WB.refresh = () => route(true);
  window.addEventListener('hashchange', () => route());
  buildNav();
  pollFoot();
  setInterval(() => { if (!document.hidden) pollFoot(); }, 5000);
  WB.catalog().then((cat) => { document.getElementById('wb-ver').textContent = cat.pp.replace(/ calibration.*/, '').replace('commit ', '· '); }).catch(() => {});
  // Chỉ dispatch route sau khi các mô-đun màn hình đã đăng ký.
  window.addEventListener('load', () => route());
})();
