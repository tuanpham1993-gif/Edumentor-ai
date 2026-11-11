// Khung trang Đăng nhập / Đăng ký (FĐ3, theo màn demo Main-LampOff / Register).
//
// Mở trang: 3 đèn TẮT, form ẩn và bị khóa. Kéo dây ở đèn đầu tiên → cả 3 đèn sáng, form hiện.
// Kéo lần nữa → tắt. Cảnh 3D ánh sáng (AuthScene, FĐ7 08/11) sáng / tối theo đèn. Thẻ `children` là nội dung bên trong thẻ form (do từng trang truyền vào).
//
// Trạng thái đèn được NHỚ trong sessionStorage (theo tab): kéo 1 lần ở Đăng nhập thì sang
// Đăng ký / Quên mật khẩu đèn vẫn sáng. Tab mới hoặc mở lại trình duyệt → đèn tắt như demo.
//
//   cardClassName : thêm class cho thẻ (vd "shake" khi đăng nhập sai)
//   onCardAnimationEnd : gỡ class "shake" khi rung xong để lần sai sau rung lại được
import { useEffect, useRef, useState } from 'react';

import cardStyles from '../styles/AuthCard.module.css';
import styles from '../styles/AuthLayout.module.css';
import PublicHeader from '../../layout/components/PublicHeader.jsx';
import { CheckCircleIcon } from '../../common/components/icons.jsx';
import AuthScene from './AuthScene.jsx';
import Lamp from './Lamp.jsx';

const LAMP_KEY = 'em-lamp-on';

function readLampOn() {
  try {
    return sessionStorage.getItem(LAMP_KEY) === '1';
  } catch {
    return false; // trình duyệt chặn storage → mặc định đèn tắt
  }
}

function saveLampOn(on) {
  try {
    sessionStorage.setItem(LAMP_KEY, on ? '1' : '0');
  } catch {
    // Bị chặn: chỉ không nhớ được giữa các trang, không ảnh hưởng gì khác.
  }
}

const FEATURES = [
  'Lộ trình học do AI đề xuất theo mục tiêu',
  'Gợi ý khóa học theo từng kỹ năng',
  'Ôn tập 15 câu để ghi nhận kỹ năng',
];

export default function AuthLayout({ children, cardClassName = '', onCardAnimationEnd }) {
  const [lampOn, setLampOn] = useState(readLampOn); // đọc trạng thái đã nhớ (chỉ lần đầu vẽ)
  const [flashKey, setFlashKey] = useState(0); // > 0 và đổi → lóe sáng; 0 = không lóe (vào trang khi đèn đã sáng)
  const cardRef = useRef(null);

  // Đèn tắt: thẻ form không bấm / Tab được (inert). React 18 chưa hỗ trợ prop `inert` → đặt bằng ref.
  useEffect(() => {
    const card = cardRef.current;
    if (!card) return;
    if (lampOn) card.removeAttribute('inert');
    else card.setAttribute('inert', '');
  }, [lampOn]);

  function toggleLamp() {
    const next = !lampOn;
    if (next) setFlashKey((key) => key + 1); // vừa bật → lóe sáng
    setLampOn(next);
    saveLampOn(next);
  }

  return (
    <>
      {/* Header khách (logo + Trang chủ / Khóa học / Tính năng / Về chúng tôi) — 08/11 */}
      <PublicHeader />
      <div className={`${styles.split} ${lampOn ? '' : styles.splitOff}`}>
      <aside className={`${styles.hero} ${lampOn ? '' : styles.dark}`}>
        {/* Cảnh 3D ánh sáng (FĐ7): sáng khi bật đèn, tối mờ khi tắt */}
        <AuthScene variant="hero" on={lampOn} />
        <Lamp on={lampOn} right={300} cord={120} glowTop={-30} delay={0} onPull={toggleLamp} />
        <div className={styles.hideOnPhone}>
          <Lamp on={lampOn} right={150} cord={220} glowTop={70} delay={-1.8} />
          <Lamp on={lampOn} right={30} cord={70} glowTop={-80} delay={-3.1} />
        </div>

        <div className={styles.copy}>
          <h2>
            Học đúng hướng,
            <br />
            <span>tiến bộ mỗi ngày.</span>
          </h2>
          <p>
            EduMentor AI gợi ý lộ trình theo mục tiêu, kết nối khóa học MOOC phù hợp và ghi nhận
            kỹ năng qua bài ôn tập.
          </p>
          <div className={styles.features}>
            {FEATURES.map((text) => (
              <span key={text}>
                <CheckCircleIcon />
                {text}
              </span>
            ))}
          </div>
          <span className={styles.lampState} aria-live="polite">
            {lampOn ? 'Kéo dây đèn lần nữa để tắt cả 3 đèn' : 'Đèn đang tắt · kéo dây đèn để mở trang'}
          </span>
          <span className={styles.copyright}>© 2026 EduMentor AI</span>
        </div>
      </aside>

      <main className={`${styles.formSide} ${lampOn ? '' : styles.formDark}`}>
        <AuthScene variant="ambient" on={lampOn} />
        <div className={styles.stage}>
          <div
            ref={cardRef}
            className={`${cardStyles.card} ${lampOn ? '' : styles.cardOff} ${cardClassName}`}
            aria-hidden={!lampOn}
            onAnimationEnd={(event) => {
              // Chỉ nhận hiệu ứng của CHÍNH thẻ (vd rung); hiệu ứng của phần tử con cũng "nổi bọt" lên đây.
              if (event.target === event.currentTarget) onCardAnimationEnd?.(event);
            }}
          >
            {lampOn && flashKey > 0 && (
              <div key={flashKey} className={styles.flash} aria-hidden="true" />
            )}
            {children}
          </div>
          <p className={`${styles.darkHint} ${lampOn ? '' : styles.darkHintOn}`} aria-hidden={lampOn}>
            Trời tối quá, không thấy gì cả.
            <br />
            Kéo dây đèn để bật đèn và mở trang.
          </p>
        </div>
      </main>
    </div>
    </>
  );
}
