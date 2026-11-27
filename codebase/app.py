"""UI web CP2 bằng thư viện chuẩn; REVIEW_LENS_MODE=cli giữ giao diện dòng lệnh."""
import json
import os
import sys

for stream in (sys.stdout, sys.stderr, sys.stdin):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def display(result):
    print("\n" + result["message"])
    print("Trạng thái: %s · Review: %d · Gắn cờ: %d" %
          (result["status"], result["summary"]["total_reviews"], result["summary"]["flagged_reviews"]))
    for i, risk in enumerate(result["risks"], 1):
        print("\n%d. %s\n   %s" % (i, risk["title"], risk["description"]))
        for ev in risk["evidence"]:
            print("   [%s] %s" % (ev["review_id"], ev["quote"]))
    for flag in result["review_flags"]:
        print("Cờ [%s]: %s" % (flag["review_id"], flag["reason"]))
    print("Chỉ phản ánh review được cung cấp; người mua tự quyết định.\n")


def cli_main():
    import tracing
    from agent import answer
    from ui_demo import adapt_answer
    from ai import MODEL_PROVIDER
    print("Review Lens — V1 nhập review thủ công")
    print("Model: %s. CP2 dùng fake; token 0, không phải đánh giá AI thật." % MODEL_PROVIDER)
    print("Mỗi dòng một review. Dòng trống để phân tích; /sample dùng dữ liệu tự dựng; /quit thoát.")
    while True:
        lines, eof = [], False
        try:
            while True:
                try:
                    line = input("> " if not lines else "… ")
                except EOFError:
                    eof = True
                    break
                if not lines and line.strip() == "/quit":
                    return 0
                if not lines and line.strip() == "/sample":
                    path = os.path.join(os.path.dirname(__file__), "ui_demo_data.json")
                    with open(path, encoding="utf-8") as f:
                        lines = [json.dumps(json.load(f)["cases"][0]["input"], ensure_ascii=False)]
                    break
                if not line.strip():
                    break
                lines.append(line)
        except KeyboardInterrupt:
            print()
            return 0
        if not lines:
            if eof:
                return 0
            print("Chưa có review; nhập nội dung rồi để một dòng trống.")
            continue
        tracing.begin("app")
        try:
            output = adapt_answer("\n".join(lines), answer)
            display(json.loads(output["output"]))
        except Exception as exc:
            print("Không thể hoàn tất: %s. Kiểm tra cấu hình model trong docs/connect-model.md." % type(exc).__name__)
        finally:
            summary, _ = tracing.end()
            print("(model: %s · gọi %d · công cụ %d · token vào %d / ra %d)" %
                  (", ".join(summary["models"]) or "không gọi", summary["model_calls"], summary["tool_calls"],
                   summary["tokens_in"], summary["tokens_out"]))
        if eof:
            return 0


def load_catalog():
    path = os.path.join(os.path.dirname(__file__), "ui_demo_data.json")
    with open(path, encoding="utf-8") as stream:
        return json.load(stream)


def create_server(port=8000):
    """Tạo server chỉ tại loopback; không tạo thư viện hoặc dịch vụ ngoài."""
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from pathlib import Path
    from urllib.parse import urlsplit
    import tracing
    from agent import answer
    from ai import MODEL_PROVIDER
    from ui_demo import MAX_INPUT_CHARS, MAX_REVIEWS, MAX_REVIEW_CHARS, MIN_CLEAN_REVIEWS, adapt_answer

    catalog = load_catalog()
    lock = threading.Lock()  # tracing của khung dùng trạng thái toàn cục.
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
                                "synthetic": True, "model_provider": MODEL_PROVIDER,
                                "limits": {"max_reviews": MAX_REVIEWS, "max_review_chars": MAX_REVIEW_CHARS,
                                           "max_input_chars": MAX_INPUT_CHARS, "min_clean_reviews": MIN_CLEAN_REVIEWS}})
            elif path.startswith("/api/products/"):
                product = next((r for r in catalog["cases"] if r["id"] == path.rsplit("/", 1)[-1]), None)
                if product:
                    self.send_data({"input": product["input"], "synthetic": True})
                else:
                    self.send_data({"message": "Không tìm thấy sản phẩm mẫu."}, 404)
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
                if not 0 < length <= 1024 * 1024:
                    self.send_data({"message": "Đầu vào rỗng hoặc quá lớn."}, 413)
                    return
                request = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(request, dict) or not isinstance(request.get("input"), str):
                    raise ValueError("Thiếu input dạng chuỗi.")
            except (ValueError, UnicodeError):
                self.send_data({"message": "Đầu vào API không hợp lệ."}, 400)
                return
            status = 200
            with lock:
                tracing.begin("web")
                try:
                    response = adapt_answer(request["input"], answer)
                    result = json.loads(response["output"])
                    sources = response.get("sources", [])
                except Exception:
                    status = 500
                    result = {"status": "error", "message": "Chưa thể hoàn tất kiểm tra. Hãy thử lại.",
                              "risks": [], "review_flags": [], "summary": {"total_reviews": 0, "flagged_reviews": 0}}
                    sources = []
                finally:
                    usage, _ = tracing.end()
            safe_usage = {k: usage[k] for k in ("model_calls", "tool_calls", "tokens_in", "tokens_out", "models")}
            print("[web] status=%s model=%s calls=%d tools=%d tokens=%d/%d" %
                  (result["status"], ",".join(safe_usage["models"]) or "none", safe_usage["model_calls"],
                   safe_usage["tool_calls"], safe_usage["tokens_in"], safe_usage["tokens_out"]), flush=True)
            self.send_data({"result": result, "sources": sources, "usage": safe_usage,
                            "mock": MODEL_PROVIDER == "fake"}, status)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    if os.environ.get("REVIEW_LENS_MODE", "web").casefold() == "cli":
        return cli_main()
    import webbrowser
    try:
        server = create_server(int(os.environ.get("REVIEW_LENS_PORT", "8000")))
    except (ValueError, OSError) as exc:
        print("Không mở được UI: %s. Chọn cổng khác bằng REVIEW_LENS_PORT." % exc)
        return 1
    url = "http://127.0.0.1:%d" % server.server_port
    print("Review Lens — mở giao diện tại %s" % url, flush=True)
    print("Dữ liệu chọn sẵn là minh họa, không phải crawl. Ctrl+C để dừng.", flush=True)
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
