import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  timeout: 30_000,
})

export const fetchJobs = (keywords = 'software engineer', country = 'us', page = 1) =>
  api.get('/jobs/fetch', { params: { keywords, country, page, results_per_page: 50 } })

export const listJobs = (page = 1, pageSize = 20) =>
  api.get('/jobs', { params: { page, page_size: pageSize } })

export const getTrendingSkills = (limit = 20) =>
  api.get('/skills/trending', { params: { limit } })

export const getSkillHistory = (topN = 5) =>
  api.get('/skills/history', { params: { top_n: topN } })

export const analyzeResume = (resumeText, topNSkills = 30) =>
  api.post('/resume/analyze', { resume_text: resumeText, top_n_skills: topNSkills })

export default api
