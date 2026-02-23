import { useState, useEffect, useCallback, useRef } from 'react';
import type { BudgetData } from '../types/budget';
import type { AIError } from '../services/aiErrors';
import { getDashboardInsights, hasAIStudioKey, openAIStudioKeySelector } from '../services/geminiService';
import { buildFingerprint } from '../services/aiCache';
import { computeLocalInsights } from '../services/localInsights';
import { FallbackInsights } from './FallbackInsights';

interface Props {
  apiKey: string;
  data: BudgetData;
  aiDisabled: boolean;
  onToggleAI: () => void;
}

export function Dashboard({ apiKey, data, aiDisabled, onToggleAI }: Props) {
  const [insights, setInsights] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AIError | null>(null);
  const [fromCache, setFromCache] = useState(false);
  const localInsights = computeLocalInsights(data);

  // Build a fingerprint of the data to avoid redundant API calls
  const fingerprint = buildFingerprint({
    transactions: data.transactions.slice(-20),
    bills: data.bills,
    goals: data.goals,
    income: data.monthlyIncome,
  });
  const prevFingerprintRef = useRef('');

  const fetchInsights = useCallback(async () => {
    if (!apiKey || aiDisabled) return;
    setLoading(true);
    setError(null);

    const result = await getDashboardInsights(apiKey, data);
    setLoading(false);

    if (result.ok) {
      setInsights(result.value);
      setFromCache(result.fromCache);
    } else {
      setError(result.error);
    }
  }, [apiKey, data, aiDisabled]);

  useEffect(() => {
    if (aiDisabled || !apiKey) return;
    // Only fetch when the data fingerprint changes
    if (prevFingerprintRef.current === fingerprint) return;
    prevFingerprintRef.current = fingerprint;
    void fetchInsights();
  }, [fingerprint, fetchInsights, aiDisabled, apiKey]);

  const netCashFlow =
    localInsights.totalIncomeThisMonth - localInsights.totalSpentThisMonth;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📊 Dashboard</h1>
        <div className="dashboard-controls">
          <button className="btn-secondary" onClick={onToggleAI}>
            {aiDisabled ? '✨ Enable AI' : '🚫 Disable AI'}
          </button>
        </div>
      </div>

      {/* Quick stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Monthly Income</span>
          <span className="stat-value positive">
            ${data.monthlyIncome.toFixed(2)}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Spent This Month</span>
          <span className="stat-value negative">
            ${localInsights.totalSpentThisMonth.toFixed(2)}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Net Cash Flow</span>
          <span className={`stat-value ${netCashFlow >= 0 ? 'positive' : 'negative'}`}>
            {netCashFlow >= 0 ? '+' : ''}${netCashFlow.toFixed(2)}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Savings Rate</span>
          <span className="stat-value">
            {(localInsights.savingsRate * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* AI Insights card */}
      <div className="ai-card">
        <div className="ai-card-header">
          <h2>✨ AI Insights</h2>
          {fromCache && (
            <span className="cache-badge" title="Loaded from cache">
              ⚡ Cached
            </span>
          )}
        </div>

        {(aiDisabled || !apiKey) && (
          <FallbackInsights
            insights={localInsights}
            reason="disabled"
            onSelectKey={hasAIStudioKey() ? openAIStudioKeySelector : undefined}
          />
        )}

        {!aiDisabled && apiKey && loading && (
          <div className="ai-loading">
            <span className="loading-spinner" />
            <span>Generating insights…</span>
          </div>
        )}

        {!aiDisabled && apiKey && error && (
          <FallbackInsights
            insights={localInsights}
            reason={
              error.kind === 'quota'
                ? 'quota'
                : error.kind === 'network'
                ? 'network'
                : 'unknown'
            }
            onSelectKey={
              error.kind === 'quota' && hasAIStudioKey()
                ? openAIStudioKeySelector
                : undefined
            }
          />
        )}

        {!aiDisabled && apiKey && !loading && !error && insights && (
          <div className="ai-insights-content">
            <p>{insights}</p>
            <button
              className="btn-text"
              onClick={() => void fetchInsights()}
            >
              ↻ Refresh
            </button>
          </div>
        )}
      </div>

      {/* Bills section */}
      {localInsights.billsDueSoon.length > 0 && (
        <div className="bills-card">
          <h2>📅 Bills Due Soon</h2>
          <ul>
            {localInsights.billsDueSoon.map((b) => (
              <li key={b.id} className="bill-item">
                <span className="bill-name">{b.name}</span>
                <span className="bill-amount">${b.amount.toFixed(2)}</span>
                <span className="bill-date">
                  {new Date(b.dueDate).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
