// Một câu trong trang Kết quả (module 09 · Tuấn · GĐ4) — màn demo ReviewDetail(-Explanation).
//   Trắc nghiệm: 4 lựa chọn, đánh dấu "Bạn chọn" / "Đáp án đúng", giải thích ẩn / hiện.
//   Tự luận: bài làm, bảng chấm từng ý (Đạt / Một phần / Chưa có + điểm + câu trích làm bằng chứng), đáp án mẫu.
import { LEVEL_TEXT, OPTION_LETTERS, RUBRIC_RESULT, formatScore } from '../reviewFormat.js';
import styles from '../styles/ResultQuestion.module.css';

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
  return (
    <article className={`card ${styles.card}`} id={`cau-${q.position}`}>
      <header className={styles.head}>
        <span className="muted small">
          Câu {q.position} · {q.skill} · {LEVEL_TEXT[q.level]}
        </span>
        <span className={`chip ${v.chip}`}>{v.text}</span>
      </header>
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
          <p className="muted small">Bài làm của bạn</p>
          <blockquote className={styles.answer}>{q.text_answer || 'Bạn đã bỏ trống câu này.'}</blockquote>
          <div className="table-wrap">
            <table className={`table ${styles.rubric}`}>
              <thead>
                <tr>
                  <th>Ý cần có</th>
                  <th>Kết quả</th>
                  <th>Điểm</th>
                  <th>Bằng chứng trong bài làm</th>
                </tr>
              </thead>
              <tbody>
                {q.rubric.map((item) => (
                  <tr key={item.text}>
                    <td>{item.text}</td>
                    <td>
                      <span className={`chip ${RUBRIC_RESULT[item.result].chip}`}>
                        {RUBRIC_RESULT[item.result].text}
                      </span>
                    </td>
                    <td className={styles.points}>
                      {formatScore(item.points)}/{formatScore(item.max_points)}
                    </td>
                    <td className={styles.evidence}>{item.evidence ? `“${item.evidence}”` : '—'}</td>
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
