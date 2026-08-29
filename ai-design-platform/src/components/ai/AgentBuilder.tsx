import React, { useState } from 'react';
import { 
  MessageSquare,
  Target,
  Sparkles,
  Play,
  Settings,
  Download,
  GitBranch,
  BarChart3,
  Layout,
  Layers,
  Zap,
  Upload,
  Save,
  Code,
  Cloud
} from 'lucide-react';
import { 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area 
} from 'recharts';

interface AgentTemplate {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: string;
  complexity: 'basic' | 'intermediate' | 'advanced';
}

interface WorkflowNode {
  id: string;
  type: 'input' | 'process' | 'decision' | 'output';
  label: string;
  x: number;
  y: number;
}

interface AgentVersion {
  version: string;
  date: Date;
  accuracy: number;
  status: 'active' | 'archived';
}

interface AnalyticsData {
  date: string;
  requests: number;
  accuracy: number;
  avgLatency: number;
}

export const AgentBuilder: React.FC = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<string>('chatbot');
  const [agentName, setAgentName] = useState('My AI Agent');
  const [isTraining, setIsTraining] = useState(false);
  const [deploymentTarget, setDeploymentTarget] = useState('cloud');

  const templates: AgentTemplate[] = [
    {
      id: 'chatbot',
      name: 'Conversational Chatbot',
      description: 'Customer service and support chatbot with natural language understanding',
      icon: <MessageSquare className="w-6 h-6" />,
      category: 'Communication',
      complexity: 'basic'
    },
    {
      id: 'classifier',
      name: 'Content Classifier',
      description: 'Classify and categorize content, documents, or messages',
      icon: <Target className="w-6 h-6" />,
      category: 'Analysis',
      complexity: 'intermediate'
    },
    {
      id: 'recommender',
      name: 'Recommendation Engine',
      description: 'Personalized recommendations based on user behavior and preferences',
      icon: <Sparkles className="w-6 h-6" />,
      category: 'Personalization',
      complexity: 'advanced'
    },
    {
      id: 'sentiment',
      name: 'Sentiment Analyzer',
      description: 'Analyze sentiment and emotions in text data',
      icon: <BarChart3 className="w-6 h-6" />,
      category: 'Analysis',
      complexity: 'basic'
    },
    {
      id: 'summarizer',
      name: 'Document Summarizer',
      description: 'Generate concise summaries of long documents',
      icon: <Code className="w-6 h-6" />,
      category: 'Processing',
      complexity: 'intermediate'
    },
    {
      id: 'translator',
      name: 'Language Translator',
      description: 'Multi-language translation with context awareness',
      icon: <Layers className="w-6 h-6" />,
      category: 'Communication',
      complexity: 'advanced'
    }
  ];

  const workflowNodes: WorkflowNode[] = [
    { id: '1', type: 'input', label: 'User Input', x: 50, y: 150 },
    { id: '2', type: 'process', label: 'Preprocessing', x: 200, y: 150 },
    { id: '3', type: 'process', label: 'AI Model', x: 350, y: 150 },
    { id: '4', type: 'decision', label: 'Confidence Check', x: 500, y: 150 },
    { id: '5', type: 'output', label: 'Response', x: 650, y: 100 },
    { id: '6', type: 'process', label: 'Human Review', x: 650, y: 200 }
  ];

  const versions: AgentVersion[] = [
    { version: 'v2.1.0', date: new Date('2024-01-22'), accuracy: 0.94, status: 'active' },
    { version: 'v2.0.5', date: new Date('2024-01-15'), accuracy: 0.91, status: 'archived' },
    { version: 'v2.0.0', date: new Date('2024-01-08'), accuracy: 0.88, status: 'archived' }
  ];

  const analyticsData: AnalyticsData[] = [
    { date: 'Jan 15', requests: 1200, accuracy: 0.89, avgLatency: 145 },
    { date: 'Jan 16', requests: 1450, accuracy: 0.90, avgLatency: 142 },
    { date: 'Jan 17', requests: 1350, accuracy: 0.91, avgLatency: 138 },
    { date: 'Jan 18', requests: 1580, accuracy: 0.92, avgLatency: 135 },
    { date: 'Jan 19', requests: 1720, accuracy: 0.93, avgLatency: 132 },
    { date: 'Jan 20', requests: 1650, accuracy: 0.93, avgLatency: 130 },
    { date: 'Jan 21', requests: 1890, accuracy: 0.94, avgLatency: 128 },
    { date: 'Jan 22', requests: 2100, accuracy: 0.94, avgLatency: 125 }
  ];

  const [configuration, setConfiguration] = useState({
    maxTokens: 2048,
    temperature: 0.7,
    topP: 0.9,
    frequencyPenalty: 0.0,
    presencePenalty: 0.0,
    systemPrompt: 'You are a helpful AI assistant.'
  });

  const handleTrain = () => {
    setIsTraining(true);
    setTimeout(() => setIsTraining(false), 3000);
  };

  const getNodeColor = (type: WorkflowNode['type']) => {
    switch (type) {
      case 'input': return 'bg-blue-500';
      case 'process': return 'bg-purple-500';
      case 'decision': return 'bg-yellow-500';
      case 'output': return 'bg-green-500';
    }
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Agent Builder</h1>
          <p className="text-gray-400">Design and deploy custom AI agents with visual workflow editor</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">
            <Save className="w-4 h-4 mr-2" />
            Save Draft
          </button>
          <button className="btn-primary">
            <Cloud className="w-4 h-4 mr-2" />
            Deploy Agent
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Canvas */}
        <div className="lg:col-span-2 space-y-6">
          {/* Templates */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Layout className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Pre-built Templates</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {templates.map((template) => (
                <div
                  key={template.id}
                  onClick={() => setSelectedTemplate(template.id)}
                  className={`p-4 rounded-lg cursor-pointer transition-all ${
                    selectedTemplate === template.id
                      ? 'bg-purple-500/20 border-2 border-purple-500'
                      : 'glass hover:bg-white/10 border-2 border-transparent'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
                      {template.icon}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium mb-1">{template.name}</div>
                      <div className="text-xs text-gray-400 mb-2">{template.description}</div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded">
                          {template.category}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          template.complexity === 'basic' ? 'bg-green-500/20 text-green-400' :
                          template.complexity === 'intermediate' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {template.complexity}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Visual Workflow Canvas */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Layers className="w-5 h-5 text-purple-400" />
                <h2 className="text-xl font-semibold">Workflow Canvas</h2>
              </div>
              <div className="text-xs text-gray-400">Drag to rearrange nodes</div>
            </div>

            <div className="relative bg-gradient-to-br from-purple-500/5 to-blue-500/5 rounded-lg p-6 min-h-[400px] border border-white/10">
              {/* Grid Pattern */}
              <div className="absolute inset-0 opacity-10" style={{
                backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)',
                backgroundSize: '20px 20px'
              }} />

              {/* Workflow Nodes */}
              {workflowNodes.map((node) => (
                <div
                  key={node.id}
                  className="absolute glass-hover rounded-lg p-3 cursor-move"
                  style={{ left: node.x, top: node.y, width: '120px' }}
                >
                  <div className={`w-2 h-2 rounded-full ${getNodeColor(node.type)} mb-2`} />
                  <div className="text-sm font-medium">{node.label}</div>
                  <div className="text-xs text-gray-500 capitalize">{node.type}</div>
                </div>
              ))}

              {/* Connection Lines (SVG) */}
              <svg className="absolute inset-0 pointer-events-none" style={{ width: '100%', height: '100%' }}>
                <line x1="120" y1="165" x2="200" y2="165" stroke="#8B5CF6" strokeWidth="2" />
                <line x1="320" y1="165" x2="350" y2="165" stroke="#8B5CF6" strokeWidth="2" />
                <line x1="470" y1="165" x2="500" y2="165" stroke="#8B5CF6" strokeWidth="2" />
                <line x1="620" y1="165" x2="650" y2="115" stroke="#10B981" strokeWidth="2" />
                <line x1="620" y1="165" x2="650" y2="215" stroke="#F59E0B" strokeWidth="2" />
              </svg>
            </div>

            <div className="mt-4 flex items-center gap-2">
              <div className="flex items-center gap-2 text-xs">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-gray-400">Input</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-3 h-3 rounded-full bg-purple-500" />
                <span className="text-gray-400">Process</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <span className="text-gray-400">Decision</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-gray-400">Output</span>
              </div>
            </div>
          </div>

          {/* Training Interface */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Zap className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Training</h2>
            </div>

            <div className="space-y-4">
              <div className="glass rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <div className="font-medium mb-1">Training Dataset</div>
                    <div className="text-sm text-gray-400">10,000 examples · 5.2 MB</div>
                  </div>
                  <button className="btn-secondary text-sm">
                    <Upload className="w-4 h-4 mr-1" />
                    Upload
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-gray-400 mb-1">Training</div>
                    <div className="font-semibold">7,000</div>
                  </div>
                  <div>
                    <div className="text-gray-400 mb-1">Validation</div>
                    <div className="font-semibold">2,000</div>
                  </div>
                  <div>
                    <div className="text-gray-400 mb-1">Testing</div>
                    <div className="font-semibold">1,000</div>
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <button 
                  onClick={handleTrain}
                  disabled={isTraining}
                  className={`btn-primary flex-1 ${isTraining ? 'opacity-50' : ''}`}
                >
                  {isTraining ? (
                    <>
                      <Settings className="w-4 h-4 mr-2 animate-spin" />
                      Training...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Start Training
                    </>
                  )}
                </button>
                <button className="btn-secondary">
                  <Settings className="w-4 h-4" />
                </button>
              </div>

              {isTraining && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Progress</span>
                    <span className="text-purple-400">45%</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-2">
                    <div className="bg-gradient-to-r from-purple-600 to-blue-500 h-2 rounded-full w-[45%] transition-all" />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Analytics Preview */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Analytics Preview</h2>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="glass rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-1">Total Requests</div>
                <div className="text-2xl font-bold text-purple-400">12.4K</div>
                <div className="text-xs text-green-400">+24% this week</div>
              </div>
              <div className="glass rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-1">Accuracy</div>
                <div className="text-2xl font-bold text-green-400">94.2%</div>
                <div className="text-xs text-green-400">+2.1% improvement</div>
              </div>
              <div className="glass rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-1">Avg Latency</div>
                <div className="text-2xl font-bold text-blue-400">125ms</div>
                <div className="text-xs text-green-400">-18ms faster</div>
              </div>
            </div>

            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={analyticsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }} 
                />
                <Area type="monotone" dataKey="requests" stroke="#8B5CF6" fill="#8B5CF620" strokeWidth={2} name="Requests" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Sidebar - Configuration */}
        <div className="space-y-6">
          {/* Agent Configuration */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Settings className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Configuration</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Agent Name</label>
                <input
                  type="text"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Max Tokens</label>
                <input
                  type="number"
                  value={configuration.maxTokens}
                  onChange={(e) => setConfiguration({ ...configuration, maxTokens: parseInt(e.target.value) })}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Temperature: {configuration.temperature}</label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={configuration.temperature}
                  onChange={(e) => setConfiguration({ ...configuration, temperature: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Top P: {configuration.topP}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={configuration.topP}
                  onChange={(e) => setConfiguration({ ...configuration, topP: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">System Prompt</label>
                <textarea
                  value={configuration.systemPrompt}
                  onChange={(e) => setConfiguration({ ...configuration, systemPrompt: e.target.value })}
                  rows={4}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                />
              </div>
            </div>
          </div>

          {/* Deployment Options */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Cloud className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Deployment</h2>
            </div>

            <div className="space-y-3">
              {[
                { id: 'cloud', name: 'Cloud', icon: <Cloud className="w-4 h-4" />, desc: 'Managed cloud hosting' },
                { id: 'edge', name: 'Edge', icon: <Zap className="w-4 h-4" />, desc: 'Low-latency edge deployment' },
                { id: 'onprem', name: 'On-Premise', icon: <Settings className="w-4 h-4" />, desc: 'Self-hosted infrastructure' }
              ].map((option) => (
                <div
                  key={option.id}
                  onClick={() => setDeploymentTarget(option.id)}
                  className={`p-3 rounded-lg cursor-pointer transition-all ${
                    deploymentTarget === option.id
                      ? 'bg-purple-500/20 border border-purple-500'
                      : 'glass hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div className="text-purple-400">{option.icon}</div>
                    <span className="font-medium">{option.name}</span>
                  </div>
                  <div className="text-xs text-gray-400">{option.desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Version Control */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <GitBranch className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Version Control</h2>
            </div>

            <div className="space-y-2">
              {versions.map((version) => (
                <div key={version.version} className="glass rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-purple-400">{version.version}</span>
                    {version.status === 'active' && (
                      <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded">
                        Active
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-400 space-y-1">
                    <div>{version.date.toLocaleDateString()}</div>
                    <div>Accuracy: {(version.accuracy * 100).toFixed(1)}%</div>
                  </div>
                </div>
              ))}
            </div>

            <button className="btn-secondary w-full mt-3">
              <Download className="w-4 h-4 mr-2" />
              Export Version
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
