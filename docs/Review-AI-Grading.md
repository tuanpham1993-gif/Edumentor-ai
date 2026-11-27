  # Review-AI-Grading — Kế hoạch AI chấm bài tự luận theo barem (module 09)

> Người thực hiện: **Tuấn** · Người hướng dẫn / review: **Claude** · Bắt đầu: **14/11/2026** · Hạn nộp: **25/11/2026**
> Nhánh làm việc: `tuan/future-auth` (xong thì gộp vào `review/featrure`, không qua `develop`).
> Liên quan: `docs/Review-Assessment.md` (GĐ7 Quản trị Ôn tập), `docs/De-xuat-AI-On-tap.md`.
> Cách dùng: làm xong việc nào thì tích `[x]` và điền **ngày thực tế**. Hết mỗi bước, nhắn **"review B<số>"** để Claude review.
> Ký hiệu: 👤 Tuấn làm · 🤖 Claude hỗ trợ · ✅ điều kiện nghiệm thu.

---

## 1. Yêu cầu đã chốt

### 1.1 Của thầy
| Ngày | Yêu cầu |
|---|---|
| 06/11 | AI sinh câu hỏi bằng **system prompt + RAG**; có trắc nghiệm và tự luận |
| 09/11 | Họp chốt A1–A13 (`BA-nhom/Cau-hoi-hop-thay-09-11-On-tap-AI_da-chot-v3.docx`): đề 15 câu (12 TN + 3 TL), chấm tự luận theo **từng ý barem**, có dự phòng khi AI lỗi |
| 14/11 | **Phiên bản 1 = LLM + RAG + Prompt Engineering**, đánh giá trên bộ bài người chấm. **Fine-tune để phát triển sau** |
| 14/11 | **Cần chứng minh độ chính xác** (so điểm AI với điểm người chấm bằng số liệu) |
| 14/11 | **Tổ chức code theo pipeline** thầy gửi trên Classroom và **tham khảo cách n8n workflow** (chuỗi khối, mỗi khối một việc, có nhánh, thử lại, ghi nhật ký từng khối) |

Tài liệu thầy gửi (chép từ thư mục môn `C:\HK2 T3.2511.M0\Language Processing(NLP)` vào `BA-nhom/pipeline/`, 14/11) và chỗ dùng trong pipeline:

| File | Nội dung | Dùng ở |
|---|---|---|
| `Session01/nlp-pipeline.py` | NLTK: tách từ → chuẩn hóa → bỏ stopwords → POS → lemmatize | **Khối 1** (B1); nền cho chấm từ khóa (B3), Verifier (B8), phát hiện chép đề |
| `Session02/demo1.py` | spaCy `EntityRuler`: luật mẫu nhận cụm từ | (tùy chọn) B3 — luật cụm từ / phủ định cho chấm từ khóa, vd "cannot" + "change" |
| `Session02/demo2.py` | Precision / Recall / F1 so dự đoán với nhãn đúng | **B5** — thêm P / R / F1 theo từng nhãn full / partial / none, bên cạnh MAE / QWK |
| `Session02/demo3.py` | LLM + **Pydantic schema** + `instructor`, `temperature 0`, có chế độ mô phỏng khi thiếu API key | **Khối 4** (B7) — schema Pydantic cho kết quả chấm; mô phỏng = `AI_MODE=mock` đã có |

Ghi chú: demo3 dùng OpenAI; dự án giữ **Gemini** (D3). Học **cách làm** của `instructor` (schema Pydantic + kiểm + thử lại khi sai) và tự viết bằng `httpx` + Pydantic đang có — không thêm thư viện `instructor` / `openai` nếu nhóm chưa đồng ý.

### 1.2 Của Tuấn (13/11)
| # | Quyết định |
|---|---|
| D1 | **Tiếng Anh** cho câu hỏi, barem, bài làm (trắc nghiệm và tự luận) — khớp QT11, QT13 |
| D2 | Fine-tune (Qwen3-1.7B QLoRA, notebook của Hòa) **để sau**, chỉ viết mục "Hướng phát triển" |
| D12 | Làm **đến hạn nộp ~25/11**, không có giai đoạn 12 tuần |
| QT10 | **Gemini là bộ chấm chính**; chấm từ khóa (1) chấm thay khi Gemini lỗi, (2) đối chiếu — lệch **> 3** điểm (thang 10 của câu) thì gắn cờ |
| QT12 | Chấm từ khóa tách vế ở `. ! ? ;` và "but / whereas / however", không tách ở "and" |
| QT13 | Bài tự luận phải viết tiếng Anh (nhắc tại ô trả lời, xác nhận khi nộp) |
| 20/11 | **Độ ổn định + cờ xem lại**: chạy pipeline thêm 2 lần trên test (cùng cấu hình B10) — 92,6% ý giữ nguyên qua 3 lần, độ chính xác 93,5–98,1% (TB 95,3%), kappa giữa các lần 0,87–0,93. Thêm cờ `ai_stricter` (ý AI Không đạt mà từ khóa Đạt) vào khối 6 + trang Kết Quả - AI Chấm: cờ bắt 62% bài AI sai (trước 1/6). Cờ B (chấm 2 lần) bắt 62% với 16% bài phải xem nhưng gấp đôi lượt Gemini → để Hướng phát triển; cờ C (câu trích) bỏ. Báo cáo mục 7.3 mới | Tuấn duyệt; commit sau mục 5 |
| 19/11 | **Sửa báo cáo theo review**: gọi lại riêng bài R0011 (lỗi 503) → Model A khớp 95,4%, RMSE 1,86, A tốt hơn từ khóa có ý nghĩa; thêm kappa AI–Hòa / AI–Tâm (pipeline 0,85 / 0,81, Hòa–Tâm 0,77); kiểm cờ: chỉ 2/6 ý AI sai bị gắn cờ, 3/6 ý đổi kết quả khi chạy lại; ghi rõ rò rỉ v2.2 → v3, người phân xử là người làm AI, nguồn bản nháp | Tuấn duyệt lại; người giữ Word cập nhật BA / SRS |
| 18/11 | **B10 xong** trên test: pipeline khớp người 94,4% (từ khóa 80,6%), QWK 0,95, 0 bài sai bị chấm cao; RAG / ví dụ nhỉnh hơn nhưng chưa có ý nghĩa thống kê → giữ cấu hình A. Điền số liệu vào báo cáo (B13) | B13: Tuấn duyệt văn phong báo cáo |
| 18/11 | **B4 xong**: Hòa + Tâm chấm 60 bài, trùng 90,7%, kappa 0,81; Tuấn phân xử 19 ý → `gold.csv`. Hướng dẫn chấm v2.2 (3 quy ước mới). **Prompt chấm lên `grade-en-v3`** cho khớp v2.2: quy tắc 7 (không chép / diễn đạt lại đề), 11 (sai ngay trong phần nói về ý), 12 (ý nhiều phần phải đủ) — chỉ quy tắc chung, không quy ước riêng câu test; thử Gemini trên câu dev: nửa ý dynamic typing → none, bài diễn đạt lại đề → none cả 3 ý | B10: chạy đo trên test (keyword, gemini, gemini-fs, pipeline) |
| 17/11 | **Chạy thật Gemini (B7 + B11)**: 2 lượt, 0 lỗi JSON, trang kết quả hiện đủ lý do / câu trích; sửa **gọi lại khi Gemini 503** (`5a41ec9`). **Trang "Bài cần xem lại"** cho admin (human-in-the-loop, `67baa6b`). **Ví dụ chấm mẫu (few-shot)** vào prompt: 9 ví dụ chỉ từ câu **dev**, bật bằng `REVIEW_GRADING_FEWSHOT` (mặc định tắt), phiên bản `grade-en-v2+fs`; thử 1 bài CS-TL-05 chỉ nêu hiện tượng: v2 cho ý 2 Đạt (sai), v2+fs cho Không đạt (đúng), là câu dev nên chưa kết luận | 20/11 chạy A/B `gemini` vs `gemini-fs` trên **test**; tốt hơn thì bật cờ |
| 16/11 | **B13 phần chữ xong**: chương báo cáo AI chấm bài (chờ số liệu B10) + sửa phần ôn tập trong BA, SRS, api-endpoints (.md) cho khớp code (15 câu, tự luận AI chấm, 6/10) | Tuấn duyệt báo cáo; 19/11 màn duyệt câu AI; 20/11 chấm chung |
| 16/11 | **B12 xong** trên Docker + Gemini thật: nộp có điểm 1,9 s (10,2 s lần đầu), chấm đúng / sai / trống hợp lý, Gemini lỗi → từ khóa; phát hiện thiếu mô hình embedding trong container + khởi động nguội chậm | Đã sửa cả 2 phát hiện (mô hình embedding trong volume; nạp sẵn NLTK → lần nộp đầu 2,1 s); tiếp B13 |
| 16/11 | GĐ7 **7.5c + 7.5a xong**; **Dockerfile tải dữ liệu NLTK** (build lại image, chạy thử trong container); **B11 code xong** (lý do, nhận xét, tô sáng câu trích, nhãn cách chấm, đang xem lại); 818 test xanh | Tuấn xem giao diện; khởi động lại container backend; B12 |
| 15/11 | **B9 phần code xong**: cờ REVIEW_GRADING_RAG (Model B), truy xuất đề + barem trong đúng kỹ năng, dùng chung với eval; 4 cách chấm Gemini trong eval_grading; 918 passed | Chạy A / B khi có điểm người chấm (thứ 5) |
| 15/11 | **B8 xong**: đủ 9 khối pipeline — Guard chỉ gắn cờ, Verifier kiểm câu trích, Đối chiếu chấm lại / needs_review; 907 passed | Đo tỉ lệ chấm lại ở B10; chờ Hòa chấm 10 bài |
| 15/11 | **Bỏ mức ½ điểm (partial) trên toàn hệ thống** theo đề xuất của Hòa: mỗi ý Đạt (trọn điểm) / Không đạt (0). Đổi: `validator.GRADE_RESULTS`, schema Gemini + Pydantic (`Literal["full","none"]`), prompt **grade-en-v2 / grade-vi-v2**, chấm từ khóa (partial bên trong → none khi ra ngoài), `gold_sheets` / `eval_grading`, RATER_GUIDELINE 2.0, HUONG_DAN_CHAM_HOA, phiếu `rater_hoa_2muc.xlsx`. Bài chấm trước 15/11 trong lịch sử vẫn hiển thị được partial. 896 passed | Gửi Hòa phiếu 2 mức |
| 15/11 | **B7 xong** (prompt grade-en-v1, responseSchema + Pydantic, thử lại khi sai khung, reason / feedback) — chưa chạy Gemini thật | Tuấn viết 40 bài nhóm; chạy thử Gemini trên dev |
| 15/11 | **Bài thật chỉ thu được 4 người (20 bài)**, hết người làm → chấp nhận bộ bài nhỏ: 20 bài thật + khoảng 40 bài nhóm viết (Tuấn, Khôi; 4 loại mỗi câu) + bài AI sinh chỉ ở dev (≤ 30%). Báo cáo ghi rõ hạn chế: mẫu nhỏ, khoảng tin cậy rộng. Mở rộng thu bài là **hướng phát triển** |
| 14/11 | **Người chấm bộ bài chuẩn: Hòa và Tâm** (hai người chấm độc lập, không phải người làm AI). Bất đồng → Tuấn hoặc thầy quyết |
| 14/11 | GĐ7 trước 25/11 chỉ làm **7.5a + 7.5c**; lùi 7.4, 7.5b, 7.5d, 7.6, 7.8; 7.7 gộp vào B13, 7.9 gộp vào B8 (chi tiết `Review-Assessment.md`) |

### 1.3 Mặc định (Claude đề xuất, đổi được nếu nhóm không đồng ý)
| # | Nội dung | Mặc định |
|---|---|---|
| D3 | LLM chính | Gemini (`REVIEW_LLM_MODEL`, hiện `gemini-3.5-flash-lite`); Qwen cục bộ không làm đợt này |
| D4 | Kho vector | Giữ JSON + cosine bằng Python (A7); pgvector để sau |
| D5 | Vị trí code | Module trong backend `app/ai/review/` (không tách dịch vụ riêng) |
| D6 | Đầu ra thêm | `reason` từng ý, `feedback` chung, `flags` — lưu trong cột JSON, không cần migration. **Không** dùng độ tin cậy do LLM tự chấm để quyết định |
| D7 | Mức chấm mỗi ý | ~~3 mức full / partial / none~~ → **15/11 (Hòa đề xuất, Tuấn chốt): 2 mức — Đạt `full` = trọn điểm ý, Không đạt `none` = 0**; dài dòng không trúng trọng tâm = 0. Áp dụng cả hệ thống |
| D8 | "Cần xem xét" | Cờ `needs_review` trong `trace`, không thêm trạng thái mới |
| D10 | Bài cần xem xét có tính Đạt không | Tạm tính, ghi "đang xem lại" |

### 1.4 Ngoài phạm vi đợt này
Fine-tune · nạp PDF / DOCX · pgvector · rerank · so sánh Qwen cục bộ · trang admin xem bài cần xem xét · chấm code chạy được · nhiều môn học.

### 1.5 Còn chờ
- [x] Tải **Session02 `demo1–3.py`** — 14/11, chép vào `BA-nhom/pipeline/Session02/`.
- [x] Chốt cách xử lý **GĐ7** bị trùng lịch — 14/11 (mục 1.2).
- [x] Người chấm bộ bài chuẩn — 14/11: **Hòa, Tâm** (mục 1.2). Cần báo hai bạn trước 15/11, mỗi bạn dành khoảng 3–4 giờ.

---

## 2. Thiết kế pipeline chấm tự luận (kiểu n8n, viết bằng Python)

```
[0] Nhận bài nộp
 → [1] Tiền xử lý NLP (theo Session 01): chuẩn hóa, tách từ, bỏ stopwords, lemmatize
 → [2] Guard: bài trống → 0 điểm · không phải tiếng Anh / quá dài / chèn lệnh → gắn cờ
 → [3] Ngữ cảnh: barem + đáp án mẫu (theo question_id) + đoạn tri thức (RAG, chỉ Model B)
 → [4] Chấm bằng LLM: JSON theo schema, kiểm bằng Pydantic, sai → thử lại 1 lần
 → [5] Verifier: câu trích có thật (so sau khối 1)? đủ số ý? → ý không có bằng chứng = none
 → [6] Đối chiếu: chấm từ khóa tiếng Anh → lệch > 3 → chấm lại 1 lần → vẫn lệch → needs_review
 → [7] Tổng hợp: code tính điểm, tổng, nhận xét
 → [8] Lưu kết quả + trace từng khối {name, ms, status, output}
```

- Mỗi khối là một hàm `run(ctx) -> ctx`; một **runner** gọi lần lượt, xử lý nhánh (6 → 4), thử lại, ghi nhật ký.
- Vị trí: `backend/app/ai/review/pipeline/`. Code đã có (`real_ai.py`, `review_grader.py`, `review_rag_service.py`) được bọc thành khối, không viết lại.
- **Model A** = pipeline không có đoạn tri thức ở khối 3. **Model B** = có. Chỉ khác một biến số (cờ `REVIEW_GRADING_RAG`).

## 3. Đo độ chính xác (yêu cầu của thầy)

| Chỉ số | Cách tính | Mục tiêu ban đầu (cần kiểm chứng, không phải cam kết) |
|---|---|---|
| MAE | Trung bình \|AI − người chấm\| trên thang 10 | ≤ 1,0 |
| RMSE | Phạt lỗi lớn | ≤ 1,5 |
| QWK | `cohen_kappa_score(..., weights="quadratic")` trên điểm làm tròn | ≥ 0,70 |
| Khớp từng ý | Tỉ lệ ý cùng kết quả với người chấm | ≥ 80% |
| Lệch ≤ 1 điểm | Tỉ lệ bài | ≥ 85% |
| Bài sai bị chấm cao | Người chấm ≤ 4 nhưng AI ≥ 7 | 0 |
| Độ ổn định | Chấm 2 lần ra cùng kết quả mọi ý | ≥ 90% |
| Độ trễ | p95 | ≤ 20 giây (`REVIEW_GRADING_TIMEOUT`) |

- So A với B bằng **paired bootstrap** (1.000 lần, khoảng tin cậy 95%); chỉ kết luận "B tốt hơn" khi khoảng tin cậy không chứa 0.
- Mức đồng thuận giữa **hai người chấm** (kappa) là trần tham chiếu — AI khó vượt.
- Chống rò rỉ: bộ bài chia **dev / test theo câu hỏi**; chỉ chỉnh prompt trên dev; test chạy **một lần** cho bản cuối.

---

## 4. Các bước

- [x] **B0 Chuẩn bị** — dự kiến 14/11 · thực tế 14/11 👤
  - [x] Tải Session02 `demo1–3.py`, đặt vào `BA-nhom/pipeline/` — 14/11 🤖 chép + đối chiếu (bảng mục 1.1).
  - [x] Chốt GĐ7 và người chấm (mục 1.5) — 14/11.
- [x] **B1 Khối 1 — tiền xử lý NLP** — dự kiến 14/11 · thực tế 14/11 👤 (🤖 review + viết theo yêu cầu Tuấn)
  - ✅ 14/11: `text_pipeline.py` + `tests/test_text_pipeline.py` **22 test**; toàn bộ **713 passed**. Đã tải đủ 4 gói dữ liệu NLTK trên máy (thiếu `wordnet` → tải lại). Khi gộp `review/featrure`: thêm `RUN python -m nltk.downloader punkt_tab stopwords wordnet averaged_perceptron_tagger_eng` vào `backend/Dockerfile`.
  - Phát hiện khi chạy thử (khác demo): `can't` → `ca` + `n't`, `cannot` → `can` + `not`; stopwords NLTK chứa `not / no / nor`; WordNet không biết `tuples`; bộ gán từ loại coi `looping` là danh từ → đã xử lý cả 4 (docstring đầu file).
  - Thêm `nltk` vào `backend/requirements.txt`; tải dữ liệu `punkt_tab`, `stopwords`, `wordnet`, `averaged_perceptron_tagger_eng` **một lần** (máy: lệnh tay; Docker: một dòng `RUN` trong Dockerfile). Không tải lúc chạy server, không tắt kiểm tra SSL như demo.
  - `backend/app/ai/review/text_pipeline.py`: `normalize`, `tokenize`, `remove_stopwords` (giữ từ phủ định), `lemmatize` (theo POS, không cố định `pos='v'`), `preprocess`.
  - ✅ `tests/test_text_pipeline.py`: "Lists CAN be changed!" → có `list`, `change`; "tuples cannot be modified" còn từ phủ định; chuỗi rỗng → `[]`; loops / looping / looped → `loop`. Toàn bộ test xanh.
- [x] **B2 Ngân hàng câu hỏi tiếng Anh** — dự kiến 14–15/11 · thực tế 14–15/11 (🤖 dịch + review 15/11 · 👤 Tuấn nạp DB) · ✅ kiểm DB 16/11: 100 câu tiếng Anh đang bật, 0 câu tiếng Việt còn bật, 15 đoạn tri thức đều có vector
  - 🤖 Review bản dịch 14/11: 70 câu trắc nghiệm, đáp án đúng (tính lại các câu đọc code); 30 câu tự luận. Sửa: tên biến một chữ `a`, `i` bị khối 1 bỏ như stopword ("a = 7" → "= 7", nên bài sai "b = 7" vẫn được ½ ý ở VAR-TL-06). Nay giữ khi đứng cạnh ký hiệu hoặc trước is/becomes/equals. Dấu phẩy trong code ("a, b = b, a") không tách vế. Thêm "again" vào từ giữ lại. Bỏ 3 từ khóa vô hiệu hoặc quá chung (`other`, `_2nums`, `example` ở PY-TL-04). Thêm 8 test.
  - ✅ 14/11 🤖: `data/review/course_312_en.json` — 100 câu (70 TN + 30 TL) + 15 đoạn, mã QT9 (`PY-TN-01`, `PY-K01`). Kiểm tự động: validator OK; loại / mức / đáp án / đoạn / điểm từng ý khớp bản tiếng Việt; **đáp án mẫu 30/30 câu tự luận đạt 10/10** với bộ chấm tiếng Anh; chép đề = 0.
  - ✅ `seed_review.py --retire <file cũ>`: nạp bản mới + tắt câu tiếng Việt (giữ lịch sử) + xóa đoạn tiếng Việt, **cùng một giao dịch**. `tests/test_seed_review_en.py` 4 test.
  - ✅ `GENERATE_SYSTEM_PROMPT` + `build_generation_prompt` sang tiếng Anh, thêm quy ước viết từ khóa (sửa 2 test kiểm câu chữ prompt). `data/review/README.md` cập nhật quy ước.
  - Khối 1 sửa thêm khi dịch: giữ `//`, số thập phân `3.5`, ghép `!=` / `**` / `<=`, tách `n+1` / `total+=i` viết liền. Toàn bộ **815 passed**.
  - 👤 Tuấn duyệt: ưu tiên **30 câu tự luận** (đề, barem, từ khóa, đáp án mẫu) rồi 70 câu trắc nghiệm.
  - 👤 Nạp DB thật (sau khi duyệt): `python -m scripts.seed_review --file data/review/course_312_en.json --retire data/review/course_312.json` → `python -m scripts.build_embeddings` → bắt đầu ôn khóa 312 thấy 15 câu tiếng Anh.
  - `backend/data/review/course_312_en.json`: 100 câu (70 TN + 30 TL) + 15 đoạn tri thức, cùng định dạng `course_312.json`; barem và từ khóa tiếng Anh.
  - Nạp bằng **mã câu mới**, tắt câu tiếng Việt (không sửa đè — đúng quy tắc phiên bản); chạy lại `scripts/build_embeddings.py`.
  - Đổi `GENERATE_SYSTEM_PROMPT` (đang yêu cầu "Viết bằng tiếng Việt") sang tiếng Anh.
  - ✅ Validator không báo lỗi; đề ôn tập khóa 312 ra 15 câu tiếng Anh.
- [x] **B3 Bộ chấm từ khóa tiếng Anh** — dự kiến 15/11 · thực tế 14/11 🤖 (Tuấn chọn: file mới + tự chọn theo ngôn ngữ)
  - ✅ `keyword_grader_en.py` (cùng luật bộ tiếng Việt: full / partial / none, phủ định, tách vế QT12, chặn mượn vế, chép đề, liệt kê, bài ngắn) — khớp trên **dãy từ đã lemmatize** của khối 1, từ khóa nhiều từ khớp khi liền nhau. `keyword_grading.py` chọn bộ chấm theo ngôn ngữ (barem / đề có dấu tiếng Việt → bộ cũ); `mock_ai.py`, `review_grader.py` gọi qua đây.
  - ✅ `tests/test_keyword_grader_en.py` **21 test**; toàn bộ **739 passed**. Kiểm ngược: bỏ phủ định → 3 test trượt; bỏ tách vế "but" → 1 trượt; bỏ chặn mượn vế → 1 trượt.
  - Sửa B1 khi làm B3: stopwords NLTK chứa **từ khóa Python** (`for, while, if, in, and, or`) → "while loop" chỉ còn "loop" → giữ nguyên từ khóa Python (`keyword.kwlist`), không lemmatize. Sửa lỗi đếm mật độ liệt kê (ký hiệu `[ ]` bị tính vào tử số).
  - **Quy ước viết từ khóa tiếng Anh cho B2**: viết dạng tự nhiên (bộ chấm tự lemmatize cả hai phía); từ khóa nhiều từ phải là cụm **liền nhau sau khi bỏ stopwords** (vd "number of loops" → number loop); ý phủ định viết kèm "not" ("not change"); ký hiệu viết cả hai dạng "[ ]" và "[]".
  - Dựa trên khối 1; giữ luật QT12 (tách vế, chặn bài chỉ liệt kê từ khóa, bỏ câu chép đề).
  - ✅ Test: diễn đạt khác dạng từ vẫn khớp; phủ định ("cannot change") không bị tính là "change"; bài chỉ liệt kê từ khóa không được đủ điểm.
  - **26/11 (Tuấn review đề 494)**: thêm "without" vào `NEGATIONS` ("without a broker" không còn được tính là ý "qua broker"); giữ "once" khi bỏ stopwords ("at most once" → `most once`, trước đây rút còn `most`). Chấm lại 298 bài (bài mẫu trong DB + bài học viên đã nộp + bài mẫu các file đề) trước/sau: **0 bài đổi kết quả**.
  - **Giới hạn đã biết (chờ sửa (c), làm riêng)**: khi một vế câu có chủ thể của hai ý, bộ chấm không biết từ khóa thuộc chủ thể nào — "Sensor data uses QoS 1 and fan commands use QoS 0" vẫn được cả hai ý. Có dấu phẩy / chấm / "but" thì chấm đúng (luật chặn mượn vế). Khi Gemini chạy, khối 6 đối chiếu + cờ `needs_review` / `ai_stricter` bắt được; chỉ lọt khi Gemini lỗi và phải chấm dự phòng bằng từ khóa. Hướng (c) đã bàn: gán từ khóa cho chủ thể gần nhất phía trước — cần thử kỹ với câu bị động trước khi làm.
  - **26/11 — động từ "-s"**: khối 1 gán từ loại SAU khi bỏ stopwords nên "A sensor detects motion" → `detects` bị coi là danh từ, không về `detect`; "uses" có lúc về `us`. Sửa trong `lemmatize`: từ đuôi "-s" bị gán danh từ / tính từ, WordNet không có danh từ đó → `wordnet.morphy(word, VERB)` (xử lý cả "-es", "-ies"); thêm `VERB_S_FORMS` (`uses` → use, `senses` → sense). Từ vừa danh từ vừa động từ ("links", "stores") vẫn đi nhánh danh từ như cũ. Đã thử gán từ loại trên câu đầy đủ (trước khi bỏ stopwords): sai nhiều hơn (users, cameras, categories) → giữ thứ tự. Chấm lại 319 bài trước/sau: **0 bài đổi, 0 bài giảm**; đề 494 bỏ được dạng "-s" thêm tay (bài đúng "detects", "delivers" 7 → 10). **Giới hạn đã biết**: "analyses" vẫn về `analysis` (danh từ số nhiều hợp lệ) → barem cần ghi thêm "analyses" khi muốn nhận động từ "analyse".
  - **27/11 — prompt `grade-en-v4`**: câu đầu bỏ *"about basic Python"* (ngân hàng có thêm khóa IoT 494), các quy tắc giữ nguyên. **Thí nghiệm** (chốt ngưỡng TRƯỚC khi chạy: độ khớp từng ý giảm quá 2 điểm % → giữ v3): chạy v3 và v4 trong CÙNG một phiên, method `gemini` (khối 4), 60 bài / 204 ý bộ bài chuẩn, `gemini-3.5-flash-lite`; bài lỗi 429 chấm lại cho đủ 204/204. Kết quả v3 → v4: độ khớp ý 93,1% → 91,7% (−1,5 điểm, bootstrap CI95 [−4,5; +1,0] — không kết luận được); MAE 0,817 → 0,883; QWK 0,872 → 0,874; within_1 80% = 80%; bài sai bị chấm cao 2 = 2; mean_bias +0,55 → +0,72. Độ ổn định giữa hai lượt 96,6% (Gemini tự dao động ~3,4% ý) → chênh lệch nằm trong nhiễu. **Đạt ngưỡng → dùng v4.** **Chỉ số theo dõi (Tuấn 27/11): `mean_bias`** — v4 nghiêng về phía rộng tay hơn (+0,55 → +0,72); học viên sai được điểm cao nguy hiểm hơn học viên đúng bị chấm thấp. Đo lại khi có thêm bài học viên thật; **vượt khoảng +0,8 → xem lại prompt**. Không chỉnh prompt theo kết quả trên phần test (chống rò rỉ). Đề 494 đo lại với v4 (`scripts.bank.probe_gemini`, 36 + 2 lần gọi): 0 lệch.
  - **27/11 — số đi kèm đơn vị đo**: `tokenize` chuẩn hóa CHỈ số đi kèm đơn vị (V, mV, kWh, Hz, ms, °C → degc, %…; đơn vị dài khớp trước, phải hết từ, đơn vị một chữ s/m/h/w chỉ khi cách số và đổi thành sec/metre/hour/watt vì "s", "m" là stopword; % là đơn vị chỉ khi sau nó không có số / tên biến): bỏ số 0 thừa ("17.0 kWh" → 17), phẩy thập phân 1–2 chữ số ("0,1 °C" → 0.1), tách số dính đơn vị ("17kWh"). Số đứng một mình / trong code giữ nguyên ("3.0", "3.0%2", "2s complement", "0x1A", "1e5"). Sửa lỗi mất số quanh dấu phẩy ("range(1,5)" trước đây mất cả hai số). "1,000" / "4,096" giữ một token, keyword_grader_en không tách vế ở dấu phẩy này. So trước/sau: 376 bài (bài mẫu DB + bài đã nộp + 4 file đề) 0 đổi điểm, chỉ 2 bài đổi token ("100,000" được giữ); bộ bài chuẩn 60 bài chấm từ khóa: 204/204 ý không đổi, 0 bài đổi token. Quy ước barem: số hàng nghìn không dấu phẩy, số kết quả không số 0 thừa (check.py báo).
  - **Quy ước viết barem (26/11)**: từ khóa chính là phần giải thích / cách xử lý, không phải tên khái niệm; tên khái niệm đặt vào `sub_keywords` khi cần gắn tính chất vào đúng đối tượng (QoS 0/1, lớp, CON/NON…); đề ghi rõ đối tượng, không cho "chọn tự do" (barem cố định không chấm được "N trong M"); mỗi câu tự luận có bộ bài thử cố định (đúng nhưng viết khác, chỉ liệt kê tên, đảo vai trò, "without").
- [x] **B4 Bộ bài chuẩn (gold set)** — dự kiến 15–17/11 · **xong 18/11**: 60 bài (20 thật + 40 bổ sung) / 204 ý, **Hòa + Tâm chấm độc lập cả 60 bài** — trùng nhãn **90,7%**, **kappa 0,812**, QWK tổng điểm 0,867 (dev 93% / test 89%; bài thật 87% / bổ sung 93%). 19 ý lệch → Tuấn phân xử (16 theo hướng dẫn, 3 chốt quy ước mới) → `private/gold.csv` (109 full / 95 none; dev 96 ý, test 108 ý). Hướng dẫn chấm lên **v2.2** (quy tắc 7 chép đề, 9 sai trong chính ý, 12 ý nhiều phần; 3 quy ước 4b)
  - **17/11 chốt cách chia (phương án A):** mỗi bài 2 người chấm độc lập để tính kappa. **Hòa** chấm nốt BÀI 31–60 trên phiếu của mình; **Tâm** chấm cả 60 bài trên phiếu riêng (`rater_tam_2muc.xlsx`, thứ tự xáo khác, tạo bằng `gold_sheets sheets --rater tam`). **Khôi và Tuấn không chấm**, vì đã viết 40 bài bổ sung và biết trước loại bài. Bất đồng giữa Hòa và Tâm → Tuấn hoặc thầy quyết (cột `final` trong `disagreements.csv`)
  - 15/11: Form đóng với **4 người thật (20 bài, `private/answers.csv`)** — dưới chỉ tiêu ≥ 40. Bù bằng `private/team_answers.csv` (40 dòng mẫu: 10 câu × 4 loại — đúng diễn đạt khác / một phần / sai đảo nghĩa / ngắn sai chính tả) do Tuấn + Khôi viết; cột `kind` không đưa vào phiếu chấm.
  - 🤖 14/11 xong phần chuẩn bị: `docs/ai-grading/RATER_GUIDELINE.md` (bản 1.0); `docs/ai-grading/DATA_COLLECTION.md` (nội dung 2 Form, loại bài nhóm cần viết, lịch, quyền riêng tư); `backend/data/ai-grading/split.json` (10 câu: 5 dev + 5 test, chia theo câu hỏi); `backend/scripts/gold_sheets.py` (`collect`, `sheets`, `merge` + kappa / QWK giữa hai người chấm; chặn bài AI ở test); `.gitignore` cho `backend/data/ai-grading/private/`; 9 test. 👤 Còn: tạo Form, thu bài, vòng hiệu chỉnh, Hòa và Tâm chấm.
  - `docs/ai-grading/RATER_GUIDELINE.md` (tiếng Anh, ví dụ full / partial / none cho từng loại ý).
  - Google Form thu bài thật (có câu đồng ý dùng cho nghiên cứu, không hỏi tên); nhóm viết thêm các loại bài còn thiếu; bài do AI sinh ≤ 30% và **không vào test**.
  - Vòng hiệu chỉnh 20 bài (Hòa + Tâm cùng chấm, so sánh, sửa hướng dẫn) → hai bạn chấm độc lập phần còn lại, **không xem điểm của nhau và không xem điểm AI** → bất đồng do Tuấn hoặc thầy quyết.
  - ✅ ≥ 120 bài (≥ 40 bài thật), có `gold.csv`, kappa giữa hai người, chia dev / test theo câu hỏi. Dữ liệu thật **không commit** lên repo.
- [x] **B5 Script đánh giá** — dự kiến 15–16/11 · thực tế 14/11 🤖 (chờ gold.csv thật để chạy số liệu)
  - ✅ `backend/scripts/eval_grading.py` có 3 lệnh. `run`: chấm, ghi `results/<run_id>.csv` (method, model, prompt_version, kết quả từng ý, độ trễ, lỗi; một bài lỗi không dừng cả lần chạy). `report`: MAE, RMSE, QWK, khớp từng ý, lệch ≤ 1, bài sai bị chấm cao, độ lệch trung bình, P / R / F1 từng nhãn theo công thức demo2, ma trận nhầm, p95 độ trễ; lưu `.metrics.json`. `compare`: paired bootstrap 1.000 lần theo bài, CI 95%, độ ổn định khi cùng cách chấm. Thêm cách chấm mới (B7, B9) bằng cách đăng ký vào `METHODS`. 11 test.
  - ✅ Chạy thử cả chuỗi `gold_sheets` → `eval_grading` trên dữ liệu giả. Bộ chấm từ khóa chấm **full cả 2 ý** cho bài đảo nghĩa "break skips to the next iteration and continue exits the loop" (vì "and" không phải ranh giới vế). Đây là ví dụ cho báo cáo: chấm từ khóa không hiểu nghĩa nên cần LLM.
  - (kế hoạch gốc) `backend/scripts/eval_grading.py`: đọc `gold.csv` + kết quả một lần chạy → các chỉ số mục 3 + bootstrap + **Precision / Recall / F1 theo từng nhãn full / partial / none** (cách tính như `Session02/demo2.py`); mỗi lần chạy lưu `results/<run_id>.csv` (method, model, prompt_version, kết quả từng ý, latency, lỗi).
  - ✅ Chạy được với chấm từ khóa trên dev; số liệu tái lập được.
- [x] **B6 Runner pipeline** — dự kiến 16/11 · thực tế 14/11 🤖
  - ✅ `app/ai/review/pipeline/runner.py`: `Node(name, run, retries, on_error)`, `Step(goto, output)`, `run_pipeline`. Chạy lần lượt; `goto` để rẽ nhánh; `ctx.done` để dừng sớm. Khối raise `NodeFailed` → thử lại `retries` lần → đi nhánh `on_error`; lỗi lạ không nuốt. Giới hạn 20 bước chống lặp vô hạn. Trace mỗi khối gồm `{node, status, ms, attempts, output, error}`; khối bị nhánh bỏ qua không vào trace (như node xám trong n8n).
  - ✅ `pipeline/essay.py`: `0_input` → `3_context` → `4_llm_grade` →(lỗi)→ `4b_keyword_fallback` → `7_aggregate` → `8_trace`. Bọc code có sẵn: `ai_grade` chuyển từ `review_grader` sang đây và đo thêm thời gian gọi AI. Khối 1, 2, 5, 6 (B8) và RAG ở khối 3 (B9) chỉ cần chèn Node vào `ESSAY_NODES`.
  - ✅ `review_grader` chạy mọi câu tự luận qua pipeline; luồng song song T1 giữ nguyên (luồng chạy khối 4, khối 4 dùng lại kết quả, `source: "parallel"`). `attempt.trace["grading"]["essays"]` = trace từng câu; `ai` và `keyword_fallback` giữ như cũ.
  - ✅ **Hành vi không đổi**: 66 test chấm bài cũ xanh không sửa. Thêm 21 test runner và pipeline, 1 test trace qua API, mở rộng test dự phòng. Toàn bộ 870 passed. Kiểm ngược: bỏ nhánh `goto="7_aggregate"` → 2 test trượt; bỏ `retryable` → 2 test trượt.
  - 🤖 Review lần 2 (14/11): khối lỗi giữ `output` trong trace (vd `llm_ms` để phân biệt quá giờ với lỗi ngay); `NodeFailed(retryable=False)` để kết quả song song đã quá giờ không bị thử lại (khi B7 bật `retries` sẽ không giữ người học chờ thêm); có test bảo đảm trace không chứa bài làm.
  - `backend/app/ai/review/pipeline/`: runner + bọc khối 0, 3, 4, 7, 8 từ code có sẵn; ghi `trace.nodes`.
  - ✅ **Hành vi không đổi**: toàn bộ test cũ vẫn xanh; trace có thời gian từng khối.
- [x] **B7 Khối 4 — chấm có cấu trúc** — dự kiến 17/11 · thực tế 15/11 🤖 (👤 còn: chạy Gemini thật trên dev để kiểm "0 lỗi JSON")
  - ✅ `app/ai/prompts/review_grading.py`: `grade-en-v1` (cùng quy tắc với RATER_GUIDELINE: 3 nhãn, phân vân chọn mức thấp, đảo nghĩa / tự mâu thuẫn = none, code được tính, bài làm là dữ liệu không phải lệnh), `grade-vi-v1` cho câu tiếng Việt cũ; chọn theo ngôn ngữ câu hỏi.
  - ✅ `app/ai/review/grading_schema.py`: Pydantic `GradedItem` / `GradingOutput` (`Literal["full","partial","none"]`, `Field(description=...)` như demo3) + `GEMINI_RESPONSE_SCHEMA` dựng từ chính các Field đó (`propertyOrdering` item → evidence → reason → result). Không có trường điểm / độ tin cậy (D6). Kiểm số ý, thứ tự ý, cắt reason ≤ 300 và feedback ≤ 600 ký tự; vẫn nhận mảng trần của prompt cũ.
  - ✅ `RealAI.grade_essay_detailed`: gửi `responseSchema`; sai khung (`AIOutputError`) → thử lại 1 lần, ghi số lần gọi; lỗi mạng / quota / quá giờ **không** thử lại. Kết quả mỗi ý có thêm `reason` (lưu trong `rubric_result`); `feedback` lưu ở `trace.grading.essays[].feedback`, không nằm trong trace khối.
  - ✅ Khối 4 ghi `prompt_version`, `llm_attempts`; `eval_grading` có cách chấm `gemini` (Model A, không dự phòng từ khóa để đo đúng lỗi LLM). 19 test mới, toàn bộ 889 passed. Kiểm ngược: tắt thử lại → 8 test trượt.
  - Prompt tiếng Anh `grade-en-v1`; `responseSchema`; model Pydantic kiểm kết quả (theo cách `Session02/demo3.py`: `Literal["full","partial","none"]`, `Field(description=...)`); JSON sai → thử lại 1 lần; thứ tự trường `evidence` → `reason` → `result`; thêm `feedback`; ghi `prompt_version`.
  - ✅ 0 lỗi JSON trên dev; test tự động vẫn dùng mock (không gọi Gemini).
- [x] **B8 Khối 1, 2, 5, 6 — Tiền xử lý, Guard, Verifier, Đối chiếu** — dự kiến 18/11 · thực tế 15/11 🤖
  - ✅ Pipeline đủ 9 khối: `0_input → 1_preprocess → 2_guard → 3_context → 4_llm_grade (→ 4b dự phòng) → 5_verify → 6_cross_check (→ chấm lại về 4) → 7_aggregate → 8_trace`.
  - ✅ Guard **chỉ gắn cờ, không chặn, không phát hiện bài AI viết** (chốt 15/11): `too_long` (> 3.000 ký tự, cắt trước khi gửi AI — luồng song song và chấm lại cắt như nhau), `instruction_in_answer` (câu ra lệnh cho AI, Anh + Việt), `vietnamese` (bài tiếng Việt cho đề tiếng Anh — vẫn chấm theo nghĩa).
  - ✅ Verifier: ý `full` phải có câu trích thật trong bài (so sau chuẩn hóa hoa thường / khoảng trắng / dấu nháy / dấu câu, hoặc ≥ 80% cụm 3 từ) — không có → `none` + cờ `evidence_missing`. RealAI không tự bỏ câu trích nữa (chuyển sang Verifier).
  - ✅ Đối chiếu: điểm AI so điểm chấm từ khóa, lệch > 3 → chấm lại 1 lần (gọi trực tiếp, không dùng lại kết quả song song) → vẫn lệch → `needs_review` (điểm AI tính tạm — D10). Chấm lại lỗi → giữ kết quả lần đầu + cờ (không rơi về từ khóa). `trace.grading.needs_review` = các câu cần xem lại; mỗi câu có `flags`.
  - ✅ 11 test mới (Guard, Verifier, khớp câu trích, đối chiếu, chấm lại, chấm lại lỗi, không dùng lại kết quả song song). Toàn bộ 907 passed. Kiểm ngược: tắt đối chiếu → 4 test trượt; tắt Verifier → 2 test trượt. Viết test đã bắt được 1 lỗi thật (khối 4 thành công vẫn chạy qua khối dự phòng).
  - ⚠️ Rủi ro cần đo ở B10: chấm từ khóa yếu → có thể nhiều câu bị chấm lại (thêm lượt Gemini + độ trễ, chấm lại chạy tuần tự khi ghi điểm). Đo tỉ lệ chấm lại trên bộ bài chuẩn rồi mới quyết giữ ngưỡng 3 hay nâng lên.
- [x] **B9 Model B (RAG khi chấm)** — phần code xong 15/11 🤖 · ✅ **18/11 đo A / B trên test**: B (RAG) khớp 96,3% vs A 92,6%, bootstrap chưa có ý nghĩa (30 bài) → **giữ A**, `REVIEW_GRADING_RAG` tắt
  - ✅ Cờ `REVIEW_GRADING_RAG` (mặc định **false** = Model A; `.env.example` đã thêm). Bật → mỗi câu tự luận kèm **2 đoạn tri thức của đúng kỹ năng**: đoạn gắn với câu hỏi (nguồn soạn câu) đứng đầu, đoạn còn lại xếp theo cosine với **câu truy vấn = đề + barem — không dùng bài làm** (bài sai không kéo theo tài liệu sai, người học không điều khiển được tài liệu).
  - ✅ `review_rag_service.rank_for_grading` là hàm thuần, **server và `eval_grading` dùng chung** → Model B khi đo giống hệt khi chạy thật. Đoạn tri thức lấy ở luồng chính (cần DB) trước khi chấm song song; lỗi truy xuất → chấm như Model A.
  - ✅ Prompt thêm mục `COURSE NOTES (reference for terms only — grade against the RUBRIC)`, phiên bản `grade-en-v2+rag`; khối 3 ghi mã đoạn + cosine vào trace (không chép nội dung).
  - ✅ `eval_grading` có 4 cách chấm Gemini: `gemini` (A, chỉ khối 4), `gemini-rag` (B, chỉ khối 4), `pipeline` (A, đủ 9 khối), `pipeline-rag` (B, đủ 9 khối). Thử truy xuất trên ngân hàng thật: PY-TL-02 → PY-K03 (gắn) + PY-K01 (0,50); COND-TL-06 → COND-K02 + COND-K03 (0,19).
  - ✅ 11 test mới, toàn bộ 918 passed. Kiểm ngược: đảo thứ tự "đoạn gắn đứng đầu" → 4 test trượt.
  - 👤 Còn: khi có `gold.csv` → chạy `keyword`, `pipeline`, `pipeline-rag` → `compare` A / B (bootstrap) → phân tích bài lệch → ghi `EXPERIMENT_LOG.md` → chốt bật / tắt cờ. Ngân hàng nhỏ (15 đoạn, 3 đoạn / kỹ năng) nên RAG gần như tra cứu cố định — kết quả A ≈ B là kết quả hợp lệ, ghi trung thực.
- [x] **B10 Chạy test** — dự kiến 20/11 · **thực tế 18/11** · phần test 30 bài / 108 ý, prompt `grade-en-v3`: khớp từng ý — từ khóa 80,6% · Gemini (A) 95,4% (sau khi gọi lại bài lỗi 503; lần đầu 92,6%) · A + ví dụ 93,5% · A + RAG (B) 96,3% · **pipeline 9 khối 94,4%, QWK 0,95, 0 bài sai bị chấm cao, lệch TB +0,03**. Bootstrap: A tốt hơn từ khóa có ý nghĩa; RAG / ví dụ / pipeline so với A chưa khác biệt có ý nghĩa (30 bài) → **giữ Model A, RAG / ví dụ tắt**. Chi tiết + 6 ý AI sai: `docs/ai-grading/BAO_CAO_AI_CHAM_BAI.md` mục 7.1; kết quả thô `private/results/b10-*.csv`
  - Chạy **một lần** cho từ khóa, A, B; bootstrap; độ trễ.
  - 17/11 thêm cấu hình **A + ví dụ chấm mẫu**: `--method gemini-fs` (chỉ khối 4) / `pipeline-fs` (đủ 9 khối). So `gemini` vs `gemini-fs` bằng `compare` (bootstrap). Ví dụ chỉ lấy từ câu dev (`FEWSHOT_SOURCE_CODES`, có test chống rò rỉ sang câu test).
  - ✅ Bảng kết quả + nhật ký chạy.
- [x] **B11 Giao diện kết quả** — code xong 16/11 🤖 · ✅ 17/11 xem trên trình duyệt với lượt chấm Gemini thật (lượt 64): lý do từng ý, câu trích tô sáng, nhận xét, nhãn "Đang xem lại" / "Giáo viên đã xem lại"
  - ✅ Backend: API kết quả (`result_view`, `/me/review-history/{id}`) trả thêm `rubric[].reason`, và với câu tự luận có bài làm: `graded_by` (`ai` | `keyword` — `AI_MODE=mock` hoặc Gemini lỗi đều là `keyword`, không ghi "Chấm bởi AI" sai sự thật), `needs_review`, `feedback`. Cờ nội bộ (chèn lệnh, quá dài…) KHÔNG trả cho người học. Lượt chấm trước B6 vẫn xem được (giá trị mặc định). 7 test; kiểm ngược: ghi mock là "ai" → test trượt.
  - ✅ Frontend `ResultQuestion`: câu trích **tô sáng ngay trong bài làm**, đánh số theo ý (`highlightSegments` — hàm thuần trong `reviewFormat.js`, kiểm bằng Node: ghép lại luôn ra đúng bài làm gốc); khung **Nhận xét**; cột **Lý do · bằng chứng**; nhãn **Chấm bởi AI / Chấm tự động theo từ khóa**; **Đang xem lại** + ghi chú điểm tạm tính; "Chưa có" → "Chưa đạt" (2 mức). `vite build` đạt.
  - ✅ Kèm theo (chuẩn bị B12): `backend/Dockerfile` tải dữ liệu NLTK (punkt_tab, stopwords, wordnet, averaged_perceptron_tagger_eng) vào image — đã build lại và chạy thử khối 1 + chấm từ khóa trong container. 818 test xanh.
- [x] **B12 Kiểm thử toàn luồng** — dự kiến 22/11 · thực tế 16/11 🤖 (Docker, `AI_MODE=real`, Gemini thật)
  - Script `backend/scripts/b12_e2e_review.py`: đóng vai học viên gọi đúng API trình duyệt gọi (đăng ký → tham gia khóa 312 → ôn tập → nộp → đọc kết quả).
  - ✅ Đề 15 câu tiếng Anh, sinh 0,1 s (ngân hàng đủ câu → không gọi Gemini). Nộp bài **10,2 s lần đầu sau khởi động** / **1,9 s khi đã ấm** (mục tiêu ≤ 20 s).
  - ✅ Chấm Gemini: bài đúng 2/2 ý full, câu trích có thật trong bài, có lý do + nhận xét; bài lạc đề 0 điểm kèm lý do; bài trống dừng ở khối 0. Trace đủ 9 khối, `grade-en-v2`, chấm song song (~2 s / câu), đối chiếu lệch 0.
  - ✅ Gemini lỗi (giả lập model không tồn tại, chạy trong container) → `4_llm_grade` lỗi → `4b_keyword_fallback` → vẫn 10/10 (cần dữ liệu NLTK — Dockerfile 16/11).
  - ✅ Frontend Docker :8088 chuyển `/api` sang backend (200).
  - ✅ Phát hiện 1 (đã sửa 16/11): trong container **không có mô hình embedding RAG** (volume `edumentor_hf_cache` chưa có `paraphrase-multilingual-MiniLM-L12-v2`, code chỉ đọc bản đã tải — `local_files_only`) → RAG xếp đoạn theo thứ tự tạo. **Đã tải mô hình vào volume** (một lần, giữ qua các lần build): log "RAG: đã nạp sẵn mô hình embedding"; sinh đề và Model B xếp theo cosine (vd PY-K03 0,65 cho câu list / tuple). Máy mới / xóa volume → tải lại: `docker exec edumentor_backend python -c "from sentence_transformers import SentenceTransformer as S; S('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"`.
  - ✅ Phát hiện 2 (đã sửa 16/11): lần nộp đầu sau khởi động chậm (~8 s) vì nạp dữ liệu NLTK lần đầu → `review_rag_service.warm_up_nlp()` nạp sẵn trong luồng `warm_up_in_background` (lỗi chỉ ghi log). Đo lại trên Docker: lần nộp đầu sau khởi động **10,2 s → 2,1 s**. 1 test.
  - Ghi chú: mỗi lần chạy script tạo 1 học viên thử `b12.<giờ>@example.com` trong DB dev (đã có 2: lượt 58, 59).
- [~] **B13 Báo cáo và tài liệu** — dự kiến 23–24/11 · phần không cần số liệu xong 16/11 🤖 · 👤 còn: điền số liệu B10 (chỗ ⟨B10⟩), Tuấn duyệt văn phong, người giữ bản Word cập nhật BA / SRS .docx theo bản .md
  - ✅ Chương báo cáo `docs/ai-grading/BAO_CAO_AI_CHAM_BAI.md`: bài toán, phạm vi / dữ liệu, kiến trúc pipeline 9 khối, chi tiết khối (NLP, LLM có cấu trúc, RAG A / B, chấm từ khóa), vận hành + kiểm thử (868 test, kết quả B12), phương pháp đánh giá (gold set, quy trình chấm mù, chỉ số), kết quả (bảng chờ B10 + quan sát định tính trên bài thật), hạn chế, hướng phát triển (fine-tune: khi nào, dữ liệu, QLoRA, cách chứng minh), phụ lục vị trí mã nguồn.
  - ✅ Sửa phần ôn tập (module 09) trong 3 file .md cho khớp code — trước ghi "20 câu trắc nghiệm, chấm theo đáp án, đạt 60%": **BA** (mục tiêu, UC-09, FR-24–28, FR-54, BR-28, BR-29, kiến trúc, 8.6, 8.7, mô hình dữ liệu, quy trình nộp bài), **SRS** (mục tiêu, Review Engine, FR-11, FR-12, FR-17, luồng, dữ liệu), **api-endpoints** §10 (thêm `PATCH .../answers`, trace admin, 10 API quản trị `/api/admin/review`, trường kết quả B11, quy trình 15 câu, 6/10). Bản .docx / .pdf trong `docs/Features` chưa đổi.
  - ✅ 19/11: BA / SRS (.md) thêm hồ sơ một cột (ngày sinh, giới tính, SĐT), giới hạn đăng nhập sai (FR-02, NFR-04, AC-01, 429), trang Kết Quả - AI Chấm (UC-22, FR-57, SRS FR-22, 2 API flags), kết quả B10 (8.7). Danh sách thay đổi cho bản Word: `docs/Thay-doi-BA-SRS-19-11.md`
- [ ] **B14 Nộp** — 25/11

**Thứ tự và phụ thuộc:** B1 → B3 · B2 → B4 → B5 · B1 + B6 → B7 → B8 → B9 (cần B4, B5) → B10 → B11 → B12 → B13. B2, B4, B5 làm song song với B1, B3, B6.

---

## 5. Nhật ký

| Ngày | Đã làm | Vướng mắc |
|---|---|---|
| 27/11 | Chuẩn hóa số đi kèm đơn vị trong khối 1 + sửa lỗi mất số quanh dấu phẩy; 376 bài cũ + 60 bài chuẩn: 0 đổi điểm | — |
| 27/11 | Prompt chấm `grade-en-v4` (bỏ "basic Python" ở câu đầu). Đo v3 vs v4 cùng phiên trên 60 bài: độ khớp ý 93,1% → 91,7% (ngưỡng −2 điểm) → đạt, dùng v4; đề 494 với v4: 0 lệch. Bộ công cụ `scripts/bank` | — |
| 26/11 | Tuấn review đề 494 đợt 1: barem tự luận chỉ dò tên khái niệm, thiếu đồng nghĩa, ép đáp án khi đề cho chọn tự do. Soạn lại 18 câu tự luận + bài thử cố định; bộ chấm thêm "without" (phủ định) và giữ "once"; 298 bài cũ không đổi kết quả | (c) gán từ khóa theo chủ thể gần nhất — để sau |
| 26/11 (tối) | Sửa lỗi động từ "-s" trong khối 1 (detects → detect, uses → use); 319 bài cũ: 0 đổi, 0 giảm; đề 494 bỏ dạng "-s" thêm tay | "analyses" → analysis (giới hạn đã biết) |
| 20/11 (tối) | Diễn tập demo qua API (Gemini thật, 9,8 s); kịch bản demo + phiếu bài mẫu riêng. Ngân hàng khóa 1855, 743 (không dùng cho đánh giá); script kiểm tra ngân hàng bắt từ khóa bị bộ chấm rút còn 1 chữ / rỗng. Báo cáo: mục 2 (phạm vi), 8 (độ phủ đề), 9 (3 hướng mở rộng) | Lần thử khóa 743 chấm 27 s → qua màn "Đang chấm"; hôm demo có thể chậm |
| 13/11 | Khảo sát AI Grading; chốt D1 tiếng Anh, D2 fine-tune để sau, D12 hạn 25/11 | — |
| 14/11 | Thầy đồng ý phiên bản 1 LLM + RAG + Prompt; yêu cầu thêm độ chính xác + pipeline kiểu n8n. Gom tài liệu pipeline Session 01. Lập file kế hoạch này | GĐ7 trùng lịch |
| 14/11 | **B6 xong**: runner pipeline kiểu n8n + pipeline chấm một câu; trace từng khối lưu vào attempt; hành vi không đổi; 865 passed | Tiếp B7 (chấm có cấu trúc) |
| 14/11 | **B5 xong**: `eval_grading.py` (run / report / compare, P/R/F1 theo demo2, bootstrap), 11 test; chạy thử cả chuỗi trên dữ liệu giả | Chờ gold.csv thật; tiếp B6 |
| 14/11 | **Review B2** (sửa khối 1: tên biến một chữ, dấu phẩy trong code; bỏ 3 từ khóa) + **B4 phần chuẩn bị** (hướng dẫn chấm, quy trình Form, split dev / test, script `gold_sheets`) | Tuấn tạo Form, báo Hòa, Tâm; nạp DB tiếng Anh |
| 14/11 | **B3 xong** (bộ chấm từ khóa tiếng Anh + chọn theo ngôn ngữ, 21 test, kiểm ngược 3 luật). **B2 bản nháp xong**: ngân hàng tiếng Anh 100 câu + 15 đoạn, đáp án mẫu 30/30 đạt 10/10; seed `--retire`; prompt sinh câu tiếng Anh. Khối 1 sửa: từ khóa Python, toán tử, số thập phân. 815 passed | Tuấn duyệt bản dịch, rồi nạp DB thật |
| 14/11 | **B1 xong**: khối 1 tiền xử lý NLP (giữ phủ định, lemmatize theo từ loại, luật số nhiều cho thuật ngữ lập trình, giữ ký hiệu `[ ] ( ) =`), 22 test, toàn bộ 713 passed | Dockerfile cần thêm bước tải dữ liệu NLTK khi gộp nhánh |
| 14/11 | Chốt B0: GĐ7 chỉ làm 7.5a + 7.5c; người chấm Hòa, Tâm. Duyệt câu AI: bấm Duyệt là xong, tự cấp mã gợi ý lúc duyệt (sửa backend 7.3, 54 test). 7.8 đi qua module Phản hồi của Tâm — gửi `BA-nhom/Gui-Tam-Bao-loi-on-tap-qua-Phan-hoi.md` | Chờ Tâm trả lời 4 câu |
| 14/11 | Chép Session01 + Session02 từ thư mục môn NLP vào `BA-nhom/pipeline/`; đối chiếu: Session01 → khối 1, demo2 (P/R/F1) → B5, demo3 (Pydantic + instructor) → khối 4 | — |
| | | |
