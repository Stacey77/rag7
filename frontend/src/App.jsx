import { useState, useEffect } from 'react';
import Login from './components/Login';
import OversightDashboard from './components/OversightDashboard';
import { auth } from './lib/auth';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    checkAuth();
  }, []);

  const checkAuth = async () => {
    if (auth.isAuthenticated()) {
      const currentUser = await auth.getCurrentUser();
      setUser(currentUser);
    }
    setLoading(false);
  };

  const handleLogin = (loggedInUser) => {
    setUser(loggedInUser);
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (loading) {
    return (
      <div style={styles.loading}>
        <p>Loading...</p>
      </div>
    );
  }

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  return <OversightDashboard user={user} onLogout={handleLogout} />;
}

const styles = {
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    fontSize: '1.2rem',
    color: '#666',
  },
};

export default App;
