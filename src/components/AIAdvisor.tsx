import { useState, useEffect, useCallback } from 'react';
import type { BudgetData } from '../types/budget';
import type { AIError } from '../services/aiErrors';
import { getAdvisorResponse, hasAIStudioKey, openAIStudioKeySelector } from '../services/geminiService';
import { cacheClearAll, buildFingerprint } from '../services/aiCache';
import { computeLocalInsights } from '../services/localInsights';
import { FallbackInsights } from './FallbackInsights';

interface Props {
  apiKey: string;
  data: BudgetData;
  aiDisabled: boolean;
  onToggleAI: () => void;
}

export function AIAdvisor({ apiKey, data, aiDisabled, onToggleAI }: Props) {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AIError | null>(null);
  const [fromCache, setFromCache] = useState(false);
  const [cacheCleared, setCacheCleared] = useState(false);

  const localInsights = computeLocalInsights(data);
  const dataFingerprint = buildFingerprint({
    transactions: data.transactions.slice(-10),
    bills: data.bills,
    goals: data.goals,
  });

  // Reset response when data changes materially
  useEffect(() => {
    setResponse(null);
    setError(null);
  }, [dataFingerprint]);

  const handleAsk = useCallback(async () => {
    if (!question.trim() || !apiKey || aiDisabled) return;
    setLoading(true);
    setError(null);
    setFromCache(false);

    const result = await getAdvisorResponse(apiKey, question.trim(), data);
    setLoading(false);

    if (result.ok) {
      setResponse(result.value);
      setFromCache(result.fromCache);
    } else {
      setError(result.error);
    }
  }, [question, apiKey, data, aiDisabled]);

  const handleClearCache = useCallback(() => {
    cacheClearAll();
    setResponse(null);
    setError(null);
    setCacheCleared(true);
    setTimeout(() => setCacheCleared(false), 2000);
  }, []);

  const handleSelectKey = useCallback(() => {
    openAIStudioKeySelector();
  }, []);

  if (aiDisabled || !apiKey) {
    return (
      <div className="ai-advisor">
        <div className="advisor-header">
          <h2>🤖 AI Financial Advisor</h2>
          <button className="btn-secondary" onClick={onToggleAI}>
            {aiDisabled ? 'Enable AI' : 'Disable AI'}
          </button>
        </div>
        <FallbackInsights
          insights={localInsights}
          reason="disabled"
        />
      </div>
    );
  }

  return (
    <div className="ai-advisor">
      <div className="advisor-header">
        <h2>🤖 AI Financial Advisor</h2>
        <div className="advisor-controls">
          <button
            className="btn-secondary"
            onClick={handleClearCache}
            title="Clear cached AI responses"
          >
            {cacheCleared ? '✓ Cleared' : 'Clear AI Cache'}
          </button>
          <button className="btn-secondary" onClick={onToggleAI}>
            Disable AI
          </button>
        </div>
      </div>

      {error && (
        <div className="ai-error">
          <div className="ai-error-content">
            <span className="error-icon">
              {error.kind === 'quota' ? '🔑' : '⚠️'}
            </span>
            <div>
              <p className="error-message">{error.message}</p>
              {error.kind === 'quota' && hasAIStudioKey() && (
                <button
                  className="btn-primary"
                  onClick={handleSelectKey}
                >
                  Connect / Select API Key
                </button>
              )}
            </div>
          </div>
          <FallbackInsights
            insights={localInsights}
            reason={error.kind === 'quota' ? 'quota' : error.kind === 'network' ? 'network' : 'unknown'}
            onSelectKey={error.kind === 'quota' ? handleSelectKey : undefined}
          />
        </div>
      )}

      {!error && (
        <div className="advisor-body">
          <div className="ask-section">
            <input
              className="question-input"
              type="text"
              placeholder="Ask a financial question, e.g. 'How can I reduce my spending?'"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
              disabled={loading}
            />
            <button
              className="btn-primary"
              onClick={handleAsk}
              disabled={loading || !question.trim()}
            >
              {loading ? '...' : 'Ask'}
            </button>
          </div>

          {response && (
            <div className="ai-response">
              <div className="response-header">
                <span className="response-label">AI Response</span>
                {fromCache && (
                  <span className="cache-badge" title="Loaded from cache">
                    ⚡ Cached
                  </span>
                )}
              </div>
              <p className="response-text">{response}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
