import { Link, useLocation, Outlet } from 'react-router-dom'
import { LayoutDashboard, BookOpen, Wrench } from 'lucide-react'

const navItems = [
  { path: '/sessions', label: 'Sessions', icon: LayoutDashboard },
  { path: '/knowledge', label: 'Knowledge', icon: BookOpen },
  { path: '/skills', label: 'Skills', icon: Wrench },
]

export function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-100">
          <h1 className="text-lg font-semibold text-gray-900">AI Context Vault</h1>
          <p className="text-sm text-gray-500 mt-1">Multi-model knowledge base</p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname.startsWith(path)
            return (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                  ? 'bg-accent-50 text-accent-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
              >
                <Icon className="w-5 h-5" />
                {label}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-gray-100">
          <div className="text-xs text-gray-400">
            Self-AI-Knowledge v0.1.0
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
