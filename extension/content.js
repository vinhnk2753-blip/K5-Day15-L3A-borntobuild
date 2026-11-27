(() => {
  if (document.getElementById("born-to-build-shopee-review-agent")) return;

  const MAX_PER_STAR = 50;
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
        width: min(390px, calc(100vw - 32px)); max-height: min(78vh, 760px);
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
      .run:disabled { opacity: .6; cursor: wait; }
      .status { color: #52615a; white-space: pre-wrap; margin: 4px 0 12px; }
      .actions { display: flex; gap: 8px; margin-bottom: 10px; }
      .actions button { border: 1px solid #b9ccc1; border-radius: 7px; padding: 8px 10px;
        background: #f3f8f5; color: #176b55; font: 600 12px system-ui, sans-serif; cursor: pointer; }
      .actions button[hidden], .json-output[hidden] { display: none; }
      .json-output { max-height: 48vh; overflow: auto; padding: 10px; margin: 0;
        border-radius: 8px; background: #f5f7f6; color: #24332b; font: 11px/1.45 ui-monospace, monospace;
        white-space: pre; }
    </style>
    <button class="launcher" type="button">Lấy review JSON</button>
    <section class="panel" hidden aria-label="Review JSON sản phẩm">
      <header><strong>Review JSON Shopee</strong><button class="close" type="button" aria-label="Đóng">×</button></header>
      <div class="body">
        <button class="run" type="button">Crawl review → JSON</button>
        <div class="status" role="status">Lấy tối đa 50 review mỗi mức sao; kết quả sẽ là JSON.</div>
        <div class="actions"><button class="copy" type="button" hidden>Copy JSON</button><button class="download" type="button" hidden>Tải JSON</button></div>
        <pre class="json-output" hidden></pre>
        <div class="results"></div>
      </div>
    </section>`;

  const launcher = shadow.querySelector(".launcher");
  const panel = shadow.querySelector(".panel");
  const closeButton = shadow.querySelector(".close");
  const runButton = shadow.querySelector(".run");
  const status = shadow.querySelector(".status");
  const results = shadow.querySelector(".results");
  const copyButton = shadow.querySelector(".copy");
  const downloadButton = shadow.querySelector(".download");
  const jsonOutput = shadow.querySelector(".json-output");
  let latestJson = "";
  let activeCrawlId = "";

  window.addEventListener("message", event => {
    const progress = event.data;
    if (event.source !== window
      || progress?.source !== "born-to-build-shopee-review-progress"
      || !activeCrawlId
      || progress.requestId !== activeCrawlId) return;

    const counts = Object.entries(progress.counts_by_star || {})
      .map(([star, count]) => `${star}★ ${count}`).join(" · ");
    const action = progress.stage === "requesting" ? "Đang tải" : "Đã xử lý";
    status.textContent = `${action} trang ${progress.page}: đã quét ${progress.scanned} review, đã lấy ${progress.collected} (${counts}).`;
  });

  launcher.addEventListener("click", () => { panel.hidden = !panel.hidden; });
  closeButton.addEventListener("click", () => { panel.hidden = true; });
  copyButton.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(latestJson);
      status.textContent = "Đã copy JSON vào clipboard.";
    } catch {
      status.textContent = "Không copy được; hãy chọn và copy JSON trong khung bên dưới.";
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
  let currentItemId = "";

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

  runButton.addEventListener("click", async () => {
    runButton.disabled = true;
    results.replaceChildren();
    jsonOutput.hidden = true;
    copyButton.hidden = true;
    downloadButton.hidden = true;
    latestJson = "";

    try {
      const ids = readProductIds();
      currentItemId = ids.itemid;
      activeCrawlId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
      status.textContent = `Đang bắt đầu crawl sản phẩm ${ids.itemid}…`;
      const response = await chrome.runtime.sendMessage({
        type: "CRAWL_SHOPEE_REVIEWS",
        payload: { ids, maxPerStar: MAX_PER_STAR, requestId: activeCrawlId }
      });
      if (!response?.ok || !response.data) throw new Error(response?.error || "Extension không nhận được JSON review.");

      latestJson = JSON.stringify(response.data, null, 2);
      jsonOutput.textContent = latestJson;
      jsonOutput.hidden = false;
      copyButton.hidden = false;
      downloadButton.hidden = false;
      const counts = Object.entries(response.data.counts_by_star || {}).map(([star, count]) => `${star}★ ${count}`).join(" · ");
      status.textContent = `Đã lấy ${response.data.review_count} review (${counts}). JSON đã sẵn sàng.`;
    } catch (error) {
      status.textContent = `Không lấy được review: ${error.message}\nHãy tải lại extension và trang Shopee rồi thử lại.`;
    } finally {
      activeCrawlId = "";
      runButton.disabled = false;
    }
  });
})();
