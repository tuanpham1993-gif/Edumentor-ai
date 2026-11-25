// Trang Quản trị lộ trình người dùng (/admin/user-paths) — F14 (API thật + UI/UX cải tiến)
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { adminApi } from '../../../api/admin.api.js';
import { buildAdminRoadmapLayout } from '../../../utils/buildAdminRoadmapLayout.js';
import { formatDate, initials, roleLabel } from '../../../utils/formatters.js';
import { sortLearningPathNodes } from '../../../utils/sortLearningPathNodes.js';
import Pagination from '../../common/components/Pagination.jsx';
import AdminRoadmapCanvas from '../components/AdminRoadmapCanvas.jsx';
import styles from '../styles/AdminUserPaths.module.css';

const STATUS_TABS = [
  { key: 'all', label: 'Tất cả' },
  { key: 'ongoing', label: 'Đang theo' },
  { key: 'completed', label: 'Hoàn thành' },
  { key: 'abandoned', label: 'Đã từ bỏ' },
];

const STATUS_LABELS = {
  ongoing: 'Đang theo',
  completed: 'Hoàn thành',
  abandoned: 'Đã từ bỏ',
};

const GOAL_TYPE_LABELS = {
  career: 'Nghề nghiệp',
  project: 'Dự án',
  template: 'Mẫu lộ trình',
};

const SKILL_STATUS_LABELS = {
  known: 'Đã biết',
  learning: 'Đang học',
  unlearned: 'Chưa học',
};

const NODE_ROLE_LABELS = {
  prerequisite: 'Tiên quyết',
  related: 'Liên quan',
  extension: 'Mở rộng',
  target: 'Mục tiêu',
};

function formatUserSummary(user) {
  if (!user.total_paths) return 'Chưa có lộ trình';
  const parts = [`${user.total_paths} lộ trình`];
  if (user.ongoing_paths > 0) parts.push(`${user.ongoing_paths} đang theo`);
  else if (user.completed_paths > 0) parts.push(`${user.completed_paths} hoàn thành`);
  return parts.join(' · ');
}

export default function AdminUserPathsPage() {
  // 1. Tổng hợp toàn hệ thống & mục tiêu phổ biến
  const [overview, setOverview] = useState(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [showAllGoals, setShowAllGoals] = useState(false);

  // 2. Bộ lọc & danh sách người dùng (cột trái)
  const [viewMode, setViewMode] = useState('user'); // 'user' | 'goal'
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedPopularGoal, setSelectedPopularGoal] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 12;

  const [users, setUsers] = useState([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [errorUsers, setErrorUsers] = useState('');

  // 3. Chi tiết người dùng đang chọn (cột phải)
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [userDetail, setUserDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [errorDetail, setErrorDetail] = useState('');

  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedPathId, setSelectedPathId] = useState(null);
  const [inspectorMode, setInspectorMode] = useState('graph'); // 'graph' | 'list'
  const [selectedSkillNode, setSelectedSkillNode] = useState(null);

  const tabRefs = useRef([]);
  const activeDetailUserRef = useRef(null);

  // Debounce từ khóa tìm kiếm (350ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
      setPage(1);
    }, 350);
    return () => clearTimeout(timer);
  }, [searchInput]);

  // Tải số liệu tổng quan & mục tiêu phổ biến
  const fetchOverview = useCallback(async () => {
    setLoadingOverview(true);
    try {
      const data = await adminApi.getUserPathsOverview();
      setOverview(data);
    } catch {
      // Lỗi thống kê tổng quan không chặn phần tra cứu chính
    } finally {
      setLoadingOverview(false);
    }
  }, []);

  useEffect(() => {
    fetchOverview();
  }, [fetchOverview]);

  // Tải danh sách người dùng kèm tổng hợp lộ trình
  const fetchUsers = useCallback(async () => {
    setLoadingUsers(true);
    setErrorUsers('');
    try {
      const data = await adminApi.getUserPathUsers({
        page,
        pageSize,
        search: debouncedSearch,
        searchBy: viewMode,
        goal: selectedPopularGoal,
      });
      const list = data.items || [];
      setUsers(list);
      setTotalUsers(data.total || 0);

      setSelectedUserId((prevId) => {
        if (list.length === 0) return null;
        if (prevId && list.some((u) => u.user_id === prevId)) return prevId;
        return list[0].user_id;
      });
    } catch (err) {
      setErrorUsers(
        err?.response?.data?.detail || 'Không thể tải danh sách người dùng từ máy chủ.'
      );
    } finally {
      setLoadingUsers(false);
    }
  }, [page, pageSize, debouncedSearch, viewMode, selectedPopularGoal]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Tải chi tiết lộ trình của user đang chọn (kèm kiểm tra chống ghi đè race-condition)
  const fetchUserDetail = useCallback(async (userId) => {
    if (!userId) {
      activeDetailUserRef.current = null;
      setUserDetail(null);
      return;
    }
    activeDetailUserRef.current = userId;
    setLoadingDetail(true);
    setErrorDetail('');
    setSelectedSkillNode(null);
    try {
      const detail = await adminApi.getUserPathsDetail(userId);
      if (activeDetailUserRef.current !== userId) return;
      setUserDetail(detail);
      setStatusFilter('all');
      if (detail.paths && detail.paths.length > 0) {
        setSelectedPathId(detail.paths[0].record_id);
      } else {
        setSelectedPathId(null);
      }
    } catch (err) {
      if (activeDetailUserRef.current !== userId) return;
      setErrorDetail(
        err?.response?.data?.detail || 'Không thể tải chi tiết lộ trình của người dùng này.'
      );
    } finally {
      if (activeDetailUserRef.current === userId) {
        setLoadingDetail(false);
      }
    }
  }, []);

  useEffect(() => {
    fetchUserDetail(selectedUserId);
  }, [selectedUserId, fetchUserDetail]);

  // Lọc lộ trình của user đang chọn theo tab trạng thái
  const filteredUserPaths = useMemo(() => {
    const allPaths = userDetail?.paths || [];
    if (statusFilter === 'all') return allPaths;
    return allPaths.filter((p) => p.status === statusFilter);
  }, [userDetail, statusFilter]);

  const activePath = useMemo(() => {
    if (filteredUserPaths.length === 0) return null;
    return (
      filteredUserPaths.find((p) => p.record_id === selectedPathId) ||
      filteredUserPaths[0]
    );
  }, [filteredUserPaths, selectedPathId]);

  // Chuẩn bị dữ liệu cho chế độ Danh sách theo thứ tự tiên quyết & thông tin quan hệ
  const sortedNodesForList = useMemo(() => {
    if (!activePath?.nodes) return [];
    return sortLearningPathNodes(activePath.nodes, activePath.edges);
  }, [activePath]);

  const layoutMetaById = useMemo(() => {
    if (!activePath?.nodes) return new Map();
    const layout = buildAdminRoadmapLayout(activePath.nodes, activePath.edges);
    return new Map(layout.nodes.map((n) => [String(n.id), n]));
  }, [activePath]);

  function handleSelectUser(u) {
    if (u.user_id !== selectedUserId) {
      setSelectedUserId(u.user_id);
    }
  }

  function handleTogglePopularGoal(goalTitle) {
    setSelectedPopularGoal((prev) => (prev === goalTitle ? '' : goalTitle));
    setPage(1);
  }

  function handleChangeViewMode(mode) {
    setViewMode(mode);
    setPage(1);
  }

  function handleSelectPath(pathId) {
    setSelectedPathId(pathId);
    setSelectedSkillNode(null);
  }

  function handleResetFilters() {
    setSearchInput('');
    setDebouncedSearch('');
    setSelectedPopularGoal('');
    setViewMode('user');
    setPage(1);
  }

  function handleTabKeyDown(e, index) {
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      const next = (index + 1) % STATUS_TABS.length;
      setStatusFilter(STATUS_TABS[next].key);
      tabRefs.current[next]?.focus();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      const prev = (index - 1 + STATUS_TABS.length) % STATUS_TABS.length;
      setStatusFilter(STATUS_TABS[prev].key);
      tabRefs.current[prev]?.focus();
    }
  }

  const stats = overview?.stats;
  const popularGoals = overview?.popular_goals || [];
  const visibleGoals = showAllGoals ? popularGoals : popularGoals.slice(0, 4);
  const totalPages = Math.max(1, Math.ceil(totalUsers / pageSize));
  const activeUserSummary = users.find((u) => u.user_id === selectedUserId) || null;
  const activeUserInfo = userDetail?.user || activeUserSummary;

  return (
    <>
      <div className={styles.pageHead}>
        <div>
          <h1>Lộ trình người dùng</h1>
          <p className={styles.pageSubtitle}>
            Tổng hợp số liệu, mục tiêu và tiến độ kỹ năng thực tế của từng tài khoản. Chế độ chỉ xem, không chỉnh sửa thay người dùng.
          </p>
        </div>
      </div>

      {/* Thanh chỉ số tổng hợp hệ thống */}
      <section className={styles.statsStrip} aria-label="Số liệu tổng hợp lộ trình">
        {loadingOverview && !stats ? (
          <div className={styles.statsSkeleton}>Đang tổng hợp số liệu hệ thống...</div>
        ) : stats ? (
          <>
            <div className={styles.statCell}>
              <span className={styles.statLabel}>Người dùng</span>
              <strong className={styles.statValue}>{stats.total_users}</strong>
              <span className={styles.statSub}>{stats.users_with_paths} có lộ trình</span>
            </div>
            <div className={styles.statCell}>
              <span className={styles.statLabel}>Tổng lộ trình</span>
              <strong className={styles.statValue}>{stats.total_paths}</strong>
              <span className={styles.statSub}>của tài khoản thật</span>
            </div>
            <div className={styles.statCell}>
              <span className={styles.statLabel}>Đang theo học</span>
              <strong className={`${styles.statValue} ${styles.statInfo}`}>
                {stats.ongoing_paths}
              </strong>
              <span className={styles.statSub}>lộ trình đang mở</span>
            </div>
            <div className={styles.statCell}>
              <span className={styles.statLabel}>Đã hoàn thành</span>
              <strong className={`${styles.statValue} ${styles.statOk}`}>
                {stats.completed_paths}
              </strong>
              <span className={styles.statSub}>{stats.abandoned_paths} đã từ bỏ</span>
            </div>
            <div className={styles.statCell}>
              <span className={styles.statLabel}>Đã chia sẻ</span>
              <strong className={`${styles.statValue} ${styles.statAccent}`}>
                {stats.shared_paths}
              </strong>
              <span className={styles.statSub}>công khai cộng đồng</span>
            </div>
          </>
        ) : null}
      </section>

      {/* Dải mục tiêu phổ biến (gọn, không cắt ngang mép phải) */}
      {popularGoals.length > 0 && (
        <section className={styles.goalStrip} aria-label="Mục tiêu phổ biến">
          <div className={styles.goalStripHeader}>
            <span className={styles.goalStripTitle}>Mục tiêu phổ biến</span>
            <div className={styles.goalStripActions}>
              {selectedPopularGoal && (
                <button
                  type="button"
                  className={styles.goalActionBtn}
                  onClick={() => handleTogglePopularGoal(selectedPopularGoal)}
                >
                  Bỏ lọc mục tiêu
                </button>
              )}
              {popularGoals.length > 4 && (
                <button
                  type="button"
                  className={styles.goalActionMutedBtn}
                  onClick={() => setShowAllGoals((prev) => !prev)}
                >
                  {showAllGoals ? 'Thu gọn' : `Xem thêm (+${popularGoals.length - 4})`}
                </button>
              )}
            </div>
          </div>
          <div className={styles.goalChips}>
            {visibleGoals.map((g) => {
              const isActive =
                selectedPopularGoal.toLowerCase() === g.title.toLowerCase();
              return (
                <button
                  key={g.title}
                  type="button"
                  title={g.title}
                  aria-pressed={isActive}
                  className={`${styles.goalChip} ${isActive ? styles.goalChipActive : ''}`}
                  onClick={() => handleTogglePopularGoal(g.title)}
                >
                  <span className={styles.goalChipTitle}>{g.title}</span>
                  <span className={styles.goalChipSub}>
                    {g.path_count} lộ trình · {g.user_count} người
                  </span>
                </button>
              );
            })}
          </div>
        </section>
      )}

      {/* Bố cục Master-Detail 2 cột */}
      <div className={styles.splitLayout}>
        {/* Cột trái cố định khi cuộn: Mode + Search + Danh sách User */}
        <aside className={styles.leftCol} aria-label="Bộ lọc và danh sách người dùng">
          <div className={styles.segmentedToggle} role="radiogroup" aria-label="Chế độ tìm kiếm">
            <button
              type="button"
              role="radio"
              aria-checked={viewMode === 'user'}
              className={`${styles.segBtn} ${viewMode === 'user' ? styles.segBtnActive : ''}`}
              onClick={() => handleChangeViewMode('user')}
            >
              Người dùng
            </button>
            <button
              type="button"
              role="radio"
              aria-checked={viewMode === 'goal'}
              className={`${styles.segBtn} ${viewMode === 'goal' ? styles.segBtnActive : ''}`}
              onClick={() => handleChangeViewMode('goal')}
            >
              Mục tiêu lộ trình
            </button>
          </div>

          <div className={styles.searchBox}>
            <svg
              aria-hidden="true"
              width="17"
              height="17"
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
              placeholder={
                viewMode === 'user' ? 'Tìm tên hoặc email...' : 'Tìm người theo mục tiêu...'
              }
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              aria-label={
                viewMode === 'user' ? 'Tìm tên hoặc email' : 'Tìm người theo mục tiêu lộ trình'
              }
            />
            {searchInput && (
              <button
                type="button"
                className={styles.clearSearchBtn}
                onClick={() => setSearchInput('')}
                aria-label="Xóa từ khóa tìm kiếm"
              >
                ×
              </button>
            )}
          </div>

          {(viewMode === 'goal' || selectedPopularGoal) && (
            <div className={styles.filterContextHint}>
              {selectedPopularGoal
                ? `Đang lọc mục tiêu: “${selectedPopularGoal}”`
                : 'Tìm tài khoản sở hữu lộ trình khớp từ khóa'}
            </div>
          )}

          {errorUsers ? (
            <div className={styles.errorBanner} role="alert">
              <p>{errorUsers}</p>
              <button type="button" className={styles.retryBtn} onClick={fetchUsers}>
                Thử lại
              </button>
            </div>
          ) : loadingUsers ? (
            <div className={styles.userList} aria-busy="true">
              {[1, 2, 3].map((n) => (
                <div key={n} className={styles.skeletonCard} />
              ))}
            </div>
          ) : users.length === 0 ? (
            <div className={styles.emptyPanel}>
              <p>Không tìm thấy người dùng nào khớp bộ lọc.</p>
              {(debouncedSearch || selectedPopularGoal) && (
                <button type="button" className={styles.retryBtn} onClick={handleResetFilters}>
                  Xóa bộ lọc
                </button>
              )}
            </div>
          ) : (
            <>
              <div className={styles.userList} role="list" aria-label="Danh sách người dùng">
                {users.map((u) => {
                  const isSelected = selectedUserId === u.user_id;
                  return (
                    <button
                      key={u.user_id}
                      type="button"
                      role="listitem"
                      aria-current={isSelected ? 'true' : undefined}
                      className={`${styles.userCard} ${isSelected ? styles.userCardActive : ''}`}
                      onClick={() => handleSelectUser(u)}
                    >
                      <span className={styles.userAvatar}>
                        {u.avatar_url ? (
                          <img src={u.avatar_url} alt="" className={styles.userAvatarImg} />
                        ) : (
                          initials(u.full_name)
                        )}
                      </span>
                      <div className={styles.userMeta}>
                        <div className={styles.userNameRow}>
                          <span className={styles.userName}>{u.full_name}</span>
                          {u.role === 'admin' && (
                            <span className={styles.userRoleTag}>Admin</span>
                          )}
                        </div>
                        <span className={styles.userEmail} title={u.email}>
                          {u.email}
                        </span>
                        <span className={styles.userSummary}>{formatUserSummary(u)}</span>
                      </div>
                    </button>
                  );
                })}
              </div>

              <Pagination
                page={page}
                totalPages={totalPages}
                onChange={setPage}
                label="Phân trang danh sách người dùng"
              />
            </>
          )}
        </aside>

        {/* Cột phải: Thông tin User + Chọn lộ trình gọn + Đồ thị/Danh sách */}
        <div className={styles.rightCol}>
          {errorDetail ? (
            <div className={styles.errorBanner} role="alert">
              <p>{errorDetail}</p>
              <button
                type="button"
                className={styles.retryBtn}
                onClick={() => fetchUserDetail(selectedUserId)}
              >
                Thử lại
              </button>
            </div>
          ) : loadingDetail ? (
            <div className={styles.detailSkeleton} aria-busy="true">
              <div className={styles.skeletonHeader} />
              <div className={styles.skeletonGrid} />
              <div className={styles.skeletonCanvas} />
            </div>
          ) : !activeUserInfo ? (
            <div className={styles.emptyPanel}>
              Chọn một người dùng ở cột bên trái để xem chi tiết lộ trình học tập.
            </div>
          ) : (
            <>
              {/* Gộp User Header + Tab trạng thái thành 1 khối thống nhất */}
              <div className={styles.inspectorHeaderCard}>
                <div className={styles.userHeaderRow}>
                  <div className={styles.userHeaderLeft}>
                    <span className={styles.userHeaderAvatar}>
                      {activeUserInfo.avatar_url ? (
                        <img
                          src={activeUserInfo.avatar_url}
                          alt=""
                          className={styles.userAvatarImg}
                        />
                      ) : (
                        initials(activeUserInfo.full_name)
                      )}
                    </span>
                    <div className={styles.userHeaderInfo}>
                      <div className={styles.userNameRow}>
                        <h2>{activeUserInfo.full_name}</h2>
                        <span className={styles.roleBadge}>
                          {roleLabel(activeUserInfo.role)}
                        </span>
                      </div>
                      <div className={styles.userHeaderMeta}>
                        {activeUserInfo.email} · tham gia {formatDate(activeUserInfo.created_at)}
                        {activeUserSummary && (
                          <>
                            {' '}
                            · {activeUserSummary.known_skills_count} kỹ năng đã biết ·{' '}
                            {activeUserSummary.learning_skills_count} đang học
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  <span className={styles.readonlyBadge}>Chỉ xem</span>
                </div>

                {/* Tab trạng thái lộ trình */}
                <div
                  className={styles.pathStatusTabs}
                  role="tablist"
                  aria-label="Trạng thái lộ trình"
                >
                  {STATUS_TABS.map((tab, idx) => {
                    const count = userDetail?.status_counts?.[tab.key] ?? 0;
                    const isActive = statusFilter === tab.key;
                    return (
                      <button
                        key={tab.key}
                        ref={(el) => {
                          tabRefs.current[idx] = el;
                        }}
                        type="button"
                        role="tab"
                        aria-selected={isActive}
                        tabIndex={isActive ? 0 : -1}
                        className={`${styles.statusTabBtn} ${
                          isActive ? styles.statusTabBtnActive : ''
                        }`}
                        onClick={() => {
                          setStatusFilter(tab.key);
                          setSelectedSkillNode(null);
                        }}
                        onKeyDown={(e) => handleTabKeyDown(e, idx)}
                      >
                        {tab.label} ({count})
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Lưới 2 cột thẻ lộ trình gọn gàng để giữ đồ thị trong vùng nhìn đầu tiên */}
              {filteredUserPaths.length === 0 ? (
                <div className={styles.emptyPanel}>
                  Người dùng này chưa có lộ trình nào ở trạng thái đã chọn.
                </div>
              ) : (
                <div className={styles.pathCardsGrid}>
                  {filteredUserPaths.map((p) => {
                    const isSelected = activePath && activePath.record_id === p.record_id;
                    let badgeClass = styles.badgeOngoing;
                    if (p.status === 'completed') badgeClass = styles.badgeCompleted;
                    if (p.status === 'abandoned') badgeClass = styles.badgeAbandoned;

                    const percent =
                      p.progress_total > 0
                        ? Math.round((p.progress_known / p.progress_total) * 100)
                        : 0;

                    return (
                      <button
                        key={p.record_id}
                        type="button"
                        title={p.original_query}
                        aria-pressed={Boolean(isSelected)}
                        className={`${styles.pathCard} ${isSelected ? styles.pathCardActive : ''}`}
                        onClick={() => handleSelectPath(p.record_id)}
                      >
                        <div className={styles.pathCardTop}>
                          <span className={styles.pathGoalLabel}>
                            {GOAL_TYPE_LABELS[p.goal_type] || 'Mục tiêu'} · #{p.record_id}
                          </span>
                          <span className={`${styles.pathStatusBadge} ${badgeClass}`}>
                            {STATUS_LABELS[p.status] || p.status}
                          </span>
                        </div>

                        <div className={styles.pathCardTitle}>“{p.original_query}”</div>

                        <div className={styles.pathCardFooter}>
                          <div className={styles.pathProgressRow}>
                            <div
                              className={styles.progressTrack}
                              role="progressbar"
                              aria-valuemin={0}
                              aria-valuemax={p.progress_total}
                              aria-valuenow={p.progress_known}
                              aria-label={`Tiến độ ${p.original_query}`}
                            >
                              <div
                                className={styles.progressFill}
                                style={{ width: `${percent}%` }}
                              />
                            </div>
                            <span className={styles.pathCardProgress}>
                              {p.progress_known}/{p.progress_total} đã biết
                            </span>
                          </div>

                          {(p.is_shared || p.cloned_from_id) && (
                            <div className={styles.pathMetaChips}>
                              {p.is_shared && (
                                <span className={styles.shareChip}>
                                  Chia sẻ · {p.clone_count} lượt
                                </span>
                              )}
                              {p.cloned_from_id && (
                                <span className={styles.cloneChip}>
                                  Từ #{p.cloned_from_id}
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Chi tiết lộ trình & Đồ thị / Danh sách tiên quyết */}
              {activePath && (
                <div className={styles.pathDetailCard}>
                  <div className={styles.pathDetailHead}>
                    <div className={styles.pathDetailMain}>
                      <div className={styles.pathDetailEyebrowRow}>
                        <h3>Mục đích của lộ trình</h3>
                        <div
                          className={styles.viewModeSwitch}
                          role="radiogroup"
                          aria-label="Chế độ xem chi tiết lộ trình"
                        >
                          <button
                            type="button"
                            role="radio"
                            aria-checked={inspectorMode === 'graph'}
                            className={`${styles.viewModeBtn} ${
                              inspectorMode === 'graph' ? styles.viewModeBtnActive : ''
                            }`}
                            onClick={() => setInspectorMode('graph')}
                          >
                            Đồ thị
                          </button>
                          <button
                            type="button"
                            role="radio"
                            aria-checked={inspectorMode === 'list'}
                            className={`${styles.viewModeBtn} ${
                              inspectorMode === 'list' ? styles.viewModeBtnActive : ''
                            }`}
                            onClick={() => setInspectorMode('list')}
                          >
                            Danh sách ({activePath.nodes.length})
                          </button>
                        </div>
                      </div>
                      <div className={styles.pathDetailTitle}>“{activePath.original_query}”</div>
                      <div className={styles.pathDetailSubtitle}>
                        {GOAL_TYPE_LABELS[activePath.goal_type] || 'Lộ trình'} ·{' '}
                        {activePath.nodes.length} kỹ năng · {activePath.edges.length} kết nối
                        {activePath.is_shared && activePath.shared_at && (
                          <> · chia sẻ ngày {formatDate(activePath.shared_at)}</>
                        )}
                      </div>
                    </div>

                    <dl className={styles.pathMetaKv}>
                      <dt>Mã lộ trình</dt>
                      <dd>#{activePath.record_id}</dd>
                      <dt>Mục tiêu</dt>
                      <dd className={styles.highlightTarget}>
                        {activePath.target_skills && activePath.target_skills.length > 0
                          ? activePath.target_skills.join(', ')
                          : 'Theo toàn bộ lộ trình'}
                      </dd>
                      <dt>Tiến độ</dt>
                      <dd>
                        {activePath.progress_known}/{activePath.progress_total} đã biết
                        {activePath.progress_learning > 0 &&
                          ` · ${activePath.progress_learning} đang học`}
                      </dd>
                    </dl>
                  </div>

                  {activePath.nodes.length === 0 ? (
                    <div className={styles.emptyPanel}>
                      Lộ trình này hiện chưa có kỹ năng nào.
                    </div>
                  ) : inspectorMode === 'graph' ? (
                    <>
                      <AdminRoadmapCanvas
                        nodes={activePath.nodes}
                        connections={activePath.edges}
                        mode="user"
                        selectedNodeId={selectedSkillNode?.id ?? null}
                        onNodeClick={(node) => setSelectedSkillNode(node)}
                      />

                      {selectedSkillNode && (
                        <div className={styles.skillInspectBar} role="status">
                          <div className={styles.skillInspectTop}>
                            <div className={styles.skillInspectMain}>
                              <span className={styles.skillInspectLabel}>Kỹ năng đang chọn:</span>
                              <strong className={styles.skillInspectName}>
                                {selectedSkillNode.name}
                              </strong>
                            </div>
                            <div className={styles.skillInspectMeta}>
                              <span className={styles.skillInspectChip}>
                                Vai trò:{' '}
                                {selectedSkillNode.isTarget
                                  ? 'Mục tiêu'
                                  : NODE_ROLE_LABELS[selectedSkillNode.role] ||
                                    'Kỹ năng trong lộ trình'}
                              </span>
                              <span
                                className={`${styles.skillInspectStatus} ${
                                  selectedSkillNode.rawStatus === 'known'
                                    ? styles.inspectKnown
                                    : selectedSkillNode.rawStatus === 'learning'
                                    ? styles.inspectLearning
                                    : styles.inspectUnlearned
                                }`}
                              >
                                {SKILL_STATUS_LABELS[selectedSkillNode.rawStatus] || 'Chưa học'}
                              </span>
                            </div>
                          </div>

                          {(selectedSkillNode.prerequisites?.length > 0 ||
                            selectedSkillNode.unlocks?.length > 0) && (
                            <div className={styles.skillRelationsRow}>
                              {selectedSkillNode.prerequisites?.length > 0 && (
                                <span className={styles.skillRelationText}>
                                  <strong>Học sau:</strong>{' '}
                                  {selectedSkillNode.prerequisites.join(', ')}
                                </span>
                              )}
                              {selectedSkillNode.unlocks?.length > 0 && (
                                <span className={styles.skillRelationText}>
                                  <strong>Mở khóa cho:</strong>{' '}
                                  {selectedSkillNode.unlocks.join(', ')}
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </>
                  ) : (
                    <ol className={styles.topoSkillList}>
                      {sortedNodesForList.map((node, idx) => {
                        const meta = layoutMetaById.get(String(node.skill_id));
                        const isSelected =
                          selectedSkillNode &&
                          String(selectedSkillNode.id) === String(node.skill_id);
                        const statusKey = node.user_skill_status || 'unlearned';
                        const statusClass =
                          statusKey === 'known'
                            ? styles.inspectKnown
                            : statusKey === 'learning'
                            ? styles.inspectLearning
                            : styles.inspectUnlearned;

                        return (
                          <li key={node.skill_id}>
                            <button
                              type="button"
                              aria-pressed={Boolean(isSelected)}
                              className={`${styles.topoSkillItem} ${
                                isSelected ? styles.topoSkillItemActive : ''
                              }`}
                              onClick={() =>
                                setSelectedSkillNode(
                                  meta || {
                                    id: String(node.skill_id),
                                    name: node.skill_name,
                                    role: node.node_role,
                                    isTarget: node.is_target,
                                    rawStatus: statusKey,
                                    prerequisites: node._topology?.prerequisiteNames || [],
                                    unlocks: [],
                                  }
                                )
                              }
                            >
                              <span className={styles.topoSkillIndex}>{idx + 1}</span>
                              <div className={styles.topoSkillBody}>
                                <span className={styles.topoSkillName}>{node.skill_name}</span>
                                <span className={styles.topoSkillHint}>
                                  {node._topology?.prerequisiteNames?.length > 0
                                    ? `↳ Cần: ${node._topology.prerequisiteNames.join(', ')}`
                                    : 'Nền tảng khởi đầu'}
                                </span>
                              </div>
                              <div className={styles.topoSkillBadges}>
                                {node.is_target && (
                                  <span className={styles.skillInspectChip}>Mục tiêu</span>
                                )}
                                <span className={`${styles.skillInspectStatus} ${statusClass}`}>
                                  {SKILL_STATUS_LABELS[statusKey] || 'Chưa học'}
                                </span>
                              </div>
                            </button>
                          </li>
                        );
                      })}
                    </ol>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
}
