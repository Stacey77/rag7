import './AIBrain.css'

const AIBrain = () => {
  return (
    <div className="ai-brain-container">
      <div className="brain-core">
        <div className="brain-pulse"></div>
        <div className="brain-ring ring-1"></div>
        <div className="brain-ring ring-2"></div>
        <div className="brain-ring ring-3"></div>
        <div className="brain-center">AI</div>
      </div>
      <div className="brain-stats">
        <div className="stat-item">
          <div className="stat-label">Neural Activity</div>
          <div className="stat-value">98%</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Response Time</div>
          <div className="stat-value">42ms</div>
        </div>
      </div>
    </div>
  )
}

export default AIBrain
