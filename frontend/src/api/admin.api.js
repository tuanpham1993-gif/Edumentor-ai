// API Quản trị dành cho Admin (F11 - Khóa học & Kỹ năng)
import client from './client.js';

export const adminApi = {
  // 1. Quản trị Khóa học
  getCourses: ({ page = 1, pageSize = 10, search = '', level = '' } = {}) => {
    const params = { page, page_size: pageSize };
    if (search && search.trim()) params.search = search.trim();
    if (level && level.trim()) params.level = level.trim();
    return client.get('/admin/courses', { params }).then((res) => res.data);
  },

  getCourseDetail: (courseId) =>
    client.get(`/admin/courses/${courseId}`).then((res) => res.data),

  createCourse: (data) =>
    client.post('/admin/courses', data).then((res) => res.data),

  updateCourse: (courseId, data) =>
    client.patch(`/admin/courses/${courseId}`, data).then((res) => res.data),

  deleteCourse: (courseId) =>
    client.delete(`/admin/courses/${courseId}`).then((res) => res.data),

  // 2. Kỹ năng
  getSkills: ({ page = 1, pageSize = 100, search = '' } = {}) => {
    const params = { page, page_size: pageSize };
    if (search && search.trim()) params.search = search.trim();
    return client.get('/admin/skills', { params }).then((res) => res.data);
  },

  // 3. Quan hệ Khóa học - Kỹ năng
  addCourseSkill: (courseId, skillId) =>
    client
      .post('/admin/course-skill-relations', { course_id: courseId, skill_id: skillId })
      .then((res) => res.data),

  deleteCourseSkill: (courseId, skillId) =>
    client
      .delete(`/admin/course-skill-relations/${courseId}/${skillId}`)
      .then((res) => res.data),
};
