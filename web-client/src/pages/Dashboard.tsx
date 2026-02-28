import AIBrain from '../components/AIBrain'
import SectionAgent from '../components/SectionAgent'

const Dashboard = () => {
  return (
    <div className="page-container fade-in">
      <h1>Dashboard</h1>
      
      <div className="grid grid-3">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Total Requests</h3>
          </div>
          <div className="flex-center" style={{ padding: '2rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', fontWeight: 900, color: 'var(--accent-primary)' }}>
                2,547
              </div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                +12% from last week
              </div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Active Flows</h3>
          </div>
          <div className="flex-center" style={{ padding: '2rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', fontWeight: 900, color: 'var(--accent-secondary)' }}>
                8
              </div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                3 running now
              </div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Success Rate</h3>
          </div>
          <div className="flex-center" style={{ padding: '2rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', fontWeight: 900, color: 'var(--success)' }}>
                99.5%
              </div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                Excellent performance
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">AI Core Status</h2>
        </div>
        <AIBrain />
      </div>
      
      <div className="grid grid-2">
        <SectionAgent
          title="Query Agent"
          status="active"
          description="Handles natural language queries and information retrieval"
        />
        
        <SectionAgent
          title="Analysis Agent"
          status="processing"
          description="Performs deep analysis on datasets and generates insights"
        />
        
        <SectionAgent
          title="Generation Agent"
          status="idle"
          description="Creates content and responses based on trained models"
        />
        
        <SectionAgent
          title="Validation Agent"
          status="active"
          description="Validates outputs and ensures quality standards"
        />
      </div>
    </div>
  )
}

export default Dashboard
