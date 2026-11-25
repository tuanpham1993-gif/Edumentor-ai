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
export async function getLearningPathById(recordId) {
  return await client.get(`/learning-paths/${recordId}`);
}

export async function addLearningPathNode(recordId, payload) {
  return await client.post(
    `/learning-paths-nodes/${recordId}/nodes`,
    payload
  );
}

export async function updateLearningPathNode(recordId, skillId, payload) {
  await client.patch(
    `/learning-paths-nodes/${recordId}/nodes/${skillId}`,
    payload
  );
}

export async function deleteLearningPathNode(recordId, skillId) {
  await client.delete(
    `/learning-paths-nodes/${recordId}/nodes/${skillId}`
  );
}

export async function addLearningPathEdge(recordId, payload) {
  await client.post(
    `/learning-path-edges/add?record_id=${recordId}`,
    payload
  );
}

export async function updateLearningPathEdge(recordId, payload) {
  await client.patch(
    `/learning-path-edges/update?record_id=${recordId}`,
    payload
  );
}

export async function deleteLearningPathEdge(recordId, payload) {
  await client.delete(
    `/learning-path-edges/remove?record_id=${recordId}`,
    { data: payload }
  );
}

// ---------------- AI learning path v2 (learning_path2) ----------------
// POST /learning-paths-generation/generate_ai_2  body = G1 input
//   { original_query, learner_input: { current_job_title, career_level, relevant_it_work_experience,
//     industry, technical_domains[], skill_profiles[{skill_name, proficiency_level, experience_duration}],
//     certifications[], learning_constraints: { available_study_time, deadline } } }
// The LLM runs on CPU: this call can take a minute or more.
export async function generateLearningPath2(payload) {
  const response = await client.post('/learning-paths-generation/generate_ai_2', payload);
  return response.data;
}

// Body = the preview from generateLearningPath2 plus { confirmed }.
export async function confirmLearningPath2(preview, confirmed = true) {
  const response = await client.post('/learning-paths-generation/confirm-2', { ...preview, confirmed });
  return response.data;
}

// { career_levels, proficiency_levels, certifications[{cert_id,name,issuer}], technical_domains[{domain_id,name}] }
export async function getLearningPathFormOptions() {
  const response = await client.get('/learning-paths-generation/options');
  return response.data;
}

// Learner profile snapshot of one AI v2 path (404 for older paths).
export async function getLearningPathProfile(recordId) {
  const response = await client.get(`/learning-paths/${recordId}/profile`);
  return response.data;
}
