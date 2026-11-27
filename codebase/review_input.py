"""Kiểm đầu vào review dùng chung cho answer, web và extension."""
from shopee_reviews import _anonymize_text

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
