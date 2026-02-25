# RAG7 - JWT Authentication Demo

A minimal, production-minded JWT authentication and authorization scaffold for FastAPI backend with a React frontend demo.

## Features

- 🔐 JWT-based authentication
- 🛡️ Protected API routes with Bearer token validation
- ⚛️ React frontend with login demo
- ✅ Comprehensive test coverage
- 🔧 Environment-based configuration
- 📝 Clean, maintainable code structure

## Project Structure

```
rag7/
├── backend/
│   ├── src/
│   │   └── utils/
│   │       └── auth.py          # JWT utilities
│   ├── tests/
│   │   ├── test_auth.py         # Auth utilities tests
│   │   └── test_api.py          # API endpoint tests
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variables template
│   └── .env                     # Environment variables (local)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Login.jsx        # Login component
│   │   ├── App.jsx              # Main app component
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Styles
│   ├── index.html               # HTML template
│   ├── vite.config.js           # Vite configuration
│   └── package.json             # Node dependencies
└── README.md
```

## Backend Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Navigate to the backend directory:
```bash
cd backend
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

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and set your JWT_SECRET in production
```

### Running the Backend

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Running Tests

```bash
pytest -v
```

## Frontend Setup

### Prerequisites
- Node.js 16+
- npm

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

### Running the Frontend

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Usage

### Demo Credentials

- **Username:** `testuser`
- **Password:** `testpassword`

### API Endpoints

#### Public Endpoints

- `GET /` - Root endpoint
- `POST /auth/login` - Login and obtain JWT token

#### Protected Endpoints (require Bearer token)

- `GET /auth/me` - Get current user information
- `GET /protected` - Example protected route

### Authentication Flow

1. **Login**: POST credentials to `/auth/login`
   ```json
   {
     "username": "testuser",
     "password": "testpassword"
   }
   ```

2. **Receive Token**: Get JWT token in response
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "token_type": "bearer"
   }
   ```

3. **Access Protected Routes**: Include token in Authorization header
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

## Configuration

Environment variables (backend/.env):

- `JWT_SECRET` - Secret key for JWT encoding/decoding (change in production!)
- `JWT_ALGORITHM` - Algorithm for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time (default: 30)

## Security Notes

⚠️ **Important for Production:**

1. Change the `JWT_SECRET` in `.env` to a strong, random secret
2. Use HTTPS in production
3. Implement proper password hashing (e.g., bcrypt)
4. Use a real database instead of the mock user database
5. Implement refresh tokens for better security
6. Add rate limiting to prevent brute force attacks
7. Never commit `.env` files to version control

## Testing

The project includes comprehensive tests:

- **test_auth.py** - Tests for JWT utility functions
- **test_api.py** - Tests for API endpoints and authentication flow

Run tests with:
```bash
cd backend
pytest -v
```

## Development

### Backend Development

The FastAPI backend uses:
- `FastAPI` - Modern web framework
- `python-jose` - JWT implementation
- `pydantic` - Data validation
- `uvicorn` - ASGI server

Key files:
- `src/utils/auth.py` - JWT utilities and models
- `main.py` - FastAPI app with routes and dependencies

### Frontend Development

The React frontend uses:
- `React 18` - UI library
- `Vite` - Build tool
- Fetch API - HTTP client

Key files:
- `src/components/Login.jsx` - Login form
- `src/App.jsx` - Main application logic

## License

MIT