# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).
> Bản CP3 · Tổng hợp: Nguyễn Thị Hải Yến (`@Jennguyen106`) · số đào data lấy từ `evidence/data-mining.md` (Nguyễn Khánh Vinh), số phỏng vấn lấy từ `evidence/interviews/P1.md`–`P4.md`.

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ N = 60, có script `evidence/count.py`, 7 ví dụ. Chưa đạt mức ≥100 review đặt ở `evidence/hypothesis.md` | `evidence/data-mining.md` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ◐ Một phần: 4 người, nhưng P2 và P4 cho biết không đọc review khi mua, nên chỉ 2/4 đúng vai "người đọc review trước khi chốt đơn". Thiếu số lần/tháng và số phút | `evidence/interviews/P1.md`…`P4.md` · `evidence/pain_evidence-summary.md` |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☐ Chưa làm | `evidence/survey/` |

## 2. Số chính

- **Đào data:** 28/60 (46,7%) review trang 1 mới nhất là nhiễu, không phản ánh chất lượng sản phẩm; 26/60 (43,3%) nêu rủi ro hoặc lỗi thật. Cả 3/3 sản phẩm vẫn hiển thị 4.9/5 (99,7–99,9% 5★). Nguồn: Điện máy XANH và Thế Giới Di Động, 20 review/sản phẩm, xem ngày 27/11/2026.
- **Phỏng vấn:** 4/4 người không tin hoặc nghi ngờ review trùng/chỉ khen giao hàng và bỏ qua chúng. 3/3 người trả lời câu 6 muốn bấm xem review gốc. 2/4 người từng mua phải hàng lỗi (phải đổi trả hoặc bỏ không dùng), nhưng cả 2 nói **review không nhắc lỗi đó**. 0/4 dùng công cụ hỗ trợ đọc review. Số lần mua/tháng và thời gian đọc review: **chưa ghi** cho cả 4 người.
- **Khảo sát:** chưa có.

| | Vai | Gặp pain? | Số lần / 1 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | Người mua online (nghề/tuổi chưa ghi) | Một phần: nghi ngờ review nhiễu; từng phải đổi trả vì giao sai hàng (review không nhắc) | chưa ghi | chưa ghi | Lọc giá, xem mô tả, đọc 10 review, xem 1 sao có vấn đề gì |
| P2 | Người mua online (nghề/tuổi chưa ghi) | Một phần: nghi ngờ review nhiễu; không đọc review khi mua | chưa ghi | chưa ghi | Không đọc review, tìm đúng loại cần mua |
| P3 | Người mua online (nghề/tuổi chưa ghi) | Một phần: nghi ngờ review nhiễu, chưa từng gặp lỗi bị bỏ sót | chưa ghi | chưa ghi | Đọc 10 review, xem 5 sao trước |
| P4 | Người mua online (nghề/tuổi chưa ghi) | Một phần: nghi ngờ review nhiễu; từng mua hàng kém chất lượng phải bỏ (review không nhắc) | chưa ghi | chưa ghi | Chọn theo thương hiệu (ghi chép mâu thuẫn: câu 2 ghi đọc 5 review) |

Phỏng vấn chỉ có một vai (người mua online), n = 4 nên không ghi %.

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. "Sài được có 2 tháng bong sơn ở đáy nồi, mấy chỗ bong có dấu hiệu rỉ set" — data `SP01 [R07]` (nồi chiên Sunhouse SHD4035, trang hiển thị 4.9/5).
2. "Dùng mới gần 9 tháng pin dự phòng đã bị phồng nhẹ, không dám dùng tiếp" — data `SP03 [R07]` (pin AVA+ Q7, 4.9/5). Đây là câu tóm ý trong `evidence/data-mining.md`; câu gốc xem `data/products/ava_plus_q7.json`.
3. "Sài ổn" — data `SP01 [R14]`: ví dụ review khen 2 chữ, không có thông tin chất lượng.
4. "không tin tưởng" (về review khen giống nhau/chỉ khen giao hàng) · xử lý: "bỏ qua" — P1, câu 4 (ghi chép của người phỏng vấn).
5. "giao hàng không đúng sản phẩm phải đổi lại" · "review không nhắc lỗi đó" — P1, câu 3 (ghi chép của người phỏng vấn).
6. "Không đọc review, chọn theo thương hiệu" — P4, câu 1 (ghi chép của người phỏng vấn).

Các câu phỏng vấn là ghi chép trong phiếu, không phải ghi âm nguyên văn.

## 4. Các nguồn có khớp nhau không

Data cho thấy gần một nửa review là nhiễu (46,7%), và điểm sao 4.9/5 che lỗi thật ở trang 1. Người dùng xác nhận vế "nhiễu làm mất lòng tin": 4/4 nghi ngờ review trùng hoặc chỉ khen giao hàng và bỏ qua chúng. **Hai nguồn khớp** ở pain review nhiễu.

**Hai nguồn lệch** ở vế "bỏ sót lỗi có trong review". Data cho thấy lỗi thật có nằm trong review (26/60). Nhưng 2/4 người từng mua lỗi đều nói review không nhắc tới lỗi đó, và 2/4 người hầu như không đọc review. Hai lý do có thể giải thích độ lệch: mẫu phỏng vấn nhỏ (n = 4, hai người không phải người đọc review), và data lấy từ Điện máy XANH/Thế Giới Di Động chứ không phải Shopee, sàn người được phỏng vấn nhắc tới.

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: **phải đổi**.
- Vế (1) **bước đầu đúng**: 46,7% review là nhiễu, vượt ngưỡng ≥40%. Nhưng N = 60, chưa đạt ≥100 như đã đặt.
- Vế (2) **chưa đạt**: ngưỡng là ≥2/3 người kể được một lần mất thời gian lọc review nhiễu hoặc mua hớ vì bỏ sót cảnh báo. Kết quả là 0/4 người có đủ chi tiết: không ai ghi thời gian, và 2 người mua lỗi đều nói review không nhắc lỗi.

→ Pain được ủng hộ là **người mua không tin review nhiễu và cần thấy review gốc để tin** (4/4 và 3/3), chứ không phải "mất 15–30 phút" hay "bỏ sót cảnh báo". Sản phẩm nên nhấn vào lọc nhiễu và trích dẫn kiểm chứng được.

**Điều vẫn chưa biết:**
- Thời gian thật người mua bỏ ra để đọc review.
- Số lần mua mỗi tháng (cần cho Impact §2 và `cost/personas.yaml`).
- Trên Shopee, lỗi người mua gặp có xuất hiện trong review 1–3 sao hay không.

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| Người mua online (P1–P4) | 27/11/2026 | Đã xong 4 người; cần hỏi lại để bổ sung số lần/tháng và số phút |
| Người mua online có đọc review (P5) | __ | Chưa |
