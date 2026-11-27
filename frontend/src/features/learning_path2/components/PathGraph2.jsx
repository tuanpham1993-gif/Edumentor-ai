import { useMemo } from 'react';
import { Background, Controls, MarkerType, MiniMap, Panel, ReactFlow } from '@xyflow/react';

import StateSkillNode from './StateSkillNode.jsx';
import { STATE_META } from '../labels.js';
import styles from '../styles/PathGraph2.module.css';

const nodeTypes = { stateSkill: StateSkillNode };

const NODE_W = 210;
const NODE_H = 78;
const COL_GAP = 110;
const ROW_GAP = 34;

// Longest-path layers from the edges (Kahn). Nodes left in a cycle go to column 0.
function layersFromEdges(nodes, edges) {
  const ids = nodes.map((n) => String(n.skill_id));
  const indeg = new Map(ids.map((id) => [id, 0]));
  const succ = new Map(ids.map((id) => [id, []]));
  const layer = new Map(ids.map((id) => [id, 0]));
  edges.forEach((e) => {
    const a = String(e.from_skill_id);
    const b = String(e.to_skill_id);
    if (!indeg.has(a) || !indeg.has(b) || a === b) return;
    succ.get(a).push(b);
    indeg.set(b, indeg.get(b) + 1);
  });
  const queue = ids.filter((id) => indeg.get(id) === 0);
  while (queue.length) {
    const id = queue.shift();
    succ.get(id).forEach((s) => {
      layer.set(s, Math.max(layer.get(s), layer.get(id) + 1));
      indeg.set(s, indeg.get(s) - 1);
      if (indeg.get(s) === 0) queue.push(s);
    });
  }
  const out = {};
  ids.forEach((id) => { (out[layer.get(id)] ??= []).push(id); });
  return out;
}

// Columns = layers (prerequisites on the left, targets on the right). The backend `layer` is used
// when it covers every node; otherwise (old paths, nodes added later) layers come from the edges.
// `states` colours a saved path, whose nodes carry no state, from the stored node_states.
export function buildFlow({ nodes = [], edges = [], layer = {} }, { states = {}, selectedId = null } = {}) {
  const byId = new Map(nodes.map((n) => [String(n.skill_id), n]));
  const covered = new Set(Object.values(layer ?? {}).flat().map(String));
  const useLayer = nodes.length > 0 && nodes.every((n) => covered.has(String(n.skill_id)));
  const columns = Object.entries(useLayer ? layer : layersFromEdges(nodes, edges))
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([, ids]) => ids.map((id) => byId.get(String(id))).filter(Boolean));
  columns.forEach((col) => col.sort((a, b) => (a.display_order ?? 0) - (b.display_order ?? 0)));

  const tallest = Math.max(1, ...columns.map((c) => c.length));
  const flowNodes = columns.flatMap((col, ci) => {
    const offset = ((tallest - col.length) * (NODE_H + ROW_GAP)) / 2;
    return col.map((n, ri) => {
      const id = String(n.skill_id);
      return {
        id,
        type: 'stateSkill',
        position: { x: ci * (NODE_W + COL_GAP), y: offset + ri * (NODE_H + ROW_GAP) },
        data: {
          skillId: n.skill_id,
          skill_id: n.skill_id,
          skillName: n.skill_name ?? n.skill?.skill,
          state: n.state ?? states[id] ?? 'locked',
          isTarget: n.is_target,
          nodeRole: n.node_role,
          selected: selectedId != null && String(selectedId) === id,
        },
        draggable: false,
      };
    });
  });

  const flowEdges = edges
    .filter((e) => byId.has(String(e.from_skill_id)) && byId.has(String(e.to_skill_id)))
    .map((e) => {
      const fromState = byId.get(String(e.from_skill_id)).state ?? states[String(e.from_skill_id)];
      const done = fromState === 'known' || fromState === 'satisfied';
      const relation = e.relation_type ?? 'prerequisite';
      const className = relation !== 'prerequisite' ? styles.edgeOther : done ? styles.edgeDone : styles.edgeTodo;
      return {
        id: `e-${e.from_skill_id}-${e.to_skill_id}`,
        source: String(e.from_skill_id),
        target: String(e.to_skill_id),
        type: 'smoothstep',
        animated: relation === 'prerequisite' && !done,
        className,
        markerEnd: relation === 'related' ? undefined : { type: MarkerType.ArrowClosed, width: 16, height: 16 },
      };
    });
  return { flowNodes, flowEdges };
}

export default function PathGraph2({ graph, states, selectedId, onSelect, height = 560 }) {
  const { flowNodes, flowEdges } = useMemo(
    () => buildFlow(graph, { states, selectedId }),
    [graph, states, selectedId],
  );

  if (!flowNodes.length) {
    return <div className={styles.empty}>Lộ trình chưa có kỹ năng nào.</div>;
  }

  return (
    <div className={styles.canvas} style={{ height }}>
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => onSelect?.(node.data)}
        nodesConnectable={false}
        nodesDraggable={false}
        fitView
        fitViewOptions={{ padding: 0.18 }}
        minZoom={0.2}
        maxZoom={1.6}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={22} size={1} className={styles.bg} />
        <Controls showInteractive={false} />
        <MiniMap pannable zoomable className={styles.minimap}
          nodeClassName={(n) => styles[`mini_${n.data.state}`]} />
        <Panel position="top-left" className={styles.legend} aria-label="Chú thích">
          {Object.entries(STATE_META).map(([key, meta]) => (
            <span key={key} title={meta.hint}>
              <i className={`${styles.swatch} ${styles[`state_${key}`]}`} aria-hidden="true" />
              {meta.label}
            </span>
          ))}
          <span><i className={`${styles.swatch} ${styles.swatchTarget}`} aria-hidden="true" />Mục tiêu</span>
        </Panel>
      </ReactFlow>
    </div>
  );
}
