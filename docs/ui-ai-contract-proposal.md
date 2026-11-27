# Hợp đồng UI / answer(text) — bản hoàn thiện CP2

Web, CLI và backend dùng chung luồng; không có bộ sinh kết quả riêng ở UI.

## 1. Đầu vào

Web POST /api/analyze với một trong hai object:

~~~json
{"mode":"link","url":"https://shopee.vn/product/123/456"}
~~~

~~~json
{"mode":"reviews","url":"https://shopee.vn/product/123/456","reviews":[
  {"rating_star":2,"comment":"Tai trái mất kết nối."},
  {"rating_star":2,"comment":"Pin nhanh hết."},
  {"rating_star":3,"comment":"Đeo đau tai."}
]}
~~~

Adapter serialize object sang chuỗi JSON và gọi agent.answer(text) đúng một lần.
answer cũng tiếp tục nhận URL trong văn bản để CLI/eval gọi; không tìm URL bên trong nội dung JSON review rồi tự crawl.

- Chỉ URL listing trên shopee.vn; URL ngoài phạm vi bị từ chối.
- Mode reviews không crawl; mode link gọi crawler một lần rồi phân tích.
- Tối đa 250 review, mỗi comment 3.000 ký tự; số sao nguyên 1–5 bắt buộc, không tự gán.
- Mỗi mức sao xét tối đa 50; số ngoài giới hạn được báo riêng, không coi là nhiễu.
- Web dán dạng mỗi dòng: số sao | nội dung. Ký hiệu [R01] trong nội dung được giữ, không bị đoán là JSON.
- Chỉ chuyển các trường sao/nội dung/ngày/biến thể, che email/SĐT trước phân tích.
- URL https://shopee.vn/product/1/1 là minh họa synthetic; chỉ dùng mode reviews, không crawl.

## 2. Điểm nối và đầu ra

~~~python
answer(text) -> {
    "output": str,
    "structured": analysis,
    "coverage": dict,
    "input_review_count": int,
}
~~~

output luôn là str cho khung eval/simulate. structured là khóa bổ sung; không parse output như JSON, không phân tích hai lần.
analyze_reviews(url, reviews, coverage) tiếp tục tồn tại cho extension và được answer gọi nội bộ.

analysis có:
- status: risks | no_clear_risk | insufficient.
- summary, model, mock, review_count, product_url.
- stats: input_total, total, excluded_limit, filtered_noise, kept_clean, noise_pct, noise_breakdown, min_clean_reviews, method.
- flags: danh sách {kind, label, citations: [source]}, duplicate_of nếu là nội dung lặp.
- anomalies: chuỗi trung lập kèm số đếm trên mẫu nhận được.
- risks: tối đa 3 object {title, summary, severity, citations: [source]}.

source có id, rating, text, date, variant, url. ID gán theo thứ tự các review được xét, trước khi loại nhiễu, nên có thể có khoảng trống giữa các nguồn rủi ro.
Text là nội dung đã che liên hệ và nằm trong giới hạn, không phải cam kết giữ mọi dữ liệu từ trang nguồn. UI hiển thị nguyên văn text này.

Response web bọc analysis, sources (gom từ cả risks và flags), coverage, input_review_count, mock, usage và origin.
usage lấy từ tracing: model_calls, tool_calls, tokens_in, tokens_out, models; không tự ước lượng token.

## 3. Quy tắc định lượng

Một lần gọi @tool quantify_review_signals trên nguồn được xét. Mỗi review bị loại thuộc tối đa một loại, theo thứ tự:
1. Trống/chỉ dấu câu.
2. Trùng nội dung sau chuẩn hóa Unicode, chữ thường, dấu câu và khoảng trắng (giữ bản đầu).
3. Nói nhận xu/nhận thưởng.
4. Nói chưa dùng/chưa sử dụng/chưa trải nghiệm.
5. Chỉ nói giao hàng/dịch vụ, không có cụm từ thuộc tính sản phẩm.
6. Khen chung theo mẫu ngắn.

So khớp cụm từ có ranh giới từ để tránh pin trong shipping, ship trong flagship; lời xin lỗi không được coi là lỗi sản phẩm.
Review không khớp quy tắc được giữ, chưa có nghĩa là đáng tin hoặc đã xác minh có giá trị ngữ nghĩa. Đây là quy tắc prototype, có thể nhận nhầm; flags có nguồn để người dùng đối chiếu.
total = filtered_noise + kept_clean; input_total = total + excluded_limit.
noise_pct = filtered_noise / total * 100, làm tròn 1 chữ số; mẫu rỗng trả 0 kèm trạng thái insufficient.
Nội dung lặp là dấu hiệu trên mẫu, không đủ để kết luận seeding/gian lận. Không dùng điểm sao để tự suy ra rủi ro.

## 4. G10 và chế độ giả

Dưới 3 review giữ lại → insufficient, risks rỗng, không gọi model, nhưng có thống kê/nguồn cờ.
Đủ dữ liệu → call_model đúng một lần. Nếu model=fake, backend dựng tối đa 3 rủi ro minh họa theo cụm từ phản ánh vấn đề trong chính input, có kiểm phủ định đơn giản.
Không tra cứu nguyên input của benchmark, không ép mọi input thành 3 rủi ro, không dùng dữ liệu mẫu làm bằng chứng pain thật.
Input tích cực không có cụm từ vấn đề → no_clear_risk. Đây không phải bảo đảm an toàn.

Demo tai nghe synthetic: 4 review → loại 1 (25%), giữ 3 → 3 rủi ro có nguồn R01/R03/R04.
Tracing: 1 model fake, 1 tool định lượng, token 0. Mẫu thiếu dữ liệu: 0 model, 1 tool.
Mode link có thêm 1 tool crawler; fake model không đồng nghĩa crawler giả, vì vậy demo không cần mạng dùng mode reviews.
Giao diện ghi rõ giả lập, chưa gọi AI thật. Token 0 không dùng để dự báo chi phí hoặc chất lượng model thật.

## 5. Trạng thái và lỗi

- risks: tối đa 3 rủi ro và nguồn đối chiếu.
- no_clear_risk: chưa thấy rủi ro theo dữ liệu/quy tắc hiện tại.
- insufficient: chưa đủ 3 review giữ lại hoặc không xác thực được model.
- refused: validation web nhận URL ngoài Shopee.
- invalid_input: số sao/schema/URL/giới hạn sai; HTTP 400/403/413 giữ thông báo máy chủ.
- error: runtime/mạng/cấu hình; giữ input, không gắn thống kê/cờ hoặc rủi ro sơ bộ vào kết quả lỗi.

34 test Python và 21 nhóm browser QA kiểm luồng qua answer, quy tắc, G10, rủi ro giả có nguồn, positive input, usage, lỗi và responsive.
OpenAI/crawler trong kiểm thử dùng stub, chưa xác minh live. Không sửa chuẩn đạt, benchmark hoặc metric.
Bộ MWG trong data/CONTRACT.md vẫn chưa được nối catalog vào backend Shopee; ngưỡng G10 mới thống nhất là 3. Xác nhận nhóm chốt hợp đồng đã được Trang cung cấp ngày 27/11/2026.
