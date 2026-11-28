const WEB_UI_ORIGIN = "http://127.0.0.1:8000";
const WEB_UI_HANDOFF_URL = `${WEB_UI_ORIGIN}/api/extension-handoff`;
const API_URL = "http://127.0.0.1:8765/analyze";

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "CRAWL_SHOPEE_REVIEWS") {
    const tabId = _sender.tab?.id;
    if (!tabId) {
      sendResponse({ ok: false, error: "Không xác định được tab Shopee hiện tại." });
      return undefined;
    }

    chrome.scripting.executeScript({
      target: { tabId },
      world: "MAIN",
      func: startCrawlInPage,
      args: [message.payload?.ids, message.payload?.maxPerStar, message.payload?.requestId]
    }).then(([result]) => {
      if (result?.error) {
        const msg = typeof result.error === "string"
          ? result.error
          : (result.error.message || JSON.stringify(result.error));
        throw new Error(msg);
      }
      sendResponse({ ok: true, started: true });
    }).catch(error => sendResponse({ ok: false, error: error?.message || String(error) }));
    return true;
  }

  if (message?.type === "PUSH_TO_WEB_UI") {
    fetch(WEB_UI_HANDOFF_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message.payload)
    })
      .then(async response => {
        const rawText = await response.text();
        let result = null;
        try {
          result = JSON.parse(rawText);
        } catch {
          throw new Error(`Web UI trả HTTP ${response.status} không phải JSON hợp lệ.`);
        }
        if (!response.ok || !result?.ok || typeof result.ui_url !== "string") {
          throw new Error(result?.message || result?.error || `Web UI trả HTTP ${response.status}`);
        }
        if (!result.ui_url.startsWith(`${WEB_UI_ORIGIN}/`)) {
          throw new Error("URL Web UI trả về không hợp lệ.");
        }
        await chrome.tabs.create({ url: result.ui_url });
        sendResponse({
          ok: true,
          ui_url: result.ui_url,
          handoff_id: result.handoff_id,
          review_count: result.review_count
        });
      })
      .catch(error => sendResponse({ ok: false, error: error?.message || String(error) }));
    return true;
  }

  if (message?.type !== "ANALYZE_SHOPEE_REVIEWS") return undefined;

  fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(message.payload)
  })
    .then(async response => {
      const rawText = await response.text();
      let result = null;
      try {
        result = JSON.parse(rawText);
      } catch {
        throw new Error(`Backend trả HTTP ${response.status} không phải JSON hợp lệ.`);
      }
      if (!response.ok) throw new Error(result?.error || `Backend trả HTTP ${response.status}`);
      sendResponse(result);
    })
    .catch(error => sendResponse({ ok: false, error: error?.message || String(error) }));

  return true;
});

// Starts the crawl in Shopee's page world and returns immediately so the MV3
// service worker does not hit its idle timeout while pages are fetched.
// Progress and final results are posted back to content.js via window.postMessage.
function startCrawlInPage(ids, maxPerStar = 50, requestId = "") {
  const PROGRESS_SOURCE = "born-to-build-shopee-review-progress";
  const RESULT_SOURCE = "born-to-build-shopee-review-result";

  (async () => {
    try {
      if (location.hostname !== "shopee.vn" || !ids?.shopid || !ids?.itemid) {
        throw new Error("Hãy mở đúng trang sản phẩm Shopee.vn rồi thử lại.");
      }

      const PAGE_SIZE = 20;
      const MAX_SCANNED = 5000;
      const WAIT_MS = 500;
      const stars = [5, 4, 3, 2, 1];
      const byStar = new Map(stars.map(star => [star, []]));
      const seen = new Set();
      const pageSignatures = new Set();
      let offset = 0;
      let scanned = 0;
      let total = null;
      let pages = 0;

      function reportProgress(stage) {
        window.postMessage({
          source: PROGRESS_SOURCE,
          requestId,
          stage,
          page: Math.max(1, pages),
          offset,
          scanned,
          collected: stars.reduce((sum, star) => sum + byStar.get(star).length, 0),
          counts_by_star: Object.fromEntries(stars.map(star => [star, byStar.get(star).length]))
        }, location.origin);
      }

      while (scanned < MAX_SCANNED && stars.some(star => byStar.get(star).length < maxPerStar)) {
        pages++;
        reportProgress("requesting");
        const url = new URL("/api/v2/item/get_ratings", location.origin);
        const params = {
          filter: 0, flag: 1, itemid: ids.itemid, limit: PAGE_SIZE,
          offset, shopid: ids.shopid, type: 0
        };
        for (const [key, value] of Object.entries(params)) url.searchParams.set(key, value);

        const response = await fetch(url, {
          method: "GET",
          credentials: "include",
          cache: "no-store",
          headers: {
            Accept: "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "X-Shopee-Language": "vi"
          }
        });
        if (!response.ok) {
          throw new Error(`Shopee trả HTTP ${response.status} khi lấy review.`);
        }

        const payload = await response.json();
        const data = payload?.data;
        const page = data?.ratings;
        if (payload?.error || !Array.isArray(page)) {
          throw new Error(payload?.error_msg || "Shopee không trả danh sách review dạng JSON.");
        }
        if (page.length === 0) {
          reportProgress("page_done");
          break;
        }

        const signature = page.map(review => review.cmtid ?? `${review.rating_star}|${review.ctime}|${review.comment}`).join(",");
        if (pageSignatures.has(signature)) break;
        pageSignatures.add(signature);

        for (const review of page) {
          const star = Number(review.rating_star);
          if (!byStar.has(star) || byStar.get(star).length >= maxPerStar) continue;
          const key = String(review.cmtid ?? `${star}|${review.ctime}|${review.comment}`);
          if (seen.has(key)) continue;
          seen.add(key);

          const ctime = Number(review.ctime) || 0;
          const variants = Array.isArray(review.product_items) ? review.product_items : [];
          byStar.get(star).push({
            review_id: String(review.cmtid ?? ""),
            rating_star: star,
            comment: String(review.comment ?? ""),
            ctime,
            date: ctime ? new Date(ctime * 1000).toISOString() : "",
            variant: variants.map(item => item?.name || item?.model_name || "").filter(Boolean).join(", ")
          });
        }

        offset += page.length;
        scanned += page.length;
        const rawTotal = data.item_rating_summary?.rating_total ?? data.item_rating_summary?.rating_count;
        if (typeof rawTotal === "number" && Number.isFinite(rawTotal)) {
          total = rawTotal;
        } else if (Array.isArray(rawTotal) && typeof rawTotal[0] === "number" && Number.isFinite(rawTotal[0])) {
          total = rawTotal[0];
        }
        reportProgress("page_done");
        if (data.has_more === false || (data.has_more !== true && page.length < PAGE_SIZE)) break;
        await new Promise(resolve => setTimeout(resolve, WAIT_MS));
      }

      reportProgress("complete");
      const reviews = stars.flatMap(star => byStar.get(star));
      const productName = (document.querySelector("h1")?.textContent || document.title || "")
        .replace(/\s+/g, " ")
        .trim()
        .slice(0, 200);
      window.postMessage({
        source: RESULT_SOURCE,
        requestId,
        ok: true,
        data: {
          ok: true,
          product: { shopid: String(ids.shopid), itemid: String(ids.itemid), name: productName, url: location.href },
          collected_at: new Date().toISOString(),
          source: "Shopee public item ratings endpoint, fetched in product page context",
          limits: { max_per_star: maxPerStar, max_scanned: MAX_SCANNED },
          scanned_count: scanned,
          review_total_reported: total,
          review_count: reviews.length,
          counts_by_star: Object.fromEntries(stars.map(star => [star, byStar.get(star).length])),
          reviews
        }
      }, location.origin);
    } catch (error) {
      window.postMessage({
        source: RESULT_SOURCE,
        requestId,
        ok: false,
        error: error?.message || String(error)
      }, location.origin);
    }
  })();

  return { started: true };
}
