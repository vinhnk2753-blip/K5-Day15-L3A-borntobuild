# Reflection — Giáp Mạnh Tuyên

> Làm ở guide bước 5.3. Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. **Vai trò + phần mình làm (trỏ tới file / commit):**
   Mình phụ trách thiết kế kiến trúc agent, luồng AI và công cụ lọc review/hậu kiểm trích dẫn `[Rxx]` (`TEAMS.md`).<br>
   Ở CP2–CP3, mình hoàn thiện luồng agent và nối model thật trong `codebase/agent.py`, `codebase/ai.py`, `codebase/tools.py` (`c0ce233`, `bd16565`).<br>
   Mình xây crawler Shopee chạy trong trang, hiển thị tiến độ và xuất JSON (`c7558f0`, `0a0d077`, `e5c6b2a`); PR #26 cải thiện lấy review từng mức sao và xử lý lỗi (`c36946b`, `eb911c4`).<br>
   Ở CP4, mình hoàn thành hai lượt eval và sửa lỗi về phạm vi review/citation sau lượt 1 (`317fe5a`, `eval/run-1.csv`, `eval/run-2.csv`), đồng chấm eval và hỗ trợ video dự phòng theo phân công trong `TEAMS.md`.

2. **AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):**
   Mình dùng Codex làm coding agent để viết và gỡ lỗi crawler, extension, luồng agent và backend local.<br>
   Mình đã yêu cầu chuyển sang crawl trực tiếp bằng JavaScript, lấy tối đa 50 review mỗi mức sao, hiển thị tiến độ và gửi JSON sang agent.<br>
   Mình không nhận nguyên kết quả đầu: các lần thử bộc lộ lỗi lấy nhầm review cũ, nhận diện sai ID và kết nối backend thất bại; mình dùng lỗi đó để điều chỉnh luồng và thông báo trong extension.<br>
   Khi rà output, mình chú ý kiểm tra review được trích có thật sự làm bằng chứng cho rủi ro hay không, ngoài việc mã `[Rxx]` có tồn tại.

3. **Một câu thử trượt của nhóm và mình học được gì từ nó:**
   Ở `B22` của `eval/run-2.csv`, model dùng `[R20]` — review cân bằng, thiên tích cực — làm bằng chứng rủi ro dù tiêu chí câu thử cấm điều đó (`eval/report.md`).<br>
   Nhóm đạt `25/32` ở metric `rui_ro_duoc_dan_chung` (`78,1%`), dưới ngưỡng `90%` (`eval/report.md`).<br>
   Ca này cho thấy kiểm tra citation có tồn tại chưa đủ; cần hậu kiểm vai trò và chiều nghĩa của review được trích, đồng thời tránh tiêu đề khẳng định quá mức khi mẫu còn nhỏ.
