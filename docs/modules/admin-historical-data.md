# Module: Dữ liệu lộ trình lịch sử (ngoài 14 tính năng, tùy chọn)

Đặc tả nghiệp vụ của phần dữ liệu lịch sử phục vụ gợi ý. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §13, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `HD-YCnn`, mã quy tắc `HD-Rnn`.

> **DRAFT.** Các endpoint là tùy chọn với bản thử nghiệm (`api-endpoints.md` §13). `docs/database-design.md` **chưa có bảng** lưu dữ liệu lịch sử.

---

## 1. Phạm vi

**Người phụ trách:** **Chờ nhóm chốt** — workbook V2 ghi "Hòa, Tuấn". · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Admin xem và nhập dữ liệu lộ trình lịch sử phục vụ Collaborative Filtering; hệ thống ghi nhận lộ trình được tạo thành công vào tập dữ liệu lịch sử và kiểm tra dữ liệu trước khi dùng.

**Thuộc module:** `/api/admin/historical-learning-paths*`, `/api/admin/historical-learning-path-imports*` (4 endpoint).

**Không thuộc module:** tạo, lưu lộ trình của người dùng (F05); thuật toán gợi ý (F05, F07).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| HD-YC01 | Quản lý dữ liệu lịch sử: kiểm tra tính hợp lệ, xử lý bản ghi không hợp lệ theo quyền | FR-35; UC-15; §4.1.2 | Định dạng file nhập: ND-75 |
| HD-YC02 | Lộ trình được tạo thành công được ghi nhận để truy cập lại và phân tích | FR-36; BR-17 | Dùng chung với F05 (LP-YC08) |
| HD-YC03 | Cung cấp dữ liệu kỹ năng, khóa học, lộ trình lịch sử hợp lệ cho thành phần đề xuất | FR-37 | — |
| HD-YC04 | Bổ sung lộ trình mới vào tập lịch sử; việc dùng dữ liệu mới để cập nhật mô hình là bước riêng | FR-39; BR-20 | — |
| HD-YC05 | Kiểm tra dữ liệu lịch sử trước khi dùng cho đề xuất hay huấn luyện | BR-19 | — |
| HD-YC06 | Lộ trình được tạo không mặc định là lộ trình thành công | BR-18 | — |

### Màn hình UI

| Màn | Route | Endpoint của module dùng |
|---|---|---|
| AdminHistorical | `/admin/historical` | `GET /api/admin/historical-learning-paths`, `POST /api/admin/historical-learning-path-imports` |

UI ghi "[Định dạng file nhóm chốt]" (ND-75) và hiển thị nguồn dữ liệu mà API chưa có (ND-54).

---

## 2. File liên quan

Theo `docs/structure.md` §2:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/admin/historical_paths.py` |
| Service | `historical_import_service` |
| Gợi ý | `recommender/collaborative_filtering` |
| Frontend | `api/admin.api.js`; `admin/AdminHistoricalPage` |

---

## 3. Dữ liệu

`docs/database-design.md` chưa có bảng lưu bản ghi lịch sử hay lần nhập: `[NEEDS DECISION]`, chưa có ND. Không tạo bảng khi chưa được duyệt (`CLAUDE.md`).

Bảng liên quan đã có: `Skill`, `LearningPath`, `LearningPathNode`, `LearningPathEdge` (`database-design.md` §2, §4).

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §13 (tùy chọn). Request, response và mã lỗi **chưa được định nghĩa**: `[NEEDS DECISION]`. Quyền: Admin.

| Mã | Method | Endpoint | Mô tả |
|---|---|---|---|
| EP-095 | GET | `/api/admin/historical-learning-paths` | Danh sách bản ghi lịch sử |
| EP-096 | GET | `/api/admin/historical-learning-paths/{record_id}` | Chi tiết một bản ghi |
| EP-097 | POST | `/api/admin/historical-learning-path-imports` | Nhập một nhóm bản ghi đã kiểm tra |
| EP-098 | GET | `/api/admin/historical-learning-path-imports/{import_id}` | Trạng thái và kết quả một lần nhập |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| HD-R01 | Các endpoint này không bắt buộc với phiên bản thử nghiệm ban đầu. | `api-endpoints.md` §13 |
| HD-R02 | Khi nhập phải kiểm tra tham chiếu kỹ năng, quan hệ giữa các bản ghi, dữ liệu trùng và phân biệt dữ liệu tổng hợp với dữ liệu người dùng thật. | `api-endpoints.md` §13 |
| HD-R03 | Dữ liệu nhập không được tự ghi đè lộ trình đang dùng của người dùng. | `api-endpoints.md` §13; `conventions.md` |
| HD-R04 | Lưu dữ liệu mới không có nghĩa mô hình được huấn luyện lại hay tự cập nhật. | BA BR-20 |

---

## 6. Luồng nghiệp vụ

Chưa có: phụ thuộc định dạng file (ND-75) và thiết kế bảng.

## 7. Transaction

Chưa có.

## 8. Bảo mật

Chỉ Admin (BA BR-32, BR-34). Dữ liệu chỉ dùng trong phạm vi được phép (BA BR-08 §5.5, NFR-30).

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F05 Lộ trình | Tham khảo lộ trình lịch sử tương tự; lộ trình mới được ghi nhận |
| F07 Gợi ý | Tín hiệu từ dữ liệu lịch sử (BA BR-14) |

---

## 10. Câu hỏi mở

`ND-75`, `ND-54` — `docs/decisions.md` §4.4, §6.

Chưa có ND: thiết kế bảng dữ liệu lịch sử; người phụ trách; request, response, mã lỗi.
