# Docker Setup and Usage Guide

This document provides instructions for running the RAG7 HR application using Docker Compose and testing the candidate creation feature.

## Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)

## Starting the Application

### 1. Build and Start All Services

From the repository root directory, run:

```bash
docker-compose up --build
```

This will:
- Start a PostgreSQL database
- Build and start the Django API backend (on port 8000)
- Build and start the React frontend (on port 3000)

Wait for all services to start. You should see logs indicating the services are ready.

### 2. Create a Django Superuser

In a new terminal, create a superuser account to log into the application:

```bash
docker-compose exec api python manage.py createsuperuser
```

Follow the prompts to set:
- Username (e.g., `admin`)
- Email (optional, can press Enter to skip)
- Password (you'll need to type it twice)

## Testing the Candidate Creation Feature

### 1. Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

### 2. Log In

- You'll be redirected to the login page
- Enter the username and password you created in step 2 above
- Click "Login"

### 3. View Candidates List

After logging in, you'll see the Candidates page with:
- A "New Candidate" button (green)
- A "Refresh" button (blue)
- A "Logout" button (red)
- An empty list or existing candidates (if any)

### 4. Create a New Candidate

1. Click the **"New Candidate"** button
2. A modal form will appear with the following fields:
   - **Full Name** (required)
   - **Email** (required)
   - **Applied Role** (required)
   - **Resume** (required) - accepts PDF, DOC, DOCX, or TXT files
3. Fill in all fields and select a resume file
4. Click **"Create Candidate"**
5. If successful:
   - The modal will close
   - The new candidate will appear at the top of the list
   - Resume file can be viewed by clicking "View Resume"

### 5. Validation

- All fields are required
- Email must be a valid email format
- Resume file is required
- API validation errors will be displayed in the modal

## Accessing the Django Admin

You can also manage candidates through the Django admin interface:

```
http://localhost:8000/admin
```

Log in with the superuser credentials you created.

## Stopping the Application

To stop all services:

```bash
docker-compose down
```

To stop and remove all data (including database):

```bash
docker-compose down -v
```

## Troubleshooting

### Frontend Can't Connect to Backend

- Ensure the API service is running: `docker-compose ps`
- Check API logs: `docker-compose logs api`
- Verify CORS settings in `backend/config/settings.py`

### Database Connection Issues

- Ensure the database service is healthy: `docker-compose ps`
- Check database logs: `docker-compose logs db`
- Try restarting services: `docker-compose restart`

### File Upload Issues

- Resume files are stored in the `media_data` Docker volume
- For persistent storage across container recreates, the volume is configured in `docker-compose.yml`
- Check API logs for file upload errors: `docker-compose logs api`

## Development Notes

### Making Code Changes

- Backend changes: Django auto-reloads are disabled in production mode. Restart the API service:
  ```bash
  docker-compose restart api
  ```

- Frontend changes: React development server watches for changes automatically. No restart needed.

### Running Migrations

After modifying Django models:

```bash
docker-compose exec api python manage.py makemigrations
docker-compose exec api python manage.py migrate
```

### Viewing Logs

- All services: `docker-compose logs -f`
- Specific service: `docker-compose logs -f api` (or `frontend`, `db`)

## Architecture Overview

- **Frontend (React)**: SPA running on port 3000, uses JWT authentication
- **API (Django/DRF)**: REST API on port 8000, handles authentication and candidate management
- **Database (PostgreSQL)**: Persistent data storage on port 5432
- **Media Files**: Stored in Docker volume `media_data` for persistence

## Security Notes

- The default configuration uses development settings
- Change `SECRET_KEY` and `DB_PASSWORD` for production use
- Enable HTTPS in production
- Configure proper ALLOWED_HOSTS and CORS_ALLOWED_ORIGINS for production
