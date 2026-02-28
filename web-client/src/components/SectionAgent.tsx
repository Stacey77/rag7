interface SectionAgentProps {
  title: string
  description: string
  status?: 'active' | 'idle' | 'error'
  icon?: string
}

function SectionAgent({ title, description, status = 'idle', icon = '🤖' }: SectionAgentProps) {
  const statusColors = {
    active: 'var(--success-color)',
    idle: 'var(--text-muted)',
    error: 'var(--error-color)',
  }

  return (
    <div className="card">
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>{icon}</span>
          <div>
            <h3 className="card-title">{title}</h3>
            <div style={{ fontSize: '0.75rem', color: statusColors[status], marginTop: '0.25rem' }}>
              {status.toUpperCase()}
            </div>
          </div>
        </div>
      </div>
      <div className="card-content">
        <p>{description}</p>
      </div>
    </div>
  )
}

export default SectionAgent
