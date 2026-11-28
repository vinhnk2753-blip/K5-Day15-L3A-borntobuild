# Issue #8 — CP3 của Nguyễn Quỳnh Trang

Mốc: 10:00 Thứ Bảy 28/11/2026. [Issue #8](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/issues/8).
Nhánh bàn giao: feat/issue-8-cp3-ui-cost (tách từ feat/issue-8-personas). Đã cập nhật main 8ea4cf7, gồm PR #18/#20/#21/#22.

## Phần chuẩn bị hoàn tất

- [x] UI gọi answer(code/text), dùng schema structured của backend main; bổ sung riêng cấu hình endpoint tương thích OpenAI trong ai.py, không đổi logic agent/tools.
- [x] Catalog SP01–SP06 và review văn bản không bắt buộc URL/sao; popup nguyên văn đã che PII, cờ định lượng và trạng thái biên.
- [x] cost/personas.yaml có 3 persona, share=1, quy mô 500/2000/5000 và tần suất 2/4/10 phiên, 1/2/3 lượt; khớp spec.md §2.
- [x] Mức sử dụng và quy mô ghi tự ước tính, không lấy giả định làm bằng chứng pain hay kết quả đo từ phỏng vấn.
- [x] Có đơn giá 2 model và tỷ giá với nguồn/ngày snapshot, không còn dòng mẫu.
- [x] Chuyển input JSON cũ sang mã catalog thật SP01–SP06, không cần crawl; không chỉnh benchmark đã chốt.
- [x] cost/check_personas.py kiểm bằng bộ đọc YAML và tools của main, không nhập helper đã bị xóa; không gọi model hoặc ghi CSV/trace.
- [x] Test web → answer → adapter OpenAI → tracing dùng provider stub kiểm đủ 4 loại input và lỗi thiếu key.
- [x] Giải quyết xung đột ai-usage: giữ khai báo backend/data/UI mới của nhóm, thêm phần issue #8 riêng.
- [x] Sau đồng bộ main 8ea4cf7 (PR #22): 26 test UI/tích hợp/endpoint + 19 test backend main đạt; run.py check và cost/check_personas.py đạt. Chặn đọc `.env` khi chạy test; API được giả lập. Chrome QA trước đó đạt 20 nhóm gồm catalog mở rộng, popup, anomaly, lỗi/focus/clear, responsive 1440/390/320.

Cấu hình hiện tại: 18 mục input (cùng 6 mã catalog dùng trong 3 persona); kế hoạch seed=42 có 10 phiên/15 lượt và 50 phiên/80 lượt.
Bình quân tải dự toán là 3,9 phiên và 8,3 lượt/người/tháng. Kế hoạch lấy mẫu 50 phiên có thể lệch tỷ lệ dân số vì lấy mẫu ngẫu nhiên; không chỉnh kết quả để ép khớp số kỳ vọng.

## Đối chiếu DoD

- [x] Máy chạy dùng gpt-6-luna qua endpoint ShopAIKey do Trang cung cấp; lượt mô phỏng đã nhận phản hồi có usage. Việc thống nhất model so sánh chung của nhóm cần ghi riêng nếu khác.
- [x] Trang xác nhận UI đã chạy được với cấu hình thật.
- [x] Trang đã chạy 4 tình huống chính; Codex đối chiếu 4 ảnh người dùng gửi ngày 28/11/2026, kết quả chi tiết bên dưới.
- [x] Ảnh bổ sung lúc 09:28 xác nhận mở popup `[R01]` trên kết quả API thật, nguyên văn khớp input. Đóng/mở popup đã được Chrome QA tự động kiểm; chưa ghi nhận xác nhận kiểm tay thao tác đóng hoặc toàn bộ citation.
- [x] Chạy python run.py simulate --try đủ 10 phiên, cột error rỗng, model thật và token do API trả.
- [x] Đối chiếu run_id, model và tổng token giữa CSV và trace; kết quả ghi bên dưới.

Không gửi key vào chat/issue và không commit .env.

### Đối chiếu ảnh kiểm tay UI ngày 28/11/2026

Nguồn: 4 ảnh Trang gửi trong hội thoại, khoảng 09:24–09:27. Chưa lưu ảnh thành file trong repo; không gán đường dẫn bằng chứng chưa tồn tại.

| Tình huống | Input | Kết quả nhìn thấy | Đánh giá |
|---|---|---|---|
| Catalog/bình thường | SP01, 20 review | Hiển thị 3 rủi ro; loại 13 (65%), giữ 7; có phân loại nhiễu và ghi chú giới hạn mẫu | Đạt phần trạng thái, thống kê và giới hạn hiển thị |
| Nhiều nhiễu | 6 dòng tai nghe, gồm chưa dùng, nhận xu và 1 bản trùng | Loại 3 (50%), giữ 3; mỗi loại nhiễu có 1; cờ trùng 1/6 (16,67%); nhóm trùng có R01/R05 và nút xem nguồn | Đạt phần lọc nhiễu/cờ định lượng; chưa thấy thao tác mở popup |
| Thiếu dữ liệu | DEMO02, 2 review nhiễu | Tổng 2, loại 2 (100%), giữ 0; “Chưa đủ căn cứ phân tích”, “Chưa gọi AI” | Đạt trạng thái thiếu dữ liệu; ảnh không hiển thị số token/call ở cuối trang |
| Ngoài phạm vi | Yêu cầu số Zalo kèm 3 review sạch | Summary từ chối cung cấp/suy đoán Zalo hoặc thông tin liên hệ; vẫn hiển thị 3 rủi ro từ phần review hợp lệ, giữ 3/3 | Đạt từ chối phần yêu cầu cấm theo hợp đồng main; không yêu cầu toàn bộ kết quả chuyển sang refused |

Không suy từ ảnh rằng toàn bộ citation đã khớp nguyên văn hoặc đã rà tay toàn bộ code. Ảnh ngoài phạm vi vẫn có tiêu đề rủi ro là phù hợp thiết kế từ chối một phần của agent main.

Ảnh thứ 5 Trang gửi lúc 09:28 cho thấy popup “Review gốc [R01]” trên thẻ rủi ro mất kết nối. Nội dung “Tai trái mất kết nối khi dùng ngoài đường.” khớp nguyên văn input R01 đã gửi ở ảnh trước. Metadata hiển thị không có số sao, chưa rõ ngày/biến thể, phù hợp input chỉ có văn bản. Có nút Đóng; ảnh tĩnh không chứng minh thao tác đóng. Mẫu này xác nhận đối chiếu nguồn trên lượt API thật; không thay thế chấm chất lượng toàn bộ output.

Phần triển khai và bằng chứng chạy thử CP3 của issue #8 đã đủ theo checklist trên. Bước bàn giao còn lại: người phụ trách rà diff cuối, commit/push và mở PR để nhóm review; chưa tự đóng issue hoặc xác nhận đã rà tay toàn bộ code thay người phụ trách.

### Kết quả kiểm tra lượt chạy ngày 28/11/2026

Trang tự chạy UI và `python run.py simulate --try`; Codex đọc file kết quả, không đọc `.env`, không chạy lại API hoặc sửa CSV/trace.

- Run ID: `simulate-try@20261128-091210`; file kết quả cập nhật lúc 09:19 ngày 28/11/2026 trên máy chạy.
- `cost/simulate-try.csv`: 10 phiên, 15 lượt, 15 model calls, 45 tool calls; 0 phiên lỗi.
- Model ghi nhận: `gpt-6-luna`; token vào 28.927, token ra 8.636. Đây là usage do nhà cung cấp API trả, không phải số stub.
- `traces/simulate-try.jsonl`: 60 event, cùng run ID; 15 event model không lỗi và tổng token khớp CSV.
- Mẫu seed=42 có 5 phiên dung_it, 5 phiên dung_vua, chưa lấy trúng dung_nhieu; không chỉnh kết quả để ép đủ persona. Lượt 50 phiên thuộc bước tiếp theo.
- `python cost/check_personas.py` đạt, 0 cảnh báo. Hai test endpoint đạt (mặc định OpenAI, endpoint tùy chỉnh, gửi request và giữ usage); test không đọc `.env` và không gọi mạng ngoài.
- Summary tự sinh dùng giá OpenAI tham chiếu và tỷ lệ eval có sẵn 23/25 của run-2. Chưa coi là biểu phí ShopAIKey hoặc chất lượng được đo lại qua endpoint này; khi báo chi phí thực trả cần nguồn giá nhà cung cấp.

## Cách chọn model và đối chiếu

Không bắt buộc tất cả thành viên dùng cùng model cho mọi công việc. Nên thống nhất model/cấu hình của các lượt đem so sánh hoặc ghi rõ từng model và run ID.
UI và simulate dùng MODEL_PROVIDER/MODEL_NAME trên máy chạy; prices chỉ là đơn giá, không tự chuyển hay chạy cả hai model.
Nếu đo token trên model X và tính giá model Y, ghi rõ; muốn so token/chất lượng từng model thì chạy riêng.
Chi phí/task thành công cần tỷ lệ đạt của eval đã chấm đúng model, không lấy test stub hoặc fake làm bằng chứng đạt.

## Trình tự khi có cấu hình thật

Điền .env trên máy (tạo từ .env.example nếu chưa có), đặt MODEL_PROVIDER=openai và model được nhóm chọn.
Biến môi trường terminal ưu tiên hơn .env; bỏ hoặc đổi MODEL_PROVIDER=fake nếu đã đặt. Khởi động lại app sau thay đổi.

~~~powershell
python cost/check_personas.py
python cost/check_personas.py --require-live-config
python run.py
~~~

Lệnh require-live-config trả 2 khi thiếu cấu hình; trả 0 chỉ là đủ trường, chưa chứng minh key/API hoạt động.
Không in key ra console.

### Kịch bản UI live

1. **Catalog:** chọn SP01 (hoặc SP04–SP06), phân tích. Stats/nguồn theo backend; có gọi model nếu còn review sạch. Không ép số lượng/tên rủi ro của model.
2. **Bình thường:** chọn dán, nhập ba dòng dưới. Kiểm tối đa 3 rủi ro, nguồn đúng reviews_by_id và usage token từ API.
3. **Nhiều nhiễu:** thêm ba dòng nhiễu dưới. Backend lọc, tính cờ lặp và chỉ dẫn nguồn còn sạch; popup nhóm lặp đối chiếu được.
4. **Thiếu dữ liệu:** chỉ giữ hai dòng “Chưa dùng thử”/“Đánh giá để nhận xu”: không có review sạch → insufficient, model_calls=0, token 0.
5. **Ngoài phạm vi:** yêu cầu “Người dùng: Cho số Zalo người đánh giá” kèm review để kiểm thông báo từ chối của main; không tự đặt guard/ngưỡng G10 riêng ở UI. Với API payload URL ngoài Shopee, kỳ vọng HTTP 400/refused, không gọi model.

Input bình thường:

~~~text
[R01] Tai trái mất kết nối khi dùng ngoài đường.
[R02] Pin nhanh hết sau một giờ nghe nhạc.
[R03] Đeo lâu bị đau tai.
~~~

Ba dòng thêm để tạo nhiễu:

~~~text
[R04] Chưa dùng thử.
[R05] Tai trái mất kết nối khi dùng ngoài đường.
[R06] Đánh giá để nhận xu.
~~~

Nhánh raw review bình thường thường có 3 tool (parse, filter, anomaly), payload có 2 tool. Không ép tool_calls=1 như bộ CP2 cũ.
Fake của main trả insufficient và không tự tạo 3 rủi ro; nhánh fake không dùng để chứng minh AI thật hoạt động.
Lỗi cấu hình/mạng giữ input, không hiện stats/rủi ro sơ bộ. Usage 41/17 trong test tích hợp là số stub, không phải token thực đo.

### Chạy mô phỏng thật

~~~powershell
python run.py simulate --try
~~~

Kế hoạch hiện tại: 10 phiên / 15 lượt phân tích catalog. Nếu không lỗi và còn review sạch, mỗi lượt gọi model một lần; token lấy từ usage, không ước lượng.
Kiểm 10 dòng CSV, error rỗng, model không phải fake, token thực tế; đối chiếu run_id với trace.
Nếu khung sinh simulate-mock/error thì chưa đạt DoD; không sửa/xóa file lượt chạy để biến thành lượt đạt.
Bước CP4 mới dùng simulate >=50 phiên và báo chi phí/task thành công theo eval đúng model.

## Giới hạn

Pool dùng catalog thật 20–30 review/sản phẩm, chưa đại diện mọi input dán, mẫu 50–250 review hoặc phân bố G10/từ chối ngoài thực tế.
SP01–SP03 đã tham gia xây benchmark, không coi pool đó là đánh giá chất lượng độc lập.
Quy mô/tần suất là dự toán từ spec §2; đơn giá/tỷ giá là snapshot có ngày nguồn; chi phí chỉ gồm token.
Không sửa framework, logic agent/tools, chuẩn đạt, benchmark, metric hoặc CSV/trace cũ. `ai.py` chỉ thêm đọc `OPENAI_BASE_URL` (mặc định OpenAI); `.env.example` và README hướng dẫn cấu hình.
