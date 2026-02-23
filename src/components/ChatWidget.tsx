import { useState, useCallback } from 'react';
import type { BudgetData } from '../types/budget';
import type { AIError } from '../services/aiErrors';
import { getAdvisorResponse, hasAIStudioKey, openAIStudioKeySelector } from '../services/geminiService';
import { FallbackInsights } from './FallbackInsights';
import { computeLocalInsights } from '../services/localInsights';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'error';
  text: string;
  fromCache?: boolean;
}

interface Props {
  apiKey: string;
  data: BudgetData;
  aiDisabled: boolean;
}

export function ChatWidget({ apiKey, data, aiDisabled }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastError, setLastError] = useState<AIError | null>(null);
  const [open, setOpen] = useState(false);

  const localInsights = computeLocalInsights(data);

  const addMessage = useCallback((msg: Omit<Message, 'id'>) => {
    setMessages((prev) => [
      ...prev,
      { ...msg, id: `${Date.now()}-${Math.random()}` },
    ]);
  }, []);

  const handleSend = useCallback(async () => {
    if (!input.trim() || loading) return;
    const text = input.trim();
    setInput('');
    addMessage({ role: 'user', text });

    if (aiDisabled || !apiKey) {
      addMessage({
        role: 'error',
        text: 'AI features are currently disabled. Enable them in settings to chat.',
      });
      return;
    }

    setLoading(true);
    setLastError(null);
    const result = await getAdvisorResponse(apiKey, text, data);
    setLoading(false);

    if (result.ok) {
      addMessage({
        role: 'assistant',
        text: result.value,
        fromCache: result.fromCache,
      });
    } else {
      setLastError(result.error);
      addMessage({
        role: 'error',
        text: result.error.message,
      });
    }
  }, [input, loading, apiKey, data, aiDisabled, addMessage]);

  if (!open) {
    return (
      <button
        className="chat-fab"
        onClick={() => setOpen(true)}
        aria-label="Open AI chat"
      >
        💬
      </button>
    );
  }

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <span>💬 AI Assistant</span>
        <button className="btn-icon" onClick={() => setOpen(false)} aria-label="Close chat">
          ✕
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="chat-empty">Ask a question about your finances…</p>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`chat-message chat-${m.role}`}>
            <span className="message-text">{m.text}</span>
            {m.fromCache && (
              <span className="cache-badge" title="From cache">⚡</span>
            )}
          </div>
        ))}
        {loading && (
          <div className="chat-message chat-assistant">
            <span className="loading-dots">…</span>
          </div>
        )}
      </div>

      {lastError?.kind === 'quota' && (
        <div className="chat-error-bar">
          <span>Quota exceeded.</span>
          {hasAIStudioKey() && (
            <button
              className="btn-link"
              onClick={openAIStudioKeySelector}
            >
              Select API Key
            </button>
          )}
        </div>
      )}

      {(aiDisabled || !apiKey) && (
        <div className="chat-fallback">
          <FallbackInsights
            insights={localInsights}
            reason="disabled"
          />
        </div>
      )}

      <div className="chat-input-row">
        <input
          className="chat-input"
          type="text"
          placeholder="Type a question…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && void handleSend()}
          disabled={loading}
        />
        <button
          className="btn-primary"
          onClick={() => void handleSend()}
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
