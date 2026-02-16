import React from 'react';
import { CheckCircle, AlertCircle, XCircle, Server, Database, Cpu, Network, HardDrive, Bell, Activity, Terminal } from 'lucide-react';

interface ServiceHealth {
  id: string;
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  uptime: number;
  responseTime: number;
  lastCheck: Date;
}

interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'warning' | 'error';
  service: string;
  message: string;
}

interface Alert {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  resolved: boolean;
}

export const Monitoring: React.FC = () => {
  const [services] = React.useState<ServiceHealth[]>([
    {
      id: '1',
      name: 'API Gateway',
      status: 'healthy',
      uptime: 99.98,
      responseTime: 45,
      lastCheck: new Date(),
    },
    {
      id: '2',
      name: 'ML Pipeline',
      status: 'healthy',
      uptime: 99.95,
      responseTime: 120,
      lastCheck: new Date(),
    },
    {
      id: '3',
      name: 'Database Cluster',
      status: 'healthy',
      uptime: 99.99,
      responseTime: 12,
      lastCheck: new Date(),
    },
    {
      id: '4',
      name: 'Cache Service',
      status: 'degraded',
      uptime: 98.5,
      responseTime: 280,
      lastCheck: new Date(),
    },
    {
      id: '5',
      name: 'Message Queue',
      status: 'healthy',
      uptime: 99.97,
      responseTime: 8,
      lastCheck: new Date(),
    },
    {
      id: '6',
      name: 'Storage Service',
      status: 'healthy',
      uptime: 99.96,
      responseTime: 55,
      lastCheck: new Date(),
    },
  ]);

  const [logs] = React.useState<LogEntry[]>([
    {
      id: '1',
      timestamp: new Date(Date.now() - 30000),
      level: 'info',
      service: 'API Gateway',
      message: 'Request processed successfully - /api/v1/predict',
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 45000),
      level: 'warning',
      service: 'Cache Service',
      message: 'High latency detected - response time: 280ms',
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 60000),
      level: 'info',
      service: 'ML Pipeline',
      message: 'Model training completed - fraud-detection-v3',
    },
    {
      id: '4',
      timestamp: new Date(Date.now() - 90000),
      level: 'error',
      service: 'Database Cluster',
      message: 'Connection pool exhausted - attempting recovery',
    },
    {
      id: '5',
      timestamp: new Date(Date.now() - 120000),
      level: 'info',
      service: 'Message Queue',
      message: 'Queue processed - 1247 messages handled',
    },
    {
      id: '6',
      timestamp: new Date(Date.now() - 150000),
      level: 'warning',
      service: 'Storage Service',
      message: 'Disk usage at 75% - cleanup recommended',
    },
  ]);

  const [alerts] = React.useState<Alert[]>([
    {
      id: '1',
      severity: 'warning',
      title: 'Cache Performance Degraded',
      message: 'Redis cluster experiencing high latency (280ms avg)',
      timestamp: new Date(Date.now() - 300000),
      resolved: false,
    },
    {
      id: '2',
      severity: 'info',
      title: 'Model Training Complete',
      message: 'fraud-detection-v3 training completed successfully',
      timestamp: new Date(Date.now() - 600000),
      resolved: true,
    },
    {
      id: '3',
      severity: 'critical',
      title: 'Database Connection Pool Full',
      message: 'All connections in use - auto-scaling initiated',
      timestamp: new Date(Date.now() - 900000),
      resolved: true,
    },
  ]);

  const [resourceMetrics] = React.useState({
    cpu: 45,
    memory: 62,
    disk: 75,
    network: 38,
  });

  const getStatusIcon = (status: ServiceHealth['status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'degraded':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      case 'down':
        return <XCircle className="w-5 h-5 text-red-400" />;
    }
  };

  const getStatusColor = (status: ServiceHealth['status']) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500/10 border-green-500/20';
      case 'degraded':
        return 'bg-yellow-500/10 border-yellow-500/20';
      case 'down':
        return 'bg-red-500/10 border-red-500/20';
    }
  };

  const getLogLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'info':
        return 'text-blue-400';
      case 'warning':
        return 'text-yellow-400';
      case 'error':
        return 'text-red-400';
    }
  };

  const getAlertColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500/10 border-red-500/20';
      case 'warning':
        return 'bg-yellow-500/10 border-yellow-500/20';
      case 'info':
        return 'bg-blue-500/10 border-blue-500/20';
    }
  };

  const healthyServices = services.filter(s => s.status === 'healthy').length;
  const degradedServices = services.filter(s => s.status === 'degraded').length;
  const downServices = services.filter(s => s.status === 'down').length;

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">System Monitoring</h1>
          <p className="text-gray-400">Real-time service health and system metrics</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">Configure Alerts</button>
          <button className="btn-primary">View Logs</button>
        </div>
      </div>

      {/* Overall Status */}
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          {degradedServices === 0 && downServices === 0 ? (
            <>
              <CheckCircle className="w-6 h-6 text-green-400" />
              <div>
                <h2 className="text-xl font-bold">All Systems Operational</h2>
                <p className="text-sm text-gray-400">{healthyServices} services running normally</p>
              </div>
            </>
          ) : (
            <>
              <AlertCircle className="w-6 h-6 text-yellow-400" />
              <div>
                <h2 className="text-xl font-bold">System Degraded</h2>
                <p className="text-sm text-gray-400">
                  {healthyServices} healthy, {degradedServices} degraded, {downServices} down
                </p>
              </div>
            </>
          )}
        </div>
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div className="text-center p-3 rounded-lg bg-green-500/10">
            <div className="text-2xl font-bold text-green-400">{healthyServices}</div>
            <div className="text-xs text-gray-400">Healthy</div>
          </div>
          <div className="text-center p-3 rounded-lg bg-yellow-500/10">
            <div className="text-2xl font-bold text-yellow-400">{degradedServices}</div>
            <div className="text-xs text-gray-400">Degraded</div>
          </div>
          <div className="text-center p-3 rounded-lg bg-red-500/10">
            <div className="text-2xl font-bold text-red-400">{downServices}</div>
            <div className="text-xs text-gray-400">Down</div>
          </div>
        </div>
      </div>

      {/* Service Health */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Service Health Checks</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map(service => (
            <div key={service.id} className={`p-4 rounded-lg border ${getStatusColor(service.status)}`}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  {getStatusIcon(service.status)}
                  <span className="font-medium">{service.name}</span>
                </div>
                <Server className="w-4 h-4 text-gray-400" />
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Uptime</span>
                  <span className="font-medium">{service.uptime}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Response</span>
                  <span className="font-medium">{service.responseTime}ms</span>
                </div>
                <div className="text-xs text-gray-500">
                  Last check: {service.lastCheck.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Resource Usage */}
        <div className="card">
          <h3 className="text-lg font-bold mb-4">Resource Usage</h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-purple-400" />
                  <span>CPU Utilization</span>
                </div>
                <span className="text-gray-400">{resourceMetrics.cpu}%</span>
              </div>
              <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                  style={{ width: `${resourceMetrics.cpu}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <div className="flex items-center gap-2">
                  <HardDrive className="w-4 h-4 text-blue-400" />
                  <span>Memory Usage</span>
                </div>
                <span className="text-gray-400">{resourceMetrics.memory}%</span>
              </div>
              <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                  style={{ width: `${resourceMetrics.memory}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-green-400" />
                  <span>Disk Usage</span>
                </div>
                <span className="text-gray-400">{resourceMetrics.disk}%</span>
              </div>
              <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                  style={{ width: `${resourceMetrics.disk}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <div className="flex items-center gap-2">
                  <Network className="w-4 h-4 text-yellow-400" />
                  <span>Network I/O</span>
                </div>
                <span className="text-gray-400">{resourceMetrics.network}%</span>
              </div>
              <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                  style={{ width: `${resourceMetrics.network}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Active Alerts */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold">Active Alerts</h3>
            <Bell className="w-5 h-5 text-gray-400" />
          </div>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {alerts.map(alert => (
              <div
                key={alert.id}
                className={`p-3 rounded-lg border ${getAlertColor(alert.severity)} ${
                  alert.resolved ? 'opacity-50' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-1">
                  <span className="font-medium text-sm">{alert.title}</span>
                  <span className="text-xs text-gray-500">
                    {Math.floor((Date.now() - alert.timestamp.getTime()) / 60000)}m ago
                  </span>
                </div>
                <div className="text-xs text-gray-400">{alert.message}</div>
                {alert.resolved && (
                  <div className="flex items-center gap-1 mt-2 text-xs text-green-400">
                    <CheckCircle className="w-3 h-3" />
                    <span>Resolved</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Live Logs */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5" />
            <h3 className="text-lg font-bold">Live Logs</h3>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-400">Streaming</span>
          </div>
        </div>
        <div className="bg-gray-950 rounded-lg p-4 font-mono text-sm space-y-2 max-h-96 overflow-y-auto">
          {logs.map(log => (
            <div key={log.id} className="flex gap-3">
              <span className="text-gray-500 text-xs">{log.timestamp.toLocaleTimeString()}</span>
              <span className={`uppercase text-xs font-bold ${getLogLevelColor(log.level)}`}>
                [{log.level}]
              </span>
              <span className="text-gray-400 text-xs">[{log.service}]</span>
              <span className="text-gray-300 text-xs flex-1">{log.message}</span>
            </div>
          ))}
        </div>
      </div>

      {/* System Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-5 h-5 text-green-400" />
            <span className="text-sm text-gray-400">System Uptime</span>
          </div>
          <div className="text-2xl font-bold">99.98%</div>
          <div className="text-xs text-gray-500 mt-1">Last 30 days</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Server className="w-5 h-5 text-blue-400" />
            <span className="text-sm text-gray-400">Total Services</span>
          </div>
          <div className="text-2xl font-bold">{services.length}</div>
          <div className="text-xs text-gray-500 mt-1">Monitoring active</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Bell className="w-5 h-5 text-yellow-400" />
            <span className="text-sm text-gray-400">Alerts Today</span>
          </div>
          <div className="text-2xl font-bold">{alerts.filter(a => !a.resolved).length}</div>
          <div className="text-xs text-gray-500 mt-1">
            {alerts.filter(a => a.resolved).length} resolved
          </div>
        </div>
      </div>
    </div>
  );
};
