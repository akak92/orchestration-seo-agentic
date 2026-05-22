import { useEffect, useRef, useState } from 'react'
import { api } from '@/lib/api'
import type { Document } from '@/types'

const STATUS_CONFIG: Record<
  string,
  { label: string; textColor: string; borderColor: string; bgColor: string }
> = {
  pending:    { label: 'Pendiente',   textColor: '#6B7280', borderColor: '#6B7280', bgColor: '#6B728015' },
  processing: { label: 'Procesando',  textColor: '#F2A900', borderColor: '#F2A900', bgColor: '#F2A90015' },
  done:       { label: 'Listo',       textColor: '#4A90E2', borderColor: '#4A90E2', bgColor: '#4A90E215' },
  failed:     { label: 'Error',       textColor: '#E35243', borderColor: '#E35243', bgColor: '#E3524315' },
}

function fileIcon(filename: string): string {
  if (filename.endsWith('.pdf'))                       return '📕'
  if (filename.endsWith('.docx'))                      return '📘'
  if (filename.match(/\.(png|jpg|jpeg)$/i))            return '🖼️'
  if (filename.endsWith('.txt'))                       return '📄'
  return '📎'
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading]     = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError]         = useState('')
  const fileInputRef              = useRef<HTMLInputElement>(null)

  async function loadDocuments() {
    try {
      const docs = await api.documents.list()
      setDocuments(docs)
    } catch {
      setError('No se pudieron cargar los documentos.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void loadDocuments() }, [])

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setError('')
    try {
      await api.documents.upload(file)
      await loadDocuments()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al subir el archivo.')
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <div className="p-6 max-w-4xl">

      {/* ── Header ────────────────────────────────── */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="font-display text-2xl font-bold text-ink">Documentos</h2>
          <p className="text-sm text-ink/60 mt-1">
            Sube archivos para procesarlos y usarlos como contexto con los agentes.
          </p>
          <p className="text-xs font-mono text-ink/40 mt-0.5">
            Formatos: PDF · DOCX · TXT · PNG · JPG (máx. 20 MB)
          </p>
        </div>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
            onChange={handleUpload}
            className="hidden"
            aria-label="Subir documento"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="px-4 py-2 bg-ink text-paper text-sm font-medium border-2 border-ink hover:bg-ink/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {uploading ? 'Subiendo…' : '+ SUBIR DOCUMENTO'}
          </button>
        </div>
      </div>

      {/* ── Error banner ──────────────────────────── */}
      {error && (
        <div className="mb-4 px-4 py-2 border-2 border-red-correction text-red-correction text-sm bg-red-correction/10">
          {error}
        </div>
      )}

      {/* ── Content ───────────────────────────────── */}
      {loading ? (
        <div className="text-center py-16 text-ink/40 font-mono text-sm">
          Cargando documentos…
        </div>
      ) : documents.length === 0 ? (
        <div
          className="border-2 border-dashed border-ink/30 p-16 text-center cursor-pointer hover:border-ink/50 transition-colors"
          onClick={() => fileInputRef.current?.click()}
        >
          <p className="text-5xl mb-4">📄</p>
          <h3 className="font-display text-lg font-bold text-ink">Sin documentos</h3>
          <p className="text-sm text-ink/60 mt-2">
            Haz clic aquí o usa el botón para subir tu primer archivo.
          </p>
        </div>
      ) : (
        <div className="border-2 border-ink divide-y-2 divide-ink bg-white">
          {documents.map((doc) => {
            const status = STATUS_CONFIG[doc.status] ?? STATUS_CONFIG['pending']
            const createdAt = doc.created_at
              ? new Date(doc.created_at).toLocaleDateString('es', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                })
              : '—'

            return (
              <div
                key={doc.document_id}
                className="flex items-center gap-4 px-4 py-3 hover:bg-paper transition-colors"
              >
                <span className="text-2xl shrink-0">{fileIcon(doc.filename)}</span>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-ink truncate">{doc.filename}</p>
                  <p className="text-xs text-ink/50 font-mono mt-0.5">{createdAt}</p>
                </div>

                {doc.status === 'done' && doc.extracted_text && (
                  <span className="text-xs text-ink/40 font-mono shrink-0 hidden sm:inline">
                    {doc.extracted_text.length.toLocaleString()} chars
                  </span>
                )}

                <span
                  className="text-xs font-mono px-2 py-1 border shrink-0"
                  style={{
                    color:           status.textColor,
                    borderColor:     status.borderColor,
                    backgroundColor: status.bgColor,
                  }}
                >
                  {status.label}
                </span>
              </div>
            )
          })}
        </div>
      )}

    </div>
  )
}
