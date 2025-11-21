import AIBrain from '../components/AIBrain'
import SectionAgent from '../components/SectionAgent'

function Dashboard() {
  return (
    <div className="dashboard">
      <h1>Ragamuffin Dashboard</h1>
      <p className="mb-2">Welcome to your AI orchestration platform</p>

      <div className="grid grid-2 mb-2">
        <div className="card">
          <h3>System Status</h3>
          <AIBrain status="active" />
          <div className="mt-2">
            <p>All systems operational</p>
            <div className="flex gap-1 mt-1">
              <span className="badge badge-success">LangFlow: Online</span>
              <span className="badge badge-success">Backend: Online</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>Quick Stats</h3>
          <div className="stats-grid mt-1">
            <div className="stat-box">
              <div className="stat-value">12</div>
              <div className="stat-label">Flows</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">45</div>
              <div className="stat-label">Executions</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">98%</div>
              <div className="stat-label">Success Rate</div>
            </div>
          </div>
        </div>
      </div>

      <h2>Active Agents</h2>
      <div className="grid grid-3">
        <SectionAgent
          name="Data Processor"
          status="online"
          tasksCompleted={23}
          description="Processing and transforming data streams"
        />
        <SectionAgent
          name="Query Handler"
          status="processing"
          tasksCompleted={15}
          description="Managing user queries and responses"
        />
        <SectionAgent
          name="Analytics Engine"
          status="online"
          tasksCompleted={31}
          description="Analyzing patterns and generating insights"
        />
      </div>
    </div>
  )
}

export default Dashboard
