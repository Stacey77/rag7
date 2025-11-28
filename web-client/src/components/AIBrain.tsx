import { useState, useEffect } from 'react'

interface AIBrainProps {
  status?: 'active' | 'thinking' | 'idle'
}

function AIBrain({ status = 'idle' }: AIBrainProps) {
  const [pulse, setPulse] = useState(false)

  useEffect(() => {
    if (status === 'thinking') {
      const interval = setInterval(() => {
        setPulse(prev => !prev)
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [status])

  return (
    <div className="ai-brain-container">
      <div className={`ai-brain ${status} ${pulse ? 'pulse' : ''}`}>
        <div className="brain-core"></div>
        <div className="brain-ring ring-1"></div>
        <div className="brain-ring ring-2"></div>
        <div className="brain-ring ring-3"></div>
      </div>
      <p className="brain-status">{status.toUpperCase()}</p>
    </div>
  )
}

export default AIBrain
