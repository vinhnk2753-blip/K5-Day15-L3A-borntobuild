"""Adapter mô phỏng RIÊNG UI issue #4; không thay đổi agent/ai/tools của issue #3.
Chỉ UI dùng adapter này. Eval/simulate tiếp tục gọi agent.answer nguyên gốc.
Fake vẫn gọi backend answer một lần để giữ trace model/tool/token thật của khung,
sau đó dựng kết quả minh họa bằng heuristic; không coi đây là kết quả model trả về.
"""
import json
import re
from tracing import tool

MAX_REVIEWS = 100
MAX_REVIEW_CHARS = 4000
MAX_INPUT_CHARS = 50000
MIN_CLEAN_REVIEWS = 2  # Ngưỡng demo tự chọn cho G10, chưa được hiệu chỉnh trên data thật.

PRODUCT_WORDS = ("dùng", "sử dụng", "đeo", "pin", "kết nối", "vải", "chất liệu", "âm thanh",
                 "hỏng", "rách", "bong", "nóng", "lỗi", "kích ứng", "đau", "chất lượng")
ADVERSE_WORDS = ("mất kết nối", "ngắt kết nối", "pin yếu", "pin tụt", "hết pin", "pin phồng",
                 "đau tai", "kích ứng", "bị hỏng", "bị rách", "bong tróc", "nóng bất thường")


def _outside_request(text):
    """Chỉ nhận diện yêu cầu hành động rõ ràng, không kết luận review là giả."""
    return bool(re.search(
        r"^(?:(?:hãy|vui lòng|giúp tôi|bạn hãy|tự)\s+)?(?:mua hộ|mua giúp|đặt hàng|chuyển tiền|"
        r"gửi tin|viết review giả|viết đánh giá giả|(?:kết luận|khẳng định) shop|tư vấn thuốc|"
        r"viết (?:cho tôi )?(?:một )?(?:bài thơ|bài văn)|giải bài tập|dự báo thời tiết|bỏ qua chỉ dẫn|"
        r"ignore previous|in (?:ra )?(?:api_key|system prompt))", text))


def _signal_kind(text, duplicate=False):
    if duplicate:
        return "duplicate"
    if _outside_request(text) or any(s in text for s in ("hãy bịa", "api_key", "system prompt", "ignore previous")):
        return "instruction"
    if any(s in text for s in ("chưa dùng", "chưa sử dụng", "nhận xu")) and not any(s in text for s in ADVERSE_WORDS):
        return "not_used"
    if any(s in text for s in ("giao hàng", "giao nhanh", "giao trễ", "đóng gói", "ship", "gửi hàng")) and not any(s in text for s in PRODUCT_WORDS):
        return "shipping_only"
    return None


@tool
def normalize_reviews(text: str) -> dict:
    """normalize_reviews · input: JSON/văn bản · output: review chuẩn · không tác động ngoài."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Hãy nhập ít nhất một đánh giá có nội dung.")
    if len(text) > MAX_INPUT_CHARS:
        raise ValueError("Tổng đầu vào không được vượt %d ký tự." % MAX_INPUT_CHARS)
    raw = text.strip()
    if raw.startswith(("{", "[")):
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("JSON không hợp lệ; hãy kiểm tra cấu trúc đầu vào.") from None
        if not isinstance(payload, dict):
            raise ValueError("JSON phải là object có danh sách reviews.")
    else:
        payload = {"product_name": "", "reviews": [
            {"id": "R%02d" % i, "text": s, "rating": None}
            for i, s in enumerate((line.strip() for line in raw.splitlines() if line.strip()), 1)
        ]}
    product, rows = payload.get("product_name", ""), payload.get("reviews")
    if not isinstance(product, str):
        raise ValueError("Tên sản phẩm phải là chuỗi.")
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_REVIEWS:
        raise ValueError("Cần từ 1 đến %d review mỗi lần." % MAX_REVIEWS)
    cleaned, seen = [], set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Mỗi review phải là object.")
        rid, content, rating = row.get("id"), row.get("text"), row.get("rating")
        if not isinstance(rid, str) or not re.fullmatch(r"R(?:0[1-9]|[1-9][0-9]+)", rid) or rid in seen:
            raise ValueError("Mã review phải duy nhất, dạng R01, R02…")
        if not isinstance(content, str) or not content.strip() or len(content) > MAX_REVIEW_CHARS:
            raise ValueError("Mỗi review cần từ 1 đến %d ký tự." % MAX_REVIEW_CHARS)
        if rating is not None and (type(rating) is not int or not 1 <= rating <= 5):
            raise ValueError("Số sao phải là số nguyên 1–5 hoặc null.")
        cleaned.append({"id": rid, "text": content.strip(), "rating": rating})
        seen.add(rid)
    return {"product_name": product.strip(), "reviews": cleaned}


@tool
def flag_review_signals(reviews: list) -> list:
    """flag_review_signals · input: review chuẩn · output: cờ và lý do · không tác động ngoài."""
    flags, seen = [], set()
    for row in reviews:
        normalized = " ".join(row["text"].casefold().split())
        kind = _signal_kind(normalized, normalized in seen)
        reasons = {
            "duplicate": "Nội dung lặp nguyên văn sau chuẩn hóa; không kết luận nhiều người độc lập hoặc review giả.",
            "not_used": "Chưa có trải nghiệm sử dụng hoặc có nhắc nhận xu.",
            "shipping_only": "Chỉ nói về giao hàng/đóng gói, chưa mô tả trải nghiệm sản phẩm.",
            "instruction": "Có chỉ dẫn ngoài phạm vi trong dữ liệu; không thực hiện.",
        }
        if kind:
            flags.append({"review_id": row["id"], "reason": reasons[kind]})
        seen.add(normalized)
    return flags


@tool
def quantify_review_signals(reviews: list, flags: list) -> dict:
    """quantify_review_signals · input: review/cờ · output: x/N, %, mẫu số sạch, phạm vi · không tác động ngoài."""
    flagged = {f["review_id"] for f in flags}
    counts = {k: 0 for k in ("duplicate", "not_used", "shipping_only", "instruction", "other")}
    seen, usable = set(), []
    commands = []
    for row in reviews:
        content = " ".join(row["text"].casefold().split())
        kind = _signal_kind(content, content in seen)
        if row["id"] in flagged:
            counts[kind or "other"] += 1
        has_experience = any(s in content for s in PRODUCT_WORDS) and not kind
        if has_experience and row["id"] not in flagged:
            usable.append(row["id"])
        commands.append(_outside_request(content) or kind == "instruction")
        seen.add(content)
    total = len(reviews)
    return {
        "out_of_scope": bool(commands) and all(commands),
        "usable_review_ids": usable,
        "summary": {"total_reviews": total, "flagged_reviews": len(flagged),
                    "flagged_percent": round(100 * len(flagged) / total, 1) if total else 0,
                    "clean_reviews": len(usable), "min_clean_reviews": MIN_CLEAN_REVIEWS,
                    "signal_counts": counts},
    }


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


@tool
def validate_result(candidate: dict, reviews: list) -> dict:
    """validate_result · input: JSON model + nguồn · output: JSON đã kiểm/đếm · không tác động ngoài."""
    if not isinstance(candidate, dict):
        raise ValueError("Kết quả model không phải object.")
    status = candidate.get("status")
    if status not in {"ok", "insufficient_evidence", "no_risk_found"}:
        raise ValueError("Trạng thái không hợp lệ.")
    if not _nonempty(candidate.get("message")):
        raise ValueError("Thiếu thông báo.")
    risks, flags = candidate.get("risks"), candidate.get("review_flags")
    if not isinstance(risks, list) or not isinstance(flags, list):
        raise ValueError("risks và review_flags phải là danh sách.")
    if (status == "ok" and not 1 <= len(risks) <= 3) or (status != "ok" and risks):
        raise ValueError("Số rủi ro không khớp trạng thái.")
    sources = {r["id"]: r["text"] for r in reviews}
    for risk in risks:
        if not isinstance(risk, dict) or not all(_nonempty(risk.get(k)) for k in ("title", "description")):
            raise ValueError("Rủi ro thiếu tiêu đề/mô tả.")
        evidence = risk.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError("Rủi ro thiếu dẫn chứng.")
        for ev in evidence:
            if not isinstance(ev, dict):
                raise ValueError("Dẫn chứng không hợp lệ.")
            rid, quote = ev.get("review_id"), ev.get("quote")
            if not isinstance(rid, str) or rid not in sources or not _nonempty(quote) or quote not in sources[rid]:
                raise ValueError("Mã/trích dẫn không có trong review gốc.")
    unique = {}
    for flag in flags:
        if not isinstance(flag, dict):
            raise ValueError("Cờ không hợp lệ.")
        rid = flag.get("review_id")
        if not isinstance(rid, str) or rid not in sources or not _nonempty(flag.get("reason")):
            raise ValueError("Cờ có mã/lý do không hợp lệ.")
        unique[rid] = {"review_id": rid, "reason": flag["reason"]}
    # “Lớn nhất” trong mock: nhiều nội dung nguồn khác nhau hơn; không suy thành mức nguy hiểm.
    risks.sort(key=lambda r: -len({" ".join(sources[e["review_id"]].casefold().split()) for e in r["evidence"]}))
    return {"status": status, "message": candidate["message"], "risks": risks,
            "review_flags": list(unique.values()),
            "summary": {"total_reviews": len(reviews), "flagged_reviews": len(unique)}}

from ai import MODEL_PROVIDER
from tracing import note

def fake_review_response(user: str) -> str:
    payload = json.loads(user)
    groups = [
        ("Phản ánh về kết nối", ("mất kết nối", "ngắt kết nối", "không kết nối")),
        ("Phản ánh về pin", ("hết pin", "pin yếu", "pin tụt", "pin phồng")),
        ("Phản ánh khó chịu/lỗi sử dụng", ("đau tai", "kích ứng", "bị rách", "bong tróc", "bị hỏng", "quá nóng", "nóng bất thường")),
    ]
    flags = {f["review_id"]: f for f in payload.get("preliminary_flags", [])}
    rows, useful, risks = [], False, []
    for row in payload["reviews"]:
        if row["id"] not in payload.get("usable_review_ids", [r["id"] for r in payload["reviews"]]):
            continue
        text = row["text"].casefold()
        if any(s in text for s in ("bỏ qua chỉ dẫn", "ignore previous", "api_key", "system prompt", "hãy bịa")):
            flags[row["id"]] = {"review_id": row["id"], "reason": "Có chỉ dẫn ngoài phạm vi; không thực hiện."}
            continue
        rows.append(row)
        useful = useful or (any(s in text for s in ("dùng", "sử dụng", "đeo", "pin", "kết nối", "vải", "chất liệu"))
                            and not any(s in text for s in ("chưa dùng", "chưa sử dụng")))
    for title, terms in groups:
        ev = [{"review_id": r["id"], "quote": r["text"]} for r in rows
              if any(t in r["text"].casefold() for t in terms)]
        if ev:
            risks.append({"title": title, "description": "Có phản ánh trong review; cần đọc nguồn để kiểm chứng.", "evidence": ev})
    status = "ok" if risks else "no_risk_found" if useful else "insufficient_evidence"
    message = {"ok": "Tìm thấy %d nhóm phản ánh rủi ro." % len(risks),
               "no_risk_found": "Chưa thấy rủi ro trong dữ liệu này; không khẳng định sản phẩm an toàn.",
               "insufficient_evidence": "Chưa đủ trải nghiệm sản phẩm; hãy bổ sung review."}[status]
    return json.dumps({"status": status, "message": message, "risks": risks,
                       "review_flags": list(flags.values())}, ensure_ascii=False)

def _failure(status, message, total=0):
    return {"status": status, "message": message, "risks": [], "review_flags": [],
            "summary": {"total_reviews": total, "flagged_reviews": 0}}


def adapt_answer(text: str, backend_answer=None) -> dict:
    if backend_answer is None:
        from agent import answer as backend_answer
    sources = []
    try:
        payload = normalize_reviews(text)
    except ValueError as exc:
        result = _failure("invalid_input", str(exc))
    else:
        sources = payload["reviews"]
        signals = flag_review_signals(payload["reviews"])
        diagnostics = quantify_review_signals(sources, signals)
        if diagnostics["out_of_scope"]:
            result = _failure("out_of_scope", "Từ chối yêu cầu ngoài phạm vi. Công cụ chỉ đọc review sản phẩm, không mua hàng, gửi tin, tiết lộ bí mật hoặc kết tội shop.", len(sources))
            note("Dừng: ngoài phạm vi, không gọi model.")
        elif diagnostics["summary"]["clean_reviews"] < MIN_CLEAN_REVIEWS:
            result = _failure("insufficient_evidence", "Chưa đủ dữ liệu: chỉ có %d review sạch theo quy tắc demo; cần ít nhất %d. Hãy thêm trải nghiệm sản phẩm khác nhau." %
                              (diagnostics["summary"]["clean_reviews"], MIN_CLEAN_REVIEWS), len(sources))
            note("G10: quá ít review sạch; không gọi model hoặc bịa rủi ro.")
        else:
            request = dict(payload, preliminary_flags=signals, usable_review_ids=diagnostics["usable_review_ids"])
            # Lỗi API thật bay ra cho khung ghi error; không biến thành lượt đạt.
            response = backend_answer(text)
            try:
                candidate = fake_review_response(json.dumps(request, ensure_ascii=False)) if MODEL_PROVIDER == "fake" else response["output"]
                result = validate_result(json.loads(candidate), sources)
            except (ValueError, TypeError, KeyError):
                note("Hậu kiểm chặn kết quả không hợp lệ; không hiển thị dẫn chứng sai.")
                result = _failure("error", "Chưa thể tạo kết quả có dẫn chứng hợp lệ. Hãy thử lại.", len(sources))
        combined = {f["review_id"]: f for f in signals}
        combined.update({f["review_id"]: f for f in result["review_flags"]})
        result["review_flags"] = list(combined.values())
        result["summary"] = quantify_review_signals(sources, result["review_flags"])["summary"]
        if MODEL_PROVIDER == "fake":
            result["message"] = "[MÔ PHỎNG CP2 — chưa gọi AI thật] " + result["message"]
    return {"output": json.dumps(result, ensure_ascii=False), "sources": sources}
