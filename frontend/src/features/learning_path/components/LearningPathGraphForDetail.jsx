import { useEffect, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import SkillNode from './SkillNode';
import RelationshipEdge from './RelationshipEdges';
import buildGraphForDetail from '../../../utils/buildGraphForDetail';
import styles from '../styles/LearningPathDetail.module.css';

const nodeTypes = { skill: SkillNode };
const edgeTypes = { relationship: RelationshipEdge };
export default function LearningPathGraphForDetail({
  learningPath, 
  onSelectSkill}){
    const graph = useMemo(() => 
        buildGraphForDetail(learningPath),
        [learningPath]);
    const [nodes, setNodes, onNodesChange] = useNodesState(graph.nodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(graph.edges);
    
    useEffect(() => {
        setNodes(graph.nodes);
        setEdges(graph.edges);
    }, [graph, setNodes, setEdges]);

    if (nodes.length === 0) {
        return (
        <div className={styles.emptyGraphDetail}>
            No learning path nodes were returned.
        </div>
        );
    }
    return (
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
      </ReactFlow>
    </div>
  );
}