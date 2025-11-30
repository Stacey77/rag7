# Docker Setup Instructions for HR System

This document provides instructions for running the HR Candidate Management System using Docker Compose.

## Prerequisites

- Docker (20.10 or later)
- Docker Compose (2.0 or later)

## Architecture

The application consists of three services:
- **db**: PostgreSQL 15 database
- **api**: Django REST Framework backend (port 8000)
- **frontend**: React SPA served by nginx (port 3000)

## Quick Start

### 1. Build and Start Services

From the repository root, run:

```bash
docker-compose up --build
```

This command will:
- Build the backend and frontend Docker images
- Start PostgreSQL, API, and frontend services
- Run database migrations automatically
- Make the app available at http://localhost:3000

### 2. Create a Django Superuser

In a new terminal, create a superuser account to log into the system:

```bash
docker-compose exec api python manage.py createsuperuser
```

Follow the prompts to enter:
- Username (e.g., `admin`)
- Email address (optional)
- Password (enter twice for confirmation)

### 3. Access the Application

1. Open your browser and navigate to **http://localhost:3000**
2. You'll be redirected to the login page
3. Enter the credentials you created in step 2
4. After successful login, you'll see the Candidates page

## Testing the New Candidate Creation Feature

### Creating a Candidate

1. On the Candidates page, click the **"New Candidate"** button in the header
2. A modal form will appear with the following fields:
   - **Full Name** (required): Enter the candidate's full name
   - **Email** (required): Enter a valid email address
   - **Applied Role** (required): Enter the job role (e.g., "Software Engineer")
   - **Resume**: Upload a PDF, DOC, DOCX, or TXT file (optional)
3. Click **"Create Candidate"** to submit
4. The modal will close and the new candidate will appear at the top of the list

### Expected Behavior

- **Success**: The modal closes, candidate appears in the list immediately
- **Validation Errors**: Form displays error messages for invalid/missing fields
- **Duplicate Email**: Backend returns an error if email already exists
- **File Upload**: Resume files are stored in the backend's media directory and accessible via the "View Resume" link

## Additional Commands

### Stop Services

```bash
docker-compose down
```

### Stop Services and Remove Volumes (⚠️ This deletes all data)

```bash
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
```

### Run Backend Tests (if any)

```bash
docker-compose exec api python manage.py test
```

### Access Django Admin

Navigate to **http://localhost:8000/admin** and log in with your superuser credentials to manage candidates directly.

## Troubleshooting

### Port Conflicts

If ports 3000, 8000, or 5432 are already in use, edit `docker-compose.yml` to change the port mappings:

```yaml
ports:
  - "3001:80"  # Change frontend to port 3001
```

### Database Connection Issues

If the API can't connect to the database, ensure the db service is healthy:

```bash
docker-compose ps
```

Wait until the `db` service shows as "healthy" before the API starts.

### Frontend Can't Reach API

The frontend is configured to connect to `http://localhost:8000/api`. If running on a different host:

1. Update `frontend/.env` with the correct API URL
2. Rebuild the frontend: `docker-compose up --build frontend`

### File Upload Issues

Resume uploads are stored in a Docker volume. To persist uploads across container restarts, the `media_files` volume is created automatically. If you encounter permission issues:

```bash
docker-compose exec api chown -R root:root /app/media
```

## Environment Variables

### Backend (API)

Set in `docker-compose.yml` under `api.environment`:
- `DEBUG`: Enable Django debug mode (True/False)
- `SECRET_KEY`: Django secret key
- `POSTGRES_*`: Database connection settings
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames
- `CORS_ALLOWED_ORIGINS`: Comma-separated CORS allowed origins

### Frontend

Set in `docker-compose.yml` under `frontend.environment`:
- `REACT_APP_API_URL`: Backend API base URL

## Development Workflow

For active development with hot-reloading:

### Backend Development

```bash
# Install dependencies locally
cd backend
pip install -r requirements.txt

# Run server with hot-reload
python manage.py runserver
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start
```

Then access the dev server at http://localhost:3000 (React's dev server with hot-reload).

## Notes

- The current setup uses basic authentication with JWT tokens stored in localStorage
- File uploads are limited by Django's default settings (2.5 MB). To increase, add `DATA_UPLOAD_MAX_MEMORY_SIZE` to Django settings
- In production, consider using a proper web server (Gunicorn/uWSGI) for the Django backend
- For production, set `DEBUG=False` and configure proper `SECRET_KEY` and `ALLOWED_HOSTS`

## Next Steps / Future Improvements

- Add candidate detail/edit views
- Implement candidate search and filtering
- Add unit and integration tests
- Set up CI/CD pipeline
- Configure production-ready environment with proper secrets management
- Add file size validation on the frontend before upload
