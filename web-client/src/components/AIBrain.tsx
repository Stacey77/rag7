import { useState, useEffect } from 'react'
import './AIBrain.css'

interface AIBrainProps {
  active?: boolean
  size?: number
}

function AIBrain({ active = false, size = 200 }: AIBrainProps) {
  const [pulseIntensity, setPulseIntensity] = useState(0.5)

  useEffect(() => {
    if (active) {
      const interval = setInterval(() => {
        setPulseIntensity(Math.random() * 0.5 + 0.5)
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [active])

  return (
    <div className="ai-brain-container" style={{ width: size, height: size }}>
      <div
        className={`ai-brain ${active ? 'active' : ''}`}
        style={{
          opacity: pulseIntensity,
        }}
      >
        <div className="brain-core"></div>
        <div className="brain-ring ring-1"></div>
        <div className="brain-ring ring-2"></div>
        <div className="brain-ring ring-3"></div>
        <div className="brain-particle particle-1"></div>
        <div className="brain-particle particle-2"></div>
        <div className="brain-particle particle-3"></div>
        <div className="brain-particle particle-4"></div>
      </div>
    </div>
  )
}

export default AIBrain
