# Chương: AI chấm bài tự luận theo barem

> Module 09 (Ôn tập & đánh giá) · người thực hiện: Tuấn · bản nháp 16/11/2026
> Số liệu đánh giá (B10) điền 18/11/2026, sửa theo góp ý review 19/11 (chạy lại bài lỗi mạng, so AI với từng người
> chấm, kiểm cờ xem lại, nêu rõ rò rỉ và vai trò người phân xử). 20/11: đo độ ổn định qua 3 lần chạy, thêm cờ
"AI chấm chặt hơn từ khóa" và đánh giá các cờ (mục 7.3). Chạy trên phần **test**, prompt `grade-en-v3`.

## 1. Bài toán

Sau mỗi khóa học, người học làm một bài ôn tập để hệ thống ghi nhận khóa đã hoàn thành và cập nhật kỹ năng.
Câu trắc nghiệm chấm được bằng đáp án lưu sẵn. **Câu tự luận thì không**: cùng một ý có thể diễn đạt theo nhiều
cách, viết bằng lời hoặc bằng code, sai chính tả, hoặc nói ngược ý.

Mục tiêu của phần này:

1. **Chấm tự luận tự động theo barem**: mỗi câu có barem gồm ý 1, ý 2, ý 3…, mỗi ý một số điểm, tổng 10.
2. **Chứng minh độ chính xác bằng số liệu**: so điểm AI với điểm người chấm trên cùng một bộ bài (yêu cầu của
   giảng viên).
3. **Tổ chức theo dạng pipeline** (theo bài học pipeline và cách dựng workflow kiểu n8n): chuỗi khối, mỗi khối một
   việc, có rẽ nhánh, thử lại và nhật ký từng khối.

**Hướng tiếp cận đã chốt** (14/11, giảng viên đồng ý): phiên bản 1 dùng **LLM + RAG + Prompt Engineering**, đánh giá
trên bộ bài do người chấm. **Fine-tune để phát triển sau** khi có đủ dữ liệu (mục 9).

## 2. Phạm vi và dữ liệu

| Hạng mục | Giá trị |
|---|---|
| Khóa học thử nghiệm | Khóa 312 "Python Basics: Selection and Iteration", 5 kỹ năng (PY, CS, ITER, VAR, COND) |
| Ngân hàng câu hỏi | 100 câu tiếng Anh: 70 trắc nghiệm, 30 tự luận; 15 đoạn tri thức (3 đoạn / kỹ năng) |
| Cấu trúc một đề | 15 câu: 6 trắc nghiệm Nhận biết + 6 Thông hiểu (0,5 điểm / câu), 2 tự luận Dễ (1 điểm / câu), 1 tự luận Nâng cao (2 điểm). Tổng 10, đạt từ 6 |
| Barem tự luận | Câu Dễ 2–3 ý, câu Nâng cao 4–5 ý; mỗi ý có điểm, tổng 10 (quy về điểm câu) |
| Quy ước chấm mỗi ý | **Đạt** (trọn điểm ý) hoặc **Không đạt** (0). Không có nửa điểm (chốt 15/11) |
| Mô hình ngôn ngữ | Google Gemini (`gemini-3.5-flash-lite`), gọi REST, nhiệt độ 0 |
| Mô hình embedding (RAG) | `paraphrase-multilingual-MiniLM-L12-v2`, vector 384 chiều, tính sẵn cho từng đoạn tri thức |

**Vì sao bỏ nửa điểm.** Ban đầu mỗi ý có 3 mức (đủ, một phần, không). Khi chấm thử, người chấm đề xuất chỉ giữ
hai mức: đúng ý thì được điểm ý, còn thiếu, mơ hồ hoặc dài dòng không trúng trọng tâm thì 0. Theo nhận xét khi
chấm thử, hai mức giúp người chấm thống nhất với nhau hơn và giảm vùng "phân vân" (kỳ vọng — nhóm **chưa đo** so
sánh với 3 mức), nên nhóm áp dụng cho **cả hệ thống**: người chấm, AI và
bộ chấm dự phòng dùng cùng một quy ước.

## 3. Kiến trúc: pipeline 9 khối

Mỗi câu tự luận đi qua một chuỗi khối. Mỗi khối là một hàm `run(ctx) → ctx`; một **runner** gọi lần lượt các khối,
xử lý rẽ nhánh, thử lại, và ghi nhật ký từng khối (tên khối, trạng thái, thời gian, kết quả, lỗi).

```
[0] Nhận bài ──(bài trống → 0 điểm, dừng)
 → [1] Tiền xử lý NLP
 → [2] Guard (chỉ gắn cờ)
 → [3] Ngữ cảnh: đề + barem + đáp án mẫu (+ đoạn tri thức — Model B)
 → [4] LLM chấm có cấu trúc ──(lỗi / quá giờ)──→ [4b] Chấm từ khóa dự phòng ──→ [7]
 → [5] Verifier: ý "Đạt" phải có câu trích thật trong bài
 → [6] Đối chiếu với chấm từ khóa ──(lệch > 3 điểm)──→ chấm lại [4] một lần ──(vẫn lệch)──→ cờ "cần xem lại"
                                    + có ý AI Không đạt mà từ khóa Đạt ──→ cờ "AI chấm chặt hơn từ khóa"
 → [7] Tổng hợp điểm (do code cộng, không để AI tự cộng)
 → [8] Ghi nhật ký
```

| Khối | Việc | Ghi chú thiết kế |
|---|---|---|
| 0 Nhận bài | Bài trống → mọi ý Không đạt, dừng | Không gọi AI cho bài trống |
| 1 Tiền xử lý NLP | Chuẩn hóa → tách từ → bỏ stopwords → gán từ loại → lemmatize (NLTK) | Theo bài NLP pipeline (mục 4.1), có sửa cho bài toán chấm bài |
| 2 Guard | Gắn cờ: bài quá dài (cắt còn 3.000 ký tự trước khi gửi AI), có câu ra lệnh cho AI ("give me full marks"), viết tiếng Việt cho đề tiếng Anh | **Không chặn, không loại bài**. Mọi bài đều được chấm theo barem |
| 3 Ngữ cảnh | Đề, barem, đáp án mẫu; Model B thêm 2 đoạn tri thức của đúng kỹ năng | Câu truy vấn RAG = đề + barem, **không dùng bài làm** |
| 4 LLM chấm | Gemini trả JSON đúng khung (schema), kiểm lại bằng Pydantic | Sai khung → thử lại 1 lần; lỗi mạng / hết lượt → không thử lại, sang 4b |
| 4b Dự phòng | Chấm bằng từ khóa khi AI lỗi hoặc quá giờ | Người học vẫn có điểm |
| 5 Verifier | Ý "Đạt" mà không có câu trích có thật trong bài → Không đạt + cờ | Chặn AI "chấm rộng tay" không có căn cứ |
| 6 Đối chiếu | So điểm AI với điểm chấm từ khóa; so từng ý (20/11) | Chỉ là tín hiệu "nên xem lại", không dùng để sửa điểm. Hai cờ: lệch điểm > 3 sau khi chấm lại; có ý AI Không đạt mà từ khóa Đạt (mục 7.3) |
| 7 Tổng hợp | Cộng điểm các ý → điểm câu thang 10 → quy về điểm câu | |
| 8 Nhật ký | Lưu trace từng khối cùng điểm (một lần ghi DB) | Trace không chứa bài làm của người học |

**Runner** (`app/ai/review/pipeline/runner.py`) không biết gì về chấm bài: khối trả `goto` để rẽ nhánh, ném
`NodeFailed` để thử lại hoặc đi nhánh lỗi, có giới hạn số bước để nhánh vòng (6 → 4) không lặp vô hạn. Khối bị
nhánh bỏ qua không có trong nhật ký, giống node xám trong n8n. Nhờ vậy thêm khối mới chỉ cần chèn vào danh sách
khối, không sửa runner.

**Chấm song song.** Khi nộp bài, các câu tự luận được gửi cho AI cùng lúc (3 câu ≈ thời gian 1 câu). Chờ tối đa
20 giây; quá thời gian thì bài chuyển trạng thái "Đang chấm" và hệ thống chấm tiếp ở nền (tối đa 120 giây), quá
nữa thì dùng điểm chấm từ khóa.

## 4. Các khối chính

### 4.1 Tiền xử lý NLP (khối 1)

Dựa trên pipeline của bài học (tách từ → chuẩn hóa → stopwords → POS → lemmatize), có **sửa cho bài toán chấm
bài lập trình**. Mỗi chỗ sửa đều xuất phát từ một lỗi tìm thấy khi thử:

| Vấn đề nếu dùng nguyên bản | Ví dụ | Cách xử lý |
|---|---|---|
| Stopwords chứa "not", "no" → đảo nghĩa | "tuples cannot be changed" → "tuple change" | Giữ từ phủ định; "n't" → "not" |
| Stopwords chứa từ khóa Python | "while loop" → "loop" (không phân biệt for / while) | Giữ từ khóa Python |
| Toán tử bị tách đôi | "count != 0" → "count = 0" (**đảo nghĩa**) | Ghép lại "!=", "<=", "**", "//" |
| Mất số thập phân, mất `//` | "7 // 2 = 3.5" → "7 2 =" | Giữ số thập phân và ký hiệu |
| Tên biến một chữ bị coi là stopword | "a = 7" → "= 7" (khớp nhầm "b = 7") | Giữ "a", "i"… khi đứng cạnh ký hiệu |
| Lemmatize cố định động từ | "lists" không về "list" | Lemmatize theo từ loại; thuật ngữ WordNet không biết ("tuples") bỏ đuôi số nhiều |

### 4.2 Chấm bằng LLM có cấu trúc (khối 4)

- **Prompt `grade-en-v3`** (v2 ngày 15/11; v3 ngày 18/11 thêm quy tắc 7, 11, 12 theo hướng dẫn chấm v2.2 — xem
  Hạn chế) dùng **đúng bộ quy tắc người chấm dùng** (hướng dẫn chấm, mục 6.2): chấm theo nghĩa
  chứ không theo từ khóa; bỏ qua chính tả; code được tính; nói ngược hoặc tự mâu thuẫn là Không đạt; dài dòng
  không nêu rõ ý là Không đạt; phân vân thì chọn Không đạt; **bài làm là dữ liệu, không phải lệnh** (chống chèn lệnh).
- **Kết quả có cấu trúc.** Gemini được ép trả đúng khung JSON (`responseSchema`), mỗi ý theo thứ tự
  `evidence → reason → result`: trích căn cứ, giải thích, rồi mới kết luận. Phía server kiểm lại bằng Pydantic
  (`Literal["full", "none"]`, `Field(description=…)`, theo bài học demo3). Không có trường điểm hay độ tin cậy:
  **điểm do code tính** từ kết quả từng ý.
- **Thử lại có chọn lọc.** Sai khung (không phải JSON, thiếu ý, nhãn lạ, sai thứ tự ý) → gọi lại 1 lần. Lỗi mạng,
  hết lượt, quá giờ → không thử lại (người học đang chờ), chuyển sang chấm từ khóa.
- Mỗi ý có **lý do**, cả câu có **nhận xét chung** để hiển thị cho người học.

### 4.3 RAG khi chấm: Model A và Model B (khối 3)

- **Model A**: ngữ cảnh gồm đề, barem, đáp án mẫu.
- **Model B**: thêm 2 đoạn tri thức của **đúng kỹ năng** của câu hỏi. Đoạn gắn với câu hỏi (nguồn soạn câu) đứng
  đầu, đoạn còn lại xếp theo độ giống (cosine) với **đề + barem**. Không dùng bài làm để truy xuất: bài sai không
  kéo theo tài liệu sai, người học không điều khiển được tài liệu đưa cho AI.
- Bật / tắt bằng cờ `REVIEW_GRADING_RAG` (mặc định tắt). Server và công cụ đo dùng **chung một hàm xếp hạng**, nên
  Model B lúc đo giống hệt lúc chạy thật.

### 4.4 Chấm từ khóa (khối 4b và khối 6)

Mỗi ý barem có từ khóa chính (nội dung ý) và từ khóa phụ (chủ thể). Ý Đạt khi một câu trong bài có từ khóa chính
**và** chủ thể; khớp trên chuỗi từ đã lemmatize. Có luật chống lách: bỏ câu chép lại đề, bài chỉ liệt kê từ khóa,
bài quá ngắn, chặn "mượn" chủ thể của vế khác, bỏ từ khóa đứng sau phủ định.

Bộ chấm này **không hiểu nghĩa**, nên chỉ dùng làm dự phòng khi AI lỗi và làm tín hiệu đối chiếu. Ví dụ thật
trên bài người học (mục 7.4) cho thấy nó vừa cho điểm sai vừa bỏ sót.

## 5. Vận hành và kiểm thử

- **Kiểm thử tự động:** 868 test cho các module ôn tập, tài khoản, hồ sơ, lập đề và quản trị khóa học. Test không
  gọi Gemini thật (AI giả lập). Các phần quan trọng được **kiểm ngược**: cố ý làm hỏng luật (bỏ thử lại, bỏ
  Verifier, bỏ đối chiếu…) và xác nhận test trượt.
- **Kiểm thử toàn luồng trên Docker** (B12, 16/11, Gemini thật), bằng script đóng vai học viên gọi đúng các API của
  trình duyệt:

| Kiểm tra | Kết quả |
|---|---|
| Sinh đề | 15 câu tiếng Anh, 1,4 giây |
| Nộp bài → có điểm | **1,9–2,1 giây** (mục tiêu ≤ 20 giây) |
| Bài đúng (đáp án mẫu) | Đạt mọi ý, câu trích có thật trong bài, có lý do và nhận xét |
| Bài lạc đề | 0 điểm, lý do: "The student answer does not mention…" |
| Bài trống | 0 điểm, không gọi AI |
| Gemini lỗi (giả lập) | Rẽ sang chấm từ khóa, bài đúng vẫn 10/10 |
| Nhật ký | Đủ 9 khối; mỗi lần gọi Gemini ~2 giây; đối chiếu lệch 0 |

Kiểm thử Docker còn phát hiện và sửa 3 lỗi môi trường: thiếu dữ liệu NLTK trong image, thiếu mô hình embedding
trong volume (RAG lặng lẽ xếp theo thứ tự tạo thay vì độ giống), và lần nộp đầu sau khởi động chậm 10 giây (đã
nạp sẵn lúc khởi động, còn 2,1 giây).

## 6. Phương pháp đánh giá độ chính xác

### 6.1 Bộ bài chuẩn (gold set)

| Nguồn | Số bài | Ghi chú |
|---|---|---|
| Bài thật của người học | 20 | Thu qua 2 Google Form ẩn danh (có câu đồng ý), 4 người, 10 câu tự luận |
| Bài bổ sung có chủ đích | 40 | 10 câu × 4 loại: đúng nhưng diễn đạt khác; đúng một phần; sai / nói ngược; ngắn, sai chính tả. Bản nháp tiếng Việt do **Claude (Anthropic)** viết theo 4 loại bài; bản tiếng Anh cũng do Claude dịch. Nhóm rà lại trước khi đưa vào phiếu. Claude là mô hình **khác Gemini** (mô hình được đánh giá), nên không có chuyện "Gemini chấm bài do chính Gemini viết"; Claude biết loại của từng bài khi viết |
| **Tổng** | **60 bài, 204 ý** | |

Bài bổ sung cần có vì bài thật thu được ít và lệch về một phía; 4 loại bài chính là những chỗ bộ chấm hay sai
(diễn đạt khác, chủ thể mơ hồ, nói ngược, sai chính tả), nên phải có trong bộ bài để đo được.

### 6.2 Quy trình chấm của người

- Người chấm là thành viên nhóm **không làm phần AI**. Người làm AI không chấm (vì biết trước loại của bài bổ sung), trừ việc phân xử — xem bên dưới.
- Chấm **mù**: phiếu dùng mã bài ẩn danh, không lộ bài nào là bài thật hay bài bổ sung, thứ tự bài xáo trộn, không
  có điểm AI.
- Chấm theo **hướng dẫn chấm** (`RATER_GUIDELINE.md`): 2 mức, 12 quy tắc chung, các quy ước riêng cho những ý barem
  dễ hiểu khác nhau, ví dụ mẫu cho từng loại ý.
- **Hai người chấm độc lập cả 60 bài** (Hòa, Tâm), mỗi người một phiếu xáo thứ tự riêng.
- **Độ đồng thuận giữa hai người**: trùng nhãn **90,7%** (185/204 ý), **Cohen's kappa 0,81** (mức "gần như hoàn toàn"),
  QWK theo tổng điểm bài 0,87. Theo phần: dev 93%, test 89%; theo nguồn: bài thật 87%, bài bổ sung 93%.
- Riêng phần **test** (108 ý): hai người trùng **88,9%**, **kappa 0,77** — đây là mốc để so với AI ở mục 7.2.
- **Phân xử**: 19 ý lệch (12 ý thuộc test, 7 ý thuộc dev) do **Tuấn** quyết theo hướng dẫn chấm (16 ý có quy tắc /
  ví dụ rõ; 3 ý chốt thêm quy ước). **Lưu ý:** Tuấn là người làm phần AI, và phần phân tích từng ý lệch đối chiếu
  với hướng dẫn chấm do **Claude** soạn để Tuấn quyết — Claude cũng là mô hình đã viết nháp và dịch bài bổ sung nên biết loại
  của chúng. Khi phân xử **không** mở file "nhãn gợi ý của AI" (bản tham khảo Claude làm ngày 15/11) và **không**
  xem kết quả AI chấm (B10 chạy sau khi phân xử xong) — xem mục Hạn chế.
  Sau phân xử, hướng dẫn chấm lên v2.2 (quy tắc 7 "không chép / diễn đạt lại đề", 9 "sai ngay trong phần nói về ý",
  12 "ý nhiều phần phải đủ"). Bộ bài chuẩn cuối: 204 ý, 109 Đạt / 95 Không đạt; dev 96 ý, test 108 ý.

### 6.3 Chỉ số

| Chỉ số | Cách tính | Mục tiêu ban đầu |
|---|---|---|
| MAE | Trung bình \|điểm AI − điểm người\| trên thang 10 | ≤ 1,0 |
| RMSE | Phạt nặng lỗi lớn | ≤ 1,5 |
| QWK | Cohen's kappa có trọng số bậc hai trên điểm làm tròn (nửa lên) | ≥ 0,70 |
| Khớp từng ý | Tỉ lệ ý AI cùng nhãn với người | ≥ 80% |
| Lệch ≤ 1 điểm | Tỉ lệ bài | ≥ 85% |
| Bài sai bị chấm cao | Người ≤ 4 nhưng AI ≥ 7 | 0 |
| Precision / Recall / F1 theo nhãn | TP / FP / FN cho từng nhãn Đạt / Không đạt (theo bài học demo2) | |
| Độ trễ | p95 thời gian chấm | ≤ 20 giây |

So sánh **5 cách chấm** trên cùng bộ bài: chấm từ khóa; Model A (Gemini, chỉ khối LLM); Model A + ví dụ chấm mẫu
(few-shot, ví dụ chỉ lấy từ câu dev); Model B (Gemini + RAG, chỉ khối LLM); pipeline đủ 9 khối với Model A (cái người
học thật sự nhận). So hai cách bằng **paired bootstrap** (1.000 lần, khoảng tin cậy 95%); chỉ kết luận "B tốt hơn A"
khi khoảng tin cậy không chứa 0. Prompt chỉ được chỉnh trên dev; phần test chạy một lần cho mỗi cách.

## 7. Kết quả

### 7.1 Bảng kết quả (phần test: 30 bài, 108 ý · 18/11/2026 · `gemini-3.5-flash-lite`, prompt `grade-en-v3`)

| Cách chấm | MAE | RMSE | QWK | Khớp từng ý | Lệch ≤ 1 | Bài sai bị chấm cao | F1 (Đạt) | p95 |
|---|---|---|---|---|---|---|---|---|
| Mục tiêu | ≤ 1,0 | ≤ 1,5 | ≥ 0,70 | ≥ 80% | ≥ 85% | 0 | | ≤ 20 s |
| Chấm từ khóa | 2,00 | 3,26 | 0,61 | 80,6% | 50,0% | 0 | 0,81 | 0,05 s |
| Model A (Gemini) ¹ | 0,53 | 1,86 | 0,87 | 95,4% | 90,0% | 2 | 0,96 | 22,7 s |
| Model A + ví dụ chấm mẫu | 0,73 | 2,03 | 0,85 | 93,5% | 83,3% | 2 | 0,94 | 20,4 s |
| Model B (Gemini + RAG) | **0,33** | 1,21 | 0,95 | **96,3%** | **90,0%** | 1 | **0,97** | 34,6 s |
| **Pipeline 9 khối (Model A)** | 0,50 | **1,17** | **0,95** | 94,4% | 80,0% | **0** | 0,95 | 48,9 s |

- ¹ Lần chạy đầu của Model A có 5 ý lỗi (bài R0011, Gemini trả 503 cả sau khi gọi lại) — số liệu khi đó: MAE 0,80,
  RMSE 2,37, QWK 0,78, khớp từng ý 92,6%. Đây là lỗi mạng, không phải chất lượng chấm, nên **gọi lại riêng bài
  R0011** với đúng cấu hình (cùng prompt, cùng model, không chỉnh gì) — vẫn giữ quy tắc "mỗi cấu hình chạy test một
  lần". Bảng dùng số sau khi gọi lại (0 ý lỗi). Các cách chấm khác không có ý lỗi.
- Độ trễ đo trong một buổi Gemini quá tải (nhiều lần 503, phải gọi lại); pipeline còn tính cả lần chấm lại của khối
  Đối chiếu. Khi vận hành, quá 20 giây thì bài chuyển "Đang chấm" và chấm nốt ở nền, người học không phải chờ.
- **Độ lệch trung bình** (AI − người, thang 10): từ khóa −0,73 (chấm chặt); Model A +0,53; A + ví dụ +0,47;
  Model B +0,33; **pipeline +0,03** (gần như không thiên lệch).

**Ma trận nhầm của pipeline 9 khối** (dòng = người, cột = AI):

| | AI: Đạt | AI: Không đạt |
|---|---|---|
| Người: Đạt | 55 | 3 |
| Người: Không đạt | 3 | 47 |

**So sánh từng cặp (paired bootstrap, 1.000 lần, CI 95%)**:

| So sánh | Chênh lệch MAE | Chênh lệch khớp từng ý | Kết luận |
|---|---|---|---|
| Model A − từ khóa | −1,47 [−2,63; −0,27] | +14,8% [+4,3%; +24,7%] | **A tốt hơn từ khóa, có ý nghĩa** |
| A + ví dụ − A | +0,20 [0,00; +0,40] | −1,9% [−4,6%; 0,0%] | Chưa kết luận được (ví dụ không giúp) |
| Model B (RAG) − A | −0,20 [−0,80; +0,20] | +0,9% [−2,7%; +5,6%] | Chưa kết luận được |
| Pipeline 9 khối − A | −0,03 [−0,63; +0,43] | −0,9% [−6,1%; +4,8%] | Chưa kết luận được (độ chính xác ngang nhau) |

**Nhận xét:**
1. **Chấm theo nghĩa tốt hơn chấm từ khóa, có ý nghĩa thống kê** (khớp từng ý +14,8 điểm %, MAE giảm 1,47).
2. **Pipeline 9 khối đạt** MAE, RMSE, QWK, khớp từng ý và **0 bài sai bị chấm cao**; **chưa đạt** "lệch ≤ 1 điểm" (80%,
   mục tiêu 85% — một ý 2–4 điểm chấm khác là đã lệch quá 1 điểm) và **độ trễ** (p95 48,9 s, mục tiêu 20 s). Model A chấm một mình (chỉ khối LLM) **chưa đạt** RMSE (1,86 > 1,5), có **2 bài sai bị
   chấm cao** và p95 cũng vượt 20 s.
3. Pipeline **không chính xác hơn** Model A (chênh lệch ≈ 0, chưa kết luận được), nhưng **an toàn hơn**: Verifier và
   khối Đối chiếu đưa số bài sai bị chấm cao từ 2 về 0.
4. **RAG và ví dụ chấm mẫu chưa cho thấy cải thiện có ý nghĩa** với 30 bài test (ví dụ chấm mẫu còn hơi kém hơn).
   Theo nguyên tắc đặt trước khi đo, hệ thống **giữ pipeline với Model A** (`REVIEW_GRADING_RAG`,
   `REVIEW_GRADING_FEWSHOT` tắt).

### 7.2 AI so với từng người chấm

So với bộ bài chuẩn đã phân xử thì AI có lợi thế (bộ chuẩn và prompt cùng theo hướng dẫn v2.2). Để so **ngang hàng**,
đo AI với **từng** người chấm trên đúng 108 ý của phần test, đặt cạnh mức hai người khớp nhau:

| Cặp so sánh (phần test, 108 ý) | Khớp từng ý | Cohen's kappa |
|---|---|---|
| **Hòa – Tâm** (hai người với nhau) | 88,9% | **0,77** |
| Từ khóa – Hòa / – Tâm | 78,7% / 76,9% | 0,57 / 0,54 |
| Model A – Hòa / – Tâm | 93,5% / 93,5% | 0,87 / 0,87 |
| A + ví dụ – Hòa / – Tâm | 91,7% / 91,7% | 0,83 / 0,83 |
| Model B (RAG) – Hòa / – Tâm | 94,4% / 94,4% | 0,89 / 0,89 |
| **Pipeline – Hòa / – Tâm** | 92,6% / 90,7% | **0,85 / 0,81** |

Mọi cách chấm bằng Gemini khớp với **từng** người chấm ít nhất ngang mức hai người khớp với nhau (κ 0,81–0,89 so với
0,77); chấm từ khóa thì thấp hơn rõ (κ 0,54–0,57). Cần đọc thận trọng: prompt v3 dùng các quy tắc rút ra khi phân xử
(xem Hạn chế), nên một phần lợi thế có thể đến từ việc AI đã "biết" cách xử các ca khó.

**Các ý pipeline chấm khác người (6/108):**

| Bài | Ý | Người | AI | Nguyên nhân |
|---|---|---|---|---|
| R0002 | CS-TL-03 ý 1 (lỗi cú pháp) | Không đạt | Đạt | Định nghĩa đúng nhưng ví dụ sai khái niệm; **hai người chấm cũng lệch**, Tuấn phân xử |
| R0007, T028 | CS-TL-03 ý 3 (ví dụ) | Không đạt | Đạt | Quy ước riêng "phải đủ hai ví dụ" — **cố ý không đưa vào prompt** để không rò rỉ câu test; hai người chấm cũng lệch |
| T025 | CS-TL-03 ý 3 | Đạt | Không đạt | AI chấm chặt hơn người |
| T030 | ITER-TL-05 ý 3 (in thông báo sau vòng lặp) | Đạt | Không đạt | AI áp quy tắc "không diễn đạt lại đề" quá rộng |
| T038 | COND-TL-06 ý 3 (vì sao dùng or) | Đạt | Không đạt | Bài nêu rõ "only 1 condition needs to be true"; AI chấm sai |

Ba trên sáu ý AI sai nằm đúng ở các ý mà **chính hai người chấm cũng không thống nhất**: lỗi của AI tập trung ở ý mơ
hồ, không rải rác. Ba ý còn lại AI chấm **chặt hơn** người (không chấm rộng tay).

**Các ý sai này có được đưa cho giáo viên xem lại không?** Chạy lại pipeline riêng cho 6 bài trong bảng trên
(19/11): với cờ lúc đó (chỉ "lệch điểm > 3") chỉ **2/6 bài bị gắn cờ**, 4 bài lọt qua. Cờ "sát ngưỡng đạt" không đo
được ở đây (cần điểm cả lượt 15 câu, bộ bài chuẩn chỉ có từng câu). Từ đó nhóm đo kỹ hơn và cải thiện cờ (mục 7.3).
Bảng 7.1 giữ số của lần đo B10 (lần chạy test chính thức); các lần chạy lại chỉ dùng để kiểm cờ và độ ổn định, không
dùng để sửa kết quả.

### 7.3 Độ ổn định và cờ "cần xem lại" (20/11)

Chạy lại pipeline **thêm 2 lần** trên 30 bài test, **cùng cấu hình** B10 (cùng model, prompt `grade-en-v3`, không RAG,
không ví dụ mẫu). Lần 3 có 3 bài Gemini lỗi tạm thời → gọi lại riêng 3 bài đó, kết quả cuối không còn bài lỗi.

| Chỉ số | Kết quả |
|---|---|
| Khớp từng ý với bộ bài chuẩn — lần 1 (B10) / lần 2 / lần 3 | 94,4% / 98,1% / 93,5% (trung bình **95,3%**) |
| Ý cho **cùng kết quả cả 3 lần** | **100/108 = 92,6%** |
| Kappa giữa hai lần chạy (3 cặp) | 0,87 – 0,93 |
| Bài có điểm câu khác nhau giữa các lần | 7/30 (chênh trung bình 0,7 điểm, lớn nhất 6 điểm, thang 10) |

- Dù nhiệt độ 0, Gemini **không hoàn toàn ổn định**: 8/108 ý đổi kết quả giữa các lần. Mức khớp với chính nó
  (kappa 0,87–0,93) vẫn **cao hơn** mức hai người chấm khớp nhau (0,77).
- 8 ý đổi kết quả **tập trung ở vài câu**: 4 ý thuộc CS-TL-03 (ý 3 "nêu ví dụ" có quy ước riêng), 2 ý PY-TL-02,
  ý 3 của ITER-TL-05 và COND-TL-06 — cũng là những chỗ hai người chấm từng lệch nhau. AI "phân vân" đúng ở ý mơ hồ.
- Độ chính xác dao động 93,5–98,1% tùy lần; con số 94,4% ở bảng 7.1 là **một** lần đo trong khoảng này.

**Cải thiện và đánh giá cờ.** Mỗi lần chạy lần lượt làm "lần chấm chính", một lần khác làm "lần chấm thứ hai" →
90 lượt bài, 13 lượt AI chấm sai:

| Cờ | Bắt được bài AI chấm sai | Số bài phải xem lại | Gắn cờ nhầm |
|---|---|---|---|
| Cũ: lệch điểm với chấm từ khóa > 3 | 1/6 (trên B10) | 7/30 | |
| **A — cũ + có ý AI Không đạt mà từ khóa Đạt** (đã đưa vào hệ thống 20/11) | 8/13 = **62%** | 38% | 26 |
| B — chấm 2 lần, có ý khác nhau | 8/13 = 62% | **16%** | **6** |
| A + B | 11/13 = **85%** | 46% | 30 |
| C — ý Đạt mà câu trích quá ngắn / giống đề | thấp | 53% | rất nhiều → **không dùng** |

- Hệ thống dùng **A** (không tốn thêm lượt Gemini). A có lợi cho học viên: AI chấm chặt (đánh trượt ý) thì có người
  xem lại. Bài lọt qua A là bài mà chấm từ khóa cũng sai giống AI.
- **B** hiệu quả nhất (ít gắn cờ nhầm) và bắt đúng loại lỗi A bỏ sót, nhưng **tốn gấp đôi lượt Gemini** cho câu tự
  luận → chưa đưa vào, ghi ở Hướng phát triển.

### 7.4 Quan sát trên bài thật (định tính, trước khi có số liệu)

Trên 20 bài thật, bộ chấm từ khóa mắc đúng hai kiểu lỗi mà chấm theo nghĩa phải khắc phục:

| Bài làm | Chấm từ khóa | Đúng ra |
|---|---|---|
| Không nhắc kiểu trả về của `input()`, chữ "string" chỉ xuất hiện ở câu về `print` | Đạt ý "input() trả về chuỗi" | Không đạt |
| Đảo nghĩa AND và OR | Cho điểm cả hai ý (khớp chữ "both", "at least one") | Không đạt |
| "as long as 2 side hold true" (ý của AND) | Không đạt (thiếu chữ "both") | Đạt |
| "it dont give ticket discount" (age = 30) | Không đạt | Đạt |

Trên cùng loại bài, Gemini (qua kiểm thử toàn luồng) chấm đúng bài đúng, bài lạc đề và đưa lý do bám theo barem.
Số liệu định lượng trên phần test ở mục 7.1: chấm từ khóa khớp người 80,6%, pipeline Gemini 94,4%.

## 8. Hạn chế

- **Mẫu nhỏ**: 60 bài (test 30 bài), trong đó 20 bài thật; khoảng tin cậy rộng nên chưa kết luận được RAG hay ví dụ
  chấm mẫu có tốt hơn hay không (mục 7.1).
- **Bài bổ sung có chủ đích** không phản ánh đúng phân bố bài thật (cố ý có nhiều bài khó).
- **Người chấm**: hai người (kappa 0,81) — đủ tin cậy cho bộ bài này, nhưng vẫn là thành viên nhóm, chưa phải giảng
  viên độc lập.
- **Độ trễ** đo trong buổi Gemini quá tải: p95 vượt mục tiêu 20 giây; hệ thống đã có chấm nền khi quá giờ.
- **Rò rỉ nhẹ từ phần test vào prompt.** Hướng dẫn chấm v2.2 ra đời **sau** khi phân xử 19 ý lệch, trong đó 12 ý thuộc
  test. Prompt `grade-en-v3` dùng các **quy tắc chung** của v2.2 (để AI và người chấm cùng chuẩn); **quy ước riêng
  của từng câu không đưa vào prompt**, ví dụ chấm mẫu chỉ lấy từ dev. Dù vậy kết quả trên test có thể **lạc quan hơn**
  khi gặp một bộ bài hoàn toàn mới — nên soạn thêm bộ test mới (chưa ai phân xử) để đo lại.
- **Người phân xử là người làm AI** (Tuấn), dựa trên phân tích do Claude soạn; Claude đã viết nháp và dịch bài bổ sung nên
  biết loại bài. Đã hạn chế bằng cách chỉ quyết theo quy tắc / ví dụ trong hướng dẫn chấm, không mở file nhãn gợi ý
  của AI, không xem kết quả AI chấm; nhưng về nguyên tắc nên có **người phân xử độc lập** (vd giảng viên).
- **AI chưa hoàn toàn ổn định giữa các lần gọi**: qua 3 lần chạy, 92,6% ý giữ nguyên kết quả, độ chính xác dao
  động 93,5–98,1% (mục 7.3). Học viên nộp lại cùng một bài có thể nhận điểm khác ở ý mơ hồ.
- **Cờ "cần xem lại" bắt khoảng 62% bài AI chấm sai** (cờ A, mục 7.3), đổi lại giáo viên phải xem khoảng 38% bài —
  giáo viên xem lại vẫn chỉ là lưới an toàn một phần.
- **RAG nhỏ**: mỗi kỹ năng chỉ 3 đoạn tri thức, RAG gần như tra cứu cố định; A ≈ B là kết quả có thể xảy ra.
- **Đối chiếu dựa vào chấm từ khóa** (yếu) nên có thể gắn cờ "cần xem lại" nhiều hơn cần thiết.
- Quy tắc chung của hướng dẫn chấm đã có trong prompt (`grade-en-v3`), nhưng **quy ước riêng từng câu** chưa ghi vào
  nội dung ý của barem, nên AI chưa "biết" (một nửa số ý AI sai rơi vào đây).
- Phụ thuộc dịch vụ ngoài (Gemini): có dự phòng chấm từ khóa nhưng chất lượng thấp hơn.

## 9. Hướng phát triển

**Fine-tune mô hình chấm** (đã thống nhất với giảng viên là phát triển sau):

- *Khi nào cần*: khi đo trên bộ bài lớn cho thấy LLM + prompt chưa đạt mục tiêu ở những lỗi có hệ thống (ví dụ
  một loại câu luôn chấm lệch), hoặc khi cần chạy cục bộ, không phụ thuộc dịch vụ ngoài.
- *Dữ liệu*: mỗi mẫu là (đề, barem, bài làm) → nhãn từng ý + lý do, do người chấm gán. Nguồn: bộ bài chuẩn mở
  rộng, bài thật tích lũy khi hệ thống chạy, và các bài được gắn cờ "cần xem lại" đã được người duyệt.
- *Cách làm*: QLoRA trên mô hình mở cỡ nhỏ (vd Qwen), giữ nguyên pipeline, chỉ thay khối 4.
- *Cách chứng minh*: chạy cùng công cụ đo, cùng bộ test, so với Model A / B bằng bootstrap như mục 6.3.

Các hướng khác:

- Mở rộng bộ bài chuẩn (trên 100 bài test) để so RAG / ví dụ chấm mẫu có ý nghĩa thống kê, thêm khóa học khác.
- Ghi các quy ước riêng vào nội dung ý của barem để AI và người chấm cùng chuẩn.
- Dùng các bài giáo viên đã chấm lại trên trang "Kết Quả - AI Chấm" làm dữ liệu cải thiện prompt / fine-tune.
- Kiểm tra theo kỹ năng từ node lộ trình, AI soạn đề và barem có cổng kiểm tra tự động, mở rộng ra 5.893 kỹ năng
  (thiết kế ở `docs/guide.md`).
- Thêm cờ **B — chấm 2 lần** (mục 7.3): chấm lần hai ở nền sau khi trả kết quả, ý nào hai lần khác nhau thì đưa
  giáo viên xem lại. Đo trên bộ test: A + B bắt 85% bài AI chấm sai; cái giá là gấp đôi lượt Gemini cho tự luận.
- Thay bộ chấm từ khóa ở khối Đối chiếu bằng một tín hiệu tốt hơn (vd chấm lại bằng mô hình thứ hai).
- Kho vector (pgvector) khi tài liệu tri thức lớn.

## Phụ lục: vị trí trong mã nguồn

| Phần | File |
|---|---|
| Runner và pipeline 9 khối | `backend/app/ai/review/pipeline/runner.py`, `essay.py` |
| Tiền xử lý NLP | `backend/app/ai/review/text_pipeline.py` |
| Prompt chấm, schema | `backend/app/ai/prompts/review_grading.py`, `backend/app/ai/review/grading_schema.py` |
| Gọi Gemini | `backend/app/ai/review/real_ai.py` |
| Chấm từ khóa | `backend/app/ai/review/keyword_grader_en.py`, `keyword_grading.py` |
| RAG | `backend/app/services/review_rag_service.py` |
| Chấm song song, ghi điểm | `backend/app/services/review_grader.py`, `review_service.py` |
| Bộ bài chuẩn, công cụ đo | `backend/scripts/gold_sheets.py`, `eval_grading.py` |
| Kiểm thử toàn luồng | `backend/scripts/b12_e2e_review.py` |
| Hướng dẫn chấm | `docs/ai-grading/RATER_GUIDELINE.md` |
