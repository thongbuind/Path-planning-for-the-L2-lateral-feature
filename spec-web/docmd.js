/*
 * Chuyển Markdown <-> HTML cho trang tài liệu. Chỉ hỗ trợ phần Markdown mà tài liệu dùng:
 * tiêu đề #..###, đoạn văn, danh sách - và 1., bảng kiểu GitHub, **đậm**, *nghiêng*,
 * `code`, [link](url), xuống dòng cứng (hai dấu cách cuối dòng), ký tự thoát \x, ---.
 * Không dùng thư viện ngoài, để web chạy được khi offline.
 *
 * toHtml(md)  : chuỗi Markdown -> chuỗi HTML (chạy được cả trong Node để kiểm tra).
 * toMd(node)  : phần tử DOM của trang (contenteditable) -> chuỗi Markdown.
 *
 * Ô bảng chỉ chứa đúng một nhãn nguồn ở một trong hai ngôn ngữ được vẽ
 * thành nhãn màu; khi lưu lại ghi đúng chữ cũ.
 */
(function (root) {
  "use strict";

  var TAGS = {
    "đã chốt": "da-chot", "đề bài": "de-bai", "mentor": "mentor", "đề xuất": "de-xuat", "cần chốt": "can-chot",
    "agreed": "da-chot", "assignment": "de-bai", "proposed": "de-xuat", "to be agreed": "can-chot"
  };

  // ---------- Markdown -> HTML ----------
  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function inline(src) {
    var slots = [];
    function keep(html) { slots.push(html); return "\u0000" + (slots.length - 1) + "\u0000"; }
    var s = src
      .replace(/\\([\\`*_{}\[\]()#+\-.!|>~])/g, function (_, ch) { return keep(esc(ch)); })
      .replace(/`([^`]+)`/g, function (_, c) { return keep("<code>" + esc(c) + "</code>"); });
    s = esc(s)
      .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, function (_, t, u) {
        return /^(https?:|mailto:|\.|\/|#)/.test(u) || !/:/.test(u) ? '<a href="' + u + '">' + t + "</a>" : t;
      })
      .replace(/\*\*([^*]+?)\*\*/g, "<b>$1</b>")
      .replace(/(^|[^*])\*([^*\s][^*]*?)\*(?!\*)/g, "$1<i>$2</i>");
    return s.replace(/\u0000(\d+)\u0000/g, function (_, i) { return slots[+i]; });
  }

  function splitRow(line) {
    var t = line.trim().replace(/^\|/, "");
    if (/(^|[^\\])\|$/.test(t)) t = t.slice(0, -1);
    var cells = [], cur = "";
    for (var i = 0; i < t.length; i++) {
      if (t[i] === "\\" && t[i + 1] === "|") { cur += "\\|"; i++; continue; }
      if (t[i] === "|") { cells.push(cur.trim()); cur = ""; continue; }
      cur += t[i];
    }
    cells.push(cur.trim());
    return cells;
  }

  function cellHtml(text) {
    var key = text.trim().toLowerCase();
    if (Object.hasOwn(TAGS, key)) {
      return '<span class="tag tag-' + TAGS[key] + '" contenteditable="false" data-md="' + esc(text.trim()) + '">' +
        esc(text.trim().charAt(0).toUpperCase() + text.trim().slice(1)) + "</span>";
    }
    return inline(text);
  }

  function paraHtml(lines) {
    return lines.map(function (l, i) {
      var hard = i < lines.length - 1 && / {2,}$/.test(l);
      return inline(l.trim()) + (hard ? "<br>" : "");
    }).join(lines.length > 1 ? "\n" : "");
  }

  var RE_UL = /^(\s*)[-*+]\s+(.*)$/;
  var RE_OL = /^(\s*)\d+[.)]\s+(.*)$/;
  var RE_SEP = /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$/;

  function heading(line) {
    var h = /^(#{1,3})\s+(.*?)\s*#*\s*$/.exec(line);
    if (!h) return null;
    var section = /\s+\{#([a-z0-9][a-z0-9-]*)\}$/.exec(h[2]);
    return { level: h[1].length, title: section ? h[2].slice(0, section.index) : h[2],
      id: section ? section[1] : "" };
  }

  function toHtml(md) {
    var lines = md.replace(/\r\n?/g, "\n").split("\n");
    var out = [];
    var i = 0;
    while (i < lines.length) {
      var line = lines[i];
      if (!line.trim()) { i++; continue; }
      var h = heading(line);
      if (h) {
        var tag = "h" + h.level;
        out.push("<" + tag + (h.id ? ' id="' + h.id + '"' : "") + ">" + inline(h.title) + "</" + tag + ">");
        i++;
        continue;
      }
      if (/^\s*(---+|\*\*\*+)\s*$/.test(line)) { out.push("<hr>"); i++; continue; }
      if (/^\s*\|/.test(line) && i + 1 < lines.length && RE_SEP.test(lines[i + 1])) {
        var head = splitRow(line);
        i += 2;
        var rows = [];
        while (i < lines.length && /^\s*\|/.test(lines[i])) { rows.push(splitRow(lines[i])); i++; }
        out.push("<table><thead><tr>" + head.map(function (c) { return "<th>" + inline(c) + "</th>"; }).join("") +
          "</tr></thead><tbody>" + rows.map(function (r) {
            return "<tr>" + head.map(function (_, k) { return "<td>" + cellHtml(r[k] || "") + "</td>"; }).join("") + "</tr>";
          }).join("") + "</tbody></table>");
        continue;
      }
      if (RE_UL.test(line) || RE_OL.test(line)) {
        var res = parseList(lines, i, (RE_UL.exec(line) || RE_OL.exec(line))[1].length);
        out.push(res.html);
        i = res.next;
        continue;
      }
      var para = [];
      while (i < lines.length && lines[i].trim() && !/^#{1,3}\s/.test(lines[i]) &&
             !RE_UL.test(lines[i]) && !RE_OL.test(lines[i]) && !/^\s*\|/.test(lines[i])) {
        para.push(lines[i]); i++;
      }
      if (!para.length) { para.push(lines[i]); i++; }
      out.push("<p>" + paraHtml(para) + "</p>");
    }
    return out.join("");
  }

  function parseList(lines, i, indent) {
    var ordered = RE_OL.test(lines[i]) && !RE_UL.test(lines[i]);
    var items = [];
    while (i < lines.length) {
      var m = (ordered ? RE_OL : RE_UL).exec(lines[i]);
      if (!m || m[1].length !== indent) break;
      var text = [m[2]];
      var sub = "";
      i++;
      while (i < lines.length && lines[i].trim()) {
        var mm = RE_UL.exec(lines[i]) || RE_OL.exec(lines[i]);
        if (mm && mm[1].length > indent) { var r = parseList(lines, i, mm[1].length); sub += r.html; i = r.next; continue; }
        if (mm) break;
        if (/^\s+/.test(lines[i])) { text.push(lines[i]); i++; continue; }
        break;
      }
      items.push("<li>" + paraHtml(text) + sub + "</li>");
      if (i < lines.length && !lines[i].trim()) {
        var j = i; while (j < lines.length && !lines[j].trim()) j++;
        var nx = j < lines.length && ((ordered ? RE_OL : RE_UL).exec(lines[j]));
        if (nx && nx[1].length === indent) { i = j; continue; }
        break;
      }
    }
    var tag = ordered ? "ol" : "ul";
    return { html: "<" + tag + ">" + items.join("") + "</" + tag + ">", next: i };
  }

  // ---------- HTML (DOM) -> Markdown ----------
  function escText(s, inTable) {
    s = s.replace(/\\/g, "\\\\").replace(/\*/g, "\\*").replace(/`/g, "\\`");
    if (inTable) s = s.replace(/\|/g, "\\|");
    return s;
  }

  // Đặt dấu ** hoặc * sát chữ: dời dấu cách ở mép ra ngoài, nếu không Markdown không nhận.
  function wrap(mark, inner) {
    var m = /^(\s*)([\s\S]*?)(\s*)$/.exec(inner);
    return m[2] ? m[1] + mark + m[2] + mark + m[3] : inner;
  }

  function inlineMd(node, ctx) {
    var out = "";
    node.childNodes.forEach(function (n) {
      if (n.nodeType === 3) { out += escText(n.nodeValue.replace(/\u00a0/g, " ").replace(/\s+/g, " "), ctx.table); return; }
      if (n.nodeType !== 1) return;
      var t = n.tagName.toLowerCase();
      if (n.classList.contains("tag")) { out += n.getAttribute("data-md") || n.textContent; return; }
      if (t === "br") { out += ctx.table ? " " : "  \n"; return; }
      var inner = inlineMd(n, ctx);
      var st = n.getAttribute("style") || "";
      if (t === "b" || t === "strong" || /font-weight:\s*(bold|[6-9]00)/.test(st)) out += wrap("**", inner);
      else if (t === "i" || t === "em" || /font-style:\s*italic/.test(st)) out += wrap("*", inner);
      else if (t === "code") out += "`" + n.textContent + "`";
      else if (t === "a" && n.getAttribute("href")) out += "[" + inner + "](" + n.getAttribute("href") + ")";
      else out += inner;
    });
    return out;
  }

  function clean(s) {
    return s.replace(/[ \t]+\n/g, function (m) { return /  \n$/.test(m) ? "  \n" : "\n"; })
      .replace(/^ +| +$/g, "").replace(/ {3,}(?!\n)/g, " ");
  }

  function listMd(list, depth) {
    var ordered = list.tagName.toLowerCase() === "ol";
    var pad = new Array(depth + 1).join("   ");
    var lines = [];
    var k = 0;
    list.childNodes.forEach(function (li) {
      if (li.nodeType !== 1) return;
      if (/^(ul|ol)$/i.test(li.tagName)) { lines.push(listMd(li, depth + 1)); return; }
      k++;
      var text = "", subs = [];
      li.childNodes.forEach(function (c) {
        if (c.nodeType === 1 && /^(ul|ol)$/i.test(c.tagName)) subs.push(listMd(c, depth + 1));
        else if (c.nodeType === 1 && /^(p|div)$/i.test(c.tagName)) text += (text ? " " : "") + inlineMd(c, {});
        else { var w = document.createElement("span"); w.appendChild(c.cloneNode(true)); text += inlineMd(w, {}); }
      });
      text = clean(text);
      if (!text && !subs.length) return;
      lines.push(pad + (ordered ? k + ". " : "- ") + text.replace(/\n/g, "\n" + pad + "  "));
      subs.forEach(function (s) { lines.push(s); });
    });
    return lines.join("\n");
  }

  function tableMd(table) {
    var rows = [];
    table.querySelectorAll("tr").forEach(function (tr) {
      var cells = [];
      tr.querySelectorAll("th, td").forEach(function (c) { cells.push(clean(inlineMd(c, { table: true })) || " "); });
      if (cells.length) rows.push(cells);
    });
    if (!rows.length) return "";
    var n = Math.max.apply(null, rows.map(function (r) { return r.length; }));
    function line(r) { var a = r.slice(); while (a.length < n) a.push(" "); return "| " + a.join(" | ") + " |"; }
    var out = [line(rows[0]), "|" + new Array(n + 1).join("---|")];
    rows.slice(1).forEach(function (r) { out.push(line(r)); });
    return out.join("\n");
  }

  function escBlockStart(s) {
    return s.replace(/^(#{1,6}\s|[-+]\s|\d+[.)]\s|>|\|)/, "\\$1");
  }

  function toMd(rootNode) {
    var blocks = [];
    function block(n) {
      if (n.nodeType === 3) {
        var t = clean(escText(n.nodeValue.replace(/\u00a0/g, " ")));
        if (t.trim()) blocks.push(escBlockStart(t.trim()));
        return;
      }
      if (n.nodeType !== 1) return;
      var t = n.tagName.toLowerCase();
      var hm = /^h([1-6])$/.exec(t);
      if (hm) {
        var txt = clean(inlineMd(n, {})).replace(/\s*\n\s*/g, " ").trim();
        if (txt) {
          var section = /^[a-z0-9][a-z0-9-]*$/.test(n.id) ? " {#" + n.id + "}" : "";
          blocks.push(new Array(Math.min(+hm[1], 3) + 1).join("#") + " " + txt + section);
        }
      } else if (t === "ul" || t === "ol") {
        var l = listMd(n, 0); if (l.trim()) blocks.push(l);
      } else if (t === "table") {
        var tb = tableMd(n); if (tb) blocks.push(tb);
      } else if (t === "hr") {
        blocks.push("---");
      } else if (t === "div" && n.querySelector("p, h1, h2, h3, ul, ol, table, div")) {
        n.childNodes.forEach(block);
      } else {
        var p = clean(inlineMd(n, {})).replace(/\s+$/, "");
        if (p.trim()) blocks.push(escBlockStart(p.trim()));
      }
    }
    rootNode.childNodes.forEach(block);
    return blocks.join("\n\n") + "\n";
  }

  var api = { heading: heading, toHtml: toHtml, toMd: toMd };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.DocMD = api;
})(this);
