# RAG7 - HR Candidate Management System

A full-stack web application for managing HR candidates with resume upload capabilities.

## Features

- **User Authentication**: JWT-based authentication with automatic token refresh
- **Candidate Management**: Create, list, and view candidates
- **Resume Upload**: Upload and store candidate resumes (PDF, DOC, DOCX, TXT)
- **Responsive UI**: Clean React interface with modal-based candidate creation
- **Docker-based Development**: Complete Docker Compose setup for easy local development

## Tech Stack

### Backend
- Python 3.11
- Django 4.2.24
- Django REST Framework 3.14.0
- PostgreSQL 15
- JWT Authentication (djangorestframework-simplejwt)

### Frontend
- React 18.2.0
- React Router 6.20.1
- Axios 1.12.0
- Inline CSS styling (no external CSS frameworks)

### Infrastructure
- Docker & Docker Compose
- PostgreSQL database with persistent volumes
- Media file storage with Docker volumes

## Quick Start

See [frontend/README_DOCKER.md](frontend/README_DOCKER.md) for detailed setup instructions.

### TL;DR

```bash
# Start all services
docker compose up --build

# Create superuser (in another terminal)
docker compose exec api python manage.py createsuperuser

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Django Admin: http://localhost:8000/admin
```

## Project Structure

```
.
├── backend/                 # Django REST API
│   ├── config/             # Django project settings
│   ├── hr/                 # HR app (Candidate model, views, serializers)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React SPA
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Login.js
│   │   │   ├── Candidates.js
│   │   │   └── CandidateCreate.js  # ⭐ Main feature
│   │   ├── App.js
│   │   └── api.js         # Axios API client with JWT handling
│   ├── Dockerfile
│   └── README_DOCKER.md   # Detailed Docker & testing guide
└── docker-compose.yml     # Multi-container setup
```

## API Endpoints

- `POST /api/token/` - Obtain JWT tokens (login)
- `POST /api/token/refresh/` - Refresh access token
- `GET /api/v1/candidates/` - List all candidates (requires auth)
- `POST /api/v1/candidates/` - Create new candidate with resume upload (requires auth)

## Security

- All dependencies scanned for vulnerabilities and updated to secure versions
- Django 4.2.24 (fixes SQL injection vulnerabilities)
- Gunicorn 22.0.0 (fixes request smuggling vulnerability)
- Axios 1.12.0 (fixes SSRF and DoS vulnerabilities)
- CodeQL security scanning passed with 0 alerts
- JWT-based authentication
- CORS configured for local development

## Development

### Running Tests

```bash
# Backend tests
docker compose exec api python manage.py test

# Frontend tests
docker compose exec frontend npm test
```

### Making Changes

- **Backend**: Restart API service after changes: `docker compose restart api`
- **Frontend**: Changes are auto-reloaded by React dev server

### Database Migrations

```bash
docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py migrate
```

## License

This project is for demonstration purposes.