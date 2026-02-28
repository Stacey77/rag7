import AIBrain from '../components/AIBrain'
import SectionAgent from '../components/SectionAgent'

function Dashboard() {
  return (
    <div>
      <header className="page-header">
        <h1>Dashboard</h1>
        <p style={{ color: 'var(--text-muted)' }}>Welcome to Ragamuffin AI Platform</p>
      </header>

      <div className="grid grid-2">
        <div className="card">
          <h2>System Status</h2>
          <AIBrain status="idle" message="All systems operational" />
        </div>

        <div className="card">
          <h2>Quick Stats</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
            <div>
              <p style={{ color: 'var(--text-muted)' }}>Active Flows</p>
              <p style={{ fontSize: '2rem', color: 'var(--primary)' }}>5</p>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)' }}>API Calls Today</p>
              <p style={{ fontSize: '2rem', color: 'var(--secondary)' }}>128</p>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)' }}>Agents</p>
              <p style={{ fontSize: '2rem', color: 'var(--accent)' }}>3</p>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)' }}>Datasets</p>
              <p style={{ fontSize: '2rem', color: 'var(--success)' }}>12</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Active Agents</h2>
        <div className="grid grid-3">
          <SectionAgent
            title="RAG Agent"
            description="Retrieval-augmented generation for document Q&A"
            status="active"
          />
          <SectionAgent
            title="Code Assistant"
            description="AI-powered code generation and review"
            status="loading"
          />
          <SectionAgent
            title="Data Analyst"
            description="Automated data analysis and insights"
            status="inactive"
            onActivate={() => alert('Activating Data Analyst...')}
          />
        </div>
      </div>

      <div className="card">
        <h2>Recent Activity</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {[
            { action: 'Flow "chat-assistant" executed', time: '2 minutes ago', status: 'success' },
            { action: 'New dataset uploaded', time: '15 minutes ago', status: 'success' },
            { action: 'Agent "code-review" updated', time: '1 hour ago', status: 'success' },
            { action: 'API rate limit warning', time: '3 hours ago', status: 'warning' },
          ].map((activity, index) => (
            <div 
              key={index}
              style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                padding: '0.75rem',
                background: 'var(--surface-light)',
                borderRadius: '8px'
              }}
            >
              <span>{activity.action}</span>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <span className={`status status-${activity.status}`}>{activity.status}</span>
                <span style={{ color: 'var(--text-muted)' }}>{activity.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
