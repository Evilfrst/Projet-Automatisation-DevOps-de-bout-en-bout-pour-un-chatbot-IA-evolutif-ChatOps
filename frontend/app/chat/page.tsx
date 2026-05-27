'use client'

import { useState } from 'react'
import axios from 'axios'

export default function ChatPage() {
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')

  const sendMessage = async () => {
    const res = await axios.get(
      axios.post('http://35.181.183.50:8000/chat', {
        prompt
})
    setResponse(res.data.response)
  }

  return (
    <main className="min-h-screen p-10 bg-gray-950 text-white">
      <h1 className="text-4xl font-bold mb-6">
        AI Chatbot
      </h1>

      <input
        className="w-full p-4 rounded-lg text-black"
        placeholder="Ask something..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />

      <button
        onClick={sendMessage}
        className="mt-4 bg-blue-600 px-6 py-3 rounded-lg"
      >
        Send
      </button>

      <div className="mt-8 bg-gray-900 p-6 rounded-xl">
        {response}
      </div>
    </main>
  )
}
