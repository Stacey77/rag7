import { useState } from 'react'
import './SectionAgent.css'

interface SectionAgentProps {
  title: string
  status: 'active' | 'idle' | 'processing'
  description: string
}

const SectionAgent = ({ title, status, description }: SectionAgentProps) => {
  const [expanded, setExpanded] = useState(false)
  
  const statusColors = {
    active: 'var(--success)',
    idle: 'var(--text-secondary)',
    processing: 'var(--warning)'
  }
  
  return (
    <div className="section-agent card">
      <div className="agent-header" onClick={() => setExpanded(!expanded)}>
        <div className="agent-info">
          <div className="agent-status" style={{ background: statusColors[status] }}></div>
          <h3 className="agent-title">{title}</h3>
        </div>
        <div className="agent-toggle">{expanded ? '▼' : '▶'}</div>
      </div>
      
      {expanded && (
        <div className="agent-content fade-in">
          <p className="agent-description">{description}</p>
          <div className="agent-metrics">
            <div className="metric">
              <span className="metric-label">Requests</span>
              <span className="metric-value">128</span>
            </div>
            <div className="metric">
              <span className="metric-label">Avg. Time</span>
              <span className="metric-value">1.2s</span>
            </div>
            <div className="metric">
              <span className="metric-label">Success Rate</span>
              <span className="metric-value">99.5%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SectionAgent
