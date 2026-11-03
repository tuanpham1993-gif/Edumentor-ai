# Module: Quản trị quan hệ giữa các kỹ năng (F12)

Đặc tả nghiệp vụ của tính năng. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §11, schema ở `docs/database-design.md` §2.4, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `SR-YCnn`, mã quy tắc `SR-Rnn`.

> **DRAFT** — dẫn xuất từ BA (bản Git HEAD) theo D-DOC-01, chưa được người phụ trách xác nhận.

---

## 1. Phạm vi

**Người phụ trách:** Tâm (D-OWN-02; workbook V2 ghi Hòa — workbook không phải nguồn quyết định) · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Admin quản lý quan hệ dùng chung giữa các kỹ năng (tiên quyết, mở rộng, liên quan). Đồ thị này được dùng để mở rộng lộ trình. Màn quản trị mở sơ đồ quan hệ khi bấm một kỹ năng.

**Thuộc module:** `/api/admin/skill-relations*` (4 endpoint).

**Không thuộc module:** cạnh trong một lộ trình cụ thể (F06); danh mục kỹ năng (F11).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| SR-YC01 | Admin tạo, xem, cập nhật, xóa quan hệ giữa kỹ năng theo loại được hỗ trợ | FR-31; UC-12 | — |
| SR-YC02 | Phân biệt quan hệ tiên quyết với các quan hệ khác; không coi mọi quan hệ là tiên quyết | BR-06; BR-07 | — |
| SR-YC03 | Phát hiện vòng lặp trong quan hệ tiên quyết | BR-08 | — |
| SR-YC04 | Kiểm tra ràng buộc trước khi thay đổi; chỉ Admin | BR-32; BR-33; BR-34 | — |

### Màn hình UI

| Màn | Route | Endpoint của module dùng |
|---|---|---|
| AdminSkills-Relations | `/admin/skills` (hộp thoại sơ đồ) | `GET`, `POST`, `PATCH`, `DELETE /api/admin/skill-relations*` |

---

## 2. File liên quan

Theo `docs/structure.md` §2, §3:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/admin/skill_relations.py` |
| Frontend | `api/admin.api.js`; `admin/AdminSkillsPage` (+ `SkillRelationMap`) |

Service: `structure.md` §2 chưa tách tên service riêng cho nhóm này.

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §2.4.

| Bảng | Đọc / ghi | Ràng buộc chính |
|---|---|---|
| `SkillRelation` | Ghi | PK (`from_skill_id`, `to_skill_id`); `relation_type` ∈ prerequisite, extension, related |
| `Skill` | Đọc | Hai đầu quan hệ |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §11. Request, response và mã lỗi **chưa được định nghĩa**: `[NEEDS DECISION]`. Quyền: Admin.

| Mã | Method | Endpoint | Mô tả |
|---|---|---|---|
| EP-070 | GET | `/api/admin/skill-relations` | Danh sách quan hệ |
| EP-071 | POST | `/api/admin/skill-relations` | Tạo quan hệ `prerequisite`, `extension` hoặc `related` |
| EP-072 | PATCH | `/api/admin/skill-relations/{from_skill_id}/{to_skill_id}` | Cập nhật quan hệ |
| EP-073 | DELETE | `/api/admin/skill-relations/{from_skill_id}/{to_skill_id}` | Xóa quan hệ |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| SR-R01 | `relation_type` là `prerequisite`, `extension` hoặc `related`; mặc định `prerequisite`. | `database-design.md` §2.4; `api-endpoints.md` §11 |
| SR-R02 | Hai đầu quan hệ phải là hai kỹ năng khác nhau. | `database-design.md` §2.4 |
| SR-R03 | Hướng quan hệ: kỹ năng nguồn được học trước kỹ năng đích. | `database-design.md` §2.4 |
| SR-R04 | Chỉ quan hệ `prerequisite` phải tạo thành đồ thị không có vòng; kiểm tra khi nạp dữ liệu và khi Admin thay đổi. | `database-design.md` §2.4; BA BR-08 |
| SR-R05 | Quan hệ này dùng chung toàn hệ thống, khác cạnh trong một lộ trình (`LearningPathEdge`). | `database-design.md` §2.4 |
| SR-R06 | Chỉ quản trị viên được thay đổi. | `api-endpoints.md` §11 |

---

## 6. Luồng nghiệp vụ

```text
POST hoặc PATCH thành prerequisite → kiểm tra không tạo vòng tiên quyết (SR-R04) → lưu
```

Mã lỗi khi tạo vòng hoặc trùng quan hệ: `[NEEDS DECISION]`, chưa có ND.

## 7. Transaction

Không có ghi nhiều bảng.

## 8. Bảo mật

SR-R06; BA BR-34.

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F05 Lộ trình | Mở rộng tiên quyết bằng đồ thị kỹ năng chung |
| F07 Gợi ý | Hiển thị quan hệ của kỹ năng đang chọn (BA FR-12) |
| F11 Kỹ năng | Xóa kỹ năng đang có quan hệ bị chặn (RESTRICT, ND-71) |

---

## 10. Câu hỏi mở

`ND-71` — `docs/decisions.md` §4.4.

Chưa có ND: mã lỗi khi tạo vòng; tên service; request, response.
