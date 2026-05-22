import { Outlet } from 'react-router'
import Sidebar from './Sidebar'

export default function RootLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-paper">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
