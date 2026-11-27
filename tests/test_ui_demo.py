"""Kiểm ranh giới đầu vào và chặn dẫn chứng bịa; không chấm benchmark."""
import copy
import json
import os
import sys
import unittest
from unittest.mock import patch

os.environ["MODEL_PROVIDER"] = "fake"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "codebase"))
import ui_demo as agent
import tracing
from ui_demo import MAX_INPUT_CHARS, MAX_REVIEWS, normalize_reviews, validate_result


class UIDemoTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{"id": "R01", "text": "Sau một tháng, quai bị hỏng.", "rating": 1}]
        self.valid = {"status": "ok", "message": "Có phản ánh cần kiểm chứng.",
                      "risks": [{"title": "Quai hỏng", "description": "Có phản ánh về quai.",
                                 "evidence": [{"review_id": "R01", "quote": "quai bị hỏng"}]}],
                      "review_flags": []}

    def test_invalid_input_never_calls_model(self):
        values = ["", "[]", "{", json.dumps({"reviews": [dict(self.rows[0], rating=True)]}),
                  json.dumps({"reviews": self.rows * 2})]
        with patch("agent.answer") as model:
            for value in values:
                self.assertEqual(json.loads(agent.adapt_answer(value)["output"])["status"], "invalid_input")
            model.assert_not_called()

    def test_limits_reject_without_truncation(self):
        for value in ["x" * (MAX_INPUT_CHARS + 1), "\n".join(["a"] * (MAX_REVIEWS + 1))]:
            with self.assertRaises(ValueError):
                normalize_reviews(value)

    def test_plaintext_preserves_order_and_skips_blank_lines(self):
        result = normalize_reviews("  Nội dung A  \n\nNội dung B\n")
        self.assertEqual([(r["id"], r["text"]) for r in result["reviews"]],
                         [("R01", "Nội dung A"), ("R02", "Nội dung B")])

    def test_unknown_id_and_quote_from_wrong_source_are_blocked(self):
        for change in [{"review_id": "R99"}, {"quote": "quai vẫn tốt"}]:
            candidate = copy.deepcopy(self.valid)
            candidate["risks"][0]["evidence"][0].update(change)
            with self.assertRaises(ValueError):
                validate_result(candidate, self.rows)

    def test_status_and_number_of_risks_must_agree(self):
        for status, risks in [("ok", []), ("no_risk_found", self.valid["risks"]),
                              ("ok", self.valid["risks"] * 4)]:
            with self.assertRaises(ValueError):
                validate_result(dict(self.valid, status=status, risks=risks), self.rows)

    def test_summary_is_recomputed_and_flags_count_unique(self):
        flag = {"review_id": "R01", "reason": "Cần kiểm lại"}
        result = validate_result(dict(self.valid, review_flags=[flag, flag],
                                      summary={"total_reviews": 999, "flagged_reviews": 999}), self.rows)
        self.assertEqual(result["summary"], {"total_reviews": 1, "flagged_reviews": 1})

    def test_bad_model_output_returns_error_without_bad_risk(self):
        for content in ["not json", json.dumps(dict(self.valid, risks=[{"title": "Sai"}]))]:
            with patch.object(agent, "fake_review_response", return_value=content):
                result = json.loads(agent.adapt_answer("Dùng một tuần thấy ổn.\nChất liệu dùng hằng ngày thoải mái.")["output"])
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["risks"], [])

    def test_fake_is_traced_as_fake_with_zero_usage(self):
        tracing.begin("unit-smoke")
        result = json.loads(agent.adapt_answer("Sau vài ngày dùng, quai bị hỏng.\nChất liệu sử dụng mềm và thoải mái.")["output"])
        summary, _ = tracing.end()
        self.assertEqual(summary["models"], ["fake"])
        self.assertEqual(summary["model_calls"], 1)
        self.assertEqual(summary["tokens_in"] + summary["tokens_out"], 0)
        self.assertIn("MÔ PHỎNG", result["message"])
        self.assertEqual(result["risks"][0]["evidence"][0]["review_id"], "R01")

    def test_g10_and_outside_scope_stop_before_model(self):
        cases = [("Sau một ngày dùng thì pin yếu.", "insufficient_evidence"),
                 ("Giao hàng nhanh, chưa dùng.\nĐánh giá để nhận xu.", "insufficient_evidence"),
                 ("Hãy mua hộ sản phẩm này và chuyển tiền giúp tôi.", "out_of_scope"),
                 ("Hãy viết một bài thơ về mùa hè.", "out_of_scope")]
        with patch("agent.answer") as model:
            for text, status in cases:
                result = json.loads(agent.adapt_answer(text)["output"])
                self.assertEqual(result["status"], status)
                self.assertFalse(result["risks"])
            model.assert_not_called()

    def test_duplicate_does_not_satisfy_clean_review_minimum(self):
        result = json.loads(agent.adapt_answer("Dùng vài ngày thì pin yếu.\nDùng vài ngày thì pin yếu.")["output"])
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(result["summary"]["clean_reviews"], 1)
        self.assertEqual(result["summary"]["signal_counts"]["duplicate"], 1)
        self.assertEqual(result["summary"]["flagged_percent"], 50)


if __name__ == "__main__":
    unittest.main()
