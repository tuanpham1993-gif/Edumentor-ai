import { useCallback, useEffect, useState } from 'react';
import * as tutorApi from '../../../api/tutor.api.js';
import TutorSidebar from '../components/TutorSidebar.jsx';
import TutorHeader from '../components/TutorHeader.jsx';
import TutorMessageList from '../components/TutorMessageList.jsx';
import TutorInputBar from '../components/TutorInputBar.jsx';
import styles from '../styles/TutorPage.module.css';

export default function TutorPage() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingSessions, setIsFetchingSessions] = useState(true);
  const [isOpenMobile, setIsOpenMobile] = useState(false);

  // 1. Tải danh sách phiên chat ban đầu
  const loadSessions = useCallback(async () => {
    try {
      setIsFetchingSessions(true);
      const data = await tutorApi.getChatSessions();
      setSessions(data || []);

      if (data && data.length > 0) {
        // Mặc định chọn phiên đầu tiên
        setActiveSessionId(data[0].session_id);
      } else {
        // Chưa có phiên nào → tạo sẵn một phiên mặc định
        const newSession = await tutorApi.createChatSession('Phiên học tập mới');
        setSessions([newSession]);
        setActiveSessionId(newSession.session_id);
      }
    } catch (err) {
      console.error('Lỗi khi tải danh sách phiên chat:', err);
    } finally {
      setIsFetchingSessions(false);
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  // 2. Tải chi tiết phiên chat và lịch sử tin nhắn khi activeSessionId đổi
  useEffect(() => {
    if (!activeSessionId) return;

    let isMounted = true;
    const fetchSessionDetail = async () => {
      try {
        const detail = await tutorApi.getChatSessionDetail(activeSessionId);
        if (isMounted) {
          setActiveSession(detail);
          setMessages(detail.messages || []);
        }
      } catch (err) {
        console.error('Lỗi khi lấy tin nhắn phiên chat:', err);
      }
    };

    fetchSessionDetail();

    return () => {
      isMounted = false;
    };
  }, [activeSessionId]);

  // 3. Tạo phiên trò chuyện mới
  const handleCreateNewSession = async () => {
    try {
      const newSession = await tutorApi.createChatSession('Phiên học tập mới');
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(newSession.session_id);
      setActiveSession(newSession);
      setMessages([]);
      setIsOpenMobile(false);
    } catch (err) {
      console.error('Không thể tạo phiên chat mới:', err);
    }
  };

  // 4. Xóa phiên trò chuyện
  const handleDeleteSession = async (sessionId, e) => {
    e?.stopPropagation();
    if (!window.confirm('Bạn có chắc chắn muốn xóa phiên trò chuyện này không?')) {
      return;
    }

    try {
      await tutorApi.deleteChatSession(sessionId);
      const nextSessions = sessions.filter((s) => s.session_id !== sessionId);
      setSessions(nextSessions);

      if (activeSessionId === sessionId) {
        if (nextSessions.length > 0) {
          setActiveSessionId(nextSessions[0].session_id);
        } else {
          // Nếu xóa hết thì tự tạo phiên mới
          handleCreateNewSession();
        }
      }
    } catch (err) {
      console.error('Lỗi khi xóa phiên chat:', err);
    }
  };

  // 5. Gửi tin nhắn (từ Input Bar hoặc từ Suggested Prompts)
  const handleSendMessage = async (userText) => {
    if (!userText.trim() || isLoading) return;

    let targetSessionId = activeSessionId;

    // Nếu chưa có phiên nào, tạo mới trước
    if (!targetSessionId) {
      try {
        const newSession = await tutorApi.createChatSession(
          userText.slice(0, 30) + '...'
        );
        targetSessionId = newSession.session_id;
        setSessions((prev) => [newSession, ...prev]);
        setActiveSessionId(targetSessionId);
        setActiveSession(newSession);
      } catch (err) {
        console.error('Lỗi tạo phiên trước khi gửi:', err);
        return;
      }
    }

    // Đẩy tạm tin nhắn của user vào giao diện ngay lập tức
    const tempUserMsg = {
      message_id: `temp-${Date.now()}`,
      role: 'user',
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const response = await tutorApi.sendChatMessage(targetSessionId, userText);

      // Thêm câu trả lời của AI vào danh sách
      const assistantMsg = {
        message_id: `ai-${Date.now()}`,
        role: 'assistant',
        content: response.assistant_message,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Nếu phiên đang mang tên mặc định, đổi tiêu đề theo câu hỏi đầu tiên
      if (
        activeSession?.topic === 'Phiên học tập mới' ||
        sessions.find((s) => s.session_id === targetSessionId)?.topic === 'Phiên học tập mới'
      ) {
        const newTopic = userText.length > 30 ? `${userText.slice(0, 30)}...` : userText;
        setSessions((prev) =>
          prev.map((s) =>
            s.session_id === targetSessionId ? { ...s, topic: newTopic } : s
          )
        );
        setActiveSession((prev) => (prev ? { ...prev, topic: newTopic } : prev));
      }
    } catch (err) {
      console.error('Lỗi khi trò chuyện với AI Tutor:', err);
      const errorMsg = {
        message_id: `err-${Date.now()}`,
        role: 'assistant',
        content: {
          answer: 'Xin lỗi bạn, hiện tại AI Tutor đang bận hoặc gặp sự cố kết nối. Vui lòng thử lại sau giây lát!',
          suggestions: [],
        },
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.tutorContainer}>
      {/* Cột trái: Sidebar quản lý danh sách phiên */}
      <TutorSidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={(id) => {
          setActiveSessionId(id);
          setIsOpenMobile(false);
        }}
        onCreateNewSession={handleCreateNewSession}
        onDeleteSession={handleDeleteSession}
        isOpenMobile={isOpenMobile}
        onCloseMobile={() => setIsOpenMobile(false)}
      />

      {/* Cột phải: Toàn bộ khu vực trò chuyện */}
      <main className={styles.chatMainArea}>
        <TutorHeader
          topic={activeSession?.topic || 'AI Tutor - Trợ lý học tập'}
          subtitle="AI Tutor nhớ ngữ cảnh trong phiên này"
          onToggleSidebar={() => setIsOpenMobile((prev) => !prev)}
        />

        {/* Khung cuộn tin nhắn */}
        <TutorMessageList
          messages={messages}
          isLoading={isLoading}
          onSelectPrompt={handleSendMessage}
        />

        {/* Khung nhập tin nhắn đáy */}
        <div className={styles.inputAreaWrapper}>
          <div className={styles.inputInner}>
            <TutorInputBar
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
