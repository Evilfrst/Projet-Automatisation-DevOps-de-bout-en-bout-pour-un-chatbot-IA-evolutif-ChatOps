'use client'

import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import Image from 'next/image'

type Message = {
  role: 'user' | 'assistant'
  content: string
}

type ConversationHistory = {
  id: number
  title?: string
  user_message: string
  ai_response: string
}

type Metrics = {
  cpu: number
  ram: number
  pods: number
  cicd: string
}

export default function Home() {
  const [input, setInput] = useState('')

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Bienvenue sur ChatOps AI Enterprise 🚀',
    },
  ])

  const [history, setHistory] = useState<ConversationHistory[]>([])

  const [metrics, setMetrics] = useState<Metrics>({
    cpu: 0,
    ram: 0,
    pods: 0,
    cicd: 'Loading...',
  })

  const router = useRouter()

  const logout = () => {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  const loadHistory = async () => {
    const token = localStorage.getItem('token')

    try {
      const response = await fetch(
        'http://35.181.183.50:8000/history',
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) return

      const data = await response.json()

      setHistory(data)
    } catch (error) {
      console.error(
        'Erreur chargement historique :',
        error
      )
    }
  }

  const loadMetrics = async () => {
    const token = localStorage.getItem('token')

    try {
      const response = await fetch(
        'http://35.181.183.50:8000/monitoring/metrics',
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) return

      const data = await response.json()

      setMetrics({
        cpu: data.cpu ?? 0,
        ram: data.ram ?? 0,
        pods: data.pods ?? 0,
        cicd: data.cicd ?? 'Unknown',
      })
    } catch (error) {
      console.error(
        'Erreur chargement métriques :',
        error
      )
    }
  }

  useEffect(() => {
    const token =
      localStorage.getItem('token')

    if (!token) {
      router.push('/login')
      return
    }

    loadHistory()
    loadMetrics()

    const interval = setInterval(() => {
      loadMetrics()
    }, 5000)

    return () => clearInterval(interval)

  }, [router])

  const sendMessage = async () => {
    if (!input.trim()) return

    const token =
      localStorage.getItem('token')

    const userMessage: Message = {
      role: 'user',
      content: input,
    }

    setMessages((prev) => [
      ...prev,
      userMessage,
    ])

    const currentInput = input

    setInput('')

    try {
      const response = await fetch(
        'http://35.181.183.50:8000/chat',
        {
          method: 'POST',
          headers: {
            'Content-Type':
              'application/json',
            Authorization:
              `Bearer ${token}`,
          },
          body: JSON.stringify({
            prompt: message,
          }),
        }
      )

      if (!response.ok) {
        throw new Error(
          'Erreur backend'
        )
      }

      const data =
        await response.json()

      await loadHistory()

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
        },
      ])
    } catch (error) {
      console.error(
        'Erreur API :',
        error
      )

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'Erreur de connexion au backend ❌',
        },
      ])
    }
  }

  return (
    <main
      className="
        min-h-screen
        bg-gradient-to-br
        from-slate-950
        via-slate-900
        to-black
        text-white
        p-8
      "
    >
      <div className="max-w-7xl mx-auto">

        <header className="flex items-center justify-between mb-12">

          <div className="flex items-center gap-4">
            <Image
              src="/chatops-logo.png"
              alt="ChatOps AI"
              width={64}
              height={64}
              priority
            />

            <div>
              <h1 className="text-4xl font-bold tracking-tight">
                ChatOps AI
              </h1>

              <p className="text-slate-400">
                Enterprise DevSecOps Platform
              </p>
            </div>
          </div>

          <div className="hidden md:flex gap-3 items-center">

            <span className="px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm">
              AI Powered
            </span>

            <span className="px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-sm">
              DevSecOps
            </span>

            <span className="px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm">
              Production Ready
            </span>

            <button
              onClick={logout}
              className="
                px-4
                py-2
                rounded-full
                bg-red-500/10
                border
                border-red-500/20
                text-red-400
                text-sm
                hover:bg-red-500/20
              "
            >
              Déconnexion
            </button>

          </div>

        </header>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">

          {[
            ['CPU Usage', `${metrics.cpu}%`],
            ['RAM Usage', `${metrics.ram}%`],
            ['Pods Running', `${metrics.pods}`],
            ['CI/CD', metrics.cicd],
          ].map(([title, value]) => (

            <div
              key={title}
              className="
                bg-slate-900/60
                backdrop-blur-xl
                border
                border-slate-800
                rounded-3xl
                p-6
                shadow-xl
                shadow-blue-500/5
              "
            >
              <p className="text-slate-400">
                {title}
              </p>

              <h2 className="text-4xl font-bold mt-3">
                {value}
              </h2>
            </div>
          ))}
        </div>
        <div className="flex gap-6">
          <div
            className="
              w-80
              bg-slate-900/70
              backdrop-blur-xl
              border
              border-slate-800
              rounded-3xl
              p-5
              h-[650px]
              overflow-auto
              shrink-0
            "
          >
            <h2 className="text-xl font-bold mb-4">
              Historique
            </h2>

            <div className="space-y-2">
              {history.map((item) => (
                <button
                  key={item.id}
                  onClick={() =>
                    setMessages([
                      {
                        role: 'user',
                        content: item.user_message,
                      },
                      {
                        role: 'assistant',
                        content: item.ai_response,
                      },
                    ])
                  }
                  className="
                    w-full
                    text-left
                    p-3
                    rounded-xl
                    bg-slate-800/50
                    hover:bg-slate-700
                    transition
                    text-sm
                  "
                >
                  {item.title ||
                    item.user_message.slice(0, 40)}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1">

            <div
              className="
                bg-slate-900/70
                backdrop-blur-xl
                border
                border-slate-800
                rounded-3xl
                p-6
                h-[650px]
                flex
                flex-col
                shadow-2xl
                shadow-blue-500/10
              "
            >
              <div className="flex-1 overflow-auto space-y-5 mb-5 pr-2">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={
                      message.role === 'user'
                       ? 'flex justify-end'
                        : 'flex justify-start'
                    }
                  >
                    <div
                      className={
                        message.role === 'user'
                          ? 'max-w-[80%] rounded-3xl px-5 py-4 bg-gradient-to-r from-blue-600 to-indigo-600'
                          : 'max-w-[80%] rounded-3xl px-5 py-4 bg-slate-800/80 border border-slate-700'
                      }
                    >
                      {message.content}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex gap-4">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask your AI DevOps assistant..."
                  className="
                    flex-1
                    bg-slate-800/80
                    border
                    border-slate-700
                    rounded-2xl
                    px-5
                    py-4
                    outline-none
                    focus:border-blue-500
                    transition
                  "
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      sendMessage()
                    }
                  }}
                />

                <button
                  onClick={sendMessage}
                  className="
                    bg-gradient-to-r
                    from-blue-600
                    to-purple-600
                    hover:from-blue-500
                    hover:to-purple-500
                    rounded-2xl
                    px-8
                    py-4
                    font-semibold
                    transition
                  "
                >
                  Send
                </button>
              </div>
            </div>

          </div>

        </div>
      </div>
    </main>
  )
}
