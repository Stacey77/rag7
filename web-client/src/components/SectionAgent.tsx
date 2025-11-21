import './SectionAgent.css'

interface SectionAgentProps {
  title: string
  description: string
  icon: string
  status?: 'active' | 'idle' | 'error'
  onClick?: () => void
}

const SectionAgent = ({ 
  title, 
  description, 
  icon, 
  status = 'idle',
  onClick 
}: SectionAgentProps) => {
  return (
    <div className={`section-agent ${status}`} onClick={onClick}>
      <div className="agent-icon">{icon}</div>
      <div className="agent-content">
        <h3 className="agent-title">{title}</h3>
        <p className="agent-description">{description}</p>
      </div>
      <div className={`agent-status status-${status}`}>
        <span className="status-dot"></span>
        <span className="status-label">{status}</span>
      </div>
    </div>
  )
}

export default SectionAgent
