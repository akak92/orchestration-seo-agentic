import { useEffect, useState, type FormEvent } from 'react'
import { api } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'

export default function ProfilePage() {
  const { user, setAuth, accessToken } = useAuthStore()

  const [fullName, setFullName] = useState(user?.full_name ?? '')
  const [saving, setSaving]     = useState(false)
  const [success, setSuccess]   = useState(false)
  const [error, setError]       = useState('')

  useEffect(() => {
    setFullName(user?.full_name ?? '')
  }, [user])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess(false)
    try {
      const updated = await api.users.update({ full_name: fullName })
      if (accessToken) setAuth(accessToken, updated)
      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar.')
    } finally {
      setSaving(false)
    }
  }

  const initial =
    user?.full_name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase() ?? '?'

  return (
    <div className="p-6 max-w-lg">

      <h2 className="font-display text-2xl font-bold text-ink mb-6">Mi Perfil</h2>

      <div className="border-2 border-ink bg-white p-6">

        {/* ── User card ─────────────────────────────── */}
        <div className="flex items-center gap-4 pb-6 mb-6 border-b-2 border-ink">
          <div className="w-14 h-14 rounded-full bg-red-correction border-2 border-ink flex items-center justify-center text-white font-bold text-xl shrink-0">
            {initial}
          </div>
          <div>
            <p className="font-display font-bold text-lg text-ink leading-tight">
              {user?.full_name ?? 'Sin nombre'}
            </p>
            <p className="text-sm text-ink/60 font-mono mt-0.5">{user?.email}</p>
            {user?.created_at && (
              <p className="text-xs text-ink/40 font-mono mt-0.5">
                Miembro desde{' '}
                {new Date(user.created_at).toLocaleDateString('es', {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric',
                })}
              </p>
            )}
          </div>
        </div>

        {/* ── Edit form ─────────────────────────────── */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email"
            type="email"
            value={user?.email ?? ''}
            disabled
            className="opacity-50 cursor-not-allowed"
          />
          <Input
            label="Nombre completo"
            type="text"
            placeholder="Tu nombre completo"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />

          {error && (
            <p className="text-sm text-red-correction border border-red-correction bg-red-correction/10 px-3 py-2">
              {error}
            </p>
          )}
          {success && (
            <p className="text-sm text-cyan-worn border border-cyan-worn bg-cyan-worn/10 px-3 py-2">
              ✓ Perfil actualizado correctamente.
            </p>
          )}

          <Button type="submit" disabled={saving} className="w-full">
            {saving ? 'Guardando…' : 'GUARDAR CAMBIOS'}
          </Button>
        </form>

      </div>
    </div>
  )
}
