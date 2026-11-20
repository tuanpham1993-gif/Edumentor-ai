import { useEffect, useMemo, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  Panel,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import SkillNode from './SkillNode';
import RelationshipEdge from './RelationshipEdges';
import buildGraphForDetail from '../../../utils/buildGraphForDetail';
import { getMySkills } from '../../../api/me.api.js';
import { SkillReviewProvider } from '../../review/components/SkillReviewContext.jsx';
import styles from '../styles/LearningPathDetail.module.css';

const nodeTypes = { skill: SkillNode };
const edgeTypes = { relationship: RelationshipEdge };

// 20/11 (Tuấn, Hòa nhờ): chú thích màu node — nền = trạng thái học, viền = vai trò.
const LEGEND = [
  { label: 'Đã biết', className: styles.legendKnown },
  { label: 'Đang học', className: styles.legendLearning },
  { label: 'Chưa học', className: '' },
  { label: 'Mục tiêu', className: styles.legendTarget },
  { label: 'Mở rộng', className: styles.legendExtension },
];

// Gắn trạng thái học (known | learning) từ hồ sơ kỹ năng vào data của node; không có → Chưa học.
function withStatus(nodes, statusById) {
  return nodes.map((node) => ({
    ...node,
    data: { ...node.data, status: statusById.get(Number(node.data.skillId)) },
  }));
}

export default function LearningPathGraphForDetail({
  learningPath,
  onSelectSkill}){
    const graph = useMemo(() =>
        buildGraphForDetail(learningPath),
        [learningPath]);
    const [statusById, setStatusById] = useState(() => new Map());
    const [nodes, setNodes, onNodesChange] = useNodesState(graph.nodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(graph.edges);

    // Trạng thái kỹ năng của người học (GET /me/skills). Nạp lại mỗi lần lộ trình đổi → ôn tập đạt rồi quay lại
    // trang là node tự sang "Đã biết". Lỗi thì giữ màu mặc định, đồ thị vẫn dùng được.
    useEffect(() => {
        let alive = true;
        getMySkills()
            .then((skills) => {
                if (alive) setStatusById(new Map(skills.map((s) => [s.skill_id, s.status])));
            })
            .catch(() => {});
        return () => {
            alive = false;
        };
    }, [learningPath]);

    useEffect(() => {
        setNodes(withStatus(graph.nodes, statusById));
        setEdges(graph.edges);
    }, [graph, setNodes, setEdges]); // eslint-disable-line react-hooks/exhaustive-deps

    // Trạng thái về sau → chỉ đổi data, giữ vị trí node người dùng đã kéo.
    useEffect(() => {
        setNodes((current) => withStatus(current, statusById));
    }, [statusById, setNodes]);

    if (nodes.length === 0) {
        return (
        <div className={styles.emptyGraphDetail}>
            Lộ trình chưa có kỹ năng nào.
        </div>
        );
    }
    // Bước 5 review-on-graph (20/11): một lần gọi GET /me/review/skills cho mọi node → huy hiệu ôn tập trên node.
    return (
    <SkillReviewProvider skillIds={(learningPath?.nodes ?? []).map((n) => n.skill_id)}>
    <div className={styles.graphCanvasDetail}>
      <ReactFlow
        nodes={nodes}
        edges={edges}

        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}

        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}

        onNodeClick={(_, node) => {
          onSelectSkill?.(node.data);
        }}

        fitView
        fitViewOptions={{
          padding: 0.15,
        }}

        nodesDraggable={true}
        nodesConnectable={false}
        elementsSelectable={true}

        minZoom={0.2}
        maxZoom={1.5}

        panOnDrag
        zoomOnScroll
      >
        <Background />
        <Controls />
        <Panel position="bottom-right" className={styles.graphLegend} aria-label="Chú thích màu kỹ năng">
          {LEGEND.map((item) => (
            <span key={item.label}>
              <i className={`${styles.legendSwatch} ${item.className}`} aria-hidden="true" />
              {item.label}
            </span>
          ))}
        </Panel>
      </ReactFlow>
    </div>
    </SkillReviewProvider>
  );
}
