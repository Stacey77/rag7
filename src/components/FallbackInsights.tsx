import type { LocalInsights } from '../types/budget';

interface Props {
  insights: LocalInsights;
  reason: 'quota' | 'network' | 'disabled' | 'unknown';
  onSelectKey?: () => void;
}

const reasonMessages: Record<Props['reason'], string> = {
  quota: 'AI insights are temporarily unavailable because the API quota has been exceeded.',
  network: 'AI insights are unavailable due to a network error.',
  disabled: 'AI features are currently disabled.',
  unknown: 'AI insights are temporarily unavailable.',
};

const reasonSuggestions: Record<Props['reason'], string> = {
  quota: 'Connect a different API key to restore AI features, or wait until your quota resets.',
  network: 'Check your internet connection and try again later.',
  disabled: 'Enable AI features in settings to get personalized insights.',
  unknown: 'Please try again later.',
};

export function FallbackInsights({ insights, reason, onSelectKey }: Props) {
  return (
    <div className="fallback-insights">
      <div className="fallback-header">
        <span className="fallback-icon">⚠️</span>
        <div>
          <p className="fallback-reason">{reasonMessages[reason]}</p>
          <p className="fallback-suggestion">{reasonSuggestions[reason]}</p>
        </div>
      </div>

      {reason === 'quota' && onSelectKey && (
        <button className="btn-primary fallback-cta" onClick={onSelectKey}>
          Connect / Select API Key
        </button>
      )}

      <div className="local-insights">
        <h3>📊 Local Insights (Last 30 Days)</h3>

        <div className="insight-row">
          <span className="insight-label">💰 Monthly cash flow</span>
          <span
            className={`insight-value ${
              insights.totalIncomeThisMonth - insights.totalSpentThisMonth >= 0
                ? 'positive'
                : 'negative'
            }`}
          >
            {insights.totalIncomeThisMonth - insights.totalSpentThisMonth >= 0
              ? '+'
              : ''}
            $
            {(
              insights.totalIncomeThisMonth - insights.totalSpentThisMonth
            ).toFixed(2)}
          </span>
        </div>

        <div className="insight-row">
          <span className="insight-label">📈 Savings rate</span>
          <span className="insight-value">
            {(insights.savingsRate * 100).toFixed(1)}%
          </span>
        </div>

        {insights.topCategories.length > 0 && (
          <div className="insight-section">
            <h4>🏷️ Top spending categories</h4>
            <ul className="category-list">
              {insights.topCategories.map((c) => (
                <li key={c.category}>
                  <span className="cat-name">{c.category}</span>
                  <span className="cat-amount">${c.total.toFixed(2)}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {insights.largestExpense && (
          <div className="insight-row">
            <span className="insight-label">📌 Largest expense</span>
            <span className="insight-value">
              {insights.largestExpense.description} ($
              {Math.abs(insights.largestExpense.amount).toFixed(2)})
            </span>
          </div>
        )}

        {insights.billsDueSoon.length > 0 && (
          <div className="insight-section">
            <h4>📅 Bills due within 7 days</h4>
            <ul className="bills-list">
              {insights.billsDueSoon.map((b) => (
                <li key={b.id}>
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
    </div>
  );
}
