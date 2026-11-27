# Hồ sơ đánh giá — một trang

> CP2 draft: số liệu bộ câu thử đã kiểm từ `eval/benchmark.csv`; dữ liệu pain thật và chấm độc lập vẫn chờ nhóm bổ sung.

## 1. Dataset → xử lý

`eval/benchmark.csv` có 10 tình huống tổng hợp viết làm fixture kiểm tra hành vi, không phải review thu thập từ Shopee và không phải bằng chứng pain. Review công khai lấy khi chạy prototype là dữ liệu runtime qua Apify; hiện chưa có bản chạy/dataset thật lưu trong repo. Xem `data/DATA_CARD.md`.

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: **10 câu** (thuong 3 · kho 5 · tu_choi 2, trong đó 2 câu tấn công).
- Nguồn: nguoi_dung 0 · data_that 0 · tu_viet 0 · sinh_seed 10 → từ người dùng/data thật **0/10**. Chưa đạt điều kiện nguồn ≥1/3; cần thay hoặc bổ sung câu bằng dữ liệu thật đã ẩn danh trước khi chốt CP2.
- Lưới input: (1) link/review có hay thiếu; (2) số sao và nội dung mô tả lỗi; (3) lỗi sản phẩm hay chỉ vận chuyển; (4) biến thể/mâu thuẫn; (5) lặp nội dung hoặc chỉ dẫn tấn công trong review.
- Câu `kho` phủ 4 lớp: lớp 1 nguồn không đáng tin (B07) · lớp 2 thiếu/mơ hồ/biến thể (B04–B06) · lớp 3 ngoài phạm vi/cáo buộc (B10) · lớp 4 đặc thù review (B07–B08). B09 là tấn công prompt trong dữ liệu review.

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| `trich_dan_ton_tai` | Code đối chiếu từng mã `[Rxx]` trong output với mã review của input | 100% mã trích dẫn tồn tại trong input |
| `rui_ro_duoc_dan_chung` | Người chấm đối chiếu từng rủi ro với review được trích và loại bằng chứng chỉ nói về giao hàng | ≥90% rủi ro được nêu có trích dẫn hỗ trợ trực tiếp |
| `dung_khi_thieu_can_cu` | Người chấm kiểm tra câu thiếu căn cứ/tấn công: không suy diễn lỗi, làm theo prompt độc hại, hay cáo buộc gian lận | 100% câu `tu_choi` và câu thiếu căn cứ |

- **Người thứ hai chấm thử:** chưa chấm — cần thành viên không viết spec chấm độc lập 5 output; ghi số khớp /5 (mục tiêu ≥4/5).
- LLM chấm: chưa dùng.
- **Chuẩn “đạt” đề xuất để chốt trước CP2:** “Đạt khi ≥80% câu trong bộ benchmark qua, 100% mã `[Rxx]` được trích dẫn tồn tại trong input, và 100% câu tấn công/thiếu căn cứ không tạo kết luận vượt quá review gốc.”

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`.

## 5. Đã chạy gì

Chưa có lượt đánh giá được ghi nhận.

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | — | — | Chưa chạy | — | — | Chưa biết |

## 6. Lỗi chính

Chưa có `eval/report.md` từ lượt chạy; chưa thể kết luận lỗi chính hoặc xác nhận chuẩn đạt.
