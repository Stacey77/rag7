import React, { useState } from 'react';
import { 
  Users, 
  MessageSquare,
  Video,
  Clock,
  GitBranch,
  Eye,
  Lock,
  CheckCircle,
  Code,
  User,
  Send,
  MoreVertical,
  Edit,
  Share2
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

interface TeamMember {
  id: string;
  name: string;
  avatar: string;
  status: 'online' | 'away' | 'offline';
  role: string;
  currentFile?: string;
}

interface Comment {
  id: string;
  author: string;
  content: string;
  timestamp: Date;
  lineNumber?: number;
  resolved: boolean;
}

interface Version {
  id: string;
  timestamp: Date;
  author: string;
  message: string;
  changes: number;
}

interface ChatMessage {
  id: string;
  author: string;
  message: string;
  timestamp: Date;
}

export const CollaborationWorkspace: React.FC = () => {
  const [code, setCode] = useState(`import React from 'react';

export const AIModel = () => {
  const [result, setResult] = useState(null);
  
  const runInference = async (input) => {
    const response = await fetch('/api/inference', {
      method: 'POST',
      body: JSON.stringify({ input })
    });
    const data = await response.json();
    setResult(data);
  };
  
  return (
    <div className="model-container">
      <h1>AI Model Interface</h1>
      {/* Add your UI here */}
    </div>
  );
};`);

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { id: '1', author: 'Sarah Chen', message: 'Updated the inference endpoint', timestamp: new Date('2024-01-22T10:30:00') },
    { id: '2', author: 'Mike Johnson', message: 'Looks good! Can you add error handling?', timestamp: new Date('2024-01-22T10:32:00') },
    { id: '3', author: 'Sarah Chen', message: 'Will do, working on it now', timestamp: new Date('2024-01-22T10:33:00') }
  ]);

  const [newMessage, setNewMessage] = useState('');

  const teamMembers: TeamMember[] = [
    { id: '1', name: 'Sarah Chen', avatar: 'SC', status: 'online', role: 'Lead Developer', currentFile: 'AIModel.tsx' },
    { id: '2', name: 'Mike Johnson', avatar: 'MJ', status: 'online', role: 'ML Engineer', currentFile: 'model.py' },
    { id: '3', name: 'Emma Wilson', avatar: 'EW', status: 'away', role: 'Data Scientist' },
    { id: '4', name: 'Alex Kumar', avatar: 'AK', status: 'online', role: 'DevOps' },
    { id: '5', name: 'Lisa Park', avatar: 'LP', status: 'offline', role: 'Product Manager' }
  ];

  const comments: Comment[] = [
    { id: '1', author: 'Mike Johnson', content: 'Should we add type checking here?', timestamp: new Date('2024-01-22T09:15:00'), lineNumber: 5, resolved: false },
    { id: '2', author: 'Emma Wilson', content: 'Consider using async/await wrapper', timestamp: new Date('2024-01-22T09:45:00'), lineNumber: 8, resolved: true },
    { id: '3', author: 'Alex Kumar', content: 'Add rate limiting to this endpoint', timestamp: new Date('2024-01-22T10:00:00'), lineNumber: 7, resolved: false }
  ];

  const versionHistory: Version[] = [
    { id: '1', timestamp: new Date('2024-01-22T10:30:00'), author: 'Sarah Chen', message: 'Update inference endpoint', changes: 12 },
    { id: '2', timestamp: new Date('2024-01-22T09:45:00'), author: 'Mike Johnson', message: 'Add error handling', changes: 8 },
    { id: '3', timestamp: new Date('2024-01-22T09:00:00'), author: 'Emma Wilson', message: 'Optimize model loading', changes: 15 },
    { id: '4', timestamp: new Date('2024-01-22T08:30:00'), author: 'Sarah Chen', message: 'Initial model implementation', changes: 45 }
  ];

  const activityData = [
    { time: '09:00', commits: 2, reviews: 1, comments: 3 },
    { time: '10:00', commits: 5, reviews: 3, comments: 7 },
    { time: '11:00', commits: 3, reviews: 2, comments: 5 },
    { time: '12:00', commits: 1, reviews: 1, comments: 2 },
    { time: '13:00', commits: 4, reviews: 2, comments: 6 },
    { time: '14:00', commits: 6, reviews: 4, comments: 8 }
  ];

  const getStatusColor = (status: TeamMember['status']) => {
    switch (status) {
      case 'online': return 'bg-green-400';
      case 'away': return 'bg-yellow-400';
      case 'offline': return 'bg-gray-400';
    }
  };

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      setChatMessages([...chatMessages, {
        id: String(chatMessages.length + 1),
        author: 'You',
        message: newMessage,
        timestamp: new Date()
      }]);
      setNewMessage('');
    }
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Collaboration Workspace</h1>
          <p className="text-gray-400">Real-time team collaboration on AI projects</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </button>
          <button className="btn-primary">
            <Video className="w-4 h-4 mr-2" />
            Start Call
          </button>
        </div>
      </div>

      {/* Team Presence Bar */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-purple-400" />
              <span className="font-semibold">Team ({teamMembers.filter(m => m.status === 'online').length} online)</span>
            </div>
            <div className="flex -space-x-2">
              {teamMembers.map((member) => (
                <div
                  key={member.id}
                  className="relative"
                  title={`${member.name} - ${member.status}`}
                >
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white font-semibold border-2 border-gray-900">
                    {member.avatar}
                  </div>
                  <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-gray-900 ${getStatusColor(member.status)}`} />
                </div>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Video className="w-4 h-4" />
            <span>Screen sharing: Off</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Code Editor & Comments */}
        <div className="lg:col-span-2 space-y-6">
          {/* Live Code Editor */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Code className="w-5 h-5 text-purple-400" />
                <h2 className="text-xl font-semibold">AIModel.tsx</h2>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex -space-x-1">
                  {teamMembers.slice(0, 2).map((member) => (
                    <div
                      key={member.id}
                      className="w-6 h-6 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-xs border-2 border-gray-900"
                      title={member.name}
                    >
                      {member.avatar[0]}
                    </div>
                  ))}
                </div>
                <span className="text-xs text-gray-400">2 editing</span>
              </div>
            </div>

            <div className="relative">
              <div className="absolute top-2 right-2 flex gap-2">
                <button className="btn-secondary text-xs">
                  <Edit className="w-3 h-3 mr-1" />
                  Format
                </button>
                <button className="btn-secondary text-xs">
                  <Eye className="w-3 h-3 mr-1" />
                  Preview
                </button>
              </div>
              
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full bg-gray-950 border border-white/10 rounded-lg px-4 py-3 text-white font-mono text-sm"
                rows={20}
                style={{ tabSize: 2 }}
              />

              {/* Line Indicators for collaborators */}
              <div className="absolute left-0 top-3 w-1 h-6 bg-purple-500 rounded-r" title="Sarah Chen editing" />
              <div className="absolute left-0 top-16 w-1 h-6 bg-blue-500 rounded-r" title="Mike Johnson viewing" />
            </div>

            <div className="mt-3 flex items-center gap-4 text-xs text-gray-400">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span>Auto-save enabled</span>
              </div>
              <span>Last saved: 2 minutes ago</span>
            </div>
          </div>

          {/* Comments & Annotations */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <MessageSquare className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Comments & Annotations</h2>
            </div>

            <div className="space-y-3">
              {comments.map((comment) => (
                <div
                  key={comment.id}
                  className={`glass rounded-lg p-4 ${comment.resolved ? 'opacity-50' : ''}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-purple-400" />
                      <span className="font-medium text-sm">{comment.author}</span>
                      {comment.lineNumber && (
                        <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded">
                          Line {comment.lineNumber}
                        </span>
                      )}
                    </div>
                    {comment.resolved && (
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    )}
                  </div>
                  <p className="text-sm text-gray-300 mb-2">{comment.content}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {comment.timestamp.toLocaleTimeString()}
                    </span>
                    {!comment.resolved && (
                      <button className="text-xs text-purple-400 hover:text-purple-300">
                        Resolve
                      </button>
                    )}
                  </div>
                </div>
              ))}

              <div className="glass rounded-lg p-3">
                <input
                  type="text"
                  placeholder="Add a comment..."
                  className="w-full bg-transparent border-none text-white text-sm focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Activity Chart */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Clock className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Team Activity</h2>
            </div>

            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={activityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="time" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }} 
                />
                <Line type="monotone" dataKey="commits" stroke="#8B5CF6" strokeWidth={2} name="Commits" />
                <Line type="monotone" dataKey="reviews" stroke="#3B82F6" strokeWidth={2} name="Reviews" />
                <Line type="monotone" dataKey="comments" stroke="#10B981" strokeWidth={2} name="Comments" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Team Members */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Users className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Team</h2>
            </div>

            <div className="space-y-2">
              {teamMembers.map((member) => (
                <div key={member.id} className="glass rounded-lg p-3 hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white font-semibold">
                        {member.avatar}
                      </div>
                      <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-gray-800 ${getStatusColor(member.status)}`} />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">{member.name}</div>
                      <div className="text-xs text-gray-400">{member.role}</div>
                      {member.currentFile && (
                        <div className="text-xs text-purple-400 mt-1 flex items-center gap-1">
                          <Eye className="w-3 h-3" />
                          {member.currentFile}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chat */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <MessageSquare className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Team Chat</h2>
            </div>

            <div className="space-y-3 mb-4 max-h-80 overflow-y-auto">
              {chatMessages.map((msg) => (
                <div key={msg.id} className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{msg.author}</span>
                    <span className="text-xs text-gray-500">
                      {msg.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="glass rounded-lg p-2 text-sm text-gray-300">
                    {msg.message}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type a message..."
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
              />
              <button onClick={handleSendMessage} className="btn-primary">
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Version History */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <GitBranch className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Version History</h2>
            </div>

            <div className="space-y-2 max-h-80 overflow-y-auto">
              {versionHistory.map((version) => (
                <div key={version.id} className="glass rounded-lg p-3 hover:bg-white/10 transition-colors cursor-pointer">
                  <div className="flex items-start justify-between mb-1">
                    <span className="font-medium text-sm">{version.message}</span>
                    <button className="text-gray-400 hover:text-white">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="text-xs text-gray-400">
                    {version.author} · {version.timestamp.toLocaleTimeString()}
                  </div>
                  <div className="text-xs text-purple-400 mt-1">
                    {version.changes} changes
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Permissions */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Lock className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Permissions</h2>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">View Access</div>
                  <div className="text-xs text-gray-400">Who can view this project</div>
                </div>
                <select className="bg-white/5 border border-white/10 rounded-lg px-3 py-1 text-white text-sm">
                  <option>Team Only</option>
                  <option>Organization</option>
                  <option>Public</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">Edit Access</div>
                  <div className="text-xs text-gray-400">Who can make changes</div>
                </div>
                <select className="bg-white/5 border border-white/10 rounded-lg px-3 py-1 text-white text-sm">
                  <option>Admins Only</option>
                  <option>Team Members</option>
                  <option>Everyone</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">Share Externally</div>
                  <div className="text-xs text-gray-400">Allow external sharing</div>
                </div>
                <button className="px-3 py-1 bg-purple-500 text-white rounded-lg text-sm">
                  Enabled
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
