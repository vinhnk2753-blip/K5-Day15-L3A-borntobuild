# Đối chiếu review PR #18

Review của vinhnk2753-blip trên commit `3984bcf`: [yêu cầu chỉnh sửa](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/pull/18#pullrequestreview-6087817796).

## Bổ sung hoàn thiện CP2 sau review

Người dùng yêu cầu bổ sung ba mục còn thiếu: định lượng, demo fake có 3 rủi ro và web gọi answer(text). Hiện web serialize input sang JSON và gọi answer một lần; nhận output chuỗi + structured, không parse output hoặc gọi model hai lần. Công cụ định lượng dùng chung backend, có nguồn cho từng cờ; G10 dưới 3 review giữ lại không gọi model. Demo tai nghe cho 4 review, loại 1 (25%), giữ 3 và 3 rủi ro giả có trích dẫn nguyên văn. Không còn các mục thiếu đó trong checklist triển khai.

Kiểm mới: **34 test Python**, **21 nhóm Chrome QA**; demo mặc định đi qua answer thật trong app với model fake, không cần chèn response fixture. API/crawler live chưa được xác minh. Backend agent/tools được bổ sung theo yêu cầu lần này; framework, ai.py, chuẩn đạt, metric và benchmark giữ nguyên. [Checklist hiện tại](issue-4-checklist.md) và [hợp đồng hiện tại](ui-ai-contract-proposal.md) thay thế mô tả hành vi trong bảng lịch sử bên dưới.

Xác nhận kiểm tay của Trang áp dụng bản trước lần bổ sung; không tự ghi người dùng đã rà code backend mới.

## Lịch sử xử lý review ở bản trước

| Nhận xét | Cách xử lý và kiểm chứng |
|---|---|
| Blocker nối `answer()` với main `4b1f050` | Đã merge main trong `b118ab7`; `ee8ce30` chuyển web sang `analyze_reviews`, không parse văn bản `answer()` như JSON. CLI vẫn dùng `answer(link)`. Test fake và HTTP stub OpenAI kiểm đúng usage. |
| Từ khóa `pin/shipping`, `ship/flagship`, `lỗi/xin lỗi`; hai danh sách từ khác nhau | Đã bỏ `ui_demo.py` và toàn bộ bộ sinh kết quả riêng. UI không phân loại nhiễu hoặc suy rủi ro bằng từ khóa. Không còn số review sạch giả. |
| `[R01]` bị parse JSON | Đã bỏ bộ đoán JSON từ raw text. Web nhận dòng `số sao | nội dung`; nội dung `[R01]` giữ nguyên. Raw text không có sao theo hợp đồng MWG chưa được backend Shopee hỗ trợ, ghi rõ giới hạn thay vì nhận nhầm JSON. |
| Gọi tool định lượng hai lần; gắn cờ khi lỗi | Đã bỏ tool định lượng riêng của UI. Dán review chỉ gọi phân tích một lần; link gọi crawler một lần rồi phân tích. Kết quả lỗi không hiển thị thống kê hoặc rủi ro mô phỏng. |
| URL trong review kích hoạt crawler | Test mới giữ URL ngoài Shopee/Shopee bên trong nội dung review; không gọi crawler ở chế độ dán. |
| Route `/api/products/foo/bar/DEMO01` vẫn khớp | Chỉ nhận một segment mã sản phẩm; test đường dẫn lồng, rỗng và dấu `/` cuối trả 404. |
| Body rỗng trả 413 | Content-Length rỗng/không hợp lệ trả 400; vượt 2 MB trả 413. Test từ chối ngay ở header. |
| Thiếu log ngoại lệ | Console chỉ ghi tên loại ngoại lệ; test bảo đảm không ghi body lỗi nhà cung cấp hoặc trả nó ra client. |
| Cổng âm/ngoài giới hạn | Bắt `OverflowError`; test `-1`, `65536` và chuỗi sai thoát gọn với mã 1. |
| Hiện cảnh báo dữ liệu cũ ngay lần nhập đầu | Theo dõi đã có kết quả; chỉ cảnh báo khi sửa dữ liệu sau kết quả, giữ qua nhiều lần sửa và ẩn khi có kết quả mới. Chrome kiểm cả ba nhánh. |
| Mất thông báo HTTP 400/403/413 | Giữ `message` của máy chủ khi payload không có `analysis`; Chrome kiểm 400/403/413/502, không hiện thống kê cho lỗi. |
| Ghi đè dòng khai báo AI chung | Khôi phục `Code bản chạy thử` và `Slide, văn bản`; khai báo UI ở các dòng riêng, giữ dòng dữ liệu của Vinh. README giữ chỗ khai báo chung và model thật cần xác minh. |
| README web và dấu nhắc CLI mâu thuẫn | Mặc định `python run.py` mở web; hướng dẫn dấu nhắc chỉ áp dụng khi đặt `REVIEW_LENS_MODE=cli`. |
| CSS khó review | Chuyển thành nhiều dòng; giữ nguyên nội dung CSS ngoài khoảng trắng. |
| Profile Chrome QA tồn đọng | `finally` đợi Chrome thoát, kiểm tra đường dẫn là thư mục riêng trong temp rồi xóa; kiểm tra thư mục đã biến mất. |

Kiểm chứng bản trước: **23 test Python đạt**, **18 nhóm kiểm tra Chrome đạt**; chạy web qua `python run.py` ở cổng 8001. Test OpenAI/crawler dùng stub; thẻ rủi ro browser dùng response fixture riêng, chưa xác minh dịch vụ live. Tại bản đó chưa sửa backend/framework/metric/benchmark/kết quả eval.

## Xác nhận người phụ trách và trạng thái duyệt

- **Kiểm tay code/fixture — đã xác nhận:** ngày 27/11/2026, Trang xác nhận đã kiểm tay code và dữ liệu mẫu. Cập nhật README, khai báo AI, checklist và provenance của `ui_demo_data.json` theo xác nhận này.
- **Chốt hợp đồng nhóm — đã xác nhận:** ngày 27/11/2026, Trang xác nhận đã chốt khác biệt hợp đồng MWG/Shopee với Tuyên/Vinh. Bản bổ sung CP2 đã có định lượng và G10 ngưỡng 3; catalog SP01–SP03/review không sao vẫn chưa được nối vào backend Shopee. [Hợp đồng UI](ui-ai-contract-proposal.md) mô tả code hiện tại.
- **Duyệt PR:** review đang `CHANGES_REQUESTED`; các commit sửa không thay thế việc reviewer kiểm lại và duyệt. Không tự resolve nhận xét hoặc merge PR.
