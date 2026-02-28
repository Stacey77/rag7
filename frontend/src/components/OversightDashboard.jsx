import { useState, useEffect } from 'react';
import { auth, authHeaders } from '../lib/auth';
import { OversightWebSocket } from '../lib/websocket';

export default function OversightDashboard({ user, onLogout }) {
  const [tasks, setTasks] = useState([]);
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({ total_tasks: 0, active_agents: 0, escalations_today: 0 });
  const [ws, setWs] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Load initial data
    loadStats();
    loadTasks();

    // Connect to WebSocket for real-time updates
    const token = auth.getToken();
    if (token) {
      const websocket = new OversightWebSocket(token);
      
      websocket.on('connected', () => {
        setConnected(true);
      });
      
      websocket.on('disconnected', () => {
        setConnected(false);
      });
      
      websocket.on('message', (data) => {
        handleWebSocketMessage(data);
      });
      
      websocket.connect();
      setWs(websocket);

      // Keep connection alive
      const pingInterval = setInterval(() => {
        websocket.ping();
      }, 30000);

      return () => {
        clearInterval(pingInterval);
        websocket.disconnect();
      };
    }
  }, []);

  const loadStats = async () => {
    try {
      const response = await fetch('/api/admin/stats', {
        headers: authHeaders(),
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (e) {
      console.error('Failed to load stats:', e);
    }
  };

  const loadTasks = async () => {
    try {
      const response = await fetch('/api/decisions/tasks', {
        headers: authHeaders(),
      });
      if (response.ok) {
        const data = await response.json();
        setTasks(data.tasks || []);
      }
    } catch (e) {
      console.error('Failed to load tasks:', e);
    }
  };

  const handleWebSocketMessage = (data) => {
    // Add event to event log
    setEvents(prev => [{
      ...data,
      timestamp: new Date().toISOString()
    }, ...prev].slice(0, 50)); // Keep last 50 events

    // Update stats or tasks based on event type
    if (data.event_type === 'task_created' || data.event_type === 'task_escalated') {
      loadTasks();
      loadStats();
    }
  };

  const handleEscalate = async (taskId) => {
    if (!confirm('Are you sure you want to escalate this task?')) {
      return;
    }

    try {
      const response = await fetch('/api/decisions/escalate', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({
          task_id: taskId,
          reason: 'Manual escalation from oversight dashboard'
        }),
      });

      if (response.ok) {
        alert('Task escalated successfully');
        loadTasks();
      } else {
        alert('Failed to escalate task');
      }
    } catch (e) {
      console.error('Failed to escalate:', e);
      alert('Error escalating task');
    }
  };

  const handleLogout = async () => {
    await auth.logout();
    onLogout();
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Agentic Oversight Dashboard</h1>
          <p style={styles.subtitle}>
            Logged in as: {user.name || user.user_id} ({user.roles.join(', ')})
            <span style={{...styles.badge, backgroundColor: connected ? '#28a745' : '#dc3545'}}>
              {connected ? '● Connected' : '● Disconnected'}
            </span>
          </p>
        </div>
        <button onClick={handleLogout} style={styles.logoutButton}>
          Logout
        </button>
      </header>

      {/* Stats */}
      <div style={styles.stats}>
        <div style={styles.statCard}>
          <div style={styles.statLabel}>Total Tasks</div>
          <div style={styles.statValue}>{stats.total_tasks}</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statLabel}>Active Agents</div>
          <div style={styles.statValue}>{stats.active_agents}</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statLabel}>Escalations Today</div>
          <div style={styles.statValue}>{stats.escalations_today}</div>
        </div>
      </div>

      <div style={styles.content}>
        {/* Tasks Panel */}
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>Recent Tasks</h2>
          <div style={styles.taskList}>
            {tasks.length === 0 ? (
              <p style={styles.emptyMessage}>No tasks to display</p>
            ) : (
              tasks.map(task => (
                <div key={task.task_id} style={styles.taskItem}>
                  <div>
                    <strong>Task #{task.task_id}</strong> - {task.state}
                    <br />
                    <span style={styles.taskMeta}>Type: {task.task_type}</span>
                  </div>
                  {auth.canEscalate() && task.state !== 'escalated' && (
                    <button 
                      onClick={() => handleEscalate(task.task_id)}
                      style={styles.escalateButton}
                    >
                      Escalate
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Events Panel */}
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>Event Stream</h2>
          <div style={styles.eventList}>
            {events.length === 0 ? (
              <p style={styles.emptyMessage}>No events yet</p>
            ) : (
              events.map((event, idx) => (
                <div key={idx} style={styles.eventItem}>
                  <div style={styles.eventType}>{event.event_type || event.type}</div>
                  <div style={styles.eventTime}>
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: 'white',
    padding: '1.5rem 2rem',
    borderBottom: '1px solid #ddd',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    margin: '0',
    fontSize: '1.5rem',
    color: '#333',
  },
  subtitle: {
    margin: '0.25rem 0 0 0',
    color: '#666',
    fontSize: '0.9rem',
  },
  badge: {
    marginLeft: '1rem',
    padding: '0.25rem 0.5rem',
    borderRadius: '4px',
    color: 'white',
    fontSize: '0.75rem',
    fontWeight: '500',
  },
  logoutButton: {
    padding: '0.5rem 1rem',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.9rem',
  },
  stats: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1rem',
    padding: '1.5rem 2rem',
  },
  statCard: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  statLabel: {
    fontSize: '0.9rem',
    color: '#666',
    marginBottom: '0.5rem',
  },
  statValue: {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#333',
  },
  content: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '1.5rem',
    padding: '0 2rem 2rem 2rem',
  },
  panel: {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    overflow: 'hidden',
  },
  panelTitle: {
    margin: '0',
    padding: '1rem 1.5rem',
    fontSize: '1.1rem',
    borderBottom: '1px solid #eee',
    color: '#333',
  },
  taskList: {
    maxHeight: '400px',
    overflowY: 'auto',
  },
  taskItem: {
    padding: '1rem 1.5rem',
    borderBottom: '1px solid #eee',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  taskMeta: {
    fontSize: '0.85rem',
    color: '#666',
  },
  escalateButton: {
    padding: '0.4rem 0.8rem',
    backgroundColor: '#ffc107',
    color: '#333',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.85rem',
    fontWeight: '500',
  },
  eventList: {
    maxHeight: '400px',
    overflowY: 'auto',
  },
  eventItem: {
    padding: '0.75rem 1.5rem',
    borderBottom: '1px solid #eee',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  eventType: {
    fontSize: '0.9rem',
    color: '#333',
  },
  eventTime: {
    fontSize: '0.8rem',
    color: '#999',
  },
  emptyMessage: {
    padding: '2rem',
    textAlign: 'center',
    color: '#999',
  },
};
