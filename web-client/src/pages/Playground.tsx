import Conversation from '../components/Conversation';

function Playground() {
  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Playground</h1>
        <p className="page-subtitle">Test and interact with your AI agents</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <h2 className="card-title">Agent Selection</h2>
          <div className="form-group">
            <label className="form-label">Select Agent</label>
            <select className="form-select">
              <option>Customer Support Agent</option>
              <option>Data Analyzer</option>
              <option>Code Assistant</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Temperature</label>
            <input type="range" min="0" max="1" step="0.1" defaultValue="0.7" className="form-input" />
          </div>
          <div className="form-group">
            <label className="form-label">Max Tokens</label>
            <input type="number" defaultValue="1000" className="form-input" />
          </div>
        </div>

        <div className="card">
          <h2 className="card-title">Configuration</h2>
          <div className="card-content">
            <p><strong>Model:</strong> GPT-4</p>
            <p><strong>Status:</strong> Ready</p>
            <p><strong>Mode:</strong> Interactive</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Conversation</h2>
        <Conversation />
      </div>
    </div>
  );
}

export default Playground;
