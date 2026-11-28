"""Kiểm cấu hình issue #8 mà không gọi API hoặc ghi file kết quả mô phỏng.

Chạy: python cost/check_personas.py
      python cost/check_personas.py --require-live-config
Lệnh thứ hai chỉ kiểm đủ cấu hình, KHÔNG xác minh key/model bằng mạng.
"""
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cost"))
sys.path.insert(0, str(ROOT / "codebase"))

import simulate
from tools import load_product_reviews, filter_review_noise


def check():
    cfg, warnings = simulate.load_config()
    if warnings:
        raise ValueError("; ".join(warnings))
    if cfg["sessions"] < 50 or len(cfg["personas"]) < 3:
        raise ValueError("Cần >=50 phiên và >=3 persona.")
    if not math.isclose(cfg["total_share"], 1, abs_tol=1e-9):
        raise ValueError("Tổng share phải bằng 1.")
    if not 0 < cfg["users"]["low"] <= cfg["users"]["base"] <= cfg["users"]["high"]:
        raise ValueError("Quy mô phải dương và low <= base <= high.")
    if len({price["model"] for price in cfg["prices"]}) < 2:
        raise ValueError("Cần >=2 model khác nhau.")
    if not cfg["fx_rate"] or cfg["fx_rate"] <= 0 or not cfg["fx_source"]:
        raise ValueError("Cần tỷ giá dương và nguồn.")
    names, checked = set(), 0
    for persona in cfg["personas"]:
        if persona["name"] in names:
            raise ValueError("Tên persona bị lặp.")
        names.add(persona["name"])
        for field in ("share", "uses_per_month", "turns_per_session"):
            if not math.isfinite(persona[field]) or persona[field] <= 0:
                raise ValueError("%s.%s phải dương và hữu hạn." % (persona["name"], field))
        pool = simulate.input_pool(persona, [])
        for text in pool:
            loaded = load_product_reviews(text)
            if not loaded.get("ok"):
                raise ValueError("Input persona phải là mã catalog hợp lệ.")
            if not filter_review_noise(loaded["reviews"])["kept"]:
                raise ValueError("Input chưa đủ dữ liệu để đo token model ở bước chạy thật.")
            checked += 1
        print("OK persona %s: %d input hợp lệ." % (persona["name"], len(pool)))
    for count in (10, cfg["sessions"]):
        plan = simulate.plan_sessions(cfg, [], count)
        print("OK kế hoạch %d phiên / %d lượt; chỉ dựng kế hoạch, chưa chạy mô phỏng." %
              (len(plan), sum(len(inputs) for _, _, inputs in plan)))
    print("OK YAML: 0 cảnh báo, %d persona, %d input, share=1, >=2 đơn giá và tỷ giá có nguồn." % (len(names), checked))
    uses = sum(p["share"] * p["uses_per_month"] for p in cfg["personas"])
    turns = sum(p["share"] * p["uses_per_month"] * p["turns_per_session"] for p in cfg["personas"])
    if not math.isclose(uses, 3.9) or not math.isclose(turns, 8.3):
        raise ValueError("Persona chưa khớp dự toán spec.md §2: 3.9 phiên, 8.3 lượt/người/tháng.")
    print("OK khớp spec.md §2: 3.9 phiên, 8.3 lượt/người/tháng; quy mô 500/2000/5000.")
    if [cfg["users"][key] for key in ("low", "base", "high")] != [500, 2000, 5000]:
        raise ValueError("Quy mô chưa khớp spec.md §2.")
    print("Các tham số tải tự ước tính; catalog thật không phải kết quả API hay bằng chứng accuracy độc lập.")


def main():
    if sys.argv[1:] not in ([], ["--require-live-config"]):
        print("Dùng: python cost/check_personas.py [--require-live-config]")
        return 2
    try:
        check()
    except (ValueError, TypeError, KeyError) as exc:
        print("Cấu hình chưa đạt: %s" % exc)
        return 1
    if "--require-live-config" in sys.argv:
        import ai
        ready = ai.MODEL_PROVIDER == "openai" and bool(ai.MODEL_NAME) and bool(ai.API_KEY)
        print("Cấu hình AI thật: %s. Không in key và chưa gọi API để xác minh." % ("đủ trường bắt buộc" if ready else "chưa đủ MODEL_PROVIDER=openai, MODEL_NAME hoặc API_KEY"))
        return 0 if ready else 2
    print("Không gọi API/crawler, không tạo CSV hoặc trace lượt chạy.")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
