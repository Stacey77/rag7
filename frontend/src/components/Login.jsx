import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const { login, loginWithOIDC, oidcConfig } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError('Login failed. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleOIDCLogin = () => {
    try {
      loginWithOIDC()
    } catch (err) {
      setError('OIDC login is not configured')
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          🤖 Agentic Platform
        </h1>
        <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', fontWeight: 400, fontSize: '1rem', color: '#6b7280' }}>
          Sign in to Oversight Dashboard
        </h2>

        {error && (
          <div className="alert alert-danger">{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="username">
              Username
            </label>
            <input
              id="username"
              type="text"
              className="form-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '1rem' }}
            disabled={isLoading}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {oidcConfig?.enabled && (
          <>
            <div style={{ 
              textAlign: 'center', 
              margin: '1.5rem 0',
              color: '#9ca3af',
              fontSize: '0.875rem'
            }}>
              or
            </div>
            <button
              type="button"
              className="btn btn-outline"
              style={{ width: '100%' }}
              onClick={handleOIDCLogin}
            >
              Sign in with SSO
            </button>
          </>
        )}

        <div style={{ 
          marginTop: '1.5rem', 
          padding: '1rem', 
          background: '#f3f4f6', 
          borderRadius: '0.375rem',
          fontSize: '0.875rem'
        }}>
          <strong>Demo Credentials:</strong>
          <ul style={{ marginTop: '0.5rem', paddingLeft: '1.25rem' }}>
            <li><code>admin_*</code> - Admin role</li>
            <li><code>reviewer_*</code> - Reviewer role</li>
            <li><code>manager_*</code> - Agent Manager role</li>
            <li>Any other username - Viewer role</li>
          </ul>
          <p style={{ marginTop: '0.5rem', color: '#6b7280' }}>
            Password can be anything in development mode.
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
