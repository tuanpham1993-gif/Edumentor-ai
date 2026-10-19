# SETUP — Hướng dẫn cài đặt EduMentor AI

> Giả định công nghệ: FastAPI + PostgreSQL + Alembic (backend), React + Vite (frontend). Điều chỉnh lệnh nếu nhóm dùng công nghệ khác.

## 1. Yêu cầu

| Công cụ | Phiên bản gợi ý |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 14+ (hoặc dùng Docker) |
| Git | mới nhất |
| Docker (tùy chọn) | để chạy PostgreSQL nhanh |

## 2. Lấy mã nguồn

```bash
git clone <repo-url> edumentor-ai
cd edumentor-ai
```

## 3. Biến môi trường

```bash
cp .env.example .env
```

Các biến chính trong `.env`:

```env
# Ứng dụng
APP_ENV=development
SECRET_KEY=doi-thanh-chuoi-bi-mat
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Cơ sở dữ liệu
DATABASE_URL=postgresql://edumentor:edumentor@localhost:5432/edumentor

# AI
LLM_API_KEY=your-api-key
LLM_MODEL=ten-model

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api
```

> Không commit file `.env`. Chỉ commit `.env.example`.

## 4. Cơ sở dữ liệu

Dùng Docker:

```bash
docker compose up -d db
```

Hoặc tạo thủ công:

```sql
CREATE USER edumentor WITH PASSWORD 'edumentor';
CREATE DATABASE edumentor OWNER edumentor;
```

## 5. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # hoặc: pip install -e .

# Tạo bảng
alembic upgrade head

# Nạp dữ liệu mẫu (khóa học, kỹ năng, quan hệ kỹ năng, câu hỏi ôn tập)
python scripts/seed_data.py

# Tạo tài khoản quản trị
python scripts/create_admin.py

# Chạy server
uvicorn app.main:app --reload --port 8000
```

Kiểm tra: mở `http://localhost:8000/docs` để xem tài liệu API tự sinh.

## 6. Frontend

```bash
cd frontend
npm install
npm run dev
```

Truy cập `http://localhost:5173`.

## 7. Chạy kiểm thử

```bash
cd backend
pytest
```

## 8. Lệnh thường dùng

| Việc cần làm | Lệnh |
|---|---|
| Tạo migration mới | `alembic revision --autogenerate -m "mo ta"` |
| Áp dụng migration | `alembic upgrade head` |
| Quay lại 1 migration | `alembic downgrade -1` |
| Định dạng code | `black . && ruff check .` |
| Chạy toàn bộ bằng Docker | `docker compose up --build` |

## 9. Xử lý sự cố

- **Không kết nối được DB:** kiểm tra `DATABASE_URL` và PostgreSQL đã chạy (`docker compose ps`).
- **Lỗi migration:** đảm bảo đã `git pull` và chạy `alembic upgrade head` trước khi tạo migration mới.
- **Lỗi gọi AI:** kiểm tra `LLM_API_KEY` và kết nối mạng.
- **Lỗi CORS ở frontend:** kiểm tra `VITE_API_BASE_URL` và cấu hình CORS trong `app/main.py`.
