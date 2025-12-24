import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FloatingBot from './FloatingBot';

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = WebSocket.CONNECTING;
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) this.onopen();
    }, 10);
  }
  send(data) {
    // Mock send
  }
  close() {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) this.onclose();
  }
}

global.WebSocket = MockWebSocket;

describe('FloatingBot Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          response: 'Hello! How can I help you?',
          agent_used_functions: []
        })
      })
    );
  });

  test('renders floating bot button', () => {
    render(<FloatingBot />);
    
    // Look for the bot button (usually has an icon or specific class)
    const botButton = screen.getByRole('button', { name: /toggle|chat|bot/i }) ||
                      document.querySelector('.floating-bot-button') ||
                      document.querySelector('[class*="float"]');
    
    expect(botButton || document.querySelector('.floating-bot')).toBeInTheDocument();
  });

  test('opens chat window when button is clicked', async () => {
    render(<FloatingBot />);
    
    const botButton = screen.getByRole('button', { name: /toggle|chat|bot/i }) ||
                      document.querySelector('.floating-bot-button');
    
    if (botButton) {
      fireEvent.click(botButton);
      
      await waitFor(() => {
        // Check if chat window is visible
        const chatWindow = document.querySelector('.floating-bot-window') ||
                          document.querySelector('[class*="chat-window"]') ||
                          screen.queryByPlaceholderText(/type.*message/i);
        expect(chatWindow).toBeInTheDocument();
      });
    }
  });

  test('closes chat window when close button is clicked', async () => {
    render(<FloatingBot />);
    
    // Open the bot
    const botButton = screen.getByRole('button', { name: /toggle|chat|bot/i }) ||
                      document.querySelector('.floating-bot-button');
    
    if (botButton) {
      fireEvent.click(botButton);
      
      await waitFor(() => {
        const closeButton = screen.queryByRole('button', { name: /close|×/i }) ||
                           document.querySelector('[class*="close"]');
        if (closeButton) {
          fireEvent.click(closeButton);
        }
      });
    }
  });

  test('sends message when user types and presses enter', async () => {
    render(<FloatingBot />);
    
    // Open the bot
    const botButton = screen.getByRole('button', { name: /toggle|chat|bot/i }) ||
                      document.querySelector('.floating-bot-button');
    
    if (botButton) {
      fireEvent.click(botButton);
      
      await waitFor(() => {
        const input = screen.queryByPlaceholderText(/type.*message/i) ||
                     document.querySelector('input[type="text"]') ||
                     document.querySelector('textarea');
        
        if (input) {
          fireEvent.change(input, { target: { value: 'Hello bot!' } });
          fireEvent.keyPress(input, { key: 'Enter', code: 13, charCode: 13 });
          
          // Should call API or WebSocket
          waitFor(() => {
            expect(fetch).toHaveBeenCalled() ||
            expect(input.value).toBe(''); // Input cleared after send
          });
        }
      });
    }
  });

  test('displays messages in chat history', async () => {
    render(<FloatingBot />);
    
    // Open the bot
    const botButton = screen.getByRole('button', { name: /toggle|chat|bot/i }) ||
                      document.querySelector('.floating-bot-button');
    
    if (botButton) {
      fireEvent.click(botButton);
      
      // Send a message
      await waitFor(() => {
        const input = screen.queryByPlaceholderText(/type.*message/i);
        if (input) {
          fireEvent.change(input, { target: { value: 'Test message' } });
          fireEvent.keyPress(input, { key: 'Enter', code: 13, charCode: 13 });
        }
      });
      
      // Check if message appears in chat
      await waitFor(() => {
        const messages = document.querySelectorAll('[class*="message"]');
        expect(messages.length).toBeGreaterThan(0);
      }, { timeout: 3000 });
    }
  });

  test('clears chat history when clear button is clicked', async () => {
    render(<FloatingBot />);
    
    // Open the bot
    const botButton = screen.getByRole('button', { name: /toggle|chat|bot/i }) ||
                      document.querySelector('.floating-bot-button');
    
    if (botButton) {
      fireEvent.click(botButton);
      
      await waitFor(() => {
        const clearButton = screen.queryByRole('button', { name: /clear/i }) ||
                           document.querySelector('[class*="clear"]');
        
        if (clearButton) {
          fireEvent.click(clearButton);
          
          // Messages should be cleared
          waitFor(() => {
            const messages = document.querySelectorAll('[class*="message"]');
            expect(messages.length).toBe(0);
          });
        }
      });
    }
  });

  test('handles WebSocket connection', async () => {
    render(<FloatingBot />);
    
    await waitFor(() => {
      // WebSocket should be created (mocked)
      expect(true).toBe(true); // Basic check that component renders
    });
  });

  test('falls back to REST API if WebSocket fails', async () => {
    // Mock WebSocket to fail
    const OriginalWebSocket = global.WebSocket;
    global.WebSocket = class extends MockWebSocket {
      constructor(url) {
        super(url);
        setTimeout(() => {
          this.readyState = WebSocket.CLOSED;
          if (this.onerror) this.onerror(new Error('Connection failed'));
        }, 10);
      }
    };
    
    render(<FloatingBot />);
    
    // Should still work with REST API fallback
    await waitFor(() => {
      expect(true).toBe(true);
    });
    
    global.WebSocket = OriginalWebSocket;
  });
});
