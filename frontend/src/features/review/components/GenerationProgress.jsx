// Màn "Đang soạn đề…" khi kỹ năng chưa đủ câu và AI soạn đề ở nền (module 09 · Tuấn · G3d-2, 25/11/2026).
// Docs: docs/Review-AI-Tu-Soan-On-Tap.md mục 7.5. Không có chuông báo khi xong (D28): ở lại trang thì đề tự mở,
// rời trang thì quay lại bấm ôn là có đề.
import styles from '../styles/ReviewStartPage.module.css';

const STEPS = ['Chuẩn bị tài liệu', 'Soạn câu trắc nghiệm', 'Soạn câu tự luận', 'Kiểm tra đủ đề'];

export default function GenerationProgress({ generation, onRetry, retrying }) {
  if (generation.status === 'failed') {
    return (
      <div className={styles.generation} role="alert">
        <strong>Chưa soạn xong đề</strong>
        <p className="muted small">{generation.error || 'Bạn thử lại sau ít phút.'}</p>
        {generation.saved > 0 && (
          <p className="muted small">AI đã soạn được {generation.saved} câu — lần thử lại chỉ soạn phần còn thiếu.</p>
        )}
        <div>
          <button type="button" className="btn btn-primary" onClick={onRetry} disabled={retrying}>
            {retrying ? 'Đang gửi…' : 'Thử lại'}
          </button>
        </div>
      </div>
    );
  }

  const current = Math.max(1, generation.step || 1);
  const percent = generation.status === 'done' ? 100 : Math.round(((current - 1) / generation.steps) * 100) + 10;
  return (
    <div className={styles.generation} role="status" aria-live="polite">
      <strong>
        {generation.status === 'done' ? 'Đã soạn xong — đang mở đề…' : `AI đang soạn đề mới… (bước ${current}/${generation.steps})`}
      </strong>
      <div className={styles.progress} aria-hidden="true">
        <span style={{ width: `${percent}%` }} />
      </div>
      <ol className={styles.genSteps}>
        {STEPS.map((text, i) => {
          const step = i + 1;
          const state = generation.status === 'done' || step < current ? 'done' : step === current ? 'now' : 'todo';
          return (
            <li key={text} data-state={state}>
              {state === 'done' ? '✓' : state === 'now' ? '…' : '·'} {text}
            </li>
          );
        })}
      </ol>
      <p className="muted small">
        Thường mất khoảng 1 phút. Bạn có thể rời trang — quay lại bấm ôn kỹ năng này là có đề.
      </p>
    </div>
  );
}
