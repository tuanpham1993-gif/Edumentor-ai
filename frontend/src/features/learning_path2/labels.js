// Display labels for AI learning path v2. Values sent to the backend stay in English.

export const CAREER_LEVEL_LABELS = {
  beginner: 'Mới bắt đầu',
  intern: 'Thực tập sinh',
  fresher: 'Fresher',
  junior: 'Junior',
  middle: 'Middle',
  senior: 'Senior',
  lead: 'Lead',
  architect: 'Architect',
  manager: 'Quản lý',
  career_switcher: 'Chuyển ngành',
  student: 'Sinh viên',
};

export const PROFICIENCY_LABELS = {
  basic: 'Cơ bản',
  beginner: 'Mới học',
  intermediate: 'Trung cấp',
  advanced: 'Nâng cao',
  expert: 'Chuyên gia',
};

// Node state from the backend graph (learning_graph.py)
export const STATE_META = {
  known: { label: 'Đã biết', hint: 'Bạn đã có kỹ năng này' },
  satisfied: { label: 'Đã đủ nền', hint: 'Suy ra từ kỹ năng bạn đã biết' },
  learning: { label: 'Đang học', hint: 'Đang học trong hồ sơ của bạn' },
  eligible: { label: 'Học ngay', hint: 'Đã đủ kỹ năng tiên quyết, có thể học ngay' },
  locked: { label: 'Chưa mở', hint: 'Cần học kỹ năng tiên quyết trước' },
};

export const EVIDENCE_LABELS = {
  explicitly_reported: 'Bạn nêu trong mô tả',
  user_provided_structured: 'Bạn nhập trong biểu mẫu',
  inferred_from_context: 'Suy ra từ ngữ cảnh',
};

export const PERIOD_LABELS = { per_day: '/ ngày', per_week: '/ tuần' };
export const UNIT_LABELS = { hours: 'giờ', minutes: 'phút' };
export const DURATION_UNIT_LABELS = { days: 'ngày', weeks: 'tuần', months: 'tháng', years: 'năm' };

export const label = (map, value, fallback = '—') => (value == null ? fallback : map[value] ?? value);
