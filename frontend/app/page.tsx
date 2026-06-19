'use client'

import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { useCallback, useEffect, useState } from 'react'

import { apiFetch, readApiError } from '@/lib/api'

type Message = {
  role: 'user' | 'assistant'
  content: string
}

type ConversationHistory = {
  id: number
  title?: string
  user_message: string
  ai_response: string
  created_at?: string
}

type Metrics = {
  cpu: number | null
  memory: number | null
  pods: number
  running_pods: number
  failed_pods: number
  open_incidents: number
  cluster_status: string
  cluster_error: string | null
  cicd: string
}

const initialMetrics: Metrics = {
  cpu: null,
  memory: null,
  pods: 0,
  running_pods: 0,
  failed_pods: 0,
  open_incidents: 0,
  cluster_status: 'unknown',
  cluster_error: null,
  cicd: 'not_connected',
}

export default function Home() {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [pageError, setPageError] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Bienvenue sur ChatOps AI 🚀',
    },
  ])
  const [history, setHistory] = useState<ConversationHistory[]>([])
  const [metrics, setMetrics] = useState<Metrics>(initialMetrics)
  const router = useRouter()

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    router.replace('/login')
  }

  const loadHistory = useCallback(async () => {
    try {
      const response = await apiFetch('/history')
      if (!response.ok) {
        throw new Error(
          await readApiError(
            response,
            "Impossible de charger l'historique",
          ),
        )
      }
      setHistory(await response.json())
    } catch (error) {
      console.error('Erreur chargement historique :', error)
      setPageError(
        error instanceof Error
          ? error.message
          : "Impossible de charger l'historique",
      )
    }
  }, [])

  const loadMetrics = useCallback(async () => {
    try {
      const response = await apiFetch('/dashboard/summary')
      if (!response.ok) {
        throw new Error(
          await readApiError(
            response,
            'Impossible de charger les métriques',
          ),
        )
      }
      const data = await response.json()
      setMetrics({ ...initialMetrics, ...data })
    } catch (error) {
      console.error('Erreur chargement métriques :', error)
    }
  }, [])

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.replace('/login')
      return
    }

    const initialLoad = window.setTimeout(() => {
      void loadHistory()
      void loadMetrics()
    }, 0)

    const interval = window.setInterval(() => {
      void loadMetrics()
    }, 15_000)

    return () => {
      window.clearTimeout(initialLoad)
      window.clearInterval(interval)
    }
  }, [loadHistory, loadMetrics, router])

  const sendMessage = async () => {
    const currentInput = input.trim()
    if (!currentInput || sending) return

    setSending(true)
    setPageError('')
    setInput('')
    setMessages((previous) => [
      ...previous,
      { role: 'user', content: currentInput },
    ])

    try {
      const response = await apiFetch('/chat', {
        method: 'POST',
        body: JSON.stringify({ prompt: currentInput }),
      })

      if (!response.ok) {
        throw new Error(
          await readApiError(response, 'Erreur du backend'),
        )
      }

      const data = await response.json()
      setMessages((previous) => [
        ...previous,
        { role: 'assistant', content: data.response },
      ])
      await loadHistory()
      await loadMetrics()
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : 'Erreur de connexion au backend'
      setMessages((previous) => [
        ...previous,
        { role: 'assistant', content: `Erreur : ${message}` },
      ])
      setPageError(message)
    } finally {
      setSending(false)
    }
  }

  const formatPercent = (value: number | null) =>
    value === null ? 'N/D' : `${value.toFixed(1)}%`

  const clusterLabel =
    metrics.cluster_status === 'healthy'
      ? 'Disponible'
      : 'Indisponible'

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-black p-4 text-white md:p-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-10 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Image
              src="/chatops-logo.png"
              alt="ChatOps AI"
              width={64}
              height={64}
              priority
            />
            <div>
              <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
                ChatOps AI
              </h1>
              <p className="text-slate-400">
                Assistant DevOps et Kubernetes
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-2 text-sm text-blue-400">
              MVP évolutif
            </span>
            <button
              onClick={logout}
              className="rounded-full border border-red-500/20 bg-red-500/10 px-4 py-2 text-sm text-red-400 hover:bg-red-500/20"
            >
              Déconnexion
            </button>
          </div>
        </header>

        {pageError && (
          <div className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
            {pageError}
          </div>
        )}

        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-6">
          {[
            ['CPU', formatPercent(metrics.cpu)],
            ['Mémoire', formatPercent(metrics.memory)],
            ['Pods', `${metrics.running_pods}/${metrics.pods}`],
            ['Pods en erreur', `${metrics.failed_pods}`],
            ['Incidents ouverts', `${metrics.open_incidents}`],
            ['Cluster', clusterLabel],
          ].map(([title, value]) => (
            <div
              key={title}
              className="rounded-3xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-xl"
            >
              <p className="text-sm text-slate-400">{title}</p>
              <h2 className="mt-2 text-2xl font-bold">{value}</h2>
            </div>
          ))}
        </div>

        {metrics.cluster_error && (
          <div className="mb-6 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-100">
            Kubernetes indisponible : {metrics.cluster_error}
          </div>
        )}

        <div className="flex flex-col gap-6 lg:flex-row">
          <aside className="h-[650px] w-full shrink-0 overflow-auto rounded-3xl border border-slate-800 bg-slate-900/70 p-5 backdrop-blur-xl lg:w-80">
            <h2 className="mb-4 text-xl font-bold">Historique</h2>
            <div className="space-y-2">
              {history.length === 0 && (
                <p className="text-sm text-slate-500">
                  Aucune conversation sauvegardée.
                </p>
              )}
              {history.map((item) => (
                <button
                  key={item.id}
                  onClick={() =>
                    setMessages([
                      { role: 'user', content: item.user_message },
                      {
                        role: 'assistant',
                        content: item.ai_response,
                      },
                    ])
                  }
                  className="w-full rounded-xl bg-slate-800/50 p-3 text-left text-sm transition hover:bg-slate-700"
                >
                  {item.title || item.user_message.slice(0, 40)}
                </button>
              ))}
            </div>
          </aside>

          <section className="flex h-[650px] flex-1 flex-col rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl backdrop-blur-xl">
            <div className="mb-5 flex-1 space-y-5 overflow-auto pr-2">
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={
                    message.role === 'user'
                      ? 'flex justify-end'
                      : 'flex justify-start'
                  }
                >
                  <div
                    className={
                      message.role === 'user'
                        ? 'max-w-[85%] whitespace-pre-wrap rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-4'
                        : 'max-w-[85%] whitespace-pre-wrap rounded-3xl border border-slate-700 bg-slate-800/80 px-5 py-4'
                    }
                  >
                    {message.content}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-3">
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Demandez à l'assistant de lister les pods..."
                disabled={sending}
                className="flex-1 rounded-2xl border border-slate-700 bg-slate-800/80 px-5 py-4 outline-none transition focus:border-blue-500 disabled:opacity-60"
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault()
                    void sendMessage()
                  }
                }}
              />
              <button
                onClick={() => void sendMessage()}
                disabled={sending || !input.trim()}
                className="rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 font-semibold transition hover:from-blue-500 hover:to-purple-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {sending ? 'Envoi...' : 'Envoyer'}
              </button>
            </div>
          </section>
        </div>
      </div>
    </main>
  )
}
