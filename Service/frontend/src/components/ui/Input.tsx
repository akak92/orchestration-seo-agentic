import type { InputHTMLAttributes } from 'react'

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export default function Input({ label, error, className = '', id, ...props }: Props) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-')

  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label
          htmlFor={inputId}
          className="text-xs font-medium text-ink uppercase tracking-wider font-mono"
        >
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={
          'w-full px-3 py-2 border-2 border-ink bg-white text-ink ' +
          'placeholder:text-ink/40 focus:outline-none focus:border-red-correction ' +
          'transition-colors rounded-none disabled:opacity-50 disabled:cursor-not-allowed ' +
          className
        }
        {...props}
      />
      {error && <p className="text-xs text-red-correction">{error}</p>}
    </div>
  )
}
