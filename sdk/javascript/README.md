# Ragamuffin JavaScript/TypeScript SDK

Official JavaScript/TypeScript client library for the Ragamuffin AI platform.

## Installation

```bash
# From npm (when published)
npm install @ragamuffin/sdk

# From source
npm install /path/to/sdk/javascript
```

## Quick Start

```typescript
import { RagamuffinClient } from '@ragamuffin/sdk';

// Initialize client
const client = new RagamuffinClient('http://localhost:8000');

// Login
await client.login('user@example.com', 'password');

// Embed documents
const result = await client.rag.embed(['Document 1', 'Document 2']);

// Search
const results = await client.rag.search('machine learning', { topK: 5 });

// RAG query
const response = await client.rag.query('What is machine learning?');
console.log(response);
```

## Features

### Authentication

```typescript
// Login
await client.login('user@example.com', 'password');

// Register new account
await client.register('John Doe', 'john@example.com', 'securepassword');

// Get current user
const user = await client.auth.me();

// Logout
client.logout();
```

### RAG Operations

```typescript
// Embed text documents
await client.rag.embed(['Doc 1', 'Doc 2'], {
  collection: 'my_collection',
});

// Embed an image
const file = new File(['...'], 'image.jpg', { type: 'image/jpeg' });
await client.rag.embedImage(file);

// Vector search
const results = await client.rag.search('query text', { topK: 10 });

// RAG query with context retrieval
const response = await client.rag.query('What is the meaning of life?');

// List collections
const { collections } = await client.rag.collections();
```

### Flow Management

```typescript
// List flows
const { flows } = await client.flows.list();

// Save a flow
await client.flows.save('my_flow', { nodes: [], edges: [] });

// Get a flow
const flow = await client.flows.get('my_flow');

// Run a flow
const result = await client.flows.run('my_flow', 'Hello!');

// Delete a flow
await client.flows.delete('my_flow');
```

### Voice (Retell.ai)

```typescript
// Check status
const status = await client.voice.status();

// List agents
const { agents } = await client.voice.agents();

// Create web call
const call = await client.voice.createWebCall('agent_123');

// Create phone call
const phoneCall = await client.voice.createPhoneCall('agent_123', '+1234567890');

// List calls
const { calls } = await client.voice.calls();

// End call
await client.voice.endCall('call_123');
```

## Error Handling

```typescript
import {
  RagamuffinClient,
  AuthenticationError,
  APIError,
  RateLimitError,
  NotFoundError,
} from '@ragamuffin/sdk';

const client = new RagamuffinClient('http://localhost:8000');

try {
  await client.login('user@example.com', 'wrong_password');
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.log('Login failed:', error.message);
  }
}

try {
  const result = await client.rag.search('query');
} catch (error) {
  if (error instanceof RateLimitError) {
    console.log(`Rate limited. Retry after ${error.retryAfter} seconds`);
  } else if (error instanceof APIError) {
    console.log('API error:', error.message);
  }
}
```

## TypeScript Types

The SDK includes full TypeScript type definitions:

```typescript
import type {
  User,
  TokenResponse,
  SearchResult,
  QueryResponse,
  Flow,
  Call,
  RetellAgent,
} from '@ragamuffin/sdk';

// All methods return properly typed responses
const user: User = await client.auth.me();
const results: SearchResult[] = (await client.rag.search('query')).results;
```

## Browser Usage

```html
<script type="module">
  import { RagamuffinClient } from '@ragamuffin/sdk';
  
  const client = new RagamuffinClient('http://localhost:8000');
  
  async function search() {
    await client.login('user@example.com', 'password');
    const results = await client.rag.search('query');
    console.log(results);
  }
  
  search();
</script>
```

## Node.js Usage

```javascript
const { RagamuffinClient } = require('@ragamuffin/sdk');

const client = new RagamuffinClient('http://localhost:8000');

async function main() {
  await client.login('user@example.com', 'password');
  const results = await client.rag.search('query');
  console.log(results);
}

main();
```

## API Reference

### RagamuffinClient

Main client class for interacting with the API.

**Constructor:**
```typescript
new RagamuffinClient(options?: RagamuffinClientOptions | string)
```

**Options:**
- `baseUrl` (string): Base URL of the Ragamuffin API
- `timeout` (number): Request timeout in milliseconds (default: 30000)
- `apiKey` (string, optional): API key for authentication

**Methods:**
- `login(email, password)`: Login with credentials
- `register(name, email, password)`: Register new account
- `logout()`: Clear authentication tokens
- `setTokens(accessToken, refreshToken)`: Set tokens directly
- `health()`: Check API health
- `isAuthenticated()`: Check if client has tokens

**Properties:**
- `auth`: AuthClient for authentication operations
- `rag`: RAGClient for RAG operations
- `flows`: FlowsClient for flow management
- `voice`: VoiceClient for voice/Retell operations

### RAGClient

**Methods:**
- `embed(texts, options)`: Embed text documents
- `embedImage(file, options)`: Embed images
- `search(query, options)`: Vector search
- `query(query, options)`: RAG query
- `collections()`: List collections
- `createCollection(name, options)`: Create collection
- `deleteCollection(name)`: Delete collection

### FlowsClient

**Methods:**
- `list()`: List all flows
- `get(name)`: Get flow by name
- `save(name, content)`: Save a flow
- `run(flow, userInput, options)`: Execute a flow
- `delete(name)`: Delete a flow

### VoiceClient

**Methods:**
- `status()`: Check Retell configuration
- `agents()`: List agents
- `getAgent(agentId)`: Get agent details
- `createWebCall(agentId, options)`: Start web call
- `createPhoneCall(agentId, toPhone, options)`: Start phone call
- `calls(options)`: List call history
- `getCall(callId)`: Get call details
- `endCall(callId)`: End call
- `voices()`: List available voices

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## License

MIT License
