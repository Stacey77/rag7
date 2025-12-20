# Contributing to RAG7

Thank you for your interest in contributing to RAG7!

## Development Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment template and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate
PYTHONPATH=$(pwd) pytest -v
```

Or use the convenience script:
```bash
./run_tests.sh
```

### Test Coverage

We aim for high test coverage. Please include tests for any new features or bug fixes.

## Code Style

### Python (Backend)

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and small

### JavaScript/React (Frontend)

- Use functional components with hooks
- Follow the existing code structure
- Use meaningful variable and function names
- Keep components focused and reusable

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear, focused commits
3. Write or update tests as needed
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a pull request with a clear description

## Security

If you discover a security vulnerability, please follow the guidelines in SECURITY.md.

## Questions?

Feel free to open an issue for any questions or concerns.
