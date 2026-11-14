# B4: Thu bài và chấm bộ bài chuẩn (gold set)

> Module 09 · Tuấn · 14/11/2026 · thuộc kế hoạch [Review-AI-Grading.md](../Review-AI-Grading.md) mục B4
> Hướng dẫn cho người chấm (tiếng Anh): [RATER_GUIDELINE.md](RATER_GUIDELINE.md) · Script: `backend/scripts/gold_sheets.py`

## 1. Chọn câu và chia dev / test (đã chốt, file `backend/data/ai-grading/split.json`)

10 câu tự luận lấy từ `course_312_en.json`. Mỗi kỹ năng có 1 câu dev và 1 câu test, mức easy và advanced xen kẽ. Chia **theo câu hỏi** để không rò rỉ: prompt chỉ được chỉnh trên câu dev, câu test chạy **một lần** cho bản cuối.

| Kỹ năng | Dev (chỉnh prompt) | Test (chạy 1 lần) |
|---|---|---|
| PY | PY-TL-03 · easy · 3 ý | PY-TL-02 · advanced · 5 ý |
| CS | CS-TL-05 · advanced · 4 ý | CS-TL-03 · easy · 3 ý |
| ITER | ITER-TL-01 · easy · 2 ý | ITER-TL-05 · advanced · 4 ý |
| VAR | VAR-TL-02 · advanced · 4 ý | VAR-TL-05 · easy · 2 ý |
| COND | COND-TL-03 · easy · 3 ý | COND-TL-06 · advanced · 4 ý |

Mỗi người chỉ làm 5 câu (khoảng 15–20 phút), nên chia thành 2 Form:
- **Form A**, câu easy: PY-TL-03, CS-TL-03, ITER-TL-01, VAR-TL-05, COND-TL-03.
- **Form B**, câu advanced: PY-TL-02, CS-TL-05, ITER-TL-05, VAR-TL-02, COND-TL-06.

## 2. Mục tiêu số lượng (tiêu chí xong B4)

| Nguồn (`source`) | Mã | Bao nhiêu | Ghi chú |
|---|---|---|---|
| Bài thật từ Form (`real`) | R0001… | **≥ 40**, nên ≥ 60 (≥ 6 người mỗi Form) | Người học / bạn cùng lớp. Hòa và Tâm **không làm** Form vì hai bạn là người chấm. |
| Nhóm tự viết (`team`) | T001… | Bù cho đủ khoảng 12 bài mỗi câu | Viết cố ý để có đủ các loại bài, xem mục 4. |
| AI sinh (`ai`) | A001… | ≤ 30% tổng số, **chỉ ở câu dev** | Script tự chặn bài AI nằm trong test. |

Tổng ≥ 120 bài, tức khoảng 400 ý. Mỗi người chấm mất khoảng 3–4 giờ.

## 3. Tạo Google Form (Tuấn làm)

**Cài đặt:** không thu email, không bắt đăng nhập, không hỏi tên. Mỗi câu là một câu hỏi kiểu *Paragraph*, không bắt buộc trả lời. Tắt "Cho phép sửa sau khi gửi".

**Tiêu đề mỗi câu bắt buộc bắt đầu bằng mã trong ngoặc vuông**, ví dụ `[ITER-TL-01] Explain the difference ...`. Lệnh `collect` dựa vào mã này để nhận ra câu, thiếu mã thì câu bị bỏ qua. Nội dung câu chép đúng từ danh sách bên dưới. Code trong đề giữ nguyên xuống dòng.

**Mô tả đầu Form (dán nguyên văn):**

> This short quiz helps us test an automatic grader for the EduMentor AI student project. Answer in your own words,
> in English, as you would in a real test — short answers are fine, and wrong answers are useful too. Please do not
> look things up or use AI tools. We do not collect your name or email. Your answers are used only to measure the
> grader's accuracy in our course project and are not published.

**Câu đầu tiên, bắt buộc, kiểu Multiple choice.** Tiêu đề phải có chữ "consent", vì script dùng chữ này để nhận ra câu đồng ý:

> **Consent**: I agree that my anonymous answers may be used to evaluate the grader in this course project.
> ○ Yes, I agree  ○ No

Người chọn *No* sẽ bị script tự loại.

**Form A**
```
[PY-TL-03] Explain what the print() and input() functions do in Python.
[CS-TL-03] How is a syntax error different from a logic error? Give an example of each.
[ITER-TL-01] Explain the difference between the break statement and the continue statement in a loop.
[VAR-TL-05] What is None in Python? How is it different from a variable that has never been assigned a value?
[COND-TL-03] Explain the meaning of the three logical operators and, or, not.
```

**Form B**
```
[PY-TL-02] Compare lists and tuples in Python, and give an example of when you should use a tuple.
[CS-TL-05] This program should compute the average of two numbers, but it prints a wrong result:
    a = 4
    b = 6
    avg = a + b / 2
    print(avg)
  What type of error is this, why is it wrong, how do you fix it, and name one way to debug it.
[ITER-TL-05] Write (or describe) a program that asks the user to enter a password until they enter 'abc123', and then prints 'Login successful'. Explain why you use while instead of for.
[VAR-TL-02] State the rules for naming variables in Python, give one valid name and one invalid name, and explain what "dynamic typing" means.
[COND-TL-06] A person gets a ticket discount if they are under 12 or aged 60 or over. Write the matching if condition, explain why you use or and not and, and say what happens when age = 30.
```

Khi xuất kết quả: trên Google Sheets của Form chọn *File → Download → CSV*, lưu thành `backend/data/ai-grading/private/form_a.csv` và `form_b.csv`. Thư mục `private/` đã nằm trong `.gitignore`, không commit.

## 4. Bài nhóm tự viết: cần đủ các loại

Bài thật thường lệch về một phía (nhiều bài đúng hoặc nhiều bài bỏ trống). Nhóm viết bù để mỗi câu có đủ các loại dưới đây. Đây cũng là những chỗ bộ chấm từ khóa dễ sai, nên phải có trong bộ bài để đo được.

| Loại bài | Ví dụ (PY-TL-02) | Mục đích |
|---|---|---|
| Đúng, diễn đạt khác barem | "Tuples are fixed once made; lists you can edit." | AI có hiểu nghĩa không |
| Một phần (thiếu ý / thiếu chủ thể) | "One of them can't be changed." | Nhãn partial |
| Đảo chủ thể | "Lists are immutable, tuples are mutable." | Phải là none |
| Phủ định | "A tuple is not something you can't change." | Bẫy phủ định |
| Liệt kê từ khóa | "mutable immutable [] () coordinates" | Chống lách |
| Chép đề | "Compare lists and tuples in Python..." | Phải là 0 |
| Đúng nhưng ngắn / sai chính tả | "list chang, tupel no" | Không phạt chính tả |
| Bằng code | `a = [1]; a.append(2)  # ok` / `t = (1,); t[0] = 2  # TypeError` | Code được tính |
| Lạc đề / trống | "I don't know." | none |

Thêm tay vào `answers.csv` (mở bằng Google Sheets), mỗi bài một dòng: `answer_id` (T001…), `question_code`, `split` (lấy theo bảng mục 1), `source` = `team`, `answer_text`.

## 5. Chạy script (trong thư mục `backend`)

```powershell
# 1. Gom bài thật từ 2 Form
python -m scripts.gold_sheets collect --form data/ai-grading/private/form_a.csv --form data/ai-grading/private/form_b.csv --out data/ai-grading/private/answers.csv
# (thêm bài team / ai vào answers.csv)

# 2. Vòng hiệu chỉnh: tạo calibration_answers.csv gồm 20 bài KHÔNG nằm trong answers.csv (cùng định dạng), rồi:
python -m scripts.gold_sheets sheets --answers data/ai-grading/private/calibration_answers.csv --out-dir data/ai-grading/private --rater hoa_calibration --rater tam_calibration

# 3. Phiếu chấm chính, gửi riêng cho từng bạn kèm RATER_GUIDELINE.md
python -m scripts.gold_sheets sheets --answers data/ai-grading/private/answers.csv --out-dir data/ai-grading/private --rater hoa --rater tam

# 4. Nhận lại 2 phiếu (lưu đè rater_hoa.csv, rater_tam.csv) rồi gộp
python -m scripts.gold_sheets merge --answers data/ai-grading/private/answers.csv --sheet data/ai-grading/private/rater_hoa.csv --sheet data/ai-grading/private/rater_tam.csv --out data/ai-grading/private/gold.csv

# 5. Điền cột final trong disagreements.csv (Tuấn hoặc thầy quyết) rồi chạy lại bước 4 kèm:
#    --adjudicated data/ai-grading/private/disagreements.csv
```

Lệnh `merge` in ra 3 con số: tỉ lệ ý hai người trùng nhãn, **kappa theo nhãn ý** và **QWK theo tổng điểm bài**. Ghi các số này vào báo cáo, vì chúng là "trần" của độ chính xác AI: AI khó đồng thuận với người hơn mức hai người đồng thuận với nhau. Kappa dưới 0,6 nghĩa là barem hoặc hướng dẫn còn mơ hồ, cần xem lại các ý lệch nhiều nhất.

Script kiểm tra trước rồi mới ghi: nếu thiếu nhãn, nhãn sai chữ, trùng mã, sai split hoặc có bài AI trong test, nó in hết lỗi ra và không ghi gì.

## 6. Lịch (khớp kế hoạch B4: 15–17/11)

| Ngày | Việc | Ai |
|---|---|---|
| 14/11 | Báo Hòa, Tâm (khoảng 3–4 giờ mỗi bạn, chấm 16–17/11); tạo 2 Form; gửi link Form | Tuấn |
| 14–15/11 | Thu bài thật; nhóm viết bài loại mục 4 | Tuấn + nhóm (trừ Hòa, Tâm) |
| 15/11 tối | Vòng hiệu chỉnh 20 bài, họp khoảng 30 phút, sửa hướng dẫn nếu cần | Hòa, Tâm, Tuấn |
| 16–17/11 | Hai bạn chấm độc lập phiếu chính | Hòa, Tâm |
| 17/11 | `merge`, phân xử, chốt `gold.csv` | Tuấn |

## 7. Quyền riêng tư

- Bài thật, phiếu chấm và `gold.csv` chỉ để trong `backend/data/ai-grading/private/`, **không commit, không gửi vào nhóm chat chung**.
- Gửi phiếu cho từng người chấm qua tin nhắn riêng hoặc Drive chia sẻ riêng.
- Báo cáo chỉ dùng số liệu tổng hợp và vài ví dụ ngắn đã ẩn danh.
