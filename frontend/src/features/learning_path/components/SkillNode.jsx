import { Handle, Position } from '@xyflow/react';
import styles from '../styles/SkillNode.module.css';
import { roleLabel } from '../roleLabels.js';
import SkillReviewBadge from '../../review/components/SkillReviewBadge.jsx';

// 20/11 (Tuấn, Hòa nhờ): nền node = trạng thái học (data.status từ GET /me/skills: known | learning | không có),
// viền node = vai trò (Mục tiêu: viền cam đậm; Mở rộng: viền nét đứt). Bỏ dấu ✓ (trước hiện cho isTarget, dễ hiểu
// nhầm là "đã biết").
const STATUS_CLASS = { known: styles.statusKnown, learning: styles.statusLearning };

export default function SkillNode({ data }) {
    const className = [
        styles.skillNodeLearningGraph,
        STATUS_CLASS[data.status],
        data.isTarget && styles.roleTarget,
        !data.isTarget && data.nodeRole === 'extension' && styles.roleExtension,
    ].filter(Boolean).join(' ');

    return (<>
    <div className={className}>
        <Handle
            type="target" position={Position.Left}
            isConnectable={false} className={styles.nodeHandleLearningGraph}/>

        {/* Bước 5 review-on-graph (20/11): huy hiệu ôn tập. Huy hiệu tự ẩn khi kỹ năng không có khóa ôn được VÀ
            chưa đủ câu để ôn riêng; ngoài <SkillReviewProvider> (vd trang xem trước) cũng không hiện.
            TẠM (Tuấn 22/11, G2 — chờ Hòa duyệt): hiện huy hiệu ở MỌI node để ôn / kiểm tra cả kỹ năng chưa học.
            Hòa không đồng ý → xóa dòng `{true && (` và bỏ comment dòng điều kiện cũ ngay dưới. */}
        {/* {(data.status === 'known' || data.status === 'learning') && ( */}
        {true && (
            <span className={styles.reviewBadgeSlot}>
                <SkillReviewBadge skillId={data.skillId} skillName={data.skillName} />
            </span>
        )}

        <div className={styles.skillContentLearningGraph}>
            <span className={styles.skillNameLearningGraph}>
                {data.skillName}
            </span>
            <span className={styles.skillRoleLearningGraph}>
                {roleLabel(data.nodeRole)}
            </span>
        </div>

        <Handle
            type="source" position={Position.Right}
            isConnectable={false} className={styles.nodeHandleLearningGraph}/>
    </div>
    </>)
}
