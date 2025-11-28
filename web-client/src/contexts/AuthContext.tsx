import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import axios from 'axios';

// Types
interface User {
  id: string;
  email: string;
  name: string;
  created_at?: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const TOKEN_KEY = 'ragamuffin_access_token';
const REFRESH_TOKEN_KEY = 'ragamuffin_refresh_token';
const USER_KEY = 'ragamuffin_user';

// API base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Provider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Clear auth state
  const clearAuth = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  }, []);

  // Internal refresh token function
  const refreshTokenInternal = useCallback(async (): Promise<boolean> => {
    const refreshTokenValue = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshTokenValue) return false;

    try {
      const response = await axios.post(`${API_URL}/auth/refresh`, {
        refresh_token: refreshTokenValue,
      });
      
      const tokens: AuthTokens = response.data;
      localStorage.setItem(TOKEN_KEY, tokens.access_token);
      if (tokens.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
      }
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;
      
      // Fetch updated user info
      const userResponse = await axios.get(`${API_URL}/auth/me`);
      setUser(userResponse.data);
      localStorage.setItem(USER_KEY, JSON.stringify(userResponse.data));
      
      return true;
    } catch {
      clearAuth();
      return false;
    }
  }, [clearAuth]);

  // Initialize auth state from storage
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);

      if (storedToken && storedUser) {
        try {
          setUser(JSON.parse(storedUser));
          // Verify token is still valid
          axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
          const response = await axios.get(`${API_URL}/auth/me`);
          setUser(response.data);
          localStorage.setItem(USER_KEY, JSON.stringify(response.data));
        } catch {
          // Token expired, try refresh
          const refreshed = await refreshTokenInternal();
          if (!refreshed) {
            clearAuth();
          }
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, [clearAuth, refreshTokenInternal]);

  // Login function
  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password,
      });
      
      const tokens: AuthTokens = response.data;
      localStorage.setItem(TOKEN_KEY, tokens.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;
      
      // Fetch user info
      const userResponse = await axios.get(`${API_URL}/auth/me`);
      setUser(userResponse.data);
      localStorage.setItem(USER_KEY, JSON.stringify(userResponse.data));
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Register function
  const register = useCallback(async (name: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      await axios.post(`${API_URL}/auth/register`, {
        name,
        email,
        password,
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Logout function
  const logout = useCallback(() => {
    clearAuth();
  }, [clearAuth]);

  // Refresh token (public)
  const refreshToken = useCallback(async (): Promise<boolean> => {
    return refreshTokenInternal();
  }, [refreshTokenInternal]);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
