import { useEffect, useRef, useState } from 'react';
import { SendIcon } from '../../common/components/icons.jsx';
import styles from '../styles/TutorInputBar.module.css';

/**
 * Khung nhập câu hỏi và nút gửi tin nhắn của AI Tutor
 * @param {Object} props
 * @param {(message: string) => void} props.onSendMessage
 * @param {boolean} [props.isLoading=false]
 * @param {string} [props.placeholder]
 */
export default function TutorInputBar({
  onSendMessage,
  isLoading = false,
  placeholder = 'Hỏi về khái niệm, dán đoạn code cần sửa lỗi...',
}) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  // Tự động điều chỉnh chiều cao textarea theo nội dung
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 140);
    textarea.style.height = `${Math.max(newHeight, 24)}px`;
  }, [text]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    onSendMessage(trimmed);
    setText('');

    // Đưa height textarea về ban đầu
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form className={styles.inputContainer} onSubmit={handleSubmit}>
      <textarea
        ref={textareaRef}
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={isLoading}
        className={styles.textarea}
        aria-label="Nhập câu hỏi cho AI Tutor"
      />

      <button
        type="submit"
        disabled={isLoading || !text.trim()}
        className={styles.sendButton}
        title="Gửi câu hỏi (Enter)"
        aria-label="Gửi câu hỏi"
      >
        {isLoading ? (
          <span className={styles.spinner} aria-hidden="true" />
        ) : (
          <SendIcon size={18} />
        )}
      </button>
    </form>
  );
}
