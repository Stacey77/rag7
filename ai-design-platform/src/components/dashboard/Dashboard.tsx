import React from 'react';
import { Activity, Cpu, HardDrive, Zap, AlertTriangle, CheckCircle } from 'lucide-react';
import type { SystemMetrics } from '../../types';

export const Dashboard: React.FC = () => {
  const [metrics] = React.useState<SystemMetrics>({
    cpu: 45,
    memory: 62,
    gpu: 38,
    activeModels: 12,
    totalRequests: 1547890,
    avgLatency: 145,
  });

  const MetricCard: React.FC<{ icon: React.ReactNode; title: string; value: string | number; subtitle: string; trend?: 'up' | 'down' }> = ({
    icon,
    title,
    value,
    subtitle,
  }) => (
    <div className="card-hover">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 text-gray-400 mb-2">
            {icon}
            <span className="text-sm">{title}</span>
          </div>
          <div className="text-3xl font-bold gradient-text mb-1">{value}</div>
          <div className="text-sm text-gray-500">{subtitle}</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Dashboard</h1>
          <p className="text-gray-400">Real-time system monitoring and insights</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">Refresh</button>
          <button className="btn-primary">Deploy Model</button>
        </div>
      </div>

      {/* System Status */}
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <CheckCircle className="w-6 h-6 text-green-400" />
          <div>
            <h2 className="text-xl font-bold">System Healthy</h2>
            <p className="text-sm text-gray-400">All services operational</p>
          </div>
        </div>
        <div className="flex gap-4 mt-4">
          <div className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>API Service</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>Database</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>ML Pipeline</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
            <span>Cache (Degraded)</span>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          icon={<Cpu className="w-5 h-5" />}
          title="CPU Usage"
          value={`${metrics.cpu}%`}
          subtitle="4 cores active"
        />
        <MetricCard
          icon={<HardDrive className="w-5 h-5" />}
          title="Memory"
          value={`${metrics.memory}%`}
          subtitle="24.8 GB / 40 GB"
        />
        <MetricCard
          icon={<Zap className="w-5 h-5" />}
          title="GPU Usage"
          value={`${metrics.gpu}%`}
          subtitle="NVIDIA A100"
        />
        <MetricCard
          icon={<Activity className="w-5 h-5" />}
          title="Active Models"
          value={metrics.activeModels}
          subtitle="12 deployed, 3 training"
        />
      </div>

      {/* Resource Usage */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Resource Monitoring</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>CPU Utilization</span>
              <span className="text-gray-400">{metrics.cpu}%</span>
            </div>
            <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-purple-500 to-blue-500" style={{ width: `${metrics.cpu}%` }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Memory Usage</span>
              <span className="text-gray-400">{metrics.memory}%</span>
            </div>
            <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-purple-500 to-blue-500" style={{ width: `${metrics.memory}%` }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>GPU Processing</span>
              <span className="text-gray-400">{metrics.gpu}%</span>
            </div>
            <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-purple-500 to-blue-500" style={{ width: `${metrics.gpu}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h4 className="text-sm text-gray-400 mb-2">Total Requests</h4>
          <div className="text-2xl font-bold">{metrics.totalRequests.toLocaleString()}</div>
          <div className="text-xs text-green-400 mt-1">↑ 12% from last week</div>
        </div>
        <div className="card">
          <h4 className="text-sm text-gray-400 mb-2">Avg Latency</h4>
          <div className="text-2xl font-bold">{metrics.avgLatency}ms</div>
          <div className="text-xs text-green-400 mt-1">↓ 8% improvement</div>
        </div>
        <div className="card">
          <h4 className="text-sm text-gray-400 mb-2">System Uptime</h4>
          <div className="text-2xl font-bold">99.98%</div>
          <div className="text-xs text-gray-400 mt-1">Last 30 days</div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Recent Alerts</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
            <div className="flex-1">
              <div className="font-medium">Cache Performance Degraded</div>
              <div className="text-sm text-gray-400">Redis cluster experiencing high latency</div>
            </div>
            <span className="text-xs text-gray-500">5m ago</span>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <div className="flex-1">
              <div className="font-medium">Model Training Complete</div>
              <div className="text-sm text-gray-400">fraud-detection-v2 ready for deployment</div>
            </div>
            <span className="text-xs text-gray-500">15m ago</span>
          </div>
        </div>
      </div>
    </div>
  );
};
