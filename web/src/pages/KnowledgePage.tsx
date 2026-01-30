import { useState, useEffect } from 'react'
import { api, type KnowledgeItem } from '../../api/client'
import { format } from 'date-fns'
import { Search, BookOpen, Lightbulb, Cpu, Sparkles } from 'lucide-react'

const categoryIcons: Record<string, React.ElementType> = {
  trusted_sources: BookOpen,
  thinking: Lightbulb,
  tech_notes: Cpu,
  skills_derived: Sparkles,
}

const categoryColors: Record<string, string> = {
  trusted_sources: 'badge-accent',
  thinking: 'badge-yellow',
  tech_notes: 'badge-blue',
  skills_derived: 'badge-purple',
}

export function KnowledgePage() {
  const [items, setItems] = useState<KnowledgeItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null)

  useEffect(() => {
    loadKnowledge()
  }, [categoryFilter])

  const loadKnowledge = async () => {
    try {
      const data = await api.listKnowledge(categoryFilter || undefined, 50)
      setItems(data)
    } finally {
      setLoading(false)
    }
  }

  const filteredItems = items.filter(item =>
    item.title.toLowerCase().includes(search.toLowerCase()) ||
    item.summary?.toLowerCase().includes(search.toLowerCase()) ||
    item.tags.some(t => t.toLowerCase().includes(search.toLowerCase()))
  )

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading knowledge...</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-900">Knowledge</h2>
        <button className="btn btn-primary">
          + Add Entry
        </button>
      </div>

      {/* Search & Filter */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search knowledge..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
        <select
          value={categoryFilter || ''}
          onChange={e => setCategoryFilter(e.target.value || null)}
          className="input w-48"
        >
          <option value="">All Categories</option>
          <option value="tech_notes">Tech Notes</option>
          <option value="thinking">Thinking</option>
          <option value="trusted_sources">Trusted Sources</option>
          <option value="skills_derived">Skills</option>
        </select>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {['tech_notes', 'thinking', 'trusted_sources', 'skills_derived'].map(cat => {
          const count = items.filter(i => i.category === cat).length
          const Icon = categoryIcons[cat]
          return (
            <div key={cat} className="card p-4">
              <div className="flex items-center gap-2 mb-1">
                <Icon className="w-4 h-4 text-gray-400" />
                <span className="text-xs text-gray-500 capitalize">{cat.replace('_', ' ')}</span>
              </div>
              <div className="text-2xl font-semibold text-gray-900">{count}</div>
            </div>
          )
        })}
      </div>

      {/* Knowledge List */}
      <div className="grid gap-4">
        {filteredItems.map(item => {
          const Icon = categoryIcons[item.category] || BookOpen
          return (
            <div key={item.id} className="card p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <div className={`p-2 rounded-lg bg-gray-100`}>
                  <Icon className="w-5 h-5 text-gray-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="badge badge-gray capitalize">
                      {item.category.replace('_', ' ')}
                    </span>
                    <span className="text-sm text-gray-400">
                      {format(new Date(item.date), 'yyyy-MM-dd')}
                    </span>
                    {item.confidence === 'high' && (
                      <span className="badge badge-accent">High Confidence</span>
                    )}
                  </div>
                  <h3 className="font-medium text-gray-900 mb-1">{item.title}</h3>
                  {item.summary && (
                    <p className="text-sm text-gray-500 line-clamp-2">{item.summary}</p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    {item.tags.map(tag => (
                      <span key={tag} className="text-xs text-gray-400">#{tag}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )
        })}

        {filteredItems.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No knowledge items found
          </div>
        )}
      </div>
    </div>
  )
}
