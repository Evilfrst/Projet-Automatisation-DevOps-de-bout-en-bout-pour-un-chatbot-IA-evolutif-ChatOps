'use client'

import { useState } from 'react'

export default function Home() {

  const [input, setInput] = useState('')

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Bienvenue sur ChatOps AI Enterprise 🚀'
    }
  ])

  const sendMessage = async () => {

    if (!input.trim()) return

    // Ajouter message utilisateur
    const userMessage = {
      role: 'user',
      content: input
    }

    setMessages((prev: any) => [
      ...prev,
      userMessage
    ])

    try {

      const response = await fetch(
        'http://backend:8000/chat',
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json',
          },

          body: JSON.stringify({
            message: input,
          }),
        }
      )

      const data = await response.json()

      // Ajouter réponse IA
      setMessages((prev: any) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response
        }
      ])

    } catch (error) {

      console.error('Erreur API :', error)

      setMessages((prev: any) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Erreur de connexion au backend ❌'
        }
      ])
    }

    // Reset input
    setInput('')
  }

  return (

    <main className="min-h-screen bg-black text-white p-10">

      <div className="max-w-6xl mx-auto">

        {/* HEADER */}
        <div className="mb-10">

          <h1 className="text-6xl font-bold mb-4">
            ChatOps AI Enterprise
          </h1>

          <p className="text-gray-400 text-xl">
            DevOps • Kubernetes • OpenAI • Monitoring
          </p>

        </div>

        {/* STATS */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">

          {[
            ['CPU Usage', '43%'],
            ['RAM Usage', '68%'],
            ['Pods Running', '12'],
            ['CI/CD', 'Healthy']
          ].map(([title, value]) => (

            <div
              key={title}
              className="bg-white/5 border border-white/10 rounded-3xl p-6"
            >

              <p className="text-gray-400">
                {title}
              </p>

              <h2 className="text-4xl font-bold mt-3">
                {value}
              </h2>

            </div>
          ))}

        </div>

        {/* CHAT */}
        <div className="bg-white/5 border border-white/10 rounded-3xl p-6 h-[600px] flex flex-col">

          {/* MESSAGES */}
          <div className="flex-1 overflow-auto space-y-5 mb-5">

            {messages.map((message: any, index) => (

              <div
                key={index}
                className={`flex ${
                  message.role === 'user'
                    ? 'justify-end'
                    : 'justify-start'
                }`}
              >

                <div
                  className={`max-w-[80%] rounded-3xl px-5 py-4 ${
                    message.role === 'user'
                      ? 'bg-blue-600'
                      : 'bg-white/10'
                  }`}
                >

                  {message.content}

                </div>

              </div>

            ))}

          </div>

          {/* INPUT */}
          <div className="flex gap-4">

            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask your AI DevOps assistant..."
              className="flex-1 bg-white/10 border border-white/10 rounded-2xl px-5 py-4 outline-none"
            />

            <button
              onClick={sendMessage}
              className="bg-blue-600 hover:bg-blue-500 rounded-2xl px-8 py-4 font-semibold transition"
            >

              Send

            </button>

          </div>

        </div>

      </div>

    </main>
  )
}
