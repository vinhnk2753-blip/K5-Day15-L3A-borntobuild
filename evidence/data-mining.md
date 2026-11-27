# Đào data — cách đếm và kết quả (Đợt 1 · CP2)

> Bản đầu CP2 (27/11/2026) · Phụ trách: Nguyễn Khánh Vinh (`@vinhnk2753-blip`).
> Script đếm tái lập được trong repo: [`evidence/count.py`](count.py) · Bảng nhãn kiểm chứng: [`evidence/cp2_labels.csv`](cp2_labels.csv) · Dữ liệu đã ẩn danh: [`data/catalog.json`](../data/catalog.json) và `data/products/*.json`.
> Đợt 2 (CP3, Issue #5) sẽ mở rộng cỡ mẫu lên ≥100–150 đánh giá và bổ sung sàn mở (Shopee/Tiki/Lazada).

## 1. Cách đếm — viết TRƯỚC khi chạy

- **Data dùng (ngày xem: `27/11/2026`):** Đánh giá công khai của **3 sản phẩm phổ biến có giá bán ≥200.000đ** thuộc 3 ngành hàng khác nhau (Gia dụng bếp · Tai nghe không dây · Phụ kiện sạc dự phòng):
  1. **SP01 — Nồi chiên không dầu Sunhouse 9 lít SHD4035** (giá 2.259.000đ · giá gốc 3.670.000đ · 4.9/5 sao, 99,7% 5★ · 69,8k khách hài lòng · 371 đánh giá hiển thị) — Điện máy XANH: `https://www.dienmayxanh.com/noi-chien-khong-dau/sunhouse-shd4035-9-lit/danh-gia`
  2. **SP02 — Tai nghe Bluetooth Apple AirPods 4 (MXP63)** (giá 2.810.000đ · giá gốc 3.790.000đ · 4.9/5 sao, 99,9% 5★ · 65,7k khách hài lòng · 48 đánh giá hiển thị) — Thế Giới Di Động: `https://www.thegioididong.com/tai-nghe/airpods-4-mxp63/danh-gia`
  3. **SP03 — Pin sạc dự phòng Polymer 20000mAh 10.5W AVA+ Q7** (giá 350.000đ · giá gốc 590.000đ · 4.9/5 sao, 99,9% 5★ · 597,3k khách hài lòng · 73 đánh giá hiển thị) — Thế Giới Di Động: `https://www.thegioididong.com/sac-dtdd/pin-sac-du-phong-polymer-20000mah-10-5w-ava-plus-q7/danh-gia`
- **Đếm gì · trên tập nào · lọc gì:**
  - Lấy trọn **20 đánh giá đầu tiên (trang 1, sắp xếp "Mới nhất")** của mỗi sản phẩm — **không chọn lọc** trước khi gán nhãn.
  - Phân mỗi đánh giá vào đúng 1 trong 2 nhóm lớn và 6 nhãn con (chi tiết định nghĩa ở [`data/CONTRACT.md`](../data/CONTRACT.md) §2):
    - **Nhiễu / không phản ánh chất lượng SP (`nhieu`):** `nhieu_trong` (chỉ bấm sao/ảnh, văn bản rỗng) · `nhieu_khen_chung` (khen siêu ngắn/chung chung không nêu thuộc tính vận hành cụ thể) · `nhieu_hoi_dap_rao_ban` (hỏi thu cũ đổi mới, hỏi hướng dẫn cài đặt, rao pass lại) · `nhieu_ngoai_chat_luong` (phàn nàn giá/KM, thái độ nhân viên, đóng gói/giao hàng, lệch ngày bảo hành, tự đánh rơi, thiếu phụ kiện vốn không kèm hộp).
    - **Có thông tin chất lượng SP (`co_thong_tin`):** `co_thong_tin_rui_ro` (mô tả lỗi/hạn chế/rủi ro cụ thể của sản phẩm) · `co_thong_tin_tich_cuc` (mô tả trải nghiệm tốt kèm ít nhất 1 chi tiết vận hành cụ thể).
  - Đồng thời so sánh **điểm sao hiển thị trên trang sản phẩm** với **tỷ lệ đánh giá nêu rủi ro/lỗi thật** trong trang 1 mới nhất.
- **Mẫu số là gì:** `N = 60` đánh giá hiển thị công khai trên trang 1 mới nhất (`20 đánh giá/sản phẩm × 3 sản phẩm`). Không dùng số "khách hài lòng" ẩn danh hàng chục nghìn người trên tiêu đề trang làm mẫu số vì không có văn bản để kiểm chứng.
- **Script / công thức tái lập:** Chạy lệnh `python3 evidence/count.py` từ thư mục gốc repo (đọc `data/catalog.json`, `data/products/*.json` và `evidence/cp2_labels.csv`; tự động kiểm tra đủ 60/60 dòng và 0 lỗi rò rỉ PII).

## 2. Đọc trước, đếm sau

Đã đọc toàn bộ `60` đánh giá trang 1 của 3 sản phẩm (20 dòng/SP) trước khi chốt bộ nhãn. Các *kiểu* hành vi nổi bật thấy được:
- **Review trống chiếm tỷ trọng lớn ở hàng gia dụng:** trên SP01 (Sunhouse SHD4035), 7/20 đánh giá không hề có chữ (chỉ bấm sao), kèm 5/20 khen cực ngắn kiểu `"Tốt"`, `"Sài ổn"`.
- **Mục đánh giá bị dùng như mục Hỏi–Đáp và chợ pass hàng:** trên SP02 (AirPods 4), người mua hỏi chính sách thu cũ đổi mới, hỏi cách cài giọng đọc tiếng Việt, thậm chí đăng tin rao pass lại tai nghe kèm số Zalo cá nhân (đã ẩn khi đưa vào `data/`).
- **Khiếu nại dịch vụ/giá/khuyến mãi trộn lẫn với lỗi kỹ thuật:** xuất hiện phàn nàn chương trình "mua 1 tặng 1", chênh lệch giá web–cửa hàng, nhân viên bóc tem cẩu thả, shipper không bỏ túi bóng, lệch ngày hết hạn bảo hành hệ thống.
- **Độ lệch nghiêm trọng giữa điểm sao hiển thị và lỗi lặp lại thật:** cả 3/3 sản phẩm đều hiển thị **4.9/5 (99,7%–99,9% 5★)**, nhưng ngay trang 1 mới nhất lại tập trung nhiều lỗi nghiêm trọng lặp lại (bong sơn & rỉ sét đáy nồi, phồng pin sau 9 tháng, sạc vào 10–16 tiếng chưa đầy, hỏng 1 bên tai nghe, rè âm thanh).

## 3. Kết quả

### 3.1. Tổng hợp toàn tập đợt 1 (`N = 60`)

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| **Tổng NHIỄU / không phản ánh chất lượng SP** | **28 / 60** | **46.7%** | Bước đầu vượt ngưỡng giả thuyết ≥40% (`evidence/hypothesis.md`) |
| ↳ Review trống / không có văn bản (`nhieu_trong`) | 10 / 60 | 16.7% | Tập trung mạnh ở SP01 (7/20) |
| ↳ Khen ngắn chung chung (`nhieu_khen_chung`) | 5 / 60 | 8.3% | Vd `"Tốt"`, `"Sài ổn"`, khen chung không nêu chi tiết |
| ↳ Hỏi đáp chính sách / hướng dẫn / rao pass (`nhieu_hoi_dap_rao_ban`) | 5 / 60 | 8.3% | Tập trung ở SP02 (5/20, gồm 1 bài rao pass kèm Zalo) |
| ↳ Ngoài chất lượng kỹ thuật SP (`nhieu_ngoai_chat_luong`) | 8 / 60 | 13.3% | Giá/KM, thái độ NV, đóng gói giao hàng, lệch ngày BH, tự làm rơi |
| **Tổng CÓ THÔNG TIN chất lượng SP** | **32 / 60** | **53.3%** | Phần lõi người mua cần đọc trước khi chốt đơn |
| ↳ Có phản ánh rủi ro / lỗi thật (`co_thong_tin_rui_ro`) | 26 / 60 | 43.3% | Bị che khuất dưới điểm hiển thị 4.9/5 (99,7%–99,9% 5★) |
| ↳ Có phản ánh tích cực chi tiết (`co_thong_tin_tich_cuc`) | 6 / 60 | 10.0% | Có ít nhất 1 chi tiết vận hành cụ thể (chiên nhanh, pin lâu, mát…) |

### 3.2. Phân rã theo từng sản phẩm (`20 review/SP`)

| Mã | Sản phẩm (giá ngày 27/11/2026) | Điểm hiển thị | Nhiễu | Rủi ro/lỗi thật | Tích cực chi tiết | Rủi ro lặp lại nổi bật |
|---|---|---|---|---|---|---|
| `SP01` | Sunhouse 9L SHD4035 (2.259.000đ) | 4.9/5 · 99,7% 5★ | 13/20 (65.0%) | 4/20 (20.0%) | 3/20 (15.0%) | Bong sơn & rỉ sét đáy nồi (`[R07]`), hỏng sau 2 lần dùng (`[R01]`), vỏ nóng & mùi nhựa (`[R05]`, `[R06]`) |
| `SP02` | Apple AirPods 4 MXP63 (2.810.000đ) | 4.9/5 · 99,9% 5★ | 10/20 (50.0%) | 8/20 (40.0%) | 2/20 (10.0%) | Lỗi sạc/hỏng 1 bên/mất kết nối (`[R02]`, `[R04]`, `[R15]`, `[R16]`), rè/lọt âm (`[R05]`, `[R07]`, `[R20]`), đeo lỏng dễ rơi (`[R01]`) |
| `SP03` | Pin sạc dự phòng AVA+ Q7 (350.000đ) | 4.9/5 · 99,9% 5★ | 5/20 (25.0%) | 14/20 (70.0%) | 1/20 (5.0%) | Sạc vào/ra rất chậm 6–16h (`[R04]`, `[R05]`, `[R08]`, `[R13]`–`[R16]`, `[R18]`), hỏng/phồng pin (`[R01]`, `[R07]`, `[R19]`), hụt dung lượng/tụt pin ảo (`[R08]`, `[R09]`, `[R14]`) |

## 4. ≥5 ví dụ cụ thể (đã ẩn danh, kèm mã nguồn)

1. **`SP01 [R03]` — Nhiễu trống (`nhieu_trong`):** `""` *(chỉ chấm sao, không có bình luận văn bản — 7/20 đánh giá trang 1 của Sunhouse SHD4035 thuộc dạng này)*.
2. **`SP01 [R14]` — Nhiễu khen siêu ngắn (`nhieu_khen_chung`):** `"Sài ổn"` *(2 từ, không cung cấp thông tin độ bền, nhiệt độ hay nhược điểm)*.
3. **`SP02 [R10]` — Nhiễu rao pass lại (`nhieu_hoi_dap_rao_ban`):** *"Rao pass lại sau 3 ngày dùng vì tai nhỏ đeo không vừa (đã ẩn thông tin liên hệ Zalo)"* — bài gốc trên TGDĐ đăng trực tiếp số Zalo cá nhân ở mục đánh giá sản phẩm (77 lượt bấm "Hữu ích").
4. **`SP03 [R03]` — Nhiễu ngoài chất lượng sản phẩm (`nhieu_ngoai_chat_luong`):** *"Phàn nàn chương trình mua 1 tặng 1 giá 590k tại cửa hàng trong khi giá lẻ trực tuyến khoảng 295k/cái"* — khiếu nại chính sách giá bán, không phản ánh chất lượng viên pin.
5. **`SP01 [R07]` — Rủi ro chất lượng thật (`co_thong_tin_rui_ro`):** `"Sài được có 2 tháng bong sơn ở đáy nồi, mấy chỗ bong có dấu hiệu rỉ set"` *(Sunhouse SHD4035, 14 lượt bấm "Hữu ích", dù sản phẩm hiển thị 4.9/5 và 99,7% 5★)*.
6. **`SP03 [R07]` — Rủi ro an toàn thật (`co_thong_tin_rui_ro`):** *"Dùng mới gần 9 tháng pin dự phòng đã bị phồng nhẹ, không dám dùng tiếp"* *(AVA+ Q7, bị chôn dưới nhãn 4.9/5 và 99,9% 5★)*.
7. **`SP02 [R04]` — Rủi ro độ bền thật (`co_thong_tin_rui_ro`):** *"Dùng chưa đầy 1 tháng đã hỏng 1 bên tai nghe, gửi đi nhưng bị từ chối bảo hành"* *(AirPods 4 MXP63, cùng cụm lỗi sạc/kết nối 1 bên với `[R02]`, `[R15]`, `[R16]`)*.

## 5. Giới hạn của data

- **Cỡ mẫu đợt 1 chưa đạt ngưỡng cuối:** đợt 1 (CP2) mới đào `N = 60` đánh giá (20/SP × 3 SP), đạt 60% mục tiêu `≥100–150` đánh giá nêu trong `evidence/hypothesis.md`. Issue #5 (CP3) sẽ tiếp tục mở rộng cỡ mẫu.
- **Lệch nguồn sàn & kiểu sắp xếp:** do Shopee và TikTok Shop yêu cầu đăng nhập khi đọc phân trang đánh giá, đợt 1 mới lấy dữ liệu công khai từ Điện máy XANH và Thế Giới Di Động (cùng tập đoàn MWG) ở trang 1 sắp xếp `"Mới nhất"`. Vì vậy đợt 1 **chưa đo trực tiếp** tỷ lệ nhiễu *"đánh giá nhận xu"* hay *"khen shipper"* đặc trưng của Shopee, và trang `"Mới nhất"` có thể có tỷ lệ phản ánh lỗi cao hơn trung bình toàn bộ lịch sử đơn hàng. Đợt 2 (CP3) sẽ bổ sung mẫu từ sàn TMĐT mở (Shopee/Tiki/Lazada) để tránh lệch một nền tảng.
- **Độ tin cậy gán nhãn:** 60 nhãn ở `evidence/cp2_labels.csv` được phân loại sơ bộ theo quy ước `data/CONTRACT.md` với sự hỗ trợ đối chiếu của coding agent; cần Nguyễn Khánh Vinh kiểm tay lại toàn bộ 60 dòng và đối chiếu chéo với thành viên thứ hai trước CP3.
- **Data cho biết nội dung đánh giá có gì, không cho biết người mua tốn bao nhiêu thời gian hay ra quyết định sai ra sao:**
  → **Kiểm lại bằng:** Phỏng vấn sâu `≥3–4` người mua ngoài nhóm (`evidence/interviews/P1.md`… do Hải Yến phụ trách trong #2 và #6) để đo thời gian lọc tay thực tế, tần suất mua sắm/tháng và tình huống từng mua nhầm vì đọc sót review.
