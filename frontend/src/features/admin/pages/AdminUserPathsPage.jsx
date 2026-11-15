// Trang Quản trị lộ trình người dùng (/admin/user-paths) — F14
import React, { useState, useMemo } from 'react';
import { POPULAR_GOALS, INITIAL_USER_PATHS } from '../data/adminMockData.js';
import AdminRoadmapCanvas from '../components/AdminRoadmapCanvas.jsx';
import styles from '../styles/AdminUserPaths.module.css';

export default function AdminUserPathsPage() {
  const [users] = useState(INITIAL_USER_PATHS);
  const [selectedUserId, setSelectedUserId] = useState('u1');
  const [selectedPathId, setSelectedPathId] = useState('p1');
  const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'ongoing' | 'completed' | 'abandoned'
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('user'); // 'user' | 'goal'
  const [selectedPopularGoal, setSelectedPopularGoal] = useState('Data Analyst');

  // Lọc người dùng
  const filteredUsers = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return users;
    return users.filter(
      (u) => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    );
  }, [users, searchQuery]);

  const activeUser = users.find((u) => u.userId === selectedUserId) || users[0];

  // Lọc các lộ trình của người dùng theo tab
  const filteredUserPaths = useMemo(() => {
    if (!activeUser || !activeUser.paths) return [];
    if (statusFilter === 'all') return activeUser.paths;
    return activeUser.paths.filter((p) => p.status === statusFilter);
  }, [activeUser, statusFilter]);

  const activePath =
    (activeUser &&
      activeUser.paths &&
      activeUser.paths.find((p) => p.pathId === selectedPathId)) ||
    (activeUser && activeUser.paths && activeUser.paths[0]) ||
    null;

  function handleSelectUser(u) {
    setSelectedUserId(u.userId);
    if (u.paths && u.paths.length > 0) {
      setSelectedPathId(u.paths[0].pathId);
    } else {
      setSelectedPathId(null);
    }
  }

  return (
    <>
      <div className={styles.pageHead}>
        <h1>Lộ trình người dùng</h1>
        <p className={styles.pageSubtitle}>
          Xem mục tiêu, lộ trình học tập và tiến độ kỹ năng của từng người dùng. Chỉ xem, không chỉnh sửa thay người dùng.
        </p>
      </div>

      {/* Dải mục tiêu phổ biến ở trên */}
      <div className={styles.goalStrip}>
        <span className={styles.goalStripTitle}>Mục tiêu phổ biến</span>
        <div className={styles.goalChips}>
          {POPULAR_GOALS.map((g) => {
            const isActive = selectedPopularGoal === g.title;
            return (
              <button
                key={g.title}
                type="button"
                className={`${styles.goalChip} ${isActive ? styles.goalChipActive : ''}`}
                onClick={() => setSelectedPopularGoal(g.title)}
              >
                <span className={styles.goalChipTitle}>{g.title}</span>
                <span className={styles.goalChipSub}>
                  {g.pathCount} lộ trình · {g.userCount} người
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Bố cục 2 cột */}
      <div className={styles.splitLayout}>
        {/* Cột trái: Segmented Mode + Search + Danh sách User */}
        <div className={styles.leftCol}>
          <div className={styles.segmentedToggle}>
            <button
              type="button"
              className={`${styles.segBtn} ${viewMode === 'user' ? styles.segBtnActive : ''}`}
              onClick={() => setViewMode('user')}
            >
              Người dùng
            </button>
            <button
              type="button"
              className={`${styles.segBtn} ${viewMode === 'goal' ? styles.segBtnActive : ''}`}
              onClick={() => setViewMode('goal')}
            >
              Mục tiêu lộ trình
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
              placeholder="Tìm tên hoặc email"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Tìm tên hoặc email"
            />
          </div>

          <div className={styles.userList}>
            {filteredUsers.map((u) => {
              const isSelected = activeUser && activeUser.userId === u.userId;
              return (
                <button
                  key={u.userId}
                  type="button"
                  className={`${styles.userCard} ${isSelected ? styles.userCardActive : ''}`}
                  onClick={() => handleSelectUser(u)}
                >
                  <span className={styles.userAvatar}>{u.initials}</span>
                  <div className={styles.userMeta}>
                    <span className={styles.userName}>{u.name}</span>
                    <span className={styles.userEmail}>{u.email}</span>
                    <span className={styles.userSummary}>{u.summary}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Cột phải: Thông tin User & Lộ trình */}
        <div className={styles.rightCol}>
          {/* Header Người dùng */}
          <div className={styles.userHeaderCard}>
            <div className={styles.userHeaderLeft}>
              <span className={styles.userHeaderAvatar}>{activeUser.initials}</span>
              <div className={styles.userHeaderInfo}>
                <h2>{activeUser.name}</h2>
                <div className={styles.userHeaderMeta}>
                  {activeUser.email} · tham gia {activeUser.joinDate}
                </div>
              </div>
            </div>

            <span className={styles.readonlyBadge}>Chỉ xem</span>
          </div>

          {/* Tab trạng thái: Tất cả, Đang theo, Hoàn thành, Đã từ bỏ */}
          <div className={styles.pathStatusTabs}>
            <button
              type="button"
              className={`${styles.statusTabBtn} ${
                statusFilter === 'all' ? styles.statusTabBtnActive : ''
              }`}
              onClick={() => setStatusFilter('all')}
            >
              Tất cả ({activeUser.paths ? activeUser.paths.length : 0})
            </button>
            <button
              type="button"
              className={`${styles.statusTabBtn} ${
                statusFilter === 'ongoing' ? styles.statusTabBtnActive : ''
              }`}
              onClick={() => setStatusFilter('ongoing')}
            >
              Đang theo ({activeUser.paths ? activeUser.paths.filter((p) => p.status === 'ongoing').length : 0})
            </button>
            <button
              type="button"
              className={`${styles.statusTabBtn} ${
                statusFilter === 'completed' ? styles.statusTabBtnActive : ''
              }`}
              onClick={() => setStatusFilter('completed')}
            >
              Hoàn thành ({activeUser.paths ? activeUser.paths.filter((p) => p.status === 'completed').length : 0})
            </button>
            <button
              type="button"
              className={`${styles.statusTabBtn} ${
                statusFilter === 'abandoned' ? styles.statusTabBtnActive : ''
              }`}
              onClick={() => setStatusFilter('abandoned')}
            >
              Đã từ bỏ ({activeUser.paths ? activeUser.paths.filter((p) => p.status === 'abandoned').length : 0})
            </button>
          </div>

          {/* Các thẻ lộ trình của người dùng */}
          {filteredUserPaths.length === 0 ? (
            <div
              style={{
                padding: '32px',
                textAlign: 'center',
                color: 'var(--text-muted)',
                background: 'var(--card)',
                borderRadius: '12px',
              }}
            >
              Người dùng này chưa có lộ trình nào ở trạng thái đã chọn.
            </div>
          ) : (
            <div className={styles.pathCardsGrid}>
              {filteredUserPaths.map((p) => {
                const isSelected = activePath && activePath.pathId === p.pathId;
                let badgeClass = styles.badgeOngoing;
                if (p.status === 'completed') badgeClass = styles.badgeCompleted;
                if (p.status === 'abandoned') badgeClass = styles.badgeAbandoned;

                return (
                  <div
                    key={p.pathId}
                    className={`${styles.pathCard} ${isSelected ? styles.pathCardActive : ''}`}
                    onClick={() => setSelectedPathId(p.pathId)}
                  >
                    <div className={styles.pathCardTop}>
                      <span className={styles.pathGoalLabel}>MỤC TIÊU</span>
                      <span className={`${styles.pathStatusBadge} ${badgeClass}`}>
                        {p.statusText}
                      </span>
                    </div>

                    <div className={styles.pathCardTitle}>“{p.title}”</div>
                    <div className={styles.pathCardTemplate}>{p.templateName}</div>
                    <div className={styles.pathCardProgress}>{p.progressText}</div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Chi tiết lộ trình & Đồ thị trực quan */}
          {activePath && (
            <div className={styles.pathDetailCard}>
              <div className={styles.pathDetailHead}>
                <div>
                  <h3>MỤC ĐÍCH CỦA LỘ TRÌNH</h3>
                  <div className={styles.pathDetailTitle}>“{activePath.title}”</div>
                  <div className={styles.pathDetailSubtitle}>{activePath.subtitle}</div>
                </div>

                <dl className={styles.pathMetaKv}>
                  <dt>Mẫu</dt>
                  <dd>{activePath.templateName}</dd>
                  <dt>Kỹ năng mục tiêu</dt>
                  <dd className={styles.highlightTarget}>{activePath.targetSkill}</dd>
                  <dt>Tiến độ</dt>
                  <dd>
                    {activePath.progressKnown}/{activePath.progressTotal} kỹ năng đã biết
                  </dd>
                </dl>
              </div>

              {/* Đồ thị SVG Bezier Canvas */}
              <AdminRoadmapCanvas
                nodes={activePath.nodes}
                connections={activePath.connections}
                width={780}
                height={260}
                mode="user"
                onNodeClick={(node) => {
                  alert(`Kỹ năng: ${node.name} (Trạng thái: ${node.status})`);
                }}
              />
            </div>
          )}
        </div>
      </div>
    </>
  );
}
