// Thẻ "bắt đầu nhanh" ở hero trang chủ (FĐ7, 08/11/2026) — 2 tab Đăng ký / Đăng nhập.
// Chỉ nhận họ tên + email rồi CHUYỂN sang trang Đăng ký / Đăng nhập đầy đủ (điền sẵn).
// Lý do không đặt ô mật khẩu ở đây: quy tắc 3 trạng thái, xác nhận mật khẩu (Q3), cảnh báo
// Caps Lock… đã có ở trang chính — không chép logic hai nơi.
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { ArrowIcon, MailIcon, UserIcon } from '../../common/components/icons.jsx';
import TextField from '../../common/components/TextField.jsx';
import styles from '../styles/QuickStartCard.module.css';

const TABS = [
  { key: 'register', text: 'Đăng ký' },
  { key: 'login', text: 'Đăng nhập' },
];

export default function QuickStartCard() {
  const navigate = useNavigate();
  const [tab, setTab] = useState('register');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');

  function handleSubmit(event) {
    event.preventDefault();
    if (tab === 'register') {
      navigate('/register', { state: { fullName: fullName.trim(), email: email.trim() } });
    } else {
      navigate('/login', { state: { email: email.trim() } });
    }
  }

  const isRegister = tab === 'register';

  return (
    <div className={styles.quick}>
      <div className={styles.tabs} role="tablist" aria-label="Bắt đầu">
        <span
          className={styles.tabPill}
          style={{ transform: isRegister ? 'none' : 'translateX(100%)' }}
          aria-hidden="true"
        />
        {TABS.map((item) => (
          <button
            key={item.key}
            type="button"
            role="tab"
            aria-selected={tab === item.key}
            className={`${styles.tab} ${tab === item.key ? styles.tabActive : ''}`}
            onClick={() => setTab(item.key)}
          >
            {item.text}
          </button>
        ))}
      </div>

      <div key={tab} className={styles.quickBody}>
        <div>
          <h2>{isRegister ? 'Đăng ký tài khoản' : 'Chào mừng trở lại'}</h2>
          <p className="muted small" style={{ margin: '6px 0 0' }}>
            {isRegister
              ? 'Điền thông tin bên dưới để tạo tài khoản miễn phí.'
              : 'Nhập email để tiếp tục đăng nhập.'}
          </p>
        </div>

        <form className="stack" style={{ gap: 14 }} onSubmit={handleSubmit}>
          {isRegister && (
            <TextField
              id="qs-name"
              label="Họ và tên"
              icon={<UserIcon />}
              placeholder="Nhập họ và tên"
              autoComplete="name"
              maxLength={100}
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
            />
          )}
          <TextField
            id="qs-email"
            label="Email"
            type="email"
            icon={<MailIcon />}
            placeholder="Nhập email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <button type="submit" className="btn btn-primary btn-lg btn-block">
            {isRegister ? 'Tiếp tục đăng ký' : 'Tiếp tục đăng nhập'} <ArrowIcon />
          </button>
        </form>

        <p className="small muted" style={{ margin: 0, textAlign: 'center' }}>
          {isRegister ? 'Đã có tài khoản? ' : 'Chưa có tài khoản? '}
          <Link to={isRegister ? '/login' : '/register'} style={{ fontWeight: 600 }}>
            {isRegister ? 'Đăng nhập' : 'Đăng ký ngay'}
          </Link>
        </p>
      </div>
    </div>
  );
}
