import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Profile: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleSave = async () => {
    // TODO: Implement profile update API call
    setMessage('Profile updated successfully!');
    setIsEditing(false);
    setTimeout(() => setMessage(''), 3000);
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement password change API call
    setMessage('Password updated successfully!');
    setCurrentPassword('');
    setNewPassword('');
    setTimeout(() => setMessage(''), 3000);
  };

  // Get user initials for avatar
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div style={{ padding: '30px', maxWidth: '800px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1))',
        borderRadius: '16px',
        padding: '30px',
        marginBottom: '30px',
        border: '1px solid rgba(0, 255, 255, 0.2)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          {/* Avatar */}
          <div style={{
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #00ffff, #ff00ff)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '28px',
            fontWeight: 'bold',
            color: '#000',
            fontFamily: 'Orbitron, sans-serif',
          }}>
            {user?.name ? getInitials(user.name) : '?'}
          </div>
          
          <div style={{ flex: 1 }}>
            <h1 style={{
              fontFamily: 'Orbitron, sans-serif',
              fontSize: '24px',
              background: 'linear-gradient(135deg, #00ffff, #ff00ff)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              marginBottom: '5px',
            }}>
              {user?.name || 'User'}
            </h1>
            <p style={{ color: '#888', fontSize: '14px' }}>{user?.email}</p>
          </div>

          <button
            onClick={handleLogout}
            style={{
              padding: '10px 20px',
              background: 'rgba(255, 0, 0, 0.2)',
              border: '1px solid rgba(255, 0, 0, 0.3)',
              borderRadius: '8px',
              color: '#ff6b6b',
              cursor: 'pointer',
              fontFamily: 'Orbitron, sans-serif',
              fontSize: '12px',
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Success message */}
      {message && (
        <div style={{
          background: 'rgba(0, 255, 0, 0.1)',
          border: '1px solid rgba(0, 255, 0, 0.3)',
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '20px',
          color: '#00ff00',
          fontSize: '14px',
        }}>
          {message}
        </div>
      )}

      {/* Profile Info */}
      <div style={{
        background: 'rgba(26, 26, 46, 0.6)',
        borderRadius: '16px',
        padding: '24px',
        marginBottom: '20px',
        border: '1px solid rgba(0, 255, 255, 0.1)',
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
        }}>
          <h2 style={{
            fontFamily: 'Orbitron, sans-serif',
            fontSize: '16px',
            color: '#00ffff',
          }}>
            Profile Information
          </h2>
          <button
            onClick={() => setIsEditing(!isEditing)}
            style={{
              padding: '8px 16px',
              background: isEditing ? 'rgba(255, 0, 0, 0.2)' : 'rgba(0, 255, 255, 0.2)',
              border: `1px solid ${isEditing ? 'rgba(255, 0, 0, 0.3)' : 'rgba(0, 255, 255, 0.3)'}`,
              borderRadius: '6px',
              color: isEditing ? '#ff6b6b' : '#00ffff',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
        </div>

        <div style={{ display: 'grid', gap: '20px' }}>
          <div>
            <label style={{
              display: 'block',
              color: '#888',
              fontSize: '12px',
              marginBottom: '8px',
            }}>
              Full Name
            </label>
            {isEditing ? (
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(0, 255, 255, 0.3)',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '14px',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            ) : (
              <p style={{ color: '#fff', fontSize: '16px' }}>{user?.name}</p>
            )}
          </div>

          <div>
            <label style={{
              display: 'block',
              color: '#888',
              fontSize: '12px',
              marginBottom: '8px',
            }}>
              Email Address
            </label>
            {isEditing ? (
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(0, 255, 255, 0.3)',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '14px',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            ) : (
              <p style={{ color: '#fff', fontSize: '16px' }}>{user?.email}</p>
            )}
          </div>

          <div>
            <label style={{
              display: 'block',
              color: '#888',
              fontSize: '12px',
              marginBottom: '8px',
            }}>
              Member Since
            </label>
            <p style={{ color: '#fff', fontSize: '16px' }}>
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
            </p>
          </div>
        </div>

        {isEditing && (
          <button
            onClick={handleSave}
            style={{
              marginTop: '20px',
              padding: '10px 24px',
              background: 'linear-gradient(135deg, #00ffff, #0080ff)',
              border: 'none',
              borderRadius: '6px',
              color: '#000',
              fontWeight: 'bold',
              cursor: 'pointer',
              fontFamily: 'Orbitron, sans-serif',
              fontSize: '12px',
            }}
          >
            Save Changes
          </button>
        )}
      </div>

      {/* Change Password */}
      <div style={{
        background: 'rgba(26, 26, 46, 0.6)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid rgba(0, 255, 255, 0.1)',
      }}>
        <h2 style={{
          fontFamily: 'Orbitron, sans-serif',
          fontSize: '16px',
          color: '#00ffff',
          marginBottom: '20px',
        }}>
          Change Password
        </h2>

        <form onSubmit={handlePasswordChange}>
          <div style={{ display: 'grid', gap: '16px' }}>
            <div>
              <label style={{
                display: 'block',
                color: '#888',
                fontSize: '12px',
                marginBottom: '8px',
              }}>
                Current Password
              </label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(0, 255, 255, 0.3)',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '14px',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
                placeholder="••••••••"
              />
            </div>

            <div>
              <label style={{
                display: 'block',
                color: '#888',
                fontSize: '12px',
                marginBottom: '8px',
              }}>
                New Password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(0, 255, 255, 0.3)',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '14px',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={!currentPassword || !newPassword}
              style={{
                padding: '10px 24px',
                background: currentPassword && newPassword
                  ? 'linear-gradient(135deg, #ff00ff, #0080ff)'
                  : 'rgba(128, 128, 128, 0.3)',
                border: 'none',
                borderRadius: '6px',
                color: currentPassword && newPassword ? '#fff' : '#888',
                fontWeight: 'bold',
                cursor: currentPassword && newPassword ? 'pointer' : 'not-allowed',
                fontFamily: 'Orbitron, sans-serif',
                fontSize: '12px',
                width: 'fit-content',
              }}
            >
              Update Password
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Profile;
