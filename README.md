# RAG7 HR - Candidate Management System

A full-stack web application for managing job candidates with resume upload functionality.

## Features

- User authentication with JWT
- Candidate management (create, list, view)
- Resume file upload
- RESTful API backend
- React SPA frontend
- Docker-based development environment

## Tech Stack

**Backend:**
- Django 4.2
- Django REST Framework
- PostgreSQL
- JWT Authentication

**Frontend:**
- React 18
- React Router
- Axios
- Modern JavaScript (ES6+)

## Quick Start

See [frontend/README_DOCKER.md](frontend/README_DOCKER.md) for detailed setup and testing instructions.

### Basic Setup

1. Clone the repository
2. Start the stack: `docker-compose up --build`
3. Create superuser: `docker-compose exec api python manage.py createsuperuser`
4. Open http://localhost:3000 and login
5. Create candidates using the "New Candidate" button

## Project Structure

```
rag7/
├── api/                    # Django backend
│   ├── config/            # Django settings
│   ├── hr/                # HR app (Candidate model, API)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Login.js
│   │   │   ├── Candidates.js
│   │   │   └── CandidateCreate.js
│   │   ├── api.js        # Axios API client
│   │   └── App.js
│   ├── package.json
│   ├── Dockerfile
│   └── README_DOCKER.md  # Detailed setup guide
└── docker-compose.yml
```

## Development

The development environment uses Docker Compose with hot-reload:
- Frontend changes are reflected immediately
- Backend changes reload the Django dev server
- Database data persists in Docker volumes

## License

MIT