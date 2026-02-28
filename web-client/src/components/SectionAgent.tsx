import { useState } from 'react'
import AIBrain from './AIBrain'
import './SectionAgent.css'

interface SectionAgentProps {
  title: string
  description: string
  icon?: string
  active?: boolean
  onActivate?: () => void
}

function SectionAgent({ title, description, icon = '🤖', active = false, onActivate }: SectionAgentProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      className={`section-agent ${active ? 'active' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onActivate}
    >
      <div className="agent-visual">
        <AIBrain active={active || isHovered} size={120} />
      </div>
      <div className="agent-info">
        <div className="agent-icon">{icon}</div>
        <h3 className="agent-title">{title}</h3>
        <p className="agent-description">{description}</p>
        {active && (
          <div className="agent-status">
            <span className="badge badge-success">Active</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default SectionAgent
