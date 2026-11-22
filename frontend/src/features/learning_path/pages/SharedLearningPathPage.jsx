import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  getSharedLearningPath,
  cloneSharedLearningPath,
} from '../../../api/learningPaths.api';
import { useAuth } from '../../../hooks/useAuth';
import LearningPathGraphForDetail from '../components/LearningPathGraphForDetail';
import CourseRecommendation from '../components/CourseRecommendation';
import { formatDate, initials } from '../../../utils/formatters';
import { sortLearningPathNodes } from '../../../utils/sortLearningPathNodes';
import styles from '../styles/SharedLearningPath.module.css';

export default function SharedLearningPathPage() {
  const { shareCode } = useParams();
  const navigate = useNavigate();
  const { user, status } = useAuth();

  const [path, setPath] = useState(null);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [isCloning, setIsCloning] = useState(false);
  const [cloneError, setCloneError] = useState('');
  const [cloneSuccess, setCloneSuccess] = useState('');
  const [showLoginModal, setShowLoginModal] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function fetchSharedPath() {
      try {
        setIsLoading(true);
        setError('');
        const data = await getSharedLearningPath(shareCode);
        if (isMounted) {
          setPath(data);
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err.response?.data?.detail ||
              'Lộ trình được chia sẻ không tồn tại hoặc đã ngừng chia sẻ.'
          );
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    if (shareCode) {
      fetchSharedPath();
    }

    return () => {
      isMounted = false;
    };
  }, [shareCode]);

  const sortedNodes = useMemo(() => {
    return sortLearningPathNodes(path?.nodes, path?.edges);
  }, [path?.nodes, path?.edges]);

  function handleSelectSkill(skill) {
    setSelectedSkill(skill);
  }

  async function handleAdoptPath() {
    setCloneError('');
    setCloneSuccess('');

    // Kiểm tra đăng nhập
    if (status !== 'authenticated' || !user) {
      setShowLoginModal(true);
      return;
    }

    // Ràng buộc an toàn: Tự clone lộ trình của chính mình
    if (path.is_owner || (path.author && path.author.user_id === user.user_id)) {
      setCloneError('Đây là lộ trình của bạn. Bạn không thể tự sao chép lộ trình của chính mình.');
      return;
    }

    setIsCloning(true);
    try {
      const response = await cloneSharedLearningPath(shareCode);
      setCloneSuccess(response.message || 'Sao chép thành công!');

      // Chuyển hướng sau 1.2s để học viên thấy thông báo thành công
      setTimeout(() => {
        navigate(`/me/my-learning-path/details/${response.new_record_id}`);
      }, 1200);
    } catch (err) {
      setCloneError(
        err.response?.data?.detail ||
          'Không thể sao chép lộ trình này. Vui lòng thử lại sau.'
      );
    } finally {
      setIsCloning(false);
    }
  }

  if (isLoading) {
    return (
      <main className={styles.container}>
        <div className={styles.loadingBox}>
          <div className={styles.spinner} />
          <p>Đang tải lộ trình được chia sẻ...</p>
        </div>
      </main>
    );
  }

  if (error || !path) {
    return (
      <main className={styles.container}>
        <div className={styles.errorBox} role="alert">
          <div className={styles.errorIcon}>⚠️</div>
          <h2>Không tìm thấy lộ trình</h2>
          <p>{error || 'Lộ trình này không khả dụng hoặc đã bị thu hồi quyền truy cập.'}</p>
          <div className={styles.errorActions}>
            <Link to="/" className="btn btn-primary">
              Về trang chủ
            </Link>
            {status === 'authenticated' && (
              <Link to="/me/my-learning-path" className="btn btn-soft">
                Lộ trình của tôi
              </Link>
            )}
          </div>
        </div>
      </main>
    );
  }

  const isOwner = Boolean(path.is_owner || (user && path.author?.user_id === user.user_id));

  return (
    <main className={styles.container}>
      {/* Header bar */}
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.authorBadge}>
            <div className={styles.avatar}>
              {path.author?.avatar_url ? (
                <img
                  src={path.author.avatar_url}
                  alt={path.author.full_name}
                  className={styles.avatarImg}
                />
              ) : (
                <span>{initials(path.author?.full_name || 'EduMentor')}</span>
              )}
            </div>
            <div className={styles.authorMeta}>
              <span className={styles.sharedByLabel}>Lộ trình chia sẻ bởi</span>
              <strong className={styles.authorName}>
                {path.author?.full_name || 'Học viên ẩn danh'}
              </strong>
              {path.shared_at && (
                <span className={styles.sharedTime}>
                  Ngày chia sẻ: {formatDate(path.shared_at)}
                </span>
              )}
            </div>
          </div>

          <h1 className={styles.pathTitle}>{path.original_query}</h1>

          <div className={styles.metaTags}>
            <span className={styles.tag}>
              🎯 Mục tiêu: {path.goal_type === 'career' ? 'Nghề nghiệp' : 'Dự án'}
            </span>
            <span className={styles.tag}>
              📚 {path.nodes?.length || 0} Kỹ năng
            </span>
            <span className={styles.tagHighlight}>
              👥 {path.clone_count || 0} Học viên đã học theo
            </span>
            {isOwner && (
              <span className={styles.tagOwner}>
                ⭐ Đây là lộ trình của bạn
              </span>
            )}
          </div>
        </div>

        {/* Action button CTA at header */}
        <div className={styles.headerRight}>
          {isOwner ? (
            <div className={styles.ownerNoticeGroup}>
              <p className={styles.ownerHint}>
                Bạn đang xem bản công khai của lộ trình do chính bạn tạo.
              </p>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => navigate(`/me/my-learning-path/details/${path.record_id}`)}
              >
                Mở trong Lộ trình của tôi →
              </button>
            </div>
          ) : (
            <button
              type="button"
              className={`btn btn-primary ${styles.adoptButton}`}
              onClick={handleAdoptPath}
              disabled={isCloning}
            >
              {isCloning ? 'Đang sao chép...' : '✨ Học theo lộ trình này'}
            </button>
          )}
        </div>
      </header>

      {/* Notifications */}
      {cloneSuccess && (
        <div className={styles.alertSuccess} role="status">
          ✓ {cloneSuccess}
        </div>
      )}

      {cloneError && (
        <div className={styles.alertError} role="alert">
          {cloneError}
        </div>
      )}

      {/* Main content: Graph + Details */}
      <section className={styles.content}>
        <div className={styles.graphWrapper}>
          <div className={styles.graphInstruction}>
            💡 <span>Bấm vào từng kỹ năng trên đồ thị để xem chi tiết và các khóa học gợi ý.</span>
          </div>

          <LearningPathGraphForDetail
            learningPath={path}
            onSelectSkill={handleSelectSkill}
          />
        </div>

        <aside className={styles.sidebar}>
          {selectedSkill ? (
            <CourseRecommendation
              skill={selectedSkill}
              learningPathId={path.record_id}
            />
          ) : (
            <div className={styles.summaryBox}>
              <h3 className={styles.summaryTitle}>Danh sách kỹ năng trong lộ trình</h3>
              <p className={styles.summaryDesc}>
                Lộ trình gồm {path.nodes?.length || 0} kỹ năng được sắp xếp theo mối quan hệ tiên quyết:
              </p>

              <ol className={styles.skillList}>
                {sortedNodes.map((node, idx) => (
                  <li
                    key={node.skill_id}
                    className={styles.skillItem}
                    onClick={() =>
                      handleSelectSkill({
                        skillId: node.skill_id,
                        skillName: node.skill?.skill || `Kỹ năng #${node.skill_id}`,
                        nodeRole: node.node_role,
                        isTarget: node.is_target,
                      })
                    }
                  >
                    <span className={styles.skillNumber}>{idx + 1}</span>
                    <div className={styles.skillContent}>
                      <span className={styles.skillName}>
                        {node.skill?.skill || `Kỹ năng #${node.skill_id}`}
                      </span>
                      {node._topology?.prerequisiteNames?.length > 0 ? (
                        <span className={styles.prereqHint}>
                          ↳ Cần: {node._topology.prerequisiteNames.join(', ')}
                        </span>
                      ) : (
                        <span className={styles.foundationHint}>
                          Nền tảng khởi đầu
                        </span>
                      )}
                    </div>
                    {node.is_target && (
                      <span className={styles.targetBadge}>Mục tiêu</span>
                    )}
                  </li>
                ))}
              </ol>
            </div>
          )}
        </aside>
      </section>

      {/* Bottom Sticky Action Bar */}
      <footer className={styles.stickyFooter}>
        <div className={styles.stickyFooterInner}>
          <div className={styles.stickyFooterText}>
            <strong>{path.original_query}</strong>
            <span>
              {isOwner
                ? '⭐ Đây là lộ trình do bạn tạo'
                : 'Muốn học theo lộ trình này? Lưu ngay về tài khoản để cá nhân hóa tiến độ.'}
            </span>
          </div>

          <div className={styles.stickyFooterAction}>
            {isOwner ? (
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => navigate(`/me/my-learning-path/details/${path.record_id}`)}
              >
                Mở chỉnh sửa
              </button>
            ) : (
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleAdoptPath}
                disabled={isCloning}
              >
                {isCloning ? 'Đang sao chép...' : 'Học theo lộ trình này'}
              </button>
            )}
          </div>
        </div>
      </footer>

      {/* Modal nhắc đăng nhập khi khách click clone */}
      {showLoginModal && (
        <div
          className={styles.modalBackdrop}
          onClick={() => setShowLoginModal(false)}
        >
          <div
            className={styles.loginModal}
            role="dialog"
            aria-modal="true"
            onClick={(e) => e.stopPropagation()}
          >
            <div className={styles.loginModalIcon}>🎓</div>
            <h2>Đăng nhập để lưu lộ trình</h2>
            <p>
              Bạn cần có tài khoản EduMentor AI để sao chép lộ trình này vào mục "Lộ trình của tôi" và bắt đầu theo dõi tiến độ.
            </p>
            <div className={styles.loginModalActions}>
              <button
                type="button"
                className="btn"
                onClick={() => setShowLoginModal(false)}
              >
                Để sau
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => {
                  navigate('/login', {
                    state: { from: `/shared/learning-paths/${shareCode}` },
                  });
                }}
              >
                Đăng nhập ngay
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
