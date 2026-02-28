# Quick Start Guide - StyleFit AI

Get up and running with StyleFit AI in minutes!

## Prerequisites

- Node.js 18+ installed
- Python 3.8+ installed
- npm and pip package managers

## Quick Setup

### 1. Install Dependencies

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Start the Backend

```bash
cd backend
python app.py
```

Backend will be available at: `http://localhost:5000`

### 3. Start the Frontend (in a new terminal)

```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### 4. Use the Platform

1. Open your browser to `http://localhost:3000`
2. Click on the upload area to select a full-body photo
3. Once uploaded, browse the garment catalog
4. Click on any garment to see the virtual try-on
5. View the fit analysis and recommendations

## Development Mode

For development with hot reloading:

```bash
# Create .env file for development
echo "FLASK_DEBUG=true" > .env

# Backend will auto-reload on changes
cd backend
python app.py

# Frontend has Vite HMR enabled by default
npm run dev
```

## Production Build

```bash
# Build frontend
npm run build

# Run backend with gunicorn
pip install gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

- `GET /api/health` - Check API status
- `GET /api/garments` - Get available garments
- `POST /api/upload-photo` - Upload user photo
- `POST /api/try-on` - Perform virtual try-on

## Troubleshooting

### Port Already in Use

If port 5000 or 3000 is already in use:

```bash
# For backend (edit backend/app.py and change port=5000)
# For frontend (edit vite.config.js and change port: 3000)
```

### Module Not Found

Make sure you're in the correct directory:

```bash
# For backend
cd backend && python app.py

# For frontend  
npm run dev  # from project root
```

### CORS Issues

The backend is configured with CORS enabled for development. For production, configure CORS to only allow your frontend domain.

## Next Steps

- Explore the code in `src/` and `backend/`
- Check out the full README.md for detailed documentation
- Customize garments in `backend/api/garment_processor.py`
- Enhance the AI models for better accuracy

Enjoy building with StyleFit AI! 🎨👗
