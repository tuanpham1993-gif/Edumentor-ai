// Hàm + hằng dùng chung cho các trang ôn tập (module 09 · Tuấn · GĐ4, 09/11/2026).

export const LEVEL_TEXT = {
  recognize: 'Trắc nghiệm · Nhận biết',
  understand: 'Trắc nghiệm · Thông hiểu',
  easy: 'Tự luận · Dễ',
  advanced: 'Tự luận · Nâng cao',
};

export const OPTION_LETTERS = ['A', 'B', 'C', 'D'];

export const RUBRIC_RESULT = {
  full: { text: 'Đạt', chip: 'chip-ok' },
  partial: { text: 'Một phần', chip: 'chip-accent' },
  none: { text: 'Chưa có', chip: 'chip-danger' },
};

// Khóa đã có ngân hàng câu hỏi ở giai đoạn 1 (chốt 09/11: khóa demo 312).
// TODO: khi trang "Khóa học của tôi" (Tâm) có nút Ôn tập dẫn tới /courses/:id/review thì bỏ danh sách này.
export const DEMO_COURSES = [{ courseId: 312, title: 'Python Basics: Selection and Iteration' }];

/** 7.7 → "7,7" ; 10 → "10" (dấu phẩy thập phân kiểu Việt Nam). */
export function formatScore(value) {
  if (value === null || value === undefined) return '—';
  return Number(value).toLocaleString('vi-VN', { maximumFractionDigits: 2 });
}

export function isAnswered(question) {
  return question.type === 'mcq'
    ? question.selected_index !== null && question.selected_index !== undefined
    : Boolean(question.text_answer && question.text_answer.trim());
}
