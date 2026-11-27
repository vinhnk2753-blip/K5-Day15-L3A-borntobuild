# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | | | | |
| Code UI issue #4 | Codex | Web gọi answer(text); bổ sung stats/flags, G10 dưới 3 review giữ lại và fake dùng chung trong backend theo yêu cầu hoàn thiện CP2; sửa nhận xét PR #18 | 34 test Python và 21 nhóm kiểm tra Chrome; Trang xác nhận đã kiểm tay bản trước và chốt khác biệt hợp đồng với Tuyên/Vinh ngày 27/11/2026; thay đổi bổ sung CP2 được ghi trong checklist, chưa gán xác nhận kiểm tay cũ cho code mới; API/crawler trong test được stub, chưa xác minh live | Trang |
| Prompt / thiết kế lời gọi mô hình | | | | |
| Đào data (viết script đếm, gợi ý nhãn) | Coding agent (Antigravity) | Hỗ trợ chuẩn hoá JSON ẩn danh từ review công khai (ĐMX/TGDĐ ngày 27/11/2026), viết script đếm tái lập `evidence/count.py`, gợi ý nhãn sơ bộ 60 dòng trong `evidence/cp2_labels.csv` và khung `data/CONTRACT.md`, `data/DATA_CARD.md` | Cần kiểm tay lại toàn bộ 60/60 nhãn & xác minh trích dẫn gốc trước khi nộp CP2/CP3 (trạng thái hiện tại: mới kiểm tự động toàn vẹn & PII 0 lỗi; chờ người kiểm tay điền số khớp 60 / 60) | Nguyễn Khánh Vinh |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | Claude Code (coding agent) | Viết script `eval/build_benchmark.py` chép nguyên văn review từ `data/products/*.json`; soạn nháp `expected`/`pass_criterion` của 15 câu B11–B25 và định nghĩa 4 metric trong `eval/metric_spec.yaml`; kiểm tự động mọi mã `[Rxx]` nhắc trong câu thử đều có trong input và đếm số review sạch theo `evidence/cp2_labels.csv` | Mỗi câu thử có `source`. Nguyễn Khánh Vinh review PR #19: đối chiếu 15 câu `data_that` với `data/products/*.json` (0 sai lệch, 0 lỗi PII) và yêu cầu sửa B15, B19, B21, B23, B25 cùng định nghĩa metric — đã sửa theo | Nguyễn Thị Hải Yến |
| Sinh data `synthetic` (nếu có) | | | Seed __ · kiểm tay __ dòng | |
| Chấm cột `pass` bằng LLM (nếu có) | | | Kiểm tra thủ công __ câu thử, khớp __/__ | |
| Slide, văn bản | | | | |
| Thiết kế UI và tài liệu issue #4 | Codex + Figma plugin | Thiết kế, hợp đồng input/output, hướng dẫn chạy và bảng đối chiếu UI | Người dùng đã xem và yêu cầu chỉnh thiết kế; không phải slide hay bằng chứng thật | Trang |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
