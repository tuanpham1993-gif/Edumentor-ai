# Mẫu đề xuất: Ôn tập ngay trên đồ thị lộ trình

- **Nguồn:** artifact https://claude.ai/artifact/Gh2BYPBGAVYaznrk23316G (tải về 17/11/2026)
- **Dựa trên:** màn `PathDetail` trong bộ thiết kế (`../../ui-design/png/PathDetail.png`)
- **Thống nhất:** Tuấn + Hòa, 17/11/2026: làm ôn tập ngay trên đồ thị lộ trình
- **Thiết kế chức năng (bản đang theo):** [docs/guide.md](../../../guide.md)

| File | Nội dung |
|---|---|
| `ReviewOnGraph.png` | Ảnh chụp toàn trang để xem nhanh |
| `index.html` + `app.css` | Trang mẫu tương tác (mở bằng trình duyệt; bấm huy hiệu trên node để mở thẻ ôn tập) |

## Giữ theo mẫu
- Huy hiệu ôn tập (icon vòng tròn mũi tên quay lại) gắn trên node. **Không dùng dấu +**, vì trang đã có nút "+ Thêm kỹ năng / kết nối".
- Huy hiệu chỉ hiện ở node **Đã biết** và **Đang học**.
- Khung "Ôn tập <kỹ năng>" ở cột bên phải, có nút **Ôn tập ngay**.
- Màn kết quả có nút **← Quay lại lộ trình**. Đạt thì node đổi sang Đã biết (hiệu ứng tick).
- Tab **Ôn tập** trên thanh điều hướng vẫn giữ, là nơi xem toàn bộ lịch sử.

## Khác với guide.md (đã chốt 17/11: theo guide khi làm; "đến hạn ôn" để sau 25/11)
| Mẫu | guide.md (đã chốt sau mẫu) |
|---|---|
| Bấm huy hiệu → danh sách **các khóa học** có bài ôn tập cho kỹ năng; bài làm lưu **theo khóa học** | Bấm → kiểm tra **theo kỹ năng**: đề 15 câu của đúng kỹ năng đó; thiếu câu thì AI tự soạn |
| "Cần đạt **7/10**" | Đạt từ **6/10** (trắc nghiệm 60%, tự luận 40%) |
| API `GET /learning-paths/{id}/nodes/{skill_id}/reviews` | `POST /skills/{skill_id}/review-attempts?path={path_id}` |
| Chấm cam "**đến hạn ôn**" (ôn lại sau N ngày) | Chưa có trong kế hoạch, cần chốt (Q10 trong guide) |

## Phân công (chốt 20/11/2026 — Tuấn; đã nhắn Hòa)

Nguyên tắc: **mỗi người làm trong module của mình**. Tuấn làm thành phần ôn tập riêng; Hòa chỉ chèn vào trang lộ trình.

| # | Việc | Ai | Khi nào | Trạng thái |
|---|---|---|---|---|
| 1 | API `GET /api/me/review/skills?skill_ids=1,2,3`: mỗi kỹ năng → các khóa người học đã tham gia có dạy kỹ năng đó và đã có đề ôn tập, kèm lần làm gần nhất / bài đang làm dở | Tuấn | trước 25/11 | ✅ 20/11 |
| 2 | Thành phần `<SkillReviewProvider>` + `<SkillReviewBadge>` (huy hiệu trên node → bảng nhỏ "Ôn tập <kỹ năng>": các khóa, điểm lần trước, nút Ôn tập → `/courses/{id}/review`) | Tuấn | trước 25/11 | ✅ 20/11 |
| 2b | Nút **← Quay lại lộ trình** ở màn Bắt đầu ôn tập và màn Kết quả khi vào từ huy hiệu (nhớ lộ trình qua `reviewReturn.js`, sessionStorage; chỉ nhận đường dẫn `/me/my-learning-path/…`) | Tuấn | trước 25/11 | ✅ 20/11 |
| 3 | Màu node theo trạng thái từ `GET /api/me/skills` (Đã biết / Đang học / Chưa học / Mục tiêu / Mở rộng) + chú thích màu; sửa dấu ✓ (đang hiện cho kỹ năng mục tiêu); bỏ `passed_test → is_target`; đầu trang (tên, chip trạng thái, "x/y kỹ năng đã biết · tạo ngày", đường dẫn); nút Đổi tên / Từ bỏ; panel phải (vai trò, thêm bởi, Học trước / Mở ra); chữ tiếng Việt; dọn file thử nghiệm | Hòa | | chờ Hòa |
| 4 | Khóa học gợi ý theo kỹ năng: API `/recommendation` + thẻ khóa (Tham gia học / Lưu dùng API của Khôi) | Hòa (+ Khôi) | | chờ Hòa |
| 5 | Chèn `<SkillReviewProvider>` quanh đồ thị và `<SkillReviewBadge>` vào `SkillNode` (chỉ node Đã biết / Đang học) | Hòa chèn, Tuấn hỗ trợ | sau bước 2 + 3 | |
| 6 | `<SkillReviewCard>` "Ôn tập ngay" theo **kỹ năng** trong panel phải (guide G1–G6, Alembic) | Tuấn | sau 25/11 | |
| 7 | Chấm "Đến hạn ôn" | Tuấn | sau 25/11 (Q10) | |

Ngưỡng đạt dùng **6/10** của hệ thống (mẫu ghi 7/10 là bản cũ).

### Cách gắn huy hiệu (bước 5 — Hòa)

```jsx
// LearningPathDetailPage.jsx — bọc vùng đồ thị (gọi API 1 lần cho mọi node)
import { SkillReviewProvider } from '../../review/components/SkillReviewContext.jsx';

<SkillReviewProvider skillIds={learningPath.nodes.map((n) => n.skill_id)}>
  <LearningPathGraphForDetail ... />
</SkillReviewProvider>

// SkillNode.jsx — đặt ở góc trên node; chỉ node Đã biết / Đang học (theo mẫu)
import SkillReviewBadge from '../../review/components/SkillReviewBadge.jsx';

{(data.status === 'known' || data.status === 'learning') && (
  <SkillReviewBadge skillId={data.skillId} skillName={data.skillName} />
)}
```

- Huy hiệu tự ẩn khi kỹ năng chưa có khóa nào ôn được (chưa tham gia khóa, khóa chưa có đề).
- Bấm huy hiệu không chọn / kéo node; bảng nhỏ vẽ ở lớp trên cùng nên không bị node khác che.
- `data.status` là trạng thái kỹ năng của người học (bước 3, lấy từ `GET /api/me/skills`); tên trường tùy Hòa đặt.
