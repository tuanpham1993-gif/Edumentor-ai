// Component vẽ đồ thị kỹ năng Admin dùng @xyflow/react theo hệ thống thiết kế learning_path2 (F11–F14).
import { useMemo } from 'react';
import { Background, Controls, Handle, MarkerType, MiniMap, Panel, Position, ReactFlow } from '@xyflow/react';
import { buildAdminRoadmapLayout } from '../../../utils/buildAdminRoadmapLayout.js';
import styles from '../styles/AdminRoadmapCanvas.module.css';

const SCALE_X = 1.48;
const SCALE_Y = 1.48;

const USER_LEGEND = [
  { key: 'known', label: 'Đã biết' },
  { key: 'learning', label: 'Đang học' },
  { key: 'locked', label: 'Chưa học' },
  { key: 'target', label: 'Mục tiêu' },
];

const TEMPLATE_LEGEND = [
  { key: 'locked', label: 'Tiên quyết' },
  { key: 'target', label: 'Mục tiêu' },
];

function resolveNodeVisual(node, mode) {
  const isTarget = Boolean(
    node.isTarget ||
    node.is_target ||
    node.role === 'target' ||
    node.status === 'target_learning' ||
    node.status === 'target_unlearned'
  );

  if (node.status === 'known') {
    return { stateKey: 'known', stateLabel: 'Đã biết', isTarget };
  }
  if (node.status === 'learning' || node.status === 'target_learning') {
    return { stateKey: 'learning', stateLabel: 'Đang học', isTarget };
  }
  if (mode === 'template') {
    return {
      stateKey: isTarget ? 'eligible' : 'locked',
      stateLabel: isTarget ? 'Kỹ năng đích' : 'Tiên quyết',
      isTarget,
    };
  }
  return {
    stateKey: isTarget ? 'eligible' : 'locked',
    stateLabel: isTarget ? 'Mục tiêu' : 'Chưa học',
    isTarget,
  };
}

function AdminSkillNode({ data }) {
  const className = [
    styles.node,
    styles[`state_${data.stateKey}`],
    data.isTarget && styles.target,
    data.selected && styles.selected,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={className} title={data.name}>
      <Handle type="target" position={Position.Left} isConnectable={false} className={styles.handle} />
      {data.isTarget && <span className={styles.targetFlag}>★ Mục tiêu</span>}
      <span className={styles.nodeName}>{data.name}</span>
      <span className={styles.nodeState}>
        <i className={styles.dot} aria-hidden="true" />
        {data.stateLabel}
      </span>
      <Handle type="source" position={Position.Right} isConnectable={false} className={styles.handle} />
    </div>
  );
}

const nodeTypes = { adminSkill: AdminSkillNode };

export default function AdminRoadmapCanvas({
  nodes = [],
  connections = [],
  height = 460,
  mode = 'user', // 'user' | 'template'
  selectedNodeId = null,
  onNodeClick,
}) {
  const resolvedHeight = Math.max(400, Number(height) || 460);

  const { flowNodes, flowEdges, isolatedCount } = useMemo(() => {
    const layout = buildAdminRoadmapLayout(nodes, connections);
    const renderNodes = layout.nodes || [];
    const renderConnections = layout.connections || [];

    const byKey = new Map();
    renderNodes.forEach((n) => {
      byKey.set(String(n.id), n);
      if (n.name) byKey.set(n.name, n);
    });

    const mappedNodes = renderNodes.map((n) => {
      const id = String(n.id);
      const { stateKey, stateLabel, isTarget } = resolveNodeVisual(n, mode);
      return {
        id,
        type: 'adminSkill',
        position: {
          x: Math.round((n.x ?? 0) * SCALE_X),
          y: Math.round((n.y ?? 0) * SCALE_Y),
        },
        data: {
          name: n.name,
          stateKey,
          stateLabel,
          isTarget,
          selected: selectedNodeId !== null && String(selectedNodeId) === id,
          rawNode: n,
        },
        draggable: false,
      };
    });

    const mappedEdges = renderConnections
      .map((c, idx) => {
        const src = byKey.get(String(c.from));
        const tgt = byKey.get(String(c.to));
        if (!src || !tgt) return null;

        const rel = c.type || 'prerequisite';
        const isDashed =
          rel === 'Mở rộng' ||
          rel === 'extension' ||
          rel === 'related' ||
          rel === 'Liên quan';
        const showArrow = rel !== 'related' && rel !== 'Liên quan' && !isDashed;
        const fromDone = src.status === 'known';

        return {
          id: `adm-e-${src.id}-${tgt.id}-${idx}`,
          source: String(src.id),
          target: String(tgt.id),
          type: 'smoothstep',
          animated: !isDashed && !fromDone,
          className: isDashed ? styles.edgeOther : fromDone ? styles.edgeDone : styles.edgeTodo,
          markerEnd: showArrow ? { type: MarkerType.ArrowClosed, width: 16, height: 16 } : undefined,
        };
      })
      .filter(Boolean);

    return {
      flowNodes: mappedNodes,
      flowEdges: mappedEdges,
      isolatedCount: layout.isolatedCount || 0,
    };
  }, [nodes, connections, mode, selectedNodeId]);

  if (!flowNodes.length) {
    return <div className={styles.empty}>Lộ trình chưa có kỹ năng nào.</div>;
  }

  const legendItems = mode === 'template' ? TEMPLATE_LEGEND : USER_LEGEND;

  return (
    <div className={styles.canvas} style={{ height: resolvedHeight }}>
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        onNodeClick={(_, rfNode) => onNodeClick?.(rfNode.data.rawNode)}
        nodesConnectable={false}
        nodesDraggable={false}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.2}
        maxZoom={1.6}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={22} size={1} className={styles.bg} />
        <Controls showInteractive={false} />
        <MiniMap
          pannable
          zoomable
          className={styles.minimap}
          nodeClassName={(n) => styles[`mini_${n.data.stateKey}`]}
        />
        <Panel position="top-left" className={styles.legend} aria-label="Chú thích trạng thái">
          {legendItems.map((item) => (
            <span key={item.key}>
              <i
                className={`${styles.swatch} ${
                  item.key === 'target' ? styles.swatchTarget : styles[`state_${item.key}`]
                }`}
                aria-hidden="true"
              />
              {item.label}
            </span>
          ))}
          {isolatedCount > 0 && (
            <span className={styles.isolatedHint}>{isolatedCount} kỹ năng độc lập</span>
          )}
        </Panel>
      </ReactFlow>
    </div>
  );
}
