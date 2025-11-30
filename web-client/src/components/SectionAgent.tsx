interface SectionAgentProps {
  title: string
  description: string
  status?: 'active' | 'inactive' | 'loading'
  onActivate?: () => void
}

function SectionAgent({ title, description, status = 'inactive', onActivate }: SectionAgentProps) {
  return (
    <div className="section-agent">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3>{title}</h3>
        <span className={`status status-${status === 'active' ? 'success' : status === 'loading' ? 'warning' : 'error'}`}>
          {status}
        </span>
      </div>
      <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>{description}</p>
      {status === 'inactive' && onActivate && (
        <button className="btn" style={{ marginTop: '1rem' }} onClick={onActivate}>
          Activate
        </button>
      )}
    </div>
  )
}

export default SectionAgent
