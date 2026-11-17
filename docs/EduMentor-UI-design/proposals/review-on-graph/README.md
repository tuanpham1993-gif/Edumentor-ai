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
