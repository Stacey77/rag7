import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Register: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const validatePassword = (pwd: string): string[] => {
    const errors: string[] = [];
    if (pwd.length < 8) errors.push('At least 8 characters');
    if (!/[A-Z]/.test(pwd)) errors.push('One uppercase letter');
    if (!/[a-z]/.test(pwd)) errors.push('One lowercase letter');
    if (!/[0-9]/.test(pwd)) errors.push('One number');
    return errors;
  };

  const passwordErrors = validatePassword(password);
  const passwordsMatch = password === confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (passwordErrors.length > 0) {
      setError('Please meet all password requirements');
      return;
    }
    if (!passwordsMatch) {
      setError('Passwords do not match');
      return;
    }
    if (!acceptTerms) {
      setError('Please accept the terms and conditions');
      return;
    }

    setIsSubmitting(true);

    try {
      await register(name, email, password);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 
        (typeof err === 'object' && err !== null && 'response' in err) ? 
          ((err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Registration failed') :
          'Registration failed. Please try again.';
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (success) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0a0a0f 100%)',
      }}>
        <div style={{
          textAlign: 'center',
          padding: '40px',
        }}>
          <div style={{ fontSize: '60px', marginBottom: '20px' }}>✅</div>
          <h2 style={{
            fontFamily: 'Orbitron, sans-serif',
            fontSize: '24px',
            color: '#00ff00',
            marginBottom: '10px',
          }}>
            Registration Successful!
          </h2>
          <p style={{ color: '#888' }}>Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0a0a0f 100%)',
      padding: '20px',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '450px',
        background: 'rgba(26, 26, 46, 0.9)',
        borderRadius: '16px',
        border: '1px solid rgba(0, 255, 255, 0.2)',
        padding: '40px',
        boxShadow: '0 0 40px rgba(0, 255, 255, 0.1)',
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <div style={{
            width: '60px',
            height: '60px',
            background: 'linear-gradient(135deg, #ff00ff, #00ffff)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px',
            fontSize: '28px',
          }}>
            🚀
          </div>
          <h1 style={{
            fontFamily: 'Orbitron, sans-serif',
            fontSize: '24px',
            background: 'linear-gradient(135deg, #ff00ff, #00ffff)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '8px',
          }}>
            Create Account
          </h1>
          <p style={{ color: '#888', fontSize: '14px' }}>
            Join the Ragamuffin platform
          </p>
        </div>

        {/* Error message */}
        {error && (
          <div style={{
            background: 'rgba(255, 0, 0, 0.1)',
            border: '1px solid rgba(255, 0, 0, 0.3)',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '20px',
            color: '#ff6b6b',
            fontSize: '14px',
          }}>
            {error}
          </div>
        )}

        {/* Register form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              color: '#00ffff',
              fontSize: '12px',
              fontWeight: 'bold',
              marginBottom: '8px',
              fontFamily: 'Orbitron, sans-serif',
            }}>
              FULL NAME
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid rgba(0, 255, 255, 0.3)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '16px',
                outline: 'none',
                boxSizing: 'border-box',
              }}
              placeholder="John Doe"
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              color: '#00ffff',
              fontSize: '12px',
              fontWeight: 'bold',
              marginBottom: '8px',
              fontFamily: 'Orbitron, sans-serif',
            }}>
              EMAIL
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid rgba(0, 255, 255, 0.3)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '16px',
                outline: 'none',
                boxSizing: 'border-box',
              }}
              placeholder="you@example.com"
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              color: '#00ffff',
              fontSize: '12px',
              fontWeight: 'bold',
              marginBottom: '8px',
              fontFamily: 'Orbitron, sans-serif',
            }}>
              PASSWORD
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '12px 48px 12px 16px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: `1px solid ${password && passwordErrors.length === 0 ? 'rgba(0, 255, 0, 0.5)' : 'rgba(0, 255, 255, 0.3)'}`,
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '16px',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#888',
                  cursor: 'pointer',
                  fontSize: '18px',
                }}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
            {/* Password requirements */}
            {password && (
              <div style={{ marginTop: '8px', fontSize: '12px' }}>
                {['At least 8 characters', 'One uppercase letter', 'One lowercase letter', 'One number'].map((req) => (
                  <div key={req} style={{
                    color: passwordErrors.includes(req) ? '#ff6b6b' : '#00ff00',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    marginBottom: '4px',
                  }}>
                    {passwordErrors.includes(req) ? '✗' : '✓'} {req}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              color: '#00ffff',
              fontSize: '12px',
              fontWeight: 'bold',
              marginBottom: '8px',
              fontFamily: 'Orbitron, sans-serif',
            }}>
              CONFIRM PASSWORD
            </label>
            <input
              type={showPassword ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'rgba(0, 0, 0, 0.3)',
                border: `1px solid ${confirmPassword && passwordsMatch ? 'rgba(0, 255, 0, 0.5)' : confirmPassword ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 255, 255, 0.3)'}`,
                borderRadius: '8px',
                color: '#fff',
                fontSize: '16px',
                outline: 'none',
                boxSizing: 'border-box',
              }}
              placeholder="••••••••"
            />
            {confirmPassword && !passwordsMatch && (
              <p style={{ color: '#ff6b6b', fontSize: '12px', marginTop: '4px' }}>
                Passwords do not match
              </p>
            )}
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              cursor: 'pointer',
              color: '#888',
              fontSize: '14px',
            }}>
              <input
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                style={{
                  width: '18px',
                  height: '18px',
                  accentColor: '#00ffff',
                }}
              />
              I accept the terms and conditions
            </label>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '14px',
              background: isSubmitting 
                ? 'rgba(255, 0, 255, 0.3)' 
                : 'linear-gradient(135deg, #ff00ff, #00ffff)',
              border: 'none',
              borderRadius: '8px',
              color: isSubmitting ? '#888' : '#fff',
              fontSize: '16px',
              fontWeight: 'bold',
              fontFamily: 'Orbitron, sans-serif',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
              marginBottom: '20px',
            }}
          >
            {isSubmitting ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        {/* Links */}
        <div style={{ textAlign: 'center' }}>
          <p style={{ color: '#888', fontSize: '14px' }}>
            Already have an account?{' '}
            <Link
              to="/login"
              style={{
                color: '#00ffff',
                textDecoration: 'none',
                fontWeight: 'bold',
              }}
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
