# Hướng dẫn chấm bài tự luận: bộ bài chuẩn EduMentor AI

> Phiên bản 2.2 · 18/11/2026 · phụ trách: Tuấn (module 09) · người chấm: **Hòa, Tâm**
> Nhật ký thay đổi ở cuối trang. Đọc hết một lượt trước khi chấm (khoảng 10 phút).
> Bản rút gọn kèm ví dụ: [HUONG_DAN_CHAM_HOA.md](HUONG_DAN_CHAM_HOA.md).

## 1. Vì sao cần bạn chấm

Nhóm đang làm một AI chấm bài tự luận về Python cơ bản, **chấm từng ý theo barem**.
Thầy yêu cầu **chứng minh AI chấm đúng bằng số liệu**, nên cần một bộ bài do người chấm: *bộ bài chuẩn* (gold set).
Điểm AI sẽ được so với điểm bạn chấm. Điểm của bạn là **đáp án chuẩn**, nên hãy chấm
**cẩn thận, độc lập và nhất quán**. Điều này quan trọng hơn tốc độ.

- Mỗi người chấm **phần bài của mình, một mình**. Không xem nhãn của người khác, và không bàn với nhau về từng bài cụ thể.
- Bạn **không bao giờ thấy điểm AI chấm**. Đừng đoán, và đừng đưa bài làm vào bất kỳ công cụ AI nào.
- Khối lượng: bộ bài có **60 bài, 204 ý**, chia cho cả nhóm. Mỗi người khoảng 15–20 bài, chừng **25–30 phút**.

## 2. Phiếu chấm

Bạn nhận một file **`.xlsx`** (mở bằng Excel hoặc Google Sheets) gồm 2 trang:

| Trang | Nội dung |
|---|---|
| `1. Hướng dẫn` | Tóm tắt cách chấm |
| `2. Chấm bài` | Các bài cần chấm. Mỗi khối là **một bài làm**: dòng xanh là đề, dòng xám là bài làm, bên dưới là các ý barem |

Mỗi dòng ý barem có các cột:

| Cột | Ý nghĩa |
|---|---|
| `Ý`, `Nội dung ý barem` | Ý cần chấm ở dòng này (barem ghi bằng tiếng Anh, giống đề) |
| `Điểm` | Số điểm của ý (chỉ để tham khảo, bạn không cần tính điểm) |
| **`Nhãn`** | **Bạn điền:** chọn `full` hoặc `none` trong danh sách thả xuống |
| `Ghi chú` | Không bắt buộc: một câu ngắn giải thích. **Nên ghi khi phân vân, hoặc khi chấm `none` cho bài có nhắc tới ý nhưng chưa trúng** |
| `row_id`, `sheet_id` | Mã ẩn danh. **Không sửa** |

⚠️ Bài làm dài có thể bị **che bớt trong ô**. Bấm vào ô hoặc kéo rộng dòng để đọc **hết** bài trước khi chấm.

Không sắp xếp, xóa hay thêm dòng. Các cột khác giữ nguyên.

## 3. Hai mức chấm

Chấm **từng ý riêng**: trong bài làm, ở *bất kỳ chỗ nào*, có nêu được ý này không?

| Nhãn | Dùng khi | Điểm (máy tự tính) |
|---|---|---|
| **full** (Đạt) | Ý được nêu **đúng, đủ, trúng trọng tâm**, và **rõ đang nói về cái gì** | Trọn điểm của ý |
| **none** (Không đạt) | Mọi trường hợp còn lại: **không có, thiếu, mơ hồ, không rõ chủ thể, sai một phần hoặc sai hoàn toàn**, tự mâu thuẫn, chỉ chép lại đề, chỉ nêu tên mà không nói gì, hoặc **dài dòng mà không nêu rõ ý** | 0 |

**Không có nửa điểm** (chốt 15/11 theo đề xuất của Hòa). Đừng ghi điểm lẻ như "1 điểm" vào Ghi chú.
Phân vân thì chọn **`none`** và ghi lý do vào Ghi chú.

## 4. Quy tắc chung

1. **Chấm theo nghĩa, không theo từ khóa.** Từ khác mà cùng nghĩa vẫn đúng ("exits the loop" =
   "stops the loop" = "jumps out of the loop"). Dùng đúng từ khóa nhưng sai nghĩa thì **không** được tính.
2. **Bỏ qua lỗi chính tả, ngữ pháp, văn phong.** "brake stop the loop" (ý nói `break`) vẫn là `full` nếu ý rõ ràng.
   Bài viết bằng tiếng Việt hoặc lẫn hai thứ tiếng cũng chấm theo nghĩa (ghi `vi` vào Ghi chú).
3. **Code cũng được tính.** `a, b = b, a`, `if n % 2 == 0:` hay `print(a + b)` tự nó đủ để đạt ý.
4. **Phải rõ chủ thể.** Câu "It cannot be changed" chỉ `full` khi đọc là biết *it* là tuple. Nếu người đọc
   không biết đang nói về cái nào thì `none`.
5. **Nói ngược hoặc gán nhầm thì `none`.** "A list cannot be changed, a tuple can" là `none` cho cả hai ý.
6. **Tự mâu thuẫn thì `none`.** Bài vừa nêu ý vừa nói điều ngược lại thì ý đó `none`.
7. **Chép lại đề không được điểm.** Những chữ chỉ lặp lại từ đề thì không tính. **Phải nêu rõ ý chính của
   barem bằng nội dung của chính người học** mới được điểm ý đó (chốt 18/11). Bài chỉ diễn đạt lại yêu cầu của đề
   rồi thêm một từ khóa (vd đề "hỏi mật khẩu đến khi nhập đúng", bài viết "Use a while loop to ask for the password
   until it is correct") thì các ý về **điều kiện lặp** và **nhập lại trong vòng lặp** đều `none`: phần "until it
   is correct" là chữ của đề, không cho thấy người học biết đặt điều kiện hay đặt `input()` ở đâu.
8. **Ví dụ nào đúng cũng được.** Ví dụ trong ngoặc ở barem chỉ là gợi ý, không phải đáp án duy nhất.
9. **Câu sai ở chỗ khác không làm mất điểm các ý khác**, trừ khi mâu thuẫn trực tiếp với ý đó (quy tắc 6).
   Ngược lại, chỗ sai nằm **ngay trong phần nói về ý đang chấm** (vd định nghĩa đúng nhưng ví dụ kèm theo sai khái
   niệm) thì ý đó `none` — là "sai một phần" (chốt 18/11).
12. **Ý gồm nhiều phần thì phải đủ các phần.** Barem ghi "A; B" hoặc "A và B" mà bài chỉ nêu A thì `none`
    (chốt 18/11, cùng tinh thần "đúng và đủ" ở mục 3).
10. **Chỉ liệt kê từ khóa** ("mutable immutable [] ()") mà không nói gì về cái gì thì `none`.
    Một câu ngắn nhưng có nghĩa ("list mutable, tuple not") vẫn được. Bài dài mà không nêu rõ ý
    cũng là `none`: đừng lục tìm từ khóa trong một đoạn lan man.
11. **Không chấm chất lượng chung của bài.** Chỉ chấm các ý barem. Bài trình bày lộn xộn vẫn có thể `full` mọi ý.

## 4b. Quy ước riêng từng câu (chốt 15/11)

| Câu | Ý | Quy ước |
|---|---|---|
| CS-TL-03 | 3: ví dụ hợp lý | Đề yêu cầu ví dụ **mỗi** loại lỗi: đủ hai ví dụ (một lỗi cú pháp, một lỗi logic) là `full`; chỉ một ví dụ là `none` |
| COND-TL-06 | 3: dùng or vì… | Chỉ cần giải thích **"chỉ cần một điều kiện đúng"** là `full`; phần trong ngoặc ("and needs both…") không bắt buộc |
| VAR-TL-02 | 2: không khoảng trắng / ký tự đặc biệt, không trùng từ khóa | Nêu đủ cả hai điều là `full`; chỉ một trong hai là `none` |
| VAR-TL-02 | 4: dynamic typing | Phải đủ **cả hai** phần: không cần khai báo kiểu **và** kiểu theo giá trị gán lúc chạy. Chỉ "không cần khai báo kiểu" là `none` (chốt 18/11) |
| CS-TL-03 | 1: lỗi cú pháp | Nói "sai ngữ pháp / sai quy tắc" nhưng lấy ví dụ không phải lỗi cú pháp (vd "dùng biến chưa khai báo" là lỗi khi chạy) là `none` (quy tắc 9, chốt 18/11) |
| ITER-TL-05 | 1, 2: điều kiện lặp, nhập lại trong vòng lặp | Chỉ viết "dùng while để hỏi mật khẩu đến khi đúng" (diễn đạt lại đề) là `none` cả hai ý (quy tắc 7, chốt 18/11) |

Quy tắc 9 cũng có nghĩa **mỗi lỗi chỉ trừ một lần**. Ví dụ bài viết `while pw == 'abc123'` thì ý "điều kiện while" là `none`,
còn ý "in thông báo sau vòng lặp" vẫn chấm theo việc bài có `print` sau vòng lặp hay không.

## 5. Ví dụ mẫu

**Ý khái niệm**: ITER-TL-01, ý 1: *"break exits / stops the loop completely"*

| Bài viết (trích) | Nhãn | Vì sao |
|---|---|---|
| "break ends the loop immediately." | full | Cùng ý, khác từ |
| "It stops the loop." (cùng câu có nói cả continue) | none | Không rõ *it* là break hay continue |
| "break skips to the next iteration." | none | Đó là continue, tức nói ngược (quy tắc 5) |
| "break is a keyword used in loops." | none | Chỉ nêu tên, không nói gì về nó |

**Ý so sánh, cần chủ thể**: PY-TL-02, ý 2: *"A tuple cannot be changed after it is created"*

| Bài viết (trích) | Nhãn | Vì sao |
|---|---|---|
| "Tuples are immutable." | full | |
| "A list can be changed, but not the other one." | none | Không rõ chủ thể |
| "You cannot change it." mà cả bài không nói "it" là gì | none | Không có chủ thể |
| "A tuple can be changed with append()." | none | Sai |

**Ý giá trị, code**: COND-TL-06, ý 1: *"Condition age < 12"*

| Bài viết (trích) | Nhãn | Vì sao |
|---|---|---|
| `if age < 12 or age >= 60:` | full | Code đạt ý |
| "people younger than 12" | full | Cùng điều kiện, viết bằng lời |
| `age <= 12` | none | Sai mốc |
| "children get a discount" | none | Không có mốc tuổi |

**Ý giải thích**: CS-TL-05, ý 2: *"the division is done before the addition (it prints 7.0)"*

| Bài viết (trích) | Nhãn | Vì sao |
|---|---|---|
| "/ has higher priority than +, so only b is divided." | full | |
| "It prints 7.0 instead of 5." | none | Chỉ nêu hiện tượng, không nêu nguyên nhân |
| "Because of operator order." | none | Có nhắc nguyên nhân nhưng không giải thích |
| "Because a and b are integers." | none | Sai nguyên nhân |

**Ý ví dụ**: CS-TL-03, ý 3: *"a sensible example (a missing colon; a wrong condition...)"*

| Bài viết (trích) | Nhãn | Vì sao |
|---|---|---|
| Ví dụ lỗi cú pháp `prnt('hi')` **và** ví dụ lỗi logic "dùng `-` thay cho `+`" | full | Ví dụ nào đúng cũng được (quy tắc 8), đủ hai loại (mục 4b) |
| Chỉ có ví dụ "quên dấu hai chấm sau if" | none | Thiếu ví dụ lỗi logic (mục 4b) |
| "for example a mistake in the code" | none | Không phải ví dụ, chỉ là nói lại |

## 6. Cách tổ chức chấm

1. **Chấm thử:** Hòa chấm trước một phần bài. Tuấn so lại, chỗ nào quy tắc chưa rõ thì cập nhật hướng dẫn này (lên phiên bản mới).
2. **Chấm chung (thứ 5):** 60 bài chia cho cả nhóm, mỗi người một phiếu riêng, chấm **độc lập** theo hướng dẫn này.
3. Tuấn gộp các phiếu thành bộ bài chuẩn. Chỗ nào nhãn sai rõ so với hướng dẫn (ví dụ thiếu nhãn, trái quy ước mục 4b) thì Tuấn hỏi lại người chấm. Tuấn **không tự sửa nhãn** của người chấm.

Tuấn không chấm, vì Tuấn là người làm AI và biết trước loại của từng bài bổ sung.

## 7. Trước khi gửi lại

- [ ] Mọi ý trong phần của bạn đều có Nhãn (`full` hoặc `none`), không bỏ trống ý nào.
- [ ] Không ghi điểm lẻ ("1 điểm") vào Ghi chú. Chỉ có Đạt hoặc Không đạt.
- [ ] Ý nào phân vân đã có Ghi chú.
- [ ] Không sắp xếp, xóa hay thêm dòng.
- [ ] Lưu đúng **`.xlsx`** và **gửi riêng cho Tuấn** (không gửi vào nhóm chung). Bài làm là dữ liệu của người học, không chia sẻ.

## Nhật ký thay đổi

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 14/11/2026 | Bản đầu tiên (tiếng Anh). |
| 1.1 | 15/11/2026 | Thêm mục 4b (ba quy ước riêng từng câu, mỗi lỗi chỉ trừ một lần). Bản rút gọn tiếng Việt cho Hòa: `HUONG_DAN_CHAM_HOA.md`. |
| 2.0 | 15/11/2026 | **Chỉ còn hai nhãn** (`full` / `none`, không có nửa điểm) theo đề xuất của Hòa; cả hệ thống đổi theo (prompt grade-en-v2). |
| 2.1 | 16/11/2026 | **Chuyển sang tiếng Việt.** Cập nhật quy trình cho đúng thực tế: phiếu `.xlsx`, 60 bài chia cả nhóm, chấm thử rồi chấm chung (thay cho "2 người chấm 120 bài + vòng hiệu chỉnh"). Ví dụ CS-TL-03 sửa theo quy ước mục 4b. **Quy tắc chấm không đổi.** |
| 2.2 | 18/11/2026 | Sau khi phân xử 19 ý Hòa và Tâm chấm lệch (trùng 90,7%, kappa 0,81): **quy tắc 7** làm rõ: không chép lại đề, phải nêu rõ ý chính của barem mới được điểm. **Quy tắc 9** thêm: sai ngay trong phần nói về ý đó là `none`. Thêm **quy tắc 12**: ý nhiều phần phải đủ các phần. Mục 4b thêm 3 quy ước (VAR-TL-02 ý 4, CS-TL-03 ý 1, ITER-TL-05 ý 1–2). |
