"""Read-only tools for the CP3 review-risk prototype (catalog, parser, noise filter, anomaly counter, optional Apify adapter)."""
import json
import os
import re
import unicodedata
from pathlib import Path

from tracing import tool, TOOLS  # noqa: F401
from shopee_reviews import fetch_product_reviews

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
_INLINE_REVIEW_ID = re.compile(r"(?<![A-Za-z0-9])\[?(R\d{1,3})\]?\s*\|", re.IGNORECASE)
_BRACKET_REVIEW_ID = re.compile(r"^\s*\[(R\d{1,3})\]\s*(?:[|:-]\s*)?(.*)$", re.IGNORECASE)
_PLAIN_REVIEW_ID = re.compile(r"^\s*(R\d{1,3})\s*(?:\||:|-)\s*(.*)$", re.IGNORECASE)
_RATING_ONLY = re.compile(r"^\s*([1-5])\s*(?:sao|\*|★)\s*$", re.IGNORECASE)
_LEADING_RATING = re.compile(r"^\s*([1-5])\s*(?:sao|\*|★)\s*(?:\||:|-)\s*(.*)$", re.IGNORECASE)

_EMPTY_COMMENTS = {
    "",
    "khong co binh luan",
    "khong binh luan",
    "chua co binh luan",
    "khong nhan xet",
    "khong co nhan xet",
}


def _plain(value):
    value = unicodedata.normalize("NFD", str(value or "").lower())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return value.replace("đ", "d")


def _normalize_plain(value):
    text = re.sub(r"[^a-z0-9 ]+", " ", _plain(value))
    return " ".join(text.split())


def _normalize_nfc(value):
    text = unicodedata.normalize("NFC", str(value or "").lower())
    text = re.sub(r"[^\w ]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def _is_empty_comment(normalized_plain: str) -> bool:
    return normalized_plain in _EMPTY_COMMENTS


def _looks_like_review_batch(text: str) -> bool:
    """Return True when input contains pasted review lines/markers rather than a catalog lookup query."""
    non_empty = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    if len(non_empty) > 1:
        return True
    if not non_empty:
        return False
    first = non_empty[0]
    return bool(
        _INLINE_REVIEW_ID.search(first)
        or _BRACKET_REVIEW_ID.match(first)
        or _PLAIN_REVIEW_ID.match(first)
    )


def _extract_header_value(text: str, plain_label: str) -> str:
    """Extract value after a 'Sản phẩm:' or 'Người dùng:' prefix (optionally preceded by '(...)')."""
    plain = _plain(text).lstrip()
    match = re.match(r"^(?:\([^)]*\)\s*)?%s\s*:\s*" % re.escape(plain_label), plain)
    if not match:
        return ""
    colon_pos = text.find(":")
    if colon_pos < 0:
        return ""
    return text[colon_pos + 1:].strip()


def _has_plain_term(normalized: str, terms) -> bool:
    return any(re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(term), normalized) for term in terms)


def _has_nfc_term(lower_nfc: str, terms) -> bool:
    return any(re.search(r"(?<!\w)%s(?!\w)" % re.escape(term), lower_nfc, flags=re.UNICODE) for term in terms)


@tool
def load_product_reviews(query: str) -> dict:
    """Đọc bộ review sản phẩm mẫu trong data/catalog.json theo mã, ID hoặc tên.
    Input: mã sản phẩm (vd SP01), product_id hoặc tên sản phẩm trong catalog (không khớp tập review dán).
    Output: metadata sản phẩm và review đã chuẩn hóa, giữ mã nguồn [Rxx].
    Tác động ngoài: không; chỉ đọc file JSON cục bộ đã ẩn danh."""
    if not isinstance(query, str) or not query.strip():
        return {"ok": False, "error": "Hãy nhập mã sản phẩm hoặc tên sản phẩm trong catalog."}
    if _looks_like_review_batch(query):
        return {"ok": False, "error": "Đầu vào là tập review dán, chuyển sang trình tách review."}

    catalog_path = DATA_DIR / "catalog.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": "Không đọc được catalog.json: %s" % type(exc).__name__}

    needle = _plain(query.strip())
    products = catalog.get("products", [])
    available_codes = [str(p.get("product_code")) for p in products if p.get("product_code")]
    exact = [p for p in products if needle in {
        _plain(p.get("product_code")), _plain(p.get("product_id")), _plain(p.get("product_name"))
    }]
    matches = exact or [p for p in products if needle and (
        needle in _plain(p.get("product_name")) or _plain(p.get("product_name")) in needle
        or needle in _plain(p.get("product_id")) or _plain(p.get("product_id")) in needle
        or bool(re.search(r"\b%s\b" % re.escape(_plain(p.get("product_code"))), needle))
    )]
    if len(matches) != 1:
        return {
            "ok": False,
            "error": "Không tìm thấy duy nhất một sản phẩm trong catalog.",
            "available_codes": available_codes,
        }

    product = matches[0]
    relative = Path(str(product.get("file", "")))
    path = (ROOT / relative).resolve()
    if os.path.commonpath((str(DATA_DIR.resolve()), str(path))) != str(DATA_DIR.resolve()):
        return {"ok": False, "error": "Đường dẫn dữ liệu ngoài thư mục data/."}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": "Không đọc được dữ liệu sản phẩm: %s" % type(exc).__name__}

    reviews = []
    for item in data.get("reviews", []):
        if not isinstance(item, dict):
            continue
        reviews.append({
            "review_id": str(item.get("id", "")),
            "rating_star": item.get("rating_star"),
            "comment": str(item.get("text", "") or ""),
            "date": str(item.get("usage_duration", "") or ""),
            "variant": str(item.get("variant", "") or ""),
        })
    return {"ok": True, "product": data, "reviews": reviews,
            "source": "data/products/%s.json" % product["product_id"]}


@tool
def parse_review_text(text: str) -> dict:
    """Chuẩn hóa review người dùng dán trực tiếp, giữ mã [Rxx] và tách yêu cầu người dùng.
    Input: văn bản review dạng [R01] nội dung, R01 | 5 sao | nội dung, hoặc mỗi dòng một review.
    Output: danh sách review có mã [Rxx], sao nếu có, nội dung nguyên văn, product_name và user_request.
    Tác động ngoài: không; chỉ xử lý văn bản đầu vào trong bộ nhớ."""
    if not isinstance(text, str):
        return {"reviews": [], "user_request": "", "product_name": ""}

    reviews = []
    used = set()
    next_id = 1
    product_name = ""
    user_requests = []

    def alloc_id(candidate_id: str) -> str:
        nonlocal next_id
        rid = candidate_id.upper() if candidate_id else ""
        if not rid or rid in used:
            while "R%02d" % next_id in used:
                next_id += 1
            rid = "R%02d" % next_id
            next_id += 1
        used.add(rid)
        return rid

    def split_rating_and_comment(body: str):
        parts = [part.strip() for part in body.split("|")]
        if len(parts) >= 2:
            for index, part in enumerate(parts):
                rating_match = _RATING_ONLY.match(part)
                if rating_match:
                    remainder = " | ".join(parts[index + 1:]).strip()
                    return int(rating_match.group(1)), remainder
        leading = _LEADING_RATING.match(body)
        if leading:
            return int(leading.group(1)), leading.group(2).strip()
        return None, body.strip()

    for raw_line in text.splitlines():
        line = raw_line.strip().lstrip("-• ").strip()
        if not line:
            continue

        inline_ids = list(_INLINE_REVIEW_ID.finditer(line))
        if inline_ids:
            prefix = line[:inline_ids[0].start()].strip()
            if prefix:
                extracted_user = _extract_header_value(prefix, "nguoi dung")
                if extracted_user:
                    user_requests.append(extracted_user)
                else:
                    extracted_prod = _extract_header_value(prefix, "san pham")
                    if extracted_prod and not product_name:
                        product_name = extracted_prod.rstrip(". ")
            for index, marker in enumerate(inline_ids):
                end = inline_ids[index + 1].start() if index + 1 < len(inline_ids) else len(line)
                body = line[marker.end():end].strip()
                rating, comment = split_rating_and_comment(body)
                review_id = alloc_id(marker.group(1))
                reviews.append({"review_id": review_id, "rating_star": rating,
                                "comment": comment, "date": "", "variant": ""})
            continue

        extracted_prod = _extract_header_value(line, "san pham")
        if extracted_prod:
            if not product_name:
                product_name = extracted_prod.rstrip(". ")
            continue
        extracted_user = _extract_header_value(line, "nguoi dung")
        if extracted_user:
            user_requests.append(extracted_user)
            continue

        explicit = _BRACKET_REVIEW_ID.match(line) or _PLAIN_REVIEW_ID.match(line)
        explicit_id = explicit.group(1) if explicit else ""
        body = explicit.group(2).strip() if explicit else line
        rating, comment = split_rating_and_comment(body)
        review_id = alloc_id(explicit_id)
        reviews.append({"review_id": review_id, "rating_star": rating,
                        "comment": comment, "date": "", "variant": ""})

    return {
        "reviews": reviews,
        "user_request": " ".join(user_requests).strip(),
        "product_name": product_name,
    }


@tool
def filter_review_noise(reviews: list) -> dict:
    """Lọc review trống, ngắn, khen chung, ship/giá/ngoài chất lượng, nhận xu, chưa dùng, hỏi đáp và lặp.
    Input: danh sách review chuẩn hóa có review_id và comment.
    Output: danh sách sạch, danh sách nhiễu, nhãn lý do và tổng từng nhóm.
    Tác động ngoài: không; quy tắc xác định, không sửa dữ liệu nguồn."""
    labels = {
        "nhieu_trong": 0,
        "nhieu_khen_chung": 0,
        "nhieu_hoi_dap_rao_ban": 0,
        "nhieu_ngoai_chat_luong": 0,
        "nhieu_lap_bat_thuong": 0,
        "nhieu_nhan_xu": 0,
        "nhieu_chua_dung": 0,
        "nhieu_qua_ngan": 0,
    }
    exact_praise = {
        "tot", "ok", "dep", "hai long", "san pham tot", "sai on", "rat ok",
        "hang tot", "mau dep", "dung tot", "ok nha", "rat tot", "san pham rat tot",
        "dung rat ok", "rat hai long", "rat ung y", "ung y", "tuyet voi",
    }
    generic_praise_terms = (
        "tot", "ok", "dep", "hai long", "ung y", "ngon", "tien loi", "nen mua",
        "sai on", "dung on", "chat luong", "phai chang", "phu hop gia", "mau ma dep",
        "tuyet voi", "dang mua",
    )
    user_damage_terms = ("danh roi", "tu lam roi", "lam roi", "tu lam vo", "lam vo")
    injection_terms = (
        "ignore all previous", "ignore previous", "bo qua cac quy tac", "bo qua quy tac",
    )
    outside_terms = (
        "giao hang", "giao nhanh", "giao cham", "giao dung hen", "nhan hang",
        "nhan duoc hang", "ship", "shipper", "dong goi", "bao bi", "tui boc", "hoa don",
        "van chuyen", "nhan vien", "vo hop",
        "khuyen mai", "gia ban", "gia le", "gia bien dong", "chenh lech gia",
        "mua 1 tang 1", "tang len", "tang gia", "giam gia",
        "han bao hanh", "le bao hanh", "thieu phu kien", "khong kem", "trong hop chi co",
    )
    courtesy_terms = ("cam on shop", "cam on", "thanks shop", "thank shop", "tks shop", "yeu shop")
    incentive_terms = ("nhan xu", "tang xu", "hoan xu", "nhan diem", "tang diem", "duoc xu")
    not_used_terms = (
        "chua dung", "chua su dung", "chua test", "chua mo hop",
        "chua trai nghiem", "chua xai", "chua dung thu",
    )
    question_nfc_terms = ("hỏi",)
    question_terms = (
        "thu cu doi moi", "chinh sach", "huong dan", "cach su dung", "cai dat",
        "pass lai", "ban lai", "thu lai", "doi sang", "doi mau", "tra hang", "doi tra",
        "co ben khong", "co tot khong", "co nen mua", "mua duoc khong",
    )
    inquiry_preamble_terms = ("thac mac", "cho minh hoi", "cho em hoi", "shop cho hoi", "xin hoi")
    # Diacritic-sensitive words where stripping accents causes collisions (rè/rẻ, yếu/yêu, cháy/chạy, phồng/phòng, nứt/nút, êm/em)
    product_nfc_terms = (
        "hỏng", "lỗi", "lổi", "rè", "xoẹt", "phồng", "nứt", "rò", "nóng", "rỉ", "gỉ",
        "kẹt", "bung", "trầy", "xước", "lỏng", "cháy", "khét", "yếu", "ngừng", "ngắt",
        "êm", "mượt", "mỏi tay",
    )
    # Unambiguous multi-word product performance / defect / experience phrases (accent-insensitive)
    product_plain_terms = (
        "am thanh", "chat am", "am luong", "chat lieu", "mui nhua", "mui khet",
        "toa nhiet", "bong son", "ri set", "ro dien", "ro nuoc", "tray xuoc",
        "mat tieng", "khong hoat dong", "khong su dung duoc", "khong ket noi",
        "mat ket noi", "khong nhan", "khong len nguon", "khong sac duoc", "sac khong vao", "khong vao pin",
        "sac cham", "sac qua cham", "sac lau", "sac rat lau", "sac vao lau",
        "sac vao rat lau", "sac day", "sac cho", "cam sac", "len vach", "vach pin",
        "muc pin", "tut pin", "het pin", "pin dung", "pin lau", "pin yeu", "pin ao",
        "dung luong", "tu tat", "chap chon", "khong khit", "de roi", "lot am", "leak",
        "de su dung", "it hao dien", "nuong nhanh", "chien nhanh", "ket noi on dinh",
        "khong nong", "van mat", "chat hon", "vua chan", "size",
        "giu nhiet", "luc phun", "phun giot", "khong thang", "lech mau",
        "khac voi mau", "khac hinh", "sai mau", "khac mo ta", "khong giong mo ta",
        "khong duoc nhu ky vong", "khong giong hinh",
    )

    def has_product_signal(lower_nfc: str, plain: str) -> bool:
        return _has_nfc_term(lower_nfc, product_nfc_terms) or _has_plain_term(plain, product_plain_terms)

    def has_substantive_product_remainder(raw_comment: str) -> bool:
        """Return True if stripping shipping/packaging/price/courtesy clauses still leaves product commentary."""
        kept_clauses = []
        raw_clauses = re.split(r"[.!?;,\n]+|\b(?:nhưng\s+mà|nhưng|tuy\s+nhiên|chỉ\s+tiếc)\b", raw_comment, flags=re.IGNORECASE)
        for clause in raw_clauses:
            c_plain = _normalize_plain(clause)
            c_nfc = _normalize_nfc(clause)
            if not c_plain or c_plain in exact_praise:
                continue
            if _has_plain_term(c_plain, outside_terms) or _has_plain_term(c_plain, incentive_terms) or _has_plain_term(c_plain, courtesy_terms) or _has_plain_term(c_plain, inquiry_preamble_terms):
                continue
            if has_product_signal(c_nfc, c_plain):
                return True
            if len(c_plain.split()) <= 4 and _has_plain_term(c_plain, generic_praise_terms):
                continue
            kept_clauses.append(c_plain)
        remainder = " ".join(kept_clauses).strip()
        if not remainder:
            return False
        rem_words = remainder.split()
        if len(rem_words) >= 5 and not (len(rem_words) <= 10 and _has_plain_term(remainder, generic_praise_terms)):
            return True
        return False

    seen = set()
    kept, noise = [], []
    for item in reviews if isinstance(reviews, list) else []:
        if not isinstance(item, dict):
            continue
        comment = str(item.get("comment", item.get("text", "")) or "").strip()
        normalized = _normalize_plain(comment)
        lower_nfc = _normalize_nfc(comment)
        has_prod = has_product_signal(lower_nfc, normalized)
        words = normalized.split()
        label = ""

        if _is_empty_comment(normalized):
            label = "nhieu_trong"
        elif _has_plain_term(normalized, injection_terms):
            label = "nhieu_ngoai_chat_luong"
        elif _has_plain_term(normalized, user_damage_terms):
            label = "nhieu_ngoai_chat_luong"
        elif normalized in exact_praise:
            label = "nhieu_khen_chung"
        elif normalized in seen and len(normalized.replace(" ", "")) >= 8:
            label = "nhieu_lap_bat_thuong"
        elif _has_plain_term(normalized, incentive_terms) and not has_prod:
            label = "nhieu_nhan_xu"
        elif _has_plain_term(normalized, not_used_terms) and not has_prod:
            label = "nhieu_chua_dung"
        elif (_has_nfc_term(lower_nfc, question_nfc_terms) or _has_plain_term(normalized, question_terms)) and not has_prod:
            label = "nhieu_hoi_dap_rao_ban"
        elif _has_plain_term(normalized, outside_terms) and not has_prod and not has_substantive_product_remainder(comment):
            label = "nhieu_ngoai_chat_luong"
        elif len(normalized.replace(" ", "")) < 5 or (len(words) <= 2 and not has_prod):
            label = "nhieu_qua_ngan"
        elif not has_prod and len(words) <= 20 and _has_plain_term(normalized, generic_praise_terms):
            label = "nhieu_khen_chung"

        if normalized and not _is_empty_comment(normalized):
            seen.add(normalized)
        if label:
            labels[label] += 1
            noise.append(dict(item, noise_label=label))
        else:
            kept.append(dict(item))
    return {"kept": kept, "noise": noise, "noise_breakdown": labels}


@tool
def flag_review_anomalies(reviews: list) -> dict:
    """Đếm cụm review trùng để người mua kiểm tra thủ công.
    Input: danh sách review có review_id và comment.
    Output: cụm lặp chính xác, số review trùng dư, tỷ lệ và cờ định lượng; không gán nhãn gian lận.
    Tác động ngoài: không; chỉ tính trên review trong bộ nhớ."""
    groups = {}
    total = 0
    for index, item in enumerate(reviews if isinstance(reviews, list) else []):
        if not isinstance(item, dict):
            continue
        comment = str(item.get("comment", item.get("text", "")) or "").strip()
        normalized = _normalize_plain(comment)
        if _is_empty_comment(normalized) or len(normalized.replace(" ", "")) < 8:
            continue
        total += 1
        review_id = str(item.get("review_id") or item.get("id") or "R%02d" % (index + 1))
        groups.setdefault(normalized, []).append(review_id)

    clusters = [{"review_ids": ids, "count": len(ids)}
                for ids in groups.values() if len(ids) > 1]
    duplicate_count = sum(cluster["count"] - 1 for cluster in clusters)
    duplicate_rate = round(duplicate_count / total, 4) if total else 0.0
    flags = []
    if duplicate_count:
        flags.append({
            "type": "repeated_text",
            "duplicate_count": duplicate_count,
            "duplicate_rate": duplicate_rate,
            "clusters": clusters,
            "note": "Nội dung trùng cần kiểm tra; đây không phải bằng chứng seeding hay gian lận.",
        })
    if total >= 5 and duplicate_rate >= 0.2:
        flags.append({
            "type": "high_repeat_ratio",
            "duplicate_count": duplicate_count,
            "duplicate_rate": duplicate_rate,
            "note": "Tỷ lệ review trùng từ 20% trong mẫu; cần đối chiếu thủ công, không kết luận nguyên nhân.",
        })
    return {"review_count": total, "duplicate_count": duplicate_count,
            "duplicate_rate": duplicate_rate, "duplicate_clusters": clusters,
            "flags": flags}


@tool
def crawl_shopee_reviews(url: str, max_reviews: int = 100) -> dict:
    """Đọc review công khai qua adapter Apify của luồng CLI cũ.
    Input: URL sản phẩm Shopee.vn và số review tối đa.
    Output: metadata sản phẩm, review đã ẩn danh và thông tin độ phủ.
    Tác động ngoài: gửi yêu cầu đọc tới dịch vụ Apify; không sửa listing Shopee."""
    return fetch_product_reviews(url, max_reviews=max_reviews)
