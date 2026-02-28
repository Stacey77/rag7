import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

function Sidebar() {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title glow">RAGAMUFFIN</h2>
        <p className="sidebar-subtitle">Visual Agent Builder</p>
      </div>

      <nav className="sidebar-nav">
        <Link
          to="/dashboard"
          className={`nav-item ${isActive('/dashboard') ? 'active' : ''}`}
        >
          <span className="nav-icon">📊</span>
          <span className="nav-text">Dashboard</span>
        </Link>

        <Link
          to="/agent-builder"
          className={`nav-item ${isActive('/agent-builder') ? 'active' : ''}`}
        >
          <span className="nav-icon">🤖</span>
          <span className="nav-text">Agent Builder</span>
        </Link>

        <Link
          to="/playground"
          className={`nav-item ${isActive('/playground') ? 'active' : ''}`}
        >
          <span className="nav-icon">🎮</span>
          <span className="nav-text">Playground</span>
        </Link>

        <Link
          to="/datasets"
          className={`nav-item ${isActive('/datasets') ? 'active' : ''}`}
        >
          <span className="nav-icon">📁</span>
          <span className="nav-text">Datasets</span>
        </Link>
      </nav>

      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span className="status-text">System Online</span>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
