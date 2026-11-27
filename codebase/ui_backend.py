"""Adapter UI cho backend Shopee của Tuyên; không sinh hoặc suy diễn rủi ro."""
import re

import agent
from ai import MODEL_PROVIDER
from shopee_reviews import _anonymize_text, _product_url

MAX_REVIEWS = 250
MAX_PER_STAR = 50
MAX_REVIEW_CHARS = 3000
MAX_BODY_BYTES = 2 * 1024 * 1024
DEMO_URL = "https://shopee.vn/product/1/1"


def prepare_reviews(incoming):
    """Chuẩn hóa giống extension: không tự gán số sao hoặc mang tên người mua vào model."""
    if not isinstance(incoming, list) or len(incoming) > MAX_REVIEWS:
        raise ValueError("Cần danh sách tối đa 250 review, có số sao 1–5.")
    cleaned = []
    for item in incoming:
        if not isinstance(item, dict):
            raise ValueError("Mỗi review phải có số sao và nội dung.")
        rating = item.get("rating_star", item.get("rating"))
        if type(rating) is not int or not 1 <= rating <= 5:
            raise ValueError("Mỗi review cần số sao nguyên từ 1 đến 5; không tự suy đoán số sao.")
        comment = item.get("comment", item.get("text", ""))
        if not isinstance(comment, str) or len(comment) > MAX_REVIEW_CHARS:
            raise ValueError("Nội dung mỗi review phải là chuỗi tối đa 3.000 ký tự.")
        date, variant = item.get("date", ""), item.get("variant", "")
        if not isinstance(date, str) or not isinstance(variant, str):
            raise ValueError("Ngày và biến thể phải là chuỗi nếu được cung cấp.")
        cleaned.append({"rating_star": rating, "comment": _anonymize_text(comment),
                        "date": date[:80], "variant": _anonymize_text(variant)[:160]})
    return cleaned


def analyze_for_ui(request):
    """Gọi chính crawler/analyze_reviews của backend một lần, giữ nguyên schema trả về."""
    if not isinstance(request, dict) or not isinstance(request.get("mode"), str) or request["mode"] not in {"link", "reviews"}:
        raise ValueError("Chọn lấy review từ link hoặc dán review có số sao.")
    if not isinstance(request.get("url"), str):
        raise ValueError("Hãy nhập link sản phẩm Shopee.vn.")
    url, _ = _product_url(request["url"])
    if request["mode"] == "link":
        if url == DEMO_URL:
            raise ValueError("Đây là URL minh họa; hãy nhập link sản phẩm thật để lấy review.")
        collected = agent.crawl_shopee_reviews(url)
        reviews = prepare_reviews(collected["reviews"])
        coverage = collected["coverage"]
    else:
        reviews = prepare_reviews(request.get("reviews"))
        per_star = {str(star): sum(r["rating_star"] == star for r in reviews) for star in range(1, 6)}
        coverage = {"counts_complete": None, "source": "Review người dùng cung cấp; chưa xác nhận độ phủ",
                    "max_per_star": MAX_PER_STAR, "collected_per_star": per_star}
    analysis = agent.analyze_reviews(url, reviews, coverage)
    # Không chuyển fake/insufficient thành rủi ro do UI tự tạo.
    if not isinstance(analysis, dict) or analysis.get("status") not in {"risks", "no_clear_risk", "insufficient"}:
        raise RuntimeError("Backend trả cấu trúc không được hỗ trợ.")
    if not isinstance(analysis.get("risks"), list) or len(analysis["risks"]) > 3:
        raise RuntimeError("Backend trả danh sách rủi ro không hợp lệ.")
    sources = {}
    for risk in analysis["risks"]:
        if not isinstance(risk, dict) or not isinstance(risk.get("citations"), list):
            raise RuntimeError("Backend thiếu nguồn trích dẫn.")
        for source in risk["citations"]:
            if not isinstance(source, dict) or not isinstance(source.get("text"), str) or not re.fullmatch(r"R\d{2,3}", str(source.get("id", ""))):
                raise RuntimeError("Backend trả nguồn trích dẫn không hợp lệ.")
            sources[source["id"]] = source
    return {"analysis": analysis, "sources": list(sources.values()), "coverage": coverage,
            "input_review_count": len(reviews), "mock": MODEL_PROVIDER == "fake"}


def public_error(exc):
    """Không đưa body lỗi nhà cung cấp hoặc credential ra giao diện."""
    if isinstance(exc, ValueError):
        return str(exc)
    message = str(exc)
    if "APIFY_TOKEN" in message:
        return "Chưa có cấu hình Apify hợp lệ để lấy review từ link. Có thể dùng chế độ dán review có số sao."
    if "API_KEY" in message or "MODEL_NAME" in message:
        return "Chưa cấu hình đầy đủ OpenAI trong .env. Kiểm tra API_KEY và MODEL_NAME trên máy chạy backend."
    status = re.search(r"HTTP\s+(\d{3})", message)
    if status:
        return "Dịch vụ trả HTTP %s; chưa có kết quả để kết luận. Hãy kiểm tra cấu hình hoặc thử lại." % status.group(1)
    return "Không thể hoàn tất lấy review hoặc phân tích. Nội dung đã nhập vẫn được giữ để bạn thử lại."
