"""Adapter web gọi answer(text); không có bộ phân tích hoặc fake riêng."""
import json
import re

import agent
from ai import MODEL_PROVIDER
from review_input import (MAX_REVIEWS, MAX_PER_STAR, MAX_REVIEW_CHARS, MAX_BODY_BYTES,
                          DEMO_URL, prepare_reviews)


def analyze_for_ui(request):
    """Một lần gọi answer; chuyển structured sang payload web và gom nguồn Rxx."""
    if not isinstance(request, dict):
        raise ValueError("Đầu vào API phải là object.")
    reply = agent.answer(json.dumps(request, ensure_ascii=False))
    if not isinstance(reply.get("output"), str):
        raise RuntimeError("Backend thiếu output dạng chuỗi.")
    analysis = reply.get("structured")
    if not isinstance(analysis, dict) or analysis.get("status") not in {"risks", "no_clear_risk", "insufficient"}:
        raise RuntimeError("Backend trả cấu trúc không được hỗ trợ.")
    if not isinstance(analysis.get("risks"), list) or len(analysis["risks"]) > 3:
        raise RuntimeError("Backend trả danh sách rủi ro không hợp lệ.")
    sources = {}
    for entry in analysis["risks"] + analysis.get("flags", []):
        if not isinstance(entry, dict) or not isinstance(entry.get("citations"), list):
            raise RuntimeError("Backend thiếu nguồn trích dẫn.")
        for source in entry["citations"]:
            if not isinstance(source, dict) or not isinstance(source.get("text"), str) or not re.fullmatch(r"R\d{2,3}", str(source.get("id", ""))):
                raise RuntimeError("Backend trả nguồn trích dẫn không hợp lệ.")
            sources[source["id"]] = source
    return {"analysis": analysis, "sources": list(sources.values()), "coverage": reply.get("coverage"),
            "input_review_count": reply.get("input_review_count"), "mock": MODEL_PROVIDER == "fake"}


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
