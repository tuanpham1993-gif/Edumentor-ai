// Đáp án (trắc nghiệm) / barem + đáp án mẫu (tự luận) của một câu — module 09 (Tuấn · 16/11/2026 · 7.6).
import { OPTION_LETTERS, formatScore } from '../../review/reviewFormat.js';
import styles from '../styles/AdminReviewQuestions.module.css';

function Keywords({ main = [], sub = [] }) {
  if (!main.length && !sub.length) return null;
  return (
    <span className={styles.keywords}>
      {main.map((k) => (
        <span key={`m-${k}`} className={`chip chip-info ${styles.kw}`} title="Từ khóa chính">
          {k}
        </span>
      ))}
      {sub.map((k) => (
        <span key={`s-${k}`} className={`chip ${styles.kw}`} title="Từ khóa phụ">
          {k}
        </span>
      ))}
    </span>
  );
}

export default function QuestionDetail({ detail }) {
  if (detail.type === 'mcq') {
    return (
      <ul className={styles.options}>
        {(detail.options || []).map((option, i) => (
          <li key={OPTION_LETTERS[i]} className={i === detail.correct_index ? styles.correct : ''}>
            <span className={styles.letter}>{OPTION_LETTERS[i]}.</span> {option}
            {i === detail.correct_index && <span className={styles.tag}>Đáp án đúng</span>}
          </li>
        ))}
        {detail.explanation && <li className={styles.explain}>Giải thích: {detail.explanation}</li>}
      </ul>
    );
  }
  const rubric = detail.rubric || [];
  const total = rubric.reduce((sum, item) => sum + Number(item.max_points || 0), 0);
  return (
    <div className={styles.rubricBox}>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Ý</th>
              <th>Nội dung ý barem · từ khóa</th>
              <th>Điểm</th>
            </tr>
          </thead>
          <tbody>
            {rubric.map((item, i) => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td>
                  {item.text}
                  <Keywords main={item.main_keywords} sub={item.sub_keywords} />
                </td>
                <td>{formatScore(item.max_points)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className={`small ${total === 10 ? 'muted' : styles.warn}`}>
        Tổng điểm barem: {formatScore(total)}/10 · mỗi ý chấm Đạt (đủ điểm) hoặc Chưa đạt (0)
      </p>
      {detail.explanation && <p className={styles.explain}>Đáp án mẫu: {detail.explanation}</p>}
    </div>
  );
}
