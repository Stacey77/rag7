import { NavLink } from 'react-router-dom'

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">🤖 RAGAMUFFIN</div>
      <nav className="sidebar-nav">
        <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
          📊 Dashboard
        </NavLink>
        <NavLink to="/playground" className={({ isActive }) => isActive ? 'active' : ''}>
          🎮 Playground
        </NavLink>
        <NavLink to="/datasets" className={({ isActive }) => isActive ? 'active' : ''}>
          📁 Datasets
        </NavLink>
        <NavLink to="/agent-builder" className={({ isActive }) => isActive ? 'active' : ''}>
          🔧 Agent Builder
        </NavLink>
      </nav>
    </aside>
  )
}

export default Sidebar
