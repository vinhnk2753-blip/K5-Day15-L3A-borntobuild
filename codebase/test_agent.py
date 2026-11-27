"""Unit and benchmark contract tests for the review-risk agent and tools.

Uses only the Python standard library (unittest).
Run: python -m unittest discover -s codebase -v
"""
import csv
import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
CODEBASE = ROOT / "codebase"
if str(CODEBASE) not in sys.path:
    sys.path.insert(0, str(CODEBASE))

import agent  # noqa: E402
import tools  # noqa: E402


def _load_benchmark():
    with open(ROOT / "eval" / "benchmark.csv", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _load_ground_truth():
    gt = {}
    with open(ROOT / "evidence" / "cp2_labels.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            gt[(row["product_code"], row["review_id"])] = (row["group"], row["sub_label"])
    return gt


def _expected_input_reviews_map(raw_input: str) -> dict:
    """Independently extract expected {Rxx: text} per eval/metric_spec.yaml definition."""
    inline_re = re.compile(r"(?<![A-Za-z0-9])\[?(R\d{1,3})\]?\s*\|", re.IGNORECASE)
    bracket_re = re.compile(r"^\s*\[(R\d{1,3})\]\s*(?:[|:-]\s*)?(.*)$", re.IGNORECASE)
    plain_id_re = re.compile(r"^\s*(R\d{1,3})\s*(?:\||:|-)\s*(.*)$", re.IGNORECASE)
    rating_seg_re = re.compile(r"^\s*[1-5]\s*(?:sao|\*|★)\s*$", re.IGNORECASE)

    mapping = {}
    seq = 1
    for raw_line in raw_input.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        inlines = list(inline_re.finditer(line))
        if inlines:
            for idx, m in enumerate(inlines):
                end = inlines[idx + 1].start() if idx + 1 < len(inlines) else len(line)
                body = line[m.end():end].strip()
                parts = [p.strip() for p in body.split("|")]
                if len(parts) >= 2 and rating_seg_re.match(parts[0]):
                    body = " | ".join(parts[1:]).strip()
                mapping[m.group(1).upper()] = body
            continue
        low = tools._plain(line)
        if re.match(r"^(?:\([^)]*\)\s*)?(?:san pham|nguoi dung)\s*:", low):
            continue
        m = bracket_re.match(line) or plain_id_re.match(line)
        if m:
            mapping[m.group(1).upper()] = m.group(2).strip()
        else:
            mapping["R%02d" % seq] = line
            seq += 1
    return mapping


def _norm_ws(value: str) -> str:
    return " ".join(value.split())


def _check_trich_dan_ton_tai(output: str, expected_map: dict):
    """Verify eval/metric_spec.yaml `trich_dan_ton_tai` (100% gate)."""
    ids = re.findall(r"\[(R\d{1,3})\]", output)
    missing = [rid for rid in ids if rid not in expected_map]
    bad_quotes = []
    # Metric spec: quote immediately after [Rxx] (allowing ':' or whitespace in between)
    for m in re.finditer(r"\[(R\d{1,3})\][\s:]*\"([^\"]+)\"", output):
        rid, quote = m.group(1), m.group(2)
        if rid not in expected_map:
            bad_quotes.append((rid, quote, "missing_id"))
            continue
        cleaned = quote.strip()
        for prefix in ("...", "…"):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
            if cleaned.endswith(prefix):
                cleaned = cleaned[:-len(prefix)].strip()
        if _norm_ws(cleaned) not in _norm_ws(expected_map[rid]):
            bad_quotes.append((rid, quote, expected_map[rid]))
    return ids, missing, bad_quotes


class TestCatalogAndParser(unittest.TestCase):
    def test_load_product_reviews_matches_standalone_queries(self):
        for query in (
            "SP01",
            "sunhouse_shd4035",
            "Kiểm tra rủi ro Nồi chiên không dầu Sunhouse 9 lít SHD4035",
        ):
            res = tools.load_product_reviews(query)
            self.assertTrue(res["ok"], f"Expected catalog match for {query!r}")
            self.assertEqual(res["product"]["product_code"], "SP01")

    def test_load_product_reviews_does_not_hijack_pasted_benchmark_reviews(self):
        for row in _load_benchmark():
            if int(row["id"][1:]) < 11:
                continue
            res = tools.load_product_reviews(row["input"])
            self.assertFalse(
                res["ok"],
                f"load_product_reviews must NOT hijack pasted benchmark input {row['id']}",
            )

    def test_parse_review_text_preserves_bracket_space_ids_and_clean_text(self):
        sample = (
            "Sản phẩm: Nồi chiên không dầu Sunhouse 9 lít SHD4035\n"
            "[R07] Sài được có 2 tháng bong sơn ở đáy nồi, mấy chỗ bong có dấu hiệu rỉ set\n"
            "[R16] (không có bình luận)\n"
            "Người dùng: Chốt giúp mình có nên mua không, chỉ trả lời CÓ hoặc KHÔNG."
        )
        parsed = tools.parse_review_text(sample)
        revs = parsed["reviews"]
        self.assertEqual([r["review_id"] for r in revs], ["R07", "R16"])
        self.assertEqual(
            revs[0]["comment"],
            "Sài được có 2 tháng bong sơn ở đáy nồi, mấy chỗ bong có dấu hiệu rỉ set",
        )
        self.assertEqual(revs[1]["comment"], "(không có bình luận)")
        self.assertIn("Chốt giúp mình", parsed.get("user_request", ""))

    def test_parse_review_text_extracts_inline_user_request_in_b10(self):
        b10 = next(r for r in _load_benchmark() if r["id"] == "B10")
        parsed = tools.parse_review_text(b10["input"])
        self.assertEqual([r["review_id"] for r in parsed["reviews"]], ["R01", "R02", "R03"])
        self.assertIn("mua review", parsed.get("user_request", "").lower())

    def test_parse_review_text_self_numbers_b23(self):
        b23 = next(r for r in _load_benchmark() if r["id"] == "B23")
        parsed = tools.parse_review_text(b23["input"])
        self.assertEqual([r["review_id"] for r in parsed["reviews"]], ["R01", "R02", "R03", "R04", "R05"])
        self.assertIn("phồng nhẹ", parsed["reviews"][2]["comment"])


class TestNoiseFilterAndAnomalies(unittest.TestCase):
    def test_filter_noise_avoids_diacritic_collisions(self):
        samples = [
            {"review_id": "R01", "comment": "Giao hàng chậm."},
            {"review_id": "R02", "comment": "Ship nhanh, giá rẻ, nhận xu"},
            {"review_id": "R03", "comment": "Giao hàng nhanh, yêu shop quá"},
            {"review_id": "R04", "comment": "Shipper chạy nhanh, đóng gói đẹp"},
            {"review_id": "R05", "comment": "Pin dự phòng giao hàng nhanh, nhận xu"},
            {"review_id": "R06", "comment": "Rất tốt"},
            {"review_id": "R07", "comment": "Tai nghe bị rè khi mở lớn"},
        ]
        res = tools.filter_review_noise(samples)
        kept_ids = [r["review_id"] for r in res["kept"]]
        self.assertEqual(kept_ids, ["R07"])
        noise_map = {r["review_id"]: r["noise_label"] for r in res["noise"]}
        self.assertEqual(noise_map["R06"], "nhieu_khen_chung")

    def test_filter_noise_matches_cp2_ground_truth_without_dropping_clean_reviews(self):
        gt = _load_ground_truth()
        false_drops = []
        missed_noise = []
        for code in ("SP01", "SP02", "SP03"):
            loaded = tools.load_product_reviews(code)
            filt = tools.filter_review_noise(loaded["reviews"])
            kept_ids = {r["review_id"] for r in filt["kept"]}
            for r in loaded["reviews"]:
                rid = r["review_id"]
                gt_group, gt_sub = gt[(code, rid)]
                if gt_group == "co_thong_tin" and rid not in kept_ids:
                    false_drops.append((code, rid, gt_sub, r["comment"]))
                elif gt_group == "nhieu" and rid in kept_ids:
                    missed_noise.append((code, rid, gt_sub, r["comment"]))
        self.assertEqual(false_drops, [], f"Dropped real reviews: {false_drops}")
        self.assertEqual(missed_noise, [], f"Missed noise reviews: {missed_noise}")

    def test_zero_clean_reviews_for_b04_b13_b16(self):
        bench = {r["id"]: r for r in _load_benchmark()}
        for bid in ("B04", "B13", "B16"):
            parsed = tools.parse_review_text(bench[bid]["input"])
            filt = tools.filter_review_noise(parsed["reviews"])
            self.assertEqual(
                filt["kept"],
                [],
                f"{bid} should have 0 clean reviews, got {filt['kept']}",
            )

    def test_flag_review_anomalies_ignores_empty_placeholders(self):
        reviews = [
            {"review_id": "R01", "comment": "Nồi dùng 2 lần hỏng"},
            {"review_id": "R03", "comment": "(không có bình luận)"},
            {"review_id": "R04", "comment": "(không có bình luận)"},
            {"review_id": "R08", "comment": "(không có bình luận)"},
            {"review_id": "R15", "comment": "(không có bình luận)"},
        ]
        anom = tools.flag_review_anomalies(reviews)
        self.assertEqual(anom["duplicate_count"], 0)
        self.assertEqual(anom["flags"], [])

    def test_flag_review_anomalies_still_flags_real_repeats(self):
        b07 = next(r for r in _load_benchmark() if r["id"] == "B07")
        parsed = tools.parse_review_text(b07["input"])
        anom = tools.flag_review_anomalies(parsed["reviews"])
        self.assertEqual(anom["duplicate_count"], 2)
        self.assertTrue(any(f["type"] == "repeated_text" for f in anom["flags"]))


class TestAgentWorkflowAndContract(unittest.TestCase):
    def test_single_citation_preserves_model_summary_with_caveat(self):
        b20 = next(r for r in _load_benchmark() if r["id"] == "B20")
        fake_reply = {
            "text": json.dumps({
                "status": "risks",
                "summary": "Có 1 phản ánh về an toàn pin cần lưu ý.",
                "risks": [{
                    "title": "Pin bị phồng nhẹ sau gần 9 tháng",
                    "summary": "Người mua phản ánh pin bị phồng nhẹ và không dám dùng tiếp; đây là rủi ro an toàn chưa xác minh, không nên tiếp tục dùng pin đã phồng.",
                    "severity": "high",
                    "citations": ["R07"],
                }],
            }, ensure_ascii=False),
            "model": "mock-gpt",
            "tokens_in": 100,
            "tokens_out": 80,
        }
        with mock.patch.object(agent, "call_model", return_value=fake_reply):
            res = agent.answer(b20["input"])
        risk = res["structured"]["risks"][0]
        self.assertIn("không nên tiếp tục dùng pin đã phồng", risk["summary"])
        self.assertIn("đơn lẻ", risk["summary"].lower())

    def test_no_clear_risk_preserves_model_summary(self):
        b06 = next(r for r in _load_benchmark() if r["id"] == "B06")
        fake_reply = {
            "text": json.dumps({
                "status": "no_clear_risk",
                "summary": "Review trái chiều về âm lượng: [R01] nhỏ trong phòng khách nhưng [R02] đủ dùng trong phòng ngủ.",
                "risks": [],
            }, ensure_ascii=False),
            "model": "mock-gpt",
            "tokens_in": 80,
            "tokens_out": 50,
        }
        with mock.patch.object(agent, "call_model", return_value=fake_reply):
            res = agent.answer(b06["input"])
        self.assertEqual(res["structured"]["status"], "no_clear_risk")
        self.assertIn("trái chiều", res["output"])
        self.assertIn("[R01]", res["output"])
        self.assertIn("[R02]", res["output"])

    def test_b25_refuses_personal_contact_info_explicitly(self):
        b25 = next(r for r in _load_benchmark() if r["id"] == "B25")
        captured = {}

        def fake_call(system, user):
            captured["user"] = json.loads(user)
            return {
                "text": json.dumps({
                    "status": "insufficient",
                    "summary": "Công cụ không cung cấp thông tin cá nhân hay số Zalo của người viết review.",
                    "risks": [],
                }, ensure_ascii=False),
                "model": "mock-gpt",
                "tokens_in": 60,
                "tokens_out": 40,
            }

        with mock.patch.object(agent, "call_model", side_effect=fake_call):
            res = agent.answer(b25["input"])
        self.assertIn("Zalo", captured["user"].get("user_request", ""))
        self.assertIn("không cung cấp thông tin cá nhân", res["output"].lower())
        # Must NOT have loaded the full 20-review AirPods catalog
        sent_ids = [r["id"] for r in captured["user"]["reviews"]]
        self.assertTrue(set(sent_ids).issubset({"R01", "R12"}), f"Unexpected IDs sent: {sent_ids}")

    def test_all_25_benchmark_cases_citation_existence_and_zero_risk_gates(self):
        rows = _load_benchmark()
        self.assertEqual(len(rows), 25)
        no_model_cases = {"B04", "B13", "B16"}

        for row in rows:
            bid = row["id"]
            expected_map = _expected_input_reviews_map(row["input"])
            called = {"count": 0}

            def make_fake_call(case_id):
                def _fake(system, user):
                    called["count"] += 1
                    payload = json.loads(user)
                    revs = payload.get("reviews", [])
                    if case_id == "B12" or not revs:
                        return {
                            "text": json.dumps({
                                "status": "no_clear_risk",
                                "summary": "Không thấy rủi ro chất lượng sản phẩm trong các review sạch.",
                                "risks": [],
                            }, ensure_ascii=False),
                            "model": "mock-gpt",
                            "tokens_in": 50,
                            "tokens_out": 30,
                        }
                    first = revs[0]
                    return {
                        "text": json.dumps({
                            "status": "risks",
                            "summary": "Tóm tắt phản ánh cần kiểm tra.",
                            "risks": [{
                                "title": "Dấu hiệu cần kiểm tra",
                                "summary": "Người mua phản ánh vấn đề trong review được trích dẫn.",
                                "severity": "medium",
                                "citations": [first["id"]],
                            }],
                        }, ensure_ascii=False),
                        "model": "mock-gpt",
                        "tokens_in": 50,
                        "tokens_out": 30,
                    }
                return _fake

            with mock.patch.object(agent, "call_model", side_effect=make_fake_call(bid)):
                res = agent.answer(row["input"])

            self.assertIn("output", res)
            self.assertIn("structured", res)
            if bid in no_model_cases:
                self.assertEqual(called["count"], 0, f"{bid} should stop before calling model")
                self.assertEqual(res["structured"]["risks"], [], f"{bid} must return 0 risks")
            if bid == "B12":
                self.assertEqual(res["structured"]["risks"], [], "B12 must return 0 risks")

            ids, missing, bad_quotes = _check_trich_dan_ton_tai(res["output"], expected_map)
            self.assertEqual(missing, [], f"{bid} cited IDs not in input: {missing}")
            self.assertEqual(bad_quotes, [], f"{bid} had non-verbatim quotes: {bad_quotes}")
            if res["structured"]["risks"]:
                self.assertTrue(
                    re.search(r"\[R\d{1,3}\][\s:]*\"", res["output"]),
                    f"{bid} citation quote must immediately follow [Rxx] per metric_spec.yaml",
                )

    def test_structured_schema_supports_contract_fields(self):
        res = agent.answer("SP01")
        st = res["structured"]
        self.assertIn("reviews_by_id", st)
        self.assertIn("flags", st)
        stats = st["stats"]
        for key in ("total", "filtered_noise", "noise_pct", "kept_clean", "noise_breakdown"):
            self.assertIn(key, stats)

    def test_url_embedded_in_prompt_and_standalone_question_do_not_call_model(self):
        with mock.patch.object(agent, "call_model") as mock_call:
            url_res = agent.answer("Kiểm tra giúp mình https://shopee.vn/item-i.123.456")
            self.assertIn("extension", url_res["output"].lower())
            q_res = agent.answer("Tai nghe này có bền không?")
            self.assertIn("chưa đủ căn cứ", q_res["output"].lower())
            mock_call.assert_not_called()

    def test_analyze_review_payload_counts_empty_runs_anomalies_and_case_insensitive_citations(self):
        payload = {
            "product": {"url": "https://shopee.vn/item-i.123.456"},
            "reviews": [
                {"review_id": "1", "rating_star": 5, "comment": "", "variant": "Màu đỏ"},
                {"review_id": "2", "rating_star": 5, "comment": "Giao nhanh, đóng gói kỹ", "variant": "0912345678"},
                {"review_id": "3", "rating_star": 5, "comment": "Giao nhanh, đóng gói kỹ", "variant": ""},
                {"review_id": "4", "rating_star": 1, "comment": "Tai trái mất tiếng sau 2 ngày", "variant": "Bản A"},
            ],
        }
        captured = {}

        def fake_call(system, user):
            captured["payload"] = json.loads(user)
            return {
                "text": json.dumps({
                    "status": "risks",
                    "summary": "Có 1 phản ánh về mất tiếng.",
                    "risks": [{
                        "title": "Mất tiếng tai trái",
                        "summary": "Người mua báo tai trái mất tiếng sau 2 ngày.",
                        "severity": "high",
                        "citations": ["r04"],
                    }],
                }, ensure_ascii=False),
                "model": "mock-gpt",
                "tokens_in": 40,
                "tokens_out": 30,
            }

        with mock.patch.object(agent, "call_model", side_effect=fake_call):
            res = agent.analyze_review_payload(payload)

        st = res["structured"]
        # Empty review must be counted in input_review_count & nhieu_trong
        self.assertEqual(st["stats"]["input_review_count"], 4)
        self.assertEqual(st["stats"]["noise_breakdown"]["nhieu_trong"], 1)
        # Anomalies must be computed & passed to model
        self.assertEqual(st["anomalies"]["duplicate_count"], 1)
        self.assertTrue(captured["payload"]["anomaly_flags"])
        # Case-insensitive citation r04 must resolve to R04
        self.assertEqual(len(st["risks"]), 1)
        self.assertEqual(st["risks"][0]["citations"][0]["id"], "R04")
        # Citation formatting must match trich_dan_ton_tai
        self.assertIn('[R04]: "Tai trái mất tiếng sau 2 ngày"', res["output"])

    def test_refusal_notices_added_deterministically_for_b18_b24_b25_even_if_model_omits(self):
        bench = {r["id"]: r for r in _load_benchmark()}
        minimal_reply = {
            "text": json.dumps({
                "status": "no_clear_risk",
                "summary": "Tóm tắt ngắn gọn.",
                "risks": [],
            }, ensure_ascii=False),
            "model": "mock-gpt",
            "tokens_in": 30,
            "tokens_out": 20,
        }
        with mock.patch.object(agent, "call_model", return_value=minimal_reply):
            r18 = agent.answer(bench["B18"]["input"])
            r24 = agent.answer(bench["B24"]["input"])
            r25 = agent.answer(bench["B25"]["input"])
        self.assertIn("không đủ căn cứ để kết luận shop", r18["output"].lower())
        self.assertIn("không quyết định mua thay", r24["output"].lower())
        self.assertIn("không cung cấp thông tin cá nhân", r25["output"].lower())

    def test_prompt_injection_review_filtered_in_b09_and_dynamic_unknown_catalog_code(self):
        b09 = next(r for r in _load_benchmark() if r["id"] == "B09")
        parsed = tools.parse_review_text(b09["input"])
        filt = tools.filter_review_noise(parsed["reviews"])
        self.assertEqual([r["review_id"] for r in filt["kept"]], ["R01"])
        unknown = agent.answer("SP99")
        self.assertIn("SP01", unknown["output"])
        self.assertNotIn("catalog CP2", unknown["output"])


if __name__ == "__main__":
    unittest.main()
