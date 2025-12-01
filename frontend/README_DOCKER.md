# Docker Setup and Testing Guide

This guide explains how to run the RAG7 HR application stack using Docker Compose and test the candidate creation feature.

## Prerequisites

- Docker and Docker Compose installed on your system
- Ports 3000 (frontend), 8000 (API), and 5432 (PostgreSQL) available

## Starting the Stack

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

   This will start three services:
   - `db`: PostgreSQL database
   - `api`: Django REST Framework backend
   - `frontend`: React application

2. **Wait for all services to start.** You should see:
   - Database migrations running
   - Django development server starting on port 8000
   - React development server starting on port 3000

## Initial Setup

### Create a Django Superuser

In a new terminal, while the stack is running, create a superuser account:

```bash
docker-compose exec api python manage.py createsuperuser
```

Follow the prompts to set:
- Username
- Email (optional)
- Password

**Example:**
```
Username: admin
Email address: admin@example.com
Password: ****
Password (again): ****
```

## Testing the Candidate Creation Feature

### 1. Login to the Application

1. Open your browser and navigate to http://localhost:3000
2. You'll be redirected to the login page
3. Enter the superuser credentials you just created
4. Click **Login**

### 2. View the Candidates List

After login, you'll be redirected to the Candidates page at http://localhost:3000/candidates

The page displays:
- A list of existing candidates (empty initially)
- **New Candidate** button (green) - Opens the creation modal
- **Refresh** button (blue) - Refreshes the candidate list
- **Logout** button (red) - Logs you out

### 3. Create a New Candidate

1. Click the **New Candidate** button in the header
2. A modal form will appear with the following fields:
   - **Full Name** (required)
   - **Email** (required)
   - **Applied Role** (required)
   - **Resume** (required) - Upload a PDF, DOC, DOCX, or TXT file

3. Fill in all the fields:
   - Full Name: e.g., "John Doe"
   - Email: e.g., "john.doe@example.com"
   - Applied Role: e.g., "Senior Software Engineer"
   - Resume: Select a file from your computer

4. Click **Create**

5. The modal will close and the new candidate should appear at the top of the list

### 4. Verify the Creation

- The new candidate should be visible in the candidates table
- You can click the "View Resume" link to see the uploaded file
- The creation date should show today's date

### 5. API Validation

The form includes client-side and server-side validation:
- All fields are required
- Email must be in valid format
- Resume must be a file
- If validation fails, error messages will appear below each field

## Persistent File Storage

### Media Files (Resume Uploads)

The docker-compose configuration includes a named volume `media_files` that persists uploaded resumes:

```yaml
volumes:
  - media_files:/app/media
```

This means uploaded files are preserved even if you stop and restart the containers.

### Changing MEDIA_ROOT

To use a local directory for media files instead of a Docker volume:

1. **Edit `docker-compose.yml`:**
   ```yaml
   api:
     volumes:
       - ./api:/app
       - ./media:/app/media  # Changed from media_files:/app/media
   ```

2. **Create the media directory:**
   ```bash
   mkdir -p media
   ```

3. **Restart the stack:**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

Now uploaded resumes will be stored in `./media/resumes/` on your host machine.

## Stopping the Stack

To stop all services:

```bash
docker-compose down
```

To stop and remove all volumes (including database and uploaded files):

```bash
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If you get a port conflict error:
- Check what's using the port: `lsof -i :3000` or `lsof -i :8000`
- Stop the conflicting service or change the port in `docker-compose.yml`

### Database Connection Errors

If the API can't connect to the database:
- Wait a few seconds for PostgreSQL to fully start
- Check logs: `docker-compose logs db`

### Frontend Can't Reach API

If you get CORS or connection errors:
- Verify the API is running: http://localhost:8000/admin
- Check that `REACT_APP_API_URL` in frontend is set correctly
- Ensure CORS settings in Django allow http://localhost:3000

### File Upload Fails

If file uploads fail:
- Check file size (default limit is 10MB)
- Verify file format is supported (PDF, DOC, DOCX, TXT)
- Check API logs: `docker-compose logs api`

## Admin Interface

You can also manage candidates through Django's admin interface:

1. Navigate to http://localhost:8000/admin
2. Login with your superuser credentials
3. Click on "Candidates" to view/add/edit candidates

## Development Notes

- The frontend runs in development mode with hot-reload enabled
- The API runs Django's development server (not for production use)
- Database data persists in a Docker volume
- Changes to source code are reflected immediately (no rebuild needed)

## Next Steps

For production deployment:
- Use production-grade WSGI server (Gunicorn is included)
- Set `DEBUG=False` in Django settings
- Use a production build of the React app
- Configure proper CORS and security settings
- Set up HTTPS/SSL certificates
- Use environment variables for sensitive data
