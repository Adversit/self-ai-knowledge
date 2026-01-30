import { useState, useEffect } from 'react'
import { api, type Skill } from '../../api/client'
import { Wrench, CheckCircle, AlertCircle } from 'lucide-react'

export function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)
  const [validating, setValidating] = useState<string | null>(null)

  useEffect(() => {
    loadSkills()
  }, [])

  const loadSkills = async () => {
    try {
      const data = await api.listSkills()
      setSkills(data)
    } finally {
      setLoading(false)
    }
  }

  const handleValidate = async (skillId: string) => {
    setValidating(skillId)
    try {
      // API call would go here
      await new Promise(r => setTimeout(r, 500)) // Placeholder
    } finally {
      setValidating(null)
    }
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading skills...</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-900">Skills</h2>
        <button className="btn btn-primary">
          + Create Skill
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="card p-4">
          <div className="text-2xl font-semibold text-gray-900">{skills.length}</div>
          <div className="text-sm text-gray-500">Total Skills</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-semibold text-gray-900">
            {skills.filter(s => s.command).length}
          </div>
          <div className="text-sm text-gray-500">With Commands</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-semibold text-gray-900">
            {skills.filter(s => s.description.length > 50).length}
          </div>
          <div className="text-sm text-gray-500">Documented</div>
        </div>
      </div>

      {/* Skills Grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {skills.map(skill => (
          <div key={skill.skill_id} className="card p-4">
            <div className="flex items-start justify-between mb-2">
              <div>
                <h3 className="font-medium text-gray-900">{skill.name}</h3>
                <code className="text-sm text-gray-500">{skill.skill_id}</code>
              </div>
              <Wrench className="w-5 h-5 text-gray-400" />
            </div>

            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {skill.description}
            </p>

            {skill.command && (
              <div className="mb-3">
                <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {skill.command}
                </code>
              </div>
            )}

            <div className="flex items-center justify-between pt-3 border-t border-gray-100">
              <span className="text-xs text-gray-400">
                Created: {skill.created_at.split('T')[0]}
              </span>
              <button
                onClick={() => handleValidate(skill.skill_id)}
                disabled={validating === skill.skill_id}
                className="btn btn-secondary text-xs py-1 px-3"
              >
                {validating === skill.skill_id ? (
                  'Validating...'
                ) : (
                  <>
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Validate
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      {skills.length === 0 && (
        <div className="text-center py-12">
          <Wrench className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">No skills yet</h3>
          <p className="text-gray-500 mb-4">Create your first skill to automate knowledge extraction</p>
          <button className="btn btn-primary">
            + Create First Skill
          </button>
        </div>
      )}
    </div>
  )
}
