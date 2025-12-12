import Conversation from '../components/Conversation'
import AIBrain from '../components/AIBrain'

function Playground() {
  return (
    <div>
      <header className="page-header">
        <h1>Playground</h1>
        <p style={{ color: 'var(--text-muted)' }}>Test and interact with AI models</p>
      </header>

      <div className="grid grid-2">
        <div className="card">
          <h2>AI Chat</h2>
          <Conversation />
        </div>

        <div>
          <div className="card">
            <h2>AI Status</h2>
            <AIBrain status="idle" message="Ready to assist" />
          </div>

          <div className="card">
            <h2>Model Settings</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Model</label>
                <select>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="claude-3">Claude 3</option>
                  <option value="llama-2">Llama 2</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Temperature</label>
                <input type="range" min="0" max="100" defaultValue="70" />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Max Tokens</label>
                <input type="number" defaultValue="2048" />
              </div>
            </div>
          </div>

          <div className="card">
            <h2>Quick Actions</h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              <button className="btn">Clear Chat</button>
              <button className="btn btn-secondary">Export</button>
              <button className="btn">Save Preset</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Playground
