# Ngân hàng câu hỏi ôn tập — quy ước soạn (module 09 · Tuấn · 10/11/2026)

Mỗi khóa một file `course_<course_id>.json`. Nạp vào DB: `python -m scripts.seed_review --file data/review/course_<id>.json`
(trong thư mục `backend`). Script **kiểm tra trước, ghi sau** — sai ở đâu in hết lỗi, không ghi gì.

## Quy ước ngôn ngữ (chốt 10/11)

| Phần | Ngôn ngữ | Ví dụ |
|---|---|---|
| **Tên trường** (key JSON) | Tiếng Anh, `snake_case` — giữ như hiện tại | `code`, `skill`, `chunk`, `type`, `level`, `content`, `options`, `correct_index`, `rubric`, `text`, `max_points`, `main_keywords`, `sub_keywords`, `explanation`, `title` |
| **Giá trị liệt kê** | Tiếng Anh | `type`: `mcq` · `essay` — `level`: `recognize` · `understand` · `easy` · `advanced` |
| **Mã** (`code`, mã kỹ năng) | Giữ như hiện tại | `312-PY-TN-01`, `312-ITER-K03`, kỹ năng `PY`, `CS`, `ITER`, `VAR`, `COND` |
| **Nội dung** | **Tiếng Việt** | đề (`content`), phương án (`options`), barem (`rubric[].text`), giải thích / đáp án mẫu (`explanation`), đoạn tri thức (`title`, `content`) |
| Từ khóa chấm (`main_keywords`, `sub_keywords`) | Tiếng Việt **có dấu** + thuật ngữ gốc tiếng Anh nếu người học hay dùng | `["thay đổi", "sửa", "mutable", "append"]` |
| Code trong đề | Python, giữ nguyên | `for i in range(1, n + 1):` |

Lý do: tên trường / mã là thứ **code đọc** (khớp model, API, test) → tiếng Anh ổn định; nội dung là thứ **người học đọc** → tiếng Việt.

## Mã (`code`)

```
<course_id>-<SKILL>-<LOẠI>-<STT>
  LOẠI:  K   = đoạn tri thức (knowledge)   vd 312-ITER-K01
         TN  = câu trắc nghiệm              vd 312-ITER-TN-01
         TL  = câu tự luận                  vd 312-ITER-TL-01
  STT:   2 chữ số, tăng dần trong cùng kỹ năng + loại
```

- Mã là **khóa** để seed cập nhật đúng câu → **không đổi mã** của câu đã nạp.
- Câu sai đáp án / sai ý: **tắt câu cũ** (`is_active = false` trong DB) và **thêm câu mới với mã mới** — không sửa đè, để lịch sử bài làm cũ vẫn đúng.
- Sai chính tả / câu chữ chưa rõ (không đổi ý): sửa thẳng trong file rồi seed lại.

## Từ khóa chấm tự luận được dùng thế nào (bản mock — `app/ai/review/keyword_grader.py`)

Mỗi ý barem có `main_keywords` (**nội dung** của ý) và `sub_keywords` (**chủ thể** của ý, có thể để rỗng):

| Kết quả ý | Điều kiện | Điểm ý |
|---|---|---|
| **Đạt** (`full`) | Một câu trong bài làm có từ khóa chính **và** từ khóa phụ (`sub_keywords` rỗng → chỉ cần từ khóa chính) | đủ `max_points` |
| **Một phần** (`partial`) | Có từ khóa chính nhưng câu đó **không có** chủ thể | ½ `max_points` |
| **Chưa có** (`none`) | Không có từ khóa chính — **chỉ nhắc chủ thể cũng = 0** (chốt 10/11) | 0 |

So khớp (chốt 10/11):
- Không phân biệt hoa thường, chuẩn Unicode (gõ NFC hay NFD như nhau), bỏ khoảng trắng quanh ký hiệu (`tong = 0` ≡ `tong=0`, `n + 1` ≡ `n+1`).
- Câu bài làm **có dấu** → so **có dấu** ("dùng" ≠ "dừng" ≠ "đúng"); câu gõ **hoàn toàn không dấu** → so bản bỏ dấu ("dieu kien" khớp "điều kiện"). Vì vậy **viết từ khóa có dấu đầy đủ**.
- Từ khóa chữ khớp **nguyên từ** ("if" không khớp trong "elif"); từ khóa có ký hiệu ở đầu / cuối (`+=`, `int(`) khớp chuỗi con ở phía đó.

Chống lách (tự động, người soạn không cần làm gì — nhưng cần biết):
- Câu **chép lại đề** (≥ 70% cụm 3 từ có trong đề) bị bỏ qua → đừng dựa vào từ có sẵn trong đề làm từ khóa duy nhất của một ý.
- Câu **liệt kê từ khóa** (> 75% số từ là từ khóa và chạm ≥ 2 ý) không được "Đạt".
- **Cả bài** có > 85% số từ là từ khóa (không tính câu chép đề) → mọi ý tối đa "Một phần" (bắt kiểu chia chuỗi từ khóa thành nhiều câu ngắn).
- Bài < 6 từ (không tính câu chép đề), hoặc câu khớp < 3 từ → tối đa "Một phần".

**Hạn chế đã biết (chốt 11/11, chấp nhận ở bản mock):** viết mỗi ý thành một câu cực ngắn kèm chữ đệm (vd *"cả hai and là. ít nhất một or là."*) vẫn có thể được trọn điểm — bộ chấm chỉ dò từ khóa, không hiểu nghĩa. Không thêm luật chặn; AI thật (bước 5.1) chấm theo nghĩa. Người soạn không cần làm gì thêm.

## Checklist khi soạn một câu

**Trắc nghiệm**
- [ ] Đúng 4 phương án, khác nhau, **độ dài tương đương** — không để đáp án đúng dài hẳn hoặc chứa sẵn lời giải thích.
- [ ] Phương án sai là lỗi hay gặp (hợp lý), không đùa.
- [ ] Giải thích ở `explanation`, không nằm trong phương án.
- [ ] Vị trí đáp án đúng (`correct_index`) rải đều A/B/C/D (khi làm bài vẫn được xáo, nhưng file gọn hơn).

**Tự luận**
- [ ] Đề hỏi gì thì barem **chấm đủ** cái đó (đề hỏi "cho ví dụ" thì phải có ý chấm ví dụ — hoặc bỏ yêu cầu khỏi đề).
- [ ] Không bắt buộc một đáp án cụ thể khi đề cho phép nhiều cách đúng (vd "kể 3 kiểu dữ liệu" mà barem chỉ nhận int / float / str).
- [ ] `easy` 2–3 ý, `advanced` 4–5 ý, **tổng `max_points` = 10**.
- [ ] Từ khóa chính **đủ đặc trưng** — tránh từ quá chung (`"không"`, `"có"`, `"là"`) vì câu bất kỳ cũng chứa.
- [ ] Liệt kê các **cách viết khác** của cùng một ý (vd `tong += i` / `tong = tong + i` / "cộng dồn").
- [ ] `explanation` = đáp án mẫu; đáp án mẫu phải chấm được **10/10** (test `test_every_bank_essay_scores_10_with_its_model_answer` kiểm tự động).

**Đoạn tri thức**
- [ ] Đúng kiến thức, không mâu thuẫn với đoạn khác.
- [ ] Mỗi câu hỏi gắn `chunk` thuộc **cùng kỹ năng**.
