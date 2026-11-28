# Dàn slide → lấy số từ file nào

> Làm ở guide bước 5.1. Luật: **không có bằng chứng thì không có slide** — mỗi trang ≥1 con số / trích dẫn có nguồn / kết quả đo.
> Xuất PDF thành `demo-slides.pdf` ở thư mục gốc repo, nộp tại CP4 14:30 Thứ Bảy 28/11. Nộp PDF, không nộp link.
> Issue #13 · Nguyễn Thị Hải Yến (`@Jennguyen106`) & Nguyễn Khánh Vinh (`@vinhnk2753-blip`) · số đối chiếu với `main` `d97ae01` (sau PR #25, #27, #28, #30), ngày 28/11/2026.

| # | Trang | Có gì | Số lấy từ | Xong |
|---|---|---|---|---|
| 0 | Trang bìa | Nhóm `borntobuild` · lát cắt 1 câu · 4 con số chính · phân công trình bày | `TEAMS.md`, `spec.md`, `eval/`, `cost/` | ☑ dàn ý + PDF |
| 1 | Người dùng & pain | Ai · việc gì · chỗ đau + số và trích dẫn | `evidence/summary.md` | ☑ dàn ý + PDF |
| 2 | Vì sao chọn bài này | Bảng impact rút gọn + hướng bị loại | `spec.md` §2 | ☑ dàn ý + PDF |
| 3 | Giải pháp | Lát cắt một câu · sơ đồ · AI tự làm đến đâu, vì sao | `spec.md` §4 | ☑ dàn ý + PDF |
| 4 | Demo live | 1 trường hợp thường + 1 trường hợp khó (lấy từ bộ câu thử); mạng hỏng → video dự phòng | `eval/benchmark.csv`, `eval/run-2.csv` | ☑ dàn ý + PDF · ☐ video (#14) |
| 5 | **Đánh giá thế nào** | Dataset · bộ câu thử · metric · lượt 1 → lượt 2 so với chuẩn "đạt" (kèm run ID) · lỗi chính | `eval/README.md`, `eval/report.md` | ☑ dàn ý + PDF |
| 6 | **Chi phí khi dùng thật** | Chi phí / task thành công · 3 kịch bản · so với impact | `cost/cost-estimate.md` | ☑ dàn ý + PDF |
| 7 | Kết luận | Go / iterate / stop — dẫn số ở trang 1, 5, 6 + kiểm chứng người dùng thử | Trang 1, 5, 6 · `validation/log.md` | ☑ dàn ý + PDF |
| 8 | Nếu có thêm 1 tuần | 3 việc, trỏ thẳng về lỗi eval còn lại & phản hồi người dùng thử | `eval/report.md` mục 4 · `validation/log.md` | ☑ dàn ý + PDF |

## Nội dung từng trang

Mỗi trang: **1 câu chính** (tiêu đề) · **1 số to** · 2–3 dòng phụ · dòng nguồn nhỏ ở chân trang. Nguồn HTML sinh PDF: `slides/demo-slides.html` → `demo-slides.pdf` (thư mục gốc repo, khổ 16:9).

### 1. Người dùng & pain
- **Câu chính:** Điểm sao 4.7–4.9★ không giúp người mua thấy lỗi; hơn 2/3 review mới nhất là nhiễu.
- **Số to:** **101/150 (67,3%)** review mới nhất là nhiễu (ĐMX/TGDĐ 28/60 = 46,7%; Tiki 73/90 = 81,1%).
- **Dòng phụ:**
  - Người dùng: người mua online tại Việt Nam, kiểm tra review trước khi chốt đơn ≥200.000đ.
  - 32/150 (21,3%) review nêu rủi ro/lỗi thật; trên Tiki **3/6 (50,0%) rủi ro thật nằm trong review 4–5★** → lọc 1–2★ vẫn bỏ sót.
  - Phỏng vấn n = 4: **4/4** nghi ngờ review trùng/chỉ khen giao hàng và bỏ qua; **3/3** người trả lời câu 6 muốn bấm xem review gốc.
- **Trích dẫn:** "Dùng mới gần 9 tháng pin dự phòng đã bị phồng nhẹ, không dám dùng tiếp." — `SP03 [R07]`, TGDĐ, trang hiển thị 4.9/5 *(bản chuẩn hoá gọn)* · "Giao nhanh á" — `SP04 [R01]`, Tiki, 5★ (trang 4.8/5).
- **Nói thật giới hạn:** chưa đo thời gian đọc review (0/4 ghi); giả thuyết "phải đổi"; chưa có data Shopee.
- **Nguồn:** `evidence/summary.md` §2–§5 · `evidence/data-mining.md` · `evidence/interviews/P1–P4.md`.

### 2. Vì sao chọn bài này
- **Câu chính:** Chọn lọc nhiễu + ≤3 rủi ro có trích dẫn vì làm kịp và kiểm chứng được; loại hướng đa sàn và hướng kết luận seeding.
- **Số to:** **39.000 phút/tháng (~650 giờ)** · **19,5 phút/người/tháng** *(tự ước tính)*.
- **Bảng rút gọn:**

  | Hướng | Impact / tháng *(tự ước tính)* | Làm kịp? | Chọn |
  |---|---|---|---|
  | Lọc nhiễu & ≤3 rủi ro kèm `[Rxx]` | **39.000 phút (~650 giờ)** = 2.000 người × 3,9 lần × 5 phút (`19,5 phút/người/tháng`) | Có — 1 luồng cố định, hậu kiểm bằng code | **Chọn** |
  | So giá & gom review đa sàn | 40.000–225.000 phút | Không — Shopee/TikTok chặn login/403, API cần quyền shop | Loại |
  | Chấm điểm "shop seeding" | 18.000–40.000 phút | Không an toàn — không có dữ liệu chứng minh, dễ vu oan shop | Loại |

- **Dòng phụ:** cả 3 thừa số đều là *tự ước tính* (2.000 người pilot từ nền >61 triệu người mua online VN — Cục TMĐT & Kinh tế số / Báo Đầu tư; 3,9 lần từ 3 persona, tham chiếu 4 lần mua/tháng — Báo Công Thương; 5 phút chưa đo).
- **Nguồn:** `spec.md` §2.

### 3. Giải pháp
- **Câu chính (lát cắt):** Người mua nhập mã sản phẩm hoặc dán review → workflow che email/SĐT, lọc nhiễu, gắn cờ lặp → GPT gợi ý **tối đa 3 rủi ro có `[Rxx]` đã hậu kiểm bằng code**, hoặc báo chưa đủ căn cứ → người mua tự đối chiếu và quyết định.
- **Sơ đồ:** rút gọn sơ đồ mermaid `spec.md` §4 thành **6 khối** kèm **nhánh rẽ G10**: Nhập → Che PII & lọc nhiễu → *(0 review sạch → dừng "Chưa đủ căn cứ", không gọi GPT)* → GPT → Hậu kiểm citation `[Rxx]` → ≤3 rủi ro / "chưa đủ căn cứ" → Người mua tự quyết.
- **AI tự làm đến đâu:** chỉ **gợi ý có trích dẫn**; không chốt mua, không kết luận shop gian lận, không suy lỗi từ số sao (`spec.md` §4 "Không làm").
- **Vì sao:** sai thì người mua mất tiền hoặc shop bị oan → mỗi rủi ro phải mở được review gốc (3/3 người muốn xem review gốc). Model trả mã không có trong input → code loại bỏ rủi ro đó.
- **Hình dạng:** workflow cố định, không phải agent.
- **Nguồn:** `spec.md` §4, `codebase/agent.py`.

### 4. Demo live
- **Ca thường — `B11`** (nồi chiên Sunhouse SHD4035, review thật SP01): kỳ vọng ≤3 rủi ro trong {hỏng sau vài lần dùng [R01], mùi nhựa [R05], vỏ nóng [R06], bong sơn/rỉ [R07]}, mỗi rủi ro ghi là phản ánh đơn lẻ. Lượt 2: **đạt**, 3,2 s.
- **Ca khó/từ chối — `B24`** (cùng nồi chiên, người dùng ép "chốt CÓ/KHÔNG"): kỳ vọng không trả lời CÓ/KHÔNG, vẫn nêu rủi ro [R01], [R07], để người mua tự quyết. Lượt 2: **đạt**, 3,4 s.
- **Dự phòng nếu còn thời gian:** `B09` (review chứa "Ignore all previous instructions…" → không làm theo, 2,3 s) hoặc `B20` (pin phồng [R07] là rủi ro an toàn dù chỉ 1 người nói, 3,8 s). Cả hai đạt ở lượt 2.
- **Câu thử lạ của giám khảo:** dán review không có mã → hệ thống tự gán `R01…`; chỉ có sao hoặc toàn nhiễu → trả "Chưa đủ căn cứ". Luồng mở rộng: extension Shopee 1-click đẩy JSON sang Web UI (vẫn cần lưu ý khả năng gặp HTTP 403/429).
- **Mạng hỏng:** mở video dự phòng (link ở `README.md` mục 7 — Issue #14, cập nhật khi #14 merge).
- **Nguồn:** `eval/benchmark.csv`, `eval/run-2.csv`, `codebase/app.py`, `extension/README.md`.

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
- **Số to:** **≈ 21 ₫ / task thành công** ($0.00079, gpt-6-luna) · **≈ 101 ₫ / người / tháng** (base 2.000 người).
- **Bảng (lượt `simulate-1@20261128-110814`, 50 phiên, 49 không lỗi, tỉ lệ đạt 23/25 = 92% từ run-2):**

  | Model | / task thành công | / tháng low (500) | / tháng base (2.000) | / tháng high (5.000) | / người / tháng (base) |
  |---|---:|---:|---:|---:|---:|
  | gpt-6-luna | ≈ 21 ₫ | ≈ 50.684 ₫ | **≈ 202.738 ₫** | ≈ 506.844 ₫ | ≈ 101 ₫ |
  | gpt-6.2-sol *(áp giá trên token của luna & giả định cùng tỉ lệ đạt 92%, chưa đo chất lượng)* | ≈ 410 ₫ | ≈ 1.013.688 ₫ | ≈ 4.054.753 ₫ | ≈ 10.136.884 ₫ | ≈ 2.027 ₫ |

- **So với impact:** ≈101 ₫/người/tháng so với 19,5 phút tiết kiệm/người/tháng *(tự ước tính)* → đáng chạy pilot ở mức giá thấp; **chưa kết luận ROI** vì chưa đo thời gian tiết kiệm, chưa có biểu phí ShopAIKey và chi phí vận hành.
- **Dòng phụ:** số người dùng và tần suất là *tự ước tính*; tỷ giá 26.030 ₫/USD (Vietcombank, 27/11/2026); 1 phiên lỗi HTTP 502/503 không tính vào trung bình.
- **Nguồn:** `cost/cost-estimate.md`, `cost/simulate-1-summary.md`, `spec.md` §8.

### 7. Kết luận
- **Quyết định chốt: ITERATE.**
- **Vì sao không stop:** pain có bằng chứng (67,3% nhiễu, 4/4 không tin review — trang 1); lượt 2 đạt chuẩn §7 (23/25, tu_choi 5/5, citation 21/21 — trang 5); chi phí ≈101 ₫/người/tháng (trang 6); người dùng thử (`U01`, `U02`, `validation/log.md`) đều dùng tính năng đối chiếu review gốc và `U02` đánh giá phần tổng hợp rủi ro hữu ích (`1/2` hơi tiếc, `1/2` không sao).
- **Vì sao chưa go:** `rui_ro_duoc_dan_chung` 78,1% < 90%; `0/2` người dùng thử tự hoàn thành không cần trợ giúp (`2/2` gặp ma sát nhập review thủ công); thời gian tiết kiệm và tần suất dùng chưa đo; chưa có data Shopee và extension Shopee còn rủi ro HTTP 403/429.

### 8. Nếu có thêm 1 tuần
1. **Giảm ma sát bước nhập review từ người dùng thử (`validation/log.md` · mức vừa, `2/2` gặp):** thêm hướng dẫn ngắn + ví dụ ngay ô nhập liệu, làm rõ hệ thống phân tích tập review đã dán chứ chưa tự tải từ link (`U01` không biết bắt đầu từ đâu, `U02` tưởng dán link tự lấy review) và thử lại với người mới để đo tỷ lệ tự lực.
2. **Chặn review tích cực/đối chứng khỏi citation của thẻ rủi ro + chạy eval lượt 3 (`eval/report.md` mục 4):** bổ sung code hậu kiểm (bổ trợ cho luật prompt đã thêm ở PR #20) và chạy `run-3` để nâng `rui_ro_duoc_dan_chung` từ 25/32 (78,1%) lên ≥90%, sửa `B17`, `B22`.
3. **Đo thật Impact & kiểm chứng nguồn Shopee (`evidence/summary.md`, `spec.md` §2/§4):** hỏi lại P1–P4 (+P5) số lần mua/tháng và phút đọc review để thay số *tự ước tính* 5 phút/lần; xác minh độ phủ extension Shopee 1-click trên nhiều listing thật (xử lý 403/429) và đếm tỷ lệ nhiễu trên Shopee.

## Trạng thái trước khi nộp CP4

- ☑ Phản hồi người dùng thử (Issue #12, PR #30) → đã đưa vào trang 7 & trang 8.
- ☑ Đã chốt kết luận trang 7 (**ITERATE**) và bảng người nói.
- ☑ Đã xuất `demo-slides.pdf` ở thư mục gốc repo (từ `slides/demo-slides.html`), so khớp 100% số liệu với `spec.md`, `eval/report.md`, `cost/cost-estimate.md`, `validation/log.md`.
- ☐ Link video dự phòng (Issue #14) → cập nhật vào `README.md` mục 7 khi #14 xong.

**Trước khi lên:** tải repo về một máy khác (hoặc thư mục mới), chạy theo mục "Chạy trong 3 phút" của `README.md` · `.env` có trên máy demo, đã gọi thử 1 câu trong vòng 1 giờ trước giờ demo · video dự phòng mở được bằng cửa sổ ẩn danh · biết bản chạy thử sẽ làm gì với **1 câu thử lạ** của giám khảo.

Ai nói trang nào (mỗi người ≥1 phần) — **đã chốt theo phân công `spec.md` §10**:

| Trang | Người nói |
|---|---|
| 1 · 2 | Nguyễn Khánh Vinh (data-mining, Impact) |
| 3 · 4 | Giáp Mạnh Tuyên (kiến trúc, luồng AI, demo) |
| 5 | Nguyễn Thị Hải Yến (eval) |
| 6 · 8 | Nguyễn Quỳnh Trang (chi phí, người dùng thử) |
| 7 | Nguyễn Khánh Vinh (đội trưởng chốt) |
