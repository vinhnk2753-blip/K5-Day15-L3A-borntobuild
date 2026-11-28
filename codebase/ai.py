"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trả một câu giả cố định, model "fake", token 0 — để luồng chạy hết từ trước CP2 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Nối model thật: đặt MODEL_PROVIDER=openai, MODEL_NAME và API_KEY trong .env (chép từ .env.example).
Nhánh OpenAI bên dưới gửi request dạng JSON và lấy token trực tiếp từ usage; không dán API key vào file này.
"""
import json
import os
import time
import urllib.error
import urllib.request

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RETRYABLE_HTTP_CODES = {429, 502, 503, 504}


def _env_int(name: str, default: int) -> int:
    try:
        return max(0, int((os.environ.get(name) or "").strip() or default))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return max(0.0, float((os.environ.get(name) or "").strip() or default))
    except ValueError:
        return default


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()
OPENAI_BASE_URL = (os.environ.get("OPENAI_BASE_URL") or "").strip().rstrip("/") or "https://api.openai.com/v1"
OPENAI_URL = (
    OPENAI_BASE_URL
    if OPENAI_BASE_URL.endswith("/chat/completions")
    else OPENAI_BASE_URL + "/chat/completions"
)
OPENAI_MAX_RETRIES = _env_int("OPENAI_MAX_RETRIES", 2)
OPENAI_RETRY_BACKOFF = _env_float("OPENAI_RETRY_BACKOFF", 1.0)


def _retry_delay(attempt: int, retry_after_header=None) -> float:
    base = OPENAI_RETRY_BACKOFF * (2 ** attempt)
    if retry_after_header:
        try:
            header_wait = float(str(retry_after_header).strip())
            if 0.0 <= header_wait <= 10.0:
                return header_wait
        except ValueError:
            pass
    return min(base, 10.0)


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}
    if MODEL_PROVIDER != "openai":
        raise RuntimeError("Bản chạy thử hiện hỗ trợ MODEL_PROVIDER=openai hoặc fake.")
    if not API_KEY:
        raise RuntimeError("Chưa cấu hình API_KEY trong .env.")
    if not MODEL_NAME:
        raise RuntimeError("Chưa cấu hình MODEL_NAME trong .env (ví dụ: gpt-6-luna).")
    if not OPENAI_URL.startswith(("https://", "http://")):
        raise RuntimeError("OPENAI_BASE_URL phải bắt đầu bằng http:// hoặc https://.")

    messages = ([{"role": "system", "content": system}] if system else [])
    messages.append({"role": "user", "content": user})
    payload = json.dumps({
        "model": MODEL_NAME,
        "messages": messages,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    result = None
    for attempt in range(OPENAI_MAX_RETRIES + 1):
        request = urllib.request.Request(OPENAI_URL, data=payload, method="POST", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                result = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            if exc.code in RETRYABLE_HTTP_CODES and attempt < OPENAI_MAX_RETRIES:
                wait = _retry_delay(attempt, exc.headers.get("Retry-After") if exc.headers else None)
                if wait > 0:
                    time.sleep(wait)
                continue
            raise RuntimeError("OpenAI API trả HTTP %s: %s" % (exc.code, detail)) from None
        except urllib.error.URLError as exc:
            if attempt < OPENAI_MAX_RETRIES:
                wait = _retry_delay(attempt)
                if wait > 0:
                    time.sleep(wait)
                continue
            raise RuntimeError("Không kết nối được OpenAI API: %s" % exc.reason) from None
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RuntimeError("OpenAI API trả phản hồi không phải JSON hợp lệ.") from None

    try:
        text = result["choices"][0]["message"]["content"]
        usage = result["usage"]
        tokens_in = int(usage["prompt_tokens"])
        tokens_out = int(usage["completion_tokens"])
    except (KeyError, IndexError, TypeError, ValueError):
        raise RuntimeError("Phản hồi OpenAI thiếu nội dung hoặc số token usage.") from None
    if not isinstance(text, str):
        raise RuntimeError("OpenAI API không trả nội dung dạng chữ.")
    return {"text": text, "model": MODEL_NAME,
            "tokens_in": tokens_in, "tokens_out": tokens_out}
