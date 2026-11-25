(() => {
  'use strict';
  const WB = window.WB;
  const PP = window.PP;
  const { h, ico, mono, wait, tag, lbl, kv, card, page } = WB;

  const ACTIVE = ['QUEUED', 'RUNNING', 'PAUSED'];
  const TRIG = { '': 'theo định nghĩa của lỗi', lka_active: 'khi LKA can thiệp', elk_active: 'khi ELK can thiệp', intervention_active: 'khi LKA hoặc ELK can thiệp', lcc_follow: 'khi LCC vào FOLLOW' };
  const jsonPost = (body) => ({ method: 'POST', headers: { 'Content-Type': 'application/json', 'Idempotency-Key': crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random() }, body: JSON.stringify(body || {}) });
  const libLine = (libs) => (libs || []).map((l) => l.pp_version).filter(Boolean).join(' | ') || null;

  function stInfo(r) {
    const s = r.state;
    if (s === 'QUEUED') return { key: 'run', text: 'Đang chờ', icon: 'i-dot', cls: 'good' };
    if (s === 'RUNNING') return { key: 'run', text: 'Đang chạy', icon: 'i-dot', cls: 'good' };
    if (s === 'PAUSED') return { key: 'run', text: 'Tạm dừng', icon: 'i-dot', cls: 'good' };
    if (s === 'COMPLETED') return { key: 'done', text: 'Hoàn tất', icon: 'i-dot', cls: '' };
    if (s === 'CANCELLED') return { key: 'cancel', text: 'Đã hủy', icon: 'i-sq', cls: 'dim' };
    if (s === 'TIMED_OUT') return { key: 'fail', text: 'Quá hạn', icon: 'i-warn', cls: 'bad' };
    return { key: 'fail', text: 'Lỗi thực thi' + (r.failure ? ' · ' + r.failure : ''), icon: 'i-warn', cls: 'bad' };
  }
  const rowLabel = (r) => WB.prettyLabel(r.label || r.target || '') || r.run_id;
  const duration = (r) => (r.ended && r.created ? r.ended - r.created : null);

  async function runList() {
    WB.title('Run');
    const st = { q: '', f: 'all' };
    let data = await WB.runs();
    const body = h('div', null);
    const chipsBox = h('div', { class: 'wb-chips', role: 'radiogroup', 'aria-label': 'Lọc theo trạng thái thực thi' });
    const live = h('span', { class: 'wb-small', role: 'status', 'aria-live': 'polite' });

    const FILTERS = [['all', 'Tất cả'], ['run', 'Đang chạy'], ['done', 'Hoàn tất'], ['fail', 'Lỗi thực thi'], ['cancel', 'Đã hủy']];
    const count = (k) => data.runs.filter((r) => k === 'all' || stInfo(r).key === k).length;

    function paint() {
      chipsBox.textContent = '';
      FILTERS.forEach(([k, t]) => {
        chipsBox.appendChild(h('button', { type: 'button', class: 'wb-chip', role: 'radio', 'aria-checked': String(st.f === k), onclick: () => { st.f = k; paint(); } },
          t, mono(String(count(k)))));
      });
      const q = st.q.trim().toLowerCase();
      const rows = data.runs.filter((r) => (st.f === 'all' || stInfo(r).key === st.f) &&
        (!q || (r.run_id + ' ' + rowLabel(r) + ' ' + (r.label || '') + ' ' + (r.message || '')).toLowerCase().includes(q)));
      body.textContent = '';
      body.appendChild(h('div', { class: 'wb-row runs h' }, ...['run_id', 'Ca', 'Nguồn', 'Thực thi', 'Kết luận', 'Thời lượng', 'Bắt đầu'].map((t) => h('span', null, t))));
      if (!rows.length) body.appendChild(h('div', { class: 'wb-loading' }, data.runs.length ? 'Không có run nào khớp bộ lọc.' : 'Chưa có run nào. Bấm Chạy mới để bắt đầu.'));
      rows.forEach((r) => {
        const s = stInfo(r);
        let verdict;
        if (r.verdict === 'pass') verdict = h('span', { class: 'wb-ico good' }, ico('i-check'), h('span', { style: 'display:flex;flex-direction:column;gap:1px' }, h('b', { style: 'font-weight:600' }, 'Đạt'), mono(r.passed + '/' + r.applicable + ' tiêu chí', { class: 'wb-mono dim', style: 'font-size:11px' })));
        else if (r.verdict === 'fail') verdict = h('span', { class: 'wb-ico bad' }, ico('i-x'), h('span', { style: 'display:flex;flex-direction:column;gap:1px' }, h('b', { style: 'font-weight:600' }, 'Trượt'), mono((r.first_fail || '') + ' · ' + r.passed + '/' + r.applicable, { class: 'wb-mono dim', style: 'font-size:11px' })));
        else if (r.verdict === 'not_judged') verdict = h('span', { class: 'dim', style: 'display:flex;flex-direction:column;gap:1px' }, h('b', { style: 'font-weight:600' }, 'Không được chấm'), mono(r.passed + '/' + r.applicable + ' tiêu chí', { class: 'wb-mono dim', style: 'font-size:11px' }));
        else verdict = h('span', { class: 'dim', style: 'display:flex;flex-direction:column;gap:1px' }, h('b', { style: 'font-weight:600' }, 'Không có'), h('span', { class: 'wb-mono', style: 'font-size:11px' }, ACTIVE.includes(r.state) ? 'run chưa xong' : 'run không chạy hết'));
        body.appendChild(h('a', { class: 'wb-row runs', href: '#/runs/' + r.run_id },
          h('span', { class: 'wb-mono', style: 'font-size:12.5px' }, r.run_id, r.pinned ? h('span', { class: 'wb-tag', style: 'margin-left:6px' }, 'ghim') : null),
          h('span', { style: 'min-width:0' }, rowLabel(r)),
          h('span', { style: 'font-size:12px;color:var(--ink-2)' }, r.source || '—'),
          h('span', { class: 'wb-ico ' + s.cls }, ico(s.icon), h('span', { style: 'font-weight:500' }, s.text)),
          verdict,
          mono(WB.dur(duration(r)), { style: 'font-size:12.5px;color:var(--ink-2)' }),
          mono(WB.time(r.created), { style: 'font-size:12.5px;color:var(--ink-2)' })));
      });
      const act = data.runs.filter((r) => ACTIVE.includes(r.state)).length;
      live.textContent = act ? act + ' run đang chạy, danh sách tự cập nhật' : '';
    }

    const search = h('input', { class: 'wb-input', type: 'search', placeholder: 'Tìm theo run_id, ca, lỗi…', 'aria-label': 'Tìm run', oninput: (e) => { st.q = e.target.value; paint(); } });
    const lim = data.limits || {};
    const root = page(
      h('header', { class: 'wb-head' },
        h('div', null, h('h1', null, 'Run'), h('p', { class: 'wb-sub' }, 'Mọi run của workbench, kể cả run chạy khi tab đã đóng. Trạng thái thực thi và kết luận đánh giá nằm ở hai cột riêng.')),
        h('a', { class: 'wb-btn primary', href: '#/chay' }, 'Chạy mới')),
      h('div', { class: 'wb-tools' }, search, chipsBox, live),
      h('div', { class: 'wb-table' }, body),
      h('div', { class: 'wb-small', style: 'display:flex;flex-wrap:wrap;gap:8px 24px' },
        h('span', null, 'Đọc từ ', mono('GET /api/runs'), '.'),
        h('span', null, lim.keep != null ? 'Dọn tự động: giữ ' + lim.keep + ' run gần nhất' + (lim.max_bytes ? ' hoặc ' + PP.f(lim.max_bytes / 1e9, 0) + ' GB' : '') + '. Run đã ghim không bị xóa.' : '')));
    paint();
    const t = setInterval(async () => {
      if (document.hidden) return;
      try { data = await WB.runs(); paint(); } catch (e) {   }
    }, data.runs.some((r) => ACTIVE.includes(r.state)) ? 2000 : 6000);
    WB.onLeave(() => clearInterval(t));
    return root;
  }

  const cfgOf = (d) => (d.request && d.request.config) || null;
  function cfgLabel(c) {
    if (!c || !c.scenario) return null;
    const f = (c.faults || []).map((x) => x[0] + ' ' + x[1]).join(' + ');
    return [c.scenario.sid + ' ' + c.scenario.v, f ? f + (c.trigger ? ' ' + TRIG[c.trigger] : '') : '', c.vehicle, 'seed ' + c.seed].filter(Boolean).join(' · ');
  }
  function simLabel(sim) {
    const o = [];
    if (sim && sim.road_mu != null) o.push('road_mu ' + PP.vn(sim.road_mu));
    if (sim && sim.camera_latency_ms != null) o.push('camera ' + sim.camera_latency_ms + ' ms');
    if (sim && sim.perception_noise_scale != null) o.push('nhiễu ×' + PP.vn(sim.perception_noise_scale));
    return o;
  }
  const applicable = (ev) => (ev ? ev.criteria.filter((c) => c.applicable) : []);
  const failing = (ev) => applicable(ev).filter((c) => !c.passed);

  function verdictPill(d) {
    const ev = d.evaluation;
    if (!ev) return h('span', { class: 'wb-pill' }, h('span', { class: 'dim' }, 'Kết luận'), h('b', { style: 'font-weight:600' }, 'Không có'), h('span', { class: 'dim' }, ACTIVE.includes(d.state) ? 'run chưa xong' : 'run không chạy hết'));
    const app = applicable(ev), bad = failing(ev);
    if (!bad.length && ev.passed === null) return h('span', { class: 'wb-pill' }, h('span', { class: 'dim' }, 'Kết luận'), ico('i-warn'), h('b', { style: 'font-weight:600' }, 'Không được chấm'), h('span', { class: 'dim' }, app.length + ' tiêu chí đạt, nhưng điều kiện của ca chưa đủ'));
    if (!bad.length) return h('span', { class: 'wb-pill pass' }, h('span', null, 'Kết luận'), ico('i-check', 'ok-ico'), h('b', { style: 'font-weight:600' }, 'Đạt trong phạm vi đã thử'), h('span', null, app.length + '/' + app.length + ' tiêu chí áp dụng'));
    const ids = bad.slice(0, 2).map((c) => c.id).join(', ') + (bad.length > 2 ? ' +' + (bad.length - 2) : '');
    return h('span', { class: 'wb-pill fail' }, h('span', null, 'Kết luận'), ico('i-x'), h('b', { style: 'font-weight:600' }, 'Trượt · ' + ids), h('span', null, bad.length + ' trên ' + app.length + ' tiêu chí áp dụng'));
  }

  function runHeader(d, id, tab, kids) {
    const ex = d.execution || d;
    const s = stInfo({ state: d.state || ex.state, failure: d.failure || ex.failure });
    const cfg = cfgOf(d);
    const title = cfgLabel(cfg) || WB.prettyLabel(ex.label || (d.manifest && d.manifest.target) || '') || id;
    const git = d.manifest && d.manifest.git;
    const pinBtn = h('button', { type: 'button', class: 'wb-btn', 'aria-pressed': String(!!d.pinned), disabled: ACTIVE.includes(d.state), onclick: async (e) => {
      const b = e.currentTarget;
      b.disabled = true;
      try { const r = await WB.api('runs/' + id + '/pin', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ on: !d.pinned }) }); d.pinned = r.pinned; b.textContent = r.pinned ? 'Bỏ ghim' : 'Ghim'; b.setAttribute('aria-pressed', String(r.pinned)); } catch (err) { b.textContent = 'Không ghim được'; }
      b.disabled = false;
    } }, d.pinned ? 'Bỏ ghim' : 'Ghim');
    const copyBtn = h('button', { type: 'button', class: 'wb-btn', onclick: (e) => WB.copy(id, e.currentTarget) }, 'Sao chép run_id');
    const canRerun = !!(d.manifest && d.manifest.bundle && d.manifest.bundle.behavior_checksum);
    const rerunMsg = h('span', { class: 'wb-small bad', role: 'alert' });
    const rerunBtn = h('button', { type: 'button', class: 'wb-btn', disabled: !canRerun || ACTIVE.includes(d.state), title: canRerun ? 'Chạy lại ca này và so behavior checksum với bản gốc' : 'Run này không có đủ recipe và checksum', onclick: async (e) => {
      const b = e.currentTarget;
      b.disabled = true; rerunMsg.textContent = '';
      try { const r = await WB.api('runs/' + id + '/rerun', jsonPost()); WB.go('#/runs/' + r.run_id); }
      catch (err) { rerunMsg.textContent = 'Không mở lại được: ' + err.message; b.disabled = false; }
    } }, 'Mở lại (chạy lại)');
    const canPlay = !!d.request && !ACTIVE.includes(d.state);
    const tabs = [['tong-quan', 'Tổng quan', null], ['dieu-tra', 'Điều tra', null], ['tep', 'Tệp bundle', null], ['con', 'Run con và giả thuyết', tag(String(kids.length))]];
    return [
      h('div', { class: 'wb-crumb' }, h('a', { href: '#/runs' }, 'Run'), ' / ', tab === 'tong-quan' ? mono(id) : h('a', { href: '#/runs/' + id }, mono(id)), tab === 'tong-quan' ? null : ' / ' + (tabs.find((t) => t[0] === tab) || [0, ''])[1]),
      h('header', { class: 'wb-head', style: 'align-items:flex-start' },
        h('div', { style: 'gap:10px' }, h('h1', null, title),
          h('div', { class: 'wb-pills' },
            h('span', { class: 'wb-pill' }, h('span', { class: 'dim' }, 'Thực thi'), ico(s.icon, s.cls), h('b', { style: 'font-weight:600' }, s.text), mono(WB.dur(ex.ended && ex.started ? ex.ended - ex.started - (ex.paused_s || 0) : null), { class: 'wb-mono dim' })),
            verdictPill(d))),
        h('div', { class: 'wb-btns' },
          canPlay ? h('a', { class: 'wb-btn', href: '#/phat/' + id, title: 'Xem lại từ bundle, không chạy planner' }, 'Phát lại') : null,
          rerunBtn,
          h('a', { class: 'wb-btn', href: '#/runs/' + id + '/con' }, 'Tạo run con'), copyBtn, pinBtn, rerunMsg)),
      git && git.dirty ? h('div', { class: 'wb-note', role: 'note' }, ico('i-warn'), h('span', null, 'Bundle tạo từ working tree có ' + (git.changed || []).length + ' thay đổi chưa commit (', mono((git.branch || '?') + ' @ ' + git.short), '). Chạy lại được trên máy này, nhưng chưa truy được về một commit.')) : null,
      h('nav', { class: 'wb-tabs', 'aria-label': 'Phần của run' }, ...tabs.map(([k, t, extra]) => h('a', { href: '#/runs/' + id + (k === 'tong-quan' ? '' : '/' + k), 'aria-current': k === (tab === 'tep' ? 'tep' : tab) ? 'page' : null }, t, extra))),
    ];
  }

  async function runDetail(id, tab) {
    WB.title('Run ' + id.slice(-6));
    const [d, all] = await Promise.all([WB.api('runs/' + id), WB.runs()]);
    if (d.execution) { d.state = d.execution.state; d.failure = d.execution.failure; }
    const kids = all.runs.filter((r) => r.parent_run_id === id);
    const head = runHeader(d, id, tab, kids);
    if (ACTIVE.includes(d.state)) {
      const t = setTimeout(() => WB.refresh(), 2000);
      WB.onLeave(() => clearTimeout(t));
      return page(...head, card('', lbl('Đang chạy'), kv('Trạng thái', d.state), kv('Pha', mono(d.phase || '—')),
        h('p', { class: 'wb-small', style: 'padding-top:10px' }, 'Run chưa xong nên chưa có bundle. Trang tự cập nhật. Xem trực tiếp ở ', h('a', { href: '#/chay' }, 'Chạy mới'), '.')));
    }
    const check = rerunCard(d);
    if (tab === 'dieu-tra') return page(...head, check, investigate(d, id));
    if (tab === 'con') return page(...head, check, await childrenTab(d, id, kids));
    return page(...head, check, await overview(d, id));
  }

  function rerunCard(d) {
    const r = d.rerun;
    if (!r) return null;
    const src = r.expected.source || {};
    const origin = src.run ? h('a', { class: 'wb-mono', href: '#/runs/' + src.run }, src.run) : src.suite ? h('a', { class: 'wb-mono', href: '#/suite/' + src.suite }, src.case) : mono('—');
    const same = r.match === true;
    return h('section', { class: 'wb-note', role: 'status', style: 'display:flex;flex-direction:column;gap:6px;align-items:flex-start' },
      h('b', { class: same ? 'good' : 'bad', style: 'font-weight:600' }, r.match === null ? 'Lần mở lại không hoàn tất' : same ? 'Checksum khớp bản gốc' : 'Checksum không khớp bản gốc'),
      h('span', null, 'Bản gốc: ', origin, ' · ', mono(WB.short(r.expected.behavior_checksum, 12)), r.actual ? [' · lần này: ', mono(WB.short(r.actual.behavior_checksum, 12))] : null),
      ...r.reasons.map((t) => h('span', null, t)));
  }

  const fmtSize = (n) => (n >= 1e6 ? PP.f(n / 1e6, 1) + ' MB' : n >= 1e3 ? PP.f(n / 1e3, 1) + ' KB' : n + ' B');

  async function overview(d, id) {
    const m = d.manifest || {}, ex = d.execution || {}, ev = d.evaluation, bun = m.bundle || {}, libs = m.libraries || [], git = m.git || {};
    const [files, gold] = await Promise.all([WB.api('runs/' + id + '/bundle').catch(() => null), WB.api('golden').catch(() => null)]);
    const match = gold && gold.recorded && bun.behavior_checksum ? gold.cases.filter((c) => c.checksum === bun.behavior_checksum) : [];
    const rc = bun.recipe || {};
    const recipe = rc.kind === 'catalog'
      ? ['catalog ' + rc.sid + ' ' + rc.v, (rc.faults || []).length ? (rc.faults || []).map((f) => f.join(' ')).join(', ') : null, rc.vehicle, ...simLabel(rc.sim)].filter(Boolean).join(' · ')
      : JSON.stringify(rc);

    const ident = card('',
      h('div', { style: 'display:flex;align-items:center;gap:8px;padding-bottom:6px' }, lbl('Danh tính'),
        match.length ? h('span', { class: 'wb-ico good', style: 'margin-left:auto;font-size:12px;font-weight:600' }, ico('i-check'), 'Checksum trùng golden ' + match.map((c) => c.id + (c.seed > 1 ? ' seed ' + c.seed : '')).join(', ')) : null),
      kv('case_hash', mono(bun.case_hash || '—', { style: 'font-size:12px' })),
      kv('behavior_checksum', mono(bun.behavior_checksum || '—', { style: 'font-size:12px' })),
      kv('Recipe', mono(recipe || '—', { style: 'font-size:12px' })),
      kv('Schema', mono([bun.schema, bun.resolved_case_schema, bun.evaluation_schema].filter(Boolean).join(' · ') || '—', { style: 'font-size:12px' })));

    let all = false;
    const critBox = h('div', null);
    const toggle = h('button', { type: 'button', class: 'wb-btn', style: 'align-self:flex-start;margin-top:10px', 'aria-expanded': 'false' });
    function paintCrit() {
      critBox.textContent = '';
      if (!ev) return;
      critBox.appendChild(h('div', { class: 'wb-row crit h', style: 'min-height:0;padding:0 0 8px' }, ...['ID', 'Metric', 'Giá trị · ngưỡng', 'Kết luận'].map((t) => h('span', null, t))));
      const list = ev.criteria.filter((c) => all || c.applicable).sort((a, b) => (a.applicable && !a.passed ? 0 : 1) - (b.applicable && !b.passed ? 0 : 1));
      list.forEach((c) => {
        const bad = c.applicable && !c.passed;
        critBox.appendChild(h('div', { class: 'wb-row crit' },
          mono(c.id, { style: 'font-size:12px' }),
          h('span', { style: 'color:var(--ink-2);line-height:1.4' }, c.metric, bad ? h('span', { class: 'wb-small', style: 'display:block' }, 'Lần trượt đầu: ', c.first_fail_s != null ? (d.request ? h('a', { href: '#/phat/' + id + '/' + c.first_fail_s }, 't = ' + WB.num(c.first_fail_s) + ' s') : 't = ' + WB.num(c.first_fail_s) + ' s') : 'tiêu chí này chấm trên cả lượt') : null),
          mono(WB.num(c.value) + ' · ' + WB.limit(c.limit), { style: 'font-size:12px' + (bad ? ';color:var(--wb-crit-ink)' : '') }),
          !c.applicable ? h('span', { class: 'dim' }, 'Không áp dụng')
            : bad ? h('span', { class: 'wb-ico bad', style: 'font-weight:600' }, ico('i-x'), 'Trượt')
              : h('span', { class: 'wb-ico good', style: 'font-weight:600' }, ico('i-check'), 'Đạt')));
      });
      toggle.textContent = all ? 'Chỉ tiêu chí áp dụng' : 'Xem đủ ' + ev.criteria.length + ' tiêu chí';
      toggle.setAttribute('aria-expanded', String(all));
    }
    toggle.addEventListener('click', () => { all = !all; paintCrit(); });
    paintCrit();
    const targets = ev && ev.targets && ev.targets.length ? h('p', { class: 'wb-small', style: 'padding-top:12px' }, 'Chỉ số theo dõi, không chấm: ',
      ev.targets.slice(0, 2).map((t, i) => [i ? ', ' : '', t.metric.toLowerCase(), ' ', mono(WB.num(t.value) + (t.unit ? ' ' + t.unit : '')), ' (' + t.id + ')'])) : null;
    const na = ev ? ev.criteria.filter((c) => !c.applicable).length : 0;
    const evalCard = card('',
      h('div', { style: 'display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px;padding-bottom:6px' }, lbl('Kết quả đánh giá'),
        ev ? h('span', { class: 'wb-small' }, ev.criteria.length + ' tiêu chí · ' + applicable(ev).length + ' áp dụng, ' + (applicable(ev).length - failing(ev).length) + ' đạt, ' + failing(ev).length + ' trượt · ' + na + ' không áp dụng · ' + (ev.issues ? ev.issues.length : 0) + ' vấn đề') : null,
        ev ? mono('evaluator ' + WB.short(ev.evaluator_commit, 7), { class: 'wb-mono dim', style: 'margin-left:auto;font-size:11.5px' }) : null),
      ev ? critBox : h('p', { class: 'wb-small' }, 'Run không có evaluation.json: ' + (ex.message || 'chưa chấm') + '.'),
      ev ? toggle : null, targets);

    const lc = bun.recipe && bun.recipe.vehicle;
    const scope = card('warn', lbl('Phạm vi kết luận'),
      kv('Mô hình xe', mono(lc || (cfgOf(d) || {}).vehicle || '—')),
      kv('Validation', h('b', { style: 'font-weight:600;color:var(--wb-warn-ink)' }, 'chưa đánh giá')),
      kv('Hồ sơ model', h('span', null, h('a', { href: '#/tincay' }, 'Simulation Handbook'))),
      h('p', { class: 'wb-small', style: 'padding-top:10px;color:var(--ink-2)' }, 'Đạt chỉ có nghĩa trong điều kiện phép thử và miền dùng của model. Không nói gì về xe thật.'));

    const execCard = card('', lbl('Thực thi'),
      kv('Trạng thái', ex.state || '—'),
      kv('Pha cuối · mã thoát', mono((ex.phase || '—') + ' · ' + (ex.returncode == null ? '—' : ex.returncode))),
      kv('Tạo · kết thúc', mono(WB.time(ex.created) + ' · ' + WB.time(ex.ended))),
      kv('Timeout · tạm dừng', mono(WB.num(ex.timeout_s) + ' s · ' + WB.num(ex.paused_s || 0) + ' s')),
      ex.failure ? kv('Lớp lỗi', h('span', { class: 'bad' }, ex.failure + (ex.message ? ' · ' + ex.message : ''))) : null);

    const libCard = card('', lbl('Thư viện SUT' + (libs.length > 1 ? ' (' + libs.length + ')' : '')),
      ...(libs.length ? libs : [{}]).flatMap((lib) => {
        const b = lib.build || {};
        return [
          kv('Phiên bản', mono(lib.pp_version || '—', { style: 'font-size:12px' })),
          kv('calibration · t7', mono((b.calibration || '—') + ' · ' + (b.t7 || '—'), { style: 'font-size:12px' })),
          kv('sha256', mono(lib.sha256 ? lib.sha256.slice(0, 16) + '…' + lib.sha256.slice(-11) : '—', { style: 'font-size:12px' })),
          b.commit && git.commit && !git.commit.startsWith(b.commit.slice(0, 7)) ? h('p', { class: 'wb-small', style: 'padding-top:10px;color:var(--wb-warn-ink)' }, 'Thư viện build từ ' + b.commit.slice(0, 7) + ', khác commit mã nguồn ' + git.short + '.') : null,
        ];
      }));

    const okFiles = files ? files.files.filter((f) => f.name !== 'SHA256SUMS') : [];
    const bundleCard = h('section', { class: 'wb-card', id: 'tep' },
      h('div', { style: 'display:flex;align-items:center;gap:8px;padding-bottom:6px' }, lbl('Tệp bundle'),
        files ? h('span', { class: 'wb-ico ' + (files.problems.length ? 'bad' : 'good'), style: 'margin-left:auto;font-size:12px;font-weight:600' }, ico(files.problems.length ? 'i-warn' : 'i-check'),
          files.problems.length ? 'SHA256SUMS lệch: ' + files.problems.join(', ') : 'SHA256SUMS khớp ' + okFiles.length + '/' + okFiles.length) : null),
      ...(files ? files.files.map((f) => h('div', { class: 'wb-kv' }, h('a', { class: 'wb-mono', style: 'font-size:12px', href: 'api/runs/' + id + '/files/' + f.name, download: id + '-' + f.name }, f.name), mono(fmtSize(f.size), { style: 'font-size:12px;color:var(--ink-3)' }))) : [h('p', { class: 'wb-small' }, 'Không đọc được danh sách tệp.')]),
      h('p', { class: 'wb-small', style: 'padding-top:10px' }, 'Bất biến sau khi hoàn tất.'));

    return h('div', { class: 'wb-cols' }, h('div', { class: 'a' }, ident, evalCard), h('div', { class: 'b' }, scope, execCard, libCard, bundleCard));
  }

  const FAULT_LISTS = [['lane_faults', 'Lane model'], ['channel_faults', 'Kênh'], ['sensor_faults', 'Cảm biến'], ['ego_motion_faults', 'Ego-motion']];
  function investigate(d, id) {
    const ev = d.evaluation, canPlay = !!d.request;
    const at = (t, text) => (canPlay ? h('a', { class: 'wb-btn', style: 'height:30px;padding:0 10px;font-size:12.5px', href: '#/phat/' + id + (t != null ? '/' + t : '') }, text) : mono('không có khung hình'));
    if (!ev) return card('', lbl('Điều tra'), h('p', { class: 'wb-sub' }, 'Run không có evaluation.json: ' + ((d.execution || {}).message || 'chưa chấm') + '.'), canPlay ? at(null, 'Phát lại phần đã chạy') : null);

    const rows = failing(ev).map((c) => ({ id: c.id, text: c.metric, t: c.first_fail_s, value: WB.num(c.value) + ' · ' + WB.limit(c.limit) }));
    (ev.issues || []).filter((i) => i.kind !== 'not_judged').forEach((i) => rows.push({ id: i.requirement || i.kind, text: i.text, t: i.first_fail_s, value: '—' }));
    rows.sort((a, b) => (a.t == null ? Infinity : a.t) - (b.t == null ? Infinity : b.t));
    const fails = card('', h('div', { style: 'display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding-bottom:8px' }, lbl('Trượt theo thời gian'), h('span', { style: 'margin-left:auto' }, at(null, 'Phát lại từ đầu'))),
      rows.length ? rows.map((r) => h('div', { class: 'wb-row crit' }, mono(r.id, { style: 'font-size:12px' }),
        h('span', { style: 'color:var(--ink-2);line-height:1.4' }, r.text), mono(r.value, { style: 'font-size:12px;color:var(--wb-crit-ink)' }),
        r.t != null ? at(r.t, 't = ' + WB.num(r.t) + ' s') : h('span', { class: 'dim' }, 'chấm trên cả lượt')))
        : h('p', { class: 'wb-small' }, 'Không có tiêu chí trượt.'));

    const notJudged = (ev.issues || []).filter((i) => i.kind === 'not_judged');
    const judged = notJudged.length ? card('warn', lbl('Không được chấm'), ...notJudged.map((i) => h('p', { class: 'wb-sub' }, i.text))) : null;

    const info = ev.info || {}, events = Object.entries(info.fault_events_s || {});
    const scCase = (d['resolved-case'] || {}).case || {};
    const planned = FAULT_LISTS.flatMap(([key, name]) => (scCase[key] || []).map((f) => ({ name, kind: f.kind + (f.channel ? ' · ' + f.channel : '') + (f.signal ? ' · ' + f.signal : ''), start: f.start_s, dur: f.duration_s, trigger: f.trigger })));
    const faults = card('', lbl('Lỗi trong ca'),
      planned.length ? planned.map((f) => kv(f.name + ' · ' + f.kind, mono(f.trigger ? 'theo sự kiện ' + f.trigger : 't = ' + WB.num(f.start) + ' s' + (f.dur != null ? ', trong ' + WB.num(f.dur) + ' s' : ', tới hết ca')))) : h('p', { class: 'wb-small' }, 'Ca này không bơm lỗi.'),
      events.map(([k, t]) => kv('Sự kiện ' + k, t == null ? h('b', { class: 'bad', style: 'font-weight:600' }, 'không xảy ra, lỗi không được bơm') : at(t, 't = ' + WB.num(t) + ' s'))));

    const legend = card('', lbl('Nguồn dữ liệu khi phát lại'),
      kv('Xe, làn, khoảng hở, a_y', 'truth của simulator'), kv('Lane model, yêu cầu, LeadTarget', 'planner nhận (perception)'),
      kv('LccStatus, InterventionStatus', 'output của từng planner'), kv('Planner được chọn, path nét liền', 'arbitrator chạy thử'),
      h('p', { class: 'wb-small', style: 'padding-top:8px' }, 'Thời điểm trượt chỉ gợi ý chỗ cần nhìn. Kết luận nguyên nhân cần run đối chứng ở tab Run con.'));
    return h('div', { class: 'wb-cols' }, h('div', { class: 'a' }, fails, judged), h('div', { class: 'b' }, faults, legend));
  }

  const jsonLine = (v) => JSON.stringify(v == null ? null : v);
  function diffLines(a, b) {
    const keys = ['scenario', 'faults', 'trigger', 'vehicle', 'seed', 'sim', 'acc'];
    const out = [];
    keys.forEach((k) => {
      if (jsonLine(a[k]) !== jsonLine(b[k])) { out.push(['m', k + ': ' + jsonLine(a[k])]); out.push(['p', k + ': ' + jsonLine(b[k])]); }
    });
    return out;
  }

  async function childrenTab(d, id, kids) {
    const cfg = cfgOf(d);
    const hyp = card('dash', h('div', { style: 'display:flex;align-items:center;gap:10px;padding-bottom:6px' }, lbl('Giả thuyết'), wait('Backlog')),
      h('p', { class: 'wb-sub' }, 'Bảng giả thuyết, run đối chứng và trạng thái (xác nhận, bác bỏ) chưa dựng. Hôm nay ghi trong báo cáo PP-PR ở ', mono('research/register.md'), '. Nguyên nhân chỉ được ghi khi có run đối chứng ủng hộ; timeline ở tab Điều tra chỉ gợi ý chỗ cần nhìn.'));
    if (!cfg || !cfg.scenario) return h('div', { style: 'display:flex;flex-direction:column;gap:18px' }, card('', lbl('Tạo run con'), h('p', { class: 'wb-sub' }, 'Run này không có cấu hình web (request.json không có config), nên chưa tạo run con từ giao diện được.')), hyp);

    const catalog = await WB.catalog().catch(() => null);
    const st = { kind: null, fault: 0, trigger: cfg.trigger || '', level: 'a', seed: cfg.seed };
    const faults = cfg.faults || [];
    const levelsOf = (fid) => { const f = catalog && catalog.faults.find((x) => x.id === fid); return f ? f.levels.map((l) => l.id) : []; };
    if (faults[0]) st.level = faults[0][1];

    function build() {
      const c = JSON.parse(JSON.stringify(cfg));
      c.rate = 0;
      if (st.kind === 'nofault') {
        c.faults = faults.filter((_, i) => i !== Number(st.fault));
        if (!c.faults.length) c.trigger = null;   // Trigger chỉ có hiệu lực khi cấu hình còn lỗi để kích hoạt.
      }
      if (st.kind === 'trigger') c.trigger = st.trigger || null;
      if (st.kind === 'level') c.faults = faults.map((f, i) => (i === Number(st.fault) ? [f[0], st.level] : f));
      if (st.kind === 'seed') c.seed = Number(st.seed);
      return c;
    }
    const diffBox = h('div', { class: 'wb-diff', role: 'status', 'aria-live': 'polite' });
    const msg = h('p', { class: 'wb-small', role: 'alert' });
    const create = h('button', { type: 'button', class: 'wb-btn primary', disabled: true }, 'Tạo run con');
    const parent = h('div', { class: 'wb-small' }, 'parent_run_id ', mono(id));

    function sync() {
      const c = build();
      const lines = st.kind ? diffLines(cfg, c) : [];
      diffBox.textContent = '';
      if (!lines.length) diffBox.appendChild(h('span', { class: 'k' }, st.kind ? 'Chưa đổi gì so với run cha.' : 'Chọn một thay đổi.'));
      lines.forEach(([k, t]) => diffBox.appendChild(h('span', { class: k }, (k === 'm' ? '− ' : '+ ') + t)));
      if (lines.length) diffBox.appendChild(h('span', { class: 'k' }, 'các khóa còn lại: giữ nguyên'));
      create.disabled = !lines.length;
    }
    const sel = (opts, val, on, label) => h('select', { class: 'wb-select', 'aria-label': label, onchange: (e) => on(e.target.value) }, ...opts.map(([v, t]) => h('option', { value: v, selected: String(v) === String(val) }, t)));
    const radio = (k, title, sub, control, off) => h('label', { class: 'wb-opt' + (off ? ' off' : '') },
      h('input', { type: 'radio', name: 'chg', value: k, disabled: !!off, onchange: () => { st.kind = k; sync(); } }),
      h('span', { style: 'flex:1;min-width:0' }, title, h('small', null, sub), control ? h('div', { class: 'sel' }, control) : null));
    const hasF = faults.length > 0;
    const form = card('', h('div', { style: 'display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding-bottom:10px' }, lbl('Tạo run con: đổi đúng một thứ')),
      h('div', { role: 'radiogroup', 'aria-label': 'Thay đổi cho run con', style: 'display:flex;flex-direction:column;gap:8px' },
        radio('nofault', 'Bỏ lỗi', 'Kiểm: lỗi này có phải nguyên nhân không', hasF ? sel(faults.map((f, i) => [i, f[0] + ' ' + f[1]]), st.fault, (v) => { st.fault = v; sync(); }, 'Lỗi cần bỏ') : null, !hasF),
        radio('trigger', 'Đổi thời điểm lỗi', 'Trước, trong, hoặc sau khi LKA, ELK can thiệp', hasF ? sel(Object.entries(TRIG), st.trigger, (v) => { st.trigger = v; sync(); }, 'Thời điểm lỗi') : null, !hasF),
        radio('level', 'Đổi mức lỗi', 'Danh định, sát ngưỡng, vượt ngưỡng', hasF && catalog ? h('span', { style: 'display:flex;gap:8px;flex-wrap:wrap' }, sel(faults.map((f, i) => [i, f[0]]), st.fault, (v) => { st.fault = v; sync(); }, 'Lỗi cần đổi mức'), sel(levelsOf(faults[0][0]).map((l) => [l, 'mức ' + l]), st.level, (v) => { st.level = v; sync(); }, 'Mức lỗi')) : null, !hasF || !catalog),
        radio('seed', 'Đổi seed', 'Kiểm hành vi có phụ thuộc nhiễu không', h('input', { class: 'wb-input', type: 'number', min: '1', max: '999', value: String(cfg.seed), style: 'max-width:110px', 'aria-label': 'Seed', oninput: (e) => { st.seed = e.target.value; sync(); } })),
        radio('lib', 'Đổi thư viện planner', 'Chọn thư viện đã build, kiểm hash trước khi chạy. Chưa có API chọn thư viện.', null, true)),
      lbl('Diff cấu hình so với run cha', { style: 'padding:14px 0 6px' }), parent, diffBox,
      h('div', { style: 'display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding-top:12px' }, create, msg),
      h('p', { class: 'wb-small', style: 'padding-top:10px' }, 'Mỗi run con một thay đổi, để kết quả quy được về đúng thay đổi đó. Run con chạy ở tốc độ tối đa; kết quả không phụ thuộc tốc độ phát.'));
    create.addEventListener('click', async () => {
      create.disabled = true; msg.textContent = '';
      try {
        const r = await WB.api('runs', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Idempotency-Key': (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random()) }, body: JSON.stringify({ config: build(), parent_run_id: id }) });
        WB.go('#/runs/' + r.run_id);
      } catch (e) { msg.textContent = 'Không tạo được run con: ' + e.message; msg.className = 'wb-small bad'; create.disabled = false; }
    });
    sync();

    const cmpBox = h('div', null);
    const kidsCard = card('', lbl('Run con'));
    if (!kids.length) kidsCard.appendChild(h('p', { class: 'wb-small' }, 'Chưa có run con. Tạo ở khung bên trên.'));
    else {
      kidsCard.appendChild(h('div', { style: 'display:flex;flex-wrap:wrap;gap:8px' }, ...kids.map((k) => h('button', { type: 'button', class: 'wb-chip', onclick: () => compare(k) }, mono(k.run_id.slice(-13)), ' ', stInfo(k).text, k.verdict ? (k.verdict === 'pass' ? ' · Đạt' : ' · Trượt') : ''))));
      kidsCard.appendChild(cmpBox);
    }
    async function compare(k) {
      cmpBox.textContent = '';
      cmpBox.appendChild(h('p', { class: 'wb-small', style: 'padding-top:10px' }, 'Đang đọc…'));
      try {
        const c = await WB.api('runs/' + k.run_id);
        cmpBox.textContent = '';
        cmpBox.appendChild(compareTable(d, c, k.run_id, id));
      } catch (e) { cmpBox.textContent = 'Không đọc được run con: ' + e.message; }
    }
    return h('div', { style: 'display:flex;flex-direction:column;gap:18px' }, form, kidsCard, hyp);
  }

  function compareTable(p, c, cid, pid) {
    const pe = p.evaluation, ce = c.evaluation;
    const pc = cfgOf(p) || {}, cc = cfgOf(c) || {};
    const dl = diffLines(pc, cc);
    const bp = (p.manifest || {}).bundle || {}, bc = (c.manifest || {}).bundle || {};
    const row = (k, a, b) => h('tr', null, h('td', { class: 'dim' }, k), h('td', null, a), h('td', null, b));
    const crit = (ev, id) => (ev ? ev.criteria.find((x) => x.id === id) : null);
    const cell = (x) => (!x ? mono('—') : h('span', null,
      x.applicable ? mono(WB.num(x.value) + ' · ' + WB.limit(x.limit)) : h('span', { class: 'dim' }, 'không áp dụng'),
      x.applicable ? h('span', { class: x.passed ? 'good' : 'bad', style: 'font-weight:600' }, ' ' + (x.passed ? 'đạt' : 'trượt')) : null));
    const libOf = (r) => libLine((r.manifest || {}).libraries);
    const lp = libOf(p), lc = libOf(c), sameLib = lp && lc && lp === lc;
    const short = (v) => (v ? (v.match(/commit (\w{7})/) || [0, v])[1] : '—');
    const ids = new Set();
    [pe, ce].forEach((ev) => ev && ev.criteria.forEach((x) => { const o = crit(pe, x.id), q = crit(ce, x.id); if ((o && o.applicable && !o.passed) || (q && q.applicable && !q.passed) || (o && q && (o.value !== q.value || o.applicable !== q.applicable))) ids.add(x.id); }));
    const rows = [...ids].sort();
    return h('div', { style: 'padding-top:12px;display:flex;flex-direction:column;gap:10px' },
      h('div', { class: 'wb-lbl' }, 'So run cha và run con'),
      sameLib ? null : h('div', { class: 'wb-note', role: 'alert' }, ico('i-warn'), h('span', null, 'Hai run dùng thư viện planner khác nhau, nên kết quả không quy được về đúng thay đổi cấu hình. Run con luôn chạy bằng thư viện đang nạp ở workbench. Muốn đối chứng sạch thì chạy lại run cha bằng thư viện hiện tại, rồi so run con với bản chạy lại đó.')),
      h('div', { style: 'overflow-x:auto' }, h('table', { class: 'wb-cmp' },
        h('thead', null, h('tr', null, h('th', null, ''), h('th', null, 'Run cha'), h('th', null, 'Run con'))),
        h('tbody', null,
          row('run_id', mono('…' + pid.slice(-13)), h('a', { class: 'wb-mono', href: '#/runs/' + cid }, '…' + cid.slice(-13))),
          row('Thay đổi', mono('—'), dl.length ? h('div', { class: 'wb-diff' }, ...dl.map(([k, t]) => h('span', { class: k }, (k === 'm' ? '− ' : '+ ') + t))) : mono('không thấy khác ở cấu hình')),
          row('Thư viện planner', h('span', { class: sameLib ? '' : 'bad', style: 'font-weight:600' }, mono(short(lp))), h('span', { class: sameLib ? '' : 'bad', style: 'font-weight:600' }, mono(short(lc)), sameLib ? '' : ' khác run cha')),
          row('case_hash', mono(WB.short(bp.case_hash, 12) + '…'), mono(WB.short(bc.case_hash, 12) + '…')),
          row('behavior_checksum', mono(WB.short(bp.behavior_checksum, 8) + '…'), mono(WB.short(bc.behavior_checksum, 8) + '…')),
          row('Tiêu chí áp dụng', pe ? applicable(pe).length + ' · ' + failing(pe).length + ' trượt' : '—', ce ? applicable(ce).length + ' · ' + failing(ce).length + ' trượt' : '—'),
          ...rows.map((rid) => row(rid, cell(crit(pe, rid)), cell(crit(ce, rid))))))),
      h('p', { class: 'wb-small' }, 'Số đọc từ evaluation.json của hai bundle. Chỉ hiện tiêu chí trượt hoặc có giá trị khác nhau.'));
  }

  WB.views.runs = (rest) => (rest[0] ? runDetail(rest[0], rest[1] || 'tong-quan') : runList());
})();
