"""Script đếm bằng chứng đào data đợt 1 (CP2) — tái lập được 100% bằng thư viện chuẩn Python.

Cách chạy từ thư mục gốc repo:
    python3 evidence/count.py

Script đọc:
  - data/catalog.json và các file data/products/*.json (dữ liệu review sạch, đã ẩn danh)
  - evidence/cp2_labels.csv (bảng gán nhãn phân loại nhiễu / có thông tin SP)

Đầu ra:
  - Kiểm tra toàn vẹn: đủ 100% cặp (product_id, review_id) khớp nhau, không rò rỉ SĐT/email
  - Thống kê tổng hợp x/N (%) theo nhóm lớn, nhãn con và từng sản phẩm
"""
from collections import Counter, defaultdict
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT, "data", "catalog.json")
LABELS_PATH = os.path.join(ROOT, "evidence", "cp2_labels.csv")

VALID_SUBLABELS = {
    "nhieu": [
        "nhieu_trong",
        "nhieu_khen_chung",
        "nhieu_hoi_dap_rao_ban",
        "nhieu_ngoai_chat_luong",
    ],
    "co_thong_tin": [
        "co_thong_tin_rui_ro",
        "co_thong_tin_tich_cuc",
    ],
}

SUBLABEL_VI = {
    "nhieu_trong": "Review trống / không có văn bản",
    "nhieu_khen_chung": "Khen ngắn chung chung, không nêu chi tiết chất lượng",
    "nhieu_hoi_dap_rao_ban": "Hỏi đáp chính sách / hướng dẫn dùng / rao pass lại",
    "nhieu_ngoai_chat_luong": "Ngoài chất lượng kỹ thuật SP (giá/KM, NV, giao hàng, lệch ngày BH, tự làm rơi)",
    "co_thong_tin_rui_ro": "Có phản ánh rủi ro / lỗi thật của sản phẩm",
    "co_thong_tin_tich_cuc": "Có phản ánh tích cực chi tiết về sản phẩm",
}

PII_PATTERNS = [
    (re.compile(r"\b0\d{8,10}\b"), "số điện thoại"),
    (re.compile(r"\*{3,}\d{2,}"), "SĐT che dở"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email"),
]


def fmt(x: int, n: int) -> str:
    pct = (100.0 * x / n) if n else 0.0
    return f"{x}/{n} ({pct:.1f}%)"


def load_reviews():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)
    products = {}
    reviews_index = {}
    pii_hits = []
    for item in catalog["products"]:
        fpath = os.path.join(ROOT, item["file"])
        with open(fpath, encoding="utf-8") as pf:
            pdata = json.load(pf)
        pid = pdata["product_id"]
        products[pid] = pdata
        for rev in pdata["reviews"]:
            key = (pid, rev["id"])
            if key in reviews_index:
                sys.exit(f"Lỗi trùng mã review: {key}")
            reviews_index[key] = rev
            text = rev.get("text", "")
            for pat, kind in PII_PATTERNS:
                if pat.search(text):
                    pii_hits.append((pid, rev["id"], kind))
    return catalog, products, reviews_index, pii_hits


def load_labels():
    rows = []
    with open(LABELS_PATH, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def main() -> int:
    catalog, products, reviews_index, pii_hits = load_reviews()
    labels = load_labels()

    if pii_hits:
        sys.exit(f"CẢNH BÁO PII chưa ẩn danh: {pii_hits}")

    label_keys = {}
    for r in labels:
        key = (r["product_id"], r["review_id"])
        group = r["group"]
        sub = r["sub_label"]
        if group not in VALID_SUBLABELS or sub not in VALID_SUBLABELS[group]:
            sys.exit(f"Nhãn không hợp lệ tại {key}: group={group}, sub_label={sub}")
        if key in label_keys:
            sys.exit(f"Trùng nhãn tại {key}")
        label_keys[key] = r

    missing_labels = set(reviews_index) - set(label_keys)
    extra_labels = set(label_keys) - set(reviews_index)
    if missing_labels or extra_labels:
        sys.exit(f"Lệch dữ liệu và bảng nhãn! Thiếu: {missing_labels} · Thừa: {extra_labels}")

    # Kiểm tra đối chiếu quy tắc tự động với review trống
    for key, rev in reviews_index.items():
        is_empty = len(rev.get("text", "").strip()) == 0
        sub = label_keys[key]["sub_label"]
        if is_empty and sub != "nhieu_trong":
            sys.exit(f"Mâu thuẫn: {key} có text trống nhưng nhãn là {sub}")
        if (not is_empty) and sub == "nhieu_trong":
            sys.exit(f"Mâu thuẫn: {key} có text nhưng nhãn là nhieu_trong")

    n_total = len(labels)
    group_counts = Counter(r["group"] for r in labels)
    sub_counts = Counter(r["sub_label"] for r in labels)
    per_product = defaultdict(Counter)
    per_product_sub = defaultdict(Counter)
    for r in labels:
        per_product[r["product_id"]][r["group"]] += 1
        per_product_sub[r["product_id"]][r["sub_label"]] += 1

    print("=" * 72)
    print(f"KIỂM TRA TOÀN VẸN: OK ({len(products)} sản phẩm · N = {n_total} review · 0 lỗi PII)")
    print("=" * 72)
    print("\n1. TỔNG HỢP TOÀN TẬP (N = %d)" % n_total)
    print(f"- Tổng NHIỄU / không phản ánh chất lượng SP : {fmt(group_counts['nhieu'], n_total)}")
    print(f"- Tổng CÓ THÔNG TIN chất lượng SP           : {fmt(group_counts['co_thong_tin'], n_total)}")
    print("\n   Chi tiết theo nhãn con:")
    for group in ("nhieu", "co_thong_tin"):
        for sub in VALID_SUBLABELS[group]:
            print(f"   - {sub:24s}: {fmt(sub_counts[sub], n_total):14s} | {SUBLABEL_VI[sub]}")

    print("\n2. CHI TIẾT THEO TỪNG SẢN PHẨM")
    for item in catalog["products"]:
        pid = item["product_id"]
        pdata = products[pid]
        n_p = len(pdata["reviews"])
        n_noise = per_product[pid]["nhieu"]
        n_risk = per_product_sub[pid]["co_thong_tin_rui_ro"]
        n_pos = per_product_sub[pid]["co_thong_tin_tich_cuc"]
        n_empty = per_product_sub[pid]["nhieu_trong"]
        print(
            f"- {pdata['product_code']} | {pdata['product_name']} "
            f"(giá {pdata['price_vnd']:,}đ · hiển thị {pdata['displayed_rating']}/5, "
            f"{pdata['displayed_five_star_pct']}% 5★)"
        )
        print(
            f"    Nhiễu: {fmt(n_noise, n_p)} (trống: {n_empty}) · "
            f"Rủi ro/lỗi thật: {fmt(n_risk, n_p)} · "
            f"Tích cực chi tiết: {fmt(n_pos, n_p)}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
