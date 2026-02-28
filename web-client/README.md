# Ragamuffin Web Client

Modern React+TypeScript frontend for the Ragamuffin visual agent builder platform.

## Features

- **Cyberpunk-themed UI** with Orbitron font
- **Dashboard** - Monitor agents and system status
- **Agent Builder** - Upload and execute LangFlow flows
- **Playground** - Interactive testing with STT/TTS support
- **Datasets** - Manage data sources

## Technology Stack

- React 18
- TypeScript
- Vite (build tool)
- React Router (routing)
- CSS3 (custom cyberpunk theme)

## Development

### Prerequisites

- Node.js 18+ and npm

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:8080

### Build for Production

```bash
npm run build
```

Build output will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Docker

### Build Image

```bash
docker build -t ragamuffin-web-client .
```

### Run Container

```bash
docker run -p 8080:80 ragamuffin-web-client
```

## Environment Variables

Configure via `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
web-client/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Sidebar.tsx
│   │   ├── AIBrain.tsx
│   │   ├── SectionAgent.tsx
│   │   └── Conversation.tsx
│   ├── pages/          # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Playground.tsx
│   │   ├── Datasets.tsx
│   │   └── AgentBuilder.tsx
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── styles.css      # Global styles
├── index.html          # HTML template
├── vite.config.ts      # Vite configuration
├── tsconfig.json       # TypeScript configuration
└── package.json        # Dependencies and scripts
```

## Features Detail

### Dashboard
- System status visualization
- AI brain animation
- Agent cards with activation states
- Quick statistics

### Agent Builder
- Connect to backend API
- List available flows
- Upload new flows (JSON)
- Execute flows with user input
- View results (real or simulated)
- Getting started guide

### Playground
- Interactive conversation interface
- STT (Speech-to-Text) support
- TTS (Text-to-Speech) support
- Real-time agent activity visualization

### Datasets
- List datasets
- Upload/download functionality
- Storage monitoring
- File metadata display

## Customization

### Theme Colors

Edit `src/styles.css` CSS variables:

```css
:root {
  --primary-color: #00d4ff;    /* Cyan */
  --secondary-color: #ff00ff;   /* Magenta */
  --accent-color: #00ff41;      /* Green */
}
```

### Adding New Pages

1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation link in `src/components/Sidebar.tsx`

## API Integration

The frontend communicates with the backend API at `VITE_API_URL`:

- `GET /list_flows/` - List all flows
- `GET /get_flow/{name}` - Get flow details
- `POST /save_flow/` - Upload new flow
- `POST /run_flow/` - Execute flow

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Performance

- Code splitting with React.lazy
- Optimized production build with Vite
- CSS minification
- Asset optimization

## Security Notes

⚠️ **Development Only**: This frontend is configured for local development.

For production:

1. **HTTPS**: Serve over HTTPS
2. **API Security**: Update API URL to production backend
3. **CORS**: Ensure backend allows your domain
4. **CSP**: Implement Content Security Policy headers
5. **Authentication**: Add JWT/OAuth integration
6. **Input Validation**: Validate all user inputs
7. **XSS Protection**: Already implemented via React's escaping

## Troubleshooting

### Port Already in Use

Change port in `vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    port: 3000  // Your preferred port
  }
})
```

### API Connection Issues

1. Check backend is running at `VITE_API_URL`
2. Verify CORS is enabled on backend
3. Check browser console for errors
4. Verify `.env` file is loaded

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

## Contributing

1. Follow existing code style
2. Use TypeScript for type safety
3. Keep components small and focused
4. Add CSS in separate files
5. Test in multiple browsers

## Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [React Router](https://reactrouter.com/)
