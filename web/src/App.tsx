import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { SessionsPage } from './pages/SessionsPage'
import { KnowledgePage } from './pages/KnowledgePage'
import { SkillsPage } from './pages/SkillsPage'

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<SessionsPage />} />
          <Route path="sessions" element={<SessionsPage />} />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="skills" element={<SkillsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
