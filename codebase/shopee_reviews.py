"""Fetch public Shopee product reviews through the configured Apify actor.

This adapter uses only the Python standard library. It deliberately returns a
small, anonymized review shape and does not retain reviewer names or media URLs.
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


ACTOR_ID = "themineworks~shopee-reviews-scraper"
APIFY_API = "https://api.apify.com/v2"
SHOPEE_HOST = "shopee.vn"
_PRODUCT_PATH = re.compile(r"^/product/(\d+)/(\d+)/?$")
_SLUG_PRODUCT = re.compile(r"-i\.(\d+)\.(\d+)(?:[/?#]|$)")
_EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
_PHONE = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s().-]*\d){8,10}(?!\d)")


def _product_url(value):
    """Validate a canonical Shopee VN product URL and return it with IDs."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Vui lòng cung cấp link sản phẩm Shopee.vn.")
    parsed = urllib.parse.urlsplit(value.strip())
    if parsed.scheme not in ("http", "https") or parsed.hostname != SHOPEE_HOST:
        raise ValueError("Chỉ hỗ trợ link sản phẩm công khai trên shopee.vn.")
    match = _PRODUCT_PATH.match(parsed.path) or _SLUG_PRODUCT.search(parsed.path)
    if not match:
        raise ValueError("Link chưa có mã sản phẩm Shopee hợp lệ.")
    return urllib.parse.urlunsplit(("https", SHOPEE_HOST, parsed.path, parsed.query, "")), match.groups()


def _request_json(url, token, payload=None, timeout=190):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="GET" if data is None else "POST")
    request.add_header("Authorization", "Bearer " + token)
    request.add_header("Accept", "application/json")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise RuntimeError("Apify từ chối xác thực; kiểm tra APIFY_TOKEN.") from None
        raise RuntimeError("Apify trả lỗi HTTP %s khi lấy review." % exc.code) from None
    except urllib.error.URLError:
        raise RuntimeError("Không kết nối được Apify để lấy review Shopee.") from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError("Apify trả dữ liệu không đúng định dạng JSON.") from None


def _anonymize_text(value):
    text = str(value or "")
    text = _EMAIL.sub("[ẩn email]", text)
    return _PHONE.sub("[ẩn số điện thoại]", text)


def fetch_product_reviews(url, max_reviews=100):
    """Fetch public reviews for one Shopee VN listing.

    Input: product URL and max_reviews (1–5000). Output: product IDs, normalized
    reviews and provider coverage metadata. Read-only third-party scraping; it
    does not modify Shopee or contact reviewers.
    """
    product_url, (shop_id, item_id) = _product_url(url)
    if isinstance(max_reviews, bool) or not isinstance(max_reviews, int) or not 1 <= max_reviews <= 5000:
        raise ValueError("max_reviews phải là số nguyên từ 1 đến 5000.")
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Chưa cấu hình APIFY_TOKEN trong biến môi trường.")

    run_url = APIFY_API + "/acts/" + ACTOR_ID + "/runs?waitForFinish=180"
    run_result = _request_json(run_url, token, {
        "startUrls": [product_url],
        "maxReviewsPerProduct": max_reviews,
        "withCommentOnly": False,
        "includeSummary": True,
    })
    run = run_result.get("data") or {}
    status = run.get("status")
    if status != "SUCCEEDED":
        raise RuntimeError("Tác vụ crawl chưa hoàn tất (trạng thái: %s)." % (status or "không rõ"))
    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        raise RuntimeError("Apify không trả về dataset review.")

    items_url = APIFY_API + "/datasets/" + urllib.parse.quote(str(dataset_id), safe="") + "/items?clean=true&format=json&limit=10000"
    items_result = _request_json(items_url, token)
    if not isinstance(items_result, list):
        raise RuntimeError("Apify trả dataset không đúng định dạng.")

    reviews = []
    coverage = None
    provider_error = None
    for item in items_result:
        if not isinstance(item, dict):
            continue
        if item.get("_type") == "error":
            provider_error = item.get("error") or item.get("message") or "Nguồn không đọc được sản phẩm."
        elif item.get("_type") == "product_summary":
            coverage = {
                "counts_complete": item.get("counts_complete"),
                "ratings_found": item.get("ratings_found"),
                "found_with_comment": item.get("found_with_comment"),
                "coverage_note": item.get("coverage_note"),
            }
        elif item.get("review_id") is not None:
            try:
                rating = int(item.get("rating"))
            except (TypeError, ValueError):
                continue
            if not 1 <= rating <= 5:
                continue
            reviews.append({
                "review_id": str(item["review_id"]),
                "rating": rating,
                "text": _anonymize_text(item.get("comment")).strip(),
                "date": str(item.get("created_at") or ""),
                "variant": str(item.get("variant") or "").strip(),
                "url": product_url,
            })

    if provider_error and not reviews:
        raise RuntimeError("Nguồn crawl báo lỗi: %s" % str(provider_error)[:240])
    return {
        "product": {"shop_id": shop_id, "item_id": item_id, "url": product_url},
        "reviews": reviews,
        "coverage": coverage or {"counts_complete": None, "ratings_found": len(reviews), "coverage_note": "Nguồn không trả thông tin độ phủ."},
        "source": "Apify actor themineworks/shopee-reviews-scraper",
    }
