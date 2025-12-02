import Conversation from '../components/Conversation'

function Playground() {
  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Playground</h1>
        <p className="page-description">
          Test and interact with your AI agents in real-time
        </p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Agent Conversation</h2>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn btn-secondary">🔄 Reset</button>
            <button className="btn btn-secondary">⚙️ Settings</button>
          </div>
        </div>
        <div className="card-content">
          <Conversation />
        </div>
      </div>

      <div className="grid grid-2 mt-3">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Flow Configuration</h3>
          </div>
          <div className="card-content">
            <div className="form-group">
              <label className="form-label">Select Flow</label>
              <select className="form-input">
                <option>Default Agent</option>
                <option>Research Agent</option>
                <option>Content Agent</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Temperature</label>
              <input type="range" min="0" max="1" step="0.1" defaultValue="0.7" className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Max Tokens</label>
              <input type="number" defaultValue="2000" className="form-input" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Execution Stats</h3>
          </div>
          <div className="card-content">
            <div style={{ marginBottom: '1rem' }}>
              <div className="stat-label">Response Time</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>0ms</div>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <div className="stat-label">Tokens Used</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>0</div>
            </div>
            <div>
              <div className="stat-label">Success Rate</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>100%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Playground
