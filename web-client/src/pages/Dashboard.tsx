import SectionAgent from '../components/SectionAgent'

const Dashboard = () => {
  return (
    <div>
      <h1>Epic Platform Dashboard</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Welcome to the AI-powered agent management platform
      </p>

      <div className="grid grid-3">
        <div className="card">
          <div className="card-header">
            <h3>System Status</h3>
          </div>
          <div className="flex-between mb-2">
            <span>Backend API</span>
            <span className="status-badge status-online">Online</span>
          </div>
          <div className="flex-between mb-2">
            <span>LangFlow</span>
            <span className="status-badge status-online">Online</span>
          </div>
          <div className="flex-between">
            <span>Agent Builder</span>
            <span className="status-badge status-online">Ready</span>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Quick Stats</h3>
          </div>
          <div className="mb-2">
            <span style={{ color: 'var(--text-secondary)' }}>Total Flows</span>
            <h2 style={{ margin: '0.5rem 0' }}>0</h2>
          </div>
          <div className="mb-2">
            <span style={{ color: 'var(--text-secondary)' }}>Active Agents</span>
            <h2 style={{ margin: '0.5rem 0' }}>0</h2>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Recent Activity</h3>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>
            No recent activity
          </p>
        </div>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h2>Available Agents</h2>
        <div className="grid grid-2">
          <SectionAgent
            title="Data Analysis Agent"
            description="Analyze datasets and generate insights"
            status="idle"
          />
          <SectionAgent
            title="Conversation Agent"
            description="Natural language interactions"
            status="idle"
          />
          <SectionAgent
            title="Research Agent"
            description="Search and summarize information"
            status="idle"
          />
          <SectionAgent
            title="Code Assistant"
            description="Help with programming tasks"
            status="idle"
          />
        </div>
      </div>
    </div>
  )
}

export default Dashboard
