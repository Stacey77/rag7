import React, { useState, useEffect } from 'react';
import { User, Mail, Lock, Eye, EyeOff, Chrome, Github, Box, Check, X } from 'lucide-react';

interface RegisterFormProps {
  onRegister?: (name: string, email: string, password: string, acceptTerms: boolean) => void;
  onOAuthRegister?: (provider: 'google' | 'github' | 'microsoft') => void;
}

interface PasswordStrength {
  score: number;
  label: string;
  color: string;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({
  onRegister,
  onOAuthRegister,
}) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>({
    score: 0,
    label: '',
    color: '',
  });

  const calculatePasswordStrength = (password: string): PasswordStrength => {
    let score = 0;
    
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    const strengthMap: Record<number, PasswordStrength> = {
      0: { score: 0, label: '', color: '' },
      1: { score: 1, label: 'Very Weak', color: 'bg-red-500' },
      2: { score: 2, label: 'Weak', color: 'bg-orange-500' },
      3: { score: 3, label: 'Fair', color: 'bg-yellow-500' },
      4: { score: 4, label: 'Good', color: 'bg-lime-500' },
      5: { score: 5, label: 'Strong', color: 'bg-green-500' },
      6: { score: 6, label: 'Very Strong', color: 'bg-emerald-500' },
    };

    return strengthMap[score] || strengthMap[0];
  };

  useEffect(() => {
    if (password) {
      setPasswordStrength(calculatePasswordStrength(password));
    } else {
      setPasswordStrength({ score: 0, label: '', color: '' });
    }
  }, [password]);

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!name.trim()) {
      newErrors.name = 'Name is required';
    } else if (name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!acceptTerms) {
      newErrors.terms = 'You must accept the terms and conditions';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      await onRegister?.(name.trim(), email, password, acceptTerms);
    } catch (error) {
      console.error('Registration error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOAuthRegister = (provider: 'google' | 'github' | 'microsoft') => {
    onOAuthRegister?.(provider);
  };

  const passwordRequirements = [
    { met: password.length >= 8, text: 'At least 8 characters' },
    { met: /[A-Z]/.test(password), text: 'One uppercase letter' },
    { met: /[a-z]/.test(password), text: 'One lowercase letter' },
    { met: /[0-9]/.test(password), text: 'One number' },
    { met: /[^a-zA-Z0-9]/.test(password), text: 'One special character' },
  ];

  return (
    <div className="w-full max-w-md mx-auto p-8 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Create Account</h2>
        <p className="text-gray-300">Join our AI Design Platform</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Name Input */}
        <div>
          <label className="block text-sm font-medium text-gray-200 mb-2">
            Full Name
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (errors.name) {
                  const { name, ...rest } = errors;
                  setErrors(rest);
                }
              }}
              className={`w-full pl-11 pr-4 py-3 rounded-lg bg-white/5 border ${
                errors.name ? 'border-red-500' : 'border-white/10'
              } text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all`}
              placeholder="John Doe"
            />
          </div>
          {errors.name && (
            <p className="mt-1 text-sm text-red-400">{errors.name}</p>
          )}
        </div>

        {/* Email Input */}
        <div>
          <label className="block text-sm font-medium text-gray-200 mb-2">
            Email Address
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errors.email) {
                  const { email, ...rest } = errors;
                  setErrors(rest);
                }
              }}
              className={`w-full pl-11 pr-4 py-3 rounded-lg bg-white/5 border ${
                errors.email ? 'border-red-500' : 'border-white/10'
              } text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all`}
              placeholder="you@example.com"
            />
          </div>
          {errors.email && (
            <p className="mt-1 text-sm text-red-400">{errors.email}</p>
          )}
        </div>

        {/* Password Input */}
        <div>
          <label className="block text-sm font-medium text-gray-200 mb-2">
            Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (errors.password) {
                  const { password, ...rest } = errors;
                  setErrors(rest);
                }
              }}
              className={`w-full pl-11 pr-12 py-3 rounded-lg bg-white/5 border ${
                errors.password ? 'border-red-500' : 'border-white/10'
              } text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all`}
              placeholder="••••••••"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.password && (
            <p className="mt-1 text-sm text-red-400">{errors.password}</p>
          )}

          {/* Password Strength Indicator */}
          {password && (
            <div className="mt-2">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-400">Password Strength</span>
                <span className={`text-xs font-medium ${
                  passwordStrength.score >= 4 ? 'text-green-400' : 
                  passwordStrength.score >= 3 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {passwordStrength.label}
                </span>
              </div>
              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${passwordStrength.color}`}
                  style={{ width: `${(passwordStrength.score / 6) * 100}%` }}
                ></div>
              </div>
              <div className="mt-2 space-y-1">
                {passwordRequirements.map((req, idx) => (
                  <div key={idx} className="flex items-center text-xs">
                    {req.met ? (
                      <Check className="w-3 h-3 text-green-400 mr-2" />
                    ) : (
                      <X className="w-3 h-3 text-gray-500 mr-2" />
                    )}
                    <span className={req.met ? 'text-green-400' : 'text-gray-400'}>
                      {req.text}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Confirm Password Input */}
        <div>
          <label className="block text-sm font-medium text-gray-200 mb-2">
            Confirm Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                if (errors.confirmPassword) {
                  const { confirmPassword, ...rest } = errors;
                  setErrors(rest);
                }
              }}
              className={`w-full pl-11 pr-12 py-3 rounded-lg bg-white/5 border ${
                errors.confirmPassword ? 'border-red-500' : 'border-white/10'
              } text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all`}
              placeholder="••••••••"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300"
            >
              {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.confirmPassword && (
            <p className="mt-1 text-sm text-red-400">{errors.confirmPassword}</p>
          )}
        </div>

        {/* Terms Acceptance */}
        <div>
          <label className="flex items-start cursor-pointer">
            <input
              type="checkbox"
              checked={acceptTerms}
              onChange={(e) => {
                setAcceptTerms(e.target.checked);
                if (errors.terms) {
                  const { terms, ...rest } = errors;
                  setErrors(rest);
                }
              }}
              className={`w-4 h-4 mt-0.5 rounded border-white/20 bg-white/5 text-blue-500 focus:ring-2 focus:ring-blue-500 ${
                errors.terms ? 'border-red-500' : ''
              }`}
            />
            <span className="ml-2 text-sm text-gray-300">
              I agree to the{' '}
              <a href="#" className="text-blue-400 hover:text-blue-300">
                Terms of Service
              </a>{' '}
              and{' '}
              <a href="#" className="text-blue-400 hover:text-blue-300">
                Privacy Policy
              </a>
            </span>
          </label>
          {errors.terms && (
            <p className="mt-1 text-sm text-red-400">{errors.terms}</p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white font-medium hover:from-blue-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </button>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/10"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-4 bg-transparent text-gray-400">Or sign up with</span>
          </div>
        </div>

        {/* OAuth Buttons */}
        <div className="grid grid-cols-3 gap-3">
          <button
            type="button"
            onClick={() => handleOAuthRegister('google')}
            className="flex items-center justify-center py-3 px-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all group"
          >
            <Chrome className="w-5 h-5 text-gray-300 group-hover:text-white transition-colors" />
          </button>
          <button
            type="button"
            onClick={() => handleOAuthRegister('github')}
            className="flex items-center justify-center py-3 px-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all group"
          >
            <Github className="w-5 h-5 text-gray-300 group-hover:text-white transition-colors" />
          </button>
          <button
            type="button"
            onClick={() => handleOAuthRegister('microsoft')}
            className="flex items-center justify-center py-3 px-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all group"
          >
            <Box className="w-5 h-5 text-gray-300 group-hover:text-white transition-colors" />
          </button>
        </div>
      </form>
    </div>
  );
};
