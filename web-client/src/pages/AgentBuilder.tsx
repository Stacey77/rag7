import { useState, useEffect } from 'react'
import './AgentBuilder.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Flow {
  name: string
}

const AgentBuilder = () => {
  const [flows, setFlows] = useState<Flow[]>([])
  const [selectedFlow, setSelectedFlow] = useState<string | null>(null)
  const [flowData, setFlowData] = useState<any>(null)
  const [userInput, setUserInput] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadFlows()
  }, [])

  const loadFlows = async () => {
    try {
      const response = await fetch(`${API_URL}/list_flows/`)
      const data = await response.json()
      setFlows(data.flows.map((name: string) => ({ name })))
    } catch (err) {
      console.error('Error loading flows:', err)
      setError('Failed to load flows')
    }
  }

  const handleFlowSelect = async (flowName: string) => {
    setSelectedFlow(flowName)
    setError(null)

    try {
      const response = await fetch(`${API_URL}/get_flow/${flowName}`)
      const data = await response.json()
      setFlowData(data.flow_data)
    } catch (err) {
      console.error('Error loading flow:', err)
      setError('Failed to load flow')
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_URL}/save_flow/`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to upload flow')
      }

      await loadFlows()
      alert('Flow uploaded successfully!')
    } catch (err) {
      console.error('Error uploading flow:', err)
      setError('Failed to upload flow')
    } finally {
      setLoading(false)
    }
  }

  const handleRunFlow = async () => {
    if (!selectedFlow || !userInput.trim()) {
      setError('Please select a flow and enter input')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // First, get the flow file
      const flowResponse = await fetch(`${API_URL}/get_flow/${selectedFlow}`)
      const flowJson = await flowResponse.json()

      // Create a blob from the flow data
      const blob = new Blob([JSON.stringify(flowJson.flow_data)], {
        type: 'application/json',
      })
      const file = new File([blob], selectedFlow, { type: 'application/json' })

      // Create form data for the run request
      const formData = new FormData()
      formData.append('flow_file', file)
      formData.append('user_input', userInput)

      const response = await fetch(`${API_URL}/run_flow/`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Flow execution failed')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      console.error('Error running flow:', err)
      setError('Failed to run flow')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="agent-builder slide-in">
      <header className="page-header">
        <h1>Agent Builder</h1>
        <p className="text-muted">Create, Manage & Execute Agent Flows</p>
      </header>

      <div className="builder-grid">
        <section className="builder-main">
          <div className="card">
            <h3 className="mb-2">Flow Management</h3>

            <div className="flow-actions mb-3">
              <button
                onClick={() => window.open('http://localhost:7860', '_blank')}
              >
                Open LangFlow Designer
              </button>

              <div className="upload-flow">
                <label htmlFor="flow-upload" className="button-like">
                  Upload Flow
                </label>
                <input
                  id="flow-upload"
                  type="file"
                  accept=".json"
                  onChange={handleFileUpload}
                  disabled={loading}
                  style={{ display: 'none' }}
                />
              </div>

              <button className="secondary" onClick={loadFlows}>
                Refresh Flows
              </button>
            </div>

            {error && (
              <div className="error-message">
                ⚠️ {error}
              </div>
            )}

            <div className="flows-section">
              <h4 className="mb-2">Saved Flows ({flows.length})</h4>

              {flows.length === 0 ? (
                <div className="empty-flows">
                  <p className="text-muted">
                    No flows saved yet. Create one in LangFlow and upload it here.
                  </p>
                </div>
              ) : (
                <div className="flows-list">
                  {flows.map((flow) => (
                    <div
                      key={flow.name}
                      className={`flow-item ${
                        selectedFlow === flow.name ? 'selected' : ''
                      }`}
                      onClick={() => handleFlowSelect(flow.name)}
                    >
                      <span className="flow-icon">📋</span>
                      <span className="flow-name">{flow.name}</span>
                      {selectedFlow === flow.name && (
                        <span className="selected-indicator">✓</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {selectedFlow && (
            <div className="card">
              <h3 className="mb-2">Execute Flow: {selectedFlow}</h3>

              <div className="execute-section">
                <label>User Input</label>
                <textarea
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="Enter your prompt or question..."
                  rows={4}
                  className="mb-2"
                />

                <button
                  onClick={handleRunFlow}
                  disabled={loading || !userInput.trim()}
                >
                  {loading ? 'Running...' : 'Run Flow'}
                </button>
              </div>

              {loading && (
                <div className="loading-container">
                  <div className="loading-spinner"></div>
                  <p className="text-muted">Executing flow...</p>
                </div>
              )}

              {result && (
                <div className="result-section">
                  <h4 className="mb-2">Result</h4>
                  <div className="result-content">
                    {result.execution_mode === 'simulated' && (
                      <div className="warning-message mb-2">
                        ⚠️ Simulated Mode: {result.note}
                      </div>
                    )}
                    <div className="result-text">
                      {result.result || 'No result returned'}
                    </div>
                    <div className="result-meta mt-2">
                      <span className="meta-item">
                        Mode: {result.execution_mode}
                      </span>
                      <span className="meta-item">
                        Status: {result.status}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        <aside className="builder-sidebar">
          <div className="card">
            <h3 className="mb-2">Quick Guide</h3>
            <div className="guide-steps">
              <div className="guide-step">
                <span className="step-number">1</span>
                <div className="step-content">
                  <h4>Design Flow</h4>
                  <p className="text-muted">
                    Open LangFlow and create your agent workflow visually
                  </p>
                </div>
              </div>

              <div className="guide-step">
                <span className="step-number">2</span>
                <div className="step-content">
                  <h4>Export & Upload</h4>
                  <p className="text-muted">
                    Export your flow as JSON and upload it here
                  </p>
                </div>
              </div>

              <div className="guide-step">
                <span className="step-number">3</span>
                <div className="step-content">
                  <h4>Test & Execute</h4>
                  <p className="text-muted">
                    Select your flow, enter input, and run it
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="mb-2">Backend API</h3>
            <div className="api-info">
              <div className="api-item">
                <span className="api-label">URL:</span>
                <span className="api-value">{API_URL}</span>
              </div>
              <div className="api-item">
                <a
                  href={`${API_URL}/docs`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="api-link"
                >
                  View API Docs →
                </a>
              </div>
            </div>
          </div>

          {flowData && (
            <div className="card">
              <h3 className="mb-2">Flow Details</h3>
              <div className="flow-details">
                <pre className="flow-json">
                  {JSON.stringify(flowData, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}

export default AgentBuilder
