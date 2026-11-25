(() => {
  'use strict';
  const WB = window.WB;
  const PP = window.PP;
  const { h, ico, mono, wait, tag, lbl, kv, card, page } = WB;

  const head = (title, sub, extra) => h('header', { class: 'wb-head' }, h('div', null, h('h1', null, title), h('p', { class: 'wb-sub' }, sub)), extra || null);
  const when = (iso) => (iso ? iso.replace('T', ' ').slice(0, 16) : '');

  async function suiteView(rest) {
    WB.title('Suite và regression');
    const list = (await WB.api('suites')).suites;
    if (!list.length) return page(head('Suite và regression', 'Chưa có lần chạy suite nào trong build/benchmark.'));
    const id = rest[0] && list.some((s) => s.id === rest[0]) ? rest[0] : list[0].id;
    const s = await WB.api('suites/' + id);
    const prev = list[list.findIndex((x) => x.id === id) + 1];
    const select = h('select', { class: 'wb-select', style: 'min-width:300px;font-family:var(--font-mono);font-size:13px', 'aria-label': 'Lần chạy', onchange: (e) => WB.go('#/suite/' + e.target.value) },
      ...list.map((x) => h('option', { value: x.id, selected: x.id === id }, x.id + (x.planner.commit ? ' · ' + x.planner.commit : ''))));
    const pass = s.verdict === 'Đạt';
    const c = s.counts || {};
    const verdict = h('section', { class: 'wb-verdict' + (pass ? ' pass' : ''), 'aria-label': 'Kết luận của suite' },
      h('div', { class: 'big' }, ico(pass ? 'i-check' : 'i-x', pass ? 'ok-ico' : 'bad-ico'),
        h('div', null, lbl('Kết luận'), h('b', { class: pass ? 'good' : 'bad' }, s.verdict || '—'), h('span', { style: 'font-size:12.5px;color:var(--ink-2)' }, 'Tích hợp được: ' + (s.integrable ? 'có' : 'không') + (s.b0_blocked ? ' · B0 bị chặn' : '')))),
      h('div', { class: 'wb-stat' }, h('b', null, String(s.runs ?? s.planned ?? '—')), h('span', null, 'lần chạy' + (s.partial ? ' (chưa đủ)' : ''))),
      h('div', { class: 'wb-stat' }, h('b', { class: c.BLOCKER ? 'bad' : '' }, String(c.BLOCKER ?? 0)), h('span', null, 'trượt BLOCKER')),
      h('div', { class: 'wb-stat' }, h('b', null, String(c.MAJOR ?? 0)), h('span', null, 'trượt MAJOR')),
      h('div', { class: 'wb-stat' }, h('b', null, String(c.MINOR ?? 0)), h('span', null, 'trượt MINOR')),
      h('div', { style: 'flex:1 1 100%;font-size:12.5px;color:var(--ink-2)' }, 'Planner ', mono((s.planner && s.planner.pp_version) || '—'), s.n_out_of_scope ? ' · ' + s.n_out_of_scope + ' lần trượt nằm ngoài phạm vi chấm, không tính vào kết luận' : ''));

    const max = Math.max(1, ...s.by_requirement.map((q) => q.n));
    const byReq = card('', lbl('Trượt BLOCKER theo requirement'),
      h('div', { class: 'wb-bars', style: 'padding-top:6px' }, ...(s.by_requirement.length ? s.by_requirement.map((q) => h('div', { class: 'wb-bar' },
        mono(q.id, { style: 'font-size:12px' }), h('span', { class: 'dim', style: 'font-size:11.5px' }, q.sg), h('i', null, h('b', { style: 'width:' + Math.max(3, Math.round(q.n / max * 100)) + '%' })), h('em', { class: 'wb-mono' }, String(q.n)))) : [h('p', { class: 'wb-small' }, 'Không có trượt BLOCKER.')])));

    const howto = h('section', { class: 'wb-card', style: 'gap:10px' }, lbl('Điều tra một ca trượt'),
      h('p', { class: 'wb-sub' }, 'Mở lại chạy lại ca từ file đã đóng băng của suite, rồi so behavior checksum với kết quả đã ghi. Run mới có đủ bundle để phát lại và tới lần trượt đầu.'),
      h('p', { class: 'wb-small' }, prev ? [h('a', { href: '#/review/so-sanh/suite/' + prev.id + '/' + id }, 'So với lần chạy ngay trước (' + prev.id + ')'), ' · '] : '', 'Đọc ', mono('conclusion.json'), ' của lần chạy', s.has_report ? [h('span', null, '; báo cáo đầy đủ ở '), h('a', { href: 'api/suites/' + id + '/report', target: '_blank', rel: 'noopener' }, 'report.html')] : '', '.'));
    const reopen = (f) => async (e) => {
      const b = e.currentTarget;
      b.disabled = true; b.textContent = 'Đang mở…';
      try {
        const r = await WB.api('suites/' + id + '/reopen', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ case: f.case, seed: f.seed }) });
        WB.go('#/runs/' + r.run_id);
      } catch (err) { b.textContent = 'Không mở được'; b.title = err.message; }
    };

    const rows = s.first_fails;
    const fails = h('section', { class: 'wb-table', 'aria-label': 'Ca trượt BLOCKER' }, h('div', { style: 'min-width:1020px' },
      h('div', { style: 'display:flex;align-items:baseline;gap:12px;padding:14px 16px 10px' }, lbl('Ca trượt BLOCKER'), h('span', { class: 'wb-small' }, rows.length + ' requirement, mỗi requirement một ca đầu tiên (tổng ' + (c.BLOCKER ?? 0) + ' lần trượt)')),
      h('div', { class: 'wb-row fails h', style: 'min-height:36px' }, ...['Requirement', 'SG', 'Ca', 'Profile', 'Seed', 'first_fail_s', 'Giá trị · ngưỡng', ''].map((t) => h('span', null, t))),
      ...rows.map((f) => h('div', { class: 'wb-row fails' },
        mono(f.requirement, { style: 'font-size:12px' }), h('span', { style: 'font-size:12px;color:var(--ink-2)' }, f.sg || '—'),
        h('span', { class: 'wb-mono', style: 'font-size:12px;min-width:0;overflow-wrap:anywhere' }, f.case, f.text ? h('span', { class: 'wb-small', style: 'display:block;font-family:var(--font)' }, f.text) : null),
        mono(f.profile || '—', { style: 'font-size:12px' }), mono(String(f.seed ?? '—'), { style: 'font-size:12px' }),
        mono(f.first_fail_s != null ? WB.num(f.first_fail_s) : 'cả lượt', { style: 'font-size:12px' + (f.first_fail_s == null ? ';color:var(--ink-3)' : '') }),
        mono(WB.num(f.value) + ' · ' + WB.limit(f.limit), { style: 'font-size:12px;color:var(--wb-crit-ink)' }),
        h('button', { type: 'button', class: 'wb-btn', style: 'height:32px;padding:0 10px;font-size:12.5px', onclick: reopen(f) }, 'Mở lại')))));

    return page(
      head('Suite và regression', h('span', null, 'Kết luận chính thức theo SQTS 8.4. Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn. Mô hình xe VP-0 đến VP-5 chưa validation.'),
        h('label', { class: 'wb-field' }, 'Lần chạy', select)),
      verdict,
      h('div', { class: 'wb-cols' }, h('div', { class: 'a', style: 'flex:1 1 320px' }, byReq), h('div', { class: 'b', style: 'flex:1 1 320px' }, howto)),
      rows.length ? fails : null,
      h('p', { class: 'wb-small' }, 'Kết thúc ', when(s.finished), '. Đọc từ ', mono('GET /api/suites/' + id), '.'));
  }

  async function trustView() {
    WB.title('Độ tin cậy');
    const g = await WB.api('golden').catch(() => ({ recorded: false }));
    const mark = (st) => (st === 'ok' ? h('span', { class: 'wb-ico good', style: 'font-weight:600' }, ico('i-check'), 'khớp')
      : st ? h('span', { class: 'wb-ico bad', style: 'font-weight:600' }, ico('i-warn'), st) : h('span', { class: 'dim' }, 'không có'));
    const env = g.environment || {};
    const golden = !g.recorded
      ? card('dash', lbl('Tất định: golden set'), h('p', { class: 'wb-sub' }, 'Chưa có baseline. Chạy ', mono('python3 -m eval.golden record'), ' để ghi.'))
      : card('', h('div', { style: 'display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 14px;padding-bottom:8px' }, lbl('Tất định: golden set'),
          h('span', { class: 'wb-pill' }, new Set(g.cases.map((c) => c.id)).size + ' ca · ' + g.cases.length + ' lượt · ' + g.n_results + ' kết quả theo đường chạy'),
          h('span', { class: 'wb-pill' }, (g.paths || []).join(' · ')),
          h('span', { class: 'wb-small' }, 'ghi lúc ' + new Date(g.recorded_at * 1000).toLocaleString('vi-VN'))),
        h('p', { class: 'wb-small', style: 'padding-bottom:10px' }, mono((env.pp_version || '—') + ' · Python ' + (env.python || '?') + ' · numpy ' + (env.numpy || '?') + ' · ' + (env.platform || '?'))),
        h('div', { class: 'wb-table' }, h('div', { style: 'min-width:740px' },
          h('div', { class: 'wb-row gold h' }, ...['ID', 'Ca', 'Seed', 'Checksum', 'runner', 'suite', 'live'].map((t) => h('span', null, t))),
          ...g.cases.map((c) => h('div', { class: 'wb-row gold' }, mono(c.id, { style: 'font-size:12px' }), h('span', null, c.purpose || '—'), mono(String(c.seed), { style: 'font-size:12px' }),
            mono(WB.short(c.checksum, 8), { style: 'font-size:12px' }), mark(c.paths.runner), mark(c.paths.suite), mark(c.paths.live))))),
        h('p', { class: 'wb-small', style: 'padding-top:10px' }, 'Baseline gắn với thư viện planner ghi ở trên. Build lại thư viện thì phải ghi lại baseline bằng ', mono('python3 -m eval.golden record'), '.'));

    const li = (icon, cls, t, d) => h('div', { class: 'wb-li' }, ico(icon, cls), h('div', { style: 'flex:1;min-width:0;display:flex;flex-direction:column;gap:3px' }, h('span', null, t), d ? h('code', null, d) : null));
    const checks = card('', lbl('Kiểm bên chấm'),
      li('i-check', 'ok-ico', 'Selfcheck: bên chấm phải bắt được lỗi cố ý', 'python3 -m eval.selfcheck'),
      li('i-check', 'ok-ico', 'Conformance B0, chạy trong CI', 'python3 -m eval.conformance'),
      li('i-check', 'ok-ico', 'Tool confidence: TI, TD, TCL theo ISO 26262-8 mục 11', 'Simulation Handbook mục 11'));
    const verif = card('dash', h('div', { style: 'display:flex;gap:10px;align-items:center;padding-bottom:6px' }, lbl('Verification')),
      li('i-check', 'ok-ico', 'Ca giải tích yaw rate ổn định: so r = v·δ / (L + K·v²) trên VP-0', 'tests/sim/test_vehicle.py'),
      li('i-check', 'ok-ico', 'Sai số rời rạc hóa ở bước 1; 0,5; 0,25 ms: dưới 1,5 mm trên ba ca vòng kín', 'python3 -m eval.verify_sim calculation'),
      li('i-check', 'ok-ico', 'Sensitivity ±20 % của C_f, C_r, I_z, trễ EPS: không đổi kết luận trên 24 lượt', 'python3 -m eval.verify_sim sensitivity'),
      li('i-wait', 'dim', 'Quét K, steering ratio, actuator delay theo dải có nguồn (backlog)'));
    const hb = card('dash', h('div', { style: 'display:flex;gap:10px;align-items:center;padding-bottom:6px' }, lbl('Simulation Handbook'), mono('docs/vi/simulation-handbook.md', { style: 'font-size:12px' })),
      h('p', { class: 'wb-sub' }, '18 mục theo R171 Annex 5, mỗi model có một mục riêng ghi mục đích, giả định, nguồn tham số, miền dùng, verification và trạng thái validation. Chưa có dữ liệu xe thật nên cả 9 model ghi "chưa validation". Mọi báo cáo kết luận ghi phiên bản simulator và trạng thái này.'));

    return page(head('Độ tin cậy', 'Kết quả của simulator tin được tới đâu: tất định, kiểm bên chấm, verification và hồ sơ theo R171 Annex 5. Chưa có dữ liệu xe thật nên validation ghi "chưa đánh giá".'),
      golden, h('div', { class: 'wb-cols' }, h('div', { class: 'a', style: 'flex:1 1 360px' }, checks), h('div', { class: 'b', style: 'flex:1 1 360px' }, verif)), hb);
  }

  function platformView() {
    WB.title('Nền tảng');
    const mod = (n, t) => h('div', { class: 'wb-mod' }, h('b', null, n), h('span', null, t));
    const arrow = (t) => h('div', { class: 'wb-link' }, h('span', { 'aria-hidden': 'true' }, '↓'), t);
    const diagram = card('', lbl('Sơ đồ lớp'),
      h('div', { style: 'display:flex;flex-direction:column;gap:2px;padding-top:8px' },
        h('div', { class: 'wb-band web' }, lbl('Web: chỉ nói chuyện qua HTTP, không đọc mã nguồn'), h('div', { class: 'wb-mods' }, mod('web/simulation', 'Giao diện workbench'), mod('web/serve.py', 'Trang tài liệu; chuyển tiếp /simulation/api tới workbench'))),
        arrow('HTTP, sự kiện NDJSON đánh số seq'),
        h('div', { class: 'wb-band core' }, lbl('Lõi chung: không biết SUT là gì, chỉ dùng thư viện chuẩn'), h('div', { class: 'wb-mods' }, mod('workbench/', 'HTTP server, API run, idempotency key'), mod('execution/', 'c14n/1, bundle v1, supervisor, phân loại lỗi'))),
        arrow('Chạy worker bằng tiến trình con, không import gói SUT'),
        h('div', { class: 'wb-band sut' }, lbl('Gói SUT đầu tiên: path planner'), h('div', { class: 'wb-mods' }, mod('eval/', 'ResolvedCase, checksum, live, runner, suite, golden'), mod('sim/', 'Harness 1 ms, mô hình xe, cảm biến, lỗi'), mod('benchmark/', 'Kịch bản, lỗi, suite'), mod('adapters/sil', 'Nạp hai thư viện bằng ctypes'), mod('planner/', 'C11, pp_lcc và pp_lkaelk'), mod('interfaces/', 'Hợp đồng dữ liệu')))),
      h('p', { class: 'wb-small', style: 'padding-top:12px' }, 'Giữ bằng ', mono('tests/test_import_rules.py'), ': execution và workbench không được import gói SUT nào; web không đọc mã nguồn.'));
    const next = card('dash', h('div', { style: 'display:flex;gap:10px;align-items:center;padding-bottom:6px' }, lbl('SUT')),
      h('div', { class: 'wb-li', style: 'border-top:0' }, ico('i-check', 'ok-ico'), h('span', null, 'Path planner ', mono('pp_lcc + pp_lkaelk · C11 · ctypes'), ' · đang dùng')),
      h('div', { class: 'wb-li' }, ico('i-wait', 'dim'), h('span', null, 'Gói SUT thứ hai, ví dụ ACC, trên cùng lõi (backlog)')),
      h('div', { class: 'wb-li' }, ico('i-wait', 'dim'), h('span', null, 'Hướng dẫn "thêm SUT mới"')),
      h('div', { class: 'wb-li' }, ico('i-wait', 'dim'), h('span', null, 'Tách ', mono('interfaces.Received'), ' khỏi ', mono('sim/runtime'), ' (backlog)')));
    const ci = card('', lbl('CI'),
      h('div', { class: 'wb-li', style: 'border-top:0' }, ico('i-wait', 'dim'), h('span', null, 'Chưa chạy trên GitHub: ', mono('.github/workflows/tests.yml'), ', chạy mỗi lần push')),
      ...[['Build hai thư viện planner', 'cmake pp_lcc pp_lkaelk'], ['Toàn bộ test, gồm quy tắc import', 'pytest -q'], ['Conformance B0', 'eval.conformance'], ['Ghi golden rồi kiểm lại', 'eval.golden record, check'], ['Selfcheck, bấm tay', 'eval.selfcheck']].map(([t, d]) => h('div', { class: 'wb-li' }, ico('i-check', 'ok-ico'), h('div', { style: 'flex:1;min-width:0;display:flex;flex-direction:column;gap:3px' }, h('span', null, t), h('code', null, d)))));
    return page(head('Nền tảng', 'Cách hệ thống được xây: lõi thực thi chung không biết gì về path planner, gói SUT cắm vào lõi, ranh giới được test giữ.'),
      h('div', { class: 'wb-cols' }, h('div', { class: 'a' }, diagram), h('div', { class: 'b' }, next, ci)));
  }

  WB.views.suite = suiteView;
  WB.views.tincay = trustView;
  WB.views.nentang = platformView;
})();
