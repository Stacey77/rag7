import AIBrain from '../components/AIBrain'
import SectionAgent from '../components/SectionAgent'
import './Dashboard.css'

const Dashboard = () => {
  return (
    <div className="dashboard slide-in">
      <header className="page-header">
        <h1>Dashboard</h1>
        <p className="text-muted">System Overview & Metrics</p>
      </header>

      <div className="dashboard-hero">
        <AIBrain active={true} size="large" />
        <div className="hero-content">
          <h2 className="glow-text">Ragamuffin AI Platform</h2>
          <p className="hero-subtitle">Visual Agent Building & Execution</p>
        </div>
      </div>

      <div className="dashboard-stats grid grid-3">
        <div className="stat-card card">
          <div className="stat-icon">📊</div>
          <div className="stat-value">0</div>
          <div className="stat-label">Active Agents</div>
        </div>

        <div className="stat-card card">
          <div className="stat-icon">⚡</div>
          <div className="stat-value">0</div>
          <div className="stat-label">Executions Today</div>
        </div>

        <div className="stat-card card">
          <div className="stat-icon">💾</div>
          <div className="stat-value">0</div>
          <div className="stat-label">Saved Flows</div>
        </div>
      </div>

      <section className="dashboard-section">
        <h2>Quick Actions</h2>
        <div className="grid grid-2">
          <SectionAgent
            title="Build Agent"
            description="Create a new agent using the visual flow builder"
            icon="🔧"
            status="idle"
            onClick={() => window.location.href = '/agent-builder'}
          />

          <SectionAgent
            title="Test Playground"
            description="Test and interact with your agents"
            icon="🎮"
            status="idle"
            onClick={() => window.location.href = '/playground'}
          />

          <SectionAgent
            title="Manage Data"
            description="Upload and manage datasets for your agents"
            icon="📁"
            status="idle"
            onClick={() => window.location.href = '/datasets'}
          />

          <SectionAgent
            title="LangFlow UI"
            description="Access the visual flow designer"
            icon="🎨"
            status="active"
            onClick={() => window.open('http://localhost:7860', '_blank')}
          />
        </div>
      </section>

      <section className="dashboard-section">
        <h2>System Status</h2>
        <div className="status-grid">
          <div className="status-item">
            <span className="status-indicator status-online"></span>
            <span className="status-name">Backend API</span>
            <span className="status-value">Online</span>
          </div>

          <div className="status-item">
            <span className="status-indicator status-online"></span>
            <span className="status-name">LangFlow</span>
            <span className="status-value">Running</span>
          </div>

          <div className="status-item">
            <span className="status-indicator status-online"></span>
            <span className="status-name">Frontend</span>
            <span className="status-value">Connected</span>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Dashboard
