import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Dashboard from './Dashboard';

// Mock fetch for API calls
global.fetch = jest.fn();

describe('Dashboard Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    // Mock successful API responses
    fetch.mockImplementation((url) => {
      if (url.includes('/health')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ status: 'healthy', agent_ready: true })
        });
      }
      if (url.includes('/integrations')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            integrations: [
              { name: 'slack', health: 'healthy', functions: 3 },
              { name: 'gmail', health: 'not configured', functions: 2 },
              { name: 'notion', health: 'not configured', functions: 2 }
            ]
          })
        });
      }
      if (url.includes('/functions')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ functions: [] })
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      });
    });
  });

  test('renders dashboard with sidebar', async () => {
    render(<Dashboard />);
    
    // Check for logo/branding
    expect(screen.getByText(/RAG7/i)).toBeInTheDocument();
    
    // Check for navigation items
    await waitFor(() => {
      expect(screen.getByText(/Chat/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/Integrations/i)).toBeInTheDocument();
    expect(screen.getByText(/Analytics/i)).toBeInTheDocument();
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  test('displays status indicator', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      const statusElements = screen.queryAllByText(/online|offline/i);
      expect(statusElements.length).toBeGreaterThan(0);
    });
  });

  test('switches between views when clicking navigation', async () => {
    render(<Dashboard />);
    
    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByText(/Chat/i)).toBeInTheDocument();
    });
    
    // Click on Integrations
    const integrationsNav = screen.getByText(/Integrations/i);
    fireEvent.click(integrationsNav);
    
    // Should show integrations view
    await waitFor(() => {
      const integrationsCards = screen.queryAllByText(/Slack|Gmail|Notion/i);
      expect(integrationsCards.length).toBeGreaterThan(0);
    });
  });

  test('displays analytics stats', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Analytics/i)).toBeInTheDocument();
    });
    
    // Click on Analytics
    const analyticsNav = screen.getByText(/Analytics/i);
    fireEvent.click(analyticsNav);
    
    // Should show stat cards
    await waitFor(() => {
      expect(screen.getByText(/Messages|Sessions|Functions|Success Rate/i)).toBeInTheDocument();
    });
  });

  test('displays settings view', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Settings/i)).toBeInTheDocument();
    });
    
    // Click on Settings
    const settingsNav = screen.getByText(/Settings/i);
    fireEvent.click(settingsNav);
    
    // Should show settings content
    await waitFor(() => {
      expect(screen.getByText(/API Configuration|Documentation/i)).toBeInTheDocument();
    });
  });

  test('fetches integration data on mount', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/integrations'));
    });
  });

  test('handles API errors gracefully', async () => {
    fetch.mockImplementationOnce(() => Promise.reject(new Error('API Error')));
    
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });
    
    consoleSpy.mockRestore();
  });
});
