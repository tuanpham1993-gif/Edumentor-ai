// Trang Quản trị kỹ năng và quan hệ (/admin/skills) — F12
import React, { useState, useMemo } from 'react';
import { INITIAL_SKILLS, INITIAL_SKILL_RELATIONS } from '../data/adminMockData.js';
import AdminSkillRelationModal from '../components/AdminSkillRelationModal.jsx';
import styles from '../styles/AdminSkills.module.css';

export default function AdminSkillsPage() {
  const [skills, setSkills] = useState(INITIAL_SKILLS);
  const [relations, setRelations] = useState(INITIAL_SKILL_RELATIONS);
  const [searchQuery, setSearchQuery] = useState('');
  const [newSkillName, setNewSkillName] = useState('');
  const [selectedSkillForModal, setSelectedSkillForModal] = useState(null);

  // Lọc kỹ năng theo tìm kiếm
  const filteredSkills = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return skills;
    return skills.filter((s) => s.name.toLowerCase().includes(q));
  }, [skills, searchQuery]);

  function handleAddSkill(e) {
    e.preventDefault();
    const name = newSkillName.trim();
    if (!name) return;

    if (skills.some((s) => s.name.toLowerCase() === name.toLowerCase())) {
      alert(`Kỹ năng "${name}" đã tồn tại!`);
      return;
    }

    const newSkill = {
      id: `skill-${Date.now()}`,
      name,
      coursesCount: 0,
      relationsCount: 0,
    };
    setSkills([...skills, newSkill]);
    setNewSkillName('');
  }

  function handleDeleteSkill(skillId, skillName) {
    if (window.confirm(`Bạn có chắc chắn muốn xóa kỹ năng "${skillName}"?`)) {
      setSkills(skills.filter((s) => s.id !== skillId));
      setRelations(relations.filter((r) => r.from !== skillName && r.to !== skillName));
      if (selectedSkillForModal && selectedSkillForModal.id === skillId) {
        setSelectedSkillForModal(null);
      }
    }
  }

  function handleCreateRelation(newRel) {
    setRelations([...relations, newRel]);
    // Cập nhật số quan hệ
    setSkills(
      skills.map((s) => {
        if (s.name === newRel.from || s.name === newRel.to) {
          return { ...s, relationsCount: s.relationsCount + 1 };
        }
        return s;
      })
    );
  }

  function handleUpdateRelationType(relId, newType) {
    setRelations(relations.map((r) => (r.id === relId ? { ...r, type: newType } : r)));
  }

  function handleDeleteRelation(relId) {
    const target = relations.find((r) => r.id === relId);
    if (!target) return;

    setRelations(relations.filter((r) => r.id !== relId));
    setSkills(
      skills.map((s) => {
        if (s.name === target.from || s.name === target.to) {
          return { ...s, relationsCount: Math.max(0, s.relationsCount - 1) };
        }
        return s;
      })
    );
  }

  return (
    <>
      <h1 className={styles.pageTitle}>Kỹ năng và quan hệ kỹ năng</h1>

      <section className={styles.panel}>
        <div className={styles.panelHead}>
          <h2>Danh mục kỹ năng</h2>
          <span className={styles.panelCount}>
            {skills.length} kỹ năng · bấm một kỹ năng để xem sơ đồ quan hệ
          </span>
        </div>

        {/* Thanh công cụ: Tìm kiếm & Thêm nhanh */}
        <div className={styles.skillTools}>
          <div className={styles.searchBox}>
            <svg
              aria-hidden="true"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input
              placeholder="Tìm kỹ năng"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Tìm kỹ năng"
            />
          </div>

          <form className={styles.addForm} onSubmit={handleAddSkill}>
            <input
              className={styles.addInput}
              placeholder="Tên kỹ năng mới"
              value={newSkillName}
              onChange={(e) => setNewSkillName(e.target.value)}
              aria-label="Tên kỹ năng mới"
            />
            <button type="submit" className={styles.addBtn}>
              Thêm
            </button>
          </form>
        </div>

        {/* Lưới các thẻ kỹ năng */}
        <div className={styles.skillGrid}>
          {filteredSkills.map((sk) => (
            <div key={sk.id} className={styles.skillCard}>
              <button
                type="button"
                className={styles.skillPick}
                onClick={() => setSelectedSkillForModal(sk)}
                aria-haspopup="dialog"
              >
                <b>{sk.name}</b>
                <span className={styles.skillSub}>
                  {sk.coursesCount} khóa học · {sk.relationsCount} quan hệ
                </span>
              </button>

              <button
                type="button"
                className={styles.deleteIconBtn}
                aria-label={`Xóa ${sk.name}`}
                onClick={() => handleDeleteSkill(sk.id, sk.name)}
              >
                <svg
                  aria-hidden="true"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Modal sơ đồ quan hệ kỹ năng */}
      <AdminSkillRelationModal
        skill={selectedSkillForModal}
        allSkills={skills}
        relations={relations}
        isOpen={Boolean(selectedSkillForModal)}
        onClose={() => setSelectedSkillForModal(null)}
        onSelectSkill={(nextSkill) => setSelectedSkillForModal(nextSkill)}
        onCreateRelation={handleCreateRelation}
        onUpdateRelationType={handleUpdateRelationType}
        onDeleteRelation={handleDeleteRelation}
      />
    </>
  );
}
