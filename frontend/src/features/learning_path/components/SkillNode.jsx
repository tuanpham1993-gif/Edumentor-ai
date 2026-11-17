import { Handle, Position } from '@xyflow/react';
import styles from '../styles/SkillNode.module.css';

export default function SkillNode({data}){
    return (<>
    <div className={styles.skillNodeLearningGraph}>
        <Handle
            type="target" position={Position.Left}
            isConnectable={false} className={styles.nodeHandleLearningGraph}/>

        <div className={styles.skillContentLearningGraph}>
            <span className={styles.skillNameLearningGraph}>
                {data.skillName}
            </span>
            {data.isTarget && (
                <span className={styles.completedMark}>
                    ✓
                </span>
            )}
            <span className={styles.skillRoleLearningGraph}>
                {data.nodeRole ?? 'Skill'}
            </span>
        </div>

        <Handle
            type="source" position={Position.Right}
            isConnectable={false} className={styles.nodeHandleLearningGraph}/>
    </div>
    </>)
}