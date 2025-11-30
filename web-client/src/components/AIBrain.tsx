import { useEffect, useState } from 'react'
import './AIBrain.css'

const AIBrain = () => {
  const [pulse, setPulse] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      setPulse(true)
      setTimeout(() => setPulse(false), 1000)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="ai-brain-container">
      <div className={`ai-brain ${pulse ? 'pulse' : ''}`}>
        <div className="brain-core"></div>
        <div className="brain-ring ring-1"></div>
        <div className="brain-ring ring-2"></div>
        <div className="brain-ring ring-3"></div>
      </div>
    </div>
  )
}

export default AIBrain
