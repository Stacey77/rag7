import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Flow {
  name: string
  size: number
  modified: string
  path: string
}

function AgentBuilder() {
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
      setFlows(data.flows || [])
    } catch (err) {
      console.error('Error loading flows:', err)
      setError('Failed to load flows. Is the backend running?')
    }
  }

  const loadFlowDetails = async (flowName: string) => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/get_flow/${flowName}`)
      const data = await response.json()
      setFlowData(data.flow)
      setSelectedFlow(flowName)
      setError(null)
    } catch (err) {
      console.error('Error loading flow:', err)
      setError('Failed to load flow details')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('flow_file', file)

    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/save_flow/`, {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      
      if (data.status === 'success') {
        alert('Flow saved successfully!')
        loadFlows()
        setError(null)
      } else {
        setError('Failed to save flow')
      }
    } catch (err) {
      console.error('Error saving flow:', err)
      setError('Failed to save flow. Check backend connection.')
    } finally {
      setLoading(false)
    }
  }

  const handleRunFlow = async () => {
    if (!selectedFlow || !userInput) {
      alert('Please select a flow and enter input')
      return
    }

    try {
      setLoading(true)
      setResult(null)

      // Create flow file blob
      const flowBlob = new Blob([JSON.stringify(flowData)], { type: 'application/json' })
      const formData = new FormData()
      formData.append('flow_file', flowBlob, selectedFlow)
      formData.append('user_input', userInput)

      const response = await fetch(`${API_URL}/run_flow/`, {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      setResult(data)
      setError(null)
    } catch (err) {
      console.error('Error running flow:', err)
      setError('Failed to run flow. Check backend connection.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="agent-builder fade-in">
      <div className="page-header">
        <h1 className="glow">AGENT BUILDER</h1>
        <p className="text-secondary">Create and manage your AI agent flows</p>
      </div>

      {error && (
        <div className="alert alert-danger">
          ⚠️ {error}
        </div>
      )}

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Your Flows</h3>
          </div>
          
          <div className="flow-upload mb-3">
            <label htmlFor="flow-upload" className="btn btn-accent" style={{ width: '100%' }}>
              <span style={{ marginRight: '8px' }}>⬆️</span>
              Upload Flow (JSON)
            </label>
            <input
              id="flow-upload"
              type="file"
              accept=".json"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>

          <div className="flows-list">
            {flows.length === 0 ? (
              <p className="text-center text-secondary">
                No flows available. Upload a LangFlow JSON file to get started.
              </p>
            ) : (
              flows.map((flow) => (
                <div
                  key={flow.name}
                  className={`flow-item ${selectedFlow === flow.name ? 'selected' : ''}`}
                  onClick={() => loadFlowDetails(flow.name)}
                >
                  <div className="flow-icon">📄</div>
                  <div className="flow-info">
                    <div className="flow-name">{flow.name}</div>
                    <div className="flow-meta">
                      <span className="text-muted">{(flow.size / 1024).toFixed(1)} KB</span>
                      <span className="text-muted">•</span>
                      <span className="text-muted">{new Date(flow.modified).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Flow Execution</h3>
          </div>

          {!selectedFlow ? (
            <div className="text-center text-secondary" style={{ padding: 'var(--spacing-xl)' }}>
              Select a flow from the list to execute it
            </div>
          ) : (
            <div>
              <div className="input-group">
                <label className="input-label">Selected Flow</label>
                <input
                  type="text"
                  value={selectedFlow}
                  readOnly
                  style={{ background: 'var(--highlight-bg)' }}
                />
              </div>

              <div className="input-group">
                <label className="input-label">User Input</label>
                <textarea
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="Enter your input for the agent..."
                  rows={4}
                />
              </div>

              <button
                className="btn btn-accent"
                onClick={handleRunFlow}
                disabled={loading || !userInput}
                style={{ width: '100%' }}
              >
                {loading ? 'Executing...' : '▶️ Run Flow'}
              </button>

              {result && (
                <div className="result-container">
                  <h4 style={{ marginBottom: 'var(--spacing-sm)' }}>Result:</h4>
                  <div className={`result-box ${result.status === 'simulated' ? 'simulated' : 'success'}`}>
                    {result.execution_mode === 'simulated' && (
                      <div className="badge badge-warning mb-2">
                        Simulated Response
                      </div>
                    )}
                    <p><strong>Status:</strong> {result.status}</p>
                    <p><strong>Message:</strong> {result.message || 'N/A'}</p>
                    <p><strong>Result:</strong></p>
                    <pre>{JSON.stringify(result.result, null, 2)}</pre>
                    {result.warning && (
                      <div className="alert alert-warning mt-2">
                        ⚠️ {result.warning}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="card mt-3">
        <div className="card-header">
          <h3 className="card-title">Getting Started</h3>
        </div>
        <div className="getting-started">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h4>Create a Flow in LangFlow</h4>
              <p>Visit <a href="http://localhost:7860" target="_blank" rel="noopener noreferrer">http://localhost:7860</a> to create your agent flow visually</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h4>Export as JSON</h4>
              <p>Export your flow as a JSON file from the LangFlow interface</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h4>Upload & Execute</h4>
              <p>Upload the JSON file here and execute it with your input</p>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .flows-list {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
          max-height: 400px;
          overflow-y: auto;
        }

        .flow-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          padding: var(--spacing-md);
          background: var(--accent-bg);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .flow-item:hover {
          border-color: var(--primary-color);
          box-shadow: var(--border-glow);
        }

        .flow-item.selected {
          border-color: var(--accent-color);
          background: var(--highlight-bg);
          box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        }

        .flow-icon {
          font-size: 2rem;
        }

        .flow-info {
          flex: 1;
        }

        .flow-name {
          font-weight: 700;
          color: var(--primary-color);
          margin-bottom: var(--spacing-xs);
        }

        .flow-meta {
          display: flex;
          gap: var(--spacing-sm);
          font-size: 0.85rem;
        }

        .result-container {
          margin-top: var(--spacing-lg);
        }

        .result-box {
          background: var(--accent-bg);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          padding: var(--spacing-md);
        }

        .result-box.simulated {
          border-color: var(--warning-color);
        }

        .result-box.success {
          border-color: var(--accent-color);
        }

        .result-box pre {
          background: var(--primary-bg);
          padding: var(--spacing-md);
          border-radius: 4px;
          overflow-x: auto;
          margin-top: var(--spacing-sm);
        }

        .getting-started {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);
        }

        .step {
          display: flex;
          gap: var(--spacing-md);
          align-items: flex-start;
        }

        .step-number {
          width: 40px;
          height: 40px;
          background: var(--primary-color);
          color: var(--primary-bg);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 900;
          font-size: 1.2rem;
          flex-shrink: 0;
        }

        .step-content h4 {
          margin: 0 0 var(--spacing-xs) 0;
          color: var(--primary-color);
        }

        .step-content p {
          margin: 0;
          color: var(--text-secondary);
        }

        .step-content a {
          color: var(--accent-color);
          text-decoration: none;
        }

        .step-content a:hover {
          text-decoration: underline;
        }

        .alert {
          padding: var(--spacing-md);
          border-radius: 8px;
          margin-bottom: var(--spacing-lg);
        }

        .alert-danger {
          background: rgba(255, 0, 85, 0.1);
          border: 1px solid var(--danger-color);
          color: var(--danger-color);
        }

        .alert-warning {
          background: rgba(255, 215, 0, 0.1);
          border: 1px solid var(--warning-color);
          color: var(--warning-color);
        }
      `}</style>
    </div>
  )
}

export default AgentBuilder
