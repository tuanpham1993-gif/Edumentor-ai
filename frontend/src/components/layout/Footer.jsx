// Footer cho trang cần đăng nhập (FĐ7, 08/11/2026). Bộ demo chưa có footer → bản đề xuất.
// 4 cột theo ý Tuấn: Giới thiệu · Học tập · Liên hệ · Địa chỉ. Hàng dưới: bản quyền + lên đầu trang.
//
// ⚠ CONTACT bên dưới đang là GIÁ TRỊ TẠM — điền email / số điện thoại / địa chỉ thật của nhóm.
import { Link } from 'react-router-dom';

import { BrandLogo } from '../auth/icons.jsx';
import styles from './Footer.module.css';
import { MAIN_NAV } from './nav.js';

// Thông tin liên hệ — SỬA Ở ĐÂY (chưa điền thì để nguyên, footer vẫn hiện bình thường)
const CONTACT = {
  email: 'contact@edumentor.example',
  phone: '(+84) 000 000 000',
  hours: 'Thứ 2 – Thứ 6, 8:00 – 17:00',
  address: ['Cập nhật tên trường / đơn vị', 'Cập nhật địa chỉ, quận / huyện', 'TP. Hồ Chí Minh, Việt Nam'],
  mapUrl: '', // link Google Maps (để trống → không hiện "Xem bản đồ")
};

// Cột Học tập: lấy từ menu chính (nav.js) — đổi menu thì footer đổi theo
const STUDY_PATHS = ['/courses', '/me/learning-paths', '/me/courses', '/me/review-history', '/tutor'];
const STUDY_LINKS = MAIN_NAV.filter((item) => STUDY_PATHS.includes(item.to));

const ICON = {
  'aria-hidden': true,
  width: 15,
  height: 15,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

function scrollToTop() {
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
}

/** guest: dùng ở trang chủ cho khách → logo dẫn về '/' thay vì /me */
export default function Footer({ guest = false }) {
  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        {/* Giới thiệu */}
        <section className={styles.about} aria-labelledby="ft-about">
          <Link to={guest ? '/' : '/me'} className={styles.brand}>
            <BrandLogo />
            <span>
              EduMentor <b>AI</b>
            </span>
          </Link>
          <h3 id="ft-about" className="sr-only">
            Giới thiệu
          </h3>
          <p>
            Nền tảng cố vấn học tập cá nhân hóa: lộ trình học bằng AI, gợi ý khóa học MOOC theo kỹ
            năng và ôn tập để ghi nhận kỹ năng.
          </p>
        </section>

        {/* Học tập */}
        <nav className={styles.column} aria-labelledby="ft-study">
          <h3 id="ft-study">Học tập</h3>
          {STUDY_LINKS.map((link) => (
            <Link key={link.to} to={link.to}>
              {link.text}
            </Link>
          ))}
        </nav>

        {/* Liên hệ */}
        <section className={styles.column} aria-labelledby="ft-contact">
          <h3 id="ft-contact">Liên hệ</h3>
          <a className={styles.withIcon} href={`mailto:${CONTACT.email}`}>
            <svg {...ICON}>
              <rect x="3" y="5" width="18" height="14" rx="2" />
              <path d="m3 7 9 6 9-6" />
            </svg>
            {CONTACT.email}
          </a>
          <a className={styles.withIcon} href={`tel:${CONTACT.phone.replace(/[^\d+]/g, '')}`}>
            <svg {...ICON}>
              <path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2" />
            </svg>
            {CONTACT.phone}
          </a>
          <span className={styles.note}>{CONTACT.hours}</span>
          <Link to="/contact" className={styles.cta}>
            Gửi yêu cầu hỗ trợ →
          </Link>
        </section>

        {/* Địa chỉ */}
        <section className={styles.column} aria-labelledby="ft-address">
          <h3 id="ft-address">Địa chỉ</h3>
          <address className={styles.address}>
            <svg {...ICON}>
              <path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z" />
              <circle cx="12" cy="9.5" r="2.5" />
            </svg>
            <span>
              {CONTACT.address.map((line) => (
                <span key={line}>{line}</span>
              ))}
            </span>
          </address>
          {CONTACT.mapUrl && (
            <a href={CONTACT.mapUrl} target="_blank" rel="noreferrer" className={styles.cta}>
              Xem bản đồ ↗
            </a>
          )}
        </section>
      </div>

      <div className={styles.bottom}>
        <span>© 2026 EduMentor AI · Đồ án nhóm</span>
        <button type="button" className={styles.top} onClick={scrollToTop}>
          Lên đầu trang ↑
        </button>
      </div>
    </footer>
  );
}
