/**
 * Utility sắp xếp các node kỹ năng trong lộ trình học theo đúng thứ tự tiên quyết (Topological Sort).
 * 
 * Quy tắc:
 * - Môn tiên quyết (indegree = 0 hoặc ở tầng trước) luôn xuất hiện TRƯỚC môn kế thừa/phụ thuộc.
 * - Sắp xếp theo Layer (Tầng 0: Nền tảng -> Tầng 1 -> Tầng 2...), trong cùng Layer ưu tiên display_order.
 * - Bổ sung thông tin môn tiên quyết để hiển thị ngữ cảnh (prerequisiteNames) cho người học.
 * 
 * @param {Array} nodes - Danh sách nodes từ backend (LearningPathNode)
 * @param {Array} edges - Danh sách edges từ backend (LearningPathEdge)
 * @returns {Array} Danh sách nodes đã được sắp xếp chuẩn xác kèm metadata tầng học
 */
export function sortLearningPathNodes(nodes = [], edges = []) {
  if (!Array.isArray(nodes) || nodes.length === 0) {
    return [];
  }

  const skillMap = new Map();
  const indegree = new Map();
  const adjacency = new Map();
  const layer = new Map();
  const prerequisitesMap = new Map();

  nodes.forEach((node) => {
    const id = String(node.skill_id);
    skillMap.set(id, node);
    indegree.set(id, 0);
    adjacency.set(id, []);
    layer.set(id, 0);
    prerequisitesMap.set(id, []);
  });

  // Duyệt các cạnh tiên quyết (from_skill_id là môn cần học trước, to_skill_id là môn học sau)
  const prereqEdges = (edges || []).filter(
    (edge) => edge.relation_type === 'prerequisite'
  );

  prereqEdges.forEach((edge) => {
    const source = String(edge.from_skill_id);
    const target = String(edge.to_skill_id);

    if (!skillMap.has(source) || !skillMap.has(target)) {
      return;
    }

    adjacency.get(source).push(target);
    indegree.set(target, (indegree.get(target) || 0) + 1);

    const sourceSkillName =
      skillMap.get(source)?.skill?.skill || `Kỹ năng #${source}`;
    prerequisitesMap.get(target).push(sourceSkillName);
  });

  // Kahn's Algorithm tính tầng tô-pô (Topological Layer)
  const queue = nodes
    .filter((node) => indegree.get(String(node.skill_id)) === 0)
    .sort((a, b) => (a.display_order ?? 0) - (b.display_order ?? 0))
    .map((node) => String(node.skill_id));

  const visited = new Set(queue);
  let queueIndex = 0;

  while (queueIndex < queue.length) {
    const currentId = queue[queueIndex++];
    const currentLayer = layer.get(currentId) || 0;

    const neighbors = adjacency.get(currentId) || [];
    for (const nextId of neighbors) {
      layer.set(nextId, Math.max(layer.get(nextId) || 0, currentLayer + 1));
      indegree.set(nextId, (indegree.get(nextId) || 0) - 1);

      if (indegree.get(nextId) === 0) {
        queue.push(nextId);
        visited.add(nextId);
      }
    }
  }

  // Fallback: nếu đồ thị có chu trình hoặc node cô lập chưa vào queue
  nodes.forEach((node) => {
    const id = String(node.skill_id);
    if (!visited.has(id)) {
      queue.push(id);
      visited.add(id);
    }
  });

  // Sắp xếp các node theo Layer tăng dần, trong cùng Layer sắp xếp theo display_order
  const sortedNodes = [...nodes].sort((a, b) => {
    const layerA = layer.get(String(a.skill_id)) ?? 0;
    const layerB = layer.get(String(b.skill_id)) ?? 0;

    if (layerA !== layerB) {
      return layerA - layerB;
    }

    const orderA = a.display_order ?? 0;
    const orderB = b.display_order ?? 0;
    if (orderA !== orderB) {
      return orderA - orderB;
    }

    return a.skill_id - b.skill_id;
  });

  // Trả về danh sách kèm metadata hỗ trợ render UI
  return sortedNodes.map((node) => {
    const id = String(node.skill_id);
    const nodeLayer = layer.get(id) ?? 0;
    const prereqs = prerequisitesMap.get(id) || [];

    return {
      ...node,
      _topology: {
        layer: nodeLayer,
        isFoundation: nodeLayer === 0,
        prerequisiteNames: prereqs,
      },
    };
  });
}

export default sortLearningPathNodes;
