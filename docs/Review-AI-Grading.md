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
| 14/11 | **Người chấm bộ bài chuẩn: Hòa và Tâm** (hai người chấm độc lập, không phải người làm AI). Bất đồng → Tuấn hoặc thầy quyết |
| 14/11 | GĐ7 trước 25/11 chỉ làm **7.5a + 7.5c**; lùi 7.4, 7.5b, 7.5d, 7.6, 7.8; 7.7 gộp vào B13, 7.9 gộp vào B8 (chi tiết `Review-Assessment.md`) |

### 1.3 Mặc định (Claude đề xuất, đổi được nếu nhóm không đồng ý)
| # | Nội dung | Mặc định |
|---|---|---|
| D3 | LLM chính | Gemini (`REVIEW_LLM_MODEL`, hiện `gemini-3.5-flash-lite`); Qwen cục bộ không làm đợt này |
| D4 | Kho vector | Giữ JSON + cosine bằng Python (A7); pgvector để sau |
| D5 | Vị trí code | Module trong backend `app/ai/review/` (không tách dịch vụ riêng) |
| D6 | Đầu ra thêm | `reason` từng ý, `feedback` chung, `flags` — lưu trong cột JSON, không cần migration. **Không** dùng độ tin cậy do LLM tự chấm để quyết định |
| D7 | Mức chấm mỗi ý | Giữ 3 mức `full` / `partial` / `none` (½ điểm cho partial) |
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
- [ ] **B2 Ngân hàng câu hỏi tiếng Anh** — dự kiến 14–15/11 · thực tế __/__ 👤 (🤖 hỗ trợ dịch nháp)
  - `backend/data/review/course_312_en.json`: 100 câu (70 TN + 30 TL) + 15 đoạn tri thức, cùng định dạng `course_312.json`; barem và từ khóa tiếng Anh.
  - Nạp bằng **mã câu mới**, tắt câu tiếng Việt (không sửa đè — đúng quy tắc phiên bản); chạy lại `scripts/build_embeddings.py`.
  - Đổi `GENERATE_SYSTEM_PROMPT` (đang yêu cầu "Viết bằng tiếng Việt") sang tiếng Anh.
  - ✅ Validator không báo lỗi; đề ôn tập khóa 312 ra 15 câu tiếng Anh.
- [ ] **B3 Bộ chấm từ khóa tiếng Anh** — dự kiến 15/11 · thực tế __/__ 👤
  - Dựa trên khối 1; giữ luật QT12 (tách vế, chặn bài chỉ liệt kê từ khóa, bỏ câu chép đề).
  - ✅ Test: diễn đạt khác dạng từ vẫn khớp; phủ định ("cannot change") không bị tính là "change"; bài chỉ liệt kê từ khóa không được đủ điểm.
- [ ] **B4 Bộ bài chuẩn (gold set)** — dự kiến 15–17/11 (song song) · thực tế __/__ 👤 soạn + **Hòa, Tâm chấm**
  - `docs/ai-grading/RATER_GUIDELINE.md` (tiếng Anh, ví dụ full / partial / none cho từng loại ý).
  - Google Form thu bài thật (có câu đồng ý dùng cho nghiên cứu, không hỏi tên); nhóm viết thêm các loại bài còn thiếu; bài do AI sinh ≤ 30% và **không vào test**.
  - Vòng hiệu chỉnh 20 bài (Hòa + Tâm cùng chấm, so sánh, sửa hướng dẫn) → hai bạn chấm độc lập phần còn lại, **không xem điểm của nhau và không xem điểm AI** → bất đồng do Tuấn hoặc thầy quyết.
  - ✅ ≥ 120 bài (≥ 40 bài thật), có `gold.csv`, kappa giữa hai người, chia dev / test theo câu hỏi. Dữ liệu thật **không commit** lên repo.
- [ ] **B5 Script đánh giá** — dự kiến 15–16/11 · thực tế __/__ 👤
  - `backend/scripts/eval_grading.py`: đọc `gold.csv` + kết quả một lần chạy → các chỉ số mục 3 + bootstrap + **Precision / Recall / F1 theo từng nhãn full / partial / none** (cách tính như `Session02/demo2.py`); mỗi lần chạy lưu `results/<run_id>.csv` (method, model, prompt_version, kết quả từng ý, latency, lỗi).
  - ✅ Chạy được với chấm từ khóa trên dev; số liệu tái lập được.
- [ ] **B6 Runner pipeline** — dự kiến 16/11 · thực tế __/__ 👤
  - `backend/app/ai/review/pipeline/`: runner + bọc khối 0, 3, 4, 7, 8 từ code có sẵn; ghi `trace.nodes`.
  - ✅ **Hành vi không đổi**: toàn bộ test cũ vẫn xanh; trace có thời gian từng khối.
- [ ] **B7 Khối 4 — chấm có cấu trúc** — dự kiến 17/11 · thực tế __/__ 👤
  - Prompt tiếng Anh `grade-en-v1`; `responseSchema`; model Pydantic kiểm kết quả (theo cách `Session02/demo3.py`: `Literal["full","partial","none"]`, `Field(description=...)`); JSON sai → thử lại 1 lần; thứ tự trường `evidence` → `reason` → `result`; thêm `feedback`; ghi `prompt_version`.
  - ✅ 0 lỗi JSON trên dev; test tự động vẫn dùng mock (không gọi Gemini).
- [ ] **B8 Khối 2, 5, 6 — Guard, Verifier, Đối chiếu** — dự kiến 18/11 · thực tế __/__ 👤
  - Guard: bài trống, không phải tiếng Anh, quá dài, dấu hiệu chèn lệnh.
  - Verifier: câu trích phải có trong bài (so sau chuẩn hóa) — không có thì ý đó `none` + cờ.
  - Đối chiếu: lệch > 3 → chấm lại 1 lần → vẫn lệch → `needs_review`.
  - ✅ Test cho từng nhánh (bằng AI mock).
- [ ] **B9 Model B (RAG khi chấm) + chỉnh trên dev** — dự kiến 18–19/11 · thực tế __/__ 👤
  - Cờ `REVIEW_GRADING_RAG`; khối 3 thêm đoạn tri thức (lọc `skill_id`, câu truy vấn = đề + barem, **không** dùng bài làm).
  - Chạy từ khóa / A / B trên dev; phân tích 20 bài lệch nhất (barem mơ hồ / truy xuất sai / bỏ sót cách diễn đạt / bằng chứng bịa / dễ dãi / lỗi JSON); chỉnh prompt, ghi `EXPERIMENT_LOG.md`.
  - ✅ Chốt `prompt_version` cuối.
- [ ] **B10 Chạy test** — dự kiến 20/11 · thực tế __/__ 👤
  - Chạy **một lần** cho từ khóa, A, B; bootstrap; độ trễ.
  - ✅ Bảng kết quả + nhật ký chạy.
- [ ] **B11 Giao diện kết quả** — dự kiến 21/11 · thực tế __/__ 👤
  - `ReviewResultPage` / chi tiết lịch sử: từng ý có kết quả, điểm, lý do, **câu trích tô sáng trong bài làm**; nhận xét chung; nhãn "Chấm bởi AI"; bài cần xem xét ghi "đang xem lại".
- [ ] **B12 Kiểm thử toàn luồng** — dự kiến 22/11 · thực tế __/__ 👤
  - Chạy trên Docker: nộp bài → có điểm ≤ 20 giây hoặc "Đang chấm"; Gemini lỗi → điểm từ khóa + cờ.
- [ ] **B13 Báo cáo và tài liệu** — dự kiến 23–24/11 · thực tế __/__ 👤
  - Chương thực nghiệm (bảng mục 3), mục "Hướng phát triển: fine-tune" (khi nào cần, dữ liệu, QLoRA, cách chứng minh).
  - Cập nhật BA / SRS / `api-endpoints.md`: hiện còn ghi **20 câu trắc nghiệm** (FR-24/25/26, UC-09) — sai so với code.
- [ ] **B14 Nộp** — 25/11

**Thứ tự và phụ thuộc:** B1 → B3 · B2 → B4 → B5 · B1 + B6 → B7 → B8 → B9 (cần B4, B5) → B10 → B11 → B12 → B13. B2, B4, B5 làm song song với B1, B3, B6.

---

## 5. Nhật ký

| Ngày | Đã làm | Vướng mắc |
|---|---|---|
| 13/11 | Khảo sát AI Grading; chốt D1 tiếng Anh, D2 fine-tune để sau, D12 hạn 25/11 | — |
| 14/11 | Thầy đồng ý phiên bản 1 LLM + RAG + Prompt; yêu cầu thêm độ chính xác + pipeline kiểu n8n. Gom tài liệu pipeline Session 01. Lập file kế hoạch này | GĐ7 trùng lịch |
| 14/11 | **B1 xong**: khối 1 tiền xử lý NLP (giữ phủ định, lemmatize theo từ loại, luật số nhiều cho thuật ngữ lập trình, giữ ký hiệu `[ ] ( ) =`), 22 test, toàn bộ 713 passed | Dockerfile cần thêm bước tải dữ liệu NLTK khi gộp nhánh |
| 14/11 | Chốt B0: GĐ7 chỉ làm 7.5a + 7.5c; người chấm Hòa, Tâm. Duyệt câu AI: bấm Duyệt là xong, tự cấp mã gợi ý lúc duyệt (sửa backend 7.3, 54 test). 7.8 đi qua module Phản hồi của Tâm — gửi `BA-nhom/Gui-Tam-Bao-loi-on-tap-qua-Phan-hoi.md` | Chờ Tâm trả lời 4 câu |
| 14/11 | Chép Session01 + Session02 từ thư mục môn NLP vào `BA-nhom/pipeline/`; đối chiếu: Session01 → khối 1, demo2 (P/R/F1) → B5, demo3 (Pydantic + instructor) → khối 4 | — |
| | | |
