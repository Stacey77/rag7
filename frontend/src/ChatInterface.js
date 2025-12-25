import React, { useState, useEffect, useRef } from 'react';
import './ChatInterface.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function ChatInterface({ connected, integrations }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
          user_id: 'dashboard_user'
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
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <div className="welcome-icon">🤖</div>
            <h2>Welcome to RAG7 AI Assistant!</h2>
            <p>I'm ready to help you with:</p>
            <div className="capabilities-grid">
              {integrations.map(integ => (
                <div key={integ.name} className={`capability ${integ.healthy ? 'active' : 'inactive'}`}>
                  <span className="capability-icon">
                    {integ.name === 'slack' && '📱'}
                    {integ.name === 'gmail' && '📧'}
                    {integ.name === 'notion' && '📝'}
                  </span>
                  <span className="capability-name">{integ.name}</span>
                  <span className="capability-status">
                    {integ.healthy ? '✓' : '○'}
                  </span>
                </div>
              ))}
            </div>
            <p className="welcome-hint">
              Try asking: "Send a message to #general" or "What can you do?"
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' && '👤'}
              {msg.role === 'assistant' && '🤖'}
              {msg.role === 'error' && '⚠️'}
            </div>
            <div className="message-bubble">
              <div className="message-content">{msg.content}</div>
              {msg.function_calls && msg.function_calls.length > 0 && (
                <div className="message-functions">
                  {msg.function_calls.map((fc, i) => (
                    <div key={i} className="function-badge">
                      <span className="function-icon">⚡</span>
                      <span className="function-text">{fc.function}</span>
                      {fc.result && fc.result.success && <span className="function-status success">✓</span>}
                      {fc.result && !fc.result.success && <span className="function-status error">✗</span>}
                    </div>
                  ))}
                </div>
              )}
              <div className="message-time">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-bubble">
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

      <form className="chat-input-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={connected ? "Type your message..." : "Connecting..."}
          disabled={!connected || loading}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={!connected || loading || !input.trim()}
          className="chat-send-button"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>
    </div>
  );
}

export default ChatInterface;
