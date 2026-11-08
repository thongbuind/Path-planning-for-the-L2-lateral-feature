(function () {
  "use strict";

  var viewport = document.getElementById("viewport");
  var world = document.getElementById("world");
  var zoomLabel = document.getElementById("zoom-level");
  var languageSwitch = document.getElementById("language-switch");
  var languageButtons = languageSwitch.querySelectorAll("button");
  var translations = window.SPEC_EN || {};
  var LANGUAGE_KEY = "spec-web.language";
  var staticSite = document.documentElement.hasAttribute("data-static");
  var route = new URLSearchParams(location.search);
  var language = "vi";
  try {
    if (localStorage.getItem(LANGUAGE_KEY) === "en") language = "en";
  } catch (err) { /* vẫn dùng được khi trình duyệt tắt lưu trữ */ }
  var requestedLanguage = route.get("lang");
  if (requestedLanguage === "vi" || requestedLanguage === "en") language = requestedLanguage;

  // Giữ nguyên văn bản gốc khi cập nhật giao diện nhiều lần.
  var interfaceText = Array.from(document.querySelectorAll("[data-i18n], [data-i18n-aria]"), function (node) {
    var attribute = node.hasAttribute("data-i18n-aria") ? "aria-label" : null;
    return { node: node, attribute: attribute, text: attribute ? node.getAttribute(attribute) : node.textContent };
  });

  function tr(text, values) {
    var message = language === "en" && Object.hasOwn(translations, text) ? translations[text] : text;
    return values ? message.replace(/\{(\w+)\}/g, function (_, key) { return values[key]; }) : message;
  }

  var MIN_K = 0.1;
  var MAX_K = 3;
  var DRAG_THRESHOLD = 5; // px: dưới ngưỡng này coi là bấm, không phải kéo
  var GRID = 24;

  var view = { x: 0, y: 0, k: 1 };
  var cards = window.SPEC_CARDS || [];

  // ---------- Hiển thị ----------
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  var ICON_STEER =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.2"/>' +
    '<path d="M3.5 10.5c3-1.4 5.8-2 8.5-2s5.5.6 8.5 2M10 13.8 6.2 19.6M14 13.8l3.8 5.8"/></svg>';
  var ICONS = {
    steer: ICON_STEER,
    lane:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 21 9.5 3M18 21 14.5 3M12 20v-2.5M12 13.5v-2.5M12 7V5"/></svg>',
    sensor:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12h4l3-7 4 14 3-7h4"/></svg>',
    object:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="3" width="12" height="18" rx="3"/><path d="M9 8h6M9 16h1.5M13.5 16H15"/></svg>',
    estimate:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h16M5 16l4.5-5 3.5 3 6-8"/></svg>',
    ego:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 20c0-6 4-8 7-8s7-2 7-8"/><path d="M15 4h4v4"/></svg>',
    adas:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="7" width="18" height="10" rx="5"/><circle cx="16" cy="12" r="2.5"/></svg>',
    config:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/></svg>',
    planner:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5" cy="19" r="2"/><circle cx="19" cy="5" r="2"/><path d="M7 19c7 0 3-14 10-14"/></svg>',
    rules:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/></svg>',
    clock:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    bus:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12h18M6 12V7M12 12V7M18 12V7M9 12v5M15 12v5"/></svg>',
    car:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 16V11l2-5h10l2 5v5H5z"/><path d="M5 11h14"/><circle cx="8" cy="16" r="1.6"/><circle cx="16" cy="16" r="1.6"/></svg>',
    camera:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="7" width="18" height="12" rx="2"/><path d="M8 7l1.5-2h5L16 7"/><circle cx="12" cy="13" r="3"/></svg>',
    flag:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 21V4M6 4h11l-2 4 2 4H6"/></svg>',
    chart:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h16M7 16v-4M12 16V8M17 16v-7"/></svg>'
  };
  var ICON_ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3.5 10.5 8 6 12.5"/></svg>';

  // Thẻ báo cáo là liên kết tới trang riêng.
  function renderDocCard(c) {
    var b = el("a", "card doc");
    b.href = reportHref(c.doc);
    b.dataset.id = c.id;
    b.dataset.region = c.region || "docs";
    b.style.left = c.x + "px";
    b.style.top = c.y + "px";

    var head = el("span", "doc-head");
    head.appendChild(el("span", "doc-kicker", tr(c.eyebrow)));
    if (c.docNo) head.appendChild(el("span", "doc-no", c.docNo));
    b.appendChild(head);

    b.appendChild(el("span", "doc-title", tr(c.title)));
    if (c.summary) b.appendChild(el("span", "doc-sub", tr(c.summary)));

    b.appendChild(el("span", "doc-toc"));
    b.appendChild(el("span", "doc-versions"));

    var foot = el("span", "doc-foot");
    foot.appendChild(el("span", "doc-file", mdName(c)));
    if (c.status) foot.appendChild(el("span", "doc-status", tr(c.status)));
    b.appendChild(foot);

    world.appendChild(b);
  }

  // Khi chạy cục bộ, bản gốc tiếng Việt đồng bộ qua API. Bản xuất đọc hai file Markdown tĩnh.
  var page = document.getElementById("doc-page");
  var backLink = document.getElementById("report-back");
  var viewerVersions = document.getElementById("doc-versions");
  var saveNote = document.getElementById("doc-save");
  var POLL_MS = 1500;
  var SERVE_URL = "http://127.0.0.1:8770/";
  var requestedDoc = route.get("doc");

  if (page && requestedDoc) {
    var mergedReport = docCards().find(function (c) { return c.mergedFrom?.doc === requestedDoc; });
    if (mergedReport) {
      var destination = new URL(location.href);
      destination.searchParams.set("doc", mergedReport.doc);
      if (!destination.hash) destination.hash = mergedReport.mergedFrom.section;
      location.replace(destination);
      return;
    }
  }

  // Mở thẳng index.html (file://) thì không đọc, ghi được md. Nếu serve.py đang chạy, chuyển sang nó.
  if (location.protocol === "file:" && !staticSite) {
    fetch(SERVE_URL + "api/ping", { cache: "no-store" })
      .then(function (r) {
        if (r.ok) location.replace(SERVE_URL + (page ? "report.html" : "") + location.search + location.hash);
      })
      .catch(function () { /* serve.py chưa chạy: trang tài liệu sẽ hướng dẫn */ });
  }
  var docState = { vi: {}, en: {} };
  var versionRecords = null;
  var pendingVersionRecords = null;
  var currentDoc = page && docCards().find(function (c) { return c.doc === requestedDoc; });
  var pageVersion = null; // Nội dung và ETag đã dùng để dựng trang đang sửa.
  var saveTimer = null;
  var saving = null;
  var dirty = false;
  var leavingDoc = false;
  var reviews = currentDoc && window.SpecReviews.mount({
    page: page,
    docId: currentDoc.doc,
    mergedDraftDoc: currentDoc.mergedFrom?.doc,
    staticSite: staticSite,
    tr: tr,
    reportTitle: function () { return tr(currentDoc.title); },
    revision: function () { return dirty || saving ? null : st(currentDoc.doc, docLanguage(currentDoc)).revision; }
  });

  if (currentDoc) {
    var fitButton = document.getElementById("report-fit");
    var desk = page.parentElement;
    function updateDocZoom() {
      if (!desk.classList.contains("fit-width")) return;
      var style = getComputedStyle(desk);
      var width = desk.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
      var paperWidth = parseFloat(style.getPropertyValue("--doc-paper-width"));
      desk.style.setProperty("--doc-zoom", Math.max(1, width / paperWidth));
    }
    fitButton.hidden = false;
    fitButton.addEventListener("click", function () {
      var fit = desk.classList.toggle("fit-width");
      fitButton.setAttribute("aria-pressed", String(fit));
      updateDocZoom();
    });
    new ResizeObserver(updateDocZoom).observe(desk);
  }

  function reportHref(doc, section) {
    var params = new URLSearchParams();
    if (doc) params.set("doc", doc);
    params.set("lang", language);
    return "report.html?" + params.toString() + (section ? "#" + section : "");
  }

  // Liên kết theo mục luôn mở bản gốc tiếng Việt của Research.
  function docLanguage(c) {
    return language === "en" && !st(c.doc, "en").missing && !(c === currentDoc && location.hash) ? "en" : "vi";
  }

  function mdName(c) { return "docs/" + docLanguage(c) + "/" + c.doc + ".md"; }
  function docUrl(id, lang) {
    id = encodeURIComponent(id);
    return staticSite || lang === "en" ? lang + "/" + id + ".md" : "api/docs/" + id;
  }
  function docCards() { return cards.filter(function (c) { return c.kind === "doc"; }); }
  function st(id, lang) {
    var states = docState[lang];
    return states[id] || (states[id] = { md: null, etag: null, revision: null, ok: null, missing: false, pending: null });
  }

  async function docRevision(bytes) {
    if (!window.crypto?.subtle) return null;
    var hash = await window.crypto.subtle.digest("SHA-256", bytes).catch(function () { return null; });
    return hash && Array.from(new Uint8Array(hash), function (byte) {
      return byte.toString(16).padStart(2, "0");
    }).join("");
  }

  function loadVersionRecords() {
    if (pendingVersionRecords) return pendingVersionRecords;
    pendingVersionRecords = fetch("en/versions.json", { cache: "no-store" })
      .then(function (r) {
        if (r.status === 404) return {};
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(function (records) { versionRecords = records; })
      .catch(function () { versionRecords = null; })
      .finally(function () { pendingVersionRecords = null; });
    return pendingVersionRecords;
  }

  function renderDocVersions(c) {
    var vi = st(c.doc, "vi");
    var en = st(c.doc, "en");
    var record = versionRecords?.[c.doc];
    var state = "pending";
    var label = "Đang đối chiếu…";
    if (en.missing) {
      label = "Chưa có bản dịch EN";
    } else if (vi.ok === false || en.ok === false) {
      label = "Chưa đọc đủ hai bản";
    } else if (vi.ok && en.ok) {
      if (!vi.revision || !en.revision || !versionRecords) {
        label = "Chưa kiểm tra được phiên bản";
      } else if (!record) {
        label = "Chưa đối chiếu";
      } else if (vi.revision !== record.vi) {
        label = "Cần cập nhật EN";
        state = "stale";
      } else if (en.revision !== record.en) {
        label = "Cần đối chiếu EN";
        state = "stale";
      } else {
        label = "Khớp bản đã đối chiếu";
        state = "ok";
      }
    }
    var ids = "VI " + (vi.ok && vi.revision ? vi.revision.slice(0, 8) : "—") +
      " · EN " + (en.ok && en.revision ? en.revision.slice(0, 8) : "—");
    var cardVersions = world?.querySelector('.card[data-id="' + c.id + '"] .doc-versions');
    var targets = currentDoc === c ? [cardVersions, viewerVersions] : [cardVersions];
    var message = tr(label);
    targets.forEach(function (node) {
      if (!node || (node.dataset.state === state && node.textContent === message + " " + ids)) return;
      node.dataset.state = state;
      node.replaceChildren(el("strong", null, message), " ", el("span", "doc-versions-ids", ids));
    });
  }

  function loadDoc(id, lang) {
    var s = st(id, lang);
    if (s.pending) return s.pending;
    var previousTag = s.etag;
    var headers = lang === "vi" && previousTag ? { "If-None-Match": previousTag } : {};
    s.pending = fetch(docUrl(id, lang), { headers: headers, cache: "no-store" })
      .then(function (r) {
        if (r.status === 304) {
          var recovered = s.ok !== true;
          s.ok = true;
          return recovered;
        }
        s.missing = r.status === 404;
        if (!r.ok) throw new Error(r.status);
        var tag = r.headers.get("ETag");
        return r.arrayBuffer().then(async function (bytes) {
          var md = new TextDecoder().decode(bytes);
          var revision = await docRevision(bytes);
          // Phản hồi bắt đầu trước lần lưu không được ghi lùi phiên bản trong bộ nhớ.
          if (s.etag !== previousTag) return false;
          var changed = md !== s.md || tag !== s.etag || s.ok !== true;
          s.md = md;
          s.etag = tag;
          s.revision = revision;
          s.ok = true;
          return changed;
        });
      })
      .catch(function () {
        var changed = s.ok !== false;
        s.ok = false;
        return changed;
      })
      .finally(function () { s.pending = null; });
    return s.pending;
  }

  function fillDocToc(c) {
    var toc = world?.querySelector('.card[data-id="' + c.id + '"] .doc-toc');
    if (!toc) return;
    toc.textContent = "";
    var s = st(c.doc, docLanguage(c));
    if (s.md == null) {
      toc.appendChild(el("span", "doc-toc-label", s.ok === null ? tr("Đang tải…") : tr("Không đọc được {file}", { file: mdName(c) })));
      return;
    }
    var heads = s.md.split("\n").map(window.DocMD.heading).filter(function (h) { return h && h.level === 2; });
    if (!heads.length) return;
    toc.appendChild(el("span", "doc-toc-label", tr("Mục lục")));
    heads.forEach(function (h, i) {
      var row = el("span", "doc-toc-row");
      row.appendChild(el("span", "doc-toc-no", String(i + 1).padStart(2, "0")));
      row.appendChild(el("span", "doc-toc-name", h.title.replace(/^\d+\.\s*/, "").replace(/[*`\\]/g, "")));
      toc.appendChild(row);
    });
  }

  function setSaveNote(text, state) {
    saveNote.textContent = text;
    saveNote.dataset.state = state || "";
  }

  function scrollToSection() {
    var heading = document.getElementById(location.hash.slice(1));
    if (heading && page.contains(heading)) heading.scrollIntoView();
  }

  function showPage(c, reloaded) {
    var lang = docLanguage(c);
    var s = st(c.doc, lang);
    pageVersion = s.md == null ? null : { md: s.md, etag: s.etag, lang: lang };
    dirty = false;
    page.contentEditable = String(!staticSite && language === "vi" && pageVersion !== null && !leavingDoc);
    setSaveNote("", "");
    if (pageVersion) {
      page.innerHTML = window.DocMD.toHtml(pageVersion.md);
      page.lang = lang;
      reviews.documentChanged(lang, true);
      if (lang !== language) setSaveNote(tr("Đang xem bản gốc tiếng Việt · chỉ đọc"));
      else if (language === "en") setSaveNote(tr("Bản dịch tiếng Anh · chỉ đọc"));
      else if (staticSite) setSaveNote(tr("Chế độ chỉ đọc"));
      else if (reloaded) setSaveNote(tr("Đã tải lại từ {file} (file vừa đổi)", { file: mdName(c) }), "ok");
      if (location.hash && !reloaded) scrollToSection();
      return;
    }
    page.replaceChildren(el("h1", null, tr(c.title)));
    reviews.documentChanged(lang, false);
    if (s.ok === null) {
      page.appendChild(el("p", null, tr("Đang tải…")));
      return;
    }
    page.appendChild(el("p", null, tr("Không đọc được {file}", { file: mdName(c) })));
    if (location.protocol === "file:" && !staticSite) {
      var path = decodeURIComponent(location.pathname).replace(/\/[^/]*$/, "");
      page.appendChild(el("p", null, tr("Chạy lệnh sau trong Terminal rồi mở {url}.", { url: SERVE_URL })));
      page.appendChild(el("code", null, 'python3 "' + path + '/serve.py"'));
    }
  }

  async function saveDoc() {
    clearTimeout(saveTimer);
    saveTimer = null;
    while (saving) {
      if (!await saving) return false;
    }
    if (staticSite || !dirty || !currentDoc || language !== "vi" || !pageVersion) return true;
    var c = currentDoc;
    var s = st(c.doc, "vi");
    var md = window.DocMD.toMd(page);
    dirty = false;
    if (md === pageVersion.md) {
      setSaveNote(tr("Đã lưu vào {file}", { file: mdName(c) }), "ok");
      return true;
    }
    setSaveNote(tr("Đang lưu…"), "busy");
    var headers = { "Content-Type": "text/markdown; charset=utf-8" };
    if (pageVersion.etag) headers["If-Match"] = pageVersion.etag;
    saving = fetch(docUrl(c.doc, "vi"), { method: "PUT", headers: headers, body: md })
      .then(async function (r) {
        if (r.status === 409) {
          // Tải phiên bản ngoài editor, kể cả khi một lần poll cũ còn đang chạy.
          if (s.pending) await s.pending;
          s.etag = null;
          await loadDoc(c.doc, "vi");
          if (!s.ok) throw new Error("Không tải lại được tài liệu");
          showPage(c);
          fillDocToc(c);
          renderDocVersions(c);
          setSaveNote(tr("{file} vừa được sửa ở ngoài · đã tải bản trên file", { file: mdName(c) }), "draft");
          return false;
        }
        if (!r.ok) throw new Error(r.status);
        var revision = await docRevision(new TextEncoder().encode(md));
        s.md = md;
        s.etag = r.headers.get("ETag");
        s.revision = revision;
        s.ok = true;
        pageVersion = { md: md, etag: s.etag, lang: "vi" };
        fillDocToc(c);
        renderDocVersions(c);
        if (!dirty) setSaveNote(tr("Đã lưu vào {file}", { file: mdName(c) }), "ok");
        return true;
      })
      .catch(function () {
        dirty = true;
        setSaveNote(tr("Không lưu được · kiểm tra serve.py còn chạy không"), "draft");
        return false;
      })
      .finally(function () { saving = null; });
    return saving;
  }

  async function afterDocSaved(action) {
    if (leavingDoc) return;
    if (!currentDoc || language === "en" || (!dirty && !saving)) { action(); return; }
    leavingDoc = true;
    page.contentEditable = "false";
    var saved;
    try {
      saved = await saveDoc();
    } finally {
      leavingDoc = false;
      page.contentEditable = "true";
    }
    if (saved) action();
  }

  function syncDocPair(c, records) {
    var editing = currentDoc === c && (dirty || saving);
    return Promise.all([!editing && loadDoc(c.doc, "vi"), loadDoc(c.doc, "en"), records])
      .then(function (changes) {
        if (changes[0] || changes[1]) fillDocToc(c);
        renderDocVersions(c);
        if (currentDoc !== c || dirty || saving) return;
        var lang = docLanguage(c);
        var s = st(c.doc, lang);
        var needsRender = pageVersion
          ? pageVersion.md !== s.md || pageVersion.etag !== s.etag || pageVersion.lang !== lang
          : changes[0] || changes[1];
        if (needsRender) showPage(c, pageVersion?.lang === lang);
      });
  }

  function poll() {
    var records = loadVersionRecords();
    var docs = currentDoc ? [currentDoc] : docCards();
    var jobs = docs.map(function (c) { return syncDocPair(c, records); });
    if (world) jobs.push(refreshDiagrams());
    return Promise.all(jobs);
  }

  // ---------- Sơ đồ vẽ từ bảng trong tài liệu ----------
  function diagramCards() { return cards.filter(function (c) { return c.kind === "diagram"; }); }

  function renderDiagramCard(c) {
    var b = el("a", "card diagram");
    b.href = reportHref(c.doc, c.section);
    b.dataset.id = c.id;
    b.dataset.region = c.region || "dynamics";
    b.style.left = c.x + "px";
    b.style.top = c.y + "px";
    var head = el("span", "doc-head");
    head.appendChild(el("span", "doc-kicker", tr(c.eyebrow)));
    b.appendChild(head);
    b.appendChild(el("span", "doc-title", tr(c.title)));
    if (c.summary) b.appendChild(el("span", "doc-sub", tr(c.summary)));
    b.appendChild(el("span", "diagram-body", tr("Đang tải sơ đồ…")));
    var cta = el("span", "card-cta", tr("Xem bảng chi tiết trong Research"));
    cta.insertAdjacentHTML("beforeend", ICON_ARROW);
    b.appendChild(cta);
    world.appendChild(b);
  }

  // Sơ đồ luôn đọc bản tiếng Việt, là bản gốc của bảng.
  function refreshDiagrams() {
    if (!window.SpecDiagrams) return Promise.resolve();
    return Promise.all(diagramCards().map(function (c) {
      return loadDoc(c.doc, "vi").then(function () {
        var card = world.querySelector('.card[data-id="' + c.id + '"]');
        var body = card && card.querySelector(".diagram-body");
        var md = st(c.doc, "vi").md;
        if (!body || !md || card._diagramMd === md) return;
        card._diagramMd = md;
        var out = window.SpecDiagrams.render(c.diagram, md, { section: c.section, lanes: c.lanes, tr: tr });
        if (out.node) body.replaceChildren(out.node);
        else body.replaceChildren(el("span", "diagram-error", tr("Không vẽ được sơ đồ: {reason}", { reason: out.error })));
      });
    }));
  }

  page?.addEventListener("input", function () {
    if (language !== "vi" || !page.isContentEditable) return;
    dirty = true;
    clearTimeout(saveTimer);
    setSaveNote(tr("Chưa lưu…"), "busy");
    saveTimer = setTimeout(saveDoc, 700);
  });
  // Dán chỉ lấy chữ, để định dạng lạ từ nơi khác không làm hỏng trang.
  page?.addEventListener("paste", function (e) {
    if (!page.isContentEditable) return;
    e.preventDefault();
    var text = (e.clipboardData || window.clipboardData).getData("text/plain");
    document.execCommand("insertText", false, text);
  });
  // Lưu bản đang sửa trước khi mở báo cáo được liên kết.
  page?.addEventListener("click", function (e) {
    var link = e.target.closest('a[href^="report.html?"]');
    if (!link || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    afterDocSaved(function () { location.assign(link.href); });
  });
  if (currentDoc) window.addEventListener("hashchange", scrollToSection);

  // Lưu bản tiếng Việt trước khi bấm liên kết về bản đồ.
  backLink?.addEventListener("click", function (e) {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || (!dirty && !saving)) return;
    e.preventDefault();
    afterDocSaved(function () { location.assign(backLink.href); });
  });
  if (currentDoc && !staticSite) {
    window.addEventListener("beforeunload", function (e) {
      if (!dirty && !saving) return;
      e.preventDefault();
      e.returnValue = "";
    });
  }

  function renderCards() {
    cards.forEach(function (c) {
      if (c.kind === "doc") { renderDocCard(c); return; }
      if (c.kind === "diagram") { renderDiagramCard(c); return; }
      var b = el("a", "card" + (c.group ? " " + c.group : ""));
      b.href = reportHref(c.research.doc, c.research.section);
      b.dataset.id = c.id;
      b.dataset.region = c.group === "sim" ? "simulation" : "vehicle";
      b.style.left = c.x + "px";
      b.style.top = c.y + "px";

      var top = el("span", "card-top");
      var icon = el("span", "card-icon");
      icon.innerHTML = ICONS[c.icon] || ICON_STEER;
      top.appendChild(icon);
      b.appendChild(top);

      b.appendChild(el("span", "card-title", tr(c.title)));
      b.appendChild(el("span", "card-summary", tr(c.summary)));
      var cta = el("span", "card-cta", tr("Đọc trong Research"));
      cta.insertAdjacentHTML("beforeend", ICON_ARROW);
      b.appendChild(cta);
      world.appendChild(b);
    });
  }

  var regionLayer = el("div", "map-regions");
  var regionObserver = world && new ResizeObserver(layoutRegions);

  function renderRegions() {
    regionLayer.replaceChildren();
    (window.SPEC_REGIONS || []).forEach(function (r) {
      var frame = el("div", "map-region");
      frame.dataset.region = r.id;
      var heading = el("h2", "region-label");
      if (r.id === "docs") {
        var link = el("a", "region-link", tr(r.text));
        link.href = reportHref();
        heading.appendChild(link);
      } else {
        heading.textContent = tr(r.text);
      }
      frame.appendChild(heading);
      if (r.note) frame.appendChild(el("p", "region-note", tr(r.note)));
      regionLayer.appendChild(frame);
    });
    layoutRegions();
    regionObserver.disconnect();
    world.querySelectorAll(".card").forEach(function (card) { regionObserver.observe(card); });
  }

  function layoutRegions() {
    var padding = 42;
    var header = 108;
    regionLayer.querySelectorAll(".map-region").forEach(function (frame) {
      var nodes = world.querySelectorAll('.card[data-region="' + frame.dataset.region + '"]');
      var bounds = boundsOf(nodes);
      frame.hidden = !bounds;
      if (!bounds) return;
      frame.style.left = bounds.minX - padding + "px";
      frame.style.top = bounds.minY - header + "px";
      frame.style.width = bounds.maxX - bounds.minX + 2 * padding + "px";
      frame.style.height = bounds.maxY - bounds.minY + header + padding + "px";
    });
  }

  // ---------- Đường dữ liệu ----------
  var edges = window.SPEC_EDGES || [];
  var SVGNS = "http://www.w3.org/2000/svg";
  var edgeLayer = document.createElementNS(SVGNS, "svg");
  edgeLayer.setAttribute("class", "edges");
  edgeLayer.setAttribute("width", "1");
  edgeLayer.setAttribute("height", "1");
  edgeLayer.setAttribute("aria-hidden", "true");
  var labelLayer = el("div", "edge-labels");

  function cardTitle(id) {
    var c = cards.find(function (x) { return x.id === id; });
    return c ? tr(c.title) : id;
  }

  function rectOf(id) {
    var n = world.querySelector('.card[data-id="' + id + '"]');
    return n && { x: n.offsetLeft, y: n.offsetTop, w: n.offsetWidth, h: n.offsetHeight };
  }

  // Điểm trên mép hình chữ nhật r theo hướng (ux, uy) tính từ tâm, lùi ra thêm margin px.
  function boundary(r, ux, uy, margin) {
    var tx = ux ? (r.w / 2) / Math.abs(ux) : Infinity;
    var ty = uy ? (r.h / 2) / Math.abs(uy) : Infinity;
    var t = Math.min(tx, ty) + margin;
    return { x: r.x + r.w / 2 + ux * t, y: r.y + r.h / 2 + uy * t };
  }

  var MARKERS =
    '<defs>' +
    '<marker id="arr-in" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">' +
    '<path d="M1 1L8 5L1 9" fill="none" stroke="#AEAEB2" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></marker>' +
    '<marker id="arr-out" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">' +
    '<path d="M1 1L8 5L1 9" fill="none" stroke="#5B3DF5" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></marker>' +
    '</defs>';

  function drawEdges() {
    edgeLayer.innerHTML = MARKERS;
    labelLayer.textContent = "";
    edges.forEach(function (e) {
      var a = rectOf(e.from), b = rectOf(e.to);
      if (!a || !b) return;
      var out = e.from === "path-planner";
      var d, lx, ly;
      if (e.from === e.to) {
        // Vòng tự nối ở góc trên bên phải thẻ.
        var p0 = { x: a.x + a.w - 90, y: a.y - 8 }, p1 = { x: a.x + a.w + 8, y: a.y + 45 };
        d = "M" + p0.x + " " + p0.y + " C" + p0.x + " " + (p0.y - 170) + " " + (p1.x + 170) + " " + p1.y + " " + p1.x + " " + p1.y;
        lx = a.x + a.w + 60;
        ly = a.y - 95;
      } else {
        var ax = a.x + a.w / 2, ay = a.y + a.h / 2, bx = b.x + b.w / 2, by = b.y + b.h / 2;
        var L = Math.hypot(bx - ax, by - ay), ux = (bx - ax) / L, uy = (by - ay) / L;
        var s = boundary(a, ux, uy, 6), t = boundary(b, -ux, -uy, 12);
        // Hai chiều giữa cùng hai thẻ: tách hai đường song song, nhãn nằm hai bên.
        var paired = edges.some(function (f) { return f.from === e.to && f.to === e.from; });
        var nx = -uy, ny = ux, off = paired ? 12 : 0, loff = paired ? 36 : 0;
        s.x += nx * off; s.y += ny * off; t.x += nx * off; t.y += ny * off;
        d = "M" + s.x + " " + s.y + " L" + t.x + " " + t.y;
        lx = (s.x + t.x) / 2 + nx * loff;
        ly = (s.y + t.y) / 2 + ny * loff;
      }
      var path = document.createElementNS(SVGNS, "path");
      path.setAttribute("d", d);
      path.setAttribute("class", "edge" + (out ? " out" : "") + (e.can ? " can" : ""));
      path.setAttribute("marker-end", out ? "url(#arr-out)" : "url(#arr-in)");
      edgeLayer.appendChild(path);

      var link = el("a", "edge-label" + (out ? " out" : ""), tr(e.label));
      link.href = reportHref(e.research.doc, e.research.section);
      link.dataset.id = e.id;
      link.style.left = lx + "px";
      link.style.top = ly + "px";
      link.setAttribute("aria-label", tr("Dữ liệu {from} gửi tới {to}: {label}", {
        from: cardTitle(e.from), to: cardTitle(e.to), label: tr(e.label)
      }));
      labelLayer.appendChild(link);
    });
  }



  // ---------- Pan / zoom ----------
  function clampK(k) { return Math.min(MAX_K, Math.max(MIN_K, k)); }

  function apply() {
    world.style.transform = "translate(" + view.x + "px," + view.y + "px) scale(" + view.k + ")";
    // Giữ khoảng cách chấm lưới trong 16–48 px để lưới không quá dày khi thu nhỏ.
    var g = GRID * view.k;
    while (g < 16) g *= 2;
    while (g > 48) g /= 2;
    viewport.style.backgroundSize = g + "px " + g + "px";
    viewport.style.backgroundPosition = view.x + "px " + view.y + "px";
    zoomLabel.textContent = Math.round(view.k * 100) + "%";
  }

  // Phóng to/thu nhỏ quanh điểm (sx, sy) trên màn hình, điểm đó đứng yên.
  function zoomAt(sx, sy, k) {
    k = clampK(k);
    var wx = (sx - view.x) / view.k;
    var wy = (sy - view.y) / view.k;
    view.k = k;
    view.x = sx - wx * k;
    view.y = sy - wy * k;
    apply();
  }

  function animateTo(target, ms) {
    var from = { x: view.x, y: view.y, k: view.k };
    var t0 = performance.now();
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) ms = 0;
    function step(now) {
      var t = ms ? Math.min(1, (now - t0) / ms) : 1;
      var e = 1 - Math.pow(1 - t, 3);
      view.x = from.x + (target.x - from.x) * e;
      view.y = from.y + (target.y - from.y) * e;
      view.k = from.k + (target.k - from.k) * e;
      apply();
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function zoomBy(factor) {
    var r = viewport.getBoundingClientRect();
    var cx = r.width / 2, cy = r.height / 2;
    var k = clampK(view.k * factor);
    var wx = (cx - view.x) / view.k, wy = (cy - view.y) / view.k;
    animateTo({ k: k, x: cx - wx * k, y: cy - wy * k }, 180);
  }

  function boundsOf(nodes) {
    if (!nodes.length) return null;
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    nodes.forEach(function (n) {
      var x = n.offsetLeft, y = n.offsetTop;
      minX = Math.min(minX, x); minY = Math.min(minY, y);
      maxX = Math.max(maxX, x + n.offsetWidth); maxY = Math.max(maxY, y + n.offsetHeight);
    });
    return { minX: minX, minY: minY, maxX: maxX, maxY: maxY };
  }

  function fit(animate) {
    layoutRegions();
    var bounds = boundsOf(world.querySelectorAll(".card, .map-region:not([hidden])"));
    if (!bounds) return;
    var width = bounds.maxX - bounds.minX, height = bounds.maxY - bounds.minY;
    var r = viewport.getBoundingClientRect();
    var padTop = 76, padBottom = 32, pad = 32;
    var availW = r.width - pad * 2, availH = r.height - padTop - padBottom;
    var k = clampK(Math.min(1, availW / width, availH / height));
    var target = {
      k: k,
      x: pad + (availW - width * k) / 2 - bounds.minX * k,
      y: padTop + (availH - height * k) / 2 - bounds.minY * k
    };
    if (animate) animateTo(target, 260);
    else { view = target; apply(); }
  }

  // Trackpad: chụm hai ngón (trình duyệt gửi wheel kèm ctrlKey) = zoom,
  //           hai ngón di chuyển cùng nhau (wheel thường) = di chuyển bản đồ.
  // Chuột có bánh lăn: lăn = zoom như Google Maps.
  function looksLikeMouseWheel(e) {
    if (e.deltaMode !== 0) return true; // cuộn theo dòng/trang: chuột
    // Bánh lăn chuột thường cho bước lớn, nguyên, chỉ theo trục dọc.
    return e.deltaX === 0 && Number.isInteger(e.deltaY) && Math.abs(e.deltaY) >= 50;
  }

  viewport?.addEventListener("wheel", function (e) {
    e.preventDefault();
    var r = viewport.getBoundingClientRect();
    var sx = e.clientX - r.left, sy = e.clientY - r.top;

    if (e.ctrlKey || e.metaKey) {
      zoomAt(sx, sy, view.k * Math.exp(-e.deltaY * 0.01));
    } else if (looksLikeMouseWheel(e)) {
      var dy = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
      zoomAt(sx, sy, view.k * Math.exp(-dy * 0.0018));
    } else {
      view.x -= e.deltaX;
      view.y -= e.deltaY;
      apply();
    }
  }, { passive: false });

  // Kéo bằng chuột/chạm, chụm hai ngón để zoom.
  var pointers = new Map();
  var drag = null;   // { startX, startY, viewX, viewY, moved, hit }
  var pinch = null;  // { dist, k, wx, wy }

  function midpoint() {
    var pts = Array.from(pointers.values());
    return { x: (pts[0].x + pts[1].x) / 2, y: (pts[0].y + pts[1].y) / 2, d: Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y) };
  }

  viewport?.addEventListener("pointerdown", function (e) {
    if (e.button !== 0 && e.pointerType === "mouse") return;
    var hit = e.target.closest(".card, .edge-label, .region-link");
    if (hit?.href && (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey)) return;
    var r = viewport.getBoundingClientRect();
    pointers.set(e.pointerId, { x: e.clientX - r.left, y: e.clientY - r.top });
    viewport.setPointerCapture(e.pointerId);

    if (pointers.size === 1) {
      drag = {
        startX: e.clientX, startY: e.clientY, viewX: view.x, viewY: view.y, moved: false,
        hit: hit
      };
    } else if (pointers.size === 2) {
      var m = midpoint();
      pinch = { dist: m.d, k: view.k, wx: (m.x - view.x) / view.k, wy: (m.y - view.y) / view.k };
      if (drag) drag.moved = true; // đang chụm thì không tính là bấm thẻ
    }
  });

  viewport?.addEventListener("pointermove", function (e) {
    if (!pointers.has(e.pointerId)) return;
    var r = viewport.getBoundingClientRect();
    pointers.set(e.pointerId, { x: e.clientX - r.left, y: e.clientY - r.top });

    if (pinch && pointers.size >= 2) {
      var m = midpoint();
      var k = clampK(pinch.k * (m.d / pinch.dist));
      view.k = k;
      view.x = m.x - pinch.wx * k;
      view.y = m.y - pinch.wy * k;
      apply();
      return;
    }
    if (!drag) return;
    var dx = e.clientX - drag.startX, dy = e.clientY - drag.startY;
    if (!drag.moved && Math.hypot(dx, dy) > DRAG_THRESHOLD) {
      drag.moved = true;
      viewport.classList.add("is-panning");
    }
    if (drag.moved) {
      view.x = drag.viewX + dx;
      view.y = drag.viewY + dy;
      apply();
    }
  });

  function endPointer(e) {
    if (!pointers.has(e.pointerId)) return;
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinch = null;
    if (pointers.size === 1 && drag) {
      // Còn một ngón: tiếp tục kéo từ vị trí hiện tại.
      var p = Array.from(pointers.values())[0];
      var r = viewport.getBoundingClientRect();
      drag = { startX: p.x + r.left, startY: p.y + r.top, viewX: view.x, viewY: view.y, moved: true, hit: null };
      return;
    }
    if (pointers.size === 0) {
      if (drag && !drag.moved && drag.hit && e.type === "pointerup") {
        location.assign(drag.hit.href);
      }
      drag = null;
      viewport.classList.remove("is-panning");
    }
  }
  viewport?.addEventListener("pointerup", endPointer);
  viewport?.addEventListener("pointercancel", endPointer);

  // Phím tắt khi bản đồ đang được focus.
  viewport?.addEventListener("keydown", function (e) {
    if (e.target !== viewport) return;
    var step = 80;
    var handled = true;
    switch (e.key) {
      case "+": case "=": zoomBy(1.25); break;
      case "-": case "_": zoomBy(0.8); break;
      case "0": fit(true); break;
      case "ArrowLeft": view.x += step; apply(); break;
      case "ArrowRight": view.x -= step; apply(); break;
      case "ArrowUp": view.y += step; apply(); break;
      case "ArrowDown": view.y -= step; apply(); break;
      default: handled = false;
    }
    if (handled) e.preventDefault();
  });

  document.getElementById("zoom-in")?.addEventListener("click", function () { zoomBy(1.25); });
  document.getElementById("zoom-out")?.addEventListener("click", function () { zoomBy(0.8); });
  document.getElementById("zoom-fit")?.addEventListener("click", function () { fit(true); });

  function renderReport() {
    backLink.href = "index.html?lang=" + language;
    document.title = tr(currentDoc ? currentDoc.title : "Báo cáo Research");
    if (currentDoc) {
      showPage(currentDoc);
      renderDocVersions(currentDoc);
      return poll();
    }

    page.classList.add("report-index");
    page.replaceChildren(el("h1", null, tr("Báo cáo Research")));
    if (requestedDoc !== null) {
      page.appendChild(el("p", null, tr("Không tìm thấy báo cáo.")));
      return;
    }
    page.appendChild(el("p", null, tr("Nguồn chính thức cho yêu cầu, thiết kế, interface và đánh giá của G1.")));
    var list = el("ul", "report-list");
    docCards().forEach(function (c) {
      var row = el("li");
      var link = el("a", null, tr(c.title));
      link.href = reportHref(c.doc);
      row.appendChild(link);
      if (c.summary) row.appendChild(el("p", null, tr(c.summary)));
      list.appendChild(row);
    });
    page.appendChild(list);
  }

  function renderLanguage() {
    document.documentElement.lang = language;
    interfaceText.forEach(function (item) {
      if (item.attribute) item.node.setAttribute(item.attribute, tr(item.text));
      else item.node.textContent = tr(item.text);
    });
    languageButtons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.lang === language));
    });

    if (!world) return renderReport();
    document.title = tr("Bản đồ yêu cầu");
    world.replaceChildren(regionLayer, edgeLayer); // khung và đường nằm dưới thẻ
    renderCards();
    world.appendChild(labelLayer);   // nhãn nằm trên thẻ
    docCards().forEach(function (c) { fillDocToc(c); renderDocVersions(c); });
    renderRegions();
    drawEdges();

    return poll();
  }

  languageButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      if (button.lang === language) return;
      afterDocSaved(function () {
        language = button.lang;
        try { localStorage.setItem(LANGUAGE_KEY, language); } catch (err) { /* vẫn đổi trong tab hiện tại */ }
        if (location.protocol !== "file:" && (page || route.has("lang"))) {
          var url = new URL(location.href);
          url.searchParams.set("lang", language);
          history.replaceState(history.state, "", url);
        }
        renderLanguage();
      });
    });
  });

  var initialLanguage = language;
  var initialDocs = renderLanguage();
  if (world) {
    fit(false);
    // Mục lục tải xong có thể làm thẻ cao hơn. Căn lại nếu người dùng chưa đổi góc nhìn.
    var initialView = { x: view.x, y: view.y, k: view.k };
    initialDocs.then(function () {
      if (language === initialLanguage && view.x === initialView.x && view.y === initialView.y && view.k === initialView.k) fit(false);
    });
    // Font tải xong có thể đổi chiều cao thẻ, vẽ lại đường cho khớp mép thẻ.
    document.fonts?.ready.then(drawEdges);
  }
  if (currentDoc && !staticSite) {
    try { document.execCommand("defaultParagraphSeparator", false, "p"); } catch (err) { /* bỏ qua */ }
  }
  if (!staticSite && (world || currentDoc)) {
    setInterval(function () {
      if (document.visibilityState !== "hidden") poll();
    }, POLL_MS);
  }
})();
