import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Sidebar.css'

function Sidebar() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Get user initials for avatar
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-logo">RAGAMUFFIN</h2>
        <p className="sidebar-subtitle">AI Orchestration</p>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          <span className="nav-icon">📊</span>
          <span>Dashboard</span>
        </NavLink>
        
        <NavLink to="/playground" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          <span className="nav-icon">🎮</span>
          <span>Playground</span>
        </NavLink>
        
        <NavLink to="/voice-calls" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          <span className="nav-icon">🎤</span>
          <span>Voice Calls</span>
        </NavLink>
        
        <NavLink to="/rag-query" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          <span className="nav-icon">🔍</span>
          <span>RAG Query</span>
        </NavLink>
        
        <NavLink to="/documents" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          <span className="nav-icon">📚</span>
          <span>Documents</span>
        </NavLink>
        
        <NavLink to="/datasets" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          <span className="nav-icon">📂</span>
          <span>Datasets</span>
        </NavLink>
        
        <NavLink to="/agent-builder" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          <span className="nav-icon">🤖</span>
          <span>Agent Builder</span>
        </NavLink>
      </nav>
      
      <div className="sidebar-footer">
        {isAuthenticated && user ? (
          <div className="user-section">
            <NavLink to="/profile" className="user-info">
              <div className="user-avatar">
                {getInitials(user.name || 'U')}
              </div>
              <div className="user-details">
                <span className="user-name">{user.name}</span>
                <span className="user-email">{user.email}</span>
              </div>
            </NavLink>
            <button onClick={handleLogout} className="logout-btn" title="Logout">
              🚪
            </button>
          </div>
        ) : (
          <NavLink to="/login" className="login-btn">
            <span>🔐</span>
            <span>Sign In</span>
          </NavLink>
        )}
        <div className="status-panel">
          <span className="status-indicator status-active"></span>
          <span>System Online</span>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
