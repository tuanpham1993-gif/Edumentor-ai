// Shell Layout chứa toàn bộ các trang Quản trị (Admin)
import React from 'react';
import { Outlet } from 'react-router-dom';
import AdminHeader from './AdminHeader.jsx';
import AdminSidebar from './AdminSidebar.jsx';
import styles from '../styles/AdminLayout.module.css';

export default function AdminLayout() {
  return (
    <div className={styles.page}>
      <AdminHeader />
      <div className={styles.body}>
        <AdminSidebar />
        <main className={styles.main}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
