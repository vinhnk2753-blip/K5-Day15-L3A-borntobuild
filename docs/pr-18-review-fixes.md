# Đối chiếu review PR #18

Review của vinhnk2753-blip trên commit `3984bcf`: [yêu cầu chỉnh sửa](https://github.com/vinhnk2753-blip/K5-Day15-L3A-borntobuild/pull/18#pullrequestreview-6087817796).

## Những điểm đã xử lý

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

Kiểm chứng: **23 test Python đạt**, **18 nhóm kiểm tra Chrome đạt**; chạy web qua `python run.py` ở cổng 8001. Test OpenAI/crawler dùng stub; thẻ rủi ro browser dùng response fixture riêng, chưa xác minh dịch vụ live. Không sửa backend, framework, metric, benchmark hay kết quả eval.

## Những điểm còn cần người phụ trách

- **Kiểm tay code/fixture:** Trang trả lời chưa rà; giữ ghi chú cần xác nhận trong README, khai báo AI, checklist và provenance của `ui_demo_data.json`. Không tự ghi đã kiểm tay.
- **Chốt hợp đồng nhóm:** backend Shopee hiện có khác `data/CONTRACT.md` của bộ MWG ở catalog SP01–SP03, sao review, thống kê nhiễu và ngưỡng G10. UI đã bỏ ngưỡng riêng, mô tả đúng code đang chạy tại [hợp đồng UI](ui-ai-contract-proposal.md). Chưa có xác nhận thống nhất từ Tuyên/Vinh; chưa đánh dấu hoàn thành yêu cầu này hoặc cờ nhiễu định lượng.
- **Duyệt PR:** review đang `CHANGES_REQUESTED`; các commit sửa không thay thế việc reviewer kiểm lại và duyệt. Không tự resolve nhận xét hoặc merge PR.
