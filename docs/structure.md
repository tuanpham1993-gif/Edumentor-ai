# STRUCTURE — Cấu trúc thư mục EduMentor AI

Tài liệu này mô tả cấu trúc thư mục của dự án và cách mỗi nhóm endpoint trong đặc tả API được ánh xạ vào file mã nguồn.

> **Giả định công nghệ:** Backend FastAPI (Python) + PostgreSQL + SQLAlchemy + Alembic; Frontend React (Vite). Nếu nhóm đổi công nghệ, giữ nguyên nguyên tắc phân lớp: *router → service → repository → model*.

---

## 1. Cây thư mục tổng quan

Cây dưới đây được **kiểm kê từ working tree** của nhánh `docs/initial-project-documentation` (HEAD `d608ab8`, đối chiếu `git ls-files` ngày 29/10/2026). Trên nhánh này, cấu trúc `backend/` giống hệt `origin/develop`; PR #1 của Hòa (`origin/Hoa`) khác ở các điểm ghi tại §1.2.

**Ký hiệu:** `✅` có nội dung · `◻` file giữ chỗ, 0 byte · `○` dự kiến — **chưa có file** · `⊘` có trên máy nhưng không được Git theo dõi (bị bỏ qua hoặc chưa commit). Mỗi package Python có `__init__.py` rỗng (không liệt kê).

```
edumentor-ai/
├── README.md                                        # ✅ Tổng quan dự án, 14 tính năng, người phụ trách
├── CLAUDE.md                                        # ✅ Chỉ thị cấp project cho Claude Code
├── AGENTS.md                                        # ✅ Chỉ thị cho Codex — bản cũ, chưa đồng bộ (decisions.md §5)
├── SETUP.md                                         # ✅ Cài đặt và chạy dự án
├── docker-compose.yml                               # ◻ Rỗng trên nhánh này; PR #1 thay bằng docker-compose.yaml (§1.2)
├── .env.example                                     # ✅ Mẫu biến môi trường (chỉ giá trị minh họa)
├── .gitignore                                       # ✅ Bỏ qua .env, .env.*, giữ !.env.example
├── .claude/
│   └── skills/
│       ├── auth-profile/
│       │   └── SKILL.md                             # ✅ Điểm vào module Xác thực & Hồ sơ
│       └── review-assessment/
│           └── SKILL.md                             # ✅ Điểm vào module Ôn tập & Đánh giá
├── .agents/
│   └── skills/
│       ├── auth-profile/
│       │   └── SKILL.md                             # ✅ Bản sao cho Codex — cũ
│       └── review-assessment/
│           └── SKILL.md                             # ✅ Bản sao cho Codex — cũ
├── docs/
│   ├── EduMentor-UI-design/                         # ✅ Prototype HTML cũ (29 trang) — không còn là nguồn giao diện (D-FE-02)
│   ├── modules/
│   │   ├── auth-profile.md                          # ✅ Đặc tả + API contract Xác thực & Hồ sơ
│   │   ├── auth-profile.tests.md                    # ✅ Kịch bản kiểm thử
│   │   ├── review-assessment.md                     # ✅ Đặc tả + API contract Ôn tập & Đánh giá
│   │   └── review-assessment.tests.md               # ✅ Kịch bản kiểm thử
│   ├── ui-animation/                                # ⊘ Báo cáo đối chiếu frontend với demo — CHƯA có trong Git (README.md, CLAUDE.md đang trỏ tới)
│   ├── api-endpoints.md                             # ✅ Đặc tả endpoint (bảng nhóm đã thống nhất)
│   ├── backend-rules.md                             # ✅ Quy tắc backend dùng chung (lỗi, transaction, bảo mật, cấu hình)
│   ├── conventions.md                               # ✅ Quy ước API, mã nguồn, Git, kiểm thử
│   ├── database-design.md                           # ✅ Thiết kế CSDL chính thức (21 bảng, FK, ràng buộc)
│   ├── decisions.md                                 # ✅ Quyết định đã chốt, mâu thuẫn, [NEEDS DECISION]
│   ├── EduMentor_Checklist_Da_Sua_API.xlsx          # ✅ Nguồn gốc checklist API, quyết định D01–D11
│   ├── EduMentor_Database_Design_Da_Sua.docx        # ✅ Nguồn gốc thiết kế CSDL đã sửa
│   └── structure.md                                 # ✅ Tài liệu này: cây thư mục, ánh xạ endpoint → file
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │       └── .gitkeep                             # ◻ Các migration (chưa có)
│   ├── app/
│   │   ├── ai/
│   │   │   ├── prompts/
│   │   │   │   ├── consultant.py                    # ◻
│   │   │   │   └── tutor.py                         # ◻
│   │   │   ├── client.py                            # ◻ Gọi LLM
│   │   │   └── validators.py                        # ◻ Xác thực mục tiêu/kỹ năng AI sinh ra với danh mục
│   │   ├── core/
│   │   │   ├── config.py                            # ◻ Đọc biến môi trường
│   │   │   ├── database.py                          # ◻ Engine, session, transaction helper
│   │   │   ├── dependencies.py                      # ◻ get_current_user, require_admin, get_db
│   │   │   ├── email.py                             # ○ send_email dùng chung: quên mật khẩu, email kết quả ôn tập
│   │   │   ├── errors.py                            # ◻ Exception chung + handler lỗi thống nhất
│   │   │   ├── pagination.py                        # ◻ Tham số và response phân trang
│   │   │   └── security.py                          # ◻ Băm mật khẩu (Argon2id — D-AUTH-04), tạo/kiểm tra JWT
│   │   ├── models/
│   │   │   ├── base_learning_path.py                # ◻ Mẫu + node + edge của mẫu
│   │   │   ├── bookmark.py                          # ◻ Tên cũ — CSDL không có bảng Bookmark (StudentCourse dùng cho cả bookmark) — ND-32
│   │   │   ├── chat_message.py                      # ◻
│   │   │   ├── chat_session.py                      # ◻ Có trường loại phiên (consultant/tutor)
│   │   │   ├── course.py                            # ◻
│   │   │   ├── course_contact.py                    # ○ Chưa có endpoint chính thức — ND-35
│   │   │   ├── course_skill.py                      # ◻ Liên kết course ↔ skill (CourseSkillRelation)
│   │   │   ├── feedback.py                          # ○ Chưa có endpoint chính thức — ND-35
│   │   │   ├── historical_path.py                   # ◻ Dữ liệu lịch sử cho Collaborative Filtering (CSDL chưa có bảng — DB-2)
│   │   │   ├── learning_path.py                     # ◻
│   │   │   ├── learning_path_edge.py                # ◻
│   │   │   ├── learning_path_node.py                # ◻ PK (path_id, skill_id)
│   │   │   ├── password_reset_token.py              # ○ Mã đặt lại mật khẩu (lưu bản băm)
│   │   │   ├── question.py                          # ○ Question: ngân hàng câu hỏi (thay review_question.py)
│   │   │   ├── review_answer.py                     # ○ 20 câu của một lần làm bài + câu trả lời
│   │   │   ├── review_attempt.py                    # ◻ Một lần làm bài, gắn StudentCourse
│   │   │   ├── review_question.py                   # ◻ Tên cũ — sẽ thay bằng question.py
│   │   │   ├── skill.py                             # ◻
│   │   │   ├── skill_relation.py                    # ◻ prerequisite / extension / related
│   │   │   ├── student_course.py                    # ○ StudentCourse: bookmarked/ongoing/completed/abandoned (thay user_course.py)
│   │   │   ├── user.py                              # ◻ Bảng users
│   │   │   ├── user_course.py                       # ◻ Tên cũ — sẽ thay bằng student_course.py
│   │   │   └── user_skill.py                        # ◻
│   │   ├── recommender/
│   │   │   ├── collaborative_filtering.py           # ◻ Tham khảo lộ trình lịch sử tương tự
│   │   │   ├── course_ranking.py                    # ◻ Độ liên quan > rating > số đánh giá
│   │   │   └── skill_graph.py                       # ◻ Mở rộng quan hệ tiên quyết
│   │   ├── repositories/
│   │   │   └── .gitkeep                             # ◻ Truy vấn CSDL, không chứa logic nghiệp vụ (chưa có repository nào)
│   │   ├── routers/
│   │   │   ├── admin/
│   │   │   │   ├── base_learning_paths.py           # ◻ §12 (kèm nodes, edges của mẫu)
│   │   │   │   ├── course_skill_relations.py        # ◻ §11
│   │   │   │   ├── courses.py                       # ◻ §11
│   │   │   │   ├── historical_paths.py              # ◻ §13 (tùy chọn)
│   │   │   │   ├── questions.py                     # ○ §11 /api/admin/questions* (ND-53)
│   │   │   │   ├── skill_relations.py               # ◻ §11
│   │   │   │   └── skills.py                        # ◻ §11
│   │   │   ├── auth.py                              # ◻ §2  /api/auth/* (register, login, refresh, logout, forgot-password, reset-password)
│   │   │   ├── chat_consultant.py                   # ◻ §5  /api/chat/learning-path
│   │   │   ├── chat_tutor.py                        # ◻ §9  /api/chat/sessions*
│   │   │   ├── course_tracking.py                   # ◻ §4  /api/courses/{id}/join
│   │   │   ├── courses.py                           # ◻ §3  /api/courses*
│   │   │   ├── learning_path_edges.py               # ◻ §7  .../edges
│   │   │   ├── learning_path_nodes.py               # ◻ §6  .../nodes
│   │   │   ├── learning_paths.py                    # ◻ §5  /api/learning-paths, /api/me/learning-paths
│   │   │   ├── me.py                                # ◻ §2  /api/me, /api/me/avatar, /api/me/change-password, /api/me/summary, /api/me/skills
│   │   │   ├── me_courses.py                        # ◻ §2,4 /api/me/courses*, /api/me/bookmarks*
│   │   │   ├── node_course_suggestions.py           # ◻ §8  .../nodes/{skill_id}/courses
│   │   │   └── reviews.py                           # ◻ §10 /api/courses/{course_id}/review*, /api/review-attempts*, /api/me/review-history*
│   │   ├── schemas/
│   │   │   ├── auth.py                              # ◻
│   │   │   ├── base_path.py                         # ◻
│   │   │   ├── chat.py                              # ◻
│   │   │   ├── common.py                            # ◻
│   │   │   ├── course.py                            # ◻
│   │   │   ├── learning_path.py                     # ◻
│   │   │   ├── review.py                            # ◻
│   │   │   ├── skill.py                             # ◻
│   │   │   └── user.py                              # ◻
│   │   ├── services/
│   │   │   ├── auth_service.py                      # ◻ Đăng ký, đăng nhập, quên/đặt lại mật khẩu
│   │   │   ├── base_path_service.py                 # ◻
│   │   │   ├── consultant_service.py                # ◻ Điều phối quy trình tạo lộ trình (§12)
│   │   │   ├── course_service.py                    # ◻ Tìm kiếm, lọc, sắp xếp
│   │   │   ├── course_tracking_service.py           # ◻ Bookmark, join, chuyển trạng thái
│   │   │   ├── historical_import_service.py         # ◻
│   │   │   ├── learning_path_service.py             # ◻ Lưu/cập nhật/abandon lộ trình
│   │   │   ├── path_graph_service.py                # ◻ Node/edge, xóa node kèm cạnh (transaction)
│   │   │   ├── recommendation_service.py            # ◻ Gợi ý khóa học theo kỹ năng
│   │   │   ├── review_service.py                    # ◻ Bài ôn tập theo khóa học: chấm điểm, completed, cập nhật kỹ năng, email
│   │   │   ├── tutor_service.py                     # ◻
│   │   │   └── user_service.py                      # ◻ Hồ sơ, đổi mật khẩu, avatar, summary, cập nhật kỹ năng
│   │   └── main.py                                  # ◻ Khởi tạo FastAPI, gắn router, middleware
│   ├── scripts/
│   │   ├── create_admin.py                          # ◻ Tạo tài khoản quản trị
│   │   └── seed_data.py                             # ◻ Nạp khóa học, kỹ năng, câu hỏi mẫu
│   ├── tests/
│   │   ├── conftest.py                              # ◻
│   │   ├── test_admin.py                            # ◻
│   │   ├── test_auth.py                             # ◻
│   │   ├── test_course_tracking.py                  # ◻
│   │   ├── test_courses.py                          # ◻
│   │   ├── test_learning_paths.py                   # ◻
│   │   ├── test_path_graph.py                       # ◻
│   │   ├── test_recommendation.py                   # ◻
│   │   ├── test_review.py                           # ◻
│   │   └── test_tutor.py                            # ◻
│   ├── alembic.ini                                  # ◻ Chưa cấu hình; chưa có migration nào
│   ├── pyproject.toml                               # ◻ (hoặc requirements.txt)
│   └── requirements.txt                             # ◻ PR #1 có nội dung (§1.2)
└── frontend/
    ├── dist/                                        # ⊘ Kết quả npm run build — không phải mã nguồn
    ├── node_modules/                                # ⊘ Sinh tự động khi npm install — không phải mã nguồn
    ├── src/
    │   ├── api/
    │   │   ├── admin.api.js                         # ◻ §11-13 /api/admin/*
    │   │   ├── auth.api.js                          # ◻ §2  /api/auth/*
    │   │   ├── client.js                            # ◻ Axios: base URL, gắn token (D-FE-05), chuẩn hóa lỗi
    │   │   ├── consultant.api.js                    # ◻ §5  /api/chat/learning-path
    │   │   ├── courses.api.js                       # ◻ §3  /api/courses*
    │   │   ├── courseTracking.api.js                # ◻ §4  bookmarks, join, status, /api/me/courses*
    │   │   ├── learningPaths.api.js                 # ◻ §5  /api/learning-paths*, /api/me/learning-paths
    │   │   ├── me.api.js                            # ◻ §2  /api/me, avatar, change-password, summary, skills
    │   │   ├── nodeSuggestions.api.js               # ◻ §8  .../nodes/{skill_id}/courses
    │   │   ├── pathGraph.api.js                     # ◻ §6,7 .../nodes*, .../edges*
    │   │   ├── review.api.js                        # ◻ §10 review, review-attempts, review-history
    │   │   └── tutor.api.js                         # ◻ §9  /api/chat/sessions*
    │   ├── components/
    │   │   ├── chat/
    │   │   │   ├── ChatBubble.jsx                   # ○ Lối tắt + AI tư vấn khóa học (phần AI chờ ND-55)
    │   │   │   ├── ChatWindow.jsx                   # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   └── MessageBubble.jsx                # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   ├── common/
    │   │   │   ├── AnimatedNumber.jsx               # ○
    │   │   │   ├── Button.jsx                       # ◻
    │   │   │   ├── ConfirmDialog.jsx                # ○
    │   │   │   ├── ErrorMessage.jsx                 # ◻
    │   │   │   ├── Icons.jsx                        # ○
    │   │   │   ├── Modal.jsx                        # ◻
    │   │   │   ├── Pagination.jsx                   # ◻
    │   │   │   ├── PasswordInput.jsx                # ○
    │   │   │   ├── PasswordRules.jsx                # ○
    │   │   │   ├── Tabs.jsx                         # ○
    │   │   │   ├── ThemeToggle.jsx                  # ○
    │   │   │   └── Toast.jsx                        # ○
    │   │   ├── course/
    │   │   │   ├── CardOpening.jsx                  # ○
    │   │   │   ├── CourseActions.jsx                # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   ├── CourseCard.jsx                   # ◻
    │   │   │   ├── CourseCardFace.jsx               # ○
    │   │   │   ├── CourseCover.jsx                  # ○
    │   │   │   ├── CourseFilters.jsx                # ◻
    │   │   │   └── JoinDialog.jsx                   # ○
    │   │   ├── layout/
    │   │   │   ├── AdminLayout.jsx                  # ○
    │   │   │   ├── AuthLayout.jsx                   # ○
    │   │   │   ├── HangingLamp.jsx                  # ○
    │   │   │   ├── Header.jsx                       # ◻
    │   │   │   ├── Logo.jsx                         # ○
    │   │   │   ├── PageLayout.jsx                   # ◻
    │   │   │   ├── PullLamp.jsx                     # ○
    │   │   │   ├── SettingsLayout.jsx               # ○
    │   │   │   └── Sidebar.jsx                      # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   ├── learning-path/
    │   │   │   ├── NodeCoursePanel.jsx              # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   ├── NodeDetailPanel.jsx              # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   ├── PathGraph.jsx                    # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   └── ProposedPathPreview.jsx          # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   ├── path/
    │   │   │   ├── PathEditDialog.jsx               # ○
    │   │   │   └── PathGraph.jsx                    # ○
    │   │   ├── profile/
    │   │   │   ├── CurrentPathCard.jsx              # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   ├── LogoutDialog.jsx                 # ○
    │   │   │   ├── MyCoursesTabs.jsx                # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   ├── ProfileEditForm.jsx              # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   ├── ProfileHeader.jsx                # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   ├── ReviewHistoryList.jsx            # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   └── SkillList.jsx                    # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   └── review/
    │   │       ├── QuestionCard.jsx                 # ◻ cấu trúc cũ, không dùng — ND-49
    │   │       └── ScoreSummary.jsx                 # ◻ cấu trúc cũ, không dùng — ND-49
    │   ├── config/
    │   │   └── links.js                             # ○ Link GitHub, Zalo
    │   ├── hooks/
    │   │   ├── useAuth.js                           # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   ├── useCourseStatus.js                   # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   └── usePagination.js                     # ◻ cấu trúc cũ, không dùng — ND-49
    │   ├── mock/
    │   │   ├── db.js                                # ○ Chỉ dùng khi VITE_USE_MOCK=true (D-FE-07)
    │   │   └── feedback.js                          # ○ Chỉ dùng khi VITE_USE_MOCK=true (D-FE-07)
    │   ├── pages/
    │   │   ├── admin/
    │   │   │   ├── AdminBasePathsPage.jsx           # ◻
    │   │   │   ├── AdminCoursesPage.jsx             # ◻
    │   │   │   ├── AdminFeedbackPage.jsx            # ○ Chưa có endpoint — ND-55
    │   │   │   ├── AdminHistoricalPage.jsx          # ◻
    │   │   │   ├── AdminRelationsPage.jsx           # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   ├── AdminSkillsPage.jsx              # ◻
    │   │   │   ├── AdminUserPathsPage.jsx           # ○ Chưa có endpoint — ND-55
    │   │   │   └── SkillRelationMap.jsx             # ○
    │   │   ├── auth/
    │   │   │   ├── ForgotPasswordPage.jsx           # ○
    │   │   │   ├── ForgotSentPage.jsx               # ○
    │   │   │   ├── LoginPage.jsx                    # ◻
    │   │   │   ├── RegisterPage.jsx                 # ◻
    │   │   │   ├── ResetExpiredPage.jsx             # ○
    │   │   │   └── ResetPasswordPage.jsx            # ○
    │   │   ├── catalog/
    │   │   │   ├── CatalogPage.jsx                  # ◻
    │   │   │   └── CourseDetailPage.jsx             # ◻
    │   │   ├── feedback/
    │   │   │   └── FeedbackPage.jsx                 # ○ Chưa có endpoint — ND-55
    │   │   ├── learning-path/
    │   │   │   ├── ConsultantChatPage.jsx           # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   ├── LearningPathDetailPage.jsx       # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   │   └── LearningPathListPage.jsx         # ◻ cấu trúc cũ, không dùng — ND-49
    │   │   ├── path/
    │   │   │   ├── ConsultantPage.jsx               # ○
    │   │   │   ├── MyPathsPage.jsx                  # ○
    │   │   │   └── PathDetailPage.jsx               # ○
    │   │   ├── profile/
    │   │   │   ├── ChangePasswordPage.jsx           # ○
    │   │   │   ├── EditProfilePage.jsx              # ○
    │   │   │   ├── ProfilePage.jsx                  # ◻
    │   │   │   └── SkillsPage.jsx                   # ○
    │   │   ├── review/
    │   │   │   ├── ReviewAttemptPage.jsx            # ◻
    │   │   │   ├── ReviewDetailPage.jsx             # ○
    │   │   │   ├── ReviewHistoryPage.jsx            # ◻
    │   │   │   ├── ReviewResultPage.jsx             # ◻
    │   │   │   └── ReviewStartPage.jsx              # ○
    │   │   ├── tracking/
    │   │   │   └── MyCoursesPage.jsx                # ○
    │   │   └── tutor/
    │   │       └── TutorPage.jsx                    # ◻
    │   ├── routes/
    │   │   ├── AdminRoute.jsx                       # ◻ Yêu cầu role admin — chỉ ẩn giao diện (D-FE-06)
    │   │   ├── index.jsx                            # ◻ Khai báo toàn bộ route (mục 3)
    │   │   └── ProtectedRoute.jsx                   # ◻ Yêu cầu đăng nhập — chỉ ẩn giao diện (D-FE-06)
    │   ├── store/
    │   │   └── authStore.js                         # ◻ cấu trúc cũ, không dùng — ND-49
    │   ├── utils/
    │   │   ├── constants.js                         # ◻ Hằng số trạng thái khớp enum backend
    │   │   ├── formatters.js                        # ◻ Định dạng số, ngày (structure cũ ghi prefersReducedMotion ở đây — hiện ở theme.js)
    │   │   └── theme.js                             # ✅ Theme Sáng/Tối (em-theme), reduced motion (em-motion), prefersReducedMotion
    │   ├── App.jsx                                  # ✅ BrowserRouter + màn tạm C1 (chưa có Routes, Toast, CardOpening, ChatBubble)
    │   ├── index.css                                # ✅ Design token Tối/Sáng, motion, class dùng chung, keyframes, reduced-motion
    │   └── main.jsx                                 # ✅ initTheme() rồi render <App/>
    ├── .env                                         # ⊘ Cục bộ, bị .gitignore bỏ qua — VITE_API_BASE_URL, VITE_USE_MOCK
    ├── .gitignore                                   # ✅ node_modules/, dist/, *.local
    ├── index.html                                   # ✅ lang=vi, font Be Vietnam Pro, nền tối trước khi tải CSS
    ├── package-lock.json                            # ✅ Khóa phiên bản npm
    ├── package.json                                 # ✅ Dependency: D-FE-09; engines ^18 || ^20 || >=22
    └── vite.config.js                               # ✅ Plugin React, cổng 5173
```

Mỗi page và component frontend dự kiến có file `*.module.css` đi kèm. Bảng chuyển màn `components/demo/` của bản demo **không** đưa vào frontend (D-FE-07). File rỗng theo cấu trúc cũ (đánh dấu "ND-49") được **giữ nguyên, không dùng** cho tới khi ND-49 được quyết định. Trang quản trị câu hỏi (`/api/admin/questions*`) chưa có trong demo — ND-53. Thư mục `docs/wireframes/` đã bị xóa ở commit `4d853cf`.

### 1.1. Hiện trạng triển khai (đã xác minh)

| Khu vực | Hiện trạng trên nhánh này | Bằng chứng |
|---|---|---|
| Backend `backend/**` | **Chưa có code**: 102 file đều 0 byte; chưa có model, migration, test | `git ls-files -s backend` + kích thước file |
| Frontend nền (C1) | `package.json`, `package-lock.json`, `vite.config.js`, `index.html`, `src/main.jsx`, `src/App.jsx`, `src/index.css`, `src/utils/theme.js` có nội dung; build chạy được | commit `a13cb8f` |
| Frontend còn lại | 62 file trong `frontend/src/` rỗng; route, API client, page, component chưa triển khai | `git ls-files frontend` |
| Docker Compose | `docker-compose.yml` rỗng | kích thước file |
| Alembic | `backend/alembic.ini` rỗng, `alembic/versions/` chỉ có `.gitkeep` | — |

### 1.2. Khác biệt với PR #1 (`origin/Hoa`, commit `26a0f63`, PR `Hoa → develop` đang mở)

Chỉ ghi các file đã đọc trực tiếp bằng `git diff --name-status origin/develop...origin/Hoa` và `git show origin/Hoa:<file>`. **Chưa merge** — chưa phải cấu trúc chính thức.

| Đường dẫn trên PR #1 | Thay đổi so với `develop` / nhánh này | Nội dung đã xác minh |
|---|---|---|
| `backend/app/main.py` | Có nội dung | FastAPI, `CORSMiddleware`, `lifespan` gọi `init_db()`, `app.include_router(api_router, prefix=settings.API_STR)`; Swagger ở `{API_STR}/docs` |
| `backend/app/core/config.py` | Có nội dung | `Settings` (pydantic-settings): **`API_STR = "/api"`**, `VERSION`, `DATABASE_URL`, `SQL_ECHO`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALLOWED_ORIGINS`; đọc `.env` ở thư mục gốc repo |
| `backend/app/core/database.py` | Có nội dung | Engine **sync**, `SessionLocal`, `Base`, `init_db()` gọi `create_all()`, `get_db()` |
| `backend/app/routers/v1/__init__.py` | Đổi tên từ `routers/auth.py` (vẫn rỗng) | — |
| `backend/app/routers/v1/api.py` | Mới | `api_router` include `endpoints/health.py` |
| `backend/app/routers/v1/endpoints/health.py` | Mới | `GET /health` → URL thực tế **`/api/health`** (không có `/api/v1`) |
| `backend/__init__.py` | Đổi tên từ `backend/app/routers/__init__.py` | Rỗng |
| `backend/app/routers/{me, me_courses, courses, course_tracking, learning_paths, learning_path_nodes, learning_path_edges, node_course_suggestions, chat_consultant, chat_tutor, reviews}.py` | **Bị xóa** (11 file rỗng) | — |
| `backend/app/routers/admin/*.py` | Giữ nguyên (rỗng) | — |
| `backend/requirements.txt` | Có nội dung | fastapi, uvicorn, pydantic-settings, sqlalchemy[asyncio], alembic, psycopg[binary], bcrypt, pyjwt, httpx, aiosmtplib, pytest… |
| `docker-compose.yaml` | Mới (thay `docker-compose.yml` bị xóa) | Dịch vụ `postgres` (postgres:16-alpine), cổng `5433:5432`, DB `edumentor_db` |
| `SETUP_BACKEND.md` | Mới | Hướng dẫn venv, pip, docker compose, pgAdmin |
| `.gitignore`, `.env.example` | Sửa — **xung đột** với nhánh này khi merge | — |

### 1.3. Cấu trúc đang chờ nhóm quyết định

| Điểm | Cấu trúc thực tế hiện tại | Cấu trúc tài liệu đề xuất | Chờ quyết định |
|---|---|---|---|
| Tổ chức router (G6) | Nhánh này / `develop`: router phẳng `backend/app/routers/*.py`. PR #1: `routers/v1/api.py` + `routers/v1/endpoints/<nhóm>.py` | Router phẳng (§1, §2) | Chọn một cách; URL giữ tiền tố `/api` ở cả hai (`API_STR = "/api"` trên PR #1) |
| Router đã bị xóa trên PR #1 | 11 file router rỗng | Mỗi nhóm endpoint một file router (§2) | Khôi phục hay chuyển sang `endpoints/` |
| Tên file Docker Compose | `docker-compose.yml` (rỗng) / PR #1: `docker-compose.yaml` | — | Chọn tên; cổng và tên DB (5432/`edumentor` hay 5433/`edumentor_db`) |
| Hướng dẫn cài đặt | `SETUP.md` / PR #1 thêm `SETUP_BACKEND.md` | Một nguồn duy nhất | Gộp hay giữ riêng |
| Tên model cũ | `models/review_question.py`, `user_course.py`, `bookmark.py` | `question.py`, `student_course.py`; không có bảng Bookmark (ND-32) | Đổi tên khi bắt đầu implement |
| Frontend cấu trúc cũ | Các file đánh dấu ND-49 | Cấu trúc theo demo (D-FE-03) | ND-49 |

---

## 2. Ánh xạ mục đặc tả → file mã nguồn

| Mục đặc tả | Nhóm endpoint | Router | Service chính |
|---|---|---|---|
| §2 | `/api/auth/*` | `routers/auth.py` | `auth_service` |
| §2 | `/api/me`, `/api/me/skills` | `routers/me.py` | `user_service` |
| §2, §4 | `/api/me/courses*`, `/api/me/bookmarks*` | `routers/me_courses.py` | `course_tracking_service` |
| §3 | `/api/courses*` | `routers/courses.py` | `course_service` |
| §4 | `/api/courses/{id}/join` | `routers/course_tracking.py` | `course_tracking_service` |
| §5 | `/api/chat/learning-path` | `routers/chat_consultant.py` | `consultant_service` |
| §5 | `/api/learning-paths*`, `/api/me/learning-paths` | `routers/learning_paths.py` | `learning_path_service` |
| §6 | `.../nodes*` | `routers/learning_path_nodes.py` | `path_graph_service` |
| §7 | `.../edges*` | `routers/learning_path_edges.py` | `path_graph_service` |
| §8 | `.../nodes/{skill_id}/courses` | `routers/node_course_suggestions.py` | `recommendation_service` |
| §9 | `/api/chat/sessions*` | `routers/chat_tutor.py` | `tutor_service` |
| §10 | `/api/courses/{course_id}/review*`, `/api/review-attempts*`, `/api/me/review-history*` | `routers/reviews.py` | `review_service` |
| §11 | `/api/admin/courses`, `skills`, `course-skill-relations`, `skill-relations` | `routers/admin/*.py` | `course_service`, `base_path_service`… |
| §11 | `/api/admin/questions*` | `routers/admin/questions.py` | (chưa đặt tên service trong tài liệu) |
| §12 | `/api/admin/base-learning-paths*` | `routers/admin/base_learning_paths.py` | `base_path_service` |
| §13 | `/api/admin/historical-learning-path*` | `routers/admin/historical_paths.py` | `historical_import_service` |

Cột "Router" mô tả cấu trúc router phẳng mà tài liệu đề xuất (đường dẫn tương đối với `backend/app/`). Hiện các file này đều rỗng; riêng `routers/admin/questions.py` chưa có file. PR #1 tổ chức router khác (`routers/v1/endpoints/`) — xem §1.2 và §1.3 (G6). URL của mọi endpoint vẫn bắt đầu bằng `/api/` theo `docs/api-endpoints.md` §1.

---

## 3. Ánh xạ trang Frontend → Endpoint Backend

Route theo bản demo (D-FE-02, D-FE-04). Guard: **C** = công khai, **P** = `ProtectedRoute`, **A** = `AdminRoute` (D-FE-06). Endpoint chỉ lấy từ `docs/api-endpoints.md` (D-FE-10). `/courses` và `/courses/:courseId` để **P** theo demo (demo chỉ có giao diện đã đăng nhập); `docs/api-endpoints.md` §3 chưa ghi quyền của `GET /api/courses*`.

| Route | Guard | Page | Endpoint backend sử dụng |
|---|---|---|---|
| `/` | C | chuyển hướng `/login` | — |
| `/login` | C | `auth/LoginPage` | `POST /api/auth/login` |
| `/register` | C | `auth/RegisterPage` | `POST /api/auth/register` |
| `/forgot-password`, `/forgot-sent` | C | `auth/ForgotPasswordPage`, `ForgotSentPage` | `POST /api/auth/forgot-password` |
| `/reset-password`, `/reset-expired` | C | `auth/ResetPasswordPage`, `ResetExpiredPage` | `POST /api/auth/reset-password` (dạng link chứa token: chưa có trong tài liệu) |
| `/me` | P | `profile/ProfilePage` | `GET /api/me`, `GET /api/me/summary`, `GET /api/me/courses?status=`, `GET /api/me/skills`, `GET /api/me/review-history`, `POST /api/auth/logout` |
| `/me/edit` | P | `profile/EditProfilePage` | `GET/PATCH /api/me`, `POST /api/me/avatar` |
| `/me/password` | P | `profile/ChangePasswordPage` | `POST /api/me/change-password` |
| `/me/skills` | P | `profile/SkillsPage` | `GET/PATCH /api/me/skills` (theo `skill_id` — D-FE-11) |
| `/courses` | P | `catalog/CatalogPage` | `GET /api/courses` (`search`, `skill_id`, `level`, `sort_by`), `POST /api/me/bookmarks`, `DELETE /api/me/bookmarks/{course_id}` |
| `/courses/:courseId` | P | `catalog/CourseDetailPage` | `GET /api/courses/{course_id}`, `GET /api/courses/{course_id}/skills`, `GET /api/me/courses/{course_id}/status`, `POST /api/courses/{course_id}/join`, `POST/DELETE /api/me/bookmarks…` |
| `/me/courses` | P | `tracking/MyCoursesPage` | `GET /api/me/courses?status=`, `GET /api/me/bookmarks`, `PATCH /api/me/courses/{course_id}/status`, `DELETE /api/me/courses/{course_id}` |
| `/consultant` | P | `path/ConsultantPage` | `POST /api/chat/learning-path`, `POST /api/learning-paths` (chỉ khi người dùng xác nhận) |
| `/me/learning-paths` | P | `path/MyPathsPage` | `GET /api/me/learning-paths` |
| `/learning-paths/:pathId` | P | `path/PathDetailPage` | `GET/PATCH/DELETE /api/learning-paths/{path_id}`, nodes `GET/POST/PATCH/DELETE`, edges `GET/POST/PATCH/DELETE`, `GET .../nodes/{skill_id}/courses` |
| `/tutor` | P | `tutor/TutorPage` | `POST/GET /api/chat/sessions`, `GET /api/chat/sessions/{session_id}`, `GET/POST .../messages`, `DELETE /api/chat/sessions/{session_id}` |
| `/courses/:courseId/review` | P | `review/ReviewStartPage` | `GET /api/courses/{course_id}/review`, `POST /api/courses/{course_id}/review-attempts` |
| `/courses/:courseId/review/attempt` | P | `review/ReviewAttemptPage` | `POST /api/courses/{course_id}/review-attempts` (trả lại bài dở — D03), `GET /api/review-attempts/{attempt_id}`, `POST /api/review-attempts/{attempt_id}/submit`. Lưu đáp án bài dở: chưa có endpoint (ND-55) |
| `/review-result/:attemptId` | P | `review/ReviewResultPage` | `GET /api/me/review-history/{attempt_id}` |
| `/me/review-history`, `/me/review-history/:attemptId` | P | `review/ReviewHistoryPage`, `ReviewDetailPage` | `GET /api/me/review-history` (`page`, `page_size`, bộ lọc — T17), `GET /api/me/review-history/{attempt_id}` |
| `/contact` | P | `feedback/FeedbackPage` | Chưa có endpoint (ND-55) — hiển thị "chưa khả dụng" |
| `/admin` | A | chuyển hướng `/admin/courses` | — |
| `/admin/courses` | A | `admin/AdminCoursesPage` | `/api/admin/courses*`, `/api/admin/course-skill-relations*` |
| `/admin/skills` | A | `admin/AdminSkillsPage` (+ `SkillRelationMap`) | `/api/admin/skills*`, `/api/admin/skill-relations*` |
| `/admin/base-paths` | A | `admin/AdminBasePathsPage` | `/api/admin/base-learning-paths*` (kèm nodes, edges) |
| `/admin/historical` | A | `admin/AdminHistoricalPage` | `/api/admin/historical-learning-paths*`, `/api/admin/historical-learning-path-imports*` (tùy chọn) |
| `/admin/feedback` | A | `admin/AdminFeedbackPage` | Chưa có endpoint (ND-55) |
| `/admin/user-paths` | A | `admin/AdminUserPathsPage` | Chưa có endpoint (ND-55) |
| `*` | — | chuyển hướng `/login` | — |

Route chỉ để mở nhanh trạng thái trong demo (`/logout`, `/courses/:courseId/join`, `/learning-paths/:pathId/edit`, `/contact-guest`) chưa đưa vào bảng — ND-50. Bong bóng chat (`ChatBubble`) hiện trên mọi trang trừ `/admin/*`, `/tutor`, `/consultant` và trang làm bài; phần "AI tư vấn khóa học" chưa có endpoint (ND-55).

### Cách frontend và backend khớp với nhau

- Mỗi file trong `frontend/src/api/` tương ứng một file router trong `backend/app/routers/` (xem bảng ở mục 2), nên đổi endpoint ở backend thì chỉ sửa đúng một file ở frontend.
- Component và page **không gọi `fetch` trực tiếp**, chỉ gọi hàm trong `api/`.
- Tên trường trong form/hiển thị trùng tên trường của Pydantic schema (`backend/app/schemas/`).
- Hằng số trạng thái (`bookmarked`, `ongoing`, `completed`, `abandoned`; `prerequisite`, `optional`, `extension`) khai báo ở `utils/constants.js` và khớp enum backend.
- `ProtectedRoute` áp cho các endpoint người dùng, `AdminRoute` áp cho `/api/admin/*`; backend vẫn kiểm tra quyền, frontend chỉ ẩn giao diện.
- Lỗi backend theo cấu trúc `error.code` / `error.message` được `client.js` xử lý một chỗ rồi hiển thị bằng `ErrorMessage`.

### Quy tắc giao diện bám theo nghiệp vụ backend

- Nút "Mở khóa học" gọi `join` rồi chuyển hướng tới URL ngoài trong phản hồi; **không** tự coi là hoàn thành.
- Trạng thái `completed` chỉ hiển thị sau khi nộp bài ôn tập; sau khi nộp, frontend chỉ tải lại dữ liệu, **không** gửi request cập nhật kỹ năng riêng.
- Lộ trình AI đề xuất chỉ hiển thị ở khung đề xuất của `ConsultantPage`; chỉ khi bấm xác nhận mới gọi `POST /api/learning-paths`.
- Gợi ý khóa học chỉ tải khi người dùng chọn một node (panel bên phải của `PathDetailPage`).
- Màn hình làm bài ôn tập không nhận đáp án đúng từ API cho tới khi nộp.
- Danh sách có thể lớn dùng `Pagination` với `page`, `page_size`.

---

## 4. Nguyên tắc phân lớp (Backend)

1. **Router** chỉ nhận request, kiểm tra quyền, gọi service và trả response. Không viết truy vấn hay logic nghiệp vụ.
2. **Service** chứa quy tắc nghiệp vụ và quản lý transaction (ví dụ: xóa node cùng các cạnh liên quan).
3. **Repository** chỉ truy vấn CSDL.
4. **Schema** kiểm tra dữ liệu vào/ra; **Model** mô tả bảng.
5. Logic AI nằm ở `ai/`, thuật toán gợi ý nằm ở `recommender/`; service gọi vào các module này.

---

## 5. Luồng nghiệp vụ chính và file liên quan

**Tạo lộ trình học tập**
`chat_consultant.py` → `consultant_service` → `ai/client` (diễn giải mục tiêu) → `ai/validators` (xác thực kỹ năng với danh mục) → `base_path_service` (tìm mẫu) → `recommender/skill_graph` (mở rộng tiên quyết) → `recommender/collaborative_filtering` (lộ trình lịch sử) → trả lộ trình **đề xuất**. Chỉ khi người dùng xác nhận qua `POST /api/learning-paths` thì `learning_path_service` mới lưu.

**Gợi ý khóa học theo node**
`node_course_suggestions.py` → `recommendation_service` → kiểm tra kỹ năng thuộc lộ trình → `recommender/course_ranking` (độ liên quan kỹ năng là yếu tố hàng đầu; **không** dùng điểm ôn tập).

**Ôn tập và hoàn thành khóa học** (theo khóa học — D01)
`reviews.py` → `review_service`: bắt đầu → chọn và lưu sẵn 20 câu từ các kỹ năng của khóa (ẩn đáp án) → khi nộp: chấm điểm, lưu lần làm, nếu đạt (≥ `REVIEW_PASS_PERCENT`) thì đánh dấu khóa học `completed` và cập nhật `user_skill` — tất cả trong một transaction → sau commit gửi email kết quả chạy nền qua `core/email.py`. Chi tiết: `docs/modules/review-assessment.md`.

**Quên mật khẩu**
`auth.py` → `auth_service` → tạo `password_reset_token` (lưu bản băm) → `core/email.py` gửi link → `reset-password` kiểm tra mã và đổi mật khẩu. Chi tiết: `docs/modules/auth-profile.md`.

---

## 6. Điểm cần nhóm chốt trước khi code

Các điểm trước đây được liệt kê ở mục này đã được giải quyết trong `docs/database-design.md`:

- `is_required` của node → `LearningPathNode.is_required`.
- Kỹ năng mục tiêu lưu riêng → `LearningPathNode.is_target`.
- Chính sách làm lại bài ôn tập và điểm tối thiểu → D03 (không giới hạn), D02 (60%).
- `DELETE /api/chat/sessions/{id}` → chuyển `ChatSession.status` sang `archived`.
- `relation_type` của cạnh → `prerequisite`, `optional`.

Các điểm còn mở (cho 2 module Xác thực & Hồ sơ, Ôn tập & Đánh giá) được theo dõi tập trung tại `docs/decisions.md`.
