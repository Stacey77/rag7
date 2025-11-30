import AIBrain from '../components/AIBrain';
import SectionAgent from '../components/SectionAgent';

function Dashboard() {
  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Monitor your AI agents and system status</p>
      </div>

      <div className="stats-container">
        <div className="stat-card">
          <div className="stat-value">3</div>
          <div className="stat-label">Active Agents</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">127</div>
          <div className="stat-label">Total Flows</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">99.8%</div>
          <div className="stat-label">Uptime</div>
        </div>
      </div>

      <AIBrain />

      <div className="card">
        <h2 className="card-title">System Status</h2>
        <div className="card-content">
          <SectionAgent name="LangFlow Service" status="Running on port 7860" avatar="🌊" />
          <SectionAgent name="Backend API" status="Running on port 8000" avatar="⚙️" />
          <SectionAgent name="Web Client" status="Running on port 8080" avatar="🌐" />
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">Recent Activity</h3>
          <div className="card-content">
            <p>• Flow "customer-support-agent" executed successfully</p>
            <p>• New dataset "knowledge-base-v2" uploaded</p>
            <p>• Agent "data-analyzer" updated</p>
          </div>
        </div>
        <div className="card">
          <h3 className="card-title">Quick Actions</h3>
          <div className="card-content">
            <button className="btn btn-primary" style={{ marginRight: '1rem', marginBottom: '1rem' }}>
              Create New Agent
            </button>
            <button className="btn btn-secondary" style={{ marginBottom: '1rem' }}>
              Upload Dataset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
