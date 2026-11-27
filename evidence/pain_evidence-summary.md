

# Review Copilot: Phỏng vấn pain và tổng hợp evidence

Trạng thái: **Đã phỏng vấn 4 người (27/11/2026), chưa đạt mục tiêu 5 người.** Phần A là kịch bản phỏng vấn. Phần B là bảng evidence. Phần C tổng hợp pain. Phần D là kết luận và việc cần làm.

> Quy tắc: chỉ ghi những gì người được phỏng vấn **thật sự nói hoặc làm**. Không ghi suy đoán của nhóm vào cột "Câu nói". Chưa phỏng vấn thì để trống, không điền mẫu cho có.

---

## A. Kịch bản phỏng vấn (15 phút / người)

**Đối tượng:** người mua online ít nhất 2 lần/tháng trên Tiki, Shopee, Lazada hoặc TikTok Shop. Mục tiêu tối thiểu: **5 người** (đủ để thấy pain lặp lại trong 1 ngày hackathon). Nếu còn thời gian: 1–2 người bán.

**Nguyên tắc:** hỏi về **lần gần nhất đã xảy ra**, không hỏi "bạn có muốn app X không". Không giới thiệu ý tưởng trước khi hỏi xong phần 1–3.

| # | Câu hỏi | Muốn tìm hiểu |
|---|---|---|
| 1 | Kể lại lần gần nhất bạn mua một món trên 300k online. Bạn chọn nó thế nào? | Hành vi thật, vai trò của review |
| 2 | Lúc đó bạn đọc khoảng bao nhiêu review? Đọc review nào trước (1 sao, mới nhất, có ảnh…)? | Cách đọc, thời gian bỏ ra |
| 3 | Có lần nào mua về mới thấy lỗi mà lẽ ra review đã nhắc tới không? Kể cụ thể. | Pain chính: bỏ sót rủi ro |
| 4 | Bạn làm gì khi thấy review khen giống hệt nhau hoặc chỉ khen giao hàng? | Pain về nhiễu / review không đáng tin |
| 5 | Hiện bạn có mẹo hay công cụ gì để đọc review nhanh hơn? | Giải pháp đang dùng (đối thủ thật) |
| 6 | Nếu có bản tóm tắt rủi ro, bạn cần thấy gì để **tin** nó? | Yêu cầu về dẫn chứng |
| 7 | (Sau khi demo mẫu) Bạn sẽ bấm vào trích dẫn để xem review gốc không? Còn thiếu gì? | Phản hồi trên mẫu |

Ghi lại: thời gian người đó nói họ bỏ ra để đọc review, và số lần họ nhắc lại cùng một vấn đề.

---

## B. Bảng evidence

Nguồn: phiếu phỏng vấn trên Claude Docs, nhập ngày 27/11/2026. Bốn người được đặt mã P1–P4 theo thứ tự câu trả lời trong phiếu.

Cột "Ghi chép" là lời ghi của người phỏng vấn, chép đúng như trong phiếu. Đó không hẳn là lời nói nguyên văn của người được hỏi. Cột mức độ chỉ điền khi câu trả lời khớp rõ với thang 1–3.

| ID | Người | Câu hỏi | Ghi chép (chép từ phiếu) | Pain liên quan | Mức độ |
|---|---|---|---|---|---|
| E01 | P1 | Q1 Cách chọn | "tìm, lọc khoảng giá, xem mô tả sản phẩm, review, 1 sao có vấn đề gì" | H2 | |
| E02 | P1 | Q2 Cách đọc | 10 review; đọc 5 sao trước | H1 | |
| E03 | P1 | Q3 Lỗi bị bỏ sót | Có: "giao hàng không đúng sản phẩm phải đổi lại"; hậu quả "đổi trả, tốn thời gian"; "review không nhắc lỗi đó" | Pain mới (giao sai hàng) | 3 |
| E04 | P1 | Q4 Review nhiễu | "không tin tưởng"; xử lý: "bỏ qua" | H4 | |
| E05 | P1 | Q6 Điều kiện để tin | "dùng thử trước nhiều lần"; muốn bấm xem review gốc: có | H3 | |
| E06 | P2 | Q1 Cách chọn | "cần mua, tìm luôn loại áo, không xem review" | — | |
| E07 | P2 | Q2 Cách đọc | 0 review; đọc 5 sao trước | H1 | |
| E08 | P2 | Q4 Review nhiễu | "không tin tưởng"; xử lý: "bỏ qua" | H4 | |
| E09 | P2 | Q6 Điều kiện để tin | "dùng thử trước"; muốn bấm xem review gốc: có | H3 | |
| E10 | P3 | Q1 Cách chọn | "đọc review, 10 review, xem 5 sao trước" | H1 | |
| E11 | P3 | Q2 Cách đọc | 10 review; đọc 5 sao trước | H1 | |
| E12 | P3 | Q4 Review nhiễu | "nghi ngờ"; xử lý: "bỏ qua" | H4 | |
| E13 | P3 | Q6 Điều kiện để tin | "dùng thử trước"; muốn bấm xem review gốc: có | H3 | |
| E14 | P4 | Q1 Cách chọn | "Không đọc review, chọn theo thương hiệu" | — | |
| E15 | P4 | Q2 Cách đọc | 5 review; đọc 5 sao trước | H1 | |
| E16 | P4 | Q3 Lỗi bị bỏ sót | Có: "sản phẩm không chất lượng"; hậu quả "bỏ không dùng"; review không nhắc lỗi đó | H2 (không ủng hộ) | 3 |
| E17 | P4 | Q4 Review nhiễu | "nghi ngờ"; xử lý: "bỏ qua" | H4 | |

Không ghi thành dòng riêng:
- **Q3 của P2 và P3:** cả hai trả lời "không", chưa từng gặp lỗi bị bỏ sót.
- **Q5 của cả 4 người:** đều trả lời "không", chưa ai dùng mẹo hay công cụ nào để đọc review nhanh hơn.

Mặt hàng được nhắc: giày, quần áo. Sàn được nhắc: Shopee. Phiếu không ghi rõ mặt hàng hay sàn này thuộc người nào.

**Dữ liệu còn thiếu hoặc mâu thuẫn**, cần hỏi lại người phỏng vấn:
- Bảng thông tin buổi phỏng vấn còn trống: ngày, hình thức, nghề nghiệp, số lần mua mỗi tháng.
- Không ai ghi thời gian đọc review (phút), nên chưa đo được H1.
- P2 đọc 0 review nhưng vẫn ghi "đọc 5 sao trước".
- P4 nói "không đọc review" ở Q1 nhưng ghi 5 review ở Q2.
- Q6 chỉ có 3 câu trả lời, chưa rõ người nào bỏ trống.
- Ô "Câu nói ấn tượng nhất" và ô phản hồi khi xem demo đều trống.

---

## C. Tổng hợp pain

Ngưỡng xác nhận: ít nhất 3 người nhắc tới. Mục tiêu ban đầu là 3/5; hiện mới có 4 người.

| Pain | Số người | Evidence | Kết luận | Tính năng tương ứng |
|---|---|---|---|---|
| H1. Đọc review mất thời gian, đọc không hết | 3/4 đọc 5–10 review; 1/4 không đọc | E02, E07, E10, E11, E15 | **Chưa xác nhận.** Mỗi người chỉ đọc 0–10 review, không ai phàn nàn mất thời gian. Phiếu đánh giá mức độ 1 (phiền nhẹ) | Tóm tắt tối đa 3 rủi ro |
| H2. Rủi ro lẫn trong review 4–5 sao nên bị bỏ sót | 2/4 từng mua phải hàng lỗi, nhưng **cả 2 đều nói review không nhắc lỗi đó** | E03, E16 | **Không được ủng hộ.** Lỗi có thật và nặng (mức 3), nhưng không nằm trong review | Rút rủi ro từ review |
| H3. Không tin bản tóm tắt nếu không thấy nguồn | 3/3 người trả lời Q6 muốn bấm xem review gốc; cả 3 nói họ tin khi "dùng thử trước" | E05, E09, E13 | **Ủng hộ một phần.** Phiếu ghi H3 là "không", nhưng Q6 cho thấy cả 3 người muốn xem nguồn. Cần thống nhất lại cách hiểu | Trích dẫn nguyên văn kèm mã review |
| H4. Review trùng hoặc chỉ khen giao hàng gây nhiễu | **4/4** không tin hoặc nghi ngờ, và đều bỏ qua | E04, E08, E12, E17 | **Đã xác nhận (4/4)** | `review_flags` |
| Mới: giao sai sản phẩm, phải đổi trả | 1/4 | E03 | Ghi nhận, chưa đủ người. Đây là vấn đề vận chuyển, không phải review | Ngoài phạm vi |

Thêm một quan sát: **4/4 người đọc review 5 sao trước**, và **0/4 dùng công cụ hỗ trợ nào**.

---



---

## D. Kết luận và việc cần làm

**Câu tóm tắt cho slide:** "4/4 người mua không tin hoặc nghi ngờ các review trùng lặp và đều bỏ qua chúng; 3/3 người muốn tự bấm xem review gốc trước khi tin một bản tóm tắt."

Hàm ý cho sản phẩm:
- **Hai tính năng có evidence ủng hộ:** gắn cờ review nhiễu (H4) và trích dẫn có nguồn (H3). Nên đưa hai phần này lên đầu bản demo.
- **Giả thuyết cốt lõi H2 chưa được ủng hộ.** Cả 2 người từng mua hàng lỗi đều nói review không nhắc tới lỗi đó, tức là Review Copilot sẽ không giúp được họ. 
- **Người dùng tin vào việc "dùng thử trước".** Bản tóm tắt nên được giới thiệu là công cụ hỗ trợ người mua tự kiểm chứng, đúng với phạm vi trong hợp đồng UI–AI, không phải để thay họ quyết định.

Việc cần làm:
- [ ] Phỏng vấn thêm ít nhất 1 người để đạt 5. Nên chọn người hay đọc review, và hỏi kỹ Q3: lỗi đó có xuất hiện ở review 1–2 sao, hay ở review 4–5 sao không.
- [ ] Bổ sung bảng thông tin buổi phỏng vấn và thời gian đọc review (phút) cho P1–P4.
- [ ] Xác nhận lại các mâu thuẫn của P2, P4 và người bỏ trống Q6.
- [ ] Ghi một câu nói nguyên văn đáng trích cho mỗi người.
