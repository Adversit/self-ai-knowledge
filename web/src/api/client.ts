const API_BASE = '/api'

export interface Session {
  session_id: string
  created_at: string
  model_source: string
  model_variant?: string
  project?: string
  tags: string[]
  messages: Message[]
  summaries: SessionSummaries
}

export interface Message {
  role: string
  content: string
  timestamp: string
}

export interface SessionSummaries {
  short?: string
  detailed?: string
  action_items: string[]
  knowledge_candidates: KnowledgeCandidate[]
}

export interface KnowledgeCandidate {
  type: string
  title: string
  content: string
  tags: string[]
  confidence: string
}

export interface KnowledgeItem {
  id: string
  title: string
  date: string
  category: string
  tags: string[]
  source_sessions: string[]
  model_sources: string[]
  confidence: string
  generated_by_skill?: string
  summary?: string
}

export interface Skill {
  skill_id: string
  name: string
  description: string
  command?: string
  created_at: string
}

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

async function postJson<T>(url: string, data: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export const api = {
  // Sessions
  async listSessions(limit = 50, model?: string) {
    const params = new URLSearchParams({ limit: String(limit) })
    if (model) params.append('model', model)
    return fetchJson<Session[]>(`${API_BASE}/sessions?${params}`)
  },

  async getSession(id: string) {
    return fetchJson<Session>(`${API_BASE}/sessions/${id}`)
  },

  // Knowledge
  async listKnowledge(category?: string, limit = 50) {
    const params = new URLSearchParams({ limit: String(limit) })
    if (category) params.append('category', category)
    return fetchJson<KnowledgeItem[]>(`${API_BASE}/knowledge?${params}`)
  },

  async createKnowledge(data: {
    title: string
    content: string
    category: string
    source_sessions: string[]
    model_sources: string[]
    tags?: string[]
  }) {
    return postJson<{ item: KnowledgeItem }>(`${API_BASE}/knowledge`, data)
  },

  // Skills
  async listSkills() {
    return fetchJson<Skill[]>(`${API_BASE}/skills`)
  },

  async getSkill(id: string) {
    return fetchJson<Skill>(`${API_BASE}/skills/${id}`)
  },

  // Search
  async search(query: string, limit = 20, category?: string) {
    const params = new URLSearchParams({ q: query, limit: String(limit) })
    if (category) params.append('category', category)
    return fetchJson<{ results: KnowledgeItem[] }>(`${API_BASE}/search?${params}`)
  },

  // Stats
  async getStats() {
    return fetchJson<{
      knowledge_items: number
      sessions: number
      by_category: Record<string, number>
    }>(`${API_BASE}/stats`)
  },
}
