import React from 'react';
import { Shield, CheckCircle, Clock, AlertTriangle, Award, FileText, Calendar, TrendingUp } from 'lucide-react';
import type { SecurityFramework } from '../../types';

export const SecurityCompliance: React.FC = () => {
  const frameworks: SecurityFramework[] = [
    {
      id: '1',
      name: 'SOC 2 Type II',
      status: 'compliant',
      progress: 100,
      lastAudit: new Date('2024-01-15'),
      controls: 64
    },
    {
      id: '2',
      name: 'ISO 27001',
      status: 'compliant',
      progress: 100,
      lastAudit: new Date('2024-02-20'),
      controls: 114
    },
    {
      id: '3',
      name: 'GDPR',
      status: 'compliant',
      progress: 100,
      lastAudit: new Date('2024-01-10'),
      controls: 42
    },
    {
      id: '4',
      name: 'HIPAA',
      status: 'in-progress',
      progress: 78,
      lastAudit: new Date('2023-11-30'),
      controls: 56
    },
    {
      id: '5',
      name: 'PCI DSS',
      status: 'in-progress',
      progress: 85,
      lastAudit: new Date('2024-02-01'),
      controls: 78
    },
    {
      id: '6',
      name: 'FedRAMP',
      status: 'not-compliant',
      progress: 45,
      lastAudit: new Date('2023-10-15'),
      controls: 325
    }
  ];

  const certificates = [
    { name: 'SOC 2 Type II', issueDate: '2024-01-15', expiryDate: '2025-01-15', status: 'active' },
    { name: 'ISO 27001:2013', issueDate: '2024-02-20', expiryDate: '2027-02-20', status: 'active' },
    { name: 'GDPR Compliance', issueDate: '2024-01-10', expiryDate: '2025-01-10', status: 'active' }
  ];

  const getStatusColor = (status: SecurityFramework['status']) => {
    switch (status) {
      case 'compliant':
        return 'text-green-400 bg-green-500/20 border-green-500/20';
      case 'in-progress':
        return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/20';
      case 'not-compliant':
        return 'text-red-400 bg-red-500/20 border-red-500/20';
    }
  };

  const getStatusIcon = (status: SecurityFramework['status']) => {
    switch (status) {
      case 'compliant':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'in-progress':
        return <Clock className="w-5 h-5 text-yellow-400" />;
      case 'not-compliant':
        return <AlertTriangle className="w-5 h-5 text-red-400" />;
    }
  };

  const getStatusLabel = (status: SecurityFramework['status']) => {
    switch (status) {
      case 'compliant':
        return 'Compliant';
      case 'in-progress':
        return 'In Progress';
      case 'not-compliant':
        return 'Not Compliant';
    }
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  const daysSinceAudit = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  };

  const overallCompliance = Math.round(
    frameworks.reduce((sum, f) => sum + f.progress, 0) / frameworks.length
  );

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Security & Compliance</h1>
          <p className="text-gray-400">Manage compliance frameworks and security standards</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">Download Report</button>
          <button className="btn-primary">Schedule Audit</button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Overall Compliance</div>
          <div className="text-3xl font-bold gradient-text">{overallCompliance}%</div>
          <div className="text-xs text-green-400 mt-1">↑ 5% from last month</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Active Frameworks</div>
          <div className="text-3xl font-bold">{frameworks.length}</div>
          <div className="text-xs text-gray-400 mt-1">6 standards tracked</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Total Controls</div>
          <div className="text-3xl font-bold">
            {frameworks.reduce((sum, f) => sum + f.controls, 0)}
          </div>
          <div className="text-xs text-gray-400 mt-1">Across all frameworks</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Active Certificates</div>
          <div className="text-3xl font-bold text-green-400">{certificates.length}</div>
          <div className="text-xs text-gray-400 mt-1">All current & valid</div>
        </div>
      </div>

      {/* Compliance Status */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Compliance Frameworks</h2>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-400 rounded-full"></div>
              <span className="text-gray-400">Compliant</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
              <span className="text-gray-400">In Progress</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-400 rounded-full"></div>
              <span className="text-gray-400">Not Compliant</span>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {frameworks.map((framework) => (
            <div key={framework.id} className="p-4 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-purple-500/50 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-start gap-3 flex-1">
                  {getStatusIcon(framework.status)}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-semibold text-lg">{framework.name}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(framework.status)}`}>
                        {getStatusLabel(framework.status)}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>{framework.controls} controls</span>
                      <span>•</span>
                      <span>Last audit: {formatDate(framework.lastAudit)}</span>
                      <span>•</span>
                      <span className={daysSinceAudit(framework.lastAudit) > 90 ? 'text-yellow-400' : ''}>
                        {daysSinceAudit(framework.lastAudit)} days ago
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold gradient-text">{framework.progress}%</div>
                  <div className="text-xs text-gray-500">Complete</div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mt-3">
                <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all ${
                      framework.status === 'compliant' 
                        ? 'bg-gradient-to-r from-green-500 to-emerald-500' 
                        : framework.status === 'in-progress'
                        ? 'bg-gradient-to-r from-yellow-500 to-orange-500'
                        : 'bg-gradient-to-r from-red-500 to-rose-500'
                    }`}
                    style={{ width: `${framework.progress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Certificates */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <Award className="w-6 h-6 text-purple-400" />
            <h2 className="text-xl font-bold">Active Certificates</h2>
          </div>
          <div className="space-y-3">
            {certificates.map((cert, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-gradient-to-r from-green-500/10 to-transparent border border-green-500/20">
                <div className="flex items-start justify-between mb-2">
                  <div className="font-semibold">{cert.name}</div>
                  <span className="px-2 py-1 rounded text-xs bg-green-500/20 text-green-400 font-medium">
                    Active
                  </span>
                </div>
                <div className="text-sm text-gray-400 space-y-1">
                  <div className="flex justify-between">
                    <span>Issued:</span>
                    <span>{formatDate(new Date(cert.issueDate))}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Expires:</span>
                    <span>{formatDate(new Date(cert.expiryDate))}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Audits */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <FileText className="w-6 h-6 text-purple-400" />
            <h2 className="text-xl font-bold">Recent Audit Activity</h2>
          </div>
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
              <div className="flex items-center gap-3 mb-2">
                <Calendar className="w-4 h-4 text-blue-400" />
                <div className="font-medium">ISO 27001 Surveillance Audit</div>
              </div>
              <div className="text-sm text-gray-400">
                Completed on {formatDate(new Date('2024-02-20'))}
              </div>
              <div className="mt-2 text-xs text-green-400">✓ No findings</div>
            </div>
            <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
              <div className="flex items-center gap-3 mb-2">
                <Calendar className="w-4 h-4 text-blue-400" />
                <div className="font-medium">SOC 2 Type II Examination</div>
              </div>
              <div className="text-sm text-gray-400">
                Completed on {formatDate(new Date('2024-01-15'))}
              </div>
              <div className="mt-2 text-xs text-green-400">✓ Clean report</div>
            </div>
            <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
              <div className="flex items-center gap-3 mb-2">
                <Calendar className="w-4 h-4 text-yellow-400" />
                <div className="font-medium">HIPAA Gap Assessment</div>
              </div>
              <div className="text-sm text-gray-400">
                Scheduled for March 15, 2024
              </div>
              <div className="mt-2 text-xs text-yellow-400">⚠ 3 items to address</div>
            </div>
          </div>
        </div>
      </div>

      {/* Security Controls */}
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-6 h-6 text-purple-400" />
          <h2 className="text-xl font-bold">Security Controls Summary</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20">
            <div className="text-sm text-gray-400 mb-2">Preventive Controls</div>
            <div className="text-3xl font-bold mb-1">342</div>
            <div className="flex items-center gap-2 text-xs text-green-400">
              <TrendingUp className="w-3 h-3" />
              <span>98% effective</span>
            </div>
          </div>
          <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/20">
            <div className="text-sm text-gray-400 mb-2">Detective Controls</div>
            <div className="text-3xl font-bold mb-1">189</div>
            <div className="flex items-center gap-2 text-xs text-green-400">
              <TrendingUp className="w-3 h-3" />
              <span>96% effective</span>
            </div>
          </div>
          <div className="p-4 rounded-lg bg-gradient-to-br from-green-500/10 to-transparent border border-green-500/20">
            <div className="text-sm text-gray-400 mb-2">Corrective Controls</div>
            <div className="text-3xl font-bold mb-1">148</div>
            <div className="flex items-center gap-2 text-xs text-green-400">
              <TrendingUp className="w-3 h-3" />
              <span>94% effective</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
