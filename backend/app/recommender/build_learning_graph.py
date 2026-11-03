skills = [
    {"skill_id": 1, "skill_name": "Programming Fundamentals"},
    {"skill_id": 2, "skill_name": "Python"},
    {"skill_id": 3, "skill_name": "SQL Fundamentals"},
    {"skill_id": 4, "skill_name": "HTTP & REST API"},
    {"skill_id": 5, "skill_name": "FastAPI"},
    {"skill_id": 6, "skill_name": "PostgreSQL"},
    {"skill_id": 7, "skill_name": "Git"},
    {"skill_id": 8, "skill_name": "Docker"},
    {"skill_id": 9, "skill_name": "Deployment"},
    {"skill_id": 10, "skill_name": "Linux Fundamentals"},
    {"skill_id": 11, "skill_name": "Flask"},
    {"skill_id": 12, "skill_name": "Advanced FastAPI"},
    {"skill_id": 13, "skill_name": "React"},
    {"skill_id": 14, "skill_name": "JavaScript"},
    {"skill_id": 15, "skill_name": "HTML & CSS"},

    # New skills
    {"skill_id": 16, "skill_name": "Data Structures & Algorithms"},
    {"skill_id": 17, "skill_name": "Object-Oriented Programming"},
    {"skill_id": 18, "skill_name": "Authentication & Authorization"},
    {"skill_id": 19, "skill_name": "Automated Testing"},
    {"skill_id": 20, "skill_name": "CI/CD"},
    {"skill_id": 21, "skill_name": "Cloud Fundamentals"},
    {"skill_id": 22, "skill_name": "Redis"},
    {"skill_id": 23, "skill_name": "Message Queues"},
    {"skill_id": 24, "skill_name": "Microservices"},
    {"skill_id": 25, "skill_name": "System Design"},
    {"skill_id": 26, "skill_name": "ORM"},
    {"skill_id": 27, "skill_name": "Java"},
    {"skill_id": 28, "skill_name": "Spring Boot"},
    {"skill_id": 29, "skill_name": "TypeScript"},
    {"skill_id": 30, "skill_name": "Next.js"},
]

skill_relations = [
    # =========================================
    # 1. Programming foundations
    # =========================================
    {"from": 1, "to": 2, "relation_type": "prerequisite"},
    {"from": 1, "to": 3, "relation_type": "prerequisite"},
    {"from": 1, "to": 16, "relation_type": "prerequisite"},
    {"from": 1, "to": 17, "relation_type": "prerequisite"},
    {"from": 1, "to": 27, "relation_type": "prerequisite"},

    {"from": 2, "to": 4, "relation_type": "prerequisite"},
    {"from": 2, "to": 6, "relation_type": "prerequisite"},
    {"from": 2, "to": 11, "relation_type": "prerequisite"},
    {"from": 2, "to": 19, "relation_type": "prerequisite"},

    # Multiple prerequisites for FastAPI
    {"from": 4, "to": 5, "relation_type": "prerequisite"},
    {"from": 17, "to": 5, "relation_type": "prerequisite"},

    # =========================================
    # 2. Database branch
    # =========================================
    {"from": 3, "to": 6, "relation_type": "prerequisite"},
    {"from": 2, "to": 26, "relation_type": "prerequisite"},
    {"from": 6, "to": 26, "relation_type": "prerequisite"},

    # =========================================
    # 3. Backend/API branch
    # =========================================
    {"from": 5, "to": 12, "relation_type": "prerequisite"},
    {"from": 5, "to": 18, "relation_type": "prerequisite"},
    {"from": 6, "to": 18, "relation_type": "prerequisite"},
    {"from": 5, "to": 19, "relation_type": "prerequisite"},
    {"from": 26, "to": 19, "relation_type": "prerequisite"},

    # Multiple frameworks may share foundational skills
    {"from": 4, "to": 11, "relation_type": "prerequisite"},
    {"from": 27, "to": 28, "relation_type": "prerequisite"},
    {"from": 4, "to": 28, "relation_type": "prerequisite"},

    # =========================================
    # 4. Deployment branch
    # =========================================
    {"from": 5, "to": 8, "relation_type": "prerequisite"},
    {"from": 7, "to": 8, "relation_type": "prerequisite"},
    {"from": 10, "to": 8, "relation_type": "prerequisite"},

    # Shared prerequisite: Git is needed by both Docker and CI/CD
    {"from": 7, "to": 20, "relation_type": "prerequisite"},
    {"from": 8, "to": 20, "relation_type": "prerequisite"},

    # Multiple prerequisites for deployment
    {"from": 8, "to": 9, "relation_type": "prerequisite"},
    {"from": 7, "to": 9, "relation_type": "prerequisite"},
    {"from": 21, "to": 9, "relation_type": "prerequisite"},

    # Cloud and Linux can be shared by several infrastructure skills
    {"from": 10, "to": 21, "relation_type": "prerequisite"},
    {"from": 8, "to": 24, "relation_type": "prerequisite"},
    {"from": 18, "to": 24, "relation_type": "prerequisite"},
    {"from": 22, "to": 24, "relation_type": "prerequisite"},
    {"from": 23, "to": 24, "relation_type": "prerequisite"},

    # =========================================
    # 5. Shared system design prerequisites
    # =========================================
    {"from": 16, "to": 25, "relation_type": "prerequisite"},
    {"from": 4, "to": 25, "relation_type": "prerequisite"},
    {"from": 6, "to": 25, "relation_type": "prerequisite"},

    # Redis and message queues have independent foundations
    {"from": 2, "to": 22, "relation_type": "prerequisite"},
    {"from": 4, "to": 23, "relation_type": "prerequisite"},

    # =========================================
    # 6. Frontend branch
    # =========================================
    {"from": 15, "to": 14, "relation_type": "prerequisite"},
    {"from": 14, "to": 13, "relation_type": "prerequisite"},
    {"from": 14, "to": 29, "relation_type": "prerequisite"},
    {"from": 29, "to": 30, "relation_type": "prerequisite"},
    {"from": 13, "to": 30, "relation_type": "prerequisite"},

    # =========================================
    # 7. Intentional cycle for testing
    # REMOVE these edges for normal sorting
    # =========================================
    {"from": 12, "to": 24, "relation_type": "prerequisite"},
    {"from": 24, "to": 12, "relation_type": "prerequisite"},

    # =========================================
    # 8. Related relations (not mandatory)
    # =========================================
    {"from": 5, "to": 11, "relation_type": "related"},
    {"from": 6, "to": 3, "relation_type": "related"},
    {"from": 13, "to": 5, "relation_type": "related"},
    {"from": 22, "to": 6, "relation_type": "related"},

    # =========================================
    # 9. Extensions (optional advanced skills)
    # =========================================
    {"from": 5, "to": 12, "relation_type": "extension"},
    {"from": 6, "to": 9, "relation_type": "extension"},
    {"from": 9, "to": 20, "relation_type": "extension"},
]
path_templates = [
    {
        "template_id": 1,
        "template_name": "Python Backend Developer",
        "skills": [
            {"skill_id": 1, "position": 1000},
            {"skill_id": 2, "position": 2000},
            {"skill_id": 4, "position": 3000},
            {"skill_id": 5, "position": 4000},
            {"skill_id": 3, "position": 5000},
            {"skill_id": 6, "position": 6000},
            {"skill_id": 18, "position": 7000},
            {"skill_id": 19, "position": 8000},
            {"skill_id": 7, "position": 9000},
            {"skill_id": 10, "position": 10000},
            {"skill_id": 8, "position": 11000},
            {"skill_id": 21, "position": 12000},
            {"skill_id": 9, "position": 13000},
            {"skill_id": 20, "position": 14000},
        ],
    },
    {
        "template_id": 2,
        "template_name": "Frontend Developer",
        "skills": [
            {"skill_id": 15, "position": 1000},
            {"skill_id": 14, "position": 2000},
            {"skill_id": 29, "position": 3000},
            {"skill_id": 13, "position": 4000},
            {"skill_id": 30, "position": 5000},
        ],
    },
    {
        "template_id": 3,
        "template_name": "Python Web Frameworks",
        "skills": [
            {"skill_id": 1, "position": 1000},
            {"skill_id": 2, "position": 2000},
            {"skill_id": 17, "position": 3000},
            {"skill_id": 4, "position": 4000},
            {"skill_id": 5, "position": 5000},
            {"skill_id": 11, "position": 6000},
            {"skill_id": 12, "position": 7000},
        ],
    },
    {
        "template_id": 4,
        "template_name": "Java Backend Developer",
        "skills": [
            {"skill_id": 1, "position": 1000},
            {"skill_id": 27, "position": 2000},
            {"skill_id": 4, "position": 3000},
            {"skill_id": 28, "position": 4000},
            {"skill_id": 3, "position": 5000},
            {"skill_id": 6, "position": 6000},
            {"skill_id": 7, "position": 7000},
            {"skill_id": 8, "position": 8000},
            {"skill_id": 9, "position": 9000},
        ],
    },
    {
        "template_id": 5,
        "template_name": "Backend Systems & Microservices",
        "skills": [
            {"skill_id": 1, "position": 1000},
            {"skill_id": 2, "position": 2000},
            {"skill_id": 4, "position": 3000},
            {"skill_id": 5, "position": 4000},
            {"skill_id": 6, "position": 5000},
            {"skill_id": 18, "position": 6000},
            {"skill_id": 22, "position": 7000},
            {"skill_id": 23, "position": 8000},
            {"skill_id": 8, "position": 9000},
            {"skill_id": 24, "position": 10000},
            {"skill_id": 16, "position": 11000},
            {"skill_id": 25, "position": 12000},
        ],
    },
]

LLM_output_skill = [5, 6, 9]

def createVisited(target_skill, all_ready_node):
    visited_set = set()
    ready_node = all_ready_node
    while (ready_node):
        skill_id = ready_node.pop(0)
        if(skill_id in visited_set):
            continue
        visited_set.add(skill_id)
        for each in skill_relations:
            if(each["relation_type"] == "prerequisite" and skill_id == each["to"]):
                ready_node.append(each["from"])
    return visited_set

target = 8
visited = createVisited(target, [target])

#can be improve with map skill_relationship
def createEdge_RetrieveRoot(visited):
    node_freq = {}
    edges = set()
    for skill_id in visited:
        count_freq = node_freq.get(skill_id, 0)
        for each in skill_relations:
            if (each["to"] == skill_id and each["from"] in visited and each["relation_type"] == "prerequisite"):
                count_freq = count_freq + 1
                edges.add((each["from"], each["to"]))
                
        node_freq[skill_id] = count_freq
    root = [n for n in node_freq.keys() if node_freq[n] == 0]
    graph = {}
    for u, v in edges:
        list_of_skill = graph.get(u, [])
        list_of_skill.append(v)
        graph[u] = list_of_skill
    return edges, graph

edges, graph = createEdge_RetrieveRoot(visited)
print(graph)
edges