// Modal sơ đồ quan hệ kỹ năng (FĐ Admin · F12, Screen 3)
import React, { useState } from 'react';
import styles from '../styles/AdminSkills.module.css';

const RELATION_TYPES = ['Tiên quyết', 'Mở rộng', 'Liên quan'];

export default function AdminSkillRelationModal({
  skill,
  allSkills = [],
  relations = [],
  isOpen,
  onClose,
  onSelectSkill,
  onCreateRelation,
  onUpdateRelationType,
  onDeleteRelation,
}) {
  const [toSkill, setToSkill] = useState('');
  const [relationType, setRelationType] = useState('Tiên quyết');

  if (!isOpen || !skill) return null;

  // Lấy các quan hệ đi vào kỹ năng này: X -> skill ("HỌC TRƯỚC")
  const prerequisites = relations.filter((r) => r.to === skill.name);

  // Lấy các quan hệ đi ra từ kỹ năng này: skill -> Y ("MỞ RA")
  const unlocks = relations.filter((r) => r.from === skill.name);

  function handleCreate(e) {
    e.preventDefault();
    if (!toSkill || toSkill === skill.name) return;

    onCreateRelation({
      id: `rel-${Date.now()}`,
      from: skill.name,
      to: toSkill,
      type: relationType,
    });
    setToSkill('');
  }

  return (
    <div className={styles.modalBackdrop} onClick={onClose} role="dialog" aria-modal="true">
      <div className={styles.modalDialog} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>
            Quan hệ của <b>{skill.name}</b>
          </h2>
          <button type="button" className={styles.closeBtn} onClick={onClose} aria-label="Đóng">
            ✕
          </button>
        </div>

        {/* Thanh tạo quan hệ */}
        <form className={styles.createRelationBar} onSubmit={handleCreate}>
          <div className={styles.relationCol}>
            <label>Từ</label>
            <input className={styles.relationSelect} value={skill.name} disabled />
          </div>

          <span className={styles.arrowIndicator}>➔</span>

          <div className={styles.relationCol}>
            <label>Đến</label>
            <select
              className={styles.relationSelect}
              value={toSkill}
              onChange={(e) => setToSkill(e.target.value)}
              required
            >
              <option value="">-- Chọn kỹ năng đích --</option>
              {allSkills
                .filter((s) => s.name !== skill.name)
                .map((s) => (
                  <option key={s.id} value={s.name}>
                    {s.name}
                  </option>
                ))}
            </select>
          </div>

          <div className={styles.relationCol}>
            <label>Loại</label>
            <select
              className={styles.relationSelect}
              value={relationType}
              onChange={(e) => setRelationType(e.target.value)}
            >
              {RELATION_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <button type="submit" className={styles.createBtn}>
            Tạo
          </button>
        </form>

        {/* Sơ đồ quan hệ 3 cột trực quan */}
        <div className={styles.diagramBoard}>
          {/* Cột 1: HỌC TRƯỚC */}
          <div className={styles.diagramCol}>
            <div className={styles.diagramColTitle}>HỌC TRƯỚC</div>
            {prerequisites.length === 0 ? (
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Chưa có</span>
            ) : (
              prerequisites.map((rel) => {
                const targetSkillObj = allSkills.find((s) => s.name === rel.from);
                return (
                  <div key={rel.id} className={styles.diagramNodeCard}>
                    <b
                      onClick={() => targetSkillObj && onSelectSkill(targetSkillObj)}
                      title="Bấm để xem sơ đồ quan hệ của kỹ năng này"
                    >
                      {rel.from}
                    </b>
                    <div className={styles.nodeActionRow}>
                      <select
                        className={styles.typeSelectSmall}
                        value={rel.type}
                        onChange={(e) => onUpdateRelationType(rel.id, e.target.value)}
                      >
                        {RELATION_TYPES.map((t) => (
                          <option key={t} value={t}>
                            {t}
                          </option>
                        ))}
                      </select>
                      <button
                        type="button"
                        className={styles.removeRelationBtn}
                        onClick={() => onDeleteRelation(rel.id)}
                        aria-label={`Xóa quan hệ ${rel.from}`}
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Mũi tên và Node Trung Tâm */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className={styles.diagramArrow}>➔</span>
            <div className={styles.centerNode}>{skill.name}</div>
            <span className={styles.diagramArrow}>➔</span>
          </div>

          {/* Cột 3: MỞ RA */}
          <div className={styles.diagramCol}>
            <div className={styles.diagramColTitle}>MỞ RA</div>
            {unlocks.length === 0 ? (
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Chưa có</span>
            ) : (
              unlocks.map((rel) => {
                const targetSkillObj = allSkills.find((s) => s.name === rel.to);
                return (
                  <div key={rel.id} className={styles.diagramNodeCard}>
                    <b
                      onClick={() => targetSkillObj && onSelectSkill(targetSkillObj)}
                      title="Bấm để xem sơ đồ quan hệ của kỹ năng này"
                    >
                      {rel.to}
                    </b>
                    <div className={styles.nodeActionRow}>
                      <select
                        className={styles.typeSelectSmall}
                        value={rel.type}
                        onChange={(e) => onUpdateRelationType(rel.id, e.target.value)}
                      >
                        {RELATION_TYPES.map((t) => (
                          <option key={t} value={t}>
                            {t}
                          </option>
                        ))}
                      </select>
                      <button
                        type="button"
                        className={styles.removeRelationBtn}
                        onClick={() => onDeleteRelation(rel.id)}
                        aria-label={`Xóa quan hệ ${rel.to}`}
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Chú giải */}
        <div className={styles.diagramLegend}>
          <span className={styles.legendItem}>
            <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>—</span> Tiên quyết
          </span>
          <span className={styles.legendItem}>
            <span style={{ color: '#8a8070', fontWeight: 'bold' }}>---</span> Mở rộng
          </span>
          <span className={styles.legendItem}>
            <span style={{ color: '#8a8070', fontWeight: 'bold' }}>····</span> Liên quan
          </span>
          <span style={{ marginLeft: 'auto', fontStyle: 'italic', opacity: 0.85 }}>
            Bấm tên kỹ năng để xem sơ đồ của kỹ năng đó
          </span>
        </div>
      </div>
    </div>
  );
}
