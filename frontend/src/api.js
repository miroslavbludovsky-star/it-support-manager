const API_BASE = '/api'

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  // Dashboard
  getDashboard: () => request('/dashboard/summary'),

  // Tickets
  getTickets: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/tickets${qs ? '?' + qs : ''}`)
  },
  getTicket: (id) => request(`/tickets/${id}`),
  getTicketByKey: (key) => request(`/tickets/by-key/${key}`),
  updateTicket: (id, data) => request(`/tickets/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  getRelatedTickets: (id) => request(`/tickets/${id}/related`),

  // Emails
  getEmails: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/emails${qs ? '?' + qs : ''}`)
  },
  getEmail: (id) => request(`/emails/${id}`),
  generateDraft: (id) => request(`/emails/${id}/draft`, { method: 'POST' }),

  // Settings
  getSettings: () => request('/settings'),
  getSetting: (key) => request(`/settings/${key}`),
  updateSetting: (key, value) => request(`/settings/${key}`, { method: 'PUT', body: JSON.stringify({ value }) }),

  // Sync
  triggerSync: () => request('/sync/trigger', { method: 'POST' }),
  getSyncStatus: () => request('/sync/status'),

  // Assistant
  chat: (message, ticketContextId = null) =>
    request('/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({ message, ticket_context_id: ticketContextId }),
    }),

  // Dev
  injectEmail: (data) => request('/dev/inject-email', { method: 'POST', body: JSON.stringify(data) }),
}
