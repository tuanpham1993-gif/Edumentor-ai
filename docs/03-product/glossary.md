# Thuật ngữ

Tài liệu dẫn xuất (D-DOC-06 (4)), **không phải nguồn định nghĩa**: mỗi dòng chỉ ghi định nghĩa ngắn hoặc trích phần cần thiết, kèm nguồn, mục và trạng thái nguồn. Khi khác nguồn, nguồn thắng. Thứ tự ưu tiên giữa các nguồn: D-DOC-01 ([`decisions.md`](../decisions.md) §1).

Trạng thái nguồn lấy từ sổ nguồn ([`decisions.md`](../decisions.md) §1):

| Viết tắt | File | Trạng thái |
|---|---|---|
| BA | [`EdumentorAi_BA.md`](../EdumentorAi_BA.md) | Chọn tạm |
| SRS v2.0 | [`EduMentor_AI_SRS_v2.0.docx`](../EduMentor_AI_SRS_v2.0.docx) | Bản gốc nhận về; chờ nhóm xác nhận các điểm Chương 13 |
| decisions | [`decisions.md`](../decisions.md) | Mã D-xx đã chốt; ND-xx là điểm chờ |

## Thuật ngữ

| Thuật ngữ | Định nghĩa ngắn hoặc trích | Nguồn, mục | Ghi chú |
|---|---|---|---|
| Học viên (User/Student) | SRS: "tài khoản role = student". BA: "người học sử dụng EduMentor AI để xác định mục tiêu nghề nghiệp, tạo lộ trình học tập cá nhân hóa…" | SRS v2.0 §1.4; BA §4.1.1 | BA gọi là "Người dùng (User)" |
| Khách | SRS: "người chưa đăng nhập" | SRS v2.0 §1.4, §4.1 | `SOURCE_CONFLICT`: BA §4.1 chỉ xác định hai vai trò, User và Admin, không có Khách. `NEEDS_OWNER_CONFIRMATION` |
| Quản trị viên (Admin) | SRS: "tài khoản role = admin, tạo bằng script, không đăng ký qua giao diện". BA: "chịu trách nhiệm quản lý dữ liệu nền và cấu hình…" | SRS v2.0 §1.4; BA §4.1.2 | — |
| AI Consultant | SRS: "AI tư vấn lộ trình, đề xuất đồ thị kỹ năng". BA: "phân tích mục tiêu học tập và trích xuất danh sách kỹ năng phù hợp" | SRS v2.0 §1.4; BA §8.1 | — |
| AI Tutor | SRS: "gia sư AI hội thoại nhiều lượt theo phiên". BA: "hỗ trợ giải thích kiến thức, giải đáp câu hỏi và gỡ lỗi lập trình" | SRS v2.0 §1.4; BA §8.1, §8.5 | — |
| Lộ trình (Learning Path) | SRS: "đồ thị kỹ năng của một học viên: node là kỹ năng, cạnh là quan hệ giữa kỹ năng" | SRS v2.0 §1.4; BA §8.3 "Personalized Learning Graph" | — |
| Mẫu lộ trình (Base Learning Path) | SRS: "lộ trình cơ sở do Admin quản lý, dùng làm điểm khởi đầu cho AI Consultant". BA: "các mẫu lộ trình có thể tái sử dụng…" | SRS v2.0 §1.4; BA §10.12 | BA còn gọi "lộ trình mẫu", "Learning Path Templates" (§5.2 UC-14, §8.3) |
| Skill Graph (đồ thị kỹ năng) | BA: "biểu diễn kỹ năng dưới dạng các nút (Nodes) và quan hệ giữa chúng dưới dạng các cạnh (Edges)"; loại cạnh: Prerequisite, Related Skill, Extension Skill | BA §8.3 | SRS v2.0 §1.4 không có mục riêng |
| Recommendation System | BA: "xếp hạng khóa học theo mức độ liên quan với kỹ năng và mục tiêu người dùng" | BA §8.1, §8.4 | SRS v2.0 §1.4 không có mục riêng |
| Bài ôn tập (Review) | SRS: "bài 20 câu trắc nghiệm theo khóa học". decisions: ôn tập theo khóa học (D01). BA: Skill Review "tạo hoặc truy xuất câu hỏi đánh giá kỹ năng bằng RAG" | SRS v2.0 §1.4; decisions D01; BA §8.1, §8.6 | `SOURCE_CONFLICT`: BA mô tả theo kỹ năng, dùng RAG; đề bài khác số câu — đang ghi ở ND-58, ND-81. Quyết định hiện hành D01 giữ hiệu lực (D-DOC-01) |
| MOOC | SRS: "nền tảng khóa học bên ngoài (Coursera, Udemy, edX…)" | SRS v2.0 §1.4; BA §4.2 | — |

## Đặc tả liên quan

Các đặc tả dùng thuật ngữ trên được liệt kê ở [`../modules/README.md`](../modules/README.md), kèm trạng thái của từng file (`SPEC CONFIRMED` hoặc `DRAFT`). Bảng thuật ngữ này không lấy định nghĩa từ đặc tả `DRAFT`.
