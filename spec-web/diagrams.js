// Sơ đồ trên bản đồ, vẽ từ bảng trong tài liệu kỹ thuật, theo khung hồ sơ phê duyệt của R79 Annex 6.
// File này không giữ dữ liệu riêng: sửa bảng trong tài liệu thì sơ đồ đổi theo.
//   sequence : Software Architectural Design, planner-sequence (cột #, Lúc, Từ → tới, Nội dung, Requirement) và dòng **Deadline.**
//   latency  : Software Architectural Design, latency-chain (cột #, Đoạn, Xấu nhất (ms), Gây ra, Bù); dòng có "song song" là chuỗi song song
//   states   : Software Architectural Design, arbitration-states (cột Sự kiện, Đang ở …, Requirement)
//   modes    : ADAS Function Specification, adas-modes (cột Từ, Tới, Khi, Chức năng)
//   curve    : Software Architectural Design, curve-strategy (cột Pha, Bắt đầu khi, Tốc độ, Path planner, Khối dọc, Requirement)
//   limits   : Software Architectural Design, design-limits (cột Chức năng, a_y, a_y thêm vào, Jerk) và dòng "Tốc độ" ở adas-availability
//   ladder   : Software Architectural Design, degradation (cột Bậc, Khi, Hệ thống làm gì, Chức năng còn, Tài xế, Requirement)
(function (root) {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var C = {
    text: "#1D1D1F", soft: "#6E6E73", faint: "#86868B", line: "#D2D2D7", fill: "#F5F5F7",
    violet: "#5B3DF5", violetTint: "#5B3DF51F", teal: "#0F7B6C", tealTint: "#0F7B6C26",
    gray: "#86868B", grayTint: "#86868B26", amber: "#B25000"
  };
  var CHAR = 6.6; // bề rộng ước lượng của một ký tự cỡ 12 px

  function node(tag, attrs, parent, text) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { if (attrs[k] != null) n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    if (parent) parent.appendChild(n);
    return n;
  }
  // Lỗi mang câu gốc tiếng Việt và giá trị riêng, để render() dịch bằng tr().
  function fail(message, values) {
    var err = new Error(message);
    err.key = message;
    err.values = values;
    return err;
  }
  function tip(parent, text) { node("title", {}, parent, text); }
  function plain(s) { return String(s || "").replace(/\*\*/g, "").replace(/`/g, "").trim(); }
  function cellsOf(line) {
    return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(function (c) { return c.trim(); });
  }

  function wrap(text, maxChars, maxLines) {
    var words = plain(text).split(/\s+/), lines = [], cur = "";
    words.forEach(function (w) {
      if (!cur) cur = w;
      else if ((cur + " " + w).length <= maxChars) cur += " " + w;
      else { lines.push(cur); cur = w; }
    });
    if (cur) lines.push(cur);
    if (maxLines && lines.length > maxLines) {
      lines = lines.slice(0, maxLines);
      lines[maxLines - 1] = lines[maxLines - 1].replace(/.{0,2}$/, "") + "…";
    }
    return lines;
  }
  function multiline(parent, x, y, lines, attrs, lineHeight) {
    var t = node("text", Object.assign({ x: x, y: y }, attrs), parent);
    lines.forEach(function (l, i) { node("tspan", { x: x, dy: i ? lineHeight || 14 : 0 }, t, l); });
    return t;
  }

  // Các bảng trong mục có ID cho trước, tính tới tiêu đề kế tiếp.
  function section(md, id) {
    var lines = md.split("\n"), start = -1, i;
    for (i = 0; i < lines.length; i++) {
      if (/^#{1,6} /.test(lines[i]) && lines[i].indexOf("{#" + id + "}") >= 0) { start = i; break; }
    }
    if (start < 0) return null;
    var tables = [], cur = null, end = lines.length;
    for (i = start + 1; i < lines.length; i++) {
      var l = lines[i];
      if (/^#{1,6} /.test(l)) { end = i; break; }
      if (l.charAt(0) === "|") {
        if (/^\|[\s|:-]+\|$/.test(l)) continue;
        if (!cur) { cur = { header: cellsOf(l), rows: [] }; tables.push(cur); }
        else cur.rows.push(cellsOf(l));
      } else if (cur) cur = null;
    }
    return { tables: tables, text: lines.slice(start + 1, end).join("\n") };
  }
  function column(table, name) {
    var i = table.header.indexOf(name);
    if (i < 0) throw fail("Bảng thiếu cột \"{name}\"", { name: name });
    return i;
  }
  function svgRoot(w, h, label) {
    var s = node("svg", { viewBox: "0 0 " + w + " " + h, width: w, height: h, role: "img", "aria-label": label,
      "font-family": "Inter, -apple-system, sans-serif", "font-size": 12 });
    var defs = node("defs", {}, s);
    [["arrow", C.violet], ["arrow-gray", C.gray]].forEach(function (m) {
      var mk = node("marker", { id: m[0], viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" }, defs);
      node("path", { d: "M1 1L9 5L1 9z", fill: m[1] }, mk);
    });
    var hatch = node("pattern", { id: "hatch", width: 6, height: 6, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, defs);
    node("rect", { width: 6, height: 6, fill: C.fill }, hatch);
    node("line", { x1: 0, y1: 0, x2: 0, y2: 6, stroke: C.faint, "stroke-width": 2 }, hatch);
    return s;
  }
  function legend(svg, x, y, items) {
    var cx = x;
    items.forEach(function (it) {
      var g = node("g", { transform: "translate(" + cx + "," + y + ")" }, svg);
      if (it.kind === "line") node("line", { x1: 0, y1: 0, x2: 28, y2: 0, stroke: it.color, "stroke-width": 2, "stroke-dasharray": it.dash }, g);
      else node("rect", { x: 0, y: -7, width: 28, height: 14, rx: 3, fill: it.fill, stroke: it.stroke || "none", "stroke-dasharray": it.dash }, g);
      node("text", { x: 36, y: 4, fill: C.soft }, g, it.text);
      cx += 36 + it.text.length * CHAR + 28;
    });
  }

  // ---------- Tuần tự một chu kỳ ----------
  function sequence(sec, opts, tr) {
    var t = sec.tables[0];
    if (!t) throw fail("Mục {id} không có bảng", { id: opts.section });
    var iNo = column(t, "#"), iAt = column(t, "Lúc"), iFT = column(t, "Từ → tới"), iTx = column(t, "Nội dung"),
      iReq = column(t, "Requirement");
    var steps = t.rows.map(function (r, i) {
      var ft = plain(r[iFT]).split(" → ");
      var labels = t.labels[i];
      return { no: plain(r[iNo]), at: plain(labels[iAt]), from: ft[0], to: ft[1] || ft[0], text: plain(labels[iTx]),
        req: plain(labels[iReq]), later: /^Sau\b/.test(plain(r[iAt])) };
    });
    var lanes = (opts.lanes || []).filter(function (n) {
      return steps.some(function (s) { return s.from === n || s.to === n; });
    });
    steps.forEach(function (s) { [s.from, s.to].forEach(function (n) { if (lanes.indexOf(n) < 0) lanes.push(n); }); });
    var own = opts.own || ["Planner"];

    // **Deadline.** Gửi xong bước a đến b trước t0 + X.
    var dl = /\*\*Deadline\.\*\*([^\n]*)/.exec(sec.text), deadline = null;
    if (dl) {
      var body = plain(dl[1]);
      var when = /trước (t0 \+ [^\s.,;]+)/.exec(body), range = /bước (\d+) đến (\d+)/.exec(body);
      if (when) deadline = { when: when[1], first: range ? range[1] : null, after: range ? range[2] : null };
    }

    var LEFT = 132, LANE = 156, TOP = 70, GAP = deadline ? 34 : 0;
    var W = LEFT + lanes.length * LANE + 16;
    var laneX = function (name) { return LEFT + lanes.indexOf(name) * LANE + LANE / 2; };
    // Chiều cao mỗi hàng theo số dòng chữ của nội dung.
    steps.forEach(function (s) {
      if (s.from === s.to) s.lines = wrap(s.text, 34, 4);
      else s.lines = wrap(s.text, Math.max(14, Math.floor((Math.abs(laneX(s.to) - laneX(s.from)) - 12) / CHAR)), 4);
      s.h = Math.max(54, 26 + s.lines.length * 14);
    });
    var H = TOP + steps.reduce(function (a, s) { return a + s.h; }, 0) + GAP + 56;
    var svg = svgRoot(W, H, tr("Tuần tự trong một chu kỳ"));

    lanes.forEach(function (name, i) {
      var x = LEFT + i * LANE, mine = own.indexOf(name) >= 0;
      node("rect", { x: x + 8, y: 8, width: LANE - 16, height: 46, rx: 10, fill: mine ? C.violetTint : C.fill,
        stroke: mine ? C.violet : C.line }, svg);
      var lines = wrap(tr(name), 20, 2);
      multiline(svg, x + LANE / 2, lines.length > 1 ? 27 : 35, lines,
        { "text-anchor": "middle", "font-weight": 600, fill: C.text }, 14);
      node("line", { x1: x + LANE / 2, y1: 54, x2: x + LANE / 2, y2: H - 44, stroke: C.line, "stroke-dasharray": "3 5" }, svg);
    });

    var y0 = TOP;
    steps.forEach(function (s) {
      var y = y0 + s.h - 18, color = s.later ? C.gray : C.violet, g = node("g", {}, svg);
      tip(g, "#" + s.no + " · " + s.at + " · " + tr(s.from) + (s.to !== s.from ? " → " + tr(s.to) : "") + "\n" + s.text +
        "\nRequirement: " + s.req);
      node("circle", { cx: 16, cy: y - 4, r: 11, fill: color }, g);
      node("text", { x: 16, y: y, "text-anchor": "middle", fill: "#FFFFFF", "font-weight": 600, "font-size": 11 }, g, s.no);
      multiline(g, 34, y - 4, wrap(s.at, 14, 2), { fill: C.soft, "font-size": 11 }, 13);
      if (s.from === s.to) {
        var x = laneX(s.from), top = y0 + 8, hh = s.h - 16;
        node("rect", { x: x - 8, y: top, width: 16, height: hh, rx: 4, fill: C.violetTint, stroke: color }, g);
        multiline(g, x + 16, top + hh / 2 - (s.lines.length - 1) * 7 + 4, s.lines, { fill: C.text }, 14);
      } else {
        var x1 = laneX(s.from), x2 = laneX(s.to);
        node("line", { x1: x1, y1: y, x2: x2 + (x2 > x1 ? -2 : 2), y2: y, stroke: color, "stroke-width": 2,
          "stroke-dasharray": s.later ? "6 4" : null, "marker-end": "url(#" + (s.later ? "arrow-gray" : "arrow") + ")" }, g);
        multiline(g, (x1 + x2) / 2, y - 8 - (s.lines.length - 1) * 14, s.lines, { "text-anchor": "middle", fill: C.text }, 14);
      }
      y0 += s.h;
      if (deadline && s.no === deadline.after) {
        var yd = y0 + GAP / 2 - 4, dg = node("g", {}, svg);
        var label = "◆ " + tr("Hạn gửi") + " · " + tr("bước {a}–{b} gửi xong trước {when}", { a: deadline.first, b: deadline.after, when: deadline.when });
        tip(dg, label);
        node("line", { x1: LEFT, y1: yd, x2: W - 16, y2: yd, stroke: C.amber, "stroke-width": 1.5, "stroke-dasharray": "2 4" }, dg);
        node("text", { x: LEFT + 6, y: yd - 6, fill: C.amber, "font-weight": 600 }, dg, label);
        y0 += GAP;
      }
    });
    legend(svg, LEFT, H - 18, [
      { kind: "line", color: C.violet, text: tr("trong chu kỳ") },
      { kind: "line", color: C.gray, dash: "6 4", text: tr("dùng ở chu kỳ sau") },
      { kind: "box", fill: C.violetTint, stroke: C.violet, text: tr("khối của Path Planner") }
    ]);
    return svg;
  }

  // ---------- Chuỗi trễ ----------
  function latency(sec, opts, tr) {
    var t = sec.tables.filter(function (x) { return x.header.indexOf("Xấu nhất (ms)") >= 0; })[0];
    if (!t) throw fail("Mục {id} không có bảng có cột \"Xấu nhất (ms)\"", { id: opts.section });
    var iNo = column(t, "#"), iName = column(t, "Đoạn"), iMs = column(t, "Xấu nhất (ms)"), iBy = column(t, "Gây ra"),
      iBu = column(t, "Bù");
    var rows = t.rows.map(function (r, i) {
      var labels = t.labels[i], v = plain(r[iMs]), lv = plain(labels[iMs]);
      var num = /^\d+(?:[.,]\d+)?/.exec(v), note = /\(([^)]*)\)\s*$/.exec(lv);
      return { no: plain(r[iNo]), name: plain(labels[iName]).replace(/,\s*(?:song song|in parallel)$/i, ""),
        parallel: /song song/i.test(plain(r[iName])),
        ms: num ? parseFloat(num[0].replace(",", ".")) : 0, known: !!num, unknown: /\?|chưa biết/.test(v),
        raw: lv, note: note ? note[1] : "", by: plain(labels[iBy]), bu: plain(r[iBu]), compensation: plain(labels[iBu]) };
    });
    rows.forEach(function (r) {
      var like = /^Như dòng (\d+)/.exec(r.bu);
      var src = like && rows.filter(function (x) { return x.no === like[1]; })[0];
      if (src) { r.bu = src.bu; r.compensation = src.compensation; }
      r.who = /^Planner/.test(r.bu) ? "planner" : /Lateral Controller/.test(r.bu) ? "controller" : "none";
    });
    var main = rows.filter(function (r) { return !r.parallel; }), parallel = rows.filter(function (r) { return r.parallel; });
    var t0 = 0;
    main.forEach(function (r) { r.start = t0; t0 += r.ms; });
    var total = t0, boundary = 0, sum = { planner: 0, controller: 0, none: 0 };
    for (var i = 0; i < main.length && main[i].who === "planner"; i++) boundary = main[i].start + main[i].ms;
    main.forEach(function (r) { sum[r.who] += r.ms; });
    // Chuỗi song song là tuổi của input khi planner đọc ở t0, nên kết thúc tại t0.
    parallel.forEach(function (r) { r.start = boundary - r.ms; r.endAtT0 = true; });
    var missing = main.filter(function (r) { return !r.known; }).map(function (r) { return r.no; });

    var LABEL = 300, CHART = 620, ROW = 34, TOP = 70;
    var maxMs = Math.ceil(Math.max(total, 1) / 50) * 50, px = CHART / maxMs;
    var nRows = main.length + 1 + (parallel.length ? parallel.length + 1 : 0);
    var W = LABEL + CHART + 180, H = TOP + nRows * ROW + 62;
    var svg = svgRoot(W, H, tr("Chuỗi trễ từ cảm biến tới bánh xe"));
    var fills = { planner: [C.violetTint, C.violet], controller: [C.tealTint, C.teal], none: [C.grayTint, C.gray] };

    for (var ms = 0; ms <= maxMs; ms += 50) {
      var gx = LABEL + ms * px;
      node("line", { x1: gx, y1: TOP - 12, x2: gx, y2: H - 40, stroke: C.line, "stroke-dasharray": ms ? "2 4" : null }, svg);
      node("text", { x: gx, y: TOP - 18, "text-anchor": "middle", fill: C.soft, "font-size": 11 }, svg, ms + " ms");
    }

    function bar(r, y) {
      var g = node("g", {}, svg), f = fills[r.who];
      tip(g, r.no + ". " + r.name + "\n" + tr("Xấu nhất") + ": " + r.raw + "\n" + tr("Gây ra") + ": " + r.by +
        "\n" + tr("Bù") + ": " + r.compensation);
      multiline(g, 12, y + 4, wrap(r.no + "  " + r.name, 44, 1), { fill: C.text }, 14);
      var w = Math.max(r.ms * px, r.ms > 0 ? 3 : 0), x = LABEL + r.start * px, HW = 22;
      if (w) node("rect", { x: x, y: y - 9, width: w, height: 18, rx: 3, fill: f[0], stroke: f[1] }, g);
      var left = x, right = x + w;
      if (r.unknown) {
        // Phần chưa biết vẽ nối tiếp phía xa t0 của thanh.
        var hx = r.endAtT0 ? x - HW - (w ? 2 : 0) : right + (w ? 2 : 0);
        node("rect", { x: hx, y: y - 9, width: HW, height: 18, rx: 3, fill: "url(#hatch)", stroke: C.faint }, g);
        left = Math.min(left, hx); right = Math.max(right, hx + HW);
      }
      var value = r.known ? r.ms + " ms" + (r.unknown ? " + ?" : "") : tr("chưa biết");
      var tx = node("text", { x: right + 6, y: y + 4, fill: C.text, "font-size": 11, "font-weight": 600 }, g, value);
      if (r.note) node("tspan", { fill: C.soft, "font-weight": 400 }, tx, "  " + r.note);
    }

    var y = TOP + ROW / 2;
    main.forEach(function (r) { bar(r, y); y += ROW; });

    var tg = node("g", {}, svg);
    tip(tg, tr("Planner bù {a} ms đầu; Lateral Controller bù {b} ms sau", { a: sum.planner, b: sum.controller }));
    node("text", { x: 12, y: y + 4, fill: C.text, "font-weight": 700 }, tg,
      tr("Tổng") + " " + total + " ms" + (missing.length ? " · " + tr("chưa kể dòng {rows}", { rows: missing.join(", ") }) : ""));
    var segs = [["planner", sum.planner], ["controller", sum.controller], ["none", sum.none]], sx = LABEL;
    segs.forEach(function (s) {
      if (!s[1]) return;
      node("rect", { x: sx, y: y - 9, width: s[1] * px, height: 18, fill: fills[s[0]][1] }, tg);
      if (s[1] * px > 40) node("text", { x: sx + s[1] * px / 2, y: y + 4, "text-anchor": "middle", fill: "#FFFFFF",
        "font-weight": 600, "font-size": 11 }, tg, s[1] + " ms");
      sx += s[1] * px;
    });

    var bx = LABEL + boundary * px;
    node("line", { x1: bx, y1: TOP - 6, x2: bx, y2: H - 40, stroke: C.violet, "stroke-width": 1.5, "stroke-dasharray": "5 3" }, svg);
    node("text", { x: bx + 6, y: TOP + 2, fill: C.violet, "font-weight": 600, "font-size": 11 }, svg,
      "▲ t0 = " + tr("stamp của path") + " · " + boundary + " ms");
    y += ROW;
    if (parallel.length) {
      node("text", { x: 12, y: y + 4, fill: C.soft, "font-weight": 600 }, svg, tr("Chuỗi song song: tuổi của input lúc planner đọc ở t0"));
      y += ROW;
      parallel.forEach(function (r) { bar(r, y); y += ROW; });
    }
    legend(svg, 12, H - 16, [
      { kind: "box", fill: C.violetTint, stroke: C.violet, text: tr("Planner bù") },
      { kind: "box", fill: C.tealTint, stroke: C.teal, text: tr("Lateral Controller bù") },
      { kind: "box", fill: C.grayTint, stroke: C.gray, text: tr("không bù") },
      { kind: "box", fill: "url(#hatch)", stroke: C.faint, text: tr("chưa biết") }
    ]);
    return svg;
  }

  // ---------- Arbitration state ----------
  function states(sec, opts, tr) {
    var t = sec.tables[0];
    if (!t) throw fail("Mục {id} không có bảng", { id: opts.section });
    var iEv = column(t, "Sự kiện"), cols = [];
    t.header.forEach(function (h, i) { var m = /^Đang ở (\S+)/.exec(h); if (m) cols.push({ i: i, name: m[1] }); });
    if (!cols.length) throw fail("Bảng thiếu các cột \"Đang ở …\"");
    var names = cols.map(function (c) { return c.name; });
    var pattern = new RegExp("(?:→|không thì)\\s*(" + names.join("|") + ")\\b", "g");
    var likeRe = new RegExp("^Như (" + names.join("|") + "|dòng trên)\\b");
    var rowRe = /như dòng "([^"]+)"/i;
    var evRaw = t.rows.map(function (r) { return plain(r[iEv]); });

    function targets(text) {
      var out = [], m;
      pattern.lastIndex = 0;
      while ((m = pattern.exec(plain(text)))) if (out.indexOf(m[1]) < 0) out.push(m[1]);
      return out;
    }
    var resolved = []; // resolved[row][state] = [đích]
    t.rows.forEach(function (r, ri) {
      var raw = {};
      cols.forEach(function (c) { raw[c.name] = plain(r[c.i] || ""); });
      var res = {};
      // Đọc một ô theo cột name. "Như HWA" là dùng chữ của ô HWA nhưng hiểu cho cột name;
      // "Như dòng trên" và như dòng "X" (dòng gần nhất phía trên có sự kiện chứa X) lấy kết quả của dòng đó, cùng cột.
      function read(text, name, seen) {
        var list = targets(text);
        var like = likeRe.exec(text);
        if (like && like[1] === "dòng trên") list = ((resolved[ri - 1] || {})[name] || []).concat(list);
        else if (like && !seen[like[1]]) {
          seen[like[1]] = true;
          list = read(raw[like[1]], name, seen).concat(list);
        }
        var ref = rowRe.exec(text);
        if (ref) {
          for (var k = ri - 1; k >= 0; k--) if (evRaw[k].indexOf(ref[1]) >= 0) { list = resolved[k][name].concat(list); break; }
        }
        return list;
      }
      names.forEach(function (n) {
        var seen = {};
        seen[n] = true;
        res[n] = read(raw[n], n, seen).filter(function (x, i, a) { return x !== n && a.indexOf(x) === i; });
      });
      resolved.push(res);
    });

    // Sự kiện đưa mọi trạng thái khác về cùng một đích thì vẽ một lần, "từ mọi trạng thái".
    var globals = [], edges = {}, moves = [];
    resolved.forEach(function (res, ri) {
      var list = [];
      names.forEach(function (from) { res[from].forEach(function (to) { list.push({ from: from, to: to }); }); });
      moves.push(list.length > 0);
      var tos = list.map(function (x) { return x.to; }).filter(function (v, i, a) { return a.indexOf(v) === i; });
      if (tos.length === 1) {
        var others = names.filter(function (n) { return n !== tos[0]; });
        var froms = list.map(function (x) { return x.from; });
        if (others.length >= 3 && others.every(function (n) { return froms.indexOf(n) >= 0; })) {
          globals.push({ to: tos[0], event: ri + 1 });
          return;
        }
      }
      list.forEach(function (x) {
        var key = x.from + ">" + x.to;
        (edges[key] = edges[key] || { from: x.from, to: x.to, events: [] });
        if (edges[key].events.indexOf(ri + 1) < 0) edges[key].events.push(ri + 1);
      });
    });

    var ladder = names.slice().reverse(); // cột cuối (ưu tiên cao nhất) ở trên cùng
    var edgeList = Object.keys(edges).map(function (k) { return edges[k]; });
    // Cung cùng phía, cùng khoảng cách thì dàn ra xa dần để không chồng nhau.
    var slots = {};
    edgeList.forEach(function (e) {
      var a = ladder.indexOf(e.from), b = ladder.indexOf(e.to);
      e.up = b < a; e.d = Math.abs(a - b);
      var key = (e.up ? "u" : "d") + e.d;
      e.slot = slots[key] = (slots[key] == null ? 0 : slots[key] + 1);
    });
    var reachOf = function (e) {
      var below = edgeList.filter(function (x) { return x.up === e.up && x.d < e.d; })
        .map(function (x) { return x.d; }).filter(function (v, i, a) { return a.indexOf(v) === i; });
      var lanesBelow = below.reduce(function (acc, d) {
        return acc + edgeList.filter(function (x) { return x.up === e.up && x.d === d; }).length;
      }, 0);
      return NODE_W / 2 + 40 + (lanesBelow + e.slot) * 46;
    };

    var byTarget = {};
    globals.forEach(function (gl) { (byTarget[gl.to] = byTarget[gl.to] || []).push(gl); });
    var STUB = 64, intoTop = !!byTarget[ladder[0]], intoBottom = Object.keys(byTarget).some(function (n) { return n !== ladder[0]; });
    var NODE_W = 132, NODE_H = 46, STEP = 132;
    var maxReach = { u: 0, d: 0 };
    edgeList.forEach(function (e) { var r = reachOf(e); e.reach = r; maxReach[e.up ? "u" : "d"] = Math.max(maxReach[e.up ? "u" : "d"], r); });
    var CX = Math.max(maxReach.u, 200) + 40, TOP = intoTop ? 56 + STUB + 10 : 56;
    var events = t.labels.map(function (r) { return plain(r[iEv]); });
    var bottom = TOP + (ladder.length - 1) * STEP + NODE_H;
    var LEG_X = CX + Math.max(maxReach.d, 200) + 70, W = LEG_X + 380;
    var H = Math.max(bottom + (intoBottom ? STUB + 30 : 0) + 50, 60 + events.length * 34 + 40);
    var svg = svgRoot(W, H, tr("Arbitration state"));
    var yOf = function (n) { return TOP + ladder.indexOf(n) * STEP + NODE_H / 2; };

    node("text", { x: 12, y: 24, fill: C.soft, "font-size": 11 }, svg, "◀ " + tr("sang chức năng ưu tiên cao hơn"));
    node("text", { x: LEG_X - 40, y: 24, fill: C.soft, "font-size": 11, "text-anchor": "end" }, svg, tr("sang chức năng ưu tiên thấp hơn") + " ▶");

    Object.keys(byTarget).forEach(function (to) {
      var list = byTarget[to], fromAbove = to === ladder[0];
      var edgeY = yOf(to) + (fromAbove ? -NODE_H / 2 : NODE_H / 2), farY = edgeY + (fromAbove ? -STUB : STUB);
      list.forEach(function (gl, i) {
        // Dàn mũi tên trong bề ngang của ô đích; nhãn nằm phía ngoài của mũi tên.
        var off = list.length === 1 ? 0 : -NODE_W / 2 + 22 + i * (NODE_W - 44) / (list.length - 1);
        var x = CX + off, left = list.length > 1 && i < list.length / 2, g = node("g", {}, svg);
        tip(g, tr("Từ mọi trạng thái") + " → " + gl.to + "\n" + gl.event + ". " + events[gl.event - 1]);
        node("line", { x1: x, y1: farY, x2: x, y2: edgeY + (fromAbove ? -3 : 3), stroke: C.violet, "stroke-width": 2,
          "marker-end": "url(#arrow)" }, g);
        node("text", { x: x + (left ? -8 : 8), y: (farY + edgeY) / 2 + 4, "text-anchor": left ? "end" : "start",
          fill: C.violet, "font-weight": 600, "font-size": 11 }, g, gl.event + " · " + tr("từ mọi trạng thái"));
      });
    });

    edgeList.forEach(function (e) {
      var side = e.up ? -1 : 1, lift = 6 + e.slot * 5;
      var x0 = CX + side * NODE_W / 2, y0 = yOf(e.from) + (e.up ? -lift : lift), y1 = yOf(e.to) + (e.up ? lift : -lift);
      var xc = CX + side * e.reach * 1.33, g = node("g", {}, svg);
      tip(g, e.from + " → " + e.to + "\n" + e.events.map(function (n) { return n + ". " + events[n - 1]; }).join("\n"));
      node("path", { d: "M" + x0 + " " + y0 + " C" + xc + " " + y0 + " " + xc + " " + y1 + " " + (x0 + side * 2) + " " + y1,
        fill: "none", stroke: C.violet, "stroke-width": 2, "marker-end": "url(#arrow)" }, g);
      var lx = CX + side * e.reach, ly = (y0 + y1) / 2;
      var label = e.events.join(", ");
      node("rect", { x: lx - label.length * 3.6 - 6, y: ly - 10, width: label.length * 7.2 + 12, height: 20, rx: 10, fill: "#FFFFFF", stroke: C.violet }, g);
      node("text", { x: lx, y: ly + 4, "text-anchor": "middle", fill: C.violet, "font-weight": 600, "font-size": 11 }, g, label);
    });

    ladder.forEach(function (n) {
      var y = yOf(n);
      node("rect", { x: CX - NODE_W / 2, y: y - NODE_H / 2, width: NODE_W, height: NODE_H, rx: 14,
        fill: n === "NONE" ? C.fill : C.violetTint, stroke: n === "NONE" ? C.line : C.violet, "stroke-width": 1.5 }, svg);
      node("text", { x: CX, y: y + 5, "text-anchor": "middle", "font-weight": 700, "font-size": 15, fill: C.text }, svg, n);
    });

    node("text", { x: LEG_X, y: 24, "font-weight": 700, fill: C.text }, svg, tr("Sự kiện"));
    events.forEach(function (ev, i) {
      var lines = wrap((i + 1) + ". " + ev, 54, 2);
      if (!moves[i]) lines[lines.length - 1] += " " + tr("(không đổi trạng thái)");
      multiline(svg, LEG_X, 50 + i * 34, lines, { fill: moves[i] ? C.text : C.faint, "font-size": 11.5 }, 13);
    });
    legend(svg, 12, H - 18, [
      { kind: "box", fill: C.violetTint, stroke: C.violet, text: tr("chức năng đang lái") },
      { kind: "line", color: C.violet, text: tr("số trên cung là sự kiện gây chuyển") }
    ]);
    return svg;
  }

  // ---------- Chung cho các sơ đồ mô tả chức năng ----------
  var W_FN = 760;
  function num(text) {
    var m = /(\d+(?:,\d+)?)/.exec(plain(text));
    return m ? parseFloat(m[1].replace(",", ".")) : null;
  }
  // Điểm trên mép hộp b (x, y, w, h) theo hướng (ux, uy) từ tâm, lùi thêm margin.
  function rim(b, ux, uy, margin) {
    var tx = ux ? (b.w / 2) / Math.abs(ux) : Infinity, ty = uy ? (b.h / 2) / Math.abs(uy) : Infinity;
    var t = Math.min(tx, ty) + (margin || 0);
    return { x: b.x + b.w / 2 + ux * t, y: b.y + b.h / 2 + uy * t };
  }
  function badge(parent, x, y, text, fill) {
    var w = Math.max(20, text.length * 6.5 + 10);
    node("rect", { x: x - w / 2, y: y - 9, width: w, height: 18, rx: 9, fill: fill }, parent);
    node("text", { x: x, y: y + 4, "text-anchor": "middle", fill: "#FFFFFF", "font-weight": 600, "font-size": 11 }, parent, text);
  }
  function fnColor(fns) {
    var hwa = /HWA/.test(fns), other = /LKA|ELK/.test(fns);
    return hwa && other ? C.gray : hwa ? C.violet : C.teal;
  }

  // ---------- Trạng thái của từng chức năng ----------
  function modes(sec, opts, tr) {
    var t = sec.tables[0];
    if (!t) throw fail("Mục {id} không có bảng", { id: opts.section });
    var iFrom = column(t, "Từ"), iTo = column(t, "Tới"), iWhen = column(t, "Khi"), iFn = column(t, "Chức năng");
    var rows = t.rows.map(function (r, i) {
      return { from: plain(r[iFrom]), to: plain(r[iTo]), when: plain(t.labels[i][iWhen]), fns: plain(r[iFn]) };
    });
    var ANY = "Mọi trạng thái";
    var POS = { OFF: [20, 44], STANDBY: [300, 44], UNAVAILABLE: [580, 44], REQUEST: [300, 214], FAULT: [580, 290] };
    var boxes = {};
    function box(name) {
      if (!boxes[name]) {
        var p = POS[name] || [20, 268];
        boxes[name] = { x: p[0], y: p[1], w: 150, h: 46, name: name };
      }
      return boxes[name];
    }
    rows.forEach(function (r) { if (r.from !== ANY) box(r.from); box(r.to); });
    // Gom các dòng cùng cặp trạng thái vào một cung.
    var arcs = [];
    rows.forEach(function (r, i) {
      var a = arcs.filter(function (x) { return x.from === r.from && x.to === r.to; })[0];
      if (!a) { a = { from: r.from, to: r.to, nos: [], fns: "" }; arcs.push(a); }
      a.nos.push(i + 1);
      a.fns += " " + r.fns;
    });
    var listTop = 366, lines = rows.map(function (r, i) {
      return wrap((i + 1) + ". " + tr(r.from) + " → " + tr(r.to) + " (" + r.fns + "): " + r.when, 112, 2);
    });
    var H = listTop + lines.reduce(function (s, l) { return s + l.length * 14 + 6; }, 0) + 40;
    var svg = svgRoot(W_FN, H, tr("Trạng thái của từng chức năng"));

    arcs.forEach(function (a) {
      var b = boxes[a.to], color = fnColor(a.fns), g = node("g", {}, svg), s, e, at = 0.5;
      tip(g, a.nos.join(", ") + " · " + tr(a.from) + " → " + tr(a.to));
      if (a.from === ANY) {
        e = { x: b.x, y: b.y + b.h / 2 };
        s = { x: b.x - 150, y: e.y };
        node("text", { x: s.x - 4, y: s.y + 4, "text-anchor": "end", fill: C.soft, "font-size": 11 }, g, tr("từ mọi trạng thái"));
      } else {
        var f = boxes[a.from];
        var ax = f.x + f.w / 2, ay = f.y + f.h / 2, bx = b.x + b.w / 2, by = b.y + b.h / 2;
        var L = Math.hypot(bx - ax, by - ay), ux = (bx - ax) / L, uy = (by - ay) / L;
        var paired = arcs.some(function (x) { return x.from === a.to && x.to === a.from; });
        var off = paired ? 9 : 0;
        if (paired) at = 0.35;
        s = rim(f, ux, uy, 4); e = rim(b, -ux, -uy, 8);
        s.x += -uy * off; s.y += ux * off; e.x += -uy * off; e.y += ux * off;
      }
      node("line", { x1: s.x, y1: s.y, x2: e.x, y2: e.y, stroke: color, "stroke-width": 2,
        "stroke-dasharray": a.from === ANY ? "5 4" : null, "marker-end": "url(#" + (color === C.gray ? "arrow-gray" : "arrow") + ")" }, g);
      badge(g, s.x + (e.x - s.x) * at, s.y + (e.y - s.y) * at, a.nos.join(","), color);
    });
    Object.keys(boxes).forEach(function (name) {
      var b = boxes[name], active = name === "REQUEST", fault = name === "FAULT";
      node("rect", { x: b.x, y: b.y, width: b.w, height: b.h, rx: 12,
        fill: active ? C.violetTint : fault ? "#B250001F" : C.fill, stroke: active ? C.violet : fault ? C.amber : C.line,
        "stroke-width": active ? 2 : 1 }, svg);
      node("text", { x: b.x + b.w / 2, y: b.y + 28, "text-anchor": "middle", "font-weight": 700, fill: C.text }, svg, tr(name));
    });
    node("text", { x: 515, y: 32, "text-anchor": "middle", fill: C.faint, "font-size": 11 }, svg, tr("standby mode"));
    node("text", { x: 375, y: 276, "text-anchor": "middle", fill: C.violet, "font-size": 11 }, svg, tr("active mode"));
    node("text", { x: 95, y: 32, "text-anchor": "middle", fill: C.faint, "font-size": 11 }, svg, tr("off mode"));

    var y = listTop;
    rows.forEach(function (r, i) {
      multiline(svg, 12, y, lines[i], { fill: C.text, "font-size": 11.5 }, 14);
      y += lines[i].length * 14 + 6;
    });
    legend(svg, 12, H - 16, [
      { kind: "line", color: C.violet, text: tr("chỉ HWA") },
      { kind: "line", color: C.teal, text: tr("LKA, ELK") },
      { kind: "line", color: C.gray, text: tr("mọi chức năng") }
    ]);
    return svg;
  }

  // ---------- Chiến lược tốc độ trong cua ----------
  function curve(sec, opts, tr) {
    var t = sec.tables[0];
    if (!t) throw fail("Mục {id} không có bảng", { id: opts.section });
    var cols = ["Pha", "Bắt đầu khi", "Tốc độ", "Path planner", "Khối dọc", "Requirement"].map(function (n) { return column(t, n); });
    var phases = t.rows.map(function (r, i) {
      var l = t.labels[i];
      return { name: plain(l[cols[0]]), when: plain(l[cols[1]]), speed: plain(r[cols[2]]), speedLabel: plain(l[cols[2]]),
        planner: plain(l[cols[3]]), lon: plain(l[cols[4]]), req: plain(l[cols[5]]) };
    });
    var LEFT = 92, n = phases.length, colW = (W_FN - LEFT) / n, chars = Math.floor((colW - 12) / 6.2);
    var rowsDef = [["when", tr("Bắt đầu khi")], ["planner", tr("Path planner")], ["lon", tr("Khối dọc")], ["req", tr("Requirement")]];
    var wrapped = phases.map(function (p) {
      var w = {};
      rowsDef.forEach(function (d) { w[d[0]] = wrap(p[d[0]], chars, 7); });
      return w;
    });
    var rowH = rowsDef.map(function (d) {
      return 18 + Math.max.apply(null, wrapped.map(function (w) { return w[d[0]].length; })) * 13;
    });
    var HEAD = 48, PLOT = 96, top = HEAD + PLOT + 14;
    var H = top + rowH.reduce(function (a, b) { return a + b; }, 0) + 36;
    var svg = svgRoot(W_FN, H, tr("Tốc độ và a_y khi vào cua"));

    phases.forEach(function (p, i) {
      var x = LEFT + i * colW;
      node("rect", { x: x + 2, y: 4, width: colW - 4, height: H - 40, rx: 8, fill: i % 2 ? "#FFFFFF" : C.fill }, svg);
      badge(svg, x + 16, 20, String(i + 1), C.violet);
      multiline(svg, x + 30, 24, wrap(p.name, chars - 4, 2), { "font-weight": 700, fill: C.text, "font-size": 12 }, 13);
    });
    // Đường v minh hoạ: Cao, Giảm, Thấp, Giữ, Tăng.
    var hi = HEAD + 18, lo = HEAD + PLOT - 18, level = hi, pts = [];
    phases.forEach(function (p, i) {
      var x0 = LEFT + i * colW + 6, x1 = LEFT + (i + 1) * colW - 6, k = p.speed.toLowerCase(), end = level;
      if (/^cao/.test(k)) { level = hi; end = hi; }
      else if (/^giảm/.test(k)) end = lo;
      else if (/^thấp/.test(k)) { level = lo; end = lo; }
      else if (/^tăng/.test(k)) end = hi;
      pts.push(x0 + "," + level, x1 + "," + end);
      level = end;
      node("text", { x: (x0 + x1) / 2, y: HEAD + PLOT + 4, "text-anchor": "middle", fill: C.soft, "font-size": 11 }, svg, p.speedLabel);
    });
    node("polyline", { points: pts.join(" "), fill: "none", stroke: C.violet, "stroke-width": 3, "stroke-linejoin": "round" }, svg);
    node("text", { x: 8, y: hi + 4, fill: C.soft, "font-size": 11 }, svg, tr("tốc độ"));
    node("text", { x: 8, y: hi + 18, fill: C.faint, "font-size": 10 }, svg, tr("(minh hoạ)"));

    var y = top;
    rowsDef.forEach(function (d, j) {
      node("line", { x1: 4, y1: y - 4, x2: W_FN - 4, y2: y - 4, stroke: C.line }, svg);
      multiline(svg, 8, y + 10, wrap(d[1], Math.floor((LEFT - 12) / 6.2)),
        { "font-weight": 600, fill: d[0] === "planner" ? C.violet : C.text, "font-size": 11.5 }, 13);
      phases.forEach(function (p, i) {
        multiline(svg, LEFT + i * colW + 8, y + 10, wrapped[i][d[0]],
          { fill: d[0] === "req" ? C.soft : C.text, "font-size": 11 }, 13);
      });
      y += rowH[j];
    });
    legend(svg, 12, H - 14, [
      { kind: "line", color: C.violet, text: tr("tốc độ xe, không theo tỉ lệ") },
      { kind: "box", fill: C.fill, text: tr("mỗi cột một pha") }
    ]);
    return svg;
  }

  // ---------- Dải tốc độ và giới hạn quyền lái ----------
  function limits(sec, opts, tr, extra) {
    var t = sec.tables[0];
    if (!t) throw fail("Mục {id} không có bảng", { id: opts.section });
    var iFn = column(t, "Chức năng"), iAy = column(t, "a_y"), iAdd = column(t, "a_y thêm vào"), iJ = column(t, "Jerk");
    var fns = t.rows.map(function (r, i) {
      var labels = t.labels[i];
      return { name: plain(r[iFn]), ay: num(r[iAy]), add: num(r[iAdd]), jerk: num(r[iJ]),
        ayText: plain(labels[iAy]), addText: plain(labels[iAdd]), jerkText: plain(labels[iJ]) };
    });
    // Dải tốc độ: dòng "Tốc độ" của bảng điều kiện khả dụng (ADAS Function Specification mục 7).
    var speedRow, speedLabels, speedTable;
    (extra[0]?.tables || []).forEach(function (tb) {
      tb.rows.forEach(function (r, i) {
        if (!speedRow && plain(r[0]) === "Tốc độ") {
          speedRow = r;
          speedLabels = tb.labels[i];
          speedTable = tb;
        }
      });
    });
    if (!speedRow) throw fail("Không thấy dòng \"Tốc độ\" trong mục {id}", { id: opts.extra?.[0]?.section || "?" });
    var speeds = {};
    fns.forEach(function (f) {
      var i = speedTable.header.indexOf(f.name);
      var text = i >= 0 ? plain(speedRow[i]) : "";
      var like = /^Như (\w+)/.exec(text);
      if (like && speeds[like[1]]) { speeds[f.name] = speeds[like[1]]; return; }
      var range = /(\d+)\s*[–-]\s*(\d+)\s*km\/h/.exec(text), from = /từ (\d+)\s*km\/h/.exec(text),
        hold = /giữ tới dưới (\d+)\s*km\/h/.exec(text), max = /tối đa (\d+)\s*km\/h/.exec(text);
      speeds[f.name] = {
        on: range ? +range[1] : from ? +from[1] : null, max: range ? +range[2] : max ? +max[1] : null,
        hold: hold ? +hold[1] : null, text: i >= 0 ? plain(speedLabels[i]) : ""
      };
    });

    var LEFT = 64, PW = W_FN - LEFT - 150, ROW = 34, top1 = 44;
    var top2 = top1 + fns.length * ROW + 70, H = top2 + fns.length * ROW + 64;
    var svg = svgRoot(W_FN, H, tr("Dải tốc độ và giới hạn quyền lái"));
    var number = new Intl.NumberFormat(opts.language || "vi");

    function axis(y0, max, step, unit, title) {
      node("text", { x: 4, y: y0 - 20, "font-weight": 700, fill: C.text }, svg, title);
      var yb = y0 + fns.length * ROW;
      for (var v = 0; v <= max; v += step) {
        var x = LEFT + v / max * PW;
        node("line", { x1: x, y1: y0 - 6, x2: x, y2: yb, stroke: C.line, "stroke-dasharray": v ? "2 4" : null }, svg);
        node("text", { x: x, y: yb + 14, "text-anchor": "middle", fill: C.soft, "font-size": 10.5 }, svg, number.format(v));
      }
      node("text", { x: LEFT + PW + 22, y: yb + 14, fill: C.soft, "font-size": 10.5 }, svg, unit);
    }
    axis(top1, 140, 20, "km/h", tr("Dải tốc độ hoạt động"));
    fns.forEach(function (f, i) {
      var s = speeds[f.name], y = top1 + i * ROW + 6, g = node("g", {}, svg), sx = function (v) { return LEFT + v / 140 * PW; };
      tip(g, f.name + ": " + s.text);
      node("text", { x: 4, y: y + 15, "font-weight": 600, fill: C.text }, g, f.name);
      if (s.on == null || s.max == null) return;
      if (s.hold != null && s.hold < s.on)
        node("rect", { x: sx(s.hold), y: y + 2, width: sx(s.on) - sx(s.hold), height: 18, rx: 4, fill: "url(#hatch)" }, g);
      node("rect", { x: sx(s.on), y: y + 2, width: sx(s.max) - sx(s.on), height: 18, rx: 4, fill: fnColor(f.name) }, g);
      node("text", { x: sx(s.max) + 6, y: y + 15, fill: C.soft, "font-size": 11 }, g,
        s.on + "–" + s.max + " km/h" + (s.hold != null && s.hold < s.on ? tr(", giữ tới {v}", { v: s.hold }) : ""));
    });
    var maxAy = 4.5;
    axis(top2, maxAy, 0.5, "m/s²", tr("Giới hạn a_y của path"));
    fns.forEach(function (f, i) {
      var y = top2 + i * ROW + 6, g = node("g", {}, svg), sx = function (v) { return LEFT + v / maxAy * PW; };
      tip(g, f.name + " · a_y " + f.ayText + " · " + tr("a_y thêm vào") + " " + f.addText + " · jerk " + f.jerkText);
      node("text", { x: 4, y: y + 15, "font-weight": 600, fill: C.text }, g, f.name);
      if (f.ay == null) return;
      node("rect", { x: LEFT, y: y + 2, width: sx(f.ay) - LEFT, height: 18, rx: 4, fill: fnColor(f.name), opacity: 0.35 }, g);
      if (f.add != null) node("rect", { x: LEFT, y: y + 6, width: sx(f.add) - LEFT, height: 10, rx: 3, fill: fnColor(f.name) }, g);
      var addNote = f.add != null ? "≤ " + number.format(f.add) : f.addText && f.addText !== "—" ? f.addText : null;
      var note = "≤ " + number.format(f.ay) + (addNote ? " · " + tr("thêm vào {value}", { value: addNote }) : "") +
        (f.jerk != null ? " · jerk ≤ " + number.format(f.jerk) + " m/s³" : "");
      node("text", { x: sx(f.ay) + 6, y: y + 15, fill: C.soft, "font-size": 11 }, g, note);
    });
    legend(svg, 12, H - 14, [
      { kind: "box", fill: C.violet, text: tr("kích hoạt được") },
      { kind: "box", fill: "url(#hatch)", text: tr("chỉ giữ, không kích hoạt mới") },
      { kind: "box", fill: C.gray, text: tr("vạch đậm: a_y thêm vào") }
    ]);
    return svg;
  }

  // ---------- Bậc suy giảm ----------
  function ladder(sec, opts, tr) {
    var t = sec.tables[0];
    if (!t) throw fail("Mục {id} không có bảng", { id: opts.section });
    var c = ["Bậc", "Khi", "Hệ thống làm gì", "Chức năng còn", "Tài xế", "Requirement"].map(function (n) { return column(t, n); });
    var steps = t.rows.map(function (r, i) {
      var l = t.labels[i];
      return { no: plain(r[c[0]]), when: plain(l[c[1]]), act: plain(l[c[2]]), left: plain(l[c[3]]),
        driver: plain(l[c[4]]), req: plain(l[c[5]]) };
    });
    var n = steps.length, colW = W_FN / n, chars = Math.floor((colW - 16) / 6);
    var PALETTE = ["#0F7B6C", "#0F7B6C", "#C27A0E", C.amber, "#B42318"];
    var whenLines = steps.map(function (s) { return wrap(s.when, chars, 5); });
    var leftLines = steps.map(function (s) { return wrap(s.left, chars, 2); });
    var actLines = steps.map(function (s) { return wrap(s.act, chars, 5); });
    var bodyLines = steps.map(function (s, i) { return leftLines[i].concat(actLines[i], [""]); });
    var WHEN = 14 + 13 * Math.max.apply(null, whenLines.map(function (l) { return l.length; }));
    var BOX = 40 + 13 * Math.max.apply(null, bodyLines.map(function (l) { return l.length; })) + 30;
    var DROP = 34, H = 24 + (n - 1) * DROP + WHEN + BOX + 40;
    var svg = svgRoot(W_FN, H, tr("Bậc suy giảm"));
    steps.forEach(function (s, i) {
      var x = i * colW + 4, y = 24 + i * DROP, color = PALETTE[Math.min(i, PALETTE.length - 1)], g = node("g", {}, svg);
      tip(g, tr("Bậc") + " " + s.no + " · " + s.when + "\n" + s.act + "\nRequirement: " + s.req);
      multiline(g, x + 4, y, whenLines[i], { fill: C.soft, "font-size": 10.5 }, 13);
      var by = y + WHEN;
      node("rect", { x: x, y: by, width: colW - 10, height: BOX, rx: 10, fill: color + "14", stroke: color, "stroke-width": 1.5 }, g);
      badge(g, x + 30, by + 16, tr("Bậc") + " " + s.no, color);
      multiline(g, x + 8, by + 40, leftLines[i], { fill: C.text, "font-size": 11, "font-weight": 700 }, 13);
      multiline(g, x + 8, by + 46 + leftLines[i].length * 13, actLines[i], { fill: C.text, "font-size": 11 }, 13);
      if (s.driver && s.driver !== "—") {
        node("rect", { x: x + 6, y: by + BOX - 26, width: colW - 22, height: 20, rx: 6, fill: color }, g);
        node("text", { x: x + 12, y: by + BOX - 12, fill: "#FFFFFF", "font-weight": 600, "font-size": 11 }, g, s.driver);
      }
      if (i < n - 1) {
        var ax = x + colW - 10, ay = by + 18;
        node("line", { x1: ax + 1, y1: ay, x2: ax + 9, y2: ay + DROP, stroke: C.gray, "stroke-width": 1.5, "marker-end": "url(#arrow-gray)" }, svg);
      }
    });
    legend(svg, 12, H - 14, [
      { kind: "box", fill: "#0F7B6C33", stroke: "#0F7B6C", text: tr("đủ chức năng") },
      { kind: "box", fill: "#B2500033", stroke: C.amber, text: tr("một phần hệ thống") },
      { kind: "box", fill: "#B4231833", stroke: "#B42318", text: tr("bỏ chức năng, trả lái") }
    ]);
    return svg;
  }

  var KINDS = { sequence: sequence, latency: latency, states: states, modes: modes, curve: curve, limits: limits, ladder: ladder };

  function labelTables(source, translation, tr) {
    var allTranslated = !!translation;
    source.tables.forEach(function (table, i) {
      var translated = translation && translation.tables[i];
      var matches = translated && translated.rows.length === table.rows.length &&
        translated.header.length === table.header.length &&
        table.header.every(function (h, j) { return tr(h) === translated.header[j]; }) &&
        table.rows.every(function (r, j) { return r.length === translated.rows[j].length; });
      if (!matches) allTranslated = false;
      table.labels = matches ? translated.rows : table.rows;
    });
    return allTranslated;
  }

  // Trả về { node } khi vẽ được, { error } khi bảng không đọc được.
  function render(kind, md, opts) {
    opts = opts || {};
    var tr = opts.tr || function (s, v) {
      return v ? s.replace(/\{(\w+)\}/g, function (m, k) { return v[k] != null ? v[k] : m; }) : s;
    };
    try {
      if (!KINDS[kind]) throw fail("Không có loại sơ đồ \"{kind}\"", { kind: kind });
      var source = section(md, opts.section);
      if (!source) throw fail("Không thấy mục {id} trong tài liệu", { id: "{#" + opts.section + "}" });
      var translation = opts.translation && section(opts.translation, opts.section);
      var allTranslated = labelTables(source, translation, tr);
      var extra = (opts.extra || []).map(function (ref) {
        var sec = section(ref.md, ref.section);
        var translated = ref.translation && section(ref.translation, ref.section);
        if (!sec || !labelTables(sec, translated, tr)) allTranslated = false;
        return sec;
      });
      return { node: KINDS[kind](source, opts, tr, extra), translated: allTranslated };
    } catch (err) {
      return { error: err.key ? tr(err.key, err.values) : err.message };
    }
  }

  root.SpecDiagrams = { render: render };
})(this);
