"""HTTP UI kiểm với backend hiện tại, không gọi dịch vụ ngoài."""
import json
import io
import http.client
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

os.environ["MODEL_PROVIDER"] = "fake"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "codebase"))
import agent
from app import create_server, main
from ui_backend import MAX_BODY_BYTES

URL = "https://shopee.vn/product/123/456"
ROWS = [{"rating_star": 2, "comment": "Tai trái mất kết nối."}]


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(0)
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()
        cls.base = "http://127.0.0.1:%d" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=5)

    def get(self, path):
        with urllib.request.urlopen(self.base + path, timeout=5) as response:
            return response.read().decode("utf-8")

    def post(self, payload, origin=None):
        headers = {"Content-Type": "application/json"}
        if origin:
            headers["Origin"] = origin
        req = urllib.request.Request(self.base + "/api/analyze", json.dumps(payload).encode("utf-8"), headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.load(response)

    def test_page_and_assets_without_external_dependencies(self):
        html = self.get("/")
        for marker in ['id="input-mode"', 'id="product-url"', 'id="source-dialog"', 'lang="vi"']:
            self.assertIn(marker, html)
        self.assertNotIn('src="https://', html)
        self.assertIn("data.analysis", self.get("/app.js"))
        self.assertIn("@media", self.get("/style.css"))

    def test_catalog_sample_follows_real_fake_backend(self):
        catalog = json.loads(self.get("/api/products"))
        self.assertTrue(catalog["synthetic"])
        self.assertNotIn("min_clean_reviews", catalog["limits"])
        sample = json.loads(self.get("/api/products/" + catalog["products"][0]["id"]))
        with patch.object(agent, "crawl_shopee_reviews") as crawl:
            response = self.post({"mode": "reviews", "url": sample["url"], "reviews": sample["reviews"]})
            crawl.assert_not_called()
        self.assertEqual(response["origin"], "backend")
        self.assertEqual(response["analysis"]["status"], "insufficient")
        self.assertEqual(response["analysis"]["model"], "fake")
        self.assertEqual(response["analysis"]["risks"], [])
        self.assertEqual(response["usage"]["model_calls"], 1)
        self.assertEqual(response["usage"]["tokens_in"], 0)
        self.assertNotIn("flagged_percent", response)

    def test_citation_from_backend_is_exposed_verbatim(self):
        content = {"status": "risks", "summary": "Có phản ánh kết nối.", "risks": [
            {"title": "Kết nối", "summary": "Có phản ánh tai trái.", "citations": ["R01"], "severity": "medium"}]}
        with patch.object(agent, "call_model", return_value={"text": json.dumps(content), "model": "test-only-model"}):
            response = self.post({"mode": "reviews", "url": URL, "reviews": ROWS})
        self.assertEqual(response["analysis"]["status"], "risks")
        self.assertEqual(response["sources"][0]["text"], ROWS[0]["comment"])
        self.assertEqual(response["sources"][0]["rating"], 2)

    def test_missing_crawler_configuration_is_clear_and_does_not_invent_results(self):
        with patch.object(agent, "crawl_shopee_reviews", side_effect=RuntimeError("Chưa cấu hình APIFY_TOKEN")):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.post({"mode": "link", "url": URL})
        self.assertEqual(error.exception.code, 502)
        body = json.load(error.exception)
        self.assertEqual(body["analysis"]["status"], "error")
        self.assertFalse(body["analysis"]["risks"])

    def test_errors_and_outside_platform_are_json_and_do_not_call_model(self):
        for payload, status in [({"mode": "reviews", "url": URL, "reviews": [{"comment": "Missing stars"}]}, "invalid_input"),
                                ({"mode": "link", "url": "https://other.example/product/1/2"}, "refused"),
                                ({"mode": "link", "url": "http://["}, "invalid_input")]:
            with patch.object(agent, "call_model") as model:
                with self.assertRaises(urllib.error.HTTPError) as error:
                    self.post(payload)
                model.assert_not_called()
            self.assertEqual(error.exception.code, 400)
            self.assertEqual(json.load(error.exception)["analysis"]["status"], status)

    def test_backend_empty_input_never_calls_model(self):
        response = self.post({"mode": "reviews", "url": URL, "reviews": []})
        self.assertEqual(response["analysis"]["status"], "insufficient")
        self.assertEqual(response["usage"]["model_calls"], 0)

    def test_arbitrary_path_and_cross_origin_are_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.get("/../.env")
        self.assertEqual(error.exception.code, 404)
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post({"mode": "reviews", "url": URL, "reviews": ROWS}, "https://other.example")
        self.assertEqual(error.exception.code, 403)

    def test_existing_ui_port_cannot_be_silently_shared(self):
        with self.assertRaises(OSError):
            create_server(self.server.server_port)

    def test_catalog_only_accepts_one_product_path_segment(self):
        for path in ["/api/products/", "/api/products/foo/bar/DEMO01", "/api/products/DEMO01/"]:
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as error:
                self.get(path)
            self.assertEqual(error.exception.code, 404)

    def test_empty_and_oversized_http_bodies_return_distinct_messages(self):
        # Máy chủ phải từ chối Content-Length sai ngay, trước khi đọc body.
        for length, expected in [(0, 400), (-1, 400), (MAX_BODY_BYTES + 1, 413)]:
            with self.subTest(length=length):
                connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
                try:
                    connection.request("POST", "/api/analyze", headers={"Content-Length": str(length)})
                    response = connection.getresponse()
                    self.assertEqual(response.status, expected)
                    self.assertTrue(json.load(response)["message"])
                finally:
                    connection.close()

    def test_server_logs_exception_type_without_provider_payload(self):
        with patch.object(agent, "analyze_reviews", side_effect=RuntimeError("secret-provider-payload")), patch("sys.stdout", new_callable=io.StringIO) as log:
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.post({"mode": "reviews", "url": URL, "reviews": ROWS})
            self.assertIn("exception=RuntimeError", log.getvalue())
            self.assertNotIn("secret-provider-payload", log.getvalue())
            self.assertNotIn("secret-provider-payload", error.exception.read().decode())

    def test_invalid_port_exits_cleanly(self):
        for port in ["-1", "65536", "invalid"]:
            with self.subTest(port=port), patch.dict(os.environ, {"REVIEW_LENS_MODE": "web", "REVIEW_LENS_PORT": port}), patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(main(), 1)


if __name__ == "__main__":
    unittest.main()
