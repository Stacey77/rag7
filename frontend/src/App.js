import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [integrations, setIntegrations] = useState([]);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check API health
    fetch(`${API_URL}/health`)
      .then(res => res.json())
      .then(data => {
        setConnected(data.agent_ready);
      })
      .catch(err => {
        console.error('Health check failed:', err);
        setConnected(false);
      });

    // Load integrations
    fetch(`${API_URL}/integrations`)
      .then(res => res.json())
      .then(data => {
        setIntegrations(data);
      })
      .catch(err => {
        console.error('Failed to load integrations:', err);
      });

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          user_id: 'web_user'
        })
      });

      const data = await response.json();

      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        function_calls: data.function_calls || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        role: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 RAG7 AI Agent Platform</h1>
        <div className="status-indicators">
          <span className={`status ${connected ? 'connected' : 'disconnected'}`}>
            {connected ? '● Connected' : '○ Disconnected'}
          </span>
          {integrations.length > 0 && (
            <span className="integrations">
              {integrations.filter(i => i.healthy).length}/{integrations.length} Integrations Active
            </span>
          )}
        </div>
      </header>

      <main className="chat-container">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Welcome to RAG7 AI Agent Platform!</h2>
              <p>I'm an AI assistant with access to:</p>
              <ul>
                {integrations.map(integ => (
                  <li key={integ.name}>
                    <strong>{integ.name}</strong>: {integ.functions_count} functions
                    {integ.healthy ? ' ✓' : ' (not configured)'}
                  </li>
                ))}
              </ul>
              <p>Ask me anything or request actions like sending Slack messages!</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-header">
                <span className="role">{msg.role === 'user' ? '👤 You' : msg.role === 'assistant' ? '🤖 Assistant' : '⚠️ Error'}</span>
                <span className="timestamp">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="message-content">
                {msg.content}
              </div>
              {msg.function_calls && msg.function_calls.length > 0 && (
                <div className="function-calls">
                  <strong>Functions executed:</strong>
                  <ul>
                    {msg.function_calls.map((fc, i) => (
                      <li key={i}>
                        {fc.function}
                        {fc.result && fc.result.success && ' ✓'}
                        {fc.result && !fc.result.success && ` ✗ (${fc.result.error})`}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="message assistant loading">
              <div className="message-header">
                <span className="role">🤖 Assistant</span>
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form className="input-form" onSubmit={sendMessage}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={connected ? "Type your message..." : "Waiting for connection..."}
            disabled={!connected || loading}
            className="message-input"
          />
          <button 
            type="submit" 
            disabled={!connected || loading || !input.trim()}
            className="send-button"
          >
            {loading ? '...' : 'Send'}
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;
