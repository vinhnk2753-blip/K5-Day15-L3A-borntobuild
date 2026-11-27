# Review Copilot: Phỏng vấn pain và tổng hợp evidence

Trạng thái: **Khung để điền**. Phần A là kịch bản phỏng vấn. Phần B là bảng ghi evidence. Phần C tổng hợp pain. Phần D là evidence đã đo được từ bộ dữ liệu Tiki (số liệu thật).

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

## B. Bảng evidence (mỗi dòng một ý)

| ID | Người (mã ẩn danh) | Câu nói / hành vi quan sát được | Pain liên quan | Lần gần nhất xảy ra | Mức độ (1–3) |
|---|---|---|---|---|---|
| E01 | P1 | | | | |
| E02 | P1 | | | | |
| E03 | P2 | | | | |
| … | | | | | |

Mức độ: 1 = phiền nhẹ · 2 = mất thời gian hoặc tiền nhỏ · 3 = mua sai, phải đổi trả hoặc mất tiền.

Không ghi tên thật, số điện thoại hay tài khoản. Chỉ dùng mã P1, P2…

---

## C. Tổng hợp pain

Điền sau khi có ít nhất 5 người. Một pain chỉ được ghi là **đã xác nhận** khi có từ 3/5 người trở lên nhắc tới.

| Pain | Số người nhắc | Evidence (ID) | Đã xác nhận? | Tính năng đáp ứng |
|---|---|---|---|---|
| H1. Đọc review mất thời gian, đọc không hết | /5 | | | Tóm tắt tối đa 3 rủi ro |
| H2. Rủi ro bị lẫn trong review 4–5 sao nên bị bỏ sót | /5 | | | Rút rủi ro không phụ thuộc số sao |
| H3. Không tin bản tóm tắt nếu không thấy nguồn | /5 | | | Trích dẫn nguyên văn và mã review |
| H4. Review trùng / chỉ khen giao hàng gây nhiễu | /5 | | | `review_flags` |
| (Pain mới phát hiện) | /5 | | | |

H1–H4 là **giả thuyết** của nhóm, chưa phải kết luận. Pain nào không đạt ngưỡng thì ghi "Chưa xác nhận" và cân nhắc bỏ tính năng tương ứng khỏi phần demo.

**Câu tóm tắt cho slide (điền sau):** "__/5 người mua cho biết ____; __/5 từng ____."

---

## D. Evidence từ bộ dữ liệu Tiki (đã đo)

Nguồn: `tiki_reviews.csv`, gồm 13.652 review, 1.821 sản phẩm, 10 danh mục.

| # | Phát hiện | Số liệu | Hỗ trợ giả thuyết |
|---|---|---|---|
| D1 | Review lệch mạnh về tích cực | 85,6% review là 4–5 sao; chỉ 2,6% là 1–2 sao | H2 |
| D2 | Ít sản phẩm có review chê rõ ràng | Chỉ 225/1.821 sản phẩm (12%) có ít nhất một review 1–2 sao | H2 |
| D3 | Rủi ro nằm cả trong review 5 sao | Bếp hồng ngoại Eurohome EIS009: cả 5 review đều 5 sao, nhưng 2 review cảnh báo bếp tỏa nhiệt nóng, không nên đứng gần, nhất là trẻ nhỏ | H2 |
| D4 | Số sao không khớp nội dung | Dầu gội Mira: một review chấm 1 sao nhưng nội dung khen và định mua tiếp | H2, lý do không lọc theo số sao |
| D5 | Dữ liệu trùng lặp | 1.451 review trùng nguyên văn trong cùng sản phẩm; 112 sản phẩm bị lặp đúng một nửa (cào dữ liệu 2 lần) | H4 |
| D6 | Nhiều review chưa xác minh mua hàng | 41% review có `verified_purchase = False` | H3, H4 (chỉ là tín hiệu, không kết luận review giả) |
| D7 | Phân bố số review rất lệch | Trung vị 2 review/sản phẩm; tối đa 244 review (khoảng 78.000 ký tự) | Cần trạng thái `insufficient_evidence` và giới hạn đầu vào |
| D8 | Review dài | 120–2.082 ký tự, trung vị khoảng 300 | H1 |

Lưu ý khi trình bày: D1–D8 cho thấy **dữ liệu có vấn đề**. Chúng không chứng minh **người mua thấy đau**. Hai loại evidence cần đi cùng nhau: phần C (người dùng nói) và phần D (dữ liệu cho thấy).
