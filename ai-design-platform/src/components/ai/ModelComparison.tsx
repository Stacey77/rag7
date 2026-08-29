import React, { useState } from 'react';
import { 
  Download, 
  CheckCircle,
  TrendingUp,
  DollarSign,
  Zap,
  Clock,
  Target,
  Award
} from 'lucide-react';
import { 
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from 'recharts';

interface Model {
  id: string;
  name: string;
  version: string;
  type: string;
}

interface ModelMetrics {
  modelId: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  latency: number;
  throughput: number;
  costPerRequest: number;
  memoryUsage: number;
}

interface BenchmarkResult {
  test: string;
  model1: number;
  model2: number;
  model3: number;
  model4: number;
}

export const ModelComparison: React.FC = () => {
  const availableModels: Model[] = [
    { id: 'gpt4', name: 'GPT-4', version: 'v1.0', type: 'Language Model' },
    { id: 'gpt3.5', name: 'GPT-3.5 Turbo', version: 'v1.0', type: 'Language Model' },
    { id: 'claude3', name: 'Claude 3 Opus', version: 'v3.0', type: 'Language Model' },
    { id: 'claude2', name: 'Claude 2', version: 'v2.1', type: 'Language Model' },
    { id: 'gemini', name: 'Gemini Pro', version: 'v1.0', type: 'Language Model' },
    { id: 'llama2', name: 'Llama 2 70B', version: 'v2.0', type: 'Language Model' },
    { id: 'mistral', name: 'Mistral 7B', version: 'v1.0', type: 'Language Model' },
    { id: 'custom1', name: 'Custom Model A', version: 'v2.3', type: 'Fine-tuned' }
  ];

  const [selectedModels, setSelectedModels] = useState<string[]>(['gpt4', 'claude3', 'gemini', 'llama2']);

  const metrics: Record<string, ModelMetrics> = {
    gpt4: {
      modelId: 'gpt4',
      accuracy: 0.94,
      precision: 0.92,
      recall: 0.95,
      f1Score: 0.93,
      latency: 1200,
      throughput: 850,
      costPerRequest: 0.03,
      memoryUsage: 4.5
    },
    'gpt3.5': {
      modelId: 'gpt3.5',
      accuracy: 0.88,
      precision: 0.86,
      recall: 0.89,
      f1Score: 0.87,
      latency: 450,
      throughput: 2200,
      costPerRequest: 0.002,
      memoryUsage: 2.1
    },
    claude3: {
      modelId: 'claude3',
      accuracy: 0.93,
      precision: 0.91,
      recall: 0.94,
      f1Score: 0.92,
      latency: 1100,
      throughput: 900,
      costPerRequest: 0.015,
      memoryUsage: 4.2
    },
    claude2: {
      modelId: 'claude2',
      accuracy: 0.89,
      precision: 0.87,
      recall: 0.90,
      f1Score: 0.88,
      latency: 800,
      throughput: 1250,
      costPerRequest: 0.008,
      memoryUsage: 3.4
    },
    gemini: {
      modelId: 'gemini',
      accuracy: 0.91,
      precision: 0.89,
      recall: 0.92,
      f1Score: 0.90,
      latency: 950,
      throughput: 1050,
      costPerRequest: 0.01,
      memoryUsage: 3.8
    },
    llama2: {
      modelId: 'llama2',
      accuracy: 0.86,
      precision: 0.84,
      recall: 0.87,
      f1Score: 0.85,
      latency: 600,
      throughput: 1650,
      costPerRequest: 0.001,
      memoryUsage: 2.8
    },
    mistral: {
      modelId: 'mistral',
      accuracy: 0.85,
      precision: 0.83,
      recall: 0.86,
      f1Score: 0.84,
      latency: 350,
      throughput: 2800,
      costPerRequest: 0.0005,
      memoryUsage: 1.9
    },
    custom1: {
      modelId: 'custom1',
      accuracy: 0.90,
      precision: 0.88,
      recall: 0.91,
      f1Score: 0.89,
      latency: 520,
      throughput: 1900,
      costPerRequest: 0.005,
      memoryUsage: 2.5
    }
  };

  const getRadarData = () => {
    const categories = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Speed'];
    
    return categories.map(category => {
      const dataPoint: any = { category };
      
      selectedModels.forEach((modelId, index) => {
        const modelMetrics = metrics[modelId];
        if (modelMetrics) {
          let value = 0;
          switch (category) {
            case 'Accuracy':
              value = modelMetrics.accuracy * 100;
              break;
            case 'Precision':
              value = modelMetrics.precision * 100;
              break;
            case 'Recall':
              value = modelMetrics.recall * 100;
              break;
            case 'F1-Score':
              value = modelMetrics.f1Score * 100;
              break;
            case 'Speed':
              value = Math.min(100, (3000 - modelMetrics.latency) / 30);
              break;
          }
          dataPoint[`model${index + 1}`] = value;
        }
      });
      
      return dataPoint;
    });
  };

  const getLatencyData = () => {
    return selectedModels.map((modelId) => ({
      name: availableModels.find(m => m.id === modelId)?.name.split(' ')[0] || modelId,
      latency: metrics[modelId]?.latency || 0
    }));
  };

  const getCostData = () => {
    return selectedModels.map((modelId) => ({
      name: availableModels.find(m => m.id === modelId)?.name.split(' ')[0] || modelId,
      cost: metrics[modelId]?.costPerRequest * 1000 || 0
    }));
  };

  const benchmarkResults: BenchmarkResult[] = [
    { test: 'Text Classification', model1: 94.2, model2: 93.1, model3: 91.5, model4: 86.8 },
    { test: 'Sentiment Analysis', model1: 92.8, model2: 91.5, model3: 90.2, model4: 88.3 },
    { test: 'Named Entity Recognition', model1: 93.5, model2: 92.8, model3: 91.0, model4: 87.5 },
    { test: 'Question Answering', model1: 95.1, model2: 94.3, model3: 92.7, model4: 85.9 },
    { test: 'Code Generation', model1: 89.5, model2: 91.2, model3: 88.8, model4: 82.4 }
  ];

  const handleModelSelect = (index: number, modelId: string) => {
    const newSelection = [...selectedModels];
    newSelection[index] = modelId;
    setSelectedModels(newSelection);
  };

  const exportReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      models: selectedModels.map(id => ({
        model: availableModels.find(m => m.id === id),
        metrics: metrics[id]
      }))
    };
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `model-comparison-${Date.now()}.json`;
    a.click();
  };

  const colors = ['#8B5CF6', '#3B82F6', '#10B981', '#F59E0B'];

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Model Comparison</h1>
          <p className="text-gray-400">Compare performance metrics across multiple models</p>
        </div>
        <button onClick={exportReport} className="btn-primary">
          <Download className="w-4 h-4 mr-2" />
          Export Report
        </button>
      </div>

      {/* Model Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[0, 1, 2, 3].map((index) => (
          <div key={index} className="card">
            <label className="text-sm text-gray-400 mb-2 block">Model {index + 1}</label>
            <select
              value={selectedModels[index] || ''}
              onChange={(e) => handleModelSelect(index, e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white"
            >
              <option value="">Select Model</option>
              {availableModels.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name} {model.version}
                </option>
              ))}
            </select>
            {selectedModels[index] && metrics[selectedModels[index]] && (
              <div className="mt-3 pt-3 border-t border-white/10">
                <div className="text-xs text-gray-400 space-y-1">
                  <div className="flex justify-between">
                    <span>Type:</span>
                    <span className="text-gray-300">
                      {availableModels.find(m => m.id === selectedModels[index])?.type}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Version:</span>
                    <span className="text-gray-300">
                      {availableModels.find(m => m.id === selectedModels[index])?.version}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Performance Metrics Table */}
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <Target className="w-5 h-5 text-purple-400" />
          <h2 className="text-xl font-semibold">Performance Metrics</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Metric</th>
                {selectedModels.map((modelId, index) => (
                  <th key={index} className="text-center py-3 px-4 text-gray-400 font-medium">
                    {availableModels.find(m => m.id === modelId)?.name || 'N/A'}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4 text-gray-300">Accuracy</td>
                {selectedModels.map((modelId, index) => {
                  const metric = metrics[modelId];
                  return (
                    <td key={index} className="text-center py-3 px-4">
                      <span className="font-semibold text-green-400">
                        {metric ? `${(metric.accuracy * 100).toFixed(1)}%` : 'N/A'}
                      </span>
                    </td>
                  );
                })}
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4 text-gray-300">Precision</td>
                {selectedModels.map((modelId, index) => {
                  const metric = metrics[modelId];
                  return (
                    <td key={index} className="text-center py-3 px-4">
                      <span className="font-semibold text-blue-400">
                        {metric ? `${(metric.precision * 100).toFixed(1)}%` : 'N/A'}
                      </span>
                    </td>
                  );
                })}
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4 text-gray-300">Recall</td>
                {selectedModels.map((modelId, index) => {
                  const metric = metrics[modelId];
                  return (
                    <td key={index} className="text-center py-3 px-4">
                      <span className="font-semibold text-purple-400">
                        {metric ? `${(metric.recall * 100).toFixed(1)}%` : 'N/A'}
                      </span>
                    </td>
                  );
                })}
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4 text-gray-300">F1 Score</td>
                {selectedModels.map((modelId, index) => {
                  const metric = metrics[modelId];
                  return (
                    <td key={index} className="text-center py-3 px-4">
                      <span className="font-semibold text-cyan-400">
                        {metric ? `${(metric.f1Score * 100).toFixed(1)}%` : 'N/A'}
                      </span>
                    </td>
                  );
                })}
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4 text-gray-300">Latency (ms)</td>
                {selectedModels.map((modelId, index) => {
                  const metric = metrics[modelId];
                  return (
                    <td key={index} className="text-center py-3 px-4">
                      <span className="font-semibold text-orange-400">
                        {metric ? `${metric.latency}` : 'N/A'}
                      </span>
                    </td>
                  );
                })}
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4 text-gray-300">Throughput (req/s)</td>
                {selectedModels.map((modelId, index) => {
                  const metric = metrics[modelId];
                  return (
                    <td key={index} className="text-center py-3 px-4">
                      <span className="font-semibold text-yellow-400">
                        {metric ? metric.throughput.toLocaleString() : 'N/A'}
                      </span>
                    </td>
                  );
                })}
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4 text-gray-300">Cost per Request ($)</td>
                {selectedModels.map((modelId, index) => {
                  const metric = metrics[modelId];
                  return (
                    <td key={index} className="text-center py-3 px-4">
                      <span className="font-semibold text-red-400">
                        {metric ? `$${metric.costPerRequest.toFixed(4)}` : 'N/A'}
                      </span>
                    </td>
                  );
                })}
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-300">Memory Usage (GB)</td>
                {selectedModels.map((modelId, index) => {
                  const metric = metrics[modelId];
                  return (
                    <td key={index} className="text-center py-3 px-4">
                      <span className="font-semibold text-pink-400">
                        {metric ? `${metric.memoryUsage.toFixed(1)}` : 'N/A'}
                      </span>
                    </td>
                  );
                })}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Comparison Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar Chart */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <Award className="w-5 h-5 text-purple-400" />
            <h2 className="text-xl font-semibold">Overall Performance</h2>
          </div>

          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={getRadarData()}>
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="category" stroke="#9CA3AF" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px'
                }} 
              />
              {selectedModels.map((modelId, index) => (
                <Radar
                  key={index}
                  name={availableModels.find(m => m.id === modelId)?.name || `Model ${index + 1}`}
                  dataKey={`model${index + 1}`}
                  stroke={colors[index]}
                  fill={colors[index]}
                  fillOpacity={0.25}
                  strokeWidth={2}
                />
              ))}
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Latency Comparison */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <Clock className="w-5 h-5 text-purple-400" />
            <h2 className="text-xl font-semibold">Latency Comparison</h2>
          </div>

          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={getLatencyData()}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px'
                }} 
              />
              <Bar dataKey="latency" fill="#8B5CF6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Cost Analysis */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <DollarSign className="w-5 h-5 text-purple-400" />
            <h2 className="text-xl font-semibold">Cost Analysis (per 1000 requests)</h2>
          </div>

          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={getCostData()}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px'
                }} 
              />
              <Bar dataKey="cost" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>

          <div className="mt-4 grid grid-cols-2 gap-4">
            {selectedModels.slice(0, 4).map((modelId, index) => {
              const metric = metrics[modelId];
              if (!metric) return null;
              
              const monthlyCost = metric.costPerRequest * 1000000;
              
              return (
                <div key={index} className="glass rounded-lg p-3">
                  <div className="text-sm text-gray-400 mb-1">
                    {availableModels.find(m => m.id === modelId)?.name}
                  </div>
                  <div className="text-lg font-bold" style={{ color: colors[index] }}>
                    ${monthlyCost.toFixed(2)}/month
                  </div>
                  <div className="text-xs text-gray-500">@ 1M requests</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Benchmark Results */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <Zap className="w-5 h-5 text-purple-400" />
            <h2 className="text-xl font-semibold">Benchmark Results</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 px-3 text-gray-400 font-medium">Test</th>
                  {selectedModels.slice(0, 4).map((_modelId, index) => (
                    <th key={index} className="text-center py-2 px-3 text-gray-400 font-medium">
                      M{index + 1}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {benchmarkResults.map((result, i) => (
                  <tr key={i} className="border-b border-white/5">
                    <td className="py-2 px-3 text-gray-300">{result.test}</td>
                    <td className="text-center py-2 px-3">
                      <span className="font-semibold" style={{ color: colors[0] }}>
                        {result.model1.toFixed(1)}%
                      </span>
                    </td>
                    <td className="text-center py-2 px-3">
                      <span className="font-semibold" style={{ color: colors[1] }}>
                        {result.model2.toFixed(1)}%
                      </span>
                    </td>
                    <td className="text-center py-2 px-3">
                      <span className="font-semibold" style={{ color: colors[2] }}>
                        {result.model3.toFixed(1)}%
                      </span>
                    </td>
                    <td className="text-center py-2 px-3">
                      <span className="font-semibold" style={{ color: colors[3] }}>
                        {result.model4.toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold text-purple-400 mb-1">Best Overall</div>
                <div className="text-sm text-gray-400">
                  {availableModels.find(m => m.id === selectedModels[0])?.name || 'Model 1'}
                </div>
              </div>
              <Award className="w-8 h-8 text-purple-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <span className="text-sm text-gray-400">Highest Accuracy</span>
          </div>
          <div className="text-2xl font-bold gradient-text">
            {Math.max(...selectedModels.map(id => (metrics[id]?.accuracy || 0) * 100)).toFixed(1)}%
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <Zap className="w-5 h-5 text-blue-400" />
            <span className="text-sm text-gray-400">Lowest Latency</span>
          </div>
          <div className="text-2xl font-bold gradient-text">
            {Math.min(...selectedModels.map(id => metrics[id]?.latency || Infinity))}ms
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="w-5 h-5 text-yellow-400" />
            <span className="text-sm text-gray-400">Most Cost-Effective</span>
          </div>
          <div className="text-2xl font-bold gradient-text">
            ${Math.min(...selectedModels.map(id => metrics[id]?.costPerRequest || Infinity)).toFixed(4)}
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            <span className="text-sm text-gray-400">Best F1 Score</span>
          </div>
          <div className="text-2xl font-bold gradient-text">
            {Math.max(...selectedModels.map(id => (metrics[id]?.f1Score || 0) * 100)).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
};
