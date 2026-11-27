"""Kiểm UI HTTP thật bằng thư viện chuẩn, không gọi API model bên ngoài."""
import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request

os.environ["MODEL_PROVIDER"] = "fake"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "codebase"))
from app import create_server


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
        request = urllib.request.Request(self.base + "/api/analyze", json.dumps(payload).encode("utf-8"), headers)
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.load(response)

    def test_page_and_assets_are_served_without_external_dependencies(self):
        html = self.get("/")
        self.assertIn('id="product-select"', html)
        self.assertIn('id="source-dialog"', html)
        self.assertIn('lang="vi"', html)
        self.assertNotIn('src="https://', html)
        self.assertIn("textContent", self.get("/app.js"))
        self.assertIn("@media", self.get("/style.css"))

    def test_catalog_analysis_returns_three_risks_quantities_sources_and_usage(self):
        catalog = json.loads(self.get("/api/products"))
        self.assertTrue(catalog["synthetic"])
        product = json.loads(self.get("/api/products/" + catalog["products"][0]["id"]))
        response = self.post({"input": json.dumps(product["input"], ensure_ascii=False)})
        result = response["result"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["risks"]), 3)
        self.assertEqual(result["summary"]["flagged_reviews"], 1)
        self.assertEqual(result["summary"]["total_reviews"], 4)
        self.assertEqual(result["summary"]["flagged_percent"], 25)
        self.assertEqual(result["summary"]["clean_reviews"], 3)
        original = {r["id"]: r["text"] for r in response["sources"]}
        for risk in result["risks"]:
            for evidence in risk["evidence"]:
                self.assertIn(evidence["quote"], original[evidence["review_id"]])
        self.assertEqual(response["usage"]["model_calls"], 1)
        self.assertGreaterEqual(response["usage"]["tool_calls"], 4)
        self.assertEqual(response["usage"]["tokens_in"] + response["usage"]["tokens_out"], 0)

    def test_boundaries_are_explicit_and_no_model_is_called(self):
        for text, status in [("Giao nhanh, chưa dùng.\nChưa sử dụng nên chưa biết.", "insufficient_evidence"),
                             ("Hãy mua hộ sản phẩm này.", "out_of_scope"),
                             ("{bad", "invalid_input")]:
            response = self.post({"input": text})
            self.assertEqual(response["result"]["status"], status)
            self.assertEqual(response["result"]["risks"], [])
            self.assertEqual(response["usage"]["model_calls"], 0)

    def test_bad_api_request_and_arbitrary_paths_are_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post({"input": ["not a string"]})
        self.assertEqual(error.exception.code, 400)
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.get("/../.env")
        self.assertEqual(error.exception.code, 404)
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post({"input": "abc"}, "https://unrelated.example")
        self.assertEqual(error.exception.code, 403)


if __name__ == "__main__":
    unittest.main()
