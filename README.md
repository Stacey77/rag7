# RAG7 - Retrieval Augmented Generation API

A production-ready RAG (Retrieval Augmented Generation) API with JWT authentication and authorization.

## Features

- 🔐 **JWT Authentication**: Secure token-based authentication for all API endpoints
- 🚀 **FastAPI Backend**: High-performance async API framework
- 🔌 **WebSocket Support**: Real-time chat with authentication
- 🧪 **Comprehensive Tests**: Full test coverage with pytest
- 🔄 **CI/CD Ready**: GitHub Actions workflow for automated testing

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and set a secure JWT_SECRET
```

**Important**: Generate a secure JWT secret for production:
```bash
# Generate a secure random secret
openssl rand -hex 32
# Add this to your .env file as JWT_SECRET
```

### Running the Application

Start the API server:
```bash
python -m src.interfaces.web_api
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

### Login

Get a JWT access token:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Protected Endpoints

Include the token in the Authorization header:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer <your-token-here>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, RAG7!"}'
```

### Refresh Token

Get a new access token using your current valid token:
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Authorization: Bearer <your-token-here>"
```

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_auth.py -v
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `JWT_SECRET` | Secret key for JWT signing | - | Yes |
| `JWT_ALGORITHM` | JWT signing algorithm | HS256 | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 | No |
| `STATIC_USERS` | Static user list (username:hash) | admin user | No |
| `APP_HOST` | Server host | 0.0.0.0 | No |
| `APP_PORT` | Server port | 8000 | No |

### Static Users (Development Only)

For development/testing, users are configured via the `STATIC_USERS` environment variable:

```bash
STATIC_USERS=user1:$2b$12$hash1,user2:$2b$12$hash2
```

Generate password hash:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("your-password")
print(hashed)
```

## Security Considerations

### Production Deployment

⚠️ **Important**: This MVP uses static user configuration and symmetric JWT signing. For production, implement the following:

#### 1. Replace Static Users with Identity Provider

Integrate with a proper identity provider:
- **OAuth 2.0 / OIDC**: Azure AD, Auth0, Okta, Google, GitHub
- **SAML**: Enterprise SSO
- **Custom**: Database-backed user management with proper password policies

#### 2. Use Asymmetric Key Signing

Replace symmetric HS256 with asymmetric RS256/ES256:
- Generate RSA/ECDSA key pair
- Use public key for token verification
- Keep private key secure (secrets manager, HSM)

```python
# Example RS256 configuration
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY=<path-to-private-key.pem>
JWT_PUBLIC_KEY=<path-to-public-key.pem>
```

#### 3. Implement Refresh Tokens

- Separate refresh tokens (longer-lived, stored securely)
- Implement token rotation
- Add revocation list for compromised tokens
- Store refresh tokens in secure, httpOnly cookies

#### 4. Additional Security Measures

- **Rate Limiting**: Protect against brute force attacks
- **HTTPS Only**: Never transmit tokens over unencrypted connections
- **CORS**: Configure allowed origins properly (not "*")
- **Token Rotation**: Rotate JWT secrets regularly
- **Audit Logging**: Log all authentication attempts
- **MFA**: Multi-factor authentication for sensitive operations

#### 5. Secrets Management

Never commit secrets to version control:
- Use environment variables
- Use secret management services (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
- Rotate secrets regularly
- Use different secrets for different environments

### Token Security

- **Token Expiration**: Keep access tokens short-lived (15-30 minutes)
- **Secure Storage**: Store tokens securely on client side
- **Transmission**: Always use HTTPS in production
- **Validation**: Verify token signature, expiration, and claims

## API Endpoints

### Public Endpoints

- `GET /` - Health check
- `GET /health` - Health check
- `POST /auth/login` - Login and get JWT token

### Protected Endpoints (Require Authentication)

- `POST /auth/refresh` - Refresh access token
- `POST /chat` - Send chat message and get response
- `GET /protected/info` - Get user information
- `WS /ws/chat` - WebSocket chat endpoint

## WebSocket Usage

Connect to WebSocket endpoint with authentication:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
  // First message must be authentication
  ws.send(JSON.stringify({
    type: 'auth',
    token: '<your-jwt-token>'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'auth_success') {
    console.log('Authenticated!');
    
    // Send chat message
    ws.send(JSON.stringify({
      type: 'chat',
      message: 'Hello!'
    }));
  }
  
  if (data.type === 'chat_response') {
    console.log('Response:', data.message);
  }
};
```

## Development Roadmap

### Current (MVP)
- ✅ JWT authentication with static users
- ✅ Protected API endpoints
- ✅ WebSocket authentication
- ✅ Comprehensive test suite
- ✅ CI/CD pipeline

### Planned
- 🔄 OAuth/OIDC integration
- 🔄 Refresh token implementation
- 🔄 Rate limiting
- 🔄 Audit logging
- 🔄 Vector store integration
- 🔄 LLM integration for RAG
- 🔄 Document ingestion pipeline
- 🔄 Dashboard UI

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.