import React, { useState } from 'react';
import { 
  Upload, 
  Brain, 
  Settings, 
  Play, 
  Pause,
  RotateCw,
  CheckCircle,
  FileText,
  Database,
  Activity,
  Target,
  Award,
  AlertCircle,
  Download,
  Eye
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

interface Dataset {
  id: string;
  name: string;
  size: number;
  type: string;
  quality: number;
  uploaded: Date;
}

interface TrainingMetrics {
  epoch: number;
  loss: number;
  accuracy: number;
  valLoss: number;
  valAccuracy: number;
}

interface HyperParameter {
  name: string;
  value: number;
  min: number;
  max: number;
  step: number;
  description: string;
}

export const AITraining: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'training' | 'evaluation' | 'hyperparameters' | 'active-learning'>('upload');
  const [isTraining, setIsTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);

  const [datasets, setDatasets] = useState<Dataset[]>([
    {
      id: '1',
      name: 'Customer_Data_2024.csv',
      size: 2.4,
      type: 'CSV',
      quality: 92,
      uploaded: new Date('2024-01-15')
    },
    {
      id: '2',
      name: 'Product_Images.zip',
      size: 145.8,
      type: 'Images',
      quality: 88,
      uploaded: new Date('2024-01-14')
    },
    {
      id: '3',
      name: 'Transaction_Logs.json',
      size: 18.5,
      type: 'JSON',
      quality: 95,
      uploaded: new Date('2024-01-13')
    }
  ]);

  const [hyperparameters, setHyperparameters] = useState<HyperParameter[]>([
    { name: 'Learning Rate', value: 0.001, min: 0.0001, max: 0.1, step: 0.0001, description: 'Controls how much to change the model in response to error' },
    { name: 'Batch Size', value: 32, min: 8, max: 256, step: 8, description: 'Number of samples processed before the model is updated' },
    { name: 'Epochs', value: 100, min: 10, max: 1000, step: 10, description: 'Number of complete passes through the training dataset' },
    { name: 'Dropout Rate', value: 0.2, min: 0, max: 0.8, step: 0.05, description: 'Fraction of neurons to drop for regularization' },
    { name: 'Weight Decay', value: 0.0001, min: 0, max: 0.01, step: 0.0001, description: 'L2 regularization parameter' }
  ]);

  const trainingMetrics: TrainingMetrics[] = [
    { epoch: 1, loss: 0.89, accuracy: 65, valLoss: 0.92, valAccuracy: 63 },
    { epoch: 2, loss: 0.75, accuracy: 72, valLoss: 0.78, valAccuracy: 70 },
    { epoch: 3, loss: 0.63, accuracy: 78, valLoss: 0.68, valAccuracy: 76 },
    { epoch: 4, loss: 0.54, accuracy: 82, valLoss: 0.59, valAccuracy: 80 },
    { epoch: 5, loss: 0.47, accuracy: 86, valLoss: 0.52, valAccuracy: 84 },
    { epoch: 6, loss: 0.41, accuracy: 89, valLoss: 0.47, valAccuracy: 87 },
    { epoch: 7, loss: 0.36, accuracy: 91, valLoss: 0.43, valAccuracy: 89 },
    { epoch: 8, loss: 0.32, accuracy: 93, valLoss: 0.40, valAccuracy: 91 }
  ];

  const evaluationMetrics = [
    { name: 'Accuracy', value: 93.2, target: 90, status: 'excellent' },
    { name: 'Precision', value: 91.8, target: 88, status: 'excellent' },
    { name: 'Recall', value: 92.5, target: 87, status: 'excellent' },
    { name: 'F1 Score', value: 92.1, target: 88, status: 'excellent' },
    { name: 'AUC-ROC', value: 0.95, target: 0.90, status: 'excellent' }
  ];

  const activeLearningData = [
    { id: '1', sample: 'Sample #1247', confidence: 45, label: 'Uncertain', priority: 'high' },
    { id: '2', sample: 'Sample #1248', confidence: 52, label: 'Uncertain', priority: 'high' },
    { id: '3', sample: 'Sample #1249', confidence: 61, label: 'Uncertain', priority: 'medium' },
    { id: '4', sample: 'Sample #1250', confidence: 68, label: 'Review', priority: 'medium' },
    { id: '5', sample: 'Sample #1251', confidence: 71, label: 'Review', priority: 'low' }
  ];

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      // Simulate file upload
      const newDataset: Dataset = {
        id: Date.now().toString(),
        name: files[0].name,
        size: files[0].size / (1024 * 1024),
        type: files[0].type.includes('image') ? 'Images' : 
              files[0].type.includes('json') ? 'JSON' : 'CSV',
        quality: Math.floor(Math.random() * 20) + 80,
        uploaded: new Date()
      };
      setDatasets(prev => [...prev, newDataset]);
    }
  };

  const startTraining = () => {
    setIsTraining(true);
    setTrainingProgress(0);
    
    const interval = setInterval(() => {
      setTrainingProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsTraining(false);
          return 100;
        }
        return prev + 2;
      });
    }, 100);
  };

  const updateHyperparameter = (index: number, value: number) => {
    setHyperparameters(prev => prev.map((hp, i) => 
      i === index ? { ...hp, value } : hp
    ));
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">AI Training Studio</h1>
          <p className="text-gray-400">Train and optimize custom AI models</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export Model
          </button>
          <button 
            className="btn-primary flex items-center gap-2"
            onClick={startTraining}
            disabled={isTraining}
          >
            {isTraining ? (
              <>
                <Pause className="w-4 h-4" />
                Training...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Start Training
              </>
            )}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 overflow-x-auto">
        {[
          { id: 'upload', label: 'Dataset Upload', icon: <Upload className="w-4 h-4" /> },
          { id: 'training', label: 'Training Progress', icon: <Activity className="w-4 h-4" /> },
          { id: 'evaluation', label: 'Model Evaluation', icon: <Target className="w-4 h-4" /> },
          { id: 'hyperparameters', label: 'Hyperparameters', icon: <Settings className="w-4 h-4" /> },
          { id: 'active-learning', label: 'Active Learning', icon: <Brain className="w-4 h-4" /> }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-all whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-purple-500 text-purple-400'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Dataset Upload */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          {/* Upload Area */}
          <div className="card">
            <div className="border-2 border-dashed border-white/20 rounded-xl p-12 text-center hover:border-purple-500/50 transition-colors cursor-pointer">
              <input
                type="file"
                id="file-upload"
                className="hidden"
                onChange={handleUpload}
                multiple
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center">
                  <Upload className="w-8 h-8 text-purple-400" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">Upload Training Data</h3>
                <p className="text-gray-400 mb-4">
                  Drag and drop files or click to browse
                </p>
                <p className="text-sm text-gray-500">
                  Supports CSV, JSON, Images (PNG, JPG), and Archive files (ZIP)
                </p>
              </label>
            </div>
          </div>

          {/* Dataset List */}
          <div className="card">
            <h2 className="text-xl font-bold text-white mb-4">Uploaded Datasets</h2>
            <div className="space-y-3">
              {datasets.map(dataset => (
                <div key={dataset.id} className="p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="p-2 bg-purple-500/20 rounded-lg">
                        {dataset.type === 'Images' ? <Database className="w-5 h-5 text-purple-400" /> : <FileText className="w-5 h-5 text-purple-400" />}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-white mb-1">{dataset.name}</h3>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span>{dataset.size.toFixed(1)} MB</span>
                          <span>•</span>
                          <span>{dataset.type}</span>
                          <span>•</span>
                          <span>{dataset.uploaded.toLocaleDateString()}</span>
                        </div>
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-gray-400">Data Quality</span>
                            <span className={`font-medium ${
                              dataset.quality >= 90 ? 'text-green-400' :
                              dataset.quality >= 75 ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                              {dataset.quality}%
                            </span>
                          </div>
                          <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${
                                dataset.quality >= 90 ? 'bg-green-500' :
                                dataset.quality >= 75 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${dataset.quality}%` }}
                            />
                          </div>
                        </div>
                      </div>
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
      )}

      {/* Training Progress */}
      {activeTab === 'training' && (
        <div className="space-y-6">
          {/* Training Status */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Training Status</h2>
                <p className="text-sm text-gray-400">
                  {isTraining ? 'Model training in progress...' : 'Ready to train'}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {isTraining && (
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
                )}
                <span className={`text-sm font-medium ${isTraining ? 'text-green-400' : 'text-gray-400'}`}>
                  {isTraining ? 'Active' : 'Idle'}
                </span>
              </div>
            </div>

            {isTraining && (
              <div className="mb-6 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-300">Overall Progress</span>
                  <span className="text-lg font-bold gradient-text">{trainingProgress}%</span>
                </div>
                <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-300 glow"
                    style={{ width: `${trainingProgress}%` }}
                  />
                </div>
                <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Epoch:</span>
                    <span className="ml-2 text-white font-medium">
                      {Math.floor(trainingProgress / 12.5)} / 8
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Loss:</span>
                    <span className="ml-2 text-white font-medium">0.32</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Accuracy:</span>
                    <span className="ml-2 text-white font-medium">93%</span>
                  </div>
                </div>
              </div>
            )}

            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trainingMetrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="epoch" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="loss" stroke="#ef4444" strokeWidth={2} name="Training Loss" />
                <Line type="monotone" dataKey="valLoss" stroke="#f59e0b" strokeWidth={2} name="Validation Loss" />
                <Line type="monotone" dataKey="accuracy" stroke="#10b981" strokeWidth={2} name="Training Accuracy" />
                <Line type="monotone" dataKey="valAccuracy" stroke="#3b82f6" strokeWidth={2} name="Validation Accuracy" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Model Evaluation */}
      {activeTab === 'evaluation' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {evaluationMetrics.map((metric, idx) => (
              <div key={idx} className="card">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-sm text-gray-400 mb-1">{metric.name}</h3>
                    <div className="text-3xl font-bold text-white">
                      {metric.name === 'AUC-ROC' ? metric.value.toFixed(2) : `${metric.value}%`}
                    </div>
                  </div>
                  <div className={`p-2 rounded-lg ${
                    metric.status === 'excellent' ? 'bg-green-500/20' : 'bg-yellow-500/20'
                  }`}>
                    <Award className={`w-5 h-5 ${
                      metric.status === 'excellent' ? 'text-green-400' : 'text-yellow-400'
                    }`} />
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-gray-400">Target:</span>
                  <span className="text-gray-300">
                    {metric.name === 'AUC-ROC' ? metric.target.toFixed(2) : `${metric.target}%`}
                  </span>
                  <CheckCircle className="w-4 h-4 text-green-400 ml-auto" />
                </div>
              </div>
            ))}
          </div>

          <div className="card">
            <h2 className="text-xl font-bold text-white mb-4">Confusion Matrix</h2>
            <div className="grid grid-cols-2 gap-4 max-w-md">
              <div className="p-6 bg-green-500/20 border border-green-500/30 rounded-lg text-center">
                <div className="text-sm text-gray-400 mb-2">True Positive</div>
                <div className="text-3xl font-bold text-green-400">842</div>
              </div>
              <div className="p-6 bg-red-500/20 border border-red-500/30 rounded-lg text-center">
                <div className="text-sm text-gray-400 mb-2">False Positive</div>
                <div className="text-3xl font-bold text-red-400">23</div>
              </div>
              <div className="p-6 bg-red-500/20 border border-red-500/30 rounded-lg text-center">
                <div className="text-sm text-gray-400 mb-2">False Negative</div>
                <div className="text-3xl font-bold text-red-400">18</div>
              </div>
              <div className="p-6 bg-green-500/20 border border-green-500/30 rounded-lg text-center">
                <div className="text-sm text-gray-400 mb-2">True Negative</div>
                <div className="text-3xl font-bold text-green-400">917</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hyperparameters */}
      {activeTab === 'hyperparameters' && (
        <div className="card space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white mb-1">Hyperparameter Tuning</h2>
              <p className="text-sm text-gray-400">Adjust model training parameters</p>
            </div>
            <button className="btn-secondary flex items-center gap-2">
              <RotateCw className="w-4 h-4" />
              Reset to Default
            </button>
          </div>

          <div className="space-y-6">
            {hyperparameters.map((param, idx) => (
              <div key={idx} className="p-4 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-white mb-1">{param.name}</h3>
                    <p className="text-xs text-gray-400">{param.description}</p>
                  </div>
                  <div className="text-right ml-4">
                    <div className="text-2xl font-bold text-purple-400">{param.value}</div>
                    <div className="text-xs text-gray-500">
                      {param.min} - {param.max}
                    </div>
                  </div>
                </div>
                <input
                  type="range"
                  min={param.min}
                  max={param.max}
                  step={param.step}
                  value={param.value}
                  onChange={(e) => updateHyperparameter(idx, parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>{param.min}</span>
                  <span>{param.max}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Learning */}
      {activeTab === 'active-learning' && (
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Active Learning Queue</h2>
                <p className="text-sm text-gray-400">Review uncertain predictions for model improvement</p>
              </div>
              <button className="btn-primary flex items-center gap-2">
                <Brain className="w-4 h-4" />
                Label Batch
              </button>
            </div>

            <div className="space-y-3">
              {activeLearningData.map((sample) => (
                <div key={sample.id} className="p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-semibold text-white">{sample.sample}</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          sample.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                          sample.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-blue-500/20 text-blue-400'
                        }`}>
                          {sample.priority.toUpperCase()}
                        </span>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 text-sm text-gray-400">
                          <AlertCircle className="w-4 h-4" />
                          Confidence: {sample.confidence}%
                        </div>
                        <div className="flex-1 max-w-xs">
                          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${
                                sample.confidence < 50 ? 'bg-red-500' :
                                sample.confidence < 70 ? 'bg-yellow-500' : 'bg-green-500'
                              }`}
                              style={{ width: `${sample.confidence}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2 ml-4">
                      <button className="btn-secondary text-sm">Review</button>
                      <button className="btn-primary text-sm">Label</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
