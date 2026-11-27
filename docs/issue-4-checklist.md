# Issue #4 — UI đồng bộ main sau PR #20

Bản ngày 28/11/2026, base main 266e007. Thay thế checklist demo backend riêng trước đó theo yêu cầu review của trưởng nhóm.

## Đã triển khai

- [x] Merge origin/main, giải quyết xung đột bằng backend chính thức.
- [x] agent.py, tools.py, ai.py giống nguyên main; không thêm/sửa bộ lọc hoặc fake.
- [x] Xóa review_input.py, review_signals.py và test riêng cho các helper đó.
- [x] Chọn catalog thật SP01–SP03 → answer(code).
- [x] Dán review nguyên văn, không cần sao/URL → answer(text).
- [x] Chọn fixture synthetic → answer(text), DEMO03 có ít nhất 3 review.
- [x] API payload Shopee gọi analyze_review_payload(payload), không gọi crawler.
- [x] Render stats schema main, flags list[str], anomalies dict và nguồn reviews_by_id.
- [x] Popup nguyên văn đã che PII cho cả nguồn rủi ro và nhóm lặp; không tự gán sao thiếu.
- [x] Fake hiển thị insufficient theo backend; không tái tạo DoD 3 rủi ro giả của workflow cũ.
- [x] Không đặt ngưỡng G10 riêng; trạng thái theo backend main.
- [x] Giữ tracing/lock, đọc ai qua module, không đóng băng MODEL_PROVIDER/MODEL_NAME.
- [x] hasResult không bật với lỗi, clear reset, edit focus đúng control; CSS invalid áp dụng cả input.
- [x] README giữ nội dung PR #20, hướng dẫn web/CLI được làm rõ.
- [x] Báo cáo và mô tả PR được viết lại theo trạng thái cuối, không lẫn backend cũ.

## Kiểm thử

- 22 test UI/adapter/HTTP.
- 19 test backend main, file codebase/test_agent.py không bị chỉnh.
- 20 nhóm Chrome QA: catalog thật, raw review, fake insufficient, schema, popup, duplicate cluster, lỗi/focus/clear, responsive 1440/390/320.
- python run.py check: 25 câu, 4 metric, không thấy vấn đề.
- Test API dùng stub; chưa xác minh live OpenAI/crawler trong lượt sửa UI này.
- Không chạy lại hay chỉnh CSV/trace kết quả đã merge từ main.

## Kiểm tay

Trang xác nhận đã tự rà bản hiện tại trước vòng đồng bộ này và sẽ rà thêm phần sửa mới (28/11/2026).
Chưa đánh dấu đã kiểm tay code cuối; không tự thay người phụ trách xác nhận. Trưởng nhóm cần review/approve lại PR #18.
Schema chi tiết: [ui-ai-contract-proposal.md](ui-ai-contract-proposal.md). Báo cáo: [pr-18-review-fixes.md](pr-18-review-fixes.md).
