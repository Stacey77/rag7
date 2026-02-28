import { useState } from 'react'
import SectionAgent from '../components/SectionAgent'
import AIBrain from '../components/AIBrain'

function Dashboard() {
  const [activeAgent, setActiveAgent] = useState<string | null>(null)

  const agents = [
    {
      id: 'research',
      title: 'Research Agent',
      description: 'Autonomously researches topics and gathers information',
      icon: '🔍',
    },
    {
      id: 'writer',
      title: 'Writer Agent',
      description: 'Generates high-quality content and documentation',
      icon: '✍️',
    },
    {
      id: 'coder',
      title: 'Coder Agent',
      description: 'Writes and reviews code across multiple languages',
      icon: '💻',
    },
    {
      id: 'analyst',
      title: 'Analyst Agent',
      description: 'Analyzes data and generates insights',
      icon: '📊',
    },
  ]

  return (
    <div className="dashboard fade-in">
      <div className="page-header">
        <h1 className="glow">DASHBOARD</h1>
        <p className="text-secondary">Monitor your AI agents and system status</p>
      </div>

      <div className="grid grid-2 mb-4">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">System Status</h3>
          </div>
          <div className="flex items-center justify-center" style={{ minHeight: '200px' }}>
            <AIBrain active={true} size={180} />
          </div>
          <div className="text-center mt-2">
            <p className="text-secondary">All systems operational</p>
            <span className="badge badge-success mt-1">Online</span>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Quick Stats</h3>
          </div>
          <div className="grid grid-2 gap-2" style={{ padding: 'var(--spacing-md) 0' }}>
            <div className="stat-item">
              <div className="stat-value">4</div>
              <div className="stat-label">Active Agents</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">127</div>
              <div className="stat-label">Tasks Completed</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">98%</div>
              <div className="stat-label">Success Rate</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">24/7</div>
              <div className="stat-label">Uptime</div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Your Agents</h3>
        </div>
        <div className="grid grid-4">
          {agents.map(agent => (
            <SectionAgent
              key={agent.id}
              title={agent.title}
              description={agent.description}
              icon={agent.icon}
              active={activeAgent === agent.id}
              onActivate={() => setActiveAgent(agent.id === activeAgent ? null : agent.id)}
            />
          ))}
        </div>
      </div>

      <style>{`
        .stat-item {
          text-align: center;
          padding: var(--spacing-md);
        }

        .stat-value {
          font-size: 2rem;
          font-weight: 900;
          color: var(--primary-color);
          margin-bottom: var(--spacing-xs);
          text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }

        .stat-label {
          font-size: 0.85rem;
          color: var(--text-secondary);
          text-transform: uppercase;
          letter-spacing: 1px;
        }
      `}</style>
    </div>
  )
}

export default Dashboard
