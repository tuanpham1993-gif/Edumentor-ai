import client from './client.js';

// /learning-paths-generation/generate: post
// /learning-paths-generation/confirm :post

export async function requestLearningPath({original_query}) {
  const response = await client.post('/learning-paths-generation/generate', {original_query});
  return response.data;
}

export async function confirmLearningPath({
  confirmed, original_query,
  goal_type, nodes, edges,
  layer}) {
  const response = await client.post('/learning-paths-generation/confirm', {
    confirmed,
    original_query,
    goal_type,
    nodes,
    edges,
    layer,
  });
  return response.data;
}


import { mockLearningPaths } from '../features/learning_path/pages/LearningPathMockData.js';

export async function getMyLearningPaths_wait({
  skip = 0, limit = 10,
  keyword = '', goalType = '',
  status = '',} = {}) {
  // Simulate an asynchronous API request.
  await new Promise((resolve) => setTimeout(resolve, 5));
  let filteredData = [...mockLearningPaths];
  // Search by original_query.
  if (keyword.trim()) {
    const normalizedKeyword = keyword.trim().toLowerCase();

    filteredData = filteredData.filter((path) =>
      path.original_query.toLowerCase().includes(normalizedKeyword)
    );
  }

  if (goalType) {
    filteredData = filteredData.filter((path) => path.goal_type === goalType);
  }

  // Filter by backend status.
  if (status) {
    filteredData = filteredData.filter((path) => path.status === status);
  }
  const total = filteredData.length;
  const data = filteredData.slice(skip, skip + limit);
  return {
    total, skip, limit,
    current_total: data.length,
    data,
  };
}

export async function getMyLearningPaths({
  skip, limit, keyword,
  goalType, status}) {
  const response = await client.get('/learning-paths', {
  params: {
    skip,
    limit,
    keyword,
    goal_type: goalType || undefined,
    status: status || undefined,
  },
});

return response.data;
}