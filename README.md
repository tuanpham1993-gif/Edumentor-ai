# EduMentor AI

Nền tảng cố vấn học tập cá nhân hóa: tạo lộ trình học theo mục tiêu bằng AI, gợi ý khóa học MOOC bên ngoài theo từng kỹ năng, hỗ trợ giải đáp với AI Tutor và ghi nhận kỹ năng thông qua bài ôn tập.

> **Giao diện tham chiếu:** bản demo React 33 màn `EduMentor AI Demo.html` (bản build một file; mã nguồn React gốc chưa có trong repo). Frontend được dựng lại theo bản demo này — xem `docs/decisions.md` D-FE-02.
> Các hình trong `docs/wireframes/` và prototype `docs/EduMentor-UI-design/` **không còn dùng** làm tham chiếu giao diện.

## Tính năng chính

| # | Nhóm | Mô tả | Phụ trách |
|---|---|---|---|
| 01 | Tài khoản & hồ sơ | Đăng ký, đăng nhập, quên/đặt lại mật khẩu, hồ sơ, đổi ảnh đại diện (bấm vào avatar), đổi mật khẩu, kỹ năng cá nhân. | Tuấn |
| 02 | Danh mục khóa học | Tìm kiếm, lọc theo kỹ năng/cấp độ, sắp xếp theo đánh giá. Khóa học dẫn tới nền tảng MOOC bên ngoài. | Khôi |
| 03 | Đánh dấu (bookmark) | Lưu khóa học để học sau. | Tâm |
| 04 | Theo dõi tiến trình | Bốn trạng thái `bookmarked`, `ongoing`, `completed`, `abandoned`; đề xuất khóa học theo node của lộ trình. | Hòa |
| 05–07 | AI Consultant, lộ trình, node/cạnh | Trò chuyện về mục tiêu để nhận lộ trình dạng đồ thị kỹ năng. Thêm/xóa node và cạnh, chọn node để xem khóa học gợi ý. | Hòa |
| 08 | AI Tutor | Giải thích kiến thức, ví dụ mã, phân tích lỗi, tạo câu trắc nghiệm củng cố. | Tâm |
| 09 | Ôn tập | Bài 20 câu trắc nghiệm **theo khóa học**, lấy từ các kỹ năng mà khóa học dạy; làm **đạt** (≥ 60%) sẽ đánh dấu khóa học `completed` và ghi nhận các kỹ năng đó. Xem lại đáp án, ẩn/hiện giải thích. | Tuấn |
| 10 | Phản hồi | Trang "Liên hệ & góp ý": gửi phản hồi về một khóa học hoặc về hệ thống, xem liên hệ của khóa học. | Tâm |
| 11 | Quản trị khóa học, kỹ năng | Khóa học, kỹ năng, liên kết khóa học ↔ kỹ năng. | Khôi |
| 12 | Quản trị quan hệ kỹ năng | Sơ đồ quan hệ giữa các kỹ năng (mở bằng cách bấm một kỹ năng). | Hòa |
| 13 | Quản trị phản hồi | Xem, lọc phản hồi theo loại, đối tượng và thời gian; sắp xếp theo thời gian. | Tâm |
| 14 | Quản trị lộ trình người dùng | Xem (chỉ đọc) lộ trình và tiến độ kỹ năng của từng người dùng. | Hòa |

Ngoài 14 tính năng, giao diện quản trị còn có Mẫu lộ trình cơ sở và Dữ liệu lịch sử (§12–§13 của `docs/api-endpoints.md`).

Tiện ích chung trên giao diện:

- **Bong bóng chat** ở góc phải: lối tắt GitHub, Zalo, Liên hệ, và AI tư vấn khóa học cho người mới hoặc tài khoản đã đăng ký.
- **Giao diện Sáng/Tối:** chọn ở trang Hồ sơ hoặc Cài đặt tài khoản.

## Nguyên tắc thiết kế

- EduMentor **không lưu nội dung khóa học** và không đăng ký thay người dùng trên nền tảng ngoài.
- Chỉ theo dõi tiến trình ở mức cơ bản (không theo dõi bài học hay video).
- `completed` chỉ có được khi làm đạt bài ôn tập của khóa học, không phải khi mở liên kết ngoài.
- Xóa lộ trình = chuyển sang `abandoned`, giữ lịch sử phục vụ phân tích.
- Mô hình AI chỉ diễn giải mục tiêu; backend ánh xạ kỹ năng, mở rộng tiên quyết, tham khảo lộ trình lịch sử (Collaborative Filtering) và lưu kết quả.
- Lộ trình AI đề xuất chỉ được lưu sau khi người dùng xác nhận.

## Luồng tạo lộ trình

```
Mục tiêu người dùng
   → AI diễn giải mục tiêu và kỹ năng đích
   → Tìm mẫu lộ trình cơ sở (nếu có)
   → Ánh xạ vào danh mục kỹ năng (xác thực đầu ra AI)
   → Mở rộng quan hệ tiên quyết từ đồ thị kỹ năng
   → Tham khảo lộ trình lịch sử tương tự
   → Lộ trình đề xuất → người dùng xem xét → lưu
```

## Tổng quan API

Tất cả endpoint bắt đầu bằng `/api/`. Chi tiết xem [`docs/api-endpoints.md`](docs/api-endpoints.md).

| Nhóm | Tiền tố |
|---|---|
| Xác thực, hồ sơ | `/api/auth/*`, `/api/me`, `/api/me/avatar`, `/api/me/change-password`, `/api/me/skills`, `/api/me/summary` |
| Danh mục khóa học | `/api/courses*` |
| Lưu & theo dõi khóa học | `/api/me/bookmarks*`, `/api/me/courses*`, `/api/courses/{id}/join` |
| Lộ trình học tập | `/api/chat/learning-path`, `/api/learning-paths*`, `/api/me/learning-paths` |
| Node & cạnh lộ trình | `/api/learning-paths/{path_id}/nodes*`, `.../edges*` |
| Gợi ý khóa học theo node | `/api/learning-paths/{path_id}/nodes/{skill_id}/courses` |
| AI Tutor | `/api/chat/sessions*` |
| Ôn tập | `/api/courses/{course_id}/review*`, `/api/review-attempts*`, `/api/me/review-history*` |
| Quản trị | `/api/admin/*` |

**Chưa có endpoint:** giao diện đã có trong bản demo nhưng `docs/api-endpoints.md` chưa định nghĩa API cho: lưu bài ôn tập làm dở, phản hồi (gửi, xem liên hệ khóa học, quản trị phản hồi), quản trị xem lộ trình người dùng, AI tư vấn khóa học trong bong bóng chat. Nhóm cần bổ sung — theo dõi tại `docs/decisions.md` ND-55. Trong lúc chờ, các màn hình này hiển thị trạng thái "chưa khả dụng" (D-FE-08).

## Cấu trúc thư mục

```
edumentor-ai/
├── README.md
├── CLAUDE.md                # Chỉ thị cho Claude Code
├── SETUP.md                 # Cài đặt và chạy dự án
├── docker-compose.yml
├── .env.example
├── docs/                    # Đặc tả API, CSDL, quyết định, cấu trúc, quy ước, báo cáo đồng bộ giao diện
├── backend/                 # FastAPI: router → service → repository → model
└── frontend/                # React + Vite, cấu trúc theo bản demo
```

Cây thư mục chi tiết của backend và frontend, ánh xạ endpoint → file và bảng **route → trang → endpoint**: [`docs/structure.md`](docs/structure.md). Quy ước giao diện (CSS Modules, design token, animation, reduced-motion, gọi API): [`docs/conventions.md`](docs/conventions.md) §4.

## Công nghệ (giả định)

- **Backend:** Python, FastAPI, SQLAlchemy (bảng tạo bằng `create_all` khi khởi động; Alembic: kế hoạch sau)
- **CSDL:** PostgreSQL
- **Frontend:** React 18, Vite 6.4.5, react-router-dom 6, CSS Modules, Axios (D-FE-09)
- **AI:** mô hình ngôn ngữ lớn qua API

## Bắt đầu nhanh

```bash
git clone <repo-url> edumentor-ai && cd edumentor-ai
cp .env.example .env        # rồi điền giá trị thật (khóa AI, SMTP, SECRET_KEY…) — xem SETUP.md
```

> `.env` phải có `ALLOWED_ORIGINS` (bắt buộc), vd `ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:8088"]`.

**Cách 1 — chạy toàn bộ bằng Docker**

```bash
docker compose up -d --build
# Frontend: http://localhost:8088   ·   Backend (Swagger): http://localhost:8001/api/docs
```

**Cách 2 — chạy dev trên máy** (Docker chỉ chạy PostgreSQL + Qdrant)

```bash
docker compose up -d postgres qdrant

cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000     # Swagger: http://localhost:8000/api/docs

cd ../frontend && npm install && npm run dev   # http://localhost:5173
```

**Dữ liệu khởi tạo — tự động khi backend khởi động trên database mới:** tạo bảng, nạp kỹ năng / khóa học /
lộ trình mẫu (`backend/app/core/seed_data/seed_data_code.py`), nạp ngân hàng đề ôn tập + embedding
(`review_autoseed.py`, chỉ khi chưa có đề). Không cần chạy migration hay script seed bằng tay.

**Chạy tay khi cần** (trong thư mục `backend`; với Docker thêm `docker compose exec backend` phía trước):

```bash
python -m app.core.seed_data.create_admin --email <email> --full-name "Quản trị viên"   # tài khoản admin (hỏi mật khẩu)
python -m app.core.seed_data.seed_students --count 200                                 # học viên mẫu (demo)
python -m app.core.seed_data.seed_review --file data/review/course_<id>_en.json        # thêm đề vào DB đã có đề
python -m app.core.seed_data.build_embeddings
```

Xem hướng dẫn đầy đủ (gồm `VITE_USE_MOCK` để xem giao diện khi chưa có backend) tại [SETUP.md](SETUP.md).

## Tài liệu liên quan

| Tài liệu | Nội dung |
|---|---|
| [SETUP.md](SETUP.md) | Cài đặt và chạy dự án |
| [docs/structure.md](docs/structure.md) | Cấu trúc thư mục, ánh xạ endpoint → file, route frontend |
| [docs/conventions.md](docs/conventions.md) | Quy ước API, mã nguồn, Git, kiểm thử |
| [docs/api-endpoints.md](docs/api-endpoints.md) | Đặc tả endpoint |
| [docs/database-design.md](docs/database-design.md) | Thiết kế cơ sở dữ liệu |
| [docs/decisions.md](docs/decisions.md) | Quyết định đã chốt và các điểm còn cần quyết định |
| [docs/ui-animation/](docs/ui-animation/) | Báo cáo đối chiếu frontend với bản demo |

## Phạm vi phiên bản thử nghiệm

- Endpoint dữ liệu lộ trình lịch sử (`/api/admin/historical-learning-path*`) là **tùy chọn**.
- Đã chốt: trường `is_required` và `is_target` (kỹ năng mục tiêu lưu riêng) cho node lộ trình — xem `docs/database-design.md`; làm lại bài ôn tập không giới hạn (D03); điểm đạt tối thiểu 60% (D02).
- Các điểm còn chờ quyết định (gồm danh sách `feedback_type` và các endpoint còn thiếu ở trên) được theo dõi tập trung tại [docs/decisions.md](docs/decisions.md) §4 và §6.

## Nhóm thực hiện

| Thành viên | Phụ trách |
|---|---|
| Tuấn | 01 Tài khoản & hồ sơ, 09 Ôn tập |
| Khôi | 02 Danh mục khóa học, 11 Quản trị khóa học và kỹ năng |
| Tâm | 03 Lưu khóa học, 08 AI Tutor, 10 Phản hồi, 13 Quản trị phản hồi |
| Hòa | 04 Theo dõi tiến trình, 05–07 Lộ trình và gợi ý, 12 Quản trị quan hệ kỹ năng, 14 Quản trị lộ trình người dùng |
