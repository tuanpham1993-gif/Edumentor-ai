import { MarkerType } from '@xyflow/react';

const NODE_WIDTH = 190;
const NODE_HEIGHT = 68;

const COLUMN_GAP = 150;
const ROW_GAP = 45;

function calculateLayers(nodes, edges) {
    const nodeIds = nodes.map((node) => String(node.skill_id));

    const indegree = new Map();
    const adjacency = new Map();
    const layer = new Map();

    nodeIds.forEach((id) => {
        indegree.set(id, 0);
        adjacency.set(id, []);
        layer.set(id, 0);
    });
    //check later
    edges.filter((edge) => edge.relation_type === 'prerequisite')
        .forEach((edge) => {
        const source = String(edge.from_skill_id);
        const target = String(edge.to_skill_id);

        if (!indegree.has(source) || !indegree.has(target)) {
            return;
        }

        adjacency.get(source).push(target);
        indegree.set(target, indegree.get(target) + 1);
        });
    
    const queue = nodeIds.filter((id) => indegree.get(id) === 0);//find root
    let queueIndex = 0;
    while (queueIndex < queue.length) {
        const current = queue[queueIndex];
        queueIndex++;
        adjacency.get(current).forEach((next) => {
            layer.set(next, Math.max(layer.get(next), layer.get(current) + 1));
            indegree.set(next, indegree.get(next) - 1);
            if (indegree.get(next) === 0) queue.push(next);  
        })
    }
    return layer
}

export default function buildGraphForDetail(data) {
    const backendNodes = data?.nodes ?? [];
    const backendEdges = data?.edges ?? [];
    if (backendNodes.length === 0) return { nodes: [], edges: [] };
    const skillMap = new Map(
        backendNodes.map((node) => [
            String(node.skill_id),
            node,
        ])
    );
    const layers = calculateLayers(backendNodes, backendEdges);
    const layerGroups = new Map();
    backendNodes.forEach((skill) => {
        const column = layers.get(String(skill.skill_id)) ?? 0;
        if (!layerGroups.has(column)) layerGroups.set(column, []);
        layerGroups.get(column).push(skill);
    });
    const sortedLayers = [...layerGroups.entries()]
    .sort(([a], [b]) => a - b);

    sortedLayers.forEach(([, skills]) => {
        skills.sort((a, b) => a.display_order - b.display_order);
    });

    const maxRows = Math.max(1,
    ...sortedLayers.map(([, skills]) => skills.length)
    );

    const flowNodes = sortedLayers.flatMap(
        ([column, skills]) =>{
            const verticalOffset = ((maxRows - skills.length) * (NODE_HEIGHT + ROW_GAP)) / 2;
            return skills.map((node, rowIndex) => ({
                id: String(node.skill_id), type: 'skill',
                position: {
                    x: column * (NODE_WIDTH + COLUMN_GAP),
                    y: verticalOffset + rowIndex * (NODE_HEIGHT + ROW_GAP),
                },
                data: {
                    skillId: node.skill_id,
                    skillName: node.skill?.skill ?? 'Unknown skill',
                    nodeRole: node.node_role,
                    isTarget: node.is_target,
                    addedBy: node.added_by,
                    displayOrder: node.display_order,
                },
                draggable: true,
                selectable: true,
            }))
        })
    const flowEdges = backendEdges.filter((edge) => {
        return (
            skillMap.has(String(edge.from_skill_id)) &&
            skillMap.has(String(edge.to_skill_id))
        );
    }).map((edge, index) => {
        let color = 'var(--edge)';
        const relationType = edge.relation_type;
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
            data: {relationType},
            markerEnd: relationType === 'related' ? undefined : {
                type: MarkerType.ArrowClosed,
                color,
            },
            style: {
                stroke: color,
                strokeWidth: 2,
            },
            selectable: true,
        }
    })
    return {
        nodes: flowNodes,
        edges: flowEdges,
    };
}
