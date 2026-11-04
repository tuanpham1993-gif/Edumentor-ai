---
name: edumentor-documentation-governance
description: Quy tắc quản trị tài liệu EduMentor AI — đọc, kiểm tra, tạo hoặc sửa tài liệu trong docs/, plans/, README.md, SETUP.md; xác định nguồn sự thật, trạng thái và bằng chứng xác nhận, người phụ trách F01–F14, cấu trúc 6 nhóm tài liệu (overview, features, product, operations, design system, design). Dùng trước mọi thay đổi tài liệu, kể cả khi người dùng chỉ nói "cập nhật tài liệu", "sửa đặc tả", "thêm vào docs", "đồng bộ owner", "glossary", "design token", "README". Có bản sao giống hệt ở .claude/skills/ và .agents/skills/.
---

# EduMentor — Documentation Governance

Quy tắc để AI đọc, kiểm tra và sửa tài liệu dự án. Skill không chứa nghiệp vụ và không chép quyết định; quyết định nằm ở `docs/decisions.md` và chỉ được trỏ bằng mã.

- Bản gốc: `.claude/skills/edumentor-documentation-governance/SKILL.md`.
- Bản sao giống từng byte: `.agents/skills/edumentor-documentation-governance/SKILL.md` (ngoại lệ D-DOC-03, 2026-11-03).
- Quy tắc làm việc chung (không suy diễn nghiệp vụ, ghi `decisions.md` trước, mỗi quy tắc một file…): mục "Quy tắc làm việc" của `CLAUDE.md` (Claude) và `AGENTS.md` (agent phụ). Skill này không chép lại các quy tắc đó.

## 1. Cấu trúc tài liệu (D-DOC-06; bản đồ: `docs/README.md`)

| Nhóm | Đường dẫn | Ghi chú |
|---|---|---|
| 01 Overview | `docs/01-overview/` | Chỉ mục. Đề bài, BA, SRS nằm ở `docs/` gốc — không di chuyển |
| 02 Features | `docs/modules/` | Đặc tả F01–F14 và phần ngoài 14 tính năng. Không tạo `docs/02-features/` |
| 03 Product | `docs/03-product/` | Chỉ mục sản phẩm, `glossary.md` (định nghĩa ngắn kèm nguồn — không phải nguồn định nghĩa) |
| 04 Operations | `docs/04-operations/` | Chỉ mục; cài đặt ở `SETUP.md` |
| 05 Design System | `docs/05-design-system/` | Token quan sát được — chưa phải Design System chính thức |
| 06 Design | `docs/06-design/` | Chỉ mục; UI ở `docs/ui-design/` |

Không di chuyển, đổi tên file để cấu trúc gọn hơn: `AGENTS.md`, `.agents/skills/`, `CLAUDE.md` và các skill trỏ theo đường dẫn hiện tại.

## 2. Nguồn sự thật

Thứ bậc khi các nguồn khác nhau: **D-DOC-01** (`docs/decisions.md` §1). Bản hiệu lực của đề bài, BA, SRS, UI, workbook: sổ nguồn ở `docs/decisions.md` §1.

| Nội dung | Nguồn chính | Nơi khác chỉ được |
|---|---|---|
| Quyết định, điểm chờ, phân công | `docs/decisions.md` (§2: D-OWN-01, D-OWN-02) | Trỏ mã D/T/ND |
| Yêu cầu nghiệp vụ, nghiệm thu | BA, SRS theo sổ nguồn | Trỏ mục, mã FR, BR, AC, SRS-xxx |
| Đặc tả tính năng | `docs/modules/<tên>.md` | Trỏ mã `XX-R`, `XX-YC` |
| Endpoint toàn hệ thống | `docs/api-endpoints.md` | Trỏ mục |
| Ràng buộc dữ liệu | `docs/database-design.md` | Trỏ mục |
| Phase, Task, trạng thái Task | `plans/` theo D-DOC-05 (8) | Chỉ mục hoặc liên kết, không ghi trạng thái |
| Giao diện | `docs/ui-design/` (D-FE-12) | Trỏ tên màn, mã S-xx |
| Token | `docs/ui-design/html/app.css` (UI), `frontend/src/index.css` (code); tài liệu: `docs/05-design-system/` | Không gọi là chính thức khi chưa có quyết định |
| Kịch bản test | `docs/modules/<tên>.tests.md` | Trỏ mã kịch bản |
| Kết quả chạy test | Chưa có quy định (ND-67) | Chỉ cột Evidence của Task |

Workbook `.xlsx` không phải nguồn quyết định (D-DOC-01, D-DOC-04); không sửa nếu không có yêu cầu riêng. Thông tin workbook ghi khác (ví dụ người phụ trách cũ) được giữ để truy vết dưới dạng "workbook V2 ghi …", kèm câu "workbook không phải nguồn quyết định", và không bao giờ được trình bày như thông tin hiện hành.

## 3. Trạng thái và bằng chứng

Chỉ dùng trạng thái đã có; không tạo trạng thái mới, không dùng `APPROVED`.

| Loại | Giá trị | Nguồn định nghĩa |
|---|---|---|
| Trạng thái đặc tả, module | `SPEC CONFIRMED`, `IMPLEMENTED`, `PENDING`, `BLOCKED`, `CONFLICT`; không dùng "DONE" cho phần chưa có code | `docs/decisions.md` §2 "Quy ước trạng thái" |
| Mục T | ☑ (nhóm đã đồng ý), ☐ (chưa) — ☐ không được coi là đã chốt | `docs/decisions.md` §3 |
| Quyết định | Có mã D-xx kèm người và ngày xác nhận; ND-xx là điểm chờ | `docs/decisions.md` |
| Trạng thái Task | 6 giá trị | `plans/plan.md` PART 2 quy tắc 5 |
| Mức sẵn sàng triển khai (chỉ ở phần đánh giá mức sẵn sàng của `plans/Fxx-*/plan.md`) | `READY_FOR_IMPLEMENTATION`, `READY_WITH_LIMITATIONS`, `NOT_READY_BLOCKED`, `NEEDS_OWNER_INPUT`, `BLOCKED_DATASET` | D-DOC-07 |
| Đặc tả soạn chưa xác nhận | `DRAFT` | `docs/modules/README.md` |

Nhãn ghi nhận (chỉ mô tả tình trạng, không phải xác nhận): `NEEDS_OWNER_CONFIRMATION`, `NEEDS_OWNER_INPUT`, `NOT_DEFINED_IN_SOURCE`, `SOURCE_CONFLICT`, `BLOCKED_DATASET`, `NEEDS_VERIFICATION`.

Trạng thái Task, trạng thái quyết định/đặc tả và mức sẵn sàng triển khai là ba hệ tách riêng (D-DOC-07): mỗi cột chỉ dùng giá trị của một hệ; không dùng `PENDING`, `CONFLICT` hoặc `BLOCKED` đơn lẻ làm mức sẵn sàng; mức sẵn sàng không phải phê duyệt và không đổi trạng thái đặc tả hay Task.

Khi viết "đã chốt" phải dẫn đúng bằng chứng gốc (mã D-xx, mục T ☑, hoặc dòng "… xác nhận <ngày>" trong `decisions.md`). Không gộp nhiều loại bằng chứng thành một trạng thái chung. Không tự nâng trạng thái (ví dụ `DRAFT` → `SPEC CONFIRMED`).

## 4. Trước khi sửa tài liệu

1. Đọc skill này, và `docs/README.md` nếu file đã tồn tại. Khi khởi tạo lần đầu (chưa có `docs/README.md`), căn cứ D-DOC-01, D-DOC-06 và các quyết định hiện có trong `docs/decisions.md`.
2. Đọc phần liên quan của `docs/decisions.md`: sổ nguồn §1, phân công §2, các ND liên quan.
3. Việc thuộc tính năng: đọc `docs/modules/README.md` và đặc tả tương ứng.
4. Việc thuộc Phase, Task: đọc `plans/plan.md` PART 2 và thư mục `plans/Fxx-*/`.
5. Xác định nguồn chính (mục 2). Chỉ sửa nội dung ở nguồn chính; nơi khác chỉ cập nhật liên kết hoặc mã.
6. Thay đổi là một quyết định → ghi vào `docs/decisions.md` trước, rồi mới sửa tài liệu khác.
7. Sau khi sửa: kiểm tra liên kết Markdown; mỗi Task ID chỉ có một dòng có trạng thái; không có đoạn chép trùng nội dung của nguồn.

## 5. Quy tắc riêng cho tài liệu

- Không đổi người phụ trách khi `docs/decisions.md` §2 chưa ghi.
- Không coi bản có ngày sửa mới nhất là bản hiệu lực; chỉ theo sổ nguồn.
- Không tạo tài liệu trùng chức năng với tài liệu đã có.
- Tài liệu dẫn xuất (kể cả glossary) được ghi định nghĩa ngắn hoặc trích phần cần thiết, kèm nguồn, mục và trạng thái nguồn; không chép nguyên chương hay nguyên mục; không bổ sung, mở rộng hay đổi nghĩa nghiệp vụ. Nguồn mâu thuẫn → ghi cả hai nguồn và trạng thái chờ xác nhận. Khi tài liệu dẫn xuất khác nguồn, nguồn thắng (D-DOC-06).
- Không chuyển BA, SRS sang bản Markdown thứ hai khi baseline chưa được xác nhận trong sổ nguồn.
- Không ghi token, màu, font, spacing không có trong file nguồn ở mục 2.
- Không tạo dataset, câu hỏi, đáp án thay dữ liệu chính thức; dữ liệu giả chỉ dùng khi được cho phép và ghi rõ là dữ liệu giả.
- Không biến mặc định an toàn thành quyết định.
- Thiếu hoặc mâu thuẫn → ghi nhãn phù hợp (mục 3) và đề xuất `ND-xx` cho người có thẩm quyền; không vá bằng nội dung tự viết.

## 6. Phối hợp agent

- Claude (`.claude/`) là agent chính: điều phối, áp dụng skill này, cập nhật skill khi được yêu cầu.
- Agent phụ (`.agents/`) áp dụng cùng quy tắc, chỉ làm trong phạm vi được giao.
- Agent phụ gặp mâu thuẫn, thiếu quyết định hoặc việc vượt quyền: dừng, báo người dùng kèm file, vị trí và nguồn; không tự quyết. Việc báo lại Claude đi qua người dùng.
- Hai bản skill phải giống từng byte: sửa bản `.claude/`, chép sang `.agents/` trong cùng thay đổi, so sánh hai file trước khi báo xong.

## 7. Git

- Không stage, commit, push khi chưa được yêu cầu.
- Kiểm tra `git status` trước và sau; không ghi đè hay xóa công việc chưa commit.
- Không dùng reset, checkout, clean, stash khi chưa được cho phép.
