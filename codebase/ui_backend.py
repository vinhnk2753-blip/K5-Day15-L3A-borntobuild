"""Adapter UI thuần: gọi backend main, không lọc nhiễu hoặc dựng rủi ro riêng."""
import json
import re
from pathlib import Path

import ai
import agent

MAX_REVIEWS = 250
MAX_REVIEW_CHARS = 3000
MAX_TEXT_CHARS = 800000
MAX_BODY_BYTES = 2 * 1024 * 1024
ROOT = Path(__file__).resolve().parent.parent


def catalog_products():
    with (ROOT / "data" / "catalog.json").open(encoding="utf-8") as stream:
        return json.load(stream)["products"]


def analyze_for_ui(request):
    """Nhận catalog/reviews/payload, gọi đúng một điểm vào của backend main."""
    if not isinstance(request, dict):
        raise ValueError("Đầu vào API phải là object.")
    mode = request.get("mode")
    if mode == "catalog":
        code = request.get("product_id")
        if not isinstance(code, str) or code not in {p["product_code"] for p in catalog_products()}:
            raise ValueError("Chọn mã sản phẩm có trong catalog.")
        reply = agent.answer(code)
    elif mode == "reviews":
        text = request.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Hãy dán tập review văn bản, mỗi review một dòng.")
        lines = text.splitlines()
        if len(text) > MAX_TEXT_CHARS or len(lines) > MAX_REVIEWS or any(len(line) > MAX_REVIEW_CHARS for line in lines):
            raise ValueError("Tối đa 250 dòng, mỗi dòng 3.000 ký tự.")
        reply = agent.answer(text)
    elif mode == "payload":
        payload = request.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("Payload Shopee phải là object có URL và reviews.")
        reply = agent.analyze_review_payload(payload)
    else:
        raise ValueError("Chọn catalog, dán review hoặc payload Shopee.")
    if not isinstance(reply, dict) or not isinstance(reply.get("output"), str):
        raise RuntimeError("Backend thiếu output dạng chuỗi.")
    analysis = reply.get("structured")
    if analysis is None:
        # Backend cố ý trả hướng dẫn thay vì structured khi chỉ nhận link/không có review.
        return {"analysis": {"status": "invalid_input", "summary": reply["output"], "risks": []},
                "sources": [], "mock": ai.MODEL_PROVIDER == "fake"}
    if not isinstance(analysis, dict) or analysis.get("status") not in {"risks", "no_clear_risk", "insufficient"}:
        raise RuntimeError("Backend trả trạng thái không được hỗ trợ.")
    if not isinstance(analysis.get("stats"), dict) or not isinstance(analysis.get("flags"), list) or not all(isinstance(flag, str) for flag in analysis["flags"]):
        raise RuntimeError("Backend trả thống kê/cờ không hợp lệ.")
    if not isinstance(analysis.get("anomalies"), dict) or not isinstance(analysis.get("reviews_by_id"), dict):
        raise RuntimeError("Backend thiếu anomaly hoặc nguồn review.")
    risks = analysis.get("risks")
    if not isinstance(risks, list) or len(risks) > 3:
        raise RuntimeError("Backend trả danh sách rủi ro không hợp lệ.")
    metadata = {}
    for risk in risks:
        if not isinstance(risk, dict) or not isinstance(risk.get("citations"), list):
            raise RuntimeError("Backend thiếu citation.")
        for source in risk["citations"]:
            if not isinstance(source, dict) or source.get("id") not in analysis["reviews_by_id"]:
                raise RuntimeError("Backend trả citation không có trong nguồn.")
            metadata[source["id"]] = source
        for source in risk.get("counter_citations") or []:
            if not isinstance(source, dict) or source.get("id") not in analysis["reviews_by_id"]:
                raise RuntimeError("Backend trả counter_citation không có trong nguồn.")
            metadata[source["id"]] = source
    sources = []
    for rid, text in analysis["reviews_by_id"].items():
        if not re.fullmatch(r"R\d{1,3}", rid) or not isinstance(text, str):
            raise RuntimeError("Backend trả nguồn không hợp lệ.")
        sources.append({**metadata.get(rid, {}), "id": rid, "text": text})
    return {"analysis": analysis, "sources": sources, "mock": ai.MODEL_PROVIDER == "fake"}


def public_error(exc):
    """Thông báo ngắn; không lộ body lỗi nhà cung cấp hoặc credential."""
    if isinstance(exc, ValueError):
        return str(exc)
    message = str(exc)
    if "API_KEY" in message or "MODEL_NAME" in message:
        return "Chưa cấu hình đầy đủ OpenAI trên máy chạy backend. Kiểm tra API_KEY và MODEL_NAME trong .env."
    status = re.search(r"HTTP\s+(\d{3})", message)
    if status:
        return "Dịch vụ trả HTTP %s; hãy kiểm tra cấu hình hoặc thử lại." % status.group(1)
    return "Chưa hoàn tất phân tích. Nội dung đã nhập vẫn được giữ để bạn thử lại."
