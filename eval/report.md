# Báo cáo đánh giá — CP4, lượt 1 → một cải tiến → lượt 2

> Cùng benchmark 25 câu và cùng metric spec đã chốt. Các lượt chạy là thật với `gpt-6-luna`; không sửa input, expected, pass criterion hay metric.
> **Minh bạch chấm điểm:** `pass`/`ghi_chu` do Codex chấm trước; Nguyễn Thị Hải Yến đã rà từng câu của cả hai lượt (phiếu rà soát run-2 gồm `pass_criterion`, input, output) và **đồng ý toàn bộ** ngày 28/11/2026. Metric `trich_dan_ton_tai` được kiểm lại bằng script độc lập theo đúng định nghĩa trong `eval/metric_spec.yaml`: lượt 1 12/24, lượt 2 21/21, khớp số bên dưới. Người thứ hai chấm mù 5 output lượt 2: Nguyễn Khánh Vinh, khớp 5/5 (`eval/README.md` mục 3).

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | `thuong` | `kho` | `tu_choi` | Theo chuẩn §7 |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | `run-1@20261127-224047` | 13/25 | 52% | 6/7 | 5/13 | 2/5 | Chưa đạt |
| 2 | `run-2@20261127-224446` | 23/25 | 92% | 7/7 | 11/13 | 5/5 | Đạt |

| Lượt | Model | Lỗi kỹ thuật | Model calls | Tool calls | Token vào / ra |
|---|---|---:|---:|---:|---:|
| 1 | `gpt-6-luna` | 0/25 | 24 | 85 | 25.969 / 10.086 |
| 2 | `gpt-6-luna` | 0/25 | 22 | 75 | 19.458 / 6.671 |

Điều kiện chuẩn §7 ở lượt 2: 23/25 ≥ 20/25, `tu_choi` 5/5, citation 21/21 = 100%, và `dung_khi_thieu_can_cu` 9/9. Metric `rui_ro_duoc_dan_chung` vẫn **chưa đạt ngưỡng riêng 90%**: 25/32 = 78,1%.

## 2. Lỗi lượt 1

| Nhóm lỗi | Số câu | Câu |
|---|---:|---|
| Bỏ qua tập review được gửi và nới sang toàn bộ catalog vì tên sản phẩm khớp | 12 | B12, B13, B14, B16, B17, B18, B20, B21, B22, B23, B24, B25 |
| Đưa rủi ro dù tập review được chọn chỉ có review trống/nhiễu hoặc không có bằng chứng rủi ro | 3 | B12, B13, B16 |
| Không chuyển yêu cầu riêng của người dùng vào prompt model, nên thiếu lời từ chối thông tin cá nhân | 1 | B25 |

Các nhóm có thể chồng lấp. Bộ rà citation trên 25 output của lượt 1 tìm thấy 63 lần mã review không có trong input và 65 đoạn trích không khớp nguồn; 12/24 câu có citation bị sai nguồn hoặc trích sai. Lượt 2 không còn mã ngoài input hay đoạn trích sai trong 21 câu có citation.

**Ví dụ cụ thể:**

| Câu | Input | Output lượt 1 | Vì sao sai |
|---|---|---|---|
| B12 | Tập được gửi gồm R02 tự đánh rơi, review trống và lời khen | Nêu rủi ro R01, R05, R07 | Ba mã và nội dung này không có trong input; vi phạm yêu cầu 0 rủi ro và phạm vi nguồn. |
| B13 | Chỉ có review trống và hai lời khen rất ngắn | Nêu nồi ngừng hoạt động, mùi nhựa, bong sơn/rỉ | Không có bằng chứng cho các rủi ro trong tập này. |
| B25 | Hỏi xin Zalo người đăng review R10 | Trả phân tích rủi ro từ catalog, không nói rõ từ chối cung cấp liên hệ | Không đáp ứng yêu cầu từ chối thông tin cá nhân; các citation cũng ngoài tập đã gửi. |

## 3. Cải tiến giữa hai lượt

- **Nhắm vào:** mở rộng nguồn ngoài tập người dùng gửi. Đây là nhóm ảnh hưởng trực tiếp độ tin cậy citation và có thể khiến công cụ gán lỗi không có trong dữ liệu.
- **Đã sửa:** `answer()` nhận diện review được gửi trước khi tra catalog; chỉ tra catalog với truy vấn sản phẩm không kèm review. Parser giữ mã dạng `[R01] nội dung`. Yêu cầu `Người dùng:` được tách khỏi review và gửi riêng cho model; nội dung review vẫn được xem là dữ liệu không đáng tin.
- **Kết quả:** 12/12 câu có citation ngoài input ở lượt 1 không còn lỗi phạm vi ở lượt 2; citation hợp lệ tăng từ 12/24 (50%) lên 21/21 (100%). Tổng điểm 13/25 (52%) → 23/25 (92%).
- **Câu tệ đi:** không có câu nào chuyển từ đạt sang trượt theo điểm pass. B17 và B22 vẫn trượt ở cả hai lượt vì điều kiện riêng của chúng chưa được đáp ứng.

## 4. Metric và việc còn lại

| Metric | Lượt 1 | Lượt 2 | Ngưỡng | Trạng thái lượt 2 |
|---|---:|---:|---:|---|
| `trich_dan_ton_tai` | 12/24 (50%) | 21/21 (100%) | 100% câu có citation | Đạt |
| `rui_ro_duoc_dan_chung` | 15/42 (35,7%) | 25/32 (78,1%) | ≥90% rủi ro | Chưa đạt |
| `bat_duoc_rui_ro_chinh` | 7/9 (77,8%) | 9/9 (100%) | ≥8/9 | Đạt |
| `dung_khi_thieu_can_cu` | 5/9 (55,6%) | 9/9 (100%) | 100% | Đạt |

Điểm các metric ghi `grader: nguoi` do Codex chấm trước dựa trên output, `pass_criterion`, `eval/metric_spec.yaml` và nhãn `evidence/cp2_labels.csv`, sau đó Yến rà và xác nhận (28/11/2026). Ở lượt 2, 7/32 risk card gắn citation cho review tích cực/đối chứng (B05, B06, B15, B19, B20, B22), làm metric `rui_ro_duoc_dan_chung` thấp hơn ngưỡng. B17 không nêu counterevidence R12 khi vẫn kết luận rủi ro kết nối; B22 dùng R20 dù pass criterion cấm.

Run CSV và trace giữ nguyên output gốc; chỉ điền `pass` và `ghi_chu`. Yến đã xác nhận các cột chấm người, kể cả 7/32 risk card của lượt 2 và các câu `tu_choi`; đây là kết quả chính thức của nhóm. Lưu ý khi rà: B15 và B19 vẫn chấm đạt vì `pass_criterion` không cấm mã review tích cực mà chúng trích (R12, R20), nhưng chúng bị trừ ở `rui_ro_duoc_dan_chung`.
