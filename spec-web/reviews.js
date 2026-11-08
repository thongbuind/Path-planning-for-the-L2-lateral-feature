(function () {
  "use strict";

  const QUOTE_LIMIT = 4096;
  const CONTEXT = 48;
  const MIN_MATCHING_CONTEXT = 8;
  const GITHUB_URL_LIMIT = 6000;

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function button(text, className = "review-button") {
    const node = el("button", className, text);
    node.type = "button";
    return node;
  }

  function newId() {
    const bytes = crypto.getRandomValues(new Uint8Array(16));
    return Array.from(bytes, byte => byte.toString(16).padStart(2, "0")).join("");
  }

  function textIndex(page) {
    const walker = document.createTreeWalker(page, NodeFilter.SHOW_TEXT);
    const nodes = [];
    let text = "";
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (!node.length) continue;
      nodes.push({ node, start: text.length });
      text += node.data;
    }
    return { text, nodes };
  }

  function locate(text, anchor, revision) {
    const { start, quote, prefix, suffix } = anchor;
    if (revision && revision === anchor.revision && text.slice(start, start + quote.length) === quote) return start;
    const first = text.indexOf(quote);
    if (first < 0) return -1;
    if (anchor.multiple === false && quote.length >= 16 && text.indexOf(quote, first + 1) < 0) return first;

    // Đoạn ngắn hoặc từng lặp lại cần khớp thêm ngữ cảnh trước khi gắn thẻ.
    let best = -1;
    let bestScore = Math.min(MIN_MATCHING_CONTEXT, prefix.length + suffix.length) - 1;
    for (let offset = first; offset >= 0; offset = text.indexOf(quote, offset + 1)) {
      let before = 0;
      let after = 0;
      while (before < prefix.length && offset > before &&
             text[offset - 1 - before] === prefix[prefix.length - 1 - before]) before++;
      const end = offset + quote.length;
      while (after < suffix.length && text[end + after] === suffix[after]) after++;
      const score = before + after;
      if (score > bestScore) {
        best = offset;
        bestScore = score;
      } else if (score === bestScore) {
        best = -1;
      }
    }
    return best;
  }

  function rangeAt(index, start, length) {
    const end = start + length;
    const left = index.nodes.find(part => part.start + part.node.length > start);
    const right = index.nodes.find(part => part.start + part.node.length >= end);
    if (!left || !right) return null;
    const range = document.createRange();
    range.setStart(left.node, start - left.start);
    range.setEnd(right.node, end - right.start);
    return range;
  }

  function githubRepository() {
    const configured = document.querySelector('meta[name="github-repository"]')?.content.trim();
    const owner = /^([a-z\d-]+)\.github\.io$/i.exec(location.hostname)?.[1];
    const projectPath = location.pathname.split("/").filter(Boolean).slice(0, -1)[0];
    const repo = configured || (owner ? owner + "/" + (projectPath || owner + ".github.io") : "");
    return /^[a-z\d][a-z\d-]{0,38}\/(?!\.{1,2}$)[a-z\d_.-]{1,100}$/i.test(repo) ? repo : "";
  }

  function fenced(text) {
    const runs = text.match(/`+/g) || [];
    const fence = "`".repeat(runs.reduce((size, run) => Math.max(size, run.length + 1), 3));
    return fence + "text\n" + text + "\n" + fence;
  }

  function mount({ page, docId, mergedDraftDoc, staticSite, tr, reportTitle, revision }) {
    const listButton = document.getElementById("review-list");
    const prompt = document.getElementById("review-prompt");
    const marks = document.getElementById("review-marks");
    const panel = document.getElementById("review-panel");
    const title = document.getElementById("review-title");
    const closeButton = document.getElementById("review-close");
    const content = document.getElementById("review-content");
    const form = document.getElementById("review-form");
    const input = document.getElementById("review-input");
    const saveButton = document.getElementById("review-save");
    const cancelEdit = document.getElementById("review-cancel-edit");
    const status = document.getElementById("review-status");
    const storagePrefix = "spec-web.reviews:" + new URL(".", location.href).pathname + ":";
    const storageKey = storagePrefix + docId;
    const endpoint = "api/reviews/" + encodeURIComponent(docId);

    let reviews = [];
    let language = "vi";
    let available = false;
    let selection = null;
    let mode = "";
    let activeAnchor = null;
    let editing = null;
    let draftId = null;
    let returnFocus = null;
    let panelPoint = null;
    let busy = false;
    let requestVersion = 0;
    let loadError = "";
    let drawFrame = 0;
    let selecting = false;
    let showDone = false;

    // Nhận xét đã xong bị ẩn khỏi trang và danh sách, trừ khi người đọc bật xem lại.
    const isDone = item => item.resolved === true;
    const openReviews = () => reviews.filter(item => !isDone(item));
    const visibleReviews = () => showDone ? reviews : openReviews();

    function updateCount() {
      listButton.textContent = tr("Nhận xét ({count})", { count: openReviews().length });
    }

    function readStoredDrafts(report) {
      const raw = localStorage.getItem(storagePrefix + report);
      if (!raw) return { report, nextNumber: 1, reviews: [] };
      const data = JSON.parse(raw);
      if (data?.report !== report || !Number.isSafeInteger(data.nextNumber) || !Array.isArray(data.reviews)) {
        throw new Error("invalid_reviews");
      }
      return data;
    }

    function readDrafts() {
      const data = readStoredDrafts(docId);
      if (!mergedDraftDoc) return data;

      let merged;
      try {
        merged = readStoredDrafts(mergedDraftDoc);
      } catch {
        return data;
      }
      // Giữ ID để các lần đọc và lưu sau nhận ra nháp đã được gộp.
      const ids = new Set(data.reviews.map(item => item.id));
      for (const item of merged.reviews) {
        if (!item?.id || !item.anchor || ids.has(item.id)) continue;
        data.reviews.push({ ...item, number: data.nextNumber++, sourceDoc: mergedDraftDoc });
        ids.add(item.id);
      }
      return data;
    }

    async function readResponse(response) {
      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        const error = new Error(details.error || String(response.status));
        error.status = response.status;
        error.review = details.review;
        throw error;
      }
      return response.json();
    }

    function needsServerRestart(error) {
      return !staticSite && (
        error.status === 405 || error.status === 501 ||
        (error.status === 404 && error.message === "404")
      );
    }

    async function refresh() {
      const request = ++requestVersion;
      try {
        const data = staticSite ? readDrafts() :
          await readResponse(await fetch(endpoint, { cache: "no-store" }));
        if (request !== requestVersion || busy) return;
        loadError = "";
        if (status.dataset.loadError) setStatus("");
        setReviews(data);
      } catch (error) {
        if (request !== requestVersion || busy) return;
        loadError = needsServerRestart(error) ?
          "Khởi động lại serve.py để dùng nhận xét." : "Không đọc được nhận xét.";
        setStatus(loadError, true);
      }
    }

    function setReviews(data) {
      if (!Array.isArray(data?.reviews)) throw new Error("invalid_reviews");
      reviews = data.reviews;
      updateCount();
      scheduleMarks();
      if (mode) renderPanel();
    }

    function setStatus(key, fromLoad = false) {
      status.textContent = key ? tr(key) : "";
      status.dataset.loadError = fromLoad ? "true" : "";
    }

    function samePassage(a, b, text) {
      if (a.language !== b.language || a.quote !== b.quote) return false;
      if (available && a.language === language) {
        const left = locate(text, a, revision());
        const right = locate(text, b, revision());
        if (left >= 0 && right >= 0) return left === right;
      }
      return a.start === b.start && a.prefix === b.prefix && a.suffix === b.suffix;
    }

    function selectionAnchor() {
      if (!available) return null;
      const selected = window.getSelection();
      if (!selected?.rangeCount || selected.isCollapsed) return null;
      const range = selected.getRangeAt(0);
      if (!page.contains(range.startContainer) || !page.contains(range.endContainer)) return null;
      const raw = range.toString();
      const quote = raw.trim();
      const excerpt = selected.toString().trim();
      if (!quote || !excerpt) return null;
      const before = document.createRange();
      before.selectNodeContents(page);
      before.setEnd(range.startContainer, range.startOffset);
      const start = before.toString().length + raw.indexOf(quote);
      const text = page.textContent;
      const end = start + quote.length;
      return {
        range: range.cloneRange(),
        anchor: {
          language, revision: revision(), start, quote, excerpt,
          multiple: text.indexOf(quote) !== start || text.indexOf(quote, start + 1) >= 0,
          prefix: text.slice(Math.max(0, start - CONTEXT), start).replace(/^[\uDC00-\uDFFF]/, ""),
          suffix: text.slice(end, end + CONTEXT).replace(/[\uD800-\uDBFF]$/, ""),
        },
      };
    }

    function headerBottom() {
      return document.querySelector(".report-header").getBoundingClientRect().bottom;
    }

    function clamp(value, min, max) {
      return Math.max(min, Math.min(value, max));
    }

    function updatePrompt() {
      if (selecting || busy) {
        prompt.hidden = true;
        return;
      }
      selection = selectionAnchor();
      if (!selection) {
        prompt.hidden = true;
        return;
      }
      const rects = Array.from(selection.range.getClientRects()).filter(rect => rect.width && rect.height);
      const minTop = headerBottom() + 8;
      const visible = rects.filter(rect => rect.bottom > minTop && rect.top < window.innerHeight);
      const rect = visible[visible.length - 1];
      if (!rect) {
        prompt.hidden = true;
        return;
      }
      prompt.hidden = false;
      const left = clamp(rect.right - prompt.offsetWidth, 8, document.documentElement.clientWidth - prompt.offsetWidth - 8);
      const above = rect.top - prompt.offsetHeight - 6;
      const top = above >= minTop ? above : Math.min(rect.bottom + 6, window.innerHeight - prompt.offsetHeight - 8);
      prompt.style.left = left + "px";
      prompt.style.top = top + "px";
    }

    function scheduleMarks() {
      if (drawFrame) return;
      drawFrame = requestAnimationFrame(() => {
        drawFrame = 0;
        drawMarks();
        updatePrompt();
      });
    }

    function drawMarks() {
      marks.replaceChildren();
      const shown = visibleReviews();
      if (!available || !shown.length) return;
      const index = textIndex(page);
      const groups = new Map();
      const documentRevision = revision();
      for (const item of shown) {
        if (item.anchor.language !== language) continue;
        const start = locate(index.text, item.anchor, documentRevision);
        if (start < 0) continue;
        const key = start + ":" + item.anchor.quote.length;
        if (!groups.has(key)) groups.set(key, { start, items: [] });
        groups.get(key).items.push(item);
      }
      const pageRect = page.getBoundingClientRect();
      const layerRect = marks.getBoundingClientRect();
      const right = Math.max(6, layerRect.right - pageRect.right - 60);
      let nextTop = 0;
      for (const group of Array.from(groups.values()).sort((a, b) => a.start - b.start)) {
        const anchor = group.items[0].anchor;
        const range = rangeAt(index, group.start, anchor.quote.length);
        const rects = Array.from(range?.getClientRects() || []).filter(rect =>
          rect.height > 0 && rect.width > 0 && rect.right > pageRect.left && rect.left < pageRect.right);
        if (!rects.length) continue;
        for (const rect of rects) {
          const highlight = el("span", "review-mark-line");
          highlight.setAttribute("aria-hidden", "true");
          highlight.style.left = Math.max(rect.left, pageRect.left) - layerRect.left + "px";
          highlight.style.top = rect.bottom - layerRect.top - 2 + "px";
          highlight.style.width = Math.min(rect.right, pageRect.right) - Math.max(rect.left, pageRect.left) + "px";
          marks.appendChild(highlight);
        }
        const numbers = group.items.map(item => "#" + item.number);
        const label = numbers.slice(0, 2).join(" ") + (numbers.length > 2 ? " +" + (numbers.length - 2) : "");
        const marker = button(label, "review-marker" + (group.items.every(isDone) ? " review-done" : ""));
        marker.setAttribute("aria-label", tr("Nhận xét {numbers}", { numbers: numbers.join(", ") }));
        marker.setAttribute("aria-controls", panel.id);
        const top = Math.max(rects[0].top - layerRect.top - 4, nextTop);
        marker.style.top = top + "px";
        marker.style.right = right + "px";
        nextTop = top + 34;
        marker.addEventListener("click", () => openThread(anchor, marker.getBoundingClientRect(), marker, false));
        marks.appendChild(marker);
      }
    }

    function positionPanel() {
      if (!panelPoint) return;
      const left = clamp(panelPoint.right + 8, 12, document.documentElement.clientWidth - panel.offsetWidth - 12);
      const top = clamp(panelPoint.top, headerBottom() + 8, window.innerHeight - panel.offsetHeight - 12);
      panel.style.left = left + "px";
      panel.style.top = top + "px";
    }

    function openPanel(nextMode, point, trigger) {
      mode = nextMode;
      panelPoint = point;
      returnFocus = trigger;
      panel.hidden = false;
      listButton.setAttribute("aria-expanded", "true");
      prompt.hidden = true;
      setStatus(loadError, Boolean(loadError));
      renderPanel();
      content.scrollTop = 0;
    }

    function showAll(point, trigger) {
      if (busy) return;
      editing = null;
      input.value = "";
      openPanel("all", point, trigger);
      closeButton.focus({ preventScroll: true });
      refresh();
    }

    function openThread(anchor, point, trigger, compose) {
      if (busy) return;
      activeAnchor = anchor;
      editing = null;
      draftId = newId();
      input.value = "";
      openPanel("thread", point, trigger);
      (compose ? input : closeButton).focus({ preventScroll: true });
    }

    function hidePanel() {
      if (busy) return;
      panel.hidden = true;
      mode = "";
      editing = null;
      input.value = "";
      listButton.setAttribute("aria-expanded", "false");
      (returnFocus?.isConnected && !returnFocus.hidden ? returnFocus : listButton).focus({ preventScroll: true });
    }

    function edit(item) {
      if (busy) return;
      editing = item;
      input.value = item.body;
      setStatus("");
      renderPanel();
      input.focus();
    }

    async function setDone(item, done) {
      if (busy) return;
      busy = true;
      ++requestVersion;
      setStatus(done ? "Đang đánh dấu đã xong…" : "Đang mở lại nhận xét…");
      try {
        const data = await persist({ id: item.id, resolved: done }, false);
        loadError = "";
        setReviews(data);
        setStatus(done ? "Đã đánh dấu xong." : "Đã mở lại nhận xét.");
      } catch (error) {
        setStatus(needsServerRestart(error) ?
          "Khởi động lại serve.py để dùng nhận xét." : "Không đổi được trạng thái nhận xét.");
      } finally {
        busy = false;
      }
    }

    function showReview(item) {
      if (busy) return;
      let point = listButton.getBoundingClientRect();
      if (available && item.anchor.language === language) {
        const index = textIndex(page);
        const offset = locate(index.text, item.anchor, revision());
        const range = offset >= 0 && rangeAt(index, offset, item.anchor.quote.length);
        if (range) {
          const rect = range.getBoundingClientRect();
          window.scrollBy(0, rect.top - window.innerHeight / 3);
          point = range.getBoundingClientRect();
        }
      }
      openThread(item.anchor, point, listButton, false);
    }

    function toolbar() {
      const actions = el("div", "review-nav");
      if (mode !== "all") {
        const all = button(tr("Tất cả nhận xét"));
        all.addEventListener("click", () => showAll(panelPoint, returnFocus));
        actions.appendChild(all);
      }
      const doneCount = reviews.length - openReviews().length;
      if (mode !== "share" && doneCount) {
        const toggle = button(showDone ?
          tr("Ẩn nhận xét đã xong") : tr("Xem nhận xét đã xong ({count})", { count: doneCount }));
        toggle.setAttribute("aria-pressed", String(showDone));
        toggle.addEventListener("click", () => {
          if (busy) return;
          showDone = !showDone;
          renderPanel();
          scheduleMarks();
        });
        actions.appendChild(toggle);
      }
      if (staticSite && openReviews().length && mode !== "share") {
        const share = button(tr("Gửi qua GitHub"));
        share.addEventListener("click", () => {
          if (busy) return;
          mode = "share";
          setStatus("");
          renderPanel();
          content.scrollTop = 0;
          content.querySelector("textarea").focus();
        });
        actions.appendChild(share);
      }
      return actions;
    }

    function renderPanel() {
      title.textContent = tr(mode === "share" ? "Gửi góp ý" : mode === "all" ? "Tất cả nhận xét" : "Nhận xét");
      content.replaceChildren(toolbar());
      form.hidden = mode !== "thread";
      if (mode === "share") {
        renderShare();
      } else if (mode === "all") {
        const shown = visibleReviews();
        if (!reviews.length) content.appendChild(el("p", "review-hint", tr("Chưa có nhận xét. Bôi chọn một đoạn để bắt đầu.")));
        else if (!shown.length) content.appendChild(el("p", "review-hint", tr("Mọi nhận xét đã xong.")));
        for (const item of shown) {
          const label = "#" + item.number + " · " + item.anchor.language.toUpperCase() + (isDone(item) ? " · " + tr("Đã xong") : "");
          const row = button(label, "review-list-item" + (isDone(item) ? " review-done" : ""));
          row.appendChild(el("span", "review-list-quote", item.anchor.excerpt));
          row.addEventListener("click", () => showReview(item));
          content.appendChild(row);
        }
      } else {
        content.appendChild(el("blockquote", "review-quote", activeAnchor.excerpt));
        const text = page.textContent;
        if (activeAnchor.language !== language) {
          content.appendChild(el("p", "review-hint", tr("Đoạn trích thuộc bản {language}.", { language: activeAnchor.language.toUpperCase() })));
        } else if (!available || locate(text, activeAnchor, revision()) < 0) {
          content.appendChild(el("p", "review-hint", tr("Không tìm thấy đoạn trích trong phiên bản đang mở.")));
        }
        for (const item of visibleReviews().filter(item => samePassage(item.anchor, activeAnchor, text))) {
          const entry = el("section", "review-entry" + (isDone(item) ? " review-done" : ""));
          const head = el("div", "review-entry-head");
          head.appendChild(el("strong", null, "#" + item.number + (isDone(item) ? " · " + tr("Đã xong") : "")));
          const tools = el("span", "review-entry-tools");
          const doneButton = button(isDone(item) ? tr("Mở lại") : tr("Đã xong"));
          doneButton.addEventListener("click", () => setDone(item, !isDone(item)));
          const editButton = button(tr("Sửa"));
          editButton.addEventListener("click", () => edit(item));
          tools.append(doneButton, editButton);
          head.appendChild(tools);
          entry.append(head, el("p", "review-text", item.body));
          if (item.resolution) entry.appendChild(el("p", "review-resolution", tr("Đã xử lý: {note}", { note: item.resolution })));
          content.appendChild(entry);
        }
        input.placeholder = editing ?
          tr("Sửa nhận xét #{number}…", { number: editing.number }) : tr("Nhập nhận xét…");
        saveButton.textContent = editing ? tr("Lưu chỉnh sửa") : tr("Lưu nhận xét");
        cancelEdit.hidden = !editing;
      }
      positionPanel();
    }

    async function persist(payload, create) {
      if (!staticSite) {
        return readResponse(await fetch(endpoint, {
          method: create ? "POST" : "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }));
      }
      function update() {
        const data = readDrafts();
        const current = data.reviews.find(item => item.id === payload.id);
        const timestamp = new Date().toISOString();
        if (create) {
          data.reviews.push({ ...payload, number: data.nextNumber++, version: 1, createdAt: timestamp, updatedAt: timestamp });
        } else {
          if (!current) throw new Error("review_missing");
          let changed = false;
          if ("body" in payload && current.body !== payload.body) {
            if (current.version !== payload.version) {
              const error = new Error("review_changed");
              error.status = 409;
              error.review = current;
              throw error;
            }
            current.body = payload.body;
            changed = true;
          }
          if (typeof payload.resolved === "boolean" && isDone(current) !== payload.resolved) {
            current.resolved = payload.resolved;
            if (payload.resolved) current.resolvedAt = timestamp;
            else delete current.resolvedAt;
            changed = true;
          }
          if (changed) Object.assign(current, { version: current.version + 1, updatedAt: timestamp });
        }
        localStorage.setItem(storageKey, JSON.stringify(data));
        return data;
      }
      return navigator.locks ? navigator.locks.request(storageKey, update) : update();
    }

    function issueBody() {
      const sections = [tr("Báo cáo") + " " + reportTitle()];
      if (location.protocol === "https:") {
        const reportUrl = new URL("report.html", location.href);
        reportUrl.searchParams.set("doc", docId);
        sections.push(reportUrl.href);
      }
      for (const item of openReviews()) {
        const { anchor } = item;
        const sourceDoc = item.sourceDoc || docId;
        const folder = item.sourceDoc
          ? (anchor.language === "en" ? "spec-web/en/" : "")
          : "docs/" + anchor.language + "/";
        const file = folder + sourceDoc + ".md";
        const version = anchor.revision ? " · SHA-256 `" + anchor.revision + "`" : "";
        sections.push(
          "## #" + item.number + " · " + anchor.language.toUpperCase(),
          "`" + file + "` · " + tr("Vị trí ký tự {offset}", { offset: anchor.start }) + version,
          "**" + tr("Đoạn trích") + "**\n\n" + fenced(anchor.excerpt),
          "**" + tr("Nhận xét") + "**\n\n" + fenced(item.body)
        );
      }
      return sections.join("\n\n");
    }

    function renderShare() {
      const body = issueBody();
      const repo = githubRepository();
      const issue = repo ? new URL("https://github.com/" + repo + "/issues/new") : null;
      let hint = "Sao chép góp ý để gửi cho chủ repo.";
      if (issue) {
        issue.searchParams.set("title", tr("Góp ý báo cáo {title}", { title: reportTitle() }));
        issue.searchParams.set("body", body);
        if (issue.href.length > GITHUB_URL_LIMIT) {
          issue.searchParams.delete("body");
          hint = "Góp ý dài. Sao chép nội dung rồi dán vào GitHub Issue.";
        } else {
          hint = "GitHub sẽ mở bản điền sẵn để bạn kiểm tra và gửi.";
        }
        content.appendChild(el("p", "review-hint", "GitHub · " + repo));
      }
      content.appendChild(el("p", "review-hint", tr(hint)));
      const text = el("textarea", "review-export");
      text.readOnly = true;
      text.value = body;
      text.setAttribute("aria-label", tr("Nội dung góp ý"));
      content.appendChild(text);

      const actions = el("div", "review-nav");
      const copy = button(tr("Sao chép góp ý"));
      copy.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(body);
          setStatus("Đã sao chép góp ý.");
        } catch {
          text.focus();
          text.select();
          setStatus("Nội dung đã được chọn để sao chép.");
        }
      });
      actions.appendChild(copy);
      if (issue) {
        const link = el("a", "review-button review-primary", tr("Mở GitHub Issue"));
        link.href = issue.href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        actions.appendChild(link);
      }
      content.appendChild(actions);
    }

    input.addEventListener("keydown", event => {
      if (event.key !== "Enter" || event.shiftKey || event.isComposing || event.keyCode === 229) return;
      event.preventDefault();
      if (!busy && input.value.trim()) form.requestSubmit();
    });

    form.addEventListener("submit", async event => {
      event.preventDefault();
      const body = input.value.trim();
      if (!body || busy) return;
      const create = !editing;
      const payload = create ? { id: draftId, anchor: activeAnchor, body } :
        { id: editing.id, version: editing.version, body };
      busy = true;
      ++requestVersion;
      saveButton.disabled = closeButton.disabled = cancelEdit.disabled = input.readOnly = true;
      setStatus("Đang lưu nhận xét…");
      try {
        const data = await persist(payload, create);
        loadError = "";
        setReviews(data);
      } catch (error) {
        if (error.review) {
          editing = error.review;
          const latest = reviews.filter(item => item.id !== editing.id).concat(editing);
          setReviews({ reviews: latest.sort((a, b) => a.number - b.number) });
          setStatus("Nhận xét đã đổi ở nơi khác. Xem bản mới ở trên trước khi lưu lại.");
        } else {
          setStatus(needsServerRestart(error) ?
            "Khởi động lại serve.py để dùng nhận xét." : "Không lưu được nhận xét. Nội dung nhập vẫn còn.");
        }
        return;
      } finally {
        busy = false;
        saveButton.disabled = closeButton.disabled = cancelEdit.disabled = input.readOnly = false;
      }
      hidePanel();
    });

    cancelEdit.addEventListener("click", () => {
      editing = null;
      input.value = "";
      draftId = newId();
      setStatus("");
      renderPanel();
      input.focus();
    });
    listButton.addEventListener("click", () => showAll(listButton.getBoundingClientRect(), listButton));
    closeButton.addEventListener("click", hidePanel);
    panel.addEventListener("keydown", event => {
      if (event.key === "Escape") {
        event.preventDefault();
        hidePanel();
      }
    });
    prompt.addEventListener("pointerdown", event => event.preventDefault());
    prompt.addEventListener("click", () => {
      if (!selection || busy) return;
      const { range, anchor } = selection;
      const point = range.getBoundingClientRect();
      window.getSelection()?.removeAllRanges();
      if (anchor.quote.length > QUOTE_LIMIT || anchor.excerpt.length > QUOTE_LIMIT) {
        showAll(point, listButton);
        setStatus("Đoạn bôi chọn quá dài. Hãy chọn một đoạn ngắn hơn.");
        return;
      }
      openThread(anchor, point, listButton, true);
    });

    page.addEventListener("pointerdown", () => {
      selecting = true;
      prompt.hidden = true;
    });
    function finishSelection() {
      if (!selecting) return;
      selecting = false;
      requestAnimationFrame(updatePrompt);
    }
    window.addEventListener("pointerup", finishSelection);
    window.addEventListener("pointercancel", finishSelection);
    document.addEventListener("selectionchange", updatePrompt);
    window.addEventListener("scroll", updatePrompt, { passive: true });
    window.addEventListener("resize", positionPanel);
    page.addEventListener("scroll", scheduleMarks, { passive: true });
    new ResizeObserver(scheduleMarks).observe(page.parentElement);
    new MutationObserver(scheduleMarks).observe(page, { childList: true, characterData: true, subtree: true });
    if (staticSite) window.addEventListener("storage", event => {
      if (event.key === storageKey) refresh();
    });

    refresh();
    return {
      documentChanged(lang, loaded) {
        language = lang;
        available = loaded;
        listButton.hidden = false;
        updateCount();
        if (mode) renderPanel();
        scheduleMarks();
      },
    };
  }

  window.SpecReviews = { mount };
})();
