# Module: Bong bóng chat và AI tư vấn khóa học (ngoài 14 tính năng)

Đặc tả của tiện ích bong bóng chat. Quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `CA-YCnn`, mã quy tắc `CA-Rnn`.

> **DRAFT, chưa có căn cứ BA.** BA không có chức năng này. Chưa có endpoint (ND-55, M4); người phụ trách, link GitHub/Zalo và phạm vi tích hợp chưa xác định (`docs/decisions.md` §5, workbook UI2-04). Không triển khai phần AI khi các mục này chưa chốt.

---

## 1. Phạm vi

**Người phụ trách:** **Chờ nhóm chốt** — workbook V2 ghi "Chưa phân công" ở màn hình, người xác nhận màn là Tâm, EP-003 ghi Tuấn. · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Bong bóng cố định ở góc màn hình với bốn lối tắt: GitHub, Zalo, Liên hệ, AI tư vấn khóa học. Phần AI gợi ý khóa học kèm thẻ khóa; khách ưu tiên khóa cơ bản, tài khoản đã đăng nhập được gợi ý theo kỹ năng.

**Thuộc module:** giao diện bong bóng; chat tư vấn khóa học (chưa có endpoint).

**Không thuộc module:** AI Consultant tạo lộ trình (F05); AI Tutor (F08); trang Liên hệ (F10).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| CA-YC01 | Bong bóng chat với lối tắt GitHub, Zalo, Liên hệ, AI tư vấn khóa học | Không có trong BA. Căn cứ khác: UI ChatBubble-Menu | `decisions.md` §5 (UI2-04, chưa có ND) |
| CA-YC02 | AI tư vấn khóa học gợi ý khóa kèm thẻ khóa; khách và tài khoản được gợi ý khác nhau | Không có trong BA. Căn cứ khác: UI ChatBubble-Advisor | ND-55 (M4) |

### Màn hình UI

| Màn | Route | Endpoint |
|---|---|---|
| ChatBubble-Menu | hiện trên `/courses` và các trang khác | Link ngoài (GitHub, Zalo — link tạm); điều hướng `/contact` |
| ChatBubble-Advisor | hiện trên `/courses` và các trang khác | Chat tư vấn: chưa có (M4); `GET /api/me/skills` (F01) để cá nhân hóa |

---

## 2. File liên quan

`docs/structure.md` §3: component `ChatBubble`, bọc ở `App.jsx`. File backend chưa có trong `docs/structure.md`.

---

## 3. Dữ liệu

Chưa xác định. Tài liệu chưa nói chat tư vấn có lưu vào `ChatSession` hay không (`session_type` hiện chỉ có `tutor`, `learning_path` — `database-design.md` §5.1).

---

## 4. Endpoint

`docs/api-endpoints.md` **chưa có endpoint** (ND-55, M4). Workbook V2 ghi EP-003 "chưa định nghĩa". Không tạo endpoint hay API giả (D-FE-08).

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| CA-R01 | Bong bóng hiện trên mọi trang trừ `/admin/*`, `/tutor`, `/consultant` và trang làm bài. | `structure.md` §3 |
| CA-R02 | Phần AI tư vấn khóa học hiển thị trạng thái "chưa khả dụng" cho tới khi có endpoint. | D-FE-08; ND-55 |

---

## 6–8. Luồng, transaction, bảo mật

Chưa có. Khách có được dùng AI tư vấn không: chưa chốt (BA không có vai trò Khách).

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F01 | `GET /api/me/skills` |
| F02 | Thẻ khóa học |
| F10 | Lối tắt "Liên hệ" |

---

## 10. Câu hỏi mở

`ND-55` (M4) — `docs/decisions.md` §6.

Chưa có ND: người phụ trách, link GitHub/Zalo, phạm vi tích hợp (ghi ở `docs/decisions.md` §5, UI2-04); quyền của khách; dữ liệu.
