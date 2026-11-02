# SETUP — Hướng dẫn cài đặt EduMentor AI

> Giả định công nghệ: FastAPI + PostgreSQL + Alembic (backend), React + Vite (frontend). Điều chỉnh lệnh nếu nhóm dùng công nghệ khác.

## 1. Yêu cầu

| Công cụ | Phiên bản gợi ý |
|---|---|
| Python | 3.11+ |
| Node.js | 18.x, 20.x hoặc ≥ 22 — `^18.0.0 \|\| ^20.0.0 \|\| >=22.0.0` (theo `engines` trong `frontend/package.json`; không hỗ trợ 19, 21) |
| PostgreSQL | 14+ |
| Git | mới nhất |
| Docker (tùy chọn) | Chưa có cấu hình Compose dùng được trên nhánh này — xem §4 |

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
VERSION=1.0.0                      # giá trị mẫu trong .env.example — xem ghi chú bên dưới

# Xác thực (docs/decisions.md D-AUTH-01 … D-AUTH-03)
SECRET_KEY=thay-bang-chuoi-ngau-nhien-xem-huong-dan-ben-duoi
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7        # đề xuất — CHƯA CHỐT (ND-40)
RESET_TOKEN_EXPIRE_MINUTES=30      # đề xuất 15–30 phút (.docx 3.4)
ALGORITHM=HS256                    # chỉ chấp nhận HS256 (D-AUTH-01)

# Email — quên mật khẩu, email kết quả ôn tập (T28)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
FRONTEND_URL=http://localhost:5173

# Cơ sở dữ liệu — cổng và tên DB CHƯA CHỐT (docs/structure.md §1.3), xem ghi chú bên dưới
DATABASE_URL=<giữ giá trị trong .env.example, sửa cho khớp PostgreSQL bạn đang chạy>

# AI
LLM_API_KEY=your-api-key
LLM_MODEL=ten-model

# Frontend (đặt trong frontend/.env — biến VITE_* bị lộ ra trình duyệt, không đặt bí mật ở đây)
VITE_API_BASE_URL=http://localhost:8000/api
VITE_USE_MOCK=false                # true = dùng dữ liệu mẫu src/mock/ khi chưa có backend (D-FE-07)
```

> Không commit file `.env`. Chỉ commit `.env.example`.

**Biến chưa thống nhất hoặc chưa có code đọc** (kiểm tra ngày 30/10/2026):

- `DATABASE_URL`: cổng và tên database **chưa được nhóm chốt** (`docs/structure.md` §1.3). Trong repo đang có hai dạng: `.env.example` dùng `postgresql+psycopg://…:5433/edumentor_db` (theo `docker-compose.yaml` của PR #1, nhánh `origin/Hoa`), còn bản hướng dẫn trước đây ghi `postgresql://…:5432/edumentor`. Không coi dạng nào là cấu hình chính thức; đặt giá trị khớp đúng host, cổng, tên database của PostgreSQL bạn đang chạy.
- `VERSION`, `ALGORITHM`: có trong `.env.example`. `backend/app/core/config.py` trên PR #1 (`origin/Hoa`) khai báo cả hai là biến bắt buộc, không có giá trị mặc định; trên nhánh này backend chưa có code nên chưa có gì đọc chúng. `ALGORITHM` chỉ được là `HS256` (D-AUTH-01).
- `REVIEW_PASS_PERCENT`: ngưỡng đạt bài ôn tập đã chốt là **≥ 60%** (D02; biến được nêu ở T28). Hiện `.env.example` **chưa có** biến này và **chưa có code nào đọc** nó, nên chưa cấu hình được — tồn đọng ở `docs/decisions.md` §5.

**Tạo `SECRET_KEY`:** khóa này dùng để ký JWT (HS256) — ai có khóa có thể giả mạo token của mọi người dùng. Tạo một chuỗi ngẫu nhiên đủ dài cho **mỗi** môi trường (máy cá nhân, server demo…), không dùng lại giá trị mẫu, không chia sẻ qua chat hay commit lên Git:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 4. Cơ sở dữ liệu

> **Hiện trạng:** nhóm chưa xác nhận cách tạo cơ sở dữ liệu.
> - `docker-compose.yml` trên nhánh này là file rỗng (0 byte), nên `docker compose` **chưa dùng được**. PR #1 (`origin/Hoa`) có file `docker-compose.yaml` riêng; tên file Compose, cổng và tên database chờ quyết định (G6; `docs/structure.md` §1.2, §1.3).
> - Nếu tự dựng PostgreSQL 14+ để thử, tạo user và database rồi đặt `DATABASE_URL` trong `.env` khớp đúng các giá trị bạn đã tạo (§3).

```sql
CREATE USER <db_user> WITH PASSWORD '<db_password>';
CREATE DATABASE <db_name> OWNER <db_user>;
```

## 5. Backend

> **Hiện trạng:** backend trên nhánh này chưa có code — `requirements.txt`, `alembic.ini`, `app/main.py`, `scripts/*.py` đều rỗng (`docs/structure.md` §1.1). Các lệnh dưới là quy trình dự kiến, **chưa chạy được** trên nhánh này.

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
npm run dev          # máy chủ phát triển
npm run build        # build production vào frontend/dist
npm run preview      # xem thử bản build
```

Truy cập `http://localhost:5173`. Khi backend chưa chạy, có thể đặt `VITE_USE_MOCK=true` trong `frontend/.env` để xem giao diện với dữ liệu mẫu; dữ liệu mẫu không phải API thật (D-FE-07).

## 7. Chạy kiểm thử

> **Hiện trạng:** `backend/tests/` chưa có test nào (file rỗng); `frontend/package.json` chưa có công cụ kiểm thử frontend.

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
| Chạy toàn bộ bằng Docker | Chưa dùng được — xem §4 |

## 9. Xử lý sự cố

- **Không kết nối được DB:** kiểm tra PostgreSQL đã chạy và `DATABASE_URL` khớp đúng host, cổng, tên database của instance đó (cổng và tên DB chưa chốt — §3).
- **Lỗi migration:** đảm bảo đã `git pull` và chạy `alembic upgrade head` trước khi tạo migration mới.
- **Lỗi gọi AI:** kiểm tra `LLM_API_KEY` và kết nối mạng.
- **Lỗi CORS ở frontend:** kiểm tra `VITE_API_BASE_URL` và cấu hình CORS trong `app/main.py`.
