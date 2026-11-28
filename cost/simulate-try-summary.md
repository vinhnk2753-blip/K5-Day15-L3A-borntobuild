# Tóm tắt mô phỏng simulate-try@20261128-091210

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 5 | 1 | 2073 | 648 | 1.0 | 3.0 |
| dung_vua | 5 | 2 | 3712 | 1079 | 2.0 | 6.0 |
| dung_nhieu | 0 | 3 | — | — | — | — |

Tỉ lệ đạt dùng để tính: 23/25 (92%) — lượt run-2@20261127-224446

- Tự chọn: lượt run-N mới nhất đã chấm xong, chạy bằng đúng model đang đo (run-2.csv). Muốn dùng lượt khác (vd lượt 2): thêm `--rate-from eval/run-2.csv`.

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (500 người) | Chi phí / tháng — cơ sở (2.000 người) | Chi phí / tháng — cao (5.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-6-luna (vào 0.1 · ra 0.5 $/1M) | $0.00072 (≈ 19 ₫) | $0.00078 (≈ 20 ₫) | $0.00052 (≈ 14 ₫) | $1.44 (≈ 37.589 ₫) | $5.78 (≈ 150.355 ₫) | $14.44 (≈ 375.887 ₫) | $0.0029 (≈ 75 ₫) |
| gpt-6.2-sol (vào 2.0 · ra 10.0 $/1M) | $0.0144 (≈ 375 ₫) | $0.0157 (≈ 408 ₫) | $0.0105 (≈ 272 ₫) | $28.88 (≈ 751.774 ₫) | $115.52 (≈ 3.007.095 ₫) | $288.81 (≈ 7.517.737 ₫) | $0.0578 (≈ 1.504 ₫) |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.5) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gpt-6-luna. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/10.
- Tỷ giá: 1 USD = 26.030 ₫ (Vietcombank https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx, truy xuất 27/11/2026; DateTime nguồn 11/27/2026 9:35:19 PM, USD Sell=26,030.00 VND/USD. Snapshot dự toán theo giá bán USD, chưa gồm phí hoặc thay đổi tỷ giá của thẻ.).
