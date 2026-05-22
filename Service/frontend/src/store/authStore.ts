import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

interface AuthState {
  accessToken: string | null
  user: User | null
  setAuth: (token: string, user: User) => void
  logout: () => void
  isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      user: null,

      setAuth: (token, user) => {
        localStorage.setItem('access_token', token)
        set({ accessToken: token, user })
      },

      logout: () => {
        localStorage.removeItem('access_token')
        set({ accessToken: null, user: null })
      },

      isAuthenticated: () => get().accessToken !== null,
    }),
    {
      name: 'newsroom-auth',
      partialize: (state) => ({ accessToken: state.accessToken, user: state.user }),
    },
  ),
)
