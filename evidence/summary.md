# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).
> Bản CP3 · Tổng hợp ban đầu: Nguyễn Thị Hải Yến (`@Jennguyen106`); đồng bộ số liệu `N = 150` sau PR #21 và chỉnh sửa theo review PR #22: Nguyễn Khánh Vinh (`@vinhnk2753-blip`) · số đào data lấy từ `evidence/data-mining.md` (`python evidence/count.py`), số phỏng vấn lấy từ `evidence/interviews/P1.md`–`P4.md`.

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ Đạt ngưỡng: `N = 150` (60 ĐMX/TGDĐ + 90 Tiki), đã kiểm tay 60/60 + 90/90 nhãn, có script tái lập `evidence/count.py`, 10 ví dụ; vượt ngưỡng `≥100` review đặt ở `evidence/hypothesis.md` | `evidence/data-mining.md` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ◐ Một phần: 4 người, nhưng P2 không đọc review và P4 mâu thuẫn giữa câu 1 ("không đọc") với câu 2 ("5 review"), nên chỉ 2/4 chắc chắn đúng vai "người đọc review trước khi chốt đơn". Thiếu số lần/tháng và số phút | `evidence/interviews/P1.md`…`P4.md` · `evidence/pain_evidence-summary.md` |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☐ Chưa làm | `evidence/survey/` |

## 2. Số chính

- **Đào data (`N = 150` · 6 sản phẩm ≥200.000đ):** **101/150 (67,3%)** review mới nhất là nhiễu, không phản ánh chất lượng sản phẩm — gồm **28/60 (46,7%)** trên Điện máy XANH / Thế Giới Di Động (20 review/SP, xem 27/11/2026) và **73/90 (81,1%)** trên Tiki.vn (30 review/SP, xem 28/11/2026; riêng `62/90 = 68,9%` là review trống chỉ bấm sao). Có **32/150 (21,3%)** nêu rủi ro/lỗi/hạn chế thật (`26/60` ĐMX/TGDĐ; `6/90` Tiki) và **17/150 (11,3%)** tích cực chi tiết. Cả `6/6` sản phẩm đều hiển thị **4.7–4.9/5★** (`81%–99,9% 5★`). Riêng 90 review Tiki có số sao từng dòng: `87/90 (96,7%)` là 4–5★ (`73/87 = 83,9%` nhiễu) và **`3/6 (50,0%)` rủi ro/hạn chế thật nằm ẩn trong 4–5★** (`SP05 [R23]` 5★, `SP06 [R20]` 4★, `SP06 [R28]` 4★).
- **Phỏng vấn (`n = 4`):** 4/4 người không tin hoặc nghi ngờ review trùng/chỉ khen giao hàng và bỏ qua chúng. 3/3 người trả lời câu 6 muốn bấm xem review gốc. 2/4 người từng gặp sự cố đơn hàng (P1 bị giao sai sản phẩm phải đổi trả; P4 mua phải hàng kém chất lượng phải bỏ không dùng), nhưng cả 2 nói **review không nhắc lỗi đó**. 0/4 dùng công cụ hỗ trợ đọc review. Số lần mua/tháng và thời gian đọc review: **chưa ghi** cho cả 4 người.
- **Khảo sát:** chưa có.

| | Vai | Gặp pain? | Số lần / 1 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | Người mua online (nghề/tuổi chưa ghi) | Một phần: nghi ngờ review nhiễu; từng phải đổi trả vì giao sai hàng (review không nhắc) | chưa ghi | chưa ghi | Lọc giá, xem mô tả, đọc 10 review, xem 1 sao có vấn đề gì |
| P2 | Người mua online (nghề/tuổi chưa ghi) | Một phần: nghi ngờ review nhiễu; không đọc review khi mua | chưa ghi | chưa ghi | Không đọc review, tìm đúng loại cần mua (ghi chép mâu thuẫn: câu 2 ghi "0 review · đọc trước: 5 sao trước") |
| P3 | Người mua online (nghề/tuổi chưa ghi) | Một phần: nghi ngờ review nhiễu, chưa từng gặp lỗi bị bỏ sót | chưa ghi | chưa ghi | Đọc 10 review, xem 5 sao trước |
| P4 | Người mua online (nghề/tuổi chưa ghi) | Một phần: nghi ngờ review nhiễu; từng mua hàng kém chất lượng phải bỏ (review không nhắc) | chưa ghi | chưa ghi | Chọn theo thương hiệu (ghi chép mâu thuẫn: câu 2 ghi đọc 5 review) |

Phỏng vấn chỉ có một vai (người mua online), n = 4 nên không ghi %.

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. "Sài được có 2 tháng bong sơn ở đáy nồi, mấy chỗ bong có dấu hiệu rỉ set" — data `SP01 [R07]` (nồi chiên Sunhouse SHD4035, ĐMX, trang hiển thị 4.9/5).
2. "Dùng mới gần 9 tháng pin dự phòng đã bị phồng nhẹ, không dám dùng tiếp." — data `SP03 [R07]` (pin AVA+ Q7, TGDĐ, 4.9/5). Lưu ý: đây là bản chuẩn hoá gọn lưu trong `data/products/ava_plus_q7.json` (xem `data/DATA_CARD.md`), không phải nguyên văn đầy đủ từ web TGDĐ.
3. "Sài ổn" — data `SP01 [R14]` (ĐMX): ví dụ review khen 2 chữ, không có thông tin chất lượng.
4. "Sản phẩm bị lỗi không nhận tín hiều bằng đầu usb .Đổi trả 2 lần, lần này là lần thứ 3. Nếu sản phẩm bị lỗi nữa xin ko bao giờ mua hàng này nữa." — data `SP04 [R27]` (Tiki, 2★, chuột Logitech M650 hiển thị 4.8/5).
5. "Ủi phẳng một số vải dễ ủi thôi nhé." — data `SP06 [R20]` (Tiki, 4★, bàn ủi Philips STH3010/70) và "Giao nhanh á" — data `SP04 [R01]` (Tiki, 5★): minh hoạ rủi ro thật ẩn trong review 4★ và nhiễu chỉ khen giao hàng ở 5★.
6. "không tin tưởng" (về review khen giống nhau/chỉ khen giao hàng) · xử lý: "bỏ qua" — P1, câu 4 (ghi chép của người phỏng vấn).
7. "giao hàng không đúng sản phẩm phải đổi lại" · "review không nhắc lỗi đó" — P1, câu 3 (ghi chép của người phỏng vấn).
8. "Không đọc review, chọn theo thương hiệu" — P4, câu 1 (ghi chép của người phỏng vấn).

Các câu phỏng vấn là ghi chép trong phiếu, không phải ghi âm nguyên văn.

## 4. Các nguồn có khớp nhau không

Data (`N = 150`) cho thấy hơn hai phần ba review mới nhất là nhiễu (`67,3%` toàn tập; `46,7%` ĐMX/TGDĐ và `81,1%` Tiki), điểm hiển thị `4.7–4.9/5★` che nhiều lỗi/hạn chế thật (`32/150`), và riêng trên Tiki `3/6` rủi ro ẩn ngay trong review 4–5★. Người dùng xác nhận vế "nhiễu làm mất lòng tin": `4/4` nghi ngờ review trùng hoặc chỉ khen giao hàng và bỏ qua chúng, `3/3` trả lời câu 6 muốn bấm xem review gốc. **Hai nguồn khớp** ở pain review nhiễu và nhu cầu kiểm chứng nguồn gốc.

**Hai nguồn lệch** ở vế "bỏ sót lỗi có trong review". Data cho thấy lỗi thật có nằm trong review (`32/150`). Nhưng `2/4` người từng gặp sự cố đơn hàng (P1 giao sai hàng, P4 hàng kém chất lượng) đều nói review không nhắc tới lỗi đó, P2 không đọc review còn P4 mâu thuẫn giữa câu 1 và câu 2. Hai lý do có thể giải thích độ lệch: mẫu phỏng vấn nhỏ (`n = 4`, chỉ 2 người chắc chắn đọc review), và data hiện lấy từ Điện máy XANH / Thế Giới Di Động và Tiki (`Tiki Trading`) chứ chưa có dữ liệu Shopee — sàn người được phỏng vấn nhắc tới.

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: **phải đổi** (vế data đã đạt, vế phỏng vấn chưa đạt).
- Vế (1) **đã đạt**: `101/150 (67,3%)` review là nhiễu — vượt cả hai ngưỡng `N ≥ 100` và `≥40%` nhiễu. Dữ liệu Tiki (`N = 90`) cũng cho thấy `3/6 (50,0%)` rủi ro ẩn trong 4–5★, phản bác cách giải thích rằng chỉ cần bấm lọc 1–2★ là đủ.
- Vế (2) **chưa đạt**: ngưỡng là `≥2/3` người kể được một lần mất thời gian lọc review nhiễu hoặc mua hớ vì bỏ sót cảnh báo. Kết quả là `0/4` người có đủ chi tiết: không ai ghi thời gian, và 2 người gặp sự cố đơn hàng đều nói review không nhắc lỗi đó.

→ Pain được ủng hộ rõ nhất là **tỷ lệ review nhiễu cao khiến người mua không tin review và cần bấm xem review gốc để tin** (`67,3%` nhiễu trên data; `4/4` và `3/3` ở phỏng vấn), cộng thêm rủi ro bị ẩn dưới điểm sao cao (4–5★) — chưa đủ bằng chứng cho vế "mất 15–30 phút" hay "bỏ sót cảnh báo". Sản phẩm nên nhấn vào lọc nhiễu, gom rủi ro qua mọi mức sao và trích dẫn `[Rxx]` kiểm chứng được.

**Điều vẫn chưa biết:**
- Thời gian thật người mua bỏ ra để đọc review (bảng Impact `spec.md` §2 đang dùng mức tự ước tính thận trọng 5 phút/lần và chờ đo ở validation CP4).
- Số lần đọc review thực tế mỗi tháng của người dùng mục tiêu (`spec.md` §2 và `cost/personas.yaml` tạm tham chiếu mức trung bình 4 lần mua online/tháng của Cục TMĐT & Kinh tế số kèm tự ước tính).
- Trên Shopee (kể cả gian hàng bên thứ ba), tỷ lệ nhiễu nhận xu/lặp nội dung và tỷ lệ lỗi xuất hiện trong review 1–3★ vs 4–5★ ra sao.

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| Người mua online (P1–P4) | 27/11/2026 | Đã xong 4 người; cần hỏi lại để bổ sung số lần/tháng và số phút |
| Người mua online có đọc review (P5) | chưa chốt lịch | Chưa |
