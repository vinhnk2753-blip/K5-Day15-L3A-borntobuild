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
      func: crawlReviewsInPage,
      args: [message.payload?.ids, message.payload?.maxPerStar]
    }).then(([result]) => {
      if (result?.error) throw new Error(result.error);
      sendResponse({ ok: true, data: result?.result });
    }).catch(error => sendResponse({ ok: false, error: error.message }));
    return true;
  }

  if (message?.type !== "ANALYZE_SHOPEE_REVIEWS") return undefined;

  fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(message.payload)
  })
    .then(async response => {
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || `Backend trả HTTP ${response.status}`);
      sendResponse(result);
    })
    .catch(error => sendResponse({ ok: false, error: error.message }));

  return true;
});

// Runs in Shopee's page world so fetch uses the same origin, session cookies,
// and page context as the working DevTools Console snippet.
async function crawlReviewsInPage(ids, maxPerStar = 50) {
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

  while (scanned < MAX_SCANNED && stars.some(star => byStar.get(star).length < maxPerStar)) {
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
    if (page.length === 0) break;

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
    if (Number.isFinite(Number(data.item_rating_summary?.rating_count))) {
      total = Number(data.item_rating_summary.rating_count);
    }
    if (data.has_more === false || (data.has_more !== true && page.length < PAGE_SIZE)) break;
    await new Promise(resolve => setTimeout(resolve, WAIT_MS));
  }

  const reviews = stars.flatMap(star => byStar.get(star));
  return {
    ok: true,
    product: { shopid: String(ids.shopid), itemid: String(ids.itemid), url: location.href },
    collected_at: new Date().toISOString(),
    source: "Shopee public item ratings endpoint, fetched in product page context",
    limits: { max_per_star: maxPerStar, max_scanned: MAX_SCANNED },
    scanned_count: scanned,
    review_total_reported: total,
    review_count: reviews.length,
    counts_by_star: Object.fromEntries(stars.map(star => [star, byStar.get(star).length])),
    reviews
  };
}
