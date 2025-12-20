# Docker Setup and Testing Instructions

This document provides instructions for running the full RAG7 application stack using Docker Compose and testing the candidate creation feature.

## Prerequisites

- Docker and Docker Compose installed
- Git repository cloned locally

## Starting the Application Stack

1. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

   This will start:
   - Django REST Framework API (backend) on port 8000
   - React SPA (frontend) on port 3000
   - PostgreSQL database
   - Any other required services

2. **Create a Django superuser** (in a new terminal):
   ```bash
   docker-compose exec api python manage.py createsuperuser
   ```

   Follow the prompts to create a username, email, and password.

## Testing the Candidate Creation Feature

1. **Access the application**:
   - Open your browser and navigate to `http://localhost:3000`

2. **Log in**:
   - Use the superuser credentials you created in the previous step
   - The SPA will authenticate and store JWT tokens in localStorage

3. **Navigate to Candidates page**:
   - Go to `/candidates` route (or click the Candidates link in the navigation)

4. **Create a new candidate**:
   - Click the "New Candidate" button in the header
   - Fill in the form fields:
     - **Full Name**: Candidate's full name (required)
     - **Email**: Candidate's email address (required)
     - **Applied Role**: The position they're applying for (required)
     - **Resume**: Optional file upload (.pdf, .txt, .doc, .docx)
   - Click "Create Candidate"
   - The new candidate should appear at the top of the candidates list

5. **Verify resume upload** (if file was uploaded):
   - The candidate row should show a "View Resume" link
   - Click the link to view/download the uploaded resume
   - Resume files are stored in the backend's media directory

## Optional: Persistent Media Storage

By default, uploaded resume files are stored inside the Docker container and will be lost when the container is removed.

**For persistent storage in a follow-up PR**, you can:
1. Configure Django's `MEDIA_ROOT` setting in the backend
2. Add a volume mount in `docker-compose.yml` for the `api` service:
   ```yaml
   volumes:
     - ./media:/app/media
   ```
3. This will mount a local `./media` directory to persist uploaded files

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

- **Port conflicts**: If ports 3000 or 8000 are already in use, modify the port mappings in `docker-compose.yml`
- **Database connection issues**: Ensure PostgreSQL service is healthy before the API starts
- **File upload errors**: Check that the API service has write permissions to the media directory
- **Authentication errors**: Verify JWT tokens are being stored in localStorage and sent with API requests

## API Endpoint Reference

The candidate creation feature uses:
- **POST** `/api/v1/candidates/` - Create a new candidate
  - Content-Type: `multipart/form-data`
  - Fields: `full_name`, `email`, `applied_role`, `resume` (optional)
  - Authentication: JWT Bearer token required

For more details on the API, refer to the backend documentation or visit `/api/docs` when the API is running.
