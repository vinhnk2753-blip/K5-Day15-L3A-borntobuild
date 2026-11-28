# AGENTS.md — hướng dẫn cho coding agent (Claude Code, Cursor, Codex…) làm việc trong repo này

> Ôn lại: ngày 12 · lab ngày 12. Nhóm sửa file này cho khớp bài của mình (thêm quy ước riêng, bỏ dòng không dùng).

## Repo này là gì

Repo nộp bài hackathon AI20K của nhóm: một bản chạy thử AI cho **một lát cắt** (xem `spec.md` §4), kèm bằng chứng, bộ câu thử và mô phỏng chi phí. Mọi câu trả lời phải chạy được bằng các lệnh dưới đây.

## Quy trình Issue → Pull Request (bắt buộc)

1. Chỉ bắt đầu phần việc đã có GitHub Issue và được assign. Đọc issue, tài liệu liên quan và giới hạn file trước khi sửa; không tự mở rộng sang task khác hoặc sửa phần do thành viên khác phụ trách.
2. Mỗi issue có branch riêng, tạo từ `dev` mới nhất theo mẫu `feat/<số-issue>-<mô-tả-ngắn>`, `fix/<số-issue>-<mô-tả-ngắn>` hoặc `docs/<số-issue>-<mô-tả-ngắn>`. Không dùng chung branch cho nhiều issue và không làm việc trực tiếp trên `main` hoặc `dev`.
3. Chia thay đổi thành các commit nhỏ; mỗi commit là một thay đổi logic hoàn chỉnh và có kiểm thử phù hợp. Trước khi push, chạy các kiểm thử liên quan và xử lý lỗi phát hiện được.
4. Tạo đúng một Pull Request cho branch của issue đó, nhắm vào `dev`; không gộp nhiều issue vào cùng một PR. PR phải nêu phạm vi thay đổi, kết quả kiểm thử và có `Closes #<số-issue>` tương ứng trong phần mô tả.
5. Yêu cầu ít nhất một thành viên khác review. Chỉ merge sau khi đã có review của người khác; người thực hiện không tự merge PR của mình.

### Ranh giới Git và dữ liệu

- Không commit hoặc push trực tiếp lên `main` hay `dev`; không force-push lên hai nhánh này.
- Không sửa file ngoài phạm vi issue được giao, trừ khi issue hoặc người phụ trách yêu cầu rõ.
- Không commit API key, `.env`, dữ liệu khách hàng/cá nhân hoặc dữ liệu nhạy cảm.
- Nếu repo hoặc quyền truy cập không có nhánh `dev`, issue chưa được assign, hay không thể tuân thủ quy trình trên, dừng trước thao tác GitHub có tác động và báo rõ trở ngại; không tự đổi sang `main`.

## Lệnh

```
python run.py                    # chạy bản chạy thử
python run.py check              # kiểm eval/benchmark.csv + eval/metric_spec.yaml
python run.py eval --try         # thử 3 câu đầu
python run.py eval               # chạy cả bộ → eval/run-N.csv + traces/run-N.jsonl
python run.py score eval/run-N.csv
python run.py simulate --try     # thử mô phỏng chi phí 10 phiên
python run.py simulate           # mô phỏng chi phí → cost/simulate-N.csv
```

Khung chỉ dùng thư viện chuẩn của Python. Thêm thư viện thì ghi vào `requirements.txt`.

## Cấu trúc code

| File | Ai sửa | Hợp đồng |
|---|---|---|
| `codebase/agent.py` | nhóm | `answer(text) -> {"output": str}` — luồng chính, đúng hình dạng ở `spec.md` §4 |
| `codebase/ai.py` | nhóm | `call_model(system, user) -> {"text", "model", "tokens_in", "tokens_out"}`, giữ `@model_call`. Token lấy từ `usage` của API, không ước lượng |
| `codebase/tools.py` | nhóm | mỗi công cụ một hàm có `@tool`, docstring: tên · input · output · có tác động ra ngoài không |
| `codebase/tracing.py`, `eval/run_eval.py`, `cost/simulate.py`, `run.py` | **khung — không sửa** | ghi trace, chạy bộ câu thử, mô phỏng chi phí |

## Luật — agent KHÔNG được làm

- Không commit `.env`, API key, dữ liệu cá nhân thật, nguyên file data BTC cấp.
- Không sửa `eval/run-*.csv`, `cost/simulate-*.csv`, `traces/*` đã chạy (trừ điền cột `pass`, `ghi_chu`).
- Không sửa chuẩn "đạt" (`spec.md` §7), `eval/metric_spec.yaml` sau CP2; không xoá câu thử trượt, không sửa `expected` cho khớp output.
- Không bịa người được phỏng vấn, trích dẫn, câu trả lời khảo sát, số liệu. Số không có nguồn thì ghi rõ *(tự ước tính)*.
- Công cụ có tác động ra ngoài (gửi tin, sửa dữ liệu, chấm điểm): chỉ tạo bản nháp chờ người duyệt.
- Không viết prompt "giấu" câu thử vào code (vd so khớp nguyên văn input của bộ câu thử).

## Quy ước của nhóm

- Ngôn ngữ trả lời người dùng: __
- Phong cách code / đặt tên: __
- Ai duyệt thay đổi do agent tạo trước khi commit: __
