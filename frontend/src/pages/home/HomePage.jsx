// Trang chủ cho KHÁCH (chưa đăng nhập) — FĐ7, 08/11/2026, theo mockup Tuấn gửi.
//   Header khách · Hero (giới thiệu + thẻ bắt đầu nhanh) · Cách hoạt động (3 bước) · Tính năng (6)
//   · Lộ trình mẫu · Khóa học nổi bật · Tin nổi bật · Kêu gọi đăng ký · Footer (dùng chung)
// Đã đăng nhập mà vào "/" → PublicRoute chuyển về /me. Header khách: components/layout/PublicHeader.
// Các khối hiện dần khi cuộn tới (data-reveal); người dùng chọn giảm chuyển động → hiện ngay.
import { useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';

import AuthScene from '../../components/auth/AuthScene.jsx';
import { ArrowIcon } from '../../components/auth/icons.jsx';
import Footer from '../../components/layout/Footer.jsx';
import PublicHeader from '../../components/layout/PublicHeader.jsx';
import HomeIcon from './HomeIcon.jsx';
import styles from './HomePage.module.css';
import {
  FEATURED_COURSES,
  FEATURES,
  HERO_POINTS,
  NEWS,
  SAMPLE_PATH,
  STEPS,
} from './homeContent.js';
import QuickStartCard from './QuickStartCard.jsx';

const STEP_LABEL = { done: 'Hoàn thành', current: 'Đang học', todo: 'Chưa bắt đầu' };

function SectionHead({ eyebrow, title, children, center = true }) {
  return (
    <div className={`${styles.sectionHead} ${center ? styles.center : ''}`} data-reveal>
      <span className={styles.eyebrow}>{eyebrow}</span>
      <h2>{title}</h2>
      {children && <p>{children}</p>}
    </div>
  );
}

export default function HomePage() {
  const rootRef = useRef(null);
  const { hash } = useLocation();

  // Đến từ trang khác qua "/#courses"… → cuộn tới phần đó
  useEffect(() => {
    if (!hash) return;
    const el = document.getElementById(hash.slice(1));
    if (el) requestAnimationFrame(() => el.scrollIntoView({ block: 'start' }));
  }, [hash]);

  // Hiện dần khi cuộn tới
  useEffect(() => {
    const root = rootRef.current;
    if (!root || !('IntersectionObserver' in window)) return undefined; // không hỗ trợ → hiện luôn
    const nodes = root.querySelectorAll('[data-reveal]');
    root.classList.add(styles.revealReady);
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add(styles.shown);
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '0px 0px -8% 0px' },
    );
    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, []);

  const doneCount = SAMPLE_PATH.steps.filter((step) => step.state === 'done').length;

  return (
    <div ref={rootRef} className={styles.page}>
      <PublicHeader />

      {/* ---------- Hero ---------- */}
      <section id="top" className={styles.hero}>
        <AuthScene variant="ambient" />
        <div className={`${styles.wrap} ${styles.heroGrid}`}>
          <div className={styles.heroCopy}>
            <span className={styles.badge}>
              <span className={styles.badgeDot} />
              Nền tảng học tập cá nhân hóa bằng AI
            </span>
            <h1>
              Học đúng hướng,
              <br />
              <span>tiến bộ mỗi ngày.</span>
            </h1>
            <p className={styles.lead}>
              EduMentor AI giúp bạn học tập hiệu quả với lộ trình cá nhân hóa thông minh, gợi ý
              đúng khóa học và ghi nhận kỹ năng sau mỗi bài ôn tập.
            </p>
            <ul className={styles.points}>
              {HERO_POINTS.map((point) => (
                <li key={point.text}>
                  <span className={styles.pointIcon}>
                    <HomeIcon name={point.icon} size={15} />
                  </span>
                  {point.text}
                </li>
              ))}
            </ul>
            <div className={styles.heroActions}>
              <Link to="/register" className="btn btn-primary btn-lg">
                Bắt đầu miễn phí <ArrowIcon />
              </Link>
              <a href="#how" className="btn btn-lg">
                Xem cách hoạt động
              </a>
            </div>
          </div>

          <QuickStartCard />
        </div>
      </section>

      {/* ---------- Cách hoạt động ---------- */}
      <section id="how" className={`${styles.section} ${styles.alt}`}>
        <div className={styles.wrap}>
          <SectionHead eyebrow="Cách hoạt động" title="Bắt đầu chỉ với 3 bước">
            Từ lúc tạo tài khoản đến khi kỹ năng được ghi nhận, EduMentor AI dẫn bạn đi từng bước.
          </SectionHead>
          <ol className={styles.steps}>
            {STEPS.map((step, index) => (
              <li
                key={step.title}
                className={`card ${styles.stepCard}`}
                data-reveal
                style={{ transitionDelay: `${index * 80}ms` }}
              >
                <span className={styles.stepNo}>{index + 1}</span>
                <h3>{step.title}</h3>
                <p>{step.text}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* ---------- Tính năng ---------- */}
      <section id="features" className={styles.section}>
        <div className={styles.wrap}>
          <SectionHead eyebrow="Tính năng" title="Mọi thứ bạn cần để học hiệu quả" />
          <div className={styles.features}>
            {FEATURES.map((feature, index) => (
              <article
                key={feature.title}
                className={`card ${styles.featureCard}`}
                data-reveal
                style={{ transitionDelay: `${(index % 3) * 70}ms` }}
              >
                <span className={styles.featureIcon}>
                  <HomeIcon name={feature.icon} />
                </span>
                <h3>{feature.title}</h3>
                <p>{feature.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ---------- Lộ trình mẫu ---------- */}
      <section id="about" className={`${styles.section} ${styles.alt}`}>
        <div className={`${styles.wrap} ${styles.pathGrid}`}>
          <div data-reveal>
            <SectionHead eyebrow="Lộ trình học" title="Một lộ trình được thiết kế cho riêng bạn" center={false}>
              Lộ trình chia thành từng khóa học rõ ràng. Hoàn thành bài ôn tập của khóa trước để mở
              khóa tiếp theo.
            </SectionHead>
            <Link to="/register" className={`btn ${styles.outlineAccent}`}>
              Tạo lộ trình của tôi <ArrowIcon />
            </Link>
          </div>

          <div className={`card ${styles.pathCard}`} data-reveal>
            <div className="between">
              <div>
                <span className="small muted">Ví dụ lộ trình</span>
                <h3>{SAMPLE_PATH.title}</h3>
              </div>
              <span className="chip chip-accent">
                {doneCount}/{SAMPLE_PATH.steps.length} khóa
              </span>
            </div>
            <div className={styles.progress}>
              <span style={{ width: `${((doneCount + 0.5) / SAMPLE_PATH.steps.length) * 100}%` }} />
            </div>
            <ol className={styles.pathSteps}>
              {SAMPLE_PATH.steps.map((step, index) => (
                <li key={step.name} className={styles[step.state]}>
                  <span className={styles.pathDot}>{step.state === 'done' ? '✓' : index + 1}</span>
                  <span className={styles.pathName}>{step.name}</span>
                  <span className={styles.pathState}>{STEP_LABEL[step.state]}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>

      {/* ---------- Khóa học nổi bật ---------- */}
      <section id="courses" className={styles.section}>
        <div className={styles.wrap}>
          <div className={styles.headRow}>
            <SectionHead eyebrow="Khóa học" title="Khóa học nổi bật" center={false} />
            <Link to="/courses" className={styles.moreLink} data-reveal>
              Xem tất cả khóa học <ArrowIcon />
            </Link>
          </div>
          <div className={styles.courses}>
            {FEATURED_COURSES.map((course, index) => (
              <article
                key={course.title}
                className={`card ${styles.courseCard}`}
                data-reveal
                style={{ transitionDelay: `${index * 80}ms` }}
              >
                <div className={styles.courseThumb}>
                  <HomeIcon name="book" size={34} />
                </div>
                <div className={styles.courseBody}>
                  <span className={`chip chip-${course.tone}`}>{course.level}</span>
                  <h3>{course.title}</h3>
                  <p>{course.text}</p>
                  <Link to="/courses" className={styles.courseLink}>
                    Xem khóa học <ArrowIcon />
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ---------- Tin nổi bật ---------- */}
      <section id="news" className={`${styles.section} ${styles.alt}`}>
        <div className={styles.wrap}>
          <SectionHead eyebrow="Tin tức" title="Tin nổi bật" center={false} />
          <div className={styles.news}>
            {NEWS.map((item, index) => (
              <article
                key={item.title}
                className={`card ${styles.newsCard}`}
                data-reveal
                style={{ transitionDelay: `${index * 80}ms` }}
              >
                <div className={styles.newsMeta}>
                  <span className={styles.newsTag}>
                    <HomeIcon name="news" size={13} />
                    {item.tag}
                  </span>
                  <span>{item.date}</span>
                </div>
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ---------- Kêu gọi đăng ký ---------- */}
      <section className={styles.section}>
        <div className={styles.wrap}>
          <div className={styles.cta} data-reveal>
            <div>
              <h2>Sẵn sàng bắt đầu hành trình học tập?</h2>
              <p>Tạo tài khoản miễn phí và nhận lộ trình đầu tiên của bạn.</p>
            </div>
            <Link to="/register" className="btn btn-primary btn-lg">
              Đăng ký ngay <ArrowIcon />
            </Link>
          </div>
        </div>
      </section>

      <Footer guest />
    </div>
  );
}
