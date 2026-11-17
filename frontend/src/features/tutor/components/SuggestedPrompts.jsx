import styles from '../styles/SuggestedPrompts.module.css';

/**
 * Hiển thị danh sách các Suggested Prompts (Gợi ý câu hỏi thông minh)
 * @param {Object} props
 * @param {Array<{label: string, prompt: string}>} props.suggestions
 * @param {(prompt: string) => void} props.onSelectPrompt
 * @param {boolean} [props.disabled=false]
 */
export default function SuggestedPrompts({ suggestions = [], onSelectPrompt, disabled = false }) {
  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div className={styles.container} aria-label="Gợi ý câu hỏi tiếp theo">
      <div className={styles.labelWrapper}>
        <span className={styles.sparkleIcon}>✨</span>
        <span className={styles.label}>Gợi ý cho bạn:</span>
      </div>
      <div className={styles.chipsList}>
        {suggestions.map((item, index) => {
          const label = item.label || item.prompt;
          const prompt = item.prompt || item.label;

          return (
            <button
              key={`${index}-${label}`}
              type="button"
              className={styles.chip}
              onClick={() => onSelectPrompt(prompt)}
              disabled={disabled}
              title={prompt}
            >
              <span className={styles.chipText}>{label}</span>
              <span className={styles.chipArrow} aria-hidden="true">→</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
