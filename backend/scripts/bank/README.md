# scripts/bank — công cụ soạn ngân hàng đề tay

Dùng khi soạn đề bằng tay cho một khóa (vd khóa 494 IoT). Chạy từ thư mục `backend/`.
Kết quả chạy (sao lưu, kết quả đo Gemini, ảnh chụp điểm, file duyệt) ghi vào `data/bank_runs/` — **đã .gitignore**,
vì có thể chứa bài làm của học viên. Key Gemini chỉ đọc từ `.env` / biến môi trường như server.

## Quy trình một đợt đề

| Bước | Lệnh | Ghi chú |
|---|---|---|
| 1. Soạn nguồn | `courses/course_<id>/` | `chunks.py`, `mcq.py`, `essays.py` (barem + bài thử), `vn_notes.py`, `__init__.py` |
| 2. Dựng JSON | `python -m scripts.bank.build <id>` | → `data/review/course_<id>_en.json` |
| 3. Kiểm (không gọi AI) | `python -m scripts.bank.check <id>` | phải ra **0 vấn đề** |
| 4. Đo Gemini | `python -m scripts.bank.probe_gemini <id> --max-calls 40` | ghi model + phiên bản prompt vào kết quả |
| 5. File duyệt | `python -m scripts.bank.render_review <id> [--essays-only] --out ~/Downloads/de.md` | gửi người duyệt |
| 6. Nạp DB | `python -m app.core.seed_data.seed_review --file data/review/course_<id>_en.json [--apply-changes]` | rồi `python -m app.core.seed_data.build_embeddings` |
| 7. Thử trên server | tài khoản thử | xong thì xóa lượt thử (dưới) |

Sửa bộ chấm từ khóa (`text_pipeline`, `keyword_grader_en`)? Chụp điểm trước và sau rồi so:
`python -m scripts.bank.regrade_compare snapshot` (trước), sửa code, `snapshot` (sau),
`python -m scripts.bank.regrade_compare compare <trước> <sau>`. **Không được có bài GIẢM điểm.**

## Quy tắc barem tự luận (Tuấn chốt 26/11)

- Từ khóa chính = **phần giải thích / cách xử lý**, không phải tên khái niệm. Chỉ liệt kê tên thì 0 điểm.
- Tên khái niệm làm **chủ thể** (`sub_keywords`) khi cần gắn tính chất vào đúng đối tượng (QoS 0/1, lớp, CON/NON…).
- Thêm từ đồng nghĩa phổ biến; từ khóa nhiều chữ không được bị rút còn 1 chữ (check báo).
- Đề **ghi rõ đối tượng**, không cho "chọn tự do" (barem cố định không chấm được "N trong M").
- Không để hai câu **trùng ý** (học viên chép bài câu trước); không hỏi kiến thức ngoài tài liệu của kỹ năng.
- Câu mô tả ý theo **mức tối thiểu**, đúng một trong hai mẫu (khớp quy tắc 8, 12 của prompt chấm):
  - `"<ý> (any one of: a, b, c)."` — nêu một chi tiết là đạt; danh sách **không** dùng chữ "and".
  - `"<chủ thể> (both needed: a; b)."` — phải đủ; **không** viết câu tóm tắt ở đầu (Gemini coi nó là ý chính).
- Từ khóa đứng riêng và từ trong câu có thể ra **dạng gốc khác nhau** (bộ gán từ loại phụ thuộc ngữ cảnh): "two
  readings" đứng riêng → `two read`, trong câu → `two reading`; "finer" → `finer` / `fine`. Bài thử "đúng nhưng viết
  khác" chấm thấp bất thường → so `preprocess(từ khóa)` với `preprocess(câu)` và thêm cả hai dạng.
- Câu đúng ở **dạng phủ định** ("readings do not follow a straight line") làm từ khóa bị coi là phủ định → thêm từ khóa
  tự mang phủ định ("not follow a straight line", "non-linear").
- Ký hiệu đơn vị bị bỏ khi tiền xử lý ("0.1 °C" → `0.1`): ý kết quả là con số thì gắn chủ thể bằng từ ngữ cảnh
  (resolution, temperature…), không chỉ bằng đơn vị.
- Thuật ngữ các sách dùng **ngược nhau** (vd active / passive): đề và barem hỏi khái niệm, không bắt nhãn; có bài thử
  cho cả hai quy ước.
- Mỗi câu tự luận có **bài thử** (`PROBES`): bài đúng viết khác, chỉ liệt kê tên, đảo vai trò, "without"… và
  `GEMINI_PROBES` (bản A một chi tiết, ý "both" chỉ một phần; bản B chi tiết khác, ý "both" đủ).
  Chuẩn đo Gemini: ý "any one of" lệch ≤ 1 điểm với từ khóa; ý "both" bản A → Gemini không đạt.
- Giới hạn đã biết của bộ chấm từ khóa: đảo vai trò trong **cùng một vế câu** vẫn lọt (bài thử ghi `"c"`); ý "both"
  nêu thiếu vẫn được từ khóa cho đạt (→ cờ `ai_stricter` cho giáo viên); câu ngắn gồm toàn từ của đề (vd "I
  recommend CoAP.") bị luật chép đề L7 bỏ dù đúng; "analyses" về "analysis". Giữ bài thử cho từng giới hạn (nhãn `"c"`).

## Xóa lượt thử — `delete_test_attempt`

```
python -m scripts.bank.delete_test_attempt <attempt_id>            # CHẠY THỬ: chỉ in những gì sẽ xóa
python -m scripts.bank.delete_test_attempt <attempt_id> --apply    # sao lưu → xóa (1 transaction) → kiểm còn 0 dòng
```

Rào chắn: chỉ tài khoản thử thỏa **cả hai** điều kiện — user ID có trong `scripts/bank/test_users.local.json`
(file cục bộ, .gitignore; chép từ `test_users.example.json`) **và** email đúng mẫu tài khoản thử (`@example.com` hoặc
bí danh `+hv<số>@`). Sao lưu bắt buộc trước khi xóa (`data/bank_runs/backups/`). Lượt đã làm khóa Hoàn thành → từ chối.
Email kết quả đã gửi thì không rút lại được.

Lưu ý khi thử trên server: luật chống học thuộc (tránh câu của 3 lượt gần nhất) với ngân hàng nhỏ sẽ khiến lượt thứ
2–3 **kích hoạt job sinh đề bổ sung** (Gemini soạn câu `auto_approved`). Dùng bài đánh dấu cho MỌI câu tự luận để một
lượt là đủ; nộp liên tiếp phải cách nhau `REVIEW_SUBMIT_COOLDOWN` (120 s).

## Việc để sau (đã ghi nhận khi soạn đề 494)

- **Chuẩn hóa số trong bộ chấm từ khóa**: "17.0" khác "17", "0,1" (dấu phẩy) bị tách thành hai số; ký hiệu đơn vị như
  "°C" bị bỏ hẳn khi tiền xử lý. Hiện vá bằng cách ghi thêm dạng ("17", "17.0") và gắn chủ thể bằng từ ngữ cảnh. Sửa
  tận gốc trong `text_pipeline` (giống lỗi "-s"), có so điểm cũ / mới.
- **(c)** gán từ khóa cho chủ thể gần nhất (đảo vai trò trong cùng một vế câu).
- **Nhóm loại trừ (7.5b)**: cột `exclusion_group` đã có nhưng bộ ráp đề chưa dùng, và file đề JSON chưa nạp cột này.
  Đến khi làm xong, câu trắc nghiệm lộ đáp án câu tự luận phải **viết lại** (đợt 3 đã viết lại DA-TN-14, DAT-TN-09, 11,
  13). Nên rà lại đợt 1–2 theo cùng tiêu chí.

