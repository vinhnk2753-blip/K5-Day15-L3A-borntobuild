# Hợp đồng UI với backend main PR #20

Cập nhật 28/11/2026 theo main commit 266e007. Đây là mô tả adapter hiển thị, không định nghĩa một workflow AI khác.

## Điểm vào

Web POST /api/analyze:
- {"mode":"catalog","product_id":"SP01"} → agent.answer("SP01"). SP01–SP03 lấy từ data/catalog.json.
- {"mode":"reviews","text":"[R01] Nội dung review...\n[R02] Nội dung khác..."} → agent.answer(text) nguyên văn. Không bắt buộc URL hoặc số sao.
- {"mode":"payload","payload":{"product":{"url":"https://shopee.vn/product/123/456"},"reviews":[{"rating_star":2,"comment":"Pin yếu sau khi dùng."}]}} → agent.analyze_review_payload(payload). API dành cho payload đã có, không crawl link.

UI có hai chế độ catalog/dán review; chọn DEMO01–DEMO03 nạp văn bản synthetic rồi gọi answer(text).
Giới hạn nhập UI: tối đa 250 dòng, 3.000 ký tự/dòng và body 2 MB. Không tự gán số sao, không gán URL Shopee cho review MWG.
Bare URL nhận đúng thông báo chưa hỗ trợ crawl từ backend, không tự gọi Apify.

## Đầu ra

Backend trả {"output": str, "structured": dict}. UI không parse output như JSON.
Khi backend chỉ trả output hướng dẫn (không có structured), UI hiện invalid_input cùng nguyên thông báo; không tạo rủi ro.

Các trường structured được giữ nguyên:
- status: risks | no_clear_risk | insufficient; summary, product_name, product_url, model.
- stats: total, filtered_noise, noise_pct, kept_clean, noise_breakdown, pii_redacted_review_count; có thêm alias/source của backend.
- flags: list[str] ghi chú anomaly.
- anomalies: dict có review_count, duplicate_count, duplicate_rate, duplicate_clusters, flags.
- reviews_by_id: {Rxx: nguyên văn đã che PII}, gồm cả review bị lọc.
- risks: tối đa 3 object có title, summary, severity, citations là source object; backend hậu kiểm ID.

UI không cần input_total, excluded_limit hoặc min_clean_reviews; không tự áp ngưỡng 3.
Theo code main hiện tại: khi không còn review sạch, dừng trước model; các trường hợp thiếu căn cứ khác theo quyết định/hậu kiểm backend.

Adapter bọc analysis, sources, mock; sources được gom từ reviews_by_id và lấy metadata nếu citation có rating/date/variant.
Popup luôn dùng text từ reviews_by_id, không suy mã từ preview và không tự sinh quote. Nguồn không có rating được ghi rõ, không hiện null sao.
Cờ lặp lấy ID từ anomalies.duplicate_clusters; tỷ lệ duplicate_rate là phân số, đổi thành phần trăm khi hiển thị; noise_pct đã là phần trăm.
PII count lấy từ stats.pii_redacted_review_count; UI không tự lọc lại nguồn.

## Chế độ giả và tracing

Đọc ai.MODEL_PROVIDER/ai.MODEL_NAME qua module ai tại thời điểm sử dụng.
MODEL_PROVIDER=fake: backend trả insufficient, không có rủi ro; UI giữ nguyên, không tạo 3 thẻ giả.
Review có nội dung sạch có thể gọi model fake (usage token 0); review chỉ nhiễu không gọi model.
Tracing begin/end được khóa ở web; model/tool/token đọc từ khung. Theo backend main, đường catalog/raw review thường có 3 tool, payload có 2 tool; không ép theo số đếm bản cũ.

## UX và lỗi

Không coi error/invalid_input/refused là kết quả thành công để bật cảnh báo stale. Clear reset hasResult; edit focus textarea ở chế độ dán và selector ở chế độ catalog.
HTTP 400/403/413/502 giữ message máy chủ; lỗi runtime không hiện thống kê/rủi ro sơ bộ và vẫn giữ input.
URL ngoài Shopee ở payload được từ chối; review văn bản không bị buộc thuộc Shopee.
CSS invalid áp dụng input, select và textarea. Không thêm dependency ngoài stdlib.

## Kiểm chứng

22 test UI/adapter/HTTP và 19 test backend main đạt; 20 nhóm Chrome QA đạt; python run.py check đạt.
Rủi ro/no_clear_risk kiểm qua model/HTTP stub và response fixture trong QA, không phải lượt API thật.
Backend agent.py/tools.py/ai.py và dữ liệu/metric/eval/trace hiện có giữ nguyên main; đã xóa review_input.py/review_signals.py và các test riêng cho workflow cũ.
