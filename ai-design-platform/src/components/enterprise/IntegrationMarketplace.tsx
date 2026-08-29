import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Cloud, 
  Database, 
  Zap,
  CheckCircle,
  XCircle,
  Settings,
  Download,
  Filter,
  ExternalLink
} from 'lucide-react';
import type { Integration } from '../../types';

export const IntegrationMarketplace: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const integrations: Integration[] = [
    {
      id: '1',
      name: 'AWS SageMaker',
      category: 'ML Platform',
      description: 'Build, train, and deploy machine learning models at scale with AWS SageMaker integration',
      icon: '☁️',
      installed: true,
      status: 'active'
    },
    {
      id: '2',
      name: 'Azure ML',
      category: 'ML Platform',
      description: 'Enterprise-grade machine learning service to build and deploy models faster',
      icon: '☁️',
      installed: true,
      status: 'active'
    },
    {
      id: '3',
      name: 'Google Cloud AI',
      category: 'ML Platform',
      description: 'Leverage Google Cloud AI and machine learning products for your AI workloads',
      icon: '☁️',
      installed: false,
      status: 'inactive'
    },
    {
      id: '4',
      name: 'Snowflake',
      category: 'Data Warehouse',
      description: 'Cloud data platform for data warehousing, data lakes, and data engineering',
      icon: '❄️',
      installed: true,
      status: 'active'
    },
    {
      id: '5',
      name: 'Databricks',
      category: 'Data Platform',
      description: 'Unified analytics platform for data engineering, ML, and analytics',
      icon: '🔷',
      installed: true,
      status: 'active'
    },
    {
      id: '6',
      name: 'BigQuery',
      category: 'Data Warehouse',
      description: 'Serverless, highly scalable data warehouse from Google Cloud',
      icon: '📊',
      installed: false,
      status: 'inactive'
    },
    {
      id: '7',
      name: 'PostgreSQL',
      category: 'Database',
      description: 'Advanced open-source relational database with powerful features',
      icon: '🐘',
      installed: true,
      status: 'active'
    },
    {
      id: '8',
      name: 'MongoDB',
      category: 'Database',
      description: 'Document-oriented NoSQL database for modern application development',
      icon: '🍃',
      installed: true,
      status: 'active'
    },
    {
      id: '9',
      name: 'Redis',
      category: 'Cache',
      description: 'In-memory data structure store for caching and real-time analytics',
      icon: '⚡',
      installed: true,
      status: 'configuring'
    },
    {
      id: '10',
      name: 'Apache Kafka',
      category: 'Streaming',
      description: 'Distributed event streaming platform for high-performance data pipelines',
      icon: '📨',
      installed: false,
      status: 'inactive'
    },
    {
      id: '11',
      name: 'Elasticsearch',
      category: 'Search',
      description: 'Distributed search and analytics engine for all types of data',
      icon: '🔍',
      installed: false,
      status: 'inactive'
    },
    {
      id: '12',
      name: 'Apache Spark',
      category: 'Processing',
      description: 'Unified analytics engine for large-scale data processing',
      icon: '⚙️',
      installed: false,
      status: 'inactive'
    },
    {
      id: '13',
      name: 'MLflow',
      category: 'ML Ops',
      description: 'Open-source platform for managing the ML lifecycle',
      icon: '🔄',
      installed: true,
      status: 'active'
    },
    {
      id: '14',
      name: 'Kubeflow',
      category: 'ML Ops',
      description: 'Machine learning toolkit for Kubernetes deployments',
      icon: '☸️',
      installed: false,
      status: 'inactive'
    }
  ];

  const categories = useMemo(() => {
    const cats = new Set(integrations.map(i => i.category));
    return ['all', ...Array.from(cats)];
  }, [integrations]);

  const filteredIntegrations = useMemo(() => {
    return integrations.filter(integration => {
      const matchesSearch = integration.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           integration.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || integration.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [integrations, searchQuery, selectedCategory]);

  const stats = useMemo(() => {
    const installed = integrations.filter(i => i.installed).length;
    const active = integrations.filter(i => i.status === 'active').length;
    return { total: integrations.length, installed, active };
  }, [integrations]);

  const getStatusBadge = (status: Integration['status']) => {
    switch (status) {
      case 'active':
        return (
          <span className="flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/20">
            <CheckCircle className="w-3 h-3" />
            Active
          </span>
        );
      case 'configuring':
        return (
          <span className="flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-400 border border-yellow-500/20">
            <Settings className="w-3 h-3" />
            Configuring
          </span>
        );
      case 'inactive':
        return (
          <span className="flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-gray-500/20 text-gray-400 border border-gray-500/20">
            <XCircle className="w-3 h-3" />
            Not Installed
          </span>
        );
    }
  };

  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: React.ReactNode } = {
      'ML Platform': <Cloud className="w-4 h-4" />,
      'Data Warehouse': <Database className="w-4 h-4" />,
      'Data Platform': <Database className="w-4 h-4" />,
      'Database': <Database className="w-4 h-4" />,
      'Cache': <Zap className="w-4 h-4" />,
      'Streaming': <Zap className="w-4 h-4" />,
      'Search': <Search className="w-4 h-4" />,
      'Processing': <Settings className="w-4 h-4" />,
      'ML Ops': <Settings className="w-4 h-4" />
    };
    return icons[category] || <Cloud className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Integration Marketplace</h1>
          <p className="text-gray-400">Connect your favorite tools and platforms</p>
        </div>
        <button className="btn-primary">Request Integration</button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Total Integrations</div>
          <div className="text-3xl font-bold gradient-text">{stats.total}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Installed</div>
          <div className="text-3xl font-bold text-blue-400">{stats.installed}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Active</div>
          <div className="text-3xl font-bold text-green-400">{stats.active}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Categories</div>
          <div className="text-3xl font-bold">{categories.length - 1}</div>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search integrations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
            />
          </div>

          {/* Category Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none min-w-[200px]"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat === 'all' ? 'All Categories' : cat}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Integrations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredIntegrations.map((integration) => (
          <div key={integration.id} className="card card-hover group">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="text-4xl">{integration.icon}</div>
                <div>
                  <h3 className="font-bold text-lg">{integration.name}</h3>
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    {getCategoryIcon(integration.category)}
                    <span>{integration.category}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Description */}
            <p className="text-sm text-gray-400 mb-4 line-clamp-2">
              {integration.description}
            </p>

            {/* Status */}
            <div className="mb-4">
              {getStatusBadge(integration.status)}
            </div>

            {/* Connection Info */}
            {integration.installed && (
              <div className="mb-4 p-3 rounded-lg bg-gray-800/50 border border-gray-700">
                <div className="text-xs text-gray-400 mb-1">Connection Status</div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {integration.status === 'active' ? (
                      <>
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        <span className="text-sm text-green-400">Connected</span>
                      </>
                    ) : (
                      <>
                        <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                        <span className="text-sm text-yellow-400">Configuring</span>
                      </>
                    )}
                  </div>
                  <button className="text-xs text-purple-400 hover:text-purple-300">
                    Test Connection
                  </button>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-4 border-t border-gray-700">
              {integration.installed ? (
                <>
                  <button className="flex-1 btn-secondary text-sm py-2 flex items-center justify-center gap-2">
                    <Settings className="w-4 h-4" />
                    Configure
                  </button>
                  <button className="px-4 btn-primary text-sm py-2">
                    <ExternalLink className="w-4 h-4" />
                  </button>
                </>
              ) : (
                <>
                  <button className="flex-1 btn-primary text-sm py-2 flex items-center justify-center gap-2">
                    <Download className="w-4 h-4" />
                    Install
                  </button>
                  <button className="px-4 btn-secondary text-sm py-2">
                    <ExternalLink className="w-4 h-4" />
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Popular Integrations */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4">Popular Integration Stacks</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20">
            <div className="font-semibold mb-3">🚀 ML Production Stack</div>
            <div className="space-y-2 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span>AWS SageMaker</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span>MLflow</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span>PostgreSQL</span>
              </div>
            </div>
            <button className="w-full mt-3 btn-secondary text-sm py-2">Install Stack</button>
          </div>

          <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/20">
            <div className="font-semibold mb-3">📊 Data Analytics Stack</div>
            <div className="space-y-2 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span>Snowflake</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span>Databricks</span>
              </div>
              <div className="flex items-center gap-2">
                <XCircle className="w-4 h-4 text-gray-600" />
                <span>Apache Spark</span>
              </div>
            </div>
            <button className="w-full mt-3 btn-secondary text-sm py-2">Install Stack</button>
          </div>

          <div className="p-4 rounded-lg bg-gradient-to-br from-green-500/10 to-transparent border border-green-500/20">
            <div className="font-semibold mb-3">⚡ Real-time Processing</div>
            <div className="space-y-2 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span>Redis</span>
              </div>
              <div className="flex items-center gap-2">
                <XCircle className="w-4 h-4 text-gray-600" />
                <span>Apache Kafka</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span>MongoDB</span>
              </div>
            </div>
            <button className="w-full mt-3 btn-secondary text-sm py-2">Install Stack</button>
          </div>
        </div>
      </div>

      {/* Integration Benefits */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4">Integration Benefits</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold mb-3 text-purple-400">For Data Teams</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                <span>Seamless data pipeline integration with existing infrastructure</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                <span>Automated data synchronization across platforms</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                <span>Support for multiple data formats and protocols</span>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3 text-blue-400">For ML Engineers</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                <span>One-click model deployment to production environments</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                <span>Centralized experiment tracking and model versioning</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                <span>Automated CI/CD pipelines for ML workflows</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
