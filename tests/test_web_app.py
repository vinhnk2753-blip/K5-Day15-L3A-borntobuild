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

    def get(self, path, origin=None):
        headers = {"Origin": origin} if origin else {}
        req = urllib.request.Request(self.base + path, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.read().decode("utf-8")

    def post(self, payload, origin=None, path="/api/analyze"):
        headers = {"Content-Type": "application/json"}
        if origin: headers["Origin"] = origin
        req = urllib.request.Request(self.base + path, json.dumps(payload).encode("utf-8"), headers)
        with urllib.request.urlopen(req, timeout=5) as response: return json.load(response)

    def raw_request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            raw = response.read().decode("utf-8")
            return response.status, dict(response.getheaders()), raw
        finally:
            connection.close()

    def test_page_assets_and_real_catalog(self):
        self.assertIn('id="reviews"', self.get("/"))
        self.assertNotIn('id="product-url"', self.get("/"))
        catalog = json.loads(self.get("/api/products"))
        self.assertTrue({"SP01", "SP02", "SP03", "SP04", "SP05", "SP06"}.issubset(
            {p["id"] for p in catalog["products"] if not p["synthetic"]}))
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

    PINNED_EXT_ID = "ioiaamibggpopefebobaeikfaabhnfln"
    PINNED_EXT_ORIGIN = "chrome-extension://" + PINNED_EXT_ID

    def test_extension_handoff_cors_and_origin_isolation(self):
        ext_origin = self.PINNED_EXT_ORIGIN
        status, headers, _ = self.raw_request(
            "OPTIONS",
            "/api/extension-handoff",
            headers={"Origin": ext_origin, "Access-Control-Request-Private-Network": "true"},
        )
        self.assertEqual(status, 204)
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), ext_origin)
        self.assertIn("POST", headers.get("Access-Control-Allow-Methods", ""))
        self.assertEqual(headers.get("Access-Control-Allow-Private-Network"), "true")

        # Reject web origins AND any Chrome extension ID not in allowlist.
        for bad_origin in (
            "https://evil.example",
            "chrome-extension://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "chrome-extension://abcdefghijklmnop",
            ext_origin + "/extra",
        ):
            status, headers, _ = self.raw_request(
                "OPTIONS",
                "/api/extension-handoff",
                headers={"Origin": bad_origin, "Access-Control-Request-Private-Network": "true"},
            )
            self.assertEqual(status, 403, f"Expected 403 for OPTIONS Origin={bad_origin}")
            self.assertNotIn("Access-Control-Allow-Origin", headers)
            self.assertNotIn("Access-Control-Allow-Private-Network", headers)

        manifest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "extension", "manifest.json")
        with open(manifest_path, encoding="utf-8") as stream:
            manifest = json.load(stream)
        self.assertIn("action", manifest)
        self.assertTrue(manifest.get("key"))
        self.assertIn("http://127.0.0.1:8000/*", manifest.get("host_permissions", []))

        status, headers, _ = self.raw_request("OPTIONS", "/api/analyze", headers={"Origin": ext_origin})
        self.assertNotEqual(status, 204)
        self.assertNotIn("Access-Control-Allow-Origin", headers)

        # POST /api/analyze must remain strictly blocked even for our own extension origin.
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post({"mode": "catalog", "product_id": "SP01"}, origin=ext_origin)
        self.assertEqual(error.exception.code, 403)

    def test_extension_handoff_roundtrip_validation_and_pii_count(self):
        ext_origin = self.PINNED_EXT_ORIGIN
        payload = {
            "product": {"shopid": "123", "itemid": "456", "name": "Tai nghe BT", "url": "https://shopee.vn/product/123/456"},
            "counts_by_star": {"5": 0, "4": 0, "3": 0, "2": 1, "1": 1},
            "reviews": [
                {"rating_star": 2, "comment": "Pin tụt nhanh, liên hệ 0912345678 nếu cần đổi."},
                {"rating_star": 1, "comment": "Tai trái hay bị ngắt kết nối khi đi ngoài đường."}
            ]
        }

        # Reject non-extension origins AND other Chrome extension IDs on POST /api/extension-handoff.
        for bad_origin in (
            None,
            "https://evil.example",
            self.base,
            "chrome-extension://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "chrome-extension://abcdefghijklmnop",
        ):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.post(payload, origin=bad_origin, path="/api/extension-handoff")
            self.assertEqual(error.exception.code, 403, f"Expected 403 for POST Origin={bad_origin}")

        # Reject non-Shopee URL and oversized review list.
        for bad_payload in (
            {**payload, "product": {"url": "https://outside.example/item/1"}},
            {"product": {"url": "https://shopee.vn/product/1/2"}, "reviews": [{"rating_star": 1, "comment": "a"}] * 251},
            {"product": {"url": "https://shopee.vn/product/1/2"}, "reviews": "not-a-list"},
        ):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.post(bad_payload, origin=ext_origin, path="/api/extension-handoff")
            self.assertEqual(error.exception.code, 400)

        # Reject empty and >2MB handoff body.
        for length, expected_code in ((0, 400), (MAX_BODY_BYTES + 1, 413)):
            status, _, raw = self.raw_request(
                "POST", "/api/extension-handoff",
                headers={"Origin": ext_origin, "Content-Length": str(length)}
            )
            self.assertEqual(status, expected_code)
            self.assertTrue(json.loads(raw)["message"])

        # Valid handoff returns ui_url + CORS header and round-trips cleanly into /api/analyze.
        status, headers, raw = self.raw_request(
            "POST", "/api/extension-handoff",
            body=json.dumps(payload).encode("utf-8"),
            headers={"Origin": ext_origin, "Content-Type": "application/json"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), ext_origin)
        created = json.loads(raw)
        self.assertTrue(created["ok"])
        hid = created["handoff_id"]
        self.assertEqual(created["ui_url"], "%s/?handoff=%s" % (self.base, hid))
        self.assertEqual(created["review_count"], 2)

        # Foreign/extension origin cannot GET the stored handoff; local UI can.
        for bad_origin in ("https://evil.example", ext_origin):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.get("/api/extension-handoff/" + hid, origin=bad_origin)
            self.assertEqual(error.exception.code, 403)

        loaded = json.loads(self.get("/api/extension-handoff/" + hid))
        self.assertTrue(loaded["ok"])
        self.assertEqual(loaded["payload"]["product"]["name"], "Tai nghe BT")

        analyzed = self.post({"mode": "payload", "payload": loaded["payload"]})
        self.assertEqual(analyzed["analysis"]["stats"]["total"], 2)
        self.assertEqual(analyzed["analysis"]["stats"]["pii_redacted_review_count"], 1)
        self.assertNotIn("0912345678", json.dumps(analyzed))

        # Unknown or malformed handoff IDs return 404.
        for bad_id in ("missing-id-12345", "short", "../etc/passwd"):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.get("/api/extension-handoff/" + bad_id)
            self.assertEqual(error.exception.code, 404)

    def test_extension_handoff_fifo_cap_and_ui_hooks(self):
        ext_origin = self.PINNED_EXT_ORIGIN
        ids = []
        for idx in range(12):
            body = {
                "product": {"url": "https://shopee.vn/product/123/%d" % idx, "name": "SP %d" % idx},
                "reviews": [{"rating_star": 2, "comment": "Lỗi sản phẩm %d sau khi dùng." % idx}]
            }
            created = self.post(body, origin=ext_origin, path="/api/extension-handoff")
            ids.append(created["handoff_id"])
        for evicted in ids[:2]:
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.get("/api/extension-handoff/" + evicted)
            self.assertEqual(error.exception.code, 404)
        latest = json.loads(self.get("/api/extension-handoff/" + ids[-1]))
        self.assertEqual(latest["payload"]["product"]["name"], "SP 11")

        html = self.get("/")
        self.assertIn('value="payload"', html)
        self.assertIn('id="payload-fields"', html)
        self.assertIn('id="payload-file"', html)
        self.assertNotIn('id="product-url"', html)
        self.assertIn("/api/extension-handoff/", self.get("/app.js"))

    def test_extension_handoff_env_allowlist_override_and_fail_closed(self):
        custom_id = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        payload = {
            "product": {"url": "https://shopee.vn/product/1/2"},
            "reviews": [{"rating_star": 2, "comment": "Pin nhanh hết sau khi sạc."}],
        }
        for env_value, allowed_origin, blocked_origin in (
            (custom_id, "chrome-extension://" + custom_id, self.PINNED_EXT_ORIGIN),
            ("*", None, self.PINNED_EXT_ORIGIN),
        ):
            with patch.dict(os.environ, {"REVIEW_LENS_EXTENSION_IDS": env_value}):
                srv = create_server(0)
            t = threading.Thread(target=srv.serve_forever, daemon=True)
            t.start()
            try:
                conn = http.client.HTTPConnection("127.0.0.1", srv.server_port, timeout=5)
                try:
                    conn.request(
                        "POST", "/api/extension-handoff",
                        body=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json", "Origin": blocked_origin},
                    )
                    self.assertEqual(conn.getresponse().status, 403)
                finally:
                    conn.close()
                if allowed_origin:
                    conn = http.client.HTTPConnection("127.0.0.1", srv.server_port, timeout=5)
                    try:
                        conn.request(
                            "POST", "/api/extension-handoff",
                            body=json.dumps(payload).encode("utf-8"),
                            headers={"Content-Type": "application/json", "Origin": allowed_origin},
                        )
                        resp = conn.getresponse()
                        self.assertEqual(resp.status, 200)
                        self.assertEqual(resp.getheader("Access-Control-Allow-Origin"), allowed_origin)
                    finally:
                        conn.close()
            finally:
                srv.shutdown()
                srv.server_close()
                t.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
