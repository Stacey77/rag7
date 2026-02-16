import React from 'react';
import { Search, Filter, Play, Archive, GitBranch, TrendingUp, Clock, CheckCircle, AlertCircle, Package } from 'lucide-react';
import type { AIModel } from '../../types';

export const ModelManagement: React.FC = () => {
  const [searchQuery, setSearchQuery] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState<string>('all');

  const [models] = React.useState<AIModel[]>([
    {
      id: '1',
      name: 'fraud-detection-v3',
      version: '3.2.1',
      status: 'deployed',
      accuracy: 98.5,
      latency: 120,
      throughput: 1500,
      createdAt: new Date('2024-01-15'),
      updatedAt: new Date('2024-01-20'),
    },
    {
      id: '2',
      name: 'customer-sentiment',
      version: '2.1.0',
      status: 'active',
      accuracy: 94.2,
      latency: 85,
      throughput: 2200,
      createdAt: new Date('2024-01-10'),
      updatedAt: new Date('2024-01-18'),
    },
    {
      id: '3',
      name: 'price-optimization',
      version: '1.5.3',
      status: 'training',
      accuracy: 91.8,
      latency: 200,
      throughput: 800,
      createdAt: new Date('2024-01-12'),
      updatedAt: new Date('2024-01-22'),
    },
    {
      id: '4',
      name: 'recommendation-engine',
      version: '4.0.0',
      status: 'deployed',
      accuracy: 96.7,
      latency: 95,
      throughput: 3000,
      createdAt: new Date('2024-01-08'),
      updatedAt: new Date('2024-01-21'),
    },
    {
      id: '5',
      name: 'churn-prediction',
      version: '2.3.1',
      status: 'archived',
      accuracy: 89.4,
      latency: 150,
      throughput: 600,
      createdAt: new Date('2023-12-20'),
      updatedAt: new Date('2024-01-05'),
    },
    {
      id: '6',
      name: 'image-classifier',
      version: '3.1.0',
      status: 'active',
      accuracy: 97.3,
      latency: 180,
      throughput: 1200,
      createdAt: new Date('2024-01-14'),
      updatedAt: new Date('2024-01-19'),
    },
  ]);

  const filteredModels = models.filter(model => {
    const matchesSearch = model.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || model.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusIcon = (status: AIModel['status']) => {
    switch (status) {
      case 'deployed':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'active':
        return <Play className="w-4 h-4 text-blue-400" />;
      case 'training':
        return <Clock className="w-4 h-4 text-yellow-400" />;
      case 'archived':
        return <Archive className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: AIModel['status']) => {
    switch (status) {
      case 'deployed':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'active':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'training':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      case 'archived':
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  const ModelCard: React.FC<{ model: AIModel }> = ({ model }) => (
    <div className="card-hover">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <Package className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-lg">{model.name}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className={`px-2 py-1 rounded-md text-xs border flex items-center gap-1 ${getStatusColor(model.status)}`}>
                {getStatusIcon(model.status)}
                {model.status}
              </span>
              <span className="text-xs text-gray-500">v{model.version}</span>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {model.status === 'active' && (
            <button className="btn-secondary text-sm">Deploy</button>
          )}
          {model.status === 'deployed' && (
            <button className="btn-secondary text-sm">Monitor</button>
          )}
          <button className="btn-secondary text-sm">
            <GitBranch className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <div className="text-xs text-gray-400 mb-1">Accuracy</div>
          <div className="text-xl font-bold gradient-text">{model.accuracy}%</div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Latency</div>
          <div className="text-xl font-bold">{model.latency}ms</div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Throughput</div>
          <div className="text-xl font-bold">{model.throughput}/s</div>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500 pt-4 border-t border-gray-800">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>Updated {model.updatedAt.toLocaleDateString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <TrendingUp className="w-3 h-3 text-green-400" />
          <span className="text-green-400">+12% requests</span>
        </div>
      </div>
    </div>
  );

  const statusCounts = {
    all: models.length,
    deployed: models.filter(m => m.status === 'deployed').length,
    active: models.filter(m => m.status === 'active').length,
    training: models.filter(m => m.status === 'training').length,
    archived: models.filter(m => m.status === 'archived').length,
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Model Management</h1>
          <p className="text-gray-400">Manage AI model lifecycle and deployments</p>
        </div>
        <button className="btn-primary">Deploy New Model</button>
      </div>

      {/* Search and Filter */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search models..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg focus:outline-none focus:border-purple-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg focus:outline-none focus:border-purple-500"
            >
              <option value="all">All ({statusCounts.all})</option>
              <option value="deployed">Deployed ({statusCounts.deployed})</option>
              <option value="active">Active ({statusCounts.active})</option>
              <option value="training">Training ({statusCounts.training})</option>
              <option value="archived">Archived ({statusCounts.archived})</option>
            </select>
          </div>
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <span className="text-sm text-gray-400">Deployed</span>
          </div>
          <div className="text-2xl font-bold">{statusCounts.deployed}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Play className="w-5 h-5 text-blue-400" />
            <span className="text-sm text-gray-400">Active</span>
          </div>
          <div className="text-2xl font-bold">{statusCounts.active}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-5 h-5 text-yellow-400" />
            <span className="text-sm text-gray-400">Training</span>
          </div>
          <div className="text-2xl font-bold">{statusCounts.training}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Archive className="w-5 h-5 text-gray-400" />
            <span className="text-sm text-gray-400">Archived</span>
          </div>
          <div className="text-2xl font-bold">{statusCounts.archived}</div>
        </div>
      </div>

      {/* Model Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredModels.length > 0 ? (
          filteredModels.map(model => <ModelCard key={model.id} model={model} />)
        ) : (
          <div className="col-span-2 card text-center py-12">
            <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-400">No models found matching your filters</p>
          </div>
        )}
      </div>
    </div>
  );
};
