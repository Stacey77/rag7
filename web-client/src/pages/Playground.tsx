import Conversation from '../components/Conversation'

const Playground = () => {
  return (
    <div className="page-container fade-in">
      <h1>Playground</h1>
      <p style={{ marginBottom: '2rem' }}>
        Test your AI flows and have real-time conversations with the system.
      </p>
      
      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Conversation Interface</h3>
          </div>
          <Conversation />
        </div>
        
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Settings</h3>
          </div>
          
          <div className="input-group">
            <label className="input-label">Model Selection</label>
            <select className="select">
              <option>GPT-4</option>
              <option>GPT-3.5 Turbo</option>
              <option>Claude 2</option>
              <option>LLaMA 2</option>
            </select>
          </div>
          
          <div className="input-group">
            <label className="input-label">Temperature</label>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.1" 
              defaultValue="0.7"
              className="input"
            />
          </div>
          
          <div className="input-group">
            <label className="input-label">Max Tokens</label>
            <input 
              type="number" 
              className="input" 
              defaultValue="2000"
              min="100"
              max="8000"
            />
          </div>
          
          <div className="input-group">
            <label className="input-label">System Prompt</label>
            <textarea 
              className="textarea"
              placeholder="Enter system prompt..."
              defaultValue="You are a helpful AI assistant."
            />
          </div>
          
          <div className="flex-gap">
            <button className="btn">Save Settings</button>
            <button className="btn btn-secondary">Reset</button>
          </div>
          
          <div style={{ marginTop: '2rem', padding: '1rem', background: 'var(--bg-tertiary)', borderRadius: '4px' }}>
            <h4 style={{ marginBottom: '1rem' }}>Quick Actions</h4>
            <div className="flex-gap" style={{ flexWrap: 'wrap' }}>
              <span className="badge badge-info">STT Enabled</span>
              <span className="badge badge-success">TTS Active</span>
              <span className="badge badge-warning">Auto-save On</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Interactions</h3>
        </div>
        <div className="grid grid-3">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div 
              key={i}
              style={{
                padding: '1rem',
                background: 'var(--bg-tertiary)',
                borderRadius: '4px',
                border: '1px solid var(--border-color)'
              }}
            >
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                {new Date(Date.now() - i * 3600000).toLocaleString()}
              </div>
              <div style={{ fontSize: '0.9rem' }}>
                Interaction #{i}: Query processed successfully
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Playground
