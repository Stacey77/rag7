import { useState, useEffect, useCallback } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Flow {
  name: string
  data?: Record<string, unknown>
}

function AgentBuilder() {
  const [flows, setFlows] = useState<string[]>([])
  const [selectedFlow, setSelectedFlow] = useState<Flow | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [userInput, setUserInput] = useState('')
  const [runResult, setRunResult] = useState<string | null>(null)
  const [isRunning, setIsRunning] = useState(false)

  // Fetch list of flows
  const fetchFlows = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_URL}/list_flows/`)
      if (!response.ok) throw new Error('Failed to fetch flows')
      const data = await response.json()
      setFlows(data.flows || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch flows')
    } finally {
      setLoading(false)
    }
  }, [])

  // Fetch specific flow
  const fetchFlow = async (flowName: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_URL}/get_flow/${encodeURIComponent(flowName)}`)
      if (!response.ok) throw new Error('Failed to fetch flow')
      const data = await response.json()
      setSelectedFlow({ name: data.flow_name, data: data.flow_data })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch flow')
    } finally {
      setLoading(false)
    }
  }

  // Save a flow
  const handleSaveFlow = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setLoading(true)
    setError(null)
    try {
      const formData = new FormData()
      formData.append('flow_file', file)

      const response = await fetch(`${API_URL}/save_flow/`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('Failed to save flow')
      await fetchFlows()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save flow')
    } finally {
      setLoading(false)
    }
  }

  // Run a flow
  const handleRunFlow = async () => {
    if (!selectedFlow || !userInput.trim()) return

    setIsRunning(true)
    setError(null)
    setRunResult(null)

    try {
      // Create a blob from the flow data
      const flowBlob = new Blob([JSON.stringify(selectedFlow.data)], { type: 'application/json' })
      const flowFile = new File([flowBlob], selectedFlow.name, { type: 'application/json' })

      const formData = new FormData()
      formData.append('flow_file', flowFile)
      formData.append('user_input', userInput)

      const response = await fetch(`${API_URL}/run_flow/`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('Failed to run flow')
      const data = await response.json()
      
      setRunResult(data.result)
      if (data.simulated) {
        setError('Warning: This is a simulated response. LangFlow is not installed on the backend.')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run flow')
    } finally {
      setIsRunning(false)
    }
  }

  useEffect(() => {
    fetchFlows()
  }, [fetchFlows])

  return (
    <div>
      <header className="page-header">
        <h1>Agent Builder</h1>
        <p style={{ color: 'var(--text-muted)' }}>Create and manage AI agents using LangFlow</p>
      </header>

      {error && (
        <div 
          className="card" 
          style={{ 
            borderColor: error.includes('Warning') ? 'var(--warning)' : 'var(--error)', 
            marginBottom: '1rem' 
          }}
        >
          <p style={{ color: error.includes('Warning') ? 'var(--warning)' : 'var(--error)' }}>
            {error}
          </p>
        </div>
      )}

      <div className="grid grid-2">
        <div>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2>Flows</h2>
              <button className="btn" onClick={fetchFlows} disabled={loading}>
                {loading ? 'Loading...' : 'Refresh'}
              </button>
            </div>

            <div style={{ marginTop: '1rem' }}>
              <input
                type="file"
                id="flow-upload"
                style={{ display: 'none' }}
                onChange={handleSaveFlow}
                accept=".json"
              />
              <label htmlFor="flow-upload">
                <span className="btn" style={{ cursor: 'pointer' }}>
                  📤 Upload Flow
                </span>
              </label>
            </div>

            <div className="flow-list" style={{ marginTop: '1rem' }}>
              {loading && flows.length === 0 ? (
                <div className="loading">
                  <div className="spinner" />
                </div>
              ) : flows.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>
                  No flows found. Upload a flow JSON file to get started.
                </p>
              ) : (
                flows.map((flow) => (
                  <div
                    key={flow}
                    className={`flow-item ${selectedFlow?.name === flow ? 'selected' : ''}`}
                    onClick={() => fetchFlow(flow)}
                  >
                    <span>📄 {flow}</span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="card">
            <h2>External Tools</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <a 
                href="http://localhost:7860" 
                target="_blank" 
                rel="noopener noreferrer"
                className="btn"
                style={{ textAlign: 'center', textDecoration: 'none' }}
              >
                🔗 Open LangFlow UI (7860)
              </a>
              <a 
                href="http://localhost:7878" 
                target="_blank" 
                rel="noopener noreferrer"
                className="btn btn-secondary"
                style={{ textAlign: 'center', textDecoration: 'none' }}
              >
                🔗 Open LangGraph (7878)
              </a>
            </div>
          </div>
        </div>

        <div>
          <div className="card">
            <h2>Flow Details</h2>
            {selectedFlow ? (
              <div>
                <p><strong>Name:</strong> {selectedFlow.name}</p>
                <pre 
                  style={{ 
                    background: 'var(--surface-light)', 
                    padding: '1rem', 
                    borderRadius: '8px',
                    marginTop: '1rem',
                    maxHeight: '200px',
                    overflow: 'auto',
                    fontSize: '0.8rem'
                  }}
                >
                  {JSON.stringify(selectedFlow.data, null, 2)}
                </pre>
              </div>
            ) : (
              <p style={{ color: 'var(--text-muted)' }}>
                Select a flow from the list to view details
              </p>
            )}
          </div>

          <div className="card">
            <h2>Run Flow</h2>
            {selectedFlow ? (
              <div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem' }}>User Input</label>
                  <textarea
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="Enter your input for the flow..."
                    style={{ minHeight: '100px' }}
                  />
                </div>
                <button 
                  className="btn" 
                  onClick={handleRunFlow}
                  disabled={isRunning || !userInput.trim()}
                >
                  {isRunning ? '⏳ Running...' : '▶️ Run Flow'}
                </button>

                {runResult && (
                  <div 
                    style={{ 
                      marginTop: '1rem',
                      padding: '1rem',
                      background: 'var(--surface-light)',
                      borderRadius: '8px',
                      borderLeft: '3px solid var(--success)'
                    }}
                  >
                    <h3 style={{ marginBottom: '0.5rem' }}>Result:</h3>
                    <p>{runResult}</p>
                  </div>
                )}
              </div>
            ) : (
              <p style={{ color: 'var(--text-muted)' }}>
                Select a flow to run it
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AgentBuilder
