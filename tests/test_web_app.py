"""HTTP UI nối backend main PR #20; chỉ kiểm local, không gọi API thật."""
import http.client
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
import agent
from app import create_server, main
from ui_backend import MAX_BODY_BYTES


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
        if origin: headers["Origin"] = origin
        req = urllib.request.Request(self.base + "/api/analyze", json.dumps(payload).encode("utf-8"), headers)
        with urllib.request.urlopen(req, timeout=5) as response: return json.load(response)

    def test_page_assets_and_real_catalog(self):
        self.assertIn('id="reviews"', self.get("/"))
        self.assertNotIn('id="product-url"', self.get("/"))
        catalog = json.loads(self.get("/api/products"))
        self.assertEqual({p["id"] for p in catalog["products"] if not p["synthetic"]}, {"SP01", "SP02", "SP03"})
        self.assertIn("input[aria-invalid=true]", self.get("/style.css"))
        self.assertNotIn("min_clean_reviews", self.get("/app.js"))

    def test_real_catalog_code_goes_to_answer(self):
        with patch.object(agent, "answer", wraps=agent.answer) as answer:
            data = self.post({"mode": "catalog", "product_id": "SP02"})
        answer.assert_called_once_with("SP02")
        self.assertEqual(data["analysis"]["stats"]["total"], 20)
        self.assertEqual(data["analysis"]["status"], "insufficient")
        self.assertEqual(data["usage"]["models"], ["fake"])

    def test_all_demo_inputs_and_demo03_has_three_reviews(self):
        for code, count in (("DEMO01", 4), ("DEMO02", 2), ("DEMO03", 3)):
            fixture = json.loads(self.get("/api/products/" + code))
            self.assertTrue(fixture["synthetic"])
            self.assertEqual(len(fixture["text"].splitlines()), count)
            data = self.post({"mode": "reviews", "text": fixture["text"]})
            self.assertEqual(data["analysis"]["stats"]["total"], count)
            self.assertEqual(data["analysis"]["status"], "insufficient")
            self.assertEqual(data["analysis"]["risks"], [])
        self.assertGreater(data["analysis"]["stats"]["kept_clean"], 0)

    def test_module_provider_and_name_update_without_reimport(self):
        with patch.multiple(ai, MODEL_PROVIDER="openai", MODEL_NAME="changed-model"):
            cfg = json.loads(self.get("/api/products"))
        self.assertEqual((cfg["model_provider"], cfg["model_name"]), ("openai", "changed-model"))

    def test_payload_and_sources_with_no_url_required_for_text(self):
        data = self.post({"mode": "reviews", "text": "[R01] Pin nhanh hết sau một giờ dùng."})
        self.assertIn("R01", data["analysis"]["reviews_by_id"])
        payload = {"product": {"url": "https://shopee.vn/product/123/456"},
                   "reviews": [{"rating_star": 2, "comment": "Pin nhanh hết sau một giờ dùng."}]}
        data = self.post({"mode": "payload", "payload": payload})
        self.assertEqual(data["analysis"]["stats"]["total"], 1)
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post({"mode": "payload", "payload": {**payload, "url": "https://outside.example/product/1/1"}})
        self.assertEqual(json.load(error.exception)["analysis"]["status"], "refused")

    def test_invalid_routes_origin_and_schema(self):
        for path in ("/../.env", "/api/products/", "/api/products/foo/SP01", "/api/products/DEMO01/"):
            with self.assertRaises(urllib.error.HTTPError) as error: self.get(path)
            self.assertEqual(error.exception.code, 404)
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post({"mode": "catalog", "product_id": "SP01"}, "https://outside.example")
        self.assertEqual(error.exception.code, 403)
        with self.assertRaises(urllib.error.HTTPError) as error: self.post({"mode": "invalid"})
        self.assertEqual(error.exception.code, 400)

    def test_empty_and_oversized_http_headers(self):
        for length, code in ((0, 400), (-1, 400), (MAX_BODY_BYTES + 1, 413)):
            connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
            try:
                connection.request("POST", "/api/analyze", headers={"Content-Length": str(length)})
                response = connection.getresponse()
                self.assertEqual(response.status, code)
                self.assertTrue(json.load(response)["message"])
            finally: connection.close()

    def test_runtime_error_hides_sources_stats_and_secret(self):
        with patch.object(agent, "answer", side_effect=RuntimeError("secret-provider-body")), patch("sys.stdout", new_callable=io.StringIO) as log:
            with self.assertRaises(urllib.error.HTTPError) as error: self.post({"mode": "catalog", "product_id": "SP01"})
            data = json.load(error.exception)
        self.assertEqual(data["analysis"]["status"], "error")
        self.assertNotIn("stats", data["analysis"])
        self.assertNotIn("secret-provider-body", json.dumps(data))
        self.assertIn("RuntimeError", log.getvalue())
        self.assertNotIn("secret-provider-body", log.getvalue())

    def test_busy_port_and_invalid_ports(self):
        with self.assertRaises(OSError): create_server(self.server.server_port)
        for port in ("-1", "65536", "invalid"):
            with patch.dict(os.environ, {"REVIEW_LENS_MODE": "web", "REVIEW_LENS_PORT": port}), patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(main(), 1)


if __name__ == "__main__":
    unittest.main()
