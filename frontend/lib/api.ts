const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim()

export function getApiUrl(): string {
  if (configuredApiUrl) {
    return configuredApiUrl.replace(/\/$/, '')
  }

  // Reprend le comportement qui fonctionnait dans le deuxième ZIP :
  // sur AWS, le frontend 35.181.183.50:3000 appelle automatiquement
  // le backend 35.181.183.50:8000, sans figer l'adresse IP dans le code.
  if (typeof window !== 'undefined') {
    return `${window.location.protocol}//${window.location.hostname}:8000`
  }

  return 'http://localhost:8000'
}

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

  const response = await fetch(`${getApiUrl()}${path}`, {
    ...init,
    headers,
  })

  if (response.status === 401 && typeof window !== 'undefined') {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('username')

    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
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
