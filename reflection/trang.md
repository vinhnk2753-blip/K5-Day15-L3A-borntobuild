# Reflection — Nguyễn Quỳnh Trang

Nhóm: borntobuild · Lớp L3A · GitHub: `@NguyenTrang005` · Ngày viết: 28/11/2026.

1. Vai trò + phần mình làm (trỏ tới file / commit):

   Em phụ trách giao diện web, mô phỏng chi phí và tổ chức người dùng thử.
   Phần UI ban đầu và đồng bộ backend nằm ở [app.py](../codebase/app.py), [ui_backend.py](../codebase/ui_backend.py), [web/](../codebase/web/) và [báo cáo PR #18](../docs/pr-18-review-fixes.md): nhập/chọn review, hiển thị nhiễu, tối đa ba rủi ro và mở nguồn `[Rxx]`.
   Em hoàn thiện [personas.yaml](../cost/personas.yaml) và [cost-estimate.md](../cost/cost-estimate.md), với 50 phiên mô phỏng thật, 49 phiên không lỗi và một phiên HTTP 502/503; kết quả được ghi rõ, không sửa dữ liệu chạy để bỏ lỗi ([commit 18e9656](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/commit/18e9656)).
   Em tổ chức hai người ngoài nhóm dùng thử và ghi [U01](../validation/U01.md), [U02](../validation/U02.md), [log tổng hợp](../validation/log.md); cả hai hoàn thành có trợ giúp, cho thấy bước nhập review thủ công còn gây khó khăn ([commit e7b68c1](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/commit/e7b68c1)).

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):

   Em dùng Codex để hỗ trợ viết/rà UI, test, cấu hình persona và tổng hợp tài liệu; phần thiết kế ban đầu có hỗ trợ từ Figma plugin, được khai trong [docs/ai-usage.md](../docs/ai-usage.md).
   Qua review PR #18, phần do AI hỗ trợ phải thu gọn về đúng UI, bỏ helper/backend trùng lặp và sửa cách đọc schema `stats`, `flags`, `anomalies`, `reviews_by_id` để dùng chung backend của Tuyên.
   Em chạy thử UI với model thật, kiểm các trạng thái bình thường, nhiều nhiễu, thiếu dữ liệu, yêu cầu ngoài phạm vi và popup nguồn; em cũng rà lại số liệu chi phí và bản tổng hợp người dùng thử.
   Qua đó, em thấy cần kiểm đầu ra AI theo hợp đồng chung và bằng chứng thực tế; một bản code chạy được hoặc một báo cáo trình bày đẹp chưa đủ để xác nhận đúng.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:

   Em chọn **B22** trong [benchmark](../eval/benchmark.csv) và [eval/run-2.csv](../eval/run-2.csv), ca pin dự phòng với phản ánh sạc iPhone; câu này vẫn bị chấm trượt ở lượt 2 đã được Yến xác nhận.
   Tiêu chí yêu cầu dùng R06 và/hoặc R15, không dùng R20 làm bằng chứng rủi ro; output vẫn trích R20 vào thẻ thời gian sạc lâu dù review đó có bối cảnh đã biết công suất thấp và thông tin đối chứng.
   Bài học của em là **mã nguồn tồn tại và đoạn trích khớp nguyên văn chưa bảo đảm nguồn đó hỗ trợ đúng kết luận**; cần kiểm cả ý nghĩa, bối cảnh và mức chắc chắn, không chỉ định dạng citation.
   Với phần UI, popup review gốc giúp người dùng đối chiếu nhưng không thay thế hậu kiểm ngữ nghĩa; khi trình bày kết quả, em cần giữ giới hạn phản ánh đơn lẻ và không gọi 92% câu đạt là mọi metric đều đạt ([eval/report.md](../eval/report.md)).
   Nếu làm tiếp, em ưu tiên phối hợp nhóm kiểm lại các thẻ dùng nguồn sai và cho người mới thử lại luồng nhập liệu, thay vì chỉ bổ sung tính năng trước khi xác nhận vấn đề cũ đã được giải quyết.
