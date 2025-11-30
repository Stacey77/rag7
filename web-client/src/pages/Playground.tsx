import Conversation from '../components/Conversation'

const Playground = () => {
  return (
    <div>
      <h1>AI Playground</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Test and interact with AI agents in real-time
      </p>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h3>Agent Conversation</h3>
          </div>
          <Conversation />
        </div>

        <div>
          <div className="card mb-3">
            <div className="card-header">
              <h3>Configuration</h3>
            </div>
            <div className="form-group">
              <label>Select Agent</label>
              <select>
                <option>Default Conversation Agent</option>
                <option>Data Analysis Agent</option>
                <option>Research Agent</option>
                <option>Code Assistant</option>
              </select>
            </div>
            <div className="form-group">
              <label>Temperature</label>
              <input type="range" min="0" max="100" defaultValue="70" />
            </div>
            <div className="form-group">
              <label>Max Tokens</label>
              <input type="number" defaultValue="1000" />
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>Quick Actions</h3>
            </div>
            <button className="btn btn-primary" style={{ width: '100%', marginBottom: '0.75rem' }}>
              🔄 Reset Conversation
            </button>
            <button className="btn btn-secondary" style={{ width: '100%', marginBottom: '0.75rem' }}>
              💾 Save Session
            </button>
            <button className="btn btn-secondary" style={{ width: '100%' }}>
              📤 Export Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Playground
