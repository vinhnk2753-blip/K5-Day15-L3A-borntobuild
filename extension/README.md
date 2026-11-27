# Shopee Review Risk Agent

Extension Chrome Manifest V3: trên trang sản phẩm Shopee.vn, bấm **Phân tích review** để lấy tối đa 50 review cho từng mức 5–4–3–2–1 sao, gửi dữ liệu đã bỏ tên người đánh giá tới backend Python cục bộ, rồi hiển thị tối đa ba rủi ro có trích dẫn.

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

1. Mở PowerShell ở thư mục gốc repo và chạy `python codebase/extension_server.py`.
2. Mở `chrome://extensions`, bật **Developer mode**, chọn **Load unpacked** và trỏ tới thư mục `extension/`.
3. Mở hoặc tải lại một trang sản phẩm `shopee.vn`, rồi bấm nút **Phân tích review** ở góc dưới bên phải.
4. Server dừng bằng `Ctrl+C`.

Backend chỉ bind vào `127.0.0.1:8765`, không lưu review vào file, giới hạn dữ liệu gửi tối đa 2 MB, và xác thực mã trích dẫn với review đầu vào trước khi trả kết quả.

## Giới hạn

- Review được lấy từ endpoint hiển thị công khai của Shopee; endpoint này không phải Open API chính thức và có thể đổi hoặc chặn yêu cầu.
- Tối đa 50 review mỗi mức sao, 250 tổng cộng; độ phủ không được xem là đầy đủ nếu Shopee không xác nhận.
- Muốn phân tích bằng GPT cần OpenAI API key và quyền sử dụng model đã chọn. Không có cấu hình thì agent chạy chế độ giả an toàn, không tự tạo rủi ro.
