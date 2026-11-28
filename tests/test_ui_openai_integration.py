"""Web -> answer -> adapter OpenAI -> tracing, HTTP nhà cung cấp được stub.

Không gọi mạng ngoài, không ghi token stub vào file mô phỏng/eval.
"""
import io
import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

os.environ["MODEL_PROVIDER"] = "fake"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "codebase"))
import ai
import app
import tools


class OpenAIWebIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.create_server(0)
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()
        cls.url = "http://127.0.0.1:%d/api/analyze" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=5)

    def post(self, rows, url=None):
        payload = ({"mode": "payload", "payload": {"url": url, "reviews": rows}} if url else
                   {"mode": "reviews", "text": "\n".join("[R%02d] %s sao | %s" %
                    (i + 1, row["rating_star"], row["comment"]) for i, row in enumerate(rows))})
        request = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        try:
            response = urllib.request.urlopen(request, timeout=5)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            return response.code, json.load(response)

    def test_four_input_types_through_openai_adapter_with_stub_usage(self):
        normal = [{"rating_star": 2, "comment": "Tai trái mất kết nối."},
                  {"rating_star": 2, "comment": "Pin nhanh hết."},
                  {"rating_star": 3, "comment": "Đeo lâu đau tai."}]
        noisy = normal + [{"rating_star": 5, "comment": "Chưa dùng thử."},
                          {"rating_star": 2, "comment": "Tai trái mất kết nối."},
                          {"rating_star": 5, "comment": "Đánh giá để nhận xu."}]
        generated = {"status": "risks", "summary": "Fixture kiểm tích hợp, không phải AI thật.",
                     "risks": [{"title": "Kết nối", "summary": "Fixture nguồn hợp lệ.",
                                "citations": ["R01", "R99"]}]}
        provider_reply = {"choices": [{"message": {"content": json.dumps(generated)}}],
                          "usage": {"prompt_tokens": 41, "completion_tokens": 17}}
        # urllib là module dùng chung: route request local tới opener thật,
        # chỉ chặn endpoint OpenAI bằng phản hồi stub, cấm mọi host khác.
        self.local_opener = urllib.request.build_opener()
        with patch.multiple(ai, MODEL_PROVIDER="openai", MODEL_NAME="test-only-openai", API_KEY="test-only-placeholder"), \
                patch.object(tools, "crawl_shopee_reviews") as crawl, \
                patch("ai.urllib.request.urlopen", side_effect=self.route(provider_reply)):
            for rows, expected in [(normal, (0, 3)), (noisy, (3, 3))]:
                code, data = self.post(rows)
                self.assertEqual(code, 200)
                self.assertFalse(data["mock"])
                self.assertEqual(data["analysis"]["status"], "risks")
                stats = data["analysis"]["stats"]
                self.assertEqual((stats["filtered_noise"], stats["kept_clean"]), expected)
                self.assertEqual(data["analysis"]["risks"][0]["citations"][0]["text"], normal[0]["comment"])
                self.assertNotIn("R99", [source["id"] for source in data["sources"]])
                self.assertEqual((data["usage"]["model_calls"], data["usage"]["tool_calls"]), (1, 3))
                self.assertEqual((data["usage"]["tokens_in"], data["usage"]["tokens_out"]), (41, 17))
            before = self.provider_calls
            code, data = self.post([noisy[3], noisy[5]])
            self.assertEqual((code, data["analysis"]["status"]), (200, "insufficient"))
            self.assertEqual(data["usage"]["model_calls"], 0)
            code, data = self.post(normal, "https://outside.example/product/1/1")
            self.assertEqual((code, data["analysis"]["status"]), (400, "refused"))
            self.assertEqual((data["usage"]["model_calls"], data["usage"]["tool_calls"]), (0, 0))
            self.assertEqual(self.provider_calls, before)
            crawl.assert_not_called()

    def route(self, reply):
        self.provider_calls = 0

        def open_request(request, **kwargs):
            if request.full_url == self.url:
                return self.local_opener.open(request, **kwargs)
            self.assertEqual(request.full_url, ai.OPENAI_URL)
            self.provider_calls += 1
            return io.BytesIO(json.dumps(reply).encode())

        return open_request

    def test_missing_api_key_is_a_safe_error_without_provider_network_call(self):
        rows = [{"rating_star": 2, "comment": text} for text in
                ("Pin nhanh hết.", "Tai trái mất kết nối.", "Đeo đau tai.")]
        with patch.multiple(ai, MODEL_PROVIDER="openai", MODEL_NAME="test-only-openai", API_KEY=""), \
                patch("ai.urllib.request.urlopen", side_effect=self.route({})):
            self.local_opener = urllib.request.build_opener()
            code, data = self.post(rows)
        self.assertEqual((code, data["analysis"]["status"]), (502, "error"))
        self.assertEqual(data["origin"], "runtime_error")
        self.assertNotIn("stats", data["analysis"])
        self.assertEqual(data["sources"], [])
        self.assertEqual(data["analysis"]["risks"], [])
        self.assertEqual((data["usage"]["tokens_in"], data["usage"]["tokens_out"]), (0, 0))
        self.assertEqual(self.provider_calls, 0)


if __name__ == "__main__":
    unittest.main()
