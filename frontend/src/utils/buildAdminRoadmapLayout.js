/**
 * Tự động tính toán tọa độ (x, y), kích thước canvas và quan hệ tiên quyết
 * cho AdminRoadmapCanvas từ dữ liệu thật (không lưu tọa độ trong DB).
 *
 * Cải tiến bố cục:
 * - Phân tách nhánh có liên kết (connected nodes) đặt ở vùng đồ thị chính phía trên
 *   theo thuật toán Kahn (từ trái sang phải).
 * - Gom các kỹ năng độc lập (chưa nối cạnh) thành lưới ngang gọn gàng phía dưới
 *   kèm dividerY để tránh cột 0 bị kéo dài tạo khoảng trống lớn.
 * - Bổ sung danh sách `prerequisites` và `unlocks` cho từng node để thanh chi tiết hiển thị.
 */

const NODE_WIDTH = 154;
const NODE_HEIGHT = 54;
const COLUMN_GAP = 64;
const ROW_GAP = 20;
const PADDING_X = 28;
const PADDING_Y = 24;
const ISOLATED_GAP_X = 14;
const ISOLATED_GAP_Y = 16;
const SECTION_GAP = 42;

function getNodeName(node, fallbackId) {
  return node?.skill_name || node?.skill?.skill || node?.name || `Kỹ năng #${fallbackId}`;
}

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
      dividerY: null,
      isolatedCount: 0,
    };
  }

  // Giữ nguyên tọa độ cho màn hình AdminBasePathsPage (mode="template")
  const hasExplicitCoords = rawNodes.every(
    (n) => typeof n.x === 'number' && typeof n.y === 'number'
  );
  if (hasExplicitCoords) {
    return {
      nodes: rawNodes,
      connections: rawEdges,
      width: null,
      height: null,
      dividerY: null,
      isolatedCount: 0,
    };
  }

  const nodeById = new Map();
  const prerequisitesMap = new Map();
  const unlocksMap = new Map();
  const connectedIds = new Set();

  rawNodes.forEach((n) => {
    const id = String(n.skill_id ?? n.id);
    nodeById.set(id, n);
    prerequisitesMap.set(id, []);
    unlocksMap.set(id, []);
  });

  const validEdges = (rawEdges || []).filter((edge) => {
    const source = String(edge.from_skill_id ?? edge.from);
    const target = String(edge.to_skill_id ?? edge.to);
    return nodeById.has(source) && nodeById.has(target) && source !== target;
  });

  validEdges.forEach((edge) => {
    const source = String(edge.from_skill_id ?? edge.from);
    const target = String(edge.to_skill_id ?? edge.to);
    connectedIds.add(source);
    connectedIds.add(target);

    const relType = edge.relation_type || edge.type || 'prerequisite';
    if (relType === 'prerequisite') {
      prerequisitesMap.get(target).push(getNodeName(nodeById.get(source), source));
      unlocksMap.get(source).push(getNodeName(nodeById.get(target), target));
    }
  });

  const connectedNodes = rawNodes.filter((n) =>
    connectedIds.has(String(n.skill_id ?? n.id))
  );
  const isolatedNodes = rawNodes
    .filter((n) => !connectedIds.has(String(n.skill_id ?? n.id)))
    .sort((a, b) => (a.display_order ?? 0) - (b.display_order ?? 0));

  // Tính phân tầng cho cụm có cạnh nối
  const indegree = new Map();
  const adjacency = new Map();
  const layer = new Map();

  connectedNodes.forEach((n) => {
    const id = String(n.skill_id ?? n.id);
    indegree.set(id, 0);
    adjacency.set(id, []);
    layer.set(id, 0);
  });

  validEdges
    .filter((e) => (e.relation_type || e.type) === 'prerequisite')
    .forEach((e) => {
      const source = String(e.from_skill_id ?? e.from);
      const target = String(e.to_skill_id ?? e.to);
      adjacency.get(source).push(target);
      indegree.set(target, (indegree.get(target) || 0) + 1);
    });

  const queue = connectedNodes
    .filter((n) => indegree.get(String(n.skill_id ?? n.id)) === 0)
    .map((n) => String(n.skill_id ?? n.id));
  const visited = new Set(queue);

  let qIdx = 0;
  while (qIdx < queue.length) {
    const current = queue[qIdx++];
    for (const next of adjacency.get(current) || []) {
      layer.set(next, Math.max(layer.get(next), layer.get(current) + 1));
      indegree.set(next, indegree.get(next) - 1);
      if (indegree.get(next) === 0 && !visited.has(next)) {
        queue.push(next);
        visited.add(next);
      }
    }
  }

  // Phòng hờ chu trình: mọi node chưa duyệt đẩy vào cột cuối
  const maxVisitedLayer = Math.max(0, ...layer.values());
  connectedNodes.forEach((n) => {
    const id = String(n.skill_id ?? n.id);
    if (!visited.has(id)) {
      layer.set(id, maxVisitedLayer + 1);
    }
  });

  const layerGroups = new Map();
  connectedNodes.forEach((n) => {
    const id = String(n.skill_id ?? n.id);
    const col = layer.get(id) ?? 0;
    if (!layerGroups.has(col)) layerGroups.set(col, []);
    layerGroups.get(col).push(n);
  });

  const sortedLayers = [...layerGroups.entries()].sort(([a], [b]) => a - b);
  sortedLayers.forEach(([, list]) => {
    list.sort((a, b) => (a.display_order ?? 0) - (b.display_order ?? 0));
  });

  const numCols = sortedLayers.length;
  const maxConnectedRows =
    numCols > 0 ? Math.max(1, ...sortedLayers.map(([, list]) => list.length)) : 0;

  const connectedWidth =
    numCols > 0 ? numCols * NODE_WIDTH + Math.max(0, numCols - 1) * COLUMN_GAP : 0;
  const connectedHeight =
    maxConnectedRows > 0
      ? maxConnectedRows * NODE_HEIGHT + Math.max(0, maxConnectedRows - 1) * ROW_GAP
      : 0;

  const isolatedColsPerRow = isolatedNodes.length > 0 ? Math.min(4, Math.max(3, numCols || 3)) : 0;
  const isolatedGridWidth =
    isolatedColsPerRow > 0
      ? Math.min(isolatedNodes.length, isolatedColsPerRow) * NODE_WIDTH +
        Math.max(0, Math.min(isolatedNodes.length, isolatedColsPerRow) - 1) * ISOLATED_GAP_X
      : 0;

  const canvasWidth = Math.max(720, Math.max(connectedWidth, isolatedGridWidth) + PADDING_X * 2);

  const effectiveColWidth =
    numCols > 1
      ? Math.max(
          NODE_WIDTH + COLUMN_GAP,
          (canvasWidth - PADDING_X * 2 - NODE_WIDTH) / (numCols - 1)
        )
      : 0;

  const layoutConnectedNodes = sortedLayers.flatMap(([, list], actualColIdx) => {
    const colContentHeight = list.length * NODE_HEIGHT + Math.max(0, list.length - 1) * ROW_GAP;
    const verticalOffset = PADDING_Y + (connectedHeight - colContentHeight) / 2;

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
        name: getNodeName(node, id),
        role: node.node_role || node.role || null,
        isTarget: Boolean(node.is_target),
        status: mapCanvasNodeStatus(node),
        rawStatus: node.user_skill_status || 'unlearned',
        prerequisites: prerequisitesMap.get(id) || [],
        unlocks: unlocksMap.get(id) || [],
        x,
        y,
      };
    });
  });

  // Bố trí nhóm kỹ năng độc lập (lưới ngang gọn gàng)
  let dividerY = null;
  let isolatedStartY = PADDING_Y;

  if (isolatedNodes.length > 0 && connectedNodes.length > 0) {
    dividerY = PADDING_Y + connectedHeight + Math.round(SECTION_GAP / 2) - 4;
    isolatedStartY = PADDING_Y + connectedHeight + SECTION_GAP + 14;
  }

  const maxPerRow = Math.max(1, Math.floor((canvasWidth - PADDING_X * 2 + ISOLATED_GAP_X) / (NODE_WIDTH + ISOLATED_GAP_X)));
  const isolatedRows = Math.ceil(isolatedNodes.length / maxPerRow);

  const layoutIsolatedNodes = isolatedNodes.map((node, i) => {
    const id = String(node.skill_id ?? node.id);
    const col = i % maxPerRow;
    const row = Math.floor(i / maxPerRow);

    return {
      id,
      skillId: node.skill_id ?? node.id,
      name: getNodeName(node, id),
      role: node.node_role || node.role || null,
      isTarget: Boolean(node.is_target),
      status: mapCanvasNodeStatus(node),
      rawStatus: node.user_skill_status || 'unlearned',
      prerequisites: [],
      unlocks: [],
      x: Math.round(PADDING_X + col * (NODE_WIDTH + ISOLATED_GAP_X)),
      y: Math.round(isolatedStartY + row * (NODE_HEIGHT + ISOLATED_GAP_Y)),
    };
  });

  const isolatedSectionHeight =
    isolatedNodes.length > 0
      ? isolatedRows * NODE_HEIGHT + Math.max(0, isolatedRows - 1) * ISOLATED_GAP_Y
      : 0;

  const totalBottom =
    isolatedNodes.length > 0
      ? isolatedStartY + isolatedSectionHeight + PADDING_Y
      : PADDING_Y + connectedHeight + PADDING_Y;

  const canvasHeight = Math.max(200, totalBottom);

  const layoutConnections = validEdges.map((edge) => ({
    from: String(edge.from_skill_id ?? edge.from),
    to: String(edge.to_skill_id ?? edge.to),
    type: edge.relation_type || edge.type || 'prerequisite',
  }));

  return {
    nodes: [...layoutConnectedNodes, ...layoutIsolatedNodes],
    connections: layoutConnections,
    width: canvasWidth,
    height: canvasHeight,
    dividerY,
    isolatedCount: isolatedNodes.length,
  };
}

export default buildAdminRoadmapLayout;
