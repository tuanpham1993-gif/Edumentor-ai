import { Handle, Position } from '@xyflow/react';
import { STATE_META } from '../labels.js';
import SkillReviewBadge from '../../review/components/SkillReviewBadge.jsx';
import styles from '../styles/PathGraph2.module.css';

// One skill in the AI v2 graph. Colour = learning state, gold ring = final target.
export default function StateSkillNode({ data }) {
  const meta = STATE_META[data.state] ?? STATE_META.locked;
  const className = [
    styles.node,
    styles[`state_${data.state}`],
    data.isTarget && styles.target,
    data.selected && styles.selected,
  ].filter(Boolean).join(' ');

  return (
    <div className={className} title={meta.hint}>
      <Handle type="target" position={Position.Left} isConnectable={false} className={styles.handle} />
      {data.isTarget && <span className={styles.targetFlag} aria-label="Mục tiêu">★ Mục tiêu</span>}
      {/* Review badge (module 09, Tuấn): only for known / learning skills; hides itself outside
          <SkillReviewProvider> (e.g. on the preview page) or when no course can be reviewed. */}
      {(data.state === 'known' || data.state === 'learning') && (
        <span className={styles.reviewSlot}>
          <SkillReviewBadge skillId={data.skillId} skillName={data.skillName} />
        </span>
      )}
      <span className={styles.nodeName}>{data.skillName}</span>
      <span className={styles.nodeState}>
        <i className={styles.dot} aria-hidden="true" />
        {meta.label}
      </span>
      <Handle type="source" position={Position.Right} isConnectable={false} className={styles.handle} />
    </div>
  );
}
