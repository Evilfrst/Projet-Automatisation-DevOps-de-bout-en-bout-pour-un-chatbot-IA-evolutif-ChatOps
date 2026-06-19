const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000'

export function apiFetch(
  endpoint: string,
  options: RequestInit = {}
) {
  return fetch(`${API_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })
}

export async function readApiError(
  response: Response,
  fallback: string
) {
  try {
    const data = await response.json()
    return data.detail || fallback
  } catch {
    return fallback
  }
}
