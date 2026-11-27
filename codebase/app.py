"""Web local dùng trực tiếp backend Shopee của Tuyên; chạy bằng python run.py."""
import json
import os
import sys
import threading
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
from ai import MODEL_NAME, MODEL_PROVIDER
from ui_backend import MAX_BODY_BYTES, MAX_PER_STAR, MAX_REVIEW_CHARS, MAX_REVIEWS, DEMO_URL, analyze_for_ui, public_error


def load_catalog():
    """Chỉ nạp fixture UI có nhãn synthetic; không giả làm listing đã crawl."""
    with Path(__file__).with_name("ui_demo_data.json").open(encoding="utf-8") as stream:
        return json.load(stream)


def cli_main():
    from agent import answer
    print("Backend Shopee — nhập link sản phẩm, /quit để thoát.")
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


def create_server(port=8000):
    catalog = load_catalog()
    lock = threading.Lock()
    static = Path(__file__).with_name("web")

    class Handler(BaseHTTPRequestHandler):
        def send_data(self, value, status=200, content_type="application/json; charset=utf-8"):
            body = json.dumps(value, ensure_ascii=False).encode("utf-8") if isinstance(value, (dict, list)) else value
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlsplit(self.path).path
            assets = {"/": ("index.html", "text/html; charset=utf-8"),
                      "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                      "/style.css": ("style.css", "text/css; charset=utf-8")}
            if path in assets:
                name, content_type = assets[path]
                self.send_data((static / name).read_bytes(), content_type=content_type)
            elif path == "/api/products":
                self.send_data({"products": [{"id": row["id"], "name": row["input"]["product_name"],
                                              "review_count": len(row["input"]["reviews"])} for row in catalog["cases"]],
                                "synthetic": True, "model_provider": MODEL_PROVIDER, "model_name": MODEL_NAME,
                                "crawler_configured": bool(os.environ.get("APIFY_TOKEN", "").strip()),
                                "limits": {"max_reviews": MAX_REVIEWS, "max_per_star": MAX_PER_STAR,
                                           "max_review_chars": MAX_REVIEW_CHARS}})
            elif path.startswith("/api/products/"):
                product_id = path[len("/api/products/"):]
                product = next((r for r in catalog["cases"] if r["id"] == product_id), None) if "/" not in product_id else None
                if not product:
                    self.send_data({"message": "Không tìm thấy bộ minh họa."}, 404)
                else:
                    rows = [{"rating_star": r["rating"], "comment": r["text"]}
                            for r in product["input"]["reviews"]]
                    self.send_data({"url": DEMO_URL, "reviews": rows, "synthetic": True,
                                    "product_name": product["input"]["product_name"]})
            else:
                self.send_data({"message": "Không tìm thấy trang."}, 404)

        def do_POST(self):
            if urlsplit(self.path).path != "/api/analyze":
                self.send_data({"message": "Không tìm thấy endpoint."}, 404)
                return
            origin = self.headers.get("Origin")
            if origin and origin not in {"http://127.0.0.1:%d" % self.server.server_port,
                                         "http://localhost:%d" % self.server.server_port}:
                self.send_data({"message": "Yêu cầu phải đến từ giao diện tại máy này."}, 403)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0:
                    self.send_data({"message": "Đầu vào rỗng hoặc Content-Length không hợp lệ."}, 400)
                    return
                if length > MAX_BODY_BYTES:
                    self.send_data({"message": "Đầu vào vượt giới hạn 2 MB."}, 413)
                    return
                request = json.loads(self.rfile.read(length).decode("utf-8"))
            except (ValueError, UnicodeError):
                self.send_data({"message": "Đầu vào API không hợp lệ."}, 400)
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
                        refused = isinstance(request, dict) and isinstance(request.get("url"), str) and urlsplit(request["url"]).hostname not in {"shopee.vn", None}
                    except ValueError:
                        refused = False
                    state = "refused" if refused else "invalid_input" if status == 400 else "error"
                    response = {"analysis": {"status": state, "summary": public_error(exc), "risks": []},
                                "sources": [], "coverage": None, "mock": MODEL_PROVIDER == "fake"}
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
    print("Review Lens — %s · backend Shopee · provider=%s" % (url, MODEL_PROVIDER), flush=True)
    print("Web gọi answer(text); fake minh họa theo quy tắc, token 0. Ctrl+C để dừng.", flush=True)
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
