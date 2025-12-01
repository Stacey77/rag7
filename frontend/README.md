# RAG7 Frontend

React-based frontend application for the RAG7 Candidate Management System.

## Features

- **Candidate List View**: Display all candidates with their details
- **Candidate Creation**: Modal form to create new candidates with resume upload
- **Resume Management**: Upload and view candidate resumes
- **Resume Scoring**: Integration for scoring candidate resumes (placeholder)
- **JWT Authentication**: Secure API communication with JWT tokens

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/
│   │   ├── Candidates.js    # Main candidates list component
│   │   ├── Candidates.css   # Styles for candidates list
│   │   ├── CandidateCreate.js   # Candidate creation modal
│   │   └── CandidateCreate.css  # Styles for creation modal
│   ├── api.js              # Axios API client configuration
│   ├── App.js              # Main App component
│   ├── App.css             # App styles
│   ├── index.js            # React entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies and scripts
├── README_DOCKER.md        # Docker setup instructions
└── .env.example            # Environment variables example
```

## Components

### Candidates.js

Main component that displays the candidate list and manages candidate interactions.

**Features:**
- Fetches and displays all candidates
- "New Candidate" button to open creation modal
- Optimistic UI updates when new candidate is created
- Resume scoring functionality (placeholder)
- Error handling and loading states

### CandidateCreate.js

Modal form component for creating new candidates.

**Props:**
- `open` (boolean): Controls modal visibility
- `onClose` (function): Callback when modal is closed
- `onCreated` (function): Callback with created candidate data

**Features:**
- Form validation
- File upload for resumes
- API error display
- Loading states during submission
- Accepts PDF, DOC, and DOCX files

## API Integration

The frontend uses an Axios client configured in `src/api.js`:

- **Base URL**: `${REACT_APP_API_URL}/v1/`
- **Authentication**: JWT token from localStorage
- **Auto-attach**: Token automatically added to all requests

### API Endpoints Used

- `GET /api/v1/candidates/` - Fetch all candidates
- `POST /api/v1/candidates/` - Create new candidate (multipart/form-data)
- `POST /api/v1/candidates/:id/score/` - Score candidate resume (placeholder)

## Development

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm start
```

Runs the app at http://localhost:3000

### Build for Production

```bash
npm run build
```

Creates optimized production build in `build/` directory.

### Run Tests

```bash
npm test
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

## Authentication

The app expects JWT authentication. The token should be stored in localStorage:

```javascript
localStorage.setItem('token', 'your-jwt-token');
```

The API client will automatically include it in the Authorization header:

```
Authorization: Bearer <token>
```

## Docker

See [README_DOCKER.md](./README_DOCKER.md) for Docker setup instructions.

## Technologies

- **React 18**: UI framework
- **Axios**: HTTP client
- **React Scripts**: Build tooling
- **CSS3**: Styling (no CSS framework for minimal dependencies)

## Future Enhancements

- User authentication UI (login/logout)
- Advanced filtering and search
- Pagination for large candidate lists
- Real-time updates with WebSockets
- Enhanced resume scoring interface
- Candidate detail view
- Edit/delete candidate functionality
