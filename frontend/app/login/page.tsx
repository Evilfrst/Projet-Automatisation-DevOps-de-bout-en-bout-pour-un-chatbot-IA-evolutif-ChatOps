'use client'

import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

import { apiFetch, readApiError } from '@/lib/api'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const router = useRouter()

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await apiFetch('/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      })

      if (!response.ok) {
        throw new Error(await readApiError(response, 'Erreur de connexion'))
      }

      const data = await response.json()
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('role', data.role || 'viewer')
      localStorage.setItem('username', data.username || username)
      router.replace('/')
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : 'Erreur de connexion au serveur',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950">
      <div className="absolute inset-0">
        <div className="absolute left-[-150px] top-[-150px] h-[400px] w-[400px] rounded-full bg-cyan-500/20 blur-[140px]" />
        <div className="absolute bottom-[-150px] right-[-150px] h-[400px] w-[400px] rounded-full bg-purple-600/20 blur-[140px]" />
      </div>

      <div className="relative z-10 w-full max-w-md px-6">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-xl">
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

          <div className="text-center">
            <h1 className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-4xl font-bold text-transparent">
              ChatOps AI
            </h1>
            <p className="mt-3 text-sm text-slate-400">
              Plateforme intelligente d&apos;automatisation DevOps
            </p>
          </div>

          <form onSubmit={handleLogin} className="mt-8 space-y-5">
            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Nom d&apos;utilisateur
              </label>
              <input
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="admin"
                required
                autoComplete="username"
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
                onChange={(event) => setPassword(event.target.value)}
                placeholder="••••••••"
                required
                autoComplete="current-password"
                className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-4 py-3 text-white outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30"
              />
            </div>

            {error && (
              <p className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-600 px-4 py-3 font-semibold text-white shadow-lg transition-all hover:scale-[1.02] hover:shadow-cyan-500/25 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>

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
