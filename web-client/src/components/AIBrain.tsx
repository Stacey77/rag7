import { useState, useEffect } from 'react'
import './AIBrain.css'

interface AIBrainProps {
  active?: boolean
  size?: 'small' | 'medium' | 'large'
}

const AIBrain = ({ active = true, size = 'medium' }: AIBrainProps) => {
  const [pulseState, setPulseState] = useState(0)

  useEffect(() => {
    if (!active) return

    const interval = setInterval(() => {
      setPulseState((prev) => (prev + 1) % 4)
    }, 500)

    return () => clearInterval(interval)
  }, [active])

  const sizeClass = `brain-${size}`

  return (
    <div className={`ai-brain ${sizeClass} ${active ? 'active' : 'inactive'}`}>
      <div className="brain-core">
        <div className={`brain-pulse pulse-${pulseState}`}></div>
        <div className="brain-icon">🧠</div>
      </div>
      <div className="brain-particles">
        {[...Array(8)].map((_, i) => (
          <div key={i} className={`particle particle-${i}`}></div>
        ))}
      </div>
    </div>
  )
}

export default AIBrain
