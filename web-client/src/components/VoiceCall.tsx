import { useState, useEffect, useRef, useCallback } from 'react'
import { RetellWebClient } from 'retell-client-js-sdk'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface CallState {
  callId: string | null
  status: 'idle' | 'connecting' | 'connected' | 'ended' | 'error'
  transcript: Array<{ role: 'agent' | 'user'; content: string; timestamp: number }>
  error: string | null
  duration: number
  isMuted: boolean
}

interface Agent {
  agent_id: string
  agent_name: string
  voice_id?: string
  language: string
}

function VoiceCall() {
  const [callState, setCallState] = useState<CallState>({
    callId: null,
    status: 'idle',
    transcript: [],
    error: null,
    duration: 0,
    isMuted: false
  })
  
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgent, setSelectedAgent] = useState<string>('')
  const [isConfigured, setIsConfigured] = useState<boolean | null>(null)
  const [callHistory, setCallHistory] = useState<any[]>([])
  const [showHistory, setShowHistory] = useState(false)
  
  const retellClientRef = useRef<RetellWebClient | null>(null)
  const durationIntervalRef = useRef<number | null>(null)
  const startTimeRef = useRef<number | null>(null)

  // Check if Retell is configured
  useEffect(() => {
    const checkConfig = async () => {
      try {
        const response = await fetch(`${API_URL}/retell/status`)
        const data = await response.json()
        setIsConfigured(data.configured)
      } catch (error) {
        console.error('Error checking Retell config:', error)
        setIsConfigured(false)
      }
    }
    checkConfig()
  }, [])

  // Load agents
  useEffect(() => {
    if (!isConfigured) return
    
    const loadAgents = async () => {
      try {
        const response = await fetch(`${API_URL}/retell/agents`)
        const data = await response.json()
        setAgents(data.agents || [])
        if (data.agents?.length > 0) {
          setSelectedAgent(data.agents[0].agent_id)
        }
      } catch (error) {
        console.error('Error loading agents:', error)
      }
    }
    loadAgents()
  }, [isConfigured])

  // Load call history
  const loadHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/retell/calls`)
      const data = await response.json()
      setCallHistory(data.calls || [])
    } catch (error) {
      console.error('Error loading call history:', error)
    }
  }, [])

  useEffect(() => {
    if (isConfigured && showHistory) {
      loadHistory()
    }
  }, [isConfigured, showHistory, loadHistory])

  // Start duration timer
  const startDurationTimer = () => {
    startTimeRef.current = Date.now()
    durationIntervalRef.current = window.setInterval(() => {
      if (startTimeRef.current) {
        setCallState(prev => ({
          ...prev,
          duration: Math.floor((Date.now() - startTimeRef.current!) / 1000)
        }))
      }
    }, 1000)
  }

  // Stop duration timer
  const stopDurationTimer = () => {
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current)
      durationIntervalRef.current = null
    }
    startTimeRef.current = null
  }

  // Format duration
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Start a web call
  const startCall = async () => {
    if (!selectedAgent) {
      setCallState(prev => ({ ...prev, error: 'Please select an agent' }))
      return
    }

    setCallState(prev => ({
      ...prev,
      status: 'connecting',
      error: null,
      transcript: [],
      duration: 0
    }))

    try {
      // Register the call with backend
      const response = await fetch(`${API_URL}/retell/web-call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: selectedAgent,
          metadata: {
            source: 'ragamuffin-ui',
            timestamp: new Date().toISOString()
          }
        })
      })

      if (!response.ok) {
        throw new Error('Failed to register call')
      }

      const { call_id, access_token } = await response.json()

      // Initialize Retell Web Client
      retellClientRef.current = new RetellWebClient()

      // Set up event handlers
      retellClientRef.current.on('call_started', () => {
        console.log('Call started')
        setCallState(prev => ({
          ...prev,
          callId: call_id,
          status: 'connected'
        }))
        startDurationTimer()
      })

      retellClientRef.current.on('call_ended', () => {
        console.log('Call ended')
        setCallState(prev => ({
          ...prev,
          status: 'ended'
        }))
        stopDurationTimer()
        loadHistory()
      })

      retellClientRef.current.on('error', (error: Error) => {
        console.error('Retell error:', error)
        setCallState(prev => ({
          ...prev,
          status: 'error',
          error: error.message
        }))
        stopDurationTimer()
      })

      retellClientRef.current.on('update', (update: any) => {
        // Handle transcript updates
        if (update.transcript) {
          const newTranscript = update.transcript.map((t: any) => ({
            role: t.role,
            content: t.content,
            timestamp: t.timestamp || Date.now()
          }))
          setCallState(prev => ({
            ...prev,
            transcript: newTranscript
          }))
        }
      })

      // Start the call
      await retellClientRef.current.startCall({
        accessToken: access_token,
        sampleRate: 24000,
        captureDeviceId: 'default'
      })

    } catch (error) {
      console.error('Error starting call:', error)
      setCallState(prev => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Failed to start call'
      }))
    }
  }

  // End the call
  const endCall = async () => {
    try {
      if (retellClientRef.current) {
        retellClientRef.current.stopCall()
        retellClientRef.current = null
      }

      if (callState.callId) {
        await fetch(`${API_URL}/retell/end-call/${callState.callId}`, {
          method: 'POST'
        })
      }

      stopDurationTimer()
      setCallState(prev => ({
        ...prev,
        status: 'ended'
      }))
    } catch (error) {
      console.error('Error ending call:', error)
    }
  }

  // Toggle mute
  const toggleMute = () => {
    if (retellClientRef.current) {
      const newMuteState = !callState.isMuted
      retellClientRef.current.mute(newMuteState)
      setCallState(prev => ({ ...prev, isMuted: newMuteState }))
    }
  }

  // Reset for new call
  const resetCall = () => {
    setCallState({
      callId: null,
      status: 'idle',
      transcript: [],
      error: null,
      duration: 0,
      isMuted: false
    })
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (retellClientRef.current) {
        retellClientRef.current.stopCall()
      }
      stopDurationTimer()
    }
  }, [])

  if (isConfigured === null) {
    return (
      <div className="voice-call-container">
        <div className="loading">Checking Retell.ai configuration...</div>
      </div>
    )
  }

  if (!isConfigured) {
    return (
      <div className="voice-call-container">
        <div className="not-configured">
          <h3>🎤 Retell.ai Voice Calls</h3>
          <p>Retell.ai is not configured. To enable voice calls:</p>
          <ol>
            <li>Get an API key from <a href="https://retell.ai" target="_blank" rel="noopener noreferrer">retell.ai</a></li>
            <li>Set <code>RETELL_API_KEY</code> in your environment</li>
            <li>Create an agent in the Retell dashboard</li>
            <li>Restart the backend service</li>
          </ol>
        </div>
      </div>
    )
  }

  return (
    <div className="voice-call-container">
      <div className="voice-call-header">
        <h3>🎤 Voice Call</h3>
        <button 
          className="history-toggle"
          onClick={() => setShowHistory(!showHistory)}
        >
          {showHistory ? 'Hide History' : 'Show History'}
        </button>
      </div>

      {showHistory ? (
        <div className="call-history">
          <h4>Call History</h4>
          {callHistory.length === 0 ? (
            <p className="empty-state">No call history yet</p>
          ) : (
            <div className="history-list">
              {callHistory.map((call, idx) => (
                <div key={idx} className="history-item">
                  <div className="history-item-header">
                    <span className={`status-badge ${call.call_status}`}>
                      {call.call_status}
                    </span>
                    <span className="call-duration">
                      {call.end_timestamp && call.start_timestamp
                        ? formatDuration(Math.floor((call.end_timestamp - call.start_timestamp) / 1000))
                        : '--:--'}
                    </span>
                  </div>
                  <div className="history-item-body">
                    <small>ID: {call.call_id?.slice(0, 8)}...</small>
                    {call.transcript && (
                      <p className="transcript-preview">
                        {call.transcript.slice(0, 100)}...
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <>
          {/* Agent Selection */}
          {callState.status === 'idle' && (
            <div className="agent-selection">
              <label>Select Agent:</label>
              <select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
                disabled={agents.length === 0}
              >
                {agents.length === 0 ? (
                  <option value="">No agents available</option>
                ) : (
                  agents.map(agent => (
                    <option key={agent.agent_id} value={agent.agent_id}>
                      {agent.agent_name} ({agent.language})
                    </option>
                  ))
                )}
              </select>
            </div>
          )}

          {/* Call Status Display */}
          <div className={`call-status status-${callState.status}`}>
            {callState.status === 'idle' && (
              <div className="status-idle">
                <span className="pulse-icon">📞</span>
                <p>Ready to start a voice call</p>
              </div>
            )}
            {callState.status === 'connecting' && (
              <div className="status-connecting">
                <span className="connecting-animation">🔄</span>
                <p>Connecting...</p>
              </div>
            )}
            {callState.status === 'connected' && (
              <div className="status-connected">
                <span className="active-icon pulse">🎙️</span>
                <p>Call in progress</p>
                <span className="duration">{formatDuration(callState.duration)}</span>
              </div>
            )}
            {callState.status === 'ended' && (
              <div className="status-ended">
                <span className="ended-icon">✅</span>
                <p>Call ended</p>
                <span className="final-duration">Duration: {formatDuration(callState.duration)}</span>
              </div>
            )}
            {callState.status === 'error' && (
              <div className="status-error">
                <span className="error-icon">❌</span>
                <p>Error: {callState.error}</p>
              </div>
            )}
          </div>

          {/* Transcript */}
          {callState.transcript.length > 0 && (
            <div className="transcript-container">
              <h4>Live Transcript</h4>
              <div className="transcript">
                {callState.transcript.map((entry, idx) => (
                  <div key={idx} className={`transcript-entry ${entry.role}`}>
                    <span className="role-label">
                      {entry.role === 'agent' ? '🤖 Agent' : '👤 You'}
                    </span>
                    <p>{entry.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Call Controls */}
          <div className="call-controls">
            {callState.status === 'idle' && (
              <button 
                className="start-call-btn"
                onClick={startCall}
                disabled={!selectedAgent || agents.length === 0}
              >
                🎤 Start Call
              </button>
            )}
            
            {callState.status === 'connecting' && (
              <button className="connecting-btn" disabled>
                Connecting...
              </button>
            )}
            
            {callState.status === 'connected' && (
              <>
                <button 
                  className={`mute-btn ${callState.isMuted ? 'muted' : ''}`}
                  onClick={toggleMute}
                >
                  {callState.isMuted ? '🔇 Unmute' : '🔊 Mute'}
                </button>
                <button 
                  className="end-call-btn"
                  onClick={endCall}
                >
                  📞 End Call
                </button>
              </>
            )}
            
            {(callState.status === 'ended' || callState.status === 'error') && (
              <button 
                className="new-call-btn"
                onClick={resetCall}
              >
                🔄 New Call
              </button>
            )}
          </div>
        </>
      )}

      <style>{`
        .voice-call-container {
          background: linear-gradient(135deg, rgba(30, 0, 50, 0.9), rgba(60, 0, 80, 0.9));
          border-radius: 16px;
          padding: 24px;
          border: 1px solid rgba(138, 43, 226, 0.3);
          box-shadow: 0 8px 32px rgba(138, 43, 226, 0.2);
        }

        .voice-call-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .voice-call-header h3 {
          margin: 0;
          font-family: 'Orbitron', sans-serif;
          color: #fff;
        }

        .history-toggle {
          background: rgba(138, 43, 226, 0.3);
          border: 1px solid rgba(138, 43, 226, 0.5);
          color: #fff;
          padding: 8px 16px;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .history-toggle:hover {
          background: rgba(138, 43, 226, 0.5);
        }

        .not-configured {
          text-align: center;
          padding: 20px;
        }

        .not-configured h3 {
          color: #fff;
          font-family: 'Orbitron', sans-serif;
        }

        .not-configured ol {
          text-align: left;
          max-width: 400px;
          margin: 20px auto;
          color: #ccc;
        }

        .not-configured code {
          background: rgba(0, 0, 0, 0.3);
          padding: 2px 6px;
          border-radius: 4px;
          color: #00ff88;
        }

        .not-configured a {
          color: #00ff88;
        }

        .agent-selection {
          margin-bottom: 20px;
        }

        .agent-selection label {
          display: block;
          margin-bottom: 8px;
          color: #ccc;
        }

        .agent-selection select {
          width: 100%;
          padding: 12px;
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(138, 43, 226, 0.3);
          border-radius: 8px;
          color: #fff;
          font-size: 16px;
        }

        .call-status {
          text-align: center;
          padding: 30px;
          border-radius: 12px;
          margin-bottom: 20px;
          min-height: 120px;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
        }

        .status-idle {
          background: rgba(100, 100, 100, 0.2);
        }

        .status-connecting {
          background: rgba(255, 193, 7, 0.2);
        }

        .status-connected {
          background: rgba(0, 255, 136, 0.2);
        }

        .status-ended {
          background: rgba(100, 149, 237, 0.2);
        }

        .status-error {
          background: rgba(255, 68, 68, 0.2);
        }

        .pulse-icon, .active-icon.pulse {
          font-size: 48px;
          animation: pulse 2s infinite;
        }

        .connecting-animation {
          font-size: 48px;
          animation: spin 1s linear infinite;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.1); opacity: 0.8; }
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .duration, .final-duration {
          font-family: 'Orbitron', sans-serif;
          font-size: 24px;
          color: #00ff88;
          margin-top: 10px;
        }

        .transcript-container {
          background: rgba(0, 0, 0, 0.3);
          border-radius: 12px;
          padding: 16px;
          margin-bottom: 20px;
          max-height: 300px;
          overflow-y: auto;
        }

        .transcript-container h4 {
          margin: 0 0 12px 0;
          color: #fff;
          font-family: 'Orbitron', sans-serif;
          font-size: 14px;
        }

        .transcript-entry {
          margin-bottom: 12px;
          padding: 10px;
          border-radius: 8px;
        }

        .transcript-entry.agent {
          background: rgba(138, 43, 226, 0.2);
          margin-right: 20%;
        }

        .transcript-entry.user {
          background: rgba(0, 255, 136, 0.2);
          margin-left: 20%;
        }

        .role-label {
          font-size: 12px;
          color: #888;
          display: block;
          margin-bottom: 4px;
        }

        .transcript-entry p {
          margin: 0;
          color: #fff;
        }

        .call-controls {
          display: flex;
          gap: 12px;
          justify-content: center;
        }

        .call-controls button {
          padding: 14px 28px;
          font-size: 16px;
          font-family: 'Orbitron', sans-serif;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s;
          border: none;
        }

        .start-call-btn, .new-call-btn {
          background: linear-gradient(135deg, #00ff88, #00cc6a);
          color: #000;
        }

        .start-call-btn:hover:not(:disabled), .new-call-btn:hover {
          transform: scale(1.05);
          box-shadow: 0 4px 20px rgba(0, 255, 136, 0.4);
        }

        .start-call-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .connecting-btn {
          background: linear-gradient(135deg, #ffc107, #ff9800);
          color: #000;
        }

        .end-call-btn {
          background: linear-gradient(135deg, #ff4444, #cc0000);
          color: #fff;
        }

        .end-call-btn:hover {
          transform: scale(1.05);
          box-shadow: 0 4px 20px rgba(255, 68, 68, 0.4);
        }

        .mute-btn {
          background: rgba(100, 100, 100, 0.5);
          color: #fff;
        }

        .mute-btn.muted {
          background: rgba(255, 68, 68, 0.3);
        }

        .mute-btn:hover {
          background: rgba(150, 150, 150, 0.5);
        }

        .call-history {
          padding: 16px;
        }

        .call-history h4 {
          margin: 0 0 16px 0;
          color: #fff;
          font-family: 'Orbitron', sans-serif;
        }

        .history-list {
          max-height: 400px;
          overflow-y: auto;
        }

        .history-item {
          background: rgba(0, 0, 0, 0.3);
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 12px;
        }

        .history-item-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .status-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          text-transform: uppercase;
        }

        .status-badge.ended {
          background: rgba(0, 255, 136, 0.2);
          color: #00ff88;
        }

        .status-badge.error {
          background: rgba(255, 68, 68, 0.2);
          color: #ff4444;
        }

        .call-duration {
          font-family: 'Orbitron', sans-serif;
          color: #888;
        }

        .history-item-body small {
          color: #666;
          display: block;
          margin-bottom: 4px;
        }

        .transcript-preview {
          margin: 0;
          color: #aaa;
          font-size: 14px;
          line-height: 1.4;
        }

        .empty-state {
          text-align: center;
          color: #666;
          padding: 40px;
        }

        .loading {
          text-align: center;
          padding: 40px;
          color: #888;
        }
      `}</style>
    </div>
  )
}

export default VoiceCall
