// Hàm + hằng dùng chung cho các trang ôn tập (module 09 · Tuấn · GĐ4, 09/11/2026).

export const LEVEL_TEXT = {
  recognize: 'Trắc nghiệm · Nhận biết',
  understand: 'Trắc nghiệm · Thông hiểu',
  easy: 'Tự luận · Dễ',
  advanced: 'Tự luận · Nâng cao',
};

export const OPTION_LETTERS = ['A', 'B', 'C', 'D'];

// 15/11: mỗi ý chỉ Đạt / Chưa đạt. "Một phần" chỉ còn ở bài chấm trước 15/11 (lịch sử).
export const RUBRIC_RESULT = {
  full: { text: 'Đạt', chip: 'chip-ok' },
  partial: { text: 'Một phần', chip: 'chip-accent' },
  none: { text: 'Chưa đạt', chip: 'chip-danger' },
};

// B11: câu tự luận được chấm thế nào (backend: graded_by). keyword = AI_MODE=mock hoặc AI lỗi → chấm từ khóa dự phòng.
export const GRADED_BY = {
  ai: { text: 'Chấm bởi AI', chip: 'chip-info' },
  keyword: { text: 'Chấm tự động theo từ khóa', chip: 'chip' },
};

/**
 * B11: chia bài làm thành các đoạn để TÔ SÁNG câu trích làm bằng chứng của từng ý.
 * evidences: mảng câu trích theo thứ tự ý (null = ý đó không có). Trả [{ text, item }] — item = số thứ tự ý (1, 2…)
 * với đoạn tô sáng, null với đoạn thường. Tìm không phân biệt hoa thường; câu trích không tìm thấy nguyên văn
 * (AI sửa vài dấu câu — backend vẫn chấp nhận) thì bỏ qua, không tô; hai câu trích chồng nhau → giữ câu đứng trước.
 */
export function highlightSegments(text, evidences) {
  if (!text) return [];
  const lower = text.toLowerCase();
  const ranges = [];
  (evidences || []).forEach((ev, i) => {
    const needle = (ev || '').trim().toLowerCase();
    if (!needle) return;
    const start = lower.indexOf(needle);
    if (start >= 0) ranges.push({ start, end: start + needle.length, item: i + 1 });
  });
  ranges.sort((a, b) => a.start - b.start || a.item - b.item);
  const segments = [];
  let pos = 0;
  for (const r of ranges) {
    if (r.start < pos) continue; // chồng lên đoạn đã tô
    if (r.start > pos) segments.push({ text: text.slice(pos, r.start), item: null });
    segments.push({ text: text.slice(r.start, r.end), item: r.item });
    pos = r.end;
  }
  if (pos < text.length) segments.push({ text: text.slice(pos), item: null });
  return segments;
}

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
