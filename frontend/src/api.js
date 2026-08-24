const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const TOKEN_KEY = 'crm_token'
const USER_KEY = 'crm_user'

export function saveSession(token, user) {
  sessionStorage.setItem(TOKEN_KEY, token)
  sessionStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function getUser() {
  const raw = sessionStorage.getItem(USER_KEY)
  return raw ? JSON.parse(raw) : null
}

export function clearSession() {
  sessionStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(USER_KEY)
}

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  console.log(`[API] ${options.method || 'GET'} ${API_BASE}${path}`)

  let response
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  } catch (err) {
    console.error(`[API ERROR] Network error:`, err)
    // Network-level failure — backend unreachable.
    throw new ApiError("I'm unable to connect to the CRM service right now. Please try again.", 0)
  }

  let data = null
  try {
    data = await response.json()
  } catch (_) {
    // no body
  }

  console.log(`[API] Response Status: ${response.status}`, data)

  if (!response.ok) {
    const message = (data && data.detail) || 'Something went wrong. Please try again.'
    throw new ApiError(typeof message === 'string' ? message : JSON.stringify(message), response.status)
  }
  return data
}

export const api = {
  login: (user_id, password) =>
    request('/api/auth/login', { method: 'POST', body: JSON.stringify({ user_id, password }) }),

  me: () => request('/api/customer/me'),

  products: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/api/products${qs ? `?${qs}` : ''}`)
  },

  categories: () => request('/api/categories'),

  ironOreSpecs: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/api/specs/iron-ore${qs ? `?${qs}` : ''}`)
  },

  ironPelletSpecs: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/api/specs/iron-pellet${qs ? `?${qs}` : ''}`)
  },

  chat: (message, action) =>
    request('/api/chat', { method: 'POST', body: JSON.stringify({ message, action }) }),

  validateOrderQuantity: (pid, quantity) =>
    request('/api/orders/validate-quantity', { 
      method: 'POST', 
      body: JSON.stringify({ pid, quantity }) 
    }),

  createComplaint: (category, description, poNumber, dispatchDate) =>
    request('/api/complaints', {
      method: 'POST',
      body: JSON.stringify({
        category_type: category,
        description,
        po_number: poNumber || null,
        dispatch_date: dispatchDate || null,
      }),
    }),

  health: () => request('/api/health'),
}

export { ApiError }