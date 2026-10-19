# STRUCTURE — Cấu trúc thư mục EduMentor AI

Tài liệu này mô tả cấu trúc thư mục của dự án và cách mỗi nhóm endpoint trong đặc tả API được ánh xạ vào file mã nguồn.

> **Giả định công nghệ:** Backend FastAPI (Python) + PostgreSQL + SQLAlchemy + Alembic; Frontend React (Vite). Nếu nhóm đổi công nghệ, giữ nguyên nguyên tắc phân lớp: *router → service → repository → model*.

---

## 1. Cây thư mục tổng quan

```
edumentor-ai/
├── README.md
├── CONVENTIONS.md
├── SETUP.md
├── STRUCTURE.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── docs/
│   ├── api-endpoints.md            # Đặc tả endpoint (bảng nhóm đã thống nhất)
│   ├── database-design.md          # ERD, mô tả bảng, khóa chính tổng hợp
│   └── wireframes/                 # Ảnh/PDF wireframe giao diện
│
├── backend/
│   ├── pyproject.toml              # (hoặc requirements.txt)
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/               # Các migration
│   │
│   ├── app/
│   │   ├── main.py                 # Khởi tạo FastAPI, gắn router, middleware
│   │   │
│   │   ├── core/
│   │   │   ├── config.py           # Đọc biến môi trường
│   │   │   ├── database.py         # Engine, session, transaction helper
│   │   │   ├── security.py         # Hash mật khẩu, tạo/kiểm tra token
│   │   │   ├── dependencies.py     # get_current_user, require_admin, get_db
│   │   │   ├── errors.py           # Exception chung + handler lỗi thống nhất
│   │   │   └── pagination.py       # Tham số và response phân trang
│   │   │
│   │   ├── routers/                # Lớp HTTP: nhận request, gọi service
│   │   │   ├── auth.py                     # §2  /api/auth/*
│   │   │   ├── me.py                       # §2  /api/me, /api/me/skills
│   │   │   ├── me_courses.py               # §2,4 /api/me/courses*, /api/me/bookmarks*
│   │   │   ├── courses.py                  # §3  /api/courses*
│   │   │   ├── course_tracking.py          # §4  /api/courses/{id}/join
│   │   │   ├── learning_paths.py           # §5  /api/learning-paths, /api/me/learning-paths
│   │   │   ├── learning_path_nodes.py      # §6  .../nodes
│   │   │   ├── learning_path_edges.py      # §7  .../edges
│   │   │   ├── node_course_suggestions.py  # §8  .../nodes/{skill_id}/courses
│   │   │   ├── chat_consultant.py          # §5  /api/chat/learning-path
│   │   │   ├── chat_tutor.py               # §9  /api/chat/sessions*
│   │   │   ├── reviews.py                  # §10 /api/skills/{id}/review*, /api/review-attempts*, /api/me/review-history*
│   │   │   └── admin/
│   │   │       ├── courses.py                  # §11
│   │   │       ├── skills.py                   # §11
│   │   │       ├── course_skill_relations.py   # §11
│   │   │       ├── skill_relations.py          # §11
│   │   │       ├── base_learning_paths.py      # §12 (kèm nodes, edges của mẫu)
│   │   │       └── historical_paths.py         # §13 (tùy chọn)
│   │   │
│   │   ├── schemas/                # Pydantic: request/response, kiểm tra dữ liệu
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── course.py
│   │   │   ├── skill.py
│   │   │   ├── learning_path.py
│   │   │   ├── chat.py
│   │   │   ├── review.py
│   │   │   ├── base_path.py
│   │   │   └── common.py           # Lỗi, phân trang, enum dùng chung
│   │   │
│   │   ├── models/                 # SQLAlchemy ORM
│   │   │   ├── user.py
│   │   │   ├── user_skill.py
│   │   │   ├── course.py
│   │   │   ├── skill.py
│   │   │   ├── course_skill.py             # Liên kết course ↔ skill
│   │   │   ├── skill_relation.py           # prerequisite / extension / related
│   │   │   ├── bookmark.py
│   │   │   ├── user_course.py              # Theo dõi: ongoing/completed/abandoned
│   │   │   ├── learning_path.py
│   │   │   ├── learning_path_node.py       # PK (path_id, skill_id)
│   │   │   ├── learning_path_edge.py
│   │   │   ├── base_learning_path.py       # Mẫu + node + edge của mẫu
│   │   │   ├── historical_path.py          # Dữ liệu lịch sử cho Collaborative Filtering
│   │   │   ├── chat_session.py             # Có trường loại phiên (consultant/tutor)
│   │   │   ├── chat_message.py
│   │   │   ├── review_question.py
│   │   │   └── review_attempt.py
│   │   │
│   │   ├── repositories/           # Truy vấn CSDL, không chứa logic nghiệp vụ
│   │   │
│   │   ├── services/               # Logic nghiệp vụ, transaction
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py             # Hồ sơ, cập nhật kỹ năng
│   │   │   ├── course_service.py           # Tìm kiếm, lọc, sắp xếp
│   │   │   ├── course_tracking_service.py  # Bookmark, join, chuyển trạng thái
│   │   │   ├── learning_path_service.py    # Lưu/cập nhật/abandon lộ trình
│   │   │   ├── path_graph_service.py       # Node/edge, xóa node kèm cạnh (transaction)
│   │   │   ├── recommendation_service.py   # Gợi ý khóa học theo kỹ năng
│   │   │   ├── review_service.py           # Tạo bài, chấm điểm, completed, cập nhật kỹ năng
│   │   │   ├── tutor_service.py
│   │   │   ├── consultant_service.py       # Điều phối quy trình tạo lộ trình (§12)
│   │   │   ├── base_path_service.py
│   │   │   └── historical_import_service.py
│   │   │
│   │   ├── ai/                     # Tích hợp mô hình ngôn ngữ
│   │   │   ├── client.py                   # Gọi LLM
│   │   │   ├── prompts/                    # Prompt consultant, tutor
│   │   │   └── validators.py               # Xác thực mục tiêu/kỹ năng AI sinh ra với danh mục
│   │   │
│   │   ├── recommender/            # Thuật toán gợi ý
│   │   │   ├── skill_graph.py              # Mở rộng quan hệ tiên quyết
│   │   │   ├── collaborative_filtering.py  # Tham khảo lộ trình lịch sử tương tự
│   │   │   └── course_ranking.py           # Độ liên quan > rating > số đánh giá
│   │   │
│   │   └── utils/
│   │
│   ├── scripts/
│   │   ├── seed_data.py            # Nạp khóa học, kỹ năng, câu hỏi mẫu
│   │   └── create_admin.py         # Tạo tài khoản quản trị
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_courses.py
│       ├── test_course_tracking.py
│       ├── test_learning_paths.py
│       ├── test_path_graph.py
│       ├── test_recommendation.py
│       ├── test_review.py
│       ├── test_tutor.py
│       └── test_admin.py
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── .env                         # VITE_API_BASE_URL
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── routes/
        │   ├── index.jsx                    # Khai báo toàn bộ route
        │   ├── ProtectedRoute.jsx           # Yêu cầu đăng nhập (endpoint người dùng)
        │   └── AdminRoute.jsx               # Yêu cầu quyền quản trị (/api/admin/*)
        │
        ├── api/                             # 1 file = 1 nhóm endpoint backend
        │   ├── client.js                    # Base URL, gắn token, xử lý lỗi thống nhất
        │   ├── auth.api.js                  # §2  /api/auth/*
        │   ├── me.api.js                    # §2  /api/me, /api/me/skills
        │   ├── courses.api.js               # §3  /api/courses*
        │   ├── courseTracking.api.js        # §4  bookmarks, join, status, /api/me/courses*
        │   ├── learningPaths.api.js         # §5  /api/learning-paths*, /api/me/learning-paths
        │   ├── pathGraph.api.js             # §6,7 .../nodes*, .../edges*
        │   ├── nodeSuggestions.api.js       # §8  .../nodes/{skill_id}/courses
        │   ├── consultant.api.js            # §5  /api/chat/learning-path
        │   ├── tutor.api.js                 # §9  /api/chat/sessions*
        │   ├── review.api.js                # §10 review, review-attempts, review-history
        │   └── admin.api.js                 # §11-13 /api/admin/*
        │
        ├── pages/
        │   ├── auth/
        │   │   ├── LoginPage.jsx
        │   │   └── RegisterPage.jsx
        │   ├── profile/
        │   │   └── ProfilePage.jsx          # Trang hồ sơ người dùng
        │   ├── catalog/
        │   │   ├── CatalogPage.jsx
        │   │   └── CourseDetailPage.jsx
        │   ├── learning-path/
        │   │   ├── ConsultantChatPage.jsx   # Chat tạo lộ trình + xem đề xuất
        │   │   ├── LearningPathListPage.jsx
        │   │   └── LearningPathDetailPage.jsx   # Đồ thị node/cạnh + gợi ý khóa học
        │   ├── tutor/
        │   │   └── TutorPage.jsx
        │   ├── review/
        │   │   ├── ReviewAttemptPage.jsx
        │   │   ├── ReviewResultPage.jsx
        │   │   └── ReviewHistoryPage.jsx
        │   └── admin/
        │       ├── AdminCoursesPage.jsx
        │       ├── AdminSkillsPage.jsx
        │       ├── AdminRelationsPage.jsx       # course-skill + skill-relations
        │       ├── AdminBasePathsPage.jsx       # Mẫu lộ trình cơ sở
        │       └── AdminHistoricalPage.jsx      # Tùy chọn
        │
        ├── components/
        │   ├── layout/                      # Header, Sidebar, PageLayout
        │   ├── common/                      # Button, Modal, Pagination, ErrorMessage
        │   ├── profile/
        │   │   ├── ProfileHeader.jsx            # GET /api/me
        │   │   ├── ProfileEditForm.jsx          # PATCH /api/me
        │   │   ├── SkillList.jsx                # GET/PATCH /api/me/skills
        │   │   ├── CurrentPathCard.jsx          # GET /api/me/learning-paths
        │   │   ├── MyCoursesTabs.jsx            # GET /api/me/courses?status=
        │   │   └── ReviewHistoryList.jsx        # GET /api/me/review-history
        │   ├── course/
        │   │   ├── CourseCard.jsx
        │   │   ├── CourseFilters.jsx            # search, skill_id, level, sort_by
        │   │   └── CourseActions.jsx            # bookmark / join / abandon
        │   ├── learning-path/
        │   │   ├── PathGraph.jsx                # Vẽ node + cạnh
        │   │   ├── NodeDetailPanel.jsx          # Sửa node_role, display_order
        │   │   ├── NodeCoursePanel.jsx          # Gợi ý khóa học khi chọn node
        │   │   └── ProposedPathPreview.jsx      # Xem đề xuất trước khi lưu
        │   ├── chat/
        │   │   ├── ChatWindow.jsx
        │   │   └── MessageBubble.jsx
        │   └── review/
        │       ├── QuestionCard.jsx
        │       └── ScoreSummary.jsx
        │
        ├── hooks/                           # useAuth, usePagination, useCourseStatus
        ├── store/                           # authStore (user, token)
        └── utils/                           # Định dạng, hằng số trạng thái
```

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
| §10 | review, review-attempts, review-history | `routers/reviews.py` | `review_service` |
| §11 | `/api/admin/courses`, `skills`, `course-skill-relations`, `skill-relations` | `routers/admin/*.py` | `course_service`, `base_path_service`… |
| §12 | `/api/admin/base-learning-paths*` | `routers/admin/base_learning_paths.py` | `base_path_service` |
| §13 | `/api/admin/historical-learning-path*` | `routers/admin/historical_paths.py` | `historical_import_service` |

---

## 3. Ánh xạ trang Frontend → Endpoint Backend

| Trang (route) | File | Endpoint backend sử dụng |
|---|---|---|
| `/login`, `/register` | `pages/auth/*` | `POST /api/auth/login`, `/register`, `/logout` |
| `/profile` | `pages/profile/ProfilePage.jsx` | `GET/PATCH /api/me`, `GET/PATCH /api/me/skills`, `GET /api/me/learning-paths`, `GET /api/me/courses?status=`, `GET /api/me/review-history` |
| `/courses` | `CatalogPage.jsx` | `GET /api/courses` (`search`, `skill_id`, `level`, `sort_by`), `POST /api/me/bookmarks` |
| `/courses/:courseId` | `CourseDetailPage.jsx` | `GET /api/courses/{id}`, `GET /api/courses/{id}/skills`, `POST /api/courses/{id}/join`, `POST/DELETE /api/me/bookmarks`, `GET/PATCH /api/me/courses/{id}/status` |
| `/learning-paths/new` | `ConsultantChatPage.jsx` | `POST /api/chat/learning-path`, `POST /api/learning-paths` (lưu khi người dùng xác nhận) |
| `/learning-paths` | `LearningPathListPage.jsx` | `GET /api/me/learning-paths`, `DELETE /api/learning-paths/{id}` (abandon) |
| `/learning-paths/:pathId` | `LearningPathDetailPage.jsx` | `GET/PATCH /api/learning-paths/{id}`, nodes `GET/POST/PATCH/DELETE`, edges `GET/POST/PATCH/DELETE`, `GET .../nodes/{skill_id}/courses` |
| `/tutor` | `TutorPage.jsx` | `POST/GET /api/chat/sessions`, `GET/POST .../messages`, `DELETE /api/chat/sessions/{id}` |
| `/review/:skillId` | `ReviewAttemptPage.jsx` | `GET /api/skills/{id}/review`, `POST .../review-attempts`, `GET /api/review-attempts/{id}`, `POST .../submit` |
| `/review/history` | `ReviewHistoryPage.jsx`, `ReviewResultPage.jsx` | `GET /api/me/review-history`, `GET /api/me/review-history/{attempt_id}` |
| `/admin/*` | `pages/admin/*` | `/api/admin/*` (§11–§13) |

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
- Lộ trình AI đề xuất chỉ hiển thị ở `ProposedPathPreview`; chỉ khi bấm xác nhận mới gọi `POST /api/learning-paths`.
- Gợi ý khóa học chỉ tải khi người dùng chọn một node (`NodeCoursePanel`).
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

**Ôn tập và hoàn thành khóa học**
`reviews.py` → `review_service`: lấy 20 câu (ẩn đáp án) → chấm điểm khi nộp → lưu lần làm → đánh dấu khóa học `completed` → cập nhật `user_skill` trong cùng transaction.

---

## 6. Điểm cần nhóm chốt trước khi code

- Thêm trường `is_required` vào node để xác định lộ trình đã `completed`.
- Lưu **kỹ năng mục tiêu** riêng, không gộp với `node_role`.
- Chính sách làm lại bài ôn tập và điểm tối thiểu để công nhận kỹ năng.
- Chính sách `DELETE /api/chat/sessions/{id}`: xóa hay lưu trữ.
- Giá trị `relation_type` của cạnh khớp thiết kế bảng.
