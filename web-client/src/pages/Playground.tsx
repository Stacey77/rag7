import Conversation from '../components/Conversation'

function Playground() {
  return (
    <div className="playground">
      <h1>AI Playground</h1>
      <p className="mb-2">Interact with your AI agents in real-time</p>

      <div className="grid grid-2">
        <div className="card">
          <h3>Conversation</h3>
          <Conversation />
        </div>

        <div className="card">
          <h3>Configuration</h3>
          <div className="config-panel">
            <div className="config-item">
              <label>Model Temperature</label>
              <input type="range" min="0" max="100" defaultValue="70" />
              <span>0.7</span>
            </div>

            <div className="config-item mt-1">
              <label>Max Tokens</label>
              <input type="number" defaultValue="2048" />
            </div>

            <div className="config-item mt-1">
              <label>System Prompt</label>
              <textarea 
                rows={4} 
                defaultValue="You are a helpful AI assistant."
              />
            </div>

            <button className="mt-1" style={{ width: '100%' }}>
              Apply Settings
            </button>
          </div>
        </div>
      </div>

      <div className="card mt-2">
        <h3>Recent Interactions</h3>
        <div className="interactions-list">
          <div className="interaction-item">
            <span className="timestamp">2 minutes ago</span>
            <p>User asked about data processing capabilities</p>
            <span className="badge badge-success">Completed</span>
          </div>
          <div className="interaction-item">
            <span className="timestamp">15 minutes ago</span>
            <p>Flow execution: customer_support_v2</p>
            <span className="badge badge-success">Success</span>
          </div>
          <div className="interaction-item">
            <span className="timestamp">1 hour ago</span>
            <p>System health check completed</p>
            <span className="badge badge-primary">System</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Playground
