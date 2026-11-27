# Hợp đồng UI–backend — đồng bộ theo backend Shopee của Tuyên

Trạng thái: cập nhật theo yêu cầu người dùng ngày 27/11/2026; thay cho bản UI nhập review không có số sao trước đây.
Nguồn triển khai: `codebase/agent.py` tại `origin/main` commit `4b1f050`. Không sửa backend, metric hoặc chuẩn đạt để khớp UI.

## 1. Các đường vào hiện được hỗ trợ

| Nguồn | UI gửi gì | Backend được gọi |
|---|---|---|
| Link Shopee | Listing hợp lệ trên shopee.vn | `crawl_shopee_reviews(url)` rồi `analyze_reviews(url, reviews, coverage)` |
| Review đã có | URL listing Shopee + review có số sao 1–5 | `analyze_reviews(url, reviews, coverage)`, không crawl |
| Fixture thử UI | URL minh họa + review synthetic có sao | Cùng hàm analyze_reviews; fake trả insufficient và không sinh rủi ro |

Web dùng trực tiếp hàm có cấu trúc của Tuyên như extension để hiển thị thẻ; không gọi thêm `answer(link)` rồi phân tích lại lần hai. CLI vẫn gọi `answer(text) -> {"output": str}` nguyên trạng.
Không phân tích catalog ĐMX/TGDĐ bằng cách giả rằng đó là listing Shopee. Dữ liệu nguồn của nhóm giữ nguyên trong data/.

## 2. API local của UI

`POST /api/analyze`, Content-Type application/json.

Lấy review từ link:
```json
{"mode": "link", "url": "https://shopee.vn/product/123/456"}
```
URL trên chỉ minh họa hình dạng, không phải listing đã xác minh.

Dán review:
```json
{
  "mode": "reviews",
  "url": "https://shopee.vn/product/123/456",
  "reviews": [
    {"rating_star": 2, "comment": "Tai trái mất kết nối sau một giờ.", "date": "2026-11-01", "variant": "Đen"},
    {"rating_star": 4, "comment": "Pin dùng đủ một buổi."}
  ]
}
```

Trong textarea: mỗi dòng `số sao | nội dung`. UI không tự điền sao còn thiếu. Số sao là điều kiện backend đang yêu cầu để nhận review, không phải bằng chứng tự nó về chất lượng sản phẩm.
Backend hiện nhận tối đa 250 mục, giữ tối đa 50 mục có nội dung mỗi mức sao. UI từ chối comment quá 3.000 ký tự thay vì cắt ngầm; giới hạn HTTP 2 MB.
Email/SĐT trong comment và variant được che bằng cùng helper của backend trước khi gửi model; không mang tên/tài khoản người viết vào payload.

## 3. Phản hồi cho web

```json
{
  "analysis": {
    "ok": true,
    "status": "risks",
    "summary": "Có phản ánh cần kiểm chứng.",
    "review_count": 2,
    "model": "model-do-backend-tra-ve",
    "risks": [{
      "title": "Kết nối",
      "summary": "Có phản ánh tai trái mất kết nối.",
      "severity": "medium",
      "citations": [{
        "id": "R01",
        "rating": 2,
        "text": "Tai trái mất kết nối sau một giờ.",
        "date": "2026-11-01",
        "variant": "Đen",
        "url": "https://shopee.vn/product/123/456"
      }]
    }]
  },
  "sources": [],
  "coverage": {"counts_complete": null},
  "usage": {"model_calls": 1, "tool_calls": 0, "tokens_in": 0, "tokens_out": 0, "models": []},
  "mock": false,
  "origin": "backend"
}
```

Đây là minh họa schema, không phải số liệu model thật. Trong phản hồi thực tế, sources được trích từ chính citation objects do backend trả; usage lấy từ tracing, không điền số mẫu.
UI hiển thị nguyên thứ tự rủi ro của backend, tối đa 3; dùng title/summary và citation object. Không tự xếp hạng lại hay gán mức nguy hiểm riêng. Mã Rxx do backend đánh sau khi nhận các review có sao/nội dung; không lấy mã từ preview textarea để suy ra citation.
Bấm Rxx mở text nguồn, số sao, ngày và biến thể nếu backend có. Text là phần nguồn đã được backend giữ/ẩn thông tin liên hệ, không hứa nguyên vẹn toàn bộ trang review gốc.

## 4. Trạng thái

| Trạng thái | Nguồn | UI |
|---|---|---|
| risks | Backend | Tối đa 3 rủi ro và nguồn |
| no_clear_risk | Backend | Chưa thấy rủi ro rõ ràng; không bảo đảm an toàn |
| insufficient | Backend | Chưa đủ căn cứ hoặc fake; không tự tạo thẻ |
| refused | Kiểm đầu vào UI | URL ngoài Shopee, từ chối tác vụ không hỗ trợ |
| invalid_input | Kiểm đầu vào UI | URL/số sao/schema/giới hạn sai, hướng sửa |
| error | Runtime/mạng/cấu hình | Không có kết quả mới, giữ input và cho thử lại |

Backend Tuyên chưa có thống kê filtered_noise/kept_clean/noise_pct hoặc ngưỡng sạch tối thiểu trong output hiện tại. UI **không dùng lại ngưỡng 2 review sạch** của adapter cũ, không suy status từ hợp đồng tài liệu ngưỡng 3, không bịa số nhiễu bằng 0. Cần phối hợp Tuyên nếu muốn thêm trường định lượng này; chưa sửa backend ở phần việc UI.
Fake của backend trả insufficient dù đã có review văn bản, model=fake và token 0. Không thay bằng rủi ro tạo ở frontend/adapter.
Backend chỉ dẫn rủi ro theo prompt; UI không tuyên bố guard phát hiện mọi kiểu tấn công hoặc backend đã hỗ trợ refused cho mọi yêu cầu ngoài phạm vi.

## 5. Tracing và kiểm thử

App dùng lock quanh tracing.begin/end vì khung có trạng thái toàn cục; giữ log model/tool/token thật của lần gọi. Chế độ dán thường không gọi tool crawler nên tool_calls có thể là 0; không ép số đếm cho giống bản cũ.
UI không trả body lỗi nhà cung cấp/key/prompt ra màn hình. Chưa nhận usage thì ghi chưa có, không ước lượng.
23 test Python và 18 nhóm kiểm tra browser smoke kiểm luồng tích hợp. HTTP OpenAI/crawler được stub trong test; ba thẻ rủi ro trong browser test dùng response fixture ghi rõ là kiểm thử, không phải một lượt AI thật. Chưa xác minh live với credential/nguồn Shopee trong phiên này. App báo lỗi khi cổng đã bị chiếm, không cho hai server dùng chung cổng trên Windows; có thể chọn REVIEW_LENS_PORT=8001 để thử riêng.

Đây là mô tả điểm nối web với backend Shopee hiện có, chưa thay thế `data/CONTRACT.md`. Ngày 27/11/2026, Trang xác nhận đã chốt khác biệt hợp đồng MWG/Shopee với Tuyên/Vinh. Hợp đồng dữ liệu MWG (SP01–SP03, review không có sao, ngưỡng sạch 3) vẫn khác backend thực thi. UI chưa nối catalog MWG, không tự gán sao hoặc đổi URL nguồn MWG thành Shopee. Việc ghi nhận xác nhận không bổ sung các khả năng này vào code.
