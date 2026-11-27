# Hợp đồng dữ liệu & I/O — Nhóm borntobuild (Track D)

> Chốt ở **CP2 (Issue #1)** để cả 4 thành viên làm song song: #2 (Eval/Benchmark), #3 (Agent/Tools), #4 (UI demo) và #5 (Mở rộng dữ liệu CP3).

---

## 1. Cấu trúc dữ liệu review trong `data/`

```text
data/
├── CONTRACT.md                  # Tài liệu hợp đồng này
├── DATA_CARD.md                 # Data card mô tả nguồn, xử lý, giới hạn
├── catalog.json                 # Chỉ mục sản phẩm sẵn có cho tool & UI
└── products/
    ├── sunhouse_shd4035.json    # SP01 — Nồi chiên không dầu Sunhouse 9 lít SHD4035
    ├── airpods_4_mxp63.json     # SP02 — Tai nghe Bluetooth Apple AirPods 4 (MXP63)
    └── ava_plus_q7.json         # SP03 — Pin sạc dự phòng Polymer 20000mAh 10.5W AVA+ Q7
```

### 1.1. Schema `data/catalog.json`

Mảng `products` gồm các bản ghi chỉ mục (dùng cho dropdown UI ở #4 và tra cứu theo mã/tên sản phẩm ở #3):

```json
{
  "version": "cp2-v1",
  "updated_at": "2026-11-27",
  "products": [
    {
      "product_code": "SP01",
      "product_id": "sunhouse_shd4035",
      "product_name": "Nồi chiên không dầu Sunhouse 9 lít SHD4035",
      "category": "Gia dụng bếp",
      "platform": "Điện máy XANH",
      "price_vnd": 2259000,
      "original_price_vnd": 3670000,
      "displayed_rating": 4.9,
      "displayed_five_star_pct": 99.7,
      "total_reviews_displayed": 371,
      "sample_review_count": 20,
      "source_url": "https://www.dienmayxanh.com/noi-chien-khong-dau/sunhouse-shd4035-9-lit/danh-gia",
      "accessed_date": "2026-11-27",
      "file": "data/products/sunhouse_shd4035.json"
    }
  ]
}
```

### 1.2. Schema `data/products/<product_id>.json`

Mỗi file chứa metadata sản phẩm và mảng `reviews` đã ẩn danh hoàn toàn (**không chứa nhãn gán tay** để tránh rò rỉ nhãn vào luồng AI):

```json
{
  "product_code": "SP01",
  "product_id": "sunhouse_shd4035",
  "product_name": "Nồi chiên không dầu Sunhouse 9 lít SHD4035",
  "category": "Gia dụng bếp",
  "platform": "Điện máy XANH",
  "price_vnd": 2259000,
  "original_price_vnd": 3670000,
  "displayed_rating": 4.9,
  "displayed_five_star_pct": 99.7,
  "satisfied_customers_text": "69.8k khách hài lòng",
  "total_reviews_displayed": 371,
  "product_url": "https://www.dienmayxanh.com/noi-chien-khong-dau/sunhouse-shd4035-9-lit",
  "source_url": "https://www.dienmayxanh.com/noi-chien-khong-dau/sunhouse-shd4035-9-lit/danh-gia",
  "accessed_date": "2026-11-27",
  "sampling_rule": "Lấy trọn 20 đánh giá đầu tiên (trang 1, sắp xếp 'Mới nhất'), không chọn lọc",
  "reviews": [
    {
      "id": "R01",
      "text": "Nồi lấy hôm 14/2 dùng được 2 lần sao giờ không sử dụng được nữa",
      "usage_duration": "Đã dùng khoảng 9 tháng",
      "helpful_count": 1,
      "has_images": true,
      "support_replied": true
    }
  ]
}
```

### 1.3. Quy ước mã trích dẫn `[Rxx]` và ẩn danh PII

- Mã đánh giá trong từng sản phẩm là `R01`, `R02`, ..., `R20` (tăng dần theo thứ tự xuất hiện trên trang nguồn). Khi trích dẫn trong prompt, câu thử và câu trả lời cho người dùng, **luôn bọc trong ngoặc vuông dạng `[R01]`**.
- Khi trích dẫn chéo nhiều sản phẩm trong báo cáo bằng chứng (`evidence/`), viết dạng `SP01 [R07]`.
- **Quy tắc ẩn danh bắt buộc:**
  1. Xoá toàn bộ tên tài khoản / họ tên người đánh giá trước khi lưu vào `data/`.
  2. Che mọi số điện thoại, Zalo, email, địa chỉ, mã đơn hàng xuất hiện bên trong nội dung bình luận bằng `[SĐT đã ẩn]` / `[đã ẩn]`.
  3. Không lưu ảnh chứa mặt người, hoá đơn, hoặc thông tin định danh cá nhân.

---

## 2. Quy ước phân loại nhiễu & thông tin thật (dùng chung cho Data Mining và Tool lọc)

| Nhóm lớn | Mã nhãn (`sub_label`) | Định nghĩa kiểm chứng được |
|---|---|---|
| **Nhiễu / không phản ánh chất lượng SP** (`nhieu`) | `nhieu_trong` | Nội dung văn bản trống (`""`) hoặc chỉ có dấu câu/ký tự vô nghĩa (vd `"."`). |
| | `nhieu_khen_chung` | Khen ngắn chung chung (vd `"Tốt"`, `"Sài ổn"`, `"Sản phẩm rất là ok"`) không nêu thuộc tính kỹ thuật, độ bền hay trải nghiệm sử dụng cụ thể. |
| | `nhieu_hoi_dap_rao_ban` | Hỏi chính sách thu cũ/đổi trả, hỏi hướng dẫn cài đặt tính năng, hoặc rao bán/pass lại sản phẩm. |
| | `nhieu_ngoai_chat_luong` | Chỉ phàn nàn/bình luận về yếu tố ngoài chất lượng kỹ thuật sản phẩm: biến động giá/khuyến mãi, thái độ nhân viên, đóng gói/giao hàng, lệch ngày kích hoạt bảo hành, thiếu phụ kiện vốn không có trong hộp, hoặc người mua tự đánh rơi làm hỏng. |
| **Có thông tin chất lượng SP** (`co_thong_tin`) | `co_thong_tin_rui_ro` | Mô tả lỗi, hạn chế, rủi ro chất lượng/độ bền/an toàn/tương thích/trải nghiệm sử dụng cụ thể của bản thân sản phẩm. |
| | `co_thong_tin_tich_cuc` | Mô tả trải nghiệm tốt có ít nhất 1 chi tiết cụ thể về công năng, hiệu năng hoặc sử dụng thực tế (vd dễ dùng, ít hao điện, chiên nhanh, pin lâu, không nóng). |

*Lưu ý cho giai đoạn mở rộng CP3 (Shopee/Tiki/Lazada):* giữ nguyên 2 nhóm lớn (`nhieu` / `co_thong_tin`) và bổ sung các nhãn con đặc trưng sàn mở nếu xuất hiện (vd `nhieu_nhan_xu`, `nhieu_chua_dung`, `nhieu_lap_bat_thuong`).

---

## 3. Hợp đồng `input` / `output` của `answer(text)` trong `codebase/agent.py`

Hợp đồng tuân thủ tuyệt đối khung repo (`run.py`, `eval/run_eval.py`, `cost/simulate.py`):

```python
def answer(text: str) -> dict:
    ...
    return {
        "output": "...",       # BẮT BUỘC (str) — dùng cho CLI, eval, simulate
        "structured": {...},   # TÙY CHỌN (dict) — dùng cho UI #4 hiển thị thẻ rủi ro & đối chiếu [Rxx]
    }
```

### 3.1. Các dạng `input` (`text: str`) được hỗ trợ

1. **Theo mã hoặc tên sản phẩm có sẵn trong `data/catalog.json`:**
   - Ví dụ: `"SP01"`, `"sunhouse_shd4035"`, hoặc `"Kiểm tra rủi ro Nồi chiên không dầu Sunhouse 9 lít SHD4035"`.
   - Tool tra `data/catalog.json` → nạp toàn bộ review gắn mã `[R01]..[Rxx]` từ `data/products/<product_id>.json`.
2. **Dán trực tiếp tập review (raw text):**
   - Người dùng dán văn bản chứa nhiều đánh giá (mỗi dòng 1 đánh giá, có sẵn `[R01]` hoặc chưa có mã).
   - Tool tách dòng, chuẩn hoá và gắn mã `[R01], [R02]...` trước khi lọc nhiễu.
3. **Trường hợp biên (lớp 1–4, G10):**
   - Tập review quá ít dữ liệu sạch (`< 3` review sau lọc nhiễu) → trả trạng thái `insufficient_data`, **không bịa rủi ro**.
   - Yêu cầu ngoài phạm vi / tấn công (ép khẳng định *"shop lừa đảo/seeding"*, hỏi tư vấn y tế/pháp lý, hoặc prompt injection giấu trong nội dung review) → từ chối đúng phần ngoài phạm vi, vẫn giữ nguyên ngôn ngữ trung lập dựa trên dấu hiệu định lượng.

### 3.2. Cấu trúc chuẩn của chuỗi `"output"`

Để người mua đọc dưới 1 phút và người chấm `eval` (#2) kiểm chứng nhất quán, `"output"` gồm 4 khối ngắn gọn:

```text
## 1. Tóm tắt lọc nhiễu & cờ bất thường
- Sản phẩm: <tên sản phẩm hoặc "Tập review người dùng dán">
- Tổng review đầu vào: <N> | Đã lọc nhiễu: <K> (<%>) | Review sạch giữ lại: <M>
- Phân nhóm nhiễu: <trống / khen chung / hỏi đáp-rao bán / ngoài chất lượng SP / lặp bất thường>
- Cờ bất thường (định lượng): <nêu dấu hiệu số liệu trung lập, vd "Hiển thị 4.9/5 (99.9% 5★) nhưng 14/20 review mới nhất nêu rủi ro sản phẩm" — hoặc "Không phát hiện bất thường rõ rệt">

## 2. Tối đa 3 rủi ro lớn nhất (kèm trích dẫn gốc)
1. <Tên rủi ro 1> (<số review nhắc tới>): <mô tả 1 câu> — Trích dẫn: [R07] "<đoạn trích ngắn nguyên văn>", [R01] "<...>"
2. <Tên rủi ro 2> ...
3. <Tên rủi ro 3> ...
(Hoặc khi < 3 review sạch: "Chưa đủ dữ liệu sạch để kết luận rủi ro (<M>/3 review tối thiểu). Cần bổ sung thêm đánh giá có mô tả trải nghiệm thực tế.")

## 3. Lưu ý kiểm chứng
- Hệ thống chỉ tóm tắt rủi ro từ dữ liệu đầu vào và gắn cờ dấu hiệu định lượng, không kết luận gian lận/seeding. Người mua đối chiếu nguyên văn các mã [Rxx] trước khi quyết định.
```

### 3.3. Cấu trúc khoá tùy chọn `"structured"` (cho UI #4)

```json
{
  "status": "ok | insufficient_data | refused",
  "product_name": "string",
  "stats": {
    "total": 20,
    "filtered_noise": 13,
    "noise_pct": 65.0,
    "kept_clean": 7,
    "noise_breakdown": {
      "nhieu_trong": 7,
      "nhieu_khen_chung": 5,
      "nhieu_hoi_dap_rao_ban": 0,
      "nhieu_ngoai_chat_luong": 1
    }
  },
  "flags": [
    "Điểm hiển thị 4.9/5 (99.7% 5★) nhưng có 4/20 review mới nhất phản ánh lỗi sản phẩm."
  ],
  "risks": [
    {
      "rank": 1,
      "title": "Bong sơn đáy nồi và rỉ sét sau thời gian ngắn",
      "summary": "Người mua phản ánh đáy nồi bong sơn và có dấu hiệu rỉ sét sau 2 tháng dùng.",
      "citations": ["R07"],
      "quotes": ["Sài được có 2 tháng bong sơn ở đáy nồi, mấy chỗ bong có dấu hiệu rỉ set"]
    }
  ],
  "reviews_by_id": {
    "R07": "Sài được có 2 tháng bong sơn ở đáy nồi, mấy chỗ bong có dấu hiệu rỉ set"
  }
}
```
