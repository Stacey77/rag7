interface SectionAgentProps {
  name: string
  status: 'online' | 'offline' | 'processing'
  tasksCompleted: number
  description?: string
}

function SectionAgent({ name, status, tasksCompleted, description }: SectionAgentProps) {
  const statusClass = status === 'online' ? 'status-active' : 
                     status === 'processing' ? 'status-warning' : 'status-error'

  return (
    <div className="card section-agent">
      <div className="flex-between mb-1">
        <h3>{name}</h3>
        <span className={`status-indicator ${statusClass}`}></span>
      </div>
      
      {description && (
        <p className="mb-1">{description}</p>
      )}
      
      <div className="agent-stats">
        <div className="stat-item">
          <span className="stat-label">Status:</span>
          <span className={`badge badge-${status === 'online' ? 'success' : status === 'processing' ? 'warning' : 'error'}`}>
            {status}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Tasks:</span>
          <span className="badge badge-primary">{tasksCompleted}</span>
        </div>
      </div>
    </div>
  )
}

export default SectionAgent
