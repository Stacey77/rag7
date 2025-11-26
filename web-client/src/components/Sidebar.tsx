import { NavLink } from 'react-router-dom'
import './Sidebar.css'

function Sidebar() {
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
        <div className="status-panel">
          <span className="status-indicator status-active"></span>
          <span>System Online</span>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
