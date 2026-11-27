# Báo cáo thay đổi issue #4 — PR #18

**Người phụ trách:** Nguyễn Quỳnh Trang (`NguyenTrang005`).

**Phạm vi:** UI demo CP2, xử lý nhận xét review và ba mục bổ sung để đáp ứng DoD.

**Bản báo cáo:** commit `e2fc08f0858d4bc8b508ed89968be8550b9c5e21`, đối chiếu base main `4a799d3`.

**Ngày kiểm tra:** 27/11/2026.

[Issue #4](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/issues/4) · [PR #18](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/pull/18) · [Review yêu cầu sửa](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/pull/18#pullrequestreview-6087817796).

## 1. Kết quả cuối của phần việc

Chạy `python run.py` mở giao diện local. Người dùng nhập link Shopee hoặc dán review có số sao, xem số liệu/cờ nhiễu, tối đa 3 rủi ro và bấm mã [Rxx] để đọc nguồn nguyên văn đã được backend giữ và che thông tin liên hệ.

Web gọi `answer(text)` một lần với JSON đầu vào; nhận `output: str` cùng `structured`. Bản giả minh họa được 3 rủi ro từ mẫu tai nghe, có nhãn giả lập rõ ràng. Dưới 3 review giữ lại sau lọc theo quy tắc thì dừng trước model, báo chưa đủ dữ liệu.

Đây là kết quả triển khai CP2, chưa phải xác nhận chất lượng hoặc khả năng chạy API thật của CP3.

## 2. Đã sửa những phần nào

| Nhóm thay đổi | File chính | Nội dung hiện tại |
|---|---|---|
| Giao diện nhập và xem kết quả | `codebase/app.py`, `codebase/web/index.html`, `app.js`, `style.css` | Web stdlib, hai chế độ link/dán review có sao, chọn mẫu synthetic; hiển thị số liệu, cờ và tối đa 3 thẻ rủi ro; responsive 1440/390/320px. |
| Đối chiếu nguồn | `codebase/web/app.js`, `codebase/ui_backend.py` | Gom nguồn từ cả rủi ro và cờ; popup nội dung, sao, ngày/biến thể nếu có; mã do backend gán, không suy từ preview. |
| Điểm nối theo issue | `codebase/agent.py`, `codebase/ui_backend.py` | Web serialize request sang chuỗi JSON rồi gọi `answer(text)` đúng một lần. Giữ hợp đồng `output: str`, bổ sung structured/coverage; CLI vẫn nhận link văn bản. Không parse output dạng văn bản như JSON hoặc phân tích hai lần. |
| Kiểm và chuẩn hóa đầu vào | `codebase/review_input.py` | Tối đa 250 review, 3.000 ký tự/comment; sao nguyên 1–5 bắt buộc; giữ trường cần thiết, che email/SĐT, không tự gán sao. Mode dán không kích hoạt crawler từ URL bên trong review. |
| Định lượng nhiễu/bất thường | `codebase/review_signals.py`, `codebase/tools.py` | Tool `quantify_review_signals` chạy một lần: đếm trống, lặp, nhận thưởng, chưa dùng, chỉ giao hàng/dịch vụ và khen chung. Hiện tổng xét, số loại, tỷ lệ, số giữ và nguồn cờ; số ngoài giới hạn 50/mức sao được báo riêng. |
| Trạng thái biên G10 | `codebase/agent.py`, web/API | Dưới 3 review giữ lại → insufficient, không gọi model. URL ngoài Shopee bị chặn; input/schema sai, thiếu cấu hình và lỗi mạng có thông báo, giữ dữ liệu nhập. |
| Demo giả đáp ứng DoD | `codebase/agent.py`, `codebase/review_signals.py`, `ui_demo_data.json` | Fake dựng minh họa theo cụm từ có trong chính input, tối đa 3 rủi ro và nguồn tồn tại. Không ép input tích cực thành rủi ro. Đã bỏ `ui_demo.py`/bộ fake riêng tại UI; fake và định lượng nằm trong luồng backend dùng chung. |
| Tracing và hậu kiểm nguồn | `agent.py`, `tools.py`, `app.py` | Giữ decorator model/tool; lock quanh begin/end của web. Loại citation không tồn tại hoặc nguồn đã lọc khỏi tập gửi model. Không sửa khung tracing, không ước lượng token. |
| Sửa lỗi API/UX và vệ sinh kiểm thử | `app.py`, `web/app.js`, `web/style.css`, `tests/browser_smoke.mjs` | Chi tiết tại bảng review bên dưới. |
| Tài liệu và khai báo AI | `README.md`, `docs/ai-usage.md`, `docs/issue-4-checklist.md`, `docs/ui-ai-contract-proposal.md`, báo cáo này | Cập nhật hướng dẫn web/CLI, schema, phần thật/giả, checklist và xác nhận kiểm tay; giữ các dòng khai báo chung của thành viên khác. |
| Dữ liệu và kiểm thử | `codebase/ui_demo_data.json`, `tests/test_review_signals.py`, `test_ui_backend.py`, `test_web_app.py`, `browser_smoke.mjs` | Fixture ghi synthetic, không coi là dữ liệu thu thập thật; có kiểm nguồn, G10, số đếm, lỗi và tracing. `.gitignore` bỏ qua thư mục QA `.local/`. |

**Phần trưởng nhóm cần chú ý khi review:** PR cuối có sửa `agent.py` và `tools.py` theo yêu cầu bổ sung ba mục CP2, không chỉ thay giao diện. `analyze_reviews` dùng chung với extension nên quy tắc lọc/G10/fake cũng áp dụng ở đường gọi đó. Không đổi chữ ký `answer(text)` hoặc khóa output bắt buộc.

## 3. Đối chiếu nhận xét của reviewer

| Nhận xét trên PR | Cách xử lý ở bản cuối | Kiểm chứng |
|---|---|---|
| Blocker không tương thích backend main, fake không gọi model, output text bị parse JSON | Nhận main; dùng điểm vào `answer(JSON)` trả output + structured. Fake chỉ gọi model khi đủ dữ liệu. | Test UI gọi answer và analyze đúng một lần; kiểm fake và HTTP OpenAI stub. |
| Từ khóa pin khớp shipping, ship khớp flagship, lỗi khớp xin lỗi; hai danh sách từ không nhất quán | Bỏ bộ heuristic cũ; helper dùng chung so khớp có ranh giới từ, xử lý xin lỗi, không có nhánh useful riêng của UI. | Test shipping/flagship/xin lỗi và review có thuộc tính sản phẩm. |
| [R01] bị nhận nhầm JSON | Web có schema tường minh; chỉ parse object JSON ở điểm vào answer, nội dung [Rxx] trong review được giữ. Raw text không sao của hợp đồng MWG chưa được hỗ trợ. | Test nội dung nguồn có [R01] và URL không gọi crawler. |
| Tool định lượng bị gọi hai lần; gắn cờ sơ bộ khi lỗi | Gọi tool một lần trong analyze_reviews; UI chỉ render kết quả. API lỗi không kèm thống kê/cờ/rủi ro sơ bộ. | Kiểm tool_calls và tên sự kiện tool; test lỗi backend. |
| Route sản phẩm nhận đường dẫn lồng | Chỉ nhận đúng một segment ID sau /api/products/. | Đường dẫn lồng, rỗng hoặc dấu / cuối trả 404. |
| Body rỗng trả 413 | Content-Length rỗng/không hợp lệ trả 400; vượt giới hạn trả 413. | Test từ chối ở header. |
| Không có log loại ngoại lệ | Ghi tên loại lỗi tại server, không ghi body lỗi nhà cung cấp. | Test log và response không chứa payload lỗi nhạy cảm. |
| Cảnh báo kết quả cũ hiện trước lần phân tích đầu | Chỉ báo sau khi đã có kết quả rồi sửa input; giữ qua nhiều lần sửa và ẩn sau kết quả mới. | Chrome QA kiểm các trạng thái. |
| HTTP 400/403/413 mất thông báo máy chủ | Ưu tiên message từ response lỗi; không thay tất cả thành lỗi mạng chung. | Chrome QA kiểm 400/403/413/502. |
| Ghi đè dòng khai báo AI chung | Khôi phục Code bản chạy thử và Slide, văn bản; thêm dòng riêng của UI, giữ nội dung của Vinh/Yến. | Đối chiếu diff docs/ai-usage.md với main. |
| README hướng dẫn web/CLI mâu thuẫn | Mặc định mở web; dấu nhắc CLI chỉ dùng khi REVIEW_LENS_MODE=cli. | README và code cùng cách chạy. |
| Cổng âm/ngoài giới hạn gây lỗi | Bắt OverflowError, thoát gọn với thông báo. | Test -1, 65536 và chuỗi sai. |
| CSS khó đọc | Định dạng nhiều dòng, giữ nội dung quy tắc CSS ngoài khoảng trắng. | Kiểm responsive và đối chiếu trước/sau format. |
| Profile Chrome QA không được dọn | Chờ Chrome thoát, xác minh thư mục temp riêng rồi xóa và kiểm tra đã xóa. | Browser smoke hoàn tất, có kiểm cleanup. |

## 4. Kiểm thử và minh họa kết quả

- **34 test Python của issue #4 đạt**, đã chạy kiểm tra lại khi lập báo cáo này; không cộng các test mới của issue #8.
- **21 nhóm Chrome QA đã đạt** ở lượt kiểm giao diện trước đó: nguồn rủi ro/cờ, fake, G10, positive input, HTTP/network, stale state, responsive. Không coi kết quả này là lượt chạy API thật.
- Thử OpenAI trong test dùng HTTP stub; token của stub không phải token thực đo từ dịch vụ.
- Chạy demo bằng `python run.py`, chọn **Dán tập review có số sao → Tai nghe minh họa → Kiểm tra rủi ro**.

| Chỉ tiêu demo synthetic | Kết quả |
|---|---|
| Review được xét | 4 |
| Loại theo quy tắc | 1 review chưa dùng, 25% |
| Review giữ lại | 3 |
| Rủi ro giả lập | 3: kết nối, pin, cảm giác đeo |
| Nguồn rủi ro / nguồn cờ | R01, R03, R04 / R02 |
| Tracing | model=fake, model_calls=1, tool_calls=1, token vào/ra=0 |
| Mẫu chỉ chưa dùng/nhận xu | insufficient, không có rủi ro, model_calls=0 |

## 5. Phần không thay đổi và giới hạn

- Không sửa framework `run.py`, `codebase/tracing.py`, `eval/run_eval.py`, `cost/simulate.py` hoặc adapter API `codebase/ai.py` trong phần issue #4.
- Không sửa chuẩn đạt, metric, benchmark hay file kết quả để làm output đạt. Thay đổi eval/spec xuất hiện từ merge main là commit của thành viên khác, không phải phần sửa issue #4.
- Không đưa `cost/personas.yaml`, `cost/check_personas.py`, checklist/test mới của issue #8 vào phạm vi báo cáo hoặc PR #18.
- Chưa xác minh crawler/OpenAI live trong phần CP2. Catalog MWG SP01–SP03 và raw review không có sao chưa được nối vào backend Shopee.
- Thống kê là quy tắc prototype, không xác minh review thật/giả. Fake chỉ minh họa luồng, không dùng để báo chất lượng AI hoặc kết luận shop gian lận.
- Trang đã xác nhận kiểm tay bản trước và chốt khác biệt hợp đồng với Tuyên/Vinh. Không gán xác nhận kiểm tay cũ cho phần backend bổ sung sau đó.

## 6. Commit và trạng thái bàn giao

| Commit | Nội dung |
|---|---|
| `3984bcf` | UI demo CP2 bản đầu. |
| `ee8ce30` | Đồng bộ schema và điểm nối với backend Shopee sau khi nhận main. |
| `40c56c1` | Sửa lỗi UX/API và các nhận xét review; giữ khai báo AI chung. |
| `a1105c1` | Ghi nhận xác nhận kiểm tay/chốt hợp đồng do Trang cung cấp. |
| `e2fc08f` | Hoàn thiện ba mục còn thiếu: định lượng, fake 3 rủi ro, web gọi answer(text). |

Tại lần kiểm tra GitHub để lập báo cáo: PR #18 vẫn open, chưa merge; review CHANGES_REQUESTED đang trỏ tới bản đầu `3984bcf`. Cần trưởng nhóm review lại bản cuối `e2fc08f`; báo cáo không thay thế việc duyệt.

## 7. Đoạn tóm tắt để cập nhật mô tả PR

Dán đoạn dưới vào phần mô tả PR #18; báo cáo chi tiết nên giữ ở file này và dẫn link tương đối để reviewer đọc cùng diff. Có thể phản hồi ngắn ở các review thread tương ứng khi người phụ trách cập nhật GitHub.

~~~markdown
Đã cập nhật issue #4 đến commit e2fc08f:

- Web gọi answer(text) đúng một lần, giữ output: str và nhận structured để hiển thị.
- Bổ sung tool định lượng, số loại/tỷ lệ/nguồn cờ; G10 dưới 3 review giữ lại dừng trước model.
- Demo giả hiển thị 3 rủi ro từ review synthetic, đối chiếu nguyên văn [R01]/[R03]/[R04].
- Sửa lỗi stale state, thông báo HTTP, route sản phẩm, body rỗng, log ngoại lệ, cổng và cleanup Chrome.
- Giữ các dòng khai báo AI chung; cập nhật hợp đồng và hướng dẫn chạy.
- Validation: 34 test Python và 21 nhóm Chrome QA đạt. API/crawler live chưa được xác minh.

Lưu ý phạm vi: có bổ sung agent.py/tools.py và helper dùng chung backend;
không sửa framework, chuẩn đạt, metric, benchmark hoặc file kết quả.
Báo cáo chi tiết: [docs/pr-18-review-fixes.md](docs/pr-18-review-fixes.md).
Refs #4.
~~~
