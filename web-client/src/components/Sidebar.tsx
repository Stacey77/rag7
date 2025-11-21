import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

const Sidebar = () => {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-logo">RAGAMUFFIN</h2>
        <p className="sidebar-tagline">AI Agent Platform</p>
      </div>

      <nav className="sidebar-nav">
        <Link 
          to="/" 
          className={`nav-item ${isActive('/') ? 'active' : ''}`}
        >
          <span className="nav-icon">📊</span>
          <span className="nav-label">Dashboard</span>
        </Link>

        <Link 
          to="/playground" 
          className={`nav-item ${isActive('/playground') ? 'active' : ''}`}
        >
          <span className="nav-icon">🎮</span>
          <span className="nav-label">Playground</span>
        </Link>

        <Link 
          to="/datasets" 
          className={`nav-item ${isActive('/datasets') ? 'active' : ''}`}
        >
          <span className="nav-icon">📁</span>
          <span className="nav-label">Datasets</span>
        </Link>

        <Link 
          to="/agent-builder" 
          className={`nav-item ${isActive('/agent-builder') ? 'active' : ''}`}
        >
          <span className="nav-icon">🔧</span>
          <span className="nav-label">Agent Builder</span>
        </Link>
      </nav>

      <div className="sidebar-footer">
        <div className="status-indicator status-online"></div>
        <span className="status-text">System Online</span>
      </div>
    </aside>
  )
}

export default Sidebar
