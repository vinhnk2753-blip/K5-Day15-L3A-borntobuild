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
      maxPerStar = Math.max(1, Math.min(50, Math.trunc(Number(maxPerStar) || 50)));
      const stars = [5, 4, 3, 2, 1];
      const byStar = new Map(stars.map(star => [star, []]));
      const seen = new Set();
      const pageSignatures = new Set();
      let scanned = 0;
      let total = null;
      let pages = 0;
      let currentStar = null;
      let currentStarPage = 1;
      let fallbackUsed = false;
      let fallbackReason = "";
      const warnings = [];

      const wait = () => new Promise(resolve => setTimeout(resolve, WAIT_MS));

      function reportProgress(stage) {
        window.postMessage({
          source: PROGRESS_SOURCE,
          requestId,
          stage,
          page: Math.max(1, pages),
          star: currentStar,
          star_page: currentStarPage,
          scanned,
          collected: stars.reduce((sum, star) => sum + byStar.get(star).length, 0),
          counts_by_star: Object.fromEntries(stars.map(star => [star, byStar.get(star).length]))
        }, location.origin);
      }

      function addReviews(page) {
        let filterIgnored = false;
        for (const review of page) {
          const rating = Number(review.rating_star);
          if (!byStar.has(rating)) continue;
          if (currentStar && rating !== currentStar) filterIgnored = true;
          if (byStar.get(rating).length >= maxPerStar) continue;
          const key = String(review.cmtid ?? `${rating}|${review.ctime}|${review.comment}`);
          if (seen.has(key)) continue;
          seen.add(key);

          const ctime = Number(review.ctime) || 0;
          const variants = Array.isArray(review.product_items) ? review.product_items : [];
          byStar.get(rating).push({
            review_id: String(review.cmtid ?? ""),
            rating_star: rating,
            comment: String(review.comment ?? ""),
            ctime,
            date: ctime ? new Date(ctime * 1000).toISOString() : "",
            variant: variants.map(item => item?.name || item?.model_name || "").filter(Boolean).join(", ")
          });
        }
        return filterIgnored;
      }

      function updateTotal(data) {
        const rawTotal = data?.item_rating_summary?.rating_total ?? data?.item_rating_summary?.rating_count;
        if (typeof rawTotal === "number" && Number.isFinite(rawTotal)) {
          total = rawTotal;
        } else if (Array.isArray(rawTotal) && typeof rawTotal[0] === "number" && Number.isFinite(rawTotal[0])) {
          total = rawTotal[0];
        }
      }

      function hasRoomForReviews() {
        return stars.some(star => byStar.get(star).length < maxPerStar);
      }

      async function fetchPage(type, offset, starLabel) {
        const url = new URL("/api/v2/item/get_ratings", location.origin);
        const params = {
          filter: 0, flag: 1, itemid: ids.itemid, limit: PAGE_SIZE,
          offset, shopid: ids.shopid, type
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
          throw new Error(`Shopee trả HTTP ${response.status} khi lấy review ${starLabel}.`);
        }
        const payload = await response.json();
        if (payload?.error || !Array.isArray(payload?.data?.ratings)) {
          throw new Error(payload?.error_msg || `Shopee không trả danh sách review ${starLabel} dạng JSON.`);
        }
        return payload.data;
      }

      let shouldFallback = false;
      for (const star of stars) {
        let offset = 0;
        let starPage = 0;
        currentStar = star;
        while (byStar.get(star).length < maxPerStar && scanned < MAX_SCANNED) {
          pages++;
          starPage++;
          currentStarPage = starPage;
          reportProgress("requesting");
          let data;
          try {
            data = await fetchPage(star, offset, `${star} sao`);
          } catch (error) {
            warnings.push(error?.message || String(error));
            fallbackUsed = true;
            fallbackReason = "Lọc theo sao bị chặn hoặc lỗi; đã thử lấy review không lọc sao.";
            shouldFallback = true;
            break;
          }
          const page = data.ratings;
          if (page.length === 0) {
            reportProgress("page_done");
            break;
          }

          const signature = `${star}:` + page.map(review => review.cmtid ?? `${review.rating_star}|${review.ctime}|${review.comment}`).join(",");
          if (pageSignatures.has(signature)) {
            reportProgress("page_done");
            break;
          }
          pageSignatures.add(signature);

          const filterIgnored = addReviews(page);

          offset += page.length;
          scanned += page.length;
          updateTotal(data);
          reportProgress("page_done");
          if (filterIgnored) {
            warnings.push(`Shopee không áp dụng bộ lọc ${star} sao; đã gom review theo số sao trả về.`);
            fallbackUsed = true;
            fallbackReason = "Endpoint bỏ qua bộ lọc sao; đã thử tiếp bằng truy vấn không lọc sao.";
            shouldFallback = true;
            break;
          }
          if (byStar.get(star).length >= maxPerStar
            || data.has_more === false
            || (data.has_more !== true && page.length < PAGE_SIZE)) break;
          await wait();
        }
        reportProgress("star_done");
        if (shouldFallback || scanned >= MAX_SCANNED) break;
        if (star !== stars[stars.length - 1] && hasRoomForReviews()) await wait();
      }

      if (shouldFallback && hasRoomForReviews() && scanned < MAX_SCANNED) {
        await wait();
        currentStar = 0;
        let offset = 0;
        let fallbackPage = 0;
        while (hasRoomForReviews() && scanned < MAX_SCANNED) {
          pages++;
          fallbackPage++;
          currentStarPage = fallbackPage;
          reportProgress("requesting");
          let data;
          try {
            data = await fetchPage(0, offset, "mọi mức sao");
          } catch (error) {
            warnings.push(`Truy vấn không lọc sao cũng thất bại: ${error?.message || String(error)}`);
            break;
          }
          const page = data.ratings;
          if (page.length === 0) {
            reportProgress("page_done");
            break;
          }
          const signature = `0:${page.map(review => review.cmtid ?? `${review.rating_star}|${review.ctime}|${review.comment}`).join(",")}`;
          if (pageSignatures.has(signature)) {
            warnings.push("Shopee trả lặp một trang review khi dùng truy vấn không lọc sao.");
            reportProgress("page_done");
            break;
          }
          pageSignatures.add(signature);
          addReviews(page);
          offset += page.length;
          scanned += page.length;
          updateTotal(data);
          reportProgress("page_done");
          if (!hasRoomForReviews()
            || data.has_more === false
            || (data.has_more !== true && page.length < PAGE_SIZE)) break;
          await wait();
        }
        reportProgress("star_done");
      }

      reportProgress("complete");
      const reviews = stars.flatMap(star => byStar.get(star));
      window.postMessage({
        source: RESULT_SOURCE,
        requestId,
        ok: true,
        data: {
          ok: true,
          product: {
            shopid: String(ids.shopid), itemid: String(ids.itemid),
            url: `https://shopee.vn/product/${encodeURIComponent(ids.shopid)}/${encodeURIComponent(ids.itemid)}`,
            page_url: location.href
          },
          collected_at: new Date().toISOString(),
          source: "Shopee public item ratings endpoint, fetched in product page context",
          crawl_strategy: fallbackUsed ? "star_filter_with_unfiltered_fallback" : "sequential_star_filter_type_5_to_1",
          crawl_warnings: warnings,
          crawl_note: fallbackUsed ? fallbackReason : "",
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
