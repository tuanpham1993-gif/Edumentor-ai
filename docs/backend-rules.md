# Quy tắc backend dùng chung — Xác thực/Hồ sơ và Ôn tập/Đánh giá

Tài liệu này gom các quy tắc kỹ thuật mà **cả hai** module cùng tuân theo, để `docs/modules/*.md` không phải lặp lại. Mọi nội dung truy xuất từ `docs/structure.md` §4, `docs/conventions.md`, `SETUP.md`, `docs/api-endpoints.md` §14 và `docs/database-design.md`. Điểm còn mở trỏ tới `docs/decisions.md`.

---

## 1. Phân lớp

```text
HTTP request
   │
   ▼
routers/      Nhận request, gắn dependency (xác thực, DB session), gọi service, trả response.
   │          Không viết truy vấn, không chứa quy tắc nghiệp vụ.
   ▼
services/     Quy tắc nghiệp vụ và ranh giới transaction.
   │
   ▼
repositories/ Chỉ truy vấn CSDL. Không chứa quy tắc nghiệp vụ.
   │
   ▼
models/       SQLAlchemy ORM — mô tả bảng đúng theo docs/database-design.md.
   │
   ▼
PostgreSQL    Thay đổi cấu trúc chỉ qua Alembic migration.

schemas/  ⇄  API   Pydantic: kiểm tra dữ liệu vào và định hình dữ liệu ra.
```

Nguồn: STRUCTURE §4, CONVENTIONS §3.

| Thư mục | Vai trò | Ghi chú cho 2 module |
|---|---|---|
| `core/config.py` | Đọc biến môi trường | Mọi bí mật, ngưỡng, thời hạn lấy từ đây; không hard-code |
| `core/database.py` | Engine, session, transaction helper | Lớp nào commit: `[NEEDS DECISION ND-16]` |
| `core/security.py` | Băm mật khẩu, tạo/kiểm tra token | JWT HS256 (D-AUTH-01), Argon2id (D-AUTH-04); thư viện: `[NEEDS DECISION ND-44, ND-45]` |
| `core/dependencies.py` | `get_current_user`, `require_admin`, `get_db` | Mọi endpoint người dùng dùng `get_current_user` |
| `core/errors.py` | Exception chung + handler lỗi thống nhất | Mục 4 |
| `core/pagination.py` | Tham số và response phân trang | Mục 5 |
| `core/email.py` | `send_email` dùng chung | Dùng cho quên mật khẩu (T01) và email kết quả ôn tập (T29). Mục 7 |
| `routers/` | Lớp HTTP | `auth.py`, `me.py`, `reviews.py` |
| `schemas/` | Pydantic | `auth.py`, `user.py`, `review.py`, `common.py` |
| `models/` | ORM | Tên file theo bảng trong `database-design.md` |
| `repositories/` | Truy vấn | STRUCTURE chưa liệt kê tên file; một repository cho mỗi nhóm bảng mà service cần |
| `services/` | Nghiệp vụ, transaction | `auth_service.py`, `user_service.py`, `review_service.py` |

---

## 2. Xác thực và phân quyền

- Endpoint người dùng yêu cầu xác thực; endpoint `/api/admin/*` yêu cầu `role = admin`. (api-endpoints §14)
- Endpoint `/api/me/...` chỉ thao tác trên dữ liệu của **người dùng đã xác thực**; không bao giờ nhận `user_id` từ client. (CONVENTIONS §1)
- Thiếu token / token không hợp lệ → **401**. Đã xác thực nhưng không đủ quyền (ví dụ không phải admin) → **403**. (CONVENTIONS §1)
- Frontend ẩn giao diện theo quyền (`ProtectedRoute`, `AdminRoute`), nhưng **backend vẫn phải tự kiểm tra quyền**. (STRUCTURE §3)
- Cơ chế token (chi tiết: `docs/modules/auth-profile.md` AP-R21, AP-R22):
  - Access token: JWT HS256 ký bằng `SECRET_KEY`, claim `sub`/`iat`/`exp`, hết hạn 30 phút, gửi qua `Authorization: Bearer <access_token>`; backend chỉ chấp nhận HS256 và lấy vai trò từ database. (D-AUTH-01, D-AUTH-02)
  - Refresh token: lưu bản băm trong PostgreSQL, rotation khi làm mới, logout thu hồi. Access token không thu hồi tức thì được. (D-AUTH-03; còn mở ND-40 … ND-43, ND-48)

### Quyền sở hữu tài nguyên (chống IDOR)

- Tài nguyên thuộc người dùng khác (ví dụ một `ReviewAttempt`) → trả **404**, không trả 403, để không lộ sự tồn tại. (T15, `.docx` 6.2)
- Luôn lọc theo người dùng hiện tại **trong truy vấn** (ví dụ attempt → StudentCourse → `user_id`), không tải bản ghi rồi mới so sánh ở router.

---

## 3. Transaction

- Mọi thao tác sửa nhiều bản ghi liên quan phải nằm trong **một transaction**; lỗi ở bất kỳ bước nào → rollback toàn bộ. (CONVENTIONS §3, api-endpoints §14)
- Ranh giới transaction thuộc lớp **service**. (STRUCTURE §4)
- Thao tác có tác dụng phụ bên ngoài (gửi email) **không** nằm trong transaction; chỉ chạy **sau khi commit thành công**. (T29)
- Kiểm tra request body, ID, giá trị trạng thái và tham chiếu **trước khi ghi**. (CONVENTIONS §3)

Các transaction cụ thể của từng module được liệt kê trong file module tương ứng.

---

## 4. Lỗi

Cấu trúc lỗi thống nhất (CONVENTIONS §1):

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Mô tả lỗi dễ hiểu",
    "details": []
  }
}
```

| HTTP | Khi nào |
|---|---|
| 400 / 422 | Dữ liệu đầu vào không hợp lệ (chọn 400 hay 422 khi tài liệu chưa ghi rõ: `[NEEDS DECISION ND-15]`) |
| 401 | Chưa xác thực |
| 403 | Không đủ quyền |
| 404 | Tài nguyên không tồn tại, **hoặc** thuộc người dùng khác |
| 409 | Chuyển trạng thái xung đột, dữ liệu trùng |
| 413 / 415 | File quá lớn / sai định dạng (upload avatar) |

- Danh mục giá trị `error.code`: `[NEEDS DECISION ND-14]`.
- Khi một endpoint đã có mã lỗi được ghi rõ trong tài liệu module, dùng đúng mã đó.
- Không trả stack trace, câu SQL, mật khẩu, mã băm hay token trong response lỗi.

---

## 5. Phân trang

Endpoint trả danh sách nhận `page` và `page_size`, trả về `items`, `total`, `page`, `page_size`. (CONVENTIONS §1) Giá trị mặc định và giới hạn `page_size` chưa được tài liệu quy định.

---

## 6. Cấu hình (biến môi trường)

| Biến | Dùng cho | Nguồn |
|---|---|---|
| `SECRET_KEY` | Ký JWT (HS256). Chuỗi ngẫu nhiên đủ mạnh, mỗi môi trường một giá trị riêng, không commit; cách tạo: `SETUP.md` §3 | SETUP §3, D-AUTH-01 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Thời hạn access token = **30** | D-AUTH-02 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Thời hạn refresh token — đề xuất 7, **chưa chốt** `[NEEDS DECISION ND-40]` | D-AUTH-03 |
| `DATABASE_URL` | Kết nối CSDL | SETUP §3 |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | Gửi email | T28 |
| `FRONTEND_URL` | Link trong email (đặt lại mật khẩu, xem kết quả ôn tập) | T28 |
| `RESET_TOKEN_EXPIRE_MINUTES` | Hạn mã đặt lại mật khẩu (đề xuất 15–30 phút) | T28, `.docx` 3.4 |
| `REVIEW_PASS_PERCENT` | Ngưỡng đạt bài ôn tập (nhóm chốt 60) | D02, T28 |

Không commit `.env`; chỉ commit `.env.example`. (SETUP §3)

---

## 7. Email

- Một hàm `send_email` trong `core/email.py`, dùng chung cho quên mật khẩu và email kết quả ôn tập. (T29)
- Email kết quả ôn tập chạy nền bằng FastAPI `BackgroundTasks` sau khi commit; gửi lỗi chỉ ghi log, không rollback, không báo lỗi cho người dùng. (T29)
- Email không chứa mật khẩu, mã băm hay đáp án bài ôn tập. (`.docx` 3.4, 6.2)

---

## 8. Dữ liệu nhạy cảm

- Không lưu mật khẩu gốc; không trả `hashed_password` trong bất kỳ response nào. (`.docx` 3.1)
- Mã đặt lại mật khẩu chỉ lưu dạng băm (`token_hash`). (`.docx` 3.4)
- Refresh token chỉ lưu dạng băm. (D-AUTH-03)
- Không ghi mật khẩu, `confirm_password`, access token, refresh token hay mã đặt lại mật khẩu (dạng gốc) vào log. (D-AUTH-05)
- `correct_index` và `explanation` không xuất hiện ở endpoint làm bài trước khi nộp. (T15)
- Không hard-code bí mật. (CONVENTIONS §3)

---

## 9. CSDL và migration

- Model khớp đúng `docs/database-design.md` (tên cột, kiểu, NN/UQ/CHECK, FK và ON DELETE).
- Bảng `User` đặt tên thật là `users`. (`.docx` §0)
- Mọi thay đổi cấu trúc qua Alembic migration, không sửa tay trên DB. (CONVENTIONS §3)
- Index ngoài PK/UQ: `[NEEDS DECISION ND-17]`.

---

## 10. Quy ước code và kiểm thử

- PEP 8, `black`, `ruff`; file/hàm/biến `snake_case`, class `PascalCase`, hằng số `UPPER_SNAKE_CASE`. (CONVENTIONS §3)
- Mỗi nhóm endpoint có file test trong `backend/tests/`; chạy `pytest` trước khi tạo Pull Request. (CONVENTIONS §6)
- Commit theo dạng `<loại>(<phạm vi>): <mô tả>`; nhánh `feature/<nhóm>-<mô-tả>`. (CONVENTIONS §5)
