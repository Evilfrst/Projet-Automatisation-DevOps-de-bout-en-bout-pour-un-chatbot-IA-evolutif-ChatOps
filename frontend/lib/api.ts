export const API_URL = (
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
).replace(/\/$/, '')

export async function apiFetch(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const headers = new Headers(init.headers)
  const token =
    typeof window !== 'undefined'
      ? localStorage.getItem('token')
      : null

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
  })

  if (response.status === 401 && typeof window !== 'undefined') {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    window.location.href = '/login'
  }

  return response
}

export async function readApiError(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const payload = await response.json()
    return payload.detail || payload.error || fallback
  } catch {
    return fallback
  }
}
