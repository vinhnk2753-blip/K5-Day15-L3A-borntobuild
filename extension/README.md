# Shopee Review Risk Agent

Extension Chrome Manifest V3: trên trang sản phẩm Shopee.vn, bấm **Phân tích review** để lấy tối đa 50 review cho từng mức 5–4–3–2–1 sao ngay trong ngữ cảnh trang Shopee. Extension gọi tuần tự endpoint với `type=5` đến `type=1`, hiển thị mức sao/trang đang crawl, rồi gửi JSON sang backend để phân tích và hiển thị thẻ rủi ro có trích dẫn `[Rxx]`. JSON crawl vẫn có thể copy/tải xuống hoặc bấm **Phân tích lại** mà không cần crawl lại.

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

1. Ở thư mục gốc repo, chạy `python codebase/extension_server.py` để bật agent backend local. Backend dùng `.env`; `MODEL_PROVIDER=openai` sẽ gọi GPT, còn `fake` trả trạng thái giả an toàn.
2. Mở `chrome://extensions`, bật **Developer mode**, chọn **Load unpacked** và trỏ tới thư mục `extension/`.
3. Nếu extension đã cài, nhấn **Reload** sau khi cập nhật code; tải lại trang sản phẩm Shopee.
4. Bấm **Phân tích review** ở góc dưới bên phải, rồi chọn **Crawl & phân tích trang này**. Trong lúc chạy, panel cập nhật mức sao/trang đang lấy và số review đã quét/đã gom theo từng mức sao (kết quả crawl được gửi về panel qua `window.postMessage` nên không bị timeout service worker MV3).
5. Extension gửi nguyên object JSON crawl sang backend local; agent lọc nhiễu, gắn cờ lặp, hậu kiểm citation `[Rxx]`, giữ ghi chú phản ánh đơn lẻ và trả `{"output": str, "structured": {...}}`. Panel hiển thị thẻ rủi ro + trích dẫn nguồn và thu gọn JSON crawl / output agent trong mục mở rộng; **Phân tích lại**, **Copy JSON** và **Tải JSON** thao tác trực tiếp trên JSON đã crawl mà không cần crawl lại.

Extension giữ nguyên JSON crawl để người dùng kiểm tra, đồng thời gửi object đó sang agent local. Nếu backend/model lỗi, JSON crawl vẫn còn trong panel để tải hoặc bấm **Phân tích lại** sau khi bật server.

## Giới hạn

- Review được lấy từ endpoint ratings hiển thị công khai của Shopee; endpoint này không phải Open API chính thức và có thể đổi hoặc chặn yêu cầu. Request chạy trong page context để dùng đúng phiên Shopee của tab, tương tự fetch từ DevTools Console.
- Bộ lọc `type=1..5` là tham số endpoint chưa được Shopee cam kết chính thức; nếu Shopee đổi API hoặc bỏ qua bộ lọc, tốc độ/số lượng crawl có thể khác dự kiến.
- Tối đa 50 review mỗi mức sao, 250 tổng cộng; độ phủ không được xem là đầy đủ nếu Shopee không xác nhận.
- Muốn phân tích bằng GPT cần OpenAI API key và quyền sử dụng model đã chọn. Không có cấu hình thì agent chạy chế độ giả an toàn, không tự tạo rủi ro.
