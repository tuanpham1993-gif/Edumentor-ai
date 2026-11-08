// "Bản nháp" của trang Kỹ năng (FĐ6, 08/11/2026) — hàm thuần, không có giao diện.
//
// Người dùng đổi / gỡ nhiều kỹ năng (thêm mới: ở trang Khám phá kỹ năng), nhưng CHƯA gửi gì lên server; chỉ khi bấm
// "Lưu tất cả" mới gửi MỘT request PATCH (FR-04). Mỗi dòng trong bản nháp:
//   { skill_id, skill, status, source, updated_at,
//     original: 'known' | 'learning' | null,   ← trạng thái đang lưu trên server (null = mới thêm)
//     removed: true | false }                   ← đánh dấu gỡ (vẫn hiện, gạch ngang, có nút Khôi phục)

/** Danh sách từ server → bản nháp (chưa có thay đổi nào). */
export function draftFromServer(skills) {
  return skills.map((s) => ({ ...s, original: s.status, removed: false }));
}

/** Loại thay đổi của một dòng: 'added' | 'changed' | 'removed' | null (không đổi). */
export function changeOf(row) {
  if (row.original === null) return 'added';
  if (row.removed) return 'removed';
  if (row.status !== row.original) return 'changed';
  return null;
}

/** Bản nháp → body PATCH /me/skills { add, update, remove }. */
export function buildChanges(rows) {
  const body = { add: [], update: [], remove: [] };
  for (const row of rows) {
    const change = changeOf(row);
    if (change === 'added') body.add.push({ skill_id: row.skill_id, status: row.status });
    if (change === 'changed') body.update.push({ skill_id: row.skill_id, status: row.status });
    if (change === 'removed') body.remove.push(row.skill_id);
  }
  return body;
}

export function countChanges(rows) {
  return rows.filter((row) => changeOf(row) !== null).length;
}

export function setStatus(rows, skillId, status) {
  return rows.map((row) => (row.skill_id === skillId ? { ...row, status } : row));
}

/** Gỡ: dòng mới thêm → bỏ hẳn khỏi nháp; dòng đã lưu → đánh dấu removed (còn khôi phục được). */
export function removeSkill(rows, skillId) {
  return rows
    .filter((row) => !(row.skill_id === skillId && row.original === null))
    .map((row) => (row.skill_id === skillId ? { ...row, removed: true } : row));
}

export function restoreSkill(rows, skillId) {
  return rows.map((row) =>
    row.skill_id === skillId ? { ...row, removed: false, status: row.original } : row,
  );
}
