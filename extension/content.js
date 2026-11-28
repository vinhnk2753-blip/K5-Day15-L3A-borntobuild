(() => {
  if (globalThis.__bornToBuildReviewAgentLoaded) return;
  globalThis.__bornToBuildReviewAgentLoaded = true;
  document.getElementById("born-to-build-shopee-review-agent")?.remove();

  const MAX_PER_STAR = 50;
  const PROGRESS_SOURCE = "born-to-build-shopee-review-progress";
  const RESULT_SOURCE = "born-to-build-shopee-review-result";

  const host = document.createElement("div");
  host.id = "born-to-build-shopee-review-agent";
  document.documentElement.appendChild(host);
  const shadow = host.attachShadow({ mode: "open" });

  shadow.innerHTML = `
    <style>
      * { box-sizing: border-box; }
      .launcher { position: fixed; z-index: 2147483647; right: 18px; bottom: 84px;
        border: 0; border-radius: 999px; padding: 13px 17px; background: #176b55;
        color: white; font: 600 14px/1.2 system-ui, sans-serif; cursor: pointer;
        box-shadow: 0 4px 18px #0003; }
      .panel { position: fixed; z-index: 2147483647; right: 18px; bottom: 140px;
        width: min(410px, calc(100vw - 32px)); max-height: min(78vh, 760px);
        display: flex; flex-direction: column; color: #17231e; background: #fff;
        border: 1px solid #dce5df; border-radius: 14px; box-shadow: 0 10px 36px #0003;
        font: 14px/1.45 system-ui, sans-serif; overflow: hidden; }
      .panel[hidden] { display: none; }
      header { display: flex; align-items: center; justify-content: space-between;
        padding: 13px 15px; background: #f3f8f5; border-bottom: 1px solid #e2e9e4; }
      header strong { font-size: 15px; }
      .close { border: 0; background: transparent; font-size: 22px; cursor: pointer; color: #52615a; }
      .body { padding: 14px 15px; overflow: auto; }
      .run { width: 100%; border: 0; border-radius: 8px; padding: 11px; margin-bottom: 11px;
        color: #fff; background: #176b55; font: 600 14px system-ui, sans-serif; cursor: pointer; }
      .run:disabled, .actions button:disabled { opacity: .6; cursor: wait; }
      .status { color: #52615a; white-space: pre-wrap; margin: 4px 0 12px; }
      .actions { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
      .actions button { border: 1px solid #b9ccc1; border-radius: 7px; padding: 7px 10px;
        background: #f3f8f5; color: #176b55; font: 600 12px system-ui, sans-serif; cursor: pointer; }
      .actions button[hidden], details[hidden] { display: none; }
      .summary { padding: 10px; border-radius: 8px; background: #f3f8f5; margin: 8px 0 12px; }
      .risk { border-top: 1px solid #e4e9e6; padding: 12px 0; }
      .risk h3 { font-size: 14px; margin: 0 0 5px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
      .risk p { margin: 4px 0; }
      .sev { font-size: 11px; text-transform: uppercase; padding: 2px 6px; border-radius: 999px; font-weight: 700; }
      .sev-high { background: #fdecec; color: #b42318; }
      .sev-medium { background: #fef6e7; color: #b54708; }
      .sev-low { background: #eef4f0; color: #176b55; }
      .badge { color: #176b55; font-weight: 700; }
      .source { margin-top: 8px; padding: 9px; border-left: 3px solid #8db9a6; background: #fafcfb; }
      .source small { color: #53635b; }
      .source-text { margin-top: 4px; white-space: pre-wrap; overflow-wrap: anywhere; }
      .product-link { color: #176b55; display: inline-block; margin-top: 8px; }
      .meta { color: #69766f; font-size: 12px; margin-top: 8px; }
      details { margin-top: 10px; border: 1px solid #e4e9e6; border-radius: 8px; padding: 8px 10px; }
      details summary { cursor: pointer; font-weight: 600; font-size: 12px; color: #24332b; }
      .json-output, .agent-output { max-height: 36vh; overflow: auto; padding: 10px; margin: 8px 0 0;
        border-radius: 8px; background: #f5f7f6; color: #24332b; font: 11px/1.45 ui-monospace, monospace;
        white-space: pre-wrap; overflow-wrap: anywhere; }
    </style>
    <button class="launcher" type="button">Phân tích review</button>
    <section class="panel" hidden aria-label="Phân tích review sản phẩm">
      <header><strong>Rủi ro từ review Shopee</strong><button class="close" type="button" aria-label="Đóng">×</button></header>
      <div class="body">
        <button class="run" type="button">Crawl &amp; phân tích lại</button>
        <div class="status" role="status">1-click: lấy tối đa 50 review mỗi mức sao (5★→1★), tự động đẩy sang Web UI Review Lens (http://127.0.0.1:8000) và chạy phân tích.</div>
        <div class="actions">
          <button class="open-ui" type="button" hidden>Mở trên Web UI</button>
          <button class="retry" type="button" hidden>Phân tích trong panel</button>
          <button class="copy" type="button" hidden>Copy JSON</button>
          <button class="download" type="button" hidden>Tải JSON</button>
        </div>
        <div class="results"></div>
        <details class="json-details" hidden>
          <summary>Xem JSON review đã crawl</summary>
          <pre class="json-output"></pre>
        </details>
        <details class="agent-details" hidden>
          <summary>Xem JSON kết quả agent (output + structured)</summary>
          <pre class="agent-output"></pre>
        </details>
      </div>
    </section>`;

  const launcher = shadow.querySelector(".launcher");
  const panel = shadow.querySelector(".panel");
  const closeButton = shadow.querySelector(".close");
  const runButton = shadow.querySelector(".run");
  const openUiButton = shadow.querySelector(".open-ui");
  const retryButton = shadow.querySelector(".retry");
  const status = shadow.querySelector(".status");
  const results = shadow.querySelector(".results");
  const copyButton = shadow.querySelector(".copy");
  const downloadButton = shadow.querySelector(".download");
  const jsonDetails = shadow.querySelector(".json-details");
  const jsonOutput = shadow.querySelector(".json-output");
  const agentDetails = shadow.querySelector(".agent-details");
  const agentOutput = shadow.querySelector(".agent-output");

  let latestCrawlData = null;
  let latestCrawlUrl = "";
  let latestJson = "";
  let currentItemId = "";
  let activeCrawlId = "";
  let pendingCrawl = null;
  let isRunning = false;

  window.addEventListener("message", event => {
    if (event.origin !== location.origin || event.source !== window) return;
    const msg = event.data;
    if (!msg || !activeCrawlId || msg.requestId !== activeCrawlId) return;

    if (msg.source === PROGRESS_SOURCE) {
      const counts = Object.entries(msg.counts_by_star || {})
        .map(([star, count]) => `${star}★ ${count}`).join(" · ");
      const action = msg.stage === "requesting" ? "Đang tải" : "Đã xử lý";
      const label = msg.star ? `${msg.star}★ trang ${msg.star_page || msg.page}` : `trang ${msg.page}`;
      status.textContent = `${action} ${label}: đã quét ${msg.scanned} review, đã lấy ${msg.collected} (${counts}).`;
      return;
    }

    if (msg.source === RESULT_SOURCE && pendingCrawl) {
      const { resolve, reject } = pendingCrawl;
      pendingCrawl = null;
      if (msg.ok && msg.data) {
        resolve(msg.data);
      } else {
        reject(new Error(msg.error || "Extension không nhận được JSON review."));
      }
    }
  });

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message?.type !== "ONE_CLICK_RUN") return undefined;
    panel.hidden = false;
    if (!isRunning) {
      runCrawlAndHandoff();
    }
    sendResponse({ ok: true });
    return undefined;
  });

  launcher.addEventListener("click", () => {
    if (isRunning) {
      panel.hidden = !panel.hidden;
      return;
    }
    if (panel.hidden && (!latestCrawlData || latestCrawlUrl !== location.href)) {
      panel.hidden = false;
      runCrawlAndHandoff();
      return;
    }
    panel.hidden = !panel.hidden;
  });
  closeButton.addEventListener("click", () => { panel.hidden = true; });
  copyButton.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(latestJson);
      status.textContent = "Đã copy JSON vào clipboard.";
    } catch {
      status.textContent = "Không copy được; hãy mở mục JSON bên dưới để copy thủ công.";
    }
  });
  downloadButton.addEventListener("click", () => {
    const blob = new Blob([latestJson], { type: "application/json;charset=utf-8" });
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = `shopee-reviews-${currentItemId || "product"}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
  });

  function addText(parent, tag, text, className) {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    parent.appendChild(node);
    return node;
  }

  function renderResult(structured, productUrl) {
    results.replaceChildren();
    addText(results, "div", structured.summary || "", "summary");

    for (const risk of structured.risks || []) {
      const card = document.createElement("article");
      card.className = "risk";
      const heading = document.createElement("h3");
      heading.appendChild(document.createTextNode(risk.title || "Rủi ro cần kiểm tra"));
      const sev = risk.severity || "medium";
      addText(heading, "span", sev, `sev sev-${sev}`);
      card.appendChild(heading);
      addText(card, "p", risk.summary || "");

      for (const source of risk.citations || []) {
        const box = document.createElement("div");
        box.className = "source";
        const ratingLabel = source.rating != null ? `${source.rating} sao` : "không rõ sao";
        addText(box, "small", `[${source.id}] ${ratingLabel}${source.variant ? ` · ${source.variant}` : ""}`, "badge");
        addText(box, "div", source.text || "", "source-text");
        card.appendChild(box);
      }
      results.appendChild(card);
    }

    const stats = structured.stats || {};
    addText(
      results,
      "div",
      `Đầu vào: ${stats.input_review_count ?? 0} · lọc nhiễu: ${stats.filtered_noise_count ?? 0} · review sạch: ${structured.review_count ?? 0} · model: ${structured.model || "không rõ"}`,
      "meta"
    );
    if (structured.anomalies?.duplicate_count) {
      addText(
        results,
        "div",
        `Cờ mẫu: ${structured.anomalies.duplicate_count}/${structured.anomalies.review_count} review có nội dung trùng (không phải bằng chứng seeding/gian lận).`,
        "meta"
      );
    }
    const link = document.createElement("a");
    link.className = "product-link";
    link.href = productUrl;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Mở trang sản phẩm để kiểm tra review gốc";
    results.appendChild(link);
  }

  function readProductIds() {
    const candidates = [location.href, location.pathname];
    try {
      let decoded = location.href;
      for (let i = 0; i < 2; i++) {
        const next = decodeURIComponent(decoded);
        if (next === decoded) break;
        decoded = next;
      }
      candidates.push(decoded);
    } catch {}
    const canonical = document.querySelector('link[rel="canonical"]')?.href;
    if (canonical) candidates.push(canonical);

    for (const value of candidates) {
      const match = value.match(/\/(?:product|item)\/(\d+)\/(\d+)/i)
        ?? value.match(/i[./](\d+)[./](\d+)/i)
        ?? value.match(/(\d{8,})[./](\d{8,})/);
      if (match) return { shopid: match[1], itemid: match[2] };
    }
    throw new Error("Không nhận diện được mã sản phẩm từ URL hiện tại.");
  }

  async function pushToWebUI(crawlData) {
    openUiButton.disabled = true;
    try {
      const response = await chrome.runtime.sendMessage({
        type: "PUSH_TO_WEB_UI",
        payload: crawlData
      });
      if (!response?.ok || !response?.ui_url) {
        throw new Error(response?.error || "Web UI local (127.0.0.1:8000) chưa phản hồi.");
      }
      results.replaceChildren();
      addText(
        results,
        "div",
        `Đã đẩy ${crawlData.review_count} review sang Web UI Review Lens và tự động mở tab phân tích.`,
        "summary"
      );
      const link = document.createElement("a");
      link.className = "product-link";
      link.href = response.ui_url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "Mở lại tab phân tích trên Web UI";
      results.appendChild(link);
      status.textContent = `Đã đẩy tự động ${crawlData.review_count} review sang Web UI (http://127.0.0.1:8000).`;
      return { ok: true, ui_url: response.ui_url };
    } finally {
      openUiButton.disabled = false;
    }
  }

  async function analyzePayload(crawlData, { silentError = false } = {}) {
    retryButton.disabled = true;
    results.replaceChildren();
    agentDetails.hidden = true;
    try {
      const analysis = await chrome.runtime.sendMessage({
        type: "ANALYZE_SHOPEE_REVIEWS",
        payload: crawlData
      });
      if (!analysis?.output || !analysis?.structured) {
        throw new Error(analysis?.error || "Agent local chưa trả output theo hợp đồng.");
      }
      renderResult(analysis.structured, crawlData.product?.url || location.href);
      agentOutput.textContent = JSON.stringify(analysis, null, 2);
      agentDetails.hidden = false;
      status.textContent = `Phân tích xong (${analysis.structured.status || "không rõ"}): ${analysis.structured.review_count ?? 0} review sạch, model ${analysis.structured.model || "không rõ"}.`;
      return { ok: true };
    } catch (error) {
      if (!silentError) {
        status.textContent = `Đã giữ JSON (${crawlData.review_count} review), nhưng agent panel (cổng 8765) chưa phân tích được: ${error.message}\nHãy chạy python run.py rồi bấm "Mở trên Web UI", hoặc chạy python codebase/extension_server.py rồi bấm "Phân tích trong panel".`;
      }
      return { ok: false, error: error.message };
    } finally {
      retryButton.disabled = false;
    }
  }

  openUiButton.addEventListener("click", async () => {
    if (!latestCrawlData) return;
    runButton.disabled = true;
    status.textContent = `Đang đẩy ${latestCrawlData.review_count} review sang Web UI Review Lens…`;
    try {
      await pushToWebUI(latestCrawlData);
    } catch (error) {
      status.textContent = `Chưa kết nối được Web UI (http://127.0.0.1:8000): ${error.message}\nHãy chạy python run.py ở thư mục gốc rồi bấm "Mở trên Web UI" lại.`;
    } finally {
      runButton.disabled = false;
    }
  });

  retryButton.addEventListener("click", async () => {
    if (!latestCrawlData) return;
    runButton.disabled = true;
    status.textContent = `Đang gửi ${latestCrawlData.review_count} review cho extension server (cổng 8765)…`;
    try {
      await analyzePayload(latestCrawlData);
    } finally {
      runButton.disabled = false;
    }
  });

  async function runCrawlAndHandoff() {
    if (isRunning) return;
    isRunning = true;
    runButton.disabled = true;
    openUiButton.hidden = true;
    retryButton.hidden = true;
    results.replaceChildren();
    jsonDetails.hidden = true;
    agentDetails.hidden = true;
    copyButton.hidden = true;
    downloadButton.hidden = true;
    latestCrawlData = null;
    latestCrawlUrl = "";
    latestJson = "";

    try {
      const ids = readProductIds();
      currentItemId = ids.itemid;
      activeCrawlId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
      status.textContent = `Đang bắt đầu crawl sản phẩm ${ids.itemid} (5★→1★)…`;

      const crawlPromise = new Promise((resolve, reject) => {
        pendingCrawl = { resolve, reject };
      });

      const startResponse = await chrome.runtime.sendMessage({
        type: "CRAWL_SHOPEE_REVIEWS",
        payload: { ids, maxPerStar: MAX_PER_STAR, requestId: activeCrawlId }
      });
      if (!startResponse?.ok) {
        pendingCrawl = null;
        throw new Error(startResponse?.error || "Không khởi động được tiến trình crawl trên tab hiện tại.");
      }

      const crawlData = await crawlPromise;
      latestCrawlData = crawlData;
      latestCrawlUrl = location.href;
      latestJson = JSON.stringify(crawlData, null, 2);
      jsonOutput.textContent = latestJson;
      jsonDetails.hidden = false;
      openUiButton.hidden = false;
      retryButton.hidden = false;
      copyButton.hidden = false;
      downloadButton.hidden = false;

      const counts = Object.entries(crawlData.counts_by_star || {}).map(([star, count]) => `${star}★ ${count}`).join(" · ");
      status.textContent = `Đã crawl ${crawlData.review_count} review (${counts}). Đang đẩy tự động sang Web UI Review Lens…`;
      try {
        await pushToWebUI(crawlData);
      } catch (uiError) {
        status.textContent = `Web UI (8000) chưa bật; đang thử phân tích qua extension server (8765)…`;
        const fallback = await analyzePayload(crawlData, { silentError: true });
        if (!fallback.ok) {
          status.textContent = `Đã giữ JSON (${crawlData.review_count} review), nhưng chưa kết nối được Web UI (8000: ${uiError.message}) hay extension server (8765: ${fallback.error}).\n• Chạy python run.py rồi bấm "Mở trên Web UI" (khuyên dùng).\n• Hoặc chạy python codebase/extension_server.py rồi bấm "Phân tích trong panel".`;
        }
      }
    } catch (error) {
      const msg = error?.message || String(error);
      if (msg.includes("Extension context invalidated")) {
        status.textContent = "Extension vừa được reload; hãy F5 tải lại trang Shopee hoặc bấm biểu tượng extension trên thanh công cụ Chrome.";
      } else {
        status.textContent = `Không lấy được review: ${msg}\nHãy tải lại extension và trang Shopee rồi thử lại.`;
      }
    } finally {
      pendingCrawl = null;
      activeCrawlId = "";
      isRunning = false;
      runButton.disabled = false;
    }
  }

  runButton.addEventListener("click", runCrawlAndHandoff);
})();
