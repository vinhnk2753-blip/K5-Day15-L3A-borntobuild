# Issue #11 — báo cáo mô phỏng chi phí CP4

Phụ trách: Nguyễn Quỳnh Trang (`@NguyenTrang005`). CP4: 14:30 ngày 28/11/2026.
[Issue #11](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/issues/11).
Nhánh: `feat/issue-11-cost-analysis`, đồng bộ main `dfdbd0b` gồm PR #23 (Issue #8) và PR #25 (Issue #10).

## Phạm vi hiện tại

Đã đồng bộ main dfdbd0b, dùng điểm eval được Yến xác nhận trong PR #25 và hoàn tất lượt 50 phiên theo yêu cầu tiếp tục của Trang. Báo cáo ghi rõ 49 phiên không lỗi, 1 phiên HTTP 502/503. Bàn giao trên nhánh `feat/issue-11-cost-analysis`; Trang sẽ tự tạo PR, chưa đóng issue.

## Đã chuẩn bị

- [x] Đọc Issue #11/#10; Issue #11 chưa có bình luận bổ sung.
- [x] Rà YAML: 3 persona, share=1, low/base/high=500/2.000/5.000; phân biệt dự toán và số đã đo.
- [x] Ghi nguồn/ngày snapshot 2 mức giá và tỷ giá; phân biệt giá OpenAI tham chiếu với biểu phí ShopAIKey.
- [x] Hoàn thiện `cost/cost-estimate.md`: đầu vào, công thức, bảng summary nguyên văn, giới hạn và kết luận đối chiếu impact tự ước tính.
- [x] Soạn độ nhạy theo mức giá, quy mô, tần suất, rate, token; không bịa kết quả tối ưu.
- [x] Cập nhật `spec.md` §8 về trạng thái thực tế và changelog §10; giữ chuẩn §7.
- [x] Đối chiếu PR #25/main dfdbd0b: Yến đã xác nhận 23/25 (92%); không tự xác nhận thay người chấm.
- [x] Kiểm offline: `python cost/check_personas.py` không có cảnh báo; `python run.py check` đạt. Tài liệu mới không cần gọi model để kiểm.

## Đối chiếu checklist Issue #11

- [x] Issue #10 xác nhận lượt eval và điểm cuối; score run-2 kiểm lại 23/25.
- [x] Chạy mô phỏng 50 phiên thật với `--rate-from eval/run-2.csv`: `simulate-1@20261128-110814`, seed 42, 80 lượt; 49 phiên không lỗi, 1 phiên lỗi. Không gọi đây là 50 phiên thành công.
- [x] Đối chiếu CSV/summary/trace: 80 model calls, 240 tool calls, 320 trace event; 153.124/41.166 token vào/ra, cùng run ID. Hai model call lỗi nằm trong S024; 78 call có usage.
- [x] Tính lại chi phí độc lập khớp khung trên 49 phiên không lỗi; chép nguyên 2 bảng summary, ghi chi phí usage của phiên lỗi riêng; giữ CSV/trace nguyên trạng.
- [x] So sánh ≥2 mức giá, có giả định và độ nhạy; chỉ đo token gpt-6-luna, chưa chạy/chấm model thứ hai.
- [x] Chốt kết luận pilot, đồng bộ §8 và changelog §10; không sửa chuẩn/eval của main.
- [x] Trang xác nhận đã rà soát lại số liệu Issue #11 ngày 28/11/2026; xác nhận này áp dụng cho số liệu, không tự mở rộng thành đã rà toàn bộ code.
- [x] Trang tạo PR #27 để nhóm review và bàn giao số liệu cho Issue #13.

## Kết quả để đưa vào slide Issue #13

| Mức giá áp lên cùng token | VND/phiên | VND/task thành công theo rate 92% | Tháng low | Tháng base | Tháng high | VND/người/tháng base |
|---|---:|---:|---:|---:|---:|---:|
| gpt-6-luna | 19 | 21 | 50.684 | 202.738 | 506.844 | 101 |
| gpt-6.2-sol | 378 | 410 | 1.013.688 | 4.054.753 | 10.136.884 | 2.027 |

Nguồn: `cost/simulate-1-summary.md`, USD→VND 26.030. Các số đã làm tròn theo khung. Dòng model thứ hai giả định cùng token và rate, chưa chứng minh chất lượng model thứ hai. Chỉ số task dựa vào eval từng câu, không trực tiếp đo cả phiên nhiều lượt thành công.

49/50 phiên không lỗi (98% về kỹ thuật) khác với 23/25 câu eval đạt (92% chất lượng). S024 nhận HTTP 502/503, bị khung loại toàn phiên khỏi trung bình. Báo cáo có phần usage vẫn phát sinh ở phiên lỗi; chưa dự báo retry hoặc chi phí không trả usage. Impact 19,5 phút/người/tháng là tự ước tính, chưa đo validation.

Kiểm sau đồng bộ: 46/46 test Python, run.py check và check_personas.py đạt. Hai bảng báo cáo được chép nguyên từ summary; số CSV/trace, run ID và phép tính chi phí được đối chiếu độc lập. Chưa cần chạy lại model để kiểm tài liệu.
