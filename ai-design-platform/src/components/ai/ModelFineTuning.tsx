import React, { useState } from 'react';
import { 
  Upload, 
  Play, 
  Pause,
  RotateCw,
  CheckCircle,
  FileText,
  Activity,
  TrendingUp,
  AlertCircle,
  Download,
  Eye,
  GitBranch,
  Zap,
  Database,
  Sliders
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  AreaChart,
  Area 
} from 'recharts';

interface Dataset {
  id: string;
  name: string;
  size: number;
  rows: number;
  columns: number;
  preview: string[][];
}

interface TrainingRun {
  id: string;
  name: string;
  timestamp: Date;
  status: 'running' | 'completed' | 'failed';
  accuracy: number;
  loss: number;
  epochs: number;
}

interface ModelVersion {
  version: string;
  date: Date;
  accuracy: number;
  size: number;
}

export const ModelFineTuning: React.FC = () => {
  const [isTraining, setIsTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [currentEpoch, setCurrentEpoch] = useState(0);
  const [autoMLEnabled, setAutoMLEnabled] = useState(false);
  const [selectedModel, setSelectedModel] = useState('resnet50');

  const [hyperparameters, setHyperparameters] = useState({
    learningRate: 0.001,
    batchSize: 32,
    epochs: 100,
    optimizer: 'adam',
    momentum: 0.9,
    weightDecay: 0.0001
  });

  const [dataset, setDataset] = useState<Dataset>({
    id: '1',
    name: 'training_data.csv',
    size: 24.5,
    rows: 10000,
    columns: 15,
    preview: [
      ['ID', 'Feature1', 'Feature2', 'Feature3', 'Label'],
      ['1', '0.234', '0.567', '0.891', 'A'],
      ['2', '0.345', '0.678', '0.912', 'B'],
      ['3', '0.456', '0.789', '0.123', 'A']
    ]
  });

  const trainingData = [
    { epoch: 0, trainLoss: 2.3, valLoss: 2.4, trainAcc: 0.25, valAcc: 0.23 },
    { epoch: 10, trainLoss: 1.8, valLoss: 1.9, trainAcc: 0.45, valAcc: 0.42 },
    { epoch: 20, trainLoss: 1.2, valLoss: 1.4, trainAcc: 0.65, valAcc: 0.61 },
    { epoch: 30, trainLoss: 0.8, valLoss: 1.0, trainAcc: 0.78, valAcc: 0.74 },
    { epoch: 40, trainLoss: 0.5, valLoss: 0.7, trainAcc: 0.86, valAcc: 0.82 },
    { epoch: 50, trainLoss: 0.3, valLoss: 0.5, trainAcc: 0.91, valAcc: 0.88 }
  ];

  const experimentRuns: TrainingRun[] = [
    { id: '1', name: 'Experiment_001', timestamp: new Date('2024-01-20'), status: 'completed', accuracy: 0.88, loss: 0.45, epochs: 50 },
    { id: '2', name: 'Experiment_002', timestamp: new Date('2024-01-21'), status: 'completed', accuracy: 0.91, loss: 0.32, epochs: 75 },
    { id: '3', name: 'Experiment_003', timestamp: new Date('2024-01-22'), status: 'running', accuracy: 0.85, loss: 0.52, epochs: 30 },
    { id: '4', name: 'Experiment_004', timestamp: new Date('2024-01-19'), status: 'failed', accuracy: 0.72, loss: 0.89, epochs: 20 }
  ];

  const modelVersions: ModelVersion[] = [
    { version: 'v3.2.1', date: new Date('2024-01-22'), accuracy: 0.91, size: 45.2 },
    { version: 'v3.2.0', date: new Date('2024-01-15'), accuracy: 0.88, size: 44.8 },
    { version: 'v3.1.5', date: new Date('2024-01-08'), accuracy: 0.85, size: 43.5 }
  ];

  const transferLearningModels = [
    { id: 'resnet50', name: 'ResNet-50', params: '25.6M', accuracy: '76.1%' },
    { id: 'vgg16', name: 'VGG-16', params: '138M', accuracy: '71.3%' },
    { id: 'inception', name: 'Inception-v3', params: '23.8M', accuracy: '77.9%' },
    { id: 'mobilenet', name: 'MobileNet-v2', params: '3.5M', accuracy: '71.8%' },
    { id: 'efficientnet', name: 'EfficientNet-B0', params: '5.3M', accuracy: '77.1%' }
  ];

  const handleStartTraining = () => {
    setIsTraining(true);
    setTrainingProgress(0);
    setCurrentEpoch(0);

    const interval = setInterval(() => {
      setTrainingProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsTraining(false);
          return 100;
        }
        return prev + 2;
      });
      setCurrentEpoch((prev) => Math.min(prev + 1, hyperparameters.epochs));
    }, 200);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setDataset({
        ...dataset,
        name: file.name,
        size: file.size / (1024 * 1024)
      });
    }
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Model Fine-Tuning</h1>
          <p className="text-gray-400">Train and optimize your ML models with advanced controls</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">
            <Download className="w-4 h-4 mr-2" />
            Export Config
          </button>
          <button 
            className={`btn-primary ${isTraining ? 'opacity-50' : ''}`}
            onClick={handleStartTraining}
            disabled={isTraining}
          >
            {isTraining ? (
              <>
                <Pause className="w-4 h-4 mr-2" />
                Training...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start Training
              </>
            )}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dataset Upload & Preview */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Database className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Dataset</h2>
            </div>

            <div className="space-y-4">
              <div className="border-2 border-dashed border-white/10 rounded-lg p-8 text-center hover:border-purple-400/50 transition-colors">
                <Upload className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                <p className="text-gray-300 mb-2">Drop your dataset here or click to browse</p>
                <input
                  type="file"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="dataset-upload"
                  accept=".csv,.json,.parquet"
                />
                <label htmlFor="dataset-upload" className="btn-secondary inline-flex items-center cursor-pointer">
                  <FileText className="w-4 h-4 mr-2" />
                  Select File
                </label>
              </div>

              {dataset && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-4 glass rounded-lg">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-blue-400" />
                      <div>
                        <p className="font-medium">{dataset.name}</p>
                        <p className="text-sm text-gray-400">
                          {dataset.size.toFixed(1)} MB · {dataset.rows.toLocaleString()} rows · {dataset.columns} columns
                        </p>
                      </div>
                    </div>
                    <button className="btn-secondary text-sm">
                      <Eye className="w-4 h-4 mr-1" />
                      Preview
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-white/10">
                          {dataset.preview[0].map((header, i) => (
                            <th key={i} className="text-left py-2 px-3 text-gray-400 font-medium">
                              {header}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {dataset.preview.slice(1).map((row, i) => (
                          <tr key={i} className="border-b border-white/5">
                            {row.map((cell, j) => (
                              <td key={j} className="py-2 px-3 text-gray-300">
                                {cell}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Training Visualization */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Training Progress</h2>
            </div>

            {isTraining && (
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Epoch {currentEpoch} / {hyperparameters.epochs}</span>
                  <span className="text-sm font-medium text-purple-400">{trainingProgress}%</span>
                </div>
                <div className="w-full bg-white/5 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-purple-600 to-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${trainingProgress}%` }}
                  />
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="glass rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Training Loss</div>
                <div className="text-2xl font-bold text-purple-400">0.32</div>
                <div className="text-xs text-green-400 flex items-center mt-1">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  -12.5%
                </div>
              </div>
              <div className="glass rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Validation Accuracy</div>
                <div className="text-2xl font-bold text-blue-400">88.4%</div>
                <div className="text-xs text-green-400 flex items-center mt-1">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  +3.2%
                </div>
              </div>
            </div>

            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trainingData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="epoch" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }} 
                />
                <Legend />
                <Line type="monotone" dataKey="trainLoss" stroke="#8B5CF6" strokeWidth={2} name="Training Loss" />
                <Line type="monotone" dataKey="valLoss" stroke="#3B82F6" strokeWidth={2} name="Validation Loss" />
              </LineChart>
            </ResponsiveContainer>

            <ResponsiveContainer width="100%" height={300} className="mt-6">
              <AreaChart data={trainingData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="epoch" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" domain={[0, 1]} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }} 
                />
                <Legend />
                <Area type="monotone" dataKey="trainAcc" stroke="#10B981" fill="#10B98120" strokeWidth={2} name="Training Accuracy" />
                <Area type="monotone" dataKey="valAcc" stroke="#06B6D4" fill="#06B6D420" strokeWidth={2} name="Validation Accuracy" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Experiment Tracking */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <GitBranch className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Experiment Tracking</h2>
            </div>

            <div className="space-y-2">
              {experimentRuns.map((run) => (
                <div key={run.id} className="glass rounded-lg p-4 flex items-center justify-between hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className={`w-3 h-3 rounded-full ${
                      run.status === 'completed' ? 'bg-green-400' :
                      run.status === 'running' ? 'bg-blue-400 animate-pulse' :
                      'bg-red-400'
                    }`} />
                    <div>
                      <p className="font-medium">{run.name}</p>
                      <p className="text-sm text-gray-400">
                        {run.timestamp.toLocaleDateString()} · {run.epochs} epochs
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <div className="text-sm text-gray-400">Accuracy</div>
                      <div className="font-semibold text-green-400">{(run.accuracy * 100).toFixed(1)}%</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-400">Loss</div>
                      <div className="font-semibold text-purple-400">{run.loss.toFixed(2)}</div>
                    </div>
                    <button className="btn-secondary text-sm">
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Sidebar - Controls */}
        <div className="space-y-6">
          {/* Hyperparameters */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Sliders className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Hyperparameters</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Learning Rate</label>
                <input
                  type="number"
                  value={hyperparameters.learningRate}
                  onChange={(e) => setHyperparameters({ ...hyperparameters, learningRate: parseFloat(e.target.value) })}
                  step="0.0001"
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Batch Size</label>
                <input
                  type="number"
                  value={hyperparameters.batchSize}
                  onChange={(e) => setHyperparameters({ ...hyperparameters, batchSize: parseInt(e.target.value) })}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Epochs</label>
                <input
                  type="number"
                  value={hyperparameters.epochs}
                  onChange={(e) => setHyperparameters({ ...hyperparameters, epochs: parseInt(e.target.value) })}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Optimizer</label>
                <select
                  value={hyperparameters.optimizer}
                  onChange={(e) => setHyperparameters({ ...hyperparameters, optimizer: e.target.value })}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white"
                >
                  <option value="adam">Adam</option>
                  <option value="sgd">SGD</option>
                  <option value="rmsprop">RMSprop</option>
                  <option value="adamw">AdamW</option>
                </select>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Momentum</label>
                <input
                  type="number"
                  value={hyperparameters.momentum}
                  onChange={(e) => setHyperparameters({ ...hyperparameters, momentum: parseFloat(e.target.value) })}
                  step="0.01"
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Weight Decay</label>
                <input
                  type="number"
                  value={hyperparameters.weightDecay}
                  onChange={(e) => setHyperparameters({ ...hyperparameters, weightDecay: parseFloat(e.target.value) })}
                  step="0.0001"
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white"
                />
              </div>
            </div>
          </div>

          {/* Transfer Learning */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <RotateCw className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Transfer Learning</h2>
            </div>

            <div className="space-y-2">
              {transferLearningModels.map((model) => (
                <div
                  key={model.id}
                  onClick={() => setSelectedModel(model.id)}
                  className={`p-3 rounded-lg cursor-pointer transition-all ${
                    selectedModel === model.id
                      ? 'bg-purple-500/20 border border-purple-500'
                      : 'glass hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">{model.name}</span>
                    {selectedModel === model.id && <CheckCircle className="w-4 h-4 text-purple-400" />}
                  </div>
                  <div className="text-xs text-gray-400">
                    {model.params} params · {model.accuracy} accuracy
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AutoML */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Zap className="w-5 h-5 text-purple-400" />
                <h2 className="text-xl font-semibold">AutoML</h2>
              </div>
              <button
                onClick={() => setAutoMLEnabled(!autoMLEnabled)}
                className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                  autoMLEnabled
                    ? 'bg-purple-500 text-white'
                    : 'bg-white/5 text-gray-400'
                }`}
              >
                {autoMLEnabled ? 'Enabled' : 'Disabled'}
              </button>
            </div>

            <p className="text-sm text-gray-400">
              Automatically optimize hyperparameters, architecture, and training strategy
            </p>

            {autoMLEnabled && (
              <div className="mt-4 p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-purple-400 mt-0.5" />
                  <div className="text-xs text-gray-300">
                    AutoML will run 20 experiments to find optimal configuration. Estimated time: 4-6 hours.
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Model Versioning */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <GitBranch className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Model Versions</h2>
            </div>

            <div className="space-y-2">
              {modelVersions.map((version, index) => (
                <div key={version.version} className="glass rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-purple-400">{version.version}</span>
                    {index === 0 && (
                      <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">Latest</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-400 space-y-1">
                    <div>Released: {version.date.toLocaleDateString()}</div>
                    <div>Accuracy: {(version.accuracy * 100).toFixed(1)}%</div>
                    <div>Size: {version.size.toFixed(1)} MB</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
