# EduMentor AI — Kế hoạch triển khai tổng (`plans/plan.md`)

> **Vai trò của tài liệu (D-DOC-05):** hướng dẫn thực hiện và theo dõi công việc chi tiết theo Phase và Task. Tài liệu này **không** là nguồn yêu cầu nghiệp vụ hay quyết định kiến trúc, **không** tạo, sửa hay phê duyệt D/ND. Mọi quyết định chỉ được tham chiếu tới `docs/decisions.md`. Thành viên hoặc AI Agent làm theo kế hoạch **không** được dựa vào file này để sửa BA, SRS hay `docs/decisions.md`.
>
> **Cấu trúc từ 2026-11-03 (D-DOC-05 (8)):** file này quản lý tổng thể dự án, Phase dùng chung P00–P03, P13, các Task dùng chung của P12 và phần ngoài 14 tính năng ở P11. Task của từng tính năng nằm trong `plans/Fxx-*/phase-NN-*.md` (NN là số Phase của khung chung); mỗi Task chỉ có **một** nơi quản lý. Mục lục thư mục tính năng: PART 1 bên dưới.
>
> Lập ngày 2026-10-30, trên nhánh `docs/initial-project-documentation` (HEAD `a49df4a`). Trạng thái ban đầu phản ánh hiện trạng repo tại thời điểm lập; chưa có dữ liệu tiến độ thực tế.

---

## PART 1 — PROJECT OVERVIEW

| Mục | Nội dung |
|---|---|
| Project name | EduMentor AI |
| Project objective | Nền tảng cố vấn học tập cá nhân hóa: lộ trình học bằng AI, gợi ý khóa học MOOC theo kỹ năng, AI Tutor, ghi nhận kỹ năng qua bài ôn tập (`README.md`; BA §2) |
| Planning scope | 14 tính năng F01–F14 (`README.md` "Tính năng chính"), phần nền dùng chung, phần ngoài 14 tính năng có trong `docs/ui-design/` và `docs/api-endpoints.md` §12–§13, khối AI/ML theo BA §8, tích hợp – kiểm thử – tài liệu – demo. Đây là đồ án học tập: **không** có nghiệm thu thương mại, release sign-off, giám sát vận hành hay SLA |
| Hiện trạng code | Backend chưa có code (mọi file 0 byte); frontend có phần nền C1 (commit `a13cb8f`) — `docs/structure.md` §1.1 |

### Tài liệu nguồn và thứ bậc (D-DOC-01)

| Bậc | Tài liệu | Dùng trong kế hoạch |
|---|---|---|
| 1 | Đề bài SRS v1.0 `docs/AI_Learning_Assistant_Recommender SRS.docx.pdf` | Yêu cầu gốc của đề bài (trang 5–7 là sơ đồ ảnh, chưa đọc được); điểm lệch: ND-81 |
| 2 | `docs/decisions.md` | Quyết định D-xx đã chốt; ND-xx **đang chờ** (không coi là đã duyệt) |
| 3 | BA `docs/EdumentorAi_BA.md` | Yêu cầu nghiệp vụ (FR, NFR, BR, UC, AC) |
| 4 | SRS v2.0 `docs/EduMentor_AI_SRS_v2.0.docx` (các task bên dưới được lập trước khi có v2.0) | Đặc tả yêu cầu |
| 5 | UI `docs/ui-design/` (D-FE-12) | Giao diện, không tạo quy tắc |
| 6 | Code | Hiện trạng triển khai |
| Dẫn xuất | `docs/modules/*.md`, `docs/api-endpoints.md`, `docs/database-design.md`, `docs/structure.md`, `docs/conventions.md`, `docs/backend-rules.md`, `SETUP.md`, `README.md`; workbook `docs/EduMentor_AI_Ke_Hoach_14_Tinh_Nang.xlsx`; **file này** | Đặc tả triển khai, kế hoạch và theo dõi; không có thứ bậc |

### Quan hệ giữa các tài liệu

| Tài liệu | Vai trò | Ghi chú |
|---|---|---|
| BA, SRS | Yêu cầu nghiệp vụ và yêu cầu gốc | Không tự ghi đè quyết định đã chốt |
| `docs/decisions.md` | Nơi lưu quyết định chính thức | Kế hoạch chỉ tham chiếu |
| Workbook chính thức | Theo dõi, đối chiếu ở **mức tính năng** (D-DOC-04) | Không ghi Task ID, tiến độ Task, effort, deadline hay dependency vào workbook |
| `plans/plan.md` | Tổng thể, Phase, Task dùng chung, phân công, dependency, trạng thái, bằng chứng, kết quả review (D-DOC-05) | Tài liệu dẫn xuất, không có thứ bậc |
| `plans/Fxx-*/` | `plan.md`, `ba-decisions-and-safe-defaults.md`, `phase-NN-*.md` của từng tính năng; nơi quản lý duy nhất Task của tính năng (D-DOC-05 (8)) | Tài liệu dẫn xuất, không có thứ bậc |

### Thư mục kế hoạch theo tính năng

Người phụ trách theo D-OWN-02 (`docs/decisions.md` §2).

| Mã | Tính năng | Người phụ trách | Thư mục |
|---|---|---|---|
| F01 | Xác thực và hồ sơ người dùng | Tuấn | [F01-authentication-profile/](F01-authentication-profile/plan.md) |
| F02 | Danh mục khóa học | Khôi | [F02-course-catalog/](F02-course-catalog/plan.md) |
| F03 | Đánh dấu (Bookmark) | Tâm | [F03-bookmark/](F03-bookmark/plan.md) |
| F04 | Theo dõi tiến trình khóa học, đề xuất khóa học liên quan đến nút của tiến trình | Hòa | [F04-course-progress/](F04-course-progress/plan.md) |
| F05 | Tư vấn viên AI và lộ trình học tập | Hòa | [F05-ai-consultant-learning-roadmap/](F05-ai-consultant-learning-roadmap/plan.md) |
| F06 | Các nút (Node) và liên kết (Edge) trong lộ trình học tập | Hòa | [F06-roadmap-nodes-edges/](F06-roadmap-nodes-edges/plan.md) |
| F07 | Gợi ý khóa học cho một kỹ năng cụ thể | Tâm | [F07-skill-course-recommendation/](F07-skill-course-recommendation/plan.md) |
| F08 | Trò chuyện với gia sư AI | Tâm | [F08-ai-tutor-chat/](F08-ai-tutor-chat/plan.md) |
| F09 | Ôn tập và đánh giá kiến thức | Tuấn | [F09-review-assessment/](F09-review-assessment/plan.md) |
| F10 | Phản hồi (Feedback) | Khôi | [F10-feedback/](F10-feedback/plan.md) |
| F11 | Quản trị — khóa học, kỹ năng và các mối liên hệ | Hòa | [F11-admin-courses-skills-relations/](F11-admin-courses-skills-relations/plan.md) |
| F12 | Quản trị — các mối liên hệ giữa các kỹ năng | Tâm | [F12-admin-skill-relations/](F12-admin-skill-relations/plan.md) |
| F13 | Quản trị — quản lý phản hồi | Hòa | [F13-admin-feedback/](F13-admin-feedback/plan.md) |
| F14 | Quản trị — xem lộ trình học tập của người dùng | Hòa | [F14-admin-user-learning-roadmap/](F14-admin-user-learning-roadmap/plan.md) |

Phần ngoài 14 tính năng (mẫu lộ trình, dữ liệu lịch sử, quản trị câu hỏi, bong bóng chat) và Task dùng chung: quản lý tại file này.

---

## PART 2 — PLANNING RULES

1. **Cấp quản lý:** Phase (P00–P13) → Task. Không có cấp thấp hơn. Từ 2026-11-03, Task của một tính năng nằm trong `plans/Fxx-*/phase-NN-*.md` (NN = số Phase); Task dùng chung nằm ở file này. Mỗi Task ID chỉ có **một** dòng đầy đủ (có Status) trong toàn bộ `plans/`; nơi khác chỉ được ghi chỉ mục hoặc liên kết, không ghi trạng thái.
2. **Task ID:** `Pxx-Txx` (ví dụ `P04-T05`), duy nhất trong toàn file, không tái sử dụng khi xóa Task; Task mới đánh số tiếp theo trong Phase.
3. **Phân công:** chỉ ghi người khi có căn cứ trong tài liệu dự án (`docs/decisions.md` §2 — D-OWN-01, D-OWN-02; `README.md` "Nhóm thực hiện") hoặc nhóm đã xác nhận. Không có căn cứ → `Chưa phân công`; Support chưa rõ → `Chưa xác định`. **Reviewer hiện chưa có căn cứ cho bất kỳ Phase nào → `Chưa phân công`.** Không tự chuyển việc giữa thành viên.
4. **Dependency:** chỉ ghi khi Task thật sự cần kết quả của Task khác. Phân loại: **[KT]** kỹ thuật (cần code/hạ tầng), **[NV]** nghiệp vụ (cần quyết định D/ND), **[TL]** tài liệu (cần đặc tả). Không tạo dependency chỉ vì khác Phase. P00 **không** chặn toàn dự án.
5. **Trạng thái** (chỉ dùng 6 giá trị):

   | Status | Ý nghĩa | Điều kiện |
   |---|---|---|
   | NOT_STARTED | Chưa bắt đầu | — |
   | IN_PROGRESS | Đang thực hiện | — |
   | BLOCKED | Bị chặn | **Bắt buộc** ghi cột Blocker: mã ND/T hoặc Task phụ thuộc |
   | REVIEW | Đã làm xong, chờ review | Có Evidence |
   | REWORK | Cần sửa sau review | Ghi nhận xét review |
   | DONE | Hoàn thành, có kết quả kiểm tra phù hợp | **Bắt buộc** có Evidence và kết quả review; DONE **không** đồng nghĩa nghiệm thu chính thức |

   Phase DONE khi mọi Task bắt buộc DONE và có kết quả review. Phase có Task BLOCKED vẫn có thể IN_PROGRESS nếu Task độc lập còn tiếp tục.
6. **Bằng chứng (Evidence):** commit hash, đường dẫn PR, đường dẫn file, kết quả `pytest`/build, ảnh chụp màn hình, mục trong báo cáo lỗi. Không ghi DONE chỉ vì "đã có code" hoặc "đã có commit".
7. **Blocker và vấn đề chưa quyết định:** ghi mã ND/T; ghi rõ phần nào **vẫn làm được**. Không tự chọn phương án cho ND đang chờ. Phát hiện thiếu hoặc mâu thuẫn tài liệu → báo người có thẩm quyền đề xuất ND trong `docs/decisions.md` (không sửa trong file này).
8. **Đặc tả và test còn thiếu:** chỉ F01 và F09 có đặc tả đã xác nhận và `*.tests.md`. Các tính năng còn lại và phần ngoài 14 tính năng có đặc tả **DRAFT** (`docs/modules/README.md`, 2026-11-03), chưa được người phụ trách xác nhận, chưa có `*.tests.md`. Các Phase còn lại có Task "rà soát nguồn", "chuẩn bị đặc tả module", "chuẩn bị test case"; expected result chỉ lấy từ nguồn đã có, không tự đặt.
9. **Kiểm thử frontend và responsive:** quy tắc cụ thể chờ **ND-67**, **ND-68** (PENDING). Không tự chọn công cụ, coverage hay breakpoint.

Viết tắt dùng trong bảng: CPC = Chưa phân công; CXĐ = Chưa xác định.

---

## PART 3 — PHASE OVERVIEW

| Phase | Tên Phase | Feature liên quan | Mục tiêu | Dependency | Responsible | Reviewer | Status |
|---|---|---|---|---|---|---|---|
| P00 | Decisions & Blocking Issues | — | Đưa các ND/vấn đề đang chặn tới người có thẩm quyền quyết định | — | CPC | CPC | NOT_STARTED |
| P01 | Backend Foundation | — | FastAPI, cấu hình, database, Alembic, xử lý lỗi, hạ tầng test | Một phần P00 | CPC | CPC | NOT_STARTED |
| P02 | Shared Data Foundation | (F02, F11, F12, F05–F07) | Bảng Course, Skill, CourseSkillRelation, SkillRelation và dữ liệu mẫu | P01 | CPC | CPC | NOT_STARTED |
| P03 | Frontend Foundation | Tất cả (giao diện) | Route, guard, API client, layout, component dùng chung | — (C1 đã có) | CPC | CPC | IN_PROGRESS |
| P04 | Authentication & Profile | F01 | Tài khoản, xác thực, hồ sơ, kỹ năng cá nhân | P01, P02, P03 | Tuấn | CPC | NOT_STARTED |
| P05 | Course Catalog & Admin Courses | F02, F11 | Danh mục, chi tiết khóa học, quản trị khóa học/kỹ năng | P02, P03, P04 (xác thực) | Khôi (F02), Hòa (F11) | CPC | NOT_STARTED |
| P06 | Bookmark & Learning Progress | F03, F04 | Lưu khóa học, tham gia, trạng thái học | P04, P05 | Tâm (F03), Hòa (F04) | CPC | NOT_STARTED |
| P07 | Roadmap, AI Consultant & Recommendations | F05, F06, F07, F12 | Tư vấn mục tiêu, lộ trình đồ thị, node/cạnh, gợi ý, quan hệ kỹ năng | P02, P04 | Hòa (F05, F06), Tâm (F07, F12) | CPC | NOT_STARTED |
| P08 | AI Tutor | F08 | Phiên hội thoại, tin nhắn | P04 | Tâm | CPC | NOT_STARTED |
| P09 | Review & Assessment | F09 | Bài ôn tập theo khóa học, chấm điểm, lịch sử | P04, P05, P06 | Tuấn | CPC | NOT_STARTED |
| P10 | Feedback | F10, F13 | Phản hồi học viên và quản trị phản hồi | P03 | Khôi (F10), Hòa (F13) | CPC | NOT_STARTED |
| P11 | User Roadmap Admin & Related Functionality | F14 (+ phần ngoài 14 tính năng) | Quản trị lộ trình người dùng; mẫu lộ trình; dữ liệu lịch sử; quản trị câu hỏi; AI trong bong bóng chat | P03, P07 | Hòa (F14); phần còn lại CPC | CPC | NOT_STARTED |
| P12 | AI/ML Work | (F05, F07, F08, F09) | Các thành phần AI/ML theo BA §8 | P07, P08 | CPC | CPC | NOT_STARTED |
| P13 | Integration, Testing & Documentation | Tất cả | Tích hợp, kiểm thử, sửa lỗi, tài liệu, demo | Các Phase triển khai | CPC | CPC | NOT_STARTED |

---

## PART 4 — DEPENDENCY & PARALLELISM

| Phase/Task | Depends on | Reason | Can run in parallel? |
|---|---|---|---|
| P00 | — | Nhóm quyết định | Có — song song mọi Phase; chỉ các Task cụ thể chờ kết quả P00 |
| P01-T03, P01-T05 | P00-T02, P00-T03 | [NV] cổng/tên DB, ND-16 | Không, cho tới khi chốt |
| P01-T07 | P00-T01 | [NV] G6 — chỉ phần gắn router | Một phần — tạo app, handler lỗi làm được |
| P01-T02, P01-T06 | — | [KT] làm được với phần đã chốt | Có |
| P02 | P01-T03, P01-T05 | [KT] cần engine và Alembic | Có (song song P03, P04 frontend) |
| P03 | — | C1 đã có; D-FE-01…12 đã chốt | Có — song song P00–P02 |
| P04 backend | P01, P02-T02 (bảng `skills`), P00-T04 (ND-44/45 cho `security.py`) | [KT] + [NV] | Có — song song P05 backend |
| P04 frontend | P03-T02, P03-T03 | [KT] | Có — song song P04 backend (dùng mock D-FE-07) |
| P05 | P02, P04-T03 (`get_current_user`, `require_admin`) | [KT] | Có — song song P04 phần còn lại, P08 |
| P06 | P04-T03, P05-T05 | [KT] cần xác thực và Course | Có — song song P07 |
| P07 | P02, P04-T03 | [KT] | Có — song song P05, P06, P08 |
| P08 | P04-T03 | [KT] | Có — song song P05–P07 |
| P09 | P04-T03, P05-T05, P06-T04 | [KT] StudentCourse, Course; RV-R03 | Có — song song P07, P08 |
| P10 giao diện | P03 | [KT]; D-FE-08 | Có — bất kỳ lúc nào sau P03 |
| P10 backend | ND-35, ND-55 (M2), ND-69 | [NV] | Không, cho tới khi chốt |
| P11 | P03; P07-T04 (đồ thị) | [KT]; phần M3, M4 chờ ND-55 | Một phần |
| P12 | P07-T05, P08-T05 | [KT] cần API nền | Có — song song P09 |
| P13 | Các Task triển khai tương ứng | [KT] | Từng phần — có thể kiểm thử theo tính năng khi tính năng đó REVIEW |
| P04-T11 (`summary`) | P06-T04, P07-T04 | [KT] đếm StudentCourse, LearningPath | Không vòng phụ thuộc: P06-T04, P07-T04 không phụ thuộc P04-T11 |

Các nhánh song song chính: **(A)** P00 ∥ P01 ∥ P03; **(B)** sau P01–P02: P04 ∥ P05 ∥ P08; **(C)** sau P04-T03 và P05-T05: P06 ∥ P07 ∥ P09-backend phần không phụ thuộc StudentCourse; **(D)** giao diện P10, P11 bất kỳ lúc nào sau P03.

---

## PART 5 — DETAILED PHASE PLAN

### P00 – Decisions & Blocking Issues

**1. Phase Information** — Phase ID: P00 · Objective: tổng hợp và đưa các vấn đề đang chặn tới người có thẩm quyền; kết quả được ghi trong `docs/decisions.md` (không trong file này) · Related Features: — · Responsible: CPC · Support: CXĐ · Reviewer: CPC · Dependencies: — · Initial Status: NOT_STARTED

**2. Scope** — Trong phạm vi: liệt kê, đưa ra thảo luận, theo dõi tới khi có quyết định. Ngoài phạm vi: tự quyết định thay nhóm; sửa BA/SRS. Nguồn: `docs/decisions.md` §4, §6; `docs/structure.md` §1.3; BA §8.6, §13.2.

**3. Detailed Tasks**

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P00-T01 | Chốt tổ chức router và Docker Compose | Đưa ra quyết định: router phẳng hay `routers/v1/`; tên file Compose | G6; `structure.md` §1.2–§1.3 | CPC | CXĐ | CPC | — | Mục G6 được chốt trong `decisions.md` | NOT_STARTED | — | — |
| P00-T02 | Chốt cổng và tên database | 5432/`edumentor` hay 5433/`edumentor_db`; driver | `structure.md` §1.3; `SETUP.md` §3 | CPC | CXĐ | CPC | — | Quyết định ghi trong `decisions.md` | NOT_STARTED | — | — |
| P00-T03 | Chốt sync/async và lớp commit | Engine sync/async; service hay helper commit | ND-16 | CPC | CXĐ | CPC | — | ND-16 được chốt | NOT_STARTED | — | — |
| P00-T04 | Chốt thư viện JWT và Argon2id | Thư viện và tham số | ND-44, ND-45 | CPC (module owner: Tuấn, D-OWN-01) | CXĐ | CPC | — | ND-44, ND-45 được chốt | NOT_STARTED | — | — |
| P00-T05 | Chốt mã lỗi và quy ước validate | Danh mục `error.code`; 400 hay 422 | ND-14, ND-15 | CPC | CXĐ | CPC | — | ND-14, ND-15 được chốt | NOT_STARTED | — | — |
| P00-T06 | Phân công phần chưa có người | Responsible và reviewer cho P00–P03, P11 (ngoài F14), P12, P13 và reviewer mọi Phase | `README.md`; workbook CK-42 | CPC | CXĐ | CPC | — | Danh sách phân công được nhóm xác nhận | NOT_STARTED | — | — |
| P00-T07 | Giải quyết người phụ trách Feedback | Người phụ trách F10 (Khôi), F13 (Hòa) đã có ở D-OWN-02; `README.md`, `docs/modules/README.md` đã đồng bộ. Còn mở: dòng "Feedback & liên hệ (T22–T25)" ở `decisions.md` §2 vẫn ghi "Chưa rõ: Khôi/Tâm" (ND-35) — quan hệ với D-OWN-02 chờ Tuấn xác nhận | `decisions.md` §2 (D-OWN-02; dòng Feedback & liên hệ); ND-35; C3 (nhãn cũ, không phải ND) | CPC | CXĐ | CPC | — | `decisions.md` §2 cập nhật | NOT_STARTED | — | — |
| P00-T08 | Chốt quy định kiểm thử frontend và responsive | Công cụ, mức kiểm thử, test report; breakpoint, phạm vi thiết bị | ND-67, ND-68; BA NFR-17, NFR-18 | CPC | CXĐ | CPC | — | ND-67, ND-68 được chốt | NOT_STARTED | — | — |
| P00-T09 | Ghi nhận mâu thuẫn trong BA | Ma trận truy vết §13.2 (FR-01–05 token) lệch §6 (token ở FR-44–46, §6.9); BA §8.6 (RAG) chưa thống nhất với D01, RV-R01 — ND-58 chưa nhắc RAG; BA thiếu FR cho phản hồi (chỉ §4.1.2) và F14 | BA §6, §8.6, §13.2; ND-58 | CPC | CXĐ | CPC | — | Đề xuất ND hoặc bổ sung ND-58 do người có thẩm quyền ghi | NOT_STARTED | — | — |
| P00-T10 | Theo dõi các ND chặn tính năng | Đưa ND-41/43/48, ND-56…62, 64, 66, 69, T16 ra thảo luận theo người phụ trách tính năng | `decisions.md` §3, §4, §6 | CPC | CXĐ | CPC | — | Bảng PART 6 được cập nhật khi có quyết định | NOT_STARTED | — | — |

**4. Deliverables** — Các quyết định được ghi trong `docs/decisions.md` bởi người có thẩm quyền; bảng PART 6 cập nhật.
**5. Review Checklist** — Mỗi quyết định có mã D/ND, ngày, người xác nhận; tài liệu bị ảnh hưởng được liệt kê; không có quyết định nào chỉ nằm trong file này.
**6. Blockers & Open Issues** — Chưa có người điều phối P00.
**7. Completion Criteria** — Không bắt buộc hoàn tất toàn bộ để các Phase khác chạy. P00 DONE khi T01–T08 có quyết định ghi trong `docs/decisions.md`; T09–T10 theo dõi liên tục.

### P01 – Backend Foundation

**1. Phase Information** — Phase ID: P01 · Objective: dựng khung backend chạy được theo kiến trúc Router → Service → Repository → Model · Related Features: — · Responsible: CPC · Support: CXĐ · Reviewer: CPC · Dependencies: P00-T01…T03, T05 (một phần) · Initial Status: NOT_STARTED

**2. Scope** — Trong: `backend/app/main.py`, `core/config.py`, `core/database.py`, Alembic, xử lý lỗi dùng chung, `tests/conftest.py`, `requirements.txt`. Ngoài: `core/security.py`, `core/dependencies.py`, `core/email.py` (thuộc module Xác thực — P04); model của tính năng. Nguồn: `docs/structure.md` §1, §1.2, §4; `docs/backend-rules.md`; `docs/conventions.md` §1, §3, §6; `SETUP.md`; PR #1 (`origin/Hoa`).

**3. Detailed Tasks**

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P01-T01 | Đối chiếu backend PR #1 | So `origin/Hoa` (main.py, config, database, routers/v1, requirements, compose) với `structure.md`; ghi phần giữ/đổi | `structure.md` §1.2 | CPC | CXĐ | CPC | — | Bảng đối chiếu trong PR mô tả | NOT_STARTED | — | — |
| P01-T02 | `core/config.py` | Settings đọc biến theo `backend-rules.md` §6 và `.env.example`; không hard-code bí mật | `backend-rules.md` §6; D-AUTH-01, 02; D02, T28 | CPC | CXĐ | CPC | — | `config.py` | NOT_STARTED | — | Một phần: `REVIEW_PASS_PERCENT` chưa có trong `.env.example`; giá trị DB chờ P00-T02 |
| P01-T03 | `core/database.py` | Engine, session, `get_db`, Base | ND-16; `structure.md` §1.2 | CPC | CXĐ | CPC | P00-T03 | `database.py` | BLOCKED | — | ND-16 |
| P01-T04 | `requirements.txt` | Dependency backend đã được duyệt | ND-44, ND-45; CLAUDE.md | CPC | CXĐ | CPC | P00-T04 | `requirements.txt` | NOT_STARTED | — | Một phần: thư viện xác thực chờ ND-44, ND-45 (PR #1 dùng `bcrypt`, trái D-AUTH-04); driver PostgreSQL chờ cổng/DB. Các thư viện trong CLAUDE.md "Công nghệ" liệt kê được ngay |
| P01-T05 | Khởi tạo Alembic | `alembic.ini`, `alembic/env.py` dùng Base và cấu hình | `backend-rules.md` §9; `conventions.md` §3 | CPC | CXĐ | CPC | P01-T03 | Alembic chạy `upgrade head` trên DB rỗng | BLOCKED | — | Theo P01-T03; P00-T02 |
| P01-T06 | Xử lý lỗi dùng chung | Exception handler trả `{"error": {"code","message","details"}}`; không lộ stack trace | `backend-rules.md` §4; `conventions.md` §1 | CPC | CXĐ | CPC | — | Handler + test | NOT_STARTED | — | Một phần: ND-14 (danh mục code), ND-15 (400/422) |
| P01-T07 | `main.py` và gắn router | FastAPI app, CORS, gắn router theo cấu trúc đã chốt | G6; D-FE-10 (tiền tố `/api`) | CPC | CXĐ | CPC | P00-T01 | `main.py` | NOT_STARTED | — | Một phần: gắn router chờ G6 (P00-T01). Tạo app, đăng ký handler lỗi, tiền tố `/api` (D-FE-10) làm được |
| P01-T08 | Hạ tầng test backend | `tests/conftest.py`: DB test, client, fixture user/admin | `conventions.md` §6 | CPC | CXĐ | CPC | P01-T03, P01-T05 | `pytest` chạy được | BLOCKED | — | Loại DB dùng cho test chưa có trong tài liệu; theo P01-T03 |
| P01-T09 | Docker Compose cho PostgreSQL | Cấu hình theo quyết định G6 và P00-T02 | G6; `structure.md` §1.3 | CPC | CXĐ | CPC | P00-T01, P00-T02 | File Compose | BLOCKED | — | G6; cổng/tên DB |
| P01-T10 | Cập nhật `SETUP.md` theo nền đã chốt | Thay các ghi chú "chưa chốt" bằng giá trị đã chốt | `SETUP.md` §3–§5 | CPC | CXĐ | CPC | P01-T02…T09 | `SETUP.md` | BLOCKED | — | Cốt lõi (ghi giá trị đã chốt vào `SETUP.md`) chờ G6 và cổng/tên DB qua P01-T03…T09 |

**4. Deliverables** — Backend khởi động được; Alembic chạy; `pytest` chạy trên DB test; `SETUP.md` đúng thực tế.
**5. Review Checklist** — Đúng phân lớp (`structure.md` §4); cấu hình đọc từ môi trường (`backend-rules.md` §6); lỗi đúng cấu trúc (§4); không commit `.env`; dependency đã được duyệt.
**6. Blockers & Open Issues** — G6, ND-14, 15, 16, 44, 45; cổng/tên DB; DB dùng cho test; PR #1 chưa merge.
**7. Completion Criteria** — T02–T10 DONE có evidence (`uvicorn` khởi động, `alembic upgrade head`, `pytest` chạy).

### P02 – Shared Data Foundation

**1. Phase Information** — Phase ID: P02 · Objective: bảng dữ liệu dùng chung và dữ liệu mẫu từ dataset · Related Features: F02, F11 (Course, Skill), F12 (SkillRelation), F05–F07 (dùng dữ liệu) · Responsible: CPC · Support: CXĐ · Reviewer: CPC · Dependencies: P01-T03, P01-T05 · Initial Status: NOT_STARTED

**2. Scope** — Trong: model + migration Course, Skill, CourseSkillRelation, SkillRelation; script nạp dataset. Ngoài: bảng của từng module (P04–P11). Nguồn: `docs/database-design.md` §1 "Nguồn dữ liệu", §2.1–§2.4; BA §8.3; PR #1 (`2d03aa3` có model và seed).

**3. Detailed Tasks**

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P02-T01 | Model + migration `Course` | Đúng cột, kiểu, ràng buộc; xử lý dữ liệu theo bảng "Nguồn dữ liệu" | `database-design.md` §1, §2.1 | CPC | CXĐ | CPC | P01-T05 | Model + migration | NOT_STARTED | — | Một phần: migration chờ Alembic (P01-T05). Class model viết được theo §2.1 |
| P02-T02 | Model + migration `Skill` | — | §2.2 | CPC | CXĐ | CPC | P01-T05 | Model + migration | NOT_STARTED | — | Một phần: migration chờ Alembic (P01-T05). Class model viết được theo §2.2 |
| P02-T03 | Model + migration `CourseSkillRelation` | Khóa chính ghép, FK | §2.3, §8.2 | CPC | CXĐ | CPC | P02-T01, P02-T02 | Model + migration | NOT_STARTED | — | Một phần: migration chờ Alembic (P01-T05). Class model viết được theo §2.3 |
| P02-T04 | Model + migration `SkillRelation` | `relation_type`; chiều quan hệ ghi "cần xác nhận" | §2.4 | CPC | CXĐ | CPC | P02-T02 | Model + migration | NOT_STARTED | — | Một phần: migration chờ Alembic (P01-T05); chiều quan hệ chưa xác nhận (§1 "Nguồn dữ liệu"). Class model viết được theo §2.4 |
| P02-T05 | Đưa dataset vào nơi dùng được | Dataset (course_table, skill_table, course_skill_relation, skill_relation) **không có trong repo**; xác định nguồn và nơi lưu | `database-design.md` §1 | CPC | CXĐ | CPC | — | Dataset có đường dẫn ổn định | NOT_STARTED | — | Vị trí dataset chưa xác định |
| P02-T06 | Script nạp dữ liệu mẫu | `scripts/seed_data.py` theo quy tắc chuyển đổi §1 | `database-design.md` §1; `SETUP.md` §5 | CPC | CXĐ | CPC | P02-T01…T05 | Script + log nạp | NOT_STARTED | — | Một phần: chạy thật cần model (P02-T01…T04) và dataset (P02-T05). Logic chuyển đổi theo §1 viết được |
| P02-T07 | Đối chiếu model/seed trên PR #1 | So model `course`, `skill`, `skill_relation`, seed của `origin/Hoa` với §2 | `structure.md` §1.2; `database-design.md` §2 | CPC | CXĐ | CPC | — | Bảng khác biệt | NOT_STARTED | — | — |

**4. Deliverables** — 4 bảng có migration; dữ liệu mẫu nạp được.
**5. Review Checklist** — Khớp `database-design.md` từng cột và ràng buộc; thay đổi qua Alembic; script nạp lặp lại được.
**6. Blockers & Open Issues** — Theo P01; chiều SkillRelation; vị trí dataset.
**7. Completion Criteria** — T01–T06 DONE, có kết quả `alembic upgrade head` và số dòng đã nạp.

### P03 – Frontend Foundation

**1. Phase Information** — Phase ID: P03 · Objective: nền frontend dùng chung cho 14 tính năng · Related Features: tất cả (giao diện) · Responsible: CPC · Support: CXĐ · Reviewer: CPC · Dependencies: — · Initial Status: IN_PROGRESS (P03-T01 ở REVIEW)

**2. Scope** — Trong: route, guard, `client.js`, layout, component dùng chung, chế độ mock, khung bong bóng chat, skill `frontend-ui`. Ngoài: page của từng tính năng. Nguồn: `docs/decisions.md` §6 (D-FE-01…12), D-DOC-02; `docs/structure.md` §1, §3; `docs/conventions.md` §4; `docs/ui-design/`.

**3. Detailed Tasks**

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P03-T01 | Phần nền C1 (hiện trạng) | `package.json`, `vite.config.js`, `index.html`, `src/main.jsx`, `App.jsx`, `index.css`, `utils/theme.js`; build chạy được. Còn thiếu: chưa có review | D-FE-09; `structure.md` §1.1 | CPC | CXĐ | CPC | — | Nền React/Vite | REVIEW | Commit `a13cb8f` (9 file). `npm run build` ngày 2026-10-30 trên nội dung trùng `a13cb8f` (frontend không khác commit): thành công, 33 module, 1,43 s; lockfile không đổi. Chưa có kiểm thử, chưa có review | — |
| P03-T02 | Khai báo route và guard | `routes/index.jsx` theo bảng `structure.md` §3; `ProtectedRoute`, `AdminRoute` chỉ ẩn giao diện | D-FE-04, D-FE-06; `structure.md` §3 | CPC | CXĐ | CPC | P03-T01 | Route + guard | NOT_STARTED | — | Một phần: ND-50 (4 route demo), ND-52 (chuyển hướng) |
| P03-T03 | API client dùng chung | `api/client.js`: Axios, `VITE_API_BASE_URL`, Bearer từ `sessionStorage`, chuẩn hóa lỗi, 401 → xóa token, về `/login` | D-FE-05, D-FE-10; `conventions.md` §4 | CPC | CXĐ | CPC | P03-T01 | `client.js` | NOT_STARTED | — | Không làm refresh (ND-41, ND-48) |
| P03-T04 | Component layout | Header, PageLayout, AuthLayout, AdminLayout, SettingsLayout, Logo, HangingLamp, PullLamp | `structure.md` §1; `ui-design` | CPC | CXĐ | CPC | P03-T01 | Component + `.module.css` | NOT_STARTED | — | — |
| P03-T05 | Component dùng chung | Button, Modal, ConfirmDialog, Toast, Tabs, PasswordInput, PasswordRules, ErrorMessage, Pagination, ThemeToggle, Icons, AnimatedNumber; xử lý trạng thái tải/rỗng/lỗi, bàn phím, reduced-motion | `structure.md` §1; `conventions.md` §4; D-FE-09 | CPC | CXĐ | CPC | P03-T01 | Component + `.module.css` | NOT_STARTED | — | PasswordRules: chỉ điều kiện đã chốt (D-AUTH-05; ND-46, ND-51) |
| P03-T06 | Chế độ mock | `src/mock/` chỉ chạy khi `VITE_USE_MOCK=true` | D-FE-07 | CPC | CXĐ | CPC | P03-T03 | Mock data + công tắc | NOT_STARTED | — | — |
| P03-T07 | Bong bóng chat — phần lối tắt | `ChatBubble`: GitHub, Zalo, Liên hệ; ẩn ở `/admin/*`, `/tutor`, `/consultant`, trang làm bài | `structure.md` §3; `ui-design` ChatBubble-Menu | CPC | CXĐ | CPC | P03-T05 | Component | NOT_STARTED | — | Một phần: link và người phụ trách chưa xác định (UI2-04, `decisions.md` §5); phần AI: P11-T07 |
| P03-T08 | Xử lý file frontend cấu trúc cũ | Giữ/đổi tên/xóa các file đánh dấu ND-49 | ND-49 | CPC | CXĐ | CPC | — | Theo quyết định | BLOCKED | — | ND-49 |
| P03-T09 | Tạo skill `frontend-ui` | `.claude/skills/frontend-ui/SKILL.md` chỉ chứa tham chiếu; tách phần riêng trong 2 skill module | D-DOC-02 | CPC | CXĐ | CPC | — | Skill | NOT_STARTED | — | — |

**4. Deliverables** — Ứng dụng mở được các route với layout; client và component dùng chung sẵn sàng; skill `frontend-ui`.
**5. Review Checklist** — Đúng cây `structure.md` §1; component không gọi `fetch`/`axios` trực tiếp; dùng biến CSS; reduced-motion; không thêm thư viện ngoài D-FE-09; an toàn điều hướng (`conventions.md` §4).
**6. Blockers & Open Issues** — ND-41, 48, 49, 50, 52; UI2-04.
**7. Completion Criteria** — T01–T07, T09 DONE; T08 theo ND-49.

### P04 – Authentication & Profile (F01)

> Task của tính năng [F01](F01-authentication-profile/phase-04-authentication-profile.md) được quản lý trong thư mục tính năng từ 2026-11-03 (D-DOC-05 (8)). Bảng dưới chỉ là chỉ mục, **không** có trạng thái.

**1. Phase Information** — Phase ID: P04 · Objective: F01 đầy đủ backend và frontend theo đặc tả · Related Features: F01 · Responsible: Tuấn (D-OWN-01, D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P01, P02-T02, P03-T02/T03/T05 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/auth/*`, `/api/me*` (trừ courses, bookmarks, review-history, learning-paths), bảng User, UserSkill, PasswordResetToken, `core/security.py`, `core/dependencies.py`, `core/email.py`, `scripts/create_admin.py`, trang `/login` … `/me/skills`. Ngoài: RefreshToken (chờ ND-43); Course Tracking; Learning Path. Nguồn: `docs/modules/auth-profile.md`, `.tests.md`; `docs/api-endpoints.md` §2; `docs/database-design.md` §3.1, §3.2, §3.4; BA §6.1 (FR-01–04), §6.9 (FR-40–46); `ui-design` Main, Main-LampOff, Register, ForgotPassword, ForgotSent, ResetPassword, ResetExpired, Profile, Profile-Light, EditProfile, ChangePassword, Skills, Logout.

**3. Detailed Tasks**

Chỉ mục Task đã chuyển:

| Task ID | Task Name | Feature | Quản lý tại |
|---|---|---|---|
| P04-T01 | Đối chiếu đặc tả F01 với BA | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T02 | `core/security.py` | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T03 | `core/dependencies.py` | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T04 | Model + migration User, UserSkill, PasswordResetToken | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T05 | `POST /api/auth/register` | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T06 | `POST /api/auth/login` (access token) | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T07 | Refresh token và logout | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T08 | Quên và đặt lại mật khẩu, `core/email.py` | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T09 | `GET/PATCH /api/me`, đổi mật khẩu | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T10 | `POST /api/me/avatar` | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T11 | `GET /api/me/summary` | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T12 | `GET/PATCH /api/me/skills` | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T13 | `scripts/create_admin.py` | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T14 | Test backend F01 | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T15 | API client F01 | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T16 | Trang Đăng nhập, Đăng ký | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T17 | Trang Quên/đặt lại mật khẩu | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T18 | Trang Hồ sơ | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T19 | Trang Sửa hồ sơ, Đổi mật khẩu | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T20 | Trang Kỹ năng | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T21 | Đăng xuất | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |
| P04-T22 | Test giao diện F01 | F01 | [F01-authentication-profile/phase-04-authentication-profile.md](F01-authentication-profile/phase-04-authentication-profile.md) |

**4–7. Deliverables, Review Checklist, Blockers, Completion Criteria** — chuyển sang [F01](F01-authentication-profile/phase-04-authentication-profile.md) mục 3.

### P05 – Course Catalog & Admin Courses (F02, F11)

> Task của tính năng [F02](F02-course-catalog/phase-05-course-catalog-admin-courses.md), [F11](F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md) được quản lý trong thư mục tính năng từ 2026-11-03 (D-DOC-05 (8)). Bảng dưới chỉ là chỉ mục, **không** có trạng thái.

**1. Phase Information** — Phase ID: P05 · Objective: danh mục khóa học cho học viên và quản trị khóa học, kỹ năng, liên kết · Related Features: F02, F11 · Responsible: theo từng tính năng — F02: Khôi, F11: Hòa (D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P02, P03, P04-T03 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/courses*`, `/api/admin/courses`, `/api/admin/skills`, `/api/admin/course-skill-relations`; trang Courses, Courses-Light, CourseDetail, JoinDialog (giao diện), AdminCourses, AdminSkills (phần danh mục). Ngoài: `join` backend (P06); quan hệ kỹ năng (P07); quản trị câu hỏi (P11). Nguồn: `docs/api-endpoints.md` §3, §11; `docs/database-design.md` §2; BA §6.3 (FR-12–16), §6.7 (FR-30, 32, 33); SRS FR-02.

**3. Detailed Tasks**

Chỉ mục Task đã chuyển:

| Task ID | Task Name | Feature | Quản lý tại |
|---|---|---|---|
| P05-T01 | Rà soát nguồn F02, F11 | F02 | [F02-course-catalog/phase-05-course-catalog-admin-courses.md](F02-course-catalog/phase-05-course-catalog-admin-courses.md) |
| P05-T02 | Chuẩn bị đặc tả module | F02 | [F02-course-catalog/phase-05-course-catalog-admin-courses.md](F02-course-catalog/phase-05-course-catalog-admin-courses.md) |
| P05-T03 | Chuẩn bị test case | F02 | [F02-course-catalog/phase-05-course-catalog-admin-courses.md](F02-course-catalog/phase-05-course-catalog-admin-courses.md) |
| P05-T04 | `GET /api/courses` | F02 | [F02-course-catalog/phase-05-course-catalog-admin-courses.md](F02-course-catalog/phase-05-course-catalog-admin-courses.md) |
| P05-T05 | `GET /api/courses/{id}`, `/skills` | F02 | [F02-course-catalog/phase-05-course-catalog-admin-courses.md](F02-course-catalog/phase-05-course-catalog-admin-courses.md) |
| P05-T06 | Quản trị khóa học | F11 | [F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md](F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md) |
| P05-T07 | Quản trị kỹ năng | F11 | [F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md](F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md) |
| P05-T08 | Quản trị liên kết khóa học–kỹ năng | F11 | [F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md](F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md) |
| P05-T09 | Test phân quyền admin (bắt buộc) | F11 | [F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md](F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md) |
| P05-T10 | API client khóa học | F02 | [F02-course-catalog/phase-05-course-catalog-admin-courses.md](F02-course-catalog/phase-05-course-catalog-admin-courses.md) |
| P05-T11 | Trang Danh mục | F02 | [F02-course-catalog/phase-05-course-catalog-admin-courses.md](F02-course-catalog/phase-05-course-catalog-admin-courses.md) |
| P05-T12 | Trang Chi tiết khóa học, hộp thoại Tham gia | F02 | [F02-course-catalog/phase-05-course-catalog-admin-courses.md](F02-course-catalog/phase-05-course-catalog-admin-courses.md) |
| P05-T13 | Trang Quản trị khóa học | F11 | [F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md](F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md) |
| P05-T14 | Trang Quản trị kỹ năng (danh mục) | F11 | [F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md](F11-admin-courses-skills-relations/phase-05-course-catalog-admin-courses.md) |

**4–7. Deliverables, Review Checklist, Blockers, Completion Criteria** — chuyển sang [F02](F02-course-catalog/phase-05-course-catalog-admin-courses.md) mục 3.

### P06 – Bookmark & Learning Progress (F03, F04)

> Task của tính năng [F03](F03-bookmark/phase-06-bookmark-learning-progress.md), [F04](F04-course-progress/phase-06-bookmark-learning-progress.md) được quản lý trong thư mục tính năng từ 2026-11-03 (D-DOC-05 (8)). Bảng dưới chỉ là chỉ mục, **không** có trạng thái.

**1. Phase Information** — Phase ID: P06 · Objective: lưu khóa học và theo dõi 4 trạng thái học · Related Features: F03 (Tâm), F04 (Hòa) · Responsible: theo từng task — F03: Tâm, F04: Hòa (D-OWN-02); task gồm cả hai tính năng: CPC · Support: CXĐ · Reviewer: CPC · Dependencies: P04-T03, P05-T05 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/me/bookmarks*`, `/api/me/courses*`, `/api/courses/{id}/join`, bảng StudentCourse; trang MyCourses; nút Lưu. Ngoài: gợi ý theo node (P07). Nguồn: `docs/api-endpoints.md` §4; `docs/database-design.md` §3.3; D05; BA §6.4 (FR-17–19); `ui-design` MyCourses.

**3. Detailed Tasks**

Chỉ mục Task đã chuyển:

| Task ID | Task Name | Feature | Quản lý tại |
|---|---|---|---|
| P06-T01 | Rà soát nguồn F03, F04 | F04 | [F04-course-progress/phase-06-bookmark-learning-progress.md](F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T02 | Chuẩn bị đặc tả module | F04 | [F04-course-progress/phase-06-bookmark-learning-progress.md](F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T03 | Chuẩn bị test case | F04 | [F04-course-progress/phase-06-bookmark-learning-progress.md](F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T04 | Model + migration StudentCourse | F04 | [F04-course-progress/phase-06-bookmark-learning-progress.md](F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T05 | API bookmark | F03 | [F03-bookmark/phase-06-bookmark-learning-progress.md](F03-bookmark/phase-06-bookmark-learning-progress.md) |
| P06-T06 | API tham gia khóa học | F04 | [F04-course-progress/phase-06-bookmark-learning-progress.md](F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T07 | API trạng thái khóa học của tôi | F04 | [F04-course-progress/phase-06-bookmark-learning-progress.md](F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T08 | Test chuyển trạng thái (bắt buộc) | F04 | [F04-course-progress/phase-06-bookmark-learning-progress.md](F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T09 | API client theo dõi | F04 | [F04-course-progress/phase-06-bookmark-learning-progress.md](F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T10 | Nút Lưu | F03 | [F03-bookmark/phase-06-bookmark-learning-progress.md](F03-bookmark/phase-06-bookmark-learning-progress.md) |
| P06-T11 | Trang Khóa học của tôi | F04 | [F04-course-progress/phase-06-bookmark-learning-progress.md](F04-course-progress/phase-06-bookmark-learning-progress.md) |

**4–7. Deliverables, Review Checklist, Blockers, Completion Criteria** — chuyển sang [F04](F04-course-progress/phase-06-bookmark-learning-progress.md) mục 3.

### P07 – Roadmap, AI Consultant & Recommendations (F05, F06, F07, F12)

> Task của tính năng [F05](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md), [F06](F06-roadmap-nodes-edges/phase-07-roadmap-consultant-recommendations.md), [F07](F07-skill-course-recommendation/phase-07-roadmap-consultant-recommendations.md), [F12](F12-admin-skill-relations/phase-07-roadmap-consultant-recommendations.md) được quản lý trong thư mục tính năng từ 2026-11-03 (D-DOC-05 (8)). Bảng dưới chỉ là chỉ mục, **không** có trạng thái.

**1. Phase Information** — Phase ID: P07 · Objective: tư vấn mục tiêu, lộ trình đồ thị, node/cạnh, gợi ý khóa học theo node, quan hệ kỹ năng · Related Features: F05, F06, F07, F12 · Responsible: theo từng tính năng — F05, F06: Hòa; F07, F12: Tâm (D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P02, P04-T03 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/chat/learning-path`, `/api/learning-paths*`, `/api/me/learning-paths`, node, edge, gợi ý §8, `/api/admin/skill-relations*`; bảng LearningPath, Node, Edge; trang Consultant, MyPaths, PathDetail, PathEdit, AdminSkills-Relations. Ngoài: thành phần mô hình AI (P12); mẫu lộ trình cơ sở (P11). Nguồn: `docs/api-endpoints.md` §5–§8, §11; `docs/database-design.md` §4.4–§4.6, §2.4; BA §6.2 (FR-05–11), §6.3 (FR-12–14), §6.7 (FR-31); SRS FR-03.

**3. Detailed Tasks**

Chỉ mục Task đã chuyển:

| Task ID | Task Name | Feature | Quản lý tại |
|---|---|---|---|
| P07-T01 | Rà soát nguồn F05–F07, F12 | F05 | [F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T02 | Chuẩn bị đặc tả module | F05 | [F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T03 | Chuẩn bị test case | F05 | [F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T04 | Model + migration lộ trình | F05 | [F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T05 | API AI Consultant | F05 | [F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T06 | API lộ trình | F05 | [F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T07 | API node và cạnh | F06 | [F06-roadmap-nodes-edges/phase-07-roadmap-consultant-recommendations.md](F06-roadmap-nodes-edges/phase-07-roadmap-consultant-recommendations.md) |
| P07-T08 | API gợi ý khóa học theo node | F07 | [F07-skill-course-recommendation/phase-07-roadmap-consultant-recommendations.md](F07-skill-course-recommendation/phase-07-roadmap-consultant-recommendations.md) |
| P07-T09 | API quản trị quan hệ kỹ năng | F12 | [F12-admin-skill-relations/phase-07-roadmap-consultant-recommendations.md](F12-admin-skill-relations/phase-07-roadmap-consultant-recommendations.md) |
| P07-T10 | Test backend (gồm xóa node kèm cạnh) | F05 | [F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T11 | API client | F05 | [F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T12 | Trang AI tư vấn lộ trình | F05 | [F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T13 | Trang Lộ trình của tôi | F05 | [F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T14 | Trang Chi tiết lộ trình và đồ thị | F06 | [F06-roadmap-nodes-edges/phase-07-roadmap-consultant-recommendations.md](F06-roadmap-nodes-edges/phase-07-roadmap-consultant-recommendations.md) |
| P07-T15 | Hộp thoại sửa lộ trình | F06 | [F06-roadmap-nodes-edges/phase-07-roadmap-consultant-recommendations.md](F06-roadmap-nodes-edges/phase-07-roadmap-consultant-recommendations.md) |
| P07-T16 | Sơ đồ quan hệ kỹ năng (quản trị) | F12 | [F12-admin-skill-relations/phase-07-roadmap-consultant-recommendations.md](F12-admin-skill-relations/phase-07-roadmap-consultant-recommendations.md) |

**4–7. Deliverables, Review Checklist, Blockers, Completion Criteria** — chuyển sang [F05](F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) mục 3.

### P08 – AI Tutor (F08)

> Task của tính năng [F08](F08-ai-tutor-chat/phase-08-ai-tutor.md) được quản lý trong thư mục tính năng từ 2026-11-03 (D-DOC-05 (8)). Bảng dưới chỉ là chỉ mục, **không** có trạng thái.

**1. Phase Information** — Phase ID: P08 · Objective: phiên hội thoại AI Tutor · Related Features: F08 · Responsible: Tâm (D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P04-T03 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/chat/sessions*`; bảng ChatSession, ChatMessage; trang Tutor. Ngoài: thiết kế mô hình và prompt (P12-T06). Nguồn: `docs/api-endpoints.md` §9; `docs/database-design.md` §5; BA §6.5 (FR-20–23); SRS FR-04–06, FR-08.

**3. Detailed Tasks**

Chỉ mục Task đã chuyển:

| Task ID | Task Name | Feature | Quản lý tại |
|---|---|---|---|
| P08-T01 | Rà soát nguồn F08 | F08 | [F08-ai-tutor-chat/phase-08-ai-tutor.md](F08-ai-tutor-chat/phase-08-ai-tutor.md) |
| P08-T02 | Chuẩn bị đặc tả module | F08 | [F08-ai-tutor-chat/phase-08-ai-tutor.md](F08-ai-tutor-chat/phase-08-ai-tutor.md) |
| P08-T03 | Chuẩn bị test case | F08 | [F08-ai-tutor-chat/phase-08-ai-tutor.md](F08-ai-tutor-chat/phase-08-ai-tutor.md) |
| P08-T04 | Model + migration ChatSession, ChatMessage | F08 | [F08-ai-tutor-chat/phase-08-ai-tutor.md](F08-ai-tutor-chat/phase-08-ai-tutor.md) |
| P08-T05 | API phiên và tin nhắn | F08 | [F08-ai-tutor-chat/phase-08-ai-tutor.md](F08-ai-tutor-chat/phase-08-ai-tutor.md) |
| P08-T06 | Test backend F08 | F08 | [F08-ai-tutor-chat/phase-08-ai-tutor.md](F08-ai-tutor-chat/phase-08-ai-tutor.md) |
| P08-T07 | API client Tutor | F08 | [F08-ai-tutor-chat/phase-08-ai-tutor.md](F08-ai-tutor-chat/phase-08-ai-tutor.md) |
| P08-T08 | Trang AI Tutor | F08 | [F08-ai-tutor-chat/phase-08-ai-tutor.md](F08-ai-tutor-chat/phase-08-ai-tutor.md) |

**4–7. Deliverables, Review Checklist, Blockers, Completion Criteria** — chuyển sang [F08](F08-ai-tutor-chat/phase-08-ai-tutor.md) mục 3.

### P09 – Review & Assessment (F09)

> Task của tính năng [F09](F09-review-assessment/phase-09-review-assessment.md) được quản lý trong thư mục tính năng từ 2026-11-03 (D-DOC-05 (8)). Bảng dưới chỉ là chỉ mục, **không** có trạng thái.

**1. Phase Information** — Phase ID: P09 · Objective: bài ôn tập 20 câu theo khóa học, chấm điểm, ghi nhận kỹ năng · Related Features: F09 · Responsible: Tuấn (D-OWN-01, D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P04-T03, P05-T05, P06-T04 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/courses/{id}/review*`, `/api/review-attempts*`, `/api/me/review-history*`; bảng Question, ReviewAttempt, ReviewAnswer; trang ReviewStart, ReviewQuiz, ReviewResult, ReviewHistory, ReviewDetail (+Explanation). Ngoài: `/api/admin/questions*` (P11, CONFLICT-SCOPE-01); RAG (P12-T07). Nguồn: `docs/modules/review-assessment.md`, `.tests.md`; `docs/api-endpoints.md` §10; `docs/database-design.md` §6; D01–D04, D10; BA §6.6 (FR-24–29).

**3. Detailed Tasks**

Chỉ mục Task đã chuyển:

| Task ID | Task Name | Feature | Quản lý tại |
|---|---|---|---|
| P09-T01 | Đối chiếu đặc tả F09 với BA/SRS | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T02 | Model + migration ôn tập | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T03 | Nguồn dữ liệu câu hỏi | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T04 | `GET /api/courses/{id}/review` | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T05 | `POST …/review-attempts` | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T06 | `GET /api/review-attempts/{id}` | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T07 | `POST …/submit` (một transaction) | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T08 | Email kết quả | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T09 | Lịch sử ôn tập | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T10 | Test backend F09 | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T11 | API client ôn tập | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T12 | Trang Bắt đầu ôn tập | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T13 | Trang Làm bài | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T14 | Trang Kết quả | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |
| P09-T15 | Trang Lịch sử, Chi tiết lần làm | F09 | [F09-review-assessment/phase-09-review-assessment.md](F09-review-assessment/phase-09-review-assessment.md) |

**4–7. Deliverables, Review Checklist, Blockers, Completion Criteria** — chuyển sang [F09](F09-review-assessment/phase-09-review-assessment.md) mục 3.

### P10 – Feedback (F10, F13)

> Task của tính năng [F10](F10-feedback/phase-10-feedback.md), [F13](F13-admin-feedback/phase-10-feedback.md) được quản lý trong thư mục tính năng từ 2026-11-03 (D-DOC-05 (8)). Bảng dưới chỉ là chỉ mục, **không** có trạng thái.

**1. Phase Information** — Phase ID: P10 · Objective: giao diện phản hồi và quản trị phản hồi; backend khi có quyết định · Related Features: F10, F13 · Responsible: theo từng tính năng — F10: Khôi, F13: Hòa (D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P03 (giao diện); ND-35, ND-55, ND-69 (backend) · Initial Status: NOT_STARTED

**2. Scope** — Trong: trang Contact, ContactGuest, AdminFeedback, AdminFeedback-Detail ở trạng thái "chưa khả dụng" (D-FE-08); rà soát nguồn. Ngoài: endpoint M2 cho tới khi có quyết định. Nguồn: `docs/database-design.md` §7; `docs/decisions.md` D11, ND-35, ND-55, ND-69; BA §4.1.2 (không có FR riêng); `ui-design`.

**3. Detailed Tasks**

Chỉ mục Task đã chuyển:

| Task ID | Task Name | Feature | Quản lý tại |
|---|---|---|---|
| P10-T01 | Rà soát nguồn phản hồi | F10 | [F10-feedback/phase-10-feedback.md](F10-feedback/phase-10-feedback.md) |
| P10-T02 | Chuẩn bị đặc tả module | F10 | [F10-feedback/phase-10-feedback.md](F10-feedback/phase-10-feedback.md) |
| P10-T03 | Trang Liên hệ và góp ý | F10 | [F10-feedback/phase-10-feedback.md](F10-feedback/phase-10-feedback.md) |
| P10-T04 | Trạng thái chưa đăng nhập | F10 | [F10-feedback/phase-10-feedback.md](F10-feedback/phase-10-feedback.md) |
| P10-T05 | Trang Quản trị phản hồi | F13 | [F13-admin-feedback/phase-10-feedback.md](F13-admin-feedback/phase-10-feedback.md) |
| P10-T06 | Backend phản hồi (M2) | F10 | [F10-feedback/phase-10-feedback.md](F10-feedback/phase-10-feedback.md) |

**4–7. Deliverables, Review Checklist, Blockers, Completion Criteria** — chuyển sang [F10](F10-feedback/phase-10-feedback.md) mục 3.

### P11 – User Roadmap Admin & Related Functionality (F14)

> Task của tính năng [F14](F14-admin-user-learning-roadmap/phase-11-user-roadmap-admin.md) được quản lý trong thư mục tính năng từ 2026-11-03 (D-DOC-05 (8)). Bảng dưới chỉ là chỉ mục, **không** có trạng thái.

**1. Phase Information** — Phase ID: P11 · Objective: quản trị lộ trình người dùng (F14) và các chức năng quản trị ngoài 14 tính năng · Related Features: F14 · Responsible: Hòa (F14, D-OWN-02); các Task ngoài F14: CPC · Support: CXĐ · Reviewer: CPC · Dependencies: P03, P07-T04 · Initial Status: NOT_STARTED

**2. Scope** — Trong: AdminUserPaths; mẫu lộ trình cơ sở (§12); dữ liệu lộ trình lịch sử (§13, tùy chọn); quản trị câu hỏi; AI tư vấn trong bong bóng chat. Nguồn: `README.md` (F14, các màn quản trị khác); `docs/api-endpoints.md` §12, §13; `docs/database-design.md` §4.1–§4.3; ND-53, ND-55; BA §6.7 (FR-34, 35), §6.8 (FR-36–39). Ghi chú: BA không có FR riêng cho F14; `database-design.md` **không có bảng** cho dữ liệu lộ trình lịch sử của §13.

**3. Detailed Tasks**

Task quản lý tại file này (dùng chung hoặc ngoài 14 tính năng):

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P11-T04 | Mẫu lộ trình cơ sở | Bảng §4.1–§4.3, API §12, AdminBasePathsPage | §12; §4.1–§4.3; BA FR-34 | CPC | CXĐ | CPC | P02-T02, P04-T03 | API + page | NOT_STARTED | — | Một phần: chạy thật cần P02-T02, P04-T03; ND-54 (trường `used`). API §12 và bảng §4.1–§4.3 đã có |
| P11-T05 | Dữ liệu lộ trình lịch sử (tùy chọn) | API §13, AdminHistoricalPage | §13; BA FR-35–39, AC-09 | CPC | CXĐ | CPC | P04-T03 | API + page | BLOCKED | — | Chưa có bảng dữ liệu lịch sử trong `database-design.md` (chưa có ND); định dạng file nhập chưa chốt. (Phân công: Chưa phân công — xem cột Responsible) |
| P11-T06 | Quản trị câu hỏi | `/api/admin/questions*` (T19–T21) | ND-53; CONFLICT-SCOPE-01 | CPC | CXĐ | CPC | P09-T02 | API + page | BLOCKED | — | ND-53; CONFLICT-SCOPE-01 |
| P11-T07 | AI tư vấn khóa học trong bong bóng chat | Phần AI của ChatBubble | ND-55 (M4); `ui-design` ChatBubble-Advisor | CPC | CXĐ | CPC | P03-T07 | Component + API | BLOCKED | — | ND-55 (M4); UI2-04 |

Chỉ mục Task đã chuyển:

| Task ID | Task Name | Feature | Quản lý tại |
|---|---|---|---|
| P11-T01 | Rà soát nguồn F14 | F14 | [F14-admin-user-learning-roadmap/phase-11-user-roadmap-admin.md](F14-admin-user-learning-roadmap/phase-11-user-roadmap-admin.md) |
| P11-T02 | Trang Lộ trình người dùng | F14 | [F14-admin-user-learning-roadmap/phase-11-user-roadmap-admin.md](F14-admin-user-learning-roadmap/phase-11-user-roadmap-admin.md) |
| P11-T03 | Backend lộ trình người dùng (M3) | F14 | [F14-admin-user-learning-roadmap/phase-11-user-roadmap-admin.md](F14-admin-user-learning-roadmap/phase-11-user-roadmap-admin.md) |

**4. Deliverables** — AdminUserPaths "chưa khả dụng"; các phần khác theo quyết định.
**5. Review Checklist** — Không tạo endpoint hay bảng chưa có trong tài liệu; giao diện "chưa khả dụng" đúng D-FE-08.
**6. Blockers & Open Issues** — ND-53, ND-54, ND-55 (M3, M4); bảng dữ liệu lịch sử; người phụ trách.
**7. Completion Criteria** — Task không bị chặn DONE.

### P12 – AI/ML Work

> Task của tính năng [F05](F05-ai-consultant-learning-roadmap/phase-12-ai-ml.md), [F07](F07-skill-course-recommendation/phase-12-ai-ml.md), [F08](F08-ai-tutor-chat/phase-12-ai-ml.md), [F09](F09-review-assessment/phase-12-ai-ml.md) được quản lý trong thư mục tính năng từ 2026-11-03 (D-DOC-05 (8)). Bảng dưới chỉ là chỉ mục, **không** có trạng thái.

**1. Phase Information** — Phase ID: P12 · Objective: các thành phần AI/ML theo BA §8, chỉ ở phạm vi đã có căn cứ · Related Features: F05, F07 (Consultant, gợi ý), F08 (Tutor), F09 (RAG — chưa thống nhất) · Responsible: CPC · Support: CXĐ · Reviewer: CPC · Dependencies: P07-T05, P07-T08, P08-T05 · Initial Status: NOT_STARTED

**2. Scope** — Trong: ánh xạ BA §8 vào F01–F14; kiểm tra đầu ra AI; xếp hạng gợi ý; đánh giá chất lượng (AC-10). Ngoài: chọn mô hình, công nghệ hay phương pháp chưa được phê duyệt (QLoRA, mô hình cụ thể ở BA §8.2 là **đề xuất của BA**, chưa có D-xx). Nguồn: BA §8.1–§8.8, §7.7, §9, §11.7 (AC-10); SRS §2; `docs/conventions.md` §2 "AI".

**3. Detailed Tasks**

Task quản lý tại file này (dùng chung hoặc ngoài 14 tính năng):

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P12-T01 | Ánh xạ BA §8 vào F01–F14 | Bảng: thành phần §8 → tính năng/endpoint → phần chưa có chỗ trong tài liệu | BA §8; `api-endpoints.md` | CPC | CXĐ | CPC | — | Bảng ánh xạ | NOT_STARTED | — | — |
| P12-T08 | Đánh giá chất lượng AI/ML | Tiêu chí và cách đo cho AC-10 | BA §8.7, §11.7 | CPC | CXĐ | CPC | P12-T03, P12-T05 | Báo cáo đánh giá | NOT_STARTED | — | Một phần: đo thật cần P12-T03, P12-T05. Soạn tiêu chí theo AC-10, BA §8.7 làm được |
| P12-T09 | Dữ liệu cho hệ thống đề xuất | BA §6.8 (FR-36–39), AC-09 | BA §6.8 | CPC | CXĐ | CPC | P11-T05 | Ghi chú | BLOCKED | — | Chưa có bảng dữ liệu lịch sử |

Chỉ mục Task đã chuyển:

| Task ID | Task Name | Feature | Quản lý tại |
|---|---|---|---|
| P12-T02 | Đề xuất phương án AI Consultant | F05 | [F05-ai-consultant-learning-roadmap/phase-12-ai-ml.md](F05-ai-consultant-learning-roadmap/phase-12-ai-ml.md) |
| P12-T03 | Kiểm tra đầu ra AI | F05 | [F05-ai-consultant-learning-roadmap/phase-12-ai-ml.md](F05-ai-consultant-learning-roadmap/phase-12-ai-ml.md) |
| P12-T04 | Skill Graph | F05 | [F05-ai-consultant-learning-roadmap/phase-12-ai-ml.md](F05-ai-consultant-learning-roadmap/phase-12-ai-ml.md) |
| P12-T05 | Xếp hạng gợi ý khóa học | F07 | [F07-skill-course-recommendation/phase-12-ai-ml.md](F07-skill-course-recommendation/phase-12-ai-ml.md) |
| P12-T06 | Hành vi AI Tutor | F08 | [F08-ai-tutor-chat/phase-12-ai-ml.md](F08-ai-tutor-chat/phase-12-ai-ml.md) |
| P12-T07 | Skill Review bằng RAG | F09 | [F09-review-assessment/phase-12-ai-ml.md](F09-review-assessment/phase-12-ai-ml.md) |

**4. Deliverables** — Bảng ánh xạ; đề xuất kỹ thuật cho nhóm; kiểm tra đầu ra AI; báo cáo đánh giá.
**5. Review Checklist** — Không tự đưa công nghệ chưa duyệt vào code; đầu ra AI được kiểm tra trước khi lưu (BR-07); dữ liệu gửi dịch vụ AI tối thiểu (NFR-31).
**6. Blockers & Open Issues** — BA §8 chưa ánh xạ đầy đủ; ND-58 (RAG), ND-59, ND-60, ND-61; công nghệ AI chưa có D-xx.
**7. Completion Criteria** — T01 DONE; các Task khác theo quyết định.

### P13 – Integration, Testing & Documentation

**1. Phase Information** — Phase ID: P13 · Objective: tích hợp, kiểm thử, sửa lỗi, tài liệu, chuẩn bị demo · Related Features: tất cả · Responsible: CPC · Support: CXĐ · Reviewer: CPC · Dependencies: các Task triển khai tương ứng · Initial Status: NOT_STARTED

**2. Scope** — Trong: tích hợp backend/frontend, kiểm thử chức năng, API, giao diện, responsive, sửa lỗi, kiểm thử hồi quy, tài liệu, demo. Ngoài: nghiệm thu thương mại, release sign-off, giám sát vận hành, SLA. Nguồn: BA §11 (AC-01…AC-11), §7.5 (NFR-17, NFR-18); `docs/conventions.md` §5, §6; `docs/modules/*.tests.md`; ND-67, ND-68; D-DOC-04, D-DOC-05.

**3. Detailed Tasks**

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P13-T01 | Môi trường tích hợp | Backend + DB + frontend chạy cùng nhau trên máy | `SETUP.md` | CPC | CXĐ | CPC | P01-T09, P01-T10 | Hướng dẫn chạy được | BLOCKED | — | G6; cổng/tên DB |
| P13-T02 | Tích hợp theo tính năng | Thay mock bằng API thật cho từng tính năng đã REVIEW | D-FE-07, D-FE-10 | CPC | CXĐ | CPC | P13-T01, P04-T05, P04-T06, P04-T08, P04-T09, P04-T12, P05-T04…T08, P06-T05…T07, P07-T05…T09, P08-T05, P09-T04…T09 | Danh sách tính năng đã tích hợp | BLOCKED | — | Theo P13-T01 |
| P13-T03 | Kiểm thử API | Chạy `pytest` toàn bộ theo các `*.tests.md` | `conventions.md` §6 | CPC | CXĐ | CPC | P04-T14, P05-T09, P06-T08, P07-T10, P08-T06, P09-T10 | Kết quả `pytest` | BLOCKED | — | Theo P01-T08 và các task test backend trong cột Dependencies |
| P13-T04 | Kiểm thử chức năng theo AC | Đối chiếu AC-01…AC-11 với tính năng đã có | BA §11 | CPC | CXĐ | CPC | P13-T02 | Bảng kết quả theo AC | NOT_STARTED | — | Một phần: chạy kiểm thử cần P13-T02. Lập bảng ánh xạ AC-01…AC-11 sang tính năng làm được |
| P13-T05 | Kiểm thử giao diện | Theo quy định đã chốt | ND-67 | CPC | CXĐ | CPC | P13-T02 | Kết quả test | BLOCKED | — | ND-67 |
| P13-T06 | Kiểm thử responsive | Theo quy định đã chốt; NFR-17, NFR-18 | ND-68; BA §7.5 | CPC | CXĐ | CPC | P13-T02 | Kết quả test | BLOCKED | — | ND-68 |
| P13-T07 | Báo cáo lỗi và sửa lỗi | Ghi lỗi (bước tái hiện, kết quả mong đợi theo nguồn), giao người phụ trách tính năng | `conventions.md` §5 | CPC | CXĐ | CPC | P13-T03…T06 | Danh sách lỗi và trạng thái | NOT_STARTED | — | Một phần: lỗi phát hiện từ P13-T03…T06; lỗi từ kiểm thử thủ công ghi được bất kỳ lúc nào |
| P13-T08 | Kiểm thử hồi quy | Chạy lại test sau khi sửa lỗi | `conventions.md` §6 | CPC | CXĐ | CPC | P13-T07 | Kết quả chạy lại | NOT_STARTED | — | — |
| P13-T09 | Cập nhật tài liệu | `structure.md` §1.1 (hiện trạng), `SETUP.md`, README; workbook ở mức tính năng (D-DOC-04) | D-DOC-04, D-DOC-05 | CPC | CXĐ | CPC | — | Tài liệu cập nhật | NOT_STARTED | — | — |
| P13-T10 | Chuẩn bị demo | Kịch bản demo, dữ liệu demo (không dùng tài khoản demo trên giao diện production — D-FE-07) | D-FE-07 | CPC | CXĐ | CPC | P13-T02 | Kịch bản demo | NOT_STARTED | — | Một phần: chạy demo cần P13-T02. Soạn kịch bản demo làm được |

**4. Deliverables** — Hệ thống chạy tích hợp; kết quả test; danh sách lỗi; tài liệu cập nhật; kịch bản demo.
**5. Review Checklist** — Kết quả test có bằng chứng; mỗi AC có kết quả hoặc lý do chưa kiểm; tài liệu khớp code.
**6. Blockers & Open Issues** — ND-67, ND-68; G6; cổng/tên DB.
**7. Completion Criteria** — T01–T10 DONE hoặc BLOCKED có lý do; không có lỗi mức chặn demo còn mở.

---

## PART 6 — CROSS-PHASE TRACKING

Chỉ dùng ND và quyết định đã có trong `docs/decisions.md`. ND PENDING **không** phải quyết định đã duyệt. Vấn đề chưa có ND được ghi riêng, **không** trình bày như ND.

Loại vấn đề: (1) ND đang PENDING · (2) D đã chốt nhưng còn ND cần làm rõ · (3) Mục T chưa được duyệt · (4) Vấn đề chưa có ND · (5) Thiếu tài liệu · (6) Mâu thuẫn giữa các nguồn.

| Issue | Loại vấn đề | Related Phase | Source | Impact | Required Action | Status |
|---|---|---|---|---|---|---|
| Tổ chức router, Docker Compose | (4) | P01, P13 | `structure.md` §1.3; workbook G6 (G6 không phải ND trong `decisions.md`) | Chặn gắn router, Compose, môi trường tích hợp | Nhóm quyết định (P00-T01) | Chưa có ND — đang chờ |
| Cổng và tên database | (4) | P01, P13 | `structure.md` §1.3; workbook DB-CONN | Chặn cấu hình DB, Compose | Nhóm quyết định (P00-T02) | Chưa có ND — đang chờ |
| Sync/async, lớp commit | (1) | P01, P04–P09 | ND-16 (`decisions.md` §4.3) | Chặn `database.py`, Alembic | P00-T03 | PENDING |
| Thư viện JWT, Argon2id | (2) | P01, P04 | D-AUTH-01, D-AUTH-04 đã chốt; ND-44, ND-45 (§4.1) | Chặn `security.py` | P00-T04 | ND-44, ND-45 PENDING |
| Mã lỗi, 400/422 | (1) | P01, P04–P11 | ND-14, ND-15 (§4.3) | Một phần handler và test | P00-T05 | PENDING |
| Refresh token, logout | (2) | P03, P04 | D-AUTH-03 đã chốt; ND-40…43, ND-48 (§4.1) | Chặn refresh/logout; client không làm refresh | Tuấn và nhóm quyết định | ND-40…43, ND-48 PENDING |
| Kiểm thử frontend | (1) | P04–P13 | ND-67 (§6) | Chặn kiểm thử giao diện | P00-T08 | PENDING |
| Kiểm thử responsive | (1) | P03–P13 | ND-68 (§6); BA NFR-18 | Chặn kiểm thử responsive | P00-T08 | PENDING |
| Điều kiện ôn tập, câu trống, nộp lần hai | (3) | P09 | T16 (`decisions.md` §3) | Một phần API ôn tập | Nhóm tick T16 | Chưa duyệt (☐) |
| Endpoint còn thiếu M1–M4 | (1) | P09, P10, P11 | ND-55 (§6) | Giao diện "chưa khả dụng" | Nhóm định nghĩa endpoint | PENDING |
| Feedback, `feedback_type` | (2) | P10 | D11 đã chốt ("không làm" danh sách loại); ND-35, ND-69 (§4.4) | Chặn backend phản hồi | Nhóm quyết định | ND-35, ND-69 PENDING |
| Người phụ trách Feedback | (6) | P10 | Đã xử lý: D-OWN-02 (`decisions.md` §2) ghi F10 Khôi, F13 Hòa; `README.md`, `docs/modules/README.md` đã đồng bộ (commit `2133863`). Còn mở: dòng "Feedback & liên hệ (T22–T25)" ở §2 vẫn ghi "Chưa rõ: Khôi/Tâm" (ND-35); quan hệ của dòng này với D-OWN-02 chưa được xác nhận. Nhãn "C3" không phải ND | P10 đã có người phụ trách theo tính năng; dòng Feedback & liên hệ ở §2 chưa thống nhất với D-OWN-02 | P00-T07 | Chưa có ND — đang chờ Tuấn xác nhận |
| Dữ liệu demo chưa có trong API | (1) | P07–P09, P11 | ND-54 (§6) | Ẩn các trường tương ứng | Nhóm quyết định | PENDING |
| Câu chữ demo khẳng định quy tắc chưa chốt | (1) | P03, P04, P09 | ND-51 (§6) | Ẩn câu chữ tương ứng | Nhóm quyết định | PENDING |
| SRS/BA khác D01, D04, RV-R01 | (1) | P09 | ND-58 (§4.2); D01, D04, RV-R01 giữ nguyên | Không làm theo SRS FR-07, BA §10.10 | Nhóm quyết định | PENDING |
| Skill Review bằng RAG | (4) | P09, P12 | BA §8.6 — chưa ND nào nhắc RAG | P12-T07 không làm | Người có thẩm quyền xem xét (P00-T09) | Chưa có ND — đang chờ |
| Cấu trúc file cũ, route demo, chuyển hướng quyền | (1) | P03 | ND-49, ND-50, ND-52 (§6) | Một phần route, file | Nhóm quyết định | PENDING |
| Người phụ trách phần nền, AI/ML, tích hợp; reviewer | (4) | P00–P03, P11, P12, P13 | `README.md` không ghi; workbook CK-42 | Nhiều task Chưa phân công | P00-T06 | Chưa có ND — đang chờ |
| Đặc tả module của 12 tính năng mới ở DRAFT | (5) | P05–P08, P10, P11 | `docs/modules/README.md` (DRAFT từ 2026-11-03, chưa được người phụ trách xác nhận); tài liệu còn thiếu từng tính năng: `plans/Fxx-*/ba-decisions-and-safe-defaults.md` mục C | Task rà soát và đặc tả đầu mỗi Phase | Người phụ trách tính năng | Thiếu tài liệu |
| Database dùng cho test | (4) | P01 | Không tài liệu nào quy định | Chặn P01-T08 | Nhóm quyết định | Chưa có ND — đang chờ |
| Quyền truy cập `GET /api/courses*` | (4) | P05 | `api-endpoints.md` §3 chưa ghi; `structure.md` §3 | Một phần P05-T04, P05-T05 | Nhóm quyết định | Chưa có ND — đang chờ |
| Nội dung email kết quả ôn tập | (6) | P09 | Ghi chú T29 so với `.docx` 6.2 và RV-R18 | Một phần P09-T08 | Nhóm quyết định | Chưa có ND — đang chờ |
| Dataset không có trong repo | (4) | P02 | `database-design.md` §1 "Nguồn dữ liệu" | Một phần P02-T06 | P02-T05 | Chưa có ND — đang chờ |
| Nguồn ngân hàng câu hỏi ôn tập | (4) | P09 | D04, RV-R02 (cần ≥ 20 câu) — nguồn chưa có | P09-T03 | Nhóm quyết định | Chưa có ND — đang chờ |
| Bảng dữ liệu lộ trình lịch sử | (4) | P11, P12 | `api-endpoints.md` §13; `database-design.md` không có bảng | Chặn P11-T05, P12-T09 | Nhóm quyết định | Chưa có ND — đang chờ |
| Thời điểm lưu lộ trình (F05) | (6) | P07 | BA UC-04 bước 7 và Postconditions ghi lưu khi tạo thành công; `api-endpoints.md` §5, `database-design.md` §4.4 và LP-R01 (`docs/modules/learning-path-consultant.md`) ghi chỉ lưu khi người dùng xác nhận. Chưa có ND (ND-74 không bao gồm điểm này). Chi tiết: [F05](F05-ai-consultant-learning-roadmap/plan.md) mục 4, mục 7 | Một phần P07-T05, P07-T06 (`SOURCE_CONFLICT` — không tự chọn nguồn) | Đề xuất (chưa có mã ND): chủ dự án xem xét lập ND mới | Chưa có ND — đang chờ |

---

## PART 7 — PROGRESS SUMMARY

> Cập nhật thủ công khi trạng thái Task thay đổi. Từ 2026-11-03, đếm trên file này **và** các file `plans/Fxx-*/phase-NN-*.md`. Số liệu dưới đây là trạng thái **ban đầu** (chuẩn hóa sau audit ngày 2026-10-30), chưa phải tiến độ thực tế.

| Chỉ số | Giá trị ban đầu |
|---|---|
| Tổng số Phase | 14 |
| Tổng số Task | 154 |
| Phase theo trạng thái | NOT_STARTED 13 · IN_PROGRESS 1 (P03) · BLOCKED 0 · REVIEW 0 · REWORK 0 · DONE 0 |
| Task theo trạng thái | NOT_STARTED 126 · IN_PROGRESS 0 · BLOCKED 27 · REVIEW 1 · REWORK 0 · DONE 0 |
| Task đang REVIEW/REWORK | P03-T01 (REVIEW — chờ phân công reviewer) |
| Task BLOCKED (27) | P01-T03, P01-T05, P01-T08, P01-T09, P01-T10, P03-T08, P04-T02, P04-T03, P04-T06, P04-T07, P04-T10, P04-T11, P04-T13, P04-T22, P07-T05, P10-T06, P11-T03, P11-T05, P11-T06, P11-T07, P12-T07, P12-T09, P13-T01, P13-T02, P13-T03, P13-T05, P13-T06 |
| Phase chưa đủ điều kiện DONE | Tất cả 14 Phase |

| Phase | Số Task | NOT_STARTED | BLOCKED | REVIEW |
|---|---|---|---|---|
| P00 | 10 | 10 | 0 | 0 |
| P01 | 10 | 5 | 5 | 0 |
| P02 | 7 | 7 | 0 | 0 |
| P03 | 9 | 7 | 1 | 1 |
| P04 | 22 | 14 | 8 | 0 |
| P05 | 14 | 14 | 0 | 0 |
| P06 | 11 | 11 | 0 | 0 |
| P07 | 16 | 15 | 1 | 0 |
| P08 | 8 | 8 | 0 | 0 |
| P09 | 15 | 15 | 0 | 0 |
| P10 | 6 | 5 | 1 | 0 |
| P11 | 7 | 3 | 4 | 0 |
| P12 | 9 | 7 | 2 | 0 |
| P13 | 10 | 5 | 5 | 0 |

---

## PART 8 — CHANGE LOG

| Date | Change | Reason | Updated By |
|---|---|---|---|
| 2026-10-30 | Tạo kế hoạch: 14 Phase, Task ban đầu, trạng thái theo hiện trạng repo | D-DOC-05 | Claude Code (theo yêu cầu của Tuấn) |
| 2026-10-30 | Chuẩn hóa sau audit: BLOCKED chỉ còn task có phần cốt lõi bị chặn; sửa lý do chặn sai loại, dependency mơ hồ, phân công P00-T04 và P06; PART 6 thêm cột "Loại vấn đề"; ghi kết quả build cho P03-T01; tính lại PART 7 | Audit `plans/plan.md` | Claude Code (theo yêu cầu của Tuấn) |
| 2026-11-03 | Chuyển Task của 14 tính năng sang `plans/Fxx-*/phase-NN-*.md`, giữ nguyên Task ID, Status, Dependencies, Evidence, Blocker; Responsible của 14 Task đổi theo bảng phân công 2026-11-03 (giá trị cũ ghi trong ngoặc); thêm chỉ mục thư mục tính năng; sửa 2 dòng PART 6 | Tuấn yêu cầu tổ chức kế hoạch theo 14 tính năng; D-DOC-05 (8) | Claude Code (theo yêu cầu của Tuấn) |
| 2026-11-03 | Phase 10: bỏ "(APPROVED)" ở tiêu đề mục B của 14 file `ba-decisions-and-safe-defaults.md`; ghi người phụ trách F07, F10–F13 theo D-OWN-02, tên workbook V2 chỉ giữ để truy vết; P05, P07, P10 ghi người phụ trách theo từng tính năng; cập nhật P00-T07 và PART 6 (phần còn mở: dòng Feedback ở `docs/decisions.md` §2, ND-35 — chưa giải quyết); đổi 15 ô mức sẵn sàng sang PENDING/CONFLICT/NEEDS_OWNER_INPUT (14 ô PENDING/CONFLICT sau đó được khôi phục ở Phase 13) | Audit Phase 9 (E1–E5) | Claude Code (theo yêu cầu của Tuấn) |
| 2026-11-03 | Phase 13: áp dụng D-DOC-07 (ghi ở `docs/decisions.md`; skill governance cập nhật) — nhãn mức sẵn sàng chỉ dùng 5 giá trị; `BLOCKED` trong cột mức sẵn sàng đổi thành `NOT_READY_BLOCKED` (24 ô); khôi phục 14 ô PENDING/CONFLICT về `READY_WITH_LIMITATIONS`; 8 ô tiêu chí nghiệm thu chuyển `NEEDS_OWNER_INPUT` kèm câu hỏi; F05, F08, F14 Database chuyển `READY_WITH_LIMITATIONS` (ND-54); viết lại dòng "Ký hiệu"; nguồn người phụ trách chuẩn hóa về D-OWN-01, D-OWN-02 (Phase P04, P06, P08, P09, P11; cột Responsible "D-OWN-02; trước: X"). Chưa hoàn tất: các câu hỏi `NEEDS_OWNER_INPUT` chờ người phụ trách trả lời; `SOURCE_CONFLICT` F05 (BA UC-04 so với API) chờ đề xuất ND | D-DOC-07; báo cáo Phase 12 | Claude Code (theo yêu cầu của Tuấn) |
| 2026-11-03 | Phase 14: bổ sung người trả lời (D-OWN-02) và câu hỏi cụ thể cho 28 ô `NEEDS_OWNER_INPUT` có từ trước và ô F01 "Quên, đặt lại mật khẩu" (frontend); F01 "Profile — ảnh đại diện" (frontend) đổi `NEEDS_OWNER_INPUT` → `NOT_READY_BLOCKED` (ND-62, ND-12); rà soát 24 ô `NOT_READY_BLOCKED` theo D-DOC-07 — F05 API đổi sang `READY_WITH_LIMITATIONS` (CRUD lộ trình làm được; `POST /api/chat/learning-path` chặn bởi ND-74, P12-T02), các ô còn lại giữ; ghi giải thích cho ô không áp dụng F01 "Tạo admin" (frontend); ghi Phase 10, Phase 13 vào change log. Chưa hoàn tất: các câu hỏi `NEEDS_OWNER_INPUT` chờ người phụ trách trả lời | D-DOC-07; báo cáo Phase 13 | Claude Code (theo yêu cầu của Tuấn) |
| 2026-11-03 | Phase 15: F01 "Làm mới phiên" (frontend) giữ `NOT_READY_BLOCKED`, ghi chú dẫn ND-41, ND-48 theo D-FE-05; F14 và F10 "Yêu cầu nghiệp vụ" đổi `NEEDS_OWNER_INPUT` → `NOT_READY_BLOCKED` (F14: ND-79; F10: T22–T25 ☐, ND-35 — giữ câu hỏi riêng cho Khôi); F05 giữ `SOURCE_CONFLICT`, ghi rõ vị trí nguồn; kiểm tra lại phân bổ ô `NEEDS_OWNER_INPUT` (API 8, kiểm thử 12, tiêu chí nghiệm thu 5, yêu cầu nghiệp vụ 3). Không đổi trạng thái D/ND/T và Task. Chưa hoàn tất: `SOURCE_CONFLICT` F05 chờ chủ dự án xem xét đề xuất ND mới | Báo cáo Phase 14 | Claude Code (theo yêu cầu của Tuấn) |
