import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { api, type Session } from '../../api/client'
import { format } from 'date-fns'
import { Search, Clock, Tag } from 'lucide-react'

export function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      const data = await api.listSessions(50)
      setSessions(data)
    } finally {
      setLoading(false)
    }
  }

  const filteredSessions = sessions.filter(s =>
    s.session_id.toLowerCase().includes(search.toLowerCase()) ||
    s.model_source.toLowerCase().includes(search.toLowerCase()) ||
    s.tags.some(t => t.toLowerCase().includes(search.toLowerCase()))
  )

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading sessions...</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-900">Sessions</h2>
        <button className="btn btn-primary">
          + New Session
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search sessions..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="input pl-10"
        />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="card p-4">
          <div className="text-2xl font-semibold text-gray-900">{sessions.length}</div>
          <div className="text-sm text-gray-500">Total Sessions</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-semibold text-gray-900">
            {new Set(sessions.map(s => s.model_source)).size}
          </div>
          <div className="text-sm text-gray-500">Agents Used</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-semibold text-gray-900">
            {sessions.filter(s => s.tags.length > 0).length}
          </div>
          <div className="text-sm text-gray-500">Tagged Sessions</div>
        </div>
      </div>

      {/* Session List */}
      <div className="space-y-3">
        {filteredSessions.map(session => (
          <div
            key={session.session_id}
            className="card p-4 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => navigate(`/sessions/${session.session_id}`)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="badge badge-accent capitalize">{session.model_source}</span>
                  {session.project && (
                    <span className="text-sm text-gray-500">@{session.project}</span>
                  )}
                </div>
                <div className="text-sm text-gray-400">
                  {format(new Date(session.created_at), 'yyyy-MM-dd HH:mm')}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {session.tags.map(tag => (
                  <span key={tag} className="badge badge-gray">#{tag}</span>
                ))}
              </div>
            </div>
          </div>
        ))}

        {filteredSessions.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No sessions found
          </div>
        )}
      </div>
    </div>
  )
}
