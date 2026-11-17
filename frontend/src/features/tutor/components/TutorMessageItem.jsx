import { useState } from 'react';
import TutorBotIcon from './TutorBotIcon.jsx';
import SuggestedPrompts from './SuggestedPrompts.jsx';
import styles from '../styles/TutorMessage.module.css';

/**
 * Hiển thị một khối code có nút copy
 */
function CodeBlock({ code, language = '' }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={styles.codeBlockWrapper}>
      <div className={styles.codeHeader}>
        <span className={styles.codeLang}>{language || 'code'}</span>
        <button
          type="button"
          className={styles.copyBtn}
          onClick={handleCopy}
          title="Sao chép mã"
        >
          {copied ? '✓ Đã chép' : 'Sao chép'}
        </button>
      </div>
      <pre className={styles.preCode}>
        <code>{code}</code>
      </pre>
    </div>
  );
}

/**
 * Parser đơn giản để render markdown, code blocks và văn bản
 */
function FormattedContent({ content }) {
  if (!content) return null;

  // Tách các khối mã ```...```
  const parts = [];
  const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n?([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        value: content.substring(lastIndex, match.index),
      });
    }
    parts.push({
      type: 'code',
      language: match[1] || 'python',
      code: match[2]?.trim(),
    });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < content.length) {
    parts.push({
      type: 'text',
      value: content.substring(lastIndex),
    });
  }

  return (
    <div className={styles.formattedBody}>
      {parts.map((part, idx) => {
        if (part.type === 'code') {
          return <CodeBlock key={idx} code={part.code} language={part.language} />;
        }

        // Render đoạn text với format dòng, gạch đầu dòng và in đậm
        const lines = part.value.split('\n');
        return (
          <div key={idx} className={styles.textBlock}>
            {lines.map((line, lIdx) => {
              const trimmed = line.trim();
              if (!trimmed) return <div key={lIdx} className={styles.spacer} />;

              // Định dạng tiêu đề dạng #, ##, ###
              if (trimmed.startsWith('### ')) {
                return (
                  <h4 key={lIdx} className={styles.heading4}>
                    {trimmed.replace(/^###\s+/, '')}
                  </h4>
                );
              }
              if (trimmed.startsWith('## ') || trimmed.startsWith('# ')) {
                return (
                  <h3 key={lIdx} className={styles.heading3}>
                    {trimmed.replace(/^#+\s+/, '')}
                  </h3>
                );
              }

              // Định dạng danh sách - hoặc *
              if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                return (
                  <li key={lIdx} className={styles.listItem}>
                    {renderInlineFormatted(trimmed.substring(2))}
                  </li>
                );
              }

              return (
                <p key={lIdx} className={styles.paragraph}>
                  {renderInlineFormatted(line)}
                </p>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

/**
 * Xử lý in đậm **text** và inline code `code`
 */
function renderInlineFormatted(text) {
  const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);

  return parts.map((seg, i) => {
    if (seg.startsWith('**') && seg.endsWith('**')) {
      return <strong key={i}>{seg.slice(2, -2)}</strong>;
    }
    if (seg.startsWith('`') && seg.endsWith('`')) {
      return (
        <code key={i} className={styles.inlineCode}>
          {seg.slice(1, -1)}
        </code>
      );
    }
    return seg;
  });
}

/**
 * Component hiển thị một bong bóng tin nhắn (User hoặc AI Tutor)
 */
export default function TutorMessageItem({
  message,
  onSelectPrompt,
  isLatestAssistant = false,
}) {
  const isUser = message.role === 'user';

  // Trích xuất content và suggestions từ chuỗi JSON nếu là assistant
  let displayContent = message.content;
  let suggestions = [];

  if (!isUser && typeof message.content === 'string') {
    try {
      const parsed = JSON.parse(message.content);
      if (parsed && typeof parsed === 'object') {
        if (parsed.answer) displayContent = parsed.answer;
        if (Array.isArray(parsed.suggestions)) suggestions = parsed.suggestions;
      }
    } catch {
      // Giữ nguyên text thuần nếu không phải JSON
    }
  }

  // Trường hợp assistant_message truyền trực tiếp object
  if (!isUser && typeof message.content === 'object' && message.content !== null) {
    displayContent = message.content.answer || '';
    suggestions = message.content.suggestions || [];
  }

  return (
    <div className={`${styles.messageRow} ${isUser ? styles.userRow : styles.assistantRow}`}>
      {/* Icon avatar AI Tutor nếu là tin nhắn của assistant */}
      {!isUser && (
        <div className={styles.avatarCol}>
          <TutorBotIcon size={28} />
        </div>
      )}

      <div className={styles.bubbleCol}>
        <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.assistantBubble}`}>
          <FormattedContent content={displayContent} />
        </div>

        {/* Gợi ý Suggested Prompts chỉ hiển thị cho tin nhắn của AI Tutor */}
        {!isUser && suggestions.length > 0 && onSelectPrompt && (
          <SuggestedPrompts
            suggestions={suggestions}
            onSelectPrompt={onSelectPrompt}
          />
        )}
      </div>
    </div>
  );
}
