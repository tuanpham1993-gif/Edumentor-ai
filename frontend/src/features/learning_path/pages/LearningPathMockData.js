
export const mockLearningPaths = [
  {
    student_id: 1,
    record_id: 101,
    original_query: 'Data Analyst',
    goal_type: 'career',
    status: 'ongoing',

    nodes: [
      {
        path_id: 101,
        skill_id: 26,
        node_role: 'prerequisite',
        is_target: true,
        added_by: 'system',
        is_required: true,
        display_order: 1000,
        skill: {
          skill_id: 26,
          skill: 'Computer Programming',
        },
      },
      {
        path_id: 101,
        skill_id: 87,
        node_role: 'prerequisite',
        is_target: true,
        added_by: 'system',
        is_required: true,
        display_order: 2000,
        skill: {
          skill_id: 87,
          skill: 'Database Management',
        },
      },
      {
        path_id: 101,
        skill_id: 305,
        node_role: 'prerequisite',
        is_target: true,
        added_by: 'system',
        is_required: true,
        display_order: 3000,
        skill: {
          skill_id: 305,
          skill: 'SQL',
        },
      },
      {
        path_id: 101,
        skill_id: 349,
        node_role: 'prerequisite',
        is_target: true,
        added_by: 'system',
        is_required: true,
        display_order: 4000,
        skill: {
          skill_id: 349,
          skill: 'SQLite',
        },
      },
      {
        path_id: 101,
        skill_id: 499,
        node_role: 'prerequisite',
        is_target: false,
        added_by: 'system',
        is_required: true,
        display_order: 5000,
        skill: {
          skill_id: 499,
          skill: 'Python Programming',
        },
      },
      {
        path_id: 101,
        skill_id: 430,
        node_role: 'prerequisite',
        is_target: false,
        added_by: 'system',
        is_required: true,
        display_order: 6000,
        skill: {
          skill_id: 430,
          skill: 'Statistics',
        },
      },
      {
        path_id: 101,
        skill_id: 941,
        node_role: 'prerequisite',
        is_target: false,
        added_by: 'system',
        is_required: true,
        display_order: 7000,
        skill: {
          skill_id: 941,
          skill: 'Data Visualization',
        },
      },
    ],

    edges: [
      {
        path_id: 101,
        from_skill_id: 26,
        to_skill_id: 499,
        relation_type: 'prerequisite',
        from_skill: {
          skill_id: 26,
          skill: 'Computer Programming',
        },
        to_skill: {
          skill_id: 499,
          skill: 'Python Programming',
        },
      },
      {
        path_id: 101,
        from_skill_id: 87,
        to_skill_id: 305,
        relation_type: 'prerequisite',
        from_skill: {
          skill_id: 87,
          skill: 'Database Management',
        },
        to_skill: {
          skill_id: 305,
          skill: 'SQL',
        },
      },
      {
        path_id: 101,
        from_skill_id: 305,
        to_skill_id: 349,
        relation_type: 'prerequisite',
        from_skill: {
          skill_id: 305,
          skill: 'SQL',
        },
        to_skill: {
          skill_id: 349,
          skill: 'SQLite',
        },
      },
      {
        path_id: 101,
        from_skill_id: 499,
        to_skill_id: 430,
        relation_type: 'related',
        from_skill: {
          skill_id: 499,
          skill: 'Python Programming',
        },
        to_skill: {
          skill_id: 430,
          skill: 'Statistics',
        },
      },
      {
        path_id: 101,
        from_skill_id: 430,
        to_skill_id: 941,
        relation_type: 'extension',
        from_skill: {
          skill_id: 430,
          skill: 'Statistics',
        },
        to_skill: {
          skill_id: 941,
          skill: 'Data Visualization',
        },
      },
    ],
  },

  {
    student_id: 1,
    record_id: 102,
    original_query: 'Android Developer',
    goal_type: 'career',
    status: 'ongoing',

    nodes: [
      {
        path_id: 102,
        skill_id: 3573,
        node_role: 'prerequisite',
        is_target: false,
        added_by: 'system',
        is_required: true,
        display_order: 1000,
        skill: {
          skill_id: 3573,
          skill: 'Kotlin',
        },
      },
      {
        path_id: 102,
        skill_id: 4073,
        node_role: 'prerequisite',
        is_target: false,
        added_by: 'system',
        is_required: true,
        display_order: 2000,
        skill: {
          skill_id: 4073,
          skill: 'Android Development',
        },
      },
      {
        path_id: 102,
        skill_id: 430,
        node_role: 'prerequisite',
        is_target: false,
        added_by: 'user',
        is_required: false,
        display_order: 3000,
        skill: {
          skill_id: 430,
          skill: 'Object-Oriented Programming',
        },
      },
    ],

    edges: [
      {
        path_id: 102,
        from_skill_id: 3573,
        to_skill_id: 4073,
        relation_type: 'prerequisite',
        from_skill: {
          skill_id: 3573,
          skill: 'Kotlin',
        },
        to_skill: {
          skill_id: 4073,
          skill: 'Android Development',
        },
      },
      {
        path_id: 102,
        from_skill_id: 430,
        to_skill_id: 4073,
        relation_type: 'related',
        from_skill: {
          skill_id: 430,
          skill: 'Object-Oriented Programming',
        },
        to_skill: {
          skill_id: 4073,
          skill: 'Android Development',
        },
      },
    ],
  },
];

export const mockLearningPathListResponse = {
  total: mockLearningPaths.length,
  skip: 0,
  limit: 10,
  current_total: mockLearningPaths.length,
  data: mockLearningPaths,
};
