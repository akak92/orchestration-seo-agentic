import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'
import { api } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'

export default function RegisterPage() {
  const [fullName, setFullName] = useState('')
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
      await api.auth.register(email, password, fullName)
      // Auto-login after registration
      const tokens = await api.auth.login(email, password)
      localStorage.setItem('access_token', tokens.access_token)
      const me = await api.users.me()
      setAuth(tokens.access_token, me)
      navigate('/')
    } catch (err) {
      localStorage.removeItem('access_token')
      setError(err instanceof Error ? err.message : 'Error al registrarse.')
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
              Nueva cuenta
            </span>
            <div className="h-px flex-1 bg-ink" />
          </div>
          <p className="text-sm text-ink/60">Crea tu cuenta de redactor</p>
        </div>

        {/* ── Form card ─────────────────── */}
        <form
          onSubmit={handleSubmit}
          className="border-2 border-ink bg-white p-6 space-y-4"
        >
          <Input
            label="Nombre completo"
            type="text"
            placeholder="María García"
            autoComplete="name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
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
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />

          {error && (
            <p className="text-sm text-red-correction border border-red-correction bg-red-correction/10 px-3 py-2">
              {error}
            </p>
          )}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Creando cuenta…' : 'CREAR CUENTA'}
          </Button>
        </form>

        <p className="text-center text-sm text-ink/60 mt-5">
          ¿Ya tienes cuenta?{' '}
          <Link
            to="/login"
            className="text-ink underline underline-offset-2 hover:text-red-correction transition-colors"
          >
            Inicia sesión
          </Link>
        </p>

      </div>
    </div>
  )
}
