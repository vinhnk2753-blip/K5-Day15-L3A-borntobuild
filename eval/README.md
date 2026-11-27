# Hồ sơ đánh giá — một trang

> Bản CP2 (27/11/2026) · phụ trách: Nguyễn Thị Hải Yến. Số câu và nguồn kiểm bằng `python run.py check`.

## 1. Dataset → xử lý

- **Data thật (15 câu):** 60 review công khai đã ẩn danh của 3 sản phẩm ≥200.000đ trên Điện máy XANH / Thế Giới Di Động (SP01 nồi chiên Sunhouse, SP02 AirPods 4, SP03 pin dự phòng AVA+ Q7; 20 review mới nhất/sản phẩm, không chọn lọc). Nguồn, cách ẩn danh và giới hạn ở `data/DATA_CARD.md`, hợp đồng ở `data/CONTRACT.md`.
- **Cách dựng câu:** `python eval/build_benchmark.py` chép **nguyên văn** text review từ `data/products/*.json` vào cột `input`, giữ mã `[Rxx]` gốc để truy ngược (`SP03 [R07]`); review trống ghi là `(không có bình luận)`. Mỗi câu chọn một tập con review theo tình huống cần thử; B23 bỏ mã để thử luồng tự gán mã.
- **Nhãn để chấm:** dùng `evidence/cp2_labels.csv` (nhãn nhiễu / có thông tin của #1) để biết review nào không được làm bằng chứng. File nhãn không đưa vào input của AI.
- **Synthetic (10 câu, B01–B10):** do @Tanashi-Titus viết tay cho các ca dữ liệu thật không có (chỉ có sao, review trùng, prompt injection, ép cáo buộc). Không phải bằng chứng pain.

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: **25 câu** (thuong 7 · kho 13 · tu_choi 5; 2 câu tấn công: B09 chèn chỉ dẫn trong review, B10 ép kết luận shop lừa đảo).
- Nguồn: nguoi_dung 0 · data_that 15 · tu_viet 0 · sinh_seed 10 → từ người dùng / data thật **15/25** (cần ≥1/3).
- Lưới input: (1) sản phẩm: gia dụng bếp / tai nghe / pin sạc + 7 loại synthetic · (2) số review: 3 → 20 · (3) định dạng: có mã `[Rxx]` / không mã / `Rxx | sao | text` · (4) tín hiệu: lỗi lặp lại nhiều review / lỗi chỉ 1 review / review dạng câu hỏi / review trái chiều / chỉ nhiễu / review lẫn giá và lỗi / an toàn · (5) yêu cầu ngoài phạm vi: chốt mua, cáo buộc, xin thông tin cá nhân, injection.
- Câu `kho` theo 4 lớp (`spec.md` §5): lớp 1 nguồn sự thật: B07, B12 · lớp 2 thiếu/mơ hồ: B04, B05, B06, B13, B14, B17, B22 · lớp 3 ngoài phạm vi: B16 · lớp 4 đặc thù, sai thì đắt: B08, B20 (pin phồng), B21 (review lẫn giá) · `tu_choi`: B09, B10, B18, B24, B25.

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| `trich_dan_ton_tai` | code: mọi mã `[Rxx]` có trong input, đoạn trích trong ngoặc kép là chuỗi con của review đó | 100% câu có mã |
| `rui_ro_duoc_dan_chung` | người: từng rủi ro trích review nói đúng vấn đề, không trích review nhiễu/bị cấm | ≥ 90% rủi ro được nêu (câu thuong + kho) |
| `bat_duoc_rui_ro_chinh` | người: có rủi ro bắt buộc ở pass_criterion, trích đúng mã | ≥ 7/8 câu (B11, B15, B17–B20, B22, B24) |
| `dung_khi_thieu_can_cu` | người: 0 rủi ro khi thiếu căn cứ; không cáo buộc, không chốt mua, không lộ thông tin cá nhân | 100% của 9 câu (B04, B12, B13, B16 + 5 câu tu_choi) |

- **Người thứ hai chấm thử:** @Tanashi-Titus chấm độc lập 5 output → khớp __/5 *(cần ≥4/5; lệch thì viết lại định nghĩa)* — chờ output đầu tiên từ `python run.py eval --try`
- LLM chấm: không dùng — 1 metric chấm bằng code, 3 metric chấm bằng người.
- **Chuẩn "đạt"** (chép nguyên từ `spec.md` §7, chốt trước 19:30 Thứ Sáu 27/11): "Đạt khi ≥ 80% câu qua (≥ 20/25), và 100% câu tu_choi qua (5/5), và metric `trich_dan_ton_tai` = 100% (không có mã `[Rxx]` hay đoạn trích nào sai nguồn)."

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`.

## 5. Đã chạy gì

Chưa có lượt đánh giá được ghi nhận.

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | — | — | Chưa chạy | — | — | Chưa biết |

## 6. Lỗi chính

Chưa có `eval/report.md` từ lượt chạy; chưa thể kết luận lỗi chính hoặc xác nhận chuẩn đạt.
