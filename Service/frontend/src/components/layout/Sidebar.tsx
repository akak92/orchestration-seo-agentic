import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router'
import { useAuthStore } from '@/store/authStore'
import { AGENTS } from '@/lib/agents'

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const initial =
    user?.full_name?.[0]?.toUpperCase() ??
    user?.email?.[0]?.toUpperCase() ??
    '?'

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 px-3 py-2 text-sm rounded transition-colors ${
      isActive
        ? 'bg-ink-light text-paper'
        : 'text-paper/70 hover:bg-ink-light/40 hover:text-paper'
    }`

  return (
    <aside
      className={`${
        collapsed ? 'w-14' : 'w-64'
      } bg-ink text-paper flex flex-col shrink-0 overflow-hidden transition-all duration-200`}
    >

      {/* ── Masthead + toggle ─────────────────────── */}
      <div className="px-3 py-4 border-b border-ink-light select-none flex items-start justify-between gap-2">
        {!collapsed && (
          <h1 className="font-display text-xl font-black tracking-wide leading-snug px-3">
            THE<br />NEWSROOM<br />DESK
            <p className="text-xs text-ink-light mt-1 font-mono tracking-widest font-normal">
              — sala de redacción —
            </p>
          </h1>
        )}
        <button
          onClick={() => setCollapsed((c) => !c)}
          title={collapsed ? 'Expandir menú' : 'Colapsar menú'}
          className="ml-auto shrink-0 w-8 h-8 flex items-center justify-center rounded text-paper/60 hover:bg-ink-light/40 hover:text-paper transition-colors cursor-pointer text-base"
        >
          {collapsed ? '›' : '‹'}
        </button>
      </div>

      {/* ── User chip ─────────────────────────────── */}
      <div className="px-3 py-3 border-b border-ink-light">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-8 h-8 rounded-full bg-red-correction border border-paper/20 flex items-center justify-center text-white font-bold text-sm shrink-0">
            {initial}
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-sm font-medium leading-none truncate">
                {user?.full_name ?? 'Redactor'}
              </p>
              <p className="text-xs text-ink-light mt-0.5 truncate">{user?.email}</p>
            </div>
          )}
        </div>
      </div>

      {/* ── Nav ───────────────────────────────────── */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-hidden">

        <NavLink to="/" end className={linkClass} title="Dashboard">
          <span className="text-base shrink-0">📋</span>
          {!collapsed && <span>Dashboard</span>}
        </NavLink>

        <NavLink to="/chat" className={linkClass} title="Mesa Editorial">
          <span className="text-base shrink-0">💬</span>
          {!collapsed && <span>Mesa Editorial</span>}
        </NavLink>

        {/* Agent legend — visual only */}
        {!collapsed && (
          <div className="px-3 pt-3 pb-1">
            <p className="text-xs font-mono text-ink-light uppercase tracking-widest mb-2">
              Agentes disponibles
            </p>
            {AGENTS.map((agent) => (
              <div key={agent.key} className="flex items-center gap-2 py-1">
                <span
                  className="w-2 h-2 rounded-full shrink-0"
                  style={{ backgroundColor: agent.color }}
                />
                <span className="text-xs text-paper/50">{agent.label}</span>
              </div>
            ))}
          </div>
        )}

        {!collapsed && (
          <p className="px-3 pt-4 pb-1 text-xs font-mono text-ink-light uppercase tracking-widest">
            Archivos
          </p>
        )}

        <NavLink to="/documents" className={linkClass} title="Documentos">
          <span className="text-base shrink-0">📄</span>
          {!collapsed && <span>Documentos</span>}
        </NavLink>

      </nav>

      {/* ── Footer actions ────────────────────────── */}
      <div className="px-3 py-4 border-t border-ink-light space-y-0.5">
        <NavLink to="/profile" className={linkClass} title="Perfil">
          <span className="text-base shrink-0">⚙</span>
          {!collapsed && <span>Perfil</span>}
        </NavLink>

        <button
          onClick={handleLogout}
          title="Cerrar sesión"
          className="w-full flex items-center gap-3 px-3 py-2 text-sm text-paper/70 hover:text-red-correction hover:bg-ink-light/40 rounded transition-colors text-left cursor-pointer"
        >
          <span className="text-base shrink-0">↩</span>
          {!collapsed && <span>Cerrar sesión</span>}
        </button>
      </div>

    </aside>
  )
}
