import { useState, useRef, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'
import { getAgent, AGENTS } from '@/lib/agents'
import { useAuthStore } from '@/store/authStore'
import type { ChatMessage, ChatSession, Document } from '@/types'
import Button from '@/components/ui/Button'

/** Strip internal [agentname] prefix the backend adds */
function stripAgentPrefix(text: string): string {
  return text.replace(/^\[[^\]]+\]\s*/, '')
}

/** Extract the agent key from the [agentname] prefix, or from agent_used field */
function resolveAgentKey(agentUsed?: string | null): string | undefined {
  if (!agentUsed) return undefined
  const clean = agentUsed.replace(/^__/, '').replace(/__$/, '')
  return AGENTS.find((a) => a.key === clean)?.key
}

function AgentBadge({ agentKey }: { agentKey?: string }) {
  const agent = agentKey ? getAgent(agentKey) : undefined
  if (!agent) return null
  return (
    <span
      className="inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 border mb-1"
      style={{ borderColor: agent.color, color: agent.color, backgroundColor: agent.color + '15' }}
    >
      {agent.icon} {agent.label}
    </span>
  )
}

export default function ChatPage() {
  const { user } = useAuthStore()

  // ── Session state ───────────────────────────────────────────────────────────
  const [sessions, setSessions]       = useState<ChatSession[]>([])
  const [activeSession, setActive]    = useState<ChatSession | null>(null)
  const [sessionsLoading, setSessLoading] = useState(true)

  // ── Message state ───────────────────────────────────────────────────────────
  const [messages, setMessages]           = useState<ChatMessage[]>([])
  const [input, setInput]                 = useState('')
  const [loading, setLoading]             = useState(false)

  // ── Attach state ────────────────────────────────────────────────────────────
  const [attachedDoc, setAttachedDoc]     = useState<Document | null>(null)
  const [docsOpen, setDocsOpen]           = useState(false)
  const [docs, setDocs]                   = useState<Document[]>([])
  const [docsLoading, setDocsLoading]     = useState(false)

  // ── Streaming state ──────────────────────────────────────────────────────────
  const [routingAgent, setRoutingAgent]     = useState<string | null>(null)
  const [streamingContent, setStreamingContent] = useState<string>('')

  const bottomRef      = useRef<HTMLDivElement>(null)
  const textareaRef    = useRef<HTMLTextAreaElement>(null)
  const attachPanelRef = useRef<HTMLDivElement>(null)

  // ── Load sessions on mount ──────────────────────────────────────────────────
  useEffect(() => {
    void loadSessions()
  }, [])

  async function loadSessions() {
    setSessLoading(true)
    try {
      const list = await api.chat.sessions.list()
      setSessions(list)
    } finally {
      setSessLoading(false)
    }
  }

  // ── Switch session ──────────────────────────────────────────────────────────
  async function selectSession(session: ChatSession) {
    if (activeSession?.id === session.id) return
    setActive(session)
    setMessages([])
    setInput('')
    setAttachedDoc(null)
    try {
      const records = await api.chat.sessions.messages(session.id)
      setMessages(
        records.map((r) => ({
          id: r.id,
          role: r.role as 'user' | 'assistant',
          content: r.role === 'assistant' ? stripAgentPrefix(r.content) : r.content,
          agentKey: resolveAgentKey(r.agent_used),
          timestamp: new Date(r.created_at),
        })),
      )
    } catch {
      // silent
    }
  }

  // ── New chat ────────────────────────────────────────────────────────────────
  function newChat() {
    setActive(null)
    setMessages([])
    setInput('')
    setAttachedDoc(null)
    textareaRef.current?.focus()
  }

  // ── Delete session ──────────────────────────────────────────────────────────
  async function deleteSession(id: string, e: React.MouseEvent) {
    e.stopPropagation()
    await api.chat.sessions.delete(id)
    setSessions((prev) => prev.filter((s) => s.id !== id))
    if (activeSession?.id === id) newChat()
  }

  // ── Scroll ──────────────────────────────────────────────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // ── Attach panel outside-click ──────────────────────────────────────────────
  const handleOutsideClick = useCallback((e: MouseEvent) => {
    if (attachPanelRef.current && !attachPanelRef.current.contains(e.target as Node)) {
      setDocsOpen(false)
    }
  }, [])

  useEffect(() => {
    if (docsOpen) document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [docsOpen, handleOutsideClick])

  async function openDocPanel() {
    setDocsOpen((prev) => !prev)
    if (docs.length === 0) {
      setDocsLoading(true)
      try {
        const all = await api.documents.list()
        setDocs(all.filter((d) => d.status === 'done' && !!d.extracted_text))
      } finally {
        setDocsLoading(false)
      }
    }
  }

  function attachDoc(doc: Document) {
    setAttachedDoc(doc)
    setDocsOpen(false)
    textareaRef.current?.focus()
  }

  // ── Send message ────────────────────────────────────────────────────────────
  async function sendMessage() {
    if (!input.trim() || loading) return
    const text = input.trim()
    setInput('')
    textareaRef.current?.focus()

    const fullMessage = attachedDoc
      ? `[Documento adjunto: ${attachedDoc.filename}]\n${attachedDoc.extracted_text ?? ''}\n\n${text}`
      : text

    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: 'user',
        content: attachedDoc ? `📎 ${attachedDoc.filename}\n\n${text}` : text,
        timestamp: new Date(),
      },
    ])
    setAttachedDoc(null)
    setLoading(true)
    setRoutingAgent(null)
    setStreamingContent('')

    let accumulated = ''
    let finalAgentKey: string | undefined = undefined
    let resolvedSessionId = activeSession?.id ?? null

    try {
      for await (const event of api.chat.stream(fullMessage, resolvedSessionId)) {
        const t = (event as Record<string, unknown>).type

        if (t === 'session') {
          const sid = event.session_id as string
          const tid = event.thread_id as string
          if (!activeSession) {
            const newSess: ChatSession = {
              id: sid,
              thread_id: tid,
              title: text.slice(0, 60) + (text.length > 60 ? '…' : ''),
              created_at: new Date().toISOString(),
              last_message: null,
            }
            setActive(newSess)
            setSessions((prev) => [newSess, ...prev])
          }
          resolvedSessionId = sid

        } else if (t === 'routing') {
          setRoutingAgent(event.agent as string)

        } else if (t === 'token') {
          accumulated += event.content as string
          setStreamingContent(accumulated)

        } else if (t === 'done') {
          finalAgentKey = resolveAgentKey(event.agent_used as string | null | undefined)
          setRoutingAgent(null)
          setStreamingContent('')
        }
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Error al contactar al supervisor. Intenta de nuevo.',
          timestamp: new Date(),
        },
      ])
      return
    } finally {
      setLoading(false)
      setRoutingAgent(null)
      setStreamingContent('')
    }

    if (accumulated) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: stripAgentPrefix(accumulated),
          agentKey: finalAgentKey,
          timestamp: new Date(),
        },
      ])
      if (resolvedSessionId) {
        setSessions((prev) =>
          prev.map((s) =>
            s.id === resolvedSessionId
              ? { ...s, last_message: accumulated.slice(0, 80) }
              : s,
          ),
        )
      }
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void sendMessage()
    }
  }

  const userInitial =
    user?.full_name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase() ?? '?'

  return (
    <div className="flex h-full overflow-hidden">

      {/* ════════════════════════════════════════════
          LEFT — Session history panel
          ════════════════════════════════════════════ */}
      <aside className="w-56 border-r-2 border-ink bg-paper-dark flex flex-col shrink-0 overflow-hidden">

        {/* Header */}
        <div className="px-3 py-3 border-b-2 border-ink flex items-center justify-between">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-ink">
            Conversaciones
          </span>
          <button
            onClick={newChat}
            title="Nueva conversación"
            className="text-sm px-2 py-0.5 border-2 border-ink text-ink hover:bg-ink hover:text-paper transition-colors cursor-pointer font-mono"
          >
            +
          </button>
        </div>

        {/* Session list */}
        <div className="flex-1 overflow-y-auto">
          {sessionsLoading ? (
            <p className="px-3 py-4 text-xs text-ink/50 font-mono">Cargando…</p>
          ) : sessions.length === 0 ? (
            <p className="px-3 py-6 text-xs text-ink/40 font-mono leading-relaxed">
              Sin conversaciones aún.{'\n'}Escribe algo para comenzar.
            </p>
          ) : (
            sessions.map((s) => (
              <button
                key={s.id}
                onClick={() => void selectSession(s)}
                className={`group w-full text-left px-3 py-2.5 border-b border-ink/10 transition-colors cursor-pointer ${
                  activeSession?.id === s.id
                    ? 'bg-ink text-paper'
                    : 'hover:bg-ink/10 text-ink'
                }`}
              >
                <div className="flex items-start justify-between gap-1">
                  <p className="text-xs font-medium leading-snug line-clamp-2 flex-1">
                    {s.title ?? 'Nueva conversación'}
                  </p>
                  <button
                    onClick={(e) => void deleteSession(s.id, e)}
                    title="Eliminar"
                    className={`shrink-0 text-[10px] opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer ${
                      activeSession?.id === s.id
                        ? 'text-paper/60 hover:text-red-correction'
                        : 'text-ink/40 hover:text-red-correction'
                    }`}
                  >
                    ✕
                  </button>
                </div>
                {s.last_message && (
                  <p
                    className={`text-[10px] mt-0.5 font-mono truncate ${
                      activeSession?.id === s.id ? 'text-paper/60' : 'text-ink/40'
                    }`}
                  >
                    {s.last_message}
                  </p>
                )}
              </button>
            ))
          )}
        </div>

      </aside>

      {/* ════════════════════════════════════════════
          RIGHT — Chat area
          ════════════════════════════════════════════ */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Header bar */}
        <div className="flex items-center gap-4 px-5 py-3 border-b-2 border-ink bg-white shrink-0">
          <div className="w-8 h-8 rounded-full bg-paper-dark border-2 border-ink flex items-center justify-center text-ink text-sm shrink-0">
            ✒️
          </div>
          <div>
            <h2 className="font-display text-base font-bold text-ink leading-none">
              Mesa Editorial
            </h2>
            <p className="text-xs text-ink/50 mt-0.5">
              {activeSession
                ? activeSession.title ?? 'Conversación activa'
                : 'Nueva conversación — escribe para comenzar'}
            </p>
          </div>
          {/* Agent legend */}
          <div className="ml-auto hidden lg:flex items-center gap-3">
            {AGENTS.map((a) => (
              <span key={a.key} className="flex items-center gap-1 text-[10px] font-mono text-ink/50">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: a.color }} />
                {a.label}
              </span>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-auto px-5 py-5 space-y-5">

          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center py-16">
              <p className="text-4xl mb-4">🗞️</p>
              <h3 className="font-display text-xl font-bold text-ink mb-2">
                ¿Qué necesitas hoy?
              </h3>
              <p className="text-sm text-ink/50 max-w-xs leading-relaxed mb-6">
                El supervisor derivará tu solicitud al agente correcto — corrector, SEO u optimizador.
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {[
                  'Corrige la ortografía de este texto:',
                  'Optimiza este artículo para SEO:',
                  'Resume en bullet points:',
                ].map((hint) => (
                  <button
                    key={hint}
                    onClick={() => setInput(hint + ' ')}
                    className="text-xs px-3 py-1.5 border-2 border-ink/30 text-ink/60 hover:border-ink hover:text-ink transition-colors cursor-pointer font-mono"
                  >
                    {hint}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => {
            const agent = msg.agentKey ? getAgent(msg.agentKey) : undefined
            return (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div
                    className="w-8 h-8 rounded-full border-2 border-ink flex items-center justify-center text-sm shrink-0 mt-5"
                    style={agent ? { backgroundColor: agent.color } : { backgroundColor: '#2B3A4220' }}
                  >
                    {agent ? agent.icon : '✒️'}
                  </div>
                )}

                <div className={`max-w-[72%] flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {msg.role === 'assistant' && <AgentBadge agentKey={msg.agentKey} />}
                  <div
                    className={`px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap border-2 border-ink ${
                      msg.role === 'user' ? 'bg-white' : 'bg-white'
                    }`}
                    style={
                      msg.role === 'assistant' && agent
                        ? { borderLeftColor: agent.color, borderLeftWidth: 4 }
                        : undefined
                    }
                  >
                    {msg.content}
                  </div>
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-ink border-2 border-ink flex items-center justify-center text-paper text-xs font-bold shrink-0 mt-5">
                    {userInitial}
                  </div>
                )}
              </div>
            )
          })}

          {loading && (
            <div className="flex gap-3 justify-start">
              <div
                className="w-8 h-8 rounded-full border-2 border-ink flex items-center justify-center text-sm shrink-0 mt-5"
                style={
                  routingAgent
                    ? { backgroundColor: getAgent(routingAgent)?.color ?? '#2B3A4220' }
                    : { backgroundColor: '#2B3A4220' }
                }
              >
                {routingAgent ? (getAgent(routingAgent)?.icon ?? '✒️') : '✒️'}
              </div>

              <div className="max-w-[72%] flex flex-col items-start">
                {routingAgent && (
                  <span
                    className="inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 border mb-1"
                    style={{
                      borderColor: getAgent(routingAgent)?.color,
                      color: getAgent(routingAgent)?.color,
                      backgroundColor: (getAgent(routingAgent)?.color ?? '#000') + '15',
                    }}
                  >
                    {getAgent(routingAgent)?.icon} {getAgent(routingAgent)?.label}
                  </span>
                )}

                <div
                  className="bg-white border-2 border-ink px-4 py-3 text-sm mt-5"
                  style={
                    routingAgent
                      ? { borderLeftColor: getAgent(routingAgent)?.color, borderLeftWidth: 4 }
                      : undefined
                  }
                >
                  {streamingContent ? (
                    <span className="whitespace-pre-wrap">{streamingContent}</span>
                  ) : routingAgent ? (
                    <span className="text-ink/60 font-mono italic text-xs">
                      Derivando al {getAgent(routingAgent)?.label}…
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1">
                      <span className="text-xs text-ink/60 font-mono italic mr-1">Analizando</span>
                      <span className="w-1.5 h-1.5 bg-ink/40 rounded-full animate-bounce [animation-delay:0ms]" />
                      <span className="w-1.5 h-1.5 bg-ink/40 rounded-full animate-bounce [animation-delay:150ms]" />
                      <span className="w-1.5 h-1.5 bg-ink/40 rounded-full animate-bounce [animation-delay:300ms]" />
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div className="px-5 py-4 border-t-2 border-ink bg-white shrink-0">

          {attachedDoc && (
            <div className="flex items-center gap-2 mb-2">
              <span className="flex items-center gap-1.5 text-xs font-mono px-2 py-1 border-2 border-l-4 border-ink bg-paper"
                style={{ borderLeftColor: '#4A90E2' }}>
                <span>📎</span>
                <span className="max-w-[240px] truncate">{attachedDoc.filename}</span>
              </span>
              <button onClick={() => setAttachedDoc(null)}
                className="text-xs text-ink/40 hover:text-red-correction transition-colors cursor-pointer">
                ✕
              </button>
            </div>
          )}

          <div className="flex gap-2 items-end">

            {/* Attach */}
            <div className="relative shrink-0" ref={attachPanelRef}>
              <button
                onClick={() => void openDocPanel()}
                title="Adjuntar documento"
                className={`h-[76px] w-10 flex items-center justify-center border-2 transition-colors cursor-pointer ${
                  attachedDoc ? 'border-ink bg-ink text-paper' : 'border-ink text-ink hover:bg-paper-dark'
                }`}
              >
                <span className="text-lg">📎</span>
              </button>

              {docsOpen && (
                <div className="absolute bottom-full left-0 mb-2 w-72 border-2 border-ink bg-white shadow-lg z-50">
                  <div className="px-3 py-2 border-b border-ink/20 flex items-center justify-between">
                    <span className="text-xs font-mono font-bold uppercase tracking-wider text-ink">
                      Documentos listos
                    </span>
                    <button onClick={() => setDocsOpen(false)}
                      className="text-xs text-ink/40 hover:text-ink cursor-pointer">✕</button>
                  </div>
                  {docsLoading ? (
                    <p className="px-3 py-4 text-xs text-ink/50 font-mono">Cargando…</p>
                  ) : docs.length === 0 ? (
                    <p className="px-3 py-4 text-xs text-ink/50 font-mono">
                      Sin documentos procesados. Sube uno en la sección Documentos.
                    </p>
                  ) : (
                    <ul className="max-h-48 overflow-y-auto divide-y divide-ink/10">
                      {docs.map((doc) => (
                        <li key={doc.document_id}>
                          <button onClick={() => attachDoc(doc)}
                            className="w-full text-left px-3 py-2.5 text-sm hover:bg-paper transition-colors cursor-pointer">
                            <span className="font-medium text-ink truncate block">{doc.filename}</span>
                            <span className="text-xs text-ink/40 font-mono">
                              {doc.extracted_text?.length.toLocaleString()} chars
                            </span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>

            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu solicitud… el supervisor derivará al agente correcto (Enter envía)"
              rows={3}
              className="flex-1 px-3 py-2 border-2 border-ink bg-paper text-ink placeholder:text-ink/40 focus:outline-none focus:border-red-correction resize-none text-sm transition-colors font-body"
            />
            <Button
              onClick={() => void sendMessage()}
              disabled={loading || !input.trim()}
              className="h-[76px] px-6 shrink-0"
            >
              {loading ? '…' : 'ENVIAR'}
            </Button>
          </div>
        </div>

      </div>
    </div>
  )
}
