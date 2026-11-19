/* Màn So sánh và campaign.
   So sánh: hai lần chạy suite, hoặc hai campaign, ghép theo ca và seed; môi trường của hai bên hiện trước kết quả.
   Campaign: một danh sách run đóng băng, chạy cùng nhau qua supervisor, tiến độ và độ phủ, hủy, lặp lại.
   Giao diện không tự tính kết luận: mọi số lấy từ /api/compare và /api/campaigns. */
(() => {
  'use strict';
  const WB = window.WB;
  const { h, ico, mono, tag, lbl, kv, card, page } = WB;

  const head = (title, sub, extra) => h('header', { class: 'wb-head' }, h('div', null, h('h1', null, title), h('p', { class: 'wb-sub' }, sub)), extra || null);
  const post = (body) => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
  const TABS = [['so-sanh', 'So sánh hai lần chạy'], ['campaign', 'Campaign']];
  const tabs = (cur) => h('nav', { class: 'wb-tabs', 'aria-label': 'Phần của màn hình' },
    ...TABS.map(([k, t]) => h('a', { href: '#/review/' + k, 'aria-current': k === cur ? 'page' : null }, t)));
  const err = (e) => h('div', { class: 'wb-err', role: 'alert' }, e.message || String(e));
  const pill = (cls, ...kids) => h('span', { class: 'wb-pill ' + cls }, ...kids);

  const STATE = {
    NOT_STARTED: ['Chưa gửi', 'dim'], QUEUED: ['Đang chờ', 'good'], RUNNING: ['Đang chạy', 'good'], PAUSED: ['Tạm dừng', 'good'],
    COMPLETED: ['Hoàn tất', ''], FAILED: ['Lỗi thực thi', 'bad'], TIMED_OUT: ['Quá hạn', 'bad'], CANCELLED: ['Đã hủy', 'dim'],
    MISSING: ['Không còn run', 'dim'],
  };
  const stateCell = (s) => { const [t, c] = STATE[s.state] || [s.state, '']; return h('span', { class: c }, t + (s.failure ? ' · ' + s.failure : '')); };
  const verdictCell = (s) => {
    if (s.verdict === 'pass') return h('span', { class: 'wb-ico good' }, ico('i-check'), 'Đạt');
    if (s.verdict === 'fail') return h('span', { class: 'wb-ico bad' }, ico('i-x'), 'Trượt' + (s.first_fail ? ' · ' + s.first_fail : ''));
    if (s.verdict === 'not_judged') return h('span', { class: 'dim' }, 'Không được chấm');
    return h('span', { class: 'dim' }, '—');
  };

  // ============================== So sánh ==============================

  const KIND = { suite: 'Lần chạy suite', campaign: 'Campaign' };
  const KIND_NOTE = {
    suite: 'Ghép theo ca và seed. Kết quả chấm theo phạm vi của từng ca (Software Qualification Test Specification 8.1).',
    campaign: 'Ghép theo cấu hình của run (bỏ nhịp phát). Chấm theo mọi tiêu chí áp dụng của run, không theo phạm vi của ca.',
  };

  async function compareView(rest) {
    const kind = rest[0] === 'campaign' ? 'campaign' : 'suite';
    const baseId = rest[1] || '';
    const candId = rest[2] || '';
    const [suites, camps] = await Promise.all([WB.api('suites'), WB.api('campaigns')]);
    const options = kind === 'suite'
      ? suites.suites.map((s) => ({ id: s.id, text: s.id + (s.planner.commit ? ' · ' + s.planner.commit : '') + (s.verdict ? ' · ' + s.verdict : '') }))
      : camps.campaigns.map((c) => ({ id: c.id, text: c.name + ' · ' + c.id.slice(0, 15) + ' · ' + c.counts.completed + '/' + c.coverage.designed }));
    const sel = (label, value) => h('label', { class: 'wb-field' }, label,
      h('select', { class: 'wb-select', style: 'min-width:320px;font-family:var(--font-mono);font-size:13px', 'aria-label': label },
        h('option', { value: '' }, 'Chọn…'), ...options.map((o) => h('option', { value: o.id, selected: o.id === value }, o.text))));
    const base = sel('Baseline', baseId);
    const cand = sel('Candidate', candId);
    const kindSel = h('label', { class: 'wb-field' }, 'Loại', h('select', { class: 'wb-select', 'aria-label': 'Loại', onchange: (e) => WB.go('#/review/so-sanh/' + e.target.value) },
      ...Object.keys(KIND).map((k) => h('option', { value: k, selected: k === kind }, KIND[k]))));
    const go = h('button', { type: 'button', class: 'wb-btn primary', onclick: () => {
      const b = base.querySelector('select').value;
      const c = cand.querySelector('select').value;
      if (b && c) WB.go('#/review/so-sanh/' + kind + '/' + b + '/' + c);
    } }, 'So sánh');
    const form = card('', lbl('Chọn hai bên'), h('div', { class: 'wb-btns', style: 'align-items:flex-end' }, kindSel, base, cand, go),
      h('p', { class: 'wb-small' }, KIND_NOTE[kind]));

    let result;
    if (baseId && candId) {
      try {
        result = renderCompare(await WB.api('compare?base=' + kind + ':' + encodeURIComponent(baseId) + '&cand=' + kind + ':' + encodeURIComponent(candId)), kind, candId);
      } catch (e) { result = err(e); }
    } else if (!options.length) {
      result = h('p', { class: 'wb-small' }, kind === 'suite' ? 'Chưa có lần chạy suite nào trong build/benchmark.' : 'Chưa có campaign nào. Tạo ở tab Campaign.');
    } else {
      result = h('p', { class: 'wb-small' }, 'Chọn baseline (bản cũ) và candidate (bản mới) rồi bấm So sánh.');
    }
    return page(head('So sánh và campaign', 'Đánh giá một thay đổi: bản mới tốt hơn hay kém hơn ở ca nào, seed nào, và hai bên có cùng môi trường không.'), tabs('so-sanh'), form, result);
  }

  const sideCard = (title, s) => card('', lbl(title),
    h('div', { style: 'display:flex;flex-direction:column;gap:4px' },
      h('span', { class: 'wb-mono', style: 'font-size:12.5px;overflow-wrap:anywhere' }, s.id),
      s.target ? h('span', { class: 'wb-small' }, s.target + (s.finished ? ' · ' + s.finished.replace('T', ' ').slice(0, 16) : '')) : null,
      kv('Kết luận', h('b', { class: s.verdict === 'Đạt' ? 'good' : 'bad' }, s.verdict || '—')),
      kv('Lượt chạy', String(s.runs_total) + (s.planned != null && s.planned !== s.runs_total ? ' trên ' + s.planned + ' dự kiến' : '')),
      s.counts && s.counts.BLOCKER != null ? kv('Trượt BLOCKER · MAJOR · MINOR', [s.counts.BLOCKER, s.counts.MAJOR, s.counts.MINOR].join(' · ')) : null,
      s.counts && s.counts.failed_runs != null ? kv('Run có tiêu chí trượt', String(s.counts.failed_runs)) : null,
      kv('Commit', s.commit ? mono(s.commit + (s.dirty ? ' (cây chưa commit)' : '')) : '—'),
      h('span', { class: 'wb-small', style: 'overflow-wrap:anywhere' }, (s.libraries || []).map((l) => l.pp_version).filter(Boolean).join(' | ') || 'không ghi thư viện')));

  const deltaCell = (d) => {
    if (d == null) return h('span', { class: 'dim' }, '—');
    const worse = d < -1e-12;
    const better = d > 1e-12;
    return h('span', { class: 'wb-mono', style: 'font-size:12px;color:' + (worse ? 'var(--wb-crit-ink)' : better ? 'var(--wb-ok-ink)' : 'var(--ink-2)') },
      (d > 0 ? '+' : '') + WB.num(d) + (worse ? ' xấu hơn' : better ? ' tốt hơn' : ''));
  };
  const KINDS = { new: ['Mới trượt', 'bad'], fixed: ['Hết trượt', 'good'], still: ['Còn trượt', ''] };

  function renderCompare(r, kind, candId) {
    const c = r.counts;
    const out = [];
    out.push(h('div', { class: 'wb-cols' }, h('div', { class: 'a', style: 'flex:1 1 320px' }, sideCard('Baseline', r.base)), h('div', { class: 'b', style: 'flex:1 1 320px' }, sideCard('Candidate', r.cand))));

    const warn = r.differences.filter((d) => d.level === 'warn');
    out.push(card(warn.length ? 'warn' : '', lbl('Môi trường của hai bên'),
      r.differences.length
        ? h('section', { class: 'wb-table', 'aria-label': 'Điểm khác nhau' }, h('div', { style: 'min-width:640px' },
          h('div', { class: 'wb-row envs h' }, ...['Điểm khác', 'Baseline', 'Candidate', ''].map((t) => h('span', null, t))),
          ...r.differences.map((d) => h('div', { class: 'wb-row envs' }, h('span', { style: 'font-size:12.5px' }, d.label),
            h('span', { class: 'wb-mono', style: 'font-size:12px;overflow-wrap:anywhere' }, fmt(d.base)), h('span', { class: 'wb-mono', style: 'font-size:12px;overflow-wrap:anywhere' }, fmt(d.cand)),
            d.level === 'warn' ? h('span', { class: 'wb-ico bad', style: 'font-size:12px' }, ico('i-warn'), 'cần chú ý') : h('span', { class: 'dim', style: 'font-size:12px' }, 'dự kiến')))))
        : h('p', { class: 'wb-sub' }, 'Hai bên cùng thư viện, calibration, commit, bộ đầu vào và môi trường chạy.'),
      warn.length ? h('p', { class: 'wb-small' }, 'Có điểm khác về môi trường chạy: kết quả hai bên có thể khác vì lý do này, không chỉ vì thay đổi cần đánh giá.') : null));

    if (r.warnings.length) out.push(card('warn', lbl('Cần đọc trước khi tin kết quả'), h('ul', { class: 'howto' }, ...r.warnings.map((w) => h('li', null, w)))));

    out.push(h('section', { class: 'wb-verdict' + (c.new ? '' : ' pass'), 'aria-label': 'Tóm tắt so sánh' },
      h('div', { class: 'wb-stat' }, h('b', null, String(c.matched)), h('span', null, 'lượt ghép được')),
      h('div', { class: 'wb-stat' }, h('b', { class: c.new ? 'bad' : '' }, String(c.new)), h('span', null, 'mới trượt')),
      h('div', { class: 'wb-stat' }, h('b', { class: c.fixed ? 'good' : '' }, String(c.fixed)), h('span', null, 'hết trượt')),
      h('div', { class: 'wb-stat' }, h('b', null, String(c.still)), h('span', null, 'còn trượt')),
      h('div', { class: 'wb-stat' }, h('b', null, String(c.behavior_changed)), h('span', null, 'lượt đổi hành vi')),
      h('div', { class: 'wb-stat' }, h('b', null, String(c.only_base + c.only_cand + c.case_changed)), h('span', null, 'lượt không so được')),
      h('div', { style: 'flex:1 1 100%;font-size:12.5px;color:var(--ink-2)' }, 'Một lượt "đổi hành vi" khi behavior_checksum khác; cùng checksum nghĩa là xe chạy giống nhau từng bit.')));

    if (r.by_requirement.length) {
      out.push(card('', lbl('Theo requirement'), h('section', { class: 'wb-table' }, h('div', { style: 'min-width:520px' },
        h('div', { class: 'wb-row reqs h' }, ...['Requirement', 'Mới trượt', 'Hết trượt', 'Còn trượt'].map((t) => h('span', null, t))),
        ...r.by_requirement.map((q) => h('div', { class: 'wb-row reqs' }, mono(q.id, { style: 'font-size:12.5px' }),
          h('span', { class: q.new ? 'bad' : 'dim' }, String(q.new)), h('span', { class: q.fixed ? 'good' : 'dim' }, String(q.fixed)), h('span', null, String(q.still))))))));
    }
    if (r.by_family.length && kind === 'suite') {
      out.push(card('', lbl('Theo họ ca (' + r.by_family.length + ' họ đổi nhiều nhất)'), h('div', { class: 'wb-pills' },
        ...r.by_family.map((f) => pill(f.new ? 'fail' : f.fixed ? 'pass' : '', mono(f.id), f.new ? '+' + f.new : '', f.fixed ? '−' + f.fixed : '', f.still ? '=' + f.still : '')))));
    }

    const reopen = (row) => async (e) => {
      const b = e.currentTarget;
      const [cs, seed] = row.key.split('|');
      b.disabled = true; b.textContent = 'Đang mở…';
      try { WB.go('#/runs/' + (await WB.api('suites/' + candId + '/reopen', post({ case: cs, seed: Number(seed) }))).run_id); }
      catch (x) { b.textContent = 'Không mở được'; b.title = x.message; }
    };
    if (r.changes.length) {
      out.push(h('section', { class: 'wb-table', 'aria-label': 'Requirement đổi kết quả' }, h('div', { style: 'min-width:1020px' },
        h('div', { style: 'display:flex;align-items:baseline;gap:12px;padding:14px 16px 10px' }, lbl('Requirement đổi kết quả hoặc còn trượt'),
          h('span', { class: 'wb-small' }, r.changes.length + (r.truncated ? ' trên ' + (r.changes.length + r.truncated) : '') + ' dòng; mới trượt xếp trước, xấu nhất lên đầu')),
        h('div', { class: 'wb-row cmp h' }, ...['', 'Requirement', 'Lượt chạy', 'Baseline', 'Candidate', 'Ngưỡng', 'Biên tới ngưỡng', ''].map((t) => h('span', null, t))),
        ...r.changes.map((x) => h('div', { class: 'wb-row cmp' },
          h('span', { class: (KINDS[x.kind][1] === 'bad' ? 'bad' : KINDS[x.kind][1] === 'good' ? 'good' : 'dim'), style: 'font-size:12px;font-weight:600' }, KINDS[x.kind][0]),
          mono(x.requirement, { style: 'font-size:12px' }),
          h('span', { class: 'wb-mono', style: 'font-size:12px;overflow-wrap:anywhere' }, x.run),
          mono(x.base_value == null ? '—' : WB.num(x.base_value), { style: 'font-size:12px' }), mono(x.cand_value == null ? '—' : WB.num(x.cand_value), { style: 'font-size:12px' }),
          mono(x.limit ? WB.limit(x.limit) : '—', { style: 'font-size:12px' }), deltaCell(x.delta_margin),
          kind === 'suite' ? h('button', { type: 'button', class: 'wb-btn', style: 'height:30px;padding:0 10px;font-size:12px', onclick: reopen(x) }, 'Mở lại ở candidate') : h('span')))),
        r.truncated ? h('p', { class: 'wb-small', style: 'padding:10px 16px' }, 'Còn ' + r.truncated + ' dòng nữa; số đếm ở trên đã gồm đủ.') : null));
    } else if (c.matched) {
      out.push(card('', lbl('Requirement đổi kết quả'), h('p', { class: 'wb-sub' }, 'Không có requirement nào đổi kết quả hoặc còn trượt ở các lượt ghép được.')));
    }
    return h('div', { class: 'wb-col', style: 'padding:0' }, ...out);
  }

  const fmt = (v) => (v == null ? '—' : Array.isArray(v) ? (v.length ? v.map(fmt).join(' | ') : '—') : typeof v === 'boolean' ? (v ? 'có' : 'không') : String(v));

  // ============================== Campaign ==============================

  const when = (epoch) => WB.time(epoch);
  const cell = (n, total, cls) => h('span', { class: cls || '' }, n + (total != null ? '/' + total : ''));

  async function campaignHome() {
    WB.title('Campaign');
    const [data, cat] = await Promise.all([WB.api('campaigns'), WB.catalog()]);
    const list = data.campaigns.length
      ? h('section', { class: 'wb-table', 'aria-label': 'Campaign' }, h('div', { style: 'min-width:820px' },
        h('div', { class: 'wb-row camps h' }, ...['Tên', 'Tạo lúc', 'Trạng thái', 'Tiến độ', 'Kết luận'].map((t) => h('span', null, t))),
        ...data.campaigns.map((c) => h('a', { class: 'wb-row camps', href: '#/review/campaign/' + c.id },
          h('span', null, c.name, h('span', { class: 'wb-mono', style: 'display:block;font-size:11px;color:var(--ink-3)' }, c.id)),
          h('span', { class: 'wb-mono', style: 'font-size:12px' }, when(c.created)),
          h('span', { class: c.state === 'running' ? 'good' : '' }, c.state === 'running' ? 'Đang chạy' : 'Xong'),
          h('span', { class: 'wb-mono', style: 'font-size:12px' }, c.counts.completed + ' xong · ' + c.counts.running + ' chạy · ' + c.counts.queued + ' chờ' + (c.counts.failed ? ' · ' + c.counts.failed + ' lỗi' : '') + (c.counts.cancelled ? ' · ' + c.counts.cancelled + ' hủy' : '') + ' / ' + c.coverage.designed),
          h('span', { class: 'wb-mono', style: 'font-size:12px' }, c.counts.pass + ' đạt · ' + c.counts.fail + ' trượt')))))
      : h('p', { class: 'wb-sub' }, 'Chưa có campaign nào. Tạo một campaign ở bên dưới.');
    return page(head('So sánh và campaign', 'Campaign là một danh sách run đóng băng, chạy cùng nhau và theo dõi cùng nhau.'), tabs('campaign'),
      card('', lbl('Campaign đã tạo'), list), createForm(cat, data.max_runs));
  }

  function createForm(cat, maxRuns) {
    const st = { name: '', filter: '', scen: new Set(), faults: [], clean: true, veh: new Set(['VP-0']), seeds: '1' };
    const box = h('div', { style: 'display:flex;flex-direction:column;gap:14px' });
    const faultsById = Object.fromEntries((cat.faults || []).map((f) => [f.id, f]));
    const seedsOf = () => st.seeds.split(/[\s,]+/).filter(Boolean).map(Number);
    const seedsOk = () => seedsOf().length > 0 && seedsOf().every((n) => Number.isInteger(n) && n >= 0 && n <= 9999);
    const sets = () => (st.clean ? 1 : 0) + st.faults.length || 1;
    const size = () => st.scen.size * sets() * st.veh.size * (seedsOk() ? seedsOf().length : 0);
    let msg = null;

    function paint() {
      box.textContent = '';
      const n = size();
      const f = st.filter.trim().toLowerCase();
      const visible = (cat.scenarios || []).filter((s) => !f || (s.id + ' ' + s.desc + ' ' + s.fn).toLowerCase().includes(f)).slice(0, 80);
      const fSel = h('select', { class: 'wb-select', 'aria-label': 'Lỗi' }, ...(cat.faults || []).map((x) => h('option', { value: x.id }, x.id + ' · ' + x.title)));
      const lvSel = h('select', { class: 'wb-select', 'aria-label': 'Mức lỗi' });
      const fillLevels = () => { lvSel.textContent = ''; ((faultsById[fSel.value] || {}).levels || []).forEach((l) => lvSel.appendChild(h('option', { value: l.id }, l.id + ' · ' + l.desc))); };
      fSel.addEventListener('change', fillLevels); fillLevels();

      box.appendChild(h('label', { class: 'wb-field' }, 'Tên campaign', h('input', { class: 'wb-input', type: 'text', maxlength: '80', value: st.name, 'aria-label': 'Tên campaign', oninput: (e) => { st.name = e.target.value; refreshGo(); } })));
      box.appendChild(h('div', null, lbl('Tình huống (' + st.scen.size + ' đã chọn)'),
        h('input', { class: 'wb-input', type: 'search', placeholder: 'Lọc theo mã hoặc mô tả, ví dụ S4 hoặc ELK', value: st.filter, 'aria-label': 'Lọc tình huống', oninput: (e) => { st.filter = e.target.value; paint(); const i = box.querySelector('input[type=search]'); i.focus(); i.setSelectionRange(st.filter.length, st.filter.length); } }),
        h('div', { class: 'wb-pickbox', role: 'group', 'aria-label': 'Tình huống' }, ...visible.map((s) => h('label', { class: 'wb-pick' },
          h('input', { type: 'checkbox', checked: st.scen.has(s.id), onchange: (e) => { if (e.target.checked) st.scen.add(s.id); else st.scen.delete(s.id); refreshCount(); } }),
          h('span', { class: 'wb-mono', style: 'font-size:12px' }, s.code), h('span', { class: 'wb-small' }, s.desc))),
          visible.length === 80 ? h('p', { class: 'wb-small' }, 'Chỉ hiện 80 tình huống đầu; lọc để thu hẹp.') : null)));
      box.appendChild(h('div', null, lbl('Lỗi (mỗi lỗi một nhóm run riêng)'),
        h('label', { class: 'wb-pick' }, h('input', { type: 'checkbox', checked: st.clean, onchange: (e) => { st.clean = e.target.checked; refreshCount(); } }), h('span', null, 'Kèm bản không lỗi')),
        h('div', { class: 'wb-btns', style: 'align-items:flex-end;padding-top:6px' }, h('label', { class: 'wb-field' }, 'Lỗi', fSel), h('label', { class: 'wb-field' }, 'Mức', lvSel),
          h('button', { type: 'button', class: 'wb-btn', onclick: () => { const pair = [fSel.value, lvSel.value]; if (pair[1] && !st.faults.some((p) => p[0] === pair[0] && p[1] === pair[1])) { st.faults.push(pair); paint(); } } }, 'Thêm lỗi')),
        st.faults.length ? h('div', { class: 'wb-pills', style: 'padding-top:8px' }, ...st.faults.map((p, i) => h('span', { class: 'wb-pill' }, mono(p[0] + ' ' + p[1]),
          h('button', { type: 'button', class: 'wb-btn', style: 'height:22px;padding:0 6px;font-size:11px', 'aria-label': 'Bỏ lỗi ' + p[0] + ' ' + p[1], onclick: () => { st.faults.splice(i, 1); paint(); } }, 'bỏ')))) : null));
      box.appendChild(h('div', { class: 'wb-btns', style: 'align-items:flex-start;gap:24px' },
        h('div', null, lbl('Mẫu xe'), h('div', { class: 'wb-pills' }, ...(cat.vehicles || []).map((v) => h('label', { class: 'wb-pick' },
          h('input', { type: 'checkbox', checked: st.veh.has(v.id), onchange: (e) => { if (e.target.checked) st.veh.add(v.id); else st.veh.delete(v.id); refreshCount(); } }), h('span', { class: 'wb-mono', style: 'font-size:12px' }, v.id))))),
        h('label', { class: 'wb-field' }, 'Seed (cách nhau bằng dấu phẩy)', h('input', { class: 'wb-input', type: 'text', value: st.seeds, 'aria-label': 'Seed', style: 'width:160px', oninput: (e) => { st.seeds = e.target.value; refreshCount(); } }))));
      const count = h('p', { class: 'wb-small', id: 'camp-count', role: 'status', 'aria-live': 'polite' });
      const go = h('button', { type: 'button', class: 'wb-btn primary', id: 'camp-go', onclick: submit }, 'Tạo và chạy campaign');
      box.appendChild(h('div', { class: 'wb-btns', style: 'align-items:center' }, go, count));
      if (msg) box.appendChild(msg);
      refreshCount();

      function refreshCount() {
        const m = size();
        count.textContent = st.scen.size + ' tình huống × ' + sets() + ' nhóm lỗi × ' + st.veh.size + ' xe × ' + (seedsOk() ? seedsOf().length : 0) + ' seed = ' + m + ' run (tối đa ' + maxRuns + ')';
        refreshGo();
      }
      function refreshGo() {
        const m = size();
        go.disabled = !(st.name.trim() && m > 0 && m <= maxRuns);
      }
      async function submit() {
        go.disabled = true; go.textContent = 'Đang tạo…';
        try {
          const res = await WB.api('campaigns', post({ name: st.name.trim(), matrix: {
            scenarios: [...st.scen].map((id) => ({ sid: id.split('/')[0], v: id.split('/')[1] })),
            fault_sets: [...(st.clean ? [[]] : []), ...st.faults.map((p) => [p])], vehicles: [...st.veh], seeds: seedsOf() } }));
          WB.go('#/review/campaign/' + res.id);
        } catch (e) { msg = err(e); go.textContent = 'Tạo và chạy campaign'; paint(); }
      }
    }
    paint();
    return card('', lbl('Tạo campaign mới'),
      h('p', { class: 'wb-sub' }, 'Chọn tình huống, lỗi, xe và seed. Danh sách run được đóng băng khi tạo; các run chạy qua cùng một supervisor, tối đa vài run cùng lúc, còn lại chờ.'), box);
  }

  async function campaignDetail(id) {
    WB.title('Campaign');
    let c;
    try { c = await WB.api('campaigns/' + id); } catch (e) { return page(head('Campaign', ''), tabs('campaign'), err(e)); }
    if (c.state === 'running') {
      const t = setInterval(() => { if (!document.hidden) WB.refresh(); }, 2000);
      WB.onLeave(() => clearInterval(t));
    }
    const n = c.counts;
    const cov = c.coverage;
    const act = (label, fn, cls) => h('button', { type: 'button', class: 'wb-btn' + (cls ? ' ' + cls : ''), onclick: async (e) => {
      const b = e.currentTarget; b.disabled = true;
      try { await fn(); } catch (x) { b.title = x.message; b.textContent = 'Không làm được: ' + x.message; return; }
    } }, label);
    const buttons = h('div', { class: 'wb-btns' },
      c.state === 'running' ? act('Hủy campaign', async () => { await WB.api('campaigns/' + id + '/cancel', post()); WB.refresh(); }) : null,
      act('Lặp lại trên bản hiện tại', async () => { WB.go('#/review/campaign/' + (await WB.api('campaigns/' + id + '/repeat', post())).id); }),
      h('a', { class: 'wb-btn', href: '#/review/so-sanh/campaign/' + (c.parent_campaign || id) + '/' + (c.parent_campaign ? id : '') }, c.parent_campaign ? 'So với campaign gốc' : 'So với campaign khác'),
      c.state === 'done' ? act('Xóa campaign', async () => { if (confirm('Xóa campaign và bỏ ghim các run của nó? Retention có thể xóa các run này sau đó.')) { await WB.api('campaigns/' + id + '/delete', post()); WB.go('#/review/campaign'); } }) : null);
    const bar = (label, v, of, note) => h('div', { class: 'wb-bar' }, h('span', { style: 'font-size:12.5px' }, label), h('span', { class: 'dim', style: 'font-size:11.5px' }, note || ''),
      h('i', null, h('b', { style: 'width:' + (of ? Math.round(v / of * 100) : 0) + '%' })), h('em', { class: 'wb-mono' }, String(v)));
    const covCard = card('', lbl('Độ phủ'), h('div', { class: 'wb-bars cov', style: 'padding-top:6px' },
      bar('Thiết kế', cov.designed, cov.designed), bar('Đã lên lịch', cov.scheduled, cov.designed), bar('Đã chạy xong', cov.ran, cov.designed), bar('Chấm được', cov.judged, cov.designed)),
      h('p', { class: 'wb-small' }, 'Chấm được: run Hoàn tất có ít nhất một tiêu chí áp dụng' + (cov.not_judged ? '; ' + cov.not_judged + ' run không được chấm' : '') + '. Điều kiện xảy ra thật (lỗi thật sự được bơm): chưa đo, vì kết quả của run chưa ghi.'));
    const rows = h('section', { class: 'wb-table', 'aria-label': 'Run của campaign' }, h('div', { style: 'min-width:760px' },
      h('div', { class: 'wb-row items h' }, ...['#', 'Run', 'Trạng thái', 'Kết luận', ''].map((t) => h('span', null, t))),
      ...c.items.map((s) => h('div', { class: 'wb-row items' }, mono(String(s.index + 1), { style: 'font-size:12px' }), h('span', { style: 'font-size:12.5px' }, WB.prettyLabel(s.label)),
        stateCell(s), verdictCell(s), s.run_id && s.state !== 'MISSING' ? h('a', { class: 'wb-btn', style: 'height:30px;padding:0 10px;font-size:12px', href: '#/runs/' + s.run_id }, 'Mở run') : h('span')))));
    return page(head(c.name, h('span', null, 'Campaign ', mono(c.id), ' · tạo lúc ' + when(c.created) + (c.parent_campaign ? ' · lặp lại từ ' + c.parent_campaign : '')), buttons), tabs('campaign'),
      h('section', { class: 'wb-verdict pass', 'aria-label': 'Tiến độ' },
        h('div', { class: 'wb-stat' }, h('b', { class: c.state === 'running' ? 'good' : '' }, c.state === 'running' ? 'Đang chạy' : 'Xong'), h('span', null, 'trạng thái')),
        h('div', { class: 'wb-stat' }, h('b', null, String(n.queued)), h('span', null, 'đang chờ')), h('div', { class: 'wb-stat' }, h('b', null, String(n.running)), h('span', null, 'đang chạy')),
        h('div', { class: 'wb-stat' }, h('b', null, String(n.completed)), h('span', null, 'hoàn tất')), h('div', { class: 'wb-stat' }, h('b', { class: n.failed ? 'bad' : '' }, String(n.failed)), h('span', null, 'lỗi thực thi')),
        h('div', { class: 'wb-stat' }, h('b', null, String(n.cancelled)), h('span', null, 'đã hủy')), h('div', { class: 'wb-stat' }, h('b', { class: n.fail ? 'bad' : '' }, n.pass + ' · ' + n.fail), h('span', null, 'đạt · trượt'))),
      h('div', { class: 'wb-cols' }, h('div', { class: 'a', style: 'flex:1 1 320px' }, covCard), h('div', { class: 'b', style: 'flex:1 1 320px' },
        card('', lbl('Về campaign này'), h('p', { class: 'wb-sub' }, 'Các run đã ghim, nên không bị xóa khi workbench dọn run cũ. Hủy chỉ dừng run của campaign này. Lặp lại tạo campaign mới với đúng danh sách này, để so sánh sau khi đổi planner hoặc calibration.')))),
      rows);
  }

  WB.views.review = async (rest) => {
    WB.title('So sánh và campaign');
    if (rest[0] === 'campaign') return rest[1] ? campaignDetail(rest[1]) : campaignHome();
    return compareView(rest.slice(1));
  };
})();
