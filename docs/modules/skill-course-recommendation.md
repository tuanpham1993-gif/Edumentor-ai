# Module: Gợi ý khóa học theo kỹ năng (F07)

Đặc tả nghiệp vụ của tính năng. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §8, schema ở `docs/database-design.md` §2, §4.5, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `RC-YCnn`, mã quy tắc `RC-Rnn`.

> **DRAFT** — dẫn xuất từ BA (bản Git HEAD) theo D-DOC-01, chưa được người phụ trách xác nhận.

---

## 1. Phạm vi

**Người phụ trách:** Tâm (D-OWN-02; workbook V2 ghi Hòa — workbook không phải nguồn quyết định) · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Khi người dùng chọn một node kỹ năng trên lộ trình, hệ thống hiển thị thông tin kỹ năng, truy xuất các khóa học liên quan, xếp hạng theo độ phù hợp và trả liên kết tới trang khóa học ngoài. Giải pháp gợi ý: BA §8.4.

**Thuộc module:** `GET /api/learning-paths/{path_id}/nodes/{skill_id}/courses` (kèm `?sort_by=`).

**Không thuộc module:** danh mục khóa học chung (F02); node, cạnh (F06). Workbook ghi endpoint này dùng chung cho "đề xuất khóa học liên quan đến node" của F04 (CT-YC06): **Chờ nhóm chốt**.

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| RC-YC01 | Chọn kỹ năng trong lộ trình thì hiển thị tên kỹ năng và các quan hệ liên quan đã lưu | FR-12; UC-06 bước 3 | — |
| RC-YC02 | Truy xuất khóa học liên quan đến kỹ năng đã chọn từ CSDL khóa học | FR-13; BR-12 | — |
| RC-YC03 | Xếp hạng theo mức phù hợp với kỹ năng đang chọn và mục tiêu; không chỉ theo độ phổ biến | FR-14; BR-13; BR-14 | — |
| RC-YC04 | Điểm khởi đầu `Score = 0.7 × skill_match + 0.3 × level_fit`; thiếu dữ liệu `level_fit` thì xếp theo `skill_match`; trọng số là giá trị khởi đầu, sẽ đánh giá lại | §8.4.3 | Trọng số không hard-code (`CLAUDE.md`); nơi cấu hình chưa ghi |
| RC-YC05 | Không dùng điểm đánh giá kỹ năng để xếp hạng khóa học | BR-15 | — |
| RC-YC06 | Không có khóa phù hợp thì thông báo; không tạo khóa học hay liên kết không có trong dữ liệu | BR-16; UC-06 luồng phụ | — |
| RC-YC07 | Sắp xếp theo điểm đánh giá hoặc số lượt đánh giá; cung cấp liên kết tới trang khóa ngoài | §10.8; UC-06 bước 7 | — |

### Màn hình UI

| Màn | Route | Endpoint của module dùng |
|---|---|---|
| PathDetail | `/learning-paths/:pathId` | `GET .../nodes/{skill_id}/courses` ở panel bên phải, chỉ khi chọn một node |

---

## 2. File liên quan

Theo `docs/structure.md` §2, §5:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/node_course_suggestions.py` |
| Service | `recommendation_service` |
| Gợi ý | `recommender/course_ranking` |
| Frontend | `api/learningPaths.api.js`; `path/PathDetailPage` |

---

## 3. Dữ liệu

Module chỉ đọc. Chi tiết cột: `docs/database-design.md` §2, §4.5.

| Bảng | Dùng cho |
|---|---|
| `LearningPathNode` | Kiểm tra kỹ năng thuộc lộ trình |
| `CourseSkillRelation`, `Course` | Khóa học liên quan đến kỹ năng; `rating`, `num_reviews`, `url`, `level` |
| `SkillRelation`, `Skill` | Quan hệ của kỹ năng (FR-12) |
| `StudentCourse` | Khóa đã hoàn thành (`previously_learned`, BA §8.4.3) |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §8. Request, response và mã lỗi **chưa được định nghĩa**: `[NEEDS DECISION]`.

| Mã | Method | Endpoint | Mô tả | Quyền |
|---|---|---|---|---|
| EP-043 | GET | `/api/learning-paths/{path_id}/nodes/{skill_id}/courses` | Khóa học gợi ý cho kỹ năng; `?sort_by=rating\|num_reviews` | Chưa ghi (workbook đề xuất `owner-only`) |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| RC-R01 | Chỉ truy xuất gợi ý khi người dùng chọn một node; không gợi ý cho mọi node khi tạo lộ trình. | `api-endpoints.md` §8; `structure.md` §3 |
| RC-R02 | Xác minh kỹ năng được chọn thuộc lộ trình tương ứng. | `api-endpoints.md` §8 bước 1 |
| RC-R03 | Độ liên quan đến kỹ năng là yếu tố hàng đầu; điểm đánh giá cao không phải bằng chứng duy nhất. | `api-endpoints.md` §8; `structure.md` §5 |
| RC-R04 | Không đưa điểm ôn tập vào xếp hạng khóa học. | `api-endpoints.md` §14; RV-R21 |
| RC-R05 | Trả thông tin khóa học cùng URL ngoài. | `api-endpoints.md` §8 bước 4 |

---

## 6. Luồng nghiệp vụ

```text
GET .../nodes/{skill_id}/courses
  → kỹ năng thuộc lộ trình? (RC-R02)
  → lấy khóa qua CourseSkillRelation
  → xếp hạng (RC-YC04, RC-R03, RC-R04) → sắp xếp theo sort_by nếu có
  → không có khóa: báo "không có", không tạo dữ liệu (RC-YC06)
```

## 7. Transaction

Không có thao tác ghi.

## 8. Bảo mật

Lộ trình thuộc người dùng hiện tại (BA §4.3, FR-41).

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F05, F06 Lộ trình | Lộ trình và node được chọn |
| F02, F11 Khóa học | Dữ liệu `Course`, `CourseSkillRelation` |
| F04 Theo dõi | `join` khi người dùng mở khóa được gợi ý; CT-YC06 |
| F09 Ôn tập | Không dùng điểm ôn tập (RV-R21) |

---

## 10. Câu hỏi mở

Không có ND riêng trong `docs/decisions.md`.

Chưa có ND: phạm vi dùng chung với F04; nơi cấu hình trọng số RC-YC04; cách tính `level_fit`, `skill_match` (BA §8.4.2 chỉ nêu tín hiệu); quyền; request, response, mã lỗi.
