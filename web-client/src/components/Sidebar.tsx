import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

const Sidebar = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/agent-builder', label: 'Agent Builder', icon: '🤖' },
    { path: '/playground', label: 'Playground', icon: '🎮' },
    { path: '/datasets', label: 'Datasets', icon: '📚' },
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">
          <span className="glow">EPIC</span>
          <br />
          <span style={{ fontSize: '0.8em', color: 'var(--neon-pink)' }}>PLATFORM</span>
        </h2>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </Link>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span>System Online</span>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
