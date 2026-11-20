// 20/11 (Tuấn, Hòa nhờ — mục 9 tiếng Việt): nhãn hiển thị cho vai trò node / loại quan hệ.
// Giá trị gửi backend giữ nguyên tiếng Anh (prerequisite | related | extension), chỉ đổi chữ trên màn hình.
export const ROLE_LABELS = {
  prerequisite: 'Tiên quyết',
  related: 'Liên quan',
  extension: 'Mở rộng',
};

export function roleLabel(value) {
  return ROLE_LABELS[value] ?? value ?? 'Kỹ năng';
}
