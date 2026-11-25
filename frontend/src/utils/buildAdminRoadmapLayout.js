/**
 * Tự động tính toán tọa độ (x, y) và kích thước canvas cho AdminRoadmapCanvas
 * từ dữ liệu thật (nodes, edges) không lưu tọa độ trong PostgreSQL.
 *
 * Dùng thuật toán Kahn phân tầng (DAG Layering) giống buildGraphForDetail.js:
 * - Các cạnh prerequisite quyết định cột (tầng học từ trái sang phải).
 * - Các cạnh related / extension vẫn được vẽ đầy đủ nhưng không gây chu trình chia tầng.
 */

const NODE_WIDTH = 154;
const NODE_HEIGHT = 54;
const COLUMN_GAP = 64;
const ROW_GAP = 22;
const PADDING_X = 28;
const PADDING_Y = 26;

function mapCanvasNodeStatus(node) {
  const skillStatus = node.user_skill_status || node.status || 'unlearned';
  const isTarget = Boolean(node.is_target);

  if (skillStatus === 'known') {
    return 'known';
  }
  if (skillStatus === 'learning') {
    return isTarget ? 'target_learning' : 'learning';
  }
  return isTarget ? 'target_unlearned' : 'unlearned';
}

export function buildAdminRoadmapLayout(rawNodes = [], rawEdges = []) {
  if (!Array.isArray(rawNodes) || rawNodes.length === 0) {
    return {
      nodes: [],
      connections: [],
      width: 720,
      height: 240,
    };
  }

  // Nếu dữ liệu đã có tọa độ (từ AdminBasePathsPage mock) thì giữ nguyên
  const hasExplicitCoords = rawNodes.every(
    (n) => typeof n.x === 'number' && typeof n.y === 'number'
  );
  if (hasExplicitCoords) {
    return {
      nodes: rawNodes,
      connections: rawEdges,
      width: null,
      height: null,
    };
  }

  const nodeIds = rawNodes.map((n) => String(n.skill_id ?? n.id));
  const indegree = new Map();
  const adjacency = new Map();
  const layer = new Map();

  nodeIds.forEach((id) => {
    indegree.set(id, 0);
    adjacency.set(id, []);
    layer.set(id, 0);
  });

  (rawEdges || [])
    .filter((edge) => (edge.relation_type || edge.type) === 'prerequisite')
    .forEach((edge) => {
      const source = String(edge.from_skill_id ?? edge.from);
      const target = String(edge.to_skill_id ?? edge.to);
      if (!indegree.has(source) || !indegree.has(target)) return;
      adjacency.get(source).push(target);
      indegree.set(target, indegree.get(target) + 1);
    });

  const queue = nodeIds.filter((id) => indegree.get(id) === 0);
  let idx = 0;
  while (idx < queue.length) {
    const current = queue[idx++];
    for (const next of adjacency.get(current) || []) {
      layer.set(next, Math.max(layer.get(next), layer.get(current) + 1));
      indegree.set(next, indegree.get(next) - 1);
      if (indegree.get(next) === 0) {
        queue.push(next);
      }
    }
  }

  const layerGroups = new Map();
  rawNodes.forEach((node) => {
    const id = String(node.skill_id ?? node.id);
    const col = layer.get(id) ?? 0;
    if (!layerGroups.has(col)) layerGroups.set(col, []);
    layerGroups.get(col).push(node);
  });

  const sortedLayers = [...layerGroups.entries()].sort(([a], [b]) => a - b);
  sortedLayers.forEach(([, list]) => {
    list.sort((a, b) => (a.display_order ?? 0) - (b.display_order ?? 0));
  });

  const numCols = sortedLayers.length;
  const maxRows = Math.max(1, ...sortedLayers.map(([, list]) => list.length));

  const contentHeight = maxRows * NODE_HEIGHT + Math.max(0, maxRows - 1) * ROW_GAP;
  const contentWidth = numCols * NODE_WIDTH + Math.max(0, numCols - 1) * COLUMN_GAP;

  const canvasWidth = Math.max(720, contentWidth + PADDING_X * 2);
  const canvasHeight = Math.max(240, contentHeight + PADDING_Y * 2);

  // Căn đều ngang nếu ít cột để canvas cân đối
  const effectiveColWidth =
    numCols > 1
      ? Math.max(NODE_WIDTH + COLUMN_GAP, (canvasWidth - PADDING_X * 2 - NODE_WIDTH) / (numCols - 1))
      : 0;

  const layoutNodes = sortedLayers.flatMap(([colIndex, list], actualColIdx) => {
    const colContentHeight = list.length * NODE_HEIGHT + Math.max(0, list.length - 1) * ROW_GAP;
    const verticalOffset = PADDING_Y + (contentHeight - colContentHeight) / 2;

    return list.map((node, rowIdx) => {
      const id = String(node.skill_id ?? node.id);
      const x =
        numCols === 1
          ? (canvasWidth - NODE_WIDTH) / 2
          : Math.round(PADDING_X + actualColIdx * effectiveColWidth);
      const y = Math.round(verticalOffset + rowIdx * (NODE_HEIGHT + ROW_GAP));

      return {
        id,
        skillId: node.skill_id ?? node.id,
        name: node.skill_name || node.name || `Kỹ năng #${id}`,
        role: node.node_role || node.role || null,
        isTarget: Boolean(node.is_target),
        status: mapCanvasNodeStatus(node),
        rawStatus: node.user_skill_status || 'unlearned',
        x,
        y,
      };
    });
  });

  const layoutConnections = (rawEdges || []).map((edge) => ({
    from: String(edge.from_skill_id ?? edge.from),
    to: String(edge.to_skill_id ?? edge.to),
    type: edge.relation_type || edge.type || 'prerequisite',
  }));

  return {
    nodes: layoutNodes,
    connections: layoutConnections,
    width: canvasWidth,
    height: canvasHeight,
  };
}

export default buildAdminRoadmapLayout;
