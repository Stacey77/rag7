import { NavLink } from 'react-router-dom'
import './Sidebar.css'

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-logo neon-text">EPIC</h1>
        <p className="sidebar-subtitle">Platform v1.0</p>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink 
          to="/" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          end
        >
          <span className="nav-icon">📊</span>
          <span className="nav-text">Dashboard</span>
        </NavLink>
        
        <NavLink 
          to="/playground" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="nav-icon">🎮</span>
          <span className="nav-text">Playground</span>
        </NavLink>
        
        <NavLink 
          to="/datasets" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="nav-icon">📁</span>
          <span className="nav-text">Datasets</span>
        </NavLink>
        
        <NavLink 
          to="/agent-builder" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="nav-icon">🤖</span>
          <span className="nav-text">Agent Builder</span>
        </NavLink>
      </nav>
      
      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span className="status-text">System Online</span>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
