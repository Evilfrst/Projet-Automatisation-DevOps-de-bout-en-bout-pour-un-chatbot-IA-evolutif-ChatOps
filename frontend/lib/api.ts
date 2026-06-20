const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  'http://35.181.183.50:8000'

export function apiFetch(
  endpoint: string,
  options: RequestInit = {}
) {
  const token =
    typeof window !== 'undefined'
      ? localStorage.getItem('token')
      : null

  return fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : {}),
      ...options.headers,
    },
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
