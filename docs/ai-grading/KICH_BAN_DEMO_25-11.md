# Kịch bản demo — AI chấm bài tự luận theo barem (25/11/2026)

> Module 09 (Ôn tập & đánh giá) · người trình bày: Tuấn · thời lượng ~12 phút + hỏi đáp
> Số liệu lấy từ `docs/ai-grading/BAO_CAO_AI_CHAM_BAI.md` (mục 7). Bài mẫu để dán: **phiếu riêng** ở máy Tuấn
> (`Downloads/Demo_25-11/Phieu_bai_mau_khoa_312.md` — có đáp án, không đưa vào repo).

## 0. Chuẩn bị (trước giờ demo 30 phút)

| # | Việc | Kiểm tra |
|---|---|---|
| 1 | Đóng bớt ứng dụng (Zalo, tab trình duyệt). Máy 8 GB RAM — backend nạp 2 mô hình AI | RAM trống ≥ 1,5 GB |
| 2 | Docker: chỉ bật `edumentor_postgres`, `edumentor_qdrant` (`docker stop` các container còn lại) | `docker ps` |
| 3 | `cd backend` → `python -m uvicorn app.main:app --port 8000` — **chờ** dòng `Application startup complete` | http://localhost:8000/api/docs mở được |
| 4 | `cd frontend` → `npm run dev` | http://localhost:5173 mở được |
| 5 | `.env`: `AI_MODE=real`, khóa Gemini còn lượt; `SMTP_*` gửi được (email kết quả) | Nộp thử 1 bài trước giờ demo |
| 6 | Tab 1: học viên `tua***@gmail.com` (đã tham gia khóa 312). Tab 2 (cửa sổ ẩn danh): admin | Đăng nhập sẵn cả hai |
| 7 | Mở sẵn: phiếu bài mẫu, báo cáo (mục 7), Swagger đã **Authorize** bằng token admin | |
| 8 | Học viên: **không còn bài dở** ở khóa 312 và **chưa nộp trong 2 phút gần nhất** (luật chặn nộp dồn dập) | Màn Bắt đầu ôn tập không báo "đang làm dở" |

## 1. Bài toán (1 phút — nói, không thao tác)

- Ôn tập 15 câu: 12 trắc nghiệm (chấm theo đáp án) + **3 tự luận do AI chấm theo barem**, đạt từ 6/10.
- AI chấm **từng ý của barem** (Đạt / Không đạt), phải **trích câu có thật trong bài** làm căn cứ; điểm do code cộng.
- Pipeline 9 khối: tiền xử lý NLP → Guard → ngữ cảnh → **Gemini chấm có cấu trúc** → Verifier → **Đối chiếu** → tổng hợp → nhật ký; AI lỗi thì chấm dự phòng bằng từ khóa.

## 2. Học viên làm bài (4 phút — Tab 1)

| Bước | Thao tác | Điểm cần nói |
|---|---|---|
| 2.1 | Khóa học của tôi → khóa **Python Basics: Selection and Iteration** → Ôn tập | Màn Bắt đầu: kỹ năng của khóa, 15 câu, đạt 6/10, ôn **không giới hạn** |
| 2.2 | Bắt đầu ôn tập → làm vài câu trắc nghiệm → **Tạm rời** → vào lại | Câu trả lời được lưu, mở lại đúng bài |
| 2.3 | 3 câu tự luận: dán từ phiếu — câu 1 **A (đáp án mẫu)**, câu 2 **B (nửa đúng)**, câu 3 **D (câu ra lệnh cho AI + lạc đề)** | Tìm câu trong phiếu bằng vài chữ đầu của đề; câu có ⚠ thì bài B giống A |
| 2.4 | Nộp bài (~5–20 giây) | Quá 20 giây → "Đang chấm", chấm tiếp ở nền, có chuông + email |
| 2.5 | Màn Kết quả: điểm, từng ý barem, **lý do**, **câu trích tô sáng**, nhận xét, đáp án mẫu | Câu A: Đạt các ý · Câu B: ý thiếu → Không đạt kèm lý do · Câu D: **0 điểm** dù "đòi" điểm tối đa — vẫn chấm theo barem |

> ⚠ Tài khoản demo **đã từng đạt** khóa 312 → dù bài đạt, màn kết quả chỉ hiện "Bạn đã đạt khóa này trước đó",
> **không** hiện "Khóa chuyển sang Hoàn thành". Đừng hứa cảnh này; nếu thầy hỏi: chỉ lần đạt đầu tiên mới chuyển khóa
> sang Hoàn thành + kỹ năng "Đã biết".

## 3. Giáo viên xem lại (3 phút — Tab 2, admin)

| Bước | Thao tác | Điểm cần nói |
|---|---|---|
| 3.1 | Quản trị → **Kết Quả - AI Chấm** | Câu tự luận bị gắn cờ tự động: lệch chấm từ khóa, AI chấm chặt hơn từ khóa, sát ngưỡng đạt, **bài có câu ra lệnh cho AI**, AI lỗi |
| 3.2 | Lọc lý do "Bài có câu ra lệnh cho AI" → mở bài câu D vừa nộp | Giáo viên thấy đề, barem, bài làm, kết quả + lý do AI từng ý. AI **không bị lừa** — 0 điểm là đúng, giáo viên **không sửa** câu này |
| 3.3 | Bỏ lọc → mở **câu B** vừa nộp (thường có cờ **"AI chấm chặt hơn từ khóa"**) → đổi ý thiếu sang Đạt → Lưu (đổi Đạt ↔ Chưa đạt có hộp xác nhận) | "Hệ thống tự nghi câu này nên đưa giáo viên; giáo viên đọc lại thấy đáng điểm." Điểm câu, điểm bài tính lại; học viên nhận thông báo; màn kết quả hiện "Giáo viên đã xem lại". Nếu câu B không bị cờ → chọn câu có cờ khác (sát ngưỡng đạt / lệch chấm từ khóa) |
| 3.4 | *(tùy thời gian)* Swagger → `GET /api/admin/review-attempts/{id}/trace` | Nhật ký từng khối pipeline: chấm lại, cờ, độ trễ — không chứa bài làm |

## 4. Số liệu đánh giá (3 phút — mở báo cáo mục 7)

| Ý | Con số (phần test: 30 bài, 108 ý, người chấm mù) |
|---|---|
| Hai người chấm khớp nhau | 88,9%, kappa 0,77 (cả bộ: 90,7%, kappa 0,81) |
| Chấm từ khóa (baseline) | khớp 80,6% |
| **Pipeline 9 khối (Gemini)** | **khớp 94,4%, QWK 0,95, 0 bài sai bị chấm cao**, lệch trung bình +0,03 |
| AI so với từng người chấm | kappa 0,81–0,85 — **ngang / cao hơn mức hai người khớp nhau** |
| Có ý nghĩa thống kê? | Gemini tốt hơn từ khóa: **có** (bootstrap). RAG, ví dụ mẫu: chưa kết luận được → giữ Model A |
| Độ ổn định (3 lần chạy) | 92,6% ý giữ nguyên; độ chính xác 93,5–98,1% |
| Cờ "cần xem lại" | bắt ~62% bài AI chấm sai (trước cải thiện: 1/6) |
| Chưa đạt | lệch ≤ 1 điểm (80% / mục tiêu 85%), độ trễ p95 (mục tiêu 20 s) |

## 5. Phương án dự phòng

| Sự cố | Cách xử lý |
|---|---|
| Gemini lỗi / hết lượt | Bài vẫn có điểm (chấm dự phòng từ khóa) — nói luôn đây là thiết kế; trang admin hiện cờ "Chấm bằng từ khóa (AI lỗi)" |
| Chấm lâu > 20 giây | Màn "Đang chấm…" tự cập nhật; trong lúc chờ chuyển sang phần 3 (admin) rồi quay lại |
| Báo "vừa nộp bài, vui lòng chờ" | Luật chống nộp tự động (2 phút) — giải thích, hoặc dùng bài đã chấm sẵn trong Lịch sử ôn tập |
| Báo "đang có 5 bài làm dở" | Bấm **Bỏ bài** một bài dở ngay trên màn đó |
| Backend không lên (`ECONNREFUSED`) | Thiếu RAM → `docker stop` các container thừa, chạy lại backend, chờ `Application startup complete` |
| Mất mạng | Mở Lịch sử ôn tập (các bài đã chấm từ trước) + báo cáo |

## 6. Câu hỏi thầy có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Sao không fine-tune? | Đã thống nhất với thầy (13/11): v1 = LLM + RAG + prompt + đánh giá. Fine-tune khi bộ bài lớn cho thấy lỗi có hệ thống — kế hoạch QLoRA ở báo cáo mục 9 |
| Làm sao biết AI chấm đúng? | Bộ bài chuẩn 60 bài, 2 người chấm mù độc lập, phân xử theo hướng dẫn; so bằng MAE / QWK / kappa + bootstrap |
| Học viên "ra lệnh" cho AI? | Guard gắn cờ, prompt bắt chấm theo barem, Verifier đòi câu trích có thật → không được điểm nếu không có nội dung đúng |
| AI bịa căn cứ? | Verifier: ý Đạt mà câu trích không có trong bài → hạ Không đạt + cờ |
| AI chấm sai thì sao? | Cờ đưa giáo viên xem lại (~62% bài sai bị bắt); giáo viên chấm lại, điểm và thông báo cập nhật |
| Kết quả có lạc quan quá không? | Có rò rỉ nhẹ (quy tắc chung rút từ phân xử, gồm câu test) và người phân xử là người làm AI — đã ghi rõ ở Hạn chế; hướng: bộ test mới + người phân xử độc lập |
| Tốn tiền / lượt AI? | Mỗi lần nộp ~3–6 lượt Gemini; chặn nộp dồn dập (2 phút), tối đa 5 bài dở |

## Diễn tập 20/11/2026 (qua API, Gemini thật, tài khoản học viên thử — không phải tài khoản demo)

Mọi bước 2.1 → 3.4 chạy đúng: lưu và mở lại bài dở; nộp **9,8 s** (Gemini, không dự phòng); câu A 1/1;
câu B 0,4/1 (ý thiếu Không đạt kèm lý do) + cờ "AI chấm chặt hơn từ khóa"; câu D **0/2** + cờ "câu ra lệnh cho AI";
giáo viên chấm lại câu B → điểm bài 2,4 → 3,0, học viên thấy "Giáo viên đã xem lại"; nhật ký chấm mở được.
Cờ của bài diễn tập đã đóng. **Chưa thử trên giao diện** (hộp xác nhận, tô sáng câu trích, chuông) → tự bấm 1 lượt ngày 24/11.

## 7. Không demo (chưa xong, nói nếu được hỏi)

- Ôn tập ngay trên đồ thị lộ trình: **đã chạy** (20/11) — node tô màu theo trạng thái, huy hiệu ôn tập ở node Đã biết /
  Đang học, nút "← Quay lại lộ trình". Có thể demo thêm nếu còn thời gian: tài khoản demo → Lộ trình của tôi → lộ trình
  "I know basic SQL…" → huy hiệu ở node **Python Programming** (đừng bấm "Bắt đầu ôn tập" nếu không định nộp).
- Ôn tập theo kỹ năng, "đến hạn ôn": sau 25/11 (`docs/guide.md`).
