# Kịch bản người dùng thử — Issue #12

Phụ trách: Nguyễn Quỳnh Trang. [Issue #12](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/issues/12) · CP4 14:30 ngày 28/11/2026, hạng mục bonus.

## Mục tiêu và người tham gia

Quan sát người mua có tự nhập/chọn dữ liệu, hiểu kết quả và đối chiếu nguồn review được không; phân biệt cờ bất thường với kết luận gian lận. Đây là thử khả năng sử dụng sản phẩm, không thay bằng chứng pain hoặc bộ eval.

Mời **2–3 người ngoài nhóm**, ưu tiên người có đọc review khi cân nhắc sản phẩm từ 200.000đ. Ghi đúng vai và bối cảnh họ tự nói, không ghi tên, tài khoản, số điện thoại. Dùng mã U01/U02/U03; không mặc định họ là người phỏng vấn P1–P4.

Tác vụ chính 3–5 phút/người; có thể dành thêm vài phút hỏi bối cảnh/trao đổi, tổng khoảng 5–10 phút. Thông báo trước nếu cần ghi âm/chụp màn hình và chỉ làm khi họ đồng ý; ghi chú chữ là đủ.

## Chuẩn bị

- Chạy `python run.py` trên máy đã cấu hình AI thật. Không mở `.env` hoặc terminal có thông tin bí mật khi chia sẻ màn hình.
- Mở `http://127.0.0.1:8000`. Nếu thử từ xa, cho người tham gia điều khiển máy qua công cụ nhóm đã có; địa chỉ 127.0.0.1 trên máy họ không trỏ tới máy của bạn. Không tự mở cổng hoặc công khai server chỉ để thử.
- Chuẩn bị một bản [phiếu ghi chép](session-template.md) cho mỗi người và đồng hồ bấm giờ. Ghi commit/bản chạy và mã model thực dùng.
- Để họ chọn sản phẩm trong catalog phù hợp mối quan tâm, hoặc mang tập review công khai đã ẩn danh của sản phẩm đang cân nhắc. Nếu chỉ thử SP01–SP06, ghi đúng là mẫu catalog; không nói đó là sản phẩm họ định mua nếu họ không nói vậy.
- Bắt đầu ở trang nhập liệu, chưa mở sẵn kết quả hoặc popup. Không cho xem đáp án/kịch bản kiểm của người quan sát.

## Năm nhịp thử

| Thời gian gợi ý | Người điều phối nói/làm | Ghi lại |
|---|---|---|
| 0:00–0:30 · Làm quen | “Mình đang thử giao diện, không kiểm tra bạn. Bạn cứ thao tác và nói điều bạn đang nghĩ; chỗ nào khó hiểu cứ nói thẳng. Mình xin ghi chú ẩn danh nhé.” | Đồng ý tham gia/ghi chú; có đồng ý ghi hình nếu cần không |
| 0:30–1:00 · Bối cảnh | “Gần đây bạn đang cân nhắc món hàng nào? Bình thường bạn xem đánh giá như thế nào?” | Vai, nhu cầu thật, cách đọc review; không suy tần suất hoặc phút nếu chưa hỏi |
| 1:00–3:00 · Giao việc | “Hãy dùng trang này để xem các phản ánh đáng cân nhắc của sản phẩm hoặc tập đánh giá bạn chọn. Chọn một nhận xét trong kết quả và chỉ cho mình bằng chứng gốc để bạn tự kiểm tra.” | Việc làm đầu tiên, đường đi, thời gian, có tự tìm được nguồn hay không |
| 3:00–4:00 · Quan sát/đào sâu | “Bạn hiểu kết quả này nói gì? Có điều gì bạn vẫn chưa thể kết luận?” Nếu người dùng chỉ khen chung, đề nghị họ chỉ ra một kết luận cụ thể và nguồn hỗ trợ. | Họ đọc/hiểu con số nhiễu, mức chắc chắn và giới hạn ra sao; trích nguyên văn nếu ghi đúng được |
| 4:00–5:00 · Hỏi sau | “Chỗ nào làm bạn do dự hoặc chưa rõ? Công cụ giúp bạn việc gì, và bạn vẫn cần tự làm gì?” Cuối cùng: “Nếu mai không được dùng nữa, bạn thấy: rất tiếc / hơi tiếc / không sao?” | Phản ứng tích cực có hành vi hỗ trợ, điểm vướng, lựa chọn và lý do thật |

Nếu hết 5 phút, dừng tính thời gian tác vụ trước khi hướng dẫn. Có thể trao đổi thêm, ghi rõ phần nào diễn ra sau khi được trợ giúp.

## Quy tắc quan sát — không đọc cho người tham gia

- Không nói trước “bấm R01”, vị trí nút, số rủi ro hoặc kết quả đúng. Giao việc theo kết quả muốn đạt, không theo từng cú bấm.
- Khi họ hỏi cách làm, hỏi lại “Bạn đang mong đợi làm gì tiếp theo?”. Nếu mắc kẹt và cần hỗ trợ, ghi thời điểm/câu hỗ trợ, rồi đánh dấu **có trợ giúp**; không tính là tự hoàn thành.
- Ghi thao tác quan sát được trước, diễn giải sau. Lời nói chỉ đưa vào ngoặc kép nếu ghi được nguyên văn; nếu chỉ nhớ ý thì ghi **diễn giải**, không dựng câu trích dẫn.
- Có thể ghi “không quan sát thấy trở ngại” nếu đúng. Không bịa lỗi để làm báo cáo phong phú; lời khen chung thiếu hành vi thì cần hỏi/tác vụ cụ thể hơn.
- Lỗi API hoặc mạng cũng ghi thật, phân biệt với vấn đề thao tác. Không biến phiên lỗi thành phiên thành công bằng cách bỏ qua khỏi log.
- Ghi thời gian thực hiện tác vụ, không gọi đó là thời gian tiết kiệm. Nếu không có phép đo đối chứng phù hợp, chưa xác nhận giả định 5 phút/lần hoặc 19,5 phút/tháng trong spec.

## Điều người quan sát cần kiểm

1. Có tự chọn mẫu/dán review và bắt đầu phân tích được không?
2. Có tìm được một phản ánh cụ thể và mở review gốc đối chiếu không? Nội dung được xem có khớp nguồn không?
3. Có phân biệt phản ánh đơn lẻ với lỗi phổ biến; nhiễu/trùng với chứng cứ gian lận không?
4. Có hiểu rằng hệ thống hỗ trợ đọc review, còn quyết định mua thuộc người dùng không?

Không cần ép cả 4 ca kiểm kỹ thuật của Issue #8 vào mỗi phiên. Khi gặp thiếu dữ liệu hoặc lỗi tự nhiên, ghi cách họ hiểu và xử lý; có thể giao thêm ca ngắn nếu còn thời gian, đánh dấu tác vụ bổ sung.

## Sau mỗi buổi

- Lưu ghi chép vào `validation/U01.md`/`U02.md`/`U03.md` theo template, chỉ tạo bản có dữ liệu khi buổi thử diễn ra; template không phải bằng chứng đã thử.
- Điền `validation/log.md`: số người thật, bối cảnh, quan sát, quote/diễn giải, mức nghiêm trọng và nhóm đã/sẽ chỉnh gì. Dẫn tới ghi chép tương ứng.
- Số người hoàn thành tự lực/có trợ giúp/không hoàn thành phải có mẫu số thực. Với 2–3 người, ưu tiên x/n; không suy rộng ra thị trường.
- Nếu sửa sản phẩm theo quan sát, ghi thay đổi thật và lý do trong `spec.md` §10; chỉ ghi “đã sửa/đã thử lại” sau khi thực sự làm.

## Lời mời mẫu — Trang tự gửi

“Mình cần nhờ bạn thử một trang hỗ trợ đọc review sản phẩm trong khoảng 5–10 phút. Bạn sẽ tự chọn một sản phẩm mẫu hoặc tập review công khai rồi thao tác theo cách của mình. Mình muốn biết chỗ nào dễ hiểu/khó hiểu và chỉ ghi chú ẩn danh; bạn không cần mua gì. Bạn có thể tham gia không?”

Mẫu lời mời chuẩn bị trước buổi thử; xem kết quả 2 buổi thật tại [validation/log.md](log.md).
