import React from 'react';
import { LoginForm, RegisterForm, UserProfile } from './components/auth';

// Example usage of Auth Components

export const AuthExample: React.FC = () => {
  // Login Form Example
  const handleLogin = (email: string, password: string, rememberMe: boolean) => {
    console.log('Login:', { email, password, rememberMe });
    // Implement your login logic here
  };

  const handleOAuthLogin = (provider: 'google' | 'github' | 'microsoft') => {
    console.log('OAuth login with:', provider);
    // Implement OAuth login logic here
  };

  const handleForgotPassword = () => {
    console.log('Forgot password clicked');
    // Navigate to forgot password page
  };

  // Register Form Example
  const handleRegister = (name: string, email: string, password: string, acceptTerms: boolean) => {
    console.log('Register:', { name, email, password, acceptTerms });
    // Implement registration logic here
  };

  const handleOAuthRegister = (provider: 'google' | 'github' | 'microsoft') => {
    console.log('OAuth register with:', provider);
    // Implement OAuth registration logic here
  };

  // User Profile Example
  const userData = {
    name: 'John Doe',
    email: 'john.doe@example.com',
    role: 'Admin',
    twoFactorEnabled: false,
  };

  const apiKeys = [
    {
      id: '1',
      name: 'Production API',
      key: 'sk_prod_abc123xyz789def456ghi789',
      createdAt: '2024-01-15',
      lastUsed: '2024-01-20',
    },
    {
      id: '2',
      name: 'Development API',
      key: 'sk_dev_xyz789abc123def456ghi789',
      createdAt: '2024-01-10',
      lastUsed: '2024-01-19',
    },
  ];

  const sessions = [
    {
      id: '1',
      device: 'Chrome on MacOS',
      location: 'San Francisco, CA',
      lastActive: '2 minutes ago',
      current: true,
    },
    {
      id: '2',
      device: 'Firefox on Windows',
      location: 'New York, NY',
      lastActive: '1 day ago',
      current: false,
    },
  ];

  const handleUpdateProfile = (data: Partial<typeof userData>) => {
    console.log('Update profile:', data);
    // Implement profile update logic here
  };

  const handleToggle2FA = (enabled: boolean) => {
    console.log('Toggle 2FA:', enabled);
    // Implement 2FA toggle logic here
  };

  const handleCreateApiKey = (name: string) => {
    console.log('Create API key:', name);
    // Implement API key creation logic here
  };

  const handleDeleteApiKey = (id: string) => {
    console.log('Delete API key:', id);
    // Implement API key deletion logic here
  };

  const handleRevokeSession = (id: string) => {
    console.log('Revoke session:', id);
    // Implement session revocation logic here
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Login Form */}
        <section>
          <h2 className="text-2xl font-bold text-white mb-6">Login Form</h2>
          <LoginForm
            onLogin={handleLogin}
            onOAuthLogin={handleOAuthLogin}
            onForgotPassword={handleForgotPassword}
          />
        </section>

        {/* Register Form */}
        <section>
          <h2 className="text-2xl font-bold text-white mb-6">Register Form</h2>
          <RegisterForm
            onRegister={handleRegister}
            onOAuthRegister={handleOAuthRegister}
          />
        </section>

        {/* User Profile */}
        <section>
          <h2 className="text-2xl font-bold text-white mb-6">User Profile</h2>
          <UserProfile
            user={userData}
            apiKeys={apiKeys}
            sessions={sessions}
            onUpdateProfile={handleUpdateProfile}
            onToggle2FA={handleToggle2FA}
            onCreateApiKey={handleCreateApiKey}
            onDeleteApiKey={handleDeleteApiKey}
            onRevokeSession={handleRevokeSession}
          />
        </section>
      </div>
    </div>
  );
};
