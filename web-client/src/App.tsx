import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Playground from './pages/Playground'
import Datasets from './pages/Datasets'
import AgentBuilder from './pages/AgentBuilder'
import RAGQuery from './pages/RAGQuery'
import Documents from './pages/Documents'
import VoiceCalls from './pages/VoiceCalls'

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/playground" element={<Playground />} />
          <Route path="/voice-calls" element={<VoiceCalls />} />
          <Route path="/datasets" element={<Datasets />} />
          <Route path="/agent-builder" element={<AgentBuilder />} />
          <Route path="/rag-query" element={<RAGQuery />} />
          <Route path="/documents" element={<Documents />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
