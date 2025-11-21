import Conversation from '../components/Conversation'
import AIBrain from '../components/AIBrain'

function Playground() {
  return (
    <div className="playground fade-in">
      <div className="page-header">
        <h1 className="glow">PLAYGROUND</h1>
        <p className="text-secondary">Test and interact with your agents</p>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Agent Interaction</h3>
          </div>
          <Conversation />
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Agent Activity</h3>
          </div>
          <div className="flex flex-col items-center justify-center" style={{ minHeight: '600px' }}>
            <AIBrain active={true} size={220} />
            <div className="text-center mt-4">
              <h3>Agent Processing</h3>
              <p className="text-secondary">Analyzing your input...</p>
              <div className="mt-3">
                <span className="badge badge-info">Thinking</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card mt-3">
        <div className="card-header">
          <h3 className="card-title">Test Scenarios</h3>
        </div>
        <div className="grid grid-3 gap-2">
          <button className="btn">
            <span style={{ marginRight: '8px' }}>🔍</span>
            Research Query
          </button>
          <button className="btn">
            <span style={{ marginRight: '8px' }}>✍️</span>
            Content Generation
          </button>
          <button className="btn">
            <span style={{ marginRight: '8px' }}>💻</span>
            Code Analysis
          </button>
        </div>
      </div>
    </div>
  )
}

export default Playground
