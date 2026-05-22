import { createBrowserRouter, RouterProvider, Navigate } from 'react-router'
import { useAuthStore } from '@/store/authStore'
import RootLayout from '@/components/layout/RootLayout'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import DashboardPage from '@/pages/DashboardPage'
import ChatPage from '@/pages/chat/ChatPage'
import DocumentsPage from '@/pages/documents/DocumentsPage'
import ProfilePage from '@/pages/profile/ProfilePage'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated())
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <RequireAuth>
        <RootLayout />
      </RequireAuth>
    ),
    children: [
      { index: true,       element: <DashboardPage /> },
      { path: 'chat',      element: <ChatPage /> },
      { path: 'documents', element: <DocumentsPage /> },
      { path: 'profile',   element: <ProfilePage /> },
    ],
  },
  { path: '/login',    element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  { path: '*',         element: <Navigate to="/" replace /> },
])

export default function App() {
  return <RouterProvider router={router} />
}
