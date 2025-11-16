import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function AgentBuilder() {
  const [flows, setFlows] = useState<string[]>([])
  const [selectedFlow, setSelectedFlow] = useState<string | null>(null)
  const [flowName, setFlowName] = useState('')
  const [flowData, setFlowData] = useState('')
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  useEffect(() => {
    fetchFlows()
  }, [])

  const fetchFlows = async () => {
    try {
      const response = await fetch(`${API_URL}/list_flows/`)
      const data = await response.json()
      setFlows(data.flows || [])
    } catch (err) {
      console.error('Failed to fetch flows:', err)
    }
  }

  const handleLoadFlow = async () => {
    if (!selectedFlow) return

    try {
      const response = await fetch(`${API_URL}/get_flow/${selectedFlow}`)
      const data = await response.json()
      setFlowName(selectedFlow)
      setFlowData(JSON.stringify(data.flow_data, null, 2))
      setMessage({ type: 'success', text: `Loaded flow: ${selectedFlow}` })
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load flow' })
    }
  }

  const handleSaveFlow = async () => {
    if (!flowName.trim() || !flowData.trim()) {
      setMessage({ type: 'error', text: 'Please provide both flow name and data' })
      return
    }

    try {
      const parsedFlowData = JSON.parse(flowData)
      
      const response = await fetch(`${API_URL}/save_flow/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flow_name: flowName,
          flow_data: parsedFlowData,
        }),
      })

      if (response.ok) {
        setMessage({ type: 'success', text: `Flow "${flowName}" saved successfully!` })
        fetchFlows()
      } else {
        setMessage({ type: 'error', text: 'Failed to save flow' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Invalid JSON format' })
    }
  }

  const handleRunFlow = async () => {
    if (!flowName.trim()) {
      setMessage({ type: 'error', text: 'Please specify a flow name' })
      return
    }

    try {
      const response = await fetch(`${API_URL}/run_flow/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flow_name: flowName,
          input_data: { message: 'Test message' },
        }),
      })

      const data = await response.json()
      
      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: `Flow executed! Result: ${JSON.stringify(data.result, null, 2)}` 
        })
      } else {
        setMessage({ type: 'error', text: 'Flow execution failed' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to execute flow' })
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Agent Builder</h1>
        <p className="page-description">
          Create and manage LangFlow AI agent configurations
        </p>
      </div>

      {message && (
        <div 
          className="card mb-3" 
          style={{ 
            backgroundColor: message.type === 'success' 
              ? 'rgba(16, 185, 129, 0.1)' 
              : 'rgba(239, 68, 68, 0.1)',
            borderColor: message.type === 'success' 
              ? 'var(--success-color)' 
              : 'var(--error-color)'
          }}
        >
          <div 
            className="card-content" 
            style={{ 
              color: message.type === 'success' 
                ? 'var(--success-color)' 
                : 'var(--error-color)' 
            }}
          >
            {message.type === 'success' ? '✅' : '⚠️'} {message.text}
          </div>
        </div>
      )}

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Load Existing Flow</h2>
          </div>
          <div className="card-content">
            <div className="form-group">
              <label className="form-label">Select Flow</label>
              <select 
                className="form-input" 
                value={selectedFlow || ''} 
                onChange={(e) => setSelectedFlow(e.target.value)}
              >
                <option value="">-- Choose a flow --</option>
                {flows.map((flow) => (
                  <option key={flow} value={flow}>
                    {flow}
                  </option>
                ))}
              </select>
            </div>
            <button 
              className="btn btn-primary" 
              onClick={handleLoadFlow}
              disabled={!selectedFlow}
            >
              📥 Load Flow
            </button>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Quick Actions</h2>
          </div>
          <div className="card-content">
            <p className="mb-2 text-muted">Access LangFlow visual editor to create flows:</p>
            <a 
              href="http://localhost:7860" 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn btn-primary"
              style={{ textDecoration: 'none', display: 'inline-block' }}
            >
              🚀 Open LangFlow Editor
            </a>
            <p className="mt-2 text-muted" style={{ fontSize: '0.875rem' }}>
              Design your flow visually, then export the JSON and paste it below.
            </p>
          </div>
        </div>
      </div>

      <div className="card mt-3">
        <div className="card-header">
          <h2 className="card-title">Flow Configuration</h2>
        </div>
        <div className="card-content">
          <div className="form-group">
            <label className="form-label">Flow Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., my_chatbot_flow"
              value={flowName}
              onChange={(e) => setFlowName(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Flow Data (JSON)</label>
            <textarea
              className="form-textarea"
              placeholder='{"nodes": [], "edges": []}'
              value={flowData}
              onChange={(e) => setFlowData(e.target.value)}
              style={{ minHeight: '300px', fontFamily: 'monospace' }}
            />
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn btn-primary" onClick={handleSaveFlow}>
              💾 Save Flow
            </button>
            <button className="btn btn-secondary" onClick={handleRunFlow}>
              ▶️ Test Run
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={() => {
                setFlowName('')
                setFlowData('')
                setMessage(null)
              }}
            >
              🗑️ Clear
            </button>
          </div>
        </div>
      </div>

      <div className="card mt-3">
        <div className="card-header">
          <h2 className="card-title">Help & Documentation</h2>
        </div>
        <div className="card-content">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>
            How to Create a Flow:
          </h3>
          <ol style={{ paddingLeft: '1.5rem', color: 'var(--text-muted)', lineHeight: 1.8 }}>
            <li>Open the LangFlow visual editor (button above)</li>
            <li>Design your agent flow using the drag-and-drop interface</li>
            <li>Add components like LLMs, chains, tools, and memory</li>
            <li>Connect components by dragging between ports</li>
            <li>Export the flow as JSON from LangFlow</li>
            <li>Paste the JSON into the "Flow Data" field above</li>
            <li>Give your flow a name and click "Save Flow"</li>
            <li>Test your flow with "Test Run"</li>
          </ol>

          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginTop: '1.5rem', marginBottom: '0.75rem' }}>
            Example Flow Structure:
          </h3>
          <pre style={{ 
            backgroundColor: 'var(--surface-light)', 
            padding: '1rem', 
            borderRadius: '0.375rem',
            overflow: 'auto',
            fontSize: '0.875rem'
          }}>
{`{
  "nodes": [
    {
      "id": "1",
      "type": "LLMChain",
      "data": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
      }
    }
  ],
  "edges": []
}`}
          </pre>
        </div>
      </div>
    </div>
  )
}

export default AgentBuilder
