// Sơ đồ trên bản đồ, vẽ từ bảng trong tài liệu Thiết kế tính năng Path Planner.
// File này không giữ dữ liệu riêng: sửa bảng trong tài liệu thì sơ đồ đổi theo.
//   sequence : bảng ở mục có ID planner-sequence (cột #, Lúc, Từ → tới, Nội dung, Yêu cầu, Trạng thái)
//   latency  : bảng ở mục latency-chain (cột #, Đoạn, Xấu nhất (ms), Bù, Trạng thái)
//   states   : bảng ở mục arbitration-states (cột Sự kiện, Đang ở …, Yêu cầu)
(function (root) {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var C = {
    text: "#1D1D1F", soft: "#6E6E73", faint: "#86868B", line: "#D2D2D7", fill: "#F5F5F7",
    violet: "#5B3DF5", violetTint: "#5B3DF51F", teal: "#0F7B6C", tealTint: "#0F7B6C26",
    gray: "#86868B", grayTint: "#86868B26", amber: "#B25000", amberTint: "#FF95002E"
  };
  var CHAR = 6.6; // bề rộng ước lượng của một ký tự cỡ 12 px

  function node(tag, attrs, parent, text) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { if (attrs[k] != null) n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    if (parent) parent.appendChild(n);
    return n;
  }
  function tip(parent, text) { node("title", {}, parent, text); }
  function plain(s) { return String(s || "").replace(/\*\*/g, "").replace(/`/g, "").trim(); }
  function cellsOf(line) {
    return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(function (c) { return c.trim(); });
  }
  function proposed(status) { return plain(status) !== "đã chốt"; }

  function wrap(text, maxChars, maxLines) {
    var words = plain(text).split(/\s+/), lines = [], cur = "";
    words.forEach(function (w) {
      if (!cur) cur = w;
      else if ((cur + " " + w).length <= maxChars) cur += " " + w;
      else { lines.push(cur); cur = w; }
    });
    if (cur) lines.push(cur);
    if (lines.length > maxLines) {
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
    if (start < 0) throw new Error("không thấy mục {#" + id + "} trong tài liệu Thiết kế");
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
    if (i < 0) throw new Error("bảng thiếu cột \"" + name + "\"");
    return i;
  }
  function svgRoot(w, h, label) {
    var s = node("svg", { viewBox: "0 0 " + w + " " + h, width: w, height: h, role: "img", "aria-label": label,
      "font-family": "Inter, -apple-system, sans-serif", "font-size": 12 });
    var defs = node("defs", {}, s);
    [["arrow", C.violet], ["arrow-amber", C.amber]].forEach(function (m) {
      var mk = node("marker", { id: m[0], viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" }, defs);
      node("path", { d: "M1 1L9 5L1 9z", fill: m[1] }, mk);
    });
    var hatch = node("pattern", { id: "hatch", width: 6, height: 6, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, defs);
    node("rect", { width: 6, height: 6, fill: C.fill }, hatch);
    node("line", { x1: 0, y1: 0, x2: 0, y2: 6, stroke: C.faint, "stroke-width": 2 }, hatch);
    return s;
  }
  function legend(svg, x, y, items) {
    items.forEach(function (it, i) {
      var g = node("g", { transform: "translate(" + (x + i * 210) + "," + y + ")" }, svg);
      if (it.kind === "line") node("line", { x1: 0, y1: 0, x2: 28, y2: 0, stroke: it.color, "stroke-width": 2, "stroke-dasharray": it.dash }, g);
      else node("rect", { x: 0, y: -7, width: 28, height: 14, rx: 3, fill: it.fill, stroke: it.stroke || "none", "stroke-dasharray": it.dash }, g);
      node("text", { x: 36, y: 4, fill: C.soft }, g, it.text);
    });
  }

  // ---------- Tuần tự một chu kỳ ----------
  function sequence(md, opts, tr) {
    var sec = section(md, opts.section), t = sec.tables[0];
    if (!t) throw new Error("mục " + opts.section + " không có bảng");
    var iNo = column(t, "#"), iAt = column(t, "Lúc"), iFT = column(t, "Từ → tới"), iTx = column(t, "Nội dung"),
      iReq = column(t, "Yêu cầu"), iSt = column(t, "Trạng thái");
    var steps = t.rows.map(function (r) {
      var ft = plain(r[iFT]).split(" → ");
      return { no: plain(r[iNo]), at: plain(r[iAt]), from: ft[0], to: ft[1] || ft[0], text: plain(r[iTx]),
        req: plain(r[iReq]), status: plain(r[iSt]) };
    });
    var lanes = (opts.lanes || []).slice();
    steps.forEach(function (s) { [s.from, s.to].forEach(function (n) { if (lanes.indexOf(n) < 0) lanes.push(n); }); });

    var dl = /\*\*Deadline\.\*\*([^\n]*)/.exec(sec.text), deadline = null;
    if (dl) {
      var when = /trước (t0 \+ [\d,]+ ms)/.exec(dl[1]), last = /bước \d+ đến (\d+)/.exec(dl[1]),
        st = /Trạng thái: (đã chốt|đề xuất|cần chốt)/.exec(dl[1]);
      if (when) deadline = { when: when[1], after: last ? last[1] : null, status: st ? st[1] : "cần chốt" };
    }

    var LEFT = 132, LANE = 156, TOP = 78, ROW = 60, GAP = deadline ? 30 : 0;
    var W = LEFT + lanes.length * LANE + 16, H = TOP + steps.length * ROW + GAP + 64;
    var svg = svgRoot(W, H, tr("Tuần tự trong một chu kỳ"));
    var laneX = function (name) { return LEFT + lanes.indexOf(name) * LANE + LANE / 2; };

    lanes.forEach(function (name, i) {
      var x = LEFT + i * LANE;
      node("rect", { x: x + 8, y: 8, width: LANE - 16, height: 46, rx: 10, fill: name === "Planner" ? C.violetTint : C.fill, stroke: C.line }, svg);
      multiline(svg, x + LANE / 2, wrap(name, 20, 2).length > 1 ? 27 : 35, wrap(name, 20, 2),
        { "text-anchor": "middle", "font-weight": 600, fill: C.text }, 14);
      node("line", { x1: x + LANE / 2, y1: 54, x2: x + LANE / 2, y2: H - 52, stroke: C.line, "stroke-dasharray": "3 5" }, svg);
    });

    var shift = 0;
    steps.forEach(function (s, k) {
      var y = TOP + k * ROW + ROW / 2 + shift, warn = proposed(s.status);
      var color = warn ? C.amber : C.violet, g = node("g", {}, svg);
      tip(g, "#" + s.no + " · " + s.at + " · " + s.from + (s.to !== s.from ? " → " + s.to : "") + "\n" + s.text +
        "\n" + tr("Yêu cầu") + ": " + s.req + " · " + s.status);
      node("circle", { cx: 16, cy: y - 4, r: 11, fill: color }, g);
      node("text", { x: 16, y: y, "text-anchor": "middle", fill: "#FFFFFF", "font-weight": 600, "font-size": 11 }, g, s.no);
      multiline(g, 34, y - 4, wrap(s.at, 14, 2), { fill: C.soft, "font-size": 11 }, 13);
      if (s.from === s.to) {
        var x = laneX(s.from);
        node("rect", { x: x - 8, y: y - ROW * 0.34, width: 16, height: ROW * 0.68, rx: 4, fill: warn ? C.amberTint : C.violetTint, stroke: color }, g);
        multiline(g, x + 16, y - 6, wrap(s.text, 34, 3), { fill: C.text }, 14);
      } else {
        var x1 = laneX(s.from), x2 = laneX(s.to), span = Math.abs(x2 - x1);
        node("line", { x1: x1, y1: y, x2: x2 + (x2 > x1 ? -2 : 2), y2: y, stroke: color, "stroke-width": 2,
          "stroke-dasharray": warn ? "6 4" : null, "marker-end": "url(#" + (warn ? "arrow-amber" : "arrow") + ")" }, g);
        var lines = wrap(s.text, Math.max(14, Math.floor((span - 12) / CHAR)), 2);
        multiline(g, (x1 + x2) / 2, y - 8 - (lines.length - 1) * 14, lines, { "text-anchor": "middle", fill: C.text }, 14);
      }
      if (deadline && s.no === deadline.after) {
        shift += GAP;
        var yd = TOP + (k + 1) * ROW + shift - GAP / 2;
        var dg = node("g", {}, svg);
        tip(dg, tr("Deadline") + ": " + deadline.when + " · " + deadline.status);
        node("line", { x1: LEFT, y1: yd, x2: W - 16, y2: yd, stroke: C.amber, "stroke-width": 1.5, "stroke-dasharray": "2 4" }, dg);
        node("text", { x: LEFT + 6, y: yd - 6, fill: C.amber, "font-weight": 600 }, dg,
          "◆ " + tr("Deadline") + " " + deadline.when + " (" + deadline.status + ")");
      }
    });
    legend(svg, LEFT, H - 22, [
      { kind: "line", color: C.violet, text: tr("đã chốt") },
      { kind: "line", color: C.amber, dash: "6 4", text: tr("đề xuất hoặc cần chốt") },
      { kind: "box", fill: C.violetTint, stroke: C.violet, text: tr("khối tự tính") }
    ]);
    return svg;
  }

  // ---------- Chuỗi trễ ----------
  function latency(md, opts, tr) {
    var sec = section(md, opts.section);
    var tables = sec.tables.filter(function (t) { return t.header.indexOf("Xấu nhất (ms)") >= 0; });
    if (!tables.length) throw new Error("mục " + opts.section + " không có bảng có cột \"Xấu nhất (ms)\"");
    function read(t) {
      var iNo = column(t, "#"), iName = column(t, "Đoạn"), iMs = column(t, "Xấu nhất (ms)"), iBu = column(t, "Bù"), iSt = column(t, "Trạng thái");
      var rows = t.rows.map(function (r) {
        var v = plain(r[iMs]);
        return { no: plain(r[iNo]), name: plain(r[iName]), ms: parseFloat(v.replace(",", ".")) || 0, unknown: v.indexOf("?") >= 0,
          raw: v, bu: plain(r[iBu]), status: plain(r[iSt]) };
      });
      rows.forEach(function (r) {
        var like = /^Như dòng (\d+)/.exec(r.bu);
        var src = like && rows.filter(function (x) { return x.no === like[1]; })[0];
        if (src) r.bu = src.bu;
        r.who = /^Planner/.test(r.bu) ? "planner" : /Lateral Controller/.test(r.bu) ? "controller" : "none";
      });
      return rows;
    }
    var main = read(tables[0]), parallel = tables[1] ? read(tables[1]) : [];
    var t0 = 0;
    main.forEach(function (r) { r.start = t0; t0 += r.ms; });
    parallel.forEach(function (r) { r.start = 0; });
    var total = t0, boundary = 0;
    for (var i = 0; i < main.length && main[i].who === "planner"; i++) boundary = main[i].start + main[i].ms;

    var LABEL = 300, CHART = 640, ROW = 34, TOP = 66;
    var maxMs = Math.ceil(Math.max(total, 1) / 50) * 50, px = CHART / maxMs;
    var nRows = main.length + 1 + (parallel.length ? parallel.length + 1 : 0);
    var W = LABEL + CHART + 120, H = TOP + nRows * ROW + 70;
    var svg = svgRoot(W, H, tr("Chuỗi trễ từ cảm biến tới bánh xe"));
    var fills = { planner: [C.violetTint, C.violet], controller: [C.tealTint, C.teal], none: [C.grayTint, C.gray] };

    for (var ms = 0; ms <= maxMs; ms += 50) {
      var gx = LABEL + ms * px;
      node("line", { x1: gx, y1: TOP - 12, x2: gx, y2: H - 46, stroke: C.line, "stroke-dasharray": ms ? "2 4" : null }, svg);
      node("text", { x: gx, y: TOP - 18, "text-anchor": "middle", fill: C.soft, "font-size": 11 }, svg, ms + " ms");
    }

    function bar(r, y) {
      var g = node("g", {}, svg), f = fills[r.who], warn = proposed(r.status);
      tip(g, r.no + ". " + r.name + "\n" + tr("Xấu nhất") + ": " + r.raw + " ms · " + tr("Bù") + ": " + r.bu + " · " + r.status);
      multiline(g, 12, y + 4, wrap(r.no + "  " + r.name, 44, 1), { fill: C.text }, 14);
      var x = LABEL + r.start * px, w = Math.max(r.ms * px, 3);
      if (r.ms > 0) node("rect", { x: x, y: y - 9, width: w, height: 18, rx: 3, fill: f[0], stroke: f[1], "stroke-dasharray": warn ? "4 3" : null }, g);
      if (r.unknown) {
        node("rect", { x: x + (r.ms > 0 ? w + 2 : 0), y: y - 9, width: 22, height: 18, rx: 3, fill: "url(#hatch)", stroke: C.faint }, g);
        w += r.ms > 0 ? 24 : 22;
      }
      node("text", { x: x + w + 6, y: y + 4, fill: C.soft, "font-size": 11 }, g, r.raw + " ms");
    }

    var y = TOP + ROW / 2;
    main.forEach(function (r) { bar(r, y); y += ROW; });
    var tg = node("g", {}, svg);
    node("text", { x: 12, y: y + 4, fill: C.text, "font-weight": 700 }, tg,
      tr("Tổng") + " " + total + " ms" + (main.some(function (r) { return r.unknown; }) ? " " + tr("cộng phần chưa biết") : ""));
    node("rect", { x: LABEL, y: y - 9, width: total * px, height: 18, rx: 3, fill: C.text }, tg);
    node("rect", { x: LABEL, y: y - 9, width: boundary * px, height: 18, rx: 3, fill: C.violet }, tg);
    var bx = LABEL + boundary * px;
    node("line", { x1: bx, y1: TOP - 6, x2: bx, y2: y + 14, stroke: C.violet, "stroke-width": 1.5, "stroke-dasharray": "5 3" }, svg);
    node("text", { x: bx + 6, y: TOP + 2, fill: C.violet, "font-weight": 600, "font-size": 11 }, svg,
      "▲ " + tr("Planner gửi path, stamp = t0") + " · " + boundary + " ms");
    y += ROW;
    if (parallel.length) {
      node("text", { x: 12, y: y + 4, fill: C.soft, "font-weight": 600 }, svg, tr("Chuỗi song song, tính từ 0"));
      y += ROW;
      parallel.forEach(function (r) { bar(r, y); y += ROW; });
    }
    legend(svg, 12, H - 22, [
      { kind: "box", fill: C.violetTint, stroke: C.violet, text: tr("Planner bù") },
      { kind: "box", fill: C.tealTint, stroke: C.teal, text: tr("Lateral Controller bù") },
      { kind: "box", fill: C.grayTint, stroke: C.gray, text: tr("không bù") },
      { kind: "box", fill: "url(#hatch)", stroke: C.faint, text: tr("chưa biết") },
      { kind: "box", fill: "#FFFFFF", stroke: C.soft, dash: "4 3", text: tr("đề xuất hoặc cần chốt") }
    ]);
    return svg;
  }

  // ---------- Chuyển trạng thái ----------
  function states(md, opts, tr) {
    var sec = section(md, opts.section), t = sec.tables[0];
    if (!t) throw new Error("mục " + opts.section + " không có bảng");
    var iEv = column(t, "Sự kiện"), cols = [];
    t.header.forEach(function (h, i) { var m = /^Đang ở (\S+)/.exec(h); if (m) cols.push({ i: i, name: m[1] }); });
    if (!cols.length) throw new Error("bảng thiếu các cột \"Đang ở …\"");
    var names = cols.map(function (c) { return c.name; });
    var pattern = new RegExp("(?:→|không thì)\\s*(" + names.join("|") + ")\\b", "g");
    var likeRe = new RegExp("^Như (" + names.join("|") + "|dòng trên)\\b");

    function targets(text, sure) {
      var out = [], m;
      pattern.lastIndex = 0;
      while ((m = pattern.exec(plain(text)))) out.push({ to: m[1], sure: sure });
      return out;
    }
    var resolved = []; // resolved[row][state] = [{to, sure}]
    t.rows.forEach(function (r, ri) {
      var raw = {};
      cols.forEach(function (c) { raw[c.name] = r[c.i] || ""; });
      var res = {};
      function solve(name, seen) {
        if (res[name]) return res[name];
        var parts = raw[name].split("**?**"), unsure = parts.slice(1).join(" ");
        var list = targets(parts[0], true).concat(targets(unsure, false));
        // "(như dòng trên)" sau dấu ? lấy lại các lần chuyển chưa chắc của dòng trên, cùng cột.
        if (/như dòng trên/i.test(plain(unsure)) && resolved[ri - 1]) {
          list = list.concat(resolved[ri - 1][name].filter(function (x) { return !x.sure; }));
        }
        var like = likeRe.exec(plain(parts[0]));
        if (like && !seen[name]) {
          seen[name] = true;
          var src = like[1] === "dòng trên" ? (resolved[ri - 1] || {})[name] || [] : solve(like[1], seen);
          list = src.concat(list);
        }
        return (res[name] = list.filter(function (x) { return x.to !== name; }));
      }
      names.forEach(function (n) { solve(n, {}); });
      resolved.push(res);
    });

    // Sự kiện đưa mọi trạng thái khác về cùng một đích thì vẽ một lần, "từ mọi trạng thái".
    var globals = [], edges = {};
    resolved.forEach(function (res, ri) {
      var list = [];
      names.forEach(function (from) { res[from].forEach(function (x) { list.push({ from: from, to: x.to, sure: x.sure }); }); });
      var tos = list.map(function (x) { return x.to; }).filter(function (v, i, a) { return a.indexOf(v) === i; });
      var sures = list.map(function (x) { return x.sure; }).filter(function (v, i, a) { return a.indexOf(v) === i; });
      if (tos.length === 1 && sures.length === 1) {
        var others = names.filter(function (n) { return n !== tos[0]; });
        var froms = list.map(function (x) { return x.from; });
        if (others.length >= 3 && others.every(function (n) { return froms.indexOf(n) >= 0; })) {
          globals.push({ to: tos[0], sure: sures[0], event: ri + 1 });
          return;
        }
      }
      list.forEach(function (x) {
        var key = x.from + ">" + x.to + ">" + (x.sure ? "s" : "u");
        (edges[key] = edges[key] || { from: x.from, to: x.to, sure: x.sure, events: [] });
        if (edges[key].events.indexOf(ri + 1) < 0) edges[key].events.push(ri + 1);
      });
    });

    var ladder = names.slice().reverse(); // cột cuối (ưu tiên cao nhất) ở trên cùng
    var NODE_W = 132, NODE_H = 46, CX = 390, TOP = 56, STEP = 132, SPREAD = 70;
    var events = t.rows.map(function (r) { return plain(r[iEv]); });
    var bottom = TOP + (ladder.length - 1) * STEP + NODE_H;
    var LEG_X = 800, W = LEG_X + 360, H = Math.max(bottom + (globals.length ? 120 : 0) + 50, 60 + events.length * 34 + 40);
    var svg = svgRoot(W, H, tr("Chuyển trạng thái phân xử"));
    var yOf = function (n) { return TOP + ladder.indexOf(n) * STEP + NODE_H / 2; };

    node("text", { x: CX - 300, y: 24, fill: C.soft, "font-size": 11 }, svg, "◀ " + tr("sang chức năng ưu tiên cao hơn"));
    node("text", { x: CX + 300, y: 24, fill: C.soft, "font-size": 11, "text-anchor": "end" }, svg, tr("sang chức năng ưu tiên thấp hơn") + " ▶");

    globals.forEach(function (gl, i) {
      var color = gl.sure ? C.violet : C.amber, x = CX + (i - (globals.length - 1) / 2) * 120, y0 = yOf(gl.to) + NODE_H / 2;
      var g = node("g", {}, svg);
      tip(g, tr("Từ mọi trạng thái") + " → " + gl.to + "\n" + gl.event + ". " + events[gl.event - 1] +
        (gl.sure ? "" : "\n" + tr("Chưa có yêu cầu quyết định (ô có ?)")));
      node("line", { x1: x, y1: y0 + 64, x2: x, y2: y0 + 4, stroke: color, "stroke-width": 2, "stroke-dasharray": gl.sure ? null : "6 4",
        "marker-end": "url(#" + (gl.sure ? "arrow" : "arrow-amber") + ")" }, g);
      node("text", { x: x, y: y0 + 84, "text-anchor": "middle", fill: color, "font-weight": 600, "font-size": 11 }, g,
        gl.event + (gl.sure ? "" : " ?") + " · " + tr("từ mọi trạng thái"));
    });

    Object.keys(edges).map(function (k) { return edges[k]; }).forEach(function (e) {
      var a = ladder.indexOf(e.from), b = ladder.indexOf(e.to), up = b < a, side = up ? -1 : 1, d = Math.abs(a - b);
      var reach = NODE_W / 2 + 34 + SPREAD * d + (e.sure ? 0 : 34);
      var x0 = CX + side * NODE_W / 2, y0 = yOf(e.from) + (up ? -8 : 8), y1 = yOf(e.to) + (up ? 8 : -8), xc = CX + side * reach;
      var color = e.sure ? C.violet : C.amber, g = node("g", {}, svg);
      tip(g, e.from + " → " + e.to + "\n" + e.events.map(function (n) { return n + ". " + events[n - 1]; }).join("\n") +
        (e.sure ? "" : "\n" + tr("Chưa có yêu cầu quyết định (ô có ?)")));
      node("path", { d: "M" + x0 + " " + y0 + " C" + xc + " " + y0 + " " + xc + " " + y1 + " " + (x0 + side * 2) + " " + y1,
        fill: "none", stroke: color, "stroke-width": 2, "stroke-dasharray": e.sure ? null : "6 4",
        "marker-end": "url(#" + (e.sure ? "arrow" : "arrow-amber") + ")" }, g);
      var lx = CX + side * (NODE_W / 2 + (reach - NODE_W / 2) * 0.75), ly = (y0 + y1) / 2;
      var label = e.events.join(", ") + (e.sure ? "" : " ?");
      node("rect", { x: lx - label.length * 3.6 - 6, y: ly - 10, width: label.length * 7.2 + 12, height: 20, rx: 10, fill: "#FFFFFF", stroke: color }, g);
      node("text", { x: lx, y: ly + 4, "text-anchor": "middle", fill: color, "font-weight": 600, "font-size": 11 }, g, label);
    });

    ladder.forEach(function (n) {
      var y = yOf(n);
      node("rect", { x: CX - NODE_W / 2, y: y - NODE_H / 2, width: NODE_W, height: NODE_H, rx: 14,
        fill: n === "NONE" ? C.fill : C.violetTint, stroke: n === "NONE" ? C.line : C.violet, "stroke-width": 1.5 }, svg);
      node("text", { x: CX, y: y + 5, "text-anchor": "middle", "font-weight": 700, "font-size": 15, fill: C.text }, svg, n);
    });

    node("text", { x: LEG_X, y: 24, "font-weight": 700, fill: C.text }, svg, tr("Sự kiện"));
    events.forEach(function (ev, i) {
      multiline(svg, LEG_X, 50 + i * 34, wrap((i + 1) + ". " + ev, 52, 2), { fill: C.text, "font-size": 11.5 }, 13);
    });
    legend(svg, 20, H - 22, [
      { kind: "line", color: C.violet, text: tr("theo yêu cầu đã có") },
      { kind: "line", color: C.amber, dash: "6 4", text: tr("chưa có yêu cầu (đề xuất)") }
    ]);
    return svg;
  }

  var KINDS = { sequence: sequence, latency: latency, states: states };

  // Trả về { node } khi vẽ được, { error } khi bảng không đọc được.
  function render(kind, md, opts) {
    var tr = (opts && opts.tr) || function (s) { return s; };
    try {
      if (!KINDS[kind]) throw new Error("không có loại sơ đồ \"" + kind + "\"");
      return { node: KINDS[kind](md, opts || {}, tr) };
    } catch (err) {
      return { error: err.message };
    }
  }

  root.SpecDiagrams = { render: render };
})(this);
