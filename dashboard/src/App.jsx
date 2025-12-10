import React, { useState, useEffect, useRef } from 'react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [token, setToken] = useState(null);
  const [regSecret, setRegSecret] = useState('');
  const [agentId, setAgentId] = useState('');
  const [agents, setAgents] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [logs, setLogs] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [snapshotId, setSnapshotId] = useState('');
  const [targetAgentId, setTargetAgentId] = useState('');
  const [jobIdLookup, setJobIdLookup] = useState('');
  const [jobStatus, setJobStatus] = useState(null);
  const wsRef = useRef(null);
  const logsEndRef = useRef(null);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [token]);

  const connectWebSocket = () => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = API_BASE.replace('http://', '').replace('https://', '');
    const wsUrl = `${wsProtocol}//${wsHost}/ws${token ? '?token=' + token : ''}`;

    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLogs(prev => [...prev, { ...data, timestamp: new Date().toISOString() }]);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
      // Reconnect after 5 seconds
      setTimeout(connectWebSocket, 5000);
    };

    wsRef.current = ws;
  };

  const authenticate = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          registration_secret: regSecret,
          agent_id: agentId || null
        })
      });

      if (!response.ok) throw new Error('Authentication failed');

      const data = await response.json();
      setToken(data.token);
      alert('Token obtained successfully!');
    } catch (error) {
      alert('Authentication failed: ' + error.message);
    }
  };

  const loadAgents = async () => {
    if (!token) {
      alert('Please authenticate first');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/agents`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to load agents');

      const data = await response.json();
      setAgents(data);
    } catch (error) {
      console.error('Error loading agents:', error);
    }
  };

  const createRestoreJob = async () => {
    if (!token) {
      alert('Please authenticate first');
      return;
    }

    if (!snapshotId || !targetAgentId) {
      alert('Please fill in all fields');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/restore-jobs`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          snapshot_id: snapshotId,
          target_agent_id: targetAgentId
        })
      });

      if (!response.ok) throw new Error('Failed to create job');

      const job = await response.json();
      setJobs(prev => [...prev, job]);
      setJobIdLookup(job.id);
      alert(`Job created: ${job.id}`);
    } catch (error) {
      alert('Failed to create job: ' + error.message);
    }
  };

  const checkJobStatus = async () => {
    if (!token || !jobIdLookup) return;

    try {
      const response = await fetch(`${API_BASE}/restore-jobs/${jobIdLookup}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Job not found');

      const job = await response.json();
      setJobStatus(job);
    } catch (error) {
      alert('Failed to get job status: ' + error.message);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🛡️ FortFail Dashboard</h1>
        <div className="ws-status">
          <span className={`indicator ${wsConnected ? 'connected' : 'disconnected'}`}></span>
          {wsConnected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      <div className="container">
        <div className="grid">
          {/* Authentication */}
          <div className="card">
            <h2>🔐 Authentication</h2>
            <div className="form-group">
              <label>Registration Secret</label>
              <input
                type="password"
                value={regSecret}
                onChange={(e) => setRegSecret(e.target.value)}
                placeholder="Enter registration secret"
              />
            </div>
            <div className="form-group">
              <label>Agent ID (optional)</label>
              <input
                type="text"
                value={agentId}
                onChange={(e) => setAgentId(e.target.value)}
                placeholder="agent-001"
              />
            </div>
            <button onClick={authenticate}>Get Token</button>
            {token && <p className="success-text">✓ Token obtained</p>}
          </div>

          {/* Agents */}
          <div className="card">
            <h2>🤖 Agents</h2>
            <button onClick={loadAgents}>Refresh Agents</button>
            <div className="list">
              {agents.length === 0 ? (
                <p className="empty">No agents found</p>
              ) : (
                agents.map(agent => (
                  <div key={agent.id} className="list-item">
                    {agent.id}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Create Job */}
          <div className="card">
            <h2>🔄 Create Restore Job</h2>
            <div className="form-group">
              <label>Snapshot ID</label>
              <input
                type="text"
                value={snapshotId}
                onChange={(e) => setSnapshotId(e.target.value)}
                placeholder="snapshot-123"
              />
            </div>
            <div className="form-group">
              <label>Target Agent ID</label>
              <input
                type="text"
                value={targetAgentId}
                onChange={(e) => setTargetAgentId(e.target.value)}
                placeholder="agent-001"
              />
            </div>
            <button onClick={createRestoreJob}>Create Job</button>
          </div>

          {/* Job Status */}
          <div className="card">
            <h2>📊 Job Status</h2>
            <div className="form-group">
              <label>Job ID</label>
              <input
                type="text"
                value={jobIdLookup}
                onChange={(e) => setJobIdLookup(e.target.value)}
                placeholder="job-123"
              />
            </div>
            <button onClick={checkJobStatus}>Check Status</button>
            {jobStatus && (
              <div className="job-details">
                <div className="detail-row">
                  <span>Status:</span>
                  <span className={`status ${jobStatus.status}`}>{jobStatus.status}</span>
                </div>
                <div className="detail-row">
                  <span>Snapshot:</span>
                  <span>{jobStatus.snapshot_id}</span>
                </div>
                <div className="detail-row">
                  <span>Agent:</span>
                  <span>{jobStatus.target_agent_id}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Logs */}
        <div className="card logs-card">
          <h2>📋 Event Logs</h2>
          <div className="logs">
            {logs.map((log, idx) => (
              <div key={idx} className="log-entry">
                <span className="log-time">{new Date(log.timestamp).toLocaleTimeString()}</span>
                <span className="log-event">{log.event}</span>
                <span className="log-detail">{JSON.stringify(log)}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>

        {/* Jobs List */}
        <div className="card">
          <h2>📋 Recent Jobs</h2>
          <div className="list">
            {jobs.length === 0 ? (
              <p className="empty">No jobs created yet</p>
            ) : (
              jobs.map(job => (
                <div key={job.id} className="list-item">
                  <span>{job.id}</span>
                  <span className={`status ${job.status}`}>{job.status}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
