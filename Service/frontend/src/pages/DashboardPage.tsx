import { useNavigate } from 'react-router'
import { AGENTS } from '@/lib/agents'
import { useAuthStore } from '@/store/authStore'

export default function DashboardPage() {
  const { user } = useAuthStore()
  const navigate = useNavigate()

  return (
    <div className="p-6 max-w-4xl mx-auto">

      {/* ── Newspaper header ──────────────────────── */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <div className="h-px flex-1 bg-ink" />
          <span className="font-mono text-xs uppercase tracking-widest text-ink/50 px-2">
            Vol. 1 — {new Date().getFullYear()}
          </span>
          <div className="h-px flex-1 bg-ink" />
        </div>

        <h2 className="font-display text-3xl font-black text-ink leading-tight">
          {user?.full_name ? `Bienvenido, ${user.full_name}` : 'Bienvenido a la redacción'}
        </h2>
        <p className="font-display text-ink/60 mt-1 italic text-lg">
          "Tu equipo de redacción con IA, listo para trabajar."
        </p>

        <div className="h-0.5 bg-ink mt-4" />
      </div>

      {/* ── Intro block ───────────────────────────── */}
      <div className="border-2 border-ink bg-white p-5 mb-8 flex gap-5 items-start">
        <div className="text-4xl shrink-0 mt-0.5">🗞️</div>
        <div>
          <h3 className="font-display text-lg font-bold text-ink mb-1">Mesa Editorial</h3>
          <p className="text-sm text-ink/70 leading-relaxed">
            La <strong>Mesa Editorial</strong> es tu punto de acceso a un equipo de tres
            agentes especializados. No necesitas elegir con cuál hablar: simplemente
            describí tu necesidad y el <span className="font-medium">Supervisor</span> derivará
            tu solicitud al agente más adecuado automáticamente.
          </p>
          <button
            onClick={() => navigate('/chat')}
            className="mt-4 inline-flex items-center gap-2 px-5 py-2 bg-ink text-paper text-sm font-medium border-2 border-ink hover:bg-ink/80 transition-colors cursor-pointer"
          >
            Abrir la Mesa Editorial →
          </button>
        </div>
      </div>

      {/* ── Section title ─────────────────────────── */}
      <div className="flex items-center gap-3 mb-4">
        <h3 className="font-display text-lg font-bold text-ink">El equipo detrás de la Mesa</h3>
        <div className="h-px flex-1 bg-ink/20" />
      </div>
      <p className="text-sm text-ink/60 mb-5 leading-relaxed">
        Estos tres agentes trabajan en segundo plano. El Supervisor analiza tu solicitud y
        decide a cuál derivar — verás el nombre del agente que respondió en cada mensaje.
      </p>

      {/* ── Agent info cards (non-clickable) ──────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
        {AGENTS.map((agent) => (
          <div
            key={agent.key}
            className="border-2 border-ink bg-white p-6"
          >
            {/* Icon circle */}
            <div
              className="w-12 h-12 rounded-full border-2 border-ink flex items-center justify-center text-xl mb-4"
              style={{ backgroundColor: agent.color }}
            >
              {agent.icon}
            </div>

            {/* Color bar */}
            <div className="h-1 w-12 mb-4" style={{ backgroundColor: agent.color }} />

            <h3 className="font-display text-xl font-bold text-ink">{agent.label}</h3>
            <p className="text-sm text-ink/60 mt-2 leading-relaxed">{agent.description}</p>

            <div
              className="mt-4 text-xs font-mono uppercase tracking-wider"
              style={{ color: agent.color }}
            >
              Agente especializado
            </div>
          </div>
        ))}
      </div>

      {/* ── Footer strip ──────────────────────────── */}
      <div className="border-t-2 border-ink pt-4">
        <p className="text-xs text-ink/40 font-mono">
          Aplicación realizada por el Área de Innovación de SofreDigital SA. Todos los derechos reservados®
        </p>
      </div>

    </div>
  )
}
