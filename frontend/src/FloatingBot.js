import React, { useState, useEffect, useRef } from 'react';
import './FloatingBot.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function FloatingBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
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
  }, []);

  // WebSocket connection for real-time chat
  useEffect(() => {
    if (isOpen && connected && !wsRef.current) {
      const wsUrl = API_URL.replace('http://', 'ws://').replace('https://', 'wss://');
      const ws = new WebSocket(`${wsUrl}/ws/chat`);

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'response') {
          const assistantMessage = {
            role: 'assistant',
            content: data.response,
            timestamp: new Date().toISOString(),
            function_calls: data.function_calls || []
          };
          setMessages(prev => [...prev, assistantMessage]);
          setLoading(false);
        } else if (data.type === 'error') {
          const errorMessage = {
            role: 'error',
            content: data.error || 'An error occurred',
            timestamp: new Date().toISOString()
          };
          setMessages(prev => [...prev, errorMessage]);
          setLoading(false);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setLoading(false);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        wsRef.current = null;
      };

      wsRef.current = ws;
    }

    return () => {
      if (wsRef.current && !isOpen) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [isOpen, connected]);

  const sendMessage = (e) => {
    e.preventDefault();
    
    if (!input.trim() || loading || !connected) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Send via WebSocket if available
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        message: input,
        user_id: 'floating_bot_user'
      }));
    } else {
      // Fallback to REST API
      fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          user_id: 'floating_bot_user'
        })
      })
      .then(res => res.json())
      .then(data => {
        const assistantMessage = {
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toISOString(),
          function_calls: data.function_calls || []
        };
        setMessages(prev => [...prev, assistantMessage]);
      })
      .catch(error => {
        console.error('Error sending message:', error);
        const errorMessage = {
          role: 'error',
          content: `Error: ${error.message}`,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, errorMessage]);
      })
      .finally(() => {
        setLoading(false);
      });
    }
  };

  const toggleBot = () => {
    setIsOpen(!isOpen);
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <>
      {/* Floating Button */}
      <button 
        className={`floating-bot-button ${isOpen ? 'open' : ''}`}
        onClick={toggleBot}
        title="Chat with AI Assistant"
      >
        {isOpen ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="floating-bot-window">
          <div className="floating-bot-header">
            <div className="header-content">
              <div className="bot-avatar">🤖</div>
              <div className="header-info">
                <h3>AI Assistant</h3>
                <span className={`status ${connected ? 'online' : 'offline'}`}>
                  {connected ? '● Online' : '○ Offline'}
                </span>
              </div>
            </div>
            <div className="header-actions">
              <button 
                className="clear-button" 
                onClick={clearChat}
                title="Clear chat"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
              <button 
                className="close-button" 
                onClick={toggleBot}
                title="Close"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>

          <div className="floating-bot-messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                <div className="bot-avatar-large">🤖</div>
                <h4>Hello! I'm your AI Assistant</h4>
                <p>Ask me anything or request actions like sending Slack messages!</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : msg.role === 'assistant' ? '🤖' : '⚠️'}
                </div>
                <div className="message-content">
                  <div className="message-text">{msg.content}</div>
                  {msg.function_calls && msg.function_calls.length > 0 && (
                    <div className="function-calls">
                      {msg.function_calls.map((fc, i) => (
                        <div key={i} className="function-call">
                          <span className="function-name">⚡ {fc.function}</span>
                          {fc.result && fc.result.success && <span className="success">✓</span>}
                          {fc.result && !fc.result.success && <span className="error">✗</span>}
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
              <div className="message assistant loading">
                <div className="message-avatar">🤖</div>
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

          <form className="floating-bot-input" onSubmit={sendMessage}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={connected ? "Type your message..." : "Connecting..."}
              disabled={!connected || loading}
            />
            <button 
              type="submit" 
              disabled={!connected || loading || !input.trim()}
              className="send-button"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </form>
        </div>
      )}
    </>
  );
}

export default FloatingBot;
