// Helper sinh Monogram (chữ viết tắt nghệ thuật) và bảng màu Cover cho thẻ khóa học.
// Khớp với thiết kế mẫu tại docs/EduMentor-UI-design/ui-design/html/Courses.html.

const PALETTES = [
  // Terracotta / Coral (ML, AI)
  {
    base: '#241615',
    ink: '#f4a58e',
    baseL: '#f8ddd5',
    inkL: '#b04d36',
  },
  // Deep Blue / Sky (Python, Cloud)
  {
    base: '#14202b',
    ink: '#7fb2e6',
    baseL: '#deeaf7',
    inkL: '#3a70a8',
  },
  // Amber / Warm Gold (Deep Learning, Advance)
  {
    base: '#2a1f10',
    ink: '#f5a524',
    baseL: '#fbe8c4',
    inkL: '#c27400',
  },
  // Olive / Sage (Database, SQL)
  {
    base: '#1b1f17',
    ink: '#c9d68a',
    baseL: '#e7eed3',
    inkL: '#6a7a24',
  },
  // Honey / Orange (Pandas, Data)
  {
    base: '#231a12',
    ink: '#ffb347',
    baseL: '#f8e0c6',
    inkL: '#c2680a',
  },
];

/**
 * Trích xuất 2 ký tự đại diện cho khóa học (vd: "Machine Learning" -> "ML", "Python" -> "Py")
 */
export function getCourseMonogram(title = '') {
  const clean = title.trim();
  const lower = clean.toLowerCase();

  if (lower.includes('machine learning')) return 'ML';
  if (lower.includes('deep learning')) return 'DL';
  if (lower.includes('python')) return 'Py';
  if (lower.includes('sql') || lower.includes('database')) return 'SQL';
  if (lower.includes('pandas')) return 'Pa';
  if (lower.includes('numpy')) return 'Nu';
  if (lower.includes('spark')) return 'Sp';
  if (lower.includes('tableau')) return 'TQ';
  if (lower.includes('excel')) return 'EN';
  if (lower.includes('google cloud') || lower.includes('cloud')) return 'GC';
  if (lower.includes('fastapi') || lower.includes('api')) return 'API';
  if (lower.includes('javascript') || lower.includes('react')) return 'JS';

  // Fallback: Lấy 2 ký tự đầu của 2 từ đầu, hoặc 2 ký tự đầu của từ đầu tiên
  const words = clean.split(/\s+/).filter(Boolean);
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase();
  }
  return clean.slice(0, 2).toUpperCase() || 'EM';
}

/**
 * Lấy bảng màu dựa trên mã hash của ID hoặc tên khóa học
 */
export function getCoursePalette(courseId, title = '') {
  const seed = (typeof courseId === 'number' ? courseId : 0) + title.length;
  return PALETTES[seed % PALETTES.length];
}
