/* Giao diện: menu chọn ca (đủ danh mục của benchmark), nhận luồng từng chu kỳ của planner đang chạy thật,
   bảng thông số trực tiếp, điều khiển tạm dừng, tốc độ, dừng, và xem lại sau khi dừng hoặc chạy xong. */
(() => {
  'use strict';
  const PP = window.PP;
  const $ = (id) => document.getElementById(id);

  const h = (tag, attrs, ...kids) => {
    const e = document.createElement(tag);
    for (const k in attrs || {}) {
      if (k === 'class') e.className = attrs[k];
      else if (k === 'text') e.textContent = attrs[k];
      else e.setAttribute(k, attrs[k]);
    }
    kids.flat().forEach((c) => c != null && e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c));
    return e;
  };
  const use = (id, cls) => {
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    const u = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    u.setAttribute('href', '#' + id);
    s.appendChild(u);
    if (cls) s.setAttribute('class', cls);
    return s;
  };
  const norm = (s) => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd');

  // ---------- Trạng thái ----------
  // phase: idle, connecting, running, paused, finishing, done, stopped, error
  const S = {
    phase: 'idle', cat: null, d: null, rate: 1, review: null, ac: null, runId: 0, lastK: -1, dirty: true, err: '',
    run: null, seq: 0, ended: false,   // lượt chạy trên server (run_id), seq của sự kiện cuối đã nhận
    playback: null, playCfg: false,    // run đang phát lại từ bundle: không chạy planner
    fnFilter: '', q: '',
    sel: { scen: 'S1/c', faults: { F01: 'c', F04: 'a' }, trigger: '', env: { mu: true, cam: true, noise: false }, veh: 'VP-0', seed: 1, acc: '' },
  };
  const R = {};   // phần tử cập nhật theo khung
  const TRIG = { lka_active: 'LKA can thiệp', elk_active: 'ELK can thiệp', intervention_active: 'LKA hoặc ELK can thiệp', lcc_follow: 'LCC vào FOLLOW' };
  const curScen = () => (S.playback && !S.playCfg ? null : S.cat.scenarios.find((x) => x.id === S.sel.scen));
  const resText = (res) => (res.passed ? 'Đạt' : res.judged === false ? 'Không được chấm' : 'Không đạt');

  // ---------- Gọi server ----------
  // Lượt chạy thuộc về server, không thuộc về tab: đóng tab không dừng lượt chạy; mở lại thì nối tiếp.
  const post = (url, body) => fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) }).catch(() => null);
  const runApi = (tail) => 'api/runs/' + S.run + tail;
  const control = (body) => (S.run ? post(runApi('/control'), body) : null);
  const ACTIVE = ['QUEUED', 'RUNNING', 'PAUSED'];
  const RUN_KEY = 'pp-sim-run';
  function remember() { try { localStorage.setItem(RUN_KEY, JSON.stringify({ run: S.run, sel: S.sel })); } catch (err) { /* không lưu được */ } }
  function forget() { try { localStorage.removeItem(RUN_KEY); } catch (err) { /* không lưu được */ } }
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function config() {
    const sc = S.cat.scenarios.find((x) => x.id === S.sel.scen);
    const sim = {};
    if (S.sel.env.mu) sim.road_mu = 0.5;
    if (S.sel.env.cam) sim.camera_latency_ms = 150;
    if (S.sel.env.noise) sim.perception_noise_scale = 1.5;
    return {
      scenario: { sid: sc.sid, v: sc.v }, faults: Object.entries(S.sel.faults), trigger: S.sel.trigger || null,
      vehicle: S.sel.veh, seed: S.sel.seed, sim, acc: S.sel.acc || null, rate: S.rate,
    };
  }

  // ---------- Menu ----------
  const scenarioGroups = new Map();
  let openGroup = null;
  let hoverTimer;

  function closeScenarioOptions(restoreFocus = false) {
    clearTimeout(hoverTimer);
    if (!openGroup) return;
    const { trigger, panel } = openGroup;
    openGroup = null;
    trigger.setAttribute('aria-expanded', 'false');
    panel.hidePopover();
    if (restoreFocus) trigger.focus({ preventScroll: true });
  }

  function positionScenarioOptions() {
    const { trigger, panel } = openGroup;
    const rect = trigger.getBoundingClientRect();
    const listRect = $('m-scen').getBoundingClientRect();
    const menuBottom = trigger.closest('.menu').getBoundingClientRect().bottom;
    const { clientWidth, clientHeight } = document.documentElement;
    const top = Math.max(listRect.top, document.querySelector('.runbox').getBoundingClientRect().bottom, 0);
    const bottom = Math.min(listRect.bottom, menuBottom, clientHeight);
    if (rect.bottom <= top || rect.top >= bottom) {
      closeScenarioOptions();
      return;
    }

    const edge = 8;
    const rightSpace = clientWidth - rect.right - edge;
    const beside = rightSpace >= 264;
    const width = Math.min(336, beside ? rightSpace : clientWidth - 2 * edge);
    const above = Math.max(rect.top, top) - edge;
    const below = clientHeight - Math.min(rect.bottom, bottom) - edge;
    const belowRow = below >= 220 || below >= above;
    const height = beside ? clientHeight - 2 * edge : (belowRow ? below : above);
    panel.style.width = width + 'px';
    panel.style.maxHeight = Math.min(360, height) + 'px';
    panel.style.left = (beside ? rect.right : Math.max(edge, Math.min(rect.left, clientWidth - width - edge))) + 'px';
    const y = beside ? Math.min(Math.max(rect.top, top), clientHeight - panel.offsetHeight - edge) :
      (belowRow ? Math.min(rect.bottom, bottom) : Math.max(rect.top, top) - panel.offsetHeight);
    panel.style.top = Math.max(edge, y) + 'px';
  }

  function openScenarioOptions(group) {
    clearTimeout(hoverTimer);
    if (openGroup === group) return;
    closeScenarioOptions();
    openGroup = group;
    group.trigger.setAttribute('aria-expanded', 'true');
    group.panel.showPopover();
    group.panel.scrollTop = 0;
    positionScenarioOptions();
  }

  function buildScenarioMenu(scenarios) {
    const fns = ['Tất cả', ...['LCC', 'LKA', 'ELK', 'LKA+ELK', 'Khác'].filter((f) => scenarios.some((s) => s.fn === f))];
    const chips = $('fn-chips');
    fns.forEach((f) => {
      const b = h('button', { type: 'button', role: 'radio', 'aria-checked': String(f === 'Tất cả'), 'data-f': f === 'Tất cả' ? '' : f, text: f });
      b.addEventListener('click', (e) => { S.fnFilter = b.dataset.f; filterScen(); [...chips.children].forEach((c) => c.setAttribute('aria-checked', String(c === b))); if (e.detail) b.blur(); });
      chips.appendChild(b);
    });

    const bySid = new Map();
    scenarios.forEach((s) => {
      if (!bySid.has(s.sid)) bySid.set(s.sid, []);
      bySid.get(s.sid).push(s);
    });
    const list = $('m-scen');
    const dotCls = { LCC: 'hwa', LKA: 'lka', ELK: 'elk', 'LKA+ELK': 'mix' };
    bySid.forEach((variants, sid) => {
      const base = variants.find((s) => s.v === 'a') || variants[0];
      const id = 'scen-options-' + sid;
      const trigger = h('button', { class: 'srow', type: 'button', 'aria-controls': id, 'aria-expanded': 'false' },
        h('i', { class: 'dot ' + (dotCls[base.fn] || ''), 'aria-hidden': 'true' }),
        h('span', { class: 'code', text: sid }), h('span', { class: 'desc', text: PP.vn(base.desc) }));
      const panel = h('section', { class: 'scen-options', id, popover: 'manual', 'aria-labelledby': id + '-title' },
        h('h3', { id: id + '-title' }, h('b', { text: sid }), h('span', { text: 'Biến thể' })));
      const row = h('div', { class: 'sgroup' }, trigger, panel);
      const options = variants.map((s) => {
        const desc = PP.vn(s.desc);
        const meta = PP.f(s.speed, 0) + ' km/h · ' + PP.f(s.dur, 0) + ' s' + (s.traffic ? ' · ' + s.traffic + ' xe khác' : '');
        const button = h('button', { class: 'soption', type: 'button', 'aria-pressed': 'false' },
          h('span', { class: 'code', text: s.code }),
          h('span', { class: 'desc', text: desc }),
          h('span', { class: 'smeta', text: meta }));
        button.addEventListener('click', () => {
          S.sel.scen = s.id;
          closeScenarioOptions(panel.contains(document.activeElement));
          syncMenu();
        });
        panel.appendChild(button);
        return { scenario: s, button, query: norm([s.code, s.sid + s.v, s.id, desc, s.fn].join(' ')) };
      });
      const group = { row, trigger, panel, options };
      scenarioGroups.set(sid, group);

      // Khoảng chờ ngắn để con trỏ đi từ hàng sang bảng.
      const leave = () => {
        if (openGroup !== group) return;
        clearTimeout(hoverTimer);
        hoverTimer = setTimeout(() => {
          if (openGroup === group && !panel.contains(document.activeElement)) closeScenarioOptions();
        }, 180);
      };
      trigger.addEventListener('pointerenter', (e) => {
        if (e.pointerType === 'touch') return;
        clearTimeout(hoverTimer);
        if (!openGroup) openScenarioOptions(group);
        else if (openGroup !== group) {
          hoverTimer = setTimeout(() => {
            if (!openGroup || openGroup.panel.contains(document.activeElement)) return;
            if (trigger.matches(':hover')) openScenarioOptions(group);
            else if (!openGroup.row.matches(':hover')) closeScenarioOptions();
          }, 220);
        }
      });
      trigger.addEventListener('pointerleave', (e) => { if (e.pointerType !== 'touch') leave(); });
      panel.addEventListener('pointerenter', () => clearTimeout(hoverTimer));
      panel.addEventListener('pointerleave', (e) => { if (e.pointerType !== 'touch') leave(); });
      trigger.addEventListener('click', (e) => {
        openScenarioOptions(group);
        if (!e.detail && openGroup === group) panel.querySelector('.soption:not([hidden])')?.focus();
      });
      row.addEventListener('focusout', (e) => {
        if (openGroup === group && e.relatedTarget && !row.contains(e.relatedTarget)) closeScenarioOptions();
      });
      list.appendChild(row);
    });

    $('q').addEventListener('input', (e) => { S.q = norm(e.target.value.trim()); filterScen(); });
    document.addEventListener('pointerdown', (e) => {
      if (openGroup && !openGroup.row.contains(e.target)) closeScenarioOptions();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape' || !openGroup) return;
      e.preventDefault();
      closeScenarioOptions(openGroup.row.contains(document.activeElement));
    });
    window.addEventListener('resize', () => { if (openGroup) positionScenarioOptions(); });
    window.addEventListener('scroll', (e) => {
      if (openGroup && e.target !== openGroup.panel) positionScenarioOptions();
    }, true);
  }

  function buildMenu(cat) {
    buildScenarioMenu(cat.scenarios);

    // lỗi
    const mf = $('m-faults');
    ['Perception', 'Timing', 'Integrity', 'Khác'].forEach((g) => {
      const fl = cat.faults.filter((f) => f.group === g);
      if (!fl.length) return;
      mf.appendChild(h('h3', { text: g }));
      fl.forEach((f) => {
        const head = h('button', { class: 'fhead', type: 'button', 'aria-pressed': 'false', title: f.title },
          h('span', { class: 'fid', text: f.id }), h('span', { class: 'ftitle', text: PP.vn(f.title) }));
        const lv = h('div', { class: 'flev', hidden: '' });
        const row = h('div', { class: 'lvs' });
        const ld = h('p', { class: 'ldesc' });
        f.levels.forEach((l) => {
          const b = h('button', { type: 'button', role: 'radio', 'aria-checked': 'false', 'data-l': l.id, title: PP.vn(l.desc), text: l.id });
          b.addEventListener('click', (e) => { S.sel.faults[f.id] = l.id; syncMenu(); if (e.detail) b.blur(); });
          row.appendChild(b);
        });
        lv.appendChild(row); lv.appendChild(ld);
        head.addEventListener('click', (e) => {
          if (S.sel.faults[f.id]) delete S.sel.faults[f.id]; else S.sel.faults[f.id] = f.levels[0].id;
          syncMenu(); if (e.detail) head.blur();
        });
        mf.appendChild(h('div', { class: 'frow', 'data-id': f.id }, head, lv));
        f.ref = { lv, row, ld, head };
      });
    });
    const mc = $('m-combo');
    cat.combos.forEach((c) => {
      const b = h('button', { type: 'button', class: 'combo', title: 'Đặt lỗi ' + c.faults.map((x) => x.join(' ')).join(' + ') + ' và môi trường của tổ hợp ' + c.id, text: c.title + ' · ' + c.id });
      b.addEventListener('click', (e) => { applyCombo(c); if (e.detail) b.blur(); });
      mc.appendChild(b);
    });
    const clr = h('button', { type: 'button', class: 'combo ghost', text: 'Bỏ hết lỗi' });
    clr.addEventListener('click', (e) => { S.sel.faults = {}; S.sel.env = { mu: false, cam: false, noise: false }; syncMenu(); if (e.detail) clr.blur(); });
    mc.appendChild(clr);
    $('trigger').addEventListener('change', (e) => { S.sel.trigger = e.target.value; });

    // môi trường
    [['mu', 'Mặt đường ướt, μ = 0,5'], ['cam', 'Camera trễ 150 ms (mặc định 100)'], ['noise', 'Nhiễu cảm biến vật thể ×1,5 (mưa)']].forEach(([k, label]) => {
      const b = h('button', { type: 'button', class: 'tog', 'aria-pressed': 'false', 'data-k': k }, h('i', { class: 'sw' }), h('span', { text: label }));
      b.addEventListener('click', (e) => { S.sel.env[k] = !S.sel.env[k]; syncMenu(); if (e.detail) b.blur(); });
      $('m-env').appendChild(b);
    });

    // xe, seed, ACC
    cat.vehicles.forEach((v) => {
      const b = h('button', { type: 'button', role: 'radio', 'aria-checked': 'false', 'data-id': v.id, text: v.id,
        title: `${v.id}: trục cơ sở ${PP.f(v.wb, 2)} m, rộng ${PP.f(v.w, 2)} m, ${PP.f(v.mass, 0)} kg` });
      b.addEventListener('click', (e) => { S.sel.veh = v.id; syncMenu(); if (e.detail) b.blur(); });
      $('m-veh').appendChild(b);
    });
    $('seed').addEventListener('input', (e) => { const n = parseInt(e.target.value, 10); if (n >= 1 && n <= 999) S.sel.seed = n; });
    $('acc').addEventListener('change', (e) => { S.sel.acc = e.target.value; });

    $('foot').textContent = '';
    $('foot').appendChild(h('div', { text: 'Planner thật (libpp_planner) chạy trong simulator SIL của repo, mỗi lần bấm Chạy. ' + cat.pp.replace('pp_planner ', 'Bản ').split(' calibration')[0] + '.' }));
    $('ver').textContent = cat.pp.replace(/ calibration.*/, '').replace('commit ', '· ');
  }

  function filterScen() {
    closeScenarioOptions();
    let n = 0;
    scenarioGroups.forEach(({ row, options }) => {
      options.forEach(({ scenario, button, query }) => {
        button.hidden = Boolean((S.fnFilter && scenario.fn !== S.fnFilter) || (S.q && !query.includes(S.q)));
      });
      row.hidden = options.every(({ button }) => button.hidden);
      if (!row.hidden) n++;
    });
    $('n-scen').textContent = n + ' / ' + scenarioGroups.size;
  }

  function applyCombo(c) {
    S.sel.faults = {};
    c.faults.forEach(([id, l]) => { S.sel.faults[id] = l; });
    const sim = c.sim || {};
    S.sel.env = { mu: (sim.road_mu ?? 1) < 1, cam: (sim.camera_latency_ms ?? 100) !== 100, noise: (sim.perception_noise_scale ?? 1) > 1 };
    if (!c.hosts.some(([a, b]) => a + '/' + b === S.sel.scen)) S.sel.scen = c.hosts[0][0] + '/' + c.hosts[0][1];
    syncMenu(true);
  }

  function syncMenu(revealScenario = false) {
    scenarioGroups.forEach(({ row, trigger, options }) => {
      const selected = options.some(({ scenario }) => scenario.id === S.sel.scen);
      trigger.toggleAttribute('data-selected', selected);
      options.forEach(({ scenario, button }) => button.setAttribute('aria-pressed', String(scenario.id === S.sel.scen)));
      if (revealScenario && selected && !row.hidden) row.scrollIntoView({ block: 'nearest' });
    });
    syncScenarioDescription();
    let nf = 0;
    S.cat.faults.forEach((f) => {
      const lvl = S.sel.faults[f.id];
      f.ref.head.setAttribute('aria-pressed', String(!!lvl));
      f.ref.lv.hidden = !lvl;
      if (lvl) {
        nf++;
        [...f.ref.row.children].forEach((b) => b.setAttribute('aria-checked', String(b.dataset.l === lvl)));
        f.ref.ld.textContent = PP.vn((f.levels.find((l) => l.id === lvl) || {}).desc || '');
      }
    });
    $('n-fault').textContent = nf ? nf + ' đã chọn' : '';
    document.querySelectorAll('#m-env .tog').forEach((b) => b.setAttribute('aria-pressed', String(!!S.sel.env[b.dataset.k])));
    [...$('m-veh').children].forEach((b) => b.setAttribute('aria-checked', String(b.dataset.id === S.sel.veh)));
    $('trigger').value = S.sel.trigger;
    $('seed').value = S.sel.seed;
    $('acc').value = S.sel.acc;
    const combo = S.cat.combos.find((c) => c.faults.length === Object.keys(S.sel.faults).length && c.faults.every(([a, b]) => S.sel.faults[a] === b));
    document.querySelectorAll('#m-combo .combo:not(.ghost)').forEach((b, i) => b.classList.toggle('on', !!combo && S.cat.combos[i] === combo));
    $('trigger').closest('label').hidden = !nf;
    if (S.phase === 'idle') setRunState();
  }

  function syncScenarioDescription() {
    const scenario = S.cat.scenarios.find((s) => s.id === S.sel.scen);
    const description = window.PP_SCENARIO_DESCRIPTIONS?.[scenario?.id]?.[document.documentElement.lang];
    $('scenario-description').hidden = !description;
    if (!description) return;
    const code = $('scenario-description-code');
    if (code.textContent === scenario.code) return;
    code.textContent = scenario.code;
    $('scenario-description-text').textContent = description;
  }

  // ---------- Pha và nút ----------
  function setPhase(p, err) {
    S.phase = p;
    if (err !== undefined) S.err = err;
    const live = p === 'running' || p === 'paused';
    $('run').textContent = p === 'idle' || p === 'done' || p === 'stopped' || p === 'error' ? 'Chạy planner' : 'Chạy lại';
    $('pause').disabled = !live;
    $('pause-ico').setAttribute('href', p === 'paused' ? '#i-play' : '#i-pause');
    $('stop').disabled = !(live || p === 'connecting' || p === 'finishing');
    $('scrub').disabled = !(p === 'paused' || p === 'done' || p === 'stopped');
    const d = S.d;
    $('screen').classList.toggle('idle', p === 'idle' || p === 'connecting' || p === 'error' || !d || !d.n);
    $('screen-msg').textContent = p === 'connecting' ? 'Đang khởi động simulator và nạp planner…' : p === 'error' ? S.err :
      'Chọn tình huống và lỗi ở bên trái, rồi bấm Chạy planner. Planner thật chạy theo thời gian thực trên máy này.';
    setRunState();
    refreshPill();
    S.dirty = true;
  }

  function setRunState() {
    const d = S.d, t = d && d.n ? d.t[d.n - 1] : 0;
    const el = $('run-state');
    el.dataset.s = S.phase;
    const txt = {
      idle: () => {
        const sc = S.cat && S.cat.scenarios.find((x) => x.id === S.sel.scen);
        const nf = Object.keys(S.sel.faults).length;
        return sc ? `Sẵn sàng: ${sc.code}, ${nf ? nf + ' lỗi' : 'không lỗi'}, ${S.sel.veh}` : 'Đang kết nối server…';
      },
      connecting: () => 'Đang khởi động simulator…',
      running: () => `Đang chạy · ${PP.f(t, 1)} / ${PP.f(d.dur, 0)} s · ${S.rate ? PP.vn(S.rate) + '×' : 'tối đa'}`,
      paused: () => `Tạm dừng ở ${PP.f(S.review != null ? d.t[S.review] : t, 1)} s`,
      finishing: () => 'Đang chấm kết quả…',
      done: () => (S.playback ? 'Phát lại · ' : 'Xong · ') + resText(d.res),
      stopped: () => `Đã dừng ở ${PP.f(t, 1)} s`,
      error: () => S.err,
    }[S.phase]();
    if (el.lastChild.textContent !== txt) el.lastChild.textContent = txt;
  }

  // ---------- Một lượt chạy ----------
  function newData(m) {
    return {
      name: m.name, desc: m.desc, dur: m.dur, dt: m.dt, seed: m.seed, pp: m.pp, veh: m.veh, road: m.road,
      tr: { dims: m.tr.dims, pos: [] }, faults: m.faults.map((f) => Object.assign({}, f, { t0: null, t1: null })),
      conds: m.conds, env: m.env, acc: m.acc, trigger: m.trigger,
      n: 0, t: [], ego: { x: [], y: [], yaw: [] }, v: [], ay: [], ayf: [], whl: [], off: [], dl: [], dr: [], fn: [], lk: [], el: [],
      steeringAngle: [], steeringSystemShare: [],
      pv: [], tv: [], lim: [], nar: [], vmax: [], dist: [], hor: [], cms: [], view: [], age: [], rq: [], tlc: [], ovr: [], traj: [], fa: [], lm: [], lmk: [],
      ch: [], alt: [], lcc: [], ka: [], lead: [], cl: [], ck: [],
      enums: { phase: ['NONE'], rq: ['OFF'] }, pre: { off: [], dlc: [], ay: [], cms: [] }, run: { mo: 0, md: Infinity, ma: 0, mc: 0 },
      res: null, lim_ay: null,
    };
  }
  const idx = (list, v) => { let i = list.indexOf(v); if (i < 0) { list.push(v); i = list.length - 1; } return i; };

  function pushFrame(m) {
    const d = S.d;
    d.t.push(m.t); d.ego.x.push(m.x); d.ego.y.push(m.y); d.ego.yaw.push(m.yaw);
    d.v.push(m.v); d.ay.push(m.ay); d.ayf.push(m.ayf); d.whl.push(m.whl); d.off.push(m.off); d.dl.push(m.dl); d.dr.push(m.dr);
    d.steeringAngle.push(m.steering_angle ?? m.whl * (d.veh.sr || 15));
    d.steeringSystemShare.push(m.steering_system_share);
    d.fn.push(Math.max(0, PP.FN.indexOf(m.fn))); d.lk.push(idx(d.enums.phase, m.lk)); d.el.push(idx(d.enums.phase, m.el));
    d.pv.push(m.pv); d.tv.push(m.tv); d.lim.push(m.lim); d.nar.push(m.nar); d.vmax.push(m.vmax); d.dist.push(m.dist);
    d.hor.push(m.hor); d.cms.push(m.cms); d.view.push(m.view); d.age.push(m.age);
    m.rq.forEach((r) => d.rq.push(idx(d.enums.rq, r)));
    d.tlc.push(m.tlc[0], m.tlc[1]); d.ovr.push(m.ovr);
    for (const v of m.traj) d.traj.push(v);
    for (const v of m.tr) d.tr.pos.push(v);
    for (const v of m.fa) d.fa.push(v);
    if (m.lm) d.lm.push(m.lm);          // chỉ có khi camera gửi frame mới; các chu kỳ sau dùng lại frame đó
    d.lmk.push(d.lm.length - 1);
    d.ch.push(m.ch ?? null); d.alt.push(m.alt ?? null); d.lcc.push(m.lcc ?? null); d.ka.push(m.ka ?? null);
    d.lead.push(m.lead ?? null); d.cl.push(m.cl ?? null); d.ck.push(m.ck ?? null);
    const r = d.run;
    r.mo = Math.max(r.mo, Math.abs(m.off)); r.md = Math.min(r.md, m.dl, m.dr); r.ma = Math.max(r.ma, Math.abs(m.ayf)); r.mc = Math.max(r.mc, m.cms);
    d.pre.off.push(r.mo * 100); d.pre.dlc.push(r.md * 100); d.pre.ay.push(r.ma); d.pre.cms.push(r.mc);
    d.n++;
    if (d.n === 1) $('screen').classList.remove('idle');
    PP.charts.push(d.n - 1);
    if (m.t >= d.dur - 0.03 && S.phase === 'running') setPhase('finishing');
    S.dirty = true;
  }

  function onMsg(m, id) {
    if (id !== S.runId) return;
    if (m.type === 'init') {
      const d = (S.d = newData(m));
      PP.scene.setCase(d);
      PP.charts.init(d);
      buildPanel(d);
      buildResultsShell(d);
      header(d);
      $('scrub').max = String(d.dur);
      $('scrub').value = '0';
      S.lastK = -1;
      setPhase('running');
      if (!S.playback && S.rate !== config().rate) control({ cmd: 'rate', value: S.rate });
    } else if (m.type === 'f') {
      if (S.d) pushFrame(m);
    } else if (m.type === 'done') {
      const d = S.d;
      d.res = m.res; d.lim_ay = m.lim_ay;
      if (document.documentElement.lang === 'en') {
        [...d.res.criteria, ...d.res.targets].forEach((item) => { item.metric = window.PP_METRICS_EN[item.metric] || item.metric; });
      }
      PP.charts.finish();
      buildResultsFinal(d);
      setPhase('done');
    } else if (m.type === 'error') {
      if (!S.playback) setPhase('error', m.message);
    } else if (m.type === 'state') {
      onState(m);
    }
  }

  // Trạng thái thực thi do server báo; kết luận đánh giá đến riêng trong 'done'.
  function onState(m) {
    if (S.playback) { if (!ACTIVE.includes(m.state) && m.state !== 'PAUSED') S.ended = true; return; }
    if (m.state === 'PAUSED' && S.phase === 'running') setPhase('paused');
    else if (m.state === 'RUNNING' && S.phase === 'paused') setPhase('running');
    if (ACTIVE.includes(m.state)) return;
    S.ended = true;
    forget();
    if (m.state === 'FAILED') setPhase('error', 'Lượt chạy lỗi (' + m.failure + ')' + (m.message ? ': ' + m.message : ''));
    else if (m.state === 'TIMED_OUT') setPhase('error', 'Lượt chạy quá thời gian cho phép');
    else if (m.state === 'CANCELLED' && !['stopped', 'idle'].includes(S.phase)) setPhase(S.d && S.d.n ? 'stopped' : 'idle');
  }

  async function start() {
    if (!S.cat) return;
    if (S.ac) S.ac.abort();
    const id = ++S.runId;
    S.d = null; S.review = null; S.lastK = -1; S.playback = null;
    PP.charts.reset(); PP.scene.clear(); resetPanels();
    $('crumb').textContent = '';
    setPhase('connecting');
    let res;
    try {
      res = await fetch('api/runs', {
        method: 'POST', body: JSON.stringify({ config: config() }),
        headers: { 'Content-Type': 'application/json', 'Idempotency-Key': Date.now() + '-' + Math.random().toString(16).slice(2) },
      });
    } catch (e) {
      if (id === S.runId) setPhase('error', 'Không kết nối được server. Mô phỏng cần máy chủ cục bộ. Chạy: python3 -m workbench.server rồi mở http://127.0.0.1:8793/');
      return;
    }
    if (!res.ok) {
      let detail = '';
      try { detail = (await res.json()).error || ''; } catch (err) { /* không phải JSON */ }
      if (id === S.runId) setPhase('error', detail || 'Server từ chối yêu cầu (' + res.status + ')');
      return;
    }
    S.run = (await res.json()).run_id;
    S.seq = 0; S.ended = false;
    remember();
    follow(id);
  }

  // Đọc luồng sự kiện của lượt chạy từ seq đã nhận; mất kết nối thì nối lại, không chạy lại.
  async function follow(id) {
    for (let attempt = 0; attempt < 6 && id === S.runId && !S.ended; attempt++) {
      const ac = (S.ac = new AbortController());
      let res;
      try {
        res = await fetch(runApi('/events?from=' + S.seq), { signal: ac.signal });
      } catch (e) {
        if (ac.signal.aborted) return;
        await sleep(1000);
        continue;
      }
      if (!res.ok) { if (id === S.runId) setPhase('error', 'Server từ chối yêu cầu (' + res.status + ')'); return; }
      const reader = res.body.getReader(), dec = new TextDecoder();
      let buf = '';
      try {
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          buf += dec.decode(value, { stream: true });
          let i;
          while ((i = buf.indexOf('\n')) >= 0) {
            const line = buf.slice(0, i);
            buf = buf.slice(i + 1);
            if (!line) continue;          // giữ kết nối
            const m = JSON.parse(line);
            if (m.seq) S.seq = m.seq;
            onMsg(m, id);
          }
        }
        attempt = -1;                     // nhận được dữ liệu: đếm lại số lần thử
      } catch (e) {
        if (ac.signal.aborted) return;
      }
      if (!S.ended) await sleep(500);
    }
    if (id === S.runId && !S.ended && ['connecting', 'running', 'paused', 'finishing'].includes(S.phase)) {
      setPhase('error', 'Mất kết nối với server giữa chừng');
    }
  }

  function stop() {
    if (!['connecting', 'running', 'paused', 'finishing'].includes(S.phase)) return;
    S.runId++;
    if (S.ac) S.ac.abort();
    if (S.run) post(runApi('/cancel'));
    forget();
    if (S.d && S.d.n) { S.review = null; setPhase('stopped'); } else setPhase('idle');
  }

  function togglePause() {
    if (S.phase === 'running') { control({ cmd: 'pause' }); setPhase('paused'); }
    else if (S.phase === 'paused') { S.review = null; control({ cmd: 'resume' }); setPhase('running'); }
  }

  // Xem lại khung k: chỉ khi không chạy trực tiếp
  function seek(k) {
    if (!S.d || !S.d.n || !['paused', 'done', 'stopped'].includes(S.phase)) return;
    S.review = PP.clamp(k, 0, S.d.n - 1);
    S.dirty = true;
  }
  PP.charts.onSeek = seek;
  // Tới khung gần thời điểm t nhất, lệch tối đa nửa chu kỳ planner.
  function seekTime(t) {
    const d = S.d;
    if (t == null || !isFinite(t) || !d || !d.n) return;
    seek(Math.round((t - d.t[0]) / d.dt));
  }

  function applyConfig(cfg) {
    const id = cfg && cfg.scenario ? cfg.scenario.sid + '/' + cfg.scenario.v : null;
    S.playCfg = !!(id && S.cat.scenarios.some((x) => x.id === id));
    if (!S.playCfg) return;
    const sim = cfg.sim || {};
    S.sel = { scen: id, faults: Object.fromEntries(cfg.faults || []), trigger: cfg.trigger || '',
      env: { mu: sim.road_mu === 0.5, cam: sim.camera_latency_ms === 150, noise: sim.perception_noise_scale === 1.5 },
      veh: cfg.vehicle || 'VP-0', seed: cfg.seed || 1, acc: cfg.acc || '' };
    syncMenu(true);
  }

  // Phát lại run đã xong từ luồng khung hình trong bundle: không sinh worker, không gọi planner.
  async function play(runId, t) {
    if (S.playback === runId && S.d && S.d.n && S.phase !== 'connecting') { seekTime(t); return; }
    if (S.ac) S.ac.abort();
    const id = ++S.runId;
    S.d = null; S.review = null; S.lastK = -1; S.run = null; S.seq = 0; S.ended = false; S.playback = runId; S.playCfg = false;
    forget();
    PP.charts.reset(); PP.scene.clear(); resetPanels();
    $('crumb').textContent = '';
    setPhase('connecting');
    let info, text;
    try {
      const a = await fetch('api/runs/' + runId);
      if (!a.ok) throw new Error('HTTP ' + a.status);
      info = await a.json();
      const b = await fetch('api/runs/' + runId + '/events?from=0');
      if (!b.ok) throw new Error('HTTP ' + b.status);
      text = await b.text();
    } catch (e) {
      if (id === S.runId) setPhase('error', 'Không đọc được run ' + runId + ': ' + e.message);
      return;
    }
    if (id !== S.runId) return;
    applyConfig(info.request && info.request.config);
    const lines = text.split('\n');
    for (let i = 0; i < lines.length; i++) {
      if (lines[i]) onMsg(JSON.parse(lines[i]), id);
      if (i % 200 === 199) { await sleep(0); if (id !== S.runId) return; }
    }
    if (!S.d || !S.d.n) { setPhase('error', 'Run này không có khung hình để phát lại.'); return; }
    if (S.phase !== 'done') setPhase('stopped');
    seekTime(t);
  }

  // ---------- Đầu trang và bảng thông số ----------
  function header(d) {
    const sc = curScen();
    const crumb = $('crumb');
    crumb.textContent = '';
    if (S.playback) {
      crumb.appendChild(h('span', { class: 'replay', text: 'Phát lại từ bundle, không chạy planner' }));
      crumb.appendChild(h('i', { text: '/' }));
    }
    crumb.appendChild(h('strong', { text: (sc ? sc.fn + ' · ' + sc.code : d.name) }));
    crumb.appendChild(h('span', { text: PP.vn((sc || {}).desc || d.desc) }));
    const fl = d.faults.map((f) => f.short);
    if (fl.length || d.conds.length) {
      crumb.appendChild(h('i', { text: '/' }));
      crumb.appendChild(h('span', { text: [...fl, ...d.conds.map((c) => c.split(',')[0].split(' (')[0])].join(', ') }));
    }
    crumb.appendChild(h('i', { text: '/' }));
    crumb.appendChild(h('span', { text: d.veh.name + ', seed ' + d.seed }));
    document.title = 'Path Planner SIL · ' + d.name;
  }

  const kv = (rows) => h('dl', { class: 'kv' }, rows.map(([k, label, unit]) => {
    const dd = h('dd', { 'data-k': k }, h('span', { class: 'v' }), unit ? h('small', { text: unit }) : null);
    R[k] = dd.querySelector('.v');
    R[k + '_dd'] = dd;
    return h('div', {}, h('dt', { text: label }), dd);
  }));

  function resetPanels() {
    $('pane-live').replaceChildren(h('p', { class: 'note', text: 'Thông số của planner và của xe sẽ cập nhật theo từng chu kỳ 25 ms khi lượt chạy bắt đầu.' }));
    $('pane-res').replaceChildren(h('p', { class: 'note', text: 'Chưa có lượt chạy.' }));
    R.pill = null; R.sum = null; R.conds = [];
  }

  function buildPanel(d) {
    const root = $('pane-live');
    root.textContent = '';
    const sc = curScen();
    R.pill = h('span', { class: 'pill run' });
    R.pillState = '';
    root.appendChild(h('div', { class: 'case-head' }, h('div', { class: 'case-title', text: sc ? PP.vn(sc.desc) : d.name }), R.pill));
    root.appendChild(h('div', { class: 'case-sub', text: (sc ? sc.code : d.name) + ' · ' + d.veh.name + ' · seed ' + d.seed + ' · ' + PP.f(d.dur, 0) + ' s' }));

    root.appendChild(h('div', { class: 'sec' }, h('h4', {}, 'Xe', h('em', { text: 'ground truth' })), kv([
      ['v', 'Tốc độ', 'km/h'], ['off', 'Lệch tâm làn, + trái', 'cm'], ['dl', 'DLC trái', 'cm'], ['dr', 'DLC phải', 'cm'],
      ['ay', 'a_y, lọc R79', 'm/s²'], ['st', 'Góc vô lăng', '°']])));

    root.appendChild(h('div', { class: 'sec' }, h('h4', {}, 'Vào', h('em', { text: 'planner nhận, mỗi 25 ms' })), kv([
      ['rq', 'Yêu cầu chức năng', ''], ['tlc', 'TLC của LKA, ELK', 's'], ['view', 'Tầm nhìn lane model', 'm'], ['age', 'Tuổi dữ liệu camera', 'ms'], ['lead', 'LeadTarget', '']])));
    const rq = h('span', { class: 'rq' }, ['LCC', 'LKA', 'ELK'].map((f) => h('span', { 'data-f': f, 'data-s': 'OFF', text: f })));
    R.rq_dd.replaceChildren(rq);
    R.rq_chips = [...rq.children];

    root.appendChild(h('div', { class: 'sec' }, h('h4', {}, 'Path được chọn', h('em', { text: 'arbitrator chạy thử' })), kv([
      ['ch', 'Planner được chọn', ''], ['fn', 'Chức năng đang lái', ''], ['pv', 'Path hợp lệ', ''], ['lim', 'Giới hạn ngang', ''], ['hor', 'Horizon quan sát', 's']])));

    root.appendChild(h('div', { class: 'sec' }, h('h4', {}, 'LCC planner', h('em', { text: 'output LccStatus' })), kv([
      ['lcm', 'Chế độ', ''], ['lcv', 'Path hợp lệ', ''], ['lcd', 'Quãng đã bám xe', 'm'], ['lct', 'Thời gian tính', 'ms']])));

    root.appendChild(h('div', { class: 'sec' }, h('h4', {}, 'LKA/ELK planner', h('em', { text: 'output InterventionStatus' })), kv([
      ['kaf', 'Chức năng', ''], ['kap', 'Pha', ''], ['kav', 'Path hợp lệ', ''], ['kat', 'Thời gian tính', 'ms']])));

    const cs = h('ul', { class: 'conds' });
    R.conds = [];
    const nf = d.faults.length;
    if (!nf && !d.conds.length) cs.appendChild(h('li', {}, h('span'), h('span', { class: 'conds-empty', text: 'Không có lỗi hay điều kiện xấu: ca chuẩn.' })));
    d.faults.forEach((f, i) => {
      const when = f.trigger ? 'khi ' + (TRIG[f.trigger] || f.trigger) : f.plan ? PP.f(f.plan[0], 1) + ' s → ' + (f.plan[1] == null ? 'hết' : PP.f(f.plan[1], 1) + ' s') : 'suốt lượt chạy';
      const li = h('li', {}, h('i', { class: 'led' }), h('span', {}, f.label, h('span', { class: 'when', text: when })));
      cs.appendChild(li);
      R.conds.push({ li, i });
    });
    d.conds.forEach((c) => {
      const li = h('li', { class: 'on' }, h('i', { class: 'led' }), h('span', {}, c, h('span', { class: 'when', text: 'suốt lượt chạy' })));
      cs.appendChild(li);
    });
    root.appendChild(h('div', { class: 'sec' }, h('h4', {}, 'Điều kiện', h('em', { text: 'chấm sáng khi đang tác động' })), cs));
  }

  function buildResultsShell(d) {
    const root = $('pane-res');
    root.textContent = '';
    R.sumT = h('em', { text: '' });
    R.sum = [];
    const cells = [['cm', 'Lệch tâm lớn nhất'], ['cm', 'DLC nhỏ nhất'], ['m/s²', 'a_y lớn nhất, lọc R79'], ['ms', 'Thời gian tính lớn nhất']]
      .map(([u, l]) => { const b = h('b', { text: '—' }); R.sum.push([b, u]); return h('div', {}, b, h('span', { text: l })); });
    root.appendChild(h('div', { class: 'sec', style: 'margin-top:0' }, h('h4', {}, 'Số liệu đến giờ', R.sumT), h('div', { class: 'summary' }, cells)));
    R.resBody = h('div', {}, h('p', { class: 'note', text: 'Kết luận của evaluator (tiêu chí, chỉ tiêu hiệu năng) có sau khi lượt chạy kết thúc.' }));
    root.appendChild(R.resBody);
  }

  const sig = (v) => PP.f(v, Math.abs(v) >= 100 ? 0 : Math.abs(v) >= 10 ? 1 : Math.abs(v) >= 1 ? 2 : Math.abs(v) >= 0.1 ? 3 : 4);
  function buildResultsFinal(d) {
    const crit = d.res.criteria, bad = crit.filter((c) => !c.passed);
    const unjudged = d.res.judged === false && !bad.length;
    const body = h('div', {});
    body.appendChild(h('div', { class: 'case-head', style: 'margin-top:14px' },
      h('div', { class: 'case-title', text: d.res.passed ? 'Đạt toàn bộ tiêu chí áp dụng' : unjudged ? 'Ca không được chấm' : 'Trượt ' + bad.length + ' tiêu chí' }),
      h('span', { class: 'pill ' + (d.res.passed ? 'ok' : unjudged ? 'idle' : 'bad') }, use(d.res.passed ? 'i-check' : unjudged ? 'i-warn' : 'i-x'), resText(d.res))));
    body.appendChild(h('div', { class: 'case-sub', text: crit.length + ' tiêu chí áp dụng cho ca này' + (bad.length ? '. Trượt: ' + bad.map((c) => c.id).join(', ') : '') }));
    (d.res.not_judged || []).forEach((t) => body.appendChild(h('p', { class: 'note', text: t })));
    const list = h('ul', { class: 'crit' });
    [...bad, ...crit.filter((c) => c.passed)].forEach((c) => {
      const info = h('span', {}, h('span', { class: 'm', text: c.metric }), h('span', { class: 'd', text: c.id + ' · đo ' + sig(c.value) + ' · giới hạn ' + PP.limit(c.limit) }));
      if (!c.passed && c.first_fail_s != null) {
        const jump = h('button', { class: 'jump', type: 'button', text: 'Tới lần trượt đầu, t = ' + PP.f(c.first_fail_s, 2) + ' s' });
        jump.addEventListener('click', () => seekTime(c.first_fail_s));
        info.appendChild(jump);
      }
      list.appendChild(h('li', { class: c.passed ? 'ok' : 'bad' }, use(c.passed ? 'i-check' : 'i-x'), info));
    });
    body.appendChild(h('div', { class: 'sec' }, h('h4', {}, 'Tiêu chí', h('em', { text: 'cả lượt chạy, trượt xếp trước' })), list));
    const tg = h('dl', { class: 'kv' });
    d.res.targets.forEach((t) => tg.appendChild(h('div', {}, h('dt', { text: t.metric }), h('dd', {}, sig(t.value), h('small', { text: t.unit })))));
    body.appendChild(h('div', { class: 'sec' }, h('h4', {}, 'Chỉ tiêu hiệu năng', h('em', { text: 'cả lượt chạy' })), tg));
    body.appendChild(h('p', { class: 'note', text: d.pp + '. Thời gian tính là đồng hồ thật của máy, gồm cả adapter SIL (ctypes), đo trong lúc chạy thời gian thực.' }));
    R.resBody.replaceWith(body);
    R.resBody = body;
  }

  // ---------- Cập nhật theo khung ----------
  const setT = (el, s) => { if (el && el.textContent !== s) el.textContent = s; };
  const flag = (ok, textOk, textNo) => h('span', { class: 'flag ' + (ok ? 'ok' : 'bad') }, use(ok ? 'i-check' : 'i-x'), ok ? textOk : textNo);

  function refreshPill() {
    if (!R.pill) return;
    const d = S.d;
    const st = S.phase === 'done' ? (d.res.passed ? 'ok' : 'bad') : S.phase === 'stopped' ? 'stop' : S.phase === 'paused' ? 'pause' : S.phase === 'finishing' ? 'run' : 'run';
    const txt = { ok: 'Đạt', bad: S.phase === 'done' ? resText(d.res) : 'Không đạt', stop: 'Đã dừng', pause: 'Tạm dừng', run: S.phase === 'finishing' ? 'Đang chấm' : 'Đang chạy' }[st];
    if (R.pillState === st + txt) return;
    R.pillState = st + txt;
    R.pill.className = 'pill ' + (st === 'pause' || st === 'stop' ? 'idle' : st);
    R.pill.replaceChildren(...(st === 'ok' || st === 'bad' ? [use(st === 'ok' ? 'i-check' : 'i-x'), txt] : st === 'run' ? [h('i', { class: 'live-dot' }), txt] : [txt]));
  }

  function readouts(d, k) {
    const sr = d.veh.sr || 15;
    const fn = d.fn[k];
    const t = d.t[k];
    setT(R.v, PP.f(d.v[k] * 3.6, 0));
    setT(R.off, PP.fs(d.off[k] * 100, 0));
    setT(R.dl, PP.f(d.dl[k] * 100, 0));
    setT(R.dr, PP.f(d.dr[k] * 100, 0));
    R.dl_dd.dataset.state = d.dl[k] < 0 ? 'bad' : '';
    R.dr_dd.dataset.state = d.dr[k] < 0 ? 'bad' : '';
    setT(R.ay, PP.f(d.ayf[k], 2));
    setT(R.st, PP.fs(d.whl[k] * sr * 180 / Math.PI, 1));

    R.rq_chips.forEach((c, i) => { const st = d.enums.rq[d.rq[k * 3 + i]]; if (c.dataset.s !== st) c.dataset.s = st; });
    const tl = d.tlc[k * 2], te = d.tlc[k * 2 + 1];
    setT(R.tlc, tl != null ? PP.f(tl, 2) + ' (LKA)' : te != null ? PP.f(te, 2) + ' (ELK)' : '—');
    setT(R.view, d.view[k] == null ? '—' : PP.f(d.view[k], 0));
    setT(R.age, d.age[k] == null ? '—' : PP.f(d.age[k], 0));

    const phase = fn === 2 ? d.enums.phase[d.lk[k]] : fn === 3 ? d.enums.phase[d.el[k]] : '';
    const fnTxt = PP.FN[fn] + (phase && phase !== 'NONE' ? ' · ' + phase : '');
    if (R.fn.dataset.v !== fnTxt) {
      R.fn.dataset.v = fnTxt;
      R.fn.replaceChildren(h('span', { class: 'fn-badge' }, h('i', { class: 'dot ' + PP.FN[fn].toLowerCase() }), fnTxt));
    }
    const pvk = (d.pv[k] ? 1 : 0) + '';
    if (R.pv.dataset.v !== pvk) {
      R.pv.dataset.v = pvk;
      R.pv.replaceChildren(flag(!!d.pv[k], 'Có', 'Không'));
    }
    setT(R.lim, d.lim[k] ? 'Chạm' + (d.vmax[k] ? ', v_max ' + PP.f(d.vmax[k] * 3.6, 0) + ' km/h' : '') : '—');
    setT(R.hor, PP.f(d.hor[k], 2));
    const lc = d.lcc[k], ka = d.ka[k], ld = d.lead[k];
    setT(R.ch, d.ch[k] == null ? '—' : d.ch[k] === 'LCC' ? 'LCC planner' : 'LKA/ELK planner');
    setT(R.lead, !ld ? '—' : ld.c + ' #' + ld.id + ', cách ' + PP.f(ld.gap, 1) + ' m' + (ld.v ? '' : ', không hợp lệ'));
    setT(R.lcm, lc ? lc.m : '—');
    setT(R.lcv, lc ? (lc.v ? 'Có' : 'Không') : '—');
    setT(R.lcd, lc ? PP.f(lc.d, 1) : '—');
    setT(R.lct, PP.f(d.cl[k], 2));
    setT(R.kaf, ka ? ka.f : '—');
    setT(R.kap, !ka ? '—' : ka.f === 'ELK' ? ka.el : ka.f === 'LKA' ? ka.lk : 'NONE');
    setT(R.kav, ka ? (ka.v ? 'Có' : 'Không') : '—');
    setT(R.kat, PP.f(d.ck[k], 2));

    const nf = d.faults.length;
    R.conds.forEach((c) => c.li.classList.toggle('on', !!d.fa[k * nf + c.i]));

    if (R.sum) {
      R.sum[0][0].textContent = PP.f(d.pre.off[k], 0) + ' ' + R.sum[0][1];
      R.sum[1][0].textContent = PP.f(d.pre.dlc[k], 0) + ' ' + R.sum[1][1];
      R.sum[2][0].textContent = PP.f(d.pre.ay[k], 2) + ' ' + R.sum[2][1];
      R.sum[3][0].textContent = PP.f(d.pre.cms[k], 2) + ' ' + R.sum[3][1];
      R.sumT.textContent = 't = ' + PP.f(t, 1) + ' s';
    }

    // HUD trên màn hình
    const chip = $('chip-fn');
    if (chip.dataset.fn !== PP.FN[fn]) chip.dataset.fn = PP.FN[fn];
    setT($('chip-fn-t'), PP.FN[fn]);
    setT($('chip-fn-s'), phase && phase !== 'NONE' ? phase : '');
    setT($('chip-path-t'), d.pv[k] ? 'Path hợp lệ' : 'Path không hợp lệ');
    $('chip-path').classList.toggle('warn', !d.pv[k]);
    setT($('hud-v'), PP.f(d.v[k] * 3.6, 0));
    // Mô hình lấy chiều trái là dương; SVG xoay theo chiều kim đồng hồ khi góc dương.
    $('hud-steering-rotor').setAttribute('transform', `rotate(${-d.steeringAngle[k] * 180 / Math.PI} 24 24)`);
    const systemShare = d.steeringSystemShare[k];
    $('hud-steering').style.color = systemShare == null ? '' :
      `color-mix(in srgb, var(--scr-steering-driver), var(--scr-steering-system) ${systemShare * 100}%)`;
    const act = [];
    for (let i = 0; i < nf; i++) if (d.fa[k * nf + i]) act.push(d.faults[i].short);
    $('fault-flag').classList.toggle('on', act.length > 0);
    setT($('fault-flag-t'), act.join(' · '));
    const br = $('hud-br');
    if (br.dataset.k !== String(k)) {
      br.replaceChildren(...[
        h('div', { text: 'Tầm nhìn lane model ' + (d.view[k] == null ? '—' : PP.f(d.view[k], 0) + ' m') }),
        h('div', { text: 'Quỹ đạo ' + PP.f(d.hor[k], 1) + ' s, 31 điểm' }),
        d.alt[k] ? h('div', { text: 'Nét đứt: path của planner không được chọn' }) : null,
        h('div', { class: 'key' }, 'vạch thật (truth)', h('i')),
        h('div', { class: 'key' }, 'lane model planner nhận', h('i', { class: 'lm' })),
      ].filter(Boolean));
      br.dataset.k = String(k);
    }
  }

  function frame() {
    const d = S.d;
    if (!d || !d.n) { setRunState(); return; }
    const k = S.review != null ? Math.min(S.review, d.n - 1) : d.n - 1;
    PP.scene.render(d, k);
    PP.charts.setCursor(k);
    if (k !== S.lastK) { readouts(d, k); S.lastK = k; }
    const sc = $('scrub');
    if (sc.disabled || document.activeElement !== sc) sc.value = String(d.t[k]);
    $('clock').replaceChildren(h('b', { text: PP.f(d.t[k], 1) }), ' / ' + PP.f(d.dur, 1) + ' s');
    setRunState();
  }

  // Vẽ theo nhịp màn hình; nếu tab bị ẩn hoặc giảm nhịp (rAF đứng) thì một bộ định giờ dự phòng vẫn cập nhật.
  let lastRaf = performance.now();
  function loop() {
    lastRaf = performance.now();
    if (S.dirty) { S.dirty = false; frame(); }
    requestAnimationFrame(loop);
  }
  setInterval(() => {
    if (S.dirty && performance.now() - lastRaf > 250) { S.dirty = false; frame(); }
  }, 100);

  // ---------- Điều khiển ----------
  $('run').addEventListener('click', (e) => { start(); if (e.detail) e.currentTarget.blur(); });
  $('pause').addEventListener('click', (e) => { togglePause(); if (e.detail) e.currentTarget.blur(); });
  $('stop').addEventListener('click', (e) => { stop(); if (e.detail) e.currentTarget.blur(); });
  $('scrub').addEventListener('input', (e) => {
    const d = S.d;
    if (d) seek(Math.round((parseFloat(e.target.value) - d.t[0]) / d.dt));
  });
  $('rate').addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    S.rate = parseFloat(b.dataset.r);
    [...$('rate').children].forEach((x) => x.setAttribute('aria-checked', String(x === b)));
    if (S.phase === 'running' || S.phase === 'paused') control({ cmd: 'rate', value: S.rate });
    setRunState();
    if (e.detail) b.blur();
  });
  $('view').addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    [...$('view').children].forEach((x) => x.setAttribute('aria-checked', String(x === b)));
    PP.charts.setMode(b.dataset.v);
    S.dirty = true; S.lastK = -1;
    if (e.detail) b.blur();
  });
  const tabs = { live: [$('tab-live'), $('pane-live')], res: [$('tab-res'), $('pane-res')] };
  Object.entries(tabs).forEach(([name, [btn]]) => btn.addEventListener('click', (e) => {
    Object.entries(tabs).forEach(([n, [b, p]]) => { b.setAttribute('aria-selected', String(n === name)); p.hidden = n !== name; });
    if (e.detail) btn.blur();
  }));

  document.addEventListener('keydown', (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const tag = e.target.tagName;
    if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;
    if (e.key === ' ' && tag === 'BUTTON') return;
    if (e.key === ' ') { e.preventDefault(); togglePause(); }
    else if (e.key === 'ArrowRight' && S.review != null) seek(S.review + (e.shiftKey ? 200 : 20));
    else if (e.key === 'ArrowLeft' && ['paused', 'done', 'stopped'].includes(S.phase) && S.d) seek((S.review != null ? S.review : S.d.n - 1) - (e.shiftKey ? 200 : 20));
  });

  window.addEventListener('pagehide', () => { if (S.ac) S.ac.abort(); });

  // ---------- Giao diện sáng tối ----------
  function themeIcon() {
    const dark = document.documentElement.dataset.theme === 'dark' ||
      (!document.documentElement.dataset.theme && window.matchMedia('(prefers-color-scheme: dark)').matches);
    document.querySelector('#theme-ico use').setAttribute('href', dark ? '#i-sun' : '#i-moon');
    return dark;
  }
  $('theme').addEventListener('click', (e) => {
    const dark = themeIcon();
    const next = dark ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('pp-theme', next); } catch (err) { /* không lưu được */ }
    themeIcon();
    PP.scene.readColors();
    PP.charts.resize();
    S.dirty = true;
    if (e.detail) e.currentTarget.blur();
  });
  if (window.matchMedia) window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { themeIcon(); PP.scene.readColors(); S.dirty = true; });

  // ---------- Khởi động ----------
  async function boot() {
    themeIcon();
    resetPanels();
    PP.scene.resize();
    PP.scene.clear();
    requestAnimationFrame(loop);
    if (location.protocol === 'file:') {
      setPhase('error', 'Trang cần server để chạy planner thật. Chạy: python3 -m workbench.server rồi mở http://127.0.0.1:8793/');
      $('run').disabled = true;
      return;
    }
    try {
      const r = await fetch('api/catalog');
      if (!r.ok) {
        let detail = '';
        try { detail = (await r.json()).error || ''; } catch (err) { /* bản tĩnh có thể trả HTML */ }
        throw new Error(detail || 'HTTP ' + r.status);
      }
      S.cat = await r.json();
      if (document.documentElement.lang === 'en') {
        S.cat.faults.forEach((fault) => {
          const entries = window.PP_FAULTS_EN[fault.id];
          if (!entries) return;
          fault.title = entries[0];
          fault.levels.forEach((level) => {
            const index = level.id.charCodeAt(0) - 96;
            const suffix = level.desc.match(/ \([^()]*\)$/);
            if (entries[index]) level.desc = entries[index] + (suffix && /(?:fault_|count|value|lines)/.test(suffix[0]) ? suffix[0] : '');
          });
        });
        S.cat.combos.forEach((combo) => { if (combo.id === 'G01') combo.title = 'Rainy night'; });
        S.cat.scenarios.forEach((sc) => {
          const entries = window.PP_SCENARIOS_EN[sc.sid];
          const index = sc.v.length === 1 ? sc.v.charCodeAt(0) - 97 : -1;
          if (entries && entries[index]) sc.desc = entries[index];
          else if (sc.sid === 'S8' && sc.v === 'late') sc.desc = 'Inject ELK REQUEST after the front tyre has crossed the marking';
          else if (sc.sid === 'S13' && /-elk$/.test(sc.v)) sc.desc = 'S5c, EPS latency ' + ({a:75,b:100,c:150}[sc.v[0]]) + ' ms';
        });
      }
    } catch (e) {
      setPhase('error', 'Không đọc được danh mục từ server (' + e.message + '). Mô phỏng cần máy chủ cục bộ. Chạy: python3 -m workbench.server rồi mở http://127.0.0.1:8793/');
      $('run').disabled = true;
      return;
    }
    buildMenu(S.cat);
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(RUN_KEY) || 'null'); } catch (err) { /* không đọc được */ }
    if (saved && saved.sel) S.sel = saved.sel;
    filterScen();
    syncMenu(true);
    setPhase('idle');
    if (saved && saved.run) resume(saved.run);
  }

  // Tab mở lại khi lượt chạy cũ còn chạy trên server: nối tiếp từ đầu luồng sự kiện.
  async function resume(runId) {
    try {
      const r = await fetch('api/runs/' + runId);
      const st = r.ok ? await r.json() : null;
      if (!st || !ACTIVE.includes(st.state)) { forget(); return; }
    } catch (err) { return; }
    S.run = runId; S.seq = 0; S.ended = false;
    const id = ++S.runId;
    setPhase('connecting');
    follow(id);
  }
  const booted = boot();
  PP.sim = { play: async (runId, t) => { await booted; if (S.cat) await play(runId, t); } };
})();
