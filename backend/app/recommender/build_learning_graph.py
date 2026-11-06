from app.recommender.collaborative_filtering import historical_record_retrieval_pipeline
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.models.learning_path import LearningPath
from app.models.skill_relation import SkillRelation
from app.core.embedding_model import model

def createVisited(db: Session, target_skill: int):
    visited_set = set()
    ready_node = [target_skill]
    while ready_node:
        skill_id = ready_node.pop(0)
        if skill_id in visited_set: continue
        visited_set.add(skill_id)

        # Search for skills that are prerequisites of the current skill
        statement = select(SkillRelation.from_skill_id).where(
            SkillRelation.to_skill_id == skill_id,
            SkillRelation.relation_type == "prerequisite"
        )

        prerequisite_ids = db.execute(statement).scalars().all()
        for prerequisite_id in prerequisite_ids: 
            ready_node.append(prerequisite_id)
    return visited_set

def get_path_templates(db: Session):
    statement = (
        select(LearningPath)
        .where(LearningPath.goal_type == "template")
        .options(selectinload(LearningPath.nodes))
    )
    templates = db.execute(statement).scalars().all()
    return [
        {
            "template_id": template.record_id,
            "skills": [
                {"skill_id": node.skill_id}
                for node in template.nodes
            ]
        }
        for template in templates
    ]

def build_learning_graph_basic(db: Session, skill_input):
    visited_skill = createVisited(db, skill_input) #expaneded till root
    node_freq_to_skills = {}
    edges_list = set()
    #this step need to be adjust to database later

    if visited_skill:
        statement = select(SkillRelation).where(
            SkillRelation.from_skill_id.in_(visited_skill),
            SkillRelation.to_skill_id.in_(visited_skill),
            SkillRelation.relation_type == "prerequisite"
        )

        relations = db.execute(statement).scalars().all()

        for relation in relations:
            from_skill = relation.from_skill_id
            to_skill = relation.to_skill_id
            edges_list.add((from_skill, to_skill))

    for skill_id in visited_skill:
        node_freq_to_skills[skill_id] = sum(
            1 for from_skill, to_skill in edges_list
            if to_skill == skill_id)
    root = [skill_id for skill_id, count in node_freq_to_skills.items() if count == 0]

    incoming_graph = {}
    for from_skill, to_skill in edges_list:
        skill_list = incoming_graph.get(from_skill, [])
        skill_list.append(to_skill)
        incoming_graph[from_skill] = skill_list
    return root, incoming_graph, visited_skill, node_freq_to_skills, edges_list

def find_cycle_edges(visited_skill, edges_list, incoming_graph = None):
    if(incoming_graph):
        graph = incoming_graph.copy()
    else:
        graph = {node: [] for node in visited_skill}
        for from_node, to_node in edges_list:
            listSkill = graph.get(from_node, [])
            listSkill.append(to_node)
            graph[from_node] = listSkill
    #print(graph)
    #0: unvisited, 1: ongoing, 2: finised
    state = {}
    for each in visited_skill: 
        state[each] = 0
    path_node = []
    edge_node = []

    def dfs(current):
        state[current] = 1
        path_node.append(current)
        for next_skill in graph.get(current, []):
            if (state[next_skill] == 0):
                edge_node.append((current, next_skill))
                have_cycle = dfs(next_skill)
                if(have_cycle is not None): return have_cycle
                edge_node.pop()
                
            elif (state[next_skill] == 1):
                position = path_node.index(next_skill)
                return edge_node[position:] + [(current, next_skill)]
        
        state[current] = 2       
        path_node.pop()
        return None

    for node in graph:
        if(state[node] == 0):
            cycle = dfs(node)
            if(cycle is not None):
                return cycle
    return None

def repair_cycle(all_nodes, all_edges):
    remaining_edges = all_edges.copy()
    removed_edges = list()
    while True:
        cycle = find_cycle_edges(visited_skill= all_nodes, edges_list = remaining_edges)
        if (cycle is None): break
        removeNode = cycle[-1]
        remaining_edges.remove(removeNode)
        removed_edges.append(removeNode)
    return remaining_edges, removed_edges

def buildLayers(visited_skill, node_freq_to_skills, incomming_graph, root):
    layer = {} 
    queue = root.copy()
    freq = node_freq_to_skills.copy()
    processed = 0
    for each in visited_skill: layer[each] = 0
    while(queue):
        current_skill = queue.pop(0)
        processed += 1
        for next_skill in incomming_graph.get(current_skill, []):
            layer[next_skill] = max(layer[current_skill] + 1, layer[next_skill])
            freq[next_skill]-= 1;
            if (freq[next_skill] == 0):
                queue.append(next_skill)
    return layer

def build_learning_path_pipeline(
    db:Session,
    LLM_input_skill_list: list[int], 
    user_query:str
):
    #======================================================
    #Merge templace pipeline
    #1. load template one by one
    #2. check score based on visited skills, save it index, later on in database can find right away 
    # => check score = alpha * targetCoverage + (1-alpha)* expandedCoverage 
    # => choice alpha = 0.65 initialize
    #3. choice template that have highest score with threshold 0.65
    #4. merge with current learning path
    #======================================================
    target_skills = set(LLM_input_skill_list)
    visited_skill = set()
    edges_list = set()
    for skill_id in target_skills:
        root, incoming_graph, skill_set, node_freq, edges = (build_learning_graph_basic(db=db, skill_input = skill_id))
        visited_skill.update(skill_set)
        edges_list.update(edges)

    # ======================================================
    # 2. Template matching
    # ======================================================

    ALPHA = 0.65
    MIN_TEMPLATE_SCORE = 0.65

    saveIndex = -1
    best_score = -1

    target_coverage_record = {}
    #this part also need search from learning_path table with goal_type with template type aside from project and career
    path_templates = get_path_templates(db)
    for template in path_templates:
        template_skills = {each["skill_id"] for each in template["skills"]}
        # Target coverage
        target_coverage = (len(target_skills & template_skills) / len(target_skills))
        # Expanded coverage
        expanded_coverage = (len(visited_skill & template_skills) / len(visited_skill))
        # Combined score
        score = ALPHA * target_coverage + (1 - ALPHA) * expanded_coverage
    
        target_coverage_record[template["template_id"]] = {
            "target_coverage": target_coverage,
            "expanded_coverage": expanded_coverage,
            "score": score
        }

        # Select the highest-scoring template
        if score > best_score:
            best_score = score
            saveIndex = template["template_id"]

    # ======================================================
    # 3. Check matching threshold and merge template
    # ======================================================

    if best_score >= MIN_TEMPLATE_SCORE:
        selected_template = next((
                template for template in path_templates
                if template["template_id"] == saveIndex
            ), None
        )
    else:
        saveIndex = -1
        selected_template = None

    if selected_template is not None:
        for each in selected_template["skills"]:
            skill_id = each["skill_id"]
            # Expand prerequisites of every template skill
            _, _, skill_set, _, edges = (
                build_learning_graph_basic(db,skill_id)
            )

            visited_skill.update(skill_set)
            edges_list.update(edges)

    # ======================================================
    # 3.1 Collaborating filtering
    # ======================================================
    global model
    historical_candidate = historical_record_retrieval_pipeline(
          db=db,
          current_query=user_query,
          model=model,
          visited_skill_ids=visited_skill,
          threshold=0.7
      )
    for each in historical_candidate:
      _, _, skill_set, _, edges = (build_learning_graph_basic(db, each["skill_id"]))
      visited_skill.update(skill_set)
      edges_list.update(edges)
    #complete retrieve student records and add to basic historical path
    # ======================================================
    # 4. Rebuild graph information after merging
    # ======================================================

    node_freq_to_skills = { skill_id: 0 for skill_id in visited_skill }
    incoming_graph = { skill_id: [] for skill_id in visited_skill }

    for from_skill, to_skill in edges_list:
        incoming_graph[from_skill].append(to_skill)
        node_freq_to_skills[to_skill] += 1

    root = [ skill_id for skill_id, indegree in node_freq_to_skills.items() if indegree == 0]

    # ======================================================
    # 5. Return merged graph and template information
    # ======================================================

    return (
        root, incoming_graph,
        visited_skill, 
        node_freq_to_skills,
        edges_list, 
    )

def fixing_building_learning_graph(visited_skill: set[int], edges_list: set[tuple[int, int]]):
    # Step 1: Detect and repair cycles
    remaining_edges, removed_edges = repair_cycle(visited_skill,edges_list)

    # Step 2: Rebuild graph structures
    node_freq_to_skills = { skill_id: 0 for skill_id in visited_skill }
    adjacency_graph = { skill_id: [] for skill_id in visited_skill }

    for from_skill, to_skill in remaining_edges:
        adjacency_graph[from_skill].append(to_skill)
        node_freq_to_skills[to_skill] += 1

    # Step 3: Find root nodes
    root = [skill_id for skill_id, indegree in node_freq_to_skills.items() if indegree == 0]

    # Step 4: Calculate graph layers
    layers = buildLayers( visited_skill, node_freq_to_skills, adjacency_graph, root)

    return (
        root,
        adjacency_graph,
        node_freq_to_skills,
        layers
    )
def build_learning_path_response(
    db: Session,
    original_query: str,
    goal_type: str,
    path_id: int,
    visited_skill: set[int],
    layers: dict[int, int],
    outgoing_graph: dict[int, list[int]]
):
    node_roles = {skill_id: "prerequisite" for skill_id in visited_skill}
    # ======================================================
    # 2. Collect graph edge pairs
    # =====================================================

    edge_pairs = []
    for from_skill,neighbors in outgoing_graph.items():
        for to_skill in neighbors:
            edge_pairs.append((from_skill, to_skill))

    # ======================================================
    # 3. Retrieve relationships from SkillRelation
    # ======================================================
    edge_pair_set = set(edge_pairs)
    relation_map = {}
    if edge_pair_set:
        statement = select(SkillRelation).where(
            SkillRelation.from_skill_id.in_({from_skill for from_skill, _ in edge_pair_set}),
            SkillRelation.to_skill_id.in_({to_skill for _, to_skill in edge_pair_set})
        )

        relations = db.execute(statement).scalars().all()

        relation_map = {
            (relation.from_skill_id, relation.to_skill_id): relation.relation_type
            for relation in relations
            if (relation.from_skill_id, relation.to_skill_id) in edge_pair_set
        }

    # ======================================================
    # 4. Determine node roles using incoming relationships
    # ======================================================

    role_priority = { "prerequisite": 0, "related": 1, "extension": 2}

    for from_skill, to_skill in edge_pairs:
        relation_type = relation_map.get((from_skill, to_skill), "extension")
        current_role = node_roles[to_skill]
        if role_priority[relation_type] > role_priority[current_role]:
            node_roles[to_skill] = relation_type

    # ======================================================
    # 5. Sort nodes by layer, then skill ID
    # ======================================================

    ordered_skills = sorted(visited_skill, key=lambda skill_id: (layers[skill_id], skill_id))

    # ======================================================
    # 6. Build nodes
    # ======================================================
    nodes = []
    for index, skill_id in enumerate(ordered_skills):
        node_role = node_roles[skill_id]
        nodes.append({
            "path_id": path_id,
            "skill_id": skill_id,
            "node_role": node_role,
            "is_target": False,
            "added_by": "system",
            "is_required": node_role == "prerequisite",
            "display_order": (index + 1) * 1000
        })

    # ======================================================
    # 7. Build edges using SkillRelation
    # ======================================================
    edges = []
    for from_skill, to_skill in edge_pairs:
        relation_type = relation_map.get((from_skill, to_skill))
        if relation_type is None: continue
        edges.append({
            "path_id": path_id,
            "from_skill_id": from_skill,
            "to_skill_id": to_skill,
            "relation_type": relation_type
        })

    # ======================================================
    # 8. Group skills by layer
    # ======================================================
    layer_groups = {}
    for skill_id, layer_number in layers.items():
        layer_groups.setdefault(layer_number, []).append(skill_id)
    layer_groups = {
        layer_number: sorted(skill_ids)
        for layer_number, skill_ids in sorted(layer_groups.items())
    }
    return {
        "original_query": original_query,
        "goal_type": goal_type,
        "nodes": nodes,
        "edges": edges,
        "layer": layer_groups
    }

def generate_learning_path(
    db: Session,
    LLM_input_skill_list: list[int],
    user_query: str,
    goal_type: str,
    path_id: int | None
):
    if not LLM_input_skill_list:
        raise ValueError("At least one target skill is required.")
    
    (root, outgoing_graph, visited_skill, node_freq_to_skills, 
     edges_list) = build_learning_path_pipeline(db, LLM_input_skill_list, user_query)

    (root, outgoing_graph, node_freq_to_skills, 
     layers) = fixing_building_learning_graph(visited_skill, edges_list)

    result = build_learning_path_response(
        db=db,
        original_query=user_query,
        goal_type=goal_type,
        path_id=path_id,
        visited_skill=visited_skill,
        layers=layers,
        outgoing_graph=outgoing_graph
    )
    return result