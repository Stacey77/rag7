import React from 'react';
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, Activity, Zap, Clock } from 'lucide-react';

export const Analytics: React.FC = () => {
  const requestTrendData = [
    { time: '00:00', requests: 1200, latency: 120 },
    { time: '04:00', requests: 800, latency: 110 },
    { time: '08:00', requests: 2400, latency: 150 },
    { time: '12:00', requests: 3200, latency: 180 },
    { time: '16:00', requests: 2800, latency: 160 },
    { time: '20:00', requests: 1800, latency: 130 },
  ];

  const modelPerformanceData = [
    { model: 'Fraud Det.', accuracy: 98.5, requests: 45000 },
    { model: 'Sentiment', accuracy: 94.2, requests: 38000 },
    { model: 'Recommend', accuracy: 96.7, requests: 52000 },
    { model: 'Image Class.', accuracy: 97.3, requests: 29000 },
    { model: 'Price Opt.', accuracy: 91.8, requests: 15000 },
  ];

  const latencyDistributionData = [
    { range: '0-50ms', count: 45000 },
    { range: '50-100ms', count: 82000 },
    { range: '100-150ms', count: 124000 },
    { range: '150-200ms', count: 68000 },
    { range: '200-250ms', count: 32000 },
    { range: '250+ms', count: 12000 },
  ];

  const dailyMetricsData = [
    { date: 'Mon', requests: 125000, errors: 240, avgLatency: 145 },
    { date: 'Tue', requests: 132000, errors: 180, avgLatency: 138 },
    { date: 'Wed', requests: 145000, errors: 210, avgLatency: 152 },
    { date: 'Thu', requests: 138000, errors: 165, avgLatency: 141 },
    { date: 'Fri', requests: 156000, errors: 195, avgLatency: 148 },
    { date: 'Sat', requests: 98000, errors: 120, avgLatency: 135 },
    { date: 'Sun', requests: 87000, errors: 98, avgLatency: 128 },
  ];

  const MetricCard: React.FC<{ icon: React.ReactNode; title: string; value: string; change: string; trend: 'up' | 'down' }> = ({
    icon,
    title,
    value,
    change,
    trend,
  }) => (
    <div className="card-hover">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 text-gray-400 mb-2">
            {icon}
            <span className="text-sm">{title}</span>
          </div>
          <div className="text-3xl font-bold gradient-text mb-1">{value}</div>
          <div className={`text-sm flex items-center gap-1 ${trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
            <TrendingUp className={`w-4 h-4 ${trend === 'down' ? 'rotate-180' : ''}`} />
            {change}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Analytics</h1>
          <p className="text-gray-400">Performance metrics and insights</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">Last 7 Days</button>
          <button className="btn-primary">Export Report</button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          icon={<Activity className="w-5 h-5" />}
          title="Total Requests"
          value="1.2M"
          change="+15.3% vs last week"
          trend="up"
        />
        <MetricCard
          icon={<Clock className="w-5 h-5" />}
          title="Avg Latency"
          value="142ms"
          change="-8.2% improvement"
          trend="down"
        />
        <MetricCard
          icon={<Zap className="w-5 h-5" />}
          title="Success Rate"
          value="99.8%"
          change="+0.3% increase"
          trend="up"
        />
        <MetricCard
          icon={<TrendingUp className="w-5 h-5" />}
          title="Throughput"
          value="2.4K/s"
          change="+22.1% growth"
          trend="up"
        />
      </div>

      {/* Request Trends */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Request Trends (24h)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={requestTrendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#F3F4F6',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="requests"
              stroke="#8B5CF6"
              strokeWidth={2}
              dot={{ fill: '#8B5CF6' }}
              name="Requests"
            />
            <Line
              type="monotone"
              dataKey="latency"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={{ fill: '#3B82F6' }}
              name="Latency (ms)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Performance */}
        <div className="card">
          <h3 className="text-lg font-bold mb-4">Model Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={modelPerformanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="model" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F3F4F6',
                }}
              />
              <Legend />
              <Bar dataKey="accuracy" fill="#8B5CF6" name="Accuracy %" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Latency Distribution */}
        <div className="card">
          <h3 className="text-lg font-bold mb-4">Latency Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={latencyDistributionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="range" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F3F4F6',
                }}
              />
              <Area
                type="monotone"
                dataKey="count"
                stroke="#3B82F6"
                fill="url(#colorCount)"
                name="Requests"
              />
              <defs>
                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1} />
                </linearGradient>
              </defs>
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Daily Metrics */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Weekly Overview</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={dailyMetricsData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#F3F4F6',
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="requests"
              stroke="#8B5CF6"
              fill="url(#colorRequests)"
              name="Requests"
            />
            <Area
              type="monotone"
              dataKey="errors"
              stroke="#EF4444"
              fill="url(#colorErrors)"
              name="Errors"
            />
            <defs>
              <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="colorErrors" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#EF4444" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#EF4444" stopOpacity={0.1} />
              </linearGradient>
            </defs>
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Performance Insights */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Performance Insights</h3>
        <div className="space-y-4">
          <div className="flex items-start gap-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
            <TrendingUp className="w-5 h-5 text-green-400 mt-0.5" />
            <div className="flex-1">
              <div className="font-medium text-green-400">Recommendation Engine Performing Well</div>
              <div className="text-sm text-gray-400 mt-1">
                52K requests with 96.7% accuracy and avg latency of 95ms
              </div>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <Activity className="w-5 h-5 text-blue-400 mt-0.5" />
            <div className="flex-1">
              <div className="font-medium text-blue-400">Peak Traffic Period</div>
              <div className="text-sm text-gray-400 mt-1">
                Highest request volume observed between 12:00-16:00 daily
              </div>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
            <Zap className="w-5 h-5 text-purple-400 mt-0.5" />
            <div className="flex-1">
              <div className="font-medium text-purple-400">Latency Optimization Opportunity</div>
              <div className="text-sm text-gray-400 mt-1">
                12K requests exceed 250ms - consider optimizing model inference
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
