import { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Flow {
  name: string;
  size: number;
  modified: number;
}

function AgentBuilder() {
  const [flows, setFlows] = useState<Flow[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFlow, setSelectedFlow] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [runResult, setRunResult] = useState('');

  // Fetch flows from backend
  const fetchFlows = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/list_flows/`);
      const data = await response.json();
      setFlows(data.flows || []);
    } catch (error) {
      console.error('Error fetching flows:', error);
      setUploadStatus('Error connecting to backend. Ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlows();
  }, []);

  // Upload flow
  const handleFlowUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('flow_file', file);

    setUploadStatus('Uploading...');
    try {
      const response = await fetch(`${API_URL}/save_flow/`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      
      if (response.ok) {
        setUploadStatus(`✓ Flow "${data.flow_name}" saved successfully!`);
        fetchFlows(); // Refresh the list
      } else {
        setUploadStatus(`Error: ${data.detail || 'Upload failed'}`);
      }
    } catch (error) {
      console.error('Error uploading flow:', error);
      setUploadStatus('Error uploading flow. Check backend connection.');
    }
  };

  // Get flow details
  const handleGetFlow = async (flowName: string) => {
    try {
      const response = await fetch(`${API_URL}/get_flow/${flowName}`);
      const data = await response.json();
      
      if (response.ok) {
        setSelectedFlow(flowName);
        console.log('Flow data:', data.flow_data);
        alert(`Flow "${flowName}" loaded. Check console for details.`);
      } else {
        alert(`Error: ${data.detail || 'Failed to load flow'}`);
      }
    } catch (error) {
      console.error('Error getting flow:', error);
      alert('Error loading flow. Check backend connection.');
    }
  };

  // Run flow
  const handleRunFlow = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    const formData = new FormData(e.currentTarget);
    const userInput = formData.get('user_input') as string;
    const file = (document.getElementById('run-flow-file') as HTMLInputElement).files?.[0];
    
    if (!file || !userInput) {
      alert('Please select a flow file and provide input');
      return;
    }

    const runFormData = new FormData();
    runFormData.append('flow_file', file);
    runFormData.append('user_input', userInput);

    setRunResult('Running flow...');
    try {
      const response = await fetch(`${API_URL}/run_flow/`, {
        method: 'POST',
        body: runFormData,
      });
      const data = await response.json();
      
      if (response.ok) {
        setRunResult(JSON.stringify(data, null, 2));
      } else {
        setRunResult(`Error: ${data.detail || 'Execution failed'}`);
      }
    } catch (error) {
      console.error('Error running flow:', error);
      setRunResult('Error running flow. Check backend connection.');
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Agent Builder</h1>
        <p className="page-subtitle">Create and manage LangFlow agents</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <h2 className="card-title">Upload Flow</h2>
          <div className="file-upload">
            <input
              type="file"
              id="flow-upload"
              accept=".json"
              onChange={handleFlowUpload}
            />
            <label htmlFor="flow-upload">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📤</div>
              <div>Click to upload LangFlow JSON</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                Export your flow from LangFlow and upload here
              </div>
            </label>
          </div>
          {uploadStatus && (
            <div className="card-content" style={{ marginTop: '1rem', textAlign: 'center' }}>
              {uploadStatus}
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="card-title">Quick Start</h2>
          <div className="card-content">
            <ol style={{ lineHeight: '2', paddingLeft: '1.5rem' }}>
              <li>Open LangFlow at <a href="http://localhost:7860" target="_blank" style={{ color: 'var(--neon-cyan)' }}>localhost:7860</a></li>
              <li>Create or edit a workflow</li>
              <li>Export the flow as JSON</li>
              <li>Upload it here to save</li>
              <li>Test the flow below</li>
            </ol>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Saved Flows</h2>
        {loading ? (
          <div className="spinner"></div>
        ) : flows.length === 0 ? (
          <div className="card-content">No flows saved yet. Upload your first flow above!</div>
        ) : (
          <ul className="flow-list">
            {flows.map((flow) => (
              <li key={flow.name} className="flow-item">
                <div>
                  <div className="flow-name">{flow.name}</div>
                  <div className="flow-meta">
                    {(flow.size / 1024).toFixed(2)} KB • Modified {new Date(flow.modified * 1000).toLocaleDateString()}
                  </div>
                </div>
                <div>
                  <button
                    className="btn btn-secondary"
                    onClick={() => handleGetFlow(flow.name)}
                    style={{ marginRight: '0.5rem' }}
                  >
                    Load
                  </button>
                  <button className="btn btn-secondary">Delete</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card">
        <h2 className="card-title">Test Flow Execution</h2>
        <form onSubmit={handleRunFlow}>
          <div className="form-group">
            <label className="form-label">Select Flow File</label>
            <input
              type="file"
              id="run-flow-file"
              accept=".json"
              className="form-input"
              style={{ padding: '0.5rem' }}
            />
          </div>
          <div className="form-group">
            <label className="form-label">User Input</label>
            <textarea
              name="user_input"
              className="form-textarea"
              placeholder="Enter your input for the flow..."
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Run Flow
          </button>
        </form>
        {runResult && (
          <div className="card-content" style={{ marginTop: '1.5rem' }}>
            <h3 className="card-title">Result:</h3>
            <pre style={{
              background: 'var(--darker-bg)',
              padding: '1rem',
              borderRadius: '8px',
              overflow: 'auto',
              maxHeight: '300px',
              fontSize: '0.85rem'
            }}>
              {runResult}
            </pre>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="card-title">Backend Status</h2>
        <div className="card-content">
          <p><strong>API URL:</strong> {API_URL}</p>
          <p><strong>Connection:</strong> {flows.length > 0 || uploadStatus ? 'Connected ✓' : 'Checking...'}</p>
          <button
            className="btn btn-secondary"
            onClick={fetchFlows}
            style={{ marginTop: '1rem' }}
          >
            Refresh Flows
          </button>
        </div>
      </div>
    </div>
  );
}

export default AgentBuilder;
