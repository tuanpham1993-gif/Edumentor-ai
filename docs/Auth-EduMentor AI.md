# Kế hoạch code tay EduMentor AI

Nov 5, 2026 · @TuanPham

## Mục tiêu và căn cứ

Bạn tự code tay từng chức năng; mình chuẩn bị trước cho mỗi chức năng: bảng dữ liệu, API, khung code mẫu và danh sách test. Bỏ `docs/decisions.md` và các file do AI tự sinh trước đó, làm lại từ 3 nguồn:

- **BA** (`EdumentorAi_BA.md`): vai trò, các tình huống sử dụng, quy tắc nghiệp vụ, đặc tả API.
- **SRS** (`AI_Learning_Assistant_Recommender SRS`): yêu cầu chức năng và phi chức năng.
- **UI demo** (`docs/EduMentor-UI-design/ui-design`): khoảng 40 màn hình, mỗi màn có route, vai trò và endpoint cần gọi.

Ba vai trò: **Khách** (chưa đăng nhập: đăng nhập, đăng ký, quên mật khẩu, xem khóa học, liên hệ bị khóa), **Học viên** (User trong BA) và **Admin**. Công nghệ: FastAPI, SQLAlchemy, Alembic, PostgreSQL, React + Vite.

Câu hỏi mở: kế hoạch này cho phần của bạn hay cả nhóm, và hạn nộp là ngày nào?

## Giai đoạn 0: chuẩn bị nền (1 đến 2 ngày)

Mục tiêu: chạy được backend rỗng nối vào Postgres, frontend gọi được `/api/health`.

- [ ] Đồng bộ code ở máy lên GitHub (repo đang thiếu nhiều file backend so với máy bạn).
- [ ] Dọn các file rỗng và code do AI sinh mà bạn không dùng.
- [ ] Chạy Postgres bằng `docker-compose`, tạo `.env` (DATABASE\_URL, SECRET\_KEY).
- [ ] Cấu hình Alembic, tạo migration đầu tiên từ các model đã có (Skill, Course, SkillRelation, LearningPath).
- [ ] Viết khung dùng chung: `core/config.py`, `core/database.py`, `core/errors.py` (định dạng lỗi chung), `core/pagination.py`.
- [ ] Chốt cấu trúc mỗi module: Router → Service → Repository → Model, Schema Pydantic riêng.
- [ ] Script seed dữ liệu mẫu (kỹ năng, khóa học) để có dữ liệu test.

Mình chuẩn bị: sơ đồ cơ sở dữ liệu tổng thể (các bảng và quan hệ) lấy từ đặc tả API trong BA, để bạn duyệt trước khi code model.

## Giai đoạn 1: tài khoản và phân quyền

Làm trước vì mọi chức năng sau đều cần biết ai đang đăng nhập và vai trò gì (các màn đăng nhập, đăng ký, quên mật khẩu, hồ sơ, kỹ năng, đăng xuất).

| Thứ tự | Chức năng | API chính | Màn UI |
| --- | --- | --- | --- |
| 1 | Model User, migration. Vai trò: Khách (chưa đăng nhập, không lưu trong bảng User), Học viên (role = student), Admin (role = admin) | Không có API riêng. Đăng ký luôn tạo role = student; tài khoản admin tạo bằng script create\_admin.py, không tạo qua API công khai | — |
| 2 | Đăng ký, đăng nhập (JWT, băm mật khẩu) | `POST /api/auth/register`, `POST /api/auth/login` | Đăng nhập, Đăng ký |
| 3 | Lấy user hiện tại, chặn theo vai trò | `get_current_user`, `require_admin` | — |
| 4 | Hồ sơ, sửa họ tên, đổi mật khẩu | `GET/PATCH /api/me`, `POST /api/me/password` | Hồ sơ, Sửa hồ sơ, Đổi mật khẩu |
| 5 | Kỹ năng của tôi | `GET/PATCH /api/me/skills` | Kỹ năng của tôi |
| 6 | Đăng xuất, quên/đặt lại mật khẩu | `POST /api/auth/logout`, `forgot-password`, `reset-password` | Quên mật khẩu, Đặt lại mật khẩu, Đăng xuất |
| 7 | Frontend: lưu token, chặn route theo vai trò | — | tất cả |

Gợi ý đơn giản hóa khi code tay: bản đầu chỉ dùng access token (chưa cần refresh token), quên mật khẩu để sau cùng vì cần gửi email.

## Giai đoạn 2: khóa học, kỹ năng và quản trị

Đây là dữ liệu nền mà lộ trình, gợi ý và ôn tập đều dùng, nên làm trước phần AI.

| Thứ tự | Chức năng | Vai trò | Màn UI |
| --- | --- | --- | --- |
| 1 | Admin: CRUD kỹ năng và quan hệ tiên quyết | Admin | Quản trị kỹ năng |
| 2 | Admin: CRUD khóa học, gắn kỹ năng cho khóa | Admin | Quản trị khóa học |
| 3 | Danh mục khóa học: tìm, lọc cấp độ, sắp xếp, phân trang | Khách, Học viên | Danh mục khóa học, Chi tiết khóa học |
| 4 | Lưu và theo dõi khóa học: bookmarked, ongoing, completed, abandoned | Học viên | Tham gia khóa học, Khóa học của tôi |
| 5 | Liên hệ, phản hồi và admin xem phản hồi | Khách xem, Học viên gửi, Admin quản lý | Liên hệ, Liên hệ khi chưa đăng nhập, Quản trị phản hồi |

Mốc kiểm tra: admin tạo được khóa học, khách thấy nó trong danh mục, học viên lưu và tham gia được. Đây là bản demo đầu tiên có đủ 3 vai trò.

## Giai đoạn 3: lộ trình, AI và ôn tập

Phần khó nhất, làm sau khi có dữ liệu khóa học và kỹ năng. Mỗi chức năng AI làm bản giả lập (trả dữ liệu cố định) trước, nối mô hình thật sau.

| Thứ tự | Chức năng | Màn UI |
| --- | --- | --- |
| 1 | Ôn tập: 20 câu trắc nghiệm theo khóa, chấm điểm, đạt thì khóa thành completed và cập nhật kỹ năng | Bắt đầu ôn tập, Làm bài, Kết quả, Lịch sử ôn tập |
| 2 | Lộ trình: xem, đổi tên, thêm/xóa node và cạnh, từ bỏ | Lộ trình của tôi, Chi tiết lộ trình, Sửa lộ trình |
| 3 | Gợi ý khóa học theo node kỹ năng | Chi tiết lộ trình |
| 4 | AI Consultant: mục tiêu → bản nháp lộ trình → người dùng xác nhận mới lưu | AI tư vấn lộ trình |
| 5 | AI Tutor: phiên chat, giải thích, tạo câu hỏi | AI Tutor |
| 6 | Admin: mẫu lộ trình, dữ liệu lịch sử, xem lộ trình người dùng | Mẫu lộ trình, Dữ liệu lịch sử, Lộ trình người dùng |

Ôn tập đứng đầu vì không phụ thuộc AI, chỉ cần ngân hàng câu hỏi do admin nhập hoặc seed.

## Bổ sung sau khi đối chiếu 14 tính năng

Workbook 14 tính năng còn thiếu 6 điểm so với BA và UI demo:

| Điểm bổ sung | Vì sao cần | Đặt vào giai đoạn |
| --- | --- | --- |
| Quản trị ngân hàng câu hỏi ôn tập | Không có câu hỏi thì Ôn tập không chạy | 3 (trước Ôn tập) |
| Mẫu lộ trình cơ sở | AI Consultant dùng làm khung | 3 |
| Dữ liệu lịch sử | Nguồn cho gợi ý lộ trình | 3 |
| Phần nền dùng chung: xác thực, lỗi, phân trang, CORS, Alembic, seed, tạo admin, gửi email | Mọi tính năng đều phụ thuộc | 0 |
| Luồng ôn tập đạt → khóa completed → kỹ năng known → tiến độ lộ trình | Đi qua 3 người, cần hợp đồng chung | 3 |
| Thuật toán lọc và xếp hạng khóa học | Tính năng gợi ý mới có endpoint | 3 |

Cần chốt trước khi code: quyền của Khách (xem danh mục và chi tiết khóa học?), sync hay async cho DB, cấu trúc router, thư viện JWT, chuỗi kết nối DB. Bong bóng chat AI tư vấn khóa học chưa có người làm và chưa có API.

## Quy trình cho mỗi chức năng

Với mỗi dòng trong các bảng trên, mình chuẩn bị gói "sẵn sàng code", bạn code tay theo đúng thứ tự:

1. **Đặc tả ngắn** (mình viết): lấy từ BA và UI demo, gồm quy tắc nghiệp vụ, trường dữ liệu, mã lỗi. Bạn duyệt.
2. **Model + migration** (bạn code): bảng, khóa ngoại, ràng buộc.
3. **Schema Pydantic**: request và response.
4. **Repository → Service → Router**: truy vấn DB, logic nghiệp vụ, endpoint.
5. **Test** (mình viết danh sách ca test, bạn code): chạy `pytest` và thử trên Swagger `/docs`.
6. **Frontend**: nối màn UI tương ứng vào API thật.
7. **Review**: bạn gửi code, mình xem và góp ý, rồi commit.

Bước đầu tiên khi bạn duyệt kế hoạch: mình làm sơ đồ cơ sở dữ liệu tổng thể và gói chuẩn bị cho Giai đoạn 0.
