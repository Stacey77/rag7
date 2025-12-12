import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import ChatInterface from './ChatInterface';
import FloatingBot from './FloatingBot';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Dashboard() {
  const [activeView, setActiveView] = useState('chat');
  const [connected, setConnected] = useState(false);
  const [integrations, setIntegrations] = useState([]);
  const [functions, setFunctions] = useState([]);
  const [stats, setStats] = useState({
    totalMessages: 0,
    activeSessions: 0,
    functionsExecuted: 0
  });

  useEffect(() => {
    // Check API health
    fetch(`${API_URL}/health`)
      .then(res => res.json())
      .then(data => {
        setConnected(data.agent_ready);
      })
      .catch(err => {
        console.error('Health check failed:', err);
        setConnected(false);
      });

    // Load integrations
    fetch(`${API_URL}/integrations`)
      .then(res => res.json())
      .then(data => {
        setIntegrations(data);
      })
      .catch(err => {
        console.error('Failed to load integrations:', err);
      });

    // Load functions
    fetch(`${API_URL}/functions`)
      .then(res => res.json())
      .then(data => {
        setFunctions(data);
      })
      .catch(err => {
        console.error('Failed to load functions:', err);
      });
  }, []);

  const renderView = () => {
    switch (activeView) {
      case 'chat':
        return <ChatInterface connected={connected} integrations={integrations} />;
      case 'integrations':
        return <IntegrationsView integrations={integrations} functions={functions} />;
      case 'analytics':
        return <AnalyticsView stats={stats} />;
      case 'settings':
        return <SettingsView />;
      default:
        return <ChatInterface connected={connected} integrations={integrations} />;
    }
  };

  return (
    <>
      <div className="dashboard">
        {/* Sidebar Navigation */}
        <aside className="dashboard-sidebar">
          <div className="sidebar-header">
            <div className="logo">
              <span className="logo-icon">🤖</span>
              <span className="logo-text">RAG7</span>
            </div>
            <div className={`status-badge ${connected ? 'online' : 'offline'}`}>
              {connected ? '● Online' : '○ Offline'}
            </div>
          </div>

          <nav className="sidebar-nav">
            <button
              className={`nav-item ${activeView === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveView('chat')}
            >
              <span className="nav-icon">💬</span>
              <span className="nav-label">Chat</span>
            </button>

            <button
              className={`nav-item ${activeView === 'integrations' ? 'active' : ''}`}
              onClick={() => setActiveView('integrations')}
            >
              <span className="nav-icon">🔌</span>
              <span className="nav-label">Integrations</span>
              {integrations.length > 0 && (
                <span className="nav-badge">
                  {integrations.filter(i => i.healthy).length}/{integrations.length}
                </span>
              )}
            </button>

            <button
              className={`nav-item ${activeView === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveView('analytics')}
            >
              <span className="nav-icon">📊</span>
              <span className="nav-label">Analytics</span>
            </button>

            <button
              className={`nav-item ${activeView === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveView('settings')}
            >
              <span className="nav-icon">⚙️</span>
              <span className="nav-label">Settings</span>
            </button>
          </nav>

          <div className="sidebar-footer">
            <div className="quick-stats">
              <div className="stat-item">
                <span className="stat-value">{integrations.filter(i => i.healthy).length}</span>
                <span className="stat-label">Active</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{functions.length}</span>
                <span className="stat-label">Functions</span>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="dashboard-main">
          <header className="dashboard-header">
            <h1 className="page-title">
              {activeView === 'chat' && '💬 Conversational AI'}
              {activeView === 'integrations' && '🔌 Integrations'}
              {activeView === 'analytics' && '📊 Analytics'}
              {activeView === 'settings' && '⚙️ Settings'}
            </h1>
            <div className="header-actions">
              <button className="btn-icon" title="Notifications">
                🔔
              </button>
              <button className="btn-icon" title="Help">
                ❓
              </button>
            </div>
          </header>

          <div className="dashboard-content">
            {renderView()}
          </div>
        </main>
      </div>

      {/* Floating Bot - Works independently */}
      <FloatingBot />
    </>
  );
}

// Integrations View Component
function IntegrationsView({ integrations, functions }) {
  return (
    <div className="integrations-view">
      <div className="view-header">
        <h2>Connected Integrations</h2>
        <p>Manage your external service connections</p>
      </div>

      <div className="integrations-grid">
        {integrations.map(integration => (
          <div key={integration.name} className={`integration-card ${integration.healthy ? 'healthy' : 'unhealthy'}`}>
            <div className="integration-header">
              <div className="integration-icon">
                {integration.name === 'slack' && '📱'}
                {integration.name === 'gmail' && '📧'}
                {integration.name === 'notion' && '📝'}
              </div>
              <div className="integration-info">
                <h3>{integration.name.charAt(0).toUpperCase() + integration.name.slice(1)}</h3>
                <span className={`status ${integration.healthy ? 'healthy' : 'unhealthy'}`}>
                  {integration.healthy ? '● Connected' : '○ Not Connected'}
                </span>
              </div>
            </div>
            <div className="integration-stats">
              <div className="stat">
                <span className="stat-label">Functions</span>
                <span className="stat-value">{integration.functions_count}</span>
              </div>
            </div>
            <div className="integration-functions">
              <h4>Available Functions:</h4>
              <ul>
                {functions
                  .filter(f => f.integration === integration.name)
                  .map((func, idx) => (
                    <li key={idx}>
                      <span className="function-name">{func.name}</span>
                      <span className="function-desc">{func.description}</span>
                    </li>
                  ))}
              </ul>
            </div>
          </div>
        ))}
      </div>

      {integrations.length === 0 && (
        <div className="empty-state">
          <p>No integrations configured yet.</p>
          <p>Add your API keys to .env to enable integrations.</p>
        </div>
      )}
    </div>
  );
}

// Analytics View Component
function AnalyticsView({ stats }) {
  return (
    <div className="analytics-view">
      <div className="view-header">
        <h2>Usage Analytics</h2>
        <p>Monitor your AI agent performance</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">💬</div>
          <div className="stat-content">
            <h3>Total Messages</h3>
            <p className="stat-number">{stats.totalMessages}</p>
            <span className="stat-change">+0% from last week</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>Active Sessions</h3>
            <p className="stat-number">{stats.activeSessions}</p>
            <span className="stat-change">Currently active</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <h3>Functions Executed</h3>
            <p className="stat-number">{stats.functionsExecuted}</p>
            <span className="stat-change">+0% from last week</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>Success Rate</h3>
            <p className="stat-number">100%</p>
            <span className="stat-change">All systems operational</span>
          </div>
        </div>
      </div>

      <div className="analytics-placeholder">
        <p>📊 Advanced analytics coming soon...</p>
        <p>Track conversation metrics, function usage, and performance over time.</p>
      </div>
    </div>
  );
}

// Settings View Component
function SettingsView() {
  return (
    <div className="settings-view">
      <div className="view-header">
        <h2>Settings</h2>
        <p>Configure your AI agent platform</p>
      </div>

      <div className="settings-sections">
        <div className="settings-section">
          <h3>🔑 API Configuration</h3>
          <div className="setting-item">
            <label>OpenAI API Key</label>
            <input type="password" placeholder="sk-..." disabled />
            <span className="setting-help">Set in .env file</span>
          </div>
          <div className="setting-item">
            <label>OpenAI Model</label>
            <select disabled>
              <option>gpt-4</option>
              <option>gpt-3.5-turbo</option>
            </select>
            <span className="setting-help">Configure in .env file</span>
          </div>
        </div>

        <div className="settings-section">
          <h3>🎨 Interface</h3>
          <div className="setting-item">
            <label>
              <input type="checkbox" defaultChecked />
              Enable floating bot widget
            </label>
          </div>
          <div className="setting-item">
            <label>
              <input type="checkbox" defaultChecked />
              Show function execution details
            </label>
          </div>
        </div>

        <div className="settings-section">
          <h3>📝 Documentation</h3>
          <div className="doc-links">
            <a href="/README.md" target="_blank">📖 README</a>
            <a href="/QUICKSTART.md" target="_blank">🚀 Quick Start Guide</a>
            <a href="/DEVELOPMENT.md" target="_blank">🛠️ Development Guide</a>
            <a href={`${API_URL}/docs`} target="_blank">📚 API Documentation</a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
