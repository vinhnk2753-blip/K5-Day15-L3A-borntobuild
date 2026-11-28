# Người dùng thử *(bonus)*

> Điền ở guide bước 4.3 — 2–3 người ngoài nhóm, ~10 phút / người, theo 5 nhịp: làm quen · bối cảnh · giao việc · quan sát · hỏi sau. Ôn lại: ngày 5, ngày 13. Chấm ở rubric Bonus.
> Không ghi tên: ghi vai. Hành vi quan sát được nặng hơn lời nói; toàn lời khen = phiên chưa đạt, giao việc khó hơn.
> Người dùng thử **không thay được** bằng chứng pain ở `evidence/`.

## Trạng thái và nguồn ghi chép

Đã có **2 phiên thật của 2 người ngoài nhóm**, do Nguyễn Quỳnh Trang tổ chức và ghi chép ngày **28/11/2026**. Trang xác nhận cả hai đã thực sự dùng thử, đồng thời chốt lại mốc giờ U02 là 12:30–12:45. Nguồn: [U01](U01.md), [U02](U02.md); không tính kiểm UI nội bộ hoặc test tự động vào số người thử.

- Bản chạy được người điều phối ghi là **v1, gpt-6-luna, AI thật**; chưa có commit chính xác, input/output hoặc ảnh đối chiếu kèm theo. Không tự gán phiên thử vào commit/model snapshot đã xác minh độc lập.
- U01: liên hệ qua mạng xã hội; 12:15–12:25, toàn buổi 10 phút, chưa ghi trực tiếp/từ xa. Thử dây cáp sạc trên Tiki; chưa đủ thông tin kết luận đây là sản phẩm đang định mua.
- U02: giới thiệu từ bạn bè; 12:30–12:45, toàn buổi 15 phút, điều khiển từ xa. Thử tai nghe Bluetooth Shopee đang thực sự cân nhắc mua; đồng ý tham gia, không ghi hình.
- [Kịch bản chuẩn bị](test-script.md) đặt tác vụ chính 3–5 phút; hai buổi thực tế kéo dài 10/15 phút, chưa tách thời gian tác vụ. Câu giao việc thực tế rộng hơn kịch bản và được lưu nguyên văn trong phiếu, không ghi rằng đã tuân thủ đầy đủ mọi bước kịch bản.
- [Template](session-template.md) chỉ là mẫu, không tính là một phiên hoặc người thử.

## Ghi chép tổng hợp

| Người thử (vai) | Việc giao (theo kết quả, không theo nút) | Quan sát (làm gì đầu tiên, chỗ do dự, chỗ hiểu sai) | Trích nguyên văn | Mức nghiêm trọng (cao / vừa / thấp) |
|---|---|---|---|---|
| [U01](U01.md) — người đọc review dây cáp sạc Tiki, ngoài nhóm | Trải nghiệm sản phẩm nhóm và nhận xét để cải thiện; nguyên câu trong phiếu | Sao chép review 1 sao từ Tiki, dán, đọc kết quả và bấm xem review gốc. Ban đầu không biết thao tác từ đâu; Trang hướng dẫn mỗi review một dòng. Hoàn thành **có trợ giúp**. Nêu UI ổn nhưng nhập thủ công bất tiện. | “Web cũng oke nhưng bất tiện quá, tích hợp luôn vào mấy web tmđt thì tốt” | **Vừa** — đánh giá tổng hợp: cần hướng dẫn để bắt đầu nhưng hoàn thành sau hỗ trợ |
| [U02](U02.md) — người cân nhắc tai nghe Bluetooth Shopee, ngoài nhóm | Trải nghiệm sản phẩm nhóm và nhận xét để cải thiện; nguyên câu trong phiếu | Tìm sản phẩm, sao chép khoảng 10 review tiêu cực, dán, đọc tổng hợp và so sánh review gốc. Ban đầu tưởng lấy review trực tiếp từ link; được giải thích sau khoảng 2 phút. Hoàn thành **có trợ giúp**. Nêu phần tổng hợp hữu ích nhưng copy review tốn công. | “Ý tưởng khá hay, nhất là khi sản phẩm có hàng nghìn đánh giá. Nhưng nếu phải copy từng review thì hơi mất thời gian, mình muốn chỉ cần dán link là xem được luôn.” | **Vừa** — đánh giá tổng hợp: hiểu sai phạm vi đầu vào, cần giải thích rồi hoàn thành |

Quan sát và quote lấy từ phiếu do Trang cung cấp. Mức nghiêm trọng và đề xuất bên dưới là phần phân tích tổng hợp, không phải lời nói thêm của người tham gia. Không có lỗi API được ghi trong hai phiếu; không suy rằng đã kiểm hết các ca lỗi hoặc đánh giá toàn bộ độ chính xác AI.

Câu hỏi sau: *"Nếu mai không được dùng nữa, bạn thấy: rất tiếc / hơi tiếc / không sao?"* → **Rất tiếc 0/2 · hơi tiếc 1/2 · không sao 1/2 · không trả lời 0/2**. U01 trả lời “không sao”; U02 được phân loại “hơi tiếc” từ nguyên văn: “Cũng hơi tiếc vì phần tổng hợp các vấn đề gặp phải khá hữu ích khi mua đồ điện tử.” Đây không phải phép đo willingness-to-pay hoặc PMF.

Hoàn thành luồng được ghi: **tự lực 0/2 · có trợ giúp 2/2 · chưa hoàn thành 0/2**. Cả hai phiếu ghi có xem/so sánh review gốc; chưa có bằng chứng kiểm nguyên văn từng citation. **2/2** nêu bất tiện của nhập review thủ công; U01 mong tích hợp sàn, U02 mong dán link lấy review. Chưa có đo đối chứng thời gian, không xác nhận 5 phút tiết kiệm/lần hoặc 19,5 phút/người/tháng trong spec.

## Tổng hợp

- **Chủ đề lặp:** bước đưa review vào hệ thống gây ma sát ở 2/2 người; cả hai hoàn thành sau trợ giúp nên chưa chứng minh UI tự hướng dẫn tốt. U02 hiểu sai phạm vi lấy dữ liệu từ link, cần giải thích rõ hơn.
- **Điểm tích cực:** U01 nhận xét UI ổn và có dùng xem nguồn; U02 đọc tổng hợp, so sánh nguồn và nói hữu ích. Đủ cơ sở giữ luồng tóm tắt → đối chiếu, chưa đủ để kết luận đọc nhanh hơn theo số đo hoặc người dùng sẽ quay lại thường xuyên.
- **Quyết định sản phẩm:** giữ lát cắt phân tích review đã cung cấp, ưu tiên cải thiện điểm bắt đầu trước khi mở rộng thu thập. Không tự bổ sung crawler/dán link lấy toàn bộ review chỉ từ hai phản hồi.

### Hành động đã/sẽ làm

| Hành động | Căn cứ | Ưu tiên và trạng thái |
|---|---|---|
| Đánh giá lại hướng dẫn tại bước nhập, thêm ví dụ ngắn ngay chỗ bắt đầu nếu cần; kiểm người mới có tự làm được không | U01 không biết bắt đầu; U02 cần giải thích luồng nhập | Ưu tiên trước demo nếu còn thời gian; **đề xuất, chưa sửa/chưa thử lại** |
| Làm rõ hệ thống chỉ phân tích review đã cung cấp, không tự tải toàn bộ review từ link trong luồng này | U02 tưởng dùng link lấy dữ liệu | Ưu tiên trước demo nếu còn thời gian; **đề xuất, chưa sửa/chưa thử lại** |
| Giữ phần tổng hợp rủi ro và khả năng xem review gốc | Cả hai có dùng nguồn; U02 nêu hữu ích | **Giữ chức năng hiện có**, không coi là thay đổi mới hoặc đã kiểm mọi citation |
| Khảo sát cách giảm sao chép thủ công, như luồng nhập dữ liệu có sẵn hoặc tích hợp được cấp quyền | Cả hai nêu bất tiện; mong muốn tích hợp/dán link | **Để giai đoạn sau**; chưa triển khai, cần kiểm nguồn/quyền truy cập và hiệu quả thực tế |

### Giới hạn và bài học cho buổi tiếp theo

Mẫu 2 người thuận tiện qua mạng xã hội/bạn bè, không đại diện thị trường. Cả hai tự chọn review tiêu cực (U01 chỉ 1 sao), không đại diện toàn bộ đánh giá sản phẩm; chưa kiểm khả năng hiểu ý kiến trái chiều, cờ nhiễu hoặc mọi trạng thái biên. Chưa ghi nguyên input/output, URL cụ thể, commit và kiểm chính xác citation; không tái hiện/chấm chất lượng AI từ hai phiếu này.

Buổi tiếp theo nên giao một kết quả cụ thể, ghi thời gian tác vụ tách khỏi trao đổi và mức trợ giúp, thử hướng dẫn mới nếu đã sửa. Không bổ sung lỗi/quote khi không có quan sát thật. Thời lượng 10/15 phút không phải thời gian tiết kiệm, không dùng thay số liệu Impact hoặc tỷ lệ đạt eval.

## Checklist Issue #12

- [x] Chuẩn bị kịch bản ngắn và mẫu ghi chép, không gợi ý trước đáp án.
- [x] Trang tổ chức 2 người ngoài nhóm dùng thử, xác nhận cả hai đã thực sự dùng bản chạy.
- [x] Có U01/U02 ẩn danh, bối cảnh, thao tác, trợ giúp, quote và phân tích mức nghiêm trọng; U02 đã được Trang xác nhận lại giờ.
- [x] Tổng hợp bài học và hành động giữ/đề xuất/để sau; changelog chỉ ghi việc tổng hợp, không giả nhận đã sửa UI.
- [x] Trang xác nhận đã rà soát đầy đủ phiếu và bản tổng hợp cuối ngày 28/11/2026.
- [x] Trang tạo PR #30 từ nhánh `feat/issue-12-user-validation` để nhóm review.

Phần ghi chép và tổng hợp đáp ứng nội dung DoD Issue #12 theo hai buổi đã cung cấp; chưa tự đóng issue hoặc xác nhận các đề xuất UX đã được triển khai.
