# feat(frontend): add candidate creation modal + Docker run notes

## Summary

This PR adds a candidate creation modal to the React frontend using Material-UI components, along with Docker run instructions.

## Changes

### 1. New Candidate Creation Modal
- **File**: `frontend/src/components/CandidateCreate.js`
- Material-UI modal form component with fields:
  - Full name (required)
  - Email (required)
  - Applied role (optional)
  - Resume file upload (optional, accepts .pdf, .txt, .doc, .docx)
- Props: `open` (bool), `onClose()`, `onCreated(createdCandidate)`
- Uses existing axios client to POST multipart/form-data to `/api/v1/candidates/`
- Displays Django REST Framework validation errors

### 2. Updated Candidates Component
- **File**: `frontend/src/components/Candidates.js`
- Added "New Candidate" button in header (next to Refresh/Logout)
- Integrated CandidateCreate modal with open/close state management
- New candidates appear at top of list upon successful creation
- Updated import to use `../api` instead of `../utils/api`

### 3. API Client Location
- **File**: `frontend/src/api.js`
- Copied from `frontend/src/utils/api.js` to match import paths in new components

### 4. Updated Dependencies
- **File**: `frontend/package.json`
- Added Material-UI dependencies:
  - `@mui/material: ^5.14.20`
  - `@emotion/react: ^11.11.1`
  - `@emotion/styled: ^11.11.0`

### 5. Docker Instructions
- **File**: `frontend/README_DOCKER.md`
- Comprehensive instructions for running the full stack with docker-compose
- Steps for creating Django superuser
- Guide for testing the candidate creation feature
- Notes on persistent media storage with Docker volumes

### 6. PR Documentation
- **File**: `PR_BODY.md` (this file)
- PR description and testing checklist

## Testing Checklist

- [ ] Start the stack: `docker-compose up --build`
- [ ] Create superuser: `docker-compose exec api python manage.py createsuperuser`
- [ ] Visit http://localhost:3000 and login with superuser credentials
- [ ] Navigate to /candidates page
- [ ] Click "New Candidate" button - modal should open
- [ ] Fill in required fields (full name and email)
- [ ] Optionally add applied role and upload resume file
- [ ] Click "Create" button
- [ ] Verify modal closes on success
- [ ] Verify new candidate appears at top of the list
- [ ] Verify resume link works if file was uploaded
- [ ] Test validation: try submitting with empty required fields
- [ ] Test error handling: try submitting duplicate email (if backend validates)

## Notes

- No changes to docker-compose.yml service definitions in this PR
- Media storage is handled via Docker volume (`media_files`)
- For persistent local media storage, a follow-up PR could mount `./media` directory
- All changes are focused on the candidate creation feature - no unrelated modifications

## Screenshots

(Screenshots to be added after UI verification)
