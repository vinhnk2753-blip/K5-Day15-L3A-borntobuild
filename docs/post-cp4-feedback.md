# Tổng hợp góp ý Sau CP4 & kế hoạch cải tiến (`Issue #15`)

> Ghi nhận ngày **28/11/2026** (Sau CP4, trước hạn 23:59). Tài liệu tách bạch rõ **(1) hạng mục đã xử lý & kiểm chứng ngay trong repo** và **(2) hướng đi tiếp cho vòng sau** để giữ trung thực phạm vi. Mọi thay đổi trong repo đều đã ghi changelog tại [`spec.md`](../spec.md) §10; **không sửa** chuẩn "đạt" (`spec.md` §7), `eval/metric_spec.yaml`, `eval/benchmark.csv`, số bằng chứng đã chốt hay kết quả các lượt đã chạy (`run-1`, `run-2`, `simulate-1`).

---

## 1. Góp ý nhận được sau Demo CP4 & buổi dùng thử (`validation/log.md`)

### A. Sản phẩm & UX (nút thắt lớn nhất)
- **Ma sát đầu vào là rào cản sống còn, không phải AI:** `validation/log.md` ghi nhận **2/2** người dùng thử (`U01`, `U02`) đều vướng ngay ở bước nhập liệu — chưa biết bắt đầu từ đâu, nhầm rằng dán link là tự tải review, và ngại copy tay nhiều dòng review.
- **Tín hiệu trạng thái chế độ giả dễ gây hiểu nhầm:** Khi chạy `MODEL_PROVIDER=fake`, giao diện trước đây dùng chung tiêu đề `"Chưa đủ căn cứ phân tích"` với trạng thái `insufficient` thật.
- **Thông điệp cốt lõi (Value Proposition) cần khớp bằng chứng:** Chưa có số đo chứng minh người mua mất 15–30 phút đọc review, nhưng bằng chứng đã chứng minh rõ 2 giá trị mạnh hơn: (1) tách lớp nhiễu **67,3%** (`101/150`) và cho bấm kiểm chứng review gốc 1-click (`4/4` nghi ngờ nhiễu, `3/3` muốn xem gốc) và (2) phát hiện rủi ro ẩn trong review **4–5★** (`3/6 = 50,0%` rủi ro Tiki nằm trong 4–5★ — bấm lọc 1–2★ vẫn sót).

### B. Kỹ thuật AI & độ tin cậy
- **Xử lý dứt điểm `rui_ro_duoc_dan_chung` (78,1% → ≥90%):** Ở `eval/run-2.csv`, 7/32 thẻ rủi ro (`B05`, `B06`, `B15`, `B19`, `B20`, `B22`) trộn review tích cực/đối chứng vào mảng `citations`, và `B17` bỏ quên ý kiến đối chứng `R12`. Cần tách rõ schema `risk_citations` (chỉ bằng chứng lỗi) và `counter_citations` (ý kiến tích cực/đối chứng) rồi chạy `eval/run-3.csv` kiểm chứng bằng số.
- **Nâng cấp `filter_review_noise` cho dữ liệu ngoài mẫu:** `data/DATA_CARD.md` phát hiện ca lọc nhầm đáng giá `SP05 [R23]` (*"Màu bình khác với màu mình đặt, nhưng vì giao hàng nhanh và mình cũng ngại đổi trả nên giữ dùng luôn."*) bị loại nhầm vì có cụm giao hàng. Cần chuyển từ "có từ khoá giao hàng là loại" sang kiểm tra phần mệnh đề còn lại sau khi bỏ mệnh đề giao hàng/đóng gói/giá/cảm ơn.
- **Chống lỗi mạng tạm thời trong `codebase/ai.py`:** `cost/simulate-1.csv` ghi nhận **1/50 phiên** (`S024`, 2%) gặp lỗi HTTP 502/503 từ API trung gian. Cần thêm retry có exponential backoff cho mã tạm thời (`429/502/503/504`).

### C. Bằng chứng & kinh tế đơn vị (vòng sau)
- Cả 3 thừa số trong bảng Impact (`spec.md` §2: `2.000 × 3,9 × 5 phút`) đều là số tự ước tính, và mẫu `N = 150` hiện thu từ ĐMX/TGDĐ + `Tiki Trading` (`0/150` `nhieu_nhan_xu` / `nhieu_lap_bat_thuong`). Vòng tiếp theo cần đo thời gian làm nhiệm vụ thực tế (có công cụ vs đọc tay) trên 10–15 người và lấy thêm mẫu gian hàng không phải Mall trên Shopee.

---

## 2. Hạng mục ĐÃ XỬ LÝ & kiểm chứng Sau CP4

| Hạng mục | Thay đổi cụ thể trong repo | Kiểm chứng bằng test / số liệu |
|---|---|---|
| **1. Giảm ma sát bước đầu trên Web UI** | Thêm nút 1-click **`Thử mẫu SP01 ngay`** (`#try-sp01`) nổi bật ở đầu form trong `codebase/web/index.html`, `app.js`, `style.css`; ghi rõ ngay ô nhập `"Dán nội dung review (không tự tải từ link)"`; cập nhật chỉ dẫn catalog từ `SP01–SP03` thành `SP01–SP06`; tách riêng tiêu đề chế độ giả thành **`"Chế độ giả — chưa gọi AI thật"`** thay vì dùng chung `"Chưa đủ căn cứ phân tích"`; hiển thị khối `counter_citations` tách biệt trong thẻ rủi ro. | `tests/test_web_app.py` (14/14 pass, gồm `test_post_cp4_ux_quick_start_hint_fake_heading_and_counter_citations`) · `node --check codebase/web/app.js` pass. *(Lưu ý: chưa tổ chức vòng thử nghiệm lại với người dùng ngoài nhóm sau khi sửa UI.)* |
| **2. Tách schema `risk_citations` vs `counter_citations` & kiểm chứng `eval/run-3.csv`** | Cập nhật `SYSTEM` prompt, hậu kiểm `_resolve_citations()`, schema `structured` và `_format_output()` trong `codebase/agent.py` (cùng `codebase/ui_backend.py`) để tách hẳn `risk_citations` (chỉ bằng chứng lỗi) khỏi `counter_citations` (hiển thị ở mục riêng `## Ý kiến tích cực / đối chứng (không phải bằng chứng rủi ro)`). | Chạy mới `python run.py eval` → `eval/run-3.csv` + `traces/run-3.jsonl` (`run-3@20261128-213651`, `gpt-6-luna`, **0/25 lỗi**, 22 model calls, 75 tool calls, 43.734/8.647 token khớp 100% trace). `trich_dan_ton_tai` = **21/21 (100%)** (script độc lập). Chấm sơ bộ (chờ người xác nhận): **24/25 (96%)** (`B17` từ trượt → đạt, 0 câu tụt điểm), **`rui_ro_duoc_dan_chung`** tăng từ **25/32 (78,1%) → 32/34 (94,1%)** (vượt ngưỡng ≥90%; còn 2 thẻ dính ca biên `SP03 [R20]` ở `B20` và `B22`). Chi tiết: `eval/report.md` §5. |
| **3. Nâng cấp `filter_review_noise` cho review trộn ngoài mẫu** | Cập nhật `codebase/tools.py`: tách mệnh đề theo dấu câu và liên từ tương phản (`nhưng`, `nhưng mà`, `tuy nhiên`, `chỉ tiếc`), bỏ mệnh đề giao hàng/đóng gói/giá/cảm ơn/câu mở đầu thắc mắc rồi chỉ lọc nếu phần chữ còn lại không chứa nhận xét sản phẩm đáng kể; đồng thời sửa lỗi đụng dấu `"hỏi"` (chuyển sang kiểm NFC để không ăn nhầm `"hơi"`, `"hôi"`). | `codebase/test_agent.py` (21/21 pass): giữ nguyên **60/60 (100%)** khớp ground truth CP2 (`SP01–SP03`), giữ lại thành công **`SP05 [R23]`** và **6/6 (100%)** review rủi ro thật trên tập Tiki ngoài mẫu (`SP04–SP06`, tổng khớp nhị phân `82/90 = 91,1%`, 0 review rủi ro bị lọc nhầm trên cả `N = 150`). |
| **4. Retry có exponential backoff cho lỗi mạng tạm thời** | Cập nhật `codebase/ai.py`: thêm retry (mặc định tối đa `OPENAI_MAX_RETRIES=2`, `OPENAI_RETRY_BACKOFF=1.0`, tôn trọng `Retry-After` ≤ 10s) cho HTTP `429/502/503/504` và `URLError` bên trong `@model_call` (không retry `400/401/403/404`, không tính trùng token). | `tests/test_ai_endpoint.py` (5/5 pass, gồm `test_retries_transient_http_502_503_and_succeeds` và `test_does_not_retry_non_retryable_http_401`) và 0/25 lỗi trong `eval/run-3.csv`. |

---

## 3. Hướng đi tiếp cho vòng sau (chưa triển khai trong hackathon)

1. **Phân phối sản phẩm qua Browser Extension 1-click & mở rộng sàn:**
   - Phát triển tiếp `extension/` (đã có handoff sang Web UI) theo hướng 1-click ngay trên trang sản phẩm để xoá hẳn thao tác copy-paste tay.
   - Bổ sung cơ chế đọc trực tiếp DOM đang hiển thị trên trang làm phương án dự phòng khi endpoint review nội bộ của Shopee trả `HTTP 403/429`.
   - Mở rộng sang **Tiki** và **Lazada** (cấu trúc review công khai ổn định hơn Shopee).
2. **Định vị lại thông điệp cốt lõi (Value Proposition) bám chặt bằng chứng:**
   - Khi pitching/giới thiệu vòng tiếp theo, không dẫn bằng con số *"tiết kiệm 15–30 phút"* khi chưa có số đo thực nghiệm; dẫn trực tiếp bằng 2 giá trị đã có bằng chứng:
     1. **Tách lớp nhiễu 67,3% (`101/150`) và kiểm chứng review gốc 1-click** (khớp `4/4` người phỏng vấn nghi ngờ nhiễu và `3/3` muốn bấm xem gốc).
     2. **Phát hiện rủi ro ẩn trong review 4–5★** (`3/6 = 50,0%` rủi ro Tiki nằm trong 4–5★ — bộ lọc 1–2★ của sàn vẫn bỏ sót).
3. **Nâng cấp bằng chứng & kinh tế đơn vị bằng số đo thực nghiệm:**
   - Tổ chức thử nghiệm lại UX bản Web UI mới + đo thời gian hoàn thành nhiệm vụ thực tế (có công cụ vs đọc tay) trên **10–15 người** ngoài nhóm để thay các thừa số tự ước tính ở `spec.md` §2 (`2.000 × 3,9 × 5 phút`).
   - Thu thêm mẫu review công khai trên gian hàng **không phải Mall** của Shopee để đo tỷ lệ thực tế của `nhieu_nhan_xu` và `nhieu_lap_bat_thuong` (hiện là `0/150` trên ĐMX/TGDĐ và `Tiki Trading`).
   - Tiếp tục tinh chỉnh phân biệt review cân bằng/hài lòng tổng thể có nhắc đặc tính công suất thấp (như `SP03 [R20]`) để xử lý nốt 2 thẻ còn lại ở `B20` và `B22`.
