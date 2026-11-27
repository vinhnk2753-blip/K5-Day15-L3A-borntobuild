# Issue #4 — hoàn thiện khung UI CP2

Phạm vi: phần việc Nguyễn Quỳnh Trang trong [issue #4](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/issues/4), cập nhật trên PR #18.
Sau khi đồng bộ backend Tuyên, người dùng yêu cầu bổ sung nốt định lượng, demo giả 3 rủi ro và điểm nối answer(text).

## Checklist triển khai

- [x] Giao diện tối giản: nhập link Shopee hoặc dán review có sao; chọn bộ minh họa.
- [x] Hiện cờ nhiễu/bất thường định lượng: tổng xét, số loại, tỷ lệ, số giữ; từng loại có nguồn Rxx.
- [x] Tối đa 3 rủi ro theo dữ liệu, có review gốc đối chiếu trong popup.
- [x] G10: dưới 3 review giữ lại sau lọc theo quy tắc → insufficient, không gọi model.
- [x] URL ngoài Shopee bị từ chối; lỗi đầu vào/cấu hình/mạng có thông báo và giữ dữ liệu.
- [x] codebase/app.py mở web; adapter gọi đúng agent.answer(text) một lần. Output luôn là str; structured là khóa bổ sung, không phá hợp đồng khung.
- [x] Tracing đếm model/tool/token thực tế; tool định lượng gọi một lần, không tính lại ở UI.
- [x] python run.py chạy được bằng Python stdlib; không thêm dependency.
- [x] 34 test Python và 21 nhóm kiểm tra Chrome đạt; kiểm desktop 1440 và mobile 390/320.

## Kịch bản demo DoD

1. Đặt MODEL_PROVIDER=fake, chạy python run.py.
2. Chọn **Dán tập review có số sao → Tai nghe minh họa → Kiểm tra rủi ro**.
3. Kết quả từ answer: 4 review xét, loại 1 review chưa dùng (25%), giữ 3.
4. Xem 3 rủi ro minh họa: kết nối, pin, cảm giác đeo; mở [R01], [R03], [R04] để đối chiếu nguyên văn. Cờ chưa dùng mở [R02].
5. Tracing: model=fake, model_calls=1, tool_calls=1, tokens_in=0, tokens_out=0.
6. Chọn mẫu chỉ nói chưa dùng/nhận xu: giữ 0/3, báo chưa đủ dữ liệu, model_calls=0, tool_calls=1.
7. Dán ít nhất 3 review tích cực khác nhau: không ép tạo rủi ro; ngoài Shopee bị chặn trước khi gọi tool/model.

Nhãn giả lập hiện xuyên suốt. Thống kê là kết quả quy tắc trên mẫu input, không phải đánh giá độ chính xác AI; không kết luận seeding hoặc shop gian lận.
Không gọi API/crawler thật trong kiểm thử. Link thật vẫn cần cấu hình Apify; demo bằng chế độ dán không gọi crawler.

## Phạm vi backend và hợp đồng

Theo yêu cầu bổ sung, thay đổi agent.py/tools.py để web, CLI, extension dùng chung định lượng, G10 và fake; tách review_input.py/review_signals.py.
Giữ nguyên tracing.py, run.py, ai.py, chuẩn đạt, metric và benchmark. Các cập nhật eval/spec từ main là commit của nhóm được merge vào nhánh, không phải sửa chuẩn để khớp output.

Ngưỡng 3 khớp data/CONTRACT.md; catalog MWG SP01–SP03 và review không có sao vẫn chưa được backend Shopee hỗ trợ, không thuộc ba mục vừa yêu cầu.
Chi tiết schema/quy tắc: [hợp đồng UI](ui-ai-contract-proposal.md).

## Xác nhận và bàn giao

Trang đã xác nhận kiểm tay code/fixture của bản trước và chốt khác biệt MWG/Shopee với Tuyên/Vinh ngày 27/11/2026.
Lần bổ sung này có thay đổi backend và được kiểm tự động như trên; không tự gán xác nhận kiểm tay trước đó cho code mới.
PR #18 vẫn cần reviewer kiểm lại/duyệt; file này đánh dấu tiến độ triển khai, không tự đóng issue hoặc merge.
