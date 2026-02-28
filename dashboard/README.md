# FortFail Dashboard

Modern React-based dashboard for the FortFail orchestrator.

## Features

- **Authentication**: Obtain JWT tokens via registration secret
- **Agent Monitoring**: View registered agents
- **Job Management**: Create and track restore jobs
- **Real-time Events**: WebSocket-based live event streaming
- **Job Status**: Check status of restore operations

## Prerequisites

- Node.js 16+ and npm

## Installation

```bash
npm install
```

## Development

```bash
npm start
```

This will start the development server on http://localhost:1234

## Build

```bash
npm build
```

Outputs optimized production build to `dist/` directory.

## Configuration

Set the orchestrator API URL via environment variable:

```bash
export REACT_APP_API_URL=http://localhost:8000
npm start
```

Default: `http://localhost:8000`

## Usage

1. **Authenticate**: Enter your registration secret to obtain a JWT token
2. **View Agents**: Click "Refresh Agents" to see registered agents
3. **Create Job**: Enter snapshot ID and target agent ID to create a restore job
4. **Monitor**: Watch real-time events in the Event Logs panel
5. **Check Status**: Enter a job ID to view its current status

## Technology Stack

- **React 18**: UI framework
- **Parcel**: Zero-config bundler
- **WebSocket**: Real-time event streaming
- **Fetch API**: REST API communication

## License

MIT License
