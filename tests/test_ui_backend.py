"""Adapter UI theo hợp đồng main PR #20; không gọi mạng ngoài."""
import io
import json
import os
import sys
import unittest
from unittest.mock import patch

os.environ["MODEL_PROVIDER"] = "fake"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "codebase"))
import ai
import agent
import tools
import tracing
from ui_backend import analyze_for_ui, public_error

TEXT = "[R01] Tai trái mất kết nối khi dùng ngoài đường.\n[R02] Pin nhanh hết sau một giờ nghe nhạc.\n[R03] Đeo lâu bị đau tai."
PAYLOAD = {"product": {"url": "https://shopee.vn/product/123/456", "name": "Tai nghe"},
           "reviews": [{"rating_star": 2, "comment": "Tai trái mất kết nối khi dùng ngoài đường."}]}


class UIBackendTests(unittest.TestCase):
    def test_catalog_calls_answer_once_without_crawling(self):
        with patch.object(agent, "answer", wraps=agent.answer) as answer, patch.object(tools, "crawl_shopee_reviews") as crawl:
            result = analyze_for_ui({"mode": "catalog", "product_id": "SP01"})
        answer.assert_called_once_with("SP01")
        crawl.assert_not_called()
        self.assertEqual(result["analysis"]["stats"]["total"], 20)
        self.assertEqual(len(result["sources"]), 20)
        self.assertEqual(result["analysis"]["status"], "insufficient")

    def test_raw_reviews_need_no_url_or_stars_and_preserve_backend_schema(self):
        with patch.object(agent, "answer", wraps=agent.answer) as answer:
            result = analyze_for_ui({"mode": "reviews", "text": TEXT})
        answer.assert_called_once_with(TEXT)
        a = result["analysis"]
        self.assertIsInstance(a["flags"], list)
        self.assertTrue(all(isinstance(flag, str) for flag in a["flags"]))
        self.assertIsInstance(a["anomalies"], dict)
        self.assertIn("pii_redacted_review_count", a["stats"])
        for key in ("min_clean_reviews", "input_total", "excluded_limit"):
            self.assertNotIn(key, a["stats"])

    def test_fake_never_generates_ui_risks_and_usage_is_traced(self):
        tracing.begin("ui-fake")
        result = analyze_for_ui({"mode": "reviews", "text": TEXT})
        usage, _ = tracing.end()
        self.assertEqual(result["analysis"]["status"], "insufficient")
        self.assertEqual(result["analysis"]["risks"], [])
        self.assertTrue(result["mock"])
        self.assertEqual(usage["models"], ["fake"])
        self.assertEqual((usage["model_calls"], usage["tool_calls"]), (1, 3))
        self.assertEqual((usage["tokens_in"], usage["tokens_out"]), (0, 0))

    def test_no_clean_reviews_stops_without_model(self):
        with patch.object(agent, "call_model") as model:
            result = analyze_for_ui({"mode": "reviews", "text": "[R01] Chưa dùng thử.\n[R02] Đánh giá để nhận xu."})
        model.assert_not_called()
        self.assertEqual(result["analysis"]["status"], "insufficient")
        self.assertEqual(result["analysis"]["stats"]["kept_clean"], 0)

    def test_one_clean_review_follows_main_not_an_extra_ui_threshold(self):
        with patch.object(agent, "call_model", wraps=agent.call_model) as model:
            result = analyze_for_ui({"mode": "reviews", "text": "[R01] Pin nhanh hết sau một giờ sử dụng."})
        model.assert_called_once()
        self.assertEqual(result["analysis"]["stats"]["kept_clean"], 1)

    def test_risks_and_quotes_come_from_backend_and_invalid_citation_is_removed(self):
        generated = {"status": "risks", "summary": "Có phản ánh đơn lẻ.", "risks": [
            {"title": "Kết nối", "summary": "Một review phản ánh mất kết nối.", "citations": ["R01", "R99"]}]}
        with patch.object(agent, "call_model", return_value={"text": json.dumps(generated), "model": "test-only"}):
            result = analyze_for_ui({"mode": "reviews", "text": TEXT})
        risk = result["analysis"]["risks"][0]
        self.assertEqual([source["id"] for source in risk["citations"]], ["R01"])
        self.assertEqual(risk["citations"][0]["text"], result["analysis"]["reviews_by_id"]["R01"])
        self.assertEqual(result["sources"][0]["text"], risk["citations"][0]["text"])

    def test_duplicate_clusters_and_sources_are_preserved(self):
        text = TEXT + "\n[R04] Tai trái mất kết nối khi dùng ngoài đường."
        a = analyze_for_ui({"mode": "reviews", "text": text})["analysis"]
        self.assertEqual(a["anomalies"]["duplicate_count"], 1)
        self.assertEqual(a["anomalies"]["duplicate_clusters"][0]["review_ids"], ["R01", "R04"])
        self.assertTrue(a["flags"])

    def test_pii_is_masked_in_sources_by_main(self):
        a = analyze_for_ui({"mode": "reviews", "text": "[R01] Pin yếu sau khi sạc, liên hệ user@example.com 0912345678."})["analysis"]
        self.assertNotIn("user@example.com", a["reviews_by_id"]["R01"])
        self.assertNotIn("0912345678", a["reviews_by_id"]["R01"])
        self.assertEqual(a["stats"]["pii_redacted_review_count"], 1)

    def test_payload_calls_main_payload_entry_once(self):
        with patch.object(agent, "analyze_review_payload", wraps=agent.analyze_review_payload) as payload, patch.object(agent, "answer") as answer:
            result = analyze_for_ui({"mode": "payload", "payload": PAYLOAD})
        payload.assert_called_once_with(PAYLOAD)
        answer.assert_not_called()
        self.assertEqual(result["analysis"]["stats"]["total"], 1)

    def test_dynamic_ai_provider_is_read_through_module(self):
        with patch.object(ai, "MODEL_PROVIDER", "openai"), patch.object(agent, "call_model", return_value={
            "text": '{"status":"no_clear_risk","summary":"Chưa thấy rủi ro.","risks":[]}', "model": "test-only"}):
            result = analyze_for_ui({"mode": "reviews", "text": TEXT})
        self.assertFalse(result["mock"])
        self.assertEqual(result["analysis"]["status"], "no_clear_risk")

    def test_invalid_inputs_are_rejected_and_bare_link_returns_backend_hint(self):
        for request in ([], {"mode": []}, {"mode": "catalog", "product_id": "SP99"},
                        {"mode": "reviews", "text": ""}, {"mode": "reviews", "text": "a" * 3001},
                        {"mode": "payload", "payload": []}):
            with self.subTest(request=str(request)[:60]), self.assertRaises(ValueError):
                analyze_for_ui(request)
        result = analyze_for_ui({"mode": "reviews", "text": "https://shopee.vn/product/123/456"})
        self.assertEqual(result["analysis"]["status"], "invalid_input")
        self.assertIn("crawl", result["analysis"]["summary"])

    def test_provider_error_body_is_hidden(self):
        self.assertNotIn("secret", public_error(RuntimeError("OpenAI HTTP 401 secret")))
        self.assertIn("401", public_error(RuntimeError("OpenAI HTTP 401 secret")))

    def test_openai_usage_from_http_stub_without_live_call(self):
        generated = {"status": "no_clear_risk", "summary": "Fixture", "risks": []}
        reply = {"choices": [{"message": {"content": json.dumps(generated)}}],
                 "usage": {"prompt_tokens": 17, "completion_tokens": 9}}
        tracing.begin("stub-only")
        with patch.multiple(ai, MODEL_PROVIDER="openai", MODEL_NAME="test-only", API_KEY="test-only"), patch("ai.urllib.request.urlopen", return_value=io.BytesIO(json.dumps(reply).encode())):
            result = analyze_for_ui({"mode": "reviews", "text": TEXT})
        usage, _ = tracing.end()
        self.assertFalse(result["mock"])
        self.assertEqual((usage["tokens_in"], usage["tokens_out"], usage["model_calls"]), (17, 9, 1))


if __name__ == "__main__":
    unittest.main()
