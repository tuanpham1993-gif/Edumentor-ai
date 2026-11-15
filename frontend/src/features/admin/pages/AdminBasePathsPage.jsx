// Trang Quản trị mẫu lộ trình cơ sở (/admin/base-paths) — F11 / F12
import React, { useState } from 'react';
import { INITIAL_BASE_PATHS, INITIAL_SKILLS } from '../data/adminMockData.js';
import AdminRoadmapCanvas from '../components/AdminRoadmapCanvas.jsx';
import styles from '../styles/AdminBasePaths.module.css';

export default function AdminBasePathsPage() {
  const [templates, setTemplates] = useState(INITIAL_BASE_PATHS);
  const [selectedTplId, setSelectedTplId] = useState('data-analyst');
  const [newSkillSelection, setNewSkillSelection] = useState('');
  const [showAddConn, setShowAddConn] = useState(false);
  const [connFrom, setConnFrom] = useState('');
  const [connTo, setConnTo] = useState('');

  const activeTpl = templates.find((t) => t.id === selectedTplId) || templates[0];

  function handleUpdateActiveTpl(partial) {
    setTemplates(
      templates.map((t) => (t.id === activeTpl.id ? { ...t, ...partial } : t))
    );
  }

  function handleCreateTemplate() {
    const newId = `tpl-${Date.now()}`;
    const newTpl = {
      id: newId,
      name: 'Mẫu lộ trình mới',
      usageCount: 0,
      skillCount: 1,
      status: 'active',
      targetGoal: 'mục tiêu nghề nghiệp mới',
      aiEnabled: true,
      nodes: [{ id: 'py', name: 'Python', role: 'target', x: 80, y: 80 }],
      skills: [{ name: 'Python', role: 'Mục tiêu' }],
      connections: [],
    };
    setTemplates([newTpl, ...templates]);
    setSelectedTplId(newId);
  }

  function handleToggleStatus() {
    const nextStatus = activeTpl.status === 'active' ? 'disabled' : 'active';
    handleUpdateActiveTpl({
      status: nextStatus,
      aiEnabled: nextStatus === 'active',
    });
  }

  function handleAddSkillToTemplate() {
    if (!newSkillSelection) return;
    if (activeTpl.skills.some((s) => s.name === newSkillSelection)) return;

    const newSkills = [...activeTpl.skills, { name: newSkillSelection, role: 'Tiên quyết' }];
    const newNodes = [
      ...activeTpl.nodes,
      {
        id: `node-${Date.now()}`,
        name: newSkillSelection,
        role: 'prerequisite',
        x: 40 + (activeTpl.nodes.length % 3) * 160,
        y: 40 + Math.floor(activeTpl.nodes.length / 3) * 70,
      },
    ];

    handleUpdateActiveTpl({
      skills: newSkills,
      nodes: newNodes,
      skillCount: newSkills.length,
    });
    setNewSkillSelection('');
  }

  function handleRemoveSkillFromTemplate(skillName) {
    const newSkills = activeTpl.skills.filter((s) => s.name !== skillName);
    const newNodes = activeTpl.nodes.filter((n) => n.name !== skillName);
    const newConnections = activeTpl.connections.filter(
      (c) => c.from !== skillName && c.to !== skillName
    );

    handleUpdateActiveTpl({
      skills: newSkills,
      nodes: newNodes,
      connections: newConnections,
      skillCount: newSkills.length,
    });
  }

  function handleAddConnection() {
    if (!connFrom || !connTo || connFrom === connTo) return;
    const exists = activeTpl.connections.some(
      (c) => c.from === connFrom && c.to === connTo
    );
    if (exists) return;

    const newConnections = [
      ...activeTpl.connections,
      { from: connFrom, to: connTo, type: 'Tiên quyết' },
    ];
    handleUpdateActiveTpl({ connections: newConnections });
    setShowAddConn(false);
    setConnFrom('');
    setConnTo('');
  }

  function handleRemoveConnection(index) {
    const newConnections = activeTpl.connections.filter((_, i) => i !== index);
    handleUpdateActiveTpl({ connections: newConnections });
  }

  function handleSaveTemplate() {
    alert(`Đã lưu thành công mẫu "${activeTpl.name}"!`);
  }

  return (
    <>
      <div className={styles.pageHead}>
        <div>
          <h1>Mẫu lộ trình cơ sở</h1>
          <p className={styles.pageSubtitle}>
            Điểm khởi đầu để AI tư vấn đề xuất lộ trình cho các mục tiêu phổ biến.
          </p>
        </div>
        <button type="button" className={styles.createTplBtn} onClick={handleCreateTemplate}>
          + Tạo mẫu mới
        </button>
      </div>

      <div className={styles.tplLayout}>
        {/* Danh sách Template bên trái */}
        <div className={styles.tplList}>
          {templates.map((tpl) => (
            <button
              key={tpl.id}
              type="button"
              className={`${styles.tplCard} ${tpl.id === activeTpl.id ? styles.tplCardActive : ''}`}
              onClick={() => setSelectedTplId(tpl.id)}
            >
              <div className={styles.tplCardTop}>
                <b>{tpl.name}</b>
                <span
                  className={
                    tpl.status === 'active' ? styles.statusBadgeActive : styles.statusBadgeDisabled
                  }
                >
                  {tpl.status === 'active' ? 'Đang dùng' : 'Đã tắt'}
                </span>
              </div>
              <span className={styles.tplSub}>
                {tpl.skillCount} kỹ năng · dùng {tpl.usageCount} lần
              </span>
            </button>
          ))}
        </div>

        {/* Khung Editor bên phải */}
        <div className={styles.editor}>
          <div className={styles.twoInputs}>
            <div className={styles.inputGroup}>
              <label htmlFor="tpl-name">Tên mẫu</label>
              <input
                id="tpl-name"
                className={styles.textInput}
                value={activeTpl.name}
                onChange={(e) => handleUpdateActiveTpl({ name: e.target.value })}
              />
            </div>

            <div className={styles.inputGroup}>
              <label htmlFor="tpl-goal">Mục tiêu phù hợp</label>
              <input
                id="tpl-goal"
                className={styles.textInput}
                value={activeTpl.targetGoal}
                onChange={(e) => handleUpdateActiveTpl({ targetGoal: e.target.value })}
              />
            </div>
          </div>

          {/* Toggle đang dùng cho AI tư vấn */}
          <div className={styles.toggleRow}>
            <button
              type="button"
              role="switch"
              aria-checked={activeTpl.aiEnabled}
              className={`${styles.toggleSwitch} ${
                activeTpl.aiEnabled ? styles.toggleSwitchActive : ''
              }`}
              onClick={() => handleUpdateActiveTpl({ aiEnabled: !activeTpl.aiEnabled })}
            >
              <span className={styles.toggleKnob} />
            </button>
            <span className={styles.toggleLabel}>Đang dùng cho AI tư vấn</span>
          </div>

          {/* Visual Graph Preview */}
          <AdminRoadmapCanvas
            nodes={activeTpl.nodes}
            connections={activeTpl.connections}
            width={640}
            height={220}
            mode="template"
          />

          {/* Chi tiết kỹ năng và kết nối */}
          <div className={styles.detailsGrid}>
            {/* Cột kỹ năng trong mẫu */}
            <div className={styles.detailCol}>
              <h3 className={styles.detailColTitle}>Kỹ năng trong mẫu</h3>
              {activeTpl.skills.length === 0 ? (
                <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Chưa có kỹ năng</span>
              ) : (
                activeTpl.skills.map((s) => (
                  <div key={s.name} className={styles.listRow}>
                    <span className={styles.rowName}>{s.name}</span>
                    <div className={styles.rowMeta}>
                      <span className={styles.roleTag}>{s.role}</span>
                      <button
                        type="button"
                        className={styles.removeBtn}
                        onClick={() => handleRemoveSkillFromTemplate(s.name)}
                        aria-label={`Xóa ${s.name}`}
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))
              )}

              <div className={styles.addRowTool}>
                <select
                  className={styles.smallSelect}
                  value={newSkillSelection}
                  onChange={(e) => setNewSkillSelection(e.target.value)}
                >
                  <option value="">Thêm kỹ năng...</option>
                  {INITIAL_SKILLS.filter(
                    (isk) => !activeTpl.skills.some((s) => s.name === isk.name)
                  ).map((isk) => (
                    <option key={isk.id} value={isk.name}>
                      {isk.name}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  className={styles.smallBtn}
                  onClick={handleAddSkillToTemplate}
                >
                  Thêm
                </button>
              </div>
            </div>

            {/* Cột kết nối */}
            <div className={styles.detailCol}>
              <h3 className={styles.detailColTitle}>Kết nối</h3>
              {activeTpl.connections.length === 0 ? (
                <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Chưa có kết nối</span>
              ) : (
                activeTpl.connections.map((c, i) => (
                  <div key={`conn-${i}`} className={styles.listRow}>
                    <span className={styles.rowName}>
                      {c.from} → {c.to}
                    </span>
                    <div className={styles.rowMeta}>
                      <span className={styles.roleTag}>{c.type}</span>
                      <button
                        type="button"
                        className={styles.removeBtn}
                        onClick={() => handleRemoveConnection(i)}
                        aria-label={`Xóa kết nối ${c.from} tới ${c.to}`}
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))
              )}

              {!showAddConn ? (
                <button
                  type="button"
                  className={styles.addConnBtn}
                  onClick={() => setShowAddConn(true)}
                >
                  + Thêm kết nối
                </button>
              ) : (
                <div style={{ display: 'flex', gap: '6px', alignItems: 'center', marginTop: '6px' }}>
                  <select
                    className={styles.smallSelect}
                    value={connFrom}
                    onChange={(e) => setConnFrom(e.target.value)}
                  >
                    <option value="">Từ...</option>
                    {activeTpl.skills.map((s) => (
                      <option key={s.name} value={s.name}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                  <span style={{ color: 'var(--text-muted)' }}>➔</span>
                  <select
                    className={styles.smallSelect}
                    value={connTo}
                    onChange={(e) => setConnTo(e.target.value)}
                  >
                    <option value="">Đến...</option>
                    {activeTpl.skills
                      .filter((s) => s.name !== connFrom)
                      .map((s) => (
                        <option key={s.name} value={s.name}>
                          {s.name}
                        </option>
                      ))}
                  </select>
                  <button type="button" className={styles.smallBtn} onClick={handleAddConnection}>
                    Lưu
                  </button>
                  <button
                    type="button"
                    className={styles.removeBtn}
                    onClick={() => setShowAddConn(false)}
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Footer nút hành động */}
          <div className={styles.editorFooter}>
            <button
              type="button"
              className={styles.disableBtn}
              onClick={handleToggleStatus}
            >
              {activeTpl.status === 'active' ? 'Ngừng dùng mẫu' : 'Bật lại mẫu'}
            </button>
            <button
              type="button"
              className={styles.saveTplBtn}
              onClick={handleSaveTemplate}
            >
              Lưu mẫu
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
