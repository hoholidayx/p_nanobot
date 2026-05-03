import axios from 'axios'

// Injected at build time by vite.config.js ← webui/settings.json
// `__API_HOST__` and `__API_PORT__` are replaced at compile time.
// During dev, the Vite proxy handles /api → backend, so we use `/api/v1`.
// For production builds, we construct the full URL.
const baseURL = import.meta.env.DEV
  ? '/api/v1'
  : `http://${__API_HOST__}:${__API_PORT__}/api/v1`

const api = axios.create({
  baseURL,
  timeout: 10000,
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message
    return Promise.reject(new Error(msg))
  },
)

export default api
