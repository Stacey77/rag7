import { useState, useEffect } from 'react'
import Login from './components/Login'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')
  const [protectedData, setProtectedData] = useState(null)

  const handleLogin = async (username, password) => {
    try {
      setError('')
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Login failed')
      }

      const data = await response.json()
      setToken(data.access_token)
      localStorage.setItem('token', data.access_token)

      // Fetch user info
      await fetchUserInfo(data.access_token)
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  const fetchUserInfo = async (authToken) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken || token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch user info')
      }

      const userData = await response.json()
      setUser(userData)
    } catch (err) {
      console.error('Error fetching user info:', err)
      setError(err.message)
    }
  }

  const testProtectedRoute = async () => {
    try {
      setError('')
      const response = await fetch(`${API_BASE_URL}/protected`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to access protected route')
      }

      const data = await response.json()
      setProtectedData(data)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleLogout = () => {
    setToken(null)
    setUser(null)
    setProtectedData(null)
    localStorage.removeItem('token')
  }

  // Load user info on mount if token exists
  useEffect(() => {
    if (token && !user) {
      fetchUserInfo(token)
    }
  }, [token])

  if (!token) {
    return <Login onLogin={handleLogin} error={error} />
  }

  return (
    <div className="app">
      <div className="container">
        <h1>🎉 Authentication Successful!</h1>
        <h2>JWT Auth Demo</h2>

        {error && <div className="error">{error}</div>}

        {user && (
          <div className="user-info">
            <h3>User Information</h3>
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Full Name:</strong> {user.full_name}</p>
            <p><strong>Status:</strong> {user.disabled ? 'Inactive' : 'Active'}</p>
          </div>
        )}

        <button onClick={testProtectedRoute}>
          Test Protected Route
        </button>

        {protectedData && (
          <div className="success">
            <strong>Protected Route Response:</strong>
            <pre style={{ marginTop: '10px', whiteSpace: 'pre-wrap' }}>
              {JSON.stringify(protectedData, null, 2)}
            </pre>
          </div>
        )}

        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  )
}

export default App
