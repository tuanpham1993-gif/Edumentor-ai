// Nhãn + bộ lọc trang quản trị câu hỏi ôn tập — module 09 (Tuấn · 16/11/2026 · 7.6).

// Trạng thái hiển thị của một câu = review_status + is_active
//   pending → Chờ duyệt (luôn tắt) · rejected → Từ chối (luôn tắt) · approved → Đang bật / Đã tắt
export function questionStatus(item) {
  if (item.review_status === 'pending') return { key: 'pending', text: 'Chờ duyệt', chip: 'chip-accent' };
  if (item.review_status === 'rejected') return { key: 'rejected', text: 'Từ chối', chip: 'chip-danger' };
  return item.is_active
    ? { key: 'active', text: 'Đang bật', chip: 'chip-ok' }
    : { key: 'disabled', text: 'Đã tắt', chip: '' };
}

// Bộ lọc "Trạng thái" → tham số GET /admin/review/questions
export const STATUS_FILTERS = [
  { value: '', text: 'Tất cả', params: {} },
  { value: 'pending', text: 'Chờ duyệt', params: { review_status: 'pending' } },
  { value: 'active', text: 'Đang bật', params: { is_active: true } },
  { value: 'disabled', text: 'Đã tắt', params: { review_status: 'approved', is_active: false } },
  { value: 'rejected', text: 'Từ chối', params: { review_status: 'rejected' } },
];

export const TYPE_FILTERS = [
  { value: '', text: 'Mọi loại' },
  { value: 'mcq', text: 'Trắc nghiệm' },
  { value: 'essay', text: 'Tự luận' },
];

export const LEVEL_FILTERS = [
  { value: '', text: 'Mọi mức' },
  { value: 'recognize', text: 'Nhận biết' },
  { value: 'understand', text: 'Thông hiểu' },
  { value: 'easy', text: 'Dễ' },
  { value: 'advanced', text: 'Nâng cao' },
];

export const SOURCE_TEXT = { bank: 'Ngân hàng', ai: 'AI soạn' };

// Cột mức trong bảng sẵn sàng theo kỹ năng (cùng thứ tự khung đề 6 NB + 6 TH + 2 TL dễ + 1 TL nâng cao)
export const READINESS_LEVELS = [
  { key: 'recognize', text: 'TN nhận biết' },
  { key: 'understand', text: 'TN thông hiểu' },
  { key: 'easy', text: 'TL dễ' },
  { key: 'advanced', text: 'TL nâng cao' },
];
