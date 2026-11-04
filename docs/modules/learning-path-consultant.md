# Module: AI Consultant và lộ trình học tập (F05)

Đặc tả nghiệp vụ của tính năng. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §5, schema ở `docs/database-design.md` §4, §5, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `LP-YCnn`, mã quy tắc `LP-Rnn`.

> **DRAFT** — dẫn xuất từ BA (bản Git HEAD) theo D-DOC-01, chưa được người phụ trách xác nhận. Chỗ BA khác tài liệu khác được ghi rõ.

---

## 1. Phạm vi

**Người phụ trách:** Hòa (workbook V2). Riêng việc cập nhật trạng thái lộ trình sau khi ôn tập đạt (T18) được `docs/decisions.md` §2 ghi Tâm: **Chờ nhóm chốt**. · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Người dùng nhập mục tiêu nghề nghiệp hoặc học tập bằng ngôn ngữ tự nhiên cho AI Consultant. Hệ thống phân tích mục tiêu, xác định kỹ năng, đối chiếu danh mục và tạo lộ trình **đề xuất** dạng đồ thị kỹ năng. Người dùng xác nhận thì lộ trình được lưu; sau đó xem danh sách, xem chi tiết, đổi thông tin hoặc trạng thái, từ bỏ lộ trình. Giải pháp AI: BA §8.2.

**Thuộc module:** `POST /api/chat/learning-path`, `GET /api/me/learning-paths`, `GET /api/learning-paths/{path_id}`, `POST /api/learning-paths`, `PATCH /api/learning-paths/{path_id}`, `DELETE /api/learning-paths/{path_id}`.

**Không thuộc module:** sửa node và cạnh (F06, `learning-path-graph.md`); gợi ý khóa học cho node (F07); mẫu lộ trình (`admin-base-paths.md`); dữ liệu lịch sử (`admin-historical-data.md`); AI Tutor (F08).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| LP-YC01 | AI Consultant nhận mục tiêu bằng ngôn ngữ tự nhiên | FR-05; UC-03 | — |
| LP-YC02 | Phân tích mục tiêu, xác định kỹ năng; đối chiếu danh mục kỹ năng trước khi dùng | FR-06; BR-01; BR-02; §8.2.4 | — |
| LP-YC03 | Hỏi lại khi mục tiêu chưa rõ; báo giới hạn khi ngoài phạm vi | FR-07; BR-04; UC-03 | ND-74 (response và cách xử lý) |
| LP-YC04 | Tạo lộ trình theo mục tiêu, kỹ năng liên quan, danh mục và quan hệ kỹ năng, dữ liệu lộ trình cũ, kỹ năng hiện có của người dùng khi phù hợp | FR-08; UC-04 | — |
| LP-YC05 | Lộ trình phù hợp mục tiêu; dùng quan hệ kỹ năng; không coi mọi quan hệ là tiên quyết; cấu trúc phải hợp lệ | BR-05 … BR-08 (§9.2) | — |
| LP-YC06 | Có thể dùng dữ liệu lộ trình cũ để hỗ trợ, nhưng không thay cấu trúc kỹ năng | BR-09; UC-04 bước 5 | — |
| LP-YC07 | Kiểm tra kết quả AI trước khi lưu hoặc dùng | FR-38; BR-03 | — |
| LP-YC08 | Lưu lộ trình và liên kết với tài khoản | FR-09; FR-36; BR-17 | **BA khác:** UC-04 bước 7 ghi hệ thống lưu sau khi tạo; `api-endpoints.md` §5 và `database-design.md` §4.4 chỉ lưu khi người dùng xác nhận (LP-R01). Chưa có ND |
| LP-YC09 | Xem danh sách lộ trình và chi tiết một lộ trình | FR-10; UC-05 | — |
| LP-YC10 | Từ bỏ lộ trình bằng cách chuyển trạng thái, không xóa lịch sử | §10.5 | — |
| LP-YC11 | Lộ trình 3–5 môn học kèm giải thích | Không có trong BA; chỉ có ở đề bài SRS v1.0 FR-03 | ND-60, ND-81: giữ đồ thị kỹ năng |

### Màn hình UI

| Màn | Route | Endpoint của module dùng |
|---|---|---|
| Consultant | `/consultant` | `POST /api/chat/learning-path`; `POST /api/learning-paths` chỉ khi bấm lưu |
| MyPaths | `/me/learning-paths` | `GET /api/me/learning-paths` |
| PathDetail | `/learning-paths/:pathId` | `GET`, `PATCH`, `DELETE /api/learning-paths/{path_id}` (màn chính của F06) |

UI demo luôn trả một bản nháp cố định và hiển thị tên lộ trình mà CSDL chưa có (ND-74, ND-54).

---

## 2. File liên quan

Theo `docs/structure.md` §2, §5:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/chat_consultant.py`, `backend/app/routers/learning_paths.py` |
| Service | `consultant_service`, `learning_path_service`, `base_path_service` |
| AI và gợi ý | `ai/client`, `ai/validators`, `recommender/skill_graph`, `recommender/collaborative_filtering` |
| Frontend | `api/consultant.api.js`, `api/learningPaths.api.js`; `path/ConsultantPage`, `path/MyPathsPage` |

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §4, §5.

| Bảng | Đọc / ghi | Dùng cho |
|---|---|---|
| `LearningPath` | Ghi | `goal_text`, `status`, `template_id` |
| `LearningPathNode`, `LearningPathEdge` | Ghi khi lưu | Đồ thị của lộ trình (quy tắc ở F06) |
| `Skill`, `SkillRelation` | Đọc | Đối chiếu danh mục, mở rộng tiên quyết |
| `BaseLearningPath*` | Đọc | Mẫu làm điểm xuất phát |
| `UserSkill` | Đọc | Kỹ năng hiện có (FR-08) |
| `ChatSession`, `ChatMessage` | Ghi? | `session_type = learning_path` có trong CSDL; có lưu hội thoại tư vấn không: chưa ghi, `[NEEDS DECISION]` |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §5. Request, response và mã lỗi **chưa được định nghĩa**; riêng `POST /api/chat/learning-path`: ND-74.

| Mã | Method | Endpoint | Mô tả | Quyền |
|---|---|---|---|---|
| EP-028 | POST | `/api/chat/learning-path` | Gửi mục tiêu, nhận lộ trình đề xuất (chưa lưu) | Chưa ghi |
| EP-029 | GET | `/api/me/learning-paths` | Lộ trình của người dùng | Người dùng |
| EP-030 | GET | `/api/learning-paths/{path_id}` | Chi tiết, gồm trạng thái và node | Chưa ghi |
| EP-031 | POST | `/api/learning-paths` | Lưu hoặc chấp nhận lộ trình đề xuất | Chưa ghi |
| EP-032 | PATCH | `/api/learning-paths/{path_id}` | Cập nhật thông tin hoặc trạng thái | Chưa ghi |
| EP-033 | DELETE | `/api/learning-paths/{path_id}` | Chuyển `abandoned` | Chưa ghi |

Workbook đề xuất `owner-only` cho các endpoint "Chưa ghi"; chưa được duyệt.

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| LP-R01 | Bản đề xuất từ `POST /api/chat/learning-path` chưa được lưu; chỉ lưu khi người dùng xác nhận qua `POST /api/learning-paths`. | `api-endpoints.md` §5; `database-design.md` §4.4; `structure.md` §3, §5 |
| LP-R02 | Trạng thái lộ trình: `ongoing`, `completed`, `abandoned`; `completed` = mọi nút bắt buộc đã hoàn thành hoặc được công nhận đã biết. | `api-endpoints.md` §5; `database-design.md` §4.4 |
| LP-R03 | `DELETE` chỉ chuyển `abandoned`. | `api-endpoints.md` §1, §5; `database-design.md` §4.4 |
| LP-R04 | Thay đổi nhỏ thì cập nhật lộ trình hiện tại; đổi sang mục tiêu khác đáng kể thì tạo lộ trình mới và giữ lộ trình cũ. | `api-endpoints.md` §5 |
| LP-R05 | Kỹ năng do AI trả về phải có trong danh mục trước khi tạo lộ trình. | `api-endpoints.md` §14; BA BR-02 |
| LP-R06 | Thứ tự xử lý: diễn giải mục tiêu → xác thực kỹ năng → tìm mẫu phù hợp → mở rộng tiên quyết bằng đồ thị kỹ năng chung → tham khảo lộ trình lịch sử → trả lộ trình đề xuất. | `structure.md` §5; `api-endpoints.md` §12 |
| LP-R07 | Mẫu lộ trình chỉ là điểm xuất phát; người cùng mục tiêu không bắt buộc nhận lộ trình giống hệt. | `api-endpoints.md` §12 |
| LP-R08 | Lộ trình được tạo thành công không có nghĩa người học đã hoàn thành hay đạt mục tiêu. | BA BR-18 |

---

## 6. Luồng nghiệp vụ

```text
POST /chat/learning-path {mục tiêu}
  → ai/client diễn giải → ai/validators đối chiếu Skill
  → base_path_service tìm mẫu → skill_graph mở rộng tiên quyết → collaborative_filtering tham khảo lịch sử
  → trả lộ trình ĐỀ XUẤT (chưa lưu)     [mục tiêu chưa rõ, ngoài phạm vi: ND-74]
Người dùng bấm lưu → POST /learning-paths → lưu LearningPath + Node + Edge
```

## 7. Transaction

Lưu lộ trình ghi `LearningPath`, `LearningPathNode`, `LearningPathEdge`: cùng một transaction theo `api-endpoints.md` §14.

## 8. Bảo mật

Lộ trình là dữ liệu cá nhân (BA §4.3, FR-41). Chỉ gửi dữ liệu cần thiết tới dịch vụ AI (BA NFR-31).

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F06 Node và cạnh | Đồ thị của lộ trình; quy tắc node, cạnh |
| F07 Gợi ý khóa học | Chọn node trên lộ trình đã lưu |
| F12 Quan hệ kỹ năng | `SkillRelation` để mở rộng tiên quyết |
| Mẫu lộ trình, Dữ liệu lịch sử | Điểm xuất phát và dữ liệu tham khảo |
| F09 Ôn tập | Cập nhật lộ trình sau khi đạt (T18 ☐, ND-24) |
| F01 Hồ sơ | `GET /api/me/summary` đếm `LearningPath` (ND-13) |

---

## 10. Câu hỏi mở

`ND-74` (hợp đồng tư vấn), `ND-54` (tên lộ trình), `ND-60`, `ND-77`, `ND-81` (đề bài), `ND-24` (cập nhật sau ôn tập) — `docs/decisions.md` §4.

Chưa có ND: thời điểm lưu lộ trình (LP-YC08); có lưu hội thoại tư vấn không; người làm T18; quyền của EP-028, EP-030 … EP-033.
