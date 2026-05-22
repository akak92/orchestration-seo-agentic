// ── Domain types mirroring API schemas ────────────────────────

export interface User {
  id: string
  email: string
  full_name: string | null
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  agentKey?: string
  timestamp: Date
}

export interface ChatApiResponse {
  response: string
  agent_used: string
  thread_id: string
  session_id: string
}

export interface ChatMessageRecord {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  agent_used?: string | null
  created_at: string
}

export interface ChatSession {
  id: string
  thread_id: string
  title: string | null
  created_at: string
  last_message: string | null
}

/** Matches DocumentStatusResponse serialized by the API */
export interface Document {
  document_id: string
  filename: string
  status: 'pending' | 'processing' | 'done' | 'failed'
  extracted_text?: string | null
  error_message?: string | null
  created_at?: string | null
}

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  status: string
}

export type AgentKey = 'editor' | 'seo_optimizer' | 'summarizer'

export interface AgentConfig {
  key: AgentKey
  label: string
  description: string
  color: string
  icon: string
}
