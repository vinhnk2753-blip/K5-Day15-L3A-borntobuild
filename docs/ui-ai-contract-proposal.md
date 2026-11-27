# Thống nhất đầu vào/đầu ra V1 — nhập review thủ công

Trạng thái: **Chốt tạm thời theo xác nhận của người dùng ngày 27/11/2026**, dùng làm cơ sở triển khai V1 cho Trang và Tuyên. Chưa ghi nhận xác nhận riêng của Tuyên trong tài liệu này.

V1 dùng cách nhập/dán review thủ công. Theo checklist issue #4 người dùng yêu cầu bổ sung, UI còn cho chọn sản phẩm **minh họa tự dựng** nạp sẵn; ghi rõ không phải dữ liệu crawl. Nhập link, tự lấy review, tải file và danh mục crawl thật để dành sau.

- Trang: giao diện nhập liệu và hiển thị kết quả.
- Tuyên: chuẩn hóa dữ liệu, luồng AI, công cụ lọc nhiễu và hậu kiểm trích dẫn.
- Phạm vi: review của **một sản phẩm** → tối đa **3 rủi ro có dẫn chứng**. Người mua tự kiểm chứng và quyết định.

**Ranh giới issue #4:** đây là hợp đồng để tích hợp, không phải xác nhận backend issue #3 đã triển khai. `agent.py`, `ai.py`, `tools.py` giữ nguyên bản Git ban đầu. UI dùng `codebase/ui_demo.py` để dựng kết quả minh họa sau khi gọi backend fake; adapter không tham gia eval/simulate.

## 1. Đầu vào trên UI

- Tên sản phẩm: tùy chọn.
- Nội dung review: dán văn bản, **mỗi dòng một review**.
- UI bỏ dòng trống, gán mã `R01`, `R02`… theo thứ tự; không đổi mã trong cùng lần phân tích.
- Bản đầu chưa nhận link sản phẩm, ảnh hoặc file. Mỗi lần chỉ phân tích một sản phẩm.
- Số sao là tùy chọn; giao diện dán văn bản mặc định truyền `null`.
- Người dùng có thể sửa đầu vào rồi phân tích lại thành một lần mới.

## 2. Cấu trúc đầu vào chuẩn

```json
{
  "product_name": "Tai nghe Bluetooth X",
  "reviews": [
    {
      "id": "R01",
      "text": "Dùng khoảng một giờ thì tai trái mất kết nối.",
      "rating": 2
    },
    {
      "id": "R02",
      "text": "Giao nhanh, đóng gói đẹp, chưa dùng thử.",
      "rating": null
    }
  ]
}
```

| Trường | Kiểu | Quy ước |
|---|---|---|
| `product_name` | string | Có thể là chuỗi rỗng |
| `reviews` | array | Ít nhất một review hợp lệ |
| `reviews[].id` | string | Duy nhất trong lần phân tích, dạng `R01`, `R02`…; từ 100 dùng `R100` |
| `reviews[].text` | string | Không rỗng; giữ nội dung gốc sau khi bỏ khoảng trắng đầu/cuối |
| `reviews[].rating` | integer hoặc null | Số nguyên 1–5, hoặc `null` nếu không có |

Không yêu cầu tên người đánh giá, tài khoản, số điện thoại hoặc thông tin định danh. Không tự suy đoán số sao từ nội dung review.

## 3. Cấu trúc đầu ra chuẩn

Ví dụ dưới đây chỉ minh họa cấu trúc, không phải kết quả đo thực tế.

```json
{
  "status": "ok",
  "message": "Tìm thấy 1 rủi ro trong tập đánh giá được cung cấp.",
  "risks": [
    {
      "title": "Mất kết nối khi sử dụng",
      "description": "Có phản ánh tai trái mất kết nối sau khoảng một giờ sử dụng.",
      "evidence": [
        {
          "review_id": "R01",
          "quote": "Dùng khoảng một giờ thì tai trái mất kết nối."
        }
      ]
    }
  ],
  "review_flags": [
    {
      "review_id": "R02",
      "reason": "Chỉ nói về giao hàng và chưa sử dụng sản phẩm."
    }
  ],
  "summary": {
    "total_reviews": 2,
    "flagged_reviews": 1
  }
}
```

Các trường trên luôn có mặt. `risks` và `review_flags` có thể là danh sách rỗng. `summary` do code tính: tổng số review hợp lệ và số mã review được gắn cờ duy nhất; không để model tự đếm.

Bổ sung cho issue #4: summary có `flagged_percent`, `clean_reviews`, `min_clean_reviews`, `signal_counts` (duplicate, not_used, shipping_only, instruction, other). Mỗi review gắn cờ được tính một lần vào một nhóm; % = số mã bị gắn cờ / tổng review hợp lệ. Ngưỡng G10 bản demo là **2 review sạch khác nội dung**, tự chọn và chưa hiệu chỉnh trên dữ liệu thật. “Sạch” chỉ là có dấu hiệu trải nghiệm, không bị gắn cờ theo heuristic; không bảo đảm review thật. Quá ít thì không gọi model, trả `insufficient_evidence` và risks rỗng.

Ví dụ JSON ở trên chỉ minh họa hình dạng một thẻ, không bảo đảm đủ review sạch theo ngưỡng mới. Có thể chọn DEMO01 trong `codebase/ui_demo_data.json` để thử luồng UI thành công.

### Trạng thái và hành vi UI

| `status` | Khi nào dùng | UI hiển thị |
|---|---|---|
| `ok` | Có ít nhất một rủi ro có dẫn chứng hợp lệ | 1–3 thẻ rủi ro, trích dẫn và mã review nguồn |
| `insufficient_evidence` | Dữ liệu ít thông tin, chỉ có nhiễu hoặc chưa đủ căn cứ để phân tích | Lý do và gợi ý bổ sung review; `risks: []` |
| `no_risk_found` | Có nội dung trải nghiệm sản phẩm nhưng chưa tìm thấy rủi ro có căn cứ | “Chưa tìm thấy rủi ro trong tập đánh giá này”; `risks: []` |
| `invalid_input` | Đầu vào trống, sai cấu trúc, trùng mã hoặc sai kiểu dữ liệu | Thông báo cách sửa; `risks: []` |
| `out_of_scope` | Toàn bộ tập chỉ là các yêu cầu rõ ràng ngoài nhiệm vụ đọc review | Từ chối mua hộ/gửi tin/lộ bí mật/kết tội shop; `risks: []`; không gọi model |
| `error` | Lỗi kỹ thuật, API hoặc đầu ra model không hợp lệ sau hậu kiểm | Thông báo ngắn và cho thử lại; `risks: []` |

Với đầu vào không thể chuẩn hóa, `summary` dùng hai giá trị 0. Với lỗi xử lý sau khi đã chuẩn hóa, giữ tổng số review hợp lệ và chỉ ghi số cờ đã kiểm chứng; chưa có cờ hợp lệ thì dùng 0. Không hiển thị API key, prompt hệ thống hoặc traceback trong thông báo UI.

## 4. Quy tắc kết quả và hậu kiểm

1. `ok` phải có 1–3 rủi ro, mỗi rủi ro có ít nhất một dẫn chứng hợp lệ. Thứ tự trong `risks` là thứ tự UI hiển thị.
2. Mọi `review_id` trong dẫn chứng hoặc cờ phải tồn tại trong đầu vào đã chuẩn hóa.
3. `quote` phải là đoạn nguyên văn liên tục trong `text` của review tương ứng. Không được diễn giải rồi đặt trong dấu trích dẫn.
4. Không có căn cứ thì không tạo rủi ro. Nếu hậu kiểm không còn dẫn chứng hợp lệ, trả `insufficient_evidence` hoặc `error` theo nguyên nhân; không trả `ok` rỗng.
5. Review là dữ liệu: bỏ qua chỉ dẫn tấn công được chèn trong nội dung review.
6. Cờ nhiễu/bất thường không phải kết luận “review giả”. Một review được gắn cờ vẫn có thể chứa thông tin sản phẩm hữu ích.
7. Không kết luận sản phẩm an toàn, tốt tuyệt đối hoặc yêu cầu người dùng mua/tránh chỉ từ tập review. Không thêm phần trăm tin cậy khi chưa có cách đo.
8. UI cho mở/xem nguyên văn review theo mã trích dẫn; không chỉ hiện mã mà thiếu nguồn đối chiếu.

## 5. Giữ tương thích với khung lab

Giữ hợp đồng hiện có, không sửa các file khung bị cấm trong `AGENTS.md`:

```python
answer(text: str) -> {"output": str}
```

- UI mã hóa đầu vào thành chuỗi JSON; adapter `adapt_answer(text, answer)` gọi backend `answer(text)` một lần nếu đủ dữ liệu đúng phạm vi. Fake output của backend khung chưa có schema này nên adapter dựng JSON mô phỏng để thử UI, không giả làm kết quả model thật.
- Adapter trả thêm `sources` ngoài `output` để UI mở review nguyên văn của đúng lần chạy. Backend `answer()` và khung eval/simulate giữ nguyên; khi nối thật cần backend trả JSON theo hợp đồng và adapter chỉ hậu kiểm/hiển thị.
- `output` là chuỗi JSON hợp lệ theo mục 3, không bọc khối Markdown và không thêm lời dẫn ngoài JSON.
- UI giải mã `output` để hiển thị. Nếu giải mã thất bại, UI báo lỗi có thể thử lại.
- Để hỗ trợ dòng lệnh và benchmark, `answer()` cũng nhận văn bản thường: mỗi dòng không trống là một review, tự gán mã, `rating: null`, tên sản phẩm rỗng.
- Nếu đầu vào bắt đầu bằng `{` hoặc `[` sau khi bỏ khoảng trắng đầu, xử lý như JSON; JSON sai cấu trúc trả `invalid_input`, không âm thầm coi là review văn bản.
- Giữ `python run.py` chạy được; giữ bộ `eval` và `simulate` gọi cùng hàm `answer()`.
- Lời gọi model giữ `@model_call`, công cụ giữ `@tool`; token lấy từ `usage` thật theo hợp đồng repo.

## 6. Trách nhiệm và phối hợp

| Trang | Tuyên |
|---|---|
| Form tên sản phẩm và vùng dán review | Chuẩn hóa và kiểm đầu vào tại backend |
| Bỏ dòng trống, gán mã để xem trước | Giữ nguyên mã đầu vào hợp lệ; không tự đổi mã gây lệch nguồn |
| Hiển thị trạng thái đang xử lý, kết quả và lỗi | Phân loại/lọc nhiễu, rút rủi ro, hậu kiểm dẫn chứng |
| Hiện nguồn theo mã review, cho sửa và chạy lại | Trả đúng cấu trúc và trạng thái đã thống nhất |
| Dùng JSON mẫu để làm UI khi AI chưa sẵn sàng | Cung cấp mẫu đầu ra cho các trạng thái để tích hợp |

Trang kiểm đầu vào giúp người dùng sửa sớm; Tuyên vẫn kiểm lại vì `eval`/`simulate` có thể gọi trực tiếp mà không qua UI.

## 7. Các trường hợp cần thử khi tích hợp

- Review có phản ánh lỗi → `ok`, tối đa 3 rủi ro và xem được nguồn.
- Chỉ khen giao hàng/chưa sử dụng → `insufficient_evidence`.
- Có trải nghiệm sản phẩm nhưng không phản ánh rủi ro → `no_risk_found`.
- Đầu vào trống, trùng mã, rating sai hoặc JSON hỏng → `invalid_input`.
- Review chứa chỉ dẫn “bỏ qua yêu cầu…” → không làm thay đổi hợp đồng hay tiết lộ prompt.
- Model bịa mã/trích dẫn → hậu kiểm chặn, không hiển thị thành rủi ro hợp lệ.
- API lỗi hoặc trả dữ liệu sai định dạng → báo lỗi, có thể thử lại.
- Người dùng sửa review và phân tích lại → kết quả chỉ thuộc lần chạy mới.

## 8. Phần đã chốt và việc cần bổ sung khi triển khai

- [x] V1 nhập review thủ công: mỗi dòng một review, một sản phẩm mỗi lần phân tích.
- [x] Cấu trúc đầu vào và đầu ra ở mục 2–3.
- [x] Quy tắc trạng thái và hậu kiểm ở mục 3–4.
- [x] Cách tích hợp qua `answer(text)` ở mục 5.
- [x] Giới hạn kỹ thuật cho bản mô phỏng CP2: tối đa 100 review, 4.000 ký tự mỗi review, 50.000 ký tự toàn bộ chuỗi đầu vào; vượt giới hạn trả `invalid_input`, không cắt ngầm. Đây là giới hạn tự chọn cho demo, cần đo lại khi chọn model thật.
- [x] Bản chạy CP2 dùng web local trong `codebase/app.py`, có CLI tùy chọn; `python run.py` giữ nguyên, không sửa file khung. Nguồn trích dẫn mở trong dialog bằng văn bản thuần.
- [ ] Người phụ trách issue #3 đồng bộ spec §4–§6 và backend. Không sửa spec hoặc metric trong phần việc UI issue #4.

Xác nhận phạm vi V1: người dùng trong cuộc trao đổi ngày 27/11/2026.

Xác nhận riêng của Tuyên / điều chỉnh sau trao đổi: chưa ghi nhận.
