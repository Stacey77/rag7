import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const AuthContext = createContext(null)

const API_BASE = '/api/v1'

// OIDC Configuration
const getOIDCConfig = async () => {
  try {
    const response = await fetch(`${API_BASE}/auth/oidc/config`)
    if (response.ok) {
      return await response.json()
    }
  } catch (error) {
    console.warn('OIDC not configured:', error)
  }
  return null
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'))
  const [isLoading, setIsLoading] = useState(true)
  const [oidcConfig, setOidcConfig] = useState(null)

  // Load OIDC config on mount
  useEffect(() => {
    getOIDCConfig().then(setOidcConfig)
  }, [])

  // Load user profile on token change
  useEffect(() => {
    const loadUser = async () => {
      if (!token) {
        setUser(null)
        setIsLoading(false)
        return
      }

      try {
        const response = await fetch(`${API_BASE}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const userData = await response.json()
          setUser(userData)
        } else {
          // Token invalid
          localStorage.removeItem('auth_token')
          setToken(null)
          setUser(null)
        }
      } catch (error) {
        console.error('Failed to load user:', error)
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    loadUser()
  }, [token])

  // Login with username/password
  const login = useCallback(async (username, password) => {
    const response = await fetch(`${API_BASE}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({ username, password })
    })

    if (!response.ok) {
      throw new Error('Login failed')
    }

    const data = await response.json()
    localStorage.setItem('auth_token', data.access_token)
    setToken(data.access_token)
    return data
  }, [])

  // OIDC login redirect
  const loginWithOIDC = useCallback(() => {
    if (!oidcConfig?.enabled) {
      throw new Error('OIDC not configured')
    }

    const state = crypto.randomUUID()
    sessionStorage.setItem('oidc_state', state)

    const params = new URLSearchParams({
      client_id: oidcConfig.client_id,
      redirect_uri: `${window.location.origin}/auth/callback`,
      response_type: 'code',
      scope: 'openid email profile',
      state
    })

    window.location.href = `${oidcConfig.authorization_endpoint}?${params}`
  }, [oidcConfig])

  // Handle OIDC callback
  const handleOIDCCallback = useCallback(async (code, state) => {
    const savedState = sessionStorage.getItem('oidc_state')
    if (state !== savedState) {
      throw new Error('Invalid state')
    }
    sessionStorage.removeItem('oidc_state')

    const response = await fetch(`${API_BASE}/auth/oidc/callback?code=${code}&state=${state}`, {
      method: 'POST'
    })

    if (!response.ok) {
      throw new Error('OIDC callback failed')
    }

    const data = await response.json()
    localStorage.setItem('auth_token', data.access_token)
    setToken(data.access_token)
    return data
  }, [])

  // Logout
  const logout = useCallback(() => {
    localStorage.removeItem('auth_token')
    setToken(null)
    setUser(null)
  }, [])

  // Check if user has specific role(s)
  const hasRole = useCallback((requiredRoles) => {
    if (!user?.roles) return false
    if (typeof requiredRoles === 'string') {
      return user.roles.includes(requiredRoles)
    }
    return requiredRoles.some(role => user.roles.includes(role))
  }, [user])

  // Get auth header for API calls
  const getAuthHeader = useCallback(() => {
    return token ? { 'Authorization': `Bearer ${token}` } : {}
  }, [token])

  const value = {
    user,
    token,
    isLoading,
    oidcConfig,
    login,
    loginWithOIDC,
    handleOIDCCallback,
    logout,
    hasRole,
    getAuthHeader
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
