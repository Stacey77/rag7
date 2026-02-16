import React, { useState } from 'react';
import { 
  Code, 
  Book,
  Play,
  Download,
  Key,
  Webhook,
  Zap,
  Copy,
  CheckCircle,
  AlertCircle,
  Globe,
  Clock,
  TrendingUp
} from 'lucide-react';
import { 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';

interface APIEndpoint {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  description: string;
  category: 'REST' | 'GraphQL';
}

interface CodeExample {
  language: string;
  code: string;
  icon: string;
}

interface SDK {
  name: string;
  language: string;
  version: string;
  downloads: number;
  size: string;
}

interface RateLimit {
  tier: string;
  requestsPerMinute: number;
  requestsPerDay: number;
  burstAllowance: number;
}

export const DeveloperPortal: React.FC = () => {
  const [selectedEndpoint, setSelectedEndpoint] = useState<string>('inference');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('python');
  const [copied, setCopied] = useState(false);
  const [testResponse, setTestResponse] = useState<any>(null);

  const apiKey = 'sk_live_abc123def456...';

  const endpoints: APIEndpoint[] = [
    { id: 'inference', method: 'POST', path: '/api/v1/inference', description: 'Run model inference', category: 'REST' },
    { id: 'models', method: 'GET', path: '/api/v1/models', description: 'List available models', category: 'REST' },
    { id: 'train', method: 'POST', path: '/api/v1/train', description: 'Start training job', category: 'REST' },
    { id: 'jobs', method: 'GET', path: '/api/v1/jobs/:id', description: 'Get job status', category: 'REST' },
    { id: 'datasets', method: 'POST', path: '/api/v1/datasets', description: 'Upload dataset', category: 'REST' },
    { id: 'metrics', method: 'GET', path: '/api/v1/metrics', description: 'Get model metrics', category: 'REST' },
    { id: 'graphql', method: 'POST', path: '/graphql', description: 'GraphQL endpoint', category: 'GraphQL' }
  ];

  const codeExamples: Record<string, CodeExample[]> = {
    inference: [
      {
        language: 'python',
        icon: '🐍',
        code: `import requests

api_key = "sk_live_abc123def456..."
url = "https://api.aiplatform.com/v1/inference"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "gpt-4",
    "input": "What is machine learning?",
    "max_tokens": 100
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
print(result)`
      },
      {
        language: 'javascript',
        icon: '📜',
        code: `const apiKey = 'sk_live_abc123def456...';
const url = 'https://api.aiplatform.com/v1/inference';

const response = await fetch(url, {
  method: 'POST',
  headers: {
    'Authorization': \`Bearer \${apiKey}\`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'gpt-4',
    input: 'What is machine learning?',
    max_tokens: 100
  })
});

const result = await response.json();
console.log(result);`
      },
      {
        language: 'java',
        icon: '☕',
        code: `import java.net.http.*;
import java.net.URI;

String apiKey = "sk_live_abc123def456...";
String url = "https://api.aiplatform.com/v1/inference";

HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create(url))
    .header("Authorization", "Bearer " + apiKey)
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString(
        "{\\"model\\":\\"gpt-4\\",\\"input\\":\\"What is ML?\\"}"
    ))
    .build();

HttpResponse<String> response = client.send(request, 
    HttpResponse.BodyHandlers.ofString());
System.out.println(response.body());`
      },
      {
        language: 'go',
        icon: '🔷',
        code: `package main

import (
    "bytes"
    "encoding/json"
    "net/http"
)

func main() {
    apiKey := "sk_live_abc123def456..."
    url := "https://api.aiplatform.com/v1/inference"
    
    payload := map[string]interface{}{
        "model": "gpt-4",
        "input": "What is machine learning?",
        "max_tokens": 100,
    }
    
    jsonData, _ := json.Marshal(payload)
    req, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
    req.Header.Set("Authorization", "Bearer "+apiKey)
    req.Header.Set("Content-Type", "application/json")
    
    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()
}`
      },
      {
        language: 'ruby',
        icon: '💎',
        code: `require 'net/http'
require 'json'

api_key = 'sk_live_abc123def456...'
url = URI('https://api.aiplatform.com/v1/inference')

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request['Authorization'] = "Bearer #{api_key}"
request['Content-Type'] = 'application/json'

request.body = {
  model: 'gpt-4',
  input: 'What is machine learning?',
  max_tokens: 100
}.to_json

response = http.request(request)
puts JSON.parse(response.body)`
      }
    ]
  };

  const sdks: SDK[] = [
    { name: 'Python SDK', language: 'Python', version: '2.1.0', downloads: 125000, size: '2.4 MB' },
    { name: 'JavaScript SDK', language: 'JavaScript', version: '1.8.5', downloads: 98000, size: '1.8 MB' },
    { name: 'Java SDK', language: 'Java', version: '1.5.2', downloads: 45000, size: '4.2 MB' },
    { name: 'Go SDK', language: 'Go', version: '1.3.0', downloads: 32000, size: '1.2 MB' },
    { name: 'Ruby SDK', language: 'Ruby', version: '1.2.8', downloads: 18000, size: '1.5 MB' }
  ];

  const rateLimits: RateLimit[] = [
    { tier: 'Free', requestsPerMinute: 60, requestsPerDay: 1000, burstAllowance: 10 },
    { tier: 'Pro', requestsPerMinute: 600, requestsPerDay: 100000, burstAllowance: 100 },
    { tier: 'Enterprise', requestsPerMinute: 6000, requestsPerDay: 1000000, burstAllowance: 1000 }
  ];

  const usageData = [
    { date: 'Jan 15', requests: 8500, errors: 45 },
    { date: 'Jan 16', requests: 9200, errors: 32 },
    { date: 'Jan 17', requests: 8900, errors: 28 },
    { date: 'Jan 18', requests: 10500, errors: 51 },
    { date: 'Jan 19', requests: 11200, errors: 38 },
    { date: 'Jan 20', requests: 10800, errors: 42 },
    { date: 'Jan 21', requests: 12400, errors: 35 }
  ];

  const handleCopyApiKey = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTryIt = () => {
    setTestResponse({
      status: 200,
      data: {
        model: 'gpt-4',
        output: 'Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.',
        tokens: 23,
        latency: 145
      }
    });
  };

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET': return 'text-green-400 bg-green-400/10';
      case 'POST': return 'text-blue-400 bg-blue-400/10';
      case 'PUT': return 'text-yellow-400 bg-yellow-400/10';
      case 'DELETE': return 'text-red-400 bg-red-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Developer Portal</h1>
          <p className="text-gray-400">Comprehensive API documentation and developer resources</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">
            <Book className="w-4 h-4 mr-2" />
            Docs
          </button>
          <button className="btn-primary">
            <Key className="w-4 h-4 mr-2" />
            Generate API Key
          </button>
        </div>
      </div>

      {/* API Key Section */}
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <Key className="w-5 h-5 text-purple-400" />
          <h2 className="text-xl font-semibold">API Key</h2>
        </div>

        <div className="flex gap-2">
          <div className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 font-mono text-sm flex items-center justify-between">
            <span className="text-gray-300">{apiKey}</span>
            <button
              onClick={handleCopyApiKey}
              className="ml-4 text-purple-400 hover:text-purple-300 transition-colors"
            >
              {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <div className="mt-3 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-yellow-400 mt-0.5" />
          <div className="text-xs text-yellow-300">
            Keep your API key secure. Never expose it in client-side code or public repositories.
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* API Endpoints & Examples */}
        <div className="lg:col-span-2 space-y-6">
          {/* Endpoints List */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Code className="w-5 h-5 text-purple-400" />
                <h2 className="text-xl font-semibold">API Endpoints</h2>
              </div>
              <div className="flex gap-2">
                <button className="btn-secondary text-xs">REST</button>
                <button className="btn-secondary text-xs">GraphQL</button>
              </div>
            </div>

            <div className="space-y-2">
              {endpoints.map((endpoint) => (
                <div
                  key={endpoint.id}
                  onClick={() => setSelectedEndpoint(endpoint.id)}
                  className={`p-4 rounded-lg cursor-pointer transition-all ${
                    selectedEndpoint === endpoint.id
                      ? 'bg-purple-500/20 border border-purple-500'
                      : 'glass hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${getMethodColor(endpoint.method)}`}>
                      {endpoint.method}
                    </span>
                    <code className="text-sm font-mono text-purple-400">{endpoint.path}</code>
                  </div>
                  <p className="text-sm text-gray-400">{endpoint.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Code Examples */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Code className="w-5 h-5 text-purple-400" />
                <h2 className="text-xl font-semibold">Code Examples</h2>
              </div>
              <div className="flex gap-2">
                {['python', 'javascript', 'java', 'go', 'ruby'].map((lang) => (
                  <button
                    key={lang}
                    onClick={() => setSelectedLanguage(lang)}
                    className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                      selectedLanguage === lang
                        ? 'bg-purple-500 text-white'
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    {lang.charAt(0).toUpperCase() + lang.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {codeExamples[selectedEndpoint]?.find(ex => ex.language === selectedLanguage) && (
              <div className="relative">
                <button
                  onClick={() => {
                    const code = codeExamples[selectedEndpoint].find(ex => ex.language === selectedLanguage)?.code || '';
                    navigator.clipboard.writeText(code);
                  }}
                  className="absolute top-4 right-4 btn-secondary text-xs z-10"
                >
                  <Copy className="w-3 h-3 mr-1" />
                  Copy
                </button>
                <pre className="bg-gray-950 border border-white/10 rounded-lg p-4 overflow-x-auto">
                  <code className="text-sm font-mono text-gray-300">
                    {codeExamples[selectedEndpoint].find(ex => ex.language === selectedLanguage)?.code}
                  </code>
                </pre>
              </div>
            )}
          </div>

          {/* Try It Out */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Play className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Try It Out</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Request Body</label>
                <textarea
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white font-mono text-sm"
                  rows={6}
                  defaultValue={`{
  "model": "gpt-4",
  "input": "What is machine learning?",
  "max_tokens": 100
}`}
                />
              </div>

              <button onClick={handleTryIt} className="btn-primary">
                <Play className="w-4 h-4 mr-2" />
                Send Request
              </button>

              {testResponse && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full" />
                    <span className="text-sm font-semibold text-green-400">
                      {testResponse.status} OK
                    </span>
                    <span className="text-xs text-gray-400">
                      {testResponse.data.latency}ms
                    </span>
                  </div>

                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Response</label>
                    <pre className="bg-gray-950 border border-white/10 rounded-lg p-4 overflow-x-auto">
                      <code className="text-sm font-mono text-gray-300">
                        {JSON.stringify(testResponse.data, null, 2)}
                      </code>
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* API Usage Statistics */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">API Usage</h2>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="glass rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-1">Requests (7d)</div>
                <div className="text-2xl font-bold text-purple-400">71.5K</div>
                <div className="text-xs text-green-400">+12.3%</div>
              </div>
              <div className="glass rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-1">Success Rate</div>
                <div className="text-2xl font-bold text-green-400">99.6%</div>
                <div className="text-xs text-green-400">+0.2%</div>
              </div>
              <div className="glass rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-1">Avg Latency</div>
                <div className="text-2xl font-bold text-blue-400">142ms</div>
                <div className="text-xs text-green-400">-8ms</div>
              </div>
            </div>

            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={usageData}>
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
                <Bar dataKey="requests" fill="#8B5CF6" />
                <Bar dataKey="errors" fill="#EF4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* SDK Downloads */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Download className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">SDK Downloads</h2>
            </div>

            <div className="space-y-2">
              {sdks.map((sdk) => (
                <div key={sdk.name} className="glass rounded-lg p-3 hover:bg-white/10 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium text-sm">{sdk.name}</div>
                    <span className="text-xs text-purple-400">{sdk.version}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
                    <span>{sdk.downloads.toLocaleString()} downloads</span>
                    <span>{sdk.size}</span>
                  </div>
                  <button className="btn-secondary w-full text-xs">
                    <Download className="w-3 h-3 mr-1" />
                    Download
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Webhooks */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Webhook className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Webhooks</h2>
            </div>

            <div className="space-y-3">
              <p className="text-sm text-gray-400">
                Configure webhooks to receive real-time notifications about events.
              </p>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Webhook URL</label>
                <input
                  type="text"
                  placeholder="https://your-app.com/webhook"
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Events</label>
                <div className="space-y-2">
                  {['model.trained', 'job.completed', 'inference.error', 'dataset.uploaded'].map((event) => (
                    <label key={event} className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" />
                      <span className="text-sm text-gray-300">{event}</span>
                    </label>
                  ))}
                </div>
              </div>

              <button className="btn-primary w-full">
                <Zap className="w-4 h-4 mr-2" />
                Add Webhook
              </button>
            </div>
          </div>

          {/* Rate Limits */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Clock className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Rate Limits</h2>
            </div>

            <div className="space-y-3">
              {rateLimits.map((limit) => (
                <div key={limit.tier} className="glass rounded-lg p-3">
                  <div className="font-medium text-sm mb-2">{limit.tier}</div>
                  <div className="space-y-1 text-xs text-gray-400">
                    <div className="flex justify-between">
                      <span>Per Minute:</span>
                      <span className="text-purple-400">{limit.requestsPerMinute.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Per Day:</span>
                      <span className="text-purple-400">{limit.requestsPerDay.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Burst:</span>
                      <span className="text-purple-400">{limit.burstAllowance}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <div className="text-xs text-blue-300">
                Current tier: <span className="font-semibold">Pro</span>
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Upgrade to Enterprise for higher limits
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <Globe className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Resources</h2>
            </div>

            <div className="space-y-2">
              {[
                { name: 'API Reference', icon: <Book className="w-4 h-4" /> },
                { name: 'Tutorials', icon: <Play className="w-4 h-4" /> },
                { name: 'Community Forum', icon: <Globe className="w-4 h-4" /> },
                { name: 'Status Page', icon: <TrendingUp className="w-4 h-4" /> },
                { name: 'Changelog', icon: <Code className="w-4 h-4" /> }
              ].map((resource) => (
                <button
                  key={resource.name}
                  className="w-full glass rounded-lg p-3 hover:bg-white/10 transition-colors text-left flex items-center gap-3"
                >
                  <div className="text-purple-400">{resource.icon}</div>
                  <span className="text-sm">{resource.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
