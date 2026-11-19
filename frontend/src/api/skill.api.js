import client from './client.js';

export async function getSkills({
  keyword = '',
  skip = 0,
  limit = 50,
} = {}) {
  return await client.get('/skills', {
    params: {
      keyword: keyword || undefined,
      skip,
      limit,
    },
  });
}