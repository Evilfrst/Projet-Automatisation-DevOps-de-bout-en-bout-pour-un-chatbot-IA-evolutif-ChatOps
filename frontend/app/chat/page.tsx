'use client'

import { useState } from 'react'

import { apiFetch, readApiError } from '@/lib/api'

export default function ChatPage() {
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const sendMessage = async () => {
    const currentPrompt = prompt.trim()
    if (!currentPrompt || loading) return

    setLoading(true)
    setError('')

    try {
      const result = await apiFetch('/chat', {
        method: 'POST',
        body: JSON.stringify({ prompt: currentPrompt }),
      })

      if (!result.ok) {
        throw new Error(await readApiError(result, 'Erreur du backend'))
      }

      const data = await result.json()
      setResponse(data.response)
      setPrompt('')
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : 'Erreur de connexion au backend',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-950 p-10 text-white">
      <h1 className="mb-6 text-4xl font-bold">AI Chatbot</h1>

      <input
        className="w-full rounded-lg p-4 text-black"
        placeholder="Ask something..."
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter') void sendMessage()
        }}
      />

      <button
        onClick={() => void sendMessage()}
        disabled={loading}
        className="mt-4 rounded-lg bg-blue-600 px-6 py-3 disabled:opacity-60"
      >
        {loading ? 'Envoi...' : 'Send'}
      </button>

      {error && (
        <div className="mt-8 rounded-xl border border-red-500/30 bg-red-500/10 p-6 text-red-300">
          {error}
        </div>
      )}

      <div className="mt-8 rounded-xl bg-gray-900 p-6">{response}</div>
    </main>
  )
}
