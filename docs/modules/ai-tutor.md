# Module: AI Tutor (F08)

Đặc tả nghiệp vụ của tính năng. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §9, schema ở `docs/database-design.md` §5, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `TU-YCnn`, mã quy tắc `TU-Rnn`.

> **DRAFT** — dẫn xuất từ BA (bản Git HEAD) theo D-DOC-01, chưa được người phụ trách xác nhận.

---

## 1. Phạm vi

**Người phụ trách:** Tâm (workbook V2) · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Người dùng trò chuyện với gia sư AI theo từng phiên: hỏi kiến thức, xin giải thích, ví dụ mã, phân tích lỗi và bài tập củng cố. Mỗi phiên giữ ngữ cảnh hội thoại và gắn với người dùng. Giải pháp AI: BA §8.5.

**Thuộc module:** `/api/chat/sessions*` (6 endpoint).

**Không thuộc module:** AI Consultant tạo lộ trình (F05, `/api/chat/learning-path`); AI tư vấn khóa học trong bong bóng chat (`chat-advisor.md`).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| TU-YC01 | Gửi câu hỏi và nhận phản hồi liên quan đến nội dung học | FR-20; UC-08 | — |
| TU-YC02 | Duy trì ngữ cảnh trong phiên để dùng các lượt trao đổi trước | FR-21; BR-21 | Số tin nhắn nạp lại: ND-59 |
| TU-YC03 | Giải thích khái niệm, làm rõ nội dung khó, phân tích mã, hỗ trợ tìm nguyên nhân lỗi | FR-22; BR-24 | — |
| TU-YC04 | Tạo bài tập củng cố theo chủ đề vừa thảo luận | FR-23; §10.9 | Dữ liệu quiz có cấu trúc: ND-54 |
| TU-YC05 | Trả lời đúng trọng tâm; không trình bày điều chưa xác minh như sự thật | BR-22; BR-23 | — |
| TU-YC06 | Không tự đổi trạng thái khóa học, kỹ năng hay kết quả đánh giá dựa trên hội thoại | BR-25 | — |
| TU-YC07 | Dịch vụ AI lỗi thì báo lỗi, không trả phản hồi thành công giả | UC-08 luồng phụ; FR-43; NFR-11 | — |
| TU-YC08 | Nạp tối đa 6 tin nhắn gần nhất; chấm sao câu trả lời; bộ nhớ phiên trên RAM/Redis | Không có trong BA; chỉ có ở đề bài SRS v1.0 | ND-59, ND-81: giữ hiện hành |

### Màn hình UI

| Màn | Route | Endpoint của module dùng |
|---|---|---|
| Tutor | `/tutor` | `GET`, `POST /api/chat/sessions`; `GET`, `DELETE /api/chat/sessions/{session_id}`; `POST .../messages` |

UI demo hiển thị tin nhắn có `code` và `quiz` có cấu trúc mà API chưa có (ND-54).

---

## 2. File liên quan

Theo `docs/structure.md` §2:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/chat_tutor.py` |
| Service | `tutor_service` |
| AI | `ai/` |
| Frontend | `api/tutor.api.js`; `tutor/TutorPage` |

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §5.

| Bảng | Đọc / ghi | Dùng cho |
|---|---|---|
| `ChatSession` | Ghi | `session_type = tutor`, `topic`, `status` |
| `ChatMessage` | Ghi | Tin nhắn `user`, `assistant` |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §9. Request, response và mã lỗi **chưa được định nghĩa**: `[NEEDS DECISION]`. Quyền: phiên gắn người dùng đã xác thực (`api-endpoints.md` §9); quy tắc chủ sở hữu chi tiết chưa ghi.

| Mã | Method | Endpoint | Mô tả |
|---|---|---|---|
| EP-044 | POST | `/api/chat/sessions` | Tạo phiên mới |
| EP-045 | GET | `/api/chat/sessions` | Danh sách phiên của người dùng |
| EP-046 | GET | `/api/chat/sessions/{session_id}` | Thông tin phiên và lịch sử |
| EP-047 | POST | `/api/chat/sessions/{session_id}/messages` | Gửi tin nhắn, nhận phản hồi AI |
| EP-048 | GET | `/api/chat/sessions/{session_id}/messages` | Tin nhắn của phiên |
| EP-049 | DELETE | `/api/chat/sessions/{session_id}` | Lưu trữ phiên (`archived`) |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| TU-R01 | Mỗi phiên gắn với người dùng đã đăng nhập; người dùng khác không đọc được. | `api-endpoints.md` §9; `database-design.md` §5.1 |
| TU-R02 | `session_id` là UUID. | `database-design.md` §5.1 |
| TU-R03 | Phiên Tutor có `session_type = tutor`; Tutor và Consultant cùng namespace `/api/chat/` nhưng endpoint và loại phiên riêng. | `api-endpoints.md` §9; `database-design.md` §5.1 |
| TU-R04 | `DELETE /api/chat/sessions/{session_id}` chuyển `status` sang `archived`. | `database-design.md` §5.1; `structure.md` §6 |
| TU-R05 | `ChatMessage.role` là `user` hoặc `assistant`. | `database-design.md` §5.2 |
| TU-R06 | Bài tập củng cố gồm ba câu trắc nghiệm theo chủ đề vừa thảo luận khi phù hợp. | `api-endpoints.md` §9 |
| TU-R07 | Chưa có cột hay endpoint chấm sao tin nhắn. | `database-design.md` §5.2; ND-59 |

---

## 6. Luồng nghiệp vụ

```text
POST /chat/sessions → tạo phiên tutor
POST /chat/sessions/{id}/messages {nội dung}
  → lưu tin user → gửi ngữ cảnh phiên + câu hỏi tới AI [số tin: ND-59]
  → AI lỗi: báo lỗi (TU-YC07) | thành công: lưu tin assistant, trả phản hồi
DELETE /chat/sessions/{id} → archived
```

## 7. Transaction

Chưa ghi trong tài liệu.

## 8. Bảo mật

Phiên là dữ liệu cá nhân (BA FR-41). Chỉ gửi dữ liệu cần thiết tới dịch vụ AI (BA NFR-31).

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F05 AI Consultant | Dùng chung `ChatSession`, `ChatMessage` với `session_type` khác |
| F04, F09 | AI Tutor không được đổi trạng thái học tập (TU-YC06) |

---

## 10. Câu hỏi mở

`ND-59`, `ND-54`, `ND-77`, `ND-81` — `docs/decisions.md` §4, §6.

Chưa có ND: quy tắc chủ sở hữu khi truy cập phiên của người khác; transaction gửi tin nhắn; request, response, mã lỗi.
