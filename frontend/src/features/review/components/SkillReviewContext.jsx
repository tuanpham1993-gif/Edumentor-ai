// Dữ liệu ôn tập cho cả đồ thị lộ trình (module 09 · Tuấn · 20/11/2026 — proposals/review-on-graph, bước 2).
// Gọi GET /me/review/skills MỘT lần cho mọi node, các <SkillReviewBadge> đọc chung — không gọi API theo từng node.
//
// Cách gắn (Hòa — trang chi tiết lộ trình):
//   <SkillReviewProvider skillIds={learningPath.nodes.map((n) => n.skill_id)}>
//     ...đồ thị...  // trong SkillNode: <SkillReviewBadge skillId={...} skillName={...} />
//   </SkillReviewProvider>
// Lỗi tải (mất mạng…) → không hiện huy hiệu, KHÔNG làm hỏng đồ thị.
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import * as reviewApi from '../../../api/review.api.js';

const SkillReviewContext = createContext(null);

export function SkillReviewProvider({ skillIds, children }) {
  const key = useMemo(() => [...new Set((skillIds ?? []).map(Number))].sort((a, b) => a - b).join(','), [skillIds]);
  const [bySkill, setBySkill] = useState({});
  const [version, setVersion] = useState(0);

  useEffect(() => {
    if (!key) return undefined;
    let active = true;
    reviewApi
      .getSkillReviews(key.split(','))
      .then((data) => {
        if (active) setBySkill(Object.fromEntries(data.items.map((item) => [item.skill_id, item.courses])));
      })
      .catch(() => {
        if (active) setBySkill({});
      });
    return () => {
      active = false;
    };
  }, [key, version]);

  const reload = useCallback(() => setVersion((v) => v + 1), []);
  const value = useMemo(() => ({ bySkill, reload }), [bySkill, reload]);
  return <SkillReviewContext.Provider value={value}>{children}</SkillReviewContext.Provider>;
}

/** Các khóa ôn tập được của một kỹ năng ([] = không có / chưa tải / ngoài Provider). */
export function useSkillReview(skillId) {
  const context = useContext(SkillReviewContext);
  return context?.bySkill[Number(skillId)] ?? [];
}
