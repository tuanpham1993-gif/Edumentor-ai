// Hàm định dạng dùng chung (FĐ2).

/** "Phạm Thanh Tuấn" → "PT" (chữ cái đầu của từ đầu và từ cuối) — avatar khi chưa có ảnh. */
export function initials(fullName) {
  const parts = String(fullName ?? '').trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '?';
  const first = parts[0][0];
  const last = parts.length > 1 ? parts[parts.length - 1][0] : '';
  return (first + last).toUpperCase();
}

/** "2026-11-05T16:01:17Z" → "05/11/2026" (giờ Việt Nam). */
export function formatDate(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  return date.toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: 'Asia/Ho_Chi_Minh',
  });
}

/** "2026-11-09T13:41:00Z" → "09/11/2026 20:41" (giờ Việt Nam) — ôn tập (09, GĐ4). */
export function formatDateTime(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
      timeZone: 'Asia/Ho_Chi_Minh',
    })
      .formatToParts(date)
      .map((p) => [p.type, p.value]),
  );
  return `${parts.day}/${parts.month}/${parts.year} ${parts.hour}:${parts.minute}`;
}

/** Thời gian tương đối kiểu Facebook: "Vừa xong", "5 phút trước", "3 giờ trước", "2 ngày trước";
 *  quá 7 ngày → ngày dd/mm/yyyy (chuông thông báo, 11/11). */
export function timeAgo(iso, now = Date.now()) {
  const time = new Date(iso).getTime();
  if (Number.isNaN(time)) return '';
  const seconds = Math.max(0, Math.floor((now - time) / 1000));
  if (seconds < 60) return 'Vừa xong';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} phút trước`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} giờ trước`;
  const days = Math.floor(hours / 24);
  if (days <= 7) return `${days} ngày trước`;
  return formatDate(iso);
}

/** "student" → "Học viên", "admin" → "Quản trị viên". */
export function roleLabel(role) {
  return role === 'admin' ? 'Quản trị viên' : 'Học viên';
}
