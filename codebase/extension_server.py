"""Local HTTP bridge used by the Shopee review Chrome extension."""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import tracing  # noqa: E402
from agent import analyze_review_payload  # noqa: E402
from shopee_reviews import _anonymize_text  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765
MAX_BODY = 2 * 1024 * 1024


class Handler(BaseHTTPRequestHandler):
    server_version = "BornToBuildReviewAgent/1.0"

    def log_message(self, fmt, *args):
        # Keep review text and payloads out of the server log.
        print("[extension] " + fmt % args)

    def _allowed_origin(self):
        origin = self.headers.get("Origin", "")
        return origin.startswith("chrome-extension://")

    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        origin = self.headers.get("Origin", "")
        if origin.startswith("chrome-extension://"):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        if not self._allowed_origin():
            self._send(403, {"ok": False, "error": "Origin không được phép."})
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"ok": True, "service": "shopee-review-agent"})
            return
        self._send(404, {"ok": False, "error": "Không tìm thấy endpoint."})

    def do_POST(self):
        if self.path != "/analyze":
            self._send(404, {"ok": False, "error": "Không tìm thấy endpoint."})
            return
        if not self._allowed_origin():
            self._send(403, {"ok": False, "error": "Chỉ nhận yêu cầu từ extension."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send(400, {"ok": False, "error": "Content-Length không hợp lệ."})
            return
        if length <= 0 or length > MAX_BODY:
            self._send(413, {"ok": False, "error": "Dữ liệu gửi lên vượt giới hạn 2 MB."})
            return
        try:
            request = json.loads(self.rfile.read(length).decode("utf-8"))
            product = request.get("product") if isinstance(request.get("product"), dict) else {}
            product_url = request.get("url") or product.get("url")
            incoming = request.get("reviews")
            if not isinstance(incoming, list) or len(incoming) > 250:
                raise ValueError("Danh sách review phải có tối đa 250 mục.")

            reviews = []
            per_star = {star: 0 for star in range(1, 6)}
            for item in incoming:
                if not isinstance(item, dict):
                    continue
                try:
                    rating = int(item.get("rating_star", item.get("rating")))
                except (TypeError, ValueError):
                    continue
                if rating not in per_star or per_star[rating] >= 50:
                    continue
                per_star[rating] += 1
                reviews.append({
                    "review_id": str(item.get("review_id", ""))[:100],
                    "rating_star": rating,
                    "comment": _anonymize_text(item.get("comment", ""))[:3000],
                    "date": str(item.get("date", ""))[:80],
                    "variant": _anonymize_text(item.get("variant", ""))[:160],
                })

            tracing.begin("extension")
            try:
                agent_input = dict(request)
                agent_input["url"] = product_url
                agent_input["reviews"] = reviews
                agent_input["counts_by_star"] = per_star
                result = analyze_review_payload(agent_input)
            finally:
                tracing.end()
            self._send(200, result)
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError, ValueError) as exc:
            self._send(400, {"ok": False, "error": str(exc)[:300]})
        except Exception as exc:
            self._send(502, {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:300])})


def main():
    server = HTTPServer((HOST, PORT), Handler)
    print("Shopee review agent sẵn sàng tại http://%s:%d" % (HOST, PORT))
    print("Dừng server bằng Ctrl+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
