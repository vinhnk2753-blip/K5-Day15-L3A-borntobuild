# Shopee Review Risk Agent

Extension Chrome Manifest V3: trên trang sản phẩm Shopee.vn, chỉ cần **1 click** vào **Phân tích review** (hoặc biểu tượng extension trên thanh công cụ Chrome) để lấy tối đa 50 review cho từng mức 5–4–3–2–1 sao ngay trong ngữ cảnh trang Shopee (gọi tuần tự `type=5` đến `type=1`, tự fallback `type=0` và giữ dữ liệu một phần nếu gặp 403/429 hoặc bộ lọc bị bỏ qua), **tự động đẩy JSON sang Web UI Review Lens (`http://127.0.0.1:8000`) và mở tab chạy phân tích**, đồng thời giữ JSON crawl để bấm **Mở trên Web UI**, **Phân tích trong panel**, **Copy JSON** hoặc **Tải JSON** mà không cần crawl lại.

## Cấu hình GPT

1. Tạo `.env` ở thư mục gốc từ `.env.example`.
2. Điền cấu hình OpenAI của nhóm:

   ```
   MODEL_PROVIDER=openai
   MODEL_NAME=gpt-6-luna
   API_KEY=<OpenAI API key>
   ```

   Có thể đổi `MODEL_NAME` sang model GPT mà tài khoản API của nhóm được phép dùng. Không đưa API key vào extension.

## Chạy thử — Cách 1: Tự đẩy sang Web UI Review Lens (khuyên dùng)

1. Ở thư mục gốc repo, chạy `python run.py` để bật Web UI Review Lens tại `http://127.0.0.1:8000`.
2. Mở `chrome://extensions`, bật **Developer mode**, chọn **Load unpacked** và trỏ tới thư mục `extension/`. Extension gắn sẵn public key (`key` trong `manifest.json`) nên có ID cố định **`ioiaamibggpopefebobaeikfaabhnfln`** trên mọi máy.
3. Nếu extension đã cài từ phiên bản cũ hơn trước khi ghim ID, nhấn **Reload** (hoặc **Remove** → **Load unpacked** lại một lần nếu Chrome vẫn giữ ID ngẫu nhiên cũ) để dùng đúng ID `ioiaamibggpopefebobaeikfaabhnfln`, rồi tải lại trang sản phẩm Shopee. Nếu dùng bản đóng gói/ID riêng, thêm `REVIEW_LENS_EXTENSION_IDS=<extension-id>` vào `.env`.
4. Trên trang sản phẩm Shopee, **chỉ cần 1 click**: bấm nút nổi **Phân tích review** ở góc dưới bên phải (hoặc bấm **biểu tượng extension** trên thanh công cụ Chrome). Extension sẽ mở panel, cập nhật tiến độ theo từng mức sao/trang (`type=5..1`, fallback `type=0` nếu lỗi), tự `POST` payload sang `http://127.0.0.1:8000/api/extension-handoff` (chỉ lưu tạm trong RAM, không ghi file) và mở tab `http://127.0.0.1:8000/?handoff=<id>`. Web UI tự nhận payload và gọi agent phân tích ngay.

> Bạn cũng có thể chọn chế độ **Dữ liệu từ Extension Shopee (JSON)** trên Web UI để nạp lại file `.json` đã tải xuống bất cứ lúc nào.

## Chạy thử — Cách 2: Xem trực tiếp trong panel Shopee (cổng 8765)

Nếu không chạy `python run.py`, bạn vẫn có thể chạy `python codebase/extension_server.py` (cổng `8765`). Khi cổng `8000` không bật, extension tự động dự phòng sang cổng `8765` (hoặc bạn bấm **Phân tích trong panel**) để hiển thị thẻ rủi ro ngay trong panel nổi trên trang Shopee.

## Giới hạn

- Review được lấy từ endpoint ratings hiển thị công khai của Shopee; endpoint này không phải Open API chính thức và có thể đổi hoặc chặn yêu cầu. Request chạy trong page context để dùng đúng phiên Shopee của tab, tương tự fetch từ DevTools Console.
- Bộ lọc `type=1..5` là tham số endpoint chưa được Shopee cam kết chính thức; nếu Shopee đổi API hoặc bỏ qua bộ lọc, tốc độ/số lượng crawl có thể khác dự kiến.
- Tối đa 50 review mỗi mức sao, 250 tổng cộng; độ phủ không được xem là đầy đủ nếu Shopee không xác nhận.
- Payload handoff trên Web UI chỉ giữ trong bộ nhớ tạm (tối đa 10 phiên, tự hủy sau 15 phút) và không ghi dữ liệu review ra ổ đĩa.
- Muốn phân tích bằng GPT cần OpenAI API key và quyền sử dụng model đã chọn. Không có cấu hình thì agent chạy chế độ giả an toàn, không tự tạo rủi ro.
