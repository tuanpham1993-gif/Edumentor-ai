const learningPathTestData = {
  original_query: "I want to become an Android app engineer.",
  goal_type: "career",

  nodes: [
    {
      skill_id: 26,
      skill_name: "Computer Programming",
      node_role: "prerequisite",
      is_required: true,
      display_order: 1000,
    },
    {
      skill_id: 87,
      skill_name: "Database (DBMS)",
      node_role: "prerequisite",
      is_required: true,
      display_order: 2000,
    },
    {
      skill_id: 305,
      skill_name: "SQL",
      node_role: "prerequisite",
      is_required: true,
      display_order: 7000,
    },
    {
      skill_id: 349,
      skill_name: "Sqlite",
      node_role: "prerequisite",
      is_required: true,
      display_order: 9000,
    },
  ],

  edges: [
    {
      from_skill_id: 87,
      to_skill_id: 305,
      relation_type: "prerequisite",
    },
    {
      from_skill_id: 305,
      to_skill_id: 349,
      relation_type: "prerequisite",
    },
  ],

  layer: {
    "0": [26, 87],
    "1": [305],
    "2": [349],
  },
};

export default learningPathTestData;