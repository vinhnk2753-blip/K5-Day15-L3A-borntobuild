# Chi phí khi dùng thật

> Issue #11 · Nguyễn Quỳnh Trang (`@NguyenTrang005`) · CP4 14:30 ngày 28/11/2026.
> **Kết quả CP4, ngày 28/11/2026.** Đã đồng bộ main `dfdbd0b`, dùng điểm eval được Yến xác nhận trong PR #25. Đã chạy 50 phiên thật: 49 phiên không lỗi, 1 phiên HTTP 502/503; bảng trung bình theo khung loại phiên lỗi.
> Kết quả phải chép từ `cost/simulate-N-summary.md` sau lượt ≥50 phiên, không sửa CSV/trace. Dùng giá trả phí khi lập dự toán.

## 1. Đầu vào

### Persona và quy mô

Nguồn cấu hình: [personas.yaml](personas.yaml); dự toán đồng bộ [spec.md §2](../spec.md). Các thông số dưới đây **tự ước tính**, chưa phải số người dùng hay tần suất đã đo từ phỏng vấn.

| Persona | Tỷ lệ người dùng | Phiên/người/tháng | Lượt phân tích/phiên | Nguồn và giới hạn |
|---|---:|---:|---:|---|
| dung_it | 50% | 2 | 1 | Tham khảo hành vi P1/P3; phỏng vấn chưa đo các thông số tải |
| dung_vua | 35% | 4 | 2 | Tham khảo 4 lần mua online/tháng; số lần mua không đồng nghĩa số lần dùng công cụ |
| dung_nhieu | 15% | 10 | 3 | Giả định phân khúc dùng nhiều; chưa có bằng chứng phỏng vấn xác nhận |

Tổng tỷ lệ = 1; bình quân gia quyền **3,9 phiên và 8,3 lượt phân tích/người/tháng**. Mỗi lượt gọi `answer(text)` độc lập, không phải chat có bộ nhớ.

| Kịch bản | Người dùng hoạt động/tháng | Trạng thái nguồn |
|---|---:|---|
| low | 500 | Tự ước tính cho pilot |
| base | 2.000 | Tự ước tính cho pilot |
| high | 5.000 | Tự ước tính cho pilot |

Tham khảo thị trường, không phải bằng chứng số người dùng pilot: [Báo Đầu tư — hơn 61 triệu người mua online](https://baodautu.vn/hon-61-trieu-nguoi-viet-mua-sam-online-kiem-soat-cac-san-thuong-mai-dien-tu-the-nao-d229437.html), [Báo Công Thương — 4 lần mua online/tháng](https://congthuong.vn/trung-binh-1-nguoi-tieu-dung-viet-nam-mua-hang-truc-tuyen-4-lanthang-366168.html). Nguồn chi tiết và ngày chốt từng tham số nằm trong YAML.

### Giá, tỷ giá và model đo token

Snapshot từ `cost/personas.yaml`, ngày xem 27/11/2026; giá model được đối chiếu lại với tài liệu OpenAI ngày 28/11/2026, không thay đổi. USD/1 triệu token, Standard, không cache:

| Mức giá tham chiếu | Input | Output | Nguồn |
|---|---:|---:|---|
| gpt-6-luna | 0,10 USD | 0,50 USD | [OpenAI model](https://developers.openai.com/api/docs/models/gpt-6-luna.md) |
| gpt-6.2-sol | 2,00 USD | 10,00 USD | [OpenAI model](https://developers.openai.com/api/docs/models/gpt-6.2-sol.md) |

Tỷ giá dự toán **1 USD = 26.030 VND**, giá bán USD theo [Vietcombank XML](https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx), snapshot 27/11/2026 trong YAML; chưa gồm phí hoặc tỷ giá thẻ.

Model ghi nhận trong CSV/trace là `gpt-6-luna`, theo cấu hình ShopAIKey của Trang. Token lấy từ `usage` API, không tự ước lượng.
So sánh hai mức giá trên cùng token là phân tích giá; chỉ gpt-6-luna được đo trong lượt này. Chưa chạy gpt-6.2-sol, chưa chứng minh hai model có cùng chất lượng/tokenizer. Cột task/câu hỏi thành công ở mức giá thứ hai chỉ là kịch bản giả định dùng cùng token và tỷ lệ đạt, không phải kết quả eval model thứ hai.

### Tỷ lệ đạt — Issue #10 đã xác nhận

`eval/run-2.csv` ghi **23/25 = 92%**, run `run-2@20261127-224446`, model `gpt-6-luna`. [Báo cáo eval](../eval/report.md) và [eval/README.md](../eval/README.md) trên main `dfdbd0b` xác nhận Nguyễn Thị Hải Yến đã rà thủ công và đồng ý toàn bộ ngày 28/11/2026; PR #25 được merge. Nguyễn Khánh Vinh chấm mù 5 output lượt 2, khớp 5/5. `python run.py score eval/run-2.csv` kiểm lại đạt 23/25.

Dùng tỷ lệ đã xác nhận **0,92** để quy đổi chi phí theo quy ước khung, trỏ rõ `--rate-from eval/run-2.csv`. Metric bổ sung `rui_ro_duoc_dan_chung` vẫn 25/32 (78,1%), dưới ngưỡng riêng 90%; không tuyên bố mọi metric đều đạt. Mô phỏng và eval cùng mã model ghi nhận; chưa có bằng chứng đồng nhất endpoint/snapshot phía dịch vụ trung gian, nên rate không phải phép đo chất lượng mới của 80 lượt catalog.

## 2. Kết quả mô phỏng

Lệnh đã chạy:

```powershell
python cost/check_personas.py
python run.py score eval/run-2.csv
python run.py simulate --rate-from eval/run-2.csv
```

- Run ID: **`simulate-1@20261128-110814`**; seed **42**, 50 phiên, 80 lượt phân tích thật.
- File gốc: [CSV](simulate-1.csv), [summary](simulate-1-summary.md), [trace](../traces/simulate-1.jsonl). Không chỉnh sửa file do khung sinh.
- Tổng toàn lượt: **80 model calls**, **240 tool calls**, **153.124 token vào / 41.166 token ra**; 320 trace event khớp CSV và run ID.
- **49/50 phiên không lỗi** (98% về kỹ thuật, không phải accuracy); **1/50 phiên lỗi** là S024 (`dung_nhieu`, input SP04 → SP03 → SP04), ghi HTTP 502 và HTTP 503. Có 78 lần gọi model nhận usage, 2 lần báo lỗi; không suy rằng toàn bộ 80 lượt đều thành công.
- Khung loại toàn bộ S024 khỏi trung bình: bảng dưới dùng **49 phiên / 77 lượt**, **151.257 token vào / 40.816 token ra**. Không gọi đây là 50 phiên thành công.
- Cơ cấu lấy mẫu: 25 dung_it, 20 dung_vua, 5 dung_nhieu; sau loại lỗi còn 25/20/4. Tổng latency ghi nhận 2.084,89 giây; trung bình toàn lượt khoảng 41,7 giây/phiên, không phải số phút tiết kiệm đã đo.

Bảng persona và bảng chi phí dưới được chép nguyên từ summary:

<!-- BEGIN SIMULATION SUMMARY TABLES -->

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 25 | 1 | 1990 | 538 | 1.0 | 3.0 |
| dung_vua | 20 | 2 | 3903 | 1026 | 2.0 | 6.0 |
| dung_nhieu | 4 | 3 | 5859 | 1710 | 3.0 | 9.0 |

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (500 người) | Chi phí / tháng — cơ sở (2.000 người) | Chi phí / tháng — cao (5.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-6-luna (vào 0.1 · ra 0.5 $/1M) | $0.00073 (≈ 19 ₫) | $0.00079 (≈ 21 ₫) | $0.00050 (≈ 13 ₫) | $1.95 (≈ 50.684 ₫) | $7.79 (≈ 202.738 ₫) | $19.47 (≈ 506.844 ₫) | $0.0039 (≈ 101 ₫) |
| gpt-6.2-sol (vào 2.0 · ra 10.0 $/1M) | $0.0145 (≈ 378 ₫) | $0.0158 (≈ 410 ₫) | $0.0100 (≈ 261 ₫) | $38.94 (≈ 1.013.688 ₫) | $155.77 (≈ 4.054.753 ₫) | $389.43 (≈ 10.136.884 ₫) | $0.0779 (≈ 2.027 ₫) |

<!-- END SIMULATION SUMMARY TABLES -->

### Ảnh hưởng của phiên lỗi

S024 vẫn có usage **1.867 token vào / 350 token ra** từ 1 lượt thành công; hai lượt kia báo HTTP 502/503. Theo cùng giá gpt-6-luna tham chiếu, phần usage của S024 tương ứng **0,0003617 USD**; bảng khung loại khoản này cùng toàn bộ phiên lỗi.

Tổng token đã ghi usage của cả 50 phiên tương ứng **0,0358954 USD (khoảng 934 VND)** theo giá tham chiếu. Nếu phân bổ cả khoản usage lỗi này cho 49 phiên hoàn tất, chi phí là khoảng **0,00073256 USD/phiên hoàn tất**; tiếp tục chia 0,92 cho chỉ số quy đổi sẽ thành **0,00079626 USD/task**, thay vì 0,00078824 USD/task trong bảng khung. Đây là phân tích bổ sung, không sửa summary. Chưa biết dịch vụ có thu phí các request không trả usage hay không; chưa dự báo chi phí retry/tháng.

HTTP 502/503 được ghi nhận từ dịch vụ trong lượt này; không thay đổi agent, framework hoặc tự thêm retry để làm đẹp kết quả. Cần theo dõi khi chạy thật; nếu nhóm yêu cầu 50/50 không lỗi, phải chạy lượt mới và giữ nguyên lượt này.

### Lịch sử chuẩn bị

Bằng chứng CP3 đã được review PR #23 ghi nhận tại `docs/issue-8-checklist.md`: run `simulate-try@20261128-091210`, 10 phiên, 15 model calls, 0 lỗi; token vào 28.927, ra 8.636. File thử không nộp theo `.gitignore`, đã gỡ khỏi Git ở PR #23; lịch sử 10 phiên không thay thế ≥50 phiên. Tỷ lệ 92% lúc chạy thử chưa được chốt, nay đã có xác nhận PR #25.

Lượt thử tự động tiếp theo bị sandbox chặn socket (`WinError 10013`), sinh `simulate-error.csv`, không có token. Lượt chạy lại có quyền mạng đã dừng theo yêu cầu Trang sau 2 phiên hoàn tất, chưa tạo bộ kết quả ≥50 phiên. Không sửa/xóa kết quả lỗi hoặc dùng lượt dở làm bằng chứng đạt.

### Công thức và giới hạn

- Chi phí một phiên: `(tokens_in × giá_input + tokens_out × giá_output) / 1.000.000` USD.
- Chi phí/phiên: trung bình trên phiên không lỗi theo khung.
- Chi phí/task thành công: chi phí/phiên chia tỷ lệ đạt eval, theo quy ước bài lab. Eval chấm từng câu, không trực tiếp đo xác suất cả phiên nhiều lượt thành công.
- Chi phí/câu hỏi đạt: chi phí/phiên chia lượt trung bình/phiên, rồi chia tỷ lệ đạt.
- Chi phí/tháng: `người dùng × tổng(share × uses_per_month × chi phí trung bình/phiên từng persona)`; không nhân máy móc trung bình mẫu với 3,9 nếu mẫu lệch.
- Chi phí/người/tháng: tháng base chia 2.000; đổi VND bằng tỷ giá snapshot.

Kế hoạch lấy mẫu theo seed có thể lệch tỷ lệ dân số; không sửa kết quả để ép khớp. Lượt này có dữ liệu của cả 3 persona, không phải dùng trung bình chung thay thế persona thiếu mẫu, nhưng nhóm dùng nhiều chỉ còn 4 phiên không lỗi nên dự báo còn nhạy với mẫu. Pool SP01–SP06 không đại diện mọi input dán hay bộ đo chất lượng độc lập.

## 3. So với impact

- `spec.md` §2 dự toán **19,5 phút tiết kiệm/người/tháng**, **39.000 phút (650 giờ)/tháng** với base 2.000 người; đều **tự ước tính**, chưa đo validation.
- Giá gpt-6-luna tham chiếu: **khoảng 101 VND/người/tháng**, **202.738 VND/tháng** ở base; low **50.684 VND**, high **506.844 VND**. Với mức giá gpt-6.2-sol áp lên cùng token: khoảng **2.027 VND/người/tháng**, base **4.054.753 VND/tháng**; chưa đo chất lượng model này.
- **Kết luận:** đáng tiếp tục pilot với mức giá thấp trong các giả định đã ghi: chi phí token khoảng 101 VND/người/tháng so với 19,5 phút tiết kiệm tự ước tính. Chưa kết luận ROI thực tế vì chưa đo thời gian tiết kiệm, chưa có biểu phí ShopAIKey và chi phí vận hành; còn 1 phiên lỗi và metric bổ sung về bằng chứng chưa đạt. Chưa quy phút sang tiền khi chưa có nguồn giá trị thời gian. Không chọn model đắt hơn chỉ dựa vào bảng áp giá.

## 4. Độ nhạy và tối ưu

Các quan hệ dưới đây là giả định tính toán, **chưa phải kết quả thử tối ưu**; không đổi chuẩn đạt để giảm chi phí.

| Yếu tố | Quan hệ có thể chốt ngay | Cần đo thêm |
|---|---|---|
| Mức giá | Snapshot gpt-6.2-sol có cả giá input/output gấp 20 lần gpt-6-luna; cùng token/rate thì chi phí gấp 20 | Chất lượng, tokenizer, latency model thứ hai |
| Quy mô | Cùng persona/tần suất: low = 0,25 × base; high = 2,5 × base | Người dùng pilot thật |
| Tần suất | Tăng đồng đều phiên/người 2 lần → chi phí tháng 2 lần | Tần suất dùng hệ thống |
| Tỷ lệ đạt | Giữ chi phí/phiên C: rate 80% → C/0,80; 92% → C/0,92; 100% → C; chỉ là kịch bản độ nhạy | Baseline đã xác nhận 92%; không coi 100% là số đo |
| Giảm token | Trên 49 phiên không lỗi, chi phí input/output chiếm khoảng 42,57%/57,43%. Giảm 25% input giả định tiết kiệm khoảng 10,64% tổng chi phí; giảm 25% output khoảng 14,36% | Đây là phép tính độ nhạy, chưa thử rút prompt/output và chấm lại chất lượng |
| Cache/giới hạn bước | Chỉ tiết kiệm nếu tránh được lượt/token tính phí hoặc có giá cache được xác nhận | Cache hit rate/giá dịch vụ; không bỏ bằng chứng để tiết kiệm |

Luồng hiện lọc review trước model, dừng khi không còn review sạch; chưa gán phần trăm tiết kiệm nếu chưa có đối chứng. Có thể cân nhắc tránh chạy lại input giống nhau hoặc tối ưu prompt ở lượt sau, kèm kiểm lại chất lượng.

Chưa tính crawler, hosting, lưu trữ, thuế/phí thanh toán/phí trung gian, giờ công người duyệt/hỗ trợ; chưa có nguồn để cộng số cho các khoản này.

## 5. Đối chiếu hoàn thành

- Đã dùng điểm Issue #10 được Yến xác nhận trong PR #25: 23/25, đúng run-2 và mã model.
- Đã chạy đủ 50 phiên thật, giữ nguyên CSV/summary/trace; báo rõ 49 phiên không lỗi và 1 lỗi dịch vụ. DoD ghi ≥50 phiên thật, không khẳng định 50/50 thành công.
- Bảng chép từ summary; tính độc lập từ CSV khớp chi phí/phiên, task, câu hỏi, 3 quy mô tháng và người/tháng trước khi làm tròn.
- Đồng bộ số liệu/kết luận vào `spec.md` §8 và changelog §10; giữ nguyên chuẩn và kết quả eval trên main.
- Kiểm sau đồng bộ: 27 test UI/endpoint + 19 test backend đạt; `run.py check` và `cost/check_personas.py` đạt. Trang xác nhận đã rà soát lại số liệu Issue #11 ngày 28/11/2026. Bàn giao trên nhánh `feat/issue-11-cost-analysis` để Trang tạo PR; chưa tự đóng Issue #11.
