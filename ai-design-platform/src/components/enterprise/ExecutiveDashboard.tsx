import React, { useState } from 'react';
import { 
  TrendingUp, 
  DollarSign, 
  Users, 
  Zap, 
  Activity,
  BarChart3,
  Target,
  Award,
  ChevronUp,
  ChevronDown,
  Calendar
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

interface KPI {
  title: string;
  value: string;
  change: number;
  trend: 'up' | 'down';
  icon: React.ReactNode;
  color: string;
}

interface DepartmentMetrics {
  name: string;
  usage: number;
  models: number;
  roi: number;
}

export const ExecutiveDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'quarter'>('month');

  const kpis: KPI[] = [
    {
      title: 'Revenue Impact',
      value: '$2.4M',
      change: 23.5,
      trend: 'up',
      icon: <DollarSign className="w-6 h-6" />,
      color: 'from-green-500 to-emerald-500'
    },
    {
      title: 'Cost Savings',
      value: '$840K',
      change: 18.2,
      trend: 'up',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'from-blue-500 to-cyan-500'
    },
    {
      title: 'Team Productivity',
      value: '+34%',
      change: 12.8,
      trend: 'up',
      icon: <Zap className="w-6 h-6" />,
      color: 'from-purple-500 to-pink-500'
    },
    {
      title: 'Active Users',
      value: '1,247',
      change: 8.4,
      trend: 'up',
      icon: <Users className="w-6 h-6" />,
      color: 'from-orange-500 to-red-500'
    }
  ];

  const departmentData: DepartmentMetrics[] = [
    { name: 'Sales', usage: 92, models: 8, roi: 340 },
    { name: 'Marketing', usage: 87, models: 12, roi: 285 },
    { name: 'Operations', usage: 78, models: 6, roi: 410 },
    { name: 'Finance', usage: 95, models: 5, roi: 520 },
    { name: 'Customer Service', usage: 88, models: 9, roi: 295 },
    { name: 'R&D', usage: 71, models: 15, roi: 180 }
  ];

  const revenueData = [
    { month: 'Jan', ai: 180, manual: 120 },
    { month: 'Feb', ai: 220, manual: 125 },
    { month: 'Mar', ai: 280, manual: 130 },
    { month: 'Apr', ai: 340, manual: 128 },
    { month: 'May', ai: 420, manual: 132 },
    { month: 'Jun', ai: 510, manual: 135 }
  ];

  const modelPerformance = [
    { name: 'Excellent', value: 45, color: '#10b981' },
    { name: 'Good', value: 35, color: '#3b82f6' },
    { name: 'Average', value: 15, color: '#f59e0b' },
    { name: 'Needs Review', value: 5, color: '#ef4444' }
  ];

  const achievements = [
    {
      title: 'Revenue Milestone',
      description: 'Exceeded $2M AI-driven revenue',
      date: '2 days ago',
      icon: <Target className="w-5 h-5 text-green-400" />,
      color: 'border-green-500/30 bg-green-500/10'
    },
    {
      title: 'Enterprise Adoption',
      description: '1,000+ active users achieved',
      date: '1 week ago',
      icon: <Users className="w-5 h-5 text-blue-400" />,
      color: 'border-blue-500/30 bg-blue-500/10'
    },
    {
      title: 'Model Excellence',
      description: '95% model accuracy across platform',
      date: '2 weeks ago',
      icon: <Award className="w-5 h-5 text-purple-400" />,
      color: 'border-purple-500/30 bg-purple-500/10'
    }
  ];

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Executive Dashboard</h1>
          <p className="text-gray-400">Strategic overview of AI platform performance</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 glass rounded-lg p-1">
            {(['week', 'month', 'quarter'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  timeRange === range
                    ? 'bg-gradient-to-r from-purple-600 to-blue-500 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {range.charAt(0).toUpperCase() + range.slice(1)}
              </button>
            ))}
          </div>
          <button className="btn-secondary flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Custom Range
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, index) => (
          <div key={index} className="card relative overflow-hidden group">
            <div className={`absolute inset-0 bg-gradient-to-br ${kpi.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
            <div className="relative">
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-xl bg-gradient-to-br ${kpi.color}`}>
                  {kpi.icon}
                </div>
                <div className={`flex items-center gap-1 text-sm font-medium ${
                  kpi.trend === 'up' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {kpi.trend === 'up' ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                  {kpi.change}%
                </div>
              </div>
              <div className="text-sm text-gray-400 mb-1">{kpi.title}</div>
              <div className="text-3xl font-bold text-white">{kpi.value}</div>
              <div className="text-xs text-gray-500 mt-2">vs. previous {timeRange}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Comparison */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-white mb-1">Revenue Impact</h2>
              <p className="text-sm text-gray-400">AI-driven vs. Manual processes</p>
            </div>
            <BarChart3 className="w-5 h-5 text-gray-400" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="month" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Bar dataKey="ai" name="AI-Driven" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
              <Bar dataKey="manual" name="Manual" fill="#6b7280" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Model Performance */}
        <div className="card">
          <div className="mb-6">
            <h2 className="text-xl font-bold text-white mb-1">Model Performance</h2>
            <p className="text-sm text-gray-400">Quality distribution</p>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={modelPerformance}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {modelPerformance.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 mt-4">
            {modelPerformance.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-gray-300">{item.name}</span>
                </div>
                <span className="font-semibold text-white">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Department Analytics */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-white mb-1">Department Analytics</h2>
            <p className="text-sm text-gray-400">Usage and ROI by business unit</p>
          </div>
          <Activity className="w-5 h-5 text-gray-400" />
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Department</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Usage</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Active Models</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">ROI</th>
              </tr>
            </thead>
            <tbody>
              {departmentData.map((dept, idx) => (
                <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="py-4 px-4">
                    <span className="font-medium text-white">{dept.name}</span>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-gray-800 rounded-full h-2 max-w-[120px]">
                        <div 
                          className="h-full rounded-full bg-gradient-to-r from-purple-500 to-blue-500"
                          style={{ width: `${dept.usage}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-300 w-12">
                        {dept.usage}%
                      </span>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <span className="text-sm font-medium text-gray-300">{dept.models}</span>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`text-sm font-semibold ${
                      dept.roi > 400 ? 'text-green-400' :
                      dept.roi > 250 ? 'text-blue-400' : 'text-yellow-400'
                    }`}>
                      {dept.roi}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Strategic Achievements */}
      <div className="card">
        <div className="mb-6">
          <h2 className="text-xl font-bold text-white mb-1">Strategic Achievements</h2>
          <p className="text-sm text-gray-400">Recent milestones and accomplishments</p>
        </div>
        <div className="space-y-3">
          {achievements.map((achievement, idx) => (
            <div 
              key={idx}
              className={`p-4 rounded-lg border transition-all duration-300 hover:scale-[1.02] ${achievement.color}`}
            >
              <div className="flex items-start gap-4">
                <div className="p-2 bg-white/10 rounded-lg">
                  {achievement.icon}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-white mb-1">{achievement.title}</h3>
                  <p className="text-sm text-gray-400 mb-2">{achievement.description}</p>
                  <span className="text-xs text-gray-500">{achievement.date}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
