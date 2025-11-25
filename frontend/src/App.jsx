import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth.jsx'
import Login from './components/Login.jsx'
import OversightDashboard from './components/OversightDashboard.jsx'

function ProtectedRoute({ children, requiredRoles = [] }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <div className="login-container">Loading...</div>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (requiredRoles.length > 0) {
    const hasRole = requiredRoles.some(role => user.roles?.includes(role))
    if (!hasRole) {
      return <div className="main"><div className="alert alert-danger">Insufficient permissions</div></div>
    }
  }

  return children
}

function App() {
  const { user, logout } = useAuth()

  return (
    <div className="app">
      {user && (
        <header className="header">
          <h1>🤖 Agentic Agent Platform</h1>
          <div className="user-menu">
            <div className="user-info">
              <div className="user-name">{user.email}</div>
              <div className="user-role">{user.roles?.join(', ')}</div>
            </div>
            <button className="btn btn-outline" onClick={logout}>
              Logout
            </button>
          </div>
        </header>
      )}
      
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <OversightDashboard />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App
