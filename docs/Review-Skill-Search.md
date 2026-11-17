# Đề xuất: Tìm kỹ năng theo tên → `skill_id` → câu hỏi ôn tập

> Module 09 (Ôn tập) · phụ trách: Tuấn · lập 17/11/2026 · trạng thái: **đề xuất, chưa code**

## 1. Bối cảnh

- Database có **5.893 kỹ năng** (`skills`), nhưng chỉ **5 kỹ năng** có ngân hàng câu hỏi (khóa 312).
- Nhiều kỹ năng **trùng tên**: 722 kỹ năng gom lại chỉ còn 338 nhóm khi bỏ khác biệt hoa/thường, dấu câu và phần trong ngoặc. Ví dụ "JavaScript", "Javascript", "JavaScript (Programming Language)" là 3 `skill_id` khác nhau.
- Khi **chấm bài**, hệ thống đã tra thẳng database (`attempt → question_id → barem, skill_id`), không dùng RAG. Cờ `REVIEW_GRADING_RAG` đang tắt.
- Chỗ cần "tìm" là **trước** bước đó: người dùng (hoặc AI lộ trình) đưa vào **một tên kỹ năng**, hệ thống phải tìm ra `skill_id` đúng, rồi mới lấy câu hỏi ôn tập theo id.

Thầy yêu cầu (bài "Kiến trúc RAG cho 6.000 kỹ năng"): gắn metadata kỹ năng để thu hẹp tìm kiếm, **hybrid search (từ khóa BM25 + vector) + rerank**, chỉ nạp rubric của đúng kỹ năng.

## 2. Mục tiêu

Một service dùng chung, **thuộc module 09**, làm hai việc:

1. `tên kỹ năng` (tiếng Việt hoặc tiếng Anh, có thể sai chính tả hoặc viết khác) → danh sách `skill_id` khớp nhất, kèm điểm và lý do khớp.
2. `skill_id` → câu hỏi ôn tập trong database (tra thẳng, **không RAG**).

**Không làm trong đề xuất này:**
- không sửa bảng `skills` hay `course_skill` (dữ liệu của Hòa và Khôi): service **chỉ đọc**;
- không tự dùng ngân hàng câu hỏi của kỹ năng khác để chấm bài, vì "Python for Quantum Computing" khác "Python Programming". Kỹ năng gần giống chỉ được **gợi ý**, admin quyết định.

## 3. Thử nghiệm 17/11 (số liệu thật)

Embedding 5.893 tên kỹ năng bằng mô hình đang dùng cho ôn tập (`paraphrase-multilingual-MiniLM-L12-v2`, 384 chiều), rồi tìm theo cosine. Tính vector cho cả 5.893 tên mất **25 giây** (làm một lần); mỗi lần tìm mất vài mili-giây. Dấu \* là kỹ năng đã có ngân hàng câu hỏi.

| Truy vấn | Top 1 (điểm) | Đánh giá |
|---|---|---|
| `javascript` | Javascript #4919 (0.99), JavaScript #4 (0.99) | ✅ gom được tên trùng |
| `Javascript programming` | JavaScript #4 (0.90), JavaScript (Programming Language) #2283 (0.87) | ✅ |
| `python` | Python #2787 (0.98), Python Programming #167\* (0.92) | ✅ nhưng top 1 chưa có ngân hàng |
| `lập trình python` | Python programming #5852 (0.97), Python Programming #167\* (0.97) | ✅ hiểu tiếng Việt |
| `giao tiếp` | communication #4123 (0.91) | ✅ hiểu tiếng Việt |
| `for loop` | For Loop #4066 (0.99) | ✅ |
| `machine learning`, `teamwork`, `Payroll`, `react js`, `SQL database` | đúng, 0.88–1.00 | ✅ |
| `vòng lặp` | Loops #4852 (0.70), các kết quả sau là rác | 🟡 đúng nhưng điểm thấp |
| `if else` | Perceptron (0.58), qlik sense… | ❌ sai hết; DB có "If Statements", "Conditionals" |
| **`java`** | **ZOWE (0.90)**, Augur (0.89), Perceptron (0.88) | ❌ **sai mà điểm cao**; DB có đúng "Java" |

**Kết luận:**
1. Chỉ tìm bằng vector thì **không đủ**, và **không thể chỉ dựa vào ngưỡng điểm**: "java" sai với điểm 0.90, cao hơn "vòng lặp" đúng (0.70). Mô hình nhỏ xử lý kém từ rất ngắn.
2. Tìm theo chữ bắt được đúng các ca vector bỏ lỡ ("java" khớp nguyên văn "Java", "if" khớp "If Statements"). Vì vậy cần **hybrid**, đúng như bài của thầy.
3. Một tên ứng với nhiều `skill_id` trùng, nên phải **ưu tiên id đã có ngân hàng câu hỏi**.

## 4. Thiết kế: pipeline tìm kỹ năng (kiểu n8n)

Chạy trên `app/ai/review/pipeline/runner.py` có sẵn: mỗi khối một việc, có trace từng khối.

| Khối | Việc | Ghi chú |
|---|---|---|
| 0 Input | Nhận `q`, cắt khoảng trắng, giới hạn 100 ký tự | Rỗng → trả danh sách rỗng |
| 1 Normalize | Chữ thường, NFC, bỏ phần trong ngoặc, bỏ ký tự thừa | `"JavaScript (Programming Language)"` → `"javascript"` |
| 2 Exact | So với tên đã chuẩn hóa của mọi kỹ năng | Khớp → điểm 1.0, `match="exact"`. Vẫn chạy tiếp để lấy các id trùng tên |
| 3 Keyword (BM25) | BM25 trên token tên kỹ năng (tự viết, khoảng 40 dòng, không thêm thư viện) | Top 20. Bắt được "java", "if" |
| 4 Vector | Cosine giữa vector truy vấn và vector tên kỹ năng (tính sẵn) | Top 20. Bắt được tiếng Việt, từ đồng nghĩa |
| 5 Fuse | Gộp 3 danh sách bằng **Reciprocal Rank Fusion** (RRF, k = 60) | Không phải chỉnh trọng số giữa hai thang điểm khác nhau |
| 6 Group | Gom các id cùng tên chuẩn hóa thành một nhóm. Đại diện nhóm = id **có nhiều câu hỏi đang bật nhất**, nếu bằng nhau thì id nhỏ nhất | Kết quả trả kèm `aliases` |
| 7 Decide | Top 1 bỏ xa top 2 (hoặc khớp exact) → `confident=true`; ngược lại trả top 5 để người dùng chọn | Không bao giờ tự chọn khi mơ hồ |
| 8 Trace | Ghi điểm từng nguồn (exact / bm25 / vector / rrf) của top 5 | Phục vụ đánh giá và debug |

**Rerank:** chưa dùng cross-encoder hoặc LLM ở bản 1, vì RRF + exact + nhóm trùng tên đã xử lý các ca thử nghiệm. Sẽ thêm khối `7a Rerank` nếu bộ test ở mục 7 cho thấy cần.

**Vector tên kỹ năng:** tính một lần bằng script và lưu ra file cache `data/cache/skill_name_vectors.npz` (kèm tên mô hình + hash danh sách kỹ năng, lệch thì tính lại). Lúc server khởi động, nạp vào RAM ở luồng nền (giống `warm_up_in_background` hiện có). Không cần bảng mới, không cần migration, không đụng bảng `skills`. Chưa có vector hoặc mô hình → pipeline bỏ khối 4, vẫn trả kết quả từ exact + BM25.

## 5. API (đề xuất)

Đặt trong router quản trị ôn tập (`/api/admin/review`, cần quyền admin):

| Method | Đường dẫn | Trả về |
|---|---|---|
| GET | `/skills/search?q=python&limit=5` | `{query, confident, results: [{skill_id, skill, score, match, aliases: [{skill_id, skill}], active_questions, pending_questions}]}` |
| GET | `/questions?skill_id=167` | (đã có) danh sách câu hỏi của kỹ năng, tra thẳng DB |

**Luồng dùng:** gõ tên kỹ năng → `skills/search` → chọn kết quả (hoặc tự chọn khi `confident`) → `questions?skill_id=…` → hiện câu hỏi ôn tập của kỹ năng đó.

**Phía học viên:** chưa mở ở bản 1, vì câu hỏi có đáp án và barem. Nếu sau này cần (ví dụ ô tìm kỹ năng ở trang Kỹ năng của tôi), mở một endpoint chỉ trả `skill_id`, tên và số câu, không trả nội dung câu hỏi.

**Cho Hòa và Khôi:** gọi hàm Python `skill_search_service.search(db, q, limit)` trực tiếp (ví dụ để đổi tên kỹ năng do AI lộ trình trả về thành `skill_id`). Hai bạn không cần sửa code của mình; service chỉ đọc.

## 6. Vị trí code (module 09)

| File | Nội dung |
|---|---|
| `app/services/skill_search_service.py` | `search(db, q, limit)`, `questions_for(db, skill_id)`; nạp và cache index |
| `app/ai/review/pipeline/skill_search.py` | Các khối 0–8 trên runner có sẵn |
| `app/ai/review/bm25.py` | BM25 nhỏ cho tên ngắn |
| `scripts/build_skill_vectors.py` | Tính vector tên kỹ năng → file cache |
| `app/routers/v1/endpoints/admin/review_admin.py` | Thêm `GET /skills/search` |
| `app/schemas/review_admin.py` | `SkillSearchOut`, `SkillMatchOut` |
| `tests/test_skill_search.py` | Test với embedder giả (không tải mô hình) |
| Frontend `/admin/questions` | Ô "Tìm kỹ năng" thay cho danh sách chọn kỹ năng khi chưa chọn khóa học |

## 7. Đánh giá

Bộ test cố định khoảng **40 truy vấn** có đáp án `skill_id` đúng (nhóm tên trùng tính là đúng):
- tiếng Anh chuẩn ("for loop"), tiếng Việt ("vòng lặp"), viết tắt hoặc ngắn ("java", "js", "ml"), sai chính tả ("pyhton"), mô tả ("câu lệnh if else");
- và 5 truy vấn **không có kỹ năng tương ứng**: phải trả `confident=false`.

**Chỉ số:**
- **Hit@1** và **Hit@5**;
- tỉ lệ `confident=true` mà sai (phải gần 0);
- thời gian mỗi truy vấn.

**So sánh ba cấu hình:** chỉ vector / chỉ BM25 / hybrid (RRF). Ghi số liệu vào báo cáo, tiếp nối bảng ở mục 3.

**Mục tiêu bản 1:** Hit@5 ≥ 95%, Hit@1 ≥ 85%, không có `confident` sai, dưới 50 ms mỗi truy vấn.

## 8. Kế hoạch

| Bước | Việc | Ước lượng |
|---|---|---|
| S1 | Script tính vector + cache, BM25, pipeline khối 0–8, service | 0,5 ngày |
| S2 | Endpoint admin + schema + test (embedder giả) | 0,5 ngày |
| S3 | Bộ 40 truy vấn + chạy so sánh 3 cấu hình, ghi kết quả | 0,5 ngày |
| S4 | Ô "Tìm kỹ năng" trên `/admin/questions` | 0,5 ngày |

## 9. Câu hỏi mở

1. Có mở tìm kiếm cho học viên ở bản 1 không? (đề xuất: chưa)
2. Bảng bí danh `skill_alias` để gộp hẳn các id trùng: để Hòa/Khôi quyết sau. Bản 1 chỉ **gom lúc tìm** (khối 6), không sửa dữ liệu.
3. Gắn metadata domain / cấp độ cho kỹ năng (ý 1 trong bài của thầy): cần dữ liệu mới. Để "Hướng phát triển", có thể suy domain từ khóa học chứa kỹ năng.

## Nhật ký

| Ngày | Nội dung |
|---|---|
| 17/11/2026 | Lập đề xuất. Thử nghiệm tìm bằng vector trên 5.893 tên kỹ năng: tốt với tên đầy đủ và tiếng Việt, sai với từ ngắn ("java", "if else") → chọn hybrid exact + BM25 + vector (RRF) |
