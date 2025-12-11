import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Playground from './pages/Playground'
import Datasets from './pages/Datasets'
import AgentBuilder from './pages/AgentBuilder'

function App() {
  return (
    <Router>
      <div className="app">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/playground" element={<Playground />} />
            <Route path="/datasets" element={<Datasets />} />
            <Route path="/agent-builder" element={<AgentBuilder />} />
          </Routes>
        </div>
      </div>
    </Router>
  )
}

export default App
