"""Kiểm adapter UI gọi backend thật, chặn mạng bên ngoài trong mọi test."""
import json
import io
import os
import sys
import unittest
from unittest.mock import patch

os.environ["MODEL_PROVIDER"] = "fake"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "codebase"))
import agent
import ai
import tracing
from ui_backend import DEMO_URL, analyze_for_ui, prepare_reviews, public_error

URL = "https://shopee.vn/product/123/456"
REVIEWS = [{"rating_star": 2, "comment": "Tai trái mất kết nối sau một giờ.", "date": "2026-11-01", "variant": "Đen"},
           {"rating_star": 4, "comment": "Pin dùng đủ một buổi."}]


class UIBackendTests(unittest.TestCase):
    def test_fake_keeps_backend_insufficient_and_never_fabricates_risks(self):
        tracing.begin("fake-integration")
        with patch.object(agent, "crawl_shopee_reviews") as crawl:
            result = analyze_for_ui({"mode": "reviews", "url": URL, "reviews": REVIEWS})
            crawl.assert_not_called()
        usage, _ = tracing.end()
        self.assertEqual(result["analysis"]["status"], "insufficient")
        self.assertEqual(result["analysis"]["model"], "fake")
        self.assertFalse(result["analysis"]["risks"])
        self.assertFalse(result["sources"])
        self.assertEqual(usage["model_calls"], 1)
        self.assertEqual(usage["tokens_in"] + usage["tokens_out"], 0)

    def test_backend_citations_metadata_and_order_are_preserved(self):
        model_output = {"status": "risks", "summary": "Có phản ánh về kết nối.",
                        "risks": [{"title": "Mất kết nối", "summary": "Tai trái có phản ánh mất kết nối.",
                                   "severity": "medium", "citations": ["R01", "R99"]}]}
        with patch.object(agent, "call_model", return_value={"text": json.dumps(model_output), "model": "test-only-model"}):
            result = analyze_for_ui({"mode": "reviews", "url": URL, "reviews": REVIEWS})
        self.assertEqual(result["analysis"]["status"], "risks")
        self.assertEqual(result["analysis"]["risks"][0]["summary"], model_output["risks"][0]["summary"])
        self.assertEqual([r["id"] for r in result["sources"]], ["R01"])
        self.assertEqual(result["sources"][0]["text"], REVIEWS[0]["comment"])
        self.assertEqual(result["sources"][0]["rating"], 2)
        self.assertEqual(result["sources"][0]["variant"], "Đen")

    def test_no_clear_risk_status_comes_from_backend(self):
        with patch.object(agent, "call_model", return_value={"text": json.dumps({"status": "no_clear_risk", "summary": "Chưa có phản ánh rõ.", "risks": []}), "model": "test-only-model"}):
            result = analyze_for_ui({"mode": "reviews", "url": URL, "reviews": REVIEWS})
        self.assertEqual(result["analysis"]["status"], "no_clear_risk")
        self.assertNotIn("noise_pct", result["analysis"])

    def test_link_calls_backend_crawler_then_analysis(self):
        with patch.object(agent, "crawl_shopee_reviews", return_value={"reviews": REVIEWS, "coverage": {"counts_complete": False}}) as crawl:
            result = analyze_for_ui({"mode": "link", "url": URL})
            crawl.assert_called_once_with(URL)
        self.assertEqual(result["input_review_count"], 2)
        self.assertFalse(result["coverage"]["counts_complete"])

    def test_empty_comments_follow_backend_g10_without_model(self):
        with patch.object(agent, "call_model") as model:
            result = analyze_for_ui({"mode": "reviews", "url": URL, "reviews": [{"rating_star": 1, "comment": ""}]})
            model.assert_not_called()
        self.assertEqual(result["analysis"]["status"], "insufficient")
        self.assertEqual(result["analysis"]["review_count"], 0)

    def test_stars_are_required_and_never_invented(self):
        for rating in [None, True, 0, 6, "2"]:
            with self.assertRaises(ValueError):
                prepare_reviews([{"rating_star": rating, "comment": "Nội dung"}])

    def test_review_links_and_source_markers_stay_content_without_crawling(self):
        rows = [{"rating_star": 2, "comment": "[R01] Shipping nhanh https://example.com"},
                {"rating_star": 3, "comment": "Flagship https://shopee.vn/product/123/456"}]
        with patch.object(agent, "crawl_shopee_reviews") as crawl:
            result = analyze_for_ui({"mode": "reviews", "url": URL, "reviews": rows})
            crawl.assert_not_called()
        self.assertEqual(result["analysis"]["review_count"], 2)
        self.assertNotIn("review_flags", result["analysis"])
        self.assertEqual(prepare_reviews(rows)[0]["comment"], rows[0]["comment"])

    def test_personal_fields_are_not_forwarded_and_contacts_are_masked(self):
        result = prepare_reviews([{"rating_star": 2, "comment": "Liên hệ user@example.com, 0912345678", "username": "private-name", "variant": "user@example.com"}])[0]
        self.assertNotIn("username", result)
        self.assertNotIn("user@example.com", result["comment"])
        self.assertNotIn("0912345678", result["comment"])
        self.assertNotIn("user@example.com", result["variant"])

    def test_invalid_url_mode_limits_and_demo_crawl_are_rejected(self):
        for request in [{"mode": "link", "url": "https://other.example/product/1/2"},
                        {"mode": "link", "url": "https://shopee.vn/"},
                        {"mode": "link", "url": DEMO_URL}, {"mode": [], "url": URL},
                        {"mode": "reviews", "url": URL, "reviews": REVIEWS * 126}]:
            with self.assertRaises(ValueError):
                analyze_for_ui(request)

    def test_public_error_does_not_leak_provider_body(self):
        error = RuntimeError("OpenAI API trả HTTP 401: secret-test-token-response")
        self.assertNotIn("secret-test-token-response", public_error(error))
        self.assertIn("401", public_error(error))

    def test_openai_adapter_usage_with_stubbed_http_not_a_live_api_call(self):
        generated = {"status": "risks", "summary": "Fixture kiểm thử adapter.", "risks": [
            {"title": "Kết nối", "summary": "Có phản ánh kết nối.", "citations": ["R01"], "severity": "medium"}]}
        response = {"choices": [{"message": {"content": json.dumps(generated)}}],
                    "usage": {"prompt_tokens": 17, "completion_tokens": 9}}
        tracing.begin("stubbed-api")
        with patch.multiple(ai, MODEL_PROVIDER="openai", MODEL_NAME="test-only-model", API_KEY="test-only-placeholder"):
            with patch("ai.urllib.request.urlopen", return_value=io.BytesIO(json.dumps(response).encode())) as http:
                result = analyze_for_ui({"mode": "reviews", "url": URL, "reviews": REVIEWS})
                http.assert_called_once()
        usage, _ = tracing.end()
        self.assertEqual(result["analysis"]["status"], "risks")
        self.assertEqual(usage["model_calls"], 1)
        self.assertEqual(usage["tokens_in"], 17)
        self.assertEqual(usage["tokens_out"], 9)


if __name__ == "__main__":
    unittest.main()
