import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Flow {
  name: string
  size: number
  modified: number
  path: string
}

function AgentBuilder() {
  const [flows, setFlows] = useState<Flow[]>([])
  const [selectedFlow, setSelectedFlow] = useState<string | null>(null)
  const [userInput, setUserInput] = useState('')
  const [executionResult, setExecutionResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load flows on mount
  useEffect(() => {
    loadFlows()
  }, [])

  const loadFlows = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await axios.get(`${API_URL}/list_flows/`)
      setFlows(response.data.flows || [])
    } catch (err: any) {
      setError(`Failed to load flows: ${err.message}`)
      console.error('Error loading flows:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.json')) {
      setError('Please upload a .json file')
      return
    }

    const formData = new FormData()
    formData.append('flow_file', file)

    try {
      setLoading(true)
      setError(null)
      const response = await axios.post(`${API_URL}/save_flow/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      console.log('Flow saved:', response.data)
      await loadFlows() // Reload the list
      alert(`Flow "${response.data.filename}" saved successfully!`)
    } catch (err: any) {
      setError(`Failed to save flow: ${err.message}`)
      console.error('Error saving flow:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRunFlow = async () => {
    if (!selectedFlow || !userInput) {
      setError('Please select a flow and enter input')
      return
    }

    try {
      setLoading(true)
      setError(null)
      setExecutionResult(null)

      // Get the flow file
      const flowResponse = await axios.get(`${API_URL}/get_flow/${selectedFlow}`)
      const flowContent = JSON.stringify(flowResponse.data.content)
      
      // Create a blob and file from the flow content
      const blob = new Blob([flowContent], { type: 'application/json' })
      const file = new File([blob], selectedFlow, { type: 'application/json' })

      // Run the flow
      const formData = new FormData()
      formData.append('flow_file', file)
      formData.append('user_input', userInput)

      const response = await axios.post(`${API_URL}/run_flow/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setExecutionResult(response.data)
    } catch (err: any) {
      setError(`Failed to run flow: ${err.message}`)
      console.error('Error running flow:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="agent-builder">
      <h1>Agent Builder</h1>
      <p className="mb-2">Build, save, and execute LangFlow agents</p>

      {error && (
        <div className="card" style={{ background: 'var(--error)', marginBottom: '1rem' }}>
          <p>{error}</p>
        </div>
      )}

      <div className="grid grid-2">
        {/* Flow Management */}
        <div className="card">
          <h3>Flow Management</h3>
          
          <div className="mb-2">
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>
              Upload Flow JSON
            </label>
            <input 
              type="file" 
              accept=".json"
              onChange={handleFileUpload}
              disabled={loading}
            />
          </div>

          <div className="mb-2">
            <div className="flex-between mb-1">
              <label>Saved Flows ({flows.length})</label>
              <button onClick={loadFlows} disabled={loading}>
                {loading ? '⏳' : '🔄'} Refresh
              </button>
            </div>
            
            <div className="flows-list" style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {flows.length === 0 ? (
                <p className="empty-state">No flows saved yet. Upload a flow to get started.</p>
              ) : (
                flows.map(flow => (
                  <div 
                    key={flow.name}
                    className={`flow-item card ${selectedFlow === flow.name ? 'selected' : ''}`}
                    onClick={() => setSelectedFlow(flow.name)}
                    style={{ 
                      cursor: 'pointer',
                      marginBottom: '0.5rem',
                      border: selectedFlow === flow.name ? '2px solid var(--accent-cyan)' : undefined
                    }}
                  >
                    <div className="flex-between">
                      <div>
                        <strong>{flow.name}</strong>
                        <p style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>
                          {(flow.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                      <span className="badge badge-primary">
                        {selectedFlow === flow.name ? '✓ Selected' : 'Select'}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="flex gap-1">
            <button 
              onClick={() => window.open('http://localhost:7860', '_blank')}
              style={{ flex: 1 }}
            >
              Open LangFlow UI
            </button>
            <button 
              onClick={() => window.open(`${API_URL}/docs`, '_blank')}
              style={{ flex: 1 }}
            >
              API Docs
            </button>
          </div>
        </div>

        {/* Flow Execution */}
        <div className="card">
          <h3>Execute Flow</h3>
          
          {selectedFlow ? (
            <>
              <p className="mb-1">
                <strong>Selected Flow:</strong> <code>{selectedFlow}</code>
              </p>

              <div className="mb-2">
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>
                  User Input
                </label>
                <textarea
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="Enter your input for the flow..."
                  rows={5}
                  style={{ width: '100%' }}
                />
              </div>

              <button 
                onClick={handleRunFlow}
                disabled={loading || !userInput}
                style={{ width: '100%' }}
              >
                {loading ? '⏳ Running...' : '▶️ Run Flow'}
              </button>

              {executionResult && (
                <div className="mt-2 card" style={{ background: 'rgba(0, 255, 249, 0.1)' }}>
                  <h4>Execution Result</h4>
                  <div className="flex gap-1 mt-1 mb-1">
                    <span className={`badge badge-${executionResult.status === 'success' ? 'success' : 'error'}`}>
                      {executionResult.status}
                    </span>
                    <span className="badge badge-secondary">
                      {executionResult.execution_mode || 'unknown'}
                    </span>
                  </div>
                  
                  {executionResult.warning && (
                    <p style={{ color: 'var(--warning)', marginBottom: '0.5rem' }}>
                      ⚠️ {executionResult.warning}
                    </p>
                  )}
                  
                  <div>
                    <strong>Input:</strong>
                    <pre style={{ marginTop: '0.5rem' }}>{executionResult.input}</pre>
                  </div>
                  
                  <div className="mt-1">
                    <strong>Output:</strong>
                    <pre style={{ marginTop: '0.5rem' }}>{executionResult.output}</pre>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <p>Select a flow from the list to execute it</p>
            </div>
          )}
        </div>
      </div>

      {/* Documentation */}
      <div className="card mt-2">
        <h3>Quick Guide</h3>
        <div className="grid grid-3">
          <div>
            <h4>1. Create Flow</h4>
            <p>Design your flow in LangFlow UI (port 7860) and export as JSON</p>
          </div>
          <div>
            <h4>2. Upload Flow</h4>
            <p>Upload the exported JSON file using the file input above</p>
          </div>
          <div>
            <h4>3. Execute</h4>
            <p>Select your flow, provide input, and click Run to execute</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AgentBuilder
