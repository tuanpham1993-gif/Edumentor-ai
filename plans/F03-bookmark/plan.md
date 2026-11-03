# F03 — Đánh dấu (Bookmark)

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F03 — Đánh dấu (Bookmark) |
| Người phụ trách | **Tâm** (D-OWN-02, `docs/decisions.md` §2) |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/course-bookmark.md`](../../docs/modules/course-bookmark.md) — DRAFT, chưa được người phụ trách xác nhận |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 2 Task: NOT_STARTED 2 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Lưu khóa học quan tâm để xem lại, xem danh sách đã lưu, bỏ lưu; bookmark là trạng thái `bookmarked` của `StudentCourse` (`docs/modules/course-bookmark.md` §1).

## 3. Phạm vi

Theo `docs/modules/course-bookmark.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: `POST`, `GET /api/me/bookmarks`, `DELETE /api/me/bookmarks/{course_id}`; nút Lưu ở Courses, CourseDetail; tab đã lưu ở MyCourses. Bảng, router, service dùng chung với F04.

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `READY_FOR_IMPLEMENTATION` | BA FR-17, §10.4 |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | BA AC-05 (chung với F04); SRS-TRK-01 — các mã này chưa có trong `docs/modules/course-bookmark.md`. Câu hỏi cho Tâm (D-OWN-02): AC-05, SRS-TRK-01 có phải tiêu chí nghiệm thu chính thức của F03 để đưa vào đặc tả không? Việc tài liệu kiểm thử (riêng): chưa có `docs/modules/course-bookmark.tests.md`, cần tạo |
| UI | `READY_FOR_IMPLEMENTATION` | Courses, CourseDetail, MyCourses |
| API | `NEEDS_OWNER_INPUT` | Endpoint có; response, mã lỗi chưa định nghĩa. Câu hỏi cho Tâm (D-OWN-02): response và mã lỗi của các endpoint F03 là gì, để ghi vào `docs/modules/course-bookmark.md`? ND-80 (hai cách lấy khóa học đã lưu) là quyết định đang chờ riêng, không thuộc câu hỏi này |
| Database | `READY_FOR_IMPLEMENTATION` | `StudentCourse` §3.3 (model ở P06-T04, quản lý ở F04) |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có test case. Câu hỏi cho Tâm (D-OWN-02): danh sách kịch bản kiểm thử của F03 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/course-bookmark.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | P06-T04 chờ P01-T05; người làm EP-020 … 022 chưa thống nhất |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P06 | [phase-06-bookmark-learning-progress.md](phase-06-bookmark-learning-progress.md) | P06-T05, P06-T10 |

Task dùng chung quản lý ở tính năng khác: P06-T01 (F04), P06-T02 (F04), P06-T03 (F04), P06-T04 (F04), P06-T09 (F04), P06-T11 (F04).

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P06-T05 | P06-T04 | F04 |
| P06-T10 | P06-T09 | F04 |
| P06-T10 | P05-T11 | F02 |

Quyết định còn chờ ảnh hưởng tính năng: ND-80, ND-32.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Xác nhận đặc tả `docs/modules/course-bookmark.md`.
2. Bổ sung response, mã lỗi (khóa không tồn tại, lưu trùng) cho EP-020 … EP-022.
3. Chốt người làm EP-020 … EP-022 (workbook sheet đối chiếu ghi Khôi).
4. Phối hợp với F04 về Task dùng chung P06-T01 … T04, T09, T11.
5. Soạn kịch bản kiểm thử.

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/course-bookmark.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: kết quả `pytest` bookmark, ảnh nút Lưu và tab đã lưu.
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §6.4 (FR-17), §10.4, UC-07, AC-05; SRS §6.4 (SRS-TRK-01); `docs/api-endpoints.md` §4; `docs/database-design.md` §3.3; `docs/modules/course-bookmark.md`.
