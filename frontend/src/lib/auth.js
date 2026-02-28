/**
 * Authentication library with OIDC support
 */

const TOKEN_KEY = 'agentic_token';
const USER_KEY = 'agentic_user';

// Simple in-memory storage for dev (use secure storage in production)
let tokenStorage = {
  token: null,
  user: null
};

export const auth = {
  /**
   * Login with username/password (dev mode)
   */
  async login(username, password) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    
    // Store token in memory (more secure than localStorage)
    tokenStorage.token = data.access_token;
    
    // Get user info
    const user = await this.getCurrentUser();
    tokenStorage.user = user;
    
    return { token: data.access_token, user };
  },

  /**
   * Get current user info
   */
  async getCurrentUser() {
    const token = this.getToken();
    if (!token) {
      return null;
    }

    const response = await fetch('/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      this.logout();
      return null;
    }

    const user = await response.json();
    tokenStorage.user = user;
    return user;
  },

  /**
   * Logout
   */
  async logout() {
    const token = this.getToken();
    
    if (token) {
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      } catch (e) {
        // Ignore errors
      }
    }
    
    tokenStorage.token = null;
    tokenStorage.user = null;
  },

  /**
   * Get stored token
   */
  getToken() {
    return tokenStorage.token;
  },

  /**
   * Get stored user
   */
  getUser() {
    return tokenStorage.user;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.getToken();
  },

  /**
   * Check if user has role
   */
  hasRole(role) {
    const user = this.getUser();
    return user?.roles?.includes(role) || user?.roles?.includes('admin');
  },

  /**
   * Check if user can override decisions
   */
  canOverride() {
    return this.hasRole('admin') || this.hasRole('reviewer');
  },

  /**
   * Check if user can escalate tasks
   */
  canEscalate() {
    return this.hasRole('admin') || this.hasRole('reviewer') || this.hasRole('agent_manager');
  },

  /**
   * Check if user can manage agents
   */
  canManageAgents() {
    return this.hasRole('admin') || this.hasRole('agent_manager');
  }
};

/**
 * Create authenticated request headers
 */
export function authHeaders() {
  const token = auth.getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
}
