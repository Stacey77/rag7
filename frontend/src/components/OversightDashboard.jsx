import { useState, useEffect, useRef, useCallback } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'

const API_BASE = '/api/v1'

// Role constants matching backend
const ROLES = {
  ADMIN: 'admin',
  REVIEWER: 'reviewer',
  AGENT_MANAGER: 'agent_manager',
  VIEWER: 'viewer'
}

function OversightDashboard() {
  const { user, hasRole, getAuthHeader, token } = useAuth()
  const [tasks, setTasks] = useState([])
  const [events, setEvents] = useState([])
  const [stats, setStats] = useState(null)
  const [escalations, setEscalations] = useState([])
  const [wsConnected, setWsConnected] = useState(false)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/decisions/tasks`, {
        headers: getAuthHeader()
      })
      if (response.ok) {
        const data = await response.json()
        setTasks(data.tasks || [])
      }
    } catch (err) {
      console.error('Failed to fetch tasks:', err)
    }
  }, [getAuthHeader])

  // Fetch events
  const fetchEvents = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/decisions/events?limit=50`, {
        headers: getAuthHeader()
      })
      if (response.ok) {
        const data = await response.json()
        setEvents(data.events || [])
      }
    } catch (err) {
      console.error('Failed to fetch events:', err)
    }
  }, [getAuthHeader])

  // Fetch stats (admin/agent_manager only)
  const fetchStats = useCallback(async () => {
    if (!hasRole([ROLES.ADMIN, ROLES.AGENT_MANAGER])) return
    
    try {
      const response = await fetch(`${API_BASE}/admin/stats`, {
        headers: getAuthHeader()
      })
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }, [getAuthHeader, hasRole])

  // Fetch escalations (reviewer/admin only)
  const fetchEscalations = useCallback(async () => {
    if (!hasRole([ROLES.ADMIN, ROLES.REVIEWER])) return
    
    try {
      const response = await fetch(`${API_BASE}/decisions/escalations`, {
        headers: getAuthHeader()
      })
      if (response.ok) {
        const data = await response.json()
        setEscalations(data.escalations || [])
      }
    } catch (err) {
      console.error('Failed to fetch escalations:', err)
    }
  }, [getAuthHeader, hasRole])

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!token) return

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${API_BASE}/oversight/ws?token=${token}`
    
    const connect = () => {
      try {
        wsRef.current = new WebSocket(wsUrl)
        
        wsRef.current.onopen = () => {
          setWsConnected(true)
          setError(null)
        }
        
        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            handleWebSocketMessage(data)
          } catch (err) {
            console.error('Failed to parse WS message:', err)
          }
        }
        
        wsRef.current.onclose = () => {
          setWsConnected(false)
          // Reconnect after 3 seconds
          setTimeout(connect, 3000)
        }
        
        wsRef.current.onerror = (err) => {
          console.error('WebSocket error:', err)
          setError('WebSocket connection failed')
        }
      } catch (err) {
        console.error('Failed to connect WebSocket:', err)
      }
    }

    connect()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [token])

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'connected':
        console.log('WebSocket connected:', data)
        break
      case 'event':
      case 'task_state_changed':
        // Refresh data on events
        fetchTasks()
        fetchEvents()
        fetchEscalations()
        break
      default:
        console.log('WebSocket message:', data)
    }
  }

  // Initial data fetch
  useEffect(() => {
    fetchTasks()
    fetchEvents()
    fetchStats()
    fetchEscalations()
  }, [fetchTasks, fetchEvents, fetchStats, fetchEscalations])

  // Override task (reviewer/admin only)
  const handleOverride = async (taskId) => {
    const reason = prompt('Enter reason for override:')
    if (!reason) return

    try {
      const response = await fetch(`${API_BASE}/decisions/task/${taskId}/override`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          reason,
          new_decision: 'manual_override',
          metadata: { overridden_at: new Date().toISOString() }
        })
      })

      if (response.ok) {
        fetchTasks()
        fetchEvents()
        alert('Override successful')
      } else {
        const data = await response.json()
        alert(`Override failed: ${data.detail}`)
      }
    } catch (err) {
      alert(`Override failed: ${err.message}`)
    }
  }

  // Escalate task
  const handleEscalate = async (taskId) => {
    const reason = prompt('Enter reason for escalation:')
    if (!reason) return

    try {
      const response = await fetch(`${API_BASE}/decisions/task/${taskId}/escalate?reason=${encodeURIComponent(reason)}`, {
        method: 'POST',
        headers: getAuthHeader()
      })

      if (response.ok) {
        fetchTasks()
        fetchEvents()
        fetchEscalations()
        alert('Escalation successful')
      } else {
        const data = await response.json()
        alert(`Escalation failed: ${data.detail}`)
      }
    } catch (err) {
      alert(`Escalation failed: ${err.message}`)
    }
  }

  // Send WebSocket action
  const sendWsAction = (action, taskId, data = {}) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'action',
        action,
        task_id: taskId,
        data
      }))
    }
  }

  const getStateBadgeClass = (state) => {
    switch (state) {
      case 'completed':
      case 'verified':
        return 'badge-success'
      case 'failed':
      case 'escalated':
        return 'badge-danger'
      case 'in_progress':
      case 'acked':
        return 'badge-info'
      default:
        return 'badge-warning'
    }
  }

  return (
    <main className="main">
      {error && <div className="alert alert-danger">{error}</div>}
      
      {/* Connection Status */}
      <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span style={{ 
          width: 10, 
          height: 10, 
          borderRadius: '50%', 
          background: wsConnected ? '#16a34a' : '#dc2626'
        }} />
        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
          {wsConnected ? 'Connected to real-time updates' : 'Disconnected'}
        </span>
      </div>

      {/* Stats Cards (Admin/Agent Manager only) */}
      {stats && hasRole([ROLES.ADMIN, ROLES.AGENT_MANAGER]) && (
        <div className="grid grid-cols-4" style={{ marginBottom: '1.5rem' }}>
          <div className="stat-card">
            <div className="stat-value">{stats.tasks?.total || 0}</div>
            <div className="stat-label">Total Tasks</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.tasks?.escalated || 0}</div>
            <div className="stat-label">Escalated</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.agents?.available || 0} / {stats.agents?.total || 0}</div>
            <div className="stat-label">Agents Available</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.models?.active || 0}</div>
            <div className="stat-label">Active Models</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2">
        {/* Tasks Panel */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Tasks</h2>
            <button className="btn btn-outline" onClick={fetchTasks}>
              Refresh
            </button>
          </div>
          
          {tasks.length === 0 ? (
            <p style={{ color: '#6b7280' }}>No tasks found</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>State</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map(task => (
                  <tr key={task.id}>
                    <td>{task.title}</td>
                    <td>{task.task_type}</td>
                    <td>
                      <span className={`badge ${getStateBadgeClass(task.state)}`}>
                        {task.state}
                      </span>
                    </td>
                    <td>
                      {/* Override button - Reviewer/Admin only */}
                      {hasRole([ROLES.REVIEWER, ROLES.ADMIN]) && (
                        <button 
                          className="btn btn-outline" 
                          style={{ marginRight: '0.5rem', padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                          onClick={() => handleOverride(task.id)}
                        >
                          Override
                        </button>
                      )}
                      
                      {/* Escalate button - Agent Manager/Reviewer/Admin */}
                      {hasRole([ROLES.AGENT_MANAGER, ROLES.REVIEWER, ROLES.ADMIN]) && task.state !== 'escalated' && (
                        <button 
                          className="btn btn-danger" 
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                          onClick={() => handleEscalate(task.id)}
                        >
                          Escalate
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Events Panel */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent Events</h2>
            <button className="btn btn-outline" onClick={fetchEvents}>
              Refresh
            </button>
          </div>
          
          {events.length === 0 ? (
            <p style={{ color: '#6b7280' }}>No events found</p>
          ) : (
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {events.slice(0, 20).map(event => (
                <div 
                  key={event.id} 
                  style={{ 
                    padding: '0.75rem', 
                    borderBottom: '1px solid #e5e7eb',
                    fontSize: '0.875rem'
                  }}
                >
                  <div style={{ fontWeight: 500 }}>{event.event_type}</div>
                  <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>
                    {event.entity_type} / {event.entity_id}
                  </div>
                  <div style={{ color: '#9ca3af', fontSize: '0.75rem' }}>
                    {new Date(event.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Escalations Panel (Reviewer/Admin only) */}
      {hasRole([ROLES.REVIEWER, ROLES.ADMIN]) && (
        <div className="card" style={{ marginTop: '1rem' }}>
          <div className="card-header">
            <h2 className="card-title">⚠️ Escalated Tasks</h2>
            <button className="btn btn-outline" onClick={fetchEscalations}>
              Refresh
            </button>
          </div>
          
          {escalations.length === 0 ? (
            <p style={{ color: '#6b7280' }}>No escalated tasks</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Priority</th>
                  <th>Retries</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {escalations.map(task => (
                  <tr key={task.id}>
                    <td>{task.title}</td>
                    <td>{task.task_type}</td>
                    <td>{task.priority}</td>
                    <td>{task.retry_count}</td>
                    <td>
                      <button 
                        className="btn btn-primary" 
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                        onClick={() => handleOverride(task.id)}
                      >
                        Resolve
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </main>
  )
}

export default OversightDashboard
