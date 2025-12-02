import { NavLink } from 'react-router-dom'

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          {!collapsed && 'Epic Platform'}
          {collapsed && '🧠'}
        </div>
        <button className="sidebar-toggle" onClick={onToggle}>
          {collapsed ? '→' : '←'}
        </button>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink to="/dashboard" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">📊</span>
          <span className="nav-label">Dashboard</span>
        </NavLink>
        
        <NavLink to="/agent-builder" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">🤖</span>
          <span className="nav-label">Agent Builder</span>
        </NavLink>
        
        <NavLink to="/playground" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">🎮</span>
          <span className="nav-label">Playground</span>
        </NavLink>
        
        <NavLink to="/datasets" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">📚</span>
          <span className="nav-label">Datasets</span>
        </NavLink>
      </nav>
      
      <div className="sidebar-footer" style={{ padding: '1rem', borderTop: '1px solid var(--border-color)' }}>
        {!collapsed && (
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            v1.0.0
          </div>
        )}
      </div>
    </aside>
  )
}

export default Sidebar
