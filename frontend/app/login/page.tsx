'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const response = await fetch(
        'http://35.181.183.50:8000/login',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username,
            password,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        alert(data.detail || 'Erreur de connexion')
        return
      }

      localStorage.setItem(
        'token',
        data.access_token
      )

      router.push('/')
    } catch (error) {
      console.error(error)

      if (error instanceof Error) {
        alert(error.message)
      } else {
        alert('Erreur serveur')
      }
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <form
        onSubmit={handleLogin}
        className="flex flex-col gap-4 p-6 border rounded"
      >
        <h1 className="text-xl font-bold">
          Connexion
        </h1>

        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Nom d'utilisateur"
          className="border p-2"
        />

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Mot de passe"
          className="border p-2"
        />

        <button
          type="submit"
          className="border p-2"
        >
          Se connecter
        </button>
      </form>
    </div>
  )
}
