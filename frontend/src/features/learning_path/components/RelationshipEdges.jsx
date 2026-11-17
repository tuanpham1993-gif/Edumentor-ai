
import { useState } from 'react';
import { BaseEdge, EdgeLabelRenderer, getBezierPath } from '@xyflow/react';
import styles from '../styles/LearningPathGraph.module.css';

export default function RelationshipEdge({
  sourceX, sourceY, targetX, targetY,
  sourcePosition, targetPosition, markerEnd, data}) {

  const [isHovered, setIsHovered] = useState(false);
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX, sourceY, sourcePosition,
    targetX, targetY, targetPosition,
  });

  const relationType = data?.relationType ?? 'prerequisite';
  const edgeStyle = {
    prerequisite: styles.prerequisiteEdge,
    related: styles.relatedEdge,
    extension: styles.extensionEdge,
  };

  return (
    <>
      <path d={edgePath}
        className={`${styles.edgePath} ${edgeStyle[relationType] ?? styles.prerequisiteEdge}`}
        markerEnd={markerEnd}/>

      <path
        d={edgePath} className={styles.edgeInteraction}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      />

      {isHovered && (
        <EdgeLabelRenderer>
          <div className={styles.edgeTooltip}
            style={{ transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,}}>
            <strong>{relationType}</strong>
            {data?.description && (<span>{data.description}</span>)}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
