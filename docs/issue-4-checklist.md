# Issue #4 — UI đồng bộ backend Shopee

Theo yêu cầu người dùng, UI đã được chuyển từ adapter fake tự dựng sang gọi trực tiếp backend Tuyên tại main commit 4b1f050.
Giữ nhánh feat/issue-4-ui-demo và cập nhật vào PR #18; không sửa agent.py, ai.py, tools.py, metric, benchmark hoặc chuẩn đạt.

## Đối chiếu hành vi hiện tại

| Phần | Hiện trạng |
|---|---|
| Nhập sản phẩm | Link listing Shopee; hoặc link + review có số sao |
| Chọn mẫu | Fixture synthetic chỉ cho chế độ dán; không crawl URL minh họa |
| Kết quả | Dùng status risks/no_clear_risk/insufficient và title/summary/citations từ backend |
| Nguồn Rxx | Popup text/rating/date/variant từ citation object backend; không dùng mã preview do UI tự gán |
| Fake | Trả insufficient đúng backend; không tự dựng 3 thẻ |
| Thiếu dữ liệu | Theo trạng thái backend, bỏ ngưỡng sạch 2 của UI cũ |
| Ngoài phạm vi | Chặn URL ngoài Shopee; không tuyên bố phát hiện mọi yêu cầu ngoài phạm vi trong review |
| Định lượng | Hiện review_count và độ phủ được trả. **Backend chưa có số review nhiễu/sạch nên chưa đủ phần cờ định lượng của checklist gốc**; không tự bịa hoặc hiện 0 |
| Tracing | begin/end quanh lời gọi thật; mode dán không gọi crawler nên tool_calls=0 là bình thường |
| Lệnh | python run.py mở web; REVIEW_LENS_MODE=cli gọi answer(link) nguyên trạng |

Hợp đồng chi tiết: docs/ui-ai-contract-proposal.md. Một lần phân tích chỉ gọi model một lần, không gọi answer để lấy văn bản rồi gọi analyze_reviews lần nữa.

## Kiểm thử

- 23 test Python: fake đúng trạng thái, backend citations, API schema, source metadata, PII, sao bắt buộc, lỗi cấu hình, luồng link gọi crawler, usage qua OpenAI HTTP stub, nội dung có URL/Rxx không kích hoạt crawler, HTTP 400/413, route sản phẩm, log ngoại lệ, cổng sai và không cho server khác dùng chung cổng UI.
- 18 nhóm kiểm tra browser QA: link/review modes, chọn mẫu, fake không bịa rủi ro, usage, không bịa tỷ lệ nhiễu, popup nguồn và metadata, lỗi mạng, thông báo HTTP 400/403/413/502, cảnh báo dữ liệu cũ và desktop/mobile. Profile tạm được dọn sau kiểm thử.
- Ba thẻ rủi ro/no_clear_risk trong browser QA dùng response fixture riêng của test. Không báo đó là kết quả OpenAI thật.
- Chưa thử live crawler/OpenAI; không có chi phí hoặc token API thật được ghi nhận.
- Không ghi/chấm benchmark, không sửa CSV kết quả hoặc trace đã có.

## Trạng thái hợp đồng và phần chưa triển khai

Theo xác nhận của Trang ngày 27/11/2026, nhóm đã chốt khác biệt hợp đồng MWG/Shopee với Tuyên/Vinh. Backend hiện chưa trả thống kê nhiễu/sạch, chưa nhận trực tiếp mã catalog MWG hoặc review không có số sao trong answer(text). Các khả năng này vẫn cần triển khai nếu nhóm đưa vào luồng chạy; xác nhận chốt hợp đồng không đồng nghĩa code đã hỗ trợ.
Mã backend đã được merge từ main nhưng không bị chỉnh trong phần đồng bộ UI này. Dữ liệu và tài liệu của Vinh/Yến giữ nguyên.

## Review PR #18 và kiểm tay

Đối chiếu từng nhận xét: [pr-18-review-fixes.md](pr-18-review-fixes.md). Ngày 27/11/2026, Trang xác nhận đã kiểm tay code và fixture `ui_demo_data.json`, đồng thời đã chốt khác biệt hợp đồng với Tuyên/Vinh. Ghi nhận theo xác nhận của người phụ trách; chưa có kết quả chạy API/crawler live trong phiên kiểm thử này.
