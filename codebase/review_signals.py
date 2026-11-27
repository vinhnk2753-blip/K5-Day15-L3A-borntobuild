"""Quy tắc minh bạch cho prototype; không xác minh tính thật/giả của review."""
import re
import unicodedata

MIN_CLEAN_REVIEWS = 3
LABELS = {
    "empty": "Trống / chỉ có dấu câu",
    "duplicate": "Nội dung lặp sau chuẩn hóa",
    "reward": "Đánh giá để nhận thưởng",
    "not_used": "Chưa dùng / chưa trải nghiệm",
    "shipping_only": "Chỉ nói giao hàng / dịch vụ",
    "generic": "Khen chung, không có chi tiết",
}
PRODUCT_TERMS = ("pin", "sạc", "kết nối", "âm thanh", "chất lượng", "chất liệu", "vải", "đeo",
                 "tai", "lỗi", "hỏng", "nóng", "màn hình", "camera", "chiên", "nồi", "công suất",
                 "rỉ", "bong", "hoàn thiện", "bền", "flagship", "sử dụng", "dùng")
SHIPPING_TERMS = ("ship", "shipping", "giao", "giao hàng", "vận chuyển", "đóng gói", "shop", "nhân viên")


def normalize(text):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFC", text).casefold()))


def contains(text, phrases):
    return any(re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text) for phrase in phrases)


def signals_for(sources, input_total=None):
    """Đếm mỗi review vào tối đa một loại nhiễu; giữ ID để đối chiếu nguyên văn."""
    seen, kept, flags = {}, [], []
    counts = {key: 0 for key in LABELS}
    for source in sources:
        text = normalize(source["text"])
        label, duplicate_of = None, None
        if not text:
            label = "empty"
        elif text in seen:
            label, duplicate_of = "duplicate", seen[text]
        elif contains(text, ("nhận xu", "kiếm xu", "nhận thưởng", "lấy xu")):
            label = "reward"
        elif contains(text, ("chưa dùng", "chưa sử dụng", "chưa trải nghiệm", "chưa dùng thử")):
            label = "not_used"
        else:
            # Lời xin lỗi không phải thuộc tính/lỗi sản phẩm.
            product_text = re.sub(r"(?<!\w)xin lỗi(?!\w)", "", text)
            if contains(text, SHIPPING_TERMS) and not contains(product_text, PRODUCT_TERMS):
                label = "shipping_only"
            elif re.fullmatch(r"(?:sản phẩm |hàng )?(?:rất )?(?:tốt|ok|ổn|đẹp|tuyệt vời|chất lượng tốt)", text):
                label = "generic"
        if text:
            seen.setdefault(text, source["id"])
        if label:
            counts[label] += 1
            flag = {"kind": label, "label": LABELS[label], "citations": [source]}
            if duplicate_of:
                flag["duplicate_of"] = duplicate_of
            flags.append(flag)
        else:
            kept.append(source)
    total = len(sources)
    filtered = sum(counts.values())
    stats = {"input_total": total if input_total is None else input_total, "total": total,
             "excluded_limit": max(0, (total if input_total is None else input_total) - total),
             "filtered_noise": filtered, "kept_clean": len(kept),
             "noise_pct": round(filtered * 100 / total, 1) if total else 0.0,
             "noise_breakdown": counts, "min_clean_reviews": MIN_CLEAN_REVIEWS,
             "method": "Quy tắc prototype: đếm trên mẫu nhận được, không xác minh review thật/giả."}
    anomalies = []
    if counts["duplicate"]:
        anomalies.append("%d/%d review lặp nội dung sau chuẩn hóa; không đủ để kết luận seeding." % (counts["duplicate"], total))
    if filtered:
        anomalies.append("%d/%d review bị loại theo quy tắc (%s%%)." % (filtered, total, stats["noise_pct"]))
    return {"stats": stats, "flags": flags, "anomalies": anomalies, "kept": kept}


def mock_risks(sources):
    """Sinh minh họa theo cụm từ trong input, không phải kết luận AI hay tra câu thử."""
    groups = [
        ("Kết nối không ổn định", ("mất kết nối", "ngắt kết nối", "chập chờn")),
        ("Thời lượng pin / sạc", ("pin yếu", "pin tụt", "pin nhanh hết", "chai pin", "không sạc", "hết pin")),
        ("Cảm giác khi sử dụng", ("đau tai", "khó chịu", "đeo chật", "kích ứng")),
        ("Độ bền và hoàn thiện", ("bong sơn", "rỉ sét", "bị hỏng", "bị vỡ")),
        ("Nhiệt độ khi sử dụng", ("quá nóng", "nóng bất thường", "nóng máy")),
    ]
    risks = []
    for title, phrases in groups:
        matched = []
        for source in sources:
            text = normalize(source["text"])
            # Không biến lời phủ định lỗi thành bằng chứng lỗi trong chế độ giả.
            for phrase in phrases:
                pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
                for match in re.finditer(pattern, text):
                    prefix = text[max(0, match.start() - 40):match.start()]
                    if not re.search(r"(?:không|chưa|hết)(?:\s+(?:bị|còn|thấy|gặp|có|hiện tượng)){0,3}\s*$", prefix):
                        matched.append(source)
                        break
                if source in matched:
                    break
        if matched:
            risks.append({"title": title, "summary": "Minh họa từ %d review có cụm từ liên quan; cần đối chiếu nguyên văn, chưa phải phân tích AI thật." % len(matched),
                          "severity": "medium", "citations": matched})
    return sorted(risks, key=lambda risk: -len(risk["citations"]))[:3]
