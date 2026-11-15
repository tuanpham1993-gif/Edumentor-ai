// Trang Quản trị phản hồi (/admin/feedback) — F13
import React, { useState, useMemo } from 'react';
import { INITIAL_FEEDBACKS } from '../data/adminMockData.js';
import AdminFeedbackDrawer from '../components/AdminFeedbackDrawer.jsx';
import styles from '../styles/AdminFeedback.module.css';

const TIME_CHIPS = ['Mọi lúc', 'Hôm nay', '7 ngày qua', '30 ngày qua', 'Tùy chọn'];
const FEEDBACK_TYPES = [
  'Mọi loại phản hồi',
  'Nội dung bài giảng',
  'Gợi ý lộ trình chưa phù hợp',
  'Đường dẫn không mở được',
  'Lỗi hệ thống',
  'Thông tin khóa học sai',
  'Giao diện, trải nghiệm',
  'Khác',
];

export default function AdminFeedbackPage() {
  const [feedbacks] = useState(INITIAL_FEEDBACKS);
  const [targetTab, setTargetTab] = useState('all'); // 'all' | 'course' | 'system'
  const [selectedType, setSelectedType] = useState('Mọi loại phản hồi');
  const [selectedTimeRange, setSelectedTimeRange] = useState('Mọi lúc');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFeedbackId, setSelectedFeedbackId] = useState(12); // Mặc định mở phản hồi #12 như ảnh
  const [sortDesc, setSortDesc] = useState(true);

  // Thống kê
  const totalCount = feedbacks.length;
  const courseCount = feedbacks.filter((f) => f.target === 'Khóa học').length;
  const systemCount = feedbacks.filter((f) => f.target === 'Hệ thống').length;

  // Lọc
  const filteredFeedbacks = useMemo(() => {
    return feedbacks
      .filter((f) => {
        // Tab lọc
        if (targetTab === 'course' && f.target !== 'Khóa học') return false;
        if (targetTab === 'system' && f.target !== 'Hệ thống') return false;

        // Loại phản hồi
        if (selectedType !== 'Mọi loại phản hồi' && f.type !== selectedType) return false;

        // Thời gian giả lập
        if (selectedTimeRange === 'Hôm nay') {
          // trong ngày hôm nay (01/11/2026)
          return f.time.startsWith('01/11/2026');
        }
        if (selectedTimeRange === '7 ngày qua') {
          return f.id >= 8;
        }
        if (selectedTimeRange === '30 ngày qua') {
          return f.id >= 5;
        }

        // Tìm kiếm
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matchContent = f.content.toLowerCase().includes(q);
          const matchSender = f.senderName.toLowerCase().includes(q) || f.senderEmail.toLowerCase().includes(q);
          const matchCourse = f.targetDetail && f.targetDetail.toLowerCase().includes(q);
          return matchContent || matchSender || matchCourse;
        }

        return true;
      })
      .sort((a, b) => {
        return sortDesc ? b.id - a.id : a.id - b.id;
      });
  }, [feedbacks, targetTab, selectedType, selectedTimeRange, searchQuery, sortDesc]);

  const selectedFeedback = feedbacks.find((f) => f.id === selectedFeedbackId);

  function handleResetFilters() {
    setTargetTab('all');
    setSelectedType('Mọi loại phản hồi');
    setSelectedTimeRange('Mọi lúc');
    setSearchQuery('');
  }

  const isFiltered =
    targetTab !== 'all' ||
    selectedType !== 'Mọi loại phản hồi' ||
    selectedTimeRange !== 'Mọi lúc' ||
    Boolean(searchQuery.trim());

  return (
    <>
      <div className={styles.pageHead}>
        <h1>Phản hồi</h1>
        <p className={styles.pageSubtitle}>
          Góp ý học viên gửi từ trang Liên hệ. Chỉ xem và lọc; bảng Feedback chưa có cột trạng thái xử lý.
        </p>
      </div>

      {/* 3 Thẻ thống kê */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>Tổng phản hồi</span>
          <span className={styles.statValue}>{totalCount}</span>
        </div>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>Về khóa học</span>
          <span className={styles.statValue}>{courseCount}</span>
        </div>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>Về hệ thống</span>
          <span className={styles.statValue}>{systemCount}</span>
        </div>
      </div>

      {/* Thanh công cụ lọc hàng 1 */}
      <div className={styles.filterRowTop}>
        <div className={styles.targetTabs}>
          <button
            type="button"
            className={`${styles.tabBtn} ${targetTab === 'all' ? styles.tabBtnActive : ''}`}
            onClick={() => setTargetTab('all')}
          >
            Tất cả ({totalCount})
          </button>
          <button
            type="button"
            className={`${styles.tabBtn} ${targetTab === 'course' ? styles.tabBtnActive : ''}`}
            onClick={() => setTargetTab('course')}
          >
            Khóa học ({courseCount})
          </button>
          <button
            type="button"
            className={`${styles.tabBtn} ${targetTab === 'system' ? styles.tabBtnActive : ''}`}
            onClick={() => setTargetTab('system')}
          >
            Hệ thống ({systemCount})
          </button>
        </div>

        <div className={styles.searchBox}>
          <svg
            aria-hidden="true"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
          <input
            placeholder="Tìm theo nội dung, người gửi, khóa học"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Tìm theo nội dung, người gửi, khóa học"
          />
        </div>

        <select
          className={styles.typeSelect}
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          aria-label="Chọn loại phản hồi"
        >
          {FEEDBACK_TYPES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>

      {/* Thanh công cụ lọc hàng 2: Thời gian */}
      <div className={styles.timeBar}>
        <div className={styles.timeChips}>
          <span className={styles.timeLabel}>Thời gian</span>
          {TIME_CHIPS.map((chip) => (
            <button
              key={chip}
              type="button"
              className={`${styles.timeChip} ${
                selectedTimeRange === chip ? styles.timeChipActive : ''
              }`}
              onClick={() => setSelectedTimeRange(chip)}
            >
              {chip}
            </button>
          ))}
        </div>

        <div className={styles.filterStatus}>
          <span>
            Đang hiện {filteredFeedbacks.length}/{totalCount} phản hồi
          </span>
          {isFiltered && (
            <button type="button" className={styles.clearFilterBtn} onClick={handleResetFilters}>
              Xóa bộ lọc
            </button>
          )}
        </div>
      </div>

      {/* Layout Bảng + Drawer chi tiết */}
      <div
        className={`${styles.feedbackSplit} ${
          !selectedFeedback ? styles.feedbackSplitFull : ''
        }`}
      >
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th style={{ width: '22%' }}>Người gửi</th>
                <th style={{ width: '18%' }}>Về</th>
                <th style={{ width: '18%' }}>Loại</th>
                <th style={{ width: '28%' }}>Nội dung</th>
                <th
                  style={{ width: '14%', cursor: 'pointer' }}
                  onClick={() => setSortDesc(!sortDesc)}
                  title="Bấm để đổi thứ tự sắp xếp"
                >
                  Thời gian {sortDesc ? '↓' : '↑'}
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredFeedbacks.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                    Không có phản hồi nào phù hợp với bộ lọc hiện tại.
                  </td>
                </tr>
              ) : (
                filteredFeedbacks.map((f) => {
                  const isSelected = selectedFeedbackId === f.id;
                  return (
                    <tr
                      key={f.id}
                      className={`${styles.tableRow} ${isSelected ? styles.tableRowSelected : ''}`}
                      onClick={() => setSelectedFeedbackId(f.id)}
                    >
                      <td>
                        <div className={styles.senderName}>{f.senderName}</div>
                        <div className={styles.senderEmail}>{f.senderEmail}</div>
                      </td>
                      <td>
                        <span
                          className={`${styles.targetBadge} ${
                            f.target === 'Hệ thống' ? styles.targetBadgeSystem : ''
                          }`}
                        >
                          {f.target}
                        </span>
                        {f.targetDetail && (
                          <div className={styles.targetDetail}>{f.targetDetail}</div>
                        )}
                      </td>
                      <td style={{ color: 'var(--text-soft)' }}>{f.type}</td>
                      <td>
                        <div className={styles.contentClamp}>{f.content}</div>
                      </td>
                      <td className={styles.timeCell}>{f.time}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Drawer bên phải */}
        <AdminFeedbackDrawer
          feedback={selectedFeedback}
          onClose={() => setSelectedFeedbackId(null)}
        />
      </div>
    </>
  );
}
