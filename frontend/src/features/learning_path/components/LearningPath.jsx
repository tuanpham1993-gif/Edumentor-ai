
import { useMemo } from 'react';
import { ReactFlow, Background, Controls, MarkerType } from '@xyflow/react';

import SkillNode from './SkillNode';
import RelationshipEdge from './RelationshipEdges';
import styles from '../styles/LearningPathGraph.module.css';

const nodeTypes = { skill: SkillNode,};
const edgeTypes = {relationship: RelationshipEdge,};

const NODE_WIDTH = 190;
const NODE_HEIGHT = 68;

const COLUMN_GAP = 150;
const ROW_GAP = 45;

function buildGraph(data) {
  const backendNodes = data?.nodes ?? [];
  const backendEdges = data?.edges ?? [];
  const backendLayers = data?.layer ?? {};

  const sortedLayers = Object.entries(backendLayers)
    .sort(([layerA], [layerB]) => Number(layerA) - Number(layerB));
  const skillMap = new Map(backendNodes.map((node) => [String(node.skill_id),node]));

  const assignedIds = new Set();
  const layerGroups = sortedLayers.map(([layerNumber, skillIds]) => {
    const skills = skillIds.map((id) => skillMap.get(String(id))).filter(Boolean)
      .sort((a, b) => a.display_order - b.display_order);
    skills.forEach((skill) => {assignedIds.add(String(skill.skill_id));});

    return {
      layerNumber: Number(layerNumber),
      skills,
    };
  });

  const unassignedSkills = backendNodes
    .filter((node) => !assignedIds.has(String(node.skill_id)))
    .sort((a, b) => a.display_order - b.display_order);

  if (unassignedSkills.length > 0) {
    layerGroups.push({
      layerNumber: layerGroups.length,
      skills: unassignedSkills,
    });
  }

  // Step 4: Find the tallest column.
  const maxRows = Math.max(1,...layerGroups.map((group) => group.skills.length));

  // Step 5: Generate React Flow nodes.
  const nodes = layerGroups.flatMap((group, columnIndex) => {
    const columnHeight = group.skills.length;

    // Vertically center smaller columns.
    const verticalOffset = ((maxRows - columnHeight) * (NODE_HEIGHT + ROW_GAP)) / 2;

    return group.skills.map((skill, rowIndex) => ({
      id: String(skill.skill_id),
      type: 'skill',
      position: {
        x: columnIndex * (NODE_WIDTH + COLUMN_GAP),
        y: verticalOffset + rowIndex * (NODE_HEIGHT + ROW_GAP),
      },

      data: {
        skillId: skill.skill_id,
        skillName: skill.skill_name,
        nodeRole: skill.node_role,
        isTarget: skill.is_target ?? false,
        isRequired: skill.is_required,
      },

      // This is a preview, so students cannot drag nodes, but can click to inspect courses.
      draggable: false,
      selectable: true,
    }));
  });

  // Step 6: Generate React Flow edges.
  const edges = backendEdges
    .filter((edge) => {
      return (
        skillMap.has(String(edge.from_skill_id)) &&
        skillMap.has(String(edge.to_skill_id))
      );
    })
    .map((edge, index) => {
      const relationType = edge.relation_type;
      let color = 'var(--edge)';

      if (relationType === 'related') {
        color = 'var(--info-fg)';
      }

      if (relationType === 'extension') {
        color = 'var(--accent)';
      }

      return {
        id: `edge-${edge.from_skill_id}-${edge.to_skill_id}-${index}`,

        source: String(edge.from_skill_id),
        target: String(edge.to_skill_id),

        type: 'relationship',

        data: {
          relationType,
          description: edge.description ?? '',
        },

        markerEnd:
          relationType === 'related'
            ? undefined
            : {
                type: MarkerType.ArrowClosed,
                color,
              },

        style: {
          stroke: color,
          strokeWidth: 2,
        },

        selectable: false,
      };
    });

  return { nodes, edges };
}

export default function LearningPathGraph({ learningPath, onSelectSkill }) {
  const { nodes, edges } = useMemo(
    () => buildGraph(learningPath),
    [learningPath]
  );

  if (nodes.length === 0) {
    return (
      <div className={styles.emptyGraph}>
        Lộ trình chưa có kỹ năng nào.
      </div>
    );
  }

  return (
    <div className={styles.graphCanvas}>
      <ReactFlow
        nodes={nodes}
        edges={edges}

        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}

        onNodeClick={(_, node) => {
          onSelectSkill?.(node.data);
        }}

        fitView
        fitViewOptions={{
          padding: 0.15,
        }}

        nodesDraggable={false}
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
