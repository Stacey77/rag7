import React, { useState } from 'react';
import {
  User,
  Mail,
  Shield,
  Key,
  Monitor,
  Edit2,
  Save,
  X,
  Copy,
  Eye,
  EyeOff,
  Trash2,
  Plus,
  AlertCircle,
} from 'lucide-react';

interface UserData {
  name: string;
  email: string;
  role: string;
  avatar?: string;
  twoFactorEnabled: boolean;
}

interface ApiKey {
  id: string;
  name: string;
  key: string;
  createdAt: string;
  lastUsed?: string;
}

interface Session {
  id: string;
  device: string;
  location: string;
  lastActive: string;
  current: boolean;
}

interface UserProfileProps {
  user?: UserData;
  apiKeys?: ApiKey[];
  sessions?: Session[];
  onUpdateProfile?: (data: Partial<UserData>) => void;
  onToggle2FA?: (enabled: boolean) => void;
  onCreateApiKey?: (name: string) => void;
  onDeleteApiKey?: (id: string) => void;
  onRevokeSession?: (id: string) => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({
  user = {
    name: 'John Doe',
    email: 'john.doe@example.com',
    role: 'Admin',
    twoFactorEnabled: false,
  },
  apiKeys = [],
  sessions = [],
  onUpdateProfile,
  onToggle2FA,
  onCreateApiKey,
  onDeleteApiKey,
  onRevokeSession,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState(user.name);
  const [editedEmail, setEditedEmail] = useState(user.email);
  const [showApiKeys, setShowApiKeys] = useState<Record<string, boolean>>({});
  const [newKeyName, setNewKeyName] = useState('');
  const [showNewKeyDialog, setShowNewKeyDialog] = useState(false);

  const handleSaveProfile = () => {
    onUpdateProfile?.({ name: editedName, email: editedEmail });
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditedName(user.name);
    setEditedEmail(user.email);
    setIsEditing(false);
  };

  const handleToggle2FA = () => {
    onToggle2FA?.(!user.twoFactorEnabled);
  };

  const handleCreateApiKey = () => {
    if (newKeyName.trim()) {
      onCreateApiKey?.(newKeyName);
      setNewKeyName('');
      setShowNewKeyDialog(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      Admin: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
      Developer: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      User: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
    };
    return colors[role] || colors.User;
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Profile Information */}
      <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white flex items-center">
            <User className="w-6 h-6 mr-2" />
            Profile Information
          </h2>
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/30 hover:bg-blue-500/30 transition-all flex items-center"
            >
              <Edit2 className="w-4 h-4 mr-2" />
              Edit
            </button>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={handleSaveProfile}
                className="px-4 py-2 rounded-lg bg-green-500/20 text-green-300 border border-green-500/30 hover:bg-green-500/30 transition-all flex items-center"
              >
                <Save className="w-4 h-4 mr-2" />
                Save
              </button>
              <button
                onClick={handleCancelEdit}
                className="px-4 py-2 rounded-lg bg-red-500/20 text-red-300 border border-red-500/30 hover:bg-red-500/30 transition-all flex items-center"
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </button>
            </div>
          )}
        </div>

        <div className="flex items-start gap-6">
          <div className="flex-shrink-0">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-3xl font-bold">
              {user.name.split(' ').map(n => n[0]).join('').toUpperCase()}
            </div>
          </div>

          <div className="flex-1 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              ) : (
                <p className="text-white text-lg">{user.name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
              {isEditing ? (
                <input
                  type="email"
                  value={editedEmail}
                  onChange={(e) => setEditedEmail(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              ) : (
                <p className="text-white text-lg flex items-center">
                  <Mail className="w-4 h-4 mr-2 text-gray-400" />
                  {user.email}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Role</label>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getRoleBadgeColor(user.role)}`}>
                <Shield className="w-4 h-4 mr-1" />
                {user.role}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Two-Factor Authentication */}
      <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center">
          <Shield className="w-5 h-5 mr-2" />
          Two-Factor Authentication
        </h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-300 mb-1">Enhance your account security</p>
            <p className="text-sm text-gray-400">
              {user.twoFactorEnabled
                ? 'Two-factor authentication is enabled'
                : 'Add an extra layer of security to your account'}
            </p>
          </div>
          <button
            onClick={handleToggle2FA}
            className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
              user.twoFactorEnabled ? 'bg-green-500' : 'bg-gray-600'
            }`}
          >
            <span
              className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                user.twoFactorEnabled ? 'translate-x-7' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      {/* API Key Management */}
      <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white flex items-center">
            <Key className="w-5 h-5 mr-2" />
            API Keys
          </h3>
          <button
            onClick={() => setShowNewKeyDialog(!showNewKeyDialog)}
            className="px-4 py-2 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/30 hover:bg-blue-500/30 transition-all flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create New Key
          </button>
        </div>

        {showNewKeyDialog && (
          <div className="mb-4 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-4 h-4 text-blue-400" />
              <h4 className="text-sm font-medium text-blue-300">Create New API Key</h4>
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                placeholder="Key name (e.g., Production API)"
                className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleCreateApiKey}
                className="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors"
              >
                Create
              </button>
              <button
                onClick={() => {
                  setShowNewKeyDialog(false);
                  setNewKeyName('');
                }}
                className="px-4 py-2 rounded-lg bg-white/5 text-gray-300 hover:bg-white/10 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {apiKeys.length === 0 ? (
            <p className="text-gray-400 text-center py-8">No API keys created yet</p>
          ) : (
            apiKeys.map((apiKey) => (
              <div
                key={apiKey.id}
                className="p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-white font-medium">{apiKey.name}</h4>
                  <button
                    onClick={() => onDeleteApiKey?.(apiKey.id)}
                    className="text-red-400 hover:text-red-300 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex items-center gap-2">
                  <code className="flex-1 px-3 py-2 rounded bg-black/20 text-gray-300 text-sm font-mono">
                    {showApiKeys[apiKey.id] ? apiKey.key : '••••••••••••••••••••••••••••••••'}
                  </code>
                  <button
                    onClick={() => setShowApiKeys({ ...showApiKeys, [apiKey.id]: !showApiKeys[apiKey.id] })}
                    className="p-2 rounded bg-white/5 text-gray-300 hover:bg-white/10 transition-colors"
                  >
                    {showApiKeys[apiKey.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => copyToClipboard(apiKey.key)}
                    className="p-2 rounded bg-white/5 text-gray-300 hover:bg-white/10 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
                <div className="mt-2 flex items-center text-xs text-gray-400">
                  <span>Created: {apiKey.createdAt}</span>
                  {apiKey.lastUsed && (
                    <>
                      <span className="mx-2">•</span>
                      <span>Last used: {apiKey.lastUsed}</span>
                    </>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Active Sessions */}
      <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center">
          <Monitor className="w-5 h-5 mr-2" />
          Active Sessions
        </h3>
        <div className="space-y-3">
          {sessions.length === 0 ? (
            <p className="text-gray-400 text-center py-8">No active sessions</p>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`p-4 rounded-lg border ${
                  session.current
                    ? 'bg-green-500/10 border-green-500/30'
                    : 'bg-white/5 border-white/10'
                } hover:bg-white/10 transition-all`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-white font-medium">{session.device}</h4>
                      {session.current && (
                        <span className="px-2 py-0.5 rounded-full bg-green-500/20 text-green-300 text-xs">
                          Current
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-400">{session.location}</p>
                    <p className="text-xs text-gray-500 mt-1">Last active: {session.lastActive}</p>
                  </div>
                  {!session.current && (
                    <button
                      onClick={() => onRevokeSession?.(session.id)}
                      className="px-3 py-1.5 rounded-lg bg-red-500/20 text-red-300 border border-red-500/30 hover:bg-red-500/30 transition-all text-sm"
                    >
                      Revoke
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
