# Multi-Agent Agentic Infrastructure Control Platform - Dashboard

A comprehensive HTML dashboard for monitoring and managing the Multi-Agent Agentic Infrastructure Control Platform.

## 🎯 Overview

This interactive dashboard provides real-time monitoring, control, and visualization capabilities for a multi-agent infrastructure management system. Built with pure HTML5, CSS3, and JavaScript - no build process required.

## ✨ Features

### Main Dashboard (`index.html`)
- **Platform Overview**: Real-time status of the entire platform
- **Agent Status Panel**: Monitor all 4 agents (Policy, Intent, Deployment, Compliance)
- **Blast Radius Visualization**: Interactive charts showing deployment impact
- **Multi-Region Map**: Global infrastructure health visualization
- **Policy Enforcement**: Active policies and violation tracking
- **Cost Optimization**: Bandwidth, compute, storage, and cost metrics
- **Activity Feed**: Real-time updates on system activities

### Policy Management (`policies.html`)
- View all active policies with OPA rules
- Policy statistics and enforcement metrics
- Search and filter policies
- Policy simulation capabilities
- Violation tracking

### Script Library (`scripts.html`)
- Browse 150+ automation scripts
- Category-based filtering (Automation, Security, Monitoring, etc.)
- Multi-cloud support (AWS, Azure, GCP)
- Script ratings and download counts
- Adapter marketplace

### Compliance Reports (`compliance.html`)
- Overall compliance score dashboard
- Framework compliance (SOC 2, HIPAA, PCI DSS)
- Audit trail viewer with search
- Compliance markers for key resources
- Trend analysis charts
- Export to PDF/CSV

### Settings (`settings.html`)
- General platform configuration
- Agent-specific settings
- API endpoint configuration
- Cloud provider credentials (AWS, Azure, GCP)
- Notification preferences (Email, Slack, PagerDuty)

## 🎨 Design

### Color Scheme
- **Primary Purple**: `#5B4B8A`, `#7B68A6`
- **Dark Background**: `#2E2547`
- **Accent Orange**: `#FF6B35`
- **Success Green**: `#4CAF50`
- **Status Colors**: Warning (`#FFA726`), Error (`#EF5350`), Info (`#42A5F5`)

### Visual Elements
- Lion logo with purple/orange gradient
- Modern card-based layout
- Responsive grid system
- Smooth animations and transitions
- Interactive charts via Chart.js

## 🚀 Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Web server (optional, for best experience)

### Installation

1. **Clone or download the repository**
   ```bash
   cd dashboard
   ```

2. **Open in browser**
   - **Option 1**: Open `index.html` directly in your browser
   - **Option 2**: Use a local web server (recommended):
     ```bash
     # Python 3
     python -m http.server 8000
     
     # Node.js
     npx serve
     ```
   - Navigate to `http://localhost:8000`

### No Build Process Required
The dashboard uses CDN-hosted libraries:
- Chart.js (v4.4.0) for data visualization
- Font Awesome (v6.4.0) for icons

## 📁 File Structure

```
/dashboard
├── index.html                 # Main dashboard
├── policies.html             # Policy management
├── scripts.html              # Script library
├── compliance.html           # Compliance reports
├── settings.html             # Settings page
├── css/
│   ├── main.css             # Main stylesheet with purple theme
│   ├── dashboard.css        # Dashboard-specific styles
│   └── responsive.css       # Mobile responsive styles
├── js/
│   ├── dashboard.js         # Main dashboard logic
│   ├── agents.js            # Agent management
│   ├── charts.js            # Chart configurations
│   ├── api.js               # API integration layer
│   └── websocket.js         # Real-time updates simulation
├── assets/
│   ├── logo.svg             # Lion logo
│   └── icons/               # (using Font Awesome)
├── data/
│   └── mock-data.json       # Mock data for demonstration
└── README.md                # This file
```

## 🔌 API Integration

### Mock Mode (Default)
The dashboard runs in mock mode by default, using `data/mock-data.json` for demonstration.

### Connecting to Real API

1. **Update API Configuration** in `js/api.js`:
   ```javascript
   constructor() {
       this.baseUrl = 'https://your-api-endpoint.com/api';
       this.mockMode = false; // Disable mock mode
   }
   ```

2. **Configure WebSocket** in `js/websocket.js`:
   ```javascript
   connect(url = 'wss://your-websocket-endpoint.com') {
       this.simulationMode = false; // Disable simulation
       // ... rest of the code
   }
   ```

### API Endpoints Expected

```
GET  /api/platform/status      # Platform status
GET  /api/agents               # All agents
GET  /api/agents/:id           # Specific agent
POST /api/agents/:id/start     # Start agent
POST /api/agents/:id/stop      # Stop agent
GET  /api/activities           # Activity feed
GET  /api/policies             # All policies
GET  /api/metrics              # Metrics data
GET  /api/regions              # Region data
GET  /api/blast-radius         # Blast radius data
```

### WebSocket Events

```javascript
// Agent status update
{
  type: 'agent_status',
  payload: {
    agentId: 'policy',
    status: 'active',
    timestamp: '2024-02-15T07:30:00Z'
  }
}

// New activity
{
  type: 'activity',
  payload: {
    type: 'policy',
    title: 'Policy Check Completed',
    description: 'All policies validated',
    time: 'just now'
  }
}

// Metric update
{
  type: 'metric_update',
  payload: {
    type: 'system_health',
    value: 98,
    timestamp: '2024-02-15T07:30:00Z'
  }
}
```

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- **Desktop**: Full feature set with side navigation
- **Tablet**: Optimized grid layouts
- **Mobile**: Collapsed navigation, stacked layouts

Breakpoints:
- Desktop: > 1024px
- Tablet: 768px - 1024px
- Mobile: < 768px

## 🔄 Real-Time Updates

### Auto-Refresh
- Dashboard data refreshes every 30 seconds
- Agent metrics update every 5 seconds
- WebSocket provides instant updates (when connected)

### Manual Refresh
Click the refresh button in the header to manually update all data.

## 🎯 Features in Detail

### Agent Management
- Start/stop individual agents
- View real-time metrics
- Monitor processing queues
- Track success rates

### Policy Enforcement
- Search policies
- View OPA rules
- Simulate policy execution
- Track violations

### Blast Radius Analysis
- Visual impact prediction
- Affected resources count
- Risk level indicators
- Approval workflow

### Cost Optimization
- Bandwidth savings tracking
- Compute efficiency metrics
- Storage utilization
- Cost trend analysis

## 🔧 Customization

### Changing Colors
Edit `css/main.css`:
```css
:root {
    --primary-purple: #5B4B8A;
    --accent-orange: #FF6B35;
    /* ... modify as needed */
}
```

### Adding New Metrics
1. Add chart configuration in `js/charts.js`
2. Update mock data in `data/mock-data.json`
3. Add chart canvas in HTML
4. Initialize in dashboard

### Custom Agents
Add new agent cards to `index.html` and update `data/mock-data.json` with agent configuration.

## 🐛 Troubleshooting

### Charts Not Displaying
- Ensure Chart.js CDN is accessible
- Check browser console for errors
- Verify canvas elements have valid IDs

### WebSocket Not Connecting
- Simulation mode is enabled by default
- Check `simulationMode` in `js/websocket.js`
- Verify WebSocket URL if using real connection

### Mock Data Not Loading
- Ensure `data/mock-data.json` exists
- Check file path is correct
- Verify JSON is valid

## 📊 Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Android

## 🔒 Security Notes

- Never commit real API keys or credentials
- Use environment variables for sensitive data
- Implement proper authentication in production
- Enable HTTPS for all API connections
- Sanitize user inputs

## 📝 License

This dashboard is part of the Multi-Agent Infrastructure Control Platform project.

## 🤝 Contributing

To contribute:
1. Follow existing code style
2. Test on multiple browsers
3. Ensure responsive design works
4. Update documentation as needed

## 📧 Support

For issues or questions, please refer to the main project repository.

## 🎉 Acknowledgments

- Chart.js for beautiful data visualization
- Font Awesome for comprehensive icon library
- Modern web standards for making this possible without a build process
