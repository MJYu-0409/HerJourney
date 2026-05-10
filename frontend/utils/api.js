// getApp() 不能在模块顶层调用（App 尚未初始化）
// 改为在每次请求时懒获取
const BASE_URL = 'http://127.0.0.1:8000'
const MOCK_USER_ID = 'mock-user-001'

// AI 接口响应慢，单独给长超时；普通接口 10s 足够
const TIMEOUT_AI = 120000
const TIMEOUT_DEFAULT = 15000

function request(method, path, data, timeout = TIMEOUT_DEFAULT) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${path}`,
      method,
      data,
      timeout,
      header: {
        'Content-Type': 'application/json',
        'X-User-Id': MOCK_USER_ID,
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          console.error(`[API] ${method} ${path} →`, res.statusCode, res.data)
          reject(res.data)
        }
      },
      fail(err) {
        console.error(`[API] ${method} ${path} 网络错误:`, err)
        reject(err)
      },
    })
  })
}

export const api = {
  // Chat
  sendMessage: (sessionId, content) =>
    request('POST', '/api/chat', { session_id: sessionId, content }, TIMEOUT_AI),
  getChatSessions: () => request('GET', '/api/chat/sessions'),
  getChatHistory: (sessionId) =>
    request('GET', `/api/chat/history?session_id=${sessionId}`),

  // Survey
  submitSurvey: (body) => request('POST', '/api/survey', body),
  getTodaySurvey: () => request('GET', '/api/survey/today'),
  getSurveyHistory: (days = 30) =>
    request('GET', `/api/survey/history?days=${days}`),

  // User
  getUserMe: () => request('GET', '/api/user/me'),

  // Profile
  getStats: () => request('GET', '/api/profile/stats'),
  getProfileStats: () => request('GET', '/api/profile/stats'),

  // Report
  getChart: (days = 90, symptoms = '') => {
    const q = symptoms ? `?days=${days}&symptoms=${symptoms}` : `?days=${days}`
    return request('GET', `/api/report/chart${q}`)
  },
  generateReport: (days, symptomKeys) =>
    request('POST', '/api/report/generate', { days, symptom_keys: symptomKeys }, TIMEOUT_AI),
  getDrafts: () => request('GET', '/api/report/drafts'),

  // Community
  getPosts: (params = {}) => {
    const q = Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== '')
      .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
      .join('&')
    return request('GET', `/api/community/posts${q ? '?' + q : ''}`)
  },
  getPost: (id) => request('GET', `/api/community/posts/${id}`),
  likePost: (id) => request('POST', `/api/community/posts/${id}/like`),
  getTags: () => request('GET', '/api/community/tags'),
  sharePost: (body) => request('POST', '/api/community/share', body),
}
