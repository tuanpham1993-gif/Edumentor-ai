// Component vẽ đồ thị các node kỹ năng và đường cong Bezier SVG kết nối (Admin F11–F14).
import React from 'react';
import styles from '../styles/AdminRoadmapCanvas.module.css';

export default function AdminRoadmapCanvas({
  nodes = [],
  connections = [],
  width = 720,
  height = 240,
  mode = 'user', // 'user' | 'template'
  onNodeClick,
}) {
  const nodeWidth = 154;
  const nodeHeight = 54;

  // Bản đồ tìm kiếm node nhanh theo id hoặc tên
  const nodeMap = new Map();
  nodes.forEach((n) => {
    nodeMap.set(n.id, n);
    nodeMap.set(n.name, n);
  });

  return (
    <div className={styles.wrap}>
      <div className={styles.canvas} style={{ width: `${width}px`, height: `${height}px` }}>
        {/* Lớp SVG vẽ các đường cong nối */}
        <svg className={styles.svg} viewBox={`0 0 ${width} ${height}`}>
          <defs>
            <marker
              id="arrow-solid"
              viewBox="0 0 10 10"
              refX="6"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 8 5 L 0 9 z" fill="#6b5a40" />
            </marker>
            <marker
              id="arrow-accent"
              viewBox="0 0 10 10"
              refX="6"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 8 5 L 0 9 z" fill="#f5a524" />
            </marker>
          </defs>

          {connections.map((c, i) => {
            const sourceNode = nodeMap.get(c.from);
            const targetNode = nodeMap.get(c.to);
            if (!sourceNode || !targetNode) return null;

            const x1 = sourceNode.x + nodeWidth;
            const y1 = sourceNode.y + nodeHeight / 2;
            const x2 = targetNode.x;
            const y2 = targetNode.y + nodeHeight / 2;
            const dx = Math.max(30, (x2 - x1) / 2);

            const pathD = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
            const isDashed = c.type === 'Mở rộng';

            return (
              <path
                key={`edge-${i}`}
                d={pathD}
                className={`${styles.edge} ${isDashed ? styles.edgeDashed : styles.edgeSolid}`}
                markerEnd={isDashed ? '' : 'url(#arrow-solid)'}
              />
            );
          })}
        </svg>

        {/* Các Node HTML */}
        {nodes.map((node) => {
          let stateClass = styles.unlearned;
          let labelSuffix = '';
          let icon = null;

          if (node.status === 'known') {
            stateClass = styles.known;
            icon = <span className={styles.checkIcon}>✓</span>;
          } else if (node.status === 'learning') {
            stateClass = styles.learning;
            labelSuffix = ' · đang học';
          } else if (node.status === 'target_learning') {
            stateClass = styles.targetLearning;
            labelSuffix = ' · đang học ◎';
          } else if (node.status === 'target_unlearned' || node.role === 'target') {
            stateClass = styles.target;
            labelSuffix = ' ◎';
          } else if (node.role === 'prerequisite') {
            stateClass = styles.unlearned;
          }

          return (
            <div
              key={node.id}
              className={`${styles.node} ${stateClass}`}
              style={{ left: `${node.x}px`, top: `${node.y}px` }}
              onClick={() => onNodeClick && onNodeClick(node)}
              role="button"
              tabIndex={0}
            >
              <span>
                {node.name}
                {labelSuffix}
              </span>
              {icon}
            </div>
          );
        })}
      </div>

      {/* Chú giải (Legend) */}
      <div className={styles.legend}>
        {mode === 'user' ? (
          <>
            <span className={styles.legendItem}>
              <span className={`${styles.swatch} ${styles.swatchKnown}`} /> Đã biết
            </span>
            <span className={styles.legendItem}>
              <span className={`${styles.swatch} ${styles.swatchLearning}`} /> Đang học
            </span>
            <span className={styles.legendItem}>
              <span className={`${styles.swatch} ${styles.swatchUnlearned}`} /> Chưa học
            </span>
            <span className={styles.legendItem}>
              <span className={`${styles.swatch} ${styles.swatchTarget}`} /> Mục tiêu
            </span>
            <span className={styles.legendItem}>
              <span className={styles.lineSampleDashed} /> Mở rộng
            </span>
            <span style={{ marginLeft: 'auto', fontStyle: 'italic', opacity: 0.8 }}>
              Bấm một kỹ năng để xem trạng thái
            </span>
          </>
        ) : (
          <>
            <span className={styles.legendItem}>
              <span className={styles.lineSample} /> Tiên quyết
            </span>
            <span className={styles.legendItem}>
              <span className={styles.lineSampleDashed} /> Mở rộng
            </span>
            <span className={styles.legendItem}>
              <span className={`${styles.swatch} ${styles.swatchTarget}`} /> Kỹ năng mục tiêu (◎)
            </span>
          </>
        )}
      </div>
    </div>
  );
}
