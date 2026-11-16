import { useEffect, useRef } from 'react';
import TutorMessageItem from './TutorMessageItem.jsx';
import TutorBotIcon from './TutorBotIcon.jsx';
import styles from '../styles/TutorMessageList.module.css';

/**
 * Danh sách hiển thị các tin nhắn trong phiên chat
 * @param {Object} props
 * @param {Array<any>} props.messages
 * @param {boolean} [props.isLoading=false]
 * @param {(prompt: string) => void} props.onSelectPrompt
 */
export default function TutorMessageList({
  messages = [],
  isLoading = false,
  onSelectPrompt,
}) {
  const bottomRef = useRef(null);

  // Tự động cuộn xuống dưới cùng khi có tin nhắn mới hoặc trạng thái loading thay đổi
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className={styles.scrollArea}>
      <div className={styles.listContainer}>
        {messages.length === 0 && !isLoading ? (
          <div className={styles.emptyWelcome}>
            <TutorBotIcon size={52} />
            <h2 className={styles.welcomeTitle}>Chào bạn, mình là AI Tutor!</h2>
            <p className={styles.welcomeDesc}>
              Hãy hỏi bất kỳ kiến thức nào về Python, SQL, cấu trúc dữ liệu hoặc dán đoạn mã bạn cần sửa lỗi.
            </p>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isLatest = index === messages.length - 1;
            return (
              <TutorMessageItem
                key={msg.message_id || `msg-${index}`}
                message={msg}
                onSelectPrompt={onSelectPrompt}
                isLatestAssistant={isLatest && msg.role === 'assistant'}
              />
            );
          })
        )}

        {/* Trạng thái AI đang suy nghĩ / trả lời */}
        {isLoading && (
          <div className={styles.thinkingRow}>
            <TutorBotIcon size={28} />
            <div className={styles.thinkingBubble}>
              <span className={styles.dot} />
              <span className={styles.dot} />
              <span className={styles.dot} />
            </div>
          </div>
        )}

        <div ref={bottomRef} style={{ height: 1 }} />
      </div>
    </div>
  );
}
