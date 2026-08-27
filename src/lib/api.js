const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

export function getSession() {
  try {
    return JSON.parse(localStorage.getItem('smm_session') || 'null')
  } catch {
    return null
  }
}

export function setSession(session) {
  if (session) localStorage.setItem('smm_session', JSON.stringify(session))
  else localStorage.removeItem('smm_session')
  window.dispatchEvent(new Event('smm-session'))
}

export async function api(path, options = {}) {
  const session = getSession()
  const headers = new Headers(options.headers || {})
  if (session?.token) headers.set('Authorization', `Bearer ${session.token}`)
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  let response
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers })
  } catch {
    throw new Error('Cannot connect to the Flask API. Start the backend on port 5001.')
  }

  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json') ? await response.json() : null
  if (!response.ok) {
    if (response.status === 401) setSession(null)
    throw new Error(data?.error || `Request failed with status ${response.status}`)
  }
  return data
}

export async function uploadPhotos(eventId, files) {
  const form = new FormData()
  form.append('event_id', eventId)
  Array.from(files).forEach((file) => form.append('photos', file))
  return api('/photos/upload', { method: 'POST', body: form })
}

export async function searchWithSelfie(eventId, accessCode, selfie) {
  const form = new FormData()
  form.append('access_code', accessCode)
  form.append('consent', 'true')
  form.append('selfie', selfie)
  return api(`/face/search/${eventId}`, { method: 'POST', body: form })
}

export { API_URL }
