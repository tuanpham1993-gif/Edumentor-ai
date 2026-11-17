# Nhờ Hòa chấm phiếu bài tự luận

> Gửi Hòa · từ Tuấn · 15/11/2026 · thời gian khoảng **1,5 giờ** · hạn: **[điền ngày]**

## Vì sao cần Hòa chấm

Nhóm đang làm phần **AI chấm bài tự luận** cho trang ôn tập. Thầy yêu cầu **chứng minh AI chấm đúng bằng số liệu**: so điểm AI với điểm **người chấm** trên cùng một bộ bài.

Điểm Hòa chấm là **đáp án chuẩn** để đối chiếu. Hòa chấm càng cẩn thận, phép đo càng đáng tin.

- Hòa chấm **một mình, theo barem**. Không dùng ChatGPT hay công cụ AI nào, và không hỏi ý người khác về từng bài.
- Hòa **không cần biết AI chấm ra sao**. Điểm của AI được giữ riêng.

## Cách tính điểm (theo đề xuất của Hòa)

Mỗi câu tự luận có barem gồm **ý 1, ý 2, ý 3…**, mỗi ý có số điểm riêng, tổng 10 điểm.

- Bài trả lời **đúng ý nào** thì được **trọn điểm ý đó**.
- Ý nào **không đúng, thiếu, hoặc dài dòng mà không trúng trọng tâm** thì được **0 điểm**.
- **Không có nửa điểm.**

## File cần chấm

**`rater_hoa.xlsx`** (Tuấn gửi kèm)

| Trang | Nội dung |
|---|---|
| `1. Hướng dẫn` | Tóm tắt cách chấm |
| `2. Chấm bài` | **60 bài**, tổng **204 ý** cần chấm |

Ở trang `2. Chấm bài`, mỗi khối là **một bài làm**:

```
[dòng xanh]  BÀI 7 · COND-TL-03 — Đề: ...
[dòng xám]   Bài làm: ...                      ← đọc kỹ TOÀN BỘ ô này (có thể nhiều dòng)
 1 | and is true when both sides are true | 4 | [Nhãn ▼] | [Ghi chú]
 2 | or is true when at least ...          | 3 | [Nhãn ▼] | [Ghi chú]
 3 | not reverses the value                | 3 | [Nhãn ▼] | [Ghi chú]
```

Hòa chỉ điền 2 cột:

- **Nhãn**: với **từng ý**, chọn **`full`** (Đạt) hoặc **`none`** (Không đạt). **Không dùng `partial`.**
- **Ghi chú**: ghi một câu ngắn khi **phân vân**, hoặc khi chấm `none` cho một bài có nhắc tới ý nhưng chưa trúng. Viết tiếng Việt cũng được.

⚠️ Bài làm dài có thể bị **che bớt trong ô**. Hãy bấm vào ô hoặc kéo rộng dòng để đọc **hết** bài trước khi chấm.

Không sửa, xóa, thêm hay sắp xếp lại dòng. Không đổi các cột `row_id` và `sheet_id`.

## Hai mức chấm

| Nhãn | Khi nào | Điểm (máy tự tính) |
|---|---|---|
| **full** (Đạt) | Bài nêu ý này **đúng, đủ, trúng trọng tâm**, và **rõ đang nói về cái gì** | Trọn điểm của ý |
| **none** (Không đạt) | Mọi trường hợp còn lại: **không có**, **thiếu**, **mơ hồ**, **không rõ chủ thể**, **sai**, **nói ngược**, **tự mâu thuẫn**, **chép lại đề**, **dài dòng không trúng trọng tâm** | 0 |

**Phân vân thì chọn `none`** và ghi lý do vào Ghi chú.

## Quy tắc

1. **Chấm theo nghĩa, không theo từ khóa.** Từ khác mà cùng nghĩa vẫn đúng ("exits the loop" và "stops the loop" là một). Dùng đúng từ khóa nhưng sai nghĩa thì không được tính.
2. **Dài dòng không trúng trọng tâm thì `none`.** Đừng cố lục trong một đoạn lan man để tìm chữ đúng.
3. **Bỏ qua lỗi chính tả và ngữ pháp.** Ví dụ "brake = exit loop" vẫn là `full` nếu ý đúng.
4. **Code cũng được tính.** Ví dụ `a, b = b, a` hay `if n % 2 == 0:` tự nó đủ để đạt ý.
5. **Phải rõ chủ thể.** Câu *"It cannot be changed"* chỉ `full` khi đọc là biết *it* là tuple. Các cách viết như *"the other one"*, *"one of them"* mà không rõ là cái nào thì `none`.
6. **Nói ngược thì `none` cho cả hai ý.** Ví dụ *"list không đổi được, tuple đổi được"*.
7. **Tự mâu thuẫn thì `none`.** Bài vừa nói một ý vừa nói điều ngược lại.
8. **Ví dụ nào đúng cũng được.** Ví dụ trong ngoặc ở barem chỉ là gợi ý.
9. **Mỗi lỗi chỉ trừ một lần.** Một ý sai không kéo các ý khác xuống, trừ khi nó mâu thuẫn trực tiếp với ý đó. Ví dụ bài viết `while pw == 'abc123'` (điều kiện sai) thì chỉ ý "điều kiện while" là `none`. Ý "có `print` sau vòng lặp" vẫn chấm theo việc bài có viết `print` sau vòng lặp hay không.

## Ba quy ước riêng (chốt 15/11)

| Câu | Ý | Quy ước |
|---|---|---|
| **CS-TL-03** (lỗi cú pháp và lỗi logic) | Ý 3: *A sensible example* | Đề yêu cầu ví dụ **mỗi** loại, nên phải có **đủ 2 ví dụ** (một lỗi cú pháp, một lỗi logic) mới `full`. Chỉ 1 ví dụ là `none` |
| **COND-TL-06** (giảm giá vé) | Ý 3: *Use or because…* | Chỉ cần giải thích **"chỉ cần một điều kiện đúng"** là `full`. Phần trong ngoặc ("and needs both…") **không bắt buộc** |
| **VAR-TL-02** (đặt tên biến) | Ý 2: *No spaces / special characters, and it cannot be a keyword* | Phải nêu **cả hai điều** mới `full`. Chỉ 1 trong 2 là `none` |

## Ví dụ mẫu

**ITER-TL-01, ý 1:** *break exits / stops the loop completely*

| Bài viết | Nhãn | Vì sao |
|---|---|---|
| "break ends the loop immediately." | full | Cùng nghĩa, khác từ |
| "brake = exit loop" | full | Sai chính tả nhưng đúng ý |
| "It stops the loop." (cùng câu có nói cả continue) | none | Không rõ *it* là break hay continue |
| "break skips to the next iteration." | none | Đó là continue, tức nói ngược |
| "break is a keyword used in loops." | none | Chỉ nêu tên, không nói gì |

**COND-TL-06, ý 1:** *Condition age < 12*

| Bài viết | Nhãn | Vì sao |
|---|---|---|
| `if age < 12 or age >= 60:` | full | Code đúng |
| "people younger than 12" | full | Cùng điều kiện, viết bằng lời |
| `age <= 12` | none | Sai mốc |
| "children get a discount" | none | Không có mốc tuổi |

## Trước khi gửi lại

- [ ] **Đủ 204 ý** đều có Nhãn **`full` hoặc `none`** (không có `partial`)
- [ ] Ý nào phân vân đã có Ghi chú
- [ ] Không thêm, xóa hay sắp xếp lại dòng
- [ ] **Lưu đúng định dạng `.xlsx`** và **gửi riêng cho Tuấn**, không gửi vào nhóm chung. Đây là bài làm của người học nên cần giữ kín.

Cảm ơn Hòa nhiều! 🙏 Có chỗ nào barem khó hiểu thì nhắn Tuấn trước khi chấm tiếp.
