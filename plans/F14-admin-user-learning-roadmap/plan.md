# F14 — Quản trị — xem lộ trình học tập của người dùng

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F14 — Quản trị — xem lộ trình học tập của người dùng |
| Người phụ trách | **Hòa** (D-OWN-02, `docs/decisions.md` §2) |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/admin-user-paths.md`](../../docs/modules/admin-user-paths.md) — DRAFT, chưa có căn cứ BA |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 3 Task: BLOCKED 1 · NOT_STARTED 2 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Admin xem, chỉ đọc, lộ trình và tiến độ kỹ năng của từng người dùng (`docs/modules/admin-user-paths.md` §1). Có giữ chức năng hay không: ND-79.

## 3. Phạm vi

Theo `docs/modules/admin-user-paths.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: Màn AdminUserPaths; backend M3 (P11-T03, BLOCKED).

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `NOT_READY_BLOCKED` | BA không có; BA §4.3, FR-41, NFR-30 giới hạn dữ liệu cá nhân. Sự tồn tại và phạm vi chức năng chờ ND-79 (PENDING): có giữ không; nếu giữ thì quy tắc quyền, ghi log và cập nhật BA. Chưa có phần nghiệp vụ nào triển khai được trước khi ND-79 được chốt |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | Chưa có; BA không có AC cho chức năng này. Câu hỏi cho Hòa (D-OWN-02): tiêu chí nghiệm thu của F14 là gì, để đưa vào `docs/modules/admin-user-paths.md`? |
| UI | `READY_WITH_LIMITATIONS` | AdminUserPaths dựng được với trạng thái "chưa khả dụng" (D-FE-08); giới hạn: chưa có endpoint (ND-55, M3); phạm vi dữ liệu admin được xem chờ ND-79 |
| API | `NOT_READY_BLOCKED` | ND-55 (M3) |
| Database | `READY_WITH_LIMITATIONS` | Chỉ đọc §3.1, §3.2, §4.4–§4.6 làm được; giới hạn: tên lộ trình (`name`) chưa có trong `LearningPath` — ND-54 |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có. Câu hỏi cho Hòa (D-OWN-02): danh sách kịch bản kiểm thử của F14 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/admin-user-paths.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | ND-79, ND-55; P07-T14 (PathGraph) |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P11 | [phase-11-user-roadmap-admin.md](phase-11-user-roadmap-admin.md) | P11-T01, P11-T02, P11-T03 |

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P11-T02 | P03-T04 | dùng chung |
| P11-T02 | P07-T14 | F06 |
| P11-T03 | P07-T04 | F05 |
| P11-T03 | P04-T03 | F01 |

Quyết định còn chờ ảnh hưởng tính năng: ND-79, ND-55, ND-54.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Đề xuất phương án ND-79 (giữ chức năng không; quyền riêng tư, ghi log).
2. Đề xuất endpoint M3 cho ND-55 (tham khảo gợi ý workbook EP-075, EP-100, chưa duyệt).
3. Bổ sung yêu cầu vào BA qua người có thẩm quyền nếu giữ chức năng.
4. Xác nhận đặc tả `docs/modules/admin-user-paths.md`; soạn kịch bản kiểm thử.

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/admin-user-paths.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: ảnh AdminUserPaths ở trạng thái "chưa khả dụng"; khi có M3: kết quả `pytest`.
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §4.3, FR-41, NFR-30; SRS §6.15 (SRS-ADMU-01 … 04); `docs/database-design.md` §3, §4; `docs/decisions.md` ND-54, ND-55, ND-79; `docs/modules/admin-user-paths.md`.
