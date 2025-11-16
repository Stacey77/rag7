# Docker Setup Instructions

This document provides instructions for running the RAG7 application using Docker.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git (to clone the repository)

## Quick Start

### 1. Start the Application Stack

From the root directory of the project, run:

```bash
docker-compose up --build
```

This will build and start three services:
- **api**: Django REST API backend (port 8000)
- **db**: PostgreSQL database (port 5432)
- **frontend**: React SPA (port 3000)

The first build may take several minutes. Subsequent starts will be faster.

### 2. Create a Django Superuser

In a new terminal, while the stack is running, create a superuser account:

```bash
docker-compose exec api python manage.py migrate
docker-compose exec api python manage.py createsuperuser
```

Follow the prompts to create a username and password. You can use simple credentials for local development (e.g., username: `admin`, password: `admin`).

### 3. Access the Application

#### Login to the SPA

1. Open your browser and navigate to: http://localhost:3000
2. You'll be redirected to the login page
3. Enter the superuser credentials you created in step 2
4. Click "Login"

#### View Candidates

After logging in, you'll be automatically redirected to the `/candidates` page where you can:
- View the list of all candidates
- Click the **"New Candidate"** button to create a new candidate

#### Create a Candidate

1. Click the **"New Candidate"** button in the header
2. Fill in the form fields:
   - **Full Name** (required)
   - **Email** (required)
   - **Applied Role** (required)
   - **Resume** (optional) - accepts `.pdf`, `.txt`, `.doc`, `.docx` files
3. Click **"Create"**
4. The new candidate will appear at the top of the candidates list
5. If there are validation errors, they will be displayed in the form

### 4. View Uploaded Resumes

Resume files are uploaded to the `./media/resumes/` directory on the host machine. To persist uploaded files:

```bash
# The media directory is already mounted in docker-compose.yml
# Files are saved to: ./media/resumes/
```

You can access resume files via the API at: `http://localhost:8000/media/resumes/<filename>`

## Development Notes

### Environment Variables

The application uses the following environment variables (configured in `docker-compose.yml`):

**Backend (api service):**
- `DEBUG=1` - Enable Django debug mode
- `SECRET_KEY` - Django secret key (change in production!)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of CORS origins

**Frontend (frontend service):**
- `REACT_APP_API_URL=http://localhost:8000` - Backend API URL
- `CHOKIDAR_USEPOLLING=true` - Enable hot reload in Docker

### Persistent Data

- Database data is stored in a Docker volume: `postgres_data`
- Media files (resumes) are mounted to `./media` on the host

### Stopping the Stack

To stop all services:

```bash
docker-compose down
```

To stop and remove all data (including the database):

```bash
docker-compose down -v
```

## Troubleshooting

### Port Conflicts

If you see port binding errors, ensure ports 3000, 8000, and 5432 are not in use by other applications.

### Database Connection Issues

If the API can't connect to the database, try:

```bash
docker-compose down
docker-compose up --build
```

### Frontend Hot Reload Not Working

The `CHOKIDAR_USEPOLLING=true` environment variable should enable hot reload. If it's still not working, restart the frontend service:

```bash
docker-compose restart frontend
```

### Permission Issues with Media Files

If you encounter permission issues with uploaded files, ensure the `./media` directory has appropriate permissions:

```bash
mkdir -p media/resumes
chmod -R 755 media
```

## Next Steps

- Configure production settings (SECRET_KEY, DEBUG=False, etc.)
- Set up a production-ready database (PostgreSQL with proper configuration)
- Add nginx for serving static/media files in production
- Implement additional candidate features (edit, delete, resume scoring)
- Add unit and integration tests
