# Đào data — cách đếm và kết quả (CP2 + CP3 · N = 150)

> Bản hoàn chỉnh CP3 (28/11/2026) · Phụ trách: Nguyễn Khánh Vinh (`@vinhnk2753-blip`).
> Script đếm tái lập 100% trong repo: [`evidence/count.py`](count.py) · Bảng nhãn kiểm chứng: [`evidence/cp2_labels.csv`](cp2_labels.csv) (Đợt 1 · 60 dòng) & [`evidence/cp3_labels.csv`](cp3_labels.csv) (Đợt 2 · 90 dòng) · Dữ liệu đã ẩn danh: [`data/catalog.json`](../data/catalog.json) và `data/products/*.json`.

## 1. Cách đếm — viết TRƯỚC khi chạy

- **Data dùng:** Đánh giá công khai của **6 sản phẩm phổ biến có giá bán ≥200.000đ** thuộc **6 ngành hàng khác nhau** trên **2 hệ sinh thái sàn/bán lẻ trực tuyến tại Việt Nam**:
  - **Đợt 1 (CP2 · ngày xem `27/11/2026`) — Hệ thống Điện máy XANH / Thế Giới Di Động (60 review, 20 review/SP):**
    1. **SP01 — Nồi chiên không dầu Sunhouse 9 lít SHD4035** (2.259.000đ · 4.9/5 sao, 99,7% 5★ · 371 đánh giá hiển thị) — Điện máy XANH: `https://www.dienmayxanh.com/noi-chien-khong-dau/sunhouse-shd4035-9-lit/danh-gia`
    2. **SP02 — Tai nghe Bluetooth Apple AirPods 4 (MXP63)** (2.810.000đ · 4.9/5 sao, 99,9% 5★ · 48 đánh giá hiển thị) — Thế Giới Di Động: `https://www.thegioididong.com/tai-nghe/airpods-4-mxp63/danh-gia`
    3. **SP03 — Pin sạc dự phòng Polymer 20000mAh 10.5W AVA+ Q7** (350.000đ · 4.9/5 sao, 99,9% 5★ · 73 đánh giá hiển thị) — Thế Giới Di Động: `https://www.thegioididong.com/sac-dtdd/pin-sac-du-phong-polymer-20000mah-10-5w-ava-plus-q7/danh-gia`
  - **Đợt 2 (CP3 · ngày xem `28/11/2026`) — Sàn TMĐT mở Tiki.vn (90 review, 30 review/SP):**
    4. **SP04 — Chuột không dây Bluetooth Logitech Signature M650 - Hàng chính hãng** (678.000đ · 4.8/5 sao, 91,0% 5★ · 849 đánh giá trong API / 787 hiển thị gian hàng) — Tiki: `https://tiki.vn/chuot-khong-day-bluetooth-logitech-signature-m650-hang-chinh-hang-p176899932.html` (API công khai: `https://tiki.vn/api/v2/reviews?limit=20&sort=id|desc&product_id=176899932`)
    5. **SP05 — Bình Giữ Nhiệt Bằng Thép Không Gỉ Lock&Lock Vacuum Bottle LHC6180SLV (800ML)** (440.220đ · 4.7/5 sao, 83,0% 5★ · 8.092 đánh giá trong API / 7.121 hiển thị gian hàng) — Tiki: `https://tiki.vn/binh-giu-nhiet-bang-thep-khong-gi-lock-lock-vacuum-bottle-lhc6180slv-800ml-p73124602.html` (API công khai: `https://tiki.vn/api/v2/reviews?limit=20&sort=id|desc&product_id=73124602`)
    6. **SP06 — Bàn Ủi Hơi Nước Philips STH3010/70 (1000W) - Hàng Chính Hãng** (784.917đ · 4.7/5 sao, 81,0% 5★ · 271 đánh giá trong API / 199 hiển thị gian hàng) — Tiki: `https://tiki.vn/ban-ui-hoi-nuoc-philips-sth3010-70-1000w-hang-chinh-hang-p81676555.html` (API công khai: `https://tiki.vn/api/v2/reviews?limit=20&sort=id|desc&product_id=81676555`)
- **Đếm gì · trên tập nào · lọc gì:**
  - **Quy tắc lấy mẫu không chọn lọc:** Đợt 1 lấy trọn 20 đánh giá đầu tiên (trang 1, xếp `"Mới nhất"`). Đợt 2 lấy trọn 30 đánh giá mới nhất đầu tiên (`sort=id|desc`, trang 1 lấy 20 + trang 2 lấy 10 đầu), **không chọn lọc** trước khi gán nhãn.
  - Phân mỗi đánh giá vào đúng 1 trong 2 nhóm lớn và 9 nhãn con (định nghĩa đầy đủ ở [`data/CONTRACT.md`](../data/CONTRACT.md) §2):
    - **Nhiễu / không phản ánh chất lượng SP (`nhieu`):**
      - `nhieu_trong`: chỉ bấm sao/ảnh hoặc tiêu đề mặc định của sàn, văn bản bình luận rỗng.
      - `nhieu_khen_chung`: khen siêu ngắn/chung chung (`"Tốt"`, `"Ok"`, `"Sài ổn"`, `"Xài ngon"`) không nêu thuộc tính vận hành cụ thể.
      - `nhieu_hoi_dap_rao_ban`: hỏi chính sách thu cũ/đổi trả, hỏi cách cài đặt, rao pass lại.
      - `nhieu_ngoai_chat_luong`: chỉ nói về giao hàng/ship, khen sàn, đóng gói nguyên seal, giá/KM, thái độ nhân viên, lệch ngày bảo hành, tự đánh rơi, thiếu phụ kiện không kèm hộp.
      - `nhieu_chua_dung`: mới nhận/mới mở hộp, tự ghi chưa dùng hoặc chưa biết chất lượng ra sao.
      - `nhieu_nhan_xu`: đánh giá đối phó để nhận xu/thưởng sàn.
      - `nhieu_lap_bat_thuong`: lặp nội dung nguyên văn bất thường (≥8 ký tự chuẩn hoá) trong cùng sản phẩm.
    - **Có thông tin chất lượng SP (`co_thong_tin`):**
      - `co_thong_tin_rui_ro`: mô tả lỗi, hạn chế hoặc rủi ro chất lượng/độ bền/an toàn/tương thích/lệch mô tả cụ thể của bản thân sản phẩm.
      - `co_thong_tin_tich_cuc`: mô tả trải nghiệm tốt kèm ít nhất 1 chi tiết vận hành cụ thể.
  - Đồng thời đo **độ lệch giữa điểm sao hiển thị và rủi ro thật**, và trên tập Tiki (có sao từng dòng review) kiểm tra **tỷ lệ rủi ro/hạn chế thật nằm trong review 4–5★** để kiểm chứng cách giải thích thay thế ở `evidence/hypothesis.md` ("chỉ cần bấm bộ lọc 1–2 sao là đủ").
- **Mẫu số là gì:** `N = 150` đánh giá công khai mới nhất (`60` review Đợt 1 ĐMX/TGDĐ + `90` review Đợt 2 Tiki). Không dùng con số "khách hài lòng" ẩn danh không có văn bản làm mẫu số.
- **Script / công thức tái lập:** Chạy `python evidence/count.py` từ thư mục gốc repo (tự động kiểm tra đủ 150/150 cặp mã khớp nhau, 0 lỗi rò rỉ PII, đối chiếu quy tắc trống/không trống và đếm cặp lặp nguyên văn ≥8 ký tự).

## 2. Đọc trước, đếm sau

Đã đọc toàn bộ `150` đánh giá (60 dòng ĐMX/TGDĐ + 90 dòng Tiki) trước khi chốt nhãn. Bốn *kiểu* hành vi nổi bật thấy rõ khi so sánh 2 hệ sinh thái sàn:

- **Tỷ lệ review trống bùng nổ trên sàn TMĐT mở Tiki (68,9% so với 16,7% ở ĐMX/TGDĐ):** Trên cả 3 sản phẩm Tiki, 62/90 đánh giá mới nhất không hề có chữ — chỉ có điểm sao và tiêu đề mặc định do sàn tự điền (`"Cực kì hài lòng"` / `"Hài lòng"`). Điều này khiến trang review bị kéo dài bởi hàng chục dòng không mang thông tin sử dụng.
- **Nhiễu "mới nhận / chưa dùng" và "chỉ khen giao hàng/sàn" xuất hiện rõ trên Tiki (`6/90` trong đó có chữ là `6/28 = 21,4%`):** Người mua nhận hàng sau 1 giờ–1 ngày đã bấm 5★ và viết *"mới dùng không biết có nóng lâu không"* (`SP05 [R10]`), *"chất lượng để sài 1 thời gian"* (`SP05 [R27]`), *"dùng thời gian sẽ đánh giá chất lượng"* (`SP06 [R08]`), hoặc chỉ khen *"Giao nhanh á"* (`SP04 [R01]`).
- **Vì sao `nhieu_nhan_xu = 0/150` và `nhieu_lap_bat_thuong = 0/150` trong mẫu này:** Cả ĐMX/TGDĐ và Tiki không có cơ chế bắt viết ≥50 ký tự kèm ảnh để nhận xu như Shopee; do đó người mua không muốn viết sẽ **bấm sao để trống văn bản** (48,0% toàn tập; 68,9% trên Tiki) thay vì sao chép văn bản đối phó. Ngoài ra 3 SP Tiki đều bán bởi gian hàng chính hãng `Tiki Trading`, chưa phản ánh nhóm gian hàng trôi nổi dễ có lặp nội dung bất thường.
- **Bấm bộ lọc 1–2 sao là KHÔNG ĐỦ để thấy hết rủi ro:** Trên Tiki (`N = 90`), 87/90 (96,7%) review là 4–5★ (trong đó 73/87 = **83,9% là nhiễu**), chỉ có 3/90 review là 1–3★. Đáng chú ý, **3/6 (50,0%) phản ánh hạn chế/rủi ro thật nằm ẩn trong đánh giá 4–5★**: lệch màu so với ảnh hộp (`SP05 [R23]`, 5★), chỉ ủi phẳng vải dễ ủi (`SP06 [R20]`, 4★), dùng không tiện/mỏi tay (`SP06 [R28]`, 4★). Còn ở ĐMX/TGDĐ, cả 3/3 sản phẩm đều hiển thị **4.9/5 (99,7%–99,9% 5★)** dù 26/60 (43,3%) review mới nhất nêu lỗi nặng (bong sơn rỉ sét, phồng pin, hỏng 1 bên tai).

## 3. Kết quả

### 3.1. Tổng hợp toàn tập (`N = 150` · tái lập bằng `python evidence/count.py`)

| Đếm gì | Toàn tập (`N = 150`) | Đợt 1 · ĐMX/TGDĐ (`N = 60`) | Đợt 2 · Tiki (`N = 90`) | Ghi chú |
|---|---|---|---|---|
| **Tổng NHIỄU / không phản ánh chất lượng SP** | **101 / 150 (67.3%)** | 28 / 60 (46.7%) | 73 / 90 (81.1%) | **Vượt ngưỡng giả thuyết** (≥100 review & ≥40% nhiễu) |
| ↳ Review trống / không có văn bản (`nhieu_trong`) | 72 / 150 (48.0%) | 10 / 60 (16.7%) | 62 / 90 (68.9%) | Chiếm tỷ trọng lớn nhất, đặc biệt trên Tiki |
| ↳ Ngoài chất lượng kỹ thuật SP (`nhieu_ngoai_chat_luong`) | 11 / 150 (7.3%) | 8 / 60 (13.3%) | 3 / 90 (3.3%) | Khen ship (`SP04 [R01]`), khen sàn, nguyên seal, giá/KM, NV, lệch BH, tự rơi |
| ↳ Khen ngắn chung chung (`nhieu_khen_chung`) | 10 / 150 (6.7%) | 5 / 60 (8.3%) | 5 / 90 (5.6%) | `"Tốt"`, `"Ok"`, `"Sài ổn"`, `"Xài ngon"`, `"Oke ạ"` |
| ↳ Hỏi đáp chính sách / rao pass (`nhieu_hoi_dap_rao_ban`) | 5 / 150 (3.3%) | 5 / 60 (8.3%) | 0 / 90 (0.0%) | Tập trung ở `SP02` (TGDĐ có ô bình luận mở kèm trả lời QTV) |
| ↳ Mới nhận / chưa dùng (`nhieu_chua_dung`) | 3 / 150 (2.0%) | 0 / 60 (0.0%) | 3 / 90 (3.3%) | Chấm 5★ sau 1 giờ–1 ngày, tự ghi chờ dùng mới biết chất lượng |
| ↳ Nhận xu đối phó (`nhieu_nhan_xu`) | 0 / 150 (0.0%) | 0 / 60 (0.0%) | 0 / 90 (0.0%) | ĐMX/TGDĐ & Tiki không thưởng xu theo độ dài chữ như Shopee |
| ↳ Lặp nội dung bất thường (`nhieu_lap_bat_thuong`) | 0 / 150 (0.0%) | 0 / 60 (0.0%) | 0 / 90 (0.0%) | 0 cặp lặp nguyên văn ≥8 ký tự (kiểm tự động trên 6 SP chính hãng) |
| **Tổng CÓ THÔNG TIN chất lượng SP** | **49 / 150 (32.7%)** | 32 / 60 (53.3%) | 17 / 90 (18.9%) | Phần lõi người mua cần đọc trước khi chốt đơn |
| ↳ Phản ánh rủi ro / lỗi / hạn chế thật (`co_thong_tin_rui_ro`) | 32 / 150 (21.3%) | 26 / 60 (43.3%) | 6 / 90 (6.7%) | Bị che khuất dưới điểm hiển thị 4.7–4.9/5 (81%–99,9% 5★) |
| ↳ Phản ánh tích cực chi tiết (`co_thong_tin_tich_cuc`) | 17 / 150 (11.3%) | 6 / 60 (10.0%) | 11 / 90 (12.2%) | Có ≥1 chi tiết vận hành cụ thể (êm, giữ nhiệt lâu, chiên nhanh…) |

*Lưu ý bổ sung nếu chỉ xét riêng các đánh giá **có văn bản** (`78/150` dòng không trống): tỷ lệ nhiễu văn bản vẫn là **29/78 (37,2%)** toàn tập — và riêng trên Tiki là **11/28 (39,3%)**.*

### 3.2. Phân rã theo từng sản phẩm (`SP01–SP06`)

| Mã | Sản phẩm (sàn · giá lúc xem) | Điểm hiển thị | Nhiễu | Rủi ro/hạn chế thật | Tích cực chi tiết | Rủi ro / hạn chế nổi bật |
|---|---|---|---|---|---|---|
| `SP01` | Sunhouse 9L SHD4035 (ĐMX · 2.259.000đ) | 4.9/5 · 99,7% 5★ | 13/20 (65.0%) | 4/20 (20.0%) | 3/20 (15.0%) | Bong sơn & rỉ sét đáy nồi (`[R07]`), hỏng sau 2 lần (`[R01]`), vỏ nóng & mùi nhựa (`[R05]`, `[R06]`) |
| `SP02` | Apple AirPods 4 MXP63 (TGDĐ · 2.810.000đ) | 4.9/5 · 99,9% 5★ | 10/20 (50.0%) | 8/20 (40.0%) | 2/20 (10.0%) | Hỏng sạc/hỏng 1 bên/mất kết nối (`[R02]`, `[R04]`, `[R15]`, `[R16]`), rè/lọt âm (`[R05]`, `[R07]`, `[R20]`), dễ rơi (`[R01]`) |
| `SP03` | Pin sạc dự phòng AVA+ Q7 (TGDĐ · 350.000đ) | 4.9/5 · 99,9% 5★ | 5/20 (25.0%) | 14/20 (70.0%) | 1/20 (5.0%) | Sạc rất chậm 6–16h (`[R04]`, `[R05]`, `[R08]`, `[R13]`–`[R16]`, `[R18]`), hỏng/phồng pin (`[R01]`, `[R07]`, `[R19]`), tụt pin ảo (`[R08]`, `[R09]`, `[R14]`) |
| `SP04` | Chuột Logitech Signature M650 (Tiki · 678.000đ) | 4.8/5 · 91,0% 5★ | 22/30 (73.3%) | 2/30 (6.7%) | 6/30 (20.0%) | Mất kết nối khi để nghỉ phải bật tắt lại (`[R07]`, 1★), lỗi không nhận đầu USB đổi trả 2 lần (`[R27]`, 2★) |
| `SP05` | Bình giữ nhiệt Lock&Lock LHC6180SLV (Tiki · 440.220đ) | 4.7/5 · 83,0% 5★ | 26/30 (86.7%) | 1/30 (3.3%) | 3/30 (10.0%) | Màu thực tế (xanh đậm gần tím nhạt) khác hình trên hộp dù khách chấm 5★ (`[R23]`) |
| `SP06` | Bàn ủi hơi nước Philips STH3010/70 (Tiki · 784.917đ) | 4.7/5 · 81,0% 5★ | 25/30 (83.3%) | 3/30 (10.0%) | 2/30 (6.7%) | Phun nước giọt lớn, ủi không thẳng (`[R29]`, 2★); chỉ ủi phẳng vải dễ ủi (`[R20]`, 4★); cầm không tiện, mỏi tay (`[R28]`, 4★) |

### 3.3. Phân bố theo số sao từng review trên Tiki (`SP04–SP06`, `N = 90`)

| Nhóm sao | Số review (`x/90`) | Nhiễu trong nhóm | Rủi ro/hạn chế thật | Ghi chú kiểm chứng giả thuyết |
|---|---|---|---|---|
| **4–5★** | 87 / 90 (96.7%) | **73 / 87 (83.9%)** | **3 / 6 (50.0% tổng rủi ro)** | `SP05 [R23]` (5★), `SP06 [R20]` (4★), `SP06 [R28]` (4★) đều bị bỏ sót nếu người mua chỉ lọc 1–2★ |
| **1–3★** | 3 / 90 (3.3%) | 0 / 3 (0.0%) | 3 / 6 (50.0% tổng rủi ro) | `SP04 [R07]` (1★), `SP04 [R27]` (2★), `SP06 [R29]` (2★) |

## 4. Ví dụ cụ thể nguyên văn (10 ví dụ đa sàn, đã ẩn danh, kèm mã nguồn)

1. **`SP01 [R03]` (ĐMX) — Nhiễu trống (`nhieu_trong`):** `""` *(chỉ chấm sao, không có chữ — chiếm 72/150 = 48,0% toàn tập và 62/90 = 68,9% trên Tiki)*.
2. **`SP04 [R01]` (Tiki, 5★) — Nhiễu chỉ khen giao hàng (`nhieu_ngoai_chat_luong`):** `"Giao nhanh á"` *(chỉ khen tốc độ giao hàng, không cung cấp thông tin về độ bền hay kết nối chuột)*.
3. **`SP05 [R10]` (Tiki, 5★, đã dùng 1 ngày) — Nhiễu chưa dùng (`nhieu_chua_dung`):** `"Bình đẹp mới dùng không biết có nóng lâu không"` *(chấm 5★ khi chưa kiểm chứng chức năng cốt lõi là giữ nhiệt)*.
4. **`SP06 [R08]` (Tiki, 5★, đã dùng 1 giờ) — Nhiễu chưa dùng (`nhieu_chua_dung`):** `"Hàng Philips xịn xò, chi tiết nào cũng đẹp , màu đẹp, dùng tiện lợi, dùng thời gian sẽ đánh giá chất lượng. Cám ơn Tiki và Philips"` *(đánh giá 5★ sau đúng 1 giờ nhận hàng)*.
5. **`SP02 [R10]` (TGDĐ) — Nhiễu rao pass lại (`nhieu_hoi_dap_rao_ban`):** *"Rao pass lại sau 3 ngày dùng vì tai nhỏ đeo không vừa (đã ẩn thông tin liên hệ Zalo)"* *(bài gốc đăng trực tiếp số Zalo cá nhân ở mục đánh giá sản phẩm)*.
6. **`SP03 [R03]` (TGDĐ) — Nhiễu giá/khuyến mãi (`nhieu_ngoai_chat_luong`):** *"Phàn nàn chương trình mua 1 tặng 1 giá 590k tại cửa hàng trong khi giá lẻ trực tuyến khoảng 295k/cái"* *(khiếu nại giá bán, không phản ánh chất lượng pin)*.
7. **`SP01 [R07]` (ĐMX) — Rủi ro độ bền (`co_thong_tin_rui_ro`):** `"Sài được có 2 tháng bong sơn ở đáy nồi, mấy chỗ bong có dấu hiệu rỉ set"` *(bị chôn dưới điểm hiển thị 4.9/5 · 99,7% 5★)*.
8. **`SP03 [R07]` (TGDĐ) — Rủi ro an toàn (`co_thong_tin_rui_ro`):** *"Dùng mới gần 9 tháng pin dự phòng đã bị phồng nhẹ, không dám dùng tiếp"* *(bị chôn dưới điểm 4.9/5 · 99,9% 5★)*.
9. **`SP04 [R27]` (Tiki, 2★) — Rủi ro lỗi lặp lại phải đổi trả (`co_thong_tin_rui_ro`):** `"Sản phẩm bị lỗi không nhận tín hiều bằng đầu usb .Đổi trả 2 lần, lần này là lần thứ 3. Nếu sản phẩm bị lỗi nữa xin ko bao giờ mua hàng này nữa."` *(cùng cụm lỗi kết nối với `SP04 [R07]` trên chuột 4.8★)*.
10. **`SP06 [R20]` (Tiki, 4★) & `SP05 [R23]` (Tiki, 5★) — Rủi ro/hạn chế ẩn trong 4–5★ (`co_thong_tin_rui_ro`):** `"Ủi phẳng một số vải dễ ủi thôi nhé."` (`SP06 [R20]`, 4★) và `"Chỉ tiếc là màu bình (xanh đậm) không được như kỳ vọng, khác với màu hình trên hộp..."` (`SP05 [R23]`, 5★) — minh hoạ rủi ro bị bỏ sót nếu chỉ lọc 1–2★.

## 5. Giới hạn của data

- **Chưa đào trực tiếp từ Shopee / TikTok Shop:** Do Shopee và TikTok Shop yêu cầu đăng nhập / trả HTTP 403 khi truy cập phân trang đánh giá công khai, dữ liệu `N = 150` kết hợp hai nguồn mở truy cập hợp lệ là **Điện máy XANH / Thế Giới Di Động** (`60` review) và **Tiki.vn** (`90` review). Vì hai hệ sinh thái này không thưởng xu theo độ dài ký tự như Shopee, tỷ lệ `nhieu_nhan_xu` và `nhieu_lap_bat_thuong` trong mẫu hiện bằng `0/150`; không suy diễn ngược sang Shopee khi chưa có mẫu Shopee xác minh.
- **Lệch gian hàng chính hãng và thứ tự "Mới nhất":** Cả 3 sản phẩm Tiki thuộc `Tiki Trading` (gian hàng chính hãng) và đều lấy theo thứ tự mới nhất (`sort=id|desc`), nên tỷ lệ lỗi nặng trên Tiki thấp hơn nhóm gian hàng bên thứ ba không kiểm duyệt, còn trên ĐMX/TGDĐ trang mới nhất có xu hướng tập trung phản ánh lỗi nhiều hơn trung bình lịch sử.
- **Độ tin cậy gán nhãn:** 60/60 nhãn đợt 1 (`evidence/cp2_labels.csv`) đã được Nguyễn Khánh Vinh kiểm tay (khai báo tại `docs/ai-usage.md`). 90 nhãn đợt 2 (`evidence/cp3_labels.csv`) được gán theo đúng bộ quy tắc `data/CONTRACT.md` với hỗ trợ của coding agent và qua kiểm tra toàn vẹn tự động (`evidence/count.py`), cần Nguyễn Khánh Vinh rà lại 90/90 dòng trước khi khoá CP4.
- **Data cho biết nội dung đánh giá có gì, không cho biết người mua tốn bao nhiêu phút hay bỏ sót lỗi ra sao:**
  → **Kiểm lại bằng:** Phỏng vấn sâu người mua ngoài nhóm (`evidence/interviews/P1.md`–`P4.md` và `evidence/pain_evidence-summary.md`, do Hải Yến tiếp tục bổ sung P5 + số phút/tần suất ở Issue #6).
