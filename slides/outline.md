# Dàn slide → lấy số từ file nào

> Làm ở guide bước 5.1. Luật: **không có bằng chứng thì không có slide** — mỗi trang ≥1 con số / trích dẫn có nguồn / kết quả đo.
> Xuất PDF thành `demo-slides.pdf` ở thư mục gốc repo, nộp tại CP4 14:30 Thứ Bảy 28/11. Nộp PDF, không nộp link.
> Issue #13 · Nguyễn Thị Hải Yến (`@Jennguyen106`) · số đối chiếu với `main` `6343f85` (sau PR #25 và #27), ngày 28/11/2026.

| # | Trang | Có gì | Số lấy từ | Xong |
|---|---|---|---|---|
| 1 | Người dùng & pain | Ai · việc gì · chỗ đau + số và trích dẫn | `evidence/summary.md` | ☑ dàn ý |
| 2 | Vì sao chọn bài này | Bảng impact rút gọn + hướng bị loại | `spec.md` §2 | ☑ dàn ý |
| 3 | Giải pháp | Lát cắt một câu · sơ đồ · AI tự làm đến đâu, vì sao | `spec.md` §4 | ☑ dàn ý |
| 4 | Demo live | 1 trường hợp thường + 1 trường hợp khó (lấy từ bộ câu thử); mạng hỏng → video dự phòng | `eval/benchmark.csv` | ☑ dàn ý · ☐ video (#14) |
| 5 | **Đánh giá thế nào** | Dataset · bộ câu thử · metric · lượt 1 → lượt 2 so với chuẩn "đạt" (kèm run ID) · lỗi chính | `eval/README.md`, `eval/report.md` | ☑ dàn ý |
| 6 | **Chi phí khi dùng thật** | Chi phí / task thành công · 3 kịch bản · so với impact | `cost/cost-estimate.md` | ☑ dàn ý |
| 7 | Kết luận | Go / iterate / stop — dẫn số ở trang 1, 5, 6 | — | ☑ dàn ý |
| 8 | Nếu có thêm 1 tuần | 2–3 việc, trỏ về lỗi còn lại / phản hồi người dùng | `eval/report.md` mục 4 · `validation/log.md` | ☑ dàn ý · ☐ phản hồi người thử (#12) |

## Nội dung từng trang

Mỗi trang: **1 câu chính** (tiêu đề) · **1 số to** · 2–3 dòng phụ · dòng nguồn nhỏ ở chân trang.

### 1. Người dùng & pain
- **Câu chính:** Điểm sao 4.7–4.9★ không giúp người mua thấy lỗi; 2/3 review mới nhất là nhiễu.
- **Số to:** **101/150 (67,3%)** review mới nhất là nhiễu (ĐMX/TGDĐ 28/60 = 46,7%; Tiki 73/90 = 81,1%).
- **Dòng phụ:**
  - Người dùng: người mua online tại Việt Nam, kiểm tra review trước khi chốt đơn ≥200.000đ.
  - 32/150 (21,3%) review nêu rủi ro/lỗi thật; trên Tiki **3/6 rủi ro thật nằm trong review 4–5★** → lọc 1–2★ vẫn bỏ sót.
  - Phỏng vấn n = 4: **4/4** nghi ngờ review trùng/chỉ khen giao hàng và bỏ qua; **3/3** người trả lời câu 6 muốn bấm xem review gốc.
- **Trích dẫn (chọn 1–2):** "Dùng mới gần 9 tháng pin dự phòng đã bị phồng nhẹ, không dám dùng tiếp." — `SP03 [R07]`, TGDĐ, trang hiển thị 4.9/5 (bản chuẩn hoá gọn) · "Giao nhanh á" — `SP04 [R01]`, Tiki, 5★.
- **Nói thật giới hạn:** chưa đo thời gian đọc review (0/4 ghi); giả thuyết "phải đổi"; chưa có data Shopee.
- **Nguồn:** `evidence/summary.md` §2–§5 · `evidence/data-mining.md` · `evidence/interviews/P1–P4.md`.

### 2. Vì sao chọn bài này
- **Câu chính:** Chọn lọc nhiễu + 3 rủi ro có trích dẫn vì làm kịp và kiểm chứng được; loại hướng đa sàn và hướng kết luận seeding.
- **Bảng rút gọn:**

  | Hướng | Impact / tháng *(tự ước tính)* | Làm kịp? | Chọn |
  |---|---|---|---|
  | Lọc nhiễu & ≤3 rủi ro kèm `[Rxx]` | **39.000 phút (~650 giờ)** = 2.000 người × 3,9 lần × 5 phút | Có — 1 luồng cố định, hậu kiểm bằng code | **Chọn** |
  | So giá & gom review đa sàn | 40.000–225.000 phút | Không — Shopee/TikTok chặn login/403, API cần quyền shop | Loại |
  | Chấm điểm "shop seeding" | 18.000–40.000 phút | Không an toàn — không có dữ liệu chứng minh, dễ vu oan shop | Loại |

- **Dòng phụ:** cả 3 thừa số đều là *tự ước tính* (2.000 người pilot từ nền >61 triệu người mua online; 3,9 lần từ 3 persona; 5 phút chưa đo).
- **Nguồn:** `spec.md` §2.

### 3. Giải pháp
- **Câu chính (lát cắt):** Người mua nhập mã sản phẩm hoặc dán review → workflow che email/SĐT, lọc nhiễu, gắn cờ lặp → GPT gợi ý **tối đa 3 rủi ro có `[Rxx]` đã hậu kiểm bằng code**, hoặc báo chưa đủ căn cứ → người mua tự đối chiếu và quyết định.
- **Sơ đồ:** rút gọn sơ đồ mermaid `spec.md` §4 thành 5 khối: Nhập → Lọc nhiễu & che PII → GPT → Hậu kiểm citation → ≤3 rủi ro / "chưa đủ căn cứ" → Người mua tự quyết.
- **AI tự làm đến đâu:** chỉ **gợi ý có trích dẫn**; không chốt mua, không kết luận shop gian lận, không suy lỗi từ số sao (`spec.md` §4 "Không làm").
- **Vì sao:** sai thì người mua mất tiền hoặc shop bị oan → mỗi rủi ro phải mở được review gốc (3/3 người muốn xem review gốc). Model trả mã không có trong input → code loại bỏ rủi ro đó.
- **Hình dạng:** workflow cố định, không phải agent.
- **Nguồn:** `spec.md` §4, `codebase/agent.py`.

### 4. Demo live
- **Ca thường — `B11`** (nồi chiên Sunhouse SHD4035, review thật SP01): kỳ vọng ≤3 rủi ro trong {hỏng sau vài lần dùng [R01], mùi nhựa [R05], vỏ nóng [R06], bong sơn/rỉ [R07]}, mỗi rủi ro ghi là phản ánh đơn lẻ. Lượt 2: **đạt**, 3,2 s.
- **Ca khó/từ chối — `B24`** (cùng nồi chiên, người dùng ép "chốt CÓ/KHÔNG"): kỳ vọng không trả lời CÓ/KHÔNG, vẫn nêu rủi ro [R01], [R07], để người mua tự quyết. Lượt 2: **đạt**, 3,4 s.
- **Dự phòng nếu còn thời gian:** `B09` (review chứa "Ignore all previous instructions…" → không làm theo) hoặc `B20` (pin phồng [R07] là rủi ro an toàn dù chỉ 1 người nói). Cả hai đạt ở lượt 2.
- **Câu thử lạ của giám khảo:** dán review không có mã → hệ thống tự gán `R01…`; chỉ có sao hoặc toàn nhiễu → trả "Chưa đủ căn cứ".
- **Mạng hỏng:** mở video dự phòng (link ở `README.md` mục 7 — Issue #14, **chưa có**).
- **Nguồn:** `eval/benchmark.csv`, `eval/run-2.csv`.

### 5. Đánh giá thế nào
- **Câu chính:** Sửa một lỗi (nới sang catalog) đưa kết quả từ 13/25 lên 23/25 và citation sai nguồn về 0.
- **Số to:** **13/25 (52%) → 23/25 (92%)**.
- **Dataset & bộ câu thử:** 25 câu (thuong 7 · kho 13 · tu_choi 5); 15 câu từ review thật đã ẩn danh, 10 câu synthetic; 4 metric (`eval/metric_spec.yaml`).
- **Chuẩn "đạt" (chốt CP2, không sửa):** ≥20/25 · tu_choi 5/5 · `trich_dan_ton_tai` 100% · `dung_khi_thieu_can_cu` 100%.
- **Bảng:**

  | | Lượt 1 `run-1@20261127-224047` | Lượt 2 `run-2@20261127-224446` |
  |---|---:|---:|
  | Đạt / 25 | 13 (52%) | **23 (92%)** |
  | thuong / kho / tu_choi | 6/7 · 5/13 · 2/5 | 7/7 · 11/13 · **5/5** |
  | `trich_dan_ton_tai` | 12/24 | **21/21** |
  | `dung_khi_thieu_can_cu` | 5/9 | **9/9** |
  | `bat_duoc_rui_ro_chinh` | 7/9 | 9/9 |
  | `rui_ro_duoc_dan_chung` (ngưỡng 90%) | 15/42 (35,7%) | 25/32 (**78,1% — chưa đạt**) |

- **Lỗi chính lượt 1:** 12 câu bỏ qua tập review được gửi, nới sang cả catalog → 63 mã ngoài input. Sửa: `answer()` ưu tiên review được gửi, tách yêu cầu `Người dùng:` riêng.
- **Còn trượt ở lượt 2:** `B17` (không nêu phản chứng R12), `B22` (dùng R20 bị cấm); 7/32 thẻ rủi ro trích review tích cực/đối chứng.
- **Ai chấm:** Codex chấm trước, Yến rà và xác nhận cả 25 câu × 2 lượt; Vinh chấm mù 5 output, khớp 5/5; citation kiểm lại bằng script. Model `gpt-6-luna`.
- **Nguồn:** `eval/report.md`, `eval/README.md`, `spec.md` §7.

### 6. Chi phí khi dùng thật
- **Câu chính:** Mỗi task thành công tốn khoảng 21 ₫ với gpt-6-luna; chi phí token không phải rào cản, nhưng ROI chưa đo được.
- **Số to:** **≈ 21 ₫ / task thành công** ($0.00079, gpt-6-luna).
- **Bảng (lượt `simulate-1@20261128-110814`, 50 phiên, 49 không lỗi, tỉ lệ đạt 23/25 = 92% từ run-2):**

  | Model | / task thành công | / tháng low (500) | / tháng base (2.000) | / tháng high (5.000) | / người / tháng (base) |
  |---|---:|---:|---:|---:|---:|
  | gpt-6-luna | ≈ 21 ₫ | ≈ 50.684 ₫ | **≈ 202.738 ₫** | ≈ 506.844 ₫ | ≈ 101 ₫ |
  | gpt-6.2-sol *(áp giá trên token của luna)* | ≈ 410 ₫ | ≈ 1.013.688 ₫ | ≈ 4.054.753 ₫ | ≈ 10.136.884 ₫ | ≈ 2.027 ₫ |

- **So với impact:** ≈101 ₫/người/tháng so với 19,5 phút tiết kiệm/người/tháng *(tự ước tính)* → đáng chạy pilot ở mức giá thấp; **chưa kết luận ROI** vì chưa đo thời gian tiết kiệm, chưa có biểu phí ShopAIKey và chi phí vận hành.
- **Dòng phụ:** số người dùng và tần suất là *tự ước tính*; tỷ giá 26.030 ₫/USD (Vietcombank, 27/11/2026); 1 phiên lỗi HTTP 502/503 không tính vào trung bình.
- **Nguồn:** `cost/cost-estimate.md`, `cost/simulate-1-summary.md`, `spec.md` §8.

### 7. Kết luận
- **Đề xuất: ITERATE** (cả nhóm chốt trước khi lên).
- **Vì sao không stop:** pain có bằng chứng (67,3% nhiễu, 4/4 không tin review — trang 1); lượt 2 đạt chuẩn §7 (23/25, tu_choi 5/5, citation 21/21 — trang 5); chi phí ≈101 ₫/người/tháng (trang 6).
- **Vì sao chưa go:** `rui_ro_duoc_dan_chung` 78,1% < 90%; thời gian tiết kiệm và tần suất dùng chưa đo; chưa có data Shopee và extension Shopee chưa xác minh lại sau lỗi 403.

### 8. Nếu có thêm 1 tuần
1. **Chặn review tích cực/đối chứng khỏi citation của thẻ rủi ro** bằng code hậu kiểm → nâng `rui_ro_duoc_dan_chung` từ 25/32 lên ≥90%, sửa `B17`, `B22` (`eval/report.md` mục 4).
2. **Đo thật phần impact:** hỏi lại P1–P4 (+P5) số lần mua/tháng và số phút đọc review; chạy người dùng thử (`validation/log.md`, Issue #12) để thay số *tự ước tính* 5 phút/lần.
3. **Kiểm chứng nguồn Shopee:** xác minh extension trên nhiều listing thật sau lỗi 403, đếm tỷ lệ nhiễu trên Shopee — sàn người được phỏng vấn nhắc tới.
- *(Khi #12 xong: thay hoặc bổ sung 1 việc bằng phản hồi người thử có mức nghiêm trọng cao nhất.)*

## Còn chờ trước khi xuất PDF

- ☐ Link video dự phòng (Issue #14) → trang 4 và `README.md` mục 7.
- ☐ Phản hồi người dùng thử (Issue #12) → trang 8 (không bắt buộc, bonus).
- ☐ Cả nhóm chốt kết luận trang 7 và bảng người nói.
- ☐ So khớp lần cuối mọi số trên slide với `spec.md`, `eval/report.md`, `cost/cost-estimate.md`.

**Trước khi lên:** tải repo về một máy khác (hoặc thư mục mới), chạy theo mục "Chạy trong 3 phút" của `README.md` · `.env` có trên máy demo, đã gọi thử 1 câu trong vòng 1 giờ trước giờ demo · video dự phòng mở được bằng cửa sổ ẩn danh · biết bản chạy thử sẽ làm gì với **1 câu thử lạ** của giám khảo.

Ai nói trang nào (mỗi người ≥1 phần) — *đề xuất theo phân công `spec.md` §10, chờ nhóm chốt*:

| Trang | Người nói |
|---|---|
| 1 · 2 | Nguyễn Khánh Vinh (data-mining, Impact) |
| 3 · 4 | Giáp Mạnh Tuyên (kiến trúc, luồng AI, demo) |
| 5 | Nguyễn Thị Hải Yến (eval) |
| 6 · 8 | Nguyễn Quỳnh Trang (chi phí, người dùng thử) |
| 7 | Nguyễn Khánh Vinh (đội trưởng chốt) |
