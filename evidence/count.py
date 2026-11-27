"""Script đếm bằng chứng đào data CP2 + CP3 (N = 150) — tái lập được 100% bằng thư viện chuẩn Python.

Cách chạy từ thư mục gốc repo:
    python evidence/count.py

Script đọc:
  - data/catalog.json và các file data/products/*.json (dữ liệu review sạch, đã ẩn danh)
  - evidence/cp2_labels.csv (đợt 1 · CP2: SP01–SP03, 60 review ĐMX/TGDĐ — giữ nguyên chuẩn eval/test)
  - evidence/cp3_labels.csv (đợt 2 · CP3: SP04–SP06, 90 review Tiki)

Đầu ra:
  - Kiểm tra toàn vẹn: đủ 100% cặp (product_id, review_id) khớp nhau, không rò rỉ SĐT/email
  - Kiểm tra lặp nội dung tự động trên review có văn bản (≥8 ký tự)
  - Thống kê tổng hợp x/N (%) toàn tập (N = 150), tách theo đợt/sàn, từng sản phẩm và phân bố sao (Tiki)
"""
from collections import Counter, defaultdict
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT, "data", "catalog.json")
LABEL_FILES = [
    ("CP2 (ĐMX/TGDĐ)", os.path.join(ROOT, "evidence", "cp2_labels.csv")),
    ("CP3 (Tiki)", os.path.join(ROOT, "evidence", "cp3_labels.csv")),
]

VALID_SUBLABELS = {
    "nhieu": [
        "nhieu_trong",
        "nhieu_khen_chung",
        "nhieu_hoi_dap_rao_ban",
        "nhieu_ngoai_chat_luong",
        "nhieu_chua_dung",
        "nhieu_nhan_xu",
        "nhieu_lap_bat_thuong",
    ],
    "co_thong_tin": [
        "co_thong_tin_rui_ro",
        "co_thong_tin_tich_cuc",
    ],
}

SUBLABEL_VI = {
    "nhieu_trong": "Review trống / không có văn bản (chỉ bấm sao/ảnh)",
    "nhieu_khen_chung": "Khen ngắn chung chung, không nêu chi tiết chất lượng",
    "nhieu_hoi_dap_rao_ban": "Hỏi đáp chính sách / hướng dẫn dùng / rao pass lại",
    "nhieu_ngoai_chat_luong": "Ngoài chất lượng kỹ thuật SP (giao hàng/ship, giá/KM, sàn, NV, lệch BH, tự làm rơi)",
    "nhieu_chua_dung": "Mới nhận / chưa dùng để kiểm chứng chất lượng",
    "nhieu_nhan_xu": "Đánh giá đối phó nhận xu / nhận thưởng sàn",
    "nhieu_lap_bat_thuong": "Lặp nội dung bất thường trong cùng sản phẩm",
    "co_thong_tin_rui_ro": "Có phản ánh rủi ro / lỗi / hạn chế thật của sản phẩm",
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


def norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def load_reviews():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)
    products = {}
    reviews_index = {}
    pii_hits = []
    exact_dups = []
    for item in catalog["products"]:
        fpath = os.path.join(ROOT, item["file"])
        with open(fpath, encoding="utf-8") as pf:
            pdata = json.load(pf)
        pid = pdata["product_id"]
        products[pid] = pdata
        seen_texts = {}
        for rev in pdata["reviews"]:
            key = (pid, rev["id"])
            if key in reviews_index:
                sys.exit(f"Lỗi trùng mã review: {key}")
            reviews_index[key] = rev
            text = rev.get("text", "")
            for pat, kind in PII_PATTERNS:
                if pat.search(text):
                    pii_hits.append((pid, rev["id"], kind))
            nt = norm_text(text)
            if len(nt.replace(" ", "")) >= 8:
                if nt in seen_texts:
                    exact_dups.append((pid, seen_texts[nt], rev["id"], text))
                else:
                    seen_texts[nt] = rev["id"]
    return catalog, products, reviews_index, pii_hits, exact_dups


def load_labels():
    rows = []
    for wave_name, path in LABEL_FILES:
        if not os.path.exists(path):
            sys.exit(f"Không tìm thấy bảng nhãn: {path}")
        with open(path, encoding="utf-8", newline="") as f:
            for lineno, row in enumerate(csv.DictReader(f), start=2):
                if None in row or any(v is None for v in row.values()):
                    sys.exit(f"Lỗi định dạng CSV tại {path}:{lineno}: {row}")
                row["_wave"] = wave_name
                rows.append(row)
    return rows


def print_block(title: str, rows: list):
    n = len(rows)
    gc = Counter(r["group"] for r in rows)
    sc = Counter(r["sub_label"] for r in rows)
    print(f"\n{title} (N = {n})")
    print(f"- Tổng NHIỄU / không phản ánh chất lượng SP : {fmt(gc['nhieu'], n)}")
    print(f"- Tổng CÓ THÔNG TIN chất lượng SP           : {fmt(gc['co_thong_tin'], n)}")
    for group in ("nhieu", "co_thong_tin"):
        for sub in VALID_SUBLABELS[group]:
            if sc[sub] > 0 or title.startswith("1."):
                print(f"   - {sub:24s}: {fmt(sc[sub], n):15s} | {SUBLABEL_VI[sub]}")


def main() -> int:
    catalog, products, reviews_index, pii_hits, exact_dups = load_reviews()
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

    for key, rev in reviews_index.items():
        is_empty = len(rev.get("text", "").strip()) == 0
        sub = label_keys[key]["sub_label"]
        if is_empty and sub != "nhieu_trong":
            sys.exit(f"Mâu thuẫn: {key} có text trống nhưng nhãn là {sub}")
        if (not is_empty) and sub == "nhieu_trong":
            sys.exit(f"Mâu thuẫn: {key} có text nhưng nhãn là nhieu_trong")

    n_total = len(labels)
    per_product = defaultdict(Counter)
    per_product_sub = defaultdict(Counter)
    by_wave = defaultdict(list)
    for r in labels:
        per_product[r["product_id"]][r["group"]] += 1
        per_product_sub[r["product_id"]][r["sub_label"]] += 1
        by_wave[r["_wave"]].append(r)

    print("=" * 78)
    print(
        f"KIỂM TRA TOÀN VẸN: OK ({len(products)} sản phẩm · N = {n_total} review · "
        f"0 lỗi PII · {len(exact_dups)} cặp lặp nguyên văn ≥8 ký tự)"
    )
    print("=" * 78)

    print_block("1. TỔNG HỢP TOÀN TẬP (ĐỢT 1 + ĐỢT 2)", labels)

    print("\n2. SO SÁNH THEO ĐỢT / HỆ SINH THÁI SÀN")
    for wave_name, _ in LABEL_FILES:
        print_block(f"   [{wave_name}]", by_wave[wave_name])

    print("\n3. CHI TIẾT THEO TỪNG SẢN PHẨM")
    for item in catalog["products"]:
        pid = item["product_id"]
        pdata = products[pid]
        n_p = len(pdata["reviews"])
        n_noise = per_product[pid]["nhieu"]
        n_risk = per_product_sub[pid]["co_thong_tin_rui_ro"]
        n_pos = per_product_sub[pid]["co_thong_tin_tich_cuc"]
        n_empty = per_product_sub[pid]["nhieu_trong"]
        n_text = n_p - n_empty
        print(
            f"- {pdata['product_code']} | {pdata['product_name']} [{pdata['platform']}] "
            f"(giá {pdata['price_vnd']:,}đ · hiển thị {pdata['displayed_rating']}/5, "
            f"{pdata['displayed_five_star_pct']}% 5★)"
        )
        print(
            f"    Nhiễu: {fmt(n_noise, n_p)} (trống: {n_empty}, có chữ: {n_text}) · "
            f"Rủi ro/lỗi thật: {fmt(n_risk, n_p)} · "
            f"Tích cực chi tiết: {fmt(n_pos, n_p)}"
        )

    # 4. Phân bố sao trên tập có rating_star (Tiki SP04-SP06)
    rated_rows = [
        (r, reviews_index[(r["product_id"], r["review_id"])]["rating_star"])
        for r in labels
        if reviews_index[(r["product_id"], r["review_id"])].get("rating_star") is not None
    ]
    if rated_rows:
        print(f"\n4. PHÂN BỐ THEO SỐ SAO TỪNG REVIEW (Tiki SP04–SP06 · N = {len(rated_rows)})")
        high_star = [(r, s) for r, s in rated_rows if s >= 4]
        low_star = [(r, s) for r, s in rated_rows if s <= 3]
        all_risks = [(r, s) for r, s in rated_rows if r["sub_label"] == "co_thong_tin_rui_ro"]
        risks_in_high = [(r, s) for r, s in all_risks if s >= 4]
        noise_in_high = [(r, s) for r, s in high_star if r["group"] == "nhieu"]
        print(f"- Review 4–5★: {fmt(len(high_star), len(rated_rows))} · trong đó NHIỄU: {fmt(len(noise_in_high), len(high_star))}")
        print(f"- Review 1–3★: {fmt(len(low_star), len(rated_rows))}")
        print(f"- Rủi ro/hạn chế thật nằm trong review 4–5★ (bỏ sót nếu chỉ lọc 1–2★): {fmt(len(risks_in_high), len(all_risks))}")
        for r, s in all_risks:
            print(f"    • {r['product_code']} [{r['review_id']}] ({s}★): {r['reason']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
