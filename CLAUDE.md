# CLAUDE.md — EduMentor AI

Chỉ thị cho Claude Code trong repo này. Ngắn gọn có chủ đích; nghiệp vụ nằm trong tài liệu nguồn bên dưới.

## Project

EduMentor AI — nền tảng cố vấn học tập cá nhân hóa: lộ trình học bằng AI, gợi ý khóa học MOOC theo kỹ năng, AI Tutor, AI tư vấn khóa học, ôn tập ghi nhận kỹ năng. Ba vai trò: Khách, Học viên (`student`), Admin (`admin`).

## Cách làm việc với Tuấn (quan trọng)

- Tuấn **tự viết code** để học. Claude hướng dẫn, đưa khung/gợi ý, giải thích, review và chỉ lỗi — **không viết thay toàn bộ** tính năng trừ khi được yêu cầu rõ.
- Tuấn phụ trách: **01 Tài khoản & hồ sơ** và **09 Ôn tập**. Không sửa code module của người khác (Khôi, Tâm, Hòa — xem `README.md`); nếu cần thay đổi ở đó thì nêu ra.
- Tài liệu cũ do AI sinh (`docs/decisions.md`, `docs/structure.md`, `docs/modules/*`, mã `ND-xx`, `D-AUTH-xx`, `AP-Rxx`…) **đã bỏ**. Không tham chiếu chúng.
- Khi tài liệu nguồn chưa nói rõ: hỏi Tuấn, không tự chọn nghiệp vụ.

## Tài liệu nguồn

| Nội dung | File |
|---|---|
| Nghiệp vụ, vai trò, đặc tả API | `EdumentorAi_BA_v3.md` |
| Yêu cầu chức năng / phi chức năng | `AI_Learning_Assistant_Recommender_SRS_v3.md` |
| Danh sách endpoint | `api-endpoints.md` |
| Thiết kế CSDL | `docs/database-design.md` (đang là khung, chưa chốt) |
| Giao diện chuẩn (~40 màn, route, endpoint mỗi màn) | `docs/EduMentor-UI-design/ui-design/` |
| Kế hoạch code tay | `docs/Auth-EduMentor AI.md` |
| Kế hoạch + tiến độ 01 Tài khoản & Hồ sơ (Claude review) | `docs/Review-Auth.md` |
| Kế hoạch + tiến độ 09 Ôn tập & Đánh giá (Claude review) | `docs/Review-Assessment.md` |
| Quy ước API, lỗi, Git | `docs/conventions.md` |
| Cài đặt backend | `SETUP_BACKEND.md` |

## Công nghệ (theo code thực tế)

- Backend: Python 3.11+, FastAPI, SQLAlchemy 2 (**sync** `Session`), Pydantic v2 + pydantic-settings, PostgreSQL 16 qua Docker (`localhost:5433`, DB `edumentor_db`).
- Bảng đang tạo bằng `Base.metadata.create_all` lúc khởi động; Alembic có khung (`alembic/env.py`) nhưng `alembic.ini` chưa cấu hình — nhóm chưa chốt chuyển sang migration.
- Auth: `bcrypt` (băm mật khẩu), `pyjwt` (JWT) — đã có trong `backend/requirements.txt`.
- Frontend: React + Vite, Axios.
- Test: `pytest`. Format: `black`, `ruff`.

## Kiến trúc backend

`backend/app/`: Router → Service → Repository → Model, Schema Pydantic cho vào/ra. Mỗi module cùng một tên ở mọi lớp.

- `routers/v1/endpoints/<module>.py` (admin: `endpoints/admin/`) — chỉ nhận request, gọi service, đổi lỗi thành `HTTPException`. Gắn router trong `routers/v1/api.py` (prefix `/api`).
- `services/<module>_service.py` — nghiệp vụ, `commit`/`rollback`.
- `repositories/<module>_repository.py` — chỉ truy vấn DB.
- `models/` — SQLAlchemy, import trong `models/__init__.py` để `create_all` thấy.
- `schemas/` — Pydantic; response không bao giờ chứa `hashed_password` hay token gốc.
- `core/` — `config`, `database`, `security`, `dependencies` (`get_current_user`, `require_admin`), `errors`, `pagination`, `email`.

Nhiều file hiện là khung rỗng (docstring + TODO) — không có nghĩa tính năng đã xong.

## Ghi chú môi trường

- Seed dữ liệu của Hòa (`core/seed_data/`, đọc `../datajson/*.json` ngoài repo) **đang được ngắt** trên nhánh `tuan/future-auth`; router/model Learning Path & Skill của Hòa cũng chưa gắn. Sẽ gộp lại sau với nhóm.
- Không commit `.env`; không hard-code bí mật.

## Lệnh

```powershell
docker compose up -d                                    # Postgres
.\.venv\Scripts\Activate.ps1
cd backend; uvicorn app.main:app --reload               # http://localhost:8000/api/docs
pytest                                                  # trong backend/
black . ; ruff check .
```

Commit: `<loại>(<phạm vi>): <mô tả>` (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`). Không commit/push khi Tuấn chưa yêu cầu.
