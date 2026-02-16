import React, { useState } from 'react';
import { 
  Play, 
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  FileCode,
  Layers,
  TrendingUp,
  BarChart3,
  Settings,
  Plus,
  Search
} from 'lucide-react';
import { 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts';

interface TestCase {
  id: string;
  name: string;
  category: 'unit' | 'integration' | 'performance' | 'regression';
  status: 'passed' | 'failed' | 'pending' | 'running';
  duration: number;
  lastRun: Date;
  coverage: number;
}

interface CoverageData {
  module: string;
  coverage: number;
  lines: number;
  coveredLines: number;
}

export const TestingSuite: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState<'all' | 'unit' | 'integration' | 'performance' | 'regression'>('all');
  const [runningTests, setRunningTests] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  const testCases: TestCase[] = [
    { id: '1', name: 'User Authentication Flow', category: 'unit', status: 'passed', duration: 125, lastRun: new Date('2024-01-22'), coverage: 95 },
    { id: '2', name: 'Database Connection Pool', category: 'unit', status: 'passed', duration: 89, lastRun: new Date('2024-01-22'), coverage: 88 },
    { id: '3', name: 'API Rate Limiting', category: 'unit', status: 'failed', duration: 156, lastRun: new Date('2024-01-22'), coverage: 72 },
    { id: '4', name: 'End-to-End User Journey', category: 'integration', status: 'passed', duration: 2340, lastRun: new Date('2024-01-22'), coverage: 85 },
    { id: '5', name: 'Payment Gateway Integration', category: 'integration', status: 'passed', duration: 1890, lastRun: new Date('2024-01-22'), coverage: 91 },
    { id: '6', name: 'Third-Party API Integration', category: 'integration', status: 'running', duration: 1200, lastRun: new Date('2024-01-22'), coverage: 78 },
    { id: '7', name: 'Load Test - 1000 Concurrent Users', category: 'performance', status: 'passed', duration: 45000, lastRun: new Date('2024-01-21'), coverage: 0 },
    { id: '8', name: 'Database Query Performance', category: 'performance', status: 'failed', duration: 3200, lastRun: new Date('2024-01-21'), coverage: 0 },
    { id: '9', name: 'Memory Leak Detection', category: 'performance', status: 'passed', duration: 8900, lastRun: new Date('2024-01-21'), coverage: 0 },
    { id: '10', name: 'Login Functionality Regression', category: 'regression', status: 'passed', duration: 234, lastRun: new Date('2024-01-22'), coverage: 92 },
    { id: '11', name: 'Data Export Regression', category: 'regression', status: 'passed', duration: 456, lastRun: new Date('2024-01-22'), coverage: 87 },
    { id: '12', name: 'UI Component Rendering', category: 'regression', status: 'pending', duration: 0, lastRun: new Date('2024-01-20'), coverage: 0 }
  ];

  const coverageData: CoverageData[] = [
    { module: 'Authentication', coverage: 95, lines: 1200, coveredLines: 1140 },
    { module: 'Database', coverage: 88, lines: 2400, coveredLines: 2112 },
    { module: 'API Handlers', coverage: 82, lines: 1800, coveredLines: 1476 },
    { module: 'Business Logic', coverage: 91, lines: 3200, coveredLines: 2912 },
    { module: 'UI Components', coverage: 76, lines: 1600, coveredLines: 1216 },
    { module: 'Utils', coverage: 93, lines: 800, coveredLines: 744 }
  ];

  const testHistoryData = [
    { date: 'Jan 15', passed: 45, failed: 3, total: 48 },
    { date: 'Jan 16', passed: 47, failed: 2, total: 49 },
    { date: 'Jan 17', passed: 46, failed: 4, total: 50 },
    { date: 'Jan 18', passed: 48, failed: 2, total: 50 },
    { date: 'Jan 19', passed: 49, failed: 1, total: 50 },
    { date: 'Jan 20', passed: 47, failed: 3, total: 50 },
    { date: 'Jan 21', passed: 50, failed: 2, total: 52 },
    { date: 'Jan 22', passed: 49, failed: 3, total: 52 }
  ];

  const filteredTests = testCases.filter(test => {
    const matchesCategory = activeCategory === 'all' || test.category === activeCategory;
    const matchesSearch = test.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const testStats = {
    total: testCases.length,
    passed: testCases.filter(t => t.status === 'passed').length,
    failed: testCases.filter(t => t.status === 'failed').length,
    running: testCases.filter(t => t.status === 'running').length,
    pending: testCases.filter(t => t.status === 'pending').length
  };

  const overallCoverage = coverageData.reduce((acc, curr) => acc + curr.coverage, 0) / coverageData.length;

  const handleRunTest = (testId: string) => {
    setRunningTests([...runningTests, testId]);
    setTimeout(() => {
      setRunningTests(runningTests.filter(id => id !== testId));
    }, 3000);
  };

  const handleRunAll = () => {
    const testsToRun = filteredTests.filter(t => t.status !== 'running').map(t => t.id);
    setRunningTests(testsToRun);
    setTimeout(() => {
      setRunningTests([]);
    }, 5000);
  };

  const getStatusIcon = (status: TestCase['status']) => {
    switch (status) {
      case 'passed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'running':
        return <Clock className="w-5 h-5 text-blue-400 animate-spin" />;
      case 'pending':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
    }
  };

  const pieData = [
    { name: 'Passed', value: testStats.passed, color: '#10B981' },
    { name: 'Failed', value: testStats.failed, color: '#EF4444' },
    { name: 'Running', value: testStats.running, color: '#3B82F6' },
    { name: 'Pending', value: testStats.pending, color: '#F59E0B' }
  ];

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Testing Suite</h1>
          <p className="text-gray-400">Automated testing dashboard with comprehensive coverage analysis</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">
            <Plus className="w-4 h-4 mr-2" />
            New Test
          </button>
          <button onClick={handleRunAll} className="btn-primary">
            <Play className="w-4 h-4 mr-2" />
            Run All Tests
          </button>
        </div>
      </div>

      {/* Test Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Total Tests</div>
          <div className="text-3xl font-bold gradient-text">{testStats.total}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
            <CheckCircle className="w-4 h-4 text-green-400" />
            Passed
          </div>
          <div className="text-3xl font-bold text-green-400">{testStats.passed}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
            <XCircle className="w-4 h-4 text-red-400" />
            Failed
          </div>
          <div className="text-3xl font-bold text-red-400">{testStats.failed}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
            <Clock className="w-4 h-4 text-blue-400" />
            Running
          </div>
          <div className="text-3xl font-bold text-blue-400">{testStats.running}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
            <BarChart3 className="w-4 h-4 text-purple-400" />
            Coverage
          </div>
          <div className="text-3xl font-bold text-purple-400">{overallCoverage.toFixed(1)}%</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Test Cases */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <FileCode className="w-5 h-5 text-purple-400" />
                <h2 className="text-xl font-semibold">Test Cases</h2>
              </div>
              <div className="flex gap-2">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search tests..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm"
                  />
                </div>
              </div>
            </div>

            {/* Category Filters */}
            <div className="flex gap-2 mb-4">
              {(['all', 'unit', 'integration', 'performance', 'regression'] as const).map((category) => (
                <button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeCategory === category
                      ? 'bg-purple-500 text-white'
                      : 'bg-white/5 text-gray-400 hover:bg-white/10'
                  }`}
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>

            {/* Test List */}
            <div className="space-y-2">
              {filteredTests.map((test) => (
                <div
                  key={test.id}
                  className="glass rounded-lg p-4 hover:bg-white/10 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      {getStatusIcon(runningTests.includes(test.id) ? 'running' : test.status)}
                      <div className="flex-1">
                        <div className="font-medium mb-1">{test.name}</div>
                        <div className="flex items-center gap-4 text-xs text-gray-400">
                          <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded">
                            {test.category}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {test.duration}ms
                          </span>
                          {test.coverage > 0 && (
                            <span className="flex items-center gap-1">
                              <BarChart3 className="w-3 h-3" />
                              {test.coverage}% coverage
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleRunTest(test.id)}
                      disabled={runningTests.includes(test.id)}
                      className="btn-secondary text-sm"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  </div>

                  {test.status === 'failed' && (
                    <div className="mt-3 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                      <div className="text-xs text-red-400">
                        AssertionError: Expected 200, received 404 at line 45
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Test History & Trends */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Test History & Trends</h2>
            </div>

            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={testHistoryData}>
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
                <Legend />
                <Area type="monotone" dataKey="passed" stackId="1" stroke="#10B981" fill="#10B98140" name="Passed" />
                <Area type="monotone" dataKey="failed" stackId="1" stroke="#EF4444" fill="#EF444440" name="Failed" />
              </AreaChart>
            </ResponsiveContainer>

            <div className="grid grid-cols-3 gap-4 mt-4">
              <div className="glass rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-1">Pass Rate</div>
                <div className="text-2xl font-bold text-green-400">94.2%</div>
                <div className="text-xs text-green-400">+2.1% this week</div>
              </div>
              <div className="glass rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-1">Avg Duration</div>
                <div className="text-2xl font-bold text-blue-400">1.2s</div>
                <div className="text-xs text-green-400">-0.3s faster</div>
              </div>
              <div className="glass rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-1">Total Runs</div>
                <div className="text-2xl font-bold text-purple-400">1,247</div>
                <div className="text-xs text-gray-400">Last 7 days</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Test Distribution */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Layers className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Test Distribution</h2>
            </div>

            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>

            <div className="space-y-2">
              {pieData.map((item) => (
                <div key={item.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-sm text-gray-400">{item.name}</span>
                  </div>
                  <span className="text-sm font-semibold">{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Code Coverage */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Code Coverage</h2>
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Overall Coverage</span>
                <span className="text-sm font-semibold text-purple-400">{overallCoverage.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-white/5 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-600 to-blue-500 h-2 rounded-full"
                  style={{ width: `${overallCoverage}%` }}
                />
              </div>
            </div>

            <div className="space-y-3">
              {coverageData.map((module) => (
                <div key={module.module} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">{module.module}</span>
                    <span className={`font-semibold ${
                      module.coverage >= 90 ? 'text-green-400' :
                      module.coverage >= 75 ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {module.coverage}%
                    </span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full ${
                        module.coverage >= 90 ? 'bg-green-400' :
                        module.coverage >= 75 ? 'bg-yellow-400' :
                        'bg-red-400'
                      }`}
                      style={{ width: `${module.coverage}%` }}
                    />
                  </div>
                  <div className="text-xs text-gray-500">
                    {module.coveredLines} / {module.lines} lines
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Custom Test Builder */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Settings className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Custom Test Builder</h2>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Test Name</label>
                <input
                  type="text"
                  placeholder="My Custom Test"
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Category</label>
                <select className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm">
                  <option value="unit">Unit Test</option>
                  <option value="integration">Integration Test</option>
                  <option value="performance">Performance Test</option>
                  <option value="regression">Regression Test</option>
                </select>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Test Script</label>
                <textarea
                  placeholder="// Write your test code here..."
                  rows={6}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm font-mono"
                />
              </div>

              <button className="btn-primary w-full">
                <Plus className="w-4 h-4 mr-2" />
                Create Test
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
