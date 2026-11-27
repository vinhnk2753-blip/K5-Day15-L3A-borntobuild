"""Local, read-only tools for the CP2 review-risk prototype."""
import json
import os
import re
import unicodedata
from pathlib import Path

from tracing import tool, TOOLS  # noqa: F401
from shopee_reviews import fetch_product_reviews

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
_RATING = re.compile(r"(?<!\d)([1-5])\s*(?:sao|\*|★)(?!\w)", re.IGNORECASE)
_REVIEW_ID = re.compile(r"^\s*\[?(R\d{1,3})\]?\s*(?:\||:|-)\s*(.*)$", re.IGNORECASE)
_INLINE_REVIEW_ID = re.compile(r"\[?(R\d{1,3})\]?\s*\|", re.IGNORECASE)


def _plain(value):
    value = unicodedata.normalize("NFD", str(value or "").lower())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return value.replace("đ", "d")


@tool
def load_product_reviews(query: str) -> dict:
    """Đọc bộ review sản phẩm mẫu CP2 theo mã, ID hoặc tên.
    Input: mã SP01–SP03, product_id hoặc một phần tên trong catalog.
    Output: metadata sản phẩm và review đã chuẩn hóa, giữ mã nguồn [Rxx].
    Tác động ngoài: không; chỉ đọc file JSON cục bộ đã ẩn danh."""
    if not isinstance(query, str) or not query.strip():
        return {"ok": False, "error": "Hãy nhập mã SP01–SP03 hoặc tên sản phẩm trong catalog."}
    catalog_path = DATA_DIR / "catalog.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": "Không đọc được catalog.json: %s" % type(exc).__name__}

    needle = _plain(query.strip())
    products = catalog.get("products", [])
    exact = [p for p in products if needle in {
        _plain(p.get("product_code")), _plain(p.get("product_id")), _plain(p.get("product_name"))
    }]
    matches = exact or [p for p in products if needle and (
        needle in _plain(p.get("product_name")) or _plain(p.get("product_name")) in needle
        or needle in _plain(p.get("product_id")) or _plain(p.get("product_id")) in needle
        or bool(re.search(r"\b%s\b" % re.escape(_plain(p.get("product_code"))), needle))
    )]
    if len(matches) != 1:
        return {"ok": False, "error": "Không tìm thấy duy nhất một sản phẩm trong catalog CP2."}

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
    """Chuẩn hóa review người dùng dán trực tiếp.
    Input: mỗi dòng một review; chấp nhận dạng [R01] | 5 sao | nội dung hoặc dòng văn bản.
    Output: danh sách review có mã [Rxx], sao nếu nhận diện được, và nội dung nguyên văn.
    Tác động ngoài: không; chỉ xử lý văn bản đầu vào trong bộ nhớ."""
    if not isinstance(text, str):
        return {"reviews": []}
    reviews = []
    used = set()
    next_id = 1
    for raw_line in text.splitlines():
        line = raw_line.strip().lstrip("-• ").strip()
        if not line:
            continue
        if _plain(line).startswith(("san pham:", "nguoi dung:")):
            continue

        inline_ids = list(_INLINE_REVIEW_ID.finditer(line))
        if inline_ids:
            for index, marker in enumerate(inline_ids):
                end = inline_ids[index + 1].start() if index + 1 < len(inline_ids) else len(line)
                body = line[marker.end():end].strip()
                match = _RATING.search(body)
                rating = int(match.group(1)) if match else None
                comment = body[match.end():].strip(" |:-") if match else body
                review_id = marker.group(1).upper()
                if review_id in used:
                    while "R%02d" % next_id in used:
                        next_id += 1
                    review_id = "R%02d" % next_id
                    next_id += 1
                used.add(review_id)
                reviews.append({"review_id": review_id, "rating_star": rating,
                                "comment": comment.strip(), "date": "", "variant": ""})
            continue

        explicit = _REVIEW_ID.match(line)
        review_id = explicit.group(1).upper() if explicit else ""
        body = explicit.group(2).strip() if explicit else line
        parts = [part.strip() for part in body.split("|")]
        rating = None
        comment_parts = []
        for index, part in enumerate(parts):
            match = _RATING.search(part)
            if match:
                rating = int(match.group(1))
                comment_parts = parts[index + 1:]
                break
        if rating is None:
            match = _RATING.search(body)
            if match:
                rating = int(match.group(1))
                comment = (body[:match.start()] + body[match.end():]).strip(" |:-")
            else:
                comment = body
        else:
            comment = " | ".join(comment_parts).strip() or parts[-1]
        if not review_id or review_id in used:
            while "R%02d" % next_id in used:
                next_id += 1
            review_id = "R%02d" % next_id
            next_id += 1
        used.add(review_id)
        reviews.append({"review_id": review_id, "rating_star": rating,
                        "comment": comment.strip(), "date": "", "variant": ""})
    return {"reviews": reviews}


@tool
def filter_review_noise(reviews: list) -> dict:
    """Lọc review trống, ngắn, khen ship, nhận xu, chưa dùng, hỏi đáp và lặp.
    Input: danh sách review chuẩn hóa có review_id và comment.
    Output: danh sách sạch, danh sách nhiễu, nhãn lý do và tổng từng nhóm.
    Tác động ngoài: không; quy tắc xác định, không sửa dữ liệu nguồn."""
    labels = {"nhieu_trong": 0, "nhieu_khen_chung": 0, "nhieu_hoi_dap_rao_ban": 0,
              "nhieu_ngoai_chat_luong": 0, "nhieu_lap_bat_thuong": 0,
              "nhieu_nhan_xu": 0, "nhieu_chua_dung": 0, "nhieu_qua_ngan": 0}
    praise = {"tot", "ok", "dep", "hai long", "san pham tot", "sai on", "rat ok",
              "hang tot", "mau dep", "dung tot", "ok nha", "rất tốt"}
    outside = ("giao hang", "giao nhanh", "giao dung hen", "nhan hang", "nhan duoc hang",
               "ship", "shipper", "dong goi", "van chuyen", "nhan vien",
               "khuyen mai", "gia ban", "han bao hanh", "le bao hanh", "thieu phu kien", "danh roi")
    incentive_terms = ("nhan xu", "tang xu", "hoan xu", "nhan diem", "tang diem", "duoc xu")
    not_used_terms = ("chua dung", "chua su dung", "chua thu", "chua test", "chua mo hop",
                      "chua trai nghiem", "chua xai")
    product_terms = ("hong", "loi", "nong", "pin", "sac", "am thanh", "chat lieu", "chay", "ri set",
                     "ro dien", "ro nuoc", "bung", "phong", "tray xuoc", "mat tieng", "khong hoat dong",
                     "cham", "yeu", "khong ket noi", "khong len nguon", "re", "nut", "tu tat")
    question_terms = ("hoi", "thu cu doi moi", "chinh sach", "huong dan", "cach su dung", "cai dat",
                      "pass lai", "ban lai", "thu lai", "doi sang", "doi mau", "tra hang", "doi tra")

    def has_term(normalized, terms):
        return any(re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(term), normalized) for term in terms)
    seen = set()
    kept, noise = [], []
    for item in reviews if isinstance(reviews, list) else []:
        if not isinstance(item, dict):
            continue
        comment = str(item.get("comment", "") or "").strip()
        normalized = re.sub(r"[^a-z0-9 ]+", " ", _plain(comment))
        normalized = " ".join(normalized.split())
        label = ""
        if not normalized or normalized in {"khong co binh luan", "khong binh luan", "chua co binh luan", "khong nhan xet"}:
            label = "nhieu_trong"
        elif normalized in seen:
            label = "nhieu_lap_bat_thuong"
        elif has_term(normalized, incentive_terms) and not has_term(normalized, product_terms):
            label = "nhieu_nhan_xu"
        elif has_term(normalized, not_used_terms) and not has_term(normalized, product_terms):
            label = "nhieu_chua_dung"
        elif normalized in praise:
            label = "nhieu_khen_chung"
        elif has_term(normalized, question_terms) and not has_term(normalized, product_terms):
            label = "nhieu_hoi_dap_rao_ban"
        elif has_term(normalized, outside) and not has_term(normalized, product_terms):
            label = "nhieu_ngoai_chat_luong"
        elif len(normalized.replace(" ", "")) < 5 or (len(normalized.split()) <= 2 and not has_term(normalized, product_terms)):
            label = "nhieu_qua_ngan"
        if normalized:
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
        normalized = re.sub(r"[^a-z0-9 ]+", " ", _plain(comment))
        normalized = " ".join(normalized.split())
        if len(normalized.replace(" ", "")) < 8:
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
