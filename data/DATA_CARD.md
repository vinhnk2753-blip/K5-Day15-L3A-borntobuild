# Data card — dữ liệu bản chạy thử dùng

> Bản đầu **CP2** (27/11/2026) · Phụ trách: Nguyễn Khánh Vinh (`@vinhnk2753-blip`). Sẽ hoàn thiện đủ ở **CP3** (Issue #5).
> Hợp đồng cấu trúc file và I/O chi tiết xem tại [`data/CONTRACT.md`](CONTRACT.md).
> Không commit dữ liệu cá nhân thật (tên người mua, SĐT, Zalo, địa chỉ, ảnh chứa thông tin cá nhân) — chỉ lưu đoạn trích ngắn / bản chuẩn hoá gọn đã ẩn danh và bảng số tổng hợp.

---

## Dataset 1 · Tập review công khai đã ẩn danh đợt 1 (`data/products/*.json`)

| Thuộc tính | Chi tiết |
|---|---|
| **Dùng để làm gì** | (1) Nguồn dữ liệu nền cho công cụ đọc review trong `codebase/tools.py` (#3) và giao diện chọn sản phẩm trong `codebase/app.py` (#4); (2) Nguồn tạo câu thử `data_that` trong `eval/benchmark.csv` (#2); (3) Dữ liệu đào bằng chứng đợt 1 trong `evidence/data-mining.md` (#1). |
| **Từ đâu** | Đánh giá công khai của người đã mua trên 2 website TMĐT/bán lẻ trực tuyến tại Việt Nam (giá bán đều ≥200.000đ):<br>• `SP01`: Nồi chiên không dầu Sunhouse 9L SHD4035 (2.259.000đ) — `https://www.dienmayxanh.com/noi-chien-khong-dau/sunhouse-shd4035-9-lit/danh-gia`<br>• `SP02`: Tai nghe Bluetooth Apple AirPods 4 MXP63 (2.810.000đ) — `https://www.thegioididong.com/tai-nghe/airpods-4-mxp63/danh-gia`<br>• `SP03`: Pin sạc dự phòng Polymer 20000mAh 10.5W AVA+ Q7 (350.000đ) — `https://www.thegioididong.com/sac-dtdd/pin-sac-du-phong-polymer-20000mah-10-5w-ava-plus-q7/danh-gia` |
| **Xử lý những bước gì** | 1. **Lấy mẫu không chọn lọc:** lấy trọn 20 đánh giá đầu tiên (trang 1, xếp theo `"Mới nhất"`) của mỗi sản phẩm.<br>2. **Ẩn danh PII:** xoá toàn bộ tên tài khoản/họ tên người đánh giá; che mọi thông tin liên hệ bên trong nội dung (vd số Zalo tại `SP02 [R10]` → đã ẩn hoàn toàn); kiểm tra tự động bằng regex trong `evidence/count.py` (0 lỗi PII).<br>3. **Chuẩn hoá & đánh mã trích dẫn:** gắn mã tuần tự `R01`–`R20` theo từng sản phẩm; rút gọn/chuẩn hoá các đoạn lan man dài ở `SP02`, `SP03` thành đoạn trích ngắn/bản tóm lược gọn giữ nguyên sự kiện và số liệu gốc; lưu tách riêng dữ liệu sạch (`data/products/*.json`, **không kèm nhãn**) và bảng nhãn thống kê (`evidence/cp2_labels.csv`) để tránh rò rỉ nhãn vào luồng AI.<br>4. **Script đếm & kiểm tra toàn vẹn:** `evidence/count.py`. |
| **Số dòng / số đoạn** | **60 đánh giá** (3 sản phẩm × 20 đánh giá/sản phẩm), tương ứng 3 file JSON trong `data/products/` và chỉ mục `data/catalog.json`. |
| **Phiên bản / ngày lấy** | `cp2-v1` · ngày truy cập & thu thập: **27/11/2026**. |
| **Nhãn** | **Thật** (đánh giá công khai thật từ người đã mua, đã ẩn danh và chuẩn hoá gọn; không dùng dữ liệu `synthetic` ở đợt 1). |
| **Giới hạn** | • Cỡ mẫu đợt 1 mới có `60` đánh giá (chưa đạt mục tiêu `≥100–150` ở CP3).<br>• Cả 3 sản phẩm đợt 1 đều lấy từ hệ thống Điện máy XANH / Thế Giới Di Động (cùng tập đoàn MWG) và chỉ lấy trang 1 `"Mới nhất"` → chưa đại diện cho sàn TMĐT mở như Shopee/TikTok Shop/Lazada (nơi phổ biến nhiễu *"đánh giá nhận xu"*, *"khen shipper"*, lặp nội dung tự động) và có thể nghiêng về các bài khiếu nại gần đây.<br>• Trang `/danh-gia` của ĐMX/TGDĐ không hiển thị số sao riêng của từng bình luận ở dạng văn bản trích xuất mà chỉ hiển thị tỷ lệ sao tổng của sản phẩm (4.9/5, 99,7%–99,9% 5★), nên chưa phân tích được độ lệch sao ở cấp từng dòng review. |

---

## Quy tắc phân loại nhiễu & thông tin thật (áp dụng thống nhất cho #1, #2, #3)

Mỗi đánh giá được gán vào 1 trong 2 nhóm chính (chi tiết định nghĩa ở [`data/CONTRACT.md`](CONTRACT.md) §2):

1. **Nhiễu / không phản ánh chất lượng sản phẩm (`nhieu`) — 28/60 (46,7% ở đợt 1):**
   - `nhieu_trong` *(10/60)*: văn bản trống, chỉ bấm sao hoặc chỉ đăng ảnh không mô tả.
   - `nhieu_khen_chung` *(5/60)*: khen ngắn chung chung (`"Tốt"`, `"Sài ổn"`, `"Sản phẩm rất là ok"`) không nêu chi tiết kỹ thuật hay sử dụng.
   - `nhieu_hoi_dap_rao_ban` *(5/60)*: hỏi chính sách thu cũ đổi mới, hỏi hướng dẫn dùng, hoặc rao pass lại sản phẩm.
   - `nhieu_ngoai_chat_luong` *(8/60)*: chỉ nói về giá/khuyến mãi, thái độ nhân viên, giao hàng/đóng gói, lệch ngày bảo hành, tự đánh rơi hoặc thiếu phụ kiện vốn không kèm hộp.
2. **Có thông tin chất lượng / trải nghiệm sản phẩm (`co_thong_tin`) — 32/60 (53,3% ở đợt 1):**
   - `co_thong_tin_rui_ro` *(26/60)*: nêu lỗi, rủi ro độ bền, an toàn, hiệu năng hoặc tương thích thực tế của sản phẩm.
   - `co_thong_tin_tich_cuc` *(6/60)*: nêu trải nghiệm tích cực kèm ít nhất 1 chi tiết vận hành cụ thể.

---

## Kế hoạch bổ sung cho CP3 (Dataset 2 — Issue #5)

- Mở rộng từ `60` lên **≥100–150 đánh giá** công khai ẩn danh, bổ sung nguồn từ sàn TMĐT mở (Shopee/Tiki/Lazada) để đo thêm 3 dạng nhiễu đặc trưng sàn (`nhieu_nhan_xu`, `nhieu_chua_dung`, `nhieu_lap_bat_thuong`) và kiểm chứng tính tổng quát của bộ lọc nhiễu trước khi chạy eval chính thức.
