// Một câu trong trang Kết quả (module 09 · Tuấn · GĐ4) — màn demo ReviewDetail(-Explanation).
//   Trắc nghiệm: 4 lựa chọn, đánh dấu "Bạn chọn" / "Đáp án đúng", giải thích ẩn / hiện.
//   Tự luận: bài làm, bảng chấm từng ý (Đạt / Chưa đạt + điểm + câu trích làm bằng chứng), đáp án mẫu.
//   B11 (16/11): câu trích TÔ SÁNG ngay trong bài làm (đánh số theo ý), lý do từng ý, nhận xét chung,
//   nhãn "Chấm bởi AI" / "Chấm tự động theo từ khóa", "Đang xem lại" (điểm tính tạm).
import { GRADED_BY, LEVEL_TEXT, OPTION_LETTERS, RUBRIC_RESULT, formatScore, highlightSegments } from '../reviewFormat.js';
import styles from '../styles/ResultQuestion.module.css';

function AnswerWithEvidence({ text, rubric }) {
  if (!text) return <blockquote className={styles.answer}>Bạn đã bỏ trống câu này.</blockquote>;
  const segments = highlightSegments(text, rubric.map((r) => (r.result === 'full' ? r.evidence : null)));
  return (
    <blockquote className={styles.answer}>
      {segments.map((s, i) =>
        s.item ? (
          <mark key={i} className={styles.mark} title={`Bằng chứng cho ý ${s.item}`}>
            {s.text}
            <sup className={styles.markNo}>{s.item}</sup>
          </mark>
        ) : (
          <span key={i}>{s.text}</span>
        ),
      )}
    </blockquote>
  );
}

function verdict(q) {
  if (q.type === 'mcq') {
    if (q.selected_index === null) return { text: 'Bỏ trống', chip: 'chip' };
    return q.is_correct ? { text: 'Đúng', chip: 'chip-ok' } : { text: 'Sai', chip: 'chip-danger' };
  }
  if (!q.text_answer) return { text: 'Bỏ trống', chip: 'chip' };
  const chip = q.points >= q.max_points ? 'chip-ok' : q.points > 0 ? 'chip-accent' : 'chip-danger';
  return { text: `${formatScore(q.points)}/${formatScore(q.max_points)} điểm`, chip };
}

export default function ResultQuestion({ question: q, showExplanation, onToggle }) {
  const v = verdict(q);
  const gradedBy = q.graded_by ? GRADED_BY[q.graded_by] : null;
  return (
    <article className={`card ${styles.card}`} id={`cau-${q.position}`}>
      <header className={styles.head}>
        <span className="muted small">
          Câu {q.position} · {q.skill} · {LEVEL_TEXT[q.level]}
        </span>
        <span className={styles.badges}>
          {gradedBy && <span className={`chip ${gradedBy.chip}`}>{gradedBy.text}</span>}
          {q.needs_review && <span className="chip chip-accent">Đang xem lại</span>}
          {q.reviewed && <span className="chip chip-ok">Giáo viên đã xem lại</span>}
          <span className={`chip ${v.chip}`}>{v.text}</span>
        </span>
      </header>
      {q.needs_review && (
        <p className={styles.reviewNote} role="note">
          Điểm câu này đang được xem lại. Kết quả hiện tại là điểm tạm tính.
        </p>
      )}
      <h3 className={styles.content}>{q.content}</h3>

      {q.type === 'mcq' ? (
        <ul className={styles.options}>
          {q.options.map((option, i) => {
            const picked = q.selected_index === i;
            const correct = q.correct_index === i;
            const cls = correct ? styles.correct : picked ? styles.wrong : '';
            return (
              <li key={OPTION_LETTERS[i]} className={`${styles.option} ${cls}`}>
                <span className={styles.letter}>{OPTION_LETTERS[i]}.</span>
                <span className={styles.text}>{option}</span>
                {(picked || correct) && (
                  <span className={styles.tag}>
                    {picked && correct ? 'Bạn chọn · Đáp án đúng' : picked ? 'Bạn chọn' : 'Đáp án đúng'}
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      ) : (
        <div className={styles.essay}>
          <p className="muted small">
            Bài làm của bạn
            {q.rubric.some((r) => r.result === 'full' && r.evidence) && ' — phần tô màu là căn cứ chấm (số = ý)'}
          </p>
          <AnswerWithEvidence text={q.text_answer} rubric={q.rubric} />
          {q.feedback && (
            <div className={styles.feedback}>
              <p className={styles.feedbackTitle}>Nhận xét</p>
              <p className={styles.feedbackText}>{q.feedback}</p>
            </div>
          )}
          <div className="table-wrap">
            <table className={`table ${styles.rubric}`}>
              <thead>
                <tr>
                  <th>Ý cần có</th>
                  <th>Kết quả</th>
                  <th>Điểm</th>
                  <th>Lý do · bằng chứng</th>
                </tr>
              </thead>
              <tbody>
                {q.rubric.map((item, i) => (
                  <tr key={item.text}>
                    <td>
                      <span className={styles.itemNo}>{i + 1}.</span> {item.text}
                    </td>
                    <td>
                      <span className={`chip ${RUBRIC_RESULT[item.result].chip}`}>
                        {RUBRIC_RESULT[item.result].text}
                      </span>
                    </td>
                    <td className={styles.points}>
                      {formatScore(item.points)}/{formatScore(item.max_points)}
                    </td>
                    <td>
                      <div className={styles.why}>
                        {item.reason && <span className={styles.reason}>{item.reason}</span>}
                        {item.evidence && <span className={styles.evidence}>“{item.evidence}”</span>}
                        {!item.reason && !item.evidence && '—'}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="muted small">
            Điểm câu = tổng điểm các ý (thang 10) quy về {formatScore(q.max_points)} điểm.
          </p>
        </div>
      )}

      {q.explanation && (
        <div className={styles.explain}>
          <button type="button" className={styles.toggle} aria-expanded={showExplanation} onClick={onToggle}>
            {showExplanation ? 'Ẩn giải thích ▴' : q.type === 'mcq' ? 'Xem giải thích ▾' : 'Xem đáp án mẫu ▾'}
          </button>
          {showExplanation && <p className={styles.explainText}>{q.explanation}</p>}
        </div>
      )}
    </article>
  );
}
