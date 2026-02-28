import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Flow {
  name: string
  created: string
  size: number
}

const AgentBuilder = () => {
  const [flows, setFlows] = useState<Flow[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedFlow, setSelectedFlow] = useState<string | null>(null)
  const [userInput, setUserInput] = useState('')
  const [result, setResult] = useState<any>(null)
  
  // Load flows from backend
  useEffect(() => {
    loadFlows()
  }, [])
  
  const loadFlows = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get(`${API_URL}/list_flows/`)
      setFlows(response.data)
    } catch (err: any) {
      setError(err.message || 'Failed to load flows')
      console.error('Error loading flows:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleSaveFlow = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    
    setLoading(true)
    setError(null)
    try {
      const response = await axios.post(`${API_URL}/save_flow/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      alert(`Flow saved: ${response.data.message}`)
      loadFlows()
      e.currentTarget.reset()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to save flow')
      console.error('Error saving flow:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleRunFlow = async () => {
    if (!selectedFlow || !userInput) {
      alert('Please select a flow and enter input')
      return
    }
    
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const formData = new FormData()
      formData.append('flow_name', selectedFlow)
      formData.append('user_input', userInput)
      
      const response = await axios.post(`${API_URL}/run_flow/`, formData)
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to run flow')
      console.error('Error running flow:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleViewFlow = async (flowName: string) => {
    try {
      const response = await axios.get(`${API_URL}/get_flow/${flowName}`)
      console.log('Flow data:', response.data)
      alert(`Flow "${flowName}" loaded. Check console for details.`)
    } catch (err: any) {
      alert(`Error: ${err.response?.data?.detail || err.message}`)
    }
  }
  
  return (
    <div className="page-container fade-in">
      <h1>Agent Builder</h1>
      <p style={{ marginBottom: '2rem' }}>
        Create, manage, and execute LangFlow agents.
      </p>
      
      {error && (
        <div className="card" style={{ background: 'rgba(255, 0, 102, 0.1)', borderColor: 'var(--error)' }}>
          <strong>Error:</strong> {error}
        </div>
      )}
      
      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Save New Flow</h3>
          </div>
          
          <form onSubmit={handleSaveFlow}>
            <div className="input-group">
              <label className="input-label">Flow Name</label>
              <input 
                type="text" 
                name="flow_name"
                className="input" 
                placeholder="my_agent_flow"
                required
              />
            </div>
            
            <div className="input-group">
              <label className="input-label">Upload Flow JSON</label>
              <input 
                type="file" 
                name="flow_json"
                className="input" 
                accept=".json"
                required
              />
              <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
                Export your flow from LangFlow (port 7860) and upload the JSON file here.
              </p>
            </div>
            
            <button 
              type="submit" 
              className="btn"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Flow'}
            </button>
          </form>
          
          <div style={{ marginTop: '2rem', padding: '1rem', background: 'var(--bg-tertiary)', borderRadius: '4px' }}>
            <h4 style={{ marginBottom: '0.5rem' }}>Quick Links</h4>
            <a 
              href="http://localhost:7860" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}
            >
              Open LangFlow UI ↗
            </a>
          </div>
        </div>
        
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Run Flow</h3>
          </div>
          
          <div className="input-group">
            <label className="input-label">Select Flow</label>
            <select 
              className="select"
              value={selectedFlow || ''}
              onChange={(e) => setSelectedFlow(e.target.value)}
              disabled={loading}
            >
              <option value="">-- Select a flow --</option>
              {flows.map(flow => (
                <option key={flow.name} value={flow.name}>
                  {flow.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="input-group">
            <label className="input-label">User Input</label>
            <textarea 
              className="textarea"
              placeholder="Enter your input for the flow..."
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              disabled={loading}
            />
          </div>
          
          <button 
            className="btn"
            onClick={handleRunFlow}
            disabled={loading || !selectedFlow || !userInput}
          >
            {loading ? 'Running...' : 'Run Flow'}
          </button>
          
          {result && (
            <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-tertiary)', borderRadius: '4px' }}>
              <h4 style={{ marginBottom: '1rem' }}>Result:</h4>
              {result.simulated && (
                <div className="badge badge-warning" style={{ marginBottom: '1rem' }}>
                  Simulated Response
                </div>
              )}
              <div className={`badge ${result.success ? 'badge-success' : 'badge-error'}`}>
                {result.success ? 'Success' : 'Failed'}
              </div>
              <pre style={{ 
                marginTop: '1rem',
                padding: '1rem',
                background: 'var(--bg-primary)',
                borderRadius: '4px',
                overflow: 'auto',
                fontSize: '0.85rem',
                border: '1px solid var(--border-color)'
              }}>
                {JSON.stringify(result.result || result.error, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <div className="flex-between">
            <h3 className="card-title">Saved Flows</h3>
            <button 
              className="btn btn-secondary" 
              onClick={loadFlows}
              disabled={loading}
              style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}
            >
              Refresh
            </button>
          </div>
        </div>
        
        {loading && flows.length === 0 ? (
          <div className="loading-container">
            <div className="loading"></div>
          </div>
        ) : flows.length === 0 ? (
          <p style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>
            No flows saved yet. Create one in LangFlow and save it above.
          </p>
        ) : (
          <div className="grid grid-3">
            {flows.map(flow => (
              <div 
                key={flow.name}
                className="card"
                style={{ background: 'var(--bg-tertiary)' }}
              >
                <h4 style={{ marginBottom: '0.5rem' }}>{flow.name}</h4>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  Created: {new Date(flow.created).toLocaleDateString()}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                  Size: {(flow.size / 1024).toFixed(2)} KB
                </div>
                <div className="flex-gap" style={{ gap: '0.5rem' }}>
                  <button 
                    className="btn"
                    style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}
                    onClick={() => handleViewFlow(flow.name)}
                  >
                    View
                  </button>
                  <button 
                    className="btn btn-secondary"
                    style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}
                    onClick={() => setSelectedFlow(flow.name)}
                  >
                    Select
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Backend Connection</h3>
        </div>
        <div className="grid grid-2">
          <div>
            <div className="input-label">API Endpoint</div>
            <div style={{ 
              padding: '0.75rem', 
              background: 'var(--bg-tertiary)', 
              borderRadius: '4px',
              fontFamily: 'monospace',
              fontSize: '0.9rem'
            }}>
              {API_URL}
            </div>
          </div>
          <div>
            <div className="input-label">Status</div>
            <div className="flex-gap" style={{ marginTop: '0.75rem' }}>
              <span className="badge badge-success">Connected</span>
              <a 
                href={`${API_URL}/docs`}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'var(--accent-primary)' }}
              >
                View API Docs ↗
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AgentBuilder
