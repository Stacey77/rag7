# Epic Platform - Web Client

Modern React + TypeScript web client with cyberpunk-themed UI for the Epic Platform.

## Features

- **Cyberpunk Theme**: Futuristic design with Orbitron font and neon accents
- **Agent Builder**: Create and manage LangFlow AI agents
- **Dashboard**: System overview and quick stats
- **Playground**: Interactive AI conversation interface
- **Datasets**: Manage and upload training data
- **Voice Interface**: Speech-to-text and text-to-speech (STT/TTS) support
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **CSS3**: Custom cyberpunk styling with animations

## Development

### Prerequisites

- Node.js 18+ and npm
- Backend API running on port 8000

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

The dev server runs on http://localhost:5173 by default.

### Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Docker

### Build and Run

```bash
# Build the image
docker build -t epic-web-client .

# Run the container
docker run -p 3000:80 epic-web-client
```

### Via Docker Compose

From the root directory:

```bash
docker-compose up frontend
```

## Project Structure

```
web-client/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Main app component with routing
│   ├── styles.css            # Global cyberpunk theme
│   ├── components/           # Reusable components
│   │   ├── Sidebar.tsx       # Navigation sidebar
│   │   ├── AIBrain.tsx       # Animated AI brain indicator
│   │   ├── SectionAgent.tsx  # Agent card component
│   │   └── Conversation.tsx  # Chat interface with STT/TTS
│   └── pages/                # Application pages
│       ├── Dashboard.tsx     # Main dashboard
│       ├── Playground.tsx    # AI testing playground
│       ├── Datasets.tsx      # Dataset management
│       └── AgentBuilder.tsx  # LangFlow agent builder
├── index.html                # HTML template
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
├── package.json              # Dependencies and scripts
├── Dockerfile                # Multi-stage Docker build
└── nginx.conf                # Nginx configuration
```

## Pages

### Dashboard (`/`)
- System status overview
- Quick statistics
- Available agents grid
- Recent activity

### Agent Builder (`/agent-builder`)
- List saved flows from backend
- Upload and save LangFlow JSON
- Load existing flows
- Execute flows with user input
- View execution results

**Backend Integration:**
- `GET /list_flows/` - Fetch all flows
- `GET /get_flow/{name}` - Load specific flow
- `POST /save_flow/` - Save new flow
- `POST /run_flow/` - Execute flow

### Playground (`/playground`)
- Interactive chat interface
- Voice input (STT)
- Voice output (TTS)
- Agent configuration
- Session management

### Datasets (`/datasets`)
- Upload datasets
- View dataset statistics
- Manage training data
- Search and filter

## Styling

The application uses a cyberpunk theme with:

- **Font**: Orbitron (Google Fonts)
- **Colors**:
  - Neon Pink: #ff006e
  - Neon Blue: #00d9ff
  - Neon Purple: #8b5cf6
  - Neon Green: #00ff88
  - Dark Background: #0a0a0f
  - Dark Card: #1a1a2e

### Custom CSS Classes

- `.card` - Card container with hover effects
- `.btn-primary` - Primary action button
- `.btn-secondary` - Secondary action button
- `.grid-2`, `.grid-3` - Responsive grid layouts
- `.glow` - Text glow effect
- `.status-badge` - Status indicator

## API Integration

The frontend connects to the FastAPI backend using the `VITE_API_URL` environment variable.

### Example API Call

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Fetch flows
const response = await fetch(`${API_URL}/list_flows/`)
const data = await response.json()

// Save flow
await fetch(`${API_URL}/save_flow/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ flow_name: 'test', flow_data: {...} })
})
```

## Building for Production

### Using npm

```bash
npm run build
# Output: dist/
```

### Using Docker

The Dockerfile uses a multi-stage build:
1. Build stage: Compiles TypeScript and bundles assets
2. Production stage: Serves via Nginx

```bash
docker build -t epic-web-client .
docker run -p 3000:80 epic-web-client
```

## Deployment

### Nginx Configuration

The included `nginx.conf`:
- Serves static files
- Enables gzip compression
- Adds security headers
- Handles client-side routing

### Environment-Specific Builds

For different environments, create `.env.production`:

```
VITE_API_URL=https://api.production.com
```

Then build:

```bash
npm run build
```

## Troubleshooting

### API Connection Issues

If the frontend can't connect to the backend:
1. Check `VITE_API_URL` in `.env`
2. Ensure backend CORS allows your frontend origin
3. Check backend is running on expected port
4. Check browser console for CORS errors

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf dist .vite
npm run build
```

### Docker Issues

```bash
# Rebuild without cache
docker build --no-cache -t epic-web-client .

# Check logs
docker logs <container-id>
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Accessibility

- Semantic HTML
- Keyboard navigation
- Screen reader support
- ARIA labels

## Performance

- Code splitting with Vite
- Lazy loading of routes
- Optimized images
- Gzip compression
- Browser caching

## Security

⚠️ **Production Checklist:**
- Enable Content Security Policy (CSP)
- Use HTTPS
- Validate all user inputs
- Sanitize displayed data
- Keep dependencies updated

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Resources

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Vite Documentation](https://vitejs.dev/)
- [React Router Documentation](https://reactrouter.com/)
