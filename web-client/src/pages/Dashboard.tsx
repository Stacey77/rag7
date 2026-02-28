import { useEffect, useState } from 'react'
import AIBrain from '../components/AIBrain'
import SectionAgent from '../components/SectionAgent'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function Dashboard() {
  const [flows, setFlows] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchFlows()
  }, [])

  const fetchFlows = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/list_flows/`)
      const data = await response.json()
      setFlows(data.flows || [])
      setError(null)
    } catch (err) {
      console.error('Failed to fetch flows:', err)
      setError('Failed to connect to backend. Make sure the API is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">
          Overview of your AI agents and flows
        </p>
      </div>

      {error && (
        <div className="card" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', borderColor: 'var(--error-color)' }}>
          <div className="card-content" style={{ color: 'var(--error-color)' }}>
            ⚠️ {error}
          </div>
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Flows</div>
          <div className="stat-value">{loading ? '...' : flows.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active Agents</div>
          <div className="stat-value">0</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">API Calls Today</div>
          <div className="stat-value">0</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Success Rate</div>
          <div className="stat-value">100%</div>
        </div>
      </div>

      <div className="card mb-3">
        <div className="card-header">
          <h2 className="card-title">AI Brain Visualization</h2>
        </div>
        <div className="card-content">
          <AIBrain />
        </div>
      </div>

      <h2 className="mb-2" style={{ fontSize: '1.5rem', fontWeight: 600 }}>Section Agents</h2>
      <div className="grid grid-2">
        <SectionAgent
          title="Research Agent"
          description="Gathers and analyzes information from multiple sources"
          status="active"
          icon="🔍"
        />
        <SectionAgent
          title="Content Agent"
          description="Generates and refines content based on research"
          status="idle"
          icon="✍️"
        />
        <SectionAgent
          title="Analysis Agent"
          description="Performs deep analysis and provides insights"
          status="idle"
          icon="📊"
        />
        <SectionAgent
          title="Summary Agent"
          description="Creates concise summaries of complex information"
          status="idle"
          icon="📝"
        />
      </div>

      {flows.length > 0 && (
        <div className="card mt-3">
          <div className="card-header">
            <h2 className="card-title">Available Flows</h2>
          </div>
          <div className="card-content">
            <ul className="list">
              {flows.map((flow) => (
                <li key={flow} className="list-item">
                  <div>
                    <div className="list-item-title">{flow}</div>
                    <div className="list-item-meta">Ready to execute</div>
                  </div>
                  <button className="btn btn-secondary">View</button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
