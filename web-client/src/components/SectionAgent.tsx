import './SectionAgent.css'

interface SectionAgentProps {
  title: string
  description: string
  status?: 'active' | 'idle' | 'processing'
  onClick?: () => void
}

const SectionAgent = ({ title, description, status = 'idle', onClick }: SectionAgentProps) => {
  return (
    <div className={`section-agent ${status}`} onClick={onClick}>
      <div className="agent-header">
        <h3 className="agent-title">{title}</h3>
        <span className={`status-badge status-${status}`}>{status}</span>
      </div>
      <p className="agent-description">{description}</p>
      <div className="agent-indicator">
        <div className="indicator-bar"></div>
      </div>
    </div>
  )
}

export default SectionAgent
