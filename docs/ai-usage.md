# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Codex · Antigravity (coding agent) | Hỗ trợ viết và rà `codebase/agent.py`, `codebase/tools.py`, `codebase/ai.py`, `codebase/extension_server.py`, `extension/` và bộ test hợp đồng `codebase/test_agent.py` | Tự rà diff, chạy `python -m unittest discover -s codebase -v`, `python run.py check`, `eval --fake`, `eval --try 25`; sửa các lỗi tách review `[Rxx]`, lọc nhiễu và UI extension theo review PR #20 | Giáp Mạnh Tuyên |
| Prompt / thiết kế lời gọi mô hình | Codex · Antigravity (coding agent) | Hỗ trợ soạn system prompt `SYSTEM` (JSON schema, hậu kiểm citation, từ chối ngoài phạm vi) và tách luồng `user_request` an toàn trong `codebase/agent.py` | Kiểm đối chiếu với `spec.md` §4–§5, `eval/metric_spec.yaml` và bộ 25 câu thử; cần chạy thêm lượt OpenAI thật khi có `.env` và chấm tay độc lập | Giáp Mạnh Tuyên |
| Đào data (viết script đếm, gợi ý nhãn) | Coding agent (Antigravity) | Đợt 1 (27/11): chuẩn hoá 60 review ĐMX/TGDĐ (`SP01–SP03`), viết `evidence/count.py`, gợi ý `evidence/cp2_labels.csv` và khung `CONTRACT`/`DATA_CARD`. Đợt 2 (28/11 · Issue #5): thu thập & ẩn danh +90 review Tiki (`SP04–SP06`, nâng `N = 150`), gợi ý `evidence/cp3_labels.csv`, nâng cấp `evidence/count.py`, chụp & che PII 4 ảnh luồng hiện tại (`evidence/screenshots/`), soạn `evidence/data-mining.md`, `data/DATA_CARD.md` và `spec.md` §0, §2 | Đợt 1: Nguyễn Khánh Vinh đã kiểm tay khớp **60/60** nhãn (commit `886ddf1`). Đợt 2: đã chạy kiểm tự động `python evidence/count.py` (150/150 dòng khớp, 0 lỗi PII), `19/19` unit test và kiểm trực quan 4/4 ảnh che PII; chờ Nguyễn Khánh Vinh rà tay đối chiếu 90/90 nhãn `cp3_labels.csv` và xác nhận số ước tính ở §2 trước khi nộp CP3 | Nguyễn Khánh Vinh |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | Claude Code (coding agent) | Viết script `eval/build_benchmark.py` chép nguyên văn review từ `data/products/*.json`; soạn nháp `expected`/`pass_criterion` của 15 câu B11–B25 và định nghĩa 4 metric trong `eval/metric_spec.yaml`; kiểm tự động mọi mã `[Rxx]` nhắc trong câu thử đều có trong input và đếm số review sạch theo `evidence/cp2_labels.csv` | Mỗi câu thử có `source`. Nguyễn Khánh Vinh review PR #19: đối chiếu 15 câu `data_that` với `data/products/*.json` (0 sai lệch, 0 lỗi PII) và yêu cầu sửa B15, B19, B21, B23, B25 cùng định nghĩa metric — đã sửa theo | Nguyễn Thị Hải Yến |
| Sinh data `synthetic` (nếu có) | | | Seed __ · kiểm tay __ dòng | |
| Chấm cột `pass` bằng LLM (nếu có) | | | Kiểm tra thủ công __ câu thử, khớp __/__ | |
| Slide, văn bản | | | | |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
