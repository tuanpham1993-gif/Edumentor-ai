# Quyết định & điểm chưa chốt — Xác thực/Hồ sơ và Ôn tập/Đánh giá

Đây là **nơi duy nhất** ghi quyết định nghiệp vụ và các điểm còn mở của 2 module:

- Xác thực & Hồ sơ người dùng (`docs/modules/auth-profile.md`)
- Ôn tập & Đánh giá kiến thức (`docs/modules/review-assessment.md`)

Các tài liệu khác chỉ tham chiếu mã (`D05`, `T13`, `ND-24`…), không chép lại nội dung. Khi một `ND-xx` được chốt: chuyển nó sang mục 2, sửa tài liệu bị ảnh hưởng, rồi mới code.

---

## 1. Nguồn sự thật

Thứ tự ưu tiên khi các nguồn khác nhau, cho 2 module trên:

1. `docs/EduMentor_Database_Design_Da_Sua.docx` và `docs/EduMentor_Checklist_Da_Sua_API.xlsx` (bản đã sửa, D01–D11 đã chốt) — **nguồn nghiệp vụ mới nhất**. Đã được chép vào `docs/database-design.md` và `docs/api-endpoints.md`.
2. `docs/structure.md` (trước đây là `STRUCTURE.md` ở root) — nguồn kiến trúc nền (phân lớp Router → Service → Repository → Model, cây thư mục).
3. `docs/conventions.md` (trước đây là `CONVENTIONS.md` ở root), `SETUP.md`, `README.md`.
4. Wireframe trong `docs/wireframes/` — chỉ mô tả giao diện; **không** tạo quy tắc API khi chưa có trong 1–3.

Không tự tạo quy tắc khi tài liệu chưa quy định → ghi `[NEEDS DECISION]` ở mục 4.

Hạng mục trong file `.xlsx` mà nhóm **chưa tick đồng ý** (☐) không được coi là đã chốt, kể cả khi file `.docx` đã ghi nội dung đó — xem mục 3.

---

## 2. Quyết định đã chốt (D01–D11)

Nguồn: sheet "Quyết định cần chốt" — tất cả đã tick "Đã chốt".

| Mã | Câu hỏi | Đã chọn | Ảnh hưởng tới module |
|---|---|---|---|
| D01 | Ôn tập theo khóa học hay kỹ năng? | **A — theo khóa học**: `/api/courses/{course_id}/review…`; 20 câu lấy từ các kỹ năng của khóa | Review |
| D02 | Điểm đạt tối thiểu? | **Khác — ≥ 60%** (biến `REVIEW_PASS_PERCENT`) | Review |
| D03 | Làm lại? Tiếp tục bài dở? | **A — không giới hạn**; mỗi khóa tối đa 1 bài đang dở; bắt đầu lại trả bài dở đó | Review |
| D04 | 20 câu lấy từ đâu khi khóa dạy nhiều kỹ năng? | **A — gộp câu của tất cả kỹ năng khóa dạy, tổng ≥ 20; chia đều giữa các kỹ năng** | Review |
| D05 | `UserSkill.status = learning` đặt khi nào? | **A — khi bấm Tham gia khóa (join)**: thêm kỹ năng của khóa ở `learning` nếu chưa `known` | Auth/Profile (bảng UserSkill) ↔ Course Tracking |
| D06 | Cho đổi email? | **A — không** (ô email chỉ đọc) | Auth/Profile |
| D07 | Ảnh đại diện: upload hay URL? | **B — tải file lên server** (`POST /api/me/avatar`); T04 ghi: giai đoạn 1 nhập URL qua `PATCH /api/me`, giai đoạn 2 upload | Auth/Profile |
| D08 | Đăng xuất hoạt động thế nào? | **A — JWT không lưu trạng thái**: client xóa token, server trả 200; không có bảng thu hồi token. **Đã bị D-AUTH-03 thay thế một phần (2026-10-24):** access token vẫn stateless, nhưng logout nay phải thu hồi refresh token lưu trong PostgreSQL | Auth/Profile |
| D09 | Làm quên mật khẩu trong bản đầu? | **A — có** (T01, T02, T28) | Auth/Profile |
| D10 | Khóa đã completed có cho ôn lại? | **B — có**: kết quả mới chỉ lưu thêm vào lịch sử, không đổi `completed` | Review |
| D11 | Danh sách "Loại phản hồi" | A (ghi "không làm") | Ngoài phạm vi |

### Phân công (ownership) — quyết định chính thức

**D-OWN-01** (Tuấn xác nhận, 2026-10-24): **Tuấn phụ trách chính thức hai module Xác thực & Hồ sơ người dùng và Ôn tập & Đánh giá kiến thức.** Quyết định này thay cho mọi thông tin phân công cũ.

| Module | Owner | Trạng thái đặc tả | Implementation | Nguồn |
|---|---|---|---|---|
| Xác thực & Hồ sơ (Auth & Profile) | **Tuấn** | SPEC CONFIRMED (một số quyết định bảo mật/nghiệp vụ còn PENDING — §4.1) | NOT IMPLEMENTED | D-OWN-01 |
| Ôn tập & Đánh giá (Review & Assessment) | **Tuấn** | SPEC CONFIRMED (một số quy tắc BLOCKED/PENDING — §3 T16, §4.2) | NOT IMPLEMENTED | D-OWN-01; sheet Endpoint "Phụ trách = Tuấn" |
| Course Tracking (`/api/me/courses*`, `/api/me/bookmarks*`, `join`) | Không phải Tuấn | OUT OF SCOPE | — | ND-SCOPE-3 (Giai đoạn 2); sheet Endpoint ghi Hòa cho `/api/me/courses*` |
| Feedback & liên hệ (T22–T25) | Chưa rõ: sheet Endpoint ghi Khôi, sheet "Danh sách thay đổi" ghi Tâm | PENDING | — | ND-35 |
| Learning Path (gồm cập nhật trạng thái sau ôn tập — T18) | Người khác (T18 ghi Tâm) | OUT OF SCOPE | — | T18 |
| Quản trị câu hỏi `/api/admin/questions*` (T19–T21) | **CONFLICT**: sheet Endpoint ghi Tuấn; Tuấn đã loại khỏi phạm vi skill (ND-SCOPE-2) | DO NOT ASSUME | — | CONFLICT-SCOPE-01 |

Quy ước trạng thái: **SPEC CONFIRMED** = phạm vi/quy tắc đã được xác nhận; **IMPLEMENTED** = đã có code chạy; **PENDING** = còn quyết định chưa chốt; **BLOCKED** = bị chặn bởi quyết định khác; **CONFLICT** = các nguồn mâu thuẫn. Không dùng "DONE" cho phần chưa có code.

> **Ghi chú lịch sử (giữ để audit):** sheet "Endpoint (bản mới)" của `EduMentor_Checklist_Da_Sua_API.xlsx` ghi "Phụ trách = Hòa" cho toàn bộ §2, còn sheet "Danh sách thay đổi" ghi T01–T10 "Phụ trách đề xuất = Tuấn". Lần đồng bộ skill Giai đoạn 2.2 đánh dấu điểm này là CONFLICT-OWN-01. **Đã giải quyết bằng D-OWN-01** — cột "Phụ trách" của §2 trong Excel là thông tin cũ (stale), cần nhóm cập nhật trong Excel.

### Quyết định xác thực (D-AUTH-01 … D-AUTH-05)

Tuấn (owner Auth & Profile, D-OWN-01) xác nhận ngày 2026-10-24, thay cho phần tương ứng của ND-01 … ND-05. Chi tiết còn mở được tách thành `ND-40` … `ND-48` (§4.1). Không phần nào ở đây đã được implement.

| Mã | Thay cho | Nội dung đã xác nhận | Còn mở |
|---|---|---|---|
| D-AUTH-01 | ND-01 | Xác thực bằng **JWT access token**, ký **HS256** bằng `SECRET_KEY` (biến môi trường; chuỗi ngẫu nhiên đủ mạnh; không commit lên Git). Client gửi qua header `Authorization: Bearer <access_token>`. JWT chứa claim chuẩn `sub` (user_id), `iat`, `exp`. Backend xác minh chữ ký, thời hạn và **chỉ chấp nhận thuật toán HS256**. Người dùng hiện tại và **vai trò được lấy từ database** khi kiểm tra quyền — không chỉ dựa vào claim vai trò trong JWT. Frontend đang định hướng lưu token trong `sessionStorage` (ghi nhận rủi ro ở `docs/modules/auth-profile.md` §8; không thay đổi khi chưa được phê duyệt). | ND-44 (thư viện JWT) |
| D-AUTH-02 | ND-02 | Access token hết hạn sau **30 phút** (`ACCESS_TOKEN_EXPIRE_MINUTES=30`). Backend từ chối access token hết hạn. Khi access token hết hạn, frontend thử làm mới phiên bằng refresh token; chỉ yêu cầu đăng nhập lại khi làm mới thất bại. | "Ghi nhớ đăng nhập" (wireframe 01) — xem ND-41 |
| D-AUTH-03 | ND-03 | **V1 CÓ dùng refresh token** (thay quyết định cũ "không dùng"). Làm mới qua `POST /api/auth/refresh`. Backend xác minh refresh token trước khi cấp token mới. **Rotation**: làm mới thành công thì cấp refresh token mới và vô hiệu refresh token cũ. Trạng thái refresh token **lưu trong PostgreSQL** (hết hạn, thu hồi, rotation, đăng xuất), **chỉ lưu bản băm**. Logout: backend thu hồi refresh token tương ứng, frontend xóa token phía client. Refresh token hết hạn / bị thu hồi / không hợp lệ / đã bị xoay vòng → làm mới thất bại, frontend yêu cầu đăng nhập lại. Access token **không** thu hồi được tức thì (vẫn sống tối đa 30 phút). | ND-40, ND-41, ND-42, ND-43, ND-48 |
| D-AUTH-04 | ND-04 | Băm mật khẩu bằng **Argon2id**; chỉ lưu bản băm trong `User.hashed_password` (VARCHAR 255 — đủ chứa chuỗi băm Argon2id); không lưu mật khẩu thuần; đăng nhập dùng hàm xác minh của thư viện. | ND-45 (thư viện, tham số) |
| D-AUTH-05 | ND-05 | Chính sách mật khẩu, áp dụng **giống nhau** cho `register`, `reset-password`, `change-password`: (1) tối thiểu **8 ký tự**; (2) tối đa **128 byte** sau khi mã hóa UTF-8; (3) ≥ 1 chữ hoa ASCII `A-Z`; (4) ≥ 1 chữ thường ASCII `a-z`; (5) ≥ 1 chữ số `0-9`; (6) ≥ 1 ký tự đặc biệt; (7) không chứa khoảng trắng. Khi request có `confirm_password`, backend kiểm `password` khớp `confirm_password`; không lưu `confirm_password`; chỉ lưu bản băm. Không ghi mật khẩu, mật khẩu xác nhận hay token gốc vào log. Mã lỗi theo ND-15. | ND-46 (tập ký tự đặc biệt, khoảng trắng, ký tự non-ASCII), ND-47 (endpoint nào nhận `confirm_password`) |

### Mâu thuẫn đã được giải quyết bằng quyết định trên

| Mã | Mâu thuẫn | Cách giải quyết |
|---|---|---|
| X1 | STRUCTURE/api-endpoints cũ: ôn tập theo kỹ năng; bản sửa: theo khóa học | D01 → theo khóa học. STRUCTURE và api-endpoints đã cập nhật |
| X2 | STRUCTURE cũ: `review_question.py`, `user_course.py`; CSDL: `Question`, `StudentCourse`, thêm `ReviewAnswer`, `PasswordResetToken` | Theo CSDL bản sửa. STRUCTURE đã cập nhật tên model |
| X3 | STRUCTURE §2 chỉ có register/login/logout, `/me`, `/me/skills` | Thêm forgot/reset/change-password, avatar, summary (T01–T05, đã tick) |
| X4 | STRUCTURE không có module email | Thêm `core/email.py` (T29, T01) |
| X5 | Sheet Endpoint ghi `POST .../review-attempts` → 409 khi "đã completed" | D10 = B thắng: khóa `completed` **được** ôn lại |
| X6 | T03 ghi sai mật khẩu hiện tại → "400/401"; `.docx` ghi 400 | Theo `.docx`: **400** |
| X8 | D08: logout stateless, không có bảng token; D-AUTH-03: lưu refresh token trong PostgreSQL, logout thu hồi | D-AUTH-03 (mới hơn, do owner xác nhận) thay phần logout của D08; access token vẫn stateless. Wireframe 02 chỉ ghi "Tối thiểu 8 ký tự" — chính sách đầy đủ theo D-AUTH-05; dòng hướng dẫn trên giao diện cần nhóm frontend cập nhật |
| X7 (CONFLICT-OWN-01) | Excel sheet Endpoint: §2 thuộc Hòa; sheet "Danh sách thay đổi": T01–T10 đề xuất Tuấn | **RESOLVED** bằng D-OWN-01: Auth & Profile thuộc Tuấn |

---

## 3. Trạng thái hạng mục T (2 module)

Nguồn: sheet "Danh sách thay đổi". ☑ = nhóm đã đồng ý; ☐ = chưa.

| Mã | Hạng mục | Module | Nhóm đồng ý |
|---|---|---|---|
| T01 | `POST /api/auth/forgot-password` | Auth | ☑ |
| T02 | `POST /api/auth/reset-password` | Auth | ☑ |
| T03 | `POST /api/me/change-password` | Auth | ☑ |
| T04 | `PATCH /api/me` nhận `avatar_url`; `POST /api/me/avatar` | Auth | ☑ |
| T05 | `GET /api/me/summary` | Auth | ☑ (ghi chú nhóm: phần đếm "nhóm chưa chốt" → ND-13) |
| T06 | Body `PATCH /api/me/skills` | Auth | ☑ |
| T07 | `GET /api/me/skills?status=` | Auth | ☑ |
| T08 | `GET /api/me/courses?status=abandoned` | Course Tracking | ☑ |
| T09 | register không nhận role | Auth | ☑ |
| T10 | Sửa mẫu trang Profile (email chỉ đọc, đổi mật khẩu, quên mật khẩu) | Frontend | ☑ |
| T11 | Đổi endpoint ôn tập sang theo khóa học | Review | ☑ |
| T12 | Xóa `GET/PATCH /api/me/skills` khỏi §10 | Review | **☐** → ND-30 |
| T13 | Nộp bài trong một transaction | Review | ☑ (bước 5 "tạm thời chưa quyết định" → ND-24) |
| T14 | Chọn 20 câu, tạo sẵn 20 ReviewAnswer | Review | ☑ (thuật toán chi tiết → ND-20) |
| T15 | Không lộ đáp án; chỉ chủ sở hữu xem attempt (404) | Review | ☑ |
| T16 | Điều kiện bắt đầu và lỗi 409 | Review | **☐ → BLOCKED**. Phần trùng với D03, D10 (một bài dở; được ôn lại khóa completed) đã chốt qua D03, D10. Phần chỉ có nguồn từ T16/`.docx` 6.2 — 409 khi chưa tham gia/thiếu câu (RV-R03), câu bỏ trống = sai (RV-R10), nộp lần hai → 409 (RV-R13) — **chưa được coi là đã chốt** (AUD-01) |
| T17 | review-history: bộ lọc và phân trang | Review | ☑ |
| T18 | Cập nhật LearningPath sau khi ôn tập đạt | Learning Path (Tâm) | **☐** → ND-24 |
| T19–T21 | Quản trị câu hỏi `/api/admin/questions*` | Admin | ☑ — **ngoài phạm vi skill Review**, chỉ là dependency dữ liệu |
| T26 | `Question.is_active` | Review (dữ liệu) | ☑ |
| T27 | `ReviewAttempt.submitted_at` | Review | **☐** → ND-31 |
| T28 | Biến môi trường SMTP_*, FRONTEND_URL, RESET_TOKEN_EXPIRE_MINUTES, REVIEW_PASS_PERCENT | Chung | ☑ |
| T29 | Email kết quả sau khi nộp bài | Review | ☑ (gửi mọi lần hay chỉ khi đạt → ND-25) |
| T22–T25 | Feedback & liên hệ | Ngoài phạm vi | ☐ → ND-35 |

---

## 4. Điểm chưa chốt — `[NEEDS DECISION]`

Không được tự chọn phương án cho các mục dưới đây. Khi gặp lúc implement: dừng lại và hỏi, hoặc chỉ làm phần không phụ thuộc vào mục đó.

### 4.1. Xác thực & Hồ sơ

| Mã | Câu hỏi | Bối cảnh / nguồn |
|---|---|---|
| ~~ND-01~~ | Thuật toán ký JWT, payload, cách gửi token — **phần chính đã chốt → D-AUTH-01**; còn ND-44 | (lịch sử) STRUCTURE `security.py`, `client.js`, `authStore` |
| ~~ND-02~~ | Thời hạn access token — **đã chốt 30 phút → D-AUTH-02**; "Ghi nhớ đăng nhập" chuyển sang ND-41 | (lịch sử) SETUP §3 từng ghi 60 |
| ~~ND-03~~ | Có refresh token không — **đã chốt CÓ → D-AUTH-03**; còn ND-40, 41, 42, 43, 48 | — |
| ~~ND-04~~ | Thuật toán băm — **đã chốt Argon2id → D-AUTH-04**; còn ND-45 | (lịch sử) `.docx` 3.1 "đã mã hóa" |
| ~~ND-05~~ | Chính sách mật khẩu — **đã chốt → D-AUTH-05**; còn ND-46, ND-47 | (lịch sử) wireframe 02 |
| ND-40 | Thời hạn **refresh token** chính thức? Đề xuất 7 ngày (biến dự kiến `REFRESH_TOKEN_EXPIRE_DAYS`) — chưa được xác nhận. | D-AUTH-03 |
| ND-41 | Refresh token: **định dạng** (chuỗi ngẫu nhiên opaque hay JWT), **cách gửi** (JSON body hay cookie `httpOnly`), **nơi lưu phía client** (cùng `sessionStorage` với access token hay chỗ khác). `sessionStorage` mất khi đóng tab — ô "Ghi nhớ đăng nhập" (wireframe 01) có ý nghĩa gì? | D-AUTH-01, D-AUTH-02, D-AUTH-03, wireframe 01 |
| ND-42 | Phát hiện **tái sử dụng** refresh token đã bị xoay vòng/thu hồi: chỉ từ chối request đó, hay thu hồi toàn bộ chuỗi token/phiên của người dùng? | D-AUTH-03 |
| ND-43 | Thiết kế bảng lưu refresh token (`docs/database-design.md` §3.5, trạng thái PROPOSED): tên bảng, cột, thuật toán băm token, có lưu liên kết rotation (`replaced_by`/family) không, cho phép nhiều phiên/thiết bị đồng thời không, dọn bản ghi hết hạn thế nào. Cần duyệt trước khi tạo model/migration. | D-AUTH-03 |
| ND-44 | Thư viện JWT (ví dụ PyJWT) và kiểm tra tương thích Python 3.11+. Chưa có dependency nào trong `requirements.txt`/`pyproject.toml` (đang rỗng). | D-AUTH-01, `CLAUDE.md` (không thêm thư viện ngoài tài liệu) |
| ND-45 | Thư viện Argon2id và tham số (memory cost, time cost, parallelism); có dùng tham số nhẹ hơn cho môi trường test không. | D-AUTH-04 |
| ND-46 | Tập **ký tự đặc biệt** hợp lệ cho D-AUTH-05 (6); "khoảng trắng" gồm những gì (dấu cách, tab, xuống dòng, khoảng trắng Unicode); ký tự non-ASCII (chữ có dấu, emoji) có được phép không và có tính là ký tự đặc biệt không. Dự án chưa có quy định. | D-AUTH-05 |
| ND-47 | Endpoint nào nhận `confirm_password`: `register` (wireframe 02 có ô "Nhập lại mật khẩu"), `reset-password`, `change-password`? Tên trường ở reset/change là `confirm_password` hay khác? Đây là thay đổi API contract. | D-AUTH-05, wireframe 02 |
| ND-48 | Hợp đồng `POST /api/auth/refresh` và logout: request/response chính xác; mã lỗi khi làm mới thất bại; logout gửi refresh token nào để thu hồi, thu hồi một phiên hay mọi phiên; logout có bắt buộc access token còn hạn không. | D-AUTH-03, ND-15, ND-19 |
| ND-06 | Có giới hạn số lần thử đăng nhập / gửi forgot-password không? | Không tài liệu nào nhắc |
| ND-07 | Email có chuẩn hóa (chữ thường, bỏ khoảng trắng) trước khi lưu/so sánh không? | `.docx`: email UQ |
| ND-08 | Register trả token (đăng nhập luôn) hay chỉ "201 + thông tin người dùng"? Wireframe 04 cho chọn kỹ năng ngay sau đăng ký — việc này cần đã xác thực. | Sheet Endpoint, wireframe 04 |
| ND-09 | Wireframe 04 "Chọn tối đa 3 kỹ năng" — có phải giới hạn của API (`PATCH /api/me/skills`) không? | Wireframe 04 |
| ND-10 | Wireframe Profile có ô "Mục tiêu học tập", nhưng `User` không có cột này và `PATCH /api/me` chỉ nhận `full_name`, `avatar_url`. Bỏ ô này hay lấy từ LearningPath.goal_text? | Wireframe Profile, `.docx` 3.1 |
| ND-11 | `PATCH /api/me/skills`: `update` hoặc `remove` một kỹ năng mà user chưa có → lỗi gì hay bỏ qua? Cùng `skill_id` xuất hiện ở nhiều khóa (`add` và `remove`)? User có được tự hạ kỹ năng do ôn tập ghi nhận từ `known` xuống `learning`? | T06 chỉ quy định skill không tồn tại → 404 |
| ND-12 | `POST /api/me/avatar`: dung lượng tối đa, định dạng cho phép, nơi lưu file, URL công khai? `avatar_url` nhập tay có kiểm tra định dạng URL không? | T04, `.docx` chỉ có mã 413/415 |
| ND-13 | `GET /api/me/summary`: ghi chú của nhóm ở T05 "Đếm từ StudentCourse, UserSkill, LearningPath (nhóm chưa chốt)" — cách đếm chính thức? | T05 |
| ND-18 | Client gửi trường không được phép (`role` ở register; `email`/`role` ở `PATCH /api/me`): bỏ qua hay trả 422? | T09, `.docx` 3.1: "không nhận" — chưa nói cách xử lý |
| ND-19 | Hình dạng response của login (tên trường token, có `token_type` không, có trả refresh token trong body không — phụ thuộc ND-41) và các trường thông tin người dùng đi kèm? | Sheet Endpoint: "access token + thông tin người dùng (gồm role)"; D-AUTH-03 |
| ND-36 | Sau khi đổi/đặt lại mật khẩu: có thu hồi mọi refresh token của người dùng không (nay khả thi nhờ D-AUTH-03)? Access token đã cấp vẫn hợp lệ tối đa 30 phút (D-AUTH-02) — nhóm có chấp nhận không? | D-AUTH-02, D-AUTH-03, T02, T03 |
| ND-37 | `full_name` có bắt buộc khi đăng ký không? CSDL cho phép NULL, nhưng sheet Endpoint liệt kê nó trong body register và wireframe 02 có ô "Họ và tên". | `.docx` 3.1, sheet Endpoint |
| ND-38 | Wireframe Profile hiển thị nguồn của kỹ năng ("Từ bài ôn tập khóa học" / "Thêm thủ công"), nhưng `UserSkill` không có cột nguồn. Bỏ nhãn này trên giao diện hay bổ sung cột? | Wireframe Profile, `.docx` 3.2 |
| ND-39 | `forgot-password`: gửi email đồng bộ hay chạy nền? Nếu gửi lỗi thì vẫn trả thông báo chung (để không lộ email) và chỉ ghi log? Mã đã tạo có giữ lại không? | T01 chỉ quy định thông báo luôn giống nhau |

### 4.2. Ôn tập & Đánh giá

| Mã | Câu hỏi | Bối cảnh / nguồn |
|---|---|---|
| ND-20 | Thuật toán "chia đều giữa các kỹ năng": phần dư chia cho kỹ năng nào? Kỹ năng không đủ câu cho phần của nó thì bù từ kỹ năng khác thế nào? T14 ghi "lấy 60 câu ngẫu nhiên" — mâu thuẫn với `.docx` 6.3 ("chọn ngẫu nhiên 20 câu"). | G5 ví dụ 7 + 7 + 6; T14 |
| ND-21 | Có giới hạn thời gian làm bài không? Bài đang dở có hết hạn không? | Không tài liệu nào nhắc |
| ND-22 | `answers` khi nộp chứa `question_id` không thuộc attempt, hoặc trùng `question_id`: bỏ qua hay trả lỗi? | G5: "câu_id lạ bị bỏ qua hoặc báo lỗi" |
| ND-23 | Ôn lại khóa đã `completed` mà đạt: có upsert `UserSkill = known` lần nữa không? | `.docx` 6.2 bước 4 không phân biệt; D10 chỉ nói không đổi status/completed_at |
| ND-24 | Bước 5 của submit — kiểm tra LearningPath `ongoing` chứa kỹ năng vừa đạt và chuyển `completed` nếu mọi nút `is_required` đã known: có làm không, có nằm trong transaction submit không? Hàm do Tâm viết trong `learning_path_service` (T18 ☐). | T13, T18, G8 |
| ND-25 | Email kết quả gửi **mọi lần nộp** hay **chỉ khi đạt**? (Đề xuất trong ghi chú T29: mọi lần — chưa chốt.) | T29 |
| ND-26 | `GET /api/review-attempts/{attempt_id}` sau khi đã nộp trả gì (chỉ điểm, hay cả chi tiết)? `GET /api/me/review-history/{attempt_id}` với attempt chưa nộp trả gì (404, 409, hay chỉ trạng thái)? | Sheet Endpoint: "hoặc kết quả nếu đã nộp"; "(chỉ sau khi nộp)" |
| ND-27 | Wireframe 11/12 hiển thị "Mức: Mạnh ≥80% / Trung bình 50–79% / Yếu <50%", điểm dạng "x/20" và cột "Kỹ năng" (trong khi bài tính theo khóa học). Có phải trường của API không? Ngưỡng mức không khớp ngưỡng đạt 60%. | Wireframe 11, 12 |
| ND-28 | StudentCourse chuyển `abandoned` khi đang có bài dở: còn được nộp không? Khóa không có kỹ năng nào trong CourseSkillRelation: `GET .../review` trả lý do gì? | Không tài liệu nào nhắc |
| ND-29 | Đồng thời: hai request bắt đầu cùng lúc (có thể tạo hai bài dở), hai request nộp cùng lúc — dùng khóa dòng, unique index một phần, hay cách khác? | D03 "tối đa 1 bài dở", T16 "nộp lần hai → 409" |
| ND-30 | T12 (xóa `GET/PATCH /api/me/skills` lặp ở §10) chưa được tick. Tạm thời §10 chỉ ghi "xem §2". | T12 ☐ |
| ND-31 | T27 (`ReviewAttempt.submitted_at`) chưa được tick, nhưng `.docx` đã đưa cột vào và dùng nó cho email kết quả. Giữ cột này không? | T27 ☐, `.docx` 6.2 |
| ND-33 | `POST /api/courses/{course_id}/review-attempts` khi đã có bài dở và trả lại bài đó: mã 200 hay 201? Response có `attempted_at`, tên khóa học…? | D03 |
| ND-34 | `GET /api/me/review-history` có liệt kê cả bài đang dở (chưa có điểm) không? | `.docx` 6.2, T17 |

### 4.3. Kiến trúc dùng chung

| Mã | Câu hỏi | Bối cảnh / nguồn |
|---|---|---|
| ND-14 | Danh mục giá trị `error.code` (ngoài ví dụ `VALIDATION_ERROR`)? | CONVENTIONS §1 |
| ND-15 | Lỗi dữ liệu đầu vào dùng 400 hay 422? (Riêng các ca tài liệu đã ghi rõ mã — ví dụ reset-password 400, PATCH /me/skills 422 — thì theo tài liệu.) | CONVENTIONS: "400 / 422" |
| ND-16 | Lớp nào gọi `commit`/`rollback`: service, hay helper transaction trong `core/database.py`? | STRUCTURE: "service quản lý transaction"; `database.py` "transaction helper" |
| ND-17 | Index ngoài PK/UQ (ví dụ `ReviewAttempt(student_course_id)`, `Question(skill_id, is_active)`, `PasswordResetToken(user_id)`)? | `.docx` không liệt kê index |

### 4.4. Ngoài phạm vi 2 module (chỉ ghi nhận)

| Mã | Nội dung |
|---|---|
| ND-32 | STRUCTURE có `models/bookmark.py`, nhưng `.docx` 3.3 nói StudentCourse dùng cho cả bookmark, "không cần bảng riêng". Thuộc module Course Tracking. |
| ND-35 | Feedback & liên hệ (T22–T25) chưa được nhóm đồng ý; bảng Feedback/CourseContact có trong CSDL nhưng chưa có endpoint chính thức. |

---

## 5. Việc tồn đọng ngoài tài liệu (chưa làm ở giai đoạn này)

Theo sheet "File cần sửa" — chưa thực hiện vì không thuộc danh sách file của giai đoạn chuẩn bị tri thức:

- `.env.example` và `SETUP.md` §3: đã thêm biến xác thực và email (2026-10-24); **còn thiếu `REVIEW_PASS_PERCENT`** (thuộc module Ôn tập, chưa thêm trong lần cập nhật xác thực). *(T28)*
- `docs/structure.md`: thêm file model cho bảng RefreshToken sau khi ND-43 được duyệt.
- ~~`README.md`: bảng "Tổng quan API" vẫn ghi `/api/skills/{id}/review*`.~~ — đã sửa (2026-10-24); `docs/conventions.md` §2 "Ôn tập" cũng đã thay bằng liên kết tới tài liệu module (AUD-03, AUD-04).
- File code rỗng đã có sẵn trong `backend/` theo tên cũ (`models/review_question.py`, `models/user_course.py`) — đổi tên/tạo mới khi bắt đầu implement, theo `docs/structure.md`.
- `TASKS.md`, mẫu giao diện Profile (T10).
- Excel `EduMentor_Checklist_Da_Sua_API.xlsx`: cột "Phụ trách" của §2 (sheet "Endpoint (bản mới)") còn ghi Hòa — cập nhật theo D-OWN-01.
- `AGENTS.md` và `.agents/skills/*` (bản cho Codex) là bản sao cũ của skill Giai đoạn 2 — chưa có trạng thái T16, D-OWN-01; cần đồng bộ lại nếu còn dùng.
