# Module: Node và cạnh trong lộ trình học tập (F06)

Đặc tả nghiệp vụ của tính năng. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §6, §7, schema ở `docs/database-design.md` §4.5, §4.6, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `LG-YCnn`, mã quy tắc `LG-Rnn`.

> **DRAFT** — dẫn xuất từ BA (bản Git HEAD) theo D-DOC-01, chưa được người phụ trách xác nhận.

---

## 1. Phạm vi

**Người phụ trách:** Hòa (workbook V2) · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Lộ trình là đồ thị kỹ năng: mỗi node là một kỹ năng của lộ trình, mỗi cạnh là kết nối "học trước, học sau" giữa hai node. Người dùng xem cấu trúc, chọn kỹ năng để khám phá, thêm, sửa, xóa node và cạnh. Khái niệm Skill Graph: BA §8.3.

**Thuộc module:** `/api/learning-paths/{path_id}/nodes*` (5 endpoint), `/api/learning-paths/{path_id}/edges*` (4 endpoint).

**Không thuộc module:** tạo, lưu, đổi trạng thái lộ trình (F05); gợi ý khóa học cho node (F07); quan hệ kỹ năng dùng chung (F12).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| LG-YC01 | Xem mục tiêu, cấu trúc và các kỹ năng của lộ trình | UC-05 bước 4; FR-10 | — |
| LG-YC02 | Chọn và khám phá kỹ năng mà không bắt buộc hoàn thành các kỹ năng trước | FR-11; BR-10 | — |
| LG-YC03 | Thêm, xem, sửa, xóa node kỹ năng | §10.6 | — |
| LG-YC04 | Thêm, xem, sửa loại, xóa cạnh | §10.7 | — |
| LG-YC05 | Cấu trúc phải dùng kỹ năng hợp lệ, quan hệ được hỗ trợ; phát hiện vòng lặp tiên quyết | BR-08 | Kiểm vòng cho cạnh **trong lộ trình** chưa ghi ở tài liệu dẫn xuất; chưa có ND |
| LG-YC06 | Không tự kết luận người học đã thành thạo kỹ năng | BR-11 | — |

### Màn hình UI

| Màn | Route | Endpoint của module dùng |
|---|---|---|
| PathDetail | `/learning-paths/:pathId` | Node `GET`, `DELETE`; cạnh `DELETE` (cùng màn với F05, F07) |
| PathEdit | `/learning-paths/:pathId/edit` | `POST .../nodes`, `POST .../edges`. Route: ND-50 |

---

## 2. File liên quan

Theo `docs/structure.md` §2:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/learning_path_nodes.py`, `backend/app/routers/learning_path_edges.py` |
| Service | `path_graph_service` |
| Frontend | `api/learningPaths.api.js`; `path/PathDetailPage` |

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §4.5, §4.6.

| Bảng | Đọc / ghi | Dùng cho |
|---|---|---|
| `LearningPathNode` | Ghi | `node_role`, `is_target`, `added_by`, `is_required`, `display_order` |
| `LearningPathEdge` | Ghi | `relation_type` |
| `LearningPath` | Đọc | Kiểm tra lộ trình tồn tại và thuộc người dùng |
| `Skill` | Đọc | Kiểm tra `skill_id` |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §6, §7. Request, response và mã lỗi **chưa được định nghĩa**: `[NEEDS DECISION]`. Quyền: chưa ghi (workbook đề xuất `owner-only`, chưa duyệt).

| Mã | Method | Endpoint | Mô tả |
|---|---|---|---|
| EP-034 | GET | `/api/learning-paths/{path_id}/nodes` | Mọi node của lộ trình |
| EP-035 | POST | `/api/learning-paths/{path_id}/nodes` | Thêm node |
| EP-036 | GET | `/api/learning-paths/{path_id}/nodes/{skill_id}` | Chi tiết một node |
| EP-037 | PATCH | `/api/learning-paths/{path_id}/nodes/{skill_id}` | Sửa `node_role`, `added_by`, `display_order` |
| EP-038 | DELETE | `/api/learning-paths/{path_id}/nodes/{skill_id}` | Xóa node và cạnh liên quan |
| EP-039 | GET | `/api/learning-paths/{path_id}/edges` | Mọi cạnh của lộ trình |
| EP-040 | POST | `/api/learning-paths/{path_id}/edges` | Thêm cạnh giữa hai node có sẵn |
| EP-041 | PATCH | `/api/learning-paths/{path_id}/edges/{from_skill_id}/{to_skill_id}` | Đổi loại quan hệ |
| EP-042 | DELETE | `/api/learning-paths/{path_id}/edges/{from_skill_id}/{to_skill_id}` | Xóa cạnh |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| LG-R01 | Khóa chính node là (`path_id`, `skill_id`); một kỹ năng chỉ xuất hiện một lần trong một lộ trình. | `api-endpoints.md` §6; `database-design.md` §4.5 |
| LG-R02 | `node_role` là `prerequisite`, `optional`, `extension` hoặc trống. | `api-endpoints.md` §6; `database-design.md` §4.5 |
| LG-R03 | Kỹ năng mục tiêu lưu riêng ở `is_target`, không gộp vào `node_role`. | `api-endpoints.md` §6; `database-design.md` §4.5; `structure.md` §6 |
| LG-R04 | `added_by` là `system` hoặc `user`. | `api-endpoints.md` §6; `database-design.md` §4.5 |
| LG-R05 | `display_order` chỉ để sắp xếp, không xác định quan hệ tiên quyết. | `api-endpoints.md` §6 |
| LG-R06 | `is_required` đánh dấu node bắt buộc để hoàn thành lộ trình. | `database-design.md` §4.5; `structure.md` §6 |
| LG-R07 | Hai đầu cạnh phải là node của cùng lộ trình. | `api-endpoints.md` §7; `database-design.md` §4.6 |
| LG-R08 | `relation_type` của cạnh là `prerequisite` hoặc `optional`. | `database-design.md` §4.6; `structure.md` §6 |
| LG-R09 | Với `prerequisite`, kỹ năng nguồn được học trước kỹ năng đích. | `api-endpoints.md` §7; `database-design.md` §4.6 |
| LG-R10 | Xóa node phải xóa các cạnh liên quan trong cùng transaction; không để cạnh mồ côi. | `api-endpoints.md` §6, §7, §14; `database-design.md` §4.5 |
| LG-R11 | Hoàn thành lộ trình dựa trên tiến độ các node bắt buộc, không dựa vào việc đi tới một node kết thúc. | `database-design.md` §4.6 |

---

## 6. Luồng nghiệp vụ

```text
Xóa node: DELETE .../nodes/{skill_id} → [transaction] xóa các cạnh có node này ở một đầu → xóa node
Thêm cạnh: POST .../edges → hai đầu là node của lộ trình? → không: lỗi [mã lỗi: NEEDS DECISION]
```

## 7. Transaction

| Thao tác | Các ghi trong cùng transaction | Nguồn |
|---|---|---|
| Xóa node | Xóa node + mọi cạnh liên quan | `api-endpoints.md` §14; `database-design.md` §4.5 |

## 8. Bảo mật

Chỉ sửa đồ thị của lộ trình thuộc người dùng hiện tại (BA §4.3, FR-41).

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F05 Lộ trình | Tạo lộ trình và đồ thị ban đầu |
| F07 Gợi ý khóa học | Chọn node để xem khóa học |
| F12 Quan hệ kỹ năng | Quan hệ chung giữa kỹ năng; khác cạnh trong một lộ trình (`database-design.md` §2.4) |
| F09 Ôn tập | `is_required` dùng cho cập nhật lộ trình sau ôn tập (ND-24) |

---

## 10. Câu hỏi mở

`ND-54` (dữ liệu UI chưa có), `ND-50` (route PathEdit), `ND-24` — `docs/decisions.md` §4.

Chưa có ND: kiểm vòng lặp tiên quyết cho cạnh trong lộ trình (LG-YC05); quyền của 9 endpoint; request, response, mã lỗi.
