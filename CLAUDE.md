# CLAUDE.md — EduMentor AI

Chỉ thị cấp project cho Claude Code. File này **không** chứa quy tắc nghiệp vụ; quy tắc nằm trong `docs/` (xem bản đồ bên dưới).

## Project

EduMentor AI — nền tảng cố vấn học tập cá nhân hóa: lộ trình học bằng AI, gợi ý khóa học MOOC bên ngoài theo kỹ năng, AI Tutor, và ghi nhận kỹ năng qua bài ôn tập. Tổng quan: `README.md`.

Trạng thái hiện tại: **chưa có code** — các file trong `backend/` và `frontend/` chỉ là file rỗng giữ chỗ. Đừng suy luận nghiệp vụ từ code; đọc tài liệu.

## Công nghệ

- Backend: Python 3.11+, FastAPI, SQLAlchemy, Alembic, Pydantic, PostgreSQL 14+.
- Frontend: React + Vite.
- Kiểm thử: `pytest`. Định dạng: `black`, `ruff`.
- Cài đặt và lệnh thường dùng: `SETUP.md`.

## Kiến trúc

Router → Service → Repository → Model, Schema (Pydantic) cho dữ liệu vào/ra. Router không viết truy vấn hay nghiệp vụ; service giữ quy tắc nghiệp vụ và transaction; repository chỉ truy vấn; thay đổi CSDL chỉ qua Alembic migration. Chi tiết: `STRUCTURE.md` §4 và `docs/backend-rules.md`. Không đổi kiến trúc này nếu không được yêu cầu.

## Nguồn sự thật

| Chủ đề | File |
|---|---|
| Quyết định đã chốt, mâu thuẫn, `[NEEDS DECISION]` | `docs/decisions.md` |
| Thiết kế CSDL (chính thức) | `docs/database-design.md` |
| Danh sách endpoint toàn hệ thống | `docs/api-endpoints.md` |
| Cây thư mục, ánh xạ endpoint → file | `STRUCTURE.md` |
| Quy ước API, code, Git, kiểm thử | `CONVENTIONS.md` |
| Quy tắc backend dùng chung (lỗi, transaction, bảo mật, cấu hình) | `docs/backend-rules.md` |
| Đặc tả + contract module Xác thực & Hồ sơ | `docs/modules/auth-profile.md` (+ `.tests.md`) |
| Đặc tả + contract module Ôn tập & Đánh giá | `docs/modules/review-assessment.md` (+ `.tests.md`) |
| Giao diện tham khảo | `docs/wireframes/` (không phải nguồn quy tắc API) |

Nguồn gốc nghiệp vụ mới nhất là `docs/EduMentor_Database_Design_Da_Sua.docx` và `docs/EduMentor_Checklist_Da_Sua_API.xlsx` (đã được chép vào các file `.md` trên). Thứ tự ưu tiên khi mâu thuẫn: `docs/decisions.md` §1.

## Phạm vi đang phụ trách

Chỉ hai module có bộ tri thức đầy đủ và skill riêng:

1. **Xác thực & Hồ sơ người dùng** → skill `auth-profile`
2. **Ôn tập & Đánh giá kiến thức** → skill `review-assessment`

Các module khác (Course Tracking, Learning Path, AI Consultant/Tutor, Recommendation, Admin) không thuộc phạm vi: không tự sửa file của chúng; nếu việc đang làm cần thay đổi ở đó, nêu ra cho người dùng.

## Quy tắc làm việc

- **Không tự suy diễn nghiệp vụ.** Khi tài liệu chưa quy định, hoặc mục đó đang là `[NEEDS DECISION]` trong `docs/decisions.md`: dừng và hỏi người dùng, hoặc chỉ làm phần không phụ thuộc rồi nói rõ chỗ còn chờ. Không chọn "phương án hợp lý" thay nhóm.
- Không thêm endpoint, bảng, cột, ràng buộc, cơ chế bảo mật hay thư viện ngoài tài liệu.
- Hạng mục chưa được nhóm tick (☐) trong `docs/decisions.md` §3 không được coi là đã chốt.
- Phát hiện tài liệu thiếu hoặc mâu thuẫn → đề xuất bổ sung `ND-xx` vào `docs/decisions.md`; không vá bằng code.
- Khi một quyết định được chốt: cập nhật `docs/decisions.md` trước, rồi mới sửa tài liệu module và code.
- Mỗi quy tắc chỉ được ghi ở **một** file; file khác tham chiếu mã (`D05`, `T13`, `AP-R14`, `RV-R07`, `ND-24`) thay vì chép lại.
- Không commit `.env`; không hard-code bí mật hay ngưỡng nghiệp vụ.

## Cách dùng skill và tài liệu

- Công việc thuộc một trong hai module trên → dùng skill tương ứng (`.claude/skills/auth-profile`, `.claude/skills/review-assessment`). Skill cho biết cần đọc phần nào của `docs/` và theo thứ tự nào; đọc đúng phần cần cho việc đang làm.
- Hai skill project này được ưu tiên hơn các skill cấp user có phạm vi tương tự (`edumentor-auth-profile`, `edumentor-review`, `database-schema`) khi làm việc trong repo này.
- Đụng tới CSDL → `docs/database-design.md`. Đụng tới lỗi, transaction, xác thực dùng chung → `docs/backend-rules.md`.

## Lệnh

```bash
cd backend && pytest                                  # kiểm thử
black . && ruff check .                               # định dạng
alembic revision --autogenerate -m "mo ta"            # migration mới
alembic upgrade head                                  # áp dụng migration
```

Commit: `<loại>(<phạm vi>): <mô tả>` (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`); nhánh `feature/<nhóm>-<mô-tả>`. Chi tiết: `CONVENTIONS.md` §5.
