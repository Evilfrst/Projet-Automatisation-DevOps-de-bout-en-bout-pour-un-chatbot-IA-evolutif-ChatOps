'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()

    setLoading(true)

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
        setLoading(false)
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
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950">

      {/* Background Glow */}
      <div className="absolute inset-0">
        <div className="absolute left-[-150px] top-[-150px] h-[400px] w-[400px] rounded-full bg-cyan-500/20 blur-[140px]" />
        <div className="absolute right-[-150px] bottom-[-150px] h-[400px] w-[400px] rounded-full bg-purple-600/20 blur-[140px]" />
      </div>

      {/* Card */}
      <div className="relative z-10 w-full max-w-md px-6">

        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl shadow-2xl">

          {/* Logo */}
          <div className="mb-6 flex justify-center">
            <Image
              src="/chatops-logo.png"
              alt="ChatOps AI"
              width={170}
              height={170}
              priority
              className="drop-shadow-2xl"
            />
          </div>

          {/* Title */}
          <div className="text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
              ChatOps AI
            </h1>

            <p className="mt-3 text-sm text-slate-400">
              Plateforme intelligente d'automatisation DevOps
            </p>
          </div>

          {/* Form */}
          <form
            onSubmit={handleLogin}
            className="mt-8 space-y-5"
          >

            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Nom d'utilisateur
              </label>

              <input
                type="text"
                value={username}
                onChange={(e) =>
                  setUsername(e.target.value)
                }
                placeholder="admin"
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-4 py-3 text-white outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Mot de passe
              </label>

              <input
                type="password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                placeholder="••••••••"
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-4 py-3 text-white outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-600 px-4 py-3 font-semibold text-white shadow-lg transition-all hover:scale-[1.02] hover:shadow-cyan-500/25 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading
                ? 'Connexion...'
                : 'Se connecter'}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 border-t border-white/10 pt-4 text-center">
            <p className="text-xs text-slate-500">
              © 2026 ChatOps AI • DevOps • Kubernetes • IA
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
