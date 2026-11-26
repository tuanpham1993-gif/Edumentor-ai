// Huy hiệu ôn tập trên node đồ thị lộ trình (module 09 · Tuấn · 20/11/2026 — proposals/review-on-graph, bước 2).
// Kỹ năng có khóa ôn tập được (đã tham gia, đủ đề) → icon vòng tròn mũi tên; bấm → bảng nhỏ "Ôn tập <kỹ năng>":
// từng khóa, điểm lần trước / "Chưa ôn" / "Đang làm dở", nút Ôn tập (→ màn Bắt đầu) hoặc Tiếp tục (→ bài đang làm).
// Không có khóa nào → không vẽ gì. Theo mẫu: chỉ gắn vào node Đã biết / Đang học (Hòa quyết ở SkillNode).
// G2 (22/11): thêm dòng đầu "Ôn riêng kỹ năng này" (15 câu của chính kỹ năng, không cần tham gia khóa) khi kỹ năng
// đủ đề / có bài dở / đã từng ôn → /skills/:id/review?path=<lộ trình đang xem>. Huy hiệu hiện khi có khóa HOẶC có dòng này.
//
// Nằm trong node React Flow:
//   - class "nodrag nopan" + chặn lan sự kiện → bấm huy hiệu không chọn / kéo node.
//   - Bảng nhỏ vẽ qua portal ra <body> (position: fixed) → không bị node bên cạnh che (mỗi node là một lớp riêng).
//     Cuộn / thu phóng / đổi cỡ cửa sổ → đóng bảng (vị trí cũ không còn đúng).
import { useCallback, useEffect, useId, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Link, useLocation } from 'react-router-dom';

import { formatDate, timeAgo } from '../../../utils/formatters.js';
import { formatScore } from '../reviewFormat.js';
import { attemptKey, courseKey, saveReturn, skillKey } from '../reviewReturn.js';
import styles from '../styles/SkillReview.module.css';
import { useSkillDirect, useSkillDue, useSkillReview } from './SkillReviewContext.jsx';

const POP_WIDTH = 280;
const GUTTER = 16;

function ReviewIcon() {
  return (
    <svg
      aria-hidden="true"
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 12a9 9 0 1 0 3-6.7" />
      <path d="M3 4v5h5" />
      <path d="M12 8v4l3 2" />
    </svg>
  );
}

function statusText(course) {
  if (course.in_progress_attempt_id) return 'Đang làm dở';
  const last = course.last_attempt;
  if (!last) return 'Chưa ôn';
  if (last.status === 'grading') return 'Đang chấm…';
  return `${formatScore(last.score)}/10 · ${timeAgo(last.submitted_at ?? last.started_at)}`;
}

// 21/11 (Q12): dòng "đến hạn ôn" — lần ôn gần nhất của KỸ NĂNG (qua bất kỳ khóa nào) + hạn ôn lại.
function dueText(due) {
  const last = `Ôn gần nhất ${due.last_passed ? 'đạt' : 'chưa đạt'} ${formatScore(due.last_score)}/10 · ${timeAgo(due.last_reviewed_at)}`;
  return due.due ? `${last} · đến hạn ôn` : `${last} · ôn lại từ ${formatDate(due.due_at)}`;
}

const PATH_ID = /\/details\/(\d+)/; // /me/my-learning-path/details/:recordId → lộ trình đang xem

export default function SkillReviewBadge({ skillId, skillName }) {
  const courses = useSkillReview(skillId);
  const direct = useSkillDirect(skillId);
  // G3d (25/11): kỹ năng chưa đủ câu nhưng AI soạn được (can_generate) cũng hiện dòng ôn riêng
  const showDirect = Boolean(
    direct && (direct.ready || direct.can_generate || direct.in_progress_attempt_id || direct.last_attempt),
  );
  const due = useSkillDue(skillId);
  const isDue = Boolean(due?.due);
  const { pathname } = useLocation();
  const [pos, setPos] = useState(null); // null = đóng; { top, left } = đang mở
  const badgeRef = useRef(null);
  const popRef = useRef(null);
  const titleId = useId();
  const close = useCallback(() => setPos(null), []);

  function toggle() {
    if (pos) return close();
    const rect = badgeRef.current.getBoundingClientRect();
    const left = Math.min(
      Math.max(rect.left + rect.width / 2 - POP_WIDTH / 2, GUTTER),
      window.innerWidth - POP_WIDTH - GUTTER,
    );
    return setPos({ top: rect.bottom + 8, left });
  }

  useEffect(() => {
    if (!pos) return undefined;
    const onKey = (event) => event.key === 'Escape' && close();
    const onDown = (event) => {
      const inside = [badgeRef.current, popRef.current].some((el) => el && el.contains(event.target));
      if (!inside) close();
    };
    document.addEventListener('keydown', onKey);
    document.addEventListener('mousedown', onDown);
    window.addEventListener('wheel', close, { passive: true });
    window.addEventListener('resize', close);
    window.addEventListener('scroll', close, true);
    return () => {
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('mousedown', onDown);
      window.removeEventListener('wheel', close);
      window.removeEventListener('resize', close);
      window.removeEventListener('scroll', close, true);
    };
  }, [pos, close]);

  if (courses.length === 0 && !showDirect) return null;
  const pathId = PATH_ID.exec(pathname)?.[1];
  const stop = (event) => event.stopPropagation(); // không để React Flow chọn / kéo node

  return (
    <span className={`${styles.wrap} nodrag nopan`} onClick={stop} onMouseDown={stop} onPointerDown={stop}>
      <button
        ref={badgeRef}
        type="button"
        className={`${styles.badge} ${isDue ? styles.badgeDue : ''}`}
        aria-label={isDue ? `Ôn tập ${skillName} — đến hạn ôn` : `Ôn tập ${skillName}`}
        aria-expanded={Boolean(pos)}
        aria-haspopup="dialog"
        onClick={toggle}
      >
        <ReviewIcon />
        {isDue && <span className={styles.dueDot} aria-hidden="true" />}
      </button>

      {pos &&
        createPortal(
          <div
            ref={popRef}
            className={styles.pop}
            style={{ top: pos.top, left: pos.left, width: POP_WIDTH }}
            role="dialog"
            aria-labelledby={titleId}
          >
            <div className={styles.popHead}>
              <strong id={titleId}>Ôn tập {skillName}</strong>
              <button type="button" className={styles.close} aria-label="Đóng" onClick={close}>
                ×
              </button>
            </div>
            {due && <p className={isDue ? styles.dueLine : styles.popSub}>{dueText(due)}</p>}
            <ul className={styles.list}>
              {showDirect && (
                <li className={styles.row}>
                  <span className={styles.rowText}>
                    <span className={styles.course}>Ôn riêng kỹ năng này</span>
                    <span className={styles.meta}>
                      {statusText(direct)} · 15 câu, không cần tham gia khóa
                      {!direct.ready && !direct.in_progress_attempt_id ? ' · AI soạn đề khi bạn bấm ôn' : ''}
                    </span>
                  </span>
                  <Link
                    to={
                      direct.in_progress_attempt_id
                        ? `/review/${direct.in_progress_attempt_id}`
                        : `/skills/${skillId}/review${pathId ? `?path=${pathId}` : ''}`
                    }
                    className="btn btn-sm btn-primary"
                    onClick={() => {
                      saveReturn(skillKey(skillId), pathname);
                      if (direct.in_progress_attempt_id) saveReturn(attemptKey(direct.in_progress_attempt_id), pathname);
                      close();
                    }}
                  >
                    {direct.in_progress_attempt_id ? 'Tiếp tục' : 'Ôn tập'}
                  </Link>
                </li>
              )}
            </ul>
            {courses.length > 0 && (
              <p className={styles.popSub}>{courses.length} khóa học có bài ôn tập cho kỹ năng này</p>
            )}
            <ul className={styles.list}>
              {courses.map((c) => (
                <li key={c.course_id} className={styles.row}>
                  <span className={styles.rowText}>
                    <span className={styles.course}>{c.course_title}</span>
                    <span className={styles.meta}>{statusText(c)}</span>
                  </span>
                  <Link
                    to={
                      c.in_progress_attempt_id
                        ? `/review/${c.in_progress_attempt_id}`
                        : `/courses/${c.course_id}/review`
                    }
                    className="btn btn-sm btn-primary"
                    onClick={() => {
                      // nhớ lộ trình đang xem → màn Kết quả có nút "← Quay lại lộ trình"
                      saveReturn(courseKey(c.course_id), pathname);
                      if (c.in_progress_attempt_id) saveReturn(attemptKey(c.in_progress_attempt_id), pathname);
                      close();
                    }}
                  >
                    {c.in_progress_attempt_id ? 'Tiếp tục' : 'Ôn tập'}
                  </Link>
                </li>
              ))}
            </ul>
          </div>,
          document.body,
        )}
    </span>
  );
}
