import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth.js';
import * as tutorApi from '../../../api/tutor.api.js';
import TutorBotIcon from './TutorBotIcon.jsx';
import TutorMessageItem from './TutorMessageItem.jsx';
import ApiKeyModal from './ApiKeyModal.jsx';
import styles from '../styles/TutorFloatingWidget.module.css';

const DEFAULT_WELCOME_MESSAGE = {
  message_id: 'welcome-0',
  role: 'assistant',
  content: {
    answer:
      'Xin chào! Mình là **AI Tutor** của EduMentor. Bạn có câu hỏi nào về bài học, đoạn mã lỗi hay cần tư vấn lộ trình học không?',
    suggestions: [
      {
        label: 'Khái niệm List comprehension',
        prompt: 'Giải thích List comprehension trong Python giúp mình, kèm ví dụ.',
      },
      {
        label: 'Các khóa học HTML',
        prompt: 'Các khóa học có kỹ năng HTML trong hệ thống cho tôi xem đi.',
      },
      {
        label: 'Lộ trình Full Stack Web',
        prompt: 'Gợi ý cho tôi lộ trình các kỹ năng cần học để trở thành Lập trình viên Web Full Stack.',
      },
    ],
  },
  created_at: new Date().toISOString(),
};

/**
 * Floating Chatbot Widget (Icon góc dưới để chat với AI Tutor trên toàn bộ trang)
 */
export default function TutorFloatingWidget() {
  const location = useLocation();
  const navigate = useNavigate();
  const { status } = useAuth();
  const isAuthenticated = status === 'authenticated';

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([DEFAULT_WELCOME_MESSAGE]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isKeyModalOpen, setIsKeyModalOpen] = useState(false);
  const [hasCustomKey, setHasCustomKey] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    setHasCustomKey(Boolean(tutorApi.getStoredApiKey()));
  }, []);

  // Tự động cuộn xuống đáy khi có tin nhắn mới
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen, isLoading]);

  // Điều chỉnh chiều cao textarea tự động
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 100)}px`;
  }, [inputText]);

  // Gửi tin nhắn tới backend
  const handleSendMessage = async (rawText) => {
    const text = (rawText || inputText).trim();
    if (!text || isLoading) return;

    let sessionId = activeSessionId;

    // Nếu đã đăng nhập và chưa có session, tạo phiên mới
    if (isAuthenticated && !sessionId) {
      try {
        const title = text.length > 25 ? `${text.slice(0, 25)}...` : text;
        const newSession = await tutorApi.createChatSession(title);
        sessionId = newSession.session_id;
        setActiveSessionId(sessionId);
      } catch (err) {
        console.error('Không thể tạo phiên chat widget:', err);
      }
    }

    const tempUserMsg = {
      message_id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setInputText('');
    setIsLoading(true);

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      if (isAuthenticated && sessionId) {
        // Đã đăng nhập: gửi tin nhắn có lưu phiên
        const res = await tutorApi.sendChatMessage(sessionId, text);
        const assistantMsg = {
          message_id: `ai-${Date.now()}`,
          role: 'assistant',
          content: res.assistant_message,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } else {
        // Khách chưa đăng nhập: gọi public ask (không cần token hay session)
        const res = await tutorApi.askPublicTutor(text);
        const assistantMsg = {
          message_id: `ai-${Date.now()}`,
          role: 'assistant',
          content: res.assistant_message,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      }
    } catch (err) {
      console.error('Lỗi khi gửi tin nhắn trong widget:', err);
      const errorMsg = {
        message_id: `err-${Date.now()}`,
        role: 'assistant',
        content: {
          answer: 'Xin lỗi bạn, kết nối tới AI Tutor bị gián đoạn. Vui lòng thử lại sau giây lát!',
          suggestions: [],
        },
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleExpandToFullPage = () => {
    setIsOpen(false);
    if (isAuthenticated) {
      navigate('/tutor');
    } else {
      // Khách bấm mở rộng -> chuyển sang đăng nhập để có trải nghiệm toàn màn hình và lưu lịch sử
      navigate('/login');
    }
  };

  // Khi đang ở chính trang /tutor toàn màn hình thì ẩn widget nổi này để tránh trùng lặp
  if (location.pathname === '/tutor') {
    return null;
  }

  return (
    <>
      {/* 1. Nút Icon Chatbot tròn nổi ở góc dưới */}
      <button
        type="button"
        className={`${styles.floatingButton} ${isOpen ? styles.buttonActive : ''}`}
        onClick={() => setIsOpen((prev) => !prev)}
        title={isOpen ? 'Thu nhỏ AI Tutor' : 'Trò chuyện với AI Tutor'}
        aria-label="Mở trợ lý học tập AI Tutor"
      >
        <div className={styles.pulseRing} />
        <TutorBotIcon size={32} />
        {!isOpen && <span className={styles.onlineBadge} />}
      </button>

      {/* 2. Cửa sổ chat nhỏ bật lên khi bấm icon */}
      {isOpen && (
        <aside className={styles.chatWindow} aria-label="Cửa sổ AI Tutor">
          {/* Header của Widget */}
          <div className={styles.widgetHeader}>
            <div className={styles.headerTitleGroup}>
              <TutorBotIcon size={26} />
              <div className={styles.headerText}>
                <div className={styles.widgetTitle}>EduMentor AI Tutor</div>
                <div className={styles.widgetStatus}>
                  <span className={styles.statusDot} />
                  <span>Đang trực tuyến</span>
                </div>
              </div>
            </div>

            <div className={styles.headerActions}>
              {/* Nút cài đặt API Key cá nhân */}
              <button
                type="button"
                className={styles.headerBtn}
                onClick={() => setIsKeyModalOpen(true)}
                title={
                  hasCustomKey
                    ? 'API Key cá nhân đang kích hoạt (Bấm để đổi/xóa)'
                    : 'Nhập Gemini API Key của bạn'
                }
                aria-label="Cài đặt API Key cá nhân"
                style={hasCustomKey ? { color: '#4ade80' } : {}}
              >
                <span style={{ fontSize: '13px' }}>🔑</span>
              </button>

              {/* Nút phóng to toàn màn hình */}
              <button
                type="button"
                className={styles.headerBtn}
                onClick={handleExpandToFullPage}
                title={
                  isAuthenticated
                    ? 'Mở toàn màn hình trang AI Tutor'
                    : 'Đăng nhập để mở toàn màn hình & lưu lịch sử'
                }
                aria-label="Mở toàn màn hình"
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />
                </svg>
              </button>

              {/* Nút đóng/thu nhỏ */}
              <button
                type="button"
                className={styles.headerBtn}
                onClick={() => setIsOpen(false)}
                title="Thu nhỏ"
                aria-label="Đóng cửa sổ"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Banner nhắc đăng nhập nếu là khách */}
          {!isAuthenticated && (
            <div className={styles.guestBanner}>
              <span>Bạn đang chat với tư cách Khách. </span>
              <Link to="/login" className={styles.loginLink} onClick={() => setIsOpen(false)}>
                Đăng nhập
              </Link>
              <span> để lưu phiên học.</span>
            </div>
          )}

          {/* Danh sách tin nhắn cuộn */}
          <div className={styles.messageScrollArea}>
            {messages.map((msg) => (
              <TutorMessageItem
                key={msg.message_id}
                message={msg}
                onSelectPrompt={(prompt) => handleSendMessage(prompt)}
                isLoading={isLoading}
              />
            ))}

            {/* Hiệu ứng đang suy nghĩ */}
            {isLoading && (
              <div className={styles.thinkingBubble}>
                <TutorBotIcon size={20} />
                <div className={styles.typingIndicator}>
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Khung nhập tin nhắn */}
          <form
            className={styles.widgetInputArea}
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
          >
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Nhập câu hỏi cho AI Tutor..."
              disabled={isLoading}
              className={styles.widgetTextarea}
            />

            <button
              type="submit"
              disabled={!inputText.trim() || isLoading}
              className={styles.widgetSendBtn}
              title="Gửi tin nhắn"
              aria-label="Gửi"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
              </svg>
            </button>
          </form>
        </aside>
      )}

      <ApiKeyModal
        isOpen={isKeyModalOpen}
        onClose={() => setIsKeyModalOpen(false)}
        onKeyChanged={(hasKey) => setHasCustomKey(hasKey)}
      />
    </>
  );
}
