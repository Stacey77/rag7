# Ragamuffin Web Client

## Overview
Modern React + TypeScript web interface for the Ragamuffin AI orchestration platform. Features a cyberpunk-inspired design with the Orbitron font.

## Tech Stack
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls

## Features
- **Dashboard**: System overview and agent status
- **Playground**: Interactive AI conversation interface with STT/TTS
- **Datasets**: Data management and storage
- **Agent Builder**: Flow management - upload, list, and execute LangFlow JSON files

## Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup
```bash
cd web-client
npm install
```

### Run Development Server
```bash
npm run dev
```
Access at http://localhost:5173

### Build for Production
```bash
npm run build
```
Output in `dist/` directory

### Preview Production Build
```bash
npm run preview
```

## Docker

### Build Image
```bash
docker build -t ragamuffin-frontend .
```

### Run Container
```bash
docker run -p 8080:80 ragamuffin-frontend
```

## Environment Variables

Create a `.env` file:
```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
web-client/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Root component with routing
│   ├── styles.css            # Global styles (Orbitron font, cyberpunk theme)
│   ├── components/
│   │   ├── Sidebar.tsx       # Navigation sidebar
│   │   ├── Sidebar.css       # Sidebar styles
│   │   ├── AIBrain.tsx       # Animated AI status indicator
│   │   ├── SectionAgent.tsx  # Agent status card
│   │   └── Conversation.tsx  # Chat interface with STT/TTS
│   └── pages/
│       ├── Dashboard.tsx     # Main dashboard
│       ├── Playground.tsx    # AI interaction playground
│       ├── Datasets.tsx      # Dataset management
│       └── AgentBuilder.tsx  # Flow builder interface
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── Dockerfile
└── .env
```

## Pages

### Dashboard (`/`)
- System status overview
- AI brain visualization
- Active agents display
- Quick statistics

### Playground (`/playground`)
- Interactive conversation interface
- Real-time AI responses
- Configuration panel
- Recent interactions log

### Datasets (`/datasets`)
- Dataset listing and search
- Upload/download functionality
- Storage usage metrics
- Status indicators

### Agent Builder (`/agent-builder`)
- Upload LangFlow JSON files
- List saved flows
- Execute flows with input
- View execution results
- Integration with backend API

## API Integration

The Agent Builder page integrates with the backend API:

```typescript
// List flows
GET ${API_URL}/list_flows/

// Save flow
POST ${API_URL}/save_flow/
FormData: { flow_file: File }

// Get flow
GET ${API_URL}/get_flow/{flow_name}

// Run flow
POST ${API_URL}/run_flow/
FormData: { flow_file: File, user_input: string }
```

## Styling

### Theme Colors
- **Primary BG**: `#0a0e27`
- **Secondary BG**: `#1a1e3e`
- **Accent Cyan**: `#00fff9`
- **Accent Purple**: `#b026ff`
- **Accent Pink**: `#ff006e`

### Typography
- **Font**: Orbitron (Google Fonts)
- **Weights**: 400, 500, 600, 700, 800, 900

### Components
All components follow the cyberpunk aesthetic with:
- Glowing effects
- Gradient accents
- Card-based layouts
- Smooth animations

## Speech Features

### Text-to-Speech (TTS)
Uses Web Speech API:
```typescript
const utterance = new SpeechSynthesisUtterance(text)
window.speechSynthesis.speak(utterance)
```

### Speech-to-Text (STT)
Placeholder for future implementation using Web Speech API or external service.

## Customization

### Change Theme Colors
Edit `src/styles.css` `:root` variables:
```css
:root {
  --primary-bg: #0a0e27;
  --accent-cyan: #00fff9;
  /* ... */
}
```

### Add New Page
1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add nav link in `src/components/Sidebar.tsx`

### Modify API URL
Update `.env`:
```
VITE_API_URL=https://your-api.com
```

## Troubleshooting

### Port 5173 Already in Use
Change port in `vite.config.ts`:
```typescript
server: {
  port: 3000
}
```

### API Connection Failed
- Check backend is running on port 8000
- Verify CORS settings in backend
- Check `VITE_API_URL` in `.env`

### Build Errors
```bash
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run build
```

### Docker Build Issues
```bash
# Build without cache
docker build --no-cache -t ragamuffin-frontend .
```

## Production Deployment

### Build Optimization
```bash
npm run build
```

### Serve with Nginx
The Dockerfile uses nginx to serve the built application:
- Static files in `/usr/share/nginx/html`
- Default port 80
- Can customize with `nginx.conf`

### Environment Variables in Production
For production, set environment variables before build:
```bash
VITE_API_URL=https://api.production.com npm run build
```

Or use runtime configuration with nginx substitution.

## Browser Support
- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions

## Performance
- Vite provides fast HMR in development
- Production build is optimized and minified
- Code splitting for efficient loading
- Tree shaking removes unused code

## Security Notes
⚠️ **Development Setup**: This is configured for local development

For production:
- Configure proper CORS origins
- Use HTTPS
- Implement authentication
- Add CSP headers
- Sanitize user inputs
- Enable rate limiting

## Contributing
1. Follow TypeScript strict mode
2. Use functional components with hooks
3. Maintain cyberpunk design aesthetic
4. Add proper types for all props and state

## License
Part of the Ragamuffin platform
