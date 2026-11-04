# F08 — Trò chuyện với gia sư AI

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F08 — Trò chuyện với gia sư AI |
| Người phụ trách | **Tâm** (D-OWN-02, `docs/decisions.md` §2) |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/ai-tutor.md`](../../docs/modules/ai-tutor.md) — DRAFT, chưa được người phụ trách xác nhận |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 9 Task: NOT_STARTED 9 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Trò chuyện với gia sư AI theo phiên: hỏi kiến thức, giải thích, ví dụ mã, phân tích lỗi, bài tập củng cố (`docs/modules/ai-tutor.md` §1).

## 3. Phạm vi

Theo `docs/modules/ai-tutor.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: `/api/chat/sessions*` (6 endpoint); màn Tutor; hành vi AI ở P12-T06.

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `READY_WITH_LIMITATIONS` | BA FR-20 … FR-23, BR-21 … BR-25; ND-59 |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | BA AC-06; SRS-TUT-01 … 07 — các mã này chưa có trong `docs/modules/ai-tutor.md`. Câu hỏi cho Tâm (D-OWN-02): AC-06, SRS-TUT-01 … 07 có phải tiêu chí nghiệm thu chính thức của F08 để đưa vào đặc tả không? Việc tài liệu kiểm thử (riêng): chưa có `docs/modules/ai-tutor.tests.md`, cần tạo |
| UI | `READY_WITH_LIMITATIONS` | Tutor; tin nhắn có cấu trúc ND-54 |
| API | `NEEDS_OWNER_INPUT` | Endpoint có; response, mã lỗi, quy tắc chủ sở hữu chưa ghi. Câu hỏi cho Tâm (D-OWN-02): response, mã lỗi và quy tắc chủ sở hữu phiên của các endpoint F08 là gì, để ghi vào `docs/modules/ai-tutor.md`? |
| Database | `READY_WITH_LIMITATIONS` | §5 làm được; giới hạn: tin nhắn Tutor có `code`/`quiz` có cấu trúc mà UI hiển thị chưa có trong API/CSDL — ND-54 |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có test case. Câu hỏi cho Tâm (D-OWN-02): danh sách kịch bản kiểm thử của F08 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/ai-tutor.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | P08-T04 chờ P01-T05; phương án mô hình AI (P12) |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P08 | [phase-08-ai-tutor.md](phase-08-ai-tutor.md) | P08-T01, P08-T02, P08-T03, P08-T04, P08-T05, P08-T06, P08-T07, P08-T08 |
| P12 | [phase-12-ai-ml.md](phase-12-ai-ml.md) | P12-T06 |

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P08-T04 | P01-T05 | dùng chung |
| P08-T04 | P04-T04 | F01 |
| P08-T06 | P01-T08 | dùng chung |
| P08-T07 | P03-T03 | dùng chung |

Quyết định còn chờ ảnh hưởng tính năng: ND-59, ND-54, ND-77, ND-81.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Xác nhận đặc tả `docs/modules/ai-tutor.md`.
2. Bổ sung response, mã lỗi, quy tắc chủ sở hữu cho EP-044 … EP-049.
3. Ghi transaction khi gửi tin nhắn (lưu tin user, tin assistant).
4. Soạn kịch bản kiểm thử (P08-T03).

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/ai-tutor.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: kết quả `pytest` F08 (P08-T06), ảnh màn Tutor.
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §6.5 (FR-20 … FR-23), §8.5, §9.5, §10.9, UC-08, AC-06; SRS §6.7 (SRS-TUT-01 … 07); `docs/api-endpoints.md` §9; `docs/database-design.md` §5; `docs/modules/ai-tutor.md`.
