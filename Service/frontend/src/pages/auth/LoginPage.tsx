import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'
import { api } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'

export default function LoginPage() {
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const tokens = await api.auth.login(email, password)
      // Set token in localStorage so the next request can use it
      localStorage.setItem('access_token', tokens.access_token)
      const me = await api.users.me()
      setAuth(tokens.access_token, me)
      navigate('/')
    } catch (err) {
      localStorage.removeItem('access_token')
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-paper flex items-center justify-center p-6">
      <div className="w-full max-w-sm">

        {/* ── Masthead ──────────────────── */}
        <div className="text-center mb-8">
          <h1 className="font-display text-4xl font-black text-ink tracking-tight leading-none">
            THE NEWSROOM<br />DESK
          </h1>
          <div className="flex items-center gap-3 justify-center my-4">
            <div className="h-px flex-1 bg-ink" />
            <span className="font-mono text-xs text-ink/50 tracking-widest uppercase px-2">
              Sala de Redacción
            </span>
            <div className="h-px flex-1 bg-ink" />
          </div>
          <p className="text-sm text-ink/60">Ingresa a tu sala de redacción</p>
        </div>

        {/* ── Form card ─────────────────── */}
        <form
          onSubmit={handleSubmit}
          className="border-2 border-ink bg-white p-6 space-y-4"
        >
          <Input
            label="Email"
            type="email"
            placeholder="redactor@newsroom.com"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            label="Contraseña"
            type="password"
            placeholder="••••••••"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && (
            <p className="text-sm text-red-correction border border-red-correction bg-red-correction/10 px-3 py-2">
              {error}
            </p>
          )}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Ingresando…' : 'INGRESAR'}
          </Button>
        </form>

        <p className="text-center text-sm text-ink/60 mt-5">
          ¿No tienes cuenta?{' '}
          <Link
            to="/register"
            className="text-ink underline underline-offset-2 hover:text-red-correction transition-colors"
          >
            Regístrate
          </Link>
        </p>

      </div>
    </div>
  )
}
