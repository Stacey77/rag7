import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Flow {
  name: string
  path: string
  size: number
}

const AgentBuilder = () => {
  const [flows, setFlows] = useState<Flow[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedFlow, setSelectedFlow] = useState<any>(null)
  const [runResult, setRunResult] = useState<any>(null)

  // Form states
  const [flowName, setFlowName] = useState('')
  const [flowData, setFlowData] = useState('')
  const [userInput, setUserInput] = useState('')

  // Fetch flows on mount
  useEffect(() => {
    fetchFlows()
  }, [])

  const fetchFlows = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_URL}/list_flows/`)
      const data = await response.json()
      if (data.success) {
        setFlows(data.data.flows || [])
      } else {
        setError('Failed to fetch flows')
      }
    } catch (err) {
      setError('Backend connection error. Is the API running?')
      console.error('Error fetching flows:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveFlow = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const parsedFlowData = JSON.parse(flowData)
      const response = await fetch(`${API_URL}/save_flow/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          flow_name: flowName,
          flow_data: parsedFlowData,
        }),
      })

      const data = await response.json()
      if (data.success) {
        alert('Flow saved successfully!')
        setFlowName('')
        setFlowData('')
        fetchFlows()
      } else {
        setError(data.message || 'Failed to save flow')
      }
    } catch (err) {
      setError('Invalid JSON or connection error')
      console.error('Error saving flow:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleGetFlow = async (flowName: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_URL}/get_flow/${flowName}`)
      const data = await response.json()
      if (data.success) {
        setSelectedFlow(data.data)
        setFlowData(JSON.stringify(data.data.flow_data, null, 2))
      } else {
        setError(data.message || 'Failed to get flow')
      }
    } catch (err) {
      setError('Connection error')
      console.error('Error getting flow:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRunFlow = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setRunResult(null)

    try {
      const parsedFlowData = JSON.parse(flowData)
      const response = await fetch(`${API_URL}/run_flow/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          flow_data: parsedFlowData,
          user_input: userInput,
        }),
      })

      const data = await response.json()
      setRunResult(data)
      if (!data.success) {
        setError(data.message || 'Failed to run flow')
      }
    } catch (err) {
      setError('Invalid JSON or connection error')
      console.error('Error running flow:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        try {
          const json = JSON.parse(event.target?.result as string)
          setFlowData(JSON.stringify(json, null, 2))
          setFlowName(file.name.replace('.json', ''))
        } catch (err) {
          setError('Invalid JSON file')
        }
      }
      reader.readAsText(file)
    }
  }

  return (
    <div>
      <h1>Agent Builder</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Create, manage, and execute LangFlow agents
      </p>

      {error && (
        <div className="card" style={{ 
          background: 'rgba(255, 0, 110, 0.1)', 
          borderColor: 'var(--neon-pink)',
          marginBottom: '1rem'
        }}>
          <p style={{ margin: 0, color: 'var(--neon-pink)' }}>⚠️ {error}</p>
        </div>
      )}

      <div className="grid grid-2">
        {/* Left Column - Flow List */}
        <div>
          <div className="card">
            <div className="card-header flex-between">
              <h3>Available Flows</h3>
              <button 
                className="btn btn-secondary" 
                onClick={fetchFlows}
                disabled={loading}
                style={{ padding: '0.5rem 1rem' }}
              >
                🔄 Refresh
              </button>
            </div>

            {loading && <div className="spinner"></div>}

            <div className="flow-list">
              {flows.length === 0 ? (
                <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic', textAlign: 'center' }}>
                  No flows found. Create one below.
                </p>
              ) : (
                flows.map((flow, idx) => (
                  <div key={idx} className="flow-item">
                    <div>
                      <h4 style={{ margin: 0, marginBottom: '0.25rem' }}>{flow.name}</h4>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        {(flow.size / 1024).toFixed(2)} KB
                      </div>
                    </div>
                    <button 
                      className="btn btn-primary" 
                      onClick={() => handleGetFlow(flow.name)}
                      disabled={loading}
                      style={{ padding: '0.5rem 1rem' }}
                    >
                      Load
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* API Connection Status */}
          <div className="card mt-3">
            <div className="card-header">
              <h3>Backend Status</h3>
            </div>
            <div className="flex-between">
              <span>API Connection</span>
              <span className={`status-badge ${error ? 'status-offline' : 'status-online'}`}>
                {error ? 'Offline' : 'Online'}
              </span>
            </div>
            <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              API URL: {API_URL}
            </div>
          </div>
        </div>

        {/* Right Column - Flow Editor */}
        <div>
          <div className="card mb-3">
            <div className="card-header">
              <h3>Save Flow</h3>
            </div>
            <form onSubmit={handleSaveFlow}>
              <div className="form-group">
                <label>Flow Name</label>
                <input
                  type="text"
                  value={flowName}
                  onChange={(e) => setFlowName(e.target.value)}
                  placeholder="my_agent_flow"
                  required
                />
              </div>

              <div className="form-group">
                <label>Flow JSON Data</label>
                <textarea
                  value={flowData}
                  onChange={(e) => setFlowData(e.target.value)}
                  placeholder='{"nodes": [], "edges": []}'
                  rows={8}
                  required
                  style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}
                />
              </div>

              <div className="form-group">
                <label>Or Upload JSON File</label>
                <input
                  type="file"
                  accept=".json"
                  onChange={handleFileUpload}
                  style={{ padding: '0.5rem' }}
                />
              </div>

              <button 
                type="submit" 
                className="btn btn-primary" 
                disabled={loading}
                style={{ width: '100%' }}
              >
                💾 Save Flow
              </button>
            </form>
          </div>

          {/* Run Flow */}
          <div className="card">
            <div className="card-header">
              <h3>Run Flow</h3>
            </div>
            <form onSubmit={handleRunFlow}>
              <div className="form-group">
                <label>User Input</label>
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="Enter your query..."
                  required
                />
              </div>

              <button 
                type="submit" 
                className="btn btn-success" 
                disabled={loading || !flowData}
                style={{ width: '100%' }}
              >
                ▶️ Execute Flow
              </button>
            </form>

            {runResult && (
              <div style={{ 
                marginTop: '1rem', 
                padding: '1rem', 
                background: 'var(--dark-bg)', 
                borderRadius: '8px',
                border: `1px solid ${runResult.success ? 'var(--neon-green)' : 'var(--neon-pink)'}`
              }}>
                <h4 style={{ marginTop: 0, color: runResult.success ? 'var(--neon-green)' : 'var(--neon-pink)' }}>
                  {runResult.success ? '✅ Success' : '❌ Error'}
                </h4>
                <p style={{ margin: 0, fontSize: '0.9rem' }}>
                  {runResult.message}
                </p>
                {runResult.data && (
                  <pre style={{ 
                    marginTop: '1rem', 
                    padding: '0.75rem', 
                    background: 'var(--dark-card)', 
                    borderRadius: '4px',
                    overflow: 'auto',
                    fontSize: '0.85rem'
                  }}>
                    {JSON.stringify(runResult.data, null, 2)}
                  </pre>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="card mt-4">
        <div className="card-header">
          <h3>Quick Start Guide</h3>
        </div>
        <ol style={{ color: 'var(--text-secondary)', lineHeight: '1.8' }}>
          <li>Open LangFlow at <a href="http://localhost:7860" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--neon-blue)' }}>http://localhost:7860</a></li>
          <li>Create a flow using the visual builder</li>
          <li>Export the flow as JSON</li>
          <li>Upload or paste the JSON in the "Save Flow" section above</li>
          <li>Click "Save Flow" to store it in the backend</li>
          <li>Load the flow from the "Available Flows" list</li>
          <li>Enter user input and click "Execute Flow" to run it</li>
        </ol>
      </div>
    </div>
  )
}

export default AgentBuilder
