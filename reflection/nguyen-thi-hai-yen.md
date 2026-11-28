# Reflection — Nguyễn Thị Hải Yến

> Làm ở guide bước 5.3. Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. **Vai trò + phần mình làm (trỏ tới file / commit):**
   Mình phụ trách bằng chứng pain, bộ câu thử + báo cáo eval, và slide demo (`spec.md` §9).
   - Phỏng vấn pain P1–P4: `evidence/interviews/P1.md`–`P4.md` (`21b8a9c`), tổng hợp ở `evidence/summary.md` (`3d1e9d1`, PR #22).
   - Bộ câu thử CP2: viết 15 câu B11–B25 từ 60 review thật (`2937a89`), chốt 4 metric và chuẩn đạt (`cf5e231`, `9b44b31`), sửa B15/B19/B21/B23/B25 theo review PR #19 (`a419ffc`).
   - Chấm eval: rà từng câu `pass` của cả 2 lượt, 25/25 câu mỗi lượt (`c0aedec`, PR #25), ghi kết quả vào `eval/report.md` và `spec.md` §7 (`dd9640b`).
   - Slide demo: dàn ý 8 trang ở `slides/outline.md` (`d6d9da1`) → `demo-slides.pdf`.

2. **AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):**
   - Claude Code viết `eval/build_benchmark.py` để chép nguyên văn review từ `data/products/*.json`, soạn nháp `expected`/`pass_criterion` cho B11–B25 và định nghĩa metric. Nó cũng tự kiểm rằng mọi mã `[Rxx]` nhắc tới đều có trong input.
   - Output AI chưa dùng được ngay: Vinh review PR #19 và yêu cầu sửa 5 câu (B15, B19, B21, B23, B25) cùng định nghĩa metric, mình đã sửa lại theo đó. Bài học: AI viết `pass_criterion` nghe hợp lý nhưng hay chưa đủ chặt để chấm.
   - Codex chấm nháp cột `pass`. Mình rà lại tay từng câu với input, output và `pass_criterion`, và đồng ý 25/25 câu mỗi lượt. Vinh chấm mù thêm 5 câu, khớp 5/5.

3. **Một câu thử trượt của nhóm và mình học được gì từ nó:**
   - **B12, lượt 1:** tập review gửi vào chỉ có R02 (khách tự đánh rơi), một review trống và lời khen, nên kỳ vọng là 0 rủi ro. Agent lại nêu rủi ro kèm mã R01, R05, R07, mà ba mã này không hề có trong input: nó đã lấy thêm review từ cả catalog chỉ vì tên sản phẩm khớp.
   - Cùng một lỗi này làm trượt 12/25 câu ở lượt 1. Sau khi sửa `answer()` để chỉ dùng đúng tập review được gửi, lượt 2 lên 23/25, citation hợp lệ từ 12/24 lên 21/21 (`eval/report.md`).
   - Điều mình học được: những câu "bẫy" kiểu chỉ có nhiễu, không có bằng chứng thì lại bắt được lỗi nặng nhất. Khi viết câu thử nên có chủ ý thêm câu mà đáp án đúng là "không có rủi ro", và chuẩn chấm phải kiểm cả phạm vi nguồn của citation chứ không chỉ xem mã có đúng định dạng hay không.
