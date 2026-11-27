# Shopee Review Risk Agent

Extension Chrome Manifest V3: trên trang sản phẩm Shopee.vn, bấm **Lấy review JSON** để lấy tối đa 50 review cho từng mức 5–4–3–2–1 sao. Extension gọi endpoint ngay trong ngữ cảnh trang Shopee, sau đó hiển thị JSON để copy hoặc tải thành file. Bước crawl không cần Apify hay backend Python.

## Cấu hình GPT

1. Tạo `.env` ở thư mục gốc từ `.env.example`.
2. Điền cấu hình OpenAI của nhóm:

   ```
   MODEL_PROVIDER=openai
   MODEL_NAME=gpt-6-luna
   API_KEY=<OpenAI API key>
   ```

   Có thể đổi `MODEL_NAME` sang model GPT mà tài khoản API của nhóm được phép dùng. Không đưa API key vào extension.

## Chạy thử giao diện extension

1. Mở `chrome://extensions`, bật **Developer mode**, chọn **Load unpacked** và trỏ tới thư mục `extension/`.
2. Nếu extension đã cài, nhấn **Reload** sau khi cập nhật code; tải lại trang sản phẩm Shopee.
3. Bấm **Lấy review JSON** ở góc dưới bên phải, rồi chọn **Crawl review → JSON**. Trong lúc chạy, panel cập nhật trang đang lấy, số review đã quét và số review gom được theo từng mức sao.
4. Xem JSON ngay trong panel, bấm **Copy JSON** hoặc **Tải JSON** để lưu file.

Luồng hiện tại tập trung vào crawl và xuất JSON. Backend agent Python được giữ riêng cho bước phân tích tiếp theo.

## Giới hạn

- Review được lấy từ endpoint ratings hiển thị công khai của Shopee; endpoint này không phải Open API chính thức và có thể đổi hoặc chặn yêu cầu. Request chạy trong page context để dùng đúng phiên Shopee của tab, tương tự fetch từ DevTools Console.
- Tối đa 50 review mỗi mức sao, 250 tổng cộng; độ phủ không được xem là đầy đủ nếu Shopee không xác nhận.
- Muốn phân tích bằng GPT cần OpenAI API key và quyền sử dụng model đã chọn. Không có cấu hình thì agent chạy chế độ giả an toàn, không tự tạo rủi ro.
