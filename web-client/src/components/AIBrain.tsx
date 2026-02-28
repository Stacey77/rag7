interface AIBrainProps {
  status?: 'idle' | 'processing' | 'success' | 'error'
  message?: string
}

function AIBrain({ status = 'idle', message }: AIBrainProps) {
  const getStatusColor = () => {
    switch (status) {
      case 'processing': return 'var(--warning)'
      case 'success': return 'var(--success)'
      case 'error': return 'var(--error)'
      default: return 'var(--primary)'
    }
  }

  return (
    <div className="ai-brain">
      <div 
        className="ai-brain-icon"
        style={{ color: getStatusColor() }}
      >
        🧠
      </div>
      <p style={{ marginTop: '1rem', textAlign: 'center' }}>
        {message || 'AI Ready'}
      </p>
      <span className={`status status-${status === 'idle' ? 'success' : status}`}>
        {status}
      </span>
    </div>
  )
}

export default AIBrain
