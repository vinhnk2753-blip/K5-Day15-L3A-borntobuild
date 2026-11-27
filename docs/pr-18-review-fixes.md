# Báo cáo cập nhật PR #18 theo main PR #20

**Phụ trách:** Nguyễn Quỳnh Trang (@NguyenTrang005). **Ngày:** 28/11/2026.
**Base:** origin/main 266e007 — đã merge PR #20 của Tuyên.
[PR #18](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/pull/18) · [Issue #4](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/issues/4).

## 1. Trạng thái cuối

PR chỉ bổ sung UI và điểm nối hiển thị. Backend codebase/agent.py, tools.py, ai.py giữ nguyên main; không có workflow lọc/G10/fake khác.
Các mô tả ở commit e2fc08f/76c8ede về backend riêng và demo fake 3 rủi ro là lịch sử, đã được thay thế ở vòng này.

## 2. Xử lý review mới

| Yêu cầu | Đã sửa | File/kiểm chứng |
|---|---|---|
| Merge main mới, thu gọn UI | Giải quyết xung đột agent/README/ai-usage; chọn backend main nguyên trạng. | git diff origin/main cho agent.py/tools.py/ai.py rỗng. |
| Bỏ helper trùng backend | Xóa review_input.py/review_signals.py và test_review_signals.py; không giữ quantify_review_signals/fake riêng. | Không còn import helper đã xóa; 19 test backend main đạt. |
| Chọn catalog thật | Dropdown SP01–SP03 lấy metadata data/catalog.json; gọi agent.answer(code) đúng một lần. | app.py, ui_backend.py; test code và 20 review/case. |
| Dán review không sao/URL | Truyền text nguyên văn tới agent.answer(text); giữ [Rxx], không biến review MWG thành payload Shopee. | ui_backend.py/web; test và Chrome raw review. |
| Payload Shopee | API mode=payload gọi analyze_review_payload(payload); bỏ mode lấy link/crawl tự động trên web. | Test spy một lần gọi, không gọi answer/crawler ở đường này. |
| Stats schema main | Render total/filtered_noise/noise_pct/kept_clean/noise_breakdown/pii_redacted_review_count. Bỏ input_total/excluded_limit/min_clean_reviews và ngưỡng riêng. | app.js; test shape và render không có undefined. |
| flags/anomalies đúng kiểu | flags list[str]; anomalies dict. Hiện duplicate_count/duplicate_rate và nhóm ID lặp. | app.js; test clusters R01/R04, Chrome popup nguồn cờ. |
| Popup đúng nguồn | reviews_by_id là nguồn text chuẩn, có danh sách mọi review. Metadata rating/date/variant chỉ hiện nếu có. | ui_backend.py/app.js; test PII và quote, Chrome nguồn không sao. |
| Fake không sinh rủi ro | Giữ insufficient/risks=[] của backend main; bỏ tuyên bố fake luôn có 3 rủi ro. | Test fake và browser; nhánh 3 thẻ rủi ro chỉ kiểm bằng fixture QA có nhãn. |
| Đọc ai động | import ai, dùng ai.MODEL_PROVIDER/ai.MODEL_NAME lúc xử lý. | Test thay provider/name sau import vẫn cập nhật API/mock. |
| DEMO03 đủ dữ liệu minh họa | Thêm review về đường may, tổng 3; giữ nhãn synthetic và trạng thái kiểm tay đúng. | ui_demo_data.json; test catalog và Chrome 3 dòng. |
| Viền lỗi input | Thêm input[aria-invalid=true] và select cạnh textarea. | style.css và test asset. |
| hasResult / clear / edit | Lỗi không bật hasResult; clear reset false; edit focus reviews khi dán, selector khi chọn mẫu. | app.js; Chrome kiểm cả error, clear và edit. |
| README và mô tả PR | Lấy README main làm nền, giữ khai báo backend/extension của PR #20; bổ sung hướng dẫn web/CLI, báo cáo UI. Mô tả PR được thay bằng phạm vi mới. | README, nội dung PR cập nhật cùng lượt push. |
| Xác nhận kiểm tay | Ghi theo lời Trang: đã rà bản trước và sẽ rà thêm phần đồng bộ mới; không ghi đã tự rà bản cuối khi chưa có xác nhận. | docs/ai-usage.md, checklist, provenance fixture. |

## 3. Các lỗi vòng trước vẫn được giữ

- Route sản phẩm chỉ nhận một segment; chặn path traversal, origin ngoài local.
- Body rỗng trả 400, quá lớn 413; thông báo HTTP được giữ, runtime không lộ body provider/key.
- Log chỉ tên loại ngoại lệ, xử lý cổng sai/bận, lock quanh tracing.
- Cảnh báo stale đúng thời điểm; profile Chrome QA được dọn; CSS nhiều dòng và không thêm dependency.
- Giữ các dòng khai báo AI chung và nội dung của Tuyên/Vinh/Yến.

## 4. Kiểm chứng

| Lệnh/phần | Kết quả |
|---|---|
| python -m unittest discover -s tests -q | 22 test UI/HTTP/adapter đạt |
| python -m unittest discover -s codebase -q | 19 test backend main đạt |
| node tests/browser_smoke.mjs | 20 nhóm kiểm tra đạt |
| python run.py check | 25 câu, 4 metric; không thấy vấn đề |
| python run.py, MODEL_PROVIDER=fake | Web catalog/review chạy ở local; fake insufficient, stats/nguồn từ main |
| git diff origin/main -- backend/framework/eval/cost/spec | Không có chỉnh sửa so với main trong các file được bảo vệ |

Mẫu SP01 ở chế độ fake: total=20, filtered_noise=13, noise_pct=65, kept_clean=7; không có rủi ro, popup đọc 20 nguồn từ reviews_by_id.
Review toàn nhiễu: không gọi model. Không tự áp ngưỡng 3 vì code main quyết định điều kiện thiếu dữ liệu.
Rủi ro/no_clear_risk và usage API trong test dùng stub/fixture, không phải token API thật. Không sửa hoặc chạy đè eval/run-1.csv, run-2.csv hay trace đã có.

## 5. Phạm vi còn lại

- Cần Trang rà lại phần đồng bộ cuối như đã xác nhận sẽ làm, rồi trưởng nhóm approve/merge PR.
- Không xác minh API live ở vòng UI này; không kết luận hoàn thành issue #8.
- Các thay đổi personas/checklist/test issue #8 đang ở nhánh làm việc riêng, không được đưa vào PR #18.

## 6. Tóm tắt cho mô tả PR

~~~markdown
Đồng bộ UI issue #4 theo main sau PR #20:
- Giữ nguyên agent.py/tools.py/ai.py; xóa helper và workflow fake/lọc riêng.
- Chọn catalog SP01–SP03 hoặc dán raw review qua answer(text), không cần URL/sao.
- Payload Shopee qua analyze_review_payload; không tự crawl Apify.
- Render đúng stats, flags list[str], anomalies dict, reviews_by_id và fake insufficient.
- Sửa hasResult/clear/edit, viền lỗi input, bổ sung DEMO03 và giữ README main.
Validation: 22 test UI + 19 test backend + 20 nhóm Chrome QA và run.py check đạt.
Báo cáo: docs/pr-18-review-fixes.md. Test API dùng stub, chưa xác minh live ở lượt sửa UI.
Refs #4.
~~~
