(() => {
  if (document.getElementById("born-to-build-shopee-review-agent")) return;

  const PAGE_SIZE = 20;
  const MAX_PER_STAR = 50;
  const MAX_SCANNED = 5000;
  const WAIT_MS = 700;
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
      .summary { padding: 10px; border-radius: 8px; background: #f3f8f5; margin: 8px 0 12px; }
      .risk { border-top: 1px solid #e4e9e6; padding: 12px 0; }
      .risk h3 { font-size: 14px; margin: 0 0 5px; }
      .risk p { margin: 4px 0; }
      .badge { color: #176b55; font-weight: 700; }
      .source { margin-top: 8px; padding: 9px; border-left: 3px solid #8db9a6; background: #fafcfb; }
      .source small { color: #53635b; }
      .source-text { margin-top: 4px; white-space: pre-wrap; overflow-wrap: anywhere; }
      .product-link { color: #176b55; }
      .meta { color: #69766f; font-size: 12px; margin-top: 12px; }
    </style>
    <button class="launcher" type="button">Phân tích review</button>
    <section class="panel" hidden aria-label="Phân tích review sản phẩm">
      <header><strong>Rủi ro từ review</strong><button class="close" type="button" aria-label="Đóng">×</button></header>
      <div class="body">
        <button class="run" type="button">Crawl &amp; phân tích trang này</button>
        <div class="status" role="status">Lấy tối đa 50 review cho mỗi mức sao.</div>
        <div class="results"></div>
      </div>
    </section>`;

  const launcher = shadow.querySelector(".launcher");
  const panel = shadow.querySelector(".panel");
  const closeButton = shadow.querySelector(".close");
  const runButton = shadow.querySelector(".run");
  const status = shadow.querySelector(".status");
  const results = shadow.querySelector(".results");

  launcher.addEventListener("click", () => { panel.hidden = !panel.hidden; });
  closeButton.addEventListener("click", () => { panel.hidden = true; });

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

  function getVariant(review) {
    const items = Array.isArray(review.product_items) ? review.product_items : [];
    return items.map(item => item?.name || item?.model_name || "").filter(Boolean).join(", ");
  }

  async function crawlReviews(ids) {
    const stars = [5, 4, 3, 2, 1];
    const byStar = new Map(stars.map(star => [star, []]));
    const seen = new Set();
    let offset = 0;
    let scanned = 0;

    // Match the Console request that asks for all ratings (type=0), then bucket locally.
    while (scanned < MAX_SCANNED && stars.some(star => byStar.get(star).length < MAX_PER_STAR)) {
      const url = new URL("/api/v2/item/get_ratings", location.origin);
      Object.entries({
        filter: 0, flag: 1, itemid: ids.itemid, limit: PAGE_SIZE, offset,
        shopid: ids.shopid, type: 0
      }).forEach(([key, value]) => url.searchParams.set(key, value));

      const response = await fetch(url, { credentials: "include" });
      if (!response.ok) {
        throw new Error(`Shopee trả HTTP ${response.status} khi lấy review (type=0).`);
      }

      const payload = await response.json();
      const page = payload?.data?.ratings;
      if (!Array.isArray(page)) throw new Error("Shopee không trả danh sách review như mong đợi.");
      if (page.length === 0) break;

      let added = 0;
      for (const review of page) {
        const star = Number(review.rating_star);
        if (!byStar.has(star) || byStar.get(star).length >= MAX_PER_STAR) continue;

        const key = review.cmtid ?? `${star}|${review.ctime}|${review.comment}`;
        if (seen.has(key)) continue;
        seen.add(key);
        byStar.get(star).push({
          review_id: String(review.cmtid ?? ""),
          rating_star: star,
          comment: String(review.comment ?? ""),
          ctime: Number(review.ctime) || 0,
          date: review.ctime ? new Date(Number(review.ctime) * 1000).toISOString() : "",
          variant: getVariant(review)
        });
        added++;
      }

      offset += page.length;
      scanned += page.length;
      const counts = stars.map(star => `${star}★ ${byStar.get(star).length}`).join(" · ");
      status.textContent = `Đã quét ${scanned}/${MAX_SCANNED} review · ${counts}`;

      if (payload.data.has_more === false || added === 0) break;
      if (payload.data.has_more !== true && page.length < PAGE_SIZE) break;
      await new Promise(resolve => setTimeout(resolve, WAIT_MS));
    }

    return stars.flatMap(star => byStar.get(star));
  }

  function addText(parent, tag, text, className) {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    parent.appendChild(node);
    return node;
  }

  function renderResult(data, productUrl) {
    results.replaceChildren();
    addText(results, "div", data.summary || "", "summary");

    for (const risk of data.risks || []) {
      const card = document.createElement("article");
      card.className = "risk";
      addText(card, "h3", risk.title);
      addText(card, "p", risk.summary);

      for (const source of risk.citations || []) {
        const box = document.createElement("div");
        box.className = "source";
        addText(box, "small", `[${source.id}] ${source.rating} sao${source.variant ? ` · ${source.variant}` : ""}`, "badge");
        addText(box, "div", source.text, "source-text");
        card.appendChild(box);
      }
      results.appendChild(card);
    }

    const link = document.createElement("a");
    link.className = "product-link";
    link.href = productUrl;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Mở trang sản phẩm để kiểm tra review gốc";
    results.appendChild(link);
    addText(results, "div", `Đã phân tích ${data.review_count || 0} review có nội dung · model: ${data.model || "không rõ"}`, "meta");
  }

  runButton.addEventListener("click", async () => {
    runButton.disabled = true;
    results.replaceChildren();

    try {
      const ids = readProductIds();
      const productUrl = location.href;
      status.textContent = `Đang crawl sản phẩm ${ids.itemid}, tối đa 50 review mỗi mức sao…`;
      const reviews = await crawlReviews(ids);
      if (!reviews.length) throw new Error("Không lấy được review nào từ trang này.");

      status.textContent = `Đã lấy ${reviews.length} review. Đang gửi cho agent…`;
      const response = await chrome.runtime.sendMessage({
        type: "ANALYZE_SHOPEE_REVIEWS",
        payload: { url: productUrl, reviews }
      });
      if (!response?.ok) throw new Error(response?.error || "Backend agent không phản hồi.");

      renderResult(response, productUrl);
      status.textContent = "Phân tích xong. Các mã [Rxx] trỏ đến review nguồn bên dưới.";
    } catch (error) {
      status.textContent = `Không hoàn tất: ${error.message}\nKiểm tra backend Python, quyền extension và phản hồi Shopee.`;
    } finally {
      runButton.disabled = false;
    }
  });
})();
