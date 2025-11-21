import Conversation from '../components/Conversation'
import AIBrain from '../components/AIBrain'
import './Playground.css'

const Playground = () => {
  return (
    <div className="playground slide-in">
      <header className="page-header">
        <h1>Playground</h1>
        <p className="text-muted">Test & Interact with Your Agents</p>
      </header>

      <div className="playground-grid">
        <section className="playground-main">
          <div className="card">
            <h3 className="mb-2">Agent Conversation</h3>
            <p className="text-muted mb-3">
              Interact with your AI agents using text or voice input.
              Supports STT (Speech-to-Text) and TTS (Text-to-Speech).
            </p>
            <Conversation />
          </div>
        </section>

        <aside className="playground-sidebar">
          <div className="card">
            <h3 className="mb-2">Agent Status</h3>
            <div className="agent-status-display">
              <AIBrain active={false} size="medium" />
              <p className="text-center text-muted mt-2">No Agent Selected</p>
            </div>
          </div>

          <div className="card">
            <h3 className="mb-2">Quick Settings</h3>
            <div className="settings-list">
              <div className="setting-item">
                <label>Model Temperature</label>
                <input type="range" min="0" max="100" defaultValue="70" />
              </div>

              <div className="setting-item">
                <label>Max Tokens</label>
                <input type="number" defaultValue="2048" />
              </div>

              <div className="setting-item">
                <label>Enable Streaming</label>
                <input type="checkbox" defaultChecked />
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="mb-2">Available Agents</h3>
            <div className="agents-list">
              <div className="agent-item">
                <span className="status-indicator status-offline"></span>
                <span>No agents available</span>
              </div>
              <p className="text-muted mt-2 text-center">
                Create agents in the Agent Builder
              </p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}

export default Playground
