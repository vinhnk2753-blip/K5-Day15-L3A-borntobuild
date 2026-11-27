# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code UI issue #4 | Codex | Web trong app.py, adapter UI giả tách riêng và kiểm thử; không sửa backend issue #3 | 14 test Python và kiểm thử Chrome; chưa có xác nhận thành viên đã rà | Trang |
| Prompt / thiết kế lời gọi mô hình | | | | |
| Đào data (viết script đếm, gợi ý nhãn) | Coding agent (Antigravity) | Hỗ trợ chuẩn hoá JSON ẩn danh từ review công khai (ĐMX/TGDĐ ngày 27/11/2026), viết script đếm tái lập `evidence/count.py`, gợi ý nhãn sơ bộ 60 dòng trong `evidence/cp2_labels.csv` và khung `data/CONTRACT.md`, `data/DATA_CARD.md` | Cần kiểm tay lại toàn bộ 60/60 nhãn & xác minh trích dẫn gốc trước khi nộp CP2/CP3 (trạng thái hiện tại: mới kiểm tự động toàn vẹn & PII 0 lỗi; chờ người kiểm tay điền số khớp 60 / 60) | Nguyễn Khánh Vinh |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | | | Mỗi câu thử có `source`; câu thử AI viết được ghi rõ | |
| Sinh data `synthetic` (nếu có) | | | Seed __ · kiểm tay __ dòng | |
| Chấm cột `pass` bằng LLM (nếu có) | | | Kiểm tra thủ công __ câu thử, khớp __/__ | |
| Thiết kế UI và tài liệu issue #4 | Codex + Figma plugin | Thiết kế, hợp đồng input/output, hướng dẫn chạy và bảng đối chiếu UI | Người dùng đã xem và yêu cầu chỉnh thiết kế; không phải slide hay bằng chứng thật | Trang |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
