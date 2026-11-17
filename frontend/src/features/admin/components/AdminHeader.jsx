// Header chuẩn dành cho phân hệ Quản trị (Admin)
import React from 'react';
import { Link } from 'react-router-dom';
import UserMenu from '../../layout/components/UserMenu.jsx';
import styles from '../styles/AdminLayout.module.css';

export default function AdminHeader() {
  return (
    <header className={styles.header}>
      <Link to="/admin/courses" className={styles.brand}>
        <svg aria-hidden="true" width="30" height="30" viewBox="0 0 32 32">
          <path
            d="M16 3 29 10.5v11L16 29 3 21.5v-11z"
            fill="none"
            stroke="var(--accent, #f5a524)"
            strokeWidth="2.4"
          />
          <path d="M8 14l8-4 8 4-8 4z" fill="var(--accent, #f5a524)" />
          <path
            d="M11 16v4c0 1.5 2.2 3 5 3s5-1.5 5-3v-4"
            fill="none"
            stroke="var(--accent, #f5a524)"
            strokeWidth="2"
          />
        </svg>
        EduMentor AI <span className={styles.brandChip}>Quản trị</span>
      </Link>

      <UserMenu />
    </header>
  );
}
