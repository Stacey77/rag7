import { useState, useCallback } from 'react';
import { Dashboard } from './components/Dashboard';
import { AIAdvisor } from './components/AIAdvisor';
import { ChatWidget } from './components/ChatWidget';
import { MOCK_BUDGET_DATA } from './data/mockBudget';
import './app.css';

const STORAGE_KEY_AI_DISABLED = 'rag7:ai-disabled';
const STORAGE_KEY_API_KEY = 'rag7:api-key';

type Tab = 'dashboard' | 'advisor';

function App() {
  const [tab, setTab] = useState<Tab>('dashboard');
  const [apiKey, setApiKey] = useState<string>(
    () => localStorage.getItem(STORAGE_KEY_API_KEY) ?? '',
  );
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [aiDisabled, setAiDisabled] = useState<boolean>(
    () => localStorage.getItem(STORAGE_KEY_AI_DISABLED) === 'true',
  );

  const toggleAI = useCallback(() => {
    setAiDisabled((prev) => {
      const next = !prev;
      localStorage.setItem(STORAGE_KEY_AI_DISABLED, String(next));
      return next;
    });
  }, []);

  const handleSaveKey = useCallback(() => {
    const trimmed = apiKeyInput.trim();
    setApiKey(trimmed);
    localStorage.setItem(STORAGE_KEY_API_KEY, trimmed);
    setApiKeyInput('');
  }, [apiKeyInput]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>💰 BudgetAI</h1>
        <nav className="app-nav">
          <button
            className={`nav-btn ${tab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`nav-btn ${tab === 'advisor' ? 'active' : ''}`}
            onClick={() => setTab('advisor')}
          >
            AI Advisor
          </button>
        </nav>
      </header>

      {!apiKey && (
        <div className="api-key-banner">
          <p>
            Enter your <strong>Gemini API key</strong> to enable AI features.
            You can get one at{' '}
            <a
              href="https://aistudio.google.com/apikey"
              target="_blank"
              rel="noreferrer"
            >
              aistudio.google.com
            </a>
            .
          </p>
          <div className="api-key-input-row">
            <input
              type="password"
              placeholder="AIza..."
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSaveKey()}
              className="api-key-input"
            />
            <button
              className="btn-primary"
              onClick={handleSaveKey}
              disabled={!apiKeyInput.trim()}
            >
              Save Key
            </button>
          </div>
        </div>
      )}

      <main className="app-main">
        {tab === 'dashboard' && (
          <Dashboard
            apiKey={apiKey}
            data={MOCK_BUDGET_DATA}
            aiDisabled={aiDisabled}
            onToggleAI={toggleAI}
          />
        )}
        {tab === 'advisor' && (
          <AIAdvisor
            apiKey={apiKey}
            data={MOCK_BUDGET_DATA}
            aiDisabled={aiDisabled}
            onToggleAI={toggleAI}
          />
        )}
      </main>

      <ChatWidget apiKey={apiKey} data={MOCK_BUDGET_DATA} aiDisabled={aiDisabled} />
    </div>
  );
}

export default App;
