import React from 'react';
import { Users, Activity, Clock, MessageSquare, GitBranch, CheckCircle } from 'lucide-react';
import type { TeamMember } from '../../types';

interface ActiveSession {
  id: string;
  userId: string;
  activity: string;
  resource: string;
  startedAt: Date;
}

interface ActivityItem {
  id: string;
  userId: string;
  userName: string;
  action: string;
  target: string;
  timestamp: Date;
}

export const Collaboration: React.FC = () => {
  const [teamMembers] = React.useState<TeamMember[]>([
    {
      id: '1',
      name: 'Sarah Chen',
      role: 'ML Engineer',
      avatar: '👩‍💻',
      status: 'online',
      lastActive: new Date(),
    },
    {
      id: '2',
      name: 'Marcus Rodriguez',
      role: 'Data Scientist',
      avatar: '👨‍🔬',
      status: 'online',
      lastActive: new Date(),
    },
    {
      id: '3',
      name: 'Emily Watson',
      role: 'DevOps Engineer',
      avatar: '👩‍💼',
      status: 'busy',
      lastActive: new Date(Date.now() - 300000),
    },
    {
      id: '4',
      name: 'David Kim',
      role: 'Product Manager',
      avatar: '👨‍💼',
      status: 'online',
      lastActive: new Date(),
    },
    {
      id: '5',
      name: 'Lisa Anderson',
      role: 'ML Engineer',
      avatar: '👩‍🎓',
      status: 'offline',
      lastActive: new Date(Date.now() - 3600000),
    },
    {
      id: '6',
      name: 'Alex Johnson',
      role: 'Data Engineer',
      avatar: '👨‍🎨',
      status: 'online',
      lastActive: new Date(),
    },
  ]);

  const [activeSessions] = React.useState<ActiveSession[]>([
    {
      id: '1',
      userId: '1',
      activity: 'Training Model',
      resource: 'fraud-detection-v4',
      startedAt: new Date(Date.now() - 1800000),
    },
    {
      id: '2',
      userId: '2',
      activity: 'Reviewing Data',
      resource: 'customer-dataset-2024',
      startedAt: new Date(Date.now() - 900000),
    },
    {
      id: '3',
      userId: '3',
      activity: 'Deploying Model',
      resource: 'recommendation-engine-v3',
      startedAt: new Date(Date.now() - 600000),
    },
    {
      id: '4',
      userId: '4',
      activity: 'Monitoring Metrics',
      resource: 'production-dashboard',
      startedAt: new Date(Date.now() - 300000),
    },
  ]);

  const [activityFeed] = React.useState<ActivityItem[]>([
    {
      id: '1',
      userId: '1',
      userName: 'Sarah Chen',
      action: 'deployed',
      target: 'fraud-detection-v3',
      timestamp: new Date(Date.now() - 300000),
    },
    {
      id: '2',
      userId: '3',
      userName: 'Emily Watson',
      action: 'updated configuration for',
      target: 'API Gateway',
      timestamp: new Date(Date.now() - 600000),
    },
    {
      id: '3',
      userId: '2',
      userName: 'Marcus Rodriguez',
      action: 'completed training for',
      target: 'sentiment-analysis-v2',
      timestamp: new Date(Date.now() - 900000),
    },
    {
      id: '4',
      userId: '4',
      userName: 'David Kim',
      action: 'created playbook',
      target: 'Q1 Model Deployment Plan',
      timestamp: new Date(Date.now() - 1200000),
    },
    {
      id: '5',
      userId: '6',
      userName: 'Alex Johnson',
      action: 'optimized pipeline',
      target: 'data-ingestion-pipeline',
      timestamp: new Date(Date.now() - 1800000),
    },
    {
      id: '6',
      userId: '1',
      userName: 'Sarah Chen',
      action: 'reviewed pull request',
      target: 'Feature: Add model versioning',
      timestamp: new Date(Date.now() - 2400000),
    },
  ]);

  const getStatusColor = (status: TeamMember['status']) => {
    switch (status) {
      case 'online':
        return 'bg-green-400';
      case 'busy':
        return 'bg-yellow-400';
      case 'offline':
        return 'bg-gray-400';
    }
  };

  const getStatusText = (status: TeamMember['status']) => {
    switch (status) {
      case 'online':
        return 'Online';
      case 'busy':
        return 'Busy';
      case 'offline':
        return 'Offline';
    }
  };

  const getRoleBadgeColor = (role: string) => {
    if (role.includes('Engineer')) return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    if (role.includes('Scientist')) return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    if (role.includes('Manager')) return 'bg-green-500/10 text-green-400 border-green-500/20';
    return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
  };

  const getTimeAgo = (date: Date) => {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  const onlineMembers = teamMembers.filter(m => m.status === 'online').length;
  const busyMembers = teamMembers.filter(m => m.status === 'busy').length;

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Team Collaboration</h1>
          <p className="text-gray-400">Real-time team activity and collaboration</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">Team Settings</button>
          <button className="btn-primary">Invite Member</button>
        </div>
      </div>

      {/* Team Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-5 h-5 text-purple-400" />
            <span className="text-sm text-gray-400">Total Members</span>
          </div>
          <div className="text-2xl font-bold">{teamMembers.length}</div>
          <div className="text-xs text-gray-500 mt-1">Across all teams</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-400">Active Now</span>
          </div>
          <div className="text-2xl font-bold text-green-400">{onlineMembers}</div>
          <div className="text-xs text-gray-500 mt-1">{busyMembers} busy</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-5 h-5 text-blue-400" />
            <span className="text-sm text-gray-400">Active Sessions</span>
          </div>
          <div className="text-2xl font-bold">{activeSessions.length}</div>
          <div className="text-xs text-gray-500 mt-1">In progress</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Team Members */}
        <div className="card">
          <h3 className="text-lg font-bold mb-4">Team Members</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {teamMembers.map(member => (
              <div key={member.id} className="card-hover p-4">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-2xl">
                      {member.avatar}
                    </div>
                    <div
                      className={`absolute -bottom-1 -right-1 w-4 h-4 ${getStatusColor(
                        member.status
                      )} rounded-full border-2 border-gray-900`}
                    ></div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{member.name}</span>
                      <span
                        className={`px-2 py-0.5 rounded-md text-xs border ${getRoleBadgeColor(
                          member.role
                        )}`}
                      >
                        {member.role}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-sm text-gray-400">
                      <span>{getStatusText(member.status)}</span>
                      {member.status !== 'online' && (
                        <>
                          <span>•</span>
                          <span>{getTimeAgo(member.lastActive)}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <button className="btn-secondary text-sm">
                    <MessageSquare className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Sessions */}
        <div className="card">
          <h3 className="text-lg font-bold mb-4">Active Sessions</h3>
          <div className="space-y-3">
            {activeSessions.map(session => {
              const member = teamMembers.find(m => m.id === session.userId);
              return (
                <div key={session.id} className="card-hover p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-xl flex-shrink-0">
                      {member?.avatar}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm">{member?.name}</span>
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                      </div>
                      <div className="text-sm text-gray-400">{session.activity}</div>
                      <div className="flex items-center gap-2 mt-2">
                        <GitBranch className="w-3 h-3 text-gray-500" />
                        <span className="text-xs text-gray-500 truncate">{session.resource}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-gray-500 flex-shrink-0">
                      <Clock className="w-3 h-3" />
                      <span>{getTimeAgo(session.startedAt)}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Activity Feed */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold">Activity Feed</h3>
          <button className="text-sm text-purple-400 hover:text-purple-300">View All</button>
        </div>
        <div className="space-y-3">
          {activityFeed.map(activity => {
            const member = teamMembers.find(m => m.id === activity.userId);
            return (
              <div key={activity.id} className="flex items-start gap-3 pb-3 border-b border-gray-800 last:border-0">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-sm flex-shrink-0">
                  {member?.avatar}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm">
                    <span className="font-medium">{activity.userName}</span>
                    <span className="text-gray-400"> {activity.action} </span>
                    <span className="font-medium text-purple-400">{activity.target}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    <span>{getTimeAgo(activity.timestamp)}</span>
                  </div>
                </div>
                <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
              </div>
            );
          })}
        </div>
      </div>

      {/* Collaboration Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h4 className="text-sm text-gray-400 mb-2">Models Deployed Today</h4>
          <div className="text-2xl font-bold">8</div>
          <div className="text-xs text-green-400 mt-1">↑ 25% from yesterday</div>
        </div>
        <div className="card">
          <h4 className="text-sm text-gray-400 mb-2">Active Pull Requests</h4>
          <div className="text-2xl font-bold">12</div>
          <div className="text-xs text-gray-400 mt-1">4 awaiting review</div>
        </div>
        <div className="card">
          <h4 className="text-sm text-gray-400 mb-2">Team Contributions</h4>
          <div className="text-2xl font-bold">47</div>
          <div className="text-xs text-gray-400 mt-1">This week</div>
        </div>
      </div>
    </div>
  );
};
