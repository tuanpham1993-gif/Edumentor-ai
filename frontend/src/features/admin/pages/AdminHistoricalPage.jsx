// Trang Quản trị dữ liệu lịch sử (/admin/historical)
import React, { useState } from 'react';
import styles from '../styles/AdminHistorical.module.css';

const INITIAL_LOGS = [
  {
    id: 1,
    time: '28/10/2026 14:20',
    filename: 'synthetic_learning_paths_v2.json',
    records: 1250,
    isSynthetic: true,
    status: 'Hoàn thành',
  },
  {
    id: 2,
    time: '15/10/2026 09:12',
    filename: 'coursera_dataset_track_2025.csv',
    records: 840,
    isSynthetic: false,
    status: 'Hoàn thành',
  },
  {
    id: 3,
    time: '02/09/2026 16:45',
    filename: 'pilot_student_history_q3.csv',
    records: 310,
    isSynthetic: false,
    status: 'Hoàn thành',
  },
];

export default function AdminHistoricalPage() {
  const [logs, setLogs] = useState(INITIAL_LOGS);
  const [isSynthetic, setIsSynthetic] = useState(true);
  const [fileName, setFileName] = useState('');

  function handleFileDrop(e) {
    e.preventDefault();
    const files = e.dataTransfer ? e.dataTransfer.files : e.target.files;
    if (files && files.length > 0) {
      setFileName(files[0].name);
    }
  }

  function handleUpload(e) {
    e.preventDefault();
    if (!fileName) {
      alert('Vui lòng chọn file CSV hoặc JSON trước khi nhập!');
      return;
    }

    const newLog = {
      id: Date.now(),
      time: 'Vừa xong',
      filename: fileName,
      records: Math.floor(Math.random() * 500) + 100,
      isSynthetic,
      status: 'Hoàn thành',
    };
    setLogs([newLog, ...logs]);
    setFileName('');
    alert(`Đã nhập thành công ${newLog.records} bản ghi từ tệp "${newLog.filename}"!`);
  }

  return (
    <>
      <div className={styles.pageHead}>
        <h1>Dữ liệu lịch sử</h1>
        <p className={styles.pageSubtitle}>
          Nhập dữ liệu lộ trình học tập lịch sử để huấn luyện và đề xuất mô hình AI.
        </p>
      </div>

      <div className={styles.importCols}>
        {/* Vùng tải lên file */}
        <div className={styles.uploadCard}>
          <h2>Nhập dữ liệu mới</h2>
          <div
            className={styles.dropZone}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
            onClick={() => document.getElementById('history-file-input').click()}
          >
            <svg
              className={styles.dropIcon}
              width="36"
              height="36"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <div>
              {fileName ? (
                <b style={{ color: 'var(--accent)' }}>{fileName}</b>
              ) : (
                <>
                  <b>Kéo thả file vào đây</b> hoặc bấm để chọn
                  <div style={{ fontSize: '12px', marginTop: '4px' }}>Hỗ trợ định dạng .csv, .json</div>
                </>
              )}
            </div>
            <input
              id="history-file-input"
              type="file"
              accept=".csv,.json"
              style={{ display: 'none' }}
              onChange={handleFileDrop}
            />
          </div>

          <label className={styles.toggleRow}>
            <input
              type="checkbox"
              checked={isSynthetic}
              onChange={(e) => setIsSynthetic(e.target.checked)}
            />
            <span>Đây là dữ liệu tổng hợp (synthetic)</span>
          </label>

          <button type="button" className={styles.submitBtn} onClick={handleUpload}>
            Bắt đầu nhập dữ liệu
          </button>
        </div>

        {/* Lịch sử các đợt import */}
        <div className={styles.logCard}>
          <h2>Lịch sử các đợt nhập</h2>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Thời gian</th>
                  <th>Tên tệp</th>
                  <th>Số bản ghi</th>
                  <th>Loại dữ liệu</th>
                  <th>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td style={{ color: 'var(--text-muted)' }}>{log.time}</td>
                    <td>
                      <b>{log.filename}</b>
                    </td>
                    <td>{log.records.toLocaleString()}</td>
                    <td>{log.isSynthetic ? 'Tổng hợp (Synthetic)' : 'Thực tế'}</td>
                    <td>
                      <span className={styles.badgeSuccess}>{log.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}
