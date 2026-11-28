> Đây là khung repo nộp bài. Điền mọi chỗ `____`, giữ nguyên tên các mục.
> Giờ, mốc, luật, rubric: xem `README.md`, `02-guide.md`, `03-rubric.md` trong repo đề (bộ đề BTC phát).

# borntobuild — Lọc nhiễu review & rút 3 rủi ro sản phẩm có trích dẫn

**Thành viên, lớp, track:** xem [TEAMS.md](TEAMS.md). **Điền TEAMS.md đúng format**: khi chấm và đánh giá, BTC quét file này để ghép điểm cho từng người.

*Lát cắt = phần nhỏ nhất làm xong được trong hackathon: một người dùng · một việc · một quyết định AI · một kết quả.*

---

## Nhóm làm gì, khung làm gì

| Nhóm quyết định và viết | Khung làm sẵn (không cần sửa) |
|---|---|
| Người dùng, pain, bằng chứng, impact (`evidence/`, `spec.md` §1–§2) | — |
| Hình dạng giải pháp, công cụ, prompt, luồng (`spec.md` §4, `codebase/agent.py`, `tools.py`, `ai.py`) | Ghi mọi lần gọi model / công cụ vào trace, cộng token (`codebase/tracing.py`) |
| Bộ câu thử, metric, chuẩn "đạt" (`eval/benchmark.csv`, `eval/metric_spec.yaml`, `spec.md` §7) | Kiểm đủ cột, đủ câu `kho` / `tu_choi`, đủ ≥1/3 câu từ người dùng / data thật (`run.py check`) |
| Chấm cột `pass` theo metric spec | Chạy cả bộ một lệnh, có run ID, model, token từng câu (`run.py eval`) · tính % đạt (`run.py score`) |
| Persona, số người dùng thật, giá model (`cost/personas.yaml`) | Sinh ~50 phiên, chạy thật qua bản chạy thử, tính chi phí / phiên, / task thành công, / tháng 3 kịch bản (`run.py simulate`) |

*Ví dụ track A (ví dụ cỡ, không phải lời giải):* nhóm viết công cụ `search_lesson` tra bài pre-class đã đánh mã đoạn, luồng "tra đoạn → model trả lời kèm mã đoạn, không có thì nói không có", metric "mọi khẳng định có mã đoạn đúng", persona "ôn dồn trước kiểm tra". Khung chạy 25 câu thử ra `run-1.csv`, nhóm chấm `pass`, `score` in % đạt; `simulate` chạy 50 phiên ra chi phí / task thành công cho hai model.

## Chạy trong 3 phút

Bộ khung cần **Python 3.10 trở lên** (Python 3.9 có sẵn trên macOS vẫn chạy được, chỉ in một dòng nhắc). **Không cần `pip install`.**

**Bước 1 — Mở cửa sổ lệnh ngay trong thư mục repo**

| Windows (PowerShell) | macOS |
|---|---|
| Mở thư mục repo bằng File Explorer → bấm vào thanh địa chỉ → gõ `powershell` → Enter | Mở **Terminal** (Cmd + Space, gõ "Terminal") → gõ `cd ` (có dấu cách) → kéo thả thư mục repo vào → Enter |

Gõ `dir` (Windows) hoặc `ls` (macOS / Linux): thấy `run.py` và `README.md` là đang đứng đúng chỗ.

**Bước 2 — Kiểm Python và chạy thử**

| Việc | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Kiểm Python | `python --version` (không được thì `py --version`) | `python3 --version` |
| Chạy bản chạy thử (chế độ giả, chưa gọi model) | `python run.py` | `python3 run.py` |
| Kiểm bộ câu thử | `python run.py check` | `python3 run.py check` |
| Tạo file `.env` để nối model | `copy .env.example .env` | `cp .env.example .env` |

- Windows: gõ `python` mà mở Microsoft Store hoặc báo không có lệnh → dùng `py`. Chưa có Python: cài từ python.org, **tick "Add python.exe to PATH"**, mở lại PowerShell.
- macOS: báo `command not found: python` là bình thường → dùng `python3`.
- Sau khi chạy `python run.py`, mở web local **http://127.0.0.1:8000**, chọn sản phẩm thật `SP01–SP06` (60 review ĐMX/TGDĐ + 90 review Tiki đã ẩn danh) hoặc chuyển sang **Dán tập review văn bản** (mỗi review một dòng, không bắt buộc URL hay số sao). Nếu `.env` đặt `MODEL_PROVIDER=openai`, agent gọi model thật; nếu không, fake trả `insufficient` và không sinh rủi ro. Bấm `[Rxx]` để đối chiếu nguồn đã che PII; Ctrl+C để dừng.
- Với nhà cung cấp tương thích OpenAI, đặt thêm `OPENAI_BASE_URL` trong `.env` theo địa chỉ nhà cung cấp (ví dụ `https://api.shopaikey.com/v1`, không thêm `/chat/completions`). Bỏ trống để dùng OpenAI trực tiếp. Giữ `MODEL_PROVIDER=openai`, dùng key và mã model của nhà cung cấp đó; dừng rồi chạy lại server sau khi đổi cấu hình. Khả năng tương thích của dịch vụ trung gian cần kiểm tra bằng một lượt gọi thật; giá trong `cost/personas.yaml` cần đối chiếu với biểu phí thực tế của dịch vụ.
- Web gọi `agent.answer(text)` cho mã catalog hoặc raw review, dùng nguyên `structured` của backend main PR #20. Chế độ payload Shopee ở API `/api/analyze` gọi `agent.analyze_review_payload(payload)`, không gọi crawler Apify. Không còn `review_input.py`/`review_signals.py` hoặc bộ fake riêng tại UI.
- CLI tùy chọn: PowerShell đặt `$env:REVIEW_LENS_MODE='cli'` rồi `python run.py`; nhập mã catalog hoặc review và `/quit` để thoát. Đặt lại `web` để mở giao diện. Nếu cổng bận, đặt `$env:REVIEW_LENS_PORT='8001'`. Không thêm dependency ngoài Python stdlib.

Trong README này lệnh viết là `python …`; máy nhóm cần `python3` hay `py` thì gõ thay.

## Lệnh

| Lệnh | Làm gì |
|---|---|
| `python run.py` | Chạy bản thử (nhập mã sản phẩm/dán review, nhận tối đa 3 rủi ro có citation đã hậu kiểm) |
| `python run.py check` | Kiểm `eval/benchmark.csv` (6 cột, số câu, `kho` / `tu_choi`, mã `source`, ô trống, dòng mẫu) `eval/metric_spec.yaml` (≥3 metric điền đủ) và `TEAMS.md` (đúng format để BTC quét). Chỉ cảnh báo, không sửa file |
| `python run.py eval --try` | **Thử luồng agent:** chạy 3 câu đầu (`--try 5` = 5 câu) → `eval/run-try.csv`; khi `.env` chọn OpenAI, xác nhận model thật và usage token. Không tính là một lượt |
| `python run.py eval` | Chạy cả bộ qua `codebase/agent.py` → `eval/run-1.csv` (lần sau `run-2.csv`…) + `traces/run-1.jsonl`. Mỗi dòng có run ID, model, số lần gọi model / công cụ, token. Model còn giả → chỉ ghi `run-mock.csv`; mọi câu lỗi → `run-error.csv`; Ctrl+C → `run-stopped.csv` — đều **không** được đánh số |
| `python run.py eval --fake` | Thử riêng bộ chạy, không gọi agent → `eval/run-fake.csv` |
| `python run.py score eval/run-1.csv` | Sau khi điền cột `pass` (1 / 0): in % đạt tổng và theo `type`. Còn ô trống → "CHƯA CHẤM XONG", không in % |
| `python run.py simulate --try` | Thử mô phỏng chi phí 10 phiên (làm trước CP3) → `cost/simulate-try.csv` |
| `python run.py simulate` | Mô phỏng chi phí khi dùng thật theo `cost/personas.yaml` (≥50 phiên) → `cost/simulate-N.csv` + `cost/simulate-N-summary.md` |
| `python run.py simulate --rate-from eval/run-2.csv` | Như trên, lấy tỉ lệ đạt từ đúng lượt chỉ định. Không ghi thì khung lấy lượt `run-N` mới nhất đã chấm, cùng model, và ghi rõ đã lấy lượt nào trong bản tóm tắt |

Gói miễn phí báo hết lượt: thêm `--wait 4` sau `eval` hoặc `simulate` (nghỉ 4 giây giữa hai lượt gọi). Sửa CSV bằng Excel: *File → Save As → CSV UTF-8*; Google Sheets: *Tệp → Tải xuống → CSV*.

**Lượt có lỗi kỹ thuật** (cột `error` có chữ): không sửa tay file đó, chạy lại thành lượt mới và ghi vào bảng các lượt ở `eval/README.md`. Không xoá file lượt nào.

Nhóm dùng stack khác (Node, Streamlit, notebook…): sửa hàm `run_app()` trong `run.py` để `python run.py` vẫn chạy được bản chạy thử, và giữ `answer()` trong `codebase/agent.py` để `eval`, `simulate` chạy được.

## Bản chạy thử — viết ở đâu

| File | Viết gì | Bước guide |
|---|---|---|
| `codebase/agent.py` | `answer(text)` — lọc, che PII, phát hiện trùng, gọi model theo `.env`, hậu kiểm citations; trả `{"output": str, "structured": dict}` | 3.2 |
| `codebase/tools.py` | Công cụ đọc catalog, chuẩn hóa review, lọc nhiễu và gắn cờ nội dung trùng; mỗi công cụ có `@tool` | 2.2, 3.2 |
| `codebase/ai.py` | `call_model(system, user)` — chỗ duy nhất gọi model; chế độ OpenAI hoặc giả | 3.3 |

- **CP3:** `answer(text)` đọc dữ liệu mẫu hoặc review dán, che email/số điện thoại, lọc review nhiễu và gửi JSON review sạch tới GPT khi `.env` chọn OpenAI. `eval --try` gọi cùng luồng; chế độ fake không đưa ra kết luận rủi ro.
- Extension crawl review công khai trong page context, hiển thị JSON và tiến độ, rồi gửi payload tới backend local. Backend dùng cùng bộ lọc, model và hậu kiểm citation.
- Bộ chạy gửi **nguyên ô `input`** của câu thử vào `answer(text)`. Dữ liệu nền (bài học, thông báo, lịch…) để trong `data/`, đọc qua công cụ.

### Dữ liệu và luồng mở rộng Shopee

Luồng CLI dùng bộ review mẫu đã ẩn danh trong `data/products/` hoặc review người dùng dán; không tự crawl URL Shopee và không cần `APIFY_TOKEN`. Với `.env` cấu hình OpenAI, agent gửi phần review đã lọc/ẩn danh tới API; không đưa API key vào extension.

Demo dạng Chrome extension có hướng dẫn riêng tại [extension/README.md](extension/README.md). Extension gọi endpoint review trong page context, xuất JSON và gửi dữ liệu đã bỏ tên người đánh giá tới agent backend Python cục bộ; agent lọc nhiễu, xác thực citation, rồi dùng GPT nếu `.env` đã cấu hình. Endpoint từng trả HTTP 403 nên cần xác minh crawl trên listing thật; không nhúng API key vào extension.

## Phần nào thật, phần nào giả

| Thành phần | Thật / Giả | Ghi chú |
|---|---|---|
| Lời gọi AI ở quyết định trung tâm (`codebase/ai.py`) | **Thật** khi `.env` đặt `MODEL_PROVIDER=openai`; **Giả** (`fake`) khi không có `.env` | Đã chạy thật 2 lượt eval 25 câu (`eval/run-1.csv`, `run-2.csv`), 50 phiên mô phỏng chi phí (`cost/simulate-1.csv`) và demo Web UI với `gpt-6-luna` (OpenAI / `OPENAI_BASE_URL` tương thích). Chế độ `fake` trả token 0, trạng thái `insufficient` và không tự sinh rủi ro |
| Dữ liệu đánh giá nền (`data/products/*.json`, `eval/benchmark.csv`) | **Thật** (150 review công khai ẩn danh `SP01–SP06` + 15 câu `B11–B25`) · **Synthetic** (10 câu `B01–B10` & 3 bộ `DEMO01–DEMO03` trong UI) | 150/150 review công khai ĐMX/TGDĐ + Tiki đã kiểm 0 lỗi PII bằng `python evidence/count.py`; dữ liệu `synthetic` chỉ dùng cho ca biên/tấn công và thử giao diện, không dùng làm bằng chứng pain |
| Web UI local (`codebase/app.py`, `codebase/web/`) | **Thật** — nối trực tiếp `agent.answer(text)` & `agent.analyze_review_payload()` | Hiển thị thống kê lọc nhiễu, cờ lặp, tối đa 3 rủi ro kèm modal đối chiếu `[Rxx]` và usage token thật từ tracing (test tự động trong `tests/` dùng stub để chạy offline) |
| Chrome extension Shopee (`extension/`) | **Thử nghiệm / phụ thuộc nền tảng** | Đọc review trong page context trên trang Shopee và đẩy JSON sang backend local; endpoint Shopee từng trả HTTP 403 nên không phải nguồn bắt buộc của luồng `python run.py`, `eval` hay `simulate` |

## Dùng AI vào việc gì

2–3 dòng (bắt buộc): nhóm dùng công cụ AI nào để làm gì, người kiểm lại phần nào. Chi tiết: [docs/ai-usage.md](docs/ai-usage.md). Coding agent đọc [AGENTS.md](AGENTS.md).

Nhóm dùng Codex, Claude Code và Antigravity để hỗ trợ viết/rà code bản chạy thử (`codebase/`, `extension/`), dựng script đếm dữ liệu (`evidence/count.py`), soạn nháp bộ câu thử (`eval/`), chấm nháp eval, chạy kiểm tra chi phí (`cost/`) và biên tập tài liệu; bản chạy thử gọi OpenAI GPT (`gpt-6-luna`) qua `.env` trên review đã lọc và che PII. Các thành viên tự kiểm tay 60/60 + 90/90 nhãn dữ liệu, rà xác nhận 25/25 câu eval cả 2 lượt + chấm mù chéo 5/5 câu, đối chiếu 50 phiên mô phỏng chi phí và chạy toàn bộ bộ test trước khi merge; không dùng AI để bịa phỏng vấn hay sửa kết quả chạy thật.

## File mẫu — điền ở bước nào

| File | Điền ở bước guide | Mốc |
|---|---|---|
| `TEAMS.md` | 1.0 | CP1 · **đúng format**, BTC quét khi chấm |
| `canvas.md` | 1.4 | CP1, cập nhật CP2 |
| `evidence/hypothesis.md` | 1.1 | trước khi tìm bằng chứng |
| `evidence/data-mining.md` · `evidence/interviews/TEMPLATE.md` → `P1.md`… · `evidence/survey/TEMPLATE.md` | 1.2 | bắt đầu sau Zoom, xong CP3 |
| `evidence/summary.md` | 1.2 | CP3 |
| `spec.md` | §0–§2: 1.1–1.3 · §3–§5: 2.1–2.3 · §7: 2.4 · §8: 4.2 · §10: suốt | §7 chốt CP2 · §0–§7 CP3 · đủ CP4 |
| `data/DATA_CARD.md` | 2.4 | bản đầu CP2 |
| `eval/benchmark.csv` · `eval/metric_spec.yaml` | 2.4 | ≥10 câu + metric chốt CP2 · 20–30 câu CP3 |
| `codebase/` | 3.2, 3.3 | khung CP2 · AI thật CP3 |
| `eval/report.md` · `eval/README.md` | 4.1 (README mục 1–4 từ 2.4) | CP4 |
| `cost/personas.yaml` · `cost/cost-estimate.md` | 4.2 | thử 10 phiên CP3 · đủ CP4 |
| `validation/log.md` *(bonus)* | 4.3 | CP4 |
| `slides/outline.md` → `demo-slides.pdf` | 5.1 | CP4 |
| `reflection/TEMPLATE.md` → `reflection/<ten>.md` | 5.3 | 23:59 Thứ Bảy 28/11 |
| `AGENTS.md` · `docs/ai-usage.md` | khi dùng coding agent / AI | suốt |

## Bảy hạng mục bắt buộc — nằm ở file nào

| # | Hạng mục | File |
|---|---|---|
| 1 | Bằng chứng pain | `evidence/` (tổng hợp ở `evidence/summary.md`) |
| 2 | Impact có số | `spec.md` §2 |
| 3 | Thiết kế giải pháp | `spec.md` §4 |
| 4 | Bản chạy thử làm trọn lát cắt | `codebase/` · lệnh ở mục "Lệnh" |
| 5 | Định nghĩa "tốt" + bộ câu thử | `data/DATA_CARD.md` · `eval/` |
| 6 | Mô phỏng chi phí khi dùng thật | `cost/` |
| 7 | Slide + demo + video dự phòng | `demo-slides.pdf` ở thư mục gốc · link video: [Video demo dự phòng (Google Drive)](https://drive.google.com/file/d/1ANgzsTN_givlL6PipNGsTdFwEgPLhk-C/view?usp=sharing) |
| + | *Bonus:* người dùng thử | `validation/log.md` |
