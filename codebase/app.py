"""Web local dùng backend main thống nhất; chạy bằng python run.py."""
import base64
import hashlib
import json
import os
import re
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

for stream in (sys.stdout, sys.stderr, sys.stdin):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tracing
import ai
from ui_backend import ROOT, MAX_BODY_BYTES, MAX_REVIEW_CHARS, MAX_REVIEWS, analyze_for_ui, public_error, catalog_products

HANDOFF_TTL_SECONDS = 900
MAX_HANDOFFS = 10
_HANDOFF_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
_EXT_ID_RE = re.compile(r"^[a-p]{32}$")
_CHROME_ID_TABLE = str.maketrans("0123456789abcdef", "abcdefghijklmnop")


def _derive_manifest_extension_id(manifest_path=None):
    """Tính Chrome Extension ID 32 ký tự cố định từ trường public `key` trong extension/manifest.json."""
    path = manifest_path or (ROOT / "extension" / "manifest.json")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        key = manifest.get("key")
        if not isinstance(key, str) or not key.strip():
            return None
        der = base64.b64decode(key.strip(), validate=True)
        ext_id = hashlib.sha256(der).hexdigest()[:32].translate(_CHROME_ID_TABLE)
        return ext_id if _EXT_ID_RE.fullmatch(ext_id) else None
    except (OSError, ValueError, TypeError):
        return None


def _load_allowed_extension_ids(override=None):
    """Trả tập Chrome Extension ID được phép gọi /api/extension-handoff (fail-closed)."""
    if override is not None:
        return frozenset(
            ext_id.strip().lower()
            for ext_id in override
            if isinstance(ext_id, str) and _EXT_ID_RE.fullmatch(ext_id.strip().lower())
        )
    raw = os.environ.get("REVIEW_LENS_EXTENSION_IDS")
    if raw is not None and raw.strip():
        tokens = [part.strip().lower() for part in re.split(r"[\s,]+", raw.strip()) if part.strip()]
        return frozenset(token for token in tokens if _EXT_ID_RE.fullmatch(token))
    manifest_id = _derive_manifest_extension_id()
    return frozenset({manifest_id}) if manifest_id else frozenset()


def _is_allowed_extension_origin(origin, allowed_ids):
    if not isinstance(origin, str) or not origin.startswith("chrome-extension://"):
        return False
    ext_id = origin[len("chrome-extension://"):]
    return bool(_EXT_ID_RE.fullmatch(ext_id) and ext_id in allowed_ids)


def _validate_handoff_payload(payload):
    """Kiểm tra sơ bộ payload từ extension; giữ nguyên văn bản để agent tự ẩn danh và đếm PII."""
    if not isinstance(payload, dict):
        raise ValueError("Payload extension phải là một object JSON.")
    product = payload.get("product") if isinstance(payload.get("product"), dict) else {}
    raw_url = payload.get("url") or product.get("url")
    parsed = urlsplit(str(raw_url or ""))
    if parsed.scheme not in {"http", "https"} or parsed.hostname != "shopee.vn":
        raise ValueError("Chỉ hỗ trợ payload sản phẩm công khai trên shopee.vn.")
    reviews = payload.get("reviews")
    if not isinstance(reviews, list) or len(reviews) > MAX_REVIEWS:
        raise ValueError("Danh sách review phải là mảng có tối đa %d mục." % MAX_REVIEWS)
    return len(reviews)


def load_catalog():
    """Chỉ nạp fixture UI có nhãn synthetic; không giả làm listing đã crawl."""
    with Path(__file__).with_name("ui_demo_data.json").open(encoding="utf-8") as stream:
        return json.load(stream)


def cli_main():
    from agent import answer
    print("Nhập SP01–SP03 hoặc review văn bản, /quit để thoát.")
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            return 0
        if text == "/quit":
            return 0
        if not text:
            continue
        tracing.begin("cli")
        try:
            print(answer(text)["output"])
        except Exception as exc:
            print(public_error(exc))
        finally:
            usage, _ = tracing.end()
            print("(model: %s · gọi %d · công cụ %d · token %d/%d)" %
                  (",".join(usage["models"]) or "none", usage["model_calls"], usage["tool_calls"],
                   usage["tokens_in"], usage["tokens_out"]))


def create_server(port=8000, allowed_extension_ids=None):
    catalog = load_catalog()
    lock = threading.Lock()
    handoff_lock = threading.Lock()
    handoffs = {}  # Chỉ lưu trong bộ nhớ tạm (không ghi file theo spec.md §9).
    allowed_ext_ids = _load_allowed_extension_ids(allowed_extension_ids)
    static = Path(__file__).with_name("web")

    def prune_handoffs(now):
        expired = [hid for hid, entry in handoffs.items() if entry["expires_at"] <= now]
        for hid in expired:
            handoffs.pop(hid, None)

    class Handler(BaseHTTPRequestHandler):
        def _local_origins(self):
            return {
                "http://127.0.0.1:%d" % self.server.server_port,
                "http://localhost:%d" % self.server.server_port,
            }

        def send_data(self, value, status=200, content_type="application/json; charset=utf-8", extra_headers=None):
            body = json.dumps(value, ensure_ascii=False).encode("utf-8") if isinstance(value, (dict, list)) else value
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            for header_name, header_value in (extra_headers or {}).items():
                self.send_header(header_name, header_value)
            self.end_headers()
            self.wfile.write(body)

        def _read_json_body(self, extra_headers=None):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0:
                    self.send_data({"message": "Đầu vào rỗng hoặc Content-Length không hợp lệ."}, 400, extra_headers=extra_headers)
                    return None
                if length > MAX_BODY_BYTES:
                    self.send_data({"message": "Đầu vào vượt giới hạn 2 MB."}, 413, extra_headers=extra_headers)
                    return None
                return json.loads(self.rfile.read(length).decode("utf-8"))
            except (ValueError, UnicodeError):
                self.send_data({"message": "Đầu vào API không hợp lệ."}, 400, extra_headers=extra_headers)
                return None

        def do_OPTIONS(self):
            path = urlsplit(self.path).path
            if path != "/api/extension-handoff":
                self.send_data({"message": "Không tìm thấy endpoint."}, 404)
                return
            origin = self.headers.get("Origin", "")
            if not _is_allowed_extension_origin(origin, allowed_ext_ids):
                self.send_data({"message": "Extension ID không nằm trong danh sách được phép."}, 403)
                return
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.send_header("Access-Control-Max-Age", "600")
            self.send_header("Vary", "Origin")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self):
            path = urlsplit(self.path).path
            assets = {"/": ("index.html", "text/html; charset=utf-8"),
                      "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                      "/style.css": ("style.css", "text/css; charset=utf-8")}
            if path in assets:
                name, content_type = assets[path]
                self.send_data((static / name).read_bytes(), content_type=content_type)
            elif path == "/api/products":
                products = [{"id": row["product_code"], "name": row["product_name"],
                             "review_count": row["sample_review_count"], "synthetic": False} for row in catalog_products()]
                products += [{"id": row["id"], "name": row["input"]["product_name"],
                              "review_count": len(row["input"]["reviews"]), "synthetic": True} for row in catalog["cases"]]
                self.send_data({"products": products, "model_provider": ai.MODEL_PROVIDER, "model_name": ai.MODEL_NAME,
                                "limits": {"max_reviews": MAX_REVIEWS, "max_review_chars": MAX_REVIEW_CHARS}})
            elif path.startswith("/api/products/"):
                product_id = path[len("/api/products/"):]
                real = next((p for p in catalog_products() if p["product_code"] == product_id), None)
                demo = next((p for p in catalog["cases"] if p["id"] == product_id), None)
                if "/" in product_id or not (real or demo):
                    self.send_data({"message": "Không tìm thấy sản phẩm."}, 404)
                else:
                    if real:
                        with (ROOT / real["file"]).open(encoding="utf-8") as stream:
                            rows = json.load(stream)["reviews"]
                    else:
                        rows = demo["input"]["reviews"]
                    text = "\n".join("[%s] %s" % (row["id"], row["text"]) for row in rows)
                    self.send_data({"id": product_id, "text": text, "synthetic": bool(demo)})
            elif path.startswith("/api/extension-handoff/"):
                origin = self.headers.get("Origin")
                if origin and origin not in self._local_origins():
                    self.send_data({"ok": False, "message": "Yêu cầu phải đến từ giao diện tại máy này."}, 403)
                    return
                handoff_id = path[len("/api/extension-handoff/"):]
                if not _HANDOFF_ID_RE.fullmatch(handoff_id):
                    self.send_data({"ok": False, "message": "Mã phiên dữ liệu từ extension không hợp lệ."}, 404)
                    return
                with handoff_lock:
                    prune_handoffs(time.monotonic())
                    entry = handoffs.get(handoff_id)
                if not entry:
                    self.send_data({"ok": False, "message": "Phiên dữ liệu từ extension không tồn tại hoặc đã hết hạn. Hãy bấm 'Mở trên Web UI' lại trong extension."}, 404)
                    return
                self.send_data({"ok": True, "handoff_id": handoff_id, "payload": entry["payload"]})
            else:
                self.send_data({"message": "Không tìm thấy trang."}, 404)

        def do_POST(self):
            path = urlsplit(self.path).path
            if path == "/api/extension-handoff":
                origin = self.headers.get("Origin", "")
                if not _is_allowed_extension_origin(origin, allowed_ext_ids):
                    self.send_data({"ok": False, "message": "Extension ID không nằm trong danh sách được phép."}, 403)
                    return
                cors = {"Access-Control-Allow-Origin": origin, "Vary": "Origin"}
                payload = self._read_json_body(extra_headers=cors)
                if payload is None:
                    return
                try:
                    review_count = _validate_handoff_payload(payload)
                except ValueError as exc:
                    self.send_data({"ok": False, "message": str(exc)}, 400, extra_headers=cors)
                    return
                now = time.monotonic()
                handoff_id = secrets.token_urlsafe(16)
                with handoff_lock:
                    prune_handoffs(now)
                    while len(handoffs) >= MAX_HANDOFFS:
                        handoffs.pop(next(iter(handoffs)))
                    handoffs[handoff_id] = {"payload": payload, "expires_at": now + HANDOFF_TTL_SECONDS}
                ui_url = "http://127.0.0.1:%d/?handoff=%s" % (self.server.server_port, handoff_id)
                print("[web] handoff_stored reviews=%d" % review_count, flush=True)
                self.send_data({"ok": True, "handoff_id": handoff_id, "ui_url": ui_url, "review_count": review_count},
                               200, extra_headers=cors)
                return

            if path != "/api/analyze":
                self.send_data({"message": "Không tìm thấy endpoint."}, 404)
                return
            origin = self.headers.get("Origin")
            if origin and origin not in self._local_origins():
                self.send_data({"message": "Yêu cầu phải đến từ giao diện tại máy này."}, 403)
                return
            request = self._read_json_body()
            if request is None:
                return
            status = 200
            with lock:
                tracing.begin("web")
                try:
                    response = analyze_for_ui(request)
                except Exception as exc:
                    print("[web] exception=%s" % type(exc).__name__, flush=True)
                    status = 400 if isinstance(exc, ValueError) else 502
                    try:
                        payload = request.get("payload") if isinstance(request, dict) else None
                        product = payload.get("product", {}) if isinstance(payload, dict) else {}
                        url = (payload.get("url") or product.get("url")) if isinstance(payload, dict) and isinstance(product, dict) else None
                        refused = isinstance(url, str) and urlsplit(url).hostname not in {"shopee.vn", None}
                    except ValueError:
                        refused = False
                    state = "refused" if refused else "invalid_input" if status == 400 else "error"
                    response = {"analysis": {"status": state, "summary": public_error(exc), "risks": []},
                                "sources": [], "coverage": None, "mock": ai.MODEL_PROVIDER == "fake"}
                finally:
                    usage, _ = tracing.end()
            response["usage"] = {k: usage[k] for k in ("model_calls", "tool_calls", "tokens_in", "tokens_out", "models")}
            response["origin"] = "backend" if status == 200 else "input_validation" if status == 400 else "runtime_error"
            print("[web] status=%s model=%s calls=%d tools=%d tokens=%d/%d" %
                  (response["analysis"]["status"], ",".join(usage["models"]) or "none", usage["model_calls"],
                   usage["tool_calls"], usage["tokens_in"], usage["tokens_out"]), flush=True)
            self.send_data(response, status)

    class LocalServer(ThreadingHTTPServer):
        allow_reuse_address = False

        def server_bind(self):
            # Windows cho phép hai listener dùng chung cổng nếu SO_REUSEADDR bật.
            if os.name == "nt":
                import socket
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            super().server_bind()

    return LocalServer(("127.0.0.1", port), Handler)


def main():
    if os.environ.get("REVIEW_LENS_MODE", "web").casefold() == "cli":
        return cli_main()
    import webbrowser
    try:
        server = create_server(int(os.environ.get("REVIEW_LENS_PORT", "8000")))
    except (ValueError, OSError, OverflowError) as exc:
        print("Không mở được UI: %s. Chọn cổng khác bằng REVIEW_LENS_PORT." % exc)
        return 1
    url = "http://127.0.0.1:%d" % server.server_port
    print("Review Lens — %s · backend main · provider=%s" % (url, ai.MODEL_PROVIDER), flush=True)
    print("Web dùng backend main; fake trả insufficient, không tự sinh rủi ro. Ctrl+C để dừng.", flush=True)
    if os.environ.get("REVIEW_LENS_NO_BROWSER") != "1":
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng UI.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
