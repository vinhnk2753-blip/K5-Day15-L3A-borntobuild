# Data card — dữ liệu bản chạy thử dùng

> Bản hoàn chỉnh **CP3** (28/11/2026) · Phụ trách: Nguyễn Khánh Vinh (`@vinhnk2753-blip`).
> Hợp đồng cấu trúc file và I/O chi tiết xem tại [`data/CONTRACT.md`](CONTRACT.md).
> Không commit dữ liệu cá nhân thật (tên người mua, SĐT, Zalo, địa chỉ, ảnh chứa thông tin cá nhân) — chỉ lưu văn bản đã ẩn danh và bảng số tổng hợp. Kiểm tra toàn vẹn & PII tự động bằng `python evidence/count.py` (**0 lỗi PII trên 150/150 review**).

---

## Tổng quan kho dữ liệu nền (`data/catalog.json` · phiên bản `cp3-v1`)

- **Tổng quy mô:** **150 đánh giá công khai thật đã ẩn danh** từ **6 sản phẩm phổ biến giá ≥200.000đ**, trải đều **6 ngành hàng** trên **2 hệ sinh thái TMĐT tại Việt Nam** (Điện máy XANH / Thế Giới Di Động và Tiki.vn).
- **Tách nhãn để chống rò rỉ vào AI:** Các file trong `data/products/*.json` **không chứa nhãn phân loại**; nhãn gán tay lưu riêng tại `evidence/cp2_labels.csv` (`SP01–SP03`) và `evidence/cp3_labels.csv` (`SP04–SP06`).
- **Bảo toàn tương thích ngược với benchmark & unit test:** Giữ nguyên 100% nội dung và mã `[R01]–[R20]` của `SP01–SP03` và `evidence/cp2_labels.csv` để `eval/benchmark.csv` (`B11–B25`), `eval/run-1.csv`, `eval/run-2.csv` và `codebase/test_agent.py` không bị xáo trộn.

---

## Dataset 1 · Tập review công khai đã ẩn danh đợt 1 (`SP01–SP03` · ĐMX/TGDĐ)

| Thuộc tính | Chi tiết |
|---|---|
| **Dùng để làm gì** | (1) Dữ liệu nền cho `codebase/tools.py` (`load_product_reviews`) và UI demo `codebase/app.py`; (2) Nguồn gốc xây 15 câu thử `data_that` (`B11–B25`) trong `eval/benchmark.csv` và kiểm thử đơn vị `codebase/test_agent.py`; (3) Bằng chứng pain đợt 1 trong `evidence/data-mining.md`. |
| **Từ đâu** | Đánh giá công khai của người đã mua trên 2 website bán lẻ trực tuyến tại Việt Nam (giá bán ≥200.000đ):<br>• `SP01`: Nồi chiên không dầu Sunhouse 9L SHD4035 (2.259.000đ) — `https://www.dienmayxanh.com/noi-chien-khong-dau/sunhouse-shd4035-9-lit/danh-gia`<br>• `SP02`: Tai nghe Bluetooth Apple AirPods 4 MXP63 (2.810.000đ) — `https://www.thegioididong.com/tai-nghe/airpods-4-mxp63/danh-gia`<br>• `SP03`: Pin sạc dự phòng Polymer 20000mAh 10.5W AVA+ Q7 (350.000đ) — `https://www.thegioididong.com/sac-dtdd/pin-sac-du-phong-polymer-20000mah-10-5w-ava-plus-q7/danh-gia` |
| **Xử lý những bước gì** | 1. **Lấy mẫu không chọn lọc:** lấy trọn 20 đánh giá đầu tiên (trang 1, xếp `"Mới nhất"`) của mỗi sản phẩm.<br>2. **Ẩn danh PII:** xoá toàn bộ tên tài khoản/họ tên; che mọi SĐT/Zalo bên trong nội dung (vd số Zalo tại `SP02 [R10]` → đã ẩn hoàn toàn); kiểm regex tự động trong `evidence/count.py` (0 lỗi PII).<br>3. **Chuẩn hoá & đánh mã trích dẫn:** gắn mã tuần tự `R01`–`R20` theo từng sản phẩm; rút gọn các đoạn lan man dài ở `SP02`, `SP03` thành đoạn trích gọn giữ nguyên sự kiện và số liệu gốc; lưu tách nhãn vào `evidence/cp2_labels.csv`. |
| **Số dòng / số đoạn** | **60 đánh giá** (3 sản phẩm × 20 đánh giá/sản phẩm) trong `data/products/sunhouse_shd4035.json`, `airpods_4_mxp63.json`, `ava_plus_q7.json`. |
| **Phiên bản / ngày lấy** | `cp2-v1` (giữ nguyên trong `cp3-v1`) · ngày truy cập: **27/11/2026**. |
| **Nhãn** | **Thật** (đánh giá công khai thật từ người đã mua, đã ẩn danh; không dùng `synthetic`). |
| **Giới hạn** | • Cùng hệ thống bán lẻ MWG (ĐMX/TGDĐ), không phải sàn TMĐT mở nhiều gian hàng.<br>• Trang `/danh-gia` không xuất số sao riêng của từng bình luận ở dạng text mà chỉ có điểm sao tổng sản phẩm (4.9/5 · 99,7%–99,9% 5★).<br>• Xếp `"Mới nhất"` có thể tập trung khiếu nại gần đây nhiều hơn trung bình toàn bộ lịch sử đơn hàng. |

---

## Dataset 2 · Tập review công khai đã ẩn danh đợt 2 (`SP04–SP06` · Sàn TMĐT Tiki)

| Thuộc tính | Chi tiết |
|---|---|
| **Dùng để làm gì** | (1) Mở rộng cỡ mẫu bằng chứng đào data từ `60` lên **`150` đánh giá** vượt ngưỡng giả thuyết `≥100–150` (`evidence/data-mining.md`); (2) Bổ sung dữ liệu có **số sao từng dòng review (`rating_star`)** từ sàn TMĐT mở Việt Nam để kiểm tra tỷ lệ nhiễu trên 4–5★, phát hiện rủi ro ẩn trong 4–5★ và kiểm tra độ tổng quát ngoài mẫu của `filter_review_noise` trong `codebase/tools.py`; (3) Mở rộng danh mục tra cứu mẫu trong `data/catalog.json` cho demo CLI/UI. |
| **Từ đâu** | Đánh giá công khai qua API đọc mở của sàn TMĐT **Tiki.vn** (không cần đăng nhập, giá bán ≥200.000đ, 3 ngành hàng mới):<br>• `SP04`: Chuột không dây Bluetooth Logitech Signature M650 (678.000đ) — `https://tiki.vn/chuot-khong-day-bluetooth-logitech-signature-m650-hang-chinh-hang-p176899932.html`<br>• `SP05`: Bình giữ nhiệt thép không gỉ Lock&Lock Vacuum Bottle LHC6180SLV 800ML (440.220đ) — `https://tiki.vn/binh-giu-nhiet-bang-thep-khong-gi-lock-lock-vacuum-bottle-lhc6180slv-800ml-p73124602.html`<br>• `SP06`: Bàn ủi hơi nước Philips STH3010/70 1000W (784.917đ) — `https://tiki.vn/ban-ui-hoi-nuoc-philips-sth3010-70-1000w-hang-chinh-hang-p81676555.html` |
| **Xử lý những bước gì** | 1. **Lấy mẫu không chọn lọc:** lấy trọn 30 đánh giá mới nhất đầu tiên (`sort=id\|desc`, trang 1 lấy 20 + trang 2 lấy 10 đầu) của mỗi sản phẩm.<br>2. **Ẩn danh PII từ đầu:** dữ liệu thô tải vào thư mục tạm ngoài repo (không bao giờ lưu trong workspace); chỉ trích 6 trường không định danh (`id`, `rating_star`, `text`, `usage_duration`, `helpful_count`, `has_images`, `support_replied`), loại bỏ hoàn toàn tên tài khoản, avatar, ID khách hàng và URL ảnh cá nhân; chạy regex kiểm tra SĐT/email bằng `evidence/count.py` (**0 lỗi PII**).<br>3. **Giữ nguyên văn nội dung bình luận:** chỉ gộp ký tự xuống dòng/khoảng trắng thừa, không viết lại lời người mua; gắn mã tuần tự `R01`–`R30` theo từng sản phẩm; lưu tách bảng nhãn tại `evidence/cp3_labels.csv`. |
| **Số dòng / số đoạn** | **90 đánh giá** (3 sản phẩm × 30 đánh giá/sản phẩm) trong `data/products/logitech_signature_m650.json`, `locknlock_lhc6180slv.json`, `philips_sth3010_70.json`. |
| **Phiên bản / ngày lấy** | `cp3-v1` · ngày truy cập & thu thập: **28/11/2026**. |
| **Nhãn** | **Thật** (đánh giá công khai thật từ khách hàng đã mua trên Tiki, giữ nguyên văn sau khi loại bỏ PII). |
| **Giới hạn** | • Cả 3 sản phẩm bán chạy lấy mẫu trên Tiki đều thuộc gian hàng `Tiki Trading` (chính hãng), chưa đại diện cho các gian hàng nhỏ lẻ dễ phát sinh lặp nội dung bất thường.<br>• Tiki không có cơ chế thưởng xu theo độ dài 50 ký tự như Shopee nên không quan sát được `nhieu_nhan_xu` (thay vào đó 62/90 = 68,9% là review trống chỉ bấm sao).<br>• Không dùng trực tiếp dữ liệu Shopee vì phân trang review công khai của Shopee chặn đăng nhập / HTTP 403.<br>• **Ghi nhận kỹ thuật ngoài mẫu cho `codebase/tools.py`:** khi chạy thử `filter_review_noise` hiện tại lên `SP04–SP06`, bộ lọc giữ đúng các lỗi chính của `SP04` (`R07`, `R27`) và `SP06` (`R20`, `R28`, `R29`), nhưng làm rớt `SP05 [R23]` (phản ánh lệch màu bình kèm câu khen giao hàng nhanh) do từ khoá `"màu"` chưa nằm trong danh sách tín hiệu sản phẩm của bộ lọc quy tắc — ghi nhận để nhóm cân nhắc cải tiến sau CP3 nếu cần. |

---

## Dataset 3 · Dữ liệu synthetic trong bộ câu thử (`eval/benchmark.csv` · `B01–B10`)

| Thuộc tính | Chi tiết |
|---|---|
| **Dùng để làm gì** | Kiểm tra các kịch bản biên và tấn công mà 60 review thật đợt 1 chưa có (chỉ toàn sao không chữ, cụm review trùng lặp, prompt injection trong review, ép cáo buộc shop seeding). **Không dùng làm bằng chứng pain.** |
| **Từ đâu** | Nhóm tự viết tay (`@Tanashi-Titus` · CP2) trong `eval/benchmark.csv` (`source = sinh_seed`). |
| **Số dòng** | **10 câu thử** (`B01–B10`) trong tổng số 25 câu của `eval/benchmark.csv` (15 câu còn lại `B11–B25` trích nguyên văn từ Dataset 1 `SP01–SP03`). |
| **Nhãn** | **Synthetic** (đã tách biệt rõ cột `source` trong `eval/benchmark.csv` và kiểm tự động bằng `python run.py check`). |

---

## Quy tắc phân loại nhiễu & thông tin thật (áp dụng thống nhất · `N = 150`)

Mỗi đánh giá được gán vào đúng 1 trong 2 nhóm lớn và 9 nhãn con (`data/CONTRACT.md` §2 · tái lập bằng `python evidence/count.py`):

1. **Nhiễu / không phản ánh chất lượng sản phẩm (`nhieu`) — 101/150 (67,3%):**
   - `nhieu_trong` *(72/150 · 48,0%)*: văn bản trống, chỉ bấm sao/ảnh hoặc tiêu đề mặc định của sàn.
   - `nhieu_ngoai_chat_luong` *(11/150 · 7,3%)*: chỉ nói về giao hàng/ship, khen sàn, đóng gói nguyên seal, giá/KM, thái độ nhân viên, lệch ngày bảo hành, tự đánh rơi hoặc thiếu phụ kiện vốn không kèm hộp.
   - `nhieu_khen_chung` *(10/150 · 6,7%)*: khen ngắn chung chung (`"Tốt"`, `"Ok"`, `"Sài ổn"`, `"Xài ngon"`) không nêu chi tiết vận hành.
   - `nhieu_hoi_dap_rao_ban` *(5/150 · 3,3%)*: hỏi chính sách thu cũ/đổi trả, hỏi hướng dẫn dùng, hoặc rao pass lại sản phẩm.
   - `nhieu_chua_dung` *(3/150 · 2,0%)*: mới nhận/mới dùng 1 giờ–1 ngày, tự ghi chưa dùng đủ để đánh giá chất lượng.
   - `nhieu_nhan_xu` *(0/150 · 0,0%)*: đánh giá đối phó nhận xu/thưởng sàn (không xuất hiện trong mẫu MWG/Tiki).
   - `nhieu_lap_bat_thuong` *(0/150 · 0,0%)*: lặp nội dung nguyên văn ≥8 ký tự trong cùng sản phẩm (kiểm tự động = 0 cặp).
2. **Có thông tin chất lượng / trải nghiệm sản phẩm (`co_thong_tin`) — 49/150 (32,7%):**
   - `co_thong_tin_rui_ro` *(32/150 · 21,3%)*: nêu lỗi, hạn chế, rủi ro độ bền, an toàn, hiệu năng, tương thích hoặc lệch mô tả thực tế của sản phẩm.
   - `co_thong_tin_tich_cuc` *(17/150 · 11,3%)*: nêu trải nghiệm tích cực kèm ít nhất 1 chi tiết vận hành cụ thể.
