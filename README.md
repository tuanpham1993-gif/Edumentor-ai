# EduMentor AI

Nền tảng cố vấn học tập cá nhân hóa: tạo lộ trình học theo mục tiêu bằng AI, gợi ý khóa học MOOC bên ngoài theo từng kỹ năng, hỗ trợ giải đáp với AI Tutor và ghi nhận kỹ năng thông qua bài ôn tập.

## Tính năng chính

| Nhóm | Mô tả |
|---|---|
| Tài khoản & hồ sơ | Đăng ký, đăng nhập, quên / đổi mật khẩu, hồ sơ và danh sách kỹ năng cá nhân. |
| Danh mục khóa học | Tìm kiếm, lọc theo kỹ năng/cấp độ, sắp xếp theo đánh giá. Khóa học dẫn tới nền tảng MOOC bên ngoài. |
| Theo dõi khóa học | Bốn trạng thái: `bookmarked`, `ongoing`, `completed`, `abandoned`. |
| AI Consultant | Trò chuyện về mục tiêu để nhận lộ trình học dạng đồ thị kỹ năng (node + cạnh). |
| Gợi ý theo node | Chọn một kỹ năng trong lộ trình để xem khóa học phù hợp. |
| AI Tutor | Giải thích kiến thức, ví dụ mã, phân tích lỗi, tạo 3 câu trắc nghiệm củng cố. |
| Ôn tập | Bài 20 câu trắc nghiệm **theo khóa học**, lấy từ các kỹ năng mà khóa học dạy; làm **đạt** (≥ 60%) sẽ đánh dấu khóa học `completed` và ghi nhận các kỹ năng đó. |
| Quản trị | Quản lý khóa học, kỹ năng, quan hệ kỹ năng, mẫu lộ trình cơ sở và dữ liệu lịch sử. |

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
| Xác thực, hồ sơ | `/api/auth/*`, `/api/me*`, `/api/me/skills` |
| Danh mục khóa học | `/api/courses*` |
| Lưu & theo dõi khóa học | `/api/me/bookmarks*`, `/api/me/courses*`, `/api/courses/{id}/join` |
| Lộ trình học tập | `/api/chat/learning-path`, `/api/learning-paths*`, `/api/me/learning-paths` |
| Node & cạnh lộ trình | `/api/learning-paths/{path_id}/nodes*`, `.../edges*` |
| Gợi ý khóa học theo node | `/api/learning-paths/{path_id}/nodes/{skill_id}/courses` |
| AI Tutor | `/api/chat/sessions*` |
| Ôn tập | `/api/courses/{course_id}/review*`, `/api/review-attempts*`, `/api/me/review-history*` |
| Quản trị | `/api/admin/*` |

## Công nghệ (giả định)

- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **CSDL:** PostgreSQL
- **Frontend:** React, Vite
- **AI:** mô hình ngôn ngữ lớn qua API

## Bắt đầu nhanh

```bash
git clone <repo-url> edumentor-ai && cd edumentor-ai
cp .env.example .env
docker compose up -d db

cd backend && pip install -r requirements.txt
alembic upgrade head && python scripts/seed_data.py
uvicorn app.main:app --reload
```

Xem hướng dẫn đầy đủ tại [SETUP.md](SETUP.md).

## Tài liệu liên quan

| Tài liệu | Nội dung |
|---|---|
| [SETUP.md](SETUP.md) | Cài đặt và chạy dự án |
| [docs/structure.md](docs/structure.md) | Cấu trúc thư mục và ánh xạ endpoint → file |
| [docs/conventions.md](docs/conventions.md) | Quy ước API, mã nguồn, Git, kiểm thử |
| [docs/api-endpoints.md](docs/api-endpoints.md) | Đặc tả endpoint |
| [docs/database-design.md](docs/database-design.md) | Thiết kế cơ sở dữ liệu |
| [docs/decisions.md](docs/decisions.md) | Quyết định đã chốt và các điểm còn cần quyết định |

## Phạm vi phiên bản thử nghiệm

- Endpoint dữ liệu lộ trình lịch sử (`/api/admin/historical-learning-path*`) là **tùy chọn**.
- Đã chốt: trường `is_required` và `is_target` (kỹ năng mục tiêu lưu riêng) cho node lộ trình — xem `docs/database-design.md`; làm lại bài ôn tập không giới hạn (D03); điểm đạt tối thiểu 60% (D02).
- Các điểm còn chờ quyết định được theo dõi tập trung tại [docs/decisions.md](docs/decisions.md) §4.

## Nhóm thực hiện

| Thành viên | Vai trò |
|---|---|
| _Tên_ | _Vai trò_ |
