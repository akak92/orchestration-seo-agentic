import type { ButtonHTMLAttributes } from 'react'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'outline'
  /** Override the primary background color with an agent color */
  accentColor?: string
}

export default function Button({
  variant = 'primary',
  accentColor,
  className = '',
  children,
  ...props
}: Props) {
  const base =
    'px-4 py-2 text-sm font-medium transition-colors cursor-pointer ' +
    'disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-2 ' +
    'focus-visible:outline-offset-2 focus-visible:outline-ink'

  const variants: Record<string, string> = {
    primary: 'bg-red-correction text-white hover:opacity-90 active:opacity-80',
    ghost:   'bg-transparent hover:bg-paper-dark text-ink',
    outline: 'border-2 border-ink text-ink hover:bg-ink hover:text-paper',
  }

  return (
    <button
      className={`${base} ${variants[variant]} ${className}`}
      style={variant === 'primary' && accentColor ? { backgroundColor: accentColor } : undefined}
      {...props}
    >
      {children}
    </button>
  )
}
