
import { useEffect, useMemo, useRef, useState } from 'react';
import styles from "../../styles/AddNodeModal.module.css";
import { getSkills } from '../../../../api/skill.api.js';
import { addLearningPathNode } from '../../../../api/learningPaths.api';
const RELATION_OPTIONS = [
  { value: '', label: 'Không có' },
  { value: 'prerequisite', label: 'Tiên quyết' },
  { value: 'related', label: 'Liên quan' },
  { value: 'extension', label: 'Mở rộng' },
];

const PAGE_SIZE = 50;

export default function AddNodeModal({
  recordId,
  nodes = [],
  onClose,
  onSuccess,
}) {
  // Available skills from the database.
  const [skills, setSkills] = useState([]);

  // Skills returned by remote search.
  const [remoteResults, setRemoteResults] = useState([]);

  // Search input.
  const [searchText, setSearchText] = useState('');

  // Selected skill to insert.
  const [selectedSkill, setSelectedSkill] = useState(null);

  // Existing learning-path node to insert before.
  const [insertBeforeSkillId, setInsertBeforeSkillId] = useState('');

  // Relationships for the inserted node.
  const [relationToCurrent, setRelationToCurrent] = useState('');
  const [relationToNext, setRelationToNext] = useState('');

  // Loading states.
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  // Error message.
  const [error, setError] = useState('');

  // Total skills available in the database.
  const [totalSkills, setTotalSkills] = useState(0);

  const [isSkillDropdownOpen, setIsSkillDropdownOpen] = useState(false);
  const skillPickerRef = useRef(null);
  // -----------------------------------------
  // 2. Load initial skills
  // -----------------------------------------

  useEffect(() => {
    let isMounted = true;

    async function loadSkills() {
      setSearching(true);
      setError('');

      try {
        const response = await getSkills({skip: 0, limit: PAGE_SIZE});
        if (!isMounted) return;
        const result = response.data;
        setSkills(result.data);
        setTotalSkills(result.total);
      } catch (err) {
        setError('Không tải được danh sách kỹ năng.');
        if (!isMounted) return;
      } finally {
        if (isMounted) {
          setSearching(false);
        }
      }
    }
    loadSkills();
    return () => { isMounted = false; };
  }, []);

  useEffect(() => {
  function handleOutsideClick(event) {
    if (skillPickerRef.current &&
      !skillPickerRef.current.contains(event.target)) {
      setIsSkillDropdownOpen(false);
    }
  }

  document.addEventListener('mousedown', handleOutsideClick);

  return () => {
    document.removeEventListener('mousedown', handleOutsideClick);
  };
  }, []);

  // -----------------------------------------
  // 3. Search locally first
  // -----------------------------------------

  const localResults = useMemo(() => {
    const keyword = searchText.trim().toLowerCase();
    if (!keyword) return [];
    return skills.filter((item) =>
      item.skill.toLowerCase().includes(keyword)
    );
  }, [skills, searchText]);

  // -----------------------------------------
  // 4. Search backend if no local results
  // -----------------------------------------

  useEffect(() => {
    const keyword = searchText.trim();
    // No search keyword: clear remote results.
    if (!keyword || localResults.length > 0) {
      setRemoteResults([]);
      setSearching(false);
      return;
    }
    let isCurrentRequest = true;
    const timeoutId = setTimeout(async () => {
      setSearching(true);
      try {
        const response = await getSkills({
          keyword,
          skip: 0,
          limit: PAGE_SIZE,
        });

        if (!isCurrentRequest) return;

        setRemoteResults(response.data.data);
      } catch (err) {
        if (!isCurrentRequest) return;

        setRemoteResults([]);
      } finally {
        if (isCurrentRequest) {
          setSearching(false);
        }
      }
    }, 350);

    return () => {
      isCurrentRequest = false;
      clearTimeout(timeoutId);
    };
  }, [searchText, localResults.length]);

  // -----------------------------------------
  // 5. Determine displayed search results
  // -----------------------------------------

  const displayedSkills = searchText.trim()
    ? localResults.length > 0
      ? localResults
      : remoteResults
    : skills;

  // -----------------------------------------
  // 6. Select a skill
  // -----------------------------------------

  function handleSelectSkill(skill) {
    setSelectedSkill(skill);
    setSearchText(skill.skill);
    setIsSkillDropdownOpen(false);
    setRemoteResults([]);
    setError('');
  }

  // -----------------------------------------
  // 7. Load more skills
  // -----------------------------------------

  async function handleShowMore() {
    if (loadingMore || skills.length >= totalSkills) return;

    setLoadingMore(true);
    setError('');

    try {
      const response = await getSkills({
        skip: skills.length,
        limit: PAGE_SIZE,
      });

      const result = response.data;

      setSkills((previous) => [
        ...previous,
        ...result.data,
      ]);

      setTotalSkills(result.total);
    } catch (err) {
      setError('Không tải thêm được kỹ năng.');
    } finally {
      setLoadingMore(false);
    }
  }

  // -----------------------------------------
  // 8. Determine the next existing node
  // -----------------------------------------

  const orderedNodes = useMemo(() => {
    return [...nodes].sort(
      (a, b) => a.display_order - b.display_order
    );
  }, [nodes]);

  const selectedAnchorIndex = orderedNodes.findIndex(
    (node) =>
      String(node.skill_id ?? node.skillId) ===
      String(insertBeforeSkillId)
  );

  const nextNode =
    selectedAnchorIndex >= 0
      ? orderedNodes[selectedAnchorIndex + 1] ?? null
      : null;

  // -----------------------------------------
  // 9. Handle insertion position
  // -----------------------------------------

  function handleInsertBeforeChange(event) {
    setInsertBeforeSkillId(event.target.value);

    // Changing the anchor changes the meaning of
    // both relationship selections.
    setRelationToCurrent('');
    setRelationToNext('');

    setError('');
  }

  // -----------------------------------------
  // 10. Submit Add Node request
  // -----------------------------------------

  async function handleSubmit(event) {
    event.preventDefault();

    if (!selectedSkill) {
      setError('Vui lòng chọn một kỹ năng.');
      return;
    }

    if (!insertBeforeSkillId) {
      setError('Vui lòng chọn vị trí chèn.');
      return;
    }

    if (!recordId) {
      setError('Thiếu mã lộ trình.');
      return;
    }

    const payload = {
      skill_id: selectedSkill.skill_id,

      insert_before_skill_id: Number(insertBeforeSkillId),

      relation_to_current: relationToCurrent || null,

      relation_to_next: nextNode
        ? relationToNext || null
        : null,

      node_role: null,

      is_target: false,

      is_required: false,
    };

    setLoading(true);
    setError('');

    try {
      await addLearningPathNode(recordId, payload);

      // Refresh the learning path in the parent component.
      await onSuccess?.(recordId);

      // Close only after successful insertion.
      onClose();

    } catch (err) {
      const message =
        err.response?.data?.detail ||
        'Không thêm được kỹ năng này vào lộ trình.';

      // Keep modal open so the user can fix the problem.
      setError(message);

    } finally {
      setLoading(false);
    }
  }

  return (
<div
  className={styles.modalOverlayNodemodal}
  onMouseDown={(event) => {
    if (event.target === event.currentTarget && !loading) {
      onClose();
    }
  }}>
  <div
    className={styles.addNodeModalNodemodal}
    role="dialog"
    aria-modal="true"
    aria-labelledby="addNodeTitle"
  >
    {/* Modal header */}
    <div className={styles.modalHeaderNodemodal}>
      <h2 id="addNodeTitle">
        Thêm kỹ năng mới
      </h2>

      <button
        type="button"
        className={styles.closeButtonNodemodal}
        onClick={onClose}
        disabled={loading}
        aria-label="Đóng"
      >
        &times;
      </button>
    </div>

    <form
      className={styles.modalFormNodemodal}
      onSubmit={handleSubmit}
    >

          
      {/* Skill picker: searchable input + dropdown */}
      <div
        className={styles.skillPickerNodemodal}
        ref={skillPickerRef}
      >
        <label
          htmlFor="skillSearch"
          className={styles.fieldLabelNodemodal}
        >
          Chọn kỹ năng
        </label>

        <div className={styles.skillSearchWrapperNodemodal}>
          <input
            id="skillSearch"
            type="text"
            className={styles.skillSearchInputNodemodal}
            placeholder="Tìm hoặc chọn kỹ năng..."
            value={searchText}
            onFocus={() => setIsSkillDropdownOpen(true)}
            onClick={() => setIsSkillDropdownOpen(true)}
            onChange={(event) => {
              setSearchText(event.target.value);
              setSelectedSkill(null);
              setIsSkillDropdownOpen(true);
              setError('');
            }}
            disabled={loading}
            autoComplete="off"
            aria-expanded={isSkillDropdownOpen}
            aria-controls="skill-options"
            role="combobox"
            aria-autocomplete="list"
          />

          <button
            type="button"
            className={styles.dropdownToggleNodemodal}
            onClick={() => {
              setIsSkillDropdownOpen((previous) => !previous);
            }}
            disabled={loading}
            aria-label="Mở / đóng danh sách kỹ năng"
          >
            <span className={isSkillDropdownOpen ? styles.arrowUpNodemodal : ''}>
              ▼
            </span>
          </button>
        </div>

        {/* Selected skill indicator */}
        {selectedSkill && (
          <div className={styles.selectedSkillTagNodemodal}>
            <span>Selected:</span>
            <strong>{selectedSkill.skill}</strong>
            <span className={styles.selectedCheckNodemodal}>✓</span>
          </div>
        )}

        {/* Dropdown */}
        {isSkillDropdownOpen && (
          <div
            className={styles.skillDropdownNodemodal}
            id="skill-options"
            role="listbox"
            aria-label="Kỹ năng có sẵn"
          >
            <div className={styles.dropdownHeadingNodemodal}>
              <span>
                {searchText.trim() ? 'Kết quả tìm kiếm' : 'Kỹ năng có sẵn'}
              </span>

              <span className={styles.skillCountNodemodal}>
                {searchText.trim()
                  ? displayedSkills.length
                  : `${skills.length} loaded`}
              </span>
            </div>

            <div className={styles.skillOptionsNodemodal}>
              {searching ? (
                <p className={styles.dropdownMessageNodemodal}>
                  Đang tìm kỹ năng...
                </p>
              ) : displayedSkills.length > 0 ? (
                displayedSkills.map((skill) => (
                  <button
                    key={skill.skill_id}
                    type="button"
                    role="option"
                    aria-selected={
                      selectedSkill?.skill_id === skill.skill_id
                    }
                    className={`${styles.skillOptionNodemodal} ${
                      selectedSkill?.skill_id === skill.skill_id
                        ? styles.skillOptionSelectedNodemodal
                        : ''
                    }`}
                    onClick={() => handleSelectSkill(skill)}
                    disabled={loading}
                  >
                    <span>{skill.skill}</span>

                    {selectedSkill?.skill_id === skill.skill_id && (
                      <span className={styles.optionCheckNodemodal}>✓</span>
                    )}
                  </button>
                ))
              ) : searchText.trim() ? (
                <p className={styles.dropdownMessageNodemodal}>
                  Không tìm thấy kỹ năng này.
                </p>
              ) : (
                <p className={styles.dropdownMessageNodemodal}>
                  Không có kỹ năng nào.
                </p>
              )}
            </div>

            {/* Load next 50 skills when browsing */}
            {!searchText.trim() && skills.length < totalSkills && (
              <button
                type="button"
                className={styles.loadMoreSkillsNodemodal}
                onClick={handleShowMore}
                disabled={loadingMore || loading}
              >
                {loadingMore
                  ? 'Đang tải kỹ năng...'
                  : `Show next 50 skills (${skills.length}/${totalSkills})`}
              </button>
            )}
          </div>
        )}
      </div>


      {/* -------------------------------- */}
      {/* Chèn trước */}
      {/* -------------------------------- */}

      <div className={styles.formGroupNodemodal}>
        <label htmlFor="insertBefore">
          Chèn trước
        </label>

        <select
          id="insertBefore"
          value={insertBeforeSkillId}
          onChange={handleInsertBeforeChange}
          disabled={loading || orderedNodes.length === 0}
        >
          <option value="">
            Chọn một kỹ năng trong lộ trình
          </option>

          {orderedNodes.map((node) => {
            const skillId = node.skill_id ?? node.skillId;

            const skillName =
              typeof node.skill === 'object'
                ? node.skill?.skill
                : node.skill ?? node.skill_name;

            return (
              <option
                key={skillId}
                value={skillId}
              >
                {skillName ?? `Kỹ năng ${skillId}`}
              </option>
            );
          })}
        </select>

        {orderedNodes.length === 0 && (
          <p className={styles.helperTextNodemodal}>
            Lộ trình chưa có kỹ năng nào.
          </p>
        )}
      </div>

      {/* -------------------------------- */}
      {/* Relationship with selected node */}
      {/* -------------------------------- */}

      <div className={styles.formGroupNodemodal}>
        <label htmlFor="relationToCurrent">
          Quan hệ với kỹ năng đã chọn
        </label>

        <select
          id="relationToCurrent"
          value={relationToCurrent}
          onChange={(event) =>
            setRelationToCurrent(event.target.value)
          }
          disabled={!insertBeforeSkillId || loading}
        >
          {RELATION_OPTIONS.map((option) => (
            <option
              key={option.value}
              value={option.value}
            >
              {option.label}
            </option>
          ))}
        </select>

        <p className={styles.helperTextNodemodal}>
          Quan hệ giữa kỹ năng mới và kỹ năng đã chọn.
        </p>
      </div>

      {/* -------------------------------- */}
      {/* Relationship with next node */}
      {/* -------------------------------- */}

      <div className={styles.formGroupNodemodal}>
        <label htmlFor="relationToNext">
          Quan hệ với kỹ năng kế tiếp
        </label>

        <select
          id="relationToNext"
          value={relationToNext}
          onChange={(event) =>
            setRelationToNext(event.target.value)
          }
          disabled={!nextNode || loading}
        >
          {RELATION_OPTIONS.map((option) => (
            <option
              key={option.value}
              value={option.value}
            >
              {option.label}
            </option>
          ))}
        </select>

        {nextNode ? (
          <p className={styles.helperTextNodemodal}>
            Quan hệ giữa kỹ năng mới và{' '}
            <strong>
              {typeof nextNode.skill === 'object'
                ? nextNode.skill?.skill
                : nextNode.skill ?? nextNode.skill_name}
            </strong>
          </p>
        ) : insertBeforeSkillId ? (
          <p className={styles.helperTextNodemodal}>
            Kỹ năng đã chọn là kỹ năng cuối.
            Không có kỹ năng kế tiếp.
          </p>
        ) : (
          <p className={styles.helperTextNodemodal}>
            Hãy chọn vị trí chèn trước.
          </p>
        )}
      </div>

      {/* -------------------------------- */}
      {/* Error message */}
      {/* -------------------------------- */}

      {error && (
        <div
          className={styles.errorMessageNodemodal}
          role="alert"
        >
          {error}
        </div>
      )}

      {/* -------------------------------- */}
      {/* Modal footer */}
      {/* -------------------------------- */}

      <div className={styles.modalFooterNodemodal}>
        <button
          type="button"
          className={styles.cancelButtonNodemodal}
          onClick={onClose}
          disabled={loading}
        >
          Hủy
        </button>

        <button
          type="submit"
          className={styles.confirmButtonNodemodal}
          disabled={loading || !selectedSkill}
        >
          {loading ? 'Đang thêm...' : 'Xác nhận'}
        </button>
      </div>
    </form>
  </div>
</div>

  );
}