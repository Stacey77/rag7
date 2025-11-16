# Epic Platform Web Client

Cyberpunk-themed React/TypeScript frontend for the Epic Platform.

## Features

- **Dashboard**: Real-time metrics and AI core status visualization
- **Playground**: Interactive conversation interface with STT/TTS support
- **Datasets**: Dataset management and upload functionality
- **Agent Builder**: Create, save, and execute LangFlow agents

## Tech Stack

- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client for API requests

## Theme

Cyberpunk-inspired design featuring:
- **Orbitron** font family
- Cyan/magenta/yellow accent colors
- Neon glow effects
- Animated components
- Dark color scheme

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Local Setup

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The dev server will start on `http://localhost:5173`

### Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

- `VITE_API_URL`: Backend API base URL

## Docker

### Build Image

```bash
docker build -t epic-platform-web-client .
```

### Run Container

```bash
docker run -p 8080:80 epic-platform-web-client
```

Access at `http://localhost:8080`

## Project Structure

```
web-client/
├── src/
│   ├── components/
│   │   ├── Sidebar.tsx        # Navigation sidebar
│   │   ├── AIBrain.tsx        # Animated AI visualization
│   │   ├── SectionAgent.tsx   # Agent status component
│   │   └── Conversation.tsx   # Chat interface with STT/TTS
│   ├── pages/
│   │   ├── Dashboard.tsx      # Main dashboard
│   │   ├── Playground.tsx     # Interactive testing
│   │   ├── Datasets.tsx       # Dataset management
│   │   └── AgentBuilder.tsx   # Flow creation and execution
│   ├── App.tsx                # Main app component with routing
│   ├── main.tsx               # Application entry point
│   └── styles.css             # Global styles and theme
├── public/                    # Static assets
├── index.html                 # HTML template
├── vite.config.ts             # Vite configuration
├── tsconfig.json              # TypeScript configuration
├── Dockerfile                 # Multi-stage Docker build
├── nginx.conf                 # Nginx configuration
└── package.json               # Dependencies and scripts
```

## Components

### Sidebar
Navigation component with:
- Dashboard
- Playground
- Datasets
- Agent Builder
- System status indicator

### AIBrain
Animated AI core visualization with:
- Rotating rings
- Pulsing center
- Real-time stats

### SectionAgent
Expandable agent cards showing:
- Status indicator
- Metrics
- Performance stats

### Conversation
Chat interface featuring:
- Message history
- Speech-to-Text (STT) input
- Text-to-Speech (TTS) output
- Real-time responses

## Pages

### Dashboard
Overview with:
- Key metrics cards
- AI core status
- Agent status panels

### Playground
Interactive testing environment:
- Conversation interface
- Model selection
- Parameter tuning
- Interaction history

### Datasets
Data management:
- Upload datasets
- View dataset list
- Dataset statistics
- File management

### Agent Builder
Flow management:
- Save flows from LangFlow
- List saved flows
- Execute flows with input
- View execution results
- Backend connection status

## API Integration

The frontend integrates with the backend API at `VITE_API_URL`:

### Endpoints Used

- `GET /list_flows/` - List all saved flows
- `POST /save_flow/` - Save a new flow
- `GET /get_flow/{flow_name}` - Get flow definition
- `POST /run_flow/` - Execute a flow

### Example Usage

```typescript
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

// List flows
const response = await axios.get(`${API_URL}/list_flows/`)

// Save flow
const formData = new FormData()
formData.append('flow_name', 'my_flow')
formData.append('flow_json', file)
await axios.post(`${API_URL}/save_flow/`, formData)

// Run flow
const formData = new FormData()
formData.append('flow_name', 'my_flow')
formData.append('user_input', 'Hello')
await axios.post(`${API_URL}/run_flow/`, formData)
```

## Styling

### CSS Variables

Theme colors defined in `:root`:
- `--bg-primary`: Main background
- `--bg-secondary`: Secondary background
- `--accent-primary`: Cyan accent
- `--accent-secondary`: Magenta accent
- `--text-primary`: Primary text
- `--border-color`: Border color

### Component Styles

Each component has its own CSS file for maintainability.

### Responsive Design

Breakpoints:
- Mobile: < 768px
- Desktop: >= 768px

## Speech APIs

### Speech-to-Text (STT)

Uses Web Speech API (when available):
```typescript
const recognition = new SpeechRecognition()
recognition.start()
```

### Text-to-Speech (TTS)

Uses Web Speech Synthesis API:
```typescript
const utterance = new SpeechSynthesisUtterance(text)
window.speechSynthesis.speak(utterance)
```

## Building for Production

```bash
# Build
npm run build

# Output in dist/ directory
ls -la dist/

# Test production build
npm run preview
```

## Nginx Configuration

The included `nginx.conf`:
- Serves SPA with proper routing
- Enables gzip compression
- Sets security headers
- Configures caching

## Troubleshooting

### Build Fails
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API Connection Issues
Check `.env` file and ensure `VITE_API_URL` is correct.

### Port Already in Use
Change port in `vite.config.ts`:
```typescript
server: {
  port: 5174, // or any available port
}
```

## Browser Support

- Chrome/Edge: Latest
- Firefox: Latest
- Safari: 14+

Speech APIs may not be available in all browsers.

## License

Part of Epic Platform monorepo.
