# Bản đồ tài liệu EduMentor AI

File này chỉ là bản đồ: chỉ ra tài liệu nằm ở đâu, không chứa nghiệp vụ hay quyết định. Cấu trúc 6 nhóm theo **D-DOC-06**; thứ tự ưu tiên giữa các nguồn theo **D-DOC-01**; bản hiệu lực của từng nguồn theo sổ nguồn — cả ba ở [`decisions.md`](decisions.md) §1.

Quy tắc đọc, tạo và sửa tài liệu: skill [`edumentor-documentation-governance`](../.claude/skills/edumentor-documentation-governance/SKILL.md) (bản sao cho agent phụ: [`.agents/skills/edumentor-documentation-governance/SKILL.md`](../.agents/skills/edumentor-documentation-governance/SKILL.md)). Bản đồ này không chép lại các quy tắc đó.

## 6 nhóm tài liệu

| Nhóm | Thư mục | Nội dung |
|---|---|---|
| 01 Overview | [`01-overview/`](01-overview/README.md) | Chỉ mục đề bài, BA, SRS, quyết định — các file nguồn vẫn ở `docs/` gốc |
| 02 Features | [`modules/`](modules/README.md) | Đặc tả F01–F14 và phần ngoài 14 tính năng |
| 03 Product | [`03-product/`](03-product/README.md) | Chỉ mục sản phẩm, [thuật ngữ](03-product/glossary.md) |
| 04 Operations | [`04-operations/`](04-operations/README.md) | Chỉ mục cài đặt, quy ước, kế hoạch |
| 05 Design System | [`05-design-system/`](05-design-system/README.md) | [Token quan sát được](05-design-system/design-tokens.md) — chưa phải Design System chính thức |
| 06 Design | [`06-design/`](06-design/README.md) | Chỉ mục giao diện — bộ UI vẫn ở [`ui-design/`](ui-design/README.md) |

## File ở `docs/` gốc

Cột "Nhóm" chỉ là phân loại để điều hướng: file vẫn nằm ở `docs/` gốc, không di chuyển và không tạo thư mục mới để chứa chúng (D-DOC-06 (3)). Việc xếp nhóm không thay đổi thứ tự ưu tiên theo D-DOC-01 và không làm file nào trở thành nguồn quyết định.

| File | Nhóm |
|---|---|
| [`AI_Learning_Assistant_Recommender SRS.docx.pdf`](<AI_Learning_Assistant_Recommender SRS.docx.pdf>) | 01 |
| [`EdumentorAi_BA.md`](EdumentorAi_BA.md) | 01 |
| [`EduMentor_AI_SRS_v2.0.docx`](EduMentor_AI_SRS_v2.0.docx), [`EduMentor_AI_SRS_v2.0.pdf`](EduMentor_AI_SRS_v2.0.pdf) | 01 |
| [`decisions.md`](decisions.md) | 01 |
| [`requirements-traceability.md`](requirements-traceability.md) | 03 |
| [`api-endpoints.md`](api-endpoints.md), [`database-design.md`](database-design.md), [`structure.md`](structure.md), [`backend-rules.md`](backend-rules.md) | 02 (dùng chung cho các tính năng) |
| [`conventions.md`](conventions.md) | 04 |
| [`EduMentor_Database_Design_Da_Sua.docx`](EduMentor_Database_Design_Da_Sua.docx), [`EduMentor_Checklist_Da_Sua_API.xlsx`](EduMentor_Checklist_Da_Sua_API.xlsx) | 02 (nguồn gốc đã chép vào các file `.md`) |
| [`EduMentor_AI_Ke_Hoach_14_Tinh_Nang.xlsx`](EduMentor_AI_Ke_Hoach_14_Tinh_Nang.xlsx) | 04 (workbook — không phải nguồn quyết định) |
| [`ui-animation/`](ui-animation/) | 06 (báo cáo lịch sử) |

Ngoài `docs/`: [`../README.md`](../README.md), [`../SETUP.md`](../SETUP.md), [`../plans/plan.md`](../plans/plan.md).
