# Đối chiếu issue #4 — UI demo CP2

Nguồn đã đọc ngày 27/11/2026: [issue #4](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/issues/4), giao Nguyễn Quỳnh Trang, hạn CP2 19:30. Đã đối chiếu thêm [issue #3](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/issues/3) và [issue #8](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/issues/8) để phân biệt khung giả với tích hợp AI thật CP3. Chỉ đọc GitHub; chưa đánh dấu checkbox, bình luận hay đóng issue từ phiên này.

## Checklist và DoD kỹ thuật

| Checklist issue | Hiện thực trong repo | Kiểm chứng |
|---|---|---|
| Nhập/chọn sản phẩm hoặc dán review → cờ định lượng → tối đa 3 rủi ro + nguồn | Form tên sản phẩm/dán review, chọn 3 bộ synthetic; số cờ x/N và %, nhóm tín hiệu; tối đa 3 thẻ; nút Rxx mở dialog nguyên văn | API và Chrome: DEMO01 trả 3 thẻ, 1/4 = 25%, 3/4 review sạch; nguồn R01 khớp đầu vào |
| G10: quá ít review sạch và ngoài phạm vi | Ngưỡng tự chọn 2 review sạch khác nội dung; duplicate không làm tăng số sạch; guard trả insufficient_evidence hoặc out_of_scope, không gọi model | Unit, HTTP, Chrome: thiếu dữ liệu/ngoài phạm vi không có rủi ro, model_calls=0 |
| app.py gọi answer(text) fake và giữ tracing | Python HTTP server chỉ loopback; UI adapter gọi backend answer nguyên gốc, sau đó dựng JSON minh họa trong chế độ fake; lock quanh tracing.begin/end | DEMO01: model=fake, 1 lần gọi, 6 công cụ, token vào/ra 0; kết quả UI là mô phỏng, không phải output model thật |
| Chạy python run.py không lỗi cú pháp/dependency | run.py giữ nguyên; app.py mặc định mở web, không thêm package Python; asset HTML/CSS/JS phục vụ tại máy | Đã khởi động bằng đúng python run.py, HTTP và browser QA qua; kiểm JavaScript bằng node --check |

**DoD kỹ thuật của issue #4 đã được thực hiện trong bản local:** chạy đúng lệnh mở web và đi hết input → kết quả fake có tối đa 3 rủi ro + Rxx. Đây không phải xác nhận người phụ trách đã duyệt hoặc issue GitHub đã đóng.

## Ranh giới file sau khi thu gọn theo yêu cầu người dùng

- Giữ app.py, codebase/web, ui_demo.py và fixture codebase/ui_demo_data.json: chỉ UI dùng adapter này.
- Giữ test UI/HTTP/browser, hợp đồng I/O và hướng dẫn UI; .gitignore thêm .local/ cho ảnh QA.
- Đã trả nguyên nội dung HEAD cho codebase/agent.py, ai.py, tools.py; canvas/spec, data/DATA_CARD.md, toàn bộ thay đổi benchmark/metric/hồ sơ eval và evidence. Không tạo hoặc sửa phần việc của issue #1–#3.
- Đã bỏ docs/cp2-status.md và eval/cp2-calibration.csv do agent tạo ngoài phạm vi UI. Không xóa/sửa run CSV hoặc trace đã chạy.
- Eval/simulate vẫn gọi backend khung ban đầu, không nhập UI adapter. Cần phối hợp Tuyên để triển khai backend thật theo hợp đồng trong chặng sau.

## Quy ước định lượng

- Mẫu số N là toàn bộ review hợp lệ trong lần kiểm tra.
- Một review bị gắn cờ tính một lần vào tử số. Các nhóm hiện có: lặp nguyên văn sau chuẩn hóa, chưa dùng/nhận xu, chỉ giao hàng/đóng gói, chỉ dẫn ngoài phạm vi, khác.
- Review sạch là có dấu hiệu trải nghiệm, không thuộc cờ và không lặp theo heuristic. Đây không phải xác minh review thật; ngưỡng 2 là cấu hình demo chưa hiệu chỉnh trên data crawl.
- Rủi ro sắp theo số nội dung nguồn khác nhau được trích, không phải điểm an toàn, mức nguy hiểm hay tỷ lệ lỗi.
- Guard ngoài phạm vi chỉ nhận diện một số yêu cầu rõ ràng; AI thật và khả năng xử lý ngôn ngữ đầy đủ thuộc CP3. Review có cả phản ánh sản phẩm và lời khen giao hàng vẫn được giữ để phân tích.

## Kiểm thử và hiện vật

- `python -m unittest discover -s tests -v`: 14 test qua.
- `node --check codebase/web/app.js`: cú pháp hợp lệ.
- `node tests/browser_smoke.mjs`: 13 nhóm kiểm UI qua trên Chrome có sẵn; Node/Chrome chỉ là công cụ QA, không phải dependency chạy sản phẩm.
- Ảnh: `.local/ui-home.png`, `.local/ui-desktop.png`, `.local/ui-mobile.png`; báo cáo `.local/browser-smoke.json` (không commit).
- Kiểm cả source dialog, mẫu số, usage, input rỗng, G10, ngoài phạm vi, no_risk_found, lỗi mạng, sửa input ẩn kết quả cũ, nút xóa và viewport 1440/390/320 px.

Benchmark, metric, expected và chuẩn đạt đã được hoàn tác về bản Git ban đầu theo yêu cầu thu gọn phạm vi. Các CSV kết quả/trace đã chạy được giữ nguyên, không coi chúng là kết quả của bản backend sau hoàn tác. Guard G10 chỉ ở UI adapter, không thay đổi hành vi bộ eval của backend.

## Ngoài phạm vi issue #4

Dữ liệu crawl và bằng chứng thật còn chờ nhóm cung cấp. Nối model thật, persona và mô phỏng có token thật thuộc issue #8/CP3; không đánh dấu xong dựa trên fake. Số liệu trong giao diện hiện là từ review synthetic của lần chạy, không phải kết quả khảo sát hay eval chất lượng.
