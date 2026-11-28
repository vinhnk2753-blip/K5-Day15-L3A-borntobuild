# Tóm tắt mô phỏng simulate-1@20261128-110814

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 25 | 1 | 1990 | 538 | 1.0 | 3.0 |
| dung_vua | 20 | 2 | 3903 | 1026 | 2.0 | 6.0 |
| dung_nhieu | 4 | 3 | 5859 | 1710 | 3.0 | 9.0 |

Tỉ lệ đạt dùng để tính: 23/25 (92%) — lượt run-2@20261127-224446

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (500 người) | Chi phí / tháng — cơ sở (2.000 người) | Chi phí / tháng — cao (5.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-6-luna (vào 0.1 · ra 0.5 $/1M) | $0.00073 (≈ 19 ₫) | $0.00079 (≈ 21 ₫) | $0.00050 (≈ 13 ₫) | $1.95 (≈ 50.684 ₫) | $7.79 (≈ 202.738 ₫) | $19.47 (≈ 506.844 ₫) | $0.0039 (≈ 101 ₫) |
| gpt-6.2-sol (vào 2.0 · ra 10.0 $/1M) | $0.0145 (≈ 378 ₫) | $0.0158 (≈ 410 ₫) | $0.0100 (≈ 261 ₫) | $38.94 (≈ 1.013.688 ₫) | $155.77 (≈ 4.054.753 ₫) | $389.43 (≈ 10.136.884 ₫) | $0.0779 (≈ 2.027 ₫) |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.6) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gpt-6-luna. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 1/50.
- Tỷ giá: 1 USD = 26.030 ₫ (Vietcombank https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx, truy xuất 27/11/2026; DateTime nguồn 11/27/2026 9:35:19 PM, USD Sell=26,030.00 VND/USD. Snapshot dự toán theo giá bán USD, chưa gồm phí hoặc thay đổi tỷ giá của thẻ.).
