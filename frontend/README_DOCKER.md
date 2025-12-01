# RAG7 Frontend - Docker Setup Guide

This guide explains how to run the RAG7 Candidate Management System using Docker Compose.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 1.29 or higher)
- Git

## Quick Start

### 1. Start the Stack

From the repository root, run:

```bash
docker-compose up
```

This will start both the Django backend API (on port 8000) and the React frontend (on port 3000).

The first run will take a few minutes as it installs dependencies.

### 2. Create a Django Superuser

In a new terminal, while the containers are running:

```bash
docker-compose exec api python manage.py createsuperuser
```

Follow the prompts to create your admin account:
- Username: admin (or your choice)
- Email: admin@example.com (or your choice)
- Password: (choose a secure password)

### 3. Access the Application

- **Frontend SPA**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1/
- **Django Admin**: http://localhost:8000/admin/

### 4. Login to the SPA

1. Open http://localhost:3000 in your browser
2. If there's a login page, use the superuser credentials you created
3. If not already logged in, you may need to implement authentication or use the Django admin to get a JWT token

### 5. Test Candidate Creation

1. In the SPA, you should see the "Candidates" page
2. Click the "**+ New Candidate**" button in the top-right
3. Fill in the form:
   - **Full Name**: John Doe
   - **Email**: john.doe@example.com
   - **Applied Role**: Senior Developer
   - **Resume**: Upload a PDF or DOC file
4. Click "**Create Candidate**"
5. The modal should close and the new candidate should appear at the top of the candidates list

## Persistent Media Storage

The `docker-compose.yml` file includes a volume mount for media files:

```yaml
volumes:
  - ./media:/app/media
```

This ensures that uploaded resume files persist between container restarts. The `media` directory will be created in your project root.

## Development Workflow

### Stop the Stack

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f api
```

### Rebuild After Changes

If you modify dependencies (package.json or requirements):

```bash
docker-compose down
docker-compose up --build
```

### Access Django Shell

```bash
docker-compose exec api python manage.py shell
```

### Run Django Migrations

```bash
docker-compose exec api python manage.py migrate
```

## Environment Variables

The frontend uses the following environment variable:

- `REACT_APP_API_URL`: API base URL (default: http://localhost:8000/api)

You can override this in `docker-compose.yml` or create a `.env` file.

## Troubleshooting

### Port Already in Use

If ports 3000 or 8000 are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Change 3001 to any available port
```

### File Upload Issues

If you encounter file upload size errors:

1. Adjust Django settings (FILE_UPLOAD_MAX_MEMORY_SIZE)
2. Add container ulimits in `docker-compose.yml`:

```yaml
ulimits:
  nofile:
    soft: 65536
    hard: 65536
```

### CORS Errors

Ensure `django-cors-headers` is installed and configured in Django settings:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

## Notes

- The frontend uses JWT authentication stored in localStorage
- The API client automatically attaches the JWT token to requests
- Resume files are uploaded as multipart/form-data
- The backend validates file types and sizes

## Next Steps

For production deployment:
1. Use production-ready images
2. Configure proper database (PostgreSQL)
3. Set up Nginx reverse proxy
4. Enable HTTPS
5. Configure proper SECRET_KEY and DEBUG=False
6. Set up proper CORS and ALLOWED_HOSTS
