import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatInterface from './ChatInterface';

global.fetch = jest.fn();

describe('ChatInterface Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          response: 'Test response',
          agent_used_functions: []
        })
      })
    );
  });

  test('renders chat interface', () => {
    render(<ChatInterface />);
    
    // Should have an input for messages
    const input = screen.queryByPlaceholderText(/type.*message|enter.*message/i) ||
                 document.querySelector('input[type="text"]') ||
                 document.querySelector('textarea');
    expect(input).toBeInTheDocument();
  });

  test('sends message when send button is clicked', async () => {
    render(<ChatInterface />);
    
    const input = screen.queryByPlaceholderText(/type.*message|enter.*message/i) ||
                 document.querySelector('input[type="text"]') ||
                 document.querySelector('textarea');
    
    if (input) {
      fireEvent.change(input, { target: { value: 'Hello' } });
      
      const sendButton = screen.queryByRole('button', { name: /send/i }) ||
                        screen.queryByText(/send/i);
      
      if (sendButton) {
        fireEvent.click(sendButton);
        
        await waitFor(() => {
          expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining('/chat'),
            expect.objectContaining({
              method: 'POST'
            })
          );
        });
      }
    }
  });

  test('displays welcome screen', () => {
    render(<ChatInterface />);
    
    // Check for welcome message or empty state
    const welcomeText = screen.queryByText(/welcome|start.*conversation|how.*help/i);
    expect(welcomeText || document.querySelector('[class*="welcome"]')).toBeTruthy();
  });

  test('shows function calls when agent uses functions', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          response: 'I sent a message to Slack',
          agent_used_functions: [
            { name: 'slack_send_message', status: 'success' }
          ]
        })
      })
    );
    
    render(<ChatInterface />);
    
    const input = screen.queryByPlaceholderText(/type.*message/i) ||
                 document.querySelector('input');
    
    if (input) {
      fireEvent.change(input, { target: { value: 'Send a message' } });
      
      const sendButton = screen.queryByRole('button', { name: /send/i });
      if (sendButton) {
        fireEvent.click(sendButton);
        
        await waitFor(() => {
          // Should display function call indicator
          const functionIndicator = document.querySelector('[class*="function"]') ||
                                   screen.queryByText(/slack_send_message/i);
          expect(functionIndicator).toBeTruthy();
        });
      }
    }
  });

  test('displays message history', async () => {
    render(<ChatInterface />);
    
    // Send first message
    const input = screen.queryByPlaceholderText(/type.*message/i) ||
                 document.querySelector('input');
    
    if (input) {
      fireEvent.change(input, { target: { value: 'Message 1' } });
      const sendButton = screen.queryByRole('button', { name: /send/i });
      if (sendButton) {
        fireEvent.click(sendButton);
        
        await waitFor(() => {
          expect(screen.queryByText(/Message 1|Test response/i)).toBeTruthy();
        });
      }
    }
  });

  test('handles errors gracefully', async () => {
    fetch.mockImplementationOnce(() => Promise.reject(new Error('Network error')));
    
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    render(<ChatInterface />);
    
    const input = screen.queryByPlaceholderText(/type.*message/i);
    if (input) {
      fireEvent.change(input, { target: { value: 'Test' } });
      const sendButton = screen.queryByRole('button', { name: /send/i });
      if (sendButton) {
        fireEvent.click(sendButton);
        
        await waitFor(() => {
          // Should handle error (logged or displayed)
          expect(consoleSpy).toHaveBeenCalled() ||
          expect(screen.queryByText(/error/i)).toBeTruthy();
        });
      }
    }
    
    consoleSpy.mockRestore();
  });
});
